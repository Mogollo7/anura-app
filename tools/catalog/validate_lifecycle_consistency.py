"""
validate_lifecycle_consistency.py — Verifica que ninguna especie tenga
visual_lifecycle_status=DEPLOYED sin estar realmente presente en species_ids[] de
al menos un catalog_release real con status FROZEN.

Motivo: generate_species_id.py hereda el lifecycle de un registry previo por diseño
(para preservar el historial de las 41 especies), pero eso significa que una entrada
incorrecta ya persistida (ej. por una ejecucion externa con codigo viejo, o edicion
manual) se perpetua indefinidamente sin este chequeo. Este script la detecta.

Uso:
    python validate_lifecycle_consistency.py \
        --species-registry taxonomy/species/species_registry.json \
        --catalog-release-manifests visual_catalog/v1.0.0/manifest.json
"""
import argparse
import json
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--species-registry", default="taxonomy/species/species_registry.json")
    ap.add_argument("--catalog-release-manifests", nargs="+", required=True,
                     help="Uno o mas manifests de catalog_release con status FROZEN")
    args = ap.parse_args()

    with open(args.species_registry, encoding="utf-8") as f:
        registry = json.load(f)

    deployed_ids_from_releases = set()
    for manifest_path in args.catalog_release_manifests:
        with open(manifest_path, encoding="utf-8") as f:
            catalog = json.load(f)
        if catalog.get("status") == "FROZEN":
            deployed_ids_from_releases.update(catalog.get("species_ids", []))

    inconsistencies = []
    for sp in registry["species"]:
        if sp["visual_lifecycle_status"] == "DEPLOYED" and sp["species_id"] not in deployed_ids_from_releases:
            inconsistencies.append(sp["species_id"])

    print(f"=== VALIDACION DE CONSISTENCIA LIFECYCLE ===")
    print(f"Especies DEPLOYED en registry: "
          f"{sum(1 for s in registry['species'] if s['visual_lifecycle_status']=='DEPLOYED')}")
    print(f"Especies en algun catalog_release FROZEN: {len(deployed_ids_from_releases)}")
    print(f"Inconsistencias (DEPLOYED sin estar en ningun release FROZEN): {len(inconsistencies)}")
    for sid in inconsistencies:
        print(f"  - {sid}")

    if inconsistencies:
        print("\nRESULTADO: FAIL")
        sys.exit(1)
    print("\nRESULTADO: PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
