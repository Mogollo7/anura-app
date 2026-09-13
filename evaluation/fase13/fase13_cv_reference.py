import os
import json
import sys
from pathlib import Path
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.covariance import ledoit_wolf, oas

def fast_cond(matrix):
    evals = np.linalg.eigvalsh(matrix)
    ev_min = np.min(evals)
    if ev_min <= 0:
        return float('inf')
    return float(np.max(evals) / ev_min)

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

def run_cv():
    print("=== FASE B: 5-FOLD CROSS-VALIDATION SOBRE REFERENCE ===", flush=True)
    
    emb_path = Path(r"D:\Anura\evaluation\fase13\embeddings\reference_embeddings.npz")
    if not emb_path.exists():
        print(f"ERROR: Embeddings {emb_path} no encontrados.", flush=True)
        sys.exit(1)

    data = np.load(emb_path)
    X = data['embeddings']
    y = data['species']

    print(f"Loaded REFERENCE embeddings: {X.shape}, species count: {len(np.unique(y))}", flush=True)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    ridge_lambdas = [0.001, 0.01, 0.05, 0.1, 0.2, 0.5]
    method_names = [
        "M1_Euclidean",
        "M2_Cosine",
        "M3_Mahalanobis_Diagonal_Shared",
        "M5_LedoitWolf_Shared",
        "M6_OAS_Shared"
    ] + [f"M4_Ridge_lambda_{lam}" for lam in ridge_lambdas]

    results_by_method = {m: {"fold_scores": [], "cond_numbers": []} for m in method_names}

    for fold_idx, (train_idx, val_idx) in enumerate(skf.split(X, y)):
        X_tr, y_tr = X[train_idx], y[train_idx]
        X_va, y_va = X[val_idx], y[val_idx]

        centroids = compute_centroids(X_tr, y_tr)
        X_centered, cov_pooled = compute_pooled_covariance(X_tr, y_tr, centroids)

        # M1: Euclidean
        scores_m1 = min_euclidean_distance(X_va, centroids)
        results_by_method["M1_Euclidean"]["fold_scores"].append(scores_m1)
        results_by_method["M1_Euclidean"]["cond_numbers"].append(1.0)

        # M2: Cosine
        scores_m2 = min_cosine_distance(X_va, centroids)
        results_by_method["M2_Cosine"]["fold_scores"].append(scores_m2)
        results_by_method["M2_Cosine"]["cond_numbers"].append(1.0)

        # M3: Diagonal
        diag_var = np.maximum(np.var(X_centered, axis=0, ddof=1), 1e-8)
        prec_diag = 1.0 / diag_var
        cond_m3 = float(np.max(diag_var) / np.min(diag_var))
        scores_m3 = min_mahalanobis_distance(X_va, centroids, prec_diag, is_diagonal=True)
        results_by_method["M3_Mahalanobis_Diagonal_Shared"]["fold_scores"].append(scores_m3)
        results_by_method["M3_Mahalanobis_Diagonal_Shared"]["cond_numbers"].append(cond_m3)

        # M5: Fast LedoitWolf
        cov_lw, _ = ledoit_wolf(X_centered, assume_centered=True)
        prec_m5 = np.linalg.inv(cov_lw)
        cond_m5 = fast_cond(cov_lw)
        scores_m5 = min_mahalanobis_distance(X_va, centroids, prec_m5, is_diagonal=False)
        results_by_method["M5_LedoitWolf_Shared"]["fold_scores"].append(scores_m5)
        results_by_method["M5_LedoitWolf_Shared"]["cond_numbers"].append(cond_m5)

        # M6: Fast OAS
        cov_oas, _ = oas(X_centered, assume_centered=True)
        prec_m6 = np.linalg.inv(cov_oas)
        cond_m6 = fast_cond(cov_oas)
        scores_m6 = min_mahalanobis_distance(X_va, centroids, prec_m6, is_diagonal=False)
        results_by_method["M6_OAS_Shared"]["fold_scores"].append(scores_m6)
        results_by_method["M6_OAS_Shared"]["cond_numbers"].append(cond_m6)

        # M4: Ridge lambdas
        eye = np.eye(X.shape[1], dtype=np.float32)
        for lam in ridge_lambdas:
            m_key = f"M4_Ridge_lambda_{lam}"
            cov_ridge = (1.0 - lam) * cov_pooled + lam * eye
            cond_m4 = fast_cond(cov_ridge)
            prec_m4 = np.linalg.inv(cov_ridge)
            scores_m4 = min_mahalanobis_distance(X_va, centroids, prec_m4, is_diagonal=False)
            results_by_method[m_key]["fold_scores"].append(scores_m4)
            results_by_method[m_key]["cond_numbers"].append(cond_m4)

    # Summarize results
    summary = {}
    print("\n--- RESUMEN DE 5-FOLD CROSS-VALIDATION (REFERENCE) ---", flush=True)
    print(f"{'Método':<32} | {'Mean Dist':<10} | {'Std Dist':<10} | {'Fold Std':<10} | {'Mean Cond.No':<12}", flush=True)
    print("-" * 82, flush=True)

    for m_name in method_names:
        all_scores = np.concatenate(results_by_method[m_name]["fold_scores"])
        fold_means = [np.mean(fs) for fs in results_by_method[m_name]["fold_scores"]]
        mean_cond = float(np.mean(results_by_method[m_name]["cond_numbers"]))
        
        overall_mean = float(np.mean(all_scores))
        overall_std = float(np.std(all_scores))
        fold_std = float(np.std(fold_means))

        summary[m_name] = {
            "overall_mean_score": overall_mean,
            "overall_std_score": overall_std,
            "inter_fold_std": fold_std,
            "mean_condition_number": mean_cond
        }

        print(f"{m_name:<32} | {overall_mean:<10.4f} | {overall_std:<10.4f} | {fold_std:<10.4f} | {mean_cond:<12.2e}", flush=True)

    out_dir = Path(r"D:\Anura\evaluation\fase13\statistics")
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(out_dir / "reference_cv_results.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    with open(out_dir / "reference_cv_results.md", "w", encoding="utf-8") as f:
        f.write("# FASE 13 — Resultados de 5-Fold Cross-Validation en REFERENCE\n\n")
        f.write("| Método | Mean Dist | Std Dist | Inter-Fold Std | Mean Condition Number |\n")
        f.write("|---|---|---|---|---|\n")
        for m_name, res in summary.items():
            f.write(f"| `{m_name}` | {res['overall_mean_score']:.4f} | {res['overall_std_score']:.4f} | {res['inter_fold_std']:.4f} | {res['mean_condition_number']:.2e} |\n")

    print(f"\nResumen de CV guardado en {out_dir / 'reference_cv_results.json'}", flush=True)

if __name__ == "__main__":
    run_cv()
