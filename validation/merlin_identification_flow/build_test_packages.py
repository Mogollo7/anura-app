"""Construye paquetes REALES a partir de artefactos ya existentes.

Fuentes (solo lectura, no se modifican):
  - evaluation/fase13/embeddings/{reference,train}_embeddings.npz  -> prototipos
  - taxonomy/species/species_registry.json                         -> metadata
  - regional_packages/{ANTIOQUIA,CAUCA}/v1.0.0/manifest.json       -> alcance
  - visual_similarity_groups.json                                  -> grupos

Salida: `package_repository/<package_id>/<version>/` (fuente filesystem
distribuible, separada de `packages_root/` que es el estado local instalado).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from package_manager import build_package  # noqa: E402
from runtime_adapters import VisualRankingAdapter  # noqa: E402

REPOSITORY = HERE / "package_repository"


def main() -> None:
    registry = json.loads((ROOT / "taxonomy/species/species_registry.json").read_text(encoding="utf-8"))
    by_id = {item["species_id"]: item for item in registry["species"]}
    id_by_name = {item["scientific_name"]: item["species_id"] for item in registry["species"]}

    adapter = VisualRankingAdapter()
    centroid_by_id = {
        id_by_name[name]: adapter.centroids[index]
        for index, name in enumerate(adapter.names)
        if name in id_by_name
    }
    catalog = json.loads((ROOT / "visual_catalog/v1.0.0/manifest.json").read_text(encoding="utf-8"))
    catalog_ids = set(catalog["species_ids"])

    groups_doc = json.loads((HERE / "visual_similarity_groups.json").read_text(encoding="utf-8"))
    all_groups = groups_doc["groups"]

    built = []
    for package_id, regional in [
        ("anura_antioquia_visual", "ANTIOQUIA"),
        ("anura_cauca_visual", "CAUCA"),
    ]:
        manifest = json.loads(
            (ROOT / f"regional_packages/{regional}/v1.0.0/manifest.json").read_text(encoding="utf-8")
        )
        ids = sorted(
            sid
            for sid in manifest["visual_classifier_scope"]["species_ids"]
            if sid in catalog_ids and sid in centroid_by_id
        )
        species = [
            {
                "species_id": sid,
                "scientific_name": by_id[sid]["scientific_name"],
                "family": by_id[sid].get("family"),
                "genus": by_id[sid].get("genus"),
                "common_name": by_id[sid].get("common_name"),
                "taxonomic_status": by_id[sid].get("taxonomic_status"),
            }
            for sid in ids
        ]
        scoped_groups = [
            group for group in all_groups if sum(1 for s in group["species_ids"] if s in set(ids)) >= 2
        ]
        target = build_package(
            REPOSITORY / package_id / "v1.0.0",
            package_id=package_id,
            package_version="v1.0.0",
            species=species,
            prototypes={sid: centroid_by_id[sid] for sid in ids},
            prototype_version="fase13_geo6_centroids/v1.0.0",
            visual_similarity_groups=scoped_groups,
            dependencies=[],
            minimum_app_version="0.1.0",
            source_artifacts={
                "regional_scope": f"regional_packages/{regional}/v1.0.0/manifest.json",
                "catalog_release": "visual_catalog/v1.0.0/manifest.json",
                "centroids": "evaluation/fase13/embeddings/{reference,train}_embeddings.npz",
                "species_metadata": "taxonomy/species/species_registry.json",
            },
        )
        built.append({"package_id": package_id, "version": "v1.0.0", "species": len(ids), "path": str(target),
                      "groups": len(scoped_groups)})

    # Segunda version del paquete A (v1.0.1) para probar convivencia de versiones:
    # mismo contenido menos una especie, para que el payload_sha256 difiera.
    base = json.loads((REPOSITORY / "anura_antioquia_visual/v1.0.0/manifest.json").read_text(encoding="utf-8"))
    reduced = [sid for sid in base["species_ids"] if sid != "ANU_COL_SCIN_RUB_001"]
    species = [
        {
            "species_id": sid,
            "scientific_name": by_id[sid]["scientific_name"],
            "family": by_id[sid].get("family"),
            "genus": by_id[sid].get("genus"),
            "common_name": by_id[sid].get("common_name"),
            "taxonomic_status": by_id[sid].get("taxonomic_status"),
        }
        for sid in reduced
    ]
    scoped_groups = [g for g in all_groups if sum(1 for s in g["species_ids"] if s in set(reduced)) >= 2]
    build_package(
        REPOSITORY / "anura_antioquia_visual" / "v1.0.1",
        package_id="anura_antioquia_visual",
        package_version="v1.0.1",
        species=species,
        prototypes={sid: centroid_by_id[sid] for sid in reduced},
        prototype_version="fase13_geo6_centroids/v1.0.0",
        visual_similarity_groups=scoped_groups,
        source_artifacts={"note": "v1.0.1 de prueba: v1.0.0 sin Scinax ruber, para validar coexistencia de versiones"},
    )
    built.append({"package_id": "anura_antioquia_visual", "version": "v1.0.1", "species": len(reduced),
                  "path": str(REPOSITORY / "anura_antioquia_visual/v1.0.1"), "groups": len(scoped_groups)})

    print(json.dumps(built, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
