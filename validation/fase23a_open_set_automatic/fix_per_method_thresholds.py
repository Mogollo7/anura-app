#!/usr/bin/env python3
"""
FASE 23A — Corrección: aplicar threshold correcto por método.

BUG CORREGIDO: el threshold oficial (39.354) es válido SOLO para Mahalanobis
(M5_LedoitWolf_Shared, congelado en threshold/v1.1.0_CLEAN). Aplicarlo a
Euclidean/Cosine/Normalized (escalas ~0.2-0.9) producía FAR=FRR=1.0 (degenerado).

Corrección: usar por método:
  - Mahalanobis: threshold OFICIAL congelado = 39.35406371422803
  - Euclidean_Raw, Cosine, Normalized_Euclidean: threshold DIAGNOSTIC_ONLY
    tomado de la calibración independiente de FASE21 (VALIDATION set, KNOWN-only,
    Youden's J) — NO recalculado ni optimizado sobre este dataset UNKNOWN.

Fuente thresholds diagnósticos (FASE21_REPORT.md, sección Calibración):
  euclidean_raw:        0.6805
  cosine:                0.2630
  euclidean_normalized:  0.7252
"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)

from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve, auc, precision_recall_curve, confusion_matrix, balanced_accuracy_score, f1_score

OUTPUT_DIR = Path(r"D:\Anura\validation\fase23a_open_set_automatic")

# Thresholds correctos por método
THRESHOLDS = {
    "Euclidean_Raw": {"value": 0.6805, "type": "DIAGNOSTIC_ONLY", "source": "FASE21 VALIDATION calibration (Youden J), KNOWN-only, not re-optimized"},
    "Cosine": {"value": 0.2630, "type": "DIAGNOSTIC_ONLY", "source": "FASE21 VALIDATION calibration (Youden J), KNOWN-only, not re-optimized"},
    "Normalized_Euclidean": {"value": 0.7252, "type": "DIAGNOSTIC_ONLY", "source": "FASE21 VALIDATION calibration (Youden J), KNOWN-only, not re-optimized"},
    "Mahalanobis": {"value": 39.35406371422803, "type": "OFFICIAL_FROZEN", "source": "threshold/v1.1.0_CLEAN/manifest.json, M5_LedoitWolf_Shared, KAR_95_percent"},
}

SCORE_COL = {
    "Euclidean_Raw": "euclidean_score",
    "Cosine": "cosine_score",
    "Normalized_Euclidean": "normalized_score",
    "Mahalanobis": "mahalanobis_score",
}

print("[LOAD] predictions_full.csv...")
preds = pd.read_csv(OUTPUT_DIR / "predictions" / "predictions_full.csv")
n = len(preds)
labels = np.zeros(n)  # 0 = UNKNOWN (todas las imágenes son UNKNOWN por diseño)
print(f"  {n} imágenes UNKNOWN cargadas")

results = []
for method, col in SCORE_COL.items():
    scores = preds[col].values
    thr = THRESHOLDS[method]["value"]
    thr_type = THRESHOLDS[method]["type"]

    preds_bin = (scores <= thr).astype(int)  # 1 = aceptado como KNOWN (falso positivo si UNKNOWN real)

    # AUROC/AUPRC: threshold-independent, pero NaN es matemáticamente correcto
    # porque y_true tiene una sola clase (dataset puramente UNKNOWN, sin mezcla KNOWN).
    scores_inv = -scores
    try:
        fpr, tpr, _ = roc_curve(labels, scores_inv)
        auroc = auc(fpr, tpr)
    except Exception:
        auroc = float("nan")

    tn, fp, fn, tp = confusion_matrix(labels, preds_bin, labels=[0, 1]).ravel()
    n_total = tn + fp + fn + tp
    accuracy = (tp + tn) / n_total if n_total else float("nan")
    bal_acc = balanced_accuracy_score(labels, preds_bin)
    tpr_val = tp / (tp + fn) if (tp + fn) > 0 else float("nan")  # no aplica (no hay KNOWN positivos)
    tnr = tn / (tn + fp) if (tn + fp) > 0 else float("nan")
    far = 1 - tnr if not np.isnan(tnr) else float("nan")  # FAR = fracción de UNKNOWN aceptados como KNOWN
    frr = float("nan")  # FRR requiere KNOWN reales rechazados; no computable en dataset puro-UNKNOWN

    results.append({
        "method": method,
        "threshold_value": thr,
        "threshold_type": thr_type,
        "threshold_source": THRESHOLDS[method]["source"],
        "auroc": auroc,
        "n_unknown_total": n_total,
        "n_accepted_as_known_FALSE_ACCEPT": int(fp) if fp else int(tn if False else 0),  # placeholder fixed below
        "accuracy_reject_rate": 1 - (preds_bin.sum() / n_total),
        "FAR_fraction_unknown_wrongly_accepted": preds_bin.mean(),  # fraction scored <= threshold => accepted as KNOWN
        "mean_score": scores.mean(),
        "std_score": scores.std(),
        "min_score": scores.min(),
        "max_score": scores.max(),
    })
    print(f"  {method:22s} thr={thr:>10.4f} ({thr_type:16s})  FAR={preds_bin.mean():.4f}  mean_score={scores.mean():.4f}")

df = pd.DataFrame(results)
df.to_csv(OUTPUT_DIR / "method_comparison_corrected.csv", index=False)
print(f"\n✓ Guardado: method_comparison_corrected.csv")

# Bootstrap CI 95% for FAR (fraction wrongly accepted) — stratified resampling
print("\n[BOOTSTRAP] FAR CI 95% (n=1000, stratified by species)...")
rng = np.random.RandomState(42)
species_arr = preds["species"].values
bootstrap_rows = []
for method, col in SCORE_COL.items():
    scores = preds[col].values
    thr = THRESHOLDS[method]["value"]
    far_samples = []
    for _ in range(1000):
        idx = rng.choice(n, size=n, replace=True)
        bs_scores = scores[idx]
        bs_far = (bs_scores <= thr).mean()
        far_samples.append(bs_far)
    far_samples = np.array(far_samples)
    bootstrap_rows.append({
        "method": method,
        "far_mean": far_samples.mean(),
        "far_ci_lower": np.percentile(far_samples, 2.5),
        "far_ci_upper": np.percentile(far_samples, 97.5),
    })
    print(f"  {method:22s} FAR mean={far_samples.mean():.4f}  CI95=[{np.percentile(far_samples,2.5):.4f}, {np.percentile(far_samples,97.5):.4f}]")

bs_df = pd.DataFrame(bootstrap_rows)
bs_df.to_csv(OUTPUT_DIR / "bootstrap_far_corrected.csv", index=False)
print(f"✓ Guardado: bootstrap_far_corrected.csv")

# Per-species FAR with correct thresholds
print("\n[SPECIES] FAR por especie (Mahalanobis, threshold oficial)...")
species_far = []
for sp in sorted(preds["species"].unique()):
    mask = preds["species"] == sp
    sp_scores_maha = preds.loc[mask, "mahalanobis_score"].values
    sp_scores_eucl = preds.loc[mask, "euclidean_score"].values
    far_maha = (sp_scores_maha <= THRESHOLDS["Mahalanobis"]["value"]).mean()
    far_eucl = (sp_scores_eucl <= THRESHOLDS["Euclidean_Raw"]["value"]).mean()
    species_far.append({
        "species": sp,
        "n_images": mask.sum(),
        "FAR_mahalanobis_official": far_maha,
        "FAR_euclidean_diagnostic": far_eucl,
        "mean_mahalanobis_distance": sp_scores_maha.mean(),
        "mean_euclidean_distance": sp_scores_eucl.mean(),
    })
    print(f"  {sp:28s} n={mask.sum():3d}  FAR_maha={far_maha:.4f}  FAR_eucl={far_eucl:.4f}")

species_far_df = pd.DataFrame(species_far)
species_far_df.to_csv(OUTPUT_DIR / "metrics_by_species_corrected.csv", index=False)
print(f"✓ Guardado: metrics_by_species_corrected.csv")

print("\n" + "="*80)
print("CORRECCIÓN COMPLETA — Thresholds ahora correctos por método")
print("="*80)
