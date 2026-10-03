"""
FASE 22 - UNKNOWN V2
Step 6: Quality audit + leakage + taxonomy resolution for newly downloaded images (step 5 output).

Leakage check for new images: since these are freshly downloaded from iNaturalist under CC
license and never touched TRAIN/REFERENCE/CALIBRATION/BLIND, we still verify by SHA256 against
the same protected-hash index built in step 3 (defense in depth - a photo could theoretically
have been reused across observations).
"""
import json, csv, sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(r"D:\Anura\tools\catalog\unknown_v2")))
sys.path.insert(0, str(Path(r"D:\Anura\tools\catalog")))
from common_quality import audit_one  # noqa: E402
from taxonomic_resolution import SpeciesResolver  # noqa: E402
from step3_leakage_and_duplicates import (  # noqa: E402
    hashes_from_train_manifest, hashes_from_calibration_style,
    hashes_from_fase16_clean_known, hashes_from_fase18_blind, sha256_of,
)

ROOT = Path(r"D:\Anura")
DL_MANIFEST = ROOT / "data/unknown_open_set_v2/manifests/download_manifest.json"
OUT_AUDIT = ROOT / "data/unknown_open_set_v2/audit/image_quality_audit.csv"
OUT_LEAK_APPEND = ROOT / "data/unknown_open_set_v2/audit/leakage_audit.csv"
OUT_TAX_APPEND = ROOT / "data/unknown_open_set_v2/metadata/taxonomy_resolution.csv"


def build_protected_index():
    protected = {}
    try:
        protected.update({k: ("TRAIN", v) for k, v in hashes_from_train_manifest().items()})
    except Exception as e:
        print("TRAIN idx err", e)
    for label, fname in [("REFERENCE", "data calibration/REFERENCE_manifest.json"),
                          ("CALIBRATION", "data calibration/CALIBRATION_manifest.json")]:
        try:
            protected.update({k: (label, v) for k, v in hashes_from_calibration_style(fname).items()})
        except Exception as e:
            print(label, "idx err", e)
    try:
        protected.update({k: ("VALIDATION_FASE16_CLEAN_KNOWN", v)
                           for k, v in hashes_from_fase16_clean_known().items()})
    except Exception as e:
        print("fase16 idx err", e)
    try:
        protected.update({k: ("BLIND_FASE18", v) for k, v in hashes_from_fase18_blind().items()})
    except Exception as e:
        print("fase18 idx err", e)
    return protected


def main():
    dl = json.loads(DL_MANIFEST.read_text(encoding="utf-8"))
    downloaded = dl["downloaded"]
    print(f"New images to audit: {len(downloaded)}")
    if not downloaded:
        print("No new images downloaded - nothing to audit. Writing empty outputs.")
        OUT_AUDIT.parent.mkdir(parents=True, exist_ok=True)
        OUT_AUDIT.write_text("image_path,decision,rejection_reason,width,height,blur_score,brightness_score,contrast_score,subject_visibility,duplicate_group,leakage_status,taxonomic_status,notes\n", encoding="utf-8")
        return

    protected = build_protected_index()
    print(f"Protected hash index size: {len(protected)}")

    resolver = SpeciesResolver(ROOT / "training/taxonomia.py", ROOT / "taxonomy/species/species_registry.json")

    audit_rows = []
    leak_rows = list(csv.DictReader(open(OUT_LEAK_APPEND, encoding="utf-8"))) if OUT_LEAK_APPEND.exists() else []
    tax_rows = list(csv.DictReader(open(OUT_TAX_APPEND, encoding="utf-8"))) if OUT_TAX_APPEND.exists() else []
    tax_seen = {r["species_raw"] for r in tax_rows}

    dup_hash_count = defaultdict(int)
    for d in downloaded:
        dup_hash_count[d["sha256"]] += 1

    species_needing_tax = sorted({d["species"] for d in downloaded})
    for sp in species_needing_tax:
        if sp in tax_seen:
            continue
        res = resolver.resolve(sp.replace("_", " "))
        tax_rows.append({
            "species_raw": sp, "canonical_name": res["canonical_name"],
            "species_id": res["species_id"] or "", "genus": sp.split("_")[0],
            "resolution_status": res["resolution_status"],
        })
        tax_seen.add(sp)

    for d in downloaded:
        p = Path(d["path"])
        row = audit_one(p)
        leaked = d["sha256"] in protected
        row["leakage_status"] = "LEAKED" if leaked else "CLEAN"
        row["taxonomic_status"] = "RESOLVED" if resolver.resolve(d["species"].replace("_", " "))["species_id"] else "UNRESOLVED_NOT_IN_REGISTRY_EXPECTED_FOR_UNKNOWN"
        if dup_hash_count[d["sha256"]] > 1:
            row["duplicate_group"] = f"NEWDUP_{d['sha256'][:10]}"
        audit_rows.append(row)
        leak_rows.append({
            "image_path": str(p), "sha256": d["sha256"],
            "leakage_status": row["leakage_status"],
            "leaked_into_set": protected[d["sha256"]][0] if leaked else "",
            "leaked_matching_path": protected[d["sha256"]][1] if leaked else "",
        })

    OUT_AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_AUDIT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(audit_rows[0].keys()))
        w.writeheader()
        w.writerows(audit_rows)

    with open(OUT_LEAK_APPEND, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(leak_rows[0].keys()))
        w.writeheader()
        w.writerows(leak_rows)

    with open(OUT_TAX_APPEND, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(tax_rows[0].keys()))
        w.writeheader()
        w.writerows(tax_rows)

    from collections import Counter
    print("New-image quality decisions:", dict(Counter(r["decision"] for r in audit_rows)))
    print("New-image leakage:", dict(Counter(r["leakage_status"] for r in audit_rows)))


if __name__ == "__main__":
    main()
