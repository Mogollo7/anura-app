"""Crea una copia limpia del dataset, lista para transfer learning.

La salida conserva una carpeta por especie, convierte imágenes a RGB JPEG,
descarta archivos inválidos o demasiado pequeños y elimina duplicados exactos
por SHA-256. La fuente nunca se modifica.

El registro usa los mismos campos taxonómicos que `prepare_dataset.py`
(especie canónica con guion bajo, género y familia derivados de `taxonomia.py`),
para que el manifiesto de entrenamiento y el inventario limpio no divergan.
"""

import argparse
import hashlib
import json
import re
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from taxonomia import ESPECIES, GENERO_A_FAMILIA, canonico, genero_de

EXTENSIONES = {".jpg", ".jpeg", ".png", ".webp"}
ETAPAS_EXCLUIDAS = {"tadpole", "renacuajo", "larva", "larvae"}


def hash_archivo(ruta: Path) -> str:
    digest = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            digest.update(bloque)
    return digest.hexdigest()


def convertir(origen: Path, destino: Path) -> tuple[str, int, int] | None:
    try:
        with Image.open(origen) as imagen:
            imagen.verify()
        with Image.open(origen) as imagen:
            imagen = imagen.convert("RGB")
            ancho, alto = imagen.size
            if ancho < 64 or alto < 64:
                return None
            destino.parent.mkdir(parents=True, exist_ok=True)
            imagen.save(destino, format="JPEG", quality=95, optimize=True)
            return hash_archivo(origen), ancho, alto
    except (OSError, UnidentifiedImageError):
        return None


def cargar_metadatos(raiz: Path) -> dict[str, dict]:
    """Indexa las fotos por nombre de archivo; las anotaciones se conservan si existen."""
    por_archivo: dict[str, dict] = {}
    for carpeta in (p for p in raiz.iterdir() if p.is_dir()):
        meta_path = carpeta / "fotos_metadata.json"
        if not meta_path.exists():
            continue
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        for foto in metadata.get("photos", []):
            nombre = foto.get("file_name")
            if nombre:
                por_archivo[nombre] = foto
    return por_archivo


def taxonomia_de(carpeta: str) -> dict:
    """Taxonomía en el formato del manifiesto de entrenamiento.

    Las carpetas que empiezan por '_' (cuarentena) no son un taxón: quedan sin
    etiqueta y marcadas para la selección manual posterior.
    """
    if carpeta.startswith("_"):
        return {
            "especie": None,
            "genero": None,
            "familia": None,
            "estado": "cuarentena_pendiente_seleccion_manual",
        }
    especie = canonico(carpeta)
    genero = genero_de(especie)
    return {
        "especie": especie,
        "genero": genero,
        "familia": GENERO_A_FAMILIA.get(genero),
        "estado": "catalogo" if especie in ESPECIES else "fuera_de_catalogo",
    }


def etapa_excluida(metadata: dict) -> str | None:
    texto = json.dumps(metadata, ensure_ascii=False).lower()
    for etapa in ETAPAS_EXCLUIDAS:
        if re.search(rf"(?<![a-z]){re.escape(etapa)}(?![a-z])", texto):
            return etapa
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", type=Path, default=Path(r"D:\Anura\data dirty"))
    parser.add_argument("--salida", type=Path, default=Path(r"D:\Anura\data cleaned"))
    args = parser.parse_args()

    if args.raiz.resolve() == args.salida.resolve():
        raise SystemExit("--salida debe ser distinta de --raiz")

    vistos: dict[str, str] = {}
    registros = []
    descartadas = []
    metadatos = cargar_metadatos(args.raiz)
    candidatos = sorted(
        ruta for ruta in args.raiz.rglob("*")
        if ruta.is_file() and ruta.suffix.lower() in EXTENSIONES and "sonidos" not in ruta.parts
    )

    for origen in candidatos:
        relativa = origen.relative_to(args.raiz)
        especie = relativa.parts[0]
        etapa = etapa_excluida(metadatos.get(origen.name, {}))
        if etapa:
            descartadas.append({
                "ruta": str(relativa).replace("\\", "/"),
                "motivo": f"etapa de vida excluida: {etapa}",
            })
            continue
        destino = args.salida / especie / f"{origen.stem}.jpg"
        resultado = convertir(origen, destino)
        if resultado is None:
            descartadas.append({
                "ruta": str(relativa).replace("\\", "/"),
                "motivo": "invalida, pequena o truncada",
            })
            continue
        digest, ancho, alto = resultado
        if digest in vistos:
            destino.unlink(missing_ok=True)
            descartadas.append({
                "ruta": str(relativa).replace("\\", "/"),
                "motivo": f"duplicado exacto de {vistos[digest]}",
            })
            continue
        ruta_limpia = str(destino.relative_to(args.salida)).replace("\\", "/")
        vistos[digest] = ruta_limpia
        taxonomia = taxonomia_de(especie)
        registros.append({
            "ruta": ruta_limpia,
            "especie": taxonomia["especie"],
            "genero": taxonomia["genero"],
            "familia": taxonomia["familia"],
            "estado": taxonomia["estado"],
            "ancho": ancho,
            "alto": alto,
            "sha256": digest,
        })

    args.salida.mkdir(parents=True, exist_ok=True)
    (args.salida / "dataset_limpio.json").write_text(
        json.dumps({"imagenes": registros, "descartadas": descartadas}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Imágenes revisadas: {len(candidatos)}")
    print(f"Imágenes listas: {len(registros)}")
    print(f"Descartadas/duplicadas: {len(descartadas)}")
    print(f"Etapas excluidas: {sum('etapa de vida excluida' in x['motivo'] for x in descartadas)}")
    print(f"Salida: {args.salida}")


if __name__ == "__main__":
    main()
