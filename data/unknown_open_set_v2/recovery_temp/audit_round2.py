import os, hashlib, csv, json
from PIL import Image, ImageStat

BASE = r"D:\Anura\data\unknown_open_set_v2"
IMG_BASE = os.path.join(BASE, "images", "primary")
AUDIT_DIR = os.path.join(BASE, "audit")

SPECIES = ["Scinax_rostratus", "Craugastor_metriosistus"]

hash_index_path = os.path.join(AUDIT_DIR, "hash_index_recovery_reference.txt")
existing_hashes = set(l.strip() for l in open(hash_index_path, encoding="utf-8") if l.strip())

quality_rows = []
dup_rows = []
leak_rows = []

seen_this_round = {}

for sp in SPECIES:
    d = os.path.join(IMG_BASE, sp)
    files = sorted(os.listdir(d))
    for fn in files:
        path = os.path.join(d, fn)
        with open(path, "rb") as f:
            content = f.read()
        sha256 = hashlib.sha256(content).hexdigest()
        size_bytes = len(content)
        status = "OK"
        width = height = None
        blur_metric = None
        brightness = None
        contrast = None
        try:
            im = Image.open(path)
            im = im.convert("RGB")
            width, height = im.size
            gray = im.convert("L")
            stat = ImageStat.Stat(gray)
            brightness = stat.mean[0]
            contrast = stat.stddev[0]
            # cheap blur proxy: variance of Laplacian approximation via simple gradient
            import numpy as np
            arr = np.asarray(gray, dtype=np.float32)
            gy, gx = np.gradient(arr)
            blur_metric = float((gx**2 + gy**2).var())
        except Exception as e:
            status = f"CORRUPT:{e}"

        if width is not None and (width < 200 or height < 200):
            status = "LOW_RESOLUTION" if status == "OK" else status
        if brightness is not None and (brightness < 15 or brightness > 240):
            status = "BAD_BRIGHTNESS" if status == "OK" else status
        if contrast is not None and contrast < 8:
            status = "LOW_CONTRAST" if status == "OK" else status

        quality_rows.append({
            "species": sp, "file": fn, "sha256": sha256, "size_bytes": size_bytes,
            "width": width, "height": height, "brightness": round(brightness,2) if brightness else None,
            "contrast": round(contrast,2) if contrast else None, "blur_metric": round(blur_metric,2) if blur_metric else None,
            "status": status,
        })

        # duplicate check (exact SHA256) within this round + against itself
        if sha256 in seen_this_round:
            dup_rows.append({"species": sp, "file": fn, "sha256": sha256, "duplicate_of": seen_this_round[sha256], "type": "EXACT_DUPLICATE_ROUND2"})
        else:
            seen_this_round[sha256] = f"{sp}/{fn}"

        # leakage check against existing index
        leak = sha256 in existing_hashes
        leak_rows.append({"species": sp, "file": fn, "sha256": sha256, "leakage_detected": leak})

os.makedirs(AUDIT_DIR, exist_ok=True)
with open(os.path.join(AUDIT_DIR, "image_quality_audit_ROUND2.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(quality_rows[0].keys()))
    w.writeheader()
    w.writerows(quality_rows)

with open(os.path.join(AUDIT_DIR, "duplicate_audit_ROUND2.csv"), "w", newline="", encoding="utf-8") as f:
    fields = ["species","file","sha256","duplicate_of","type"]
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(dup_rows)

with open(os.path.join(AUDIT_DIR, "leakage_audit_ROUND2.csv"), "w", newline="", encoding="utf-8") as f:
    fields = ["species","file","sha256","leakage_detected"]
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(leak_rows)

# summary
from collections import Counter
by_species_status = {}
for sp in SPECIES:
    rows = [r for r in quality_rows if r["species"] == sp]
    c = Counter(r["status"] for r in rows)
    by_species_status[sp] = dict(c)
    print(sp, "total", len(rows), "status breakdown", dict(c))

leak_count = sum(1 for r in leak_rows if r["leakage_detected"])
dup_count = len(dup_rows)
print("Total leakage detected:", leak_count)
print("Total exact duplicates (round2 internal):", dup_count)

json.dump({"by_species_status": by_species_status, "leak_count": leak_count, "dup_count": dup_count},
          open(os.path.join(AUDIT_DIR, "audit_summary_ROUND2.json"), "w", encoding="utf-8"), indent=2)
