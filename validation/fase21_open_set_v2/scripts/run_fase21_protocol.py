"""
run_fase21_protocol.py -- FASE 21: Validación independiente de Open Set V2
Protocolo riguroso de comparación experimental entre métodos de distancia.

CONTEXTO (Fase 20):
- Raw embedding BioCLIP: AUROC ≈ 0.6936 (centroides oficiales)
- Post-processing Mahalanobis actual: AUROC ≈ 0.5920
- Euclidean sobre embedding crudo: mejor método diagnóstico
- UNKNOWN insuficiente: 2 especies, 35 individuos, 56 imágenes
- BioCLIP congelado, sin fine-tuning, sin commit/push

HIPÓTESIS CENTRAL H1:
Una distancia no-whitened (Euclidean o Cosine) sobre embedding BioCLIP preserva mejor
separación KNOWN/UNKNOWN que Mahalanobis con covarianza compartida.

PROTOCOLO (orden estricto):
21.1 — Diseñar protocolo antes de calcular
21.2 — Construir tres pipelines candidatos
21.3 — Calibración separada
21.4 — Evaluación independiente (VALIDATION + BLIND TEST)
21.5 — Comparación estadística
21.6 — Análisis por taxonomía
21.7 — Análisis de especies difíciles
21.8 — Ablation del Mahalanobis (6 variantes)
21.9 — Evaluar estabilidad de covarianza
21.10 — Prueba contra hipótesis alternativa
21.11 — Criterio de decisión estricto
21.12 — No tocar producción

PURAMENTE DIAGNOSTICO. No modifica BioCLIP, no reentrena, no recalibra threshold/covariance
oficiales. Reutiliza embeddings ya extraídos. Escribe SOLO bajo validation/fase21_open_set_v2/.
"""
import csv
import hashlib
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Tuple, List

import numpy as np
from scipy.spatial.distance import cdist, euclidean, cosine
from scipy.optimize import minimize_scalar
from sklearn.metrics import (
    roc_auc_score, precision_recall_curve, auc,
    confusion_matrix, balanced_accuracy_score, precision_score, recall_score, f1_score
)
from sklearn.covariance import LedoitWolf

ROOT = Path(r"D:\Anura")
OUT = ROOT / "validation" / "fase21_open_set_v2"
sys.path.insert(0, str(ROOT / "tools" / "catalog"))

try:
    from taxonomic_resolution import SpeciesResolver
except ImportError:
    print("[WARN] taxonomic_resolution not found, fallback mode")
    SpeciesResolver = None

RNG = np.random.RandomState(21)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_content(data):
    """SHA256 of binary data."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest()


def stats_block(arr):
    arr = np.asarray(arr, dtype=float)
    return {
        "n": int(len(arr)), "mean": float(arr.mean()), "median": float(np.median(arr)),
        "std": float(arr.std()),
        "p10": float(np.percentile(arr, 10)), "p25": float(np.percentile(arr, 25)),
        "p50": float(np.percentile(arr, 50)), "p75": float(np.percentile(arr, 75)),
        "p90": float(np.percentile(arr, 90)), "p95": float(np.percentile(arr, 95)),
        "p99": float(np.percentile(arr, 99)),
    }


def youden_j_optimal_threshold(y_true, scores, higher_is_more_unknown=True):
    """
    Find threshold that maximizes Youden's J statistic.
    y_true: 1=UNKNOWN, 0=KNOWN
    scores: distance-like metric (higher => more anomalous if higher_is_more_unknown=True)
    Returns: optimal_threshold, max_youden_j
    """
    if not higher_is_more_unknown:
        scores = -scores

    unique_scores = np.unique(scores)
    best_tau = None
    best_youden = -np.inf

    for tau in unique_scores:
        known_mask = y_true == 0
        unknown_mask = y_true == 1

        # FAR: False Acceptance Rate (UNKNOWN accepted incorrectly)
        far = float(np.mean(scores[unknown_mask] <= tau)) if unknown_mask.sum() else 0.0

        # FRR: False Rejection Rate (KNOWN rejected incorrectly)
        frr = float(np.mean(scores[known_mask] > tau)) if known_mask.sum() else 0.0

        # Youden's J = TPR + TNR - 1 = (1-FRR) + (1-FAR) - 1
        kar = 1.0 - frr  # True Positive Rate for KNOWN
        udr = 1.0 - far  # True Negative Rate for UNKNOWN
        youden = kar + udr - 1.0

        if youden > best_youden:
            best_youden = youden
            best_tau = tau

    return best_tau if best_tau is not None else np.median(scores), best_youden


def evaluate_distance_metric(y_true, scores, metric_name="unknown_metric"):
    """
    Evaluate distance metric performance.
    y_true: 1=UNKNOWN, 0=KNOWN
    scores: distance-like (higher => more anomalous)
    Returns: dict with AUROC, optimal_threshold, metrics
    """
    try:
        auroc = roc_auc_score(y_true, scores)
    except Exception as e:
        print(f"[WARN] AUROC computation failed ({metric_name}): {e}")
        auroc = np.nan

    # Precision-Recall AUC (if feasible)
    try:
        precision, recall, _ = precision_recall_curve(y_true, scores)
        prc_auc = auc(recall, precision) if len(recall) > 1 else np.nan
    except Exception as e:
        prc_auc = np.nan

    # Optimal threshold (Youden's J)
    opt_tau, opt_youden = youden_j_optimal_threshold(y_true, scores, higher_is_more_unknown=True)

    # Evaluate at optimal threshold
    known_mask = y_true == 0
    unknown_mask = y_true == 1
    far = float(np.mean(scores[unknown_mask] <= opt_tau)) if unknown_mask.sum() else np.nan
    frr = float(np.mean(scores[known_mask] > opt_tau)) if known_mask.sum() else np.nan
    kar = 1.0 - frr if not np.isnan(frr) else np.nan
    udr = 1.0 - far if not np.isnan(far) else np.nan
    bacc = (kar + udr) / 2.0 if not (np.isnan(kar) or np.isnan(udr)) else np.nan

    # Confusion matrix based metrics
    y_pred = (scores > opt_tau).astype(int)  # 1 = UNKNOWN, 0 = KNOWN
    try:
        precision = precision_score(y_true, y_pred, zero_division=np.nan)
        recall = recall_score(y_true, y_pred, zero_division=np.nan)
        f1 = f1_score(y_true, y_pred, zero_division=np.nan)
    except Exception as e:
        precision = recall = f1 = np.nan

    return {
        "auroc": auroc,
        "pr_auc": prc_auc,
        "optimal_threshold": float(opt_tau),
        "youden_j": float(opt_youden),
        "far": float(far),
        "frr": float(frr),
        "kar": float(kar),
        "udr": float(udr),
        "balanced_accuracy": float(bacc),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }


def main():
    print("\n" + "=" * 80)
    print("FASE 21 — VALIDACIÓN INDEPENDIENTE DE OPEN SET V2")
    print("Protocolo riguroso: Euclidean vs Cosine vs Mahalanobis")
    print("=" * 80 + "\n")

    # ══════════════════════════════════════════════════════════════════════════════
    # FASE 21.1: DISEÑAR PROTOCOLO ANTES DE CALCULAR
    # Inspeccionar datasets, garantías de independencia, ubicación de embeddings/centroides
    # ══════════════════════════════════════════════════════════════════════════════
    print("[FASE 21.1] Diseño de protocolo: inspección de datasets y garantías de independencia\n")

    # 21.1.1: Verificar encoder
    encoder_path = ROOT / "bioclip/checkpoints/encoder_anura_fp16.onnx"
    encoder_sha = sha256_file(encoder_path)
    expected_sha = "219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad"
    encoder_match = (encoder_sha == expected_sha)
    print(f"[encoder] Verificación SHA256: {encoder_match}")
    if not encoder_match:
        print(f"  ACTUAL:   {encoder_sha}")
        print(f"  ESPERADO: {expected_sha}")
        print("[ERROR] Encoder no coincide. Abortar.")
        return

    # 21.1.2: Cargar todos los datasets
    print("\n[datasets] Cargando embeddings y manifests...")
    ref = np.load(ROOT / "evaluation/fase13/embeddings/reference_embeddings.npz")
    train = np.load(ROOT / "evaluation/fase13/embeddings/train_embeddings.npz")
    clean = np.load(ROOT / "validation/fase16_clean_open_set/clean_known_embeddings.npz")

    with open(ROOT / "validation/fase16_clean_open_set/clean_known_manifest.json", encoding="utf-8") as f:
        clean_manifest = json.load(f)

    # UNKNOWN (F4)
    f4_all = np.load(ROOT / "evaluation/open_set_v1/knn/knn_embeddings.npz")["embeddings"].astype(np.float32)
    with open(ROOT / "evaluation/open_set_v1/knn/knn_open_set_results.json", encoding="utf-8") as f:
        f3f4_records = json.load(f)["records"]

    unknown_records = [r for r in f3f4_records if r["known_unknown"] == "UNKNOWN"]
    unknown_idx = [i for i, r in enumerate(f3f4_records) if r["known_unknown"] == "UNKNOWN"]
    X_unknown = f4_all[unknown_idx]

    # Catalog
    with open(ROOT / "visual_catalog/v1.0.0/manifest.json", encoding="utf-8") as f:
        catalog = json.load(f)
    release_species_ids = set(catalog["species_ids"])

    print(f"  REFERENCE: {ref['embeddings'].shape[0]} imágenes, {len(np.unique(ref['species']))} especies")
    print(f"  TRAIN:     {train['embeddings'].shape[0]} imágenes, {len(np.unique(train['species']))} especies")
    print(f"  KNOWN limpio (Fase16): {clean['embeddings'].shape[0]} imágenes")
    print(f"  UNKNOWN (F4): {X_unknown.shape[0]} imágenes")

    # 21.1.3: Verificar dimensiones
    dim_ok = (ref["embeddings"].shape[1] == 512 and clean["embeddings"].shape[1] == 512
              and X_unknown.shape[1] == 512)
    print(f"[dimensión] Todas 512-D: {dim_ok}")

    # 21.1.4: Identificar SPLIT structure
    # Del reporte de Fase 16:
    # REFERENCE: 798 imágenes (calibra covarianza)
    # CALIBRATION: 192 imágenes (calibra threshold)
    # TRAIN: 4724 imágenes (centroides Group B)
    # KNOWN limpio (Fase16): 7475 imágenes → VALIDATION + BLIND TEST (separar)
    # UNKNOWN: 56 imágenes (F4) → BLIND TEST
    print(f"\n[split_structure] Composición de datasets según protocolo:")
    print(f"  TRAIN (centroides Group B):              {train['embeddings'].shape[0]} imágenes")
    print(f"  REFERENCE (centroides Group A + cov):    {ref['embeddings'].shape[0]} imágenes")
    print(f"  CALIBRATION (threshold calibration):     192 imágenes (implícito en Fase13)")
    print(f"  KNOWN limpio (Fase16):                   {clean['embeddings'].shape[0]} imágenes")
    print(f"  UNKNOWN (F4):                             {X_unknown.shape[0]} imágenes")

    # 21.1.5: Separar VALIDATION de BLIND TEST
    # Usaremos: 60% KNOWN limpio = VALIDATION, 40% = BLIND TEST
    # UNKNOWN completo = BLIND TEST (separado)
    n_known_total = clean["embeddings"].shape[0]
    n_validation = int(np.ceil(0.60 * n_known_total))
    validation_idx = np.arange(n_validation)
    blind_known_idx = np.arange(n_validation, n_known_total)

    X_validation_known = clean["embeddings"][validation_idx]
    X_blind_known = clean["embeddings"][blind_known_idx]

    print(f"\n[split] KNOWN limpio dividido:")
    print(f"  VALIDATION (60%):  {X_validation_known.shape[0]} imágenes")
    print(f"  BLIND TEST (40%):  {X_blind_known.shape[0]} imágenes")
    print(f"  BLIND TEST UNKNOWN: {X_unknown.shape[0]} imágenes")

    # Construir etiquetas
    y_validation = np.zeros(X_validation_known.shape[0], dtype=int)  # 0 = KNOWN
    y_blind = np.concatenate([
        np.zeros(X_blind_known.shape[0], dtype=int),
        np.ones(X_unknown.shape[0], dtype=int)
    ])
    X_blind = np.vstack([X_blind_known, X_unknown])

    print(f"  Total VALIDATION: {len(y_validation)} imágenes (todas KNOWN)")
    print(f"  Total BLIND TEST: {len(y_blind)} imágenes ({np.sum(y_blind == 0)} KNOWN, {np.sum(y_blind == 1)} UNKNOWN)")

    # 21.1.6: Resolvers para taxonomía
    if SpeciesResolver:
        try:
            resolver = SpeciesResolver(ROOT / "training/taxonomia.py",
                                      ROOT / "taxonomy/species/species_registry.json")
        except Exception as e:
            print(f"[WARN] SpeciesResolver error: {e}. Fallback to direct taxonomia.py")
            resolver = None
    else:
        resolver = None

    import importlib.util
    spec = importlib.util.spec_from_file_location("taxonomia", ROOT / "training/taxonomia.py")
    taxonomia = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(taxonomia)
    except Exception as e:
        print(f"[WARN] taxonomia.py load error: {e}. Some taxonomic operations will be limited")
        taxonomia = None

    def sp_meta(name_underscored):
        """Get genus and family for a species."""
        if not taxonomia:
            return "UNKNOWN_GENUS", "UNKNOWN_FAMILY"
        try:
            return taxonomia.genero_de(name_underscored), taxonomia.familia_de(name_underscored)
        except Exception:
            return "UNKNOWN_GENUS", "UNKNOWN_FAMILY"

    # 21.1.7: Construir manifests de composición
    protocol_manifest = {
        "phase": "FASE21_OPEN_SET_V2",
        "hypothesis": "H1: Non-whitened distance (Euclidean/Cosine) preserves KNOWN/UNKNOWN separation better than Mahalanobis",
        "encoder_sha256": encoder_sha,
        "encoder_match_with_fase13_16_19": encoder_match,
        "datasets": {
            "reference": {
                "n_images": int(ref["embeddings"].shape[0]),
                "n_species": int(len(np.unique(ref["species"]))),
                "role": "REFERENCE (Group A centroids + covariance source)"
            },
            "train": {
                "n_images": int(train["embeddings"].shape[0]),
                "n_species": int(len(np.unique(train["species"]))),
                "role": "TRAIN (Group B centroids)"
            },
            "known_clean": {
                "n_images": n_known_total,
                "role": "KNOWN clean from Fase16 (no leakage verified)"
            },
            "unknown": {
                "n_images": int(X_unknown.shape[0]),
                "n_species": len(unknown_records),
                "role": "UNKNOWN (F4, held-out)"
            }
        },
        "splits": {
            "validation": {
                "n_images": X_validation_known.shape[0],
                "composition": "60% of KNOWN clean",
                "use": "Compare methods, select best"
            },
            "blind_test_known": {
                "n_images": X_blind_known.shape[0],
                "composition": "40% of KNOWN clean",
                "use": "Independent evaluation"
            },
            "blind_test_unknown": {
                "n_images": int(X_unknown.shape[0]),
                "composition": "F4 (held-out UNKNOWN)",
                "use": "Independent evaluation"
            }
        },
        "independence_guarantees": {
            "encoder_frozen": True,
            "bioclip_not_retrained": True,
            "no_production_modification": True,
            "known_clean_excludes_reference_train": True,
            "note": "UNKNOWN independence from KNOWN per Fase16 audit (F4 clean)"
        },
        "data_limitation": {
            "unknown_coverage": "2 real species only (insufficient for general conclusions)",
            "unknown_images": 56,
            "known_species_with_images": "24/41 catalog species"
        }
    }

    with open(OUT / "protocol_manifest.json", "w", encoding="utf-8") as f:
        json.dump(protocol_manifest, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] FASE 21.1 completado. Protocol manifest guardado.")

    # ══════════════════════════════════════════════════════════════════════════════
    # FASE 21.2: CONSTRUIR TRES PIPELINES CANDIDATOS
    # V2-EUCLIDEAN, V2-COSINE, V2-MAHALANOBIS
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n[FASE 21.2] Construcción de pipelines candidatos\n")

    # Preparar centroides oficiales (como en Fase20)
    def resolve_species_name(name):
        """Resolve species name to canonical form."""
        if resolver:
            try:
                return resolver.resolve(name.replace("_", " "))["canonical_name"]
            except Exception:
                pass
        # Fallback: remove underscores
        return name.replace("_", " ")

    ref_canonical = np.array([resolve_species_name(n) for n in ref["species"]])
    train_canonical = np.array([resolve_species_name(n) for n in train["species"]])

    def compute_centroids(X, y):
        return {c: np.mean(X[y == c], axis=0) for c in np.unique(y)}

    ref_centroids = compute_centroids(ref["embeddings"], ref_canonical)
    train_centroids = compute_centroids(train["embeddings"], train_canonical)

    official_centroids = {}
    for name, c in ref_centroids.items():
        try:
            if resolver:
                sid = resolver.resolve(name)["species_id"]
                if sid in release_species_ids:
                    official_centroids[sid] = c
        except Exception:
            pass

    for name, c in train_centroids.items():
        try:
            if resolver:
                sid = resolver.resolve(name)["species_id"]
                if sid in release_species_ids and sid not in official_centroids:
                    official_centroids[sid] = c
        except Exception:
            pass

    centroid_ids = sorted(official_centroids.keys())
    C = np.array([official_centroids[c] for c in centroid_ids])
    print(f"[centroids] Disponibles: {len(centroid_ids)}/{len(release_species_ids)} especies del catálogo")

    # 21.2.1: Pipeline V2-EUCLIDEAN
    def pipeline_euclidean(X, C, normalize=True):
        """
        V2-EUCLIDEAN:
        input embedding → [normalize if requested] → euclidean distance → min distance to centroid
        """
        if normalize:
            # L2 normalization
            X_norm = X / np.linalg.norm(X, axis=1, keepdims=True)
            C_norm = C / np.linalg.norm(C, axis=1, keepdims=True)
        else:
            X_norm = X
            C_norm = C

        # Min euclidean distance
        distances = cdist(X_norm, C_norm, metric='euclidean')
        min_distances = np.min(distances, axis=1)
        return min_distances

    # 21.2.2: Pipeline V2-COSINE
    def pipeline_cosine(X, C):
        """
        V2-COSINE:
        input embedding → cosine distance (1 - cosine_similarity) → min distance to centroid
        """
        # Cosine distance = 1 - cosine_similarity
        # cdist with cosine metric already computes 1 - similarity
        distances = cdist(X, C, metric='cosine')
        min_distances = np.min(distances, axis=1)
        return min_distances

    # 21.2.3: Pipeline V2-MAHALANOBIS (reproduce official)
    def pipeline_mahalanobis(X, C, X_ref_for_cov=None):
        """
        V2-MAHALANOBIS:
        input embedding → center (subtract mean) → mahalanobis with Ledoit-Wolf covariance
        """
        if X_ref_for_cov is None:
            X_ref_for_cov = X

        # Center
        mu = np.mean(X_ref_for_cov, axis=0)
        X_centered = X - mu
        C_centered = C - mu

        # Ledoit-Wolf covariance
        try:
            lw = LedoitWolf()
            lw.fit(X_ref_for_cov)
            cov = lw.covariance_
        except Exception as e:
            print(f"[WARN] Ledoit-Wolf error: {e}. Using sample covariance")
            cov = np.cov(X_ref_for_cov.T)

        # Invert covariance
        try:
            cov_inv = np.linalg.inv(cov)
        except Exception as e:
            print(f"[WARN] Covariance inversion failed: {e}. Using pinv")
            cov_inv = np.linalg.pinv(cov)

        # Mahalanobis distance
        distances = np.zeros((X_centered.shape[0], C_centered.shape[0]))
        for i, x in enumerate(X_centered):
            for j, c in enumerate(C_centered):
                diff = x - c
                distances[i, j] = np.sqrt(diff @ cov_inv @ diff.T)

        min_distances = np.min(distances, axis=1)
        return min_distances

    # Compute scores on VALIDATION split
    print(f"\n[validation] Computar scores...")
    scores_val = {
        "euclidean_normalized": pipeline_euclidean(X_validation_known, C, normalize=True),
        "euclidean_raw": pipeline_euclidean(X_validation_known, C, normalize=False),
        "cosine": pipeline_cosine(X_validation_known, C),
        "mahalanobis": pipeline_mahalanobis(X_validation_known, C, X_ref_for_cov=ref["embeddings"]),
    }

    print(f"  [OK] Scores computados para {X_validation_known.shape[0]} imagenes VALIDATION")

    # Compute scores on BLIND TEST
    print(f"[blind_test] Computar scores...")
    scores_blind = {
        "euclidean_normalized": pipeline_euclidean(X_blind, C, normalize=True),
        "euclidean_raw": pipeline_euclidean(X_blind, C, normalize=False),
        "cosine": pipeline_cosine(X_blind, C),
        "mahalanobis": pipeline_mahalanobis(X_blind, C, X_ref_for_cov=ref["embeddings"]),
    }

    print(f"  [OK] Scores computados para {X_blind.shape[0]} imagenes BLIND TEST")

    print(f"\n[OK] FASE 21.2 completado. Pipelines construidos y evaluados.")

    # ══════════════════════════════════════════════════════════════════════════════
    # FASE 21.3: CALIBRACIÓN SEPARADA
    # Usar VALIDATION para seleccionar threshold (no BLIND TEST)
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n[FASE 21.3] Calibración separada (usar VALIDATION para threshold)\n")

    calibration_results = {}

    for method_name, scores_val_method in scores_val.items():
        print(f"[{method_name}]")

        # Optimal threshold on VALIDATION (Youden's J)
        opt_tau, opt_youden = youden_j_optimal_threshold(y_validation, scores_val_method)

        calibration_results[method_name] = {
            "method": method_name,
            "optimal_threshold_validation": float(opt_tau),
            "youden_j_validation": float(opt_youden),
            "dataset_used": "VALIDATION (60% of KNOWN clean)",
            "hash_validation_set": sha256_content(str(sorted(validation_idx.tolist()))),
        }
        print(f"  Optimal tau: {opt_tau:.6f}, Youden J: {opt_youden:.6f}")

    with open(OUT / "threshold_calibration.json", "w", encoding="utf-8") as f:
        json.dump(calibration_results, f, indent=2)

    print(f"\n[OK] FASE 21.3 completado. Thresholds calibrados en VALIDATION.")

    # ══════════════════════════════════════════════════════════════════════════════
    # FASE 21.4: EVALUACIÓN INDEPENDIENTE
    # Evaluar los tres métodos en BLIND TEST
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n[FASE 21.4] Evaluación independiente en BLIND TEST\n")

    blind_test_results = {}

    for method_name, scores_blind_method in scores_blind.items():
        print(f"[{method_name}]")

        # Evaluate on blind test
        metrics = evaluate_distance_metric(y_blind, scores_blind_method, method_name)
        blind_test_results[method_name] = metrics

        print(f"  AUROC: {metrics['auroc']:.4f}")
        print(f"  Balanced Accuracy: {metrics['balanced_accuracy']:.4f}")
        print(f"  FAR: {metrics['far']:.4f}, FRR: {metrics['frr']:.4f}")
        print()

    with open(OUT / "blind_test_results.json", "w", encoding="utf-8") as f:
        json.dump(blind_test_results, f, indent=2)

    # Save metric comparison CSV
    comparison_rows = []
    for method_name, metrics in blind_test_results.items():
        comparison_rows.append({
            "method": method_name,
            "auroc": metrics["auroc"],
            "pr_auc": metrics["pr_auc"],
            "optimal_threshold": metrics["optimal_threshold"],
            "far": metrics["far"],
            "frr": metrics["frr"],
            "kar": metrics["kar"],
            "udr": metrics["udr"],
            "balanced_accuracy": metrics["balanced_accuracy"],
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
        })

    with open(OUT / "metric_comparison.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=comparison_rows[0].keys())
        writer.writeheader()
        writer.writerows(comparison_rows)

    print(f"[OK] FASE 21.4 completado. Metricas guardadas.")

    n_blind_known = X_blind_known.shape[0]

    # ══════════════════════════════════════════════════════════════════════════════
    # FASE 21.5: COMPARACIÓN ESTADÍSTICA
    # Bootstrap a nivel individual_id
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n[FASE 21.5] Comparacion estadistica (bootstrap a nivel individual)\n")

    statistical_comparison = {
        "bootstrap_samples": 10000,
        "unit": "individual_id (observation in BLIND TEST UNKNOWN)",
        "note": "Bootstrapped at individual level to capture correlations",
        "comparisons": {}
    }

    # Extract individual_id for BLIND TEST UNKNOWN samples
    # This is a simplified version - in reality we'd need the manifest with individual_id
    unknown_individual_groups = defaultdict(list)
    obs_pat = re.compile(r"col_obs_(\d+)_photo")
    for i, r in enumerate(unknown_records):
        m = obs_pat.search(r["path"])
        ind = m.group(1) if m else f"__noind__{i}"
        unknown_individual_groups[ind].append(i)

    # For BOOTSTRAP: we resample individuals (not images)
    n_unknown_individuals = len(unknown_individual_groups)
    bootstrap_samples = 10000

    print(f"[bootstrap] UNKNOWN individuals: {n_unknown_individuals}, samples: {bootstrap_samples}")

    # Compare methods pairwise
    method_pairs = [
        ("euclidean_normalized", "mahalanobis"),
        ("cosine", "mahalanobis"),
        ("euclidean_normalized", "cosine"),
    ]

    for m1, m2 in method_pairs:
        print(f"  Comparing {m1} vs {m2}...")

        # Bootstrap difference in AUROC
        auroc_diff_samples = []
        for _ in range(bootstrap_samples):
            # Resample individuals with replacement
            sampled_inds = np.random.choice(list(unknown_individual_groups.keys()),
                                           size=n_unknown_individuals, replace=True)
            sampled_idx = []
            for ind in sampled_inds:
                sampled_idx.extend(unknown_individual_groups[ind])

            # Indices in blind_test space
            sampled_idx_blind = [n_blind_known + idx for idx in sampled_idx]
            y_sampled = y_blind[sampled_idx_blind]
            scores_m1_sampled = scores_blind[m1][sampled_idx_blind]
            scores_m2_sampled = scores_blind[m2][sampled_idx_blind]

            try:
                auroc_m1 = roc_auc_score(y_sampled, scores_m1_sampled)
                auroc_m2 = roc_auc_score(y_sampled, scores_m2_sampled)
                auroc_diff_samples.append(auroc_m1 - auroc_m2)
            except Exception:
                pass

        auroc_diff_array = np.array(auroc_diff_samples)
        ci_lower = np.percentile(auroc_diff_array, 2.5)
        ci_upper = np.percentile(auroc_diff_array, 97.5)

        statistical_comparison["comparisons"][f"{m1}_vs_{m2}"] = {
            "mean_auroc_diff": float(np.mean(auroc_diff_array)),
            "std_auroc_diff": float(np.std(auroc_diff_array)),
            "ci_lower_2_5": float(ci_lower),
            "ci_upper_97_5": float(ci_upper),
            "note": "Positive = m1 better"
        }

    with open(OUT / "statistical_comparison.json", "w", encoding="utf-8") as f:
        json.dump(statistical_comparison, f, indent=2)

    print(f"[OK] FASE 21.5 completado. Comparacion estadistica guardada.")

    # ══════════════════════════════════════════════════════════════════════════════
    # FASE 21.8: ABLATION DEL MAHALANOBIS (OBLIGATORIO)
    # Construir 6 variantes y evaluar en VALIDATION
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n[FASE 21.8] Ablation de Mahalanobis (6 variantes en VALIDATION)\n")

    ablation_results = []

    # A. Raw + Euclidean
    print("A. Raw + Euclidean")
    scores_a = pipeline_euclidean(X_validation_known, C, normalize=False)
    try:
        auroc_a = roc_auc_score(y_validation, scores_a)
    except Exception as e:
        auroc_a = np.nan
    _, youden_a = youden_j_optimal_threshold(y_validation, scores_a)
    far_a, frr_a, bacc_a, _ = evaluate_distance_metric(y_validation, scores_a)["far"], \
                               evaluate_distance_metric(y_validation, scores_a)["frr"], \
                               evaluate_distance_metric(y_validation, scores_a)["balanced_accuracy"], None
    ablation_results.append({"pipeline": "A_raw_euclidean", "auroc": auroc_a,
                             "far": far_a, "frr": frr_a, "balanced_acc": bacc_a})
    print(f"  AUROC: {auroc_a:.4f}, balanced_acc: {bacc_a:.4f}")

    # B. Raw + Cosine
    print("B. Raw + Cosine")
    scores_b = pipeline_cosine(X_validation_known, C)
    try:
        auroc_b = roc_auc_score(y_validation, scores_b)
    except Exception as e:
        auroc_b = np.nan
    metrics_b = evaluate_distance_metric(y_validation, scores_b)
    ablation_results.append({"pipeline": "B_raw_cosine", "auroc": metrics_b["auroc"],
                             "far": metrics_b["far"], "frr": metrics_b["frr"],
                             "balanced_acc": metrics_b["balanced_accuracy"]})
    print(f"  AUROC: {metrics_b['auroc']:.4f}, balanced_acc: {metrics_b['balanced_accuracy']:.4f}")

    # C. Centered + Euclidean
    print("C. Centered + Euclidean")
    mu_center = np.mean(X_validation_known, axis=0)
    X_val_centered = X_validation_known - mu_center
    C_centered = C - mu_center
    distances_c = cdist(X_val_centered / np.linalg.norm(X_val_centered, axis=1, keepdims=True),
                        C_centered / np.linalg.norm(C_centered, axis=1, keepdims=True),
                        metric='euclidean')
    scores_c = np.min(distances_c, axis=1)
    metrics_c = evaluate_distance_metric(y_validation, scores_c)
    ablation_results.append({"pipeline": "C_centered_euclidean", "auroc": metrics_c["auroc"],
                             "far": metrics_c["far"], "frr": metrics_c["frr"],
                             "balanced_acc": metrics_c["balanced_accuracy"]})
    print(f"  AUROC: {metrics_c['auroc']:.4f}, balanced_acc: {metrics_c['balanced_accuracy']:.4f}")

    # D. Centered + Cosine
    print("D. Centered + Cosine")
    distances_d = cdist(X_val_centered, C_centered, metric='cosine')
    scores_d = np.min(distances_d, axis=1)
    metrics_d = evaluate_distance_metric(y_validation, scores_d)
    ablation_results.append({"pipeline": "D_centered_cosine", "auroc": metrics_d["auroc"],
                             "far": metrics_d["far"], "frr": metrics_d["frr"],
                             "balanced_acc": metrics_d["balanced_accuracy"]})
    print(f"  AUROC: {metrics_d['auroc']:.4f}, balanced_acc: {metrics_d['balanced_accuracy']:.4f}")

    # E. Centered + Mahalanobis
    print("E. Centered + Mahalanobis")
    scores_e = pipeline_mahalanobis(X_validation_known, C, X_ref_for_cov=ref["embeddings"])
    metrics_e = evaluate_distance_metric(y_validation, scores_e)
    ablation_results.append({"pipeline": "E_centered_mahalanobis", "auroc": metrics_e["auroc"],
                             "far": metrics_e["far"], "frr": metrics_e["frr"],
                             "balanced_acc": metrics_e["balanced_accuracy"]})
    print(f"  AUROC: {metrics_e['auroc']:.4f}, balanced_acc: {metrics_e['balanced_accuracy']:.4f}")

    # F. Normalized + Euclidean (already computed as "euclidean_normalized")
    print("F. Normalized + Euclidean")
    metrics_f = evaluate_distance_metric(y_validation, scores_val["euclidean_normalized"])
    ablation_results.append({"pipeline": "F_normalized_euclidean", "auroc": metrics_f["auroc"],
                             "far": metrics_f["far"], "frr": metrics_f["frr"],
                             "balanced_acc": metrics_f["balanced_accuracy"]})
    print(f"  AUROC: {metrics_f['auroc']:.4f}, balanced_acc: {metrics_f['balanced_accuracy']:.4f}")

    # Save ablation CSV
    with open(OUT / "ablation_mahalanobis.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["pipeline", "auroc", "far", "frr", "balanced_acc"])
        writer.writeheader()
        writer.writerows(ablation_results)

    print(f"\n[OK] FASE 21.8 completado. Ablation table guardada.")

    # ══════════════════════════════════════════════════════════════════════════════
    # FINAL SUMMARY
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("FASE 21 — RESUMEN PARCIAL")
    print("=" * 80)
    print("\nMétodos evaluados en BLIND TEST:")
    for method_name, metrics in blind_test_results.items():
        print(f"\n{method_name.upper()}:")
        print(f"  AUROC: {metrics['auroc']:.4f}")
        print(f"  Balanced Accuracy: {metrics['balanced_accuracy']:.4f}")
        print(f"  FAR: {metrics['far']:.4f}, FRR: {metrics['frr']:.4f}")

    print(f"\nArtefactos generados bajo: {OUT}")
    print(f"  - protocol_manifest.json")
    print(f"  - threshold_calibration.json")
    print(f"  - blind_test_results.json")
    print(f"  - metric_comparison.csv")
    print(f"  - statistical_comparison.json")
    print(f"  - ablation_mahalanobis.csv")

    print("\n[OK] FASE 21 ejecución parcial completada.")
    print("  Pasos 21.1-21.5, 21.8 completados.")
    print("  Pasos 21.6, 21.7, 21.9, 21.10, 21.11, 21.12 requieren análisis adicional.")


if __name__ == "__main__":
    main()
