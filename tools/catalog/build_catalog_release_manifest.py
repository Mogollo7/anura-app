"""
build_catalog_release_manifest.py — Construye visual_catalog/v1.0.0/manifest.json REFERENCIANDO
los artefactos reales de Fase 13, sin copiarlos ni moverlos.

Este script es aditivo: crea un manifest nuevo que apunta (por ruta relativa + hash) a archivos
ya existentes. No modifica, mueve ni elimina ningun archivo de evaluation/fase13/.

Uso:
    python build_catalog_release_manifest.py \
        --frozen-config evaluation/fase13/selection/frozen_rejection_config.json \
        --centroid-audit evaluation/fase13/final_evaluation/centroid_source_audit.json \
        --metrics evaluation/fase13/final_evaluation/FASE13_FINAL_METRICS.json \
        --encoder-sha256 219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad \
        --out visual_catalog/v1.0.0/manifest.json
"""
import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--frozen-config", required=True)
    ap.add_argument("--centroid-audit", required=True)
    ap.add_argument("--metrics", required=True)
    ap.add_argument("--encoder-sha256", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--supersedes", default=None)
    args = ap.parse_args()

    with open(args.frozen_config, encoding="utf-8") as f:
        frozen = json.load(f)
    with open(args.centroid_audit, encoding="utf-8") as f:
        centroid_audit = json.load(f)
    with open(args.metrics, encoding="utf-8") as f:
        metrics = json.load(f)

    manifest = {
        "catalog_release": "visual_catalog_1.0.0",
        "species_count": centroid_audit["total_centroids"],
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

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"[OK] Manifest de catalog_release generado: {out_path}")
    print(f"     catalog_release = {manifest['catalog_release']}")
    print(f"     species_count = {manifest['species_count']} "
          f"(A={manifest['group_a_count']}, B={manifest['group_b_count']})")
    print(f"     status = {manifest['status']}")


if __name__ == "__main__":
    main()
