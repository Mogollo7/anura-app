"""Fase 2 — Obtener embeddings de una muestra del dataset.

Genera y guarda embeddings para una muestra pequeña del dataset antes de
entrenar, para verificar que el pipeline funciona de punta a punta.

Uso:
    python bioclip/scripts/fase_2_obtener_embeddings.py
    python bioclip/scripts/fase_2_obtener_embeddings.py --imagenes-por-especie 10
    python bioclip/scripts/fase_2_obtener_embeddings.py --todas
"""

import argparse
import io
import json
import sys
from pathlib import Path

import numpy as np
import torch
import open_clip
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)


RAIZ_DATOS = Path(r"D:\Anura\data dirty")
SALIDA = Path(r"D:\Anura\bioclip\datasets\embeddings_muestra.npy")
SALIDA_META = Path(r"D:\Anura\bioclip\datasets\embeddings_muestra_meta.json")
MODELO_HF = "hf-hub:imageomics/bioclip"
EXTENSIONES = {".jpg", ".jpeg", ".png"}
LISTA_NEGRA = Path(r"D:\Anura\training\lista_negra.json")


def cargar_lista_negra():
    if LISTA_NEGRA.exists():
        return set(json.loads(LISTA_NEGRA.read_text(encoding="utf-8")))
    return set()


def descubrir_imagenes(especie: str, maximo: int, lista_negra: set) -> list[Path]:
    carpeta = RAIZ_DATOS / especie / "fotos"
    if not carpeta.is_dir():
        carpeta = RAIZ_DATOS / especie
    if not carpeta.is_dir():
        return []
    imagenes = sorted(
        p for p in carpeta.rglob("*")
        if p.is_file()
        and p.suffix.lower() in EXTENSIONES
        and "sonidos" not in p.parts
        and str(p.relative_to(RAIZ_DATOS)).replace("\\", "/") not in lista_negra
    )
    return imagenes[:maximo]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--imagenes-por-especie", type=int, default=10)
    parser.add_argument("--todas", action="store_true", help="Procesar todas las imágenes del dataset")
    args = parser.parse_args()

    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Dispositivo: {dispositivo}")

    # Cargar BioCLIP
    print("Cargando BioCLIP v1...")
    modelo, _, preprocesar = open_clip.create_model_and_transforms(MODELO_HF)
    modelo = modelo.to(dispositivo).eval()
    print(f"  OK ({sum(p.numel() for p in modelo.parameters()):,} parámetros)")

    # Descubrir imágenes
    lista_negra = cargar_lista_negra()
    maximo = 9999 if args.todas else args.imagenes_por_especie
    especies = sorted(p.name for p in RAIZ_DATOS.iterdir() if p.is_dir())

    print(f"\nDescubriendo imágenes ({maximo} max/especie)...")
    entradas = []
    for especie in especies:
        imgs = descubrir_imagenes(especie, maximo, lista_negra)
        for img in imgs:
            entradas.append((especie, img))
    print(f"  {len(entradas)} imágenes de {len(especies)} especies")

    # Generar embeddings
    print("\nGenerando embeddings...")
    embeddings = []
    metadatos = []
    errores = 0

    for i, (especie, ruta) in enumerate(entradas, 1):
        try:
            with Image.open(ruta).convert("RGB") as img:
                tensor = preprocesar(img).unsqueeze(0).to(dispositivo)
            with torch.no_grad():
                emb = modelo.encode_image(tensor)
                emb = emb / emb.norm(dim=-1, keepdim=True)
            embeddings.append(emb.cpu().numpy())
            metadatos.append({
                "especie": especie,
                "ruta": str(ruta.relative_to(RAIZ_DATOS)).replace("\\", "/"),
            })
        except Exception as exc:
            print(f"  [ERROR] {ruta.name}: {exc}")
            errores += 1

        if i % 50 == 0:
            print(f"  {i}/{len(entradas)} procesadas, {errores} errores")

    # Guardar
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    np.save(SALIDA, np.concatenate(embeddings, axis=0))
    SALIDA_META.write_text(json.dumps(metadatos, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nResultados:")
    print(f"  Embeddings guardados: {len(metadatos)}")
    print(f"  Forma array: {np.load(SALIDA).shape}")
    print(f"  Errores: {errores}")
    print(f"  Archivos: {SALIDA}, {SALIDA_META}")
    print(f"\n✅ FASE 2 OK — embeddings listos para baseline")


if __name__ == "__main__":
    sys.exit(main())
