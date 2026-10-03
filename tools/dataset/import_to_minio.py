"""M1 — Sube el dataset limpio a MinIO y registra su procedencia en Postgres (esquema dataset).

Idempotente: se puede correr las veces que sea. Un objeto que ya existe en MinIO no se vuelve
a subir; las filas se insertan con ON CONFLICT. La clave en MinIO es el sha256 del archivo
(fotos/<sha[0:2]>/<sha256>.jpg): cambiar el nombre de una especie no mueve archivos.

Corre dentro de la red de docker-compose.server.yml (ver 19_ADMIN/Plan del Backend Real, M1):
  docker run --rm --network anura_anura-net --env-file D:/server/Anura/.env \
    -v "D:/Anura:/anura:ro" -v "D:/Anura/tools/dataset:/app:ro" python:3.12-slim \
    sh -c "pip install -q minio psycopg[binary] && python /app/import_to_minio.py"
"""

import csv
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import psycopg
from minio import Minio

ROOT = Path(os.environ.get("ANURA_ROOT", "/anura"))
CLEANED = ROOT / "data cleaned"
DIRTY = ROOT / "data dirty"
MANIFIESTO = ROOT / "training" / "manifiesto.json"
RECORDS = ROOT / "COLOMBIA_ANURA" / "ANTIOQUIA" / "occurrences" / "records_v1.csv"
CATALOG = ROOT / "COLOMBIA_ANURA" / "ANTIOQUIA" / "catalog" / "catalog_v1.json"
BUCKET = os.environ.get("DATASET_BUCKET", "anura-dataset")

OBS_RE = re.compile(r"obs_(\d+)")
PHOTO_RE = re.compile(r"photo_(\d+)")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def licencia_de(meta: dict) -> str | None:
    """iNaturalist deja license_code en null cuando la foto es "todos los derechos reservados":
    eso no es una licencia desconocida. NULL queda solo para fotos sin metadatos."""
    if not meta:
        return None
    return meta.get("license_code") or "all-rights-reserved"


def object_key(sha: str) -> str:
    return f"fotos/{sha[:2]}/{sha}.jpg"


def main() -> int:
    minio = Minio(
        f"{os.environ.get('MINIO_ENDPOINT', 'minio')}:{os.environ.get('MINIO_PORT', '9000')}",
        access_key=os.environ["MINIO_ROOT_USER"],
        secret_key=os.environ["MINIO_ROOT_PASSWORD"],
        secure=False,
    )
    if not minio.bucket_exists(BUCKET):
        minio.make_bucket(BUCKET)
        print(f"bucket {BUCKET} creado (privado)")

    limpio = json.loads((CLEANED / "dataset_limpio.json").read_text(encoding="utf-8"))
    imagenes, descartadas = limpio["imagenes"], limpio["descartadas"]

    catalogo = json.loads(CATALOG.read_text(encoding="utf-8"))["taxa"]
    taxon_por_nombre = {t["scientific_name"].strip().lower(): t["taxon_id"] for t in catalogo}

    meta = {}
    for f in DIRTY.glob("*/fotos_metadata.json"):
        for p in json.loads(f.read_text(encoding="utf-8")).get("photos", []):
            meta[p["file_name"]] = p

    coords = {}
    with open(RECORDS, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["source"] == "inaturalist" and r["latitude"] and r["longitude"]:
                coords[r["record_id"].split(":")[-1]] = r

    # 1) Hash real + subida, en paralelo. El sha256 declarado se verifica, no se confía.
    def subir(img):
        path = CLEANED / img["ruta"]
        if not path.exists():
            return img, None, "falta en disco"
        sha = sha256_file(path)
        key = object_key(sha)
        try:
            minio.stat_object(BUCKET, key)
            estado = "ya estaba"
        except Exception:
            minio.fput_object(BUCKET, key, str(path), content_type="image/jpeg")
            estado = "subida"
        return img, (sha, key, path.stat().st_size), estado

    resultados = []
    estados = Counter()
    with ThreadPoolExecutor(max_workers=8) as pool:
        for n, (img, info, estado) in enumerate(pool.map(subir, imagenes), 1):
            estados[estado] += 1
            resultados.append((img, info))
            if n % 1000 == 0:
                print(f"  {n}/{len(imagenes)} {dict(estados)}", flush=True)
    print("MinIO:", dict(estados))

    sha_distinto = sum(1 for img, info in resultados if info and info[0] != img["sha256"])
    ruta_a_sha = {img["ruta"]: info[0] for img, info in resultados if info}

    with psycopg.connect(os.environ["DATASET_DB_URL"]) as db, db.cursor() as cur:
        especie_id = {}
        for carpeta in sorted({i["especie"] for i in imagenes}):
            muestra = next(i for i in imagenes if i["especie"] == carpeta)
            nombre = carpeta.replace("_", " ")
            cur.execute(
                """INSERT INTO dataset.especie (carpeta, nombre_cientifico, genero, familia, taxon_id)
                   VALUES (%s, %s, %s, %s, %s)
                   ON CONFLICT (carpeta) DO UPDATE SET taxon_id = COALESCE(dataset.especie.taxon_id, EXCLUDED.taxon_id)
                   RETURNING id""",
                (carpeta, nombre, muestra["genero"], muestra["familia"], taxon_por_nombre.get(nombre.lower())),
            )
            especie_id[carpeta] = cur.fetchone()[0]

        obs_id = {}
        vistos = {}
        conflictos = 0
        for img, info in resultados:
            if not info:
                continue
            sha, key, size = info
            nombre = os.path.basename(img["ruta"])
            m_obs, m_photo = OBS_RE.search(nombre), PHOTO_RE.search(nombre)
            inat_obs = m_obs.group(1) if m_obs else None
            p = meta.get(nombre, {})

            oid = None
            if inat_obs:
                if inat_obs not in obs_id:
                    r = coords.get(inat_obs)
                    cur.execute(
                        """INSERT INTO dataset.observacion
                             (fuente, fuente_id, latitud, longitud, incertidumbre_m, coordenada_oculta,
                              coordenada_fuente, lugar, observada_en)
                           VALUES ('inaturalist', %s, %s, %s, %s, %s, %s, %s, %s)
                           ON CONFLICT (fuente, fuente_id) DO UPDATE SET
                             latitud = COALESCE(dataset.observacion.latitud, EXCLUDED.latitud),
                             longitud = COALESCE(dataset.observacion.longitud, EXCLUDED.longitud),
                             incertidumbre_m = COALESCE(dataset.observacion.incertidumbre_m, EXCLUDED.incertidumbre_m),
                             coordenada_fuente = COALESCE(dataset.observacion.coordenada_fuente, EXCLUDED.coordenada_fuente),
                             lugar = COALESCE(dataset.observacion.lugar, EXCLUDED.lugar),
                             observada_en = COALESCE(dataset.observacion.observada_en, EXCLUDED.observada_en)
                           RETURNING id""",
                        (
                            inat_obs,
                            float(r["latitude"]) if r else None,
                            float(r["longitude"]) if r else None,
                            float(r["uncertainty_m"]) if r and r["uncertainty_m"] else None,
                            (r["obscured"] == "True") if r else False,
                            "records_v1" if r else None,
                            p.get("place_guess"),
                            p.get("observed_on") or None,
                        ),
                    )
                    obs_id[inat_obs] = cur.fetchone()[0]
                oid = obs_id[inat_obs]

            if sha in vistos and vistos[sha] != img["especie"]:
                conflictos += 1
                print(f"  aviso: {sha[:12]} aparece en {vistos[sha]} y en {img['especie']}")
            vistos[sha] = img["especie"]

            cur.execute(
                """INSERT INTO dataset.foto
                     (sha256, object_key, especie_id, observacion_id, archivo_original, fuente_foto_id,
                      ancho, alto, bytes, licencia, atribucion, url_origen, estado, sha256_origen)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   ON CONFLICT (sha256) DO UPDATE SET sha256_origen = EXCLUDED.sha256_origen""",
                (
                    sha, key, especie_id[img["especie"]], oid, img["ruta"],
                    m_photo.group(1) if m_photo else None,
                    img.get("ancho"), img.get("alto"), size,
                    licencia_de(p), p.get("attribution"), p.get("url"),
                    img["estado"], img["sha256"],
                ),
            )

        for d in descartadas:
            cur.execute(
                """INSERT INTO dataset.exclusion (ruta_original, motivo)
                   VALUES (%s, %s)
                   ON CONFLICT (ruta_original, motivo) WHERE por IS NULL DO NOTHING""",
                (d["ruta"], d["motivo"]),
            )

        manifiesto_raw = MANIFIESTO.read_bytes()
        manifiesto = json.loads(manifiesto_raw.decode("utf-8"))
        cur.execute(
            """INSERT INTO dataset.version (nombre, descripcion, manifiesto_sha256, parametros)
               VALUES (%s, %s, %s, %s)
               ON CONFLICT (nombre) DO UPDATE SET manifiesto_sha256 = EXCLUDED.manifiesto_sha256
               RETURNING id""",
            (
                "v1 · manifiesto de entrenamiento",
                "Particiones con las que se entrenó encoder_anura (training/manifiesto.json).",
                hashlib.sha256(manifiesto_raw).hexdigest(),
                json.dumps(manifiesto["meta"], ensure_ascii=False),
            ),
        )
        version_id = cur.fetchone()[0]
        copias = defaultdict(Counter)
        for particion, filas in manifiesto["particiones"].items():
            for f in filas:
                copias[f["ruta"]][particion] += 1
        sin_foto = en_dos = 0
        for ruta, por_particion in copias.items():
            sha = ruta_a_sha.get(ruta)
            if not sha:
                sin_foto += 1
                continue
            if len(por_particion) > 1:
                en_dos += 1
            particion, n = por_particion.most_common(1)[0]
            cur.execute(
                """INSERT INTO dataset.version_foto (version_id, sha256, particion, copias)
                   VALUES (%s, %s, %s, %s)
                   ON CONFLICT (version_id, sha256) DO UPDATE SET particion = EXCLUDED.particion, copias = EXCLUDED.copias""",
                (version_id, sha, particion, n),
            )
        db.commit()

    # limpiar_dataset.py declara el sha256 del original descargado; el archivo limpio es un JPEG
    # recodificado. Si alguno coincide, esa foto no se recodificó.
    print(f"sha256 del original distinto del limpio (esperado): {sha_distinto}")
    print(f"misma foto en dos especies: {conflictos}")
    print(f"manifiesto: {len(copias)} rutas, sin foto subida {sin_foto}, en dos particiones {en_dos}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
