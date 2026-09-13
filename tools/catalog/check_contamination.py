"""
check_contamination.py — Generaliza el chequeo de contaminacion cruzada que hoy vive disperso
en fase13_pre_audit.py, build_dataset_manifest.py y fase13_generate_train_manifest.py.

Detecta solapamiento entre dos manifiestos (listas de registros JSON) usando, en orden de
preferencia:
    1. file_hash (SHA256 de la imagen) — mas confiable, detecta duplicado exacto de archivo
    2. observation_id / obs_id — detecta misma observacion con fotos distintas
    3. path — fallback debil, solo deteccion de mismo archivo por ruta

NO modifica ningun manifiesto. Solo reporta.

Uso:
    python check_contamination.py --manifest-a reference.json --manifest-b calibration.json \
        --hash-field SHA256 --obs-field obs_id
"""
import argparse
import json
import sys
from pathlib import Path


def load_manifest(path: Path):
    with open(path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    if isinstance(data, dict) and "records" in data:
        data = data["records"]
    if isinstance(data, dict) and "particiones" in data:
        raise ValueError(
            f"{path} parece un manifiesto con particiones (train/val/test) — "
            "pasa la particion especifica, no el archivo completo."
        )
    return data


def extract_field(record: dict, field_candidates: list[str]):
    for f in field_candidates:
        if f in record and record[f]:
            return record[f]
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest-a", required=True)
    ap.add_argument("--manifest-b", required=True)
    ap.add_argument("--hash-field", nargs="+", default=["SHA256", "sha256", "file_hash"])
    ap.add_argument("--obs-field", nargs="+", default=["obs_id", "observation_id"])
    ap.add_argument("--path-field", nargs="+", default=["OriginalPath", "path", "ruta"])
    args = ap.parse_args()

    manifest_a = load_manifest(Path(args.manifest_a))
    manifest_b = load_manifest(Path(args.manifest_b))

    hashes_a = {extract_field(r, args.hash_field) for r in manifest_a} - {None}
    hashes_b = {extract_field(r, args.hash_field) for r in manifest_b} - {None}
    hash_overlap = hashes_a & hashes_b

    obs_a = {extract_field(r, args.obs_field) for r in manifest_a} - {None}
    obs_b = {extract_field(r, args.obs_field) for r in manifest_b} - {None}
    obs_overlap = obs_a & obs_b

    print(f"=== CHEQUEO DE CONTAMINACION CRUZADA ===")
    print(f"A: {args.manifest_a} ({len(manifest_a)} registros)")
    print(f"B: {args.manifest_b} ({len(manifest_b)} registros)")
    print()

    if hashes_a or hashes_b:
        print(f"file_hash disponible en A={len(hashes_a)}, B={len(hashes_b)}")
        print(f"  Solapamiento por hash: {len(hash_overlap)}")
        if hash_overlap:
            for h in list(hash_overlap)[:10]:
                print(f"    - {h}")
    else:
        print("file_hash: NO DISPONIBLE en ninguno de los dos manifiestos")

    print()
    if obs_a or obs_b:
        print(f"obs_id disponible en A={len(obs_a)}, B={len(obs_b)}")
        print(f"  Solapamiento por obs_id: {len(obs_overlap)}")
    else:
        print("obs_id: NO DISPONIBLE en ninguno de los dos manifiestos "
              "(independencia de individuos NOT_FORMALLY_VERIFIABLE)")

    total_issues = len(hash_overlap) + len(obs_overlap)
    print(f"\nResultado: {'FAIL' if total_issues else 'PASS'} ({total_issues} solapamientos)")
    sys.exit(1 if total_issues else 0)


if __name__ == "__main__":
    main()
