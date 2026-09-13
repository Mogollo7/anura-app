"""Sincroniza dataset_limpio.json con lo que realmente existe en disco.

Tras una pasada de selección manual (borrar fotos malas directamente desde el
explorador), el inventario queda con rutas huérfanas. Este script las retira y
las registra como descartadas, sin volver a procesar la fuente: reejecutar
`limpiar_dataset.py` reconstruiría desde `data dirty` y revertiría la selección.

Uso:
    python training/sincronizar_dataset.py
    python training/sincronizar_dataset.py --dry-run
"""

import argparse
import collections
import json
from pathlib import Path

MINIMO_RECOMENDADO = 70


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", type=Path, default=Path(r"D:\Anura\data cleaned"))
    parser.add_argument("--dry-run", action="store_true", help="Solo reporta, no escribe")
    args = parser.parse_args()

    inventario = args.raiz / "dataset_limpio.json"
    datos = json.loads(inventario.read_text(encoding="utf-8"))

    conservadas, huerfanas = [], []
    for registro in datos["imagenes"]:
        if (args.raiz / registro["ruta"]).is_file():
            conservadas.append(registro)
        else:
            huerfanas.append(registro)

    antes = collections.Counter(r["especie"] for r in datos["imagenes"])
    despues = collections.Counter(r["especie"] for r in conservadas)

    print(f"{'ESPECIE':<32}{'ANTES':>7}{'AHORA':>7}{'BORRADAS':>10}{'%':>7}  AVISO")
    print("-" * 82)
    for especie in sorted(antes, key=lambda e: (e is None, e)):
        n_antes, n_ahora = antes[especie], despues.get(especie, 0)
        borradas = n_antes - n_ahora
        pct = 100 * borradas / n_antes if n_antes else 0
        aviso = ""
        if n_ahora == 0:
            aviso = "ESPECIE VACÍA"
        elif especie is not None and n_ahora < MINIMO_RECOMENDADO:
            aviso = f"bajo el mínimo ({MINIMO_RECOMENDADO})"
        etiqueta = especie if especie is not None else "(sin taxón)"
        print(f"{etiqueta:<32}{n_antes:>7}{n_ahora:>7}{borradas:>10}{pct:>6.1f}%  {aviso}")

    print("-" * 82)
    print(f"Conservadas: {len(conservadas)}  |  Huérfanas retiradas: {len(huerfanas)}")

    if args.dry_run:
        print("\n--dry-run: no se escribió nada.")
        return

    datos["imagenes"] = conservadas
    datos["descartadas"].extend(
        {"ruta": r["ruta"], "motivo": "eliminada en selección manual"} for r in huerfanas
    )
    inventario.write_text(
        json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nInventario actualizado: {inventario}")


if __name__ == "__main__":
    main()
