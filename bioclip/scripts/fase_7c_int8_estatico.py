"""Fase 7c — Cuantización estática int8 vía ONNX Runtime (distinta de la
cuantización DINÁMICA de PyTorch que probamos en Fase 6b y perdió 5.35pp).

La diferencia importa: la dinámica solo toca capas Linear y calcula los rangos
de cada activación en cada inferencia (overhead, sin aprovechar bien la CPU).
La estática cuantiza TODO el grafo (incluida la convolución de patch embedding
y las matmul de atención) usando rangos precalculados sobre un set de
calibración real — es la que de verdad puede acelerar y reducir RAM en CPU.

Calibración: 200 imágenes de TRAIN (no aumentadas, no test — usar test aquí
sería la misma fuga de datos que evitamos en el prior geográfico).

Validación: Top-1 real sobre las 766 imágenes de test completas (no una
muestra de 64) porque la cuantización estática es más agresiva y una muestra
chica podría esconder una caída real.

Uso:
    python bioclip/scripts/fase_7c_int8_estatico.py
"""

import json
import sys
from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort
import open_clip
import torch
from onnxruntime.quantization import (
    CalibrationDataReader, CalibrationMethod, QuantFormat, QuantType, quantize_static,
)
from onnxruntime.quantization.shape_inference import quant_pre_process
from PIL import Image
from torch.utils.data import DataLoader, Dataset

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ_DATOS = Path(r"D:\Anura\data cleaned")
MANIFIESTO = Path(r"D:\Anura\training\manifiesto.json")
MODELO_FP32 = Path(r"D:\Anura\bioclip\checkpoints\anura_clasificador.onnx")
MODELO_FP32_PREP = Path(r"D:\Anura\bioclip\checkpoints\anura_clasificador_preprocesado.onnx")
SALIDA_INT8 = Path(r"D:\Anura\bioclip\checkpoints\anura_clasificador_int8_estatico.onnx")
N_CALIBRACION = 200
MODELO_HF = "hf-hub:imageomics/bioclip"


class DatasetImagenes(Dataset):
    def __init__(self, entradas, preprocess):
        self.entradas = entradas
        self.preprocess = preprocess

    def __len__(self):
        return len(self.entradas)

    def __getitem__(self, idx):
        e = self.entradas[idx]
        with Image.open(RAIZ_DATOS / e["ruta"]).convert("RGB") as img:
            return self.preprocess(img), e["idx_especie"]


class LectorCalibracion(CalibrationDataReader):
    """Entrega los tensores de calibración uno por uno, como pide la API de
    ONNX Runtime. Usa SOLO train (no aumentadas) — nunca test."""

    def __init__(self, tensores: np.ndarray, nombre_input: str):
        self._tensores = tensores
        self._nombre = nombre_input
        self._idx = 0

    def get_next(self):
        if self._idx >= len(self._tensores):
            return None
        t = self._tensores[self._idx:self._idx + 1]
        self._idx += 1
        return {self._nombre: t}

    def rewind(self):
        self._idx = 0


@torch.no_grad()
def top1_de(sesion, dl, nombre_input):
    aciertos, total = 0, 0
    for x, y in dl:
        salida = sesion.run(None, {nombre_input: x.numpy()})
        pred = salida[2].argmax(-1)
        aciertos += int((pred == y.numpy()).sum())
        total += len(y)
    return aciertos / total


def main():
    print(f"{'='*88}\nFASE 7c: Cuantización estática int8 (ONNX Runtime)\n{'='*88}\n")

    print("[1/6] Cargando preprocess y manifiesto...")
    _, _, preprocess = open_clip.create_model_and_transforms(MODELO_HF)
    manifiesto = json.loads(MANIFIESTO.read_text(encoding="utf-8"))

    entradas_train = [e for e in manifiesto["particiones"]["train"] if not e.get("aumentada")]
    rng = np.random.default_rng(42)
    idx_calib = rng.choice(len(entradas_train), size=min(N_CALIBRACION, len(entradas_train)),
                            replace=False)
    entradas_calib = [entradas_train[i] for i in idx_calib]
    print(f"  Calibración: {len(entradas_calib)} imágenes de TRAIN (nunca test)")

    print("\n[2/6] Preprocesando set de calibración...")
    ds_calib = DatasetImagenes(entradas_calib, preprocess)
    tensores_calib = np.stack([ds_calib[i][0].numpy() for i in range(len(ds_calib))])

    sesion_tmp = ort.InferenceSession(str(MODELO_FP32), providers=["CPUExecutionProvider"])
    nombre_input = sesion_tmp.get_inputs()[0].name
    del sesion_tmp

    print("\n[3/6] Pre-procesando el grafo (shape inference + constant folding)...")
    # Sin esto, el cuantizador no tiene shapes completas y trata pesos de
    # LayerNorm (rank 1) como si tuvieran el eje de canal de una Conv/MatMul
    # (rank 2+) — eso fue lo que corrompió el modelo en el primer intento
    # (Top-1 3.5%, ver warnings "Axis 1 is out-of-range ... with rank 1").
    # skip_symbolic_shape=False (el modo completo) rompe con un bug interno
    # de symbolic_shape_infer.py en un nodo Expand del grafo que genera el
    # exportador dynamo de PyTorch — no es nuestro grafo el que está mal,
    # es una incompatibilidad conocida de la herramienta. La variante básica
    # (solo ONNX shape inference, sin symbolic) es más robusta.
    quant_pre_process(str(MODELO_FP32), str(MODELO_FP32_PREP), skip_symbolic_shape=True)
    print(f"  ✓ {MODELO_FP32_PREP.name}")

    print("\n[4/6] Cuantizando (QDQ, int8 activaciones + pesos)...")
    lector = LectorCalibracion(tensores_calib, nombre_input)
    SALIDA_INT8.parent.mkdir(parents=True, exist_ok=True)
    # per_channel=True corrompió el modelo (Top-1 3.5%, bug de ejes en
    # LayerNorm). per_channel=False lo arregló pero quedó en 8.2%: los ViT
    # son conocidos por ser sensibles a MinMax en Softmax/LayerNorm, cuyos
    # rangos dinámicos MinMax no captura bien (los outliers de pocos frames
    # dominan la escala). Percentile recorta esos outliers al calibrar.
    quantize_static(
        model_input=str(MODELO_FP32_PREP),
        model_output=str(SALIDA_INT8),
        calibration_data_reader=lector,
        quant_format=QuantFormat.QDQ,
        activation_type=QuantType.QInt8,
        weight_type=QuantType.QInt8,
        per_channel=False,
        calibrate_method=CalibrationMethod.Percentile,
        extra_options={"CalibPercentile": 99.999},
    )
    mb_fp32 = MODELO_FP32.stat().st_size / (1024 * 1024)
    mb_int8 = SALIDA_INT8.stat().st_size / (1024 * 1024)
    print(f"  ✓ {SALIDA_INT8.name} ({mb_int8:.1f} MB, desde {mb_fp32:.1f} MB fp32, "
          f"{mb_fp32/mb_int8:.2f}x más liviano)")

    print(f"\n[5/6] Validando Top-1 sobre las 766 imágenes de TEST completas...")
    entradas_test = manifiesto["particiones"]["test"]
    dl_test = DataLoader(DatasetImagenes(entradas_test, preprocess), batch_size=1, num_workers=2)

    sesion_fp32 = ort.InferenceSession(str(MODELO_FP32), providers=["CPUExecutionProvider"])
    sesion_int8 = ort.InferenceSession(str(SALIDA_INT8), providers=["CPUExecutionProvider"])

    top1_fp32 = top1_de(sesion_fp32, dl_test, nombre_input)
    top1_int8 = top1_de(sesion_int8, dl_test, nombre_input)

    print(f"  Top-1 fp32 (ONNX) : {top1_fp32:.2%}")
    print(f"  Top-1 int8 estático : {top1_int8:.2%}")
    print(f"  Δ : {(top1_int8-top1_fp32)*100:+.2f} pp")

    print(f"\n[6/6] Comparando contra int8 DINÁMICO de Fase 6b (referencia)...")
    comparacion_previa = Path(r"D:\Anura\bioclip\evaluation\comparacion_precisiones.json")
    if comparacion_previa.exists():
        prev = json.loads(comparacion_previa.read_text(encoding="utf-8"))
        if "int8" in prev:
            print(f"  int8 dinámico (PyTorch, Fase 6b): Top-1={prev['int8']['top1']:.2%} "
                  f"(Δ={( prev['int8']['top1']-prev['fp32']['top1'])*100:+.2f}pp vs fp32)")
    print(f"  int8 estático (ONNX, esta fase)  : Top-1={top1_int8:.2%} "
          f"(Δ={(top1_int8-top1_fp32)*100:+.2f}pp vs fp32)")

    resumen = {
        "n_calibracion": len(entradas_calib),
        "n_test": len(entradas_test),
        "mb_fp32": round(mb_fp32, 1),
        "mb_int8_estatico": round(mb_int8, 1),
        "top1_fp32": top1_fp32,
        "top1_int8_estatico": top1_int8,
        "delta_pp": (top1_int8 - top1_fp32) * 100,
    }
    salida_json = Path(r"D:\Anura\bioclip\evaluation\int8_estatico_resultado.json")
    salida_json.write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nGuardado en {salida_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
