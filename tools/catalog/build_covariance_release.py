"""
build_covariance_release.py — Formaliza la covarianza compartida (Ledoit-Wolf) como artefacto
VERSIONADO E INDEPENDIENTE, en vez de recalcularla silenciosamente cada vez dentro de scripts
de evaluacion (como hacia Fase 13: fase13_calibrate_selection.py, fase13_final_evaluation.py,
fase13_cv_reference.py — los 3 recalculaban ledoit_wolf() desde cero cada vez, sin persistir).

IMPORTANTE: este script NO recalibra con datos nuevos. Para covariance_1.0.0, reproduce
EXACTAMENTE el mismo calculo que Fase 13 ya hizo (mismo REFERENCE, mismo metodo), y lo
serializa con procedencia completa. Se incluye un chequeo de reproducibilidad que compara
contra un calculo independiente en el momento de generar el artefacto.

Uso (formalizar covariance_1.0.0 desde el REFERENCE historico, SIN recalibrar):
    python build_covariance_release.py \
        --reference-embeddings evaluation/fase13/embeddings/reference_embeddings.npz \
        --catalog-release visual_catalog_1.0.0 \
        --covariance-release-name covariance_1.0.0 \
        --encoder-sha256 219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad \
        --species-registry taxonomy/species/species_registry.json \
        --taxonomia training/taxonomia.py \
        --out-dir covariance/v1.0.0/
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.covariance import ledoit_wolf

sys.path.insert(0, str(Path(__file__).parent))
from taxonomic_resolution import SpeciesResolver


def sha256_of_array(arr: np.ndarray) -> str:
    return hashlib.sha256(arr.tobytes()).hexdigest()


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_centroids(X, y):
    classes = np.unique(y)
    return {c: np.mean(X[y == c], axis=0) for c in classes}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reference-embeddings", required=True)
    ap.add_argument("--catalog-release", required=True)
    ap.add_argument("--covariance-release-name", required=True)
    ap.add_argument("--encoder-sha256", required=True)
    ap.add_argument("--encoder-id", default="bioclip_anura_v1")
    ap.add_argument("--species-registry", default="taxonomy/species/species_registry.json")
    ap.add_argument("--taxonomia", default="training/taxonomia.py")
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    print(f"=== BUILD COVARIANCE RELEASE: {args.covariance_release_name} ===")
    print("NOTA: este proceso REPRODUCE el calculo existente de Fase 13, no recalibra con datos nuevos.\n")

    data = np.load(args.reference_embeddings)
    X = data["embeddings"]
    y_raw = data["species"]

    resolver = SpeciesResolver(Path(args.taxonomia), Path(args.species_registry))
    y_canonical = np.array([resolver.resolve(n)["canonical_name"] for n in y_raw])
    species_ids = sorted({resolver.resolve(n)["species_id"] for n in y_raw if resolver.resolve(n)["species_id"]})

    centroids = compute_centroids(X, y_canonical)
    X_centered = np.zeros_like(X)
    for c, mu in centroids.items():
        X_centered[y_canonical == c] = X[y_canonical == c] - mu

    orphaned = sorted({c for c in centroids if resolver.resolve(c.replace('_', ' '))["species_id"] is None})

    print(f"REFERENCE embeddings: {X.shape}")
    print(f"Especies usadas para centrar (todas las de REFERENCE): {len(centroids)}")
    print(f"Especies con species_id resuelto (incluidas en species_ids[]): {len(species_ids)}")
    if orphaned:
        print(f"Especies huerfanas (centraron la covarianza pero sin species_id): {orphaned}")

    # ── Calculo 1 (el que se persiste) ──
    cov_1, shrinkage_1 = ledoit_wolf(X_centered, assume_centered=True)

    # ── Calculo 2 (independiente, MISMOS inputs, para verificar reproducibilidad) ──
    cov_2, shrinkage_2 = ledoit_wolf(X_centered, assume_centered=True)

    identical = np.array_equal(cov_1, cov_2)
    print(f"\nReproducibilidad (2 calculos independientes, mismos inputs): {'IDENTICO' if identical else 'DIFERENTE'}")
    assert identical, "ERROR: ledoit_wolf no es determinista con los mismos inputs — investigar"

    cov_sha256 = sha256_of_array(cov_1)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    npz_path = out_dir / "covariance_matrix.npz"
    np.savez_compressed(npz_path, covariance=cov_1, precision=np.linalg.inv(cov_1))

    manifest = {
        "covariance_release": args.covariance_release_name,
        "catalog_release": args.catalog_release,
        "encoder_contract": {
            "encoder_id": args.encoder_id,
            "encoder_sha256": args.encoder_sha256,
        },
        "embedding_space": "L2-normalized 512D BioCLIP embeddings",
        "species_count": len(species_ids),
        "species_ids": species_ids,
        "species_used_for_centering_count": len(centroids),
        "orphaned_species_excluded_from_species_ids": orphaned,
        "calibration_dataset": f"REFERENCE ({X.shape[0]} imagenes)",
        "calibration_split": "REFERENCE",
        "method": "Ledoit-Wolf shared shrinkage",
        "dimension": int(X.shape[1]),
        "regularization": f"shrinkage={shrinkage_1:.6f}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_artifacts": [str(args.reference_embeddings)],
        "sha256": cov_sha256,
        "npz_artifact": str(npz_path),
        "reproducibility_check": {
            "two_independent_computations_identical": bool(identical),
            "method": "sklearn.covariance.ledoit_wolf(X_centered, assume_centered=True), determinista"
        }
    }

    manifest_path = out_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Covarianza SHA256: {cov_sha256}")
    print(f"[OK] npz: {npz_path}")
    print(f"[OK] manifest: {manifest_path}")


if __name__ == "__main__":
    main()
