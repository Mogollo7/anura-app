"""
build_splits.py — FASE 18.1: divide el pool KNOWN limpio (Fase 16, 7475 imgs) y el pool
UNKNOWN (F4, 56 imgs) en CALIBRATION_18 / BLIND_F18, disjuntos por individual_id (obs_id),
estratificado por especie. Semilla fija para reproducibilidad.

Marca explicitamente que el pool completo de Fase 16/17 (usado como METHOD_SELECTION_BLIND)
no se reutiliza como blind final aqui — se re-particiona en dos mitades nuevas y mas pequenas,
cada imagen cae en calibration O blind, nunca en ambos, y ningun individuo se reparte entre los dos.
"""
import json
import random
from pathlib import Path
from collections import defaultdict

ROOT = Path(r"D:\Anura")
F16 = ROOT / "validation" / "fase16_clean_open_set"
OUT = ROOT / "validation" / "fase18_clean_calibration"
SEED = 1618  # fijo, documentado, no elegido por ensayo-error

CALIBRATION_FRACTION = 0.35  # el resto va a BLIND_F18


def split_by_individual(images, individual_key, seed):
    """Agrupa por individuo, reparte grupos completos (nunca una imagen suelta)."""
    by_individual = defaultdict(list)
    for img in images:
        key = img.get(individual_key) or f"__no_individual__{img['image_id']}"
        by_individual[key].append(img)

    individuals = sorted(by_individual.keys())  # orden determinista antes de mezclar
    rng = random.Random(seed)
    rng.shuffle(individuals)

    n_cal = max(1, int(len(individuals) * CALIBRATION_FRACTION))
    cal_individuals = set(individuals[:n_cal])

    calibration, blind = [], []
    for ind, imgs in by_individual.items():
        target = calibration if ind in cal_individuals else blind
        target.extend(imgs)
    return calibration, blind


def main():
    print("=== FASE 18.1: CONSTRUCCION DE SPLITS CALIBRATION_18 / BLIND_F18 ===\n")

    with open(F16 / "clean_known_manifest.json", encoding="utf-8") as f:
        known_manifest = json.load(f)

    # Split KNOWN estratificado por especie (cada especie se reparte independientemente,
    # para que BLIND_F18 tenga representacion de las 24 especies, no solo las mas grandes)
    by_species = defaultdict(list)
    for img in known_manifest["images"]:
        by_species[img["species_id"]].append(img)

    cal_known, blind_known = [], []
    for sid, imgs in sorted(by_species.items()):
        c, b = split_by_individual(imgs, "individual_id", SEED + hash(sid) % 10000)
        cal_known.extend(c)
        blind_known.extend(b)

    print(f"KNOWN total: {len(known_manifest['images'])}")
    print(f"  CALIBRATION_18: {len(cal_known)}")
    print(f"  BLIND_F18:      {len(blind_known)}")

    # Split UNKNOWN (F4) por individuo, estratificado por especie
    f4_json = ROOT / "evaluation/open_set_v1/knn/knn_open_set_results.json"
    with open(f4_json, encoding="utf-8") as f:
        f3f4 = json.load(f)["records"]
    unknown_records = [r for r in f3f4 if r["known_unknown"] == "UNKNOWN"]

    import re
    obs_pat = re.compile(r"col_obs_(\d+)_photo")
    for r in unknown_records:
        m = obs_pat.search(r["path"])
        r["individual_id"] = m.group(1) if m else None

    by_species_unk = defaultdict(list)
    for r in unknown_records:
        by_species_unk[r["true_species"]].append(r)

    cal_unknown, blind_unknown = [], []
    for sp, recs in sorted(by_species_unk.items()):
        for r in recs:
            r["image_id"] = r.get("image_id", r["path"])
        c, b = split_by_individual(recs, "individual_id", SEED + hash(sp) % 10000)
        cal_unknown.extend(c)
        blind_unknown.extend(b)

    print(f"\nUNKNOWN total: {len(unknown_records)}")
    print(f"  CALIBRATION_18: {len(cal_unknown)}")
    print(f"  BLIND_F18:      {len(blind_unknown)}")

    # ── Verificar 0 overlap de individual_id entre calibration y blind ──
    cal_known_ind = {img.get("individual_id") for img in cal_known if img.get("individual_id")}
    blind_known_ind = {img.get("individual_id") for img in blind_known if img.get("individual_id")}
    overlap_known_ind = cal_known_ind & blind_known_ind

    cal_unk_ind = {r.get("individual_id") for r in cal_unknown if r.get("individual_id")}
    blind_unk_ind = {r.get("individual_id") for r in blind_unknown if r.get("individual_id")}
    overlap_unk_ind = cal_unk_ind & blind_unk_ind

    print(f"\nOverlap individual_id KNOWN (cal vs blind): {len(overlap_known_ind)}")
    print(f"Overlap individual_id UNKNOWN (cal vs blind): {len(overlap_unk_ind)}")
    assert len(overlap_known_ind) == 0, "FALLO: individuo KNOWN repartido entre calibration y blind"
    assert len(overlap_unk_ind) == 0, "FALLO: individuo UNKNOWN repartido entre calibration y blind"

    calibration_manifest = {
        "phase": "18.1",
        "seed": SEED,
        "calibration_fraction_target": CALIBRATION_FRACTION,
        "known": cal_known,
        "unknown": cal_unknown,
        "n_known": len(cal_known), "n_unknown": len(cal_unknown),
        "n_known_individuals": len(cal_known_ind), "n_unknown_individuals": len(cal_unk_ind),
        "n_known_species": len({img["species_id"] for img in cal_known}),
        "n_unknown_species": len({r["true_species"] for r in cal_unknown}),
    }
    blind_manifest = {
        "phase": "18.1",
        "seed": SEED,
        "known": blind_known,
        "unknown": blind_unknown,
        "n_known": len(blind_known), "n_unknown": len(blind_unknown),
        "n_known_individuals": len(blind_known_ind), "n_unknown_individuals": len(blind_unk_ind),
        "n_known_species": len({img["species_id"] for img in blind_known}),
        "n_unknown_species": len({r["true_species"] for r in blind_unknown}),
    }

    with open(OUT / "calibration_manifest.json", "w", encoding="utf-8") as f:
        json.dump(calibration_manifest, f, indent=2, ensure_ascii=False)
    with open(OUT / "blind_manifest.json", "w", encoding="utf-8") as f:
        json.dump(blind_manifest, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] CALIBRATION_18: {len(cal_known)} KNOWN ({calibration_manifest['n_known_species']} sp, "
          f"{calibration_manifest['n_known_individuals']} ind) + "
          f"{len(cal_unknown)} UNKNOWN ({calibration_manifest['n_unknown_species']} sp, "
          f"{calibration_manifest['n_unknown_individuals']} ind)")
    print(f"[OK] BLIND_F18:      {len(blind_known)} KNOWN ({blind_manifest['n_known_species']} sp, "
          f"{blind_manifest['n_known_individuals']} ind) + "
          f"{len(blind_unknown)} UNKNOWN ({blind_manifest['n_unknown_species']} sp, "
          f"{blind_manifest['n_unknown_individuals']} ind)")


if __name__ == "__main__":
    main()
