"""Escanea el dataset en busca de imágenes corruptas/truncadas antes de entrenar.

`data dirty/` no es un nombre casual: el scraper de iNaturalist puede haber dejado
descargas incompletas. Fallar a mitad del DataLoader (como ya pasó una vez) es más
caro que filtrar de antemano.

Uso:
    python training/validar_integridad.py
    python training/validar_integridad.py --escribir-lista-negra
"""

import argparse
import json
from pathlib import Path

from PIL import Image

EXTENSIONES = {".jpg", ".jpeg", ".png"}


def validar(ruta: Path) -> str | None:
    """Devuelve None si la imagen está bien, o un mensaje de error si no."""
    try:
        with Image.open(ruta) as img:
            img.verify()
        # verify() deja el objeto inutilizable; reabrir y cargar de verdad es lo que
        # hace el DataLoader en la práctica (convert + acceso a píxeles).
        with Image.open(ruta) as img:
            img.convert("RGB").load()
        return None
    except Exception as exc:
        return f"{type(exc).__name__}: {exc}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", type=Path, default=Path(r"D:\Anura\data dirty"))
    parser.add_argument("--escribir-lista-negra", action="store_true")
    parser.add_argument("--salida", type=Path, default=Path(r"D:\Anura\training\lista_negra.json"))
    args = parser.parse_args()

    rutas = sorted(
        p
        for p in args.raiz.rglob("*")
        if p.is_file() and p.suffix.lower() in EXTENSIONES and "sonidos" not in p.parts
    )
    print(f"Validando {len(rutas)} imágenes en {args.raiz} ...")

    rotas = []
    for i, ruta in enumerate(rutas, 1):
        error = validar(ruta)
        if error:
            # Forward slashes: así es como prepare_dataset.py guarda y compara rutas
            # en el manifiesto (str(...).replace("\\", "/")). Sin esto, la lista negra
            # nunca hace match en Windows y la imagen rota se vuelve a colar.
            relativa = str(ruta.relative_to(args.raiz)).replace("\\", "/")
            rotas.append((relativa, error))
            print(f"  [ROTA] {relativa} — {error}")
        if i % 2000 == 0:
            print(f"  ... {i}/{len(rutas)} revisadas, {len(rotas)} rotas hasta ahora")

    print(f"\nTotal: {len(rotas)} imágenes rotas de {len(rutas)} ({len(rotas)/len(rutas)*100:.2f}%)")
    if args.escribir_lista_negra:
        args.salida.write_text(
            json.dumps([r[0] for r in rotas], ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"Lista negra escrita en {args.salida}")


if __name__ == "__main__":
    main()
