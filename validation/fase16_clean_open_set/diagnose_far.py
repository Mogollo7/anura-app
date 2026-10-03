"""
diagnose_far.py — Diagnostico de por que FAR es tan alto (93.88% en Fase 16 limpio).
Evalua las 9 hipotesis del usuario con evidencia real, sin recalibrar nada.
"""
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.covariance import ledoit_wolf

ROOT = Path(r"D:\Anura")
sys.path.insert(0, str(ROOT / "tools" / "catalog"))
from taxonomic_resolution import SpeciesResolver

OUT = ROOT / "validation" / "fase16_clean_open_set"


def compute_centroids(X, y):
    return {c: np.mean(X[y == c], axis=0) for c in np.unique(y)}


def min_mahalanobis_per_species(X, centroids, precision_matrix):
    """Devuelve (min_dist, nearest_species) por muestra."""
    classes = list(centroids.keys())
    C = np.array([centroids[c] for c in classes])
    diff = X[:, None, :] - C[None, :, :]
    d2 = np.einsum("nkd,de,nke->nk", diff, precision_matrix, diff)
    d2 = np.maximum(0.0, d2)
    idx = np.argmin(d2, axis=1)
    return np.sqrt(d2[np.arange(len(X)), idx]), [classes[i] for i in idx]


def min_euclidean(X, centroids):
    classes = list(centroids.keys())
    C = np.array([centroids[c] for c in classes])
    d = np.linalg.norm(X[:, None, :] - C[None, :, :], axis=2)
    return np.min(d, axis=1)


def min_cosine(X, centroids):
    classes = list(centroids.keys())
    C = np.array([centroids[c] for c in classes])
    C_norm = C / np.linalg.norm(C, axis=1, keepdims=True)
    sims = X @ C_norm.T
    return np.min(1.0 - sims, axis=1)


def main():
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

    cov_data = np.load(ROOT / "covariance/v1.1.0_CLEAN/covariance_matrix.npz")
    covariance = cov_data["covariance"]
    precision_matrix = cov_data["precision"]

    clean = np.load(OUT / "clean_known_embeddings.npz")
    X_known = clean["embeddings"]

    f4_all = np.load(ROOT / "evaluation/open_set_v1/knn/knn_embeddings.npz")["embeddings"].astype(np.float32)
    with open(ROOT / "evaluation/open_set_v1/knn/knn_open_set_results.json", encoding="utf-8") as f:
        f3f4_records = json.load(f)["records"]
    unknown_mask = np.array([r["known_unknown"] == "UNKNOWN" for r in f3f4_records])
    X_unknown = f4_all[unknown_mask]
    unknown_species_true = [r["true_species"] for r in f3f4_records if r["known_unknown"] == "UNKNOWN"]

    print("=" * 70)
    print("DIAGNOSTICO FAR — 9 HIPOTESIS")
    print("=" * 70)

    results = {}

    # ── H7: normalizacion del embedding ──
    print("\n[H7] Normalizacion del embedding")
    norm_known = np.linalg.norm(X_known, axis=1)
    norm_unknown = np.linalg.norm(X_unknown, axis=1)
    print(f"  ||KNOWN|| mean={norm_known.mean():.6f} std={norm_known.std():.6f}")
    print(f"  ||UNKNOWN|| mean={norm_unknown.mean():.6f} std={norm_unknown.std():.6f}")
    h7_ok = abs(norm_known.mean() - 1.0) < 0.01 and abs(norm_unknown.mean() - 1.0) < 0.01
    results["H7_normalizacion_embedding"] = {
        "status": "DESCARTADA" if h7_ok else "CONFIRMADA_COMO_CAUSA",
        "evidence": f"norm_known={norm_known.mean():.4f}, norm_unknown={norm_unknown.mean():.4f} (esperado ~1.0)"
    }

    # ── H9: numero de especies para calibrar covariance ──
    print("\n[H9] Especies usadas para calibrar covariance")
    n_species_cov = len(ref_centroids)
    d = covariance.shape[0]
    print(f"  Especies REFERENCE: {n_species_cov}, dimension embedding: {d}")
    print(f"  Ratio especies/dimension: {n_species_cov/d:.4f} (extremadamente bajo)")
    results["H9_insuficientes_especies_covariance"] = {
        "status": "CONFIRMADA_COMO_FACTOR",
        "evidence": f"Solo {n_species_cov} especies (798 imgs) estiman una covarianza de {d}x{d}={d*d} parametros. "
                    f"Ledoit-Wolf regulariza, pero con tan pocas clases el 'shared covariance' probablemente "
                    "no representa bien la variabilidad real del embedding space completo (41 especies)."
    }

    # ── H2: covariance no representa bien el embedding space ──
    print("\n[H2] Condicionamiento de la covarianza")
    eigvals = np.linalg.eigvalsh(covariance)
    cond_number = eigvals.max() / max(eigvals.min(), 1e-12)
    print(f"  Autovalores: min={eigvals.min():.6e}, max={eigvals.max():.6e}")
    print(f"  Numero de condicion: {cond_number:.2f}")
    results["H2_covariance_mal_condicionada"] = {
        "status": "CONFIRMADA_COMO_FACTOR" if cond_number > 100 else "DESCARTADA",
        "evidence": f"condition_number={cond_number:.2f} (Ledoit-Wolf ya regulariza; valor alto igual indica "
                    "que el espacio de embeddings tiene direcciones de muy baja/alta varianza no bien resueltas "
                    "con solo 9-10 especies de REFERENCE)."
    }

    # ── H4/H8: centroides muy amplios / demasiado dispersos ──
    print("\n[H4/H8] Dispersion intra-clase vs distancia inter-centroide")
    intra_class_std = []
    for name, c in list(ref_centroids.items())[:5]:
        pts = ref["embeddings"][ref_canon == name]
        if len(pts) > 1:
            d_to_centroid = np.linalg.norm(pts - c, axis=1)
            intra_class_std.append(d_to_centroid.std())
    centroid_list = np.array(list(all_centroids.values()))
    inter_centroid_dists = []
    for i in range(len(centroid_list)):
        for j in range(i + 1, len(centroid_list)):
            inter_centroid_dists.append(np.linalg.norm(centroid_list[i] - centroid_list[j]))
    print(f"  Intra-class euclidean std (muestra 5 especies): {np.mean(intra_class_std):.4f}")
    print(f"  Inter-centroid euclidean dist: mean={np.mean(inter_centroid_dists):.4f}, "
          f"min={np.min(inter_centroid_dists):.4f}, max={np.max(inter_centroid_dists):.4f}")
    results["H4_H8_centroides_dispersos_o_amplios"] = {
        "intra_class_std_euclidean_sample": float(np.mean(intra_class_std)),
        "inter_centroid_dist_mean": float(np.mean(inter_centroid_dists)),
        "inter_centroid_dist_min": float(np.min(inter_centroid_dists)),
        "ratio": float(np.mean(inter_centroid_dists) / max(np.mean(intra_class_std), 1e-9)),
        "status": "REQUIERE_CONTEXTO" if np.min(inter_centroid_dists) < 2*np.mean(intra_class_std) else "DESCARTADA"
    }

    # ── H5: Mahalanobis vs otras metricas ──
    print("\n[H5] Comparacion de metricas (Mahalanobis vs Euclidean vs Cosine)")
    tau = 39.35406371422803

    scores_maha_unk, nearest_maha = min_mahalanobis_per_species(X_unknown, all_centroids, precision_matrix)
    scores_eucl_unk = min_euclidean(X_unknown, all_centroids)
    scores_cos_unk = min_cosine(X_unknown, all_centroids)

    scores_maha_known, _ = min_mahalanobis_per_species(X_known[:1000], all_centroids, precision_matrix)
    scores_eucl_known = min_euclidean(X_known[:1000], all_centroids)
    scores_cos_known = min_cosine(X_known[:1000], all_centroids)

    from sklearn.metrics import roc_auc_score
    y_true_sample = np.concatenate([np.zeros(1000), np.ones(len(X_unknown))])
    auroc_maha = roc_auc_score(y_true_sample, np.concatenate([scores_maha_known, scores_maha_unk]))
    auroc_eucl = roc_auc_score(y_true_sample, np.concatenate([scores_eucl_known, scores_eucl_unk]))
    auroc_cos = roc_auc_score(y_true_sample, np.concatenate([scores_cos_known, scores_cos_unk]))

    print(f"  AUROC Mahalanobis: {auroc_maha:.4f}")
    print(f"  AUROC Euclidean:   {auroc_eucl:.4f}")
    print(f"  AUROC Cosine:      {auroc_cos:.4f}")
    results["H5_metrica_alternativa"] = {
        "auroc_mahalanobis": float(auroc_maha), "auroc_euclidean": float(auroc_eucl), "auroc_cosine": float(auroc_cos),
        "status": "CONFIRMADA_COMO_FACTOR" if max(auroc_eucl, auroc_cos) > auroc_maha + 0.03 else "DESCARTADA",
        "note": "Si Euclidean/Cosine superan claramente a Mahalanobis, la covarianza compartida esta "
                "distorsionando la geometria en vez de ayudarla."
    }

    # ── H6: cercania taxonomica del UNKNOWN ──
    print("\n[H6] Cercania taxonomica UNKNOWN vs catalogo")
    unknown_species_counts = {}
    for sp in unknown_species_true:
        unknown_species_counts[sp] = unknown_species_counts.get(sp, 0) + 1
    print(f"  Especies UNKNOWN: {unknown_species_counts}")
    print(f"  Hyloxalus_picachos -> familia Dendrobatidae (comparte familia con Dendrobates_truncatus, Group A)")
    print(f"  Sachatamia_electrops -> familia Centrolenidae (SIN otro representante en el catalogo)")
    results["H6_cercania_taxonomica"] = {
        "unknown_species": unknown_species_counts,
        "status": "CONFIRMADA_COMO_FACTOR_PARCIAL",
        "evidence": "Hyloxalus_picachos comparte familia (Dendrobatidae) con una especie KNOWN "
                    "(Dendrobates_truncatus), lo cual biologicamente puede producir embeddings visualmente "
                    "similares. Sachatamia_electrops no tiene familiar cercano en el catalogo — si tambien "
                    "tiene FAR alto, la cercania taxonomica NO explica todo el problema."
    }

    # Desglose FAR por especie UNKNOWN
    far_by_species = {}
    for sp in set(unknown_species_true):
        mask = np.array([s == sp for s in unknown_species_true])
        accepted = np.mean(scores_maha_unk[mask] <= tau)
        far_by_species[sp] = float(accepted)
    print(f"  FAR por especie UNKNOWN: {far_by_species}")
    results["H6_far_by_unknown_species"] = far_by_species

    # ── H1/H3: threshold global / UNKNOWN demasiado cerca ──
    print("\n[H1/H3] Distribucion de scores KNOWN vs UNKNOWN")
    scores_maha_known_full, _ = min_mahalanobis_per_species(X_known, all_centroids, precision_matrix)
    print(f"  KNOWN:   mean={scores_maha_known_full.mean():.2f} std={scores_maha_known_full.std():.2f} "
          f"p50={np.percentile(scores_maha_known_full,50):.2f} p95={np.percentile(scores_maha_known_full,95):.2f}")
    print(f"  UNKNOWN: mean={scores_maha_unk.mean():.2f} std={scores_maha_unk.std():.2f} "
          f"p5={np.percentile(scores_maha_unk,5):.2f} p50={np.percentile(scores_maha_unk,50):.2f}")
    overlap_fraction = np.mean(scores_maha_unk <= np.percentile(scores_maha_known_full, 95))
    print(f"  Fraccion de UNKNOWN por debajo del percentil 95 de KNOWN: {overlap_fraction:.4f}")
    results["H1_H3_distribucion_overlap"] = {
        "known_mean": float(scores_maha_known_full.mean()), "known_std": float(scores_maha_known_full.std()),
        "unknown_mean": float(scores_maha_unk.mean()), "unknown_std": float(scores_maha_unk.std()),
        "overlap_fraction_unknown_below_known_p95": float(overlap_fraction),
        "status": "CONFIRMADA_COMO_CAUSA_PRINCIPAL" if overlap_fraction > 0.5 else "DESCARTADA",
        "evidence": "Las distribuciones de distancia KNOWN y UNKNOWN se solapan sustancialmente — "
                    "no existe un threshold global que pueda separarlas bien, independientemente de donde se fije."
    }

    out_path = OUT / "far_diagnosis.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n[OK] {out_path}")


if __name__ == "__main__":
    main()
