"""
run_fase16_blind_test.py — FASE 16.9/16.10: ejecuta el blind test DESPUES del freeze,
usando covariance_1.1.0_CLEAN + threshold_1.1.0_CLEAN (ya congelados, sin recalibrar).

KNOWN = clean_known_embeddings.npz (7475 imgs, 24 especies, OUT_OF_SAMPLE verificado)
UNKNOWN = F4 embeddings (56 imgs, 2 especies, ya verificado limpio en Fase 15/16.1)

Clasifica cada caso en: KNOWN_ACCEPTED, KNOWN_REJECTED, UNKNOWN_REJECTED,
UNKNOWN_FALSE_ACCEPTED, NO_CONCLUSIVE (zona de margen alrededor del threshold, opcional).
"""
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import (roc_auc_score, precision_score, recall_score, f1_score,
                              balanced_accuracy_score)

ROOT = Path(r"D:\Anura")
sys.path.insert(0, str(ROOT / "tools" / "catalog"))
from taxonomic_resolution import SpeciesResolver

MARGIN_FRACTION = 0.05  # +-5% del threshold como zona NO_CONCLUSIVE


def compute_centroids(X, y):
    return {c: np.mean(X[y == c], axis=0) for c in np.unique(y)}


def min_mahalanobis(X, centroids, precision_matrix):
    classes = list(centroids.keys())
    C = np.array([centroids[c] for c in classes])
    diff = X[:, None, :] - C[None, :, :]
    d2 = np.einsum("nkd,de,nke->nk", diff, precision_matrix, diff)
    return np.sqrt(np.maximum(0.0, np.min(d2, axis=1)))


def main():
    OUT = ROOT / "validation" / "fase16_clean_open_set"

    with open(OUT / "fase16_freeze_manifest.json", encoding="utf-8") as f:
        freeze = json.load(f)
    tau = freeze["threshold_value_frozen"]
    print(f"Threshold congelado (freeze): {tau}\n")

    cov_data = np.load(ROOT / "covariance/v1.1.0_CLEAN/covariance_matrix.npz")
    precision_matrix = cov_data["precision"]

    # ── Centroides: Group A (REFERENCE) + Group B (TRAIN), identico a Fase 13/v1.0.0 ──
    resolver = SpeciesResolver(ROOT / "training/taxonomia.py", ROOT / "taxonomy/species/species_registry.json")
    ref = np.load(ROOT / "evaluation/fase13/embeddings/reference_embeddings.npz")
    train = np.load(ROOT / "evaluation/fase13/embeddings/train_embeddings.npz")

    ref_canon = np.array([resolver.resolve(n)["canonical_name"] for n in ref["species"]])
    train_canon = np.array([resolver.resolve(n)["canonical_name"] for n in train["species"]])
    ref_centroids = compute_centroids(ref["embeddings"], ref_canon)
    train_centroids = compute_centroids(train["embeddings"], train_canon)

    with open(ROOT / "visual_catalog/v1.0.0/manifest.json", encoding="utf-8") as f:
        catalog = json.load(f)
    release_ids = set(catalog["species_ids"])

    all_centroids = {}
    for name, c in ref_centroids.items():
        sid = resolver.resolve(name.replace("_", " "))["species_id"]
        if sid in release_ids:
            all_centroids[sid] = c
    for name, c in train_centroids.items():
        sid = resolver.resolve(name.replace("_", " "))["species_id"]
        if sid in release_ids and sid not in all_centroids:
            all_centroids[sid] = c
    print(f"Centroides disponibles: {len(all_centroids)} / {len(release_ids)} del release\n")

    # ── KNOWN (clean, out-of-sample) ──
    clean_data = np.load(OUT / "clean_known_embeddings.npz")
    X_known = clean_data["embeddings"]
    known_species_ids = clean_data["species_ids"]
    scores_known = min_mahalanobis(X_known, all_centroids, precision_matrix)

    # ── UNKNOWN (F4, ya verificado limpio) ──
    f4_all = np.load(ROOT / "evaluation/open_set_v1/knn/knn_embeddings.npz")["embeddings"].astype(np.float32)
    with open(ROOT / "evaluation/open_set_v1/knn/knn_open_set_results.json", encoding="utf-8") as f:
        f3f4_records = json.load(f)["records"]
    unknown_mask_f3f4 = np.array([r["known_unknown"] == "UNKNOWN" for r in f3f4_records])
    X_unknown = f4_all[unknown_mask_f3f4]
    scores_unknown = min_mahalanobis(X_unknown, all_centroids, precision_matrix)

    print(f"KNOWN limpio: {len(scores_known)} imagenes")
    print(f"UNKNOWN (F4): {len(scores_unknown)} imagenes\n")

    # ── Clasificacion en 5 categorias ──
    margin = tau * MARGIN_FRACTION
    lo, hi = tau - margin, tau + margin

    def classify(score, is_known):
        if lo <= score <= hi:
            return "NO_CONCLUSIVE"
        if is_known:
            return "KNOWN_ACCEPTED" if score <= tau else "KNOWN_REJECTED"
        else:
            return "UNKNOWN_FALSE_ACCEPTED" if score <= tau else "UNKNOWN_REJECTED"

    known_decisions = [classify(s, True) for s in scores_known]
    unknown_decisions = [classify(s, False) for s in scores_unknown]

    from collections import Counter
    known_counts = Counter(known_decisions)
    unknown_counts = Counter(unknown_decisions)

    print("KNOWN decisions:", dict(known_counts))
    print("UNKNOWN decisions:", dict(unknown_counts))

    # ── Metricas (excluyendo NO_CONCLUSIVE del calculo binario estandar, reportado aparte) ──
    known_conclusive_mask = np.array([d != "NO_CONCLUSIVE" for d in known_decisions])
    unknown_conclusive_mask = np.array([d != "NO_CONCLUSIVE" for d in unknown_decisions])

    known_acc = known_counts.get("KNOWN_ACCEPTED", 0)
    known_rej = known_counts.get("KNOWN_REJECTED", 0)
    unk_rej = unknown_counts.get("UNKNOWN_REJECTED", 0)
    unk_fa = unknown_counts.get("UNKNOWN_FALSE_ACCEPTED", 0)

    n_known_conclusive = known_acc + known_rej
    n_unknown_conclusive = unk_rej + unk_fa

    kar = known_acc / n_known_conclusive if n_known_conclusive else None
    frr = known_rej / n_known_conclusive if n_known_conclusive else None
    udr = unk_rej / n_unknown_conclusive if n_unknown_conclusive else None
    far = unk_fa / n_unknown_conclusive if n_unknown_conclusive else None

    y_true = np.concatenate([np.zeros(len(scores_known)), np.ones(len(scores_unknown))])
    y_score = np.concatenate([scores_known, scores_unknown])
    y_pred_unknown = np.concatenate([
        (scores_known > tau).astype(int), (scores_unknown > tau).astype(int)
    ])
    # y_pred_unknown aqui: 1 = predicho como rechazado/unknown. Comparamos contra y_true (1=es unknown real)
    y_pred_reject = np.concatenate([
        (scores_known > tau).astype(int), (scores_unknown <= tau).astype(int) * 0 + (scores_unknown > tau).astype(int)
    ])

    auroc = float(roc_auc_score(y_true, y_score))
    precision = float(precision_score(y_true, y_pred_unknown, zero_division=0))
    recall = float(recall_score(y_true, y_pred_unknown, zero_division=0))
    f1 = float(f1_score(y_true, y_pred_unknown, zero_division=0))
    bal_acc = float(balanced_accuracy_score(y_true, y_pred_unknown))

    n_species_known = len(set(known_species_ids.tolist()))

    report = {
        "phase": "16.9_16.10_BLIND_TEST",
        "frozen_threshold": tau,
        "margin_fraction_for_no_conclusive": MARGIN_FRACTION,
        "n_images": {"known": int(len(scores_known)), "unknown": int(len(scores_unknown))},
        "n_individuals": {"known": int(len(set(clean_data["image_ids"].tolist())))},
        "n_species": {"known": n_species_known, "unknown": 2},
        "classification_counts": {
            "KNOWN_ACCEPTED": known_acc, "KNOWN_REJECTED": known_rej,
            "UNKNOWN_REJECTED": unk_rej, "UNKNOWN_FALSE_ACCEPTED": unk_fa,
            "NO_CONCLUSIVE_known": int(known_counts.get("NO_CONCLUSIVE", 0)),
            "NO_CONCLUSIVE_unknown": int(unknown_counts.get("NO_CONCLUSIVE", 0)),
        },
        "metrics": {
            "known_acceptance_rate_KAR": kar,
            "known_false_rejection_rate_FRR": frr,
            "unknown_rejection_rate_UDR": udr,
            "unknown_false_acceptance_rate_FAR": far,
            "precision_unknown_detection": precision,
            "recall_unknown_detection": recall,
            "f1_unknown_detection": f1,
            "balanced_accuracy": bal_acc,
            "auroc": auroc,
        },
        "coverage_note": f"KNOWN limpio cubre {n_species_known}/41 especies del catalogo "
                          "(solo las que tenian imagenes reales sin usar en TRAIN/REFERENCE/CALIBRATION/F3). "
                          "Las 17 especies restantes no tienen datos held-out disponibles.",
    }

    out_path = OUT / "fase16_blind_test_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n=== METRICAS FASE 16 (BLIND LIMPIO) ===")
    print(json.dumps(report["metrics"], indent=2))
    print(f"\n[OK] {out_path}")


if __name__ == "__main__":
    main()
