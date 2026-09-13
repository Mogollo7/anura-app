"""
resolve_regional_species_ids.py — Resuelve species_id para cada especie de un paquete regional
YA GENERADO por pipeline_dataset/construir_paquete_departamental.py, sin modificar sus archivos.

Lee COLOMBIA_ANURA/{DEPARTMENT}/SPECIES/*/species.json (scientific_name), resuelve cada uno
via taxonomic_resolution.SpeciesResolver (mismo canonico() de training/taxonomia.py) y escribe
un artefacto NUEVO y separado: COLOMBIA_ANURA/{DEPARTMENT}/metadata/species_id_resolution.json

Esto cierra el flujo pedido:
    regional species.json (nombre crudo)
        -> canonico()
        -> species_registry.json
        -> species_id
        -> (build_regional_package.py hace el join final por species_id, no por nombre)

Uso:
    python resolve_regional_species_ids.py --department ANTIOQUIA \
        --taxonomia training/taxonomia.py \
        --species-registry taxonomy/species/species_registry.json
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from taxonomic_resolution import SpeciesResolver


def load_regional_species(department_dir: Path) -> list[dict]:
    species_dir = department_dir / "SPECIES"
    if not species_dir.exists():
        return []
    records = []
    for sp_dir in sorted(species_dir.iterdir()):
        sp_json = sp_dir / "species.json"
        if sp_json.exists():
            with open(sp_json, "r", encoding="utf-8") as f:
                records.append(json.load(f))
    return records


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--department", required=True)
    ap.add_argument("--taxonomia", default="training/taxonomia.py")
    ap.add_argument("--species-registry", default="taxonomy/species/species_registry.json")
    ap.add_argument("--colombia-anura-root", default="COLOMBIA_ANURA")
    args = ap.parse_args()

    department = args.department.strip().upper()
    department_dir = Path(args.colombia_anura_root) / department

    regional_species = load_regional_species(department_dir)
    if not regional_species:
        print(f"[ERROR] No hay especies en {department_dir / 'SPECIES'}")
        sys.exit(1)

    resolver = SpeciesResolver(Path(args.taxonomia), Path(args.species_registry))

    resolutions = []
    for sp in regional_species:
        result = resolver.resolve(sp["scientific_name"])
        resolutions.append({
            "taxon_id": sp["taxon_id"],
            "scientific_name": sp["scientific_name"],
            "canonical_name": result["canonical_name"],
            "species_id": result["species_id"],
            "resolution_status": result["resolution_status"],
            "occurrences_in_department": sp.get("occurrences_in_department", 0),
        })

    resolved_count = sum(1 for r in resolutions if r["resolution_status"] == "RESOLVED")
    unresolved_count = len(resolutions) - resolved_count

    out = {
        "department": department,
        "source": "COLOMBIA_ANURA/{}/SPECIES/*/species.json (no modificado)".format(department),
        "taxonomia_source": str(args.taxonomia),
        "species_registry_source": str(args.species_registry),
        "total_species": len(resolutions),
        "resolved_count": resolved_count,
        "unresolved_count": unresolved_count,
        "resolutions": resolutions,
    }

    out_path = department_dir / "metadata" / "species_id_resolution.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"=== RESOLUCION DE species_id: {department} ===")
    print(f"Total especies regionales: {len(resolutions)}")
    print(f"Resueltas a species_id:    {resolved_count}")
    print(f"NO resueltas:              {unresolved_count}")
    if unresolved_count:
        print("Especies no resueltas (no estan en species_registry.json, ej. excluidas del catalogo visual):")
        for r in resolutions:
            if r["resolution_status"] != "RESOLVED":
                print(f"    - {r['scientific_name']} (canonico={r['canonical_name']})")
    print(f"\n[OK] Escrito en: {out_path}")


if __name__ == "__main__":
    main()
