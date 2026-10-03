import json, hashlib, os, time, urllib.request, datetime, sys

BASE = r"D:\Anura\data\unknown_open_set_v2"
IMG_BASE = os.path.join(BASE, "images", "primary")
MANIFEST_PATH = os.path.join(BASE, "manifests", "download_manifest_ROUND2.json")

SPECIES = [
    {
        "name": "Scinax_rostratus",
        "sci_name": "Scinax rostratus",
        "taxon_id": 24292,
        "gbif_key": 5217865,
        "obs_file": os.path.join(BASE, "recovery_temp", "scinax_obs.json"),
    },
    {
        "name": "Craugastor_metriosistus",
        "sci_name": "Craugastor metriosistus",
        "taxon_id": 517046,
        "gbif_key": 10819374,
        "obs_file": os.path.join(BASE, "recovery_temp", "craugastor_obs.json"),
    },
]

CAP = 110
HEADERS = {"User-Agent": "AnuraResearchDataset/1.0 (contact: sebastianmartinez06.js@gmail.com)"}

manifest = []

for sp in SPECIES:
    print("=== ", sp["name"])
    data = json.load(open(sp["obs_file"], encoding="utf-8"))
    results = data["results"]
    out_dir = os.path.join(IMG_BASE, sp["name"])
    os.makedirs(out_dir, exist_ok=True)
    count = 0
    for obs in results:
        if count >= CAP:
            break
        obs_id = obs["id"]
        photos = obs.get("photos", [])
        if not photos:
            continue
        photo = photos[0]
        photo_id = photo["id"]
        license_code = photo.get("license_code")
        url = photo.get("url", "")
        # url is usually square; get medium/large version
        img_url = url.replace("square", "medium") if url else None
        if not img_url:
            continue
        ext = ".jpg"
        fname = f"{obs_id}_{photo_id}{ext}"
        local_path = os.path.join(out_dir, fname)
        try:
            req = urllib.request.Request(img_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as resp:
                content = resp.read()
        except Exception as e:
            print("FAIL", obs_id, photo_id, e)
            continue
        with open(local_path, "wb") as f:
            f.write(content)
        sha256 = hashlib.sha256(content).hexdigest()
        coords = obs.get("geojson", {}).get("coordinates") if obs.get("geojson") else None
        manifest.append({
            "species": sp["sci_name"],
            "taxon_id": sp["taxon_id"],
            "gbif_taxon_key": sp["gbif_key"],
            "observation_id": obs_id,
            "photo_id": photo_id,
            "license": license_code,
            "original_url": img_url,
            "local_path": local_path,
            "sha256": sha256,
            "download_timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "quality_grade": obs.get("quality_grade"),
            "coordinates": coords,
            "observed_on": obs.get("observed_on"),
        })
        count += 1
        if count % 10 == 0:
            print(" downloaded", count)
        time.sleep(1.0)  # rate limit respect
    print(sp["name"], "downloaded:", count)

os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
print("TOTAL manifest entries:", len(manifest))
