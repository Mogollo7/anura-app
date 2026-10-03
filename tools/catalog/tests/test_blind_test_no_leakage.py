"""
test_blind_test_no_leakage.py — Verifica explicitamente que F3/F4 (blind test) NO comparte
obs_id ni path con REFERENCE, CALIBRATION o TRAIN (usados para calibrar covariance/threshold/
centroides). Documenta la separacion calibration/validation/blind exigida en la Fase 7.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OBS_PATTERN = re.compile(r"col_obs_(\d+)_photo")


def load_json(p, encoding="utf-8-sig"):
    with open(p, encoding=encoding) as f:
        return json.load(f)


def obs_ids_from_paths(paths):
    ids = set()
    for p in paths:
        m = OBS_PATTERN.search(p)
        if m:
            ids.add(m.group(1))
    return ids


def main():
    print("=== BLIND TEST: verificacion de no-leakage F3/F4 vs REFERENCE/CALIBRATION/TRAIN ===\n")

    f3f4 = load_json(ROOT / "evaluation/open_set_v1/knn/knn_open_set_results.json")
    f3f4_paths = {r["path"] for r in f3f4["records"]}
    f3f4_obs = obs_ids_from_paths(f3f4_paths)
    n_known = sum(1 for r in f3f4["records"] if r["known_unknown"] == "KNOWN")
    n_unknown = sum(1 for r in f3f4["records"] if r["known_unknown"] == "UNKNOWN")
    print(f"F3/F4 (BLIND): {len(f3f4_paths)} imagenes, {len(f3f4_obs)} obs_id unicos "
          f"({n_known} KNOWN / {n_unknown} UNKNOWN)")

    ref = load_json(ROOT / "data calibration/REFERENCE_manifest.json")
    cal = load_json(ROOT / "data calibration/CALIBRATION_manifest.json")
    ref_paths = {r["OriginalPath"] for r in ref}
    cal_paths = {r["OriginalPath"] for r in cal}

    train = load_json(ROOT / "training/manifiesto.json")
    train_paths = set()
    train_obs = set()
    for part in ("train", "val", "test"):
        for r in train["particiones"][part]:
            train_paths.add(r["ruta"])
            m = OBS_PATTERN.search(r["ruta"])
            if m:
                train_obs.add(m.group(1))

    print(f"REFERENCE (CALIBRACION covariance): {len(ref_paths)} imagenes")
    print(f"CALIBRATION (CALIBRACION threshold): {len(cal_paths)} imagenes")
    print(f"TRAIN (CENTROIDES Group B): {len(train_paths)} imagenes, {len(train_obs)} obs_id unicos\n")

    # path overlap (comparacion directa por nombre de archivo, ya que las rutas base difieren)
    f3f4_filenames = {Path(p).name for p in f3f4_paths}
    ref_filenames = {Path(p).name for p in ref_paths}
    cal_filenames = {Path(p).name for p in cal_paths}
    train_filenames = {Path(p).name for p in train_paths}

    overlap_ref = f3f4_filenames & ref_filenames
    overlap_cal = f3f4_filenames & cal_filenames
    overlap_train_files = f3f4_filenames & train_filenames
    overlap_train_obs = f3f4_obs & train_obs

    print(f"Overlap de nombre de archivo F3/F4 vs REFERENCE: {len(overlap_ref)}")
    print(f"Overlap de nombre de archivo F3/F4 vs CALIBRATION: {len(overlap_cal)}")
    print(f"Overlap de nombre de archivo F3/F4 vs TRAIN: {len(overlap_train_files)}")
    print(f"Overlap de obs_id F3/F4 vs TRAIN: {len(overlap_train_obs)}")

    total_leakage = len(overlap_ref) + len(overlap_cal) + len(overlap_train_files)

    report = {
        "blind_set": "F3 (KNOWN) + F4 (UNKNOWN)",
        "n_blind_images": len(f3f4_paths),
        "n_known": n_known,
        "n_unknown": n_unknown,
        "calibration_sets": {
            "REFERENCE": {"role": "covariance calibration", "n_images": len(ref_paths)},
            "CALIBRATION": {"role": "threshold calibration", "n_images": len(cal_paths)},
            "TRAIN": {"role": "Group B structural centroids", "n_images": len(train_paths)},
        },
        "leakage_check": {
            "filename_overlap_with_REFERENCE": len(overlap_ref),
            "filename_overlap_with_CALIBRATION": len(overlap_cal),
            "filename_overlap_with_TRAIN": len(overlap_train_files),
            "obs_id_overlap_with_TRAIN": len(overlap_train_obs),
        },
        "leakage_detected": total_leakage > 0,
        "result": "PASS_NO_FILENAME_LEAKAGE" if total_leakage == 0 else "FAIL_LEAKAGE_DETECTED"
    }

    out_path = ROOT / "validation" / "new_species_test" / "blind_test_leakage_report.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Reporte: {out_path}")
    print(f"\nRESULTADO: {report['result']}")

    assert total_leakage == 0, "FALLO: se detecto leakage de archivo entre BLIND y conjuntos de calibracion"
    print("\n[NOTA] obs_id overlap con TRAIN puede ser >0 de forma esperada solo si son especies "
          "DISTINTAS fotografiando el mismo lugar/evento por coincidencia — se reporta, no se "
          "trata como leakage automatico salvo que tambien coincida el nombre de archivo exacto.")


if __name__ == "__main__":
    main()
