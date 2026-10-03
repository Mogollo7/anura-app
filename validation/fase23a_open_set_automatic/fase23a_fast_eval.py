#!/usr/bin/env python3
"""
FASE 23A — FAST EVALUATION (Batched inference)
Optimizado para ejecución rápida con BioCLIP.
"""

import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)

import json
from pathlib import Path
import numpy as np
import torch
import open_clip
from PIL import Image
from scipy.spatial.distance import cdist
from scipy.stats import gaussian_kde
from sklearn.metrics import roc_curve, auc, precision_recall_curve, confusion_matrix, balanced_accuracy_score, f1_score
import pandas as pd

print("[START] FASE 23A - Fast Evaluation")

# Configuración
ROOT = Path(r"D:\Anura")
UNKNOWN_DIR = ROOT / "data" / "unknown_open_set_v2" / "images" / "final"
KNOWN_EMBEDDINGS = ROOT / "evaluation" / "fase13" / "embeddings" / "train_embeddings.npz"
COVARIANCE_FILE = ROOT / "covariance" / "v1.1.0_CLEAN" / "covariance_matrix.npz"
THRESHOLD = 39.35406371422803
OUTPUT_DIR = ROOT / "validation" / "fase23a_open_set_automatic"

BATCH_SIZE = 32
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[CONFIG] Device: {DEVICE}, Batch: {BATCH_SIZE}")

# Crear output dirs
(OUTPUT_DIR / "plots").mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / "predictions").mkdir(parents=True, exist_ok=True)

# =============================================================================
# 1. LOAD COMPONENTS
# =============================================================================
print("\n[STEP 1] Load BioCLIP encoder...")
model, _, preprocess = open_clip.create_model_and_transforms("hf-hub:imageomics/bioclip")
model = model.to(DEVICE).eval()
print(f"  ✓ Model loaded")

print("[LOAD] Known embeddings...")
data = np.load(KNOWN_EMBEDDINGS)
known_emb = data["embeddings"].astype(np.float32)
known_species = data["species"]
if isinstance(known_species[0], bytes):
    known_species = [s.decode('utf-8') for s in known_species]
print(f"  ✓ {known_emb.shape[0]} known images")

print("[LOAD] Covariance matrix...")
cov_data = np.load(COVARIANCE_FILE)
if "precision" in cov_data.files:
    inv_cov = cov_data["precision"].astype(np.float32)
else:
    cov = cov_data["covariance"].astype(np.float32)
    inv_cov = np.linalg.inv(cov + 1e-6 * np.eye(cov.shape[0]))
print(f"  ✓ Covariance {inv_cov.shape}")

# =============================================================================
# 2. GENERATE UNKNOWN EMBEDDINGS (BATCHED)
# =============================================================================
print("\n[STEP 2] Generate UNKNOWN embeddings (batched)...")

unknown_images = []
unknown_species_list = []
unknown_embs = []

# Discover all images
for sp_dir in sorted(UNKNOWN_DIR.iterdir()):
    if not sp_dir.is_dir():
        continue
    sp_name = sp_dir.name
    for img_path in sorted(sp_dir.glob("*.jpg")) + sorted(sp_dir.glob("*.jpeg")) + sorted(sp_dir.glob("*.png")):
        unknown_images.append(img_path)
        unknown_species_list.append(sp_name)

print(f"  Found {len(unknown_images)} images from {len(set(unknown_species_list))} species")

# Batch processing
for batch_idx in range(0, len(unknown_images), BATCH_SIZE):
    batch_paths = unknown_images[batch_idx:batch_idx + BATCH_SIZE]
    batch_imgs = []

    for img_path in batch_paths:
        try:
            img = Image.open(img_path).convert("RGB")
            batch_imgs.append(preprocess(img))
        except Exception as e:
            print(f"    ✗ Error {img_path.name}: {e}")
            continue

    if batch_imgs:
        batch_tensor = torch.stack(batch_imgs).to(DEVICE)
        with torch.no_grad():
            batch_emb = model.encode_image(batch_tensor)
            batch_emb = batch_emb / batch_emb.norm(dim=-1, keepdim=True)
        unknown_embs.append(batch_emb.cpu().numpy())

    if (batch_idx // BATCH_SIZE + 1) % 5 == 0:
        print(f"  {batch_idx + len(batch_imgs)}/{len(unknown_images)} processed")

unknown_emb = np.concatenate(unknown_embs, axis=0).astype(np.float32)
print(f"  ✓ {unknown_emb.shape[0]} embeddings generated")

# =============================================================================
# 3. COMPUTE DISTANCE SCORES (4 METHODS)
# =============================================================================
print("\n[STEP 3] Compute distance scores (4 methods)...")

# Euclidean
dist_euclidean = cdist(unknown_emb, known_emb, metric="euclidean").min(axis=1)

# Cosine
dist_cosine = cdist(unknown_emb, known_emb, metric="cosine").min(axis=1)

# Normalized Euclidean
unknown_norm = unknown_emb / np.linalg.norm(unknown_emb, axis=1, keepdims=True)
known_norm = known_emb / np.linalg.norm(known_emb, axis=1, keepdims=True)
dist_normalized = cdist(unknown_norm, known_norm, metric="euclidean").min(axis=1)

# Mahalanobis
dist_mahal = []
for emb in unknown_emb:
    dists = []
    for known in known_emb:
        diff = emb - known
        d = np.sqrt(diff @ inv_cov @ diff.T)
        dists.append(d)
    dist_mahal.append(min(dists))
dist_mahal = np.array(dist_mahal)

print(f"  ✓ Euclidean: mean={dist_euclidean.mean():.3f}")
print(f"  ✓ Cosine: mean={dist_cosine.mean():.3f}")
print(f"  ✓ Normalized: mean={dist_normalized.mean():.3f}")
print(f"  ✓ Mahalanobis: mean={dist_mahal.mean():.3f}")

# =============================================================================
# 4. COMPUTE METRICS
# =============================================================================
print("\n[STEP 4] Compute metrics...")

unknown_labels = np.zeros(len(unknown_emb))  # 0 = UNKNOWN

results = []
for name, scores in [
    ("Euclidean_Raw", dist_euclidean),
    ("Cosine", dist_cosine),
    ("Normalized_Euclidean", dist_normalized),
    ("Mahalanobis", dist_mahal),
]:
    # Predictions
    preds = (scores <= THRESHOLD).astype(int)

    # AUROC
    scores_inv = -scores
    fpr, tpr, _ = roc_curve(unknown_labels, scores_inv)
    auroc = auc(fpr, tpr)

    # AUPRC
    precision, recall, _ = precision_recall_curve(unknown_labels, scores_inv)
    auprc = auc(recall, precision)

    # Other metrics
    tn, fp, fn, tp = confusion_matrix(unknown_labels, preds).ravel()
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    bal_acc = balanced_accuracy_score(unknown_labels, preds)
    precision_val = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall_val = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = f1_score(unknown_labels, preds, zero_division=0)
    tpr_val = tp / (tp + fn) if (tp + fn) > 0 else 0
    tnr = tn / (tn + fp) if (tn + fp) > 0 else 0
    far = 1 - tnr
    frr = 1 - tpr_val

    results.append({
        "method": name,
        "auroc": auroc,
        "auprc": auprc,
        "accuracy": accuracy,
        "balanced_accuracy": bal_acc,
        "precision": precision_val,
        "recall": recall_val,
        "f1": f1,
        "tpr": tpr_val,
        "tnr": tnr,
        "far": far,
        "frr": frr,
    })

    print(f"  {name}:")
    print(f"    AUROC={auroc:.4f}, FAR={far:.4f}, FRR={frr:.4f}, F1={f1:.4f}")

results_df = pd.DataFrame(results)
results_df.to_csv(OUTPUT_DIR / "method_comparison.csv", index=False)

# =============================================================================
# 5. SAVE PREDICTIONS
# =============================================================================
print("\n[STEP 5] Save predictions...")

preds_df = pd.DataFrame({
    "image": [p.name for p in unknown_images[:len(unknown_emb)]],
    "species": unknown_species_list[:len(unknown_emb)],
    "euclidean_score": dist_euclidean,
    "cosine_score": dist_cosine,
    "normalized_score": dist_normalized,
    "mahalanobis_score": dist_mahal,
})
preds_df.to_csv(OUTPUT_DIR / "predictions" / "predictions_full.csv", index=False)
print(f"  ✓ {len(preds_df)} predictions saved")

# =============================================================================
# 6. SPECIES ANALYSIS
# =============================================================================
print("\n[STEP 6] Species analysis...")

species_results = []
species_idx = {sp: [] for sp in set(unknown_species_list)}
for i, sp in enumerate(unknown_species_list[:len(unknown_emb)]):
    species_idx[sp].append(i)

taxonomy = {
    "Smilisca_phaeota": "Hylidae",
    "Boana_albifrons": "Hylidae",
    "Pristimantis_brevirostris": "Craugastoridae",
    "Espadarana_prosoblepon": "Centrolenidae",
    "Leptodactylus_fragilis": "Leptodactylidae",
    "Rhinella_marina": "Bufonidae",
    "Dendropsophus_labialis": "Hylidae",
}

for sp in sorted(species_idx.keys()):
    indices = species_idx[sp]
    sp_dist = dist_euclidean[indices]

    # AUROC for this species
    sp_labels = np.zeros(len(indices))
    sp_scores_inv = -sp_dist
    fpr, tpr, _ = roc_curve(sp_labels, sp_scores_inv)
    sp_auroc = auc(fpr, tpr)

    species_results.append({
        "species": sp,
        "n_images": len(indices),
        "family": taxonomy.get(sp, "Unknown"),
        "auroc": sp_auroc,
        "mean_distance": sp_dist.mean(),
        "std_distance": sp_dist.std(),
    })
    print(f"  {sp}: {len(indices)} images, AUROC={sp_auroc:.4f}")

species_df = pd.DataFrame(species_results)
species_df.to_csv(OUTPUT_DIR / "metrics_by_species.csv", index=False)

# =============================================================================
# 7. GENERATE REPORT
# =============================================================================
print("\n[STEP 7] Generate report...")

report = f"""# FASE 23A — EVALUACIÓN OPEN SET CON DATOS AUTOMÁTICOS

**Status:** FASE23A_COMPLETE
**Fecha:** 2026-09-14
**Dataset:** UNKNOWN_V2.1 PRIMARY (automático)

## Resumen

- **Imágenes UNKNOWN:** {len(unknown_emb)}
- **Especies UNKNOWN:** {len(set(unknown_species_list))}
- **Encoder:** BioCLIP congelado (Fase 13)
- **Threshold oficial:** {THRESHOLD:.2f}
- **Métodos:** 4 (Euclidean, Cosine, Normalized Euclidean, Mahalanobis)

## Resultados Principales

### Comparación de Métodos

"""
report += results_df[["method", "auroc", "auprc", "balanced_accuracy", "far", "frr"]].to_string(index=False)

report += """

### Análisis por Especie

"""
report += species_df[["species", "n_images", "family", "auroc", "mean_distance"]].to_string(index=False)

report += """

## Artefactos Generados

- method_comparison.csv (4 métodos)
- metrics_by_species.csv (7 especies)
- predictions/predictions_full.csv (todas las predicciones)

**No se realizó commit ni push.**
"""

(OUTPUT_DIR / "FASE23A_COMPLETE_REPORT.md").write_text(report, encoding="utf-8")
print(f"  ✓ Report saved")

# =============================================================================
# COMPLETION
# =============================================================================
print("\n" + "="*80)
print("FASE 23A COMPLETE")
print("="*80)
print(f"Output directory: {OUTPUT_DIR}/")
print(f"Results:")
for _, row in results_df.iterrows():
    print(f"  {row['method']}: AUROC={row['auroc']:.4f}")
print("\nNo commit or push made.")
