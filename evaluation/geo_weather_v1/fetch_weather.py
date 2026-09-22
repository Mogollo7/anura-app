"""Paso 1 del prior de clima: resuelve fecha+coordenadas reales de cada observacion de
referencia/prueba (desde occurrences/records_v1.csv, sin scraping nuevo -- las fechas de
iNaturalist ya estaban en el CSV, solo nadie las habia unido a las imagenes) y consulta
temperatura/humedad historica via Open-Meteo (gratis, sin API key) con cache en disco.

Uso: python evaluation/geo_weather_v1/fetch_weather.py
"""
import json
import re
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(r"D:/Anura/pipeline_dataset")))
import pandas as pd
import paquetes_zonales as pz  # reuso seleccionar_referencias/constantes ya validadas

sys.stdout.reconfigure(line_buffering=True)

OUT = Path(__file__).parent
CACHE_PATH = OUT / "open_meteo_cache.json"
API = "https://archive-api.open-meteo.com/v1/archive"


def cargar_seleccion():
    dir_d = pz.RAIZ / "ANTIOQUIA"
    catalogo = json.loads((dir_d / "catalog" / "catalog_v1.json").read_text(encoding="utf-8"))
    guia = json.loads((pz.RAIZ / "taxonomy" / "taxonomy_guide.json").read_text(encoding="utf-8"))
    taxa = sorted(catalogo["taxa"], key=lambda t: t["taxon_id"])
    visuales = {t["taxon_id"] for t in taxa if t["visual_status"] == "VISUAL_ENABLED"}
    legado = {tid: guia[tid]["directory_legacy"] for tid in visuales}

    split = {}
    manifest = json.loads(pz.MANIFIESTO.read_text(encoding="utf-8"))
    for particion in ("train", "val", "test"):
        for e in manifest["particiones"][particion]:
            if not e.get("aumentada"):
                split[e["ruta"].replace("\\", "/")] = particion

    referencias, prueba = pz.seleccionar_referencias(visuales, legado, split)
    return referencias, prueba, dir_d


def cargar_lookup_fecha_coords(dir_d):
    recs = pd.read_csv(dir_d / "occurrences" / "records_v1.csv")
    inat = recs[recs["record_id"].str.startswith("inat:")].copy()
    inat["obs_id"] = inat["record_id"].str.replace("inat:", "", regex=False)
    inat = inat[inat["event"].astype(str).str.len() == 10]  # solo fecha dia-completo, no solo-año
    return inat.set_index("obs_id")[["latitude", "longitude", "event"]].to_dict("index")


def climakey(lat, lon, fecha):
    return f"{round(lat, 2)},{round(lon, 2)},{fecha}"


def _una_consulta(lat, lon, fecha):
    # subprocess a curl, no requests/urllib: en este entorno el stack de red de Python se
    # cuelga (>10 min sin error) tras un numero variable de llamadas, mientras que 40 llamadas
    # curl seguidas (proceso nuevo cada vez) fueron consistentes a ~750ms cada una.
    url = (
        f"{API}?latitude={lat}&longitude={lon}&start_date={fecha}&end_date={fecha}"
        "&daily=temperature_2m_mean,relative_humidity_2m_mean&timezone=auto"
    )
    resultado = subprocess.run(
        ["curl", "-s", "-m", "12", url], capture_output=True, text=True, timeout=15,
    )
    if resultado.returncode != 0 or not resultado.stdout:
        raise RuntimeError(f"curl exit={resultado.returncode} stderr={resultado.stderr[:200]}")
    payload = json.loads(resultado.stdout)
    daily = payload.get("daily", {})
    temp = (daily.get("temperature_2m_mean") or [None])[0]
    hum = (daily.get("relative_humidity_2m_mean") or [None])[0]
    return {"temp_c": temp, "humidity_pct": hum}


def consultar_clima(pares, cache):
    faltantes = [p for p in pares if climakey(*p) not in cache]
    print(f"pares de clima: {len(pares)}  en cache: {len(pares) - len(faltantes)}  a consultar: {len(faltantes)}", flush=True)
    t0 = time.time()
    for i, (lat, lon, fecha) in enumerate(faltantes):
        resultado = None
        for intento in range(3):
            try:
                resultado = _una_consulta(lat, lon, fecha)
                break
            except subprocess.TimeoutExpired:
                print(f"  TIMEOUT duro {lat},{lon},{fecha} intento={intento}", flush=True)
            except Exception as e:
                print(f"  ERROR {lat},{lon},{fecha}: {e}", flush=True)
                time.sleep(1)
        cache[climakey(lat, lon, fecha)] = resultado or {"temp_c": None, "humidity_pct": None}
        if (i + 1) % 20 == 0 or i + 1 == len(faltantes):
            elapsed = time.time() - t0
            print(f"  {i + 1}/{len(faltantes)}  ({elapsed:.0f}s, {elapsed / (i + 1):.2f}s/consulta)", flush=True)
            CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    return cache


def main():
    referencias, prueba, dir_d = cargar_seleccion()
    print(f"referencias={len(referencias)} prueba={len(prueba)}")
    lookup = cargar_lookup_fecha_coords(dir_d)

    def resolver(obs):
        if obs.startswith("manual:"):
            return None
        r = lookup.get(obs)
        if not r or pd_isna(r["latitude"]) or pd_isna(r["longitude"]):
            return None
        return float(r["latitude"]), float(r["longitude"]), r["event"]

    def pd_isna(v):
        return v is None or v != v  # NaN check sin importar pandas aqui

    ctx_ref = {obs: resolver(obs) for _, _, obs in referencias}
    ctx_test = {obs: resolver(obs) for _, _, obs in prueba}
    resueltas = {o: c for o, c in {**ctx_ref, **ctx_test}.items() if c is not None}
    print(f"observaciones con fecha+coords resueltas: {len(resueltas)}")

    pares = sorted({(c[0], c[1], c[2]) for c in resueltas.values()})
    cache = json.loads(CACHE_PATH.read_text(encoding="utf-8")) if CACHE_PATH.exists() else {}
    cache = consultar_clima(pares, cache)

    salida = {}
    for obs, (lat, lon, fecha) in resueltas.items():
        clima = cache.get(climakey(lat, lon, fecha), {})
        if clima.get("temp_c") is not None:
            salida[obs] = {"lat": lat, "lon": lon, "fecha": fecha, **clima}
    out_path = OUT / "obs_clima.json"
    out_path.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"observaciones con clima real resuelto: {len(salida)} -> {out_path}")


if __name__ == "__main__":
    main()
