"""
build_catalog_release_manifest.py — Construye visual_catalog/{release}/manifest.json REFERENCIANDO
los artefactos reales de Fase 13, sin copiarlos ni moverlos.

Este script es aditivo: crea un manifest nuevo que apunta (por ruta relativa + hash) a archivos
ya existentes. No modifica, mueve ni elimina ningun archivo de evaluation/fase13/.

CORRECCION (post-auditoria de build_regional_package.py): el manifest ahora incluye
"species_ids": [...] resuelto vía taxonomic_resolution.py (mismo mecanismo de canonico()
que training/taxonomia.py ya tenia, no un join por nombre ad-hoc). Esto permite que un
paquete regional pregunte "¿este species_id pertenece a ESTE release especifico?" en vez
de asumir que el registry global completo pertenece a cualquier release.

Uso:
    python build_catalog_release_manifest.py \
        --frozen-config evaluation/fase13/selection/frozen_rejection_config.json \
        --centroid-audit evaluation/fase13/final_evaluation/centroid_source_audit.json \
        --metrics evaluation/fase13/final_evaluation/FASE13_FINAL_METRICS.json \
        --encoder-sha256 219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad \
        --taxonomia training/taxonomia.py \
        --species-registry taxonomy/species/species_registry.json \
        --out visual_catalog/v1.0.0/manifest.json
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from taxonomic_resolution import SpeciesResolver


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--frozen-config", required=True)
    ap.add_argument("--centroid-audit", required=True)
    ap.add_argument("--metrics", required=True)
    ap.add_argument("--encoder-sha256", required=True)
    ap.add_argument("--taxonomia", default="training/taxonomia.py")
    ap.add_argument("--species-registry", default="taxonomy/species/species_registry.json")
    ap.add_argument("--catalog-release-name", default="visual_catalog_1.0.0")
    ap.add_argument("--out", required=True)
    ap.add_argument("--supersedes", default=None)
    args = ap.parse_args()

    with open(args.frozen_config, encoding="utf-8") as f:
        frozen = json.load(f)
    with open(args.centroid_audit, encoding="utf-8") as f:
        centroid_audit = json.load(f)
    with open(args.metrics, encoding="utf-8") as f:
        metrics = json.load(f)

    resolver = SpeciesResolver(Path(args.taxonomia), Path(args.species_registry))

    # ── Resolver cada especie del centroid_audit a species_id (via canonico(), no por string crudo) ──
    species_ids = []
    unresolved = []
    for raw_name in centroid_audit["species_details"].keys():
        result = resolver.resolve(raw_name)
        if result["resolution_status"] == "RESOLVED":
            species_ids.append(result["species_id"])
        else:
            unresolved.append(result)

    if unresolved:
        print(f"[WARNING] {len(unresolved)} especies del catalog_release NO se pudieron resolver "
              f"a species_id (quedan fuera de species_ids[], reportadas en 'unresolved_species'):")
        for u in unresolved:
            print(f"    - '{u['raw_name']}' -> canonico='{u['canonical_name']}' -> NOT_IN_REGISTRY")

    manifest = {
        "catalog_release": args.catalog_release_name,
        "species_count": centroid_audit["total_centroids"],
        "species_ids": sorted(species_ids),
        "unresolved_species": unresolved,
        "group_a_count": centroid_audit["group_a_count"],
        "group_b_count": centroid_audit["group_b_count"],
        "method": frozen["selected_method"],
        "threshold_frozen": frozen["selected_threshold_tau_95KAR"],
        "encoder_sha256": args.encoder_sha256,
        "status": "FROZEN",
        "validation_report": "validation/v1.0.0/validation_report.json",
        "supersedes": args.supersedes,
        "source_artifacts": {
            "note": "Rutas relativas a artefactos EXISTENTES, no copiados. No modificar los originales.",
            "frozen_rejection_config": str(args.frozen_config),
            "centroid_source_audit": str(args.centroid_audit),
            "final_metrics": str(args.metrics),
            "species_registry": str(args.species_registry),
            "reference_embeddings": "evaluation/fase13/embeddings/reference_embeddings.npz",
            "calibration_embeddings": "evaluation/fase13/embeddings/calibration_embeddings.npz",
            "train_embeddings": "evaluation/fase13/embeddings/train_embeddings.npz",
        },
        "evidence_summary": {
            "auroc": metrics.get("auroc_out_of_sample"),
            "kar": metrics.get("kar_known_total"),
            "udr": metrics.get("udr_unknown_total"),
            "far": metrics.get("far_unknown_total"),
        }
    }

    if len(species_ids) != len(set(species_ids)):
        print("[ERROR] species_ids duplicados detectados en el release — esto no debería ocurrir "
              "si species_registry.json no tiene colisiones.")
        sys.exit(1)

    if len(species_ids) != centroid_audit["total_centroids"] - len(unresolved) or \
       len(species_ids) + len(unresolved) != centroid_audit["total_centroids"]:
        print(f"[WARNING] species_ids ({len(species_ids)}) + unresolved ({len(unresolved)}) "
              f"no suman exactamente total_centroids ({centroid_audit['total_centroids']}) — revisar manualmente.")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Manifest de catalog_release generado: {out_path}")
    print(f"     catalog_release = {manifest['catalog_release']}")
    print(f"     species_count = {manifest['species_count']} "
          f"(A={manifest['group_a_count']}, B={manifest['group_b_count']})")
    print(f"     species_ids resueltos = {len(species_ids)}")
    print(f"     unresolved = {len(unresolved)}")
    print(f"     status = {manifest['status']}")


if __name__ == "__main__":
    main()
