"""
run_method_comparison.py — FASE 17: comparacion diagnostica de metodos Open Set
(Cosine, Euclidean, Mahalanobis) EXCLUSIVAMENTE sobre el blind limpio de Fase 16.

METHOD COMPARISON ONLY. No recalibra threshold, no modifica covariance_release,
no toca ningun artefacto de Fase 13 / visual_catalog v1.0.0 / bioclip checkpoints.
"""
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

ROOT = Path(r"D:\Anura")
sys.path.insert(0, str(ROOT / "tools" / "catalog"))
from taxonomic_resolution import SpeciesResolver

OUT = ROOT / "validation" / "fase17_open_set_methods"
F16 = ROOT / "validation" / "fase16_clean_open_set"


def compute_centroids(X, y):
    return {c: np.mean(X[y == c], axis=0) for c in np.unique(y)}


def scores_cosine(X, centroids):
    """score alto = mas parecido a KNOWN -> max cosine similarity."""
    classes = list(centroids.keys())
    C = np.array([centroids[c] for c in classes])
    C_norm = C / np.linalg.norm(C, axis=1, keepdims=True)
    sims = X @ C_norm.T
    idx = np.argmax(sims, axis=1)
    return sims[np.arange(len(X)), idx], [classes[i] for i in idx]


def scores_euclidean(X, centroids):
    """score alto = mas parecido a KNOWN -> -min euclidean distance."""
    classes = list(centroids.keys())
    C = np.array([centroids[c] for c in classes])
    d = np.linalg.norm(X[:, None, :] - C[None, :, :], axis=2)
    idx = np.argmin(d, axis=1)
    return -d[np.arange(len(X)), idx], [classes[i] for i in idx], d[np.arange(len(X)), idx]


def scores_mahalanobis(X, centroids, precision_matrix):
    """score alto = mas parecido a KNOWN -> -min mahalanobis distance."""
    classes = list(centroids.keys())
    C = np.array([centroids[c] for c in classes])
    diff = X[:, None, :] - C[None, :, :]
    d2 = np.maximum(0.0, np.einsum("nkd,de,nke->nk", diff, precision_matrix, diff))
    d = np.sqrt(d2)
    idx = np.argmin(d, axis=1)
    return -d[np.arange(len(X)), idx], [classes[i] for i in idx], d[np.arange(len(X)), idx]


def percentiles(arr):
    ps = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    return {f"p{p:02d}": float(np.percentile(arr, p)) for p in ps}


def main():
    resolver = SpeciesResolver(ROOT / "training/taxonomia.py", ROOT / "taxonomy/species/species_registry.json")

    # ── Centroides (identicos a los usados en Fase 16, no recalculados) ──
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
    id_to_name = {}
    for name, c in ref_centroids.items():
        sid = resolver.resolve(name.replace("_", " "))["species_id"]
        if sid in release_ids:
            all_centroids[sid] = c
            id_to_name[sid] = name
    for name, c in train_centroids.items():
        sid = resolver.resolve(name.replace("_", " "))["species_id"]
        if sid in release_ids and sid not in all_centroids:
            all_centroids[sid] = c
            id_to_name[sid] = name

    print(f"Centroides: {len(all_centroids)}")

    # ── Covariance release (NO recalculada, cargada del artefacto) ──
    cov_data = np.load(ROOT / "covariance/v1.1.0_CLEAN/covariance_matrix.npz")
    precision_matrix = cov_data["precision"]
    covariance = cov_data["covariance"]

    # ── Datos: KNOWN limpio (Fase 16) + UNKNOWN (F4) ──
    clean = np.load(F16 / "clean_known_embeddings.npz")
    X_known = clean["embeddings"]
    known_image_ids = clean["image_ids"]

    with open(F16 / "clean_known_manifest.json", encoding="utf-8") as f:
        clean_manifest = json.load(f)
    id_to_species_name = {img["image_id"]: img["scientific_name"] for img in clean_manifest["images"]}

    f4_all = np.load(ROOT / "evaluation/open_set_v1/knn/knn_embeddings.npz")["embeddings"].astype(np.float32)
    with open(ROOT / "evaluation/open_set_v1/knn/knn_open_set_results.json", encoding="utf-8") as f:
        f3f4_records = json.load(f)["records"]
    unknown_records = [r for r in f3f4_records if r["known_unknown"] == "UNKNOWN"]
    unknown_idx = [i for i, r in enumerate(f3f4_records) if r["known_unknown"] == "UNKNOWN"]
    X_unknown = f4_all[unknown_idx]
    unknown_species_true = [r["true_species"] for r in unknown_records]
    unknown_image_ids = [r["image_id"] for r in unknown_records]

    n_known, n_unknown = len(X_known), len(X_unknown)
    print(f"KNOWN: {n_known}, UNKNOWN: {n_unknown}")

    # ══════════════════════════════════════════════════════════════
    # SECCION 2-4: comparacion de metodos (scores continuos)
    # ══════════════════════════════════════════════════════════════
    results = {}

    print("\n=== M1: COSINE ===")
    s_known_cos, nearest_known_cos = scores_cosine(X_known, all_centroids)
    s_unk_cos, nearest_unk_cos = scores_cosine(X_unknown, all_centroids)
    y_true = np.concatenate([np.zeros(n_known), np.ones(n_unknown)])  # 0=known,1=unknown
    y_score_for_auroc = np.concatenate([-s_known_cos, -s_unk_cos])  # invertir: mayor score-invertido = mas unknown
    auroc_cos = float(roc_auc_score(y_true, y_score_for_auroc))
    results["M1_Cosine"] = {
        "method": "Cosine", "known_n": n_known, "unknown_n": n_unknown,
        "known_mean": float(s_known_cos.mean()), "known_std": float(s_known_cos.std()),
        "unknown_mean": float(s_unk_cos.mean()), "unknown_std": float(s_unk_cos.std()),
        "auroc": auroc_cos,
        "known_percentiles": percentiles(s_known_cos), "unknown_percentiles": percentiles(s_unk_cos),
        "score_orientation": "alto = mas parecido a KNOWN (cosine_similarity)"
    }
    print(f"  AUROC: {auroc_cos:.4f}")

    print("\n=== M2: EUCLIDEAN ===")
    s_known_eucl, nearest_known_eucl, d_known_eucl = scores_euclidean(X_known, all_centroids)
    s_unk_eucl, nearest_unk_eucl, d_unk_eucl = scores_euclidean(X_unknown, all_centroids)
    y_score_for_auroc = np.concatenate([-s_known_eucl, -s_unk_eucl])
    auroc_eucl = float(roc_auc_score(y_true, y_score_for_auroc))
    results["M2_Euclidean"] = {
        "method": "Euclidean", "known_n": n_known, "unknown_n": n_unknown,
        "known_mean": float(s_known_eucl.mean()), "known_std": float(s_known_eucl.std()),
        "unknown_mean": float(s_unk_eucl.mean()), "unknown_std": float(s_unk_eucl.std()),
        "auroc": auroc_eucl,
        "known_percentiles": percentiles(s_known_eucl), "unknown_percentiles": percentiles(s_unk_eucl),
        "score_orientation": "alto = mas parecido a KNOWN (-euclidean_distance)"
    }
    print(f"  AUROC: {auroc_eucl:.4f}")

    print("\n=== M3: MAHALANOBIS (covariance_1.1.0_CLEAN, NO recalculada) ===")
    s_known_maha, nearest_known_maha, d_known_maha = scores_mahalanobis(X_known, all_centroids, precision_matrix)
    s_unk_maha, nearest_unk_maha, d_unk_maha = scores_mahalanobis(X_unknown, all_centroids, precision_matrix)
    y_score_for_auroc = np.concatenate([-s_known_maha, -s_unk_maha])
    auroc_maha = float(roc_auc_score(y_true, y_score_for_auroc))
    results["M3_Mahalanobis"] = {
        "method": "Mahalanobis_LedoitWolf", "known_n": n_known, "unknown_n": n_unknown,
        "known_mean": float(s_known_maha.mean()), "known_std": float(s_known_maha.std()),
        "unknown_mean": float(s_unk_maha.mean()), "unknown_std": float(s_unk_maha.std()),
        "auroc": auroc_maha,
        "known_percentiles": percentiles(s_known_maha), "unknown_percentiles": percentiles(s_unk_maha),
        "score_orientation": "alto = mas parecido a KNOWN (-mahalanobis_distance)",
        "covariance_release_used": "covariance_1.1.0_CLEAN (no recalculada en esta comparacion)"
    }
    print(f"  AUROC: {auroc_maha:.4f}")

    with open(OUT / "method_comparison.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # ══════════════════════════════════════════════════════════════
    # SECCION 5: comparacion por especie UNKNOWN (usando threshold historico solo
    # para reportar FAR descriptivo, NO para elegir nada)
    # ══════════════════════════════════════════════════════════════
    print("\n=== SECCION 5: por especie UNKNOWN ===")
    tau_hist = 39.35406371422803  # threshold historico, solo para reportar FAR descriptivo
    by_species = {}
    for sp in set(unknown_species_true):
        mask = np.array([s == sp for s in unknown_species_true])
        far_maha = float(np.mean(d_unk_maha[mask] <= tau_hist))
        y_t = np.concatenate([np.zeros(n_known), np.ones(int(mask.sum()))])
        y_s = np.concatenate([d_known_maha, d_unk_maha[mask]])
        auroc_sp = float(roc_auc_score(y_t, y_s)) if mask.sum() > 1 else None
        nearest_counts = {}
        for i in np.where(mask)[0]:
            n = id_to_name.get(nearest_unk_maha[i], nearest_unk_maha[i])
            nearest_counts[n] = nearest_counts.get(n, 0) + 1
        by_species[sp] = {
            "n": int(mask.sum()), "FAR_at_historical_threshold": far_maha,
            "AUROC_vs_all_known": auroc_sp,
            "mahalanobis_dist_mean": float(d_unk_maha[mask].mean()),
            "mahalanobis_dist_std": float(d_unk_maha[mask].std()),
            "nearest_known_species_counts": nearest_counts,
        }
        print(f"  {sp}: n={mask.sum()}, FAR={far_maha:.4f}, AUROC={auroc_sp}")

    with open(OUT / "unknown_by_species.json", "w", encoding="utf-8") as f:
        json.dump(by_species, f, indent=2, ensure_ascii=False)

    # ══════════════════════════════════════════════════════════════
    # SECCION 6: falsos aceptados (Mahalanobis, threshold historico) — top 20
    # ══════════════════════════════════════════════════════════════
    print("\n=== SECCION 6: falsos aceptados (top 20) ===")
    false_accepts = []
    for i in range(n_unknown):
        if d_unk_maha[i] <= tau_hist:
            false_accepts.append({
                "unknown_species": unknown_species_true[i],
                "image_id": unknown_image_ids[i],
                "nearest_species": id_to_name.get(nearest_unk_maha[i], nearest_unk_maha[i]),
                "mahalanobis_distance": float(d_unk_maha[i]),
                "cosine_score": float(s_unk_cos[i]),
                "euclidean_distance": float(d_unk_eucl[i]),
            })
    false_accepts.sort(key=lambda x: x["mahalanobis_distance"])
    top20 = false_accepts[:20]

    nearest_species_freq = {}
    for fa in false_accepts:
        nearest_species_freq[fa["nearest_species"]] = nearest_species_freq.get(fa["nearest_species"], 0) + 1

    with open(OUT / "unknown_false_accepts.json", "w", encoding="utf-8") as f:
        json.dump({
            "total_false_accepts_mahalanobis_hist_threshold": len(false_accepts),
            "nearest_species_frequency": nearest_species_freq,
            "top20_closest": top20
        }, f, indent=2, ensure_ascii=False)

    print(f"  Total false accepts: {len(false_accepts)}")
    print(f"  Nearest species frequency: {nearest_species_freq}")

    # ══════════════════════════════════════════════════════════════
    # SECCION 7: dispersion por especie KNOWN (24 especies limpias)
    # ══════════════════════════════════════════════════════════════
    print("\n=== SECCION 7: dispersion KNOWN por especie ===")
    known_species_ids = clean["species_ids"]
    known_dispersion = {}
    for sid in set(known_species_ids.tolist()):
        mask = known_species_ids == sid
        n = int(mask.sum())
        d_to_own = d_known_maha[mask]  # nota: esto es distancia al centroide MAS CERCANO, no necesariamente el propio
        name = id_to_name.get(sid, sid)
        known_dispersion[name] = {
            "species_id": sid, "n_images": n,
            "nearest_centroid_dist_mean": float(d_to_own.mean()),
            "nearest_centroid_dist_std": float(d_to_own.std()),
            "nearest_centroid_dist_p95": float(np.percentile(d_to_own, 95)),
            "nearest_centroid_dist_p99": float(np.percentile(d_to_own, 99)) if n > 1 else None,
        }
    with open(OUT / "known_dispersion.json", "w", encoding="utf-8") as f:
        json.dump(known_dispersion, f, indent=2, ensure_ascii=False)
    for name, d in sorted(known_dispersion.items(), key=lambda x: -x[1]["nearest_centroid_dist_std"])[:5]:
        print(f"  {name}: n={d['n_images']}, mean_dist={d['nearest_centroid_dist_mean']:.2f}, std={d['nearest_centroid_dist_std']:.2f}")

    # ══════════════════════════════════════════════════════════════
    # SECCION 8: matriz de distancias entre centroides
    # ══════════════════════════════════════════════════════════════
    print("\n=== SECCION 8: matriz de distancias entre centroides ===")
    ids_list = list(all_centroids.keys())
    C = np.array([all_centroids[i] for i in ids_list])
    dist_matrix_eucl = np.linalg.norm(C[:, None, :] - C[None, :, :], axis=2)
    pairs = []
    for i in range(len(ids_list)):
        for j in range(i + 1, len(ids_list)):
            pairs.append({
                "species_A": id_to_name.get(ids_list[i], ids_list[i]),
                "species_B": id_to_name.get(ids_list[j], ids_list[j]),
                "distance_euclidean": float(dist_matrix_eucl[i, j])
            })
    pairs.sort(key=lambda x: x["distance_euclidean"])
    all_dists = [p["distance_euclidean"] for p in pairs]

    centroid_matrix_report = {
        "n_centroids": len(ids_list),
        "min_centroid_distance": float(min(all_dists)),
        "median_centroid_distance": float(np.median(all_dists)),
        "max_centroid_distance": float(max(all_dists)),
        "top10_closest_pairs": pairs[:10]
    }
    with open(OUT / "centroid_distance_matrix.json", "w", encoding="utf-8") as f:
        json.dump(centroid_matrix_report, f, indent=2, ensure_ascii=False)

    print(f"  min={centroid_matrix_report['min_centroid_distance']:.4f}, "
          f"median={centroid_matrix_report['median_centroid_distance']:.4f}, "
          f"max={centroid_matrix_report['max_centroid_distance']:.4f}")
    print("  Top 5 pares mas cercanos:")
    for p in pairs[:5]:
        print(f"    {p['species_A']} <-> {p['species_B']}: {p['distance_euclidean']:.4f}")

    # ══════════════════════════════════════════════════════════════
    # SECCION 9: diagnostico Mahalanobis (documentacion)
    # ══════════════════════════════════════════════════════════════
    eigvals = np.linalg.eigvalsh(covariance)
    mahalanobis_diagnosis = {
        "embedding_dimension": 512,
        "covariance_parameters": "512x512",
        "effective_parameters": 512 * 512,
        "calibration_species": len(ref_centroids),
        "calibration_images": int(ref["embeddings"].shape[0]),
        "condition_number": float(eigvals.max() / max(eigvals.min(), 1e-12)),
    }
    with open(OUT / "mahalanobis_diagnosis.json", "w", encoding="utf-8") as f:
        json.dump(mahalanobis_diagnosis, f, indent=2)

    # ══════════════════════════════════════════════════════════════
    # SECCION 10: comparacion con Fase 13 (referencia historica, NO mezclada)
    # ══════════════════════════════════════════════════════════════
    with open(ROOT / "evaluation/fase13/final_evaluation/FASE13_FINAL_METRICS.json", encoding="utf-8") as f:
        fase13_metrics = json.load(f)
    with open(ROOT / "evaluation/fase13/statistics/reference_cv_results.json", encoding="utf-8") as f:
        fase13_cv = json.load(f)

    fase13_vs_fase16 = {
        "historical_fase13": {
            "note": "CONTAMINATED KNOWN evaluation (F3 KNOWN es subconjunto exacto de TRAIN, ver Fase 15/16 leakage audit)",
            "AUROC_final_blind": fase13_metrics["auroc_out_of_sample"],
            "method_selected_via_CV_on_REFERENCE": "M5_LedoitWolf_Shared",
            "CV_mean_scores_on_REFERENCE": {
                "M1_Euclidean": fase13_cv.get("M1_Euclidean", {}).get("overall_mean_score"),
                "M2_Cosine": fase13_cv.get("M2_Cosine", {}).get("overall_mean_score"),
                "M5_LedoitWolf": fase13_cv.get("M5_LedoitWolf_Shared", {}).get("overall_mean_score"),
            },
            "cv_selection_caveat": "La CV de Fase 13 comparo METODOS sobre REFERENCE usando estabilidad de "
                                    "scores/condicionamiento, NO AUROC KNOWN-vs-UNKNOWN (no habia UNKNOWN "
                                    "disponible en esa etapa por diseno). No es directamente comparable a AUROC de Fase 17."
        },
        "clean_fase16_fase17": {
            "note": "CLEAN evaluation (blind KNOWN sin leakage, verificado Fase 16)",
            "AUROC_Cosine": auroc_cos,
            "AUROC_Euclidean": auroc_eucl,
            "AUROC_Mahalanobis": auroc_maha,
        },
        "explicit_non_mixing_statement": "Los resultados de Fase 13 (contaminados) y Fase 16/17 (limpios) "
                                          "se reportan por separado y NUNCA se combinan en un promedio ni se "
                                          "usan uno para validar al otro."
    }
    with open(OUT / "fase13_vs_fase16_methods.json", "w", encoding="utf-8") as f:
        json.dump(fase13_vs_fase16, f, indent=2, ensure_ascii=False)

    # ══════════════════════════════════════════════════════════════
    # Conclusion (seccion 11/15)
    # ══════════════════════════════════════════════════════════════
    if auroc_cos > auroc_maha + 0.03 and auroc_eucl > auroc_maha + 0.03:
        scenario = "A"
        conclusion = "MAHALANOBIS_WEAKER_THAN_ALTERNATIVES"
    elif abs(auroc_cos - auroc_maha) < 0.03 and abs(auroc_eucl - auroc_maha) < 0.03:
        scenario = "B"
        conclusion = "METHODS_INCONCLUSIVE"
    else:
        scenario = "C"
        conclusion = "MAHALANOBIS_SUPPORTED"

    final = {
        "cosine_auroc": auroc_cos, "euclidean_auroc": auroc_eucl, "mahalanobis_auroc": auroc_maha,
        "scenario": scenario, "conclusion": conclusion,
    }
    with open(OUT / "fase17_conclusion.json", "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2)

    print(f"\n=== CONCLUSION ===")
    print(json.dumps(final, indent=2))


if __name__ == "__main__":
    main()
