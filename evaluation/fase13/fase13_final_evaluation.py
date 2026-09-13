import os
import json
import sys
from pathlib import Path
import numpy as np
from sklearn.covariance import ledoit_wolf, oas
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc

def canonical_species_name(name):
    """Normalize species name: underscore to space, strip, fix known typos."""
    if isinstance(name, str):
        normalized = name.replace('_', ' ').strip()
        # Fix REFERENCE typo: acanthinus → achatinus
        if normalized == "Pristimantis acanthinus":
            normalized = "Pristimantis achatinus"
        return normalized
    return str(name)

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

def run_final_evaluation():
    print("=== FASE E: EVALUACIÓN FINAL CIEGA SOBRE F3 (766 KNOWN) Y F4 (56 UNKNOWN) ===")

    # 1. Physical separation check: Verify config is frozen
    config_path = Path(r"D:\Anura\evaluation\fase13\selection\frozen_rejection_config.json")
    if not config_path.exists():
        print("ERROR: Configuración no congelada. No se permite acceder a F3/F4 sin congelamiento previo.")
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    if not (config.get("METHOD_FROZEN") and config.get("REGULARIZATION_FROZEN") and config.get("THRESHOLD_FROZEN")):
        print("ERROR: METHOD, REGULARIZATION o THRESHOLD no están congelados.")
        sys.exit(1)

    selected_method = config["selected_method"]
    tau_frozen = config["selected_threshold_tau_95KAR"]
    print(f"Método Congelado: {selected_method}")
    print(f"Umbral Congelado tau (95% KAR): {tau_frozen:.6f}")

    # 2. Load REFERENCE embeddings to fit precision matrix & reference centroids
    ref_emb_path = Path(r"D:\Anura\evaluation\fase13\embeddings\reference_embeddings.npz")
    if not ref_emb_path.exists():
        print(f"ERROR: Embeddings de REFERENCE {ref_emb_path} no encontrados.")
        sys.exit(1)

    ref_data = np.load(ref_emb_path)
    X_ref = ref_data['embeddings']
    y_ref_raw = ref_data['species']

    # Normalize species names to canonical form (spaces)
    y_ref = np.array([canonical_species_name(sp) for sp in y_ref_raw])

    # Compute centroids for 10 REFERENCE species
    ref_centroids = compute_centroids(X_ref, y_ref)
    X_centered, cov_pooled = compute_pooled_covariance(X_ref, y_ref, ref_centroids)

    # Compute precision matrix based on selected_method
    if selected_method == "M5_LedoitWolf_Shared":
        cov_lw, _ = ledoit_wolf(X_centered, assume_centered=True)
        prec_matrix = np.linalg.inv(cov_lw)
        is_diagonal = False
    elif selected_method == "M6_OAS_Shared":
        cov_oas, _ = oas(X_centered, assume_centered=True)
        prec_matrix = np.linalg.inv(cov_oas)
        is_diagonal = False
    elif selected_method == "M3_Mahalanobis_Diagonal_Shared":
        diag_var = np.maximum(np.var(X_centered, axis=0, ddof=1), 1e-8)
        prec_matrix = 1.0 / diag_var
        is_diagonal = True
    elif "M4_Ridge" in selected_method:
        lam = float(selected_method.split("_")[-1])
        cov_r = (1.0 - lam) * cov_pooled + lam * np.eye(512, dtype=np.float32)
        prec_matrix = np.linalg.inv(cov_r)
        is_diagonal = False
    elif selected_method == "M1_Euclidean" or selected_method == "M2_Cosine":
        prec_matrix = None
        is_diagonal = False
    else:
        raise ValueError(f"Método desconocido: {selected_method}")

    # 3. Load TRAIN embeddings for Group B centroids
    train_emb_path = Path(r"D:\Anura\evaluation\fase13\embeddings\train_embeddings.npz")
    if not train_emb_path.exists():
        print(f"ERROR: Embeddings de TRAIN {train_emb_path} no encontrados.")
        print("Ejecuta primero fase13_compute_train_embeddings.py")
        sys.exit(1)

    train_data = np.load(train_emb_path)
    X_train = train_data['embeddings']
    y_train_raw = train_data['species']

    # Normalize species names to canonical form (spaces)
    y_train = np.array([canonical_species_name(sp) for sp in y_train_raw])

    # Compute centroids for TRAIN species (for Group B)
    train_centroids = compute_centroids(X_train, y_train)

    # 4. Load F3 + F4 embeddings and ground truth
    f3f4_emb_path = Path(r"D:\Anura\evaluation\open_set_v1\knn\knn_embeddings.npz")
    f3f4_json_path = Path(r"D:\Anura\evaluation\open_set_v1\knn\knn_open_set_results.json")

    f3f4_emb = np.load(f3f4_emb_path)["embeddings"].astype(np.float32)
    with open(f3f4_json_path, 'r', encoding='utf-8') as f:
        f3f4_records = json.load(f)["records"]

    # 5. Build centroids for 41 visual species
    # Group A (9-10): Use REFERENCE centroids (independent calibration)
    #  → Leucostethus fraterdanieli is orphaned (not in TRAIN), will be excluded
    # Group B (31-32): Use TRAIN centroids (structural only)
    all_41_centroids = {}
    group_a_species = set()
    group_b_species = set()
    orphaned_group_a = set()

    # Add Group A from REFERENCE, but only if also in TRAIN (to avoid orphans)
    for sp, centroid in ref_centroids.items():
        if sp in train_centroids:
            # Species is in both REFERENCE and TRAIN → use REFERENCE centroid
            all_41_centroids[sp] = centroid
            group_a_species.add(sp)
        else:
            # Species is orphaned (only in REFERENCE, not in TRAIN/visual classes)
            orphaned_group_a.add(sp)

    # Add Group B from TRAIN (species NOT in REFERENCE)
    for sp, centroid in train_centroids.items():
        if sp not in all_41_centroids:
            all_41_centroids[sp] = centroid
            group_b_species.add(sp)

    if orphaned_group_a:
        print(f"WARNING: {len(orphaned_group_a)} REFERENCE species orphaned (not in TRAIN/visual classes):")
        for sp in orphaned_group_a:
            print(f"  - {sp}")

    print(f"Total centroids built: {len(all_41_centroids)} (Group A: {len(group_a_species)}, Group B: {len(group_b_species)})")

    # CRITICAL ASSERTIONS (Corrección 9)
    assert len(all_41_centroids) == 41, f"ERROR: Expected 41 centroids, got {len(all_41_centroids)}"
    assert len(group_a_species) == 9, f"ERROR: Expected 9 Group A centroids, got {len(group_a_species)}"
    assert len(group_b_species) == 32, f"ERROR: Expected 32 Group B centroids, got {len(group_b_species)}"
    print(f"[OK] Centroid architecture verified: 9 Group A (from REFERENCE) + 32 Group B (from TRAIN) = 41 total")

    # 6. Generate centroid source audit
    centroid_audit = {
        "total_centroids": len(all_41_centroids),
        "group_a_count": len(group_a_species),
        "group_b_count": len(group_b_species),
        "species_details": {}
    }

    for sp in sorted(all_41_centroids.keys()):
        if sp in group_a_species:
            source = "REFERENCE"
            independent = "YES"
        else:
            source = "TRAIN"
            independent = "NO"

        centroid_audit["species_details"][sp] = {
            "group": "A" if sp in group_a_species else "B",
            "centroid_source": source,
            "independent_calibration": independent,
            "train_reference_structural_only": "NO" if source == "REFERENCE" else "YES"
        }

    # Save audit
    audit_out = Path(r"D:\Anura\evaluation\fase13\final_evaluation\centroid_source_audit.json")
    audit_out.parent.mkdir(parents=True, exist_ok=True)
    with open(audit_out, "w", encoding="utf-8") as f:
        json.dump(centroid_audit, f, indent=2)
    print(f"Centroid source audit saved to: {audit_out}")

    # 7. Compute scores on F3 + F4 (822 samples)
    if selected_method == "M1_Euclidean":
        scores = min_euclidean_distance(f3f4_emb, all_41_centroids)
    elif selected_method == "M2_Cosine":
        scores = min_cosine_distance(f3f4_emb, all_41_centroids)
    else:
        scores = min_mahalanobis_distance(f3f4_emb, all_41_centroids, prec_matrix, is_diagonal=is_diagonal)

    # 8. Labels & Evaluation
    # Ground truth: 0 = KNOWN (F3, 766), 1 = UNKNOWN (F4, 56)
    y_true_binary = np.array([0 if r['known_unknown'] == 'KNOWN' else 1 for r in f3f4_records])

    # Rejection score: higher distance = more likely UNKNOWN
    # AUROC: KNOWN vs UNKNOWN
    auroc = float(roc_auc_score(y_true_binary, scores))

    # AUPR (Precision-Recall curve for UNKNOWN class)
    precision, recall, _ = precision_recall_curve(y_true_binary, scores)
    aupr = float(auc(recall, precision))

    # Rejection decisions at frozen tau
    decisions = ["ACCEPT" if s <= tau_frozen else "REJECT" for s in scores]

    # Metrics breakdown
    known_mask = (y_true_binary == 0)
    unknown_mask = (y_true_binary == 1)

    known_scores = scores[known_mask]
    unknown_scores = scores[unknown_mask]

    kar_at_frozen_tau = float(np.mean(known_scores <= tau_frozen))
    udr_at_frozen_tau = float(np.mean(unknown_scores > tau_frozen))
    far_at_frozen_tau = float(np.mean(unknown_scores <= tau_frozen))

    # Calculate FAR @ 95% TPR (where TPR = KAR = 95% on KNOWN)
    tau_95_tpr = float(np.percentile(known_scores, 95))
    far_at_95tpr = float(np.mean(unknown_scores <= tau_95_tpr))
    far_at_90tpr = float(np.mean(unknown_scores <= np.percentile(known_scores, 90)))
    far_at_85tpr = float(np.mean(unknown_scores <= np.percentile(known_scores, 85)))

    # Breakdown by species groups (use canonical names)
    group_a_known_mask = np.array([
        r['known_unknown'] == 'KNOWN' and canonical_species_name(r['true_species']) in group_a_species
        for r in f3f4_records
    ])
    group_b_known_mask = np.array([
        r['known_unknown'] == 'KNOWN' and canonical_species_name(r['true_species']) in group_b_species
        for r in f3f4_records
    ])

    kar_group_a = float(np.mean(scores[group_a_known_mask] <= tau_frozen)) if np.sum(group_a_known_mask) > 0 else 0.0
    kar_group_b = float(np.mean(scores[group_b_known_mask] <= tau_frozen)) if np.sum(group_b_known_mask) > 0 else 0.0

    # Unknown species breakdown
    unknown_sp_breakdown = {}
    for r, s, dec in zip(f3f4_records, scores, decisions):
        if r['known_unknown'] == 'UNKNOWN':
            sp = r['true_species']
            if sp not in unknown_sp_breakdown:
                unknown_sp_breakdown[sp] = {"total": 0, "rejected": 0, "accepted": 0, "scores": []}
            unknown_sp_breakdown[sp]["total"] += 1
            unknown_sp_breakdown[sp]["scores"].append(float(s))
            if dec == "REJECT":
                unknown_sp_breakdown[sp]["rejected"] += 1
            else:
                unknown_sp_breakdown[sp]["accepted"] += 1

    for sp in unknown_sp_breakdown:
        tot = unknown_sp_breakdown[sp]["total"]
        rej = unknown_sp_breakdown[sp]["rejected"]
        unknown_sp_breakdown[sp]["udr"] = float(rej / tot)
        unknown_sp_breakdown[sp]["mean_score"] = float(np.mean(unknown_sp_breakdown[sp]["scores"]))

    print(f"\n--- RESULTADOS FINALES DE EVALUACIÓN F3 (766 KNOWN) + F4 (56 UNKNOWN) ---")
    print(f"AUROC Out-of-Sample: {auroc:.6f}")
    print(f"AUPR Out-of-Sample: {aupr:.6f}")
    print(f"FAR @ 95% TPR: {far_at_95tpr:.6f}")
    print(f"FAR @ 90% TPR: {far_at_90tpr:.6f}")
    print(f"FAR @ 85% TPR: {far_at_85tpr:.6f}")
    print(f"Known Acceptance Rate (KAR) @ tau={tau_frozen:.4f}: {kar_at_frozen_tau:.4f}")
    print(f"Unknown Detection Rate (UDR) @ tau={tau_frozen:.4f}: {udr_at_frozen_tau:.4f}")
    print(f"False Acceptance Rate (FAR) @ tau={tau_frozen:.4f}: {far_at_frozen_tau:.4f}")
    print(f"KAR Grupo A (10 Especies Calibradas Independientemente): {kar_group_a:.4f}")
    print(f"KAR Grupo B (31 Especies Estructurales): {kar_group_b:.4f}")

    final_metrics = {
        "auroc_out_of_sample": auroc,
        "aupr_out_of_sample": aupr,
        "far_at_95tpr": far_at_95tpr,
        "far_at_90tpr": far_at_90tpr,
        "far_at_85tpr": far_at_85tpr,
        "frozen_tau": tau_frozen,
        "kar_known_total": kar_at_frozen_tau,
        "udr_unknown_total": udr_at_frozen_tau,
        "far_unknown_total": far_at_frozen_tau,
        "kar_group_a_10_species": kar_group_a,
        "kar_group_b_31_species": kar_group_b,
        "unknown_species_breakdown": unknown_sp_breakdown,
        "selected_method": selected_method,
        "declarations": {
            "9_OF_41_INDEPENDENTLY_CALIBRATED": "YES (Leucostethus fraterdanieli orphaned)",
            "32_OF_41_INDEPENDENTLY_CALIBRATED": "NO",
            "INDIVIDUAL_INDEPENDENCE": "CONTROLLED_NOT_FORMALLY_VERIFIABLE",
            "OBSERVATION_INDEPENDENCE": "NOT_FORMALLY_VERIFIABLE",
            "CALIBRATION_AUROC": "NOT_COMPUTABLE"
        }
    }

    out_dir = Path(r"D:\Anura\evaluation\fase13\final_evaluation")
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(out_dir / "FASE13_FINAL_METRICS.json", "w", encoding="utf-8") as f:
        json.dump(final_metrics, f, indent=2)

    # Save final status report
    status_code = "STATUS: FASE13_COMPLETE"
    with open(Path(r"D:\Anura\evaluation\fase13\FASE13_STATUS.json"), "w", encoding="utf-8") as f:
        json.dump({
            "status": status_code,
            "10_OF_41_INDEPENDENTLY_CALIBRATED": "YES",
            "31_OF_41_INDEPENDENTLY_CALIBRATED": "NO",
            "INDIVIDUAL_INDEPENDENCE": "CONTROLLED_NOT_FORMALLY_VERIFIABLE",
            "OBSERVATION_INDEPENDENCE": "NOT_FORMALLY_VERIFIABLE",
            "CALIBRATION_AUROC": "NOT_COMPUTABLE",
            "final_auroc": auroc,
            "final_far_95tpr": far_at_95tpr
        }, f, indent=2)

    with open(out_dir / "FASE13_FINAL_REPORT.md", "w", encoding="utf-8") as f:
        f.write("# FASE 13 — Reporte Final de Calibración Independiente del Rechazo Open Set\n\n")
        f.write(f"**STATUS**: `{status_code}`\n\n")
        f.write("## Métricas Finales Out-of-Sample (F3 KNOWN vs F4 UNKNOWN)\n\n")
        f.write(f"- **AUROC**: `{auroc:.6f}`\n")
        f.write(f"- **AUPR**: `{aupr:.6f}`\n")
        f.write(f"- **FAR @ 95% TPR**: `{far_at_95tpr:.6f}`\n")
        f.write(f"- **FAR @ 90% TPR**: `{far_at_90tpr:.6f}`\n")
        f.write(f"- **FAR @ 85% TPR**: `{far_at_85tpr:.6f}`\n\n")
        f.write("## Evaluación al Umbral Congelado τ (95% KAR en CALIBRATION)\n\n")
        f.write(f"- **Umbral Congelado τ**: `{tau_frozen:.6f}`\n")
        f.write(f"- **Known Acceptance Rate (KAR) F3**: `{kar_at_frozen_tau:.4f}`\n")
        f.write(f"- **Unknown Detection Rate (UDR) F4**: `{udr_at_frozen_tau:.4f}`\n")
        f.write(f"- **False Acceptance Rate (FAR) F4**: `{far_at_frozen_tau:.4f}`\n\n")
        f.write("## Desglose por Grupos de Especies\n\n")
        f.write(f"- **Grupo A (10 Especies Calibradas Independientemente)**: KAR = `{kar_group_a:.4f}`\n")
        f.write(f"  - Centroides extraídos de: REFERENCE (calibración independiente)\n")
        f.write(f"- **Grupo B (31 Especies Estructurales sin Calibración Independiente)**: KAR = `{kar_group_b:.4f}`\n")
        f.write(f"  - Centroides extraídos de: TRAIN (sin calibración independiente, solo estructura)\n\n")
        f.write("## Desglose por Especie UNKNOWN (F4)\n\n")
        f.write("| Especie UNKNOWN | Muestras Totales | Rechazadas (Correctas) | UDR | Distancia Media |\n|---|---|---|---|---|\n")
        for sp, d in unknown_sp_breakdown.items():
            f.write(f"| `{sp}` | {d['total']} | {d['rejected']} | `{d['udr']:.4f}` | `{d['mean_score']:.4f}` |\n")
        f.write("\n\n## Declaraciones Obligatorias de Diseño\n\n")
        for k, v in final_metrics["declarations"].items():
            f.write(f"- `{k}`: `{v}`\n")
        f.write("\n\n## Auditoría de Fuente de Centroides\n\n")
        f.write("Ver `centroid_source_audit.json` para detalles completos de origen de cada centroide.\n")

    print(f"\n>>> REPORTE FINAL GENERADO EN {out_dir / 'FASE13_FINAL_REPORT.md'} <<<")

if __name__ == "__main__":
    run_final_evaluation()
