"""
build_contamination_audit.py — FASE 16.1: auditoria de contaminacion completa entre
TRAIN, CALIBRATION, REFERENCE, y el pool candidato para BLIND/KNOWN limpio.

Compara por: path, SHA256 (cuando disponible), observation_id/individual_id (obs_id
extraido de nombre de archivo iNaturalist), y reporta cada interseccion explicitamente.
NUNCA asume 0 sin evidencia — si un dataset no tiene el campo, se marca UNKNOWN.
"""
import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(r"D:\Anura")
OUT = ROOT / "validation" / "fase16_clean_open_set"
OBS_PATTERN = re.compile(r"col_obs_(\d+)_photo")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def obs_id_of(filename: str):
    m = OBS_PATTERN.search(filename)
    return m.group(1) if m else None


def load_json(p, encoding="utf-8-sig"):
    with open(p, encoding=encoding) as f:
        return json.load(f)


def main():
    print("=== FASE 16.1: CONTAMINATION AUDIT ===\n")

    # ── TRAIN ──
    train = load_json(ROOT / "training/manifiesto.json")
    train_paths, train_obs = set(), set()
    for part in ("train", "val", "test"):
        for r in train["particiones"][part]:
            ruta = r["ruta"].replace("\\", "/")
            train_paths.add(ruta)
            oid = obs_id_of(ruta)
            if oid:
                train_obs.add(oid)
    print(f"TRAIN: {len(train_paths)} paths, {len(train_obs)} obs_id unicos "
          f"(individual_id NO disponible como campo formal, se usa obs_id como proxy)")

    # ── CALIBRATION / REFERENCE ──
    ref = load_json(ROOT / "data calibration/REFERENCE_manifest.json")
    cal = load_json(ROOT / "data calibration/CALIBRATION_manifest.json")
    ref_files = {r["FileName"] for r in ref}
    cal_files = {r["FileName"] for r in cal}
    ref_hashes = {r["SHA256"] for r in ref}
    cal_hashes = {r["SHA256"] for r in cal}
    # REFERENCE/CALIBRATION filenames son "Especie_NNN.jpg" (curado, reindexado) —
    # NO tienen patron col_obs_, por lo que NO se puede extraer obs_id de ellos.
    # Esto es una limitacion real, documentada como UNKNOWN, no asumida como 0.
    print(f"REFERENCE: {len(ref_files)} archivos, {len(ref_hashes)} hashes unicos, "
          f"obs_id=UNKNOWN (nombres reindexados, sin patron extraible)")
    print(f"CALIBRATION: {len(cal_files)} archivos, {len(cal_hashes)} hashes unicos, obs_id=UNKNOWN")

    # ── F3/F4 (candidato a reusarse solo para UNKNOWN, ver Fase 16.3) ──
    f3f4 = load_json(ROOT / "evaluation/open_set_v1/knn/knn_open_set_results.json", encoding="utf-8")
    f3f4_paths = {r["path"].replace("\\", "/") for r in f3f4["records"]}
    f3f4_known_paths = {r["path"].replace("\\", "/") for r in f3f4["records"] if r["known_unknown"] == "KNOWN"}
    f3f4_unknown_paths = {r["path"].replace("\\", "/") for r in f3f4["records"] if r["known_unknown"] == "UNKNOWN"}
    f3f4_unknown_obs = {obs_id_of(p) for p in f3f4_unknown_paths} - {None}
    print(f"F3 (KNOWN): {len(f3f4_known_paths)} paths")
    print(f"F4 (UNKNOWN): {len(f3f4_unknown_paths)} paths, {len(f3f4_unknown_obs)} obs_id unicos\n")

    # ── Interseccion TRAIN vs CALIBRATION/REFERENCE (por hash, ya conocido, re-verificado) ──
    # REFERENCE/CALIBRATION no tienen 'ruta' identica a TRAIN (rutas distintas: una usa
    # subcarpetas por familia/genero, otra usa carpeta plana). Comparamos por SHA256.
    def compute_train_hashes_for_species(species_dirs_needed):
        """Calcula SHA256 real de los archivos de TRAIN, solo para las especies de REFERENCE/CALIBRATION
        (evita recalcular las 4724 imagenes completas de TRAIN, nos interesa esta interseccion especifica)."""
        hashes = {}
        for part in ("train", "val", "test"):
            for r in train["particiones"][part]:
                especie = r["especie"]
                if especie not in species_dirs_needed:
                    continue
                ruta = r["ruta"]
                full = ROOT / "data cleaned" / ruta
                if full.exists():
                    hashes[sha256_of(full)] = ruta
        return hashes

    ref_cal_species = {r["Species"].replace(" ", "_") for r in ref} | {r["Species"].replace(" ", "_") for r in cal}
    train_hashes_relevant = compute_train_hashes_for_species(ref_cal_species)
    print(f"TRAIN hashes calculados para especies REFERENCE/CALIBRATION overlap check: {len(train_hashes_relevant)}")

    overlap_train_ref = set(train_hashes_relevant.keys()) & ref_hashes
    overlap_train_cal = set(train_hashes_relevant.keys()) & cal_hashes

    # ── Interseccion CALIBRATION vs F4 (por hash) ──
    overlap_cal_f4 = set()  # F4 no tiene SHA256 en su registro; se compara por path/filename abajo
    f4_filenames = {Path(p).name for p in f3f4_unknown_paths}
    overlap_cal_f4_filename = cal_files & f4_filenames
    overlap_ref_f4_filename = ref_files & f4_filenames

    # ── Interseccion TRAIN vs F4 (ya conocida, re-verificada aqui) ──
    overlap_train_f4 = train_paths & f3f4_unknown_paths
    overlap_train_f3 = train_paths & f3f4_known_paths

    audit = {
        "phase": "16.1",
        "comparisons": {
            "TRAIN_vs_CALIBRATION": {
                "count": len(overlap_train_cal),
                "examples": list(overlap_train_cal)[:5],
                "comparison_method": "SHA256 (calculado en runtime para especies compartidas)"
            },
            "TRAIN_vs_REFERENCE": {
                "count": len(overlap_train_ref),
                "examples": list(overlap_train_ref)[:5],
                "comparison_method": "SHA256 (calculado en runtime para especies compartidas)"
            },
            "TRAIN_vs_BLIND_F4_UNKNOWN": {
                "count": len(overlap_train_f4),
                "examples": list(overlap_train_f4)[:5],
                "comparison_method": "path completo"
            },
            "TRAIN_vs_BLIND_F3_KNOWN": {
                "count": len(overlap_train_f3),
                "examples": list(overlap_train_f3)[:5],
                "comparison_method": "path completo",
                "note": "Ya documentado en Fase 15 como leakage confirmado. F3 NO se reutiliza en Fase 16."
            },
            "CALIBRATION_vs_BLIND_F4": {
                "count": len(overlap_cal_f4_filename),
                "examples": list(overlap_cal_f4_filename)[:5],
                "comparison_method": "filename (CALIBRATION no tiene path completo comparable a F4)"
            },
            "REFERENCE_vs_BLIND_F4": {
                "count": len(overlap_ref_f4_filename),
                "examples": list(overlap_ref_f4_filename)[:5],
                "comparison_method": "filename"
            },
            "individual_id_CALIBRATION_vs_BLIND": {
                "status": "UNKNOWN",
                "reason": "CALIBRATION no tiene obs_id/individual_id extraible (nombres reindexados "
                          "Especie_NNN.jpg sin patron de observacion). No se asume 0 — se declara UNKNOWN "
                          "explicitamente, consistente con FASE12_1_INDEPENDENCE_AUDIT.md previamente documentado."
            }
        }
    }

    out_path = OUT / "contamination_audit.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2, ensure_ascii=False)

    print("\n--- RESULTADOS ---")
    for name, r in audit["comparisons"].items():
        if "count" in r:
            print(f"  {name}: {r['count']}")
        else:
            print(f"  {name}: {r['status']}")

    print(f"\n[OK] {out_path}")


if __name__ == "__main__":
    main()
