"""
build_fixture_manifest.py — Construye observations/images para el fixture SYNTHETIC_TEST_ONLY,
respetando la distincion species/observation/individual/image de CATALOG_SCHEMA.md.

Reutiliza 25 imagenes REALES de data cleaned/Dendrobates_truncatus (hash, obs_id reales),
pero las declara bajo el species_id sintetico ANU_COL_TEST_SYN_001. Ver FIXTURE_DECLARATION.json.
"""
import hashlib
import json
import re
from pathlib import Path

SOURCE_DIR = Path(r"D:\Anura\data cleaned\Dendrobates_truncatus")
N_IMAGES = 25
SYNTHETIC_SPECIES_ID = "ANU_COL_TEST_SYN_001"
OBS_PATTERN = re.compile(r"col_obs_(\d+)_photo")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    files = sorted(SOURCE_DIR.iterdir())[:N_IMAGES]

    observations_by_obsid = {}
    images = []

    for img_path in files:
        m = OBS_PATTERN.search(img_path.name)
        obs_id_source = m.group(1) if m else None
        observation_id = f"OBS_TEST_SYN_{obs_id_source}" if obs_id_source else f"OBS_TEST_SYN_NOID_{len(images)}"

        if observation_id not in observations_by_obsid:
            observations_by_obsid[observation_id] = {
                "observation_id": observation_id,
                "source": "SYNTHETIC_TEST_ONLY (real iNaturalist obs_id borrowed from Dendrobates_truncatus)",
                "source_id": obs_id_source,
                "species_id": SYNTHETIC_SPECIES_ID,
                "quality_status": "PENDING",
            }

        file_hash = sha256_of(img_path)
        image_id = f"IMG_TEST_{file_hash[:12]}"
        images.append({
            "image_id": image_id,
            "observation_id": observation_id,
            "file_hash": file_hash,
            "path": str(img_path),
            "annotation_status": "NONE",
            "segmentation_status": "NONE",
            "quality_status": "PENDING",
        })

    individual_count = len(observations_by_obsid)
    image_count = len(images)

    manifest = {
        "fixture_type": "SYNTHETIC_TEST_ONLY",
        "species_id": SYNTHETIC_SPECIES_ID,
        "individual_count": individual_count,
        "observation_count": individual_count,  # 1 observacion = 1 individuo en este modelo
        "image_count": image_count,
        "observations": list(observations_by_obsid.values()),
        "images": images,
    }

    out_path = Path(r"D:\Anura\validation\new_species_test\fixture\fixture_manifest.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"[OK] individual_count={individual_count}, observation_count={individual_count}, image_count={image_count}")
    print(f"[OK] {image_count} imagenes agrupadas en {individual_count} observaciones/individuos "
          f"(NO {image_count} individuos independientes)")
    print(f"[OK] Manifest fixture: {out_path}")


if __name__ == "__main__":
    main()
