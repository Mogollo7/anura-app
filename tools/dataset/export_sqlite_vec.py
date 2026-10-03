"""
Exporta los vectores de pgvector (dataset.embedding, M2) a un SQLite con la misma tabla
`vec_references` que usan los paquetes del teléfono (pipeline_dataset/paquetes_zonales.py y
PackageVectorIndex.kt): vec0(taxon_id TEXT, embedding FLOAT[512] distance_metric=cosine),
blob float32 little-endian, sqlite-vec 0.1.9.

No arma un paquete (eso es M4: qué fotos, centroides, zonas, priors). Sirve para comprobar que
los vectores del servidor pasan al formato del teléfono sin conversiones, y como base del
compilador.

Corre en un contenedor temporal dentro de la red del servidor (Postgres no se expone):

  MSYS_NO_PATHCONV=1 docker run --rm --network anura_anura-net --env-file D:/server/Anura/.env \
    -v "D:/Anura:/anura" python:3.12-slim sh -c \
    "pip install -q 'psycopg[binary]' sqlite-vec==0.1.9 numpy && \
     python /anura/tools/dataset/export_sqlite_vec.py --out /anura/tools/dataset/salida/vectores.sqlite"
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sqlite3
import struct
import sys
from pathlib import Path

import numpy as np
import psycopg
import sqlite_vec

DIM = 512


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--encoder", help="sha256 del encoder; por defecto el único registrado")
    ap.add_argument("--solo-manifiesto", action="store_true", help="solo fotos de la última versión del manifiesto")
    args = ap.parse_args()

    url = os.environ.get("DATASET_DB_URL") or os.environ["DATABASE_URL"]
    with psycopg.connect(url) as pg:
        encoders = [r[0] for r in pg.execute("SELECT sha256 FROM dataset.encoder ORDER BY registrado")]
        encoder = args.encoder or (encoders[-1] if encoders else None)
        if encoder not in encoders:
            print(f"Encoder no registrado: {encoder}", file=sys.stderr)
            return 1
        filtro = """AND EXISTS (SELECT 1 FROM dataset.version_foto vf WHERE vf.sha256 = f.sha256
                      AND vf.version_id = (SELECT MAX(id) FROM dataset.version))""" if args.solo_manifiesto else ""
        # vector::real[] = float4 tal cual lo guarda pgvector: ni redondeo ni cambio de precisión.
        filas = pg.execute(f"""
            SELECT e.sha256, COALESCE(s.taxon_id, 'CARPETA:' || s.carpeta), o.fuente, o.fuente_id,
                   f.licencia, f.atribucion, e.vector::real[]
            FROM dataset.embedding e
            JOIN dataset.foto f ON f.sha256 = e.sha256
            JOIN dataset.especie s ON s.id = f.especie_id
            LEFT JOIN dataset.observacion o ON o.id = f.observacion_id
            WHERE e.encoder_sha256 = %s
              AND NOT EXISTS (SELECT 1 FROM dataset.exclusion x WHERE x.sha256 = f.sha256 AND x.revertida IS NULL)
              {filtro}
            ORDER BY e.sha256""", (encoder,)).fetchall()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.unlink(missing_ok=True)
    conn = sqlite3.connect(out)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.executescript(f"""
        CREATE TABLE reference_images (
            ref_id INTEGER PRIMARY KEY,
            source_record_id TEXT,
            license_code TEXT NOT NULL,
            attribution TEXT NOT NULL,
            sha256 TEXT NOT NULL
        );
        CREATE VIRTUAL TABLE vec_references USING vec0(
            taxon_id TEXT,
            embedding FLOAT[{DIM}] distance_metric=cosine
        );
        CREATE TABLE export_info (key TEXT PRIMARY KEY, value TEXT NOT NULL);
    """)
    h = hashlib.sha256()
    for ref_id, (sha, taxon, fuente, fuente_id, lic, attr, vec) in enumerate(filas, start=1):
        v = np.asarray(vec, dtype="<f4")
        assert v.shape == (DIM,), v.shape
        blob = v.tobytes()  # == struct.pack("512f", …) en x86, como paquetes_zonales.py
        origen = f"inat:{fuente_id}" if fuente == "inaturalist" and fuente_id else fuente or ""
        conn.execute("INSERT INTO reference_images VALUES (?,?,?,?,?)", (ref_id, origen, lic or "", attr or "", sha))
        conn.execute("INSERT INTO vec_references(rowid, taxon_id, embedding) VALUES (?,?,?)", (ref_id, taxon, blob))
        h.update(ref_id.to_bytes(4, "little") + taxon.encode() + blob)
    info = {"encoder_sha256": encoder, "vectores": str(len(filas)), "vec_references_sha256": h.hexdigest(),
            "vec_version": conn.execute("select vec_version()").fetchone()[0]}
    conn.executemany("INSERT INTO export_info VALUES (?,?)", info.items())
    conn.commit()

    # Comprobación: cada vector debe encontrarse a sí mismo a distancia ~0 (lo mismo que hace el teléfono).
    muestra = conn.execute("SELECT rowid, embedding FROM vec_references ORDER BY rowid LIMIT 200").fetchall()
    fallos = 0
    for rowid, blob in muestra:
        top = conn.execute("SELECT rowid, distance FROM vec_references WHERE embedding MATCH ? AND k = 1", (blob,)).fetchone()
        fallos += not (top[0] == rowid or top[1] < 1e-6)
    # Y el blob leído de sqlite-vec es idéntico, bit a bit, al float4 de pgvector.
    primero = struct.unpack(f"{DIM}f", muestra[0][1]) if muestra else ()
    igual = bool(filas) and np.array_equal(np.asarray(primero, "<f4"), np.asarray(filas[0][6], "<f4"))
    conn.close()
    print({**info, "autocoincidencias_fallidas": fallos, "muestra": len(muestra), "blob_identico_a_pgvector": igual,
           "archivo": str(out), "mb": round(out.stat().st_size / 1e6, 1)})
    return 0 if fallos == 0 and igual else 1


if __name__ == "__main__":
    sys.exit(main())
