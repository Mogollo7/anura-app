"""
run_open_set_evaluation.py — Evaluacion Open Set REPRODUCIBLE, usando artefactos VERSIONADOS
(covariance_release, threshold_release) en vez de recalcularlos ad-hoc como hacia
fase13_final_evaluation.py. Verifica compatibilidad ANTES de evaluar.

Separa explicitamente:
    KNOWN         -> especie pertenece al catalog_release
    UNKNOWN       -> especie NO pertenece al catalog_release (pero se evalua igual)
    NO_CONCLUSIVE -> score en zona ambigua (opcional, si se pasa --margin)

Reporta: AUROC, AUPR, KAR, UDR, FAR, FRR, precision, recall, F1, distribucion de distancias.

Uso (regresion contra F3/F4 real, usando artefactos v1.0.0 ya formalizados):
    python run_open_set_evaluation.py \
        --catalog-release-manifest visual_catalog/v1.0.0/manifest.json \
        --covariance-release-manifest covariance/v1.0.0/manifest.json \
        --covariance-npz covariance/v1.0.0/covariance_matrix.npz \
        --threshold-release-manifest threshold/v1.0.0/manifest.json \
        --reference-embeddings evaluation/fase13/embeddings/reference_embeddings.npz \
        --train-embeddings evaluation/fase13/embeddings/train_embeddings.npz \
        --eval-embeddings evaluation/open_set_v1/knn/knn_embeddings.npz \
        --eval-labels evaluation/open_set_v1/knn/knn_open_set_results.json \
        --taxonomia training/taxonomia.py \
        --species-registry taxonomy/species/species_registry.json \
        --out validation/new_species_test/open_set_eval_v1.0.0_reproduced.json
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc, precision_score, recall_score, f1_score

sys.path.insert(0, str(Path(__file__).parent))
from taxonomic_resolution import SpeciesResolver


def compute_centroids(X, y):
    return {c: np.mean(X[y == c], axis=0) for c in np.unique(y)}


def min_mahalanobis(X, centroids, precision_matrix):
    classes = list(centroids.keys())
    C = np.array([centroids[c] for c in classes])
    diff = X[:, None, :] - C[None, :, :]
    d2 = np.einsum("nkd,de,nke->nk", diff, precision_matrix, diff)
    return np.sqrt(np.maximum(0.0, np.min(d2, axis=1)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--catalog-release-manifest", required=True)
    ap.add_argument("--covariance-release-manifest", required=True)
    ap.add_argument("--covariance-npz", required=True)
    ap.add_argument("--threshold-release-manifest", required=True)
    ap.add_argument("--reference-embeddings", required=True)
    ap.add_argument("--train-embeddings", required=True)
    ap.add_argument("--eval-embeddings", required=True)
    ap.add_argument("--eval-labels", required=True)
    ap.add_argument("--taxonomia", default="training/taxonomia.py")
    ap.add_argument("--species-registry", default="taxonomy/species/species_registry.json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--skip-compatibility-check", action="store_true")
    args = ap.parse_args()

    # ── Paso 0: verificar compatibilidad ANTES de evaluar ──
    if not args.skip_compatibility_check:
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent / "check_release_compatibility.py"),
             "--catalog-release-manifest", args.catalog_release_manifest,
             "--covariance-release-manifest", args.covariance_release_manifest,
             "--threshold-release-manifest", args.threshold_release_manifest],
            capture_output=True, text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print("[ABORT] Releases incompatibles — evaluacion Open Set NO ejecutada.")
            sys.exit(1)

    with open(args.catalog_release_manifest, encoding="utf-8") as f:
        catalog = json.load(f)
    with open(args.threshold_release_manifest, encoding="utf-8") as f:
        threshold_release = json.load(f)

    cov_data = np.load(args.covariance_npz)
    precision_matrix = cov_data["precision"]
    tau = threshold_release["threshold"]
    release_species_ids = set(catalog["species_ids"])

    resolver = SpeciesResolver(Path(args.taxonomia), Path(args.species_registry))

    ref = np.load(args.reference_embeddings)
    train = np.load(args.train_embeddings)

    ref_canonical = np.array([resolver.resolve(n)["canonical_name"] for n in ref["species"]])
    train_canonical = np.array([resolver.resolve(n)["canonical_name"] for n in train["species"]])

    ref_centroids = compute_centroids(ref["embeddings"], ref_canonical)
    train_centroids = compute_centroids(train["embeddings"], train_canonical)

    # Centroides: Group A desde REFERENCE tiene prioridad; Group B desde TRAIN completa el resto,
    # SOLO para especies que pertenecen al catalog_release (species_ids)
    all_centroids = {}
    for name, c in ref_centroids.items():
        sid = resolver.resolve(name.replace("_", " "))["species_id"]
        if sid in release_species_ids:
            all_centroids[sid] = c
    for name, c in train_centroids.items():
        sid = resolver.resolve(name.replace("_", " "))["species_id"]
        if sid in release_species_ids and sid not in all_centroids:
            all_centroids[sid] = c

    print(f"Centroides disponibles para evaluacion: {len(all_centroids)} / {len(release_species_ids)} en el release")

    eval_emb = np.load(args.eval_embeddings)["embeddings"].astype(np.float32)
    with open(args.eval_labels, encoding="utf-8") as f:
        eval_records = json.load(f)["records"]

    scores = min_mahalanobis(eval_emb, all_centroids, precision_matrix)
    y_true = np.array([0 if r["known_unknown"] == "KNOWN" else 1 for r in eval_records])  # 0=KNOWN, 1=UNKNOWN

    decisions = np.where(scores <= tau, "ACCEPT", "REJECT")
    y_pred_unknown = (decisions == "REJECT").astype(int)

    known_mask = y_true == 0
    unknown_mask = y_true == 1

    auroc = float(roc_auc_score(y_true, scores))
    precision, recall, _ = precision_recall_curve(y_true, scores)
    aupr = float(auc(recall, precision))

    kar = float(np.mean(scores[known_mask] <= tau))       # Known Acceptance Rate
    udr = float(np.mean(scores[unknown_mask] > tau))       # Unknown Detection Rate
    far = float(np.mean(scores[unknown_mask] <= tau))      # False Acceptance Rate (unknown accepted)
    frr = float(np.mean(scores[known_mask] > tau))         # False Rejection Rate (known rejected)

    prec = float(precision_score(y_true, y_pred_unknown, zero_division=0))
    rec = float(recall_score(y_true, y_pred_unknown, zero_division=0))
    f1 = float(f1_score(y_true, y_pred_unknown, zero_division=0))

    report = {
        "catalog_release": catalog["catalog_release"],
        "covariance_release": threshold_release["covariance_release"],
        "threshold_release": threshold_release["threshold_release"],
        "threshold_used": tau,
        "n_known": int(known_mask.sum()),
        "n_unknown": int(unknown_mask.sum()),
        "metrics": {
            "auroc": auroc, "aupr": aupr, "kar": kar, "udr": udr, "far": far, "frr": frr,
            "precision_unknown": prec, "recall_unknown": rec, "f1_unknown": f1,
        },
        "score_distribution": {
            "known_mean": float(np.mean(scores[known_mask])), "known_std": float(np.std(scores[known_mask])),
            "unknown_mean": float(np.mean(scores[unknown_mask])), "unknown_std": float(np.std(scores[unknown_mask])),
        },
        "reused_artifacts": {
            "covariance_npz": str(args.covariance_npz),
            "threshold_release_manifest": str(args.threshold_release_manifest),
            "note": "Covariance NO fue recalculada aqui — se cargo directamente del .npz versionado."
        }
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n=== OPEN SET EVALUATION: {catalog['catalog_release']} ===")
    print(json.dumps(report["metrics"], indent=2))
    print(f"\n[OK] Guardado en {out_path}")


if __name__ == "__main__":
    main()
