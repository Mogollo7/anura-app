"""M1 — Rellena la coordenada de las observaciones del dataset que no la tienen, desde la API
pública de iNaturalist (200 observaciones por consulta, una consulta por segundo).

Solo toca filas con latitud NULL: lo que vino de records_v1 no se reemplaza. Si iNaturalist
oculta la coordenada (geoprivacidad o especie amenazada), se guarda la que publica —ya
desplazada por ellos— con coordenada_oculta = TRUE, para que la capa de altitud la trate
distinto. Observaciones borradas o privadas quedan sin coordenada y se cuentan al final.

Corre como import_to_minio.py, en la red del servidor:
  docker run --rm --network anura_anura-net --env-file D:/server/Anura/.env \
    -v "D:/Anura:/anura:ro" python:3.12-slim \
    sh -c "pip install -q 'psycopg[binary]' && python /anura/tools/dataset/backfill_inaturalist.py"
"""

import json
import os
import sys
import time
import urllib.request

import psycopg

API = "https://api.inaturalist.org/v1/observations"
LOTE = 200
USER_AGENT = "ANURA-dataset-backfill/1.0 (anura.juanlabs.me)"


def consultar(ids):
    url = f"{API}?id={','.join(ids)}&per_page={LOTE}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    for intento in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as res:
                return json.loads(res.read().decode("utf-8"))["results"]
        except Exception as err:  # red o 429: espera y reintenta
            espera = 5 * (intento + 1)
            print(f"  consulta falló ({err}); reintento en {espera}s", flush=True)
            time.sleep(espera)
    raise RuntimeError("iNaturalist no respondió tras 4 intentos")


def main() -> int:
    with psycopg.connect(os.environ["DATASET_DB_URL"]) as db, db.cursor() as cur:
        cur.execute(
            """SELECT fuente_id FROM dataset.observacion
               WHERE fuente = 'inaturalist' AND latitud IS NULL AND fuente_id IS NOT NULL
               ORDER BY id"""
        )
        pendientes = [r[0] for r in cur.fetchall()]
        print(f"observaciones sin coordenada: {len(pendientes)}", flush=True)

        con = ocultas = 0
        for i in range(0, len(pendientes), LOTE):
            lote = pendientes[i : i + LOTE]
            for r in consultar(lote):
                geo = r.get("geojson") or {}
                c = geo.get("coordinates")
                if not c:
                    continue
                oculta = bool(r.get("obscured")) or r.get("geoprivacy") in ("obscured", "private") \
                    or r.get("taxon_geoprivacy") in ("obscured", "private")
                cur.execute(
                    """UPDATE dataset.observacion
                       SET latitud = %s, longitud = %s, incertidumbre_m = %s,
                           coordenada_oculta = %s, coordenada_fuente = 'inaturalist_api',
                           lugar = COALESCE(lugar, %s), observada_en = COALESCE(observada_en, %s)
                       WHERE fuente = 'inaturalist' AND fuente_id = %s AND latitud IS NULL""",
                    (c[1], c[0], r.get("positional_accuracy"), oculta,
                     r.get("place_guess"), r.get("observed_on"), str(r["id"])),
                )
                con += cur.rowcount
                ocultas += cur.rowcount if oculta else 0
            db.commit()
            print(f"  {min(i + LOTE, len(pendientes))}/{len(pendientes)} · con coordenada {con} · ocultas {ocultas}", flush=True)
            time.sleep(1.1)

    print(f"listo: {con} con coordenada ({ocultas} ocultas por iNaturalist), {len(pendientes) - con} sin respuesta")
    return 0


if __name__ == "__main__":
    sys.exit(main())
