import json, hashlib, os, datetime

BASE = r"D:\Anura\data\unknown_open_set_v2"
IMG_BASE = os.path.join(BASE, "images", "primary")

SPECIES = [
    {"name": "Scinax_rostratus", "sci_name": "Scinax rostratus", "taxon_id": 24292,
     "gbif_key": 5217865, "obs_file": os.path.join(BASE, "recovery_temp", "scinax_obs.json")},
    {"name": "Craugastor_metriosistus", "sci_name": "Craugastor metriosistus", "taxon_id": 517046,
     "gbif_key": 10819374, "obs_file": os.path.join(BASE, "recovery_temp", "craugastor_obs.json")},
]

manifest = []
for sp in SPECIES:
    obs_index = {}
    data = json.load(open(sp["obs_file"], encoding="utf-8"))
    for obs in data["results"]:
        obs_index[obs["id"]] = obs

    out_dir = os.path.join(IMG_BASE, sp["name"])
    if not os.path.isdir(out_dir):
        continue
    files = sorted(os.listdir(out_dir))
    for fn in files:
        base = fn.rsplit(".", 1)[0]
        parts = base.split("_")
        if len(parts) != 2:
            continue
        obs_id, photo_id = int(parts[0]), int(parts[1])
        obs = obs_index.get(obs_id)
        path = os.path.join(out_dir, fn)
        content = open(path, "rb").read()
        sha256 = hashlib.sha256(content).hexdigest()
        photo = next((p for p in obs.get("photos", []) if p["id"] == photo_id), None) if obs else None
        license_code = photo.get("license_code") if photo else None
        coords = obs.get("geojson", {}).get("coordinates") if obs and obs.get("geojson") else None
        manifest.append({
            "species": sp["sci_name"],
            "taxon_id": sp["taxon_id"],
            "gbif_taxon_key": sp["gbif_key"],
            "observation_id": obs_id,
            "photo_id": photo_id,
            "license": license_code,
            "original_url": (photo.get("url", "").replace("square", "medium")) if photo else None,
            "local_path": path,
            "sha256": sha256,
            "download_timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "quality_grade": obs.get("quality_grade") if obs else None,
            "coordinates": coords,
            "observed_on": obs.get("observed_on") if obs else None,
        })

manifest_path = os.path.join(BASE, "manifests", "download_manifest_ROUND2.json")
os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
json.dump(manifest, open(manifest_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("manifest entries:", len(manifest))
from collections import Counter
print(Counter(m["species"] for m in manifest))
