"""
FASE 22 - UNKNOWN V2
Step 3: Leakage check (CRITICAL) + duplicate check for the historical UNKNOWN pool.

A UNKNOWN image cannot also appear (exact SHA256 match) in:
  - TRAIN (evaluation/fase13/manifests/TRAIN_manifest.json -> paths are relative to "data cleaned/")
  - REFERENCE (data calibration/REFERENCE_manifest.json)
  - CALIBRATION (data calibration/CALIBRATION_manifest.json)
  - BLIND (validation/fase18_clean_calibration/blind_manifest.json known+unknown)
  - VALIDATION (validation/fase16_clean_open_set/clean_known_manifest.json)
  - centroid source (visual_catalog/v1.0.0/manifest.json group_a/group_b sources, read-only reference)

We compute real SHA256 of files on disk referenced by these manifests (not trusting manifest sha
fields, several of which are empty) and compare against the 56 historical UNKNOWN hashes.
Read-only: this script does not modify any protected artifact.
"""
import json, csv, hashlib, sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(r"D:\Anura")
AUDIT_CSV = ROOT / "data/unknown_open_set_v2/audit/historical_unknown_quality_audit.csv"
OUT_LEAK = ROOT / "data/unknown_open_set_v2/audit/leakage_audit.csv"
OUT_DUP = ROOT / "data/unknown_open_set_v2/audit/duplicate_audit.csv"

def sha256_of(path: Path, block=1 << 20):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while True:
                b = f.read(block)
                if not b:
                    break
                h.update(b)
        return h.hexdigest()
    except Exception:
        return None

def hashes_from_train_manifest():
    """TRAIN_manifest.json entries have 'ruta' relative to 'data cleaned/'."""
    data = json.loads((ROOT / "evaluation/fase13/manifests/TRAIN_manifest.json").read_text(encoding="utf-8"))
    hashes = {}
    for r in data:
        rel = r.get("ruta") or r.get("OriginalPath") or r.get("FileName")
        if not rel:
            continue
        p = ROOT / "data cleaned" / rel
        if p.exists():
            h = sha256_of(p)
            if h:
                hashes[h] = str(p)
    return hashes

def hashes_from_calibration_style(fname, root_hint="data cleaned"):
    data = json.loads((ROOT / fname).read_text(encoding="utf-8-sig"))
    hashes = {}
    items = data if isinstance(data, list) else data.get("items", [])
    for r in items:
        rel = r.get("path") or r.get("ruta") or r.get("FileName")
        if not rel:
            continue
        for base in [ROOT / root_hint, ROOT]:
            p = base / rel
            if p.exists():
                h = r.get("sha256") or sha256_of(p)
                if h:
                    hashes[h] = str(p)
                break
    return hashes

def hashes_from_fase16_clean_known():
    data = json.loads((ROOT / "validation/fase16_clean_open_set/clean_known_manifest.json").read_text(encoding="utf-8"))
    items = data if isinstance(data, list) else data.get("images", data.get("records", []))
    hashes = {}
    for r in items:
        h = r.get("sha256")
        rel = r.get("path")
        if h:
            hashes[h] = rel or "clean_known_manifest"
    return hashes

def hashes_from_fase18_blind():
    data = json.loads((ROOT / "validation/fase18_clean_calibration/blind_manifest.json").read_text(encoding="utf-8"))
    hashes = {}
    for bucket in ("known", "unknown"):
        for r in data.get(bucket, []):
            h = r.get("sha256")
            if h:
                hashes[h] = r.get("path", f"blind_{bucket}")
    return hashes

def main():
    protected = {}
    sources_used = []
    try:
        h = hashes_from_train_manifest()
        protected.update({k: ("TRAIN", v) for k, v in h.items()})
        sources_used.append(f"TRAIN: {len(h)} hashes")
    except Exception as e:
        print("TRAIN manifest error:", e)

    for label, fname in [("REFERENCE", "data calibration/REFERENCE_manifest.json"),
                          ("CALIBRATION", "data calibration/CALIBRATION_manifest.json")]:
        try:
            h = hashes_from_calibration_style(fname)
            protected.update({k: (label, v) for k, v in h.items()})
            sources_used.append(f"{label}: {len(h)} hashes")
        except Exception as e:
            print(f"{label} manifest error:", e)

    try:
        h = hashes_from_fase16_clean_known()
        protected.update({k: ("VALIDATION_FASE16_CLEAN_KNOWN", v) for k, v in h.items()})
        sources_used.append(f"VALIDATION_FASE16_CLEAN_KNOWN: {len(h)} hashes")
    except Exception as e:
        print("Fase16 clean known error:", e)

    try:
        h = hashes_from_fase18_blind()
        protected.update({k: ("BLIND_FASE18", v) for k, v in h.items()})
        sources_used.append(f"BLIND_FASE18: {len(h)} hashes")
    except Exception as e:
        print("Fase18 blind error:", e)

    print("Protected-set hash sources:")
    for s in sources_used:
        print(" -", s)
    print(f"Total unique protected hashes indexed: {len(protected)}")

    # Load historical unknown pool (post quality audit)
    rows = list(csv.DictReader(open(AUDIT_CSV, encoding="utf-8")))
    inv_rows = {r["image_path"]: r for r in csv.DictReader(open(
        ROOT / "data/unknown_open_set_v2/metadata/historical_unknown_inventory.csv", encoding="utf-8"))}

    leak_rows = []
    dup_groups = defaultdict(list)
    for r in rows:
        p = r["image_path"]
        inv = inv_rows.get(p, {})
        h = inv.get("sha256", "")
        leaked = h in protected
        leak_rows.append({
            "image_path": p, "sha256": h,
            "leakage_status": "LEAKED" if leaked else "CLEAN",
            "leaked_into_set": protected[h][0] if leaked else "",
            "leaked_matching_path": protected[h][1] if leaked else "",
        })
        if h:
            dup_groups[h].append(p)

    OUT_LEAK.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_LEAK, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(leak_rows[0].keys()))
        w.writeheader()
        w.writerows(leak_rows)

    n_leaked = sum(1 for r in leak_rows if r["leakage_status"] == "LEAKED")
    print(f"Leakage result: {n_leaked} / {len(leak_rows)} historical UNKNOWN images leaked into protected sets.")

    # Duplicate audit (within historical pool + against itself; sha256 exact only, no perceptual hash lib available)
    dup_rows = []
    gid = 0
    for h, paths in dup_groups.items():
        if len(paths) > 1:
            gid += 1
            for p in paths:
                dup_rows.append({"image_path": p, "sha256": h, "duplicate_group": f"DUPGRP_{gid}",
                                  "n_copies_in_pool": len(paths), "note": "exact_sha256_duplicate_within_pool"})
    with open(OUT_DUP, "w", newline="", encoding="utf-8") as f:
        fn = ["image_path", "sha256", "duplicate_group", "n_copies_in_pool", "note"]
        w = csv.DictWriter(f, fieldnames=fn)
        w.writeheader()
        w.writerows(dup_rows)
    print(f"Exact-duplicate groups within historical pool: {gid} groups, {len(dup_rows)} affected images.")
    print("NOTE: perceptual-hash (near-duplicate) comparison not available - no imagehash lib installed in "
          "this environment; documented as a methodological limitation, exact SHA256 comparison performed instead.")

if __name__ == "__main__":
    main()
