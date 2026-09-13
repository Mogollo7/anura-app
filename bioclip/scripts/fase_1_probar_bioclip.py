"""Fase 1 — Probar BioCLIP v1 original sin modificaciones.

Objetivo: confirmar que el modelo carga correctamente, procesa una imagen,
produce un embedding 512-d y no tiene problemas de CUDA.

No entrena nada. Solo valida que el pipeline funciona.

Uso:
    python bioclip/scripts/fase_1_probar_bioclip.py
    python bioclip/scripts/fase_1_probar_bioclip.py --imagen "ruta/a/rana.jpg"
"""

import argparse
import io
import sys
from pathlib import Path

import torch
import open_clip
from PIL import Image

# Consola de Windows (cp1252) no soporta los emojis de los mensajes de estado.
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)


MODELO_HF = "hf-hub:imageomics/bioclip"
DIM_EMBEDDING = 512


def cargar_bioclip(dispositivo: str):
    print(f"Cargando BioCLIP v1 en {dispositivo}...")
    modelo, _, preprocesar = open_clip.create_model_and_transforms(MODELO_HF)
    modelo = modelo.to(dispositivo).eval()
    params_totales = sum(p.numel() for p in modelo.parameters())
    params_visual = sum(p.numel() for p in modelo.visual.parameters())
    params_texto = params_totales - params_visual
    print(f"  Parámetros modelo completo (visual + texto): {params_totales:,}")
    print(f"  Parámetros Image Encoder (model.visual):      {params_visual:,}  <- esto es lo que se extrae en Fase 6")
    print(f"  Parámetros Text Encoder (no viaja al móvil):   {params_texto:,}")
    print(f"  Dispositivo: {next(modelo.parameters()).device}")
    return modelo, preprocesar


def embedding_de_imagen(modelo, preprocesar, ruta: Path, dispositivo: str) -> torch.Tensor:
    with Image.open(ruta).convert("RGB") as img:
        tensor = preprocesar(img).unsqueeze(0).to(dispositivo)
    with torch.no_grad(), torch.autocast(device_type="cuda" if "cuda" in dispositivo else "cpu"):
        emb = modelo.encode_image(tensor)
        emb = emb / emb.norm(dim=-1, keepdim=True)  # L2 normalización
    return emb.cpu()


def validar_embedding(emb: torch.Tensor):
    assert emb.shape == (1, DIM_EMBEDDING), f"Forma inesperada: {emb.shape}, esperaba (1, {DIM_EMBEDDING})"
    norma = emb.norm(dim=-1).item()
    assert abs(norma - 1.0) < 1e-4, f"Norma L2 inesperada: {norma:.6f}, esperaba ≈1.0"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--imagen", type=Path, help="Ruta a imagen de prueba (opcional)")
    args = parser.parse_args()

    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n{'='*60}")
    print("FASE 1: Probar BioCLIP v1 original")
    print(f"{'='*60}")
    print(f"CUDA disponible: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"VRAM disponible: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

    # Cargar modelo
    modelo, preprocesar = cargar_bioclip(dispositivo)

    # Validar encoder visual
    print("\n[encoder visual]")
    visual = modelo.visual
    print(f"  Tipo: {type(visual).__name__}")

    # Probar con imagen si se da, o con tensor aleatorio
    if args.imagen and args.imagen.exists():
        print(f"\n[imagen real] {args.imagen}")
        emb = embedding_de_imagen(modelo, preprocesar, args.imagen, dispositivo)
    else:
        print("\n[imagen sintética] tensor aleatorio 224×224")
        with torch.no_grad():
            tensor = torch.randn(1, 3, 224, 224).to(dispositivo)
            emb = modelo.encode_image(tensor)
            emb = emb / emb.norm(dim=-1, keepdim=True)
            emb = emb.cpu()

    # Validar
    validar_embedding(emb)

    print(f"\nResultados:")
    print(f"  Forma embedding: {emb.shape}")
    print(f"  Norma L2: {emb.norm(dim=-1).item():.6f}")
    print(f"  Primeros 5 valores: {emb[0, :5].tolist()}")
    print(f"\n✅ FASE 1 OK — BioCLIP v1 carga y genera embeddings correctamente")

    return 0


if __name__ == "__main__":
    sys.exit(main())
