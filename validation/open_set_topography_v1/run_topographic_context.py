"""Frozen topographic-context experiment; source artifacts are read-only."""
from __future__ import annotations

import hashlib
import json
import math
import re
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(r"D:\Anura")
OUT = Path(__file__).resolve().parent
CAL_MANIFEST = ROOT / "validation/fase18_clean_calibration/calibration_manifest.json"
CLEAN_KNOWN = ROOT / "validation/fase16_clean_open_set/clean_known_embeddings.npz"
F23 = ROOT / "validation/fase23a_open_set_automatic/embeddings/unknown_embeddings.npz"
TRAIN = ROOT / "evaluation/fase13/embeddings/train_embeddings.npz"
AUDIT = ROOT / "bioclip/evaluation/coordenadas_auditoria.json"
UNKNOWN_DOWNLOAD = ROOT / "data/unknown_open_set_v2/manifests/download_manifest.json"
UNKNOWN_FINAL = ROOT / "data/unknown_open_set_v2/images/final"
UNKNOWN_SPECIES = {"Hyloxalus_picachos", "Dendropsophus_minutus", "Pristimantis_w_nigrum", "Sachatamia_electrops"}
VISUAL_SUMMARY = ROOT / "validation/open_set_calibration_v1/summary.json"
API, INTERPOLATION = "https://api.opentopodata.org/v1/srtm30m", "bilinear"
RADIUS_METERS, BATCH, MIN_TRAIN_LOCALITIES, TARGET_FAR = 90.0, 100, 10, 0.05


def dump(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
def obs_id(value): return str(value).removeprefix("OBS_")
def path_obs(value):
    match = re.search(r"col_obs_([0-9]+)_", str(value))
    return match.group(1) if match else None
def ckey(lat, lon): return f"{lat:.7f},{lon:.7f}"


def sources():
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))["coordenadas_limpias"]
    result = {obs_id(x["observation_id"]): {"lat": float(x["lat"]), "lon": float(x["lon"]), "source": "coordinate_audit", "accuracy_m": x.get("accuracy_m")} for x in audit}
    for x in json.loads(UNKNOWN_DOWNLOAD.read_text(encoding="utf-8"))["downloaded"]:
        result.setdefault(str(x["observation_id"]), {"lat": float(x["latitude"]), "lon": float(x["longitude"]), "source": "unknown_download_manifest", "accuracy_m": None})
    return result


def offsets(lat, lon):
    dlat = RADIUS_METERS / 111320.0
    dlon = RADIUS_METERS / max(111320.0 * math.cos(math.radians(lat)), 1.0)
    return [(lat, lon), (lat + dlat, lon), (lat - dlat, lon), (lat, lon + dlon), (lat, lon - dlon)]


def elevations(points):
    cache_path = OUT / "opentopodata_cache.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    needed = [(lat, lon) for lat, lon in points if ckey(lat, lon) not in cache]
    for start in range(0, len(needed), BATCH):
        chunk = needed[start:start + BATCH]
        locations = "|".join(f"{lat:.7f},{lon:.7f}" for lat, lon in chunk)
        url = API + "?" + urllib.parse.urlencode({"locations": locations, "interpolation": INTERPOLATION, "nodata_value": "null"})
        request = urllib.request.Request(url, headers={"User-Agent": "ANURA-topography-validation/1.0"})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=45) as response: payload = json.loads(response.read().decode("utf-8"))
                if payload.get("status") != "OK" or len(payload.get("results", [])) != len(chunk): raise RuntimeError("invalid OpenTopoData response")
                for point, row in zip(chunk, payload["results"]): cache[ckey(*point)] = {"elevation_m": row.get("elevation"), "dataset": row.get("dataset")}
                break
            except Exception:
                if attempt == 2: raise
                time.sleep(2 ** attempt)
        dump(cache_path, cache)
        print(f"[opentopodata] {min(start + len(chunk), len(needed))}/{len(needed)} new points", flush=True)
        if start + BATCH < len(needed): time.sleep(1.05)
    return cache


def vector(coord, cache):
    vals = [cache.get(ckey(a, b), {}).get("elevation_m") for a, b in offsets(float(coord["lat"]), float(coord["lon"]))]
    if any(v is None for v in vals): return None
    centre, north, south, east, west = map(float, vals)
    dx, dy = (east - west) / (2 * RADIUS_METERS), (north - south) / (2 * RADIUS_METERS)
    aspect = math.atan2(dx, dy)
    return np.array([float(coord["lat"]), float(coord["lon"]), centre, math.degrees(math.atan(math.hypot(dx, dy))), math.sin(aspect), math.cos(aspect), max(vals) - min(vals), float(np.std(vals))])


def train_rows(coords):
    data, seen, rows = np.load(TRAIN, allow_pickle=True), set(), []
    for species, path in zip(data["species"], data["paths"]):
        oid = path_obs(path); key = (str(species), oid)
        if oid is not None and oid in coords and key not in seen:
            seen.add(key); rows.append({"species": str(species), "observation_id": oid, "coord": coords[oid]})
    return rows


def calibration_rows(coords):
    manifest = json.loads(CAL_MANIFEST.read_text(encoding="utf-8"))["known"]
    clean = np.load(CLEAN_KNOWN, allow_pickle=True); indices = {str(x): i for i, x in enumerate(clean["image_ids"])}
    known = [{"species": x["scientific_name"], "observation_id": obs_id(x["observation_id"]), "coord": coords.get(obs_id(x["observation_id"])), "image_id": x["image_id"]} for x in manifest]
    unknown = []
    for p in sorted(UNKNOWN_FINAL.rglob("*")):
        if p.suffix.lower() in {".jpg", ".jpeg", ".png"} and p.parent.name in UNKNOWN_SPECIES:
            oid = path_obs(p.name); unknown.append({"species": p.parent.name.replace("_", " "), "observation_id": oid, "coord": coords.get(oid) if oid else None, "path": str(p)})
    saved = np.load(ROOT / "validation/open_set_calibration_v1/supplementary_unknown_embeddings.npz", allow_pickle=True)
    path_index = {str(x): i for i, x in enumerate(saved["paths"])}
    return known, unknown, clean["embeddings"][[indices[str(x["image_id"])] for x in manifest]].astype(np.float32), saved["embeddings"][[path_index[x["path"]] for x in unknown]].astype(np.float32)


def blind_rows(coords):
    data = np.load(F23, allow_pickle=True)
    rows = [{"species": str(s).replace("_", " "), "observation_id": str(o), "coord": coords.get(str(o)), "path": str(p)} for s, o, p in zip(data["species"], data["observation_id"], data["paths"])]
    return rows, data["embeddings"].astype(np.float32)


def visual(kx, ux, bx):
    import sys
    sys.path.insert(0, str(ROOT / "validation/open_set_calibration_v1"))
    from run_protocol import build_centroids, multiple_prototype_centers, prototype_features
    centers, names, samples, dispersion = build_centroids(); protos, labels = multiple_prototype_centers(samples, names)
    return tuple(prototype_features(x, protos, labels, names, dispersion) for x in (kx, ux, bx))


def visual_accept(f):
    p = json.loads(VISUAL_SUMMARY.read_text(encoding="utf-8"))["frozen"]["parameters"]
    return (f["d1"] <= p["distance_threshold"]) & (f["margin"] >= p["margin_threshold"])


def profiles(train, vectors):
    groups = defaultdict(list)
    for row, vec in zip(train, vectors):
        if vec is not None: groups[row["species"]].append(vec)
    output = {}
    floor = np.array([0.01, 0.01, 30, 2, .1, .1, 10, 5])
    for species, values in groups.items():
        data = np.asarray(values)
        if len(data) >= MIN_TRAIN_LOCALITIES:
            centre = np.median(data, axis=0); scale = np.maximum(np.median(np.abs(data - centre), axis=0) * 1.4826, floor)
            output[species] = {"centre": centre, "scale": scale, "n_localities": len(data)}
    return output


def distances(feature, vectors, fitted):
    out = np.full(len(vectors), np.nan)
    for i, (species, vec) in enumerate(zip(feature["selected"], vectors)):
        p = fitted.get(str(species))
        if vec is not None and p is not None: out[i] = float(np.sqrt(np.square((vec - p["centre"]) / p["scale"]).sum()))
    return out


def score(known, unknown):
    far, kar = float(unknown.mean()), float(known.mean())
    return {"far": far, "udr": 1-far, "kar": kar, "frr": 1-kar, "balanced_accuracy": ((1-far)+kar)/2, "known_accepted": int(known.sum()), "unknown_false_accepted": int(unknown.sum())}


def choose(kv, uv, kd, ud):
    grid = np.unique(np.quantile(np.concatenate([kd[np.isfinite(kd)], ud[np.isfinite(ud)]]), np.linspace(0, 1, 201)))
    best = None
    for threshold in grid:
        ka, ua = kv & (~np.isfinite(kd) | (kd <= threshold)), uv & (~np.isfinite(ud) | (ud <= threshold))
        result = score(ka, ua); candidate = (result["far"] <= TARGET_FAR, result["kar"], -result["far"])
        if best is None or candidate > best[0]: best = (candidate, float(threshold), result)
    return best[1], best[2]


def main():
    coords = sources(); train = train_rows(coords); known, unknown, kx, ux = calibration_rows(coords); blind, bx = blind_rows(coords)
    points = {}
    for row in train + known + unknown + blind:
        if row.get("coord"):
            for point in offsets(float(row["coord"]["lat"]), float(row["coord"]["lon"])): points.setdefault(ckey(*point), point)
    cache = elevations(list(points.values()))
    tv = [vector(r["coord"], cache) for r in train]
    kv = [vector(r["coord"], cache) if r["coord"] else None for r in known]
    uv = [vector(r["coord"], cache) if r["coord"] else None for r in unknown]
    bv = [vector(r["coord"], cache) if r["coord"] else None for r in blind]
    fitted = profiles(train, tv); kf, uf, bf = visual(kx, ux, bx); ka0, ua0, ba0 = map(visual_accept, (kf, uf, bf))
    kd, ud, bd = distances(kf, kv, fitted), distances(uf, uv, fitted), distances(bf, bv, fitted)
    threshold, cal_context = choose(ka0, ua0, kd, ud)
    ka, ua, ba = ka0 & (~np.isfinite(kd) | (kd <= threshold)), ua0 & (~np.isfinite(ud) | (ud <= threshold)), ba0 & (~np.isfinite(bd) | (bd <= threshold))
    covered = np.isfinite(bd)
    false = [{"index": int(i), "true_species_evaluation_only": blind[i]["species"], "predicted_species": str(bf["selected"][i]), "observation_id": blind[i]["observation_id"], "topographic_distance": None if not np.isfinite(bd[i]) else float(bd[i]), "topographic_context_available": bool(covered[i]), "visual_d1": float(bf["d1"][i]), "margin": float(bf["margin"][i])} for i in np.flatnonzero(ba)]
    dump(OUT / "fase23a_false_accepts_context_frozen.json", false)
    result = {"method": "frozen_visual_k2_margin + train_only_topographic_habitat_envelope", "opentopodata": {"endpoint": API, "dataset": "srtm30m", "interpolation": INTERPOLATION, "radius_m": RADIUS_METERS, "cache_sha256": hashlib.sha256((OUT / "opentopodata_cache.json").read_bytes()).hexdigest()}, "profile": {"features": ["latitude", "longitude", "elevation_m", "slope_deg", "aspect_sin", "aspect_cos", "local_relief_m", "roughness_m"], "source_split": "Fase13 TRAIN only", "minimum_train_localities": MIN_TRAIN_LOCALITIES, "profiles_enabled": len(fitted), "train_localities_total": len(train)}, "coverage": {"calibration_known_images": {"total": len(known), "topography": int(np.isfinite(kd).sum())}, "calibration_unknown_images": {"total": len(unknown), "topography": int(np.isfinite(ud).sum())}, "fase23a_blind_images": {"total": len(blind), "topography": int(covered.sum()), "without_context": int((~covered).sum())}}, "freeze": {"visual_method": "F_multiple_prototypes_k2_margin", "topographic_distance_threshold": threshold, "selection": "max calibration KAR subject to calibration FAR <= 5%; Fase23A excluded"}, "calibration": {"visual_only": score(ka0, ua0), "visual_plus_topography": cal_context}, "fase23a_blind": {"visual_only_all": score(ba0, ba0), "visual_plus_topography_all": score(ba, ba), "visual_only_covered": score(ba0[covered], ba0[covered]), "visual_plus_topography_covered": score(ba[covered], ba[covered]), "accepted_by_true_species_evaluation_only": dict(Counter(str(blind[i]["species"]) for i in np.flatnonzero(ba))), "accepted_by_predicted_catalog_species": dict(Counter(str(bf["selected"][i]) for i in np.flatnonzero(ba)))}, "invariants": {"encoder_weights_modified": False, "source_embeddings_modified": False, "fase23a_used_for_selection": False, "missing_coordinate_does_not_reject": True, "context_cannot_accept_visual_rejection": True}}
    dump(OUT / "summary.json", result); print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__": main()
