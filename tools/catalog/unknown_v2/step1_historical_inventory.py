"""
FASE 22 - UNKNOWN V2
Step 1: Recover historical UNKNOWN inventory (Fase 16 / 19 / 20 / 21 source).

Source of truth for which images were used as UNKNOWN in Fase 16/19/20/21:
evaluation/open_set_v1/knn/knn_open_set_results.json (records with known_unknown == "UNKNOWN")
This file is READ-ONLY (protected artifact fase13 lineage) - we only read it.

Output: data/unknown_open_set_v2/metadata/historical_unknown_inventory.csv
"""
import json, csv, hashlib, os, sys
from pathlib import Path

ROOT = Path(r"D:\Anura")
OUT = ROOT / "data/unknown_open_set_v2/metadata/historical_unknown_inventory.csv"

sys.path.insert(0, str(ROOT))

def sha256_of(path: Path, block=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(block)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def find_image_on_disk(rel_path_windows: str):
    """rel_path_windows like 'Hyloxalus_picachos\\bmc_campo_02.jpg' -> search known raw dirs."""
    rel = rel_path_windows.replace("\\", "/")
    candidates = [
        ROOT / "data cleaned" / rel,
        ROOT / "data dirty" / rel,
    ]
    for c in candidates:
        if c.exists():
            return c
    # fallback: search by basename anywhere under data cleaned / data dirty
    base = Path(rel).name
    for base_dir in [ROOT / "data cleaned", ROOT / "data dirty"]:
        for p in base_dir.rglob(base):
            return p
    return None

def main():
    src = json.loads((ROOT / "evaluation/open_set_v1/knn/knn_open_set_results.json").read_text(encoding="utf-8"))
    recs = [r for r in src["records"] if r.get("known_unknown") == "UNKNOWN"]
    print(f"Historical UNKNOWN records found in source-of-truth: {len(recs)}")

    rows = []
    missing = []
    for r in recs:
        rel = r["path"]
        species = r["true_species"]
        disk_path = find_image_on_disk(rel)
        row = {
            "image_id": r["image_id"],
            "image_path": str(disk_path) if disk_path else "",
            "source_phase": "FASE16_FASE19_FASE20_FASE21",
            "observation_id": "",
            "individual_id": "",
            "species": species,
            "genus": species.split("_")[0],
            "family": "",
            "taxon_id": "",
            "source": "evaluation/open_set_v1/knn/knn_open_set_results.json",
            "original_url": "",
            "sha256": "",
            "width": "",
            "height": "",
            "file_size": "",
            "quality_grade": "",
            "latitude": "",
            "longitude": "",
            "date": "",
            "original_inclusion_status": "ACCEPTED_HISTORICAL",
        }
        if disk_path:
            try:
                row["sha256"] = sha256_of(disk_path)
                row["file_size"] = disk_path.stat().st_size
            except Exception as e:
                row["original_inclusion_status"] = f"ERROR_READ:{e}"
        else:
            row["original_inclusion_status"] = "MISSING_ON_DISK"
            missing.append(rel)
        rows.append(row)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUT}")
    print(f"Missing on disk: {len(missing)}")
    for m in missing:
        print("  MISSING:", m)

if __name__ == "__main__":
    main()
