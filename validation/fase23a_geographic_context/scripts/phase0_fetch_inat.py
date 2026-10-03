#!/usr/bin/env python3
"""FASE 0 - Recupera coordenadas/elevacion/lugar de iNaturalist para obs_id de UNKNOWN y KNOWN."""
import json, time, re, sys
from pathlib import Path
import numpy as np
import requests

BASE = Path("D:/Anura")
OUT = BASE / "validation/fase23a_geographic_context"
CACHE = OUT / "cache/inat_observations_cache.json"

def load_cache():
    if CACHE.exists():
        try:
            return json.load(open(CACHE, encoding="utf-8"))
        except Exception as e:
            print(f"WARNING: cache file unreadable ({e}), starting fresh")
            return {}
    return {}

def collect_ids():
    ids = set()
    # UNKNOWN
    d = np.load(BASE / "validation/fase23a_open_set_automatic/embeddings/unknown_embeddings.npz", allow_pickle=True)
    for oid in d["observation_id"]:
        ids.add(str(oid))
    # KNOWN
    manifest = json.load(open(BASE / "validation/fase16_clean_open_set/clean_known_manifest.json", encoding="utf-8"))
    known_ids = set()
    for im in manifest["images"]:
        oid = im.get("observation_id")
        if oid and oid.startswith("OBS_"):
            known_ids.add(oid[4:])
    ids |= known_ids
    return sorted(ids, key=lambda x: int(x)), len(d["observation_id"]), len(known_ids)

def extract_record(res):
    if res is None:
        return None
    out = {"obscured": bool(res.get("obscured") or res.get("geoprivacy") in ("obscured", "private")),
           "place_guess": res.get("place_guess")}
    lat = lon = None
    geojson = res.get("geojson")
    if geojson and geojson.get("coordinates"):
        lon, lat = geojson["coordinates"][0], geojson["coordinates"][1]
    elif res.get("location"):
        parts = res["location"].split(",")
        if len(parts) == 2:
            lat, lon = float(parts[0]), float(parts[1])
    out["lat"] = lat
    out["lon"] = lon
    out["elevation_m"] = res.get("elevation")
    return out

def save_cache_atomic(cache):
    tmp = CACHE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)
    tmp.replace(CACHE)

def fetch_batches(ids, cache):
    todo = [i for i in ids if i not in cache]
    print(f"Total unique ids: {len(ids)}, already cached: {len(ids)-len(todo)}, to fetch: {len(todo)}", flush=True)
    batch = 200
    checkpoint_every = 5
    since_checkpoint = 0
    for start in range(0, len(todo), batch):
        chunk = todo[start:start+batch]
        url = "https://api.inaturalist.org/v1/observations"
        params = {"id": ",".join(chunk), "per_page": 200}
        try:
            r = requests.get(url, params=params, timeout=30)
            r.raise_for_status()
            js = r.json()
            got = {}
            for res in js.get("results", []):
                got[str(res["id"])] = extract_record(res)  # store EXTRACTED fields only, not raw payload
            for cid in chunk:
                cache[cid] = got.get(cid, None)
            print(f"  batch {start}-{start+len(chunk)}: got {len(got)}/{len(chunk)}", flush=True)
        except Exception as e:
            print(f"  ERROR batch {start}: {e}", flush=True)
            for cid in chunk:
                cache.setdefault(cid, None)
        since_checkpoint += 1
        if since_checkpoint >= checkpoint_every:
            save_cache_atomic(cache)
            since_checkpoint = 0
        time.sleep(1.1)
    save_cache_atomic(cache)
    return cache

def main():
    ids, n_unknown_rows, n_known_unique = collect_ids()
    cache = load_cache()
    cache = fetch_batches(ids, cache)

    extracted = {oid: cache.get(oid) for oid in ids}
    n_found = sum(1 for v in extracted.values() if v is not None)
    n_geo = sum(1 for v in extracted.values() if v and v["lat"] is not None)
    n_elev = sum(1 for v in extracted.values() if v and v.get("elevation_m") is not None)
    print(f"unique obs ids={len(ids)} found={n_found} with_geo={n_geo} with_elev={n_elev}")

    json.dump(extracted, open(OUT/"cache/inat_extracted.json","w",encoding="utf-8"), ensure_ascii=False, indent=0)
    summary = {"n_unique_ids": len(ids), "n_found": n_found, "n_with_geo": n_geo, "n_with_elev": n_elev,
               "n_unknown_image_rows": n_unknown_rows, "n_known_unique_obs": n_known_unique}
    json.dump(summary, open(OUT/"cache/fetch_summary.json","w",encoding="utf-8"), indent=2)

if __name__ == "__main__":
    main()
