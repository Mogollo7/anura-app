"""
build_clean_known_manifest.py — FASE 16.2: construye un conjunto KNOWN genuinamente
held-out, SIN usar F3. Filtra por archivo (path) Y por obs_id (individuo), para no
contar como "independiente" una segunda foto del mismo individuo ya usado en TRAIN.

REFERENCE/CALIBRATION no tienen obs_id extraible (nombres reindexados) — se excluyen
por archivo/hash, pero no puede verificarse independencia de individuo contra ellos.
Esto se declara como limitacion explicita (Fase 16.1), no se oculta.
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
    print("=== FASE 16.2: CLEAN KNOWN MANIFEST ===\n")

    train = load_json(ROOT / "training/manifiesto.json")
    train_paths, train_obs = set(), set()
    for part in ("train", "val", "test"):
        for r in train["particiones"][part]:
            ruta = r["ruta"].replace("\\", "/")
            train_paths.add(ruta)
            oid = obs_id_of(ruta)
            if oid:
                train_obs.add(oid)

    ref = load_json(ROOT / "data calibration/REFERENCE_manifest.json")
    cal = load_json(ROOT / "data calibration/CALIBRATION_manifest.json")
    ref_files = {r["FileName"] for r in ref}
    cal_files = {r["FileName"] for r in cal}
    ref_hashes = {r["SHA256"] for r in ref}
    cal_hashes = {r["SHA256"] for r in cal}

    f3f4 = load_json(ROOT / "evaluation/open_set_v1/knn/knn_open_set_results.json", encoding="utf-8")
    f3f4_paths = {r["path"].replace("\\", "/") for r in f3f4["records"]}

    import sys
    sys.path.insert(0, str(ROOT / "tools" / "catalog"))
    from taxonomic_resolution import SpeciesResolver
    resolver = SpeciesResolver(ROOT / "training/taxonomia.py", ROOT / "taxonomy/species/species_registry.json")

    data_cleaned = ROOT / "data cleaned"
    manifest = []
    rejected_by_obsid = []
    image_id_counter = 0

    for sp_dir in sorted(os.listdir(data_cleaned)):
        full_dir = data_cleaned / sp_dir
        if not full_dir.is_dir():
            continue
        resolved = resolver.resolve(sp_dir.replace("_", " "))
        if resolved["species_id"] is None:
            continue  # especie fuera del catalogo visual (huerfana), no aplica a KNOWN

        imgs = [f for f in os.listdir(full_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        for img in imgs:
            rel_path = f"{sp_dir}/{img}"
            full_path = full_dir / img

            if rel_path in train_paths:
                continue
            if rel_path in f3f4_paths:
                continue
            if img in ref_files or img in cal_files:
                continue

            oid = obs_id_of(img)
            if oid and oid in train_obs:
                rejected_by_obsid.append({"path": rel_path, "obs_id": oid,
                                           "reason": "mismo individuo (obs_id) ya presente en TRAIN"})
                continue

            file_hash = sha256_of(full_path)
            if file_hash in ref_hashes or file_hash in cal_hashes:
                continue  # duplicado exacto de REFERENCE/CALIBRATION por contenido, no solo nombre

            image_id_counter += 1
            manifest.append({
                "image_id": f"CLEAN_KNOWN_{image_id_counter:05d}",
                "species_id": resolved["species_id"],
                "scientific_name": resolved["canonical_name"].replace("_", " "),
                "observation_id": f"OBS_{oid}" if oid else None,
                "individual_id": oid,  # proxy: mismo obs_id = mismo individuo
                "path": rel_path,
                "sha256": file_hash,
                "source": "data cleaned/ (real, no usado en TRAIN/REFERENCE/CALIBRATION/F3F4)",
                "split": "CLEAN_KNOWN_FASE16",
            })

    n_individuals = len({r["individual_id"] for r in manifest if r["individual_id"]})
    n_no_individual = sum(1 for r in manifest if r["individual_id"] is None)
    n_species = len({r["species_id"] for r in manifest})

    print(f"Imagenes candidatas totales: {len(manifest) + len(rejected_by_obsid)}")
    print(f"Rechazadas por obs_id ya en TRAIN (mismo individuo, archivo distinto): {len(rejected_by_obsid)}")
    print(f"KNOWN limpio final: {len(manifest)} imagenes")
    print(f"  Individuos distintos (via obs_id): {n_individuals}")
    print(f"  Sin obs_id extraible (imagen manual/museo, contada como propia): {n_no_individual}")
    print(f"  Especies distintas: {n_species}")

    out = {
        "phase": "16.2",
        "n_images": len(manifest),
        "n_individuals": n_individuals + n_no_individual,
        "n_species": n_species,
        "rejected_by_individual_overlap": len(rejected_by_obsid),
        "images": manifest,
    }
    out_path = OUT / "clean_known_manifest.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    rejected_path = OUT / "clean_known_rejected_by_individual.json"
    with open(rejected_path, "w", encoding="utf-8") as f:
        json.dump(rejected_by_obsid[:200], f, indent=2, ensure_ascii=False)

    print(f"\n[OK] {out_path}")
    print(f"[OK] Rechazados (muestra 200): {rejected_path}")


if __name__ == "__main__":
    main()
