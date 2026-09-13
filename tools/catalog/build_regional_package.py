"""
build_regional_package.py — Generador CANÓNICO de paquete regional.

Unifica (sin fusionar código, sin eliminar ninguno de los dos) las dos fuentes de verdad
que hoy existen por separado:

  1. Catálogo REGIONAL / biodiversidad (pipeline_dataset/construir_paquete_departamental.py)
     → produce COLOMBIA_ANURA/{DEPTO}/metadata/package.json + SPECIES/*/species.json
     → responde: "¿qué especies existen/tienen ocurrencia confirmada en este departamento?"

  2. Catálogo VISUAL versionado (tools/catalog/build_catalog_release_manifest.py)
     → produce visual_catalog/{release}/manifest.json, con "species_ids": [...] explícito
     → responde: "¿qué especies puede identificar ESTE release específico del clasificador?"

CORRECCION DE DISEÑO (v2): el join entre ambos sistemas ahora es por species_id, NO por
nombre científico. El nombre científico nunca se usa aquí como clave de relación:

    regional species.json (nombre crudo)
            │
            ▼  (resuelto previamente por resolve_regional_species_ids.py, NO en este script)
    species_id_resolution.json  ──────────┐
                                           │
                                           ▼
                              visual_catalog/{release}/manifest.json
                                    "species_ids": [...]
                                           │
                                           ▼
                              set intersection por species_id

Esto permite que la pregunta sea inequívocamente "¿este species_id pertenece a ESTE release
específico?", no "¿está en el registry global?" — un release 1.1.0 con especies nuevas NO
las reporta como soportadas si se le pide construir contra 1.0.0.

Prerrequisitos (no se generan aquí si faltan — se reporta y se detiene):
  - COLOMBIA_ANURA/{DEPARTMENT}/metadata/package.json
        → python pipeline_dataset/construir_paquete_departamental.py --departamento {DEPARTMENT}
  - COLOMBIA_ANURA/{DEPARTMENT}/metadata/species_id_resolution.json
        → python tools/catalog/resolve_regional_species_ids.py --department {DEPARTMENT}
  - visual_catalog/{release}/manifest.json (con "species_ids": [...])
        → python tools/catalog/build_catalog_release_manifest.py ...

Uso:
    python tools/catalog/build_regional_package.py \
        --department ANTIOQUIA \
        --catalog-release visual_catalog_1.0.0 \
        --output regional_packages/ANTIOQUIA/v1.0.0/
"""
import argparse
import json
import sys
from pathlib import Path


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--department", required=True, help="ej. ANTIOQUIA")
    ap.add_argument("--catalog-release", required=True, help="ej. visual_catalog_1.0.0")
    ap.add_argument("--output", required=True, help="Directorio de salida, ej. regional_packages/ANTIOQUIA/v1.0.0/")
    ap.add_argument("--package-version", default=None)
    ap.add_argument("--validation-status", default="PILOT", choices=["PILOT", "FIELD_VALIDATED", "PRODUCTION"])
    ap.add_argument("--colombia-anura-root", default="COLOMBIA_ANURA")
    ap.add_argument("--visual-catalog-root", default="visual_catalog")
    ap.add_argument("--visual-catalog-manifest", default=None,
                     help="Ruta explicita al manifest del release, para testing con fixtures fuera del arbol real")
    args = ap.parse_args()

    department = args.department.strip().upper()

    # ── 1. Prerrequisito: catálogo regional (biodiversidad) ──
    department_dir = Path(args.colombia_anura_root) / department
    regional_package_path = department_dir / "metadata" / "package.json"
    if not regional_package_path.exists():
        print(f"[ERROR] No existe {regional_package_path}")
        print(f"        Generar con: python pipeline_dataset/construir_paquete_departamental.py --departamento {department}")
        sys.exit(1)
    regional_package = load_json(regional_package_path)

    # ── 2. Prerrequisito: resolución de species_id regional (NO nombre crudo) ──
    resolution_path = department_dir / "metadata" / "species_id_resolution.json"
    if not resolution_path.exists():
        print(f"[ERROR] No existe {resolution_path}")
        print(f"        Generar con: python tools/catalog/resolve_regional_species_ids.py --department {department}")
        sys.exit(1)
    resolution = load_json(resolution_path)

    # ── 3. Prerrequisito: catalog_release visual con species_ids explícitos ──
    if args.visual_catalog_manifest:
        catalog_release_path = Path(args.visual_catalog_manifest)
    else:
        catalog_release_path = Path(args.visual_catalog_root) / args.catalog_release.replace("visual_catalog_", "v") / "manifest.json"
        if not catalog_release_path.exists():
            alt = Path(args.visual_catalog_root) / args.catalog_release / "manifest.json"
            if alt.exists():
                catalog_release_path = alt

    if not catalog_release_path.exists():
        print(f"[ERROR] No existe manifest de catalog_release en {catalog_release_path}")
        print(f"        Generar con tools/catalog/build_catalog_release_manifest.py")
        sys.exit(1)
    catalog_release = load_json(catalog_release_path)

    if "species_ids" not in catalog_release:
        print(f"[ERROR] {catalog_release_path} no contiene 'species_ids' — regenerar con la version "
              f"corregida de build_catalog_release_manifest.py")
        sys.exit(1)

    release_species_ids = set(catalog_release["species_ids"])

    if catalog_release.get("status") not in ("FROZEN", "TEST_SIMULATION"):
        print(f"[WARNING] catalog_release '{args.catalog_release}' status="
              f"{catalog_release.get('status')}, no FROZEN.")

    # ── 4. JOIN POR species_id (no por nombre) ──
    visual_supported_ids = []
    regional_present_count = 0
    regional_without_visual_support = []       # resuelto a species_id, pero NO en este release
    regional_taxonomically_unresolved = []      # ni siquiera se pudo resolver a species_id

    for r in resolution["resolutions"]:
        if r.get("occurrences_in_department", 0) <= 0:
            continue
        regional_present_count += 1

        species_id = r["species_id"]
        if species_id is None:
            regional_taxonomically_unresolved.append(r["scientific_name"])
            continue

        if species_id in release_species_ids:
            visual_supported_ids.append(species_id)
        else:
            regional_without_visual_support.append({
                "scientific_name": r["scientific_name"],
                "species_id": species_id,
                "reason": f"species_id resuelto pero NO pertenece a {args.catalog_release}"
            })

    # ── 5. Construir regional_package ──
    package_version = args.package_version or Path(args.output.rstrip("/\\")).name

    manifest = {
        "package_id": department,
        "package_version": package_version,
        "catalog_release": args.catalog_release,
        "validation_status": args.validation_status,
        "regional_catalog_scope": {
            "species_present_estimated": regional_package.get("species_in_department", regional_present_count),
            "geobounds_reference": regional_package.get("geographic_assignment", {}).get("source"),
            "source_package": str(regional_package_path),
            "generated_on": regional_package.get("generated_on"),
            "data_status_counts": regional_package.get("data_status_counts"),
            "caveat": regional_package.get("caveat"),
        },
        "visual_classifier_scope": {
            "species_supported": len(visual_supported_ids),
            "species_ids": sorted(visual_supported_ids),
            "source_catalog_release_manifest": str(catalog_release_path),
            "join_method": "species_id (set intersection contra catalog_release.species_ids)",
        },
        "regional_species_without_visual_support": regional_without_visual_support,
        "regional_species_taxonomically_unresolved": sorted(regional_taxonomically_unresolved),
        "notes": [
            "regional_catalog_scope = biodiversidad/presencia (fuente: construir_paquete_departamental.py).",
            "visual_classifier_scope = interseccion por species_id contra catalog_release.species_ids "
            "del release especifico solicitado. Presencia regional NO implica soporte visual.",
            "El join usa species_id como clave, resuelto previamente por resolve_regional_species_ids.py "
            "via taxonomia.canonico() (incluye alias conocidos como acanthinus->achatinus). El nombre "
            "cientifico NUNCA se usa como clave de relacion en este script.",
            f"{len(regional_without_visual_support)} especies resueltas a species_id pero ausentes de "
            f"{args.catalog_release} (pueden existir en un release posterior).",
            f"{len(regional_taxonomically_unresolved)} especies regionales sin species_id "
            "(no estan en species_registry.json, ej. excluidas del catalogo visual).",
        ],
    }

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "manifest.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n=== PAQUETE REGIONAL UNIFICADO: {department} ===")
    print(f"catalog_release: {args.catalog_release} ({len(release_species_ids)} species_ids en el release)")
    print(f"Especies presentes en {department} (regional_catalog_scope): "
          f"{manifest['regional_catalog_scope']['species_present_estimated']}")
    print(f"Especies con soporte visual EN ESTE RELEASE: {len(visual_supported_ids)}")
    print(f"Especies resueltas pero fuera de este release: {len(regional_without_visual_support)}")
    for x in regional_without_visual_support:
        print(f"    - {x['scientific_name']} ({x['species_id']}) — {x['reason']}")
    print(f"Especies sin species_id (no resueltas taxonomicamente): {len(regional_taxonomically_unresolved)}")
    for n in regional_taxonomically_unresolved:
        print(f"    - {n}")
    print(f"\n[OK] Manifest escrito en: {out_path}")


if __name__ == "__main__":
    main()
