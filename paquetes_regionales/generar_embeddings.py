"""Generador de paquetes de embeddings para el módulo de descarga por zonas.

Toma imágenes organizadas por especie (mismo formato que `data dirty/<especie>/fotos/`)
y genera/actualiza un paquete SQLite (sqlite-vec) con: embedding 512-d + metadata
(especie, género, familia, ubicación) por cada foto de referencia.

Diseñado para CRECIMIENTO AUTOMÁTICO, no para una corrida única:
  - Re-ejecutable: identifica fotos por (especie, obs_id, photo_id) y SOLO
    procesa las que no están ya en el paquete. Agregar una especie nueva o
    más fotos de una existente = volver a correr el mismo comando.
  - Encoder desacoplado del paquete: se puede regenerar todo con un encoder
    mejor sin tocar el código, pasando --encoder distinto (zero-shot ahora,
    el extraído en Fase 6 en producción).
  - Taxonomía leída de `data dirty/arbol_taxonomico.json` (generado por el
    scraper), no de training/taxonomia.py — así cualquier especie que se
    scrapee (objetivo o auxiliar) queda con género/familia correctos sin
    tocar código cuando el catálogo crece.
  - Especies auxiliares y objetivo se codifican EXACTAMENTE igual aquí; la
    app decide después (fuera de este script) cuáles mostrar como resultado
    identificable — este paquete no distingue una cosa de otra.

Uso:
    # Validar el pipeline end-to-end con BioCLIP zero-shot (antes de tener
    # el encoder final de Fase 6 — sirve para probar que todo funciona)
    python paquetes_regionales/generar_embeddings.py --encoder zero-shot

    # Producción, con el encoder ya extraído y afinado (Fase 6)
    python paquetes_regionales/generar_embeddings.py --encoder bioclip/checkpoints/encoder_final.pt

    # Crecimiento incremental: solo una especie que se agregó después
    python paquetes_regionales/generar_embeddings.py --encoder zero-shot --especies "Boana_platanera"
"""

import argparse
import io
import json
import sqlite3
import sys
from pathlib import Path

import numpy as np
import open_clip
import sqlite_vec
import torch
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)

RAIZ_DATOS = Path(r"D:\Anura\data dirty")
ARBOL_TAXONOMICO = RAIZ_DATOS / "arbol_taxonomico.json"
SALIDA_DEFECTO = Path(r"D:\Anura\paquetes_regionales\paquete_nacional.sqlite")
MODELO_HF = "hf-hub:imageomics/bioclip"
DIM_EMBEDDING = 512
EXTENSIONES = {".jpg", ".jpeg", ".png"}


# ─── Taxonomía dinámica (crece sola con lo que haya sido scrapeado) ────────

def cargar_taxonomia_dinamica() -> dict[str, dict]:
    """especie (con espacio, ej 'Boana platanera') -> {familia, genero}.

    Lee arbol_taxonomico.json, que el scraper regenera cada vez que se
    agregan especies nuevas — así este script nunca necesita un mapeo
    hardcodeado que se quede corto cuando el catálogo crece.
    """
    if not ARBOL_TAXONOMICO.exists():
        raise FileNotFoundError(
            f"No existe {ARBOL_TAXONOMICO}. Corre scraper_inaturalist.py primero."
        )
    arbol = json.loads(ARBOL_TAXONOMICO.read_text(encoding="utf-8"))
    mapeo = {}
    for familia_nombre, familia in arbol.get("families", {}).items():
        for genero_nombre, genero in familia.get("genera", {}).items():
            for especie in genero.get("species", []):
                nombre = especie.get("scientific_name")
                if nombre:
                    mapeo[nombre] = {"familia": familia_nombre, "genero": genero_nombre}
    return mapeo


# ─── Encoder desacoplado (zero-shot o checkpoint entrenado) ────────────────

def cargar_encoder(spec: str, dispositivo: str):
    """spec == 'zero-shot' -> BioCLIP original sin modificar.
    spec == ruta a .pt -> carga visual_state_dict del checkpoint de Fase 4/6.
    """
    modelo_clip, _, preprocess = open_clip.create_model_and_transforms(MODELO_HF)
    visual = modelo_clip.visual

    if spec != "zero-shot":
        ruta_checkpoint = Path(spec)
        if not ruta_checkpoint.exists():
            raise FileNotFoundError(f"Checkpoint no encontrado: {ruta_checkpoint}")
        checkpoint = torch.load(ruta_checkpoint, map_location=dispositivo, weights_only=False)
        estado = checkpoint.get("visual_state_dict", checkpoint)
        visual.load_state_dict(estado)
        print(f"  Encoder cargado desde checkpoint: {ruta_checkpoint} (época {checkpoint.get('epoca', '?')})")
    else:
        print("  Encoder: BioCLIP v1 zero-shot (sin fine-tuning)")

    return visual.to(dispositivo).eval(), preprocess


# ─── Descubrimiento de imágenes + metadata de ubicación ────────────────────

def cargar_coordenadas_por_foto(especie_dir: Path) -> dict[str, dict]:
    """photo filename -> {lat, lng, departamento_guess} si hay coordenadas."""
    ruta_coords = especie_dir / "coordenadas_distribucion.json"
    ruta_fotos_meta = especie_dir / "fotos_metadata.json"
    if not ruta_coords.exists() or not ruta_fotos_meta.exists():
        return {}

    coords_por_obs = {}
    for c in json.loads(ruta_coords.read_text(encoding="utf-8")):
        obs_id = c.get("observation_id")
        if obs_id is not None:
            coords_por_obs[obs_id] = c

    resultado = {}
    for p in json.loads(ruta_fotos_meta.read_text(encoding="utf-8")).get("photos", []):
        obs_id = p.get("observation_id")
        c = coords_por_obs.get(obs_id)
        if c:
            resultado[p["file_name"]] = {
                "latitud": c.get("latitude"),
                "longitud": c.get("longitude"),
                "lugar_texto": c.get("place_guess", ""),
            }
    return resultado


def descubrir_especies(filtro: list[str] | None) -> list[Path]:
    if filtro:
        return [RAIZ_DATOS / e for e in filtro if (RAIZ_DATOS / e).is_dir()]
    return sorted(p for p in RAIZ_DATOS.iterdir() if p.is_dir() and (p / "fotos").is_dir())


# ─── Base de datos sqlite-vec (crecimiento incremental) ────────────────────

def conectar_paquete(ruta: Path) -> sqlite3.Connection:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(ruta))
    con.enable_load_extension(True)
    sqlite_vec.load(con)
    con.enable_load_extension(False)

    con.execute(f"""
        CREATE VIRTUAL TABLE IF NOT EXISTS embeddings USING vec0(
            embedding float[{DIM_EMBEDDING}]
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            id INTEGER PRIMARY KEY,
            especie TEXT NOT NULL,
            genero TEXT,
            familia TEXT,
            archivo TEXT NOT NULL,
            clave_unica TEXT NOT NULL UNIQUE,
            latitud REAL,
            longitud REAL,
            lugar_texto TEXT,
            encoder_usado TEXT
        )
    """)
    con.commit()
    return con


def fotos_ya_procesadas(con: sqlite3.Connection) -> set[str]:
    return {row[0] for row in con.execute("SELECT clave_unica FROM metadata")}


# ─── Pipeline principal ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--encoder", default="zero-shot", help="'zero-shot' o ruta a checkpoint .pt de Fase 4/6")
    parser.add_argument("--salida", type=Path, default=SALIDA_DEFECTO)
    parser.add_argument("--especies", nargs="*", default=None, help="Subconjunto a procesar (nombres de carpeta, ej: Boana_platanera). Omitir = todas.")
    args = parser.parse_args()

    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"{'='*70}\nGENERADOR DE PAQUETES DE EMBEDDINGS (crecimiento automático)\n{'='*70}")
    print(f"Dispositivo: {dispositivo}")
    print(f"Paquete de salida: {args.salida}")

    taxonomia = cargar_taxonomia_dinamica()
    print(f"Taxonomía dinámica: {len(taxonomia)} especies conocidas en arbol_taxonomico.json")

    visual, preprocess = cargar_encoder(args.encoder, dispositivo)
    con = conectar_paquete(args.salida)
    ya_procesadas = fotos_ya_procesadas(con)
    print(f"Fotos ya en el paquete (se omiten): {len(ya_procesadas)}")

    especies_dirs = descubrir_especies(args.especies)
    print(f"Especies a revisar: {len(especies_dirs)}\n")

    total_nuevas = 0
    total_omitidas = 0
    total_sin_taxonomia = 0

    for especie_dir in especies_dirs:
        especie_slug = especie_dir.name
        especie_nombre = especie_slug.replace("_", " ")
        info_tax = taxonomia.get(especie_nombre)
        if not info_tax:
            print(f"[!] {especie_nombre}: sin entrada en arbol_taxonomico.json, se omite")
            total_sin_taxonomia += 1
            continue

        coords_por_foto = cargar_coordenadas_por_foto(especie_dir)
        fotos_dir = especie_dir / "fotos"
        imagenes = sorted(
            p for p in fotos_dir.iterdir()
            if p.is_file() and p.suffix.lower() in EXTENSIONES
        )

        nuevas_en_especie = 0
        filas_pendientes = []
        embeddings_pendientes = []

        for img_path in imagenes:
            clave_unica = f"{especie_slug}::{img_path.name}"
            if clave_unica in ya_procesadas:
                total_omitidas += 1
                continue

            try:
                with Image.open(img_path).convert("RGB") as img:
                    tensor = preprocess(img).unsqueeze(0).to(dispositivo)
                with torch.no_grad():
                    emb = visual(tensor)
                    emb = emb / emb.norm(dim=-1, keepdim=True)
                embeddings_pendientes.append(emb.cpu().numpy()[0])

                loc = coords_por_foto.get(img_path.name, {})
                filas_pendientes.append((
                    especie_nombre, info_tax["genero"], info_tax["familia"],
                    img_path.name, clave_unica,
                    loc.get("latitud"), loc.get("longitud"), loc.get("lugar_texto"),
                    args.encoder,
                ))
                nuevas_en_especie += 1
            except Exception as exc:
                print(f"  [ERROR] {img_path.name}: {exc}")

        if nuevas_en_especie:
            for fila, emb in zip(filas_pendientes, embeddings_pendientes):
                cursor = con.execute(
                    "INSERT INTO metadata (especie, genero, familia, archivo, clave_unica, latitud, longitud, lugar_texto, encoder_usado) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    fila,
                )
                con.execute(
                    "INSERT INTO embeddings (rowid, embedding) VALUES (?, ?)",
                    (cursor.lastrowid, emb.astype(np.float32).tobytes()),
                )
            con.commit()
            print(f"[+] {especie_nombre}: {nuevas_en_especie} embeddings nuevos ({info_tax['genero']}/{info_tax['familia']})")
            total_nuevas += nuevas_en_especie

    print(f"\n{'='*70}")
    print(f"RESUMEN")
    print(f"{'='*70}")
    print(f"  Embeddings nuevos agregados:  {total_nuevas}")
    print(f"  Ya existentes (omitidas):     {total_omitidas}")
    print(f"  Especies sin taxonomía:       {total_sin_taxonomia}")
    total_en_paquete = con.execute("SELECT COUNT(*) FROM metadata").fetchone()[0]
    print(f"  Total en el paquete ahora:    {total_en_paquete}")
    print(f"\n✅ Paquete actualizado: {args.salida}")
    print("   Volver a correr este mismo comando cuando lleguen fotos/especies nuevas — no reprocesa lo existente.")

    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
