"""Fase 5 — Evaluación completa por especie del checkpoint de Fase 4.

Responde: ¿el 57,0% Top-1 global está distribuido parejo entre las 41 especies,
o unas pocas especies escasas lo están arrastrando? De eso depende si conviene
reentrenar (con más paciencia / más datos en las débiles) o pasar ya a Fase 6.

Genera Top-1, F1, precisión y recall por especie, los pares que más se confunden
entre sí, y un corte específico sobre las especies con pocos individuos reales.

Uso:
    python bioclip/scripts/fase_5_evaluacion_completa.py
"""

import json
import sys
from pathlib import Path

import numpy as np
import open_clip
import torch
from PIL import Image
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from torch.utils.data import DataLoader, Dataset

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "training"))

from fase_4_transfer_learning import BioClipMultiHead  # noqa: E402  (re-envuelve sys.stdout al importar)
from taxonomia import vocabularios  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ_DATOS = Path(r"D:\Anura\data cleaned")
MANIFIESTO = Path(r"D:\Anura\training\manifiesto.json")
CHECKPOINT = Path(r"D:\Anura\bioclip\checkpoints\bioclip_anura_mejor.pt")
SALIDA = Path(r"D:\Anura\bioclip\evaluation\fase_5_completa.json")
MODELO_HF = "hf-hub:imageomics/bioclip"


class DatasetTest(Dataset):
    def __init__(self, entradas: list[dict], preprocess):
        self.entradas = entradas
        self.preprocess = preprocess

    def __len__(self):
        return len(self.entradas)

    def __getitem__(self, idx):
        entrada = self.entradas[idx]
        with Image.open(RAIZ_DATOS / entrada["ruta"]).convert("RGB") as img:
            tensor = self.preprocess(img)
        return tensor, entrada["idx_especie"]


@torch.no_grad()
def predecir(modelo, cargador, dispositivo):
    modelo.eval()
    predicciones, etiquetas, top3_ok = [], [], []
    for x, y_esp in cargador:
        x = x.to(dispositivo, non_blocking=True)
        with torch.autocast(device_type="cuda" if "cuda" in dispositivo else "cpu"):
            _, (_, _, logits_esp) = modelo(x)
        logits_esp = logits_esp.float().cpu()
        predicciones.append(logits_esp.argmax(-1).numpy())
        top3 = logits_esp.topk(3, dim=-1).indices
        top3_ok.append((top3 == y_esp.unsqueeze(-1)).any(-1).numpy())
        etiquetas.append(y_esp.numpy())
    return (
        np.concatenate(predicciones),
        np.concatenate(etiquetas),
        np.concatenate(top3_ok),
    )


def main():
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"{'='*78}\nFASE 5: Evaluación completa por especie\n{'='*78}")

    familias, generos, especies = vocabularios()
    manifiesto = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    entradas_test = manifiesto["particiones"]["test"]

    # Individuos reales en train por especie: contexto para leer los resultados
    # (una especie con 8 individuos reales y Top-1 bajo no es el mismo problema
    # que una con 49 individuos reales y Top-1 bajo).
    individuos_train = {}
    for entrada in manifiesto["particiones"]["train"]:
        if not entrada.get("aumentada"):
            individuos_train.setdefault(entrada["especie"], set()).add(entrada["grupo"])

    modelo_clip, _, preprocess_val = open_clip.create_model_and_transforms(MODELO_HF)
    checkpoint = torch.load(CHECKPOINT, map_location=dispositivo, weights_only=False)

    modelo = BioClipMultiHead(modelo_clip.visual, len(familias), len(generos), len(especies)).to(dispositivo)
    modelo.visual.load_state_dict(checkpoint["visual_state_dict"])
    modelo.cabeza_familia.load_state_dict(checkpoint["cabezas_state_dict"]["familia"])
    modelo.cabeza_genero.load_state_dict(checkpoint["cabezas_state_dict"]["genero"])
    modelo.cabeza_especie.load_state_dict(checkpoint["cabezas_state_dict"]["especie"])

    dl_test = DataLoader(DatasetTest(entradas_test, preprocess_val), batch_size=32, num_workers=2)
    print(f"Evaluando {len(entradas_test)} imágenes de test...\n")
    predicciones, etiquetas, top3_ok = predecir(modelo, dl_test, dispositivo)

    precision, recall, f1, soporte = precision_recall_fscore_support(
        etiquetas, predicciones, labels=range(len(especies)), average=None, zero_division=0
    )

    filas = []
    for i, especie in enumerate(especies):
        mascara = etiquetas == i
        n_test = int(mascara.sum())
        filas.append({
            "especie": especie,
            "n_test": n_test,
            "n_individuos_train_reales": len(individuos_train.get(especie, ())),
            "top1": float((predicciones[mascara] == i).mean()) if n_test else 0.0,
            "top3": float(top3_ok[mascara].mean()) if n_test else 0.0,
            "f1": float(f1[i]),
            "precision": float(precision[i]),
            "recall": float(recall[i]),
        })

    filas.sort(key=lambda r: r["top1"])

    print(f"{'ESPECIE':<30}{'N_TEST':>7}{'IND_TR':>7}{'TOP-1':>8}{'TOP-3':>8}{'F1':>7}")
    print("-" * 78)
    for r in filas:
        print(f"{r['especie']:<30}{r['n_test']:>7}{r['n_individuos_train_reales']:>7}"
              f"{r['top1']:>7.0%}{r['top3']:>8.0%}{r['f1']:>7.2f}")

    top1_global = float((predicciones == etiquetas).mean())
    print("-" * 78)
    print(f"Top-1 global: {top1_global:.1%}   Top-3 global: {top3_ok.mean():.1%}")

    # ── ¿El daño se concentra en las especies con pocos individuos reales? ──
    escasas = [r for r in filas if r["n_individuos_train_reales"] < 45]
    abundantes = [r for r in filas if r["n_individuos_train_reales"] >= 45]
    print(f"\n{'='*78}\n¿DÓNDE ESTÁ EL DAÑO?\n{'='*78}")
    for nombre, grupo in (("Escasas (<45 individuos reales en train)", escasas),
                          ("Abundantes (>=45)", abundantes)):
        if not grupo:
            continue
        media_top1 = np.mean([r["top1"] for r in grupo])
        media_f1 = np.mean([r["f1"] for r in grupo])
        print(f"{nombre:<45} n={len(grupo):>2}  Top-1 medio={media_top1:>6.1%}  F1 medio={media_f1:.2f}")

    ceros = [r for r in filas if r["top1"] == 0.0]
    if ceros:
        print(f"\nEspecies con Top-1 = 0% ({len(ceros)}): {', '.join(r['especie'] for r in ceros)}")

    # ── Pares que más se confunden entre sí ──
    cm = confusion_matrix(etiquetas, predicciones, labels=range(len(especies)))
    pares = []
    for i in range(len(especies)):
        for j in range(i + 1, len(especies)):
            total = int(cm[i, j] + cm[j, i])
            if total:
                pares.append((total, especies[i], especies[j]))
    pares.sort(reverse=True)

    print(f"\n{'='*78}\nPARES MÁS CONFUNDIBLES (top 10)\n{'='*78}")
    for total, esp_a, esp_b in pares[:10]:
        print(f"{total:>3} confusiones   {esp_a:<28} <-> {esp_b}")

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps({
        "meta": {
            "n_especies": len(especies),
            "n_test": int(len(etiquetas)),
            "top1_global": top1_global,
            "top3_global": float(top3_ok.mean()),
        },
        "por_especie": filas,
        "pares_confundibles": [
            {"confusiones": t, "especie_a": a, "especie_b": b} for t, a, b in pares
        ],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nGuardado en {SALIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
