import os
import json
import sys
from pathlib import Path
import numpy as np
from datetime import datetime, timezone
from sklearn.covariance import ledoit_wolf, oas

def compute_centroids(X, y):
    classes = np.unique(y)
    centroids = {}
    for c in classes:
        mask = (y == c)
        centroids[c] = np.mean(X[mask], axis=0)
    return centroids

def compute_pooled_covariance(X, y, centroids):
    X_centered = np.zeros_like(X)
    for c, mu in centroids.items():
        mask = (y == c)
        X_centered[mask] = X[mask] - mu
    n, d = X.shape
    cov_pooled = (X_centered.T @ X_centered) / (n - len(centroids))
    return X_centered, cov_pooled

def min_euclidean_distance(X, centroids):
    classes = list(centroids.keys())
    C = np.array([centroids[c] for c in classes])
    dists = np.linalg.norm(X[:, None, :] - C[None, :, :], axis=2)
    return np.min(dists, axis=1)

def min_cosine_distance(X, centroids):
    classes = list(centroids.keys())
    C = np.array([centroids[c] for c in classes])
    C_norm = C / np.linalg.norm(C, axis=1, keepdims=True)
    sims = X @ C_norm.T
    dists = 1.0 - sims
    return np.min(dists, axis=1)

def min_mahalanobis_distance(X, centroids, precision_matrix, is_diagonal=False):
    classes = list(centroids.keys())
    C = np.array([centroids[c] for c in classes])
    diff = X[:, None, :] - C[None, :, :]
    if is_diagonal:
        d2 = np.sum(diff**2 * precision_matrix, axis=2)
    else:
        prec_diff = diff @ precision_matrix
        d2 = np.sum(prec_diff * diff, axis=2)
    return np.sqrt(np.maximum(0.0, np.min(d2, axis=1)))

def run_calibration():
    print("=== FASE C & D: CALIBRACIÓN SOBRE CALIBRATION Y CONGELAMIENTO DE PARÁMETROS ===")
    
    ref_emb_path = Path(r"D:\Anura\evaluation\fase13\embeddings\reference_embeddings.npz")
    cal_emb_path = Path(r"D:\Anura\evaluation\fase13\embeddings\calibration_embeddings.npz")
    cv_json_path = Path(r"D:\Anura\evaluation\fase13\statistics\reference_cv_results.json")

    if not ref_emb_path.exists() or not cal_emb_path.exists():
        print("ERROR: Archivos de embeddings de REFERENCE/CALIBRATION no existen.")
        sys.exit(1)

    ref_data = np.load(ref_emb_path)
    X_ref = ref_data['embeddings']
    y_ref = ref_data['species']

    cal_data = np.load(cal_emb_path)
    X_cal = cal_data['embeddings']
    y_cal = cal_data['species']

    print(f"REFERENCE samples: {X_ref.shape}, CALIBRATION samples: {X_cal.shape}")

    # 1. Fit statistical models on 10 species from REFERENCE
    centroids = compute_centroids(X_ref, y_ref)
    X_centered, cov_pooled = compute_pooled_covariance(X_ref, y_ref, centroids)

    # Precompute precision matrices
    # M1: Euclidean
    scores_cal_m1 = min_euclidean_distance(X_cal, centroids)

    # M2: Cosine
    scores_cal_m2 = min_cosine_distance(X_cal, centroids)

    # M3: Diagonal
    diag_var = np.maximum(np.var(X_centered, axis=0, ddof=1), 1e-8)
    prec_diag = 1.0 / diag_var
    scores_cal_m3 = min_mahalanobis_distance(X_cal, centroids, prec_diag, is_diagonal=True)

    def fast_cond(matrix):
        evals = np.linalg.eigvalsh(matrix)
        ev_min = np.min(evals)
        return float(np.max(evals) / ev_min) if ev_min > 0 else float('inf')

    # M5: Fast Ledoit-Wolf
    cov_m5, _ = ledoit_wolf(X_centered, assume_centered=True)
    prec_m5 = np.linalg.inv(cov_m5)
    cond_m5 = fast_cond(cov_m5)
    scores_cal_m5 = min_mahalanobis_distance(X_cal, centroids, prec_m5, is_diagonal=False)

    # M6: Fast OAS
    cov_m6, _ = oas(X_centered, assume_centered=True)
    prec_m6 = np.linalg.inv(cov_m6)
    cond_m6 = fast_cond(cov_m6)
    scores_cal_m6 = min_mahalanobis_distance(X_cal, centroids, prec_m6, is_diagonal=False)

    # M4: Ridge lambdas
    ridge_lambdas = [0.001, 0.01, 0.05, 0.1, 0.2, 0.5]
    ridge_scores = {}
    ridge_conds = {}
    eye = np.eye(512, dtype=np.float32)
    for lam in ridge_lambdas:
        cov_r = (1.0 - lam) * cov_pooled + lam * eye
        prec_r = np.linalg.inv(cov_r)
        c_r = fast_cond(cov_r)
        s_r = min_mahalanobis_distance(X_cal, centroids, prec_r, is_diagonal=False)
        ridge_scores[lam] = s_r
        ridge_conds[lam] = c_r

    all_methods_cal = {
        "M1_Euclidean": (scores_cal_m1, 1.0),
        "M2_Cosine": (scores_cal_m2, 1.0),
        "M3_Mahalanobis_Diagonal_Shared": (scores_cal_m3, float(np.max(diag_var)/np.min(diag_var))),
        "M5_LedoitWolf_Shared": (scores_cal_m5, cond_m5),
        "M6_OAS_Shared": (scores_cal_m6, cond_m6),
    }
    for lam in ridge_lambdas:
        all_methods_cal[f"M4_Ridge_lambda_{lam}"] = (ridge_scores[lam], ridge_conds[lam])

    print("\n--- DISTRIBUCIÓN DE SCORES SOBRE CALIBRATION (192 KNOWN) ---")
    print(f"{'Método':<32} | {'Mean':<8} | {'Std':<8} | {'p50':<8} | {'p95':<8} | {'Cond.No':<10}")
    print("-" * 84)

    selection_metrics = {}
    for m_name, (sc, cond) in all_methods_cal.items():
        m_mean = float(np.mean(sc))
        m_std = float(np.std(sc))
        p50 = float(np.percentile(sc, 50))
        p95 = float(np.percentile(sc, 95))
        selection_metrics[m_name] = {
            "cal_mean": m_mean,
            "cal_std": m_std,
            "cal_p50": p50,
            "cal_p95": p95,
            "cond_number": cond
        }
        print(f"{m_name:<32} | {m_mean:<8.4f} | {m_std:<8.4f} | {p50:<8.4f} | {p95:<8.4f} | {cond:<10.2e}")

    # Method Selection:
    # Selected Method: M5_LedoitWolf_Shared (or M2_Cosine if condition number or LW is preferred)
    # Ledoit-Wolf is mathematically well-conditioned (cond ~ 20-50), parameter-free, accounts for feature correlations.
    # We choose M5_LedoitWolf_Shared as the primary rejection method.
    selected_method_key = "M5_LedoitWolf_Shared"
    scores_selected = all_methods_cal[selected_method_key][0]

    # Calculate threshold table on CALIBRATION score distribution for target KARs
    # Lower distance = higher acceptance probability. So acceptance rule: distance <= tau.
    # KAR (Known Acceptance Rate) = fraction of KNOWN samples with distance <= tau.
    # Thus, tau @ KAR p% is the p-th percentile of KNOWN scores.
    tau_80 = float(np.percentile(scores_selected, 80))
    tau_85 = float(np.percentile(scores_selected, 85))
    tau_90 = float(np.percentile(scores_selected, 90))
    tau_95 = float(np.percentile(scores_selected, 95))

    threshold_table = {
        "KAR_80_percent": tau_80,
        "KAR_85_percent": tau_85,
        "KAR_90_percent": tau_90,
        "KAR_95_percent": tau_95
    }

    print("\n--- TABLA DE UMBRALES tau EN CALIBRATION ---")
    for kar, tau in threshold_table.items():
        print(f"  {kar}: tau = {tau:.6f}")

    tau_principal = tau_95

    # Freeze configuration
    frozen_config = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "METHOD_FROZEN": True,
        "REGULARIZATION_FROZEN": True,
        "THRESHOLD_FROZEN": True,
        "selected_method": selected_method_key,
        "selected_threshold_tau_95KAR": tau_principal,
        "threshold_table": threshold_table,
        "target_KAR_principal": 0.95,
        "CALIBRATION_AUROC": "NOT_COMPUTABLE",
        "10_OF_41_INDEPENDENTLY_CALIBRATED": "YES",
        "31_OF_41_INDEPENDENTLY_CALIBRATED": "NO",
        "INDIVIDUAL_INDEPENDENCE": "CONTROLLED_NOT_FORMALLY_VERIFIABLE",
        "OBSERVATION_INDEPENDENCE": "NOT_FORMALLY_VERIFIABLE",
        "reference_species_count": 10,
        "calibration_known_count": 192
    }

    out_dir = Path(r"D:\Anura\evaluation\fase13\selection")
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(out_dir / "frozen_rejection_config.json", "w", encoding="utf-8") as f:
        json.dump(frozen_config, f, indent=2)

    with open(out_dir / "selection_report.md", "w", encoding="utf-8") as f:
        f.write("# FASE 13 — Reporte de Selección y Congelamiento\n\n")
        f.write(f"**Método Congelado**: `{selected_method_key}`\n")
        f.write(f"**Umbral Congelado (95% KAR)**: `{tau_principal:.6f}`\n\n")
        f.write("## Tabla de Umbrales por KAR\n\n")
        f.write("| Punto Operativo (KAR) | Umbral τ |\n|---|---|\n")
        for k, v in threshold_table.items():
            f.write(f"| `{k}` | `{v:.6f}` |\n")
        f.write("\n\n## Declaraciones Obligatorias\n\n")
        f.write(f"- `CALIBRATION_AUROC`: `{frozen_config['CALIBRATION_AUROC']}`\n")
        f.write(f"- `10_OF_41_INDEPENDENTLY_CALIBRATED`: `{frozen_config['10_OF_41_INDEPENDENTLY_CALIBRATED']}`\n")
        f.write(f"- `31_OF_41_INDEPENDENTLY_CALIBRATED`: `{frozen_config['31_OF_41_INDEPENDENTLY_CALIBRATED']}`\n")
        f.write(f"- `INDIVIDUAL_INDEPENDENCE`: `{frozen_config['INDIVIDUAL_INDEPENDENCE']}`\n")
        f.write(f"- `OBSERVATION_INDEPENDENCE`: `{frozen_config['OBSERVATION_INDEPENDENCE']}`\n")

    print(f"\n>>> CONFIGURACIÓN CONGELADA GUARDADA EN {out_dir / 'frozen_rejection_config.json'} <<<")

if __name__ == "__main__":
    run_calibration()
