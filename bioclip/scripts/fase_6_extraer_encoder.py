"""Fase 6 — Extrae el encoder visual de BioCLIP del checkpoint Fase 4.

Exporta el encoder (sin las cabezas de clasificación) en dos precisiones:
  - fp32 (~329 MB): referencia, máxima fidelidad
  - fp16 (~165 MB): mitad de peso, para despliegue

La validación NO usa ruido aleatorio: mide la degradación real sobre imágenes
del split de test. Un tensor aleatorio no dice nada sobre el impacto en el uso
real, porque la geometría del embedding solo importa en la región del espacio
donde caen las fotos de ranas. Se reporta la similitud coseno fp32 vs fp16 y,
sobre todo, si el ranking de vecinos más cercanos cambia — que es lo que de
verdad rompería una búsqueda por similitud.

Uso:
    python bioclip/scripts/fase_6_extraer_encoder.py
"""

import json
import sys
from pathlib import Path

import open_clip
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ_DATOS = Path(r"D:\Anura\data cleaned")
MANIFIESTO = Path(r"D:\Anura\training\manifiesto.json")
CHECKPOINT = Path(r"D:\Anura\bioclip\checkpoints\bioclip_anura_mejor.pt")
SALIDA_FP32 = Path(r"D:\Anura\bioclip\checkpoints\encoder_anura.pt")
SALIDA_FP16 = Path(r"D:\Anura\bioclip\checkpoints\encoder_anura_fp16.pt")
METADATA = Path(r"D:\Anura\bioclip\evaluation\encoder_metadata.json")
MODELO_HF = "hf-hub:imageomics/bioclip"

N_VALIDACION = 256  # imágenes de test para medir la degradación fp16


class EncoderVisual(torch.nn.Module):
    """Encoder visual BioCLIP: imagen 224x224 -> embedding 512D normalizado."""

    def __init__(self, visual_encoder):
        super().__init__()
        self.visual = visual_encoder

    def forward(self, x):
        emb = self.visual(x)
        return emb / emb.norm(dim=-1, keepdim=True)


class DatasetValidacion(Dataset):
    def __init__(self, entradas, preprocess):
        self.entradas = entradas
        self.preprocess = preprocess

    def __len__(self):
        return len(self.entradas)

    def __getitem__(self, idx):
        with Image.open(RAIZ_DATOS / self.entradas[idx]["ruta"]).convert("RGB") as img:
            return self.preprocess(img)


@torch.no_grad()
def embeddings_de(encoder, cargador, dispositivo, dtype):
    salida = []
    for x in cargador:
        x = x.to(dispositivo, dtype=dtype)
        salida.append(encoder(x).float().cpu())
    return torch.cat(salida)


def main():
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"{'='*78}\nFASE 6: Extracción de Encoder Visual (fp32 + fp16)\n{'='*78}")
    print(f"Dispositivo: {dispositivo}\n")

    print("[1/5] Cargando BioCLIP v1 y pesos de Fase 4...")
    modelo_clip, _, preprocess = open_clip.create_model_and_transforms(MODELO_HF)
    checkpoint = torch.load(CHECKPOINT, map_location="cpu", weights_only=False)
    modelo_clip.visual.load_state_dict(checkpoint["visual_state_dict"])

    encoder = EncoderVisual(modelo_clip.visual).to(dispositivo).eval()
    n_params = sum(p.numel() for p in encoder.parameters())
    print(f"  ✓ Encoder listo — {n_params:,} parámetros")

    # ── Export fp32 ──
    print(f"\n[2/5] Exportando fp32...")
    SALIDA_FP32.parent.mkdir(parents=True, exist_ok=True)
    torch.save(encoder.state_dict(), SALIDA_FP32)
    mb_fp32 = SALIDA_FP32.stat().st_size / (1024 * 1024)
    print(f"  ✓ {SALIDA_FP32.name} ({mb_fp32:.1f} MB)")

    # ── Export fp16 ──
    print(f"[3/5] Exportando fp16...")
    estado_fp16 = {k: v.half() for k, v in encoder.state_dict().items()}
    torch.save(estado_fp16, SALIDA_FP16)
    mb_fp16 = SALIDA_FP16.stat().st_size / (1024 * 1024)
    print(f"  ✓ {SALIDA_FP16.name} ({mb_fp16:.1f} MB)  —  {mb_fp32/mb_fp16:.2f}x más liviano")

    # ── Validación sobre imágenes reales ──
    print(f"\n[4/5] Midiendo degradación sobre {N_VALIDACION} imágenes reales de test...")
    manifiesto = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    entradas = manifiesto["particiones"]["test"][:N_VALIDACION]
    dl = DataLoader(DatasetValidacion(entradas, preprocess), batch_size=32, num_workers=2)

    emb32 = embeddings_de(encoder, dl, dispositivo, torch.float32)

    encoder_fp16 = EncoderVisual(modelo_clip.visual).to(dispositivo).half().eval()
    encoder_fp16.load_state_dict(estado_fp16)
    emb16 = embeddings_de(encoder_fp16, dl, dispositivo, torch.float16)

    cos = torch.nn.functional.cosine_similarity(emb32, emb16, dim=-1)
    print(f"  Similitud coseno fp32 vs fp16:")
    print(f"    media   = {cos.mean():.6f}")
    print(f"    mínima  = {cos.min():.6f}")
    print(f"    p1      = {cos.quantile(0.01):.6f}")

    # ── Lo que de verdad importa: ¿cambia el vecino más cercano? ──
    print(f"\n[5/5] ¿Se conserva el ranking de vecinos (uso real en búsqueda)?")
    sim32 = emb32 @ emb32.T
    sim16 = emb16 @ emb16.T
    sim32.fill_diagonal_(-2)
    sim16.fill_diagonal_(-2)

    vecino32 = sim32.argmax(dim=-1)
    vecino16 = sim16.argmax(dim=-1)
    coincide_top1 = (vecino32 == vecino16).float().mean()

    top5_32 = sim32.topk(5, dim=-1).indices
    top5_16 = sim16.topk(5, dim=-1).indices
    solape_top5 = torch.stack([
        torch.isin(top5_32[i], top5_16[i]).float().mean() for i in range(len(top5_32))
    ]).mean()

    print(f"    vecino #1 idéntico   = {coincide_top1:.1%}")
    print(f"    solape del top-5     = {solape_top5:.1%}")

    ok = coincide_top1 > 0.95 and cos.min() > 0.999
    print(f"\n  {'✓ fp16 es seguro para producción' if ok else '⚠ revisar: degradación mayor a la esperada'}")

    metadata = {
        "nombre": "Encoder Visual BioCLIP Anura v1",
        "base_model": "imageomics/bioclip",
        "n_parametros": n_params,
        "entrenamiento": {
            "dataset": "12,254 fotos limpias, 41 especies",
            "loss": "jerárquica: familia(0.2) + género(0.3) + especie(0.5)",
            "oversampling": "proporcional (umbral 70 reales/especie, tope 4x)",
            "class_weights": "frecuencia inversa sobre especie",
        },
        "metricas_clasificador_fase4": {
            "top1_test": 0.5705,
            "top3_test": 0.8238,
            "n_test": 766,
        },
        "salida": {"embedding_dim": 512, "input_shape": [3, 224, 224], "normalizado_l2": True},
        "formatos": {
            "fp32": {"ruta": str(SALIDA_FP32), "mb": round(mb_fp32, 1)},
            "fp16": {"ruta": str(SALIDA_FP16), "mb": round(mb_fp16, 1)},
        },
        "validacion_fp16": {
            "n_imagenes_reales": len(entradas),
            "cos_media": float(cos.mean()),
            "cos_minima": float(cos.min()),
            "vecino_1_identico": float(coincide_top1),
            "solape_top5": float(solape_top5),
            "apto_produccion": bool(ok),
        },
    }
    METADATA.parent.mkdir(parents=True, exist_ok=True)
    METADATA.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n✅ FASE 6 OK — metadata en {METADATA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
