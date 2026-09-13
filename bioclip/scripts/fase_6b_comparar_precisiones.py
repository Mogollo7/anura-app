"""Fase 6b — Compara fp32 / fp16 / int8 con la métrica que importa: Top-1 real.

La comparación de embeddings por similitud coseno (Fase 6) dice si los vectores
se parecen, no si el modelo *acierta* igual. Aquí se mide el Top-1 y Top-3 del
clasificador completo sobre el mismo test set en las tres precisiones, más la
latencia real en CPU — que es el motivo de existir de int8.

int8 se aplica con cuantización dinámica sobre las capas Linear (el grueso de
un ViT). No necesita calibración y es la variante que acelera en CPU.

Uso:
    python bioclip/scripts/fase_6b_comparar_precisiones.py
"""

import json
import sys
import time
from pathlib import Path

import numpy as np
import open_clip
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "training"))

from fase_4_transfer_learning import BioClipMultiHead  # noqa: E402
from taxonomia import vocabularios  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ_DATOS = Path(r"D:\Anura\data cleaned")
MANIFIESTO = Path(r"D:\Anura\training\manifiesto.json")
CHECKPOINT = Path(r"D:\Anura\bioclip\checkpoints\bioclip_anura_mejor.pt")
SALIDA_INT8 = Path(r"D:\Anura\bioclip\checkpoints\encoder_anura_int8.pt")
SALIDA = Path(r"D:\Anura\bioclip\evaluation\comparacion_precisiones.json")
MODELO_HF = "hf-hub:imageomics/bioclip"

N_LATENCIA = 24  # imágenes para medir latencia en CPU (int8 en CPU es lento de medir)


class DatasetTest(Dataset):
    def __init__(self, entradas, preprocess):
        self.entradas = entradas
        self.preprocess = preprocess

    def __len__(self):
        return len(self.entradas)

    def __getitem__(self, idx):
        e = self.entradas[idx]
        with Image.open(RAIZ_DATOS / e["ruta"]).convert("RGB") as img:
            return self.preprocess(img), e["idx_especie"]


def construir_modelo(familias, generos, especies, dispositivo):
    modelo_clip, _, preprocess = open_clip.create_model_and_transforms(MODELO_HF)
    ck = torch.load(CHECKPOINT, map_location="cpu", weights_only=False)
    modelo = BioClipMultiHead(modelo_clip.visual, len(familias), len(generos), len(especies))
    modelo.visual.load_state_dict(ck["visual_state_dict"])
    modelo.cabeza_familia.load_state_dict(ck["cabezas_state_dict"]["familia"])
    modelo.cabeza_genero.load_state_dict(ck["cabezas_state_dict"]["genero"])
    modelo.cabeza_especie.load_state_dict(ck["cabezas_state_dict"]["especie"])
    return modelo.to(dispositivo).eval(), preprocess


@torch.no_grad()
def evaluar(modelo, cargador, dispositivo, dtype=torch.float32):
    aciertos1, aciertos3, total = 0, 0, 0
    for x, y in cargador:
        x = x.to(dispositivo, dtype=dtype)
        _, (_, _, logits) = modelo(x)
        logits = logits.float().cpu()
        aciertos1 += (logits.argmax(-1) == y).sum().item()
        aciertos3 += (logits.topk(3, -1).indices == y.unsqueeze(-1)).any(-1).sum().item()
        total += len(y)
    return aciertos1 / total, aciertos3 / total


@torch.no_grad()
def medir_latencia(modelo, tensores, dtype=torch.float32):
    modelo(tensores[0].unsqueeze(0).to(dtype))  # warm-up
    t0 = time.perf_counter()
    for t in tensores:
        modelo(t.unsqueeze(0).to(dtype))
    return (time.perf_counter() - t0) / len(tensores) * 1000  # ms/imagen


def main():
    familias, generos, especies = vocabularios()
    manifiesto = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    entradas = manifiesto["particiones"]["test"]
    print(f"{'='*78}\nFASE 6b: fp32 vs fp16 vs int8\n{'='*78}")
    print(f"Test set: {len(entradas)} imágenes\n")

    resultados = {}

    # ── fp32 y fp16 en GPU (si hay) ──
    if torch.cuda.is_available():
        modelo, preprocess = construir_modelo(familias, generos, especies, "cuda")
        dl = DataLoader(DatasetTest(entradas, preprocess), batch_size=32, num_workers=2)

        print("[fp32] evaluando en GPU...")
        t1, t3 = evaluar(modelo, dl, "cuda", torch.float32)
        resultados["fp32"] = {"top1": t1, "top3": t3, "mb": 328.9}
        print(f"  Top-1 = {t1:.2%}   Top-3 = {t3:.2%}")

        print("[fp16] evaluando en GPU...")
        modelo_h = modelo.half()
        t1, t3 = evaluar(modelo_h, dl, "cuda", torch.float16)
        resultados["fp16"] = {"top1": t1, "top3": t3, "mb": 164.4}
        print(f"  Top-1 = {t1:.2%}   Top-3 = {t3:.2%}")
        del modelo, modelo_h
        torch.cuda.empty_cache()

    # ── int8 en CPU ──
    print("\n[int8] cuantizando en CPU (dinámica sobre capas Linear)...")
    modelo_cpu, preprocess = construir_modelo(familias, generos, especies, "cpu")
    modelo_int8 = torch.ao.quantization.quantize_dynamic(
        modelo_cpu, {torch.nn.Linear}, dtype=torch.qint8
    )
    torch.save(modelo_int8.state_dict(), SALIDA_INT8)
    mb_int8 = SALIDA_INT8.stat().st_size / (1024 * 1024)
    print(f"  ✓ {SALIDA_INT8.name} ({mb_int8:.1f} MB)")

    dl_cpu = DataLoader(DatasetTest(entradas, preprocess), batch_size=16, num_workers=2)
    print("  evaluando en CPU (puede tardar)...")
    t1, t3 = evaluar(modelo_int8, dl_cpu, "cpu")
    resultados["int8"] = {"top1": t1, "top3": t3, "mb": round(mb_int8, 1)}
    print(f"  Top-1 = {t1:.2%}   Top-3 = {t3:.2%}")

    # ── Latencia en CPU: fp32 vs int8 ──
    print(f"\n[latencia CPU] {N_LATENCIA} imágenes, 1 por vez...")
    tensores = [DatasetTest(entradas[:N_LATENCIA], preprocess)[i][0] for i in range(N_LATENCIA)]
    ms_fp32 = medir_latencia(modelo_cpu, tensores)
    ms_int8 = medir_latencia(modelo_int8, tensores)
    resultados["fp32"]["ms_cpu"] = round(ms_fp32, 1)
    resultados["int8"]["ms_cpu"] = round(ms_int8, 1)
    print(f"  fp32 = {ms_fp32:6.1f} ms/img")
    print(f"  int8 = {ms_int8:6.1f} ms/img   ({ms_fp32/ms_int8:.2f}x)")

    # ── Tabla ──
    base = resultados["fp32"]["top1"]
    print(f"\n{'='*78}\n{'FORMATO':<10}{'TAMAÑO':>10}{'TOP-1':>9}{'Δ TOP-1':>10}{'TOP-3':>9}{'CPU ms':>10}\n{'='*78}")
    for nombre in ("fp32", "fp16", "int8"):
        if nombre not in resultados:
            continue
        r = resultados[nombre]
        delta = (r["top1"] - base) * 100
        ms = f"{r['ms_cpu']:.0f}" if "ms_cpu" in r else "-"
        print(f"{nombre:<10}{r['mb']:>8.1f}MB{r['top1']:>8.1%}{delta:>+9.2f}pp{r['top3']:>8.1%}{ms:>10}")

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nGuardado en {SALIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
