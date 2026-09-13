"""Experimento controlado: ¿el recorte segmentado ayuda o daña los embeddings de BioCLIP?

Fase 4 variante C dio peor resultado que variante A, pero la comparación estaba
confundida: variante A corrió con 28 especies y variante C con 41. Este script
aísla la variable real usando EXACTAMENTE el mismo conjunto de imágenes (las 41
especies del manifiesto actual) y el mismo encoder BioCLIP zero-shot, cambiando
solo una cosa: si la imagen se recorta al bounding box de la máscara o no.

No entrena nada — solo extrae embeddings y hace k-NN (train como referencia,
test como consulta). Si el modo recortado rinde peor, confirma que el recorte
saca a las imágenes de la distribución que BioCLIP conoce, y explicaría el
resultado de variante C sin necesidad de otra corrida de entrenamiento.

Uso:
    python bioclip/scripts/experimento_recorte_vs_completa.py
"""

import io
import json
import sys
import time
from pathlib import Path

import numpy as np
import open_clip
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)

RAIZ_DATOS = Path(r"D:\Anura\data dirty")
MANIFIESTO = Path(r"D:\Anura\training\manifiesto.json")
MASCARAS = Path(r"D:\Anura\segmentacion\mascaras_dataset")
SALIDA = Path(r"D:\Anura\bioclip\evaluation\experimento_recorte.json")
MODELO_HF = "hf-hub:imageomics/bioclip"


class DatasetComparacion(Dataset):
    """Devuelve el embedding de entrada en modo recortado o completo."""

    def __init__(self, entradas, preprocess, recortar: bool):
        self.entradas = entradas
        self.preprocess = preprocess
        self.recortar = recortar

    def __len__(self):
        return len(self.entradas)

    def _recortar(self, imagen: Image.Image, ruta_relativa: str) -> Image.Image:
        ruta_mascara = MASCARAS / Path(ruta_relativa).with_suffix(".png")
        if not ruta_mascara.exists():
            return imagen
        with Image.open(ruta_mascara).convert("L") as m:
            mascara = np.array(m)
        filas = np.any(mascara > 127, axis=1)
        cols = np.any(mascara > 127, axis=0)
        if not filas.any() or not cols.any():
            return imagen
        y0, y1 = np.where(filas)[0][[0, -1]]
        x0, x1 = np.where(cols)[0][[0, -1]]
        return imagen.crop((int(x0), int(y0), int(x1) + 1, int(y1) + 1))

    def __getitem__(self, idx):
        entrada = self.entradas[idx]
        with Image.open(RAIZ_DATOS / entrada["ruta"]).convert("RGB") as img:
            if self.recortar:
                img = self._recortar(img, entrada["ruta"])
            tensor = self.preprocess(img)
        return tensor, entrada["idx_especie"]


@torch.no_grad()
def extraer(visual, dl, dispositivo):
    embs, etiquetas = [], []
    for x, y in dl:
        x = x.to(dispositivo)
        with torch.autocast(device_type="cuda" if "cuda" in dispositivo else "cpu"):
            e = visual(x)
        e = e.float()
        e = e / e.norm(dim=-1, keepdim=True)
        embs.append(e.cpu().numpy())
        etiquetas.append(y.numpy())
    return np.concatenate(embs), np.concatenate(etiquetas)


def knn_evaluar(emb_train, y_train, emb_test, y_test, k=5):
    """k-NN por similitud coseno (embeddings ya normalizados). Top-1 y Top-3."""
    similitudes = emb_test @ emb_train.T  # (n_test, n_train)
    vecinos = np.argsort(-similitudes, axis=1)[:, :k]

    n_clases = int(max(y_train.max(), y_test.max())) + 1
    aciertos_top1 = 0
    aciertos_top3 = 0
    for i in range(len(y_test)):
        votos = np.zeros(n_clases)
        for rango, j in enumerate(vecinos[i]):
            votos[y_train[j]] += similitudes[i, j]
        orden = np.argsort(-votos)
        if orden[0] == y_test[i]:
            aciertos_top1 += 1
        if y_test[i] in orden[:3]:
            aciertos_top3 += 1
    return aciertos_top1 / len(y_test), aciertos_top3 / len(y_test)


def main():
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"{'='*70}\nEXPERIMENTO: recorte segmentado vs imagen completa\n{'='*70}")
    print(f"Dispositivo: {dispositivo}")
    print("Encoder: BioCLIP v1 zero-shot (SIN fine-tuning, idéntico en ambos modos)")

    manifiesto = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    entradas_train = manifiesto["particiones"]["train"]
    entradas_test = manifiesto["particiones"]["test"]
    n_especies = len({e["idx_especie"] for e in entradas_train})
    print(f"Mismo conjunto en ambos modos: {len(entradas_train)} train, {len(entradas_test)} test, {n_especies} especies\n")

    modelo_clip, _, preprocess = open_clip.create_model_and_transforms(MODELO_HF)
    visual = modelo_clip.visual.to(dispositivo).eval()

    resultados = {}
    for modo, recortar in (("completa", False), ("recortada", True)):
        t0 = time.time()
        dl_train = DataLoader(DatasetComparacion(entradas_train, preprocess, recortar), batch_size=32, num_workers=0)
        dl_test = DataLoader(DatasetComparacion(entradas_test, preprocess, recortar), batch_size=32, num_workers=0)

        emb_train, y_train = extraer(visual, dl_train, dispositivo)
        emb_test, y_test = extraer(visual, dl_test, dispositivo)
        top1, top3 = knn_evaluar(emb_train, y_train, emb_test, y_test)
        dt = time.time() - t0

        resultados[modo] = {"top1": top1, "top3": top3}
        print(f"  [{modo:>10}]  Top-1 = {top1:>6.1%}   Top-3 = {top3:>6.1%}   ({dt:.0f}s)")

    print(f"\n{'='*70}\nVEREDICTO\n{'='*70}")
    delta_top1 = resultados["recortada"]["top1"] - resultados["completa"]["top1"]
    delta_top3 = resultados["recortada"]["top3"] - resultados["completa"]["top3"]
    print(f"  Δ Top-1 (recortada − completa): {delta_top1:+.1%}")
    print(f"  Δ Top-3 (recortada − completa): {delta_top3:+.1%}")
    if delta_top1 < -0.02:
        print(f"\n  ❌ El recorte DAÑA los embeddings de BioCLIP.")
        print(f"     Explica el resultado de Fase 4 variante C sin necesidad de más entrenamientos.")
        print(f"     Causa probable: recortar ~10% del encuadre y reescalar a 224x224 introduce")
        print(f"     borrosidad severa, y/o se pierde contexto que BioCLIP usa como señal.")
    elif delta_top1 > 0.02:
        print(f"\n  ✅ El recorte AYUDA a los embeddings.")
        print(f"     El mal resultado de variante C viene de otro lado (ajuste de hiperparámetros,")
        print(f"     no de la segmentación en sí).")
    else:
        print(f"\n  ⚖️  Diferencia despreciable (<2pp): el recorte no cambia la calidad del embedding.")
        print(f"     La segmentación no aporta ni perjudica a este encoder — el cuello de botella")
        print(f"     está en otra parte.")

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps({
        "n_train": len(entradas_train), "n_test": len(entradas_test), "n_especies": n_especies,
        "resultados": resultados, "delta_top1": delta_top1, "delta_top3": delta_top3,
    }, indent=2), encoding="utf-8")
    print(f"\n  Guardado en {SALIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
