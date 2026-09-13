import os
import json
import hashlib
import sys
from pathlib import Path

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def run_pre_audit():
    print("=== FASE 13: PRE-AUDITORÍA DE INTEGRIDAD DE DATOS Y ARTEFACTOS ===")
    
    audit_results = {
        "status": "UNKNOWN",
        "checks": {}
    }
    
    all_passed = True

    # 1. Manifest Paths
    ref_manifest_path = Path(r"D:\Anura\data calibration\REFERENCE_manifest.json")
    cal_manifest_path = Path(r"D:\Anura\data calibration\CALIBRATION_manifest.json")
    
    if not ref_manifest_path.exists() or not cal_manifest_path.exists():
        print("ERROR: Manifiestos de REFERENCE o CALIBRATION no existen.")
        audit_results["checks"]["manifests_exist"] = False
        all_passed = False
    else:
        audit_results["checks"]["manifests_exist"] = True

    with open(ref_manifest_path, 'r', encoding='utf-8-sig') as f:
        ref_records = json.load(f)
    with open(cal_manifest_path, 'r', encoding='utf-8-sig') as f:
        cal_records = json.load(f)

    if not isinstance(ref_records, list):
        ref_records = ref_records.get('records', [])
    if not isinstance(cal_records, list):
        cal_records = cal_records.get('records', [])

    # Check sizes
    ref_size = len(ref_records)
    cal_size = len(cal_records)
    print(f"REFERENCE Size: {ref_size} (Expected 798)")
    print(f"CALIBRATION Size: {cal_size} (Expected 192)")

    audit_results["checks"]["reference_size"] = {
        "actual": ref_size,
        "expected": 798,
        "pass": ref_size == 798
    }
    audit_results["checks"]["calibration_size"] = {
        "actual": cal_size,
        "expected": 192,
        "pass": cal_size == 192
    }
    if ref_size != 798 or cal_size != 192:
        all_passed = False

    # Check species counts
    ref_species = set(r.get('Species', r.get('species')) for r in ref_records)
    cal_species = set(r.get('Species', r.get('species')) for r in cal_records)
    print(f"REFERENCE Species ({len(ref_species)}): {sorted(list(ref_species))}")
    print(f"CALIBRATION Species ({len(cal_species)}): {sorted(list(cal_species))}")

    audit_results["checks"]["species_count"] = {
        "ref_species_count": len(ref_species),
        "cal_species_count": len(cal_species),
        "pass": len(ref_species) == 10 and len(cal_species) == 10 and ref_species == cal_species
    }
    if len(ref_species) != 10 or len(cal_species) != 10 or ref_species != cal_species:
        all_passed = False

    # Check cross-split duplicates & contamination
    ref_hashes = {r.get('SHA256', r.get('sha256')): r for r in ref_records}
    cal_hashes = {r.get('SHA256', r.get('sha256')): r for r in cal_records}
    cross_duplicates = set(ref_hashes.keys()).intersection(set(cal_hashes.keys()))

    ref_contaminated = sum(1 for r in ref_records if r.get('is_contaminated', False))
    cal_contaminated = sum(1 for r in cal_records if r.get('is_contaminated', False))

    print(f"Cross-split duplicates: {len(cross_duplicates)} (Expected 0)")
    print(f"Contaminated in REFERENCE: {ref_contaminated} (Expected 0)")
    print(f"Contaminated in CALIBRATION: {cal_contaminated} (Expected 0)")

    audit_results["checks"]["integrity"] = {
        "cross_split_duplicates": len(cross_duplicates),
        "ref_contaminated": ref_contaminated,
        "cal_contaminated": cal_contaminated,
        "pass": len(cross_duplicates) == 0 and ref_contaminated == 0 and cal_contaminated == 0
    }
    if len(cross_duplicates) > 0 or ref_contaminated > 0 or cal_contaminated > 0:
        all_passed = False

    # Check Encoder ONNX hash
    encoder_path = Path(r"D:\Anura\bioclip\checkpoints\encoder_anura_fp16.onnx")
    expected_encoder_hash = "219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad"
    if not encoder_path.exists():
        print("ERROR: Encoder ONNX no encontrado.")
        audit_results["checks"]["encoder_exists"] = False
        all_passed = False
    else:
        actual_encoder_hash = sha256_file(encoder_path)
        print(f"Encoder Hash: {actual_encoder_hash}")
        encoder_match = actual_encoder_hash.lower() == expected_encoder_hash.lower()
        audit_results["checks"]["encoder_hash"] = {
            "actual": actual_encoder_hash,
            "expected": expected_encoder_hash,
            "pass": encoder_match
        }
        if not encoder_match:
            all_passed = False

    # Check F3 and F4 embeddings integrity (without peeking at evaluation scores)
    knn_emb_path = Path(r"D:\Anura\evaluation\open_set_v1\knn\knn_embeddings.npz")
    if not knn_emb_path.exists():
        print("ERROR: knn_embeddings.npz de F3/F4 no encontrado.")
        audit_results["checks"]["f3f4_embeddings_exist"] = False
        all_passed = False
    else:
        audit_results["checks"]["f3f4_embeddings_exist"] = True

    # Final Status
    if all_passed:
        audit_results["status"] = "PASS"
        print("\n>>> AUDITORÍA PREVIA: PASS <<<")
    else:
        audit_results["status"] = "BLOCKED"
        print("\n>>> AUDITORÍA PREVIA: BLOCKED <<<")

    # Output directory
    out_dir = Path(r"D:\Anura\evaluation\fase13\audit")
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(out_dir / "FASE13_PRE_AUDIT.json", "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2)

    with open(out_dir / "FASE13_PRE_AUDIT.md", "w", encoding="utf-8") as f:
        f.write("# FASE 13 — Reporte de Auditoría Previa\n\n")
        f.write(f"**STATUS**: {audit_results['status']}\n\n")
        f.write("## Detalle de Verificaciones\n\n")
        for k, v in audit_results["checks"].items():
            f.write(f"- **{k}**: `{v}`\n")

    return audit_results["status"] == "PASS"

if __name__ == "__main__":
    success = run_pre_audit()
    sys.exit(0 if success else 1)
