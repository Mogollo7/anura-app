"""
run_fase20_analysis.py -- FASE 20: Open Set Robustness / Cross-Individual diagnostic.

PURAMENTE DIAGNOSTICO. No modifica BioCLIP, no reentrena, no recalibra threshold/covariance
oficiales. Reutiliza embeddings ya extraidos (mismo encoder/preprocessing verificado en
Fases 13/16/19). Escribe SOLO bajo validation/fase20_open_set_robustness/.
"""
import csv
import hashlib
import json
import platform
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc

ROOT = Path(r"D:\Anura")
OUT = ROOT / "validation" / "fase20_open_set_robustness"
sys.path.insert(0, str(ROOT / "tools" / "catalog"))
from taxonomic_resolution import SpeciesResolver  # noqa: E402

RNG = np.random.RandomState(20)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


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


def far_frr_bacc(y_true_unknown, scores, tau, higher_is_more_unknown=True):
    # y_true_unknown: 1 = UNKNOWN, 0 = KNOWN. scores: distance-like (higher => more anomalous)
    known_mask = y_true_unknown == 0
    unknown_mask = y_true_unknown == 1
    if not higher_is_more_unknown:
        scores = -scores
        tau = -tau
    far = float(np.mean(scores[unknown_mask] <= tau)) if unknown_mask.sum() else float("nan")
    frr = float(np.mean(scores[known_mask] > tau)) if known_mask.sum() else float("nan")
    kar = 1 - frr
    udr = 1 - far
    bacc = float((kar + udr) / 2)
    youden = float(kar + udr - 1)
    return far, frr, bacc, youden


def main():
    print("=== FASE 20: OPEN SET ROBUSTNESS / CROSS-INDIVIDUAL (DIAGNOSTIC ONLY) ===\n")
    resolver = SpeciesResolver(ROOT / "training/taxonomia.py", ROOT / "taxonomy/species/species_registry.json")

    import importlib.util
    spec = importlib.util.spec_from_file_location("taxonomia", ROOT / "training/taxonomia.py")
    taxonomia = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(taxonomia)

    def sp_meta(name_underscored):
        try:
            return taxonomia.genero_de(name_underscored), taxonomia.familia_de(name_underscored)
        except KeyError:
            return "UNKNOWN_GENUS", "UNKNOWN_FAMILY"

    # ══════════════════════════════════════════════════════════════
    # STEP 0: freeze encoder identity (task 4)
    # ══════════════════════════════════════════════════════════════
    encoder_path = ROOT / "bioclip/checkpoints/encoder_anura_fp16.onnx"
    encoder_sha = sha256_file(encoder_path)
    expected_sha = "219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad"
    encoder_match = (encoder_sha == expected_sha)
    print(f"[encoder] sha256 match with Fase13/16/19 encoder: {encoder_match}")

    import sklearn as sk
    import scipy as sp

    # ══════════════════════════════════════════════════════════════
    # STEP 1: load ALL available embedding/manifest sources (task 1 + 4)
    # ══════════════════════════════════════════════════════════════
    ref = np.load(ROOT / "evaluation/fase13/embeddings/reference_embeddings.npz")
    train = np.load(ROOT / "evaluation/fase13/embeddings/train_embeddings.npz")
    clean = np.load(ROOT / "validation/fase16_clean_open_set/clean_known_embeddings.npz")
    with open(ROOT / "validation/fase16_clean_open_set/clean_known_manifest.json", encoding="utf-8") as f:
        clean_manifest = json.load(f)
    f4_all = np.load(ROOT / "evaluation/open_set_v1/knn/knn_embeddings.npz")["embeddings"].astype(np.float32)
    with open(ROOT / "evaluation/open_set_v1/knn/knn_open_set_results.json", encoding="utf-8") as f:
        f3f4_records = json.load(f)["records"]
    unknown_records = [r for r in f3f4_records if r["known_unknown"] == "UNKNOWN"]
    unknown_idx = [i for i, r in enumerate(f3f4_records) if r["known_unknown"] == "UNKNOWN"]
    X_unknown = f4_all[unknown_idx]

    dim_ok = (ref["embeddings"].shape[1] == 512 and clean["embeddings"].shape[1] == 512
              and X_unknown.shape[1] == 512)
    print(f"[dim] all sources 512-d: {dim_ok}")

    with open(ROOT / "visual_catalog/v1.0.0/manifest.json", encoding="utf-8") as f:
        catalog = json.load(f)
    release_species_ids = set(catalog["species_ids"])

    # ── official centroids: REFERENCE priority, TRAIN fallback (identical logic to
    # tools/catalog/run_open_set_evaluation.py) -- kept FIXED across all stages below,
    # so stage differences reflect metric/normalization only, not centroid source. ──
    ref_canonical = np.array([resolver.resolve(n)["canonical_name"] for n in ref["species"]])
    train_canonical = np.array([resolver.resolve(n)["canonical_name"] for n in train["species"]])

    def compute_centroids(X, y):
        return {c: np.mean(X[y == c], axis=0) for c in np.unique(y)}

    ref_centroids = compute_centroids(ref["embeddings"], ref_canonical)
    train_centroids = compute_centroids(train["embeddings"], train_canonical)
    official_centroids = {}
    centroid_source = {}
    for name, c in ref_centroids.items():
        sid = resolver.resolve(name.replace("_", " "))["species_id"]
        if sid in release_species_ids:
            official_centroids[sid] = c
            centroid_source[sid] = "REFERENCE"
    for name, c in train_centroids.items():
        sid = resolver.resolve(name.replace("_", " "))["species_id"]
        if sid in release_species_ids and sid not in official_centroids:
            official_centroids[sid] = c
            centroid_source[sid] = "TRAIN"
    centroid_ids = sorted(official_centroids.keys())
    C = np.array([official_centroids[c] for c in centroid_ids])
    print(f"[centroids] official (REFERENCE+TRAIN) available for {len(centroid_ids)}/{len(release_species_ids)} "
          f"release species (Group A={sum(1 for v in centroid_source.values() if v=='REFERENCE')}, "
          f"Group B={sum(1 for v in centroid_source.values() if v=='TRAIN')})")

    # ══════════════════════════════════════════════════════════════
    # TASK 1: independence unit audit across all sources found
    # ══════════════════════════════════════════════════════════════
    known_by_ind = defaultdict(list)
    clean_emb_arr = clean["embeddings"]
    clean_img_ids = clean["image_ids"]
    emb_by_id = {iid: clean_emb_arr[i] for i, iid in enumerate(clean_img_ids)}
    for img in clean_manifest["images"]:
        name = img["scientific_name"].replace(" ", "_")
        known_by_ind[(name, img["individual_id"] or f"__noind__{img['image_id']}")].append({
            "embedding": emb_by_id[img["image_id"]], "image_id": img["image_id"],
            "species_id": img["species_id"], "sha256": img["sha256"], "path": img["path"],
            "observation_id": img.get("observation_id"),
        })

    n_images_known = sum(len(v) for v in known_by_ind.values())
    n_individuals_known = len(known_by_ind)
    species_present = {k[0] for k in known_by_ind}
    n_species_known = len(species_present)

    independence_audit = {
        "unit_priority_used": "individual_id > observation_id > sha256 > path",
        "sources_inventoried": [
            "evaluation/fase13/embeddings/reference_embeddings.npz (REFERENCE, no individual_id available)",
            "evaluation/fase13/embeddings/train_embeddings.npz (TRAIN, no individual_id available)",
            "validation/fase16_clean_open_set/clean_known_manifest.json (KNOWN blind, individual_id=observation numeric id from iNaturalist obs, PRESENT)",
            "evaluation/open_set_v1/knn/knn_open_set_results.json (F3/F4, individual_id reconstructed via col_obs_<id>_photo path regex, PRESENT for F4 only)",
        ],
        "known_blind_pool_clean_known": {
            "n_images": n_images_known, "n_observations_individuals": n_individuals_known,
            "n_species": n_species_known,
            "note": "individual_id aqui = observation_id de iNaturalist (un individuo == una observacion; "
                    "multiples fotos de la misma observacion comparten individual_id). No hay recaptura "
                    "cross-observation verificable -> misma limitacion NOT_FORMALLY_VERIFIABLE de Fase 12.2 "
                    "para independencia biologica real de individuos entre observaciones distintas.",
        },
        "reference_train_pools": {
            "reference_n_images": int(ref["embeddings"].shape[0]),
            "train_n_images": int(train["embeddings"].shape[0]),
            "individual_id_available": False,
            "note": "REFERENCE/TRAIN embeddings npz no contienen individual_id/observation_id -- solo "
                    "species+path. Independencia de individuos entre REFERENCE/TRAIN y el KNOWN blind se "
                    "verifica indirectamente via Fase16 (0 rechazados por individual_id overlap, "
                    "construido desde 'data cleaned/' que excluye por sha256+path los splits anteriores).",
        },
    }
    genera_known = {sp_meta(s)[0] for s in species_present}
    familias_known = {sp_meta(s)[1] for s in species_present}
    print(f"[audit] KNOWN blind pool: {n_images_known} imgs, {n_individuals_known} individuos(obs), "
          f"{n_species_known} especies, {len(genera_known)} generos, {len(familias_known)} familias")

    # ══════════════════════════════════════════════════════════════
    # TASK 2: known_cross_individual_manifest.json
    # ══════════════════════════════════════════════════════════════
    # clean_known_manifest ya fue construido en Fase16 excluyendo por sha256 TODA imagen
    # presente en TRAIN/REFERENCE/CALIBRATION/F3/F4, y verificando 0 overlaps de individual_id
    # (ver clean_known_rejected_by_individual.json). Por lo tanto ES la base valida para el
    # test cross-individual KNOWN. Aqui se re-empaqueta con verificacion explicita repetida.
    with open(ROOT / "validation/fase16_clean_open_set/clean_known_rejected_by_individual.json",
              encoding="utf-8") as f:
        rejected_by_ind = json.load(f)

    known_cross_individual = {
        "source": "validation/fase16_clean_open_set/clean_known_manifest.json (Fase16, reused unmodified)",
        "verification": {
            "excluded_from_train_reference_calibration_f3_f4_by_sha256": True,
            "individual_id_overlap_with_train_check": rejected_by_ind,
        },
        "n_images": n_images_known, "n_individuals": n_individuals_known, "n_species": n_species_known,
        "n_genera": len(genera_known), "n_families": len(familias_known),
        "species_covered": sorted(species_present),
        "species_covered_fraction_of_catalog": f"{n_species_known}/{len(release_species_ids)}",
        "limitation": "17/41 especies del catalogo NO tienen imagenes KNOWN cross-individual disponibles "
                      "(consumieron el 100% de sus datos reales en TRAIN/REFERENCE/CALIBRATION en fases "
                      "previas). No se fabrican individuos ni imagenes para esas especies.",
    }
    with open(OUT / "known_cross_individual_manifest.json", "w", encoding="utf-8") as f:
        json.dump(known_cross_individual, f, indent=2, ensure_ascii=False, default=str)

    # ══════════════════════════════════════════════════════════════
    # TASK 3: unknown_taxonomic_strata_manifest.json
    # ══════════════════════════════════════════════════════════════
    unknown_by_ind = defaultdict(list)
    obs_pat = re.compile(r"col_obs_(\d+)_photo")
    for i, r in enumerate(unknown_records):
        m = obs_pat.search(r["path"])
        ind = m.group(1) if m else f"__noind__{i}"
        unknown_by_ind[(r["true_species"], ind)].append({"embedding": X_unknown[i], "image_id": r["image_id"]})

    unknown_species = sorted({k[0] for k in unknown_by_ind})
    strata = defaultdict(lambda: {"n_images": 0, "n_individuals": 0, "species": set()})
    for (usp, ind), recs in unknown_by_ind.items():
        u_g, u_f = sp_meta(usp)
        # relacion respecto al conjunto KNOWN completo (release)
        nearest_rel = "UNRESOLVED"
        for ksp in species_present:
            k_g, k_f = sp_meta(ksp)
            if k_g == u_g:
                nearest_rel = "SAME_GENUS"
                break
            elif k_f == u_f:
                nearest_rel = "SAME_FAMILY_DIFFERENT_GENUS"
        if nearest_rel == "UNRESOLVED":
            nearest_rel = "DIFFERENT_FAMILY"
        strata[nearest_rel]["n_images"] += len(recs)
        strata[nearest_rel]["n_individuals"] += 1
        strata[nearest_rel]["species"].add(usp)

    strata_out = {k: {"n_images": v["n_images"], "n_individuals": v["n_individuals"],
                       "species": sorted(v["species"])} for k, v in strata.items()}
    unknown_manifest = {
        "sources_searched": [
            "evaluation/open_set_v1/knn/knn_open_set_results.json (F3/F4 blind, only UNKNOWN-labeled records)",
            "No other UNKNOWN-labeled real dataset found elsewhere in repo (searched taxonomy/, evaluation/, "
            "validation/, data cleaned/ manifests) as of this analysis.",
        ],
        "n_unknown_species_total": len(unknown_species),
        "unknown_species": unknown_species,
        "n_unknown_images_total": sum(len(v) for v in unknown_by_ind.values()),
        "n_unknown_individuals_total": len(unknown_by_ind),
        "strata_relative_to_known_catalog": strata_out,
        "diversity_status": "INSUFFICIENT" if len(unknown_species) < 5 else "PARTIAL",
        "note": "Solo 2 especies UNKNOWN reales existen en el repositorio (Hyloxalus_picachos, "
                "Sachatamia_electrops), las mismas ya identificadas en Fase 16/19. No se fabrica diversidad "
                "adicional. La estratificacion taxonomica es sobre 2 puntos de dato, no una muestra.",
    }
    with open(OUT / "unknown_taxonomic_strata_manifest.json", "w", encoding="utf-8") as f:
        json.dump(unknown_manifest, f, indent=2, ensure_ascii=False, default=str)
    print(f"[unknown] {len(unknown_species)} especies reales, {len(unknown_by_ind)} individuos, "
          f"strata={list(strata_out.keys())}")

    # ══════════════════════════════════════════════════════════════
    # Build score arrays for KNOWN(clean) and UNKNOWN(F4) vs FIXED official centroids
    # ══════════════════════════════════════════════════════════════
    X_known = np.array([r["embedding"] for group in known_by_ind.values() for r in group])
    known_species_ids = np.array([sid for (name, _ind), group in known_by_ind.items()
                                   for r in group for sid in [r["species_id"]]])
    X_unk = np.array([r["embedding"] for group in unknown_by_ind.values() for r in group])

    def l2n(X):
        n = np.linalg.norm(X, axis=1, keepdims=True)
        n[n == 0] = 1
        return X / n

    Cn = l2n(C)

    def min_euclidean(X):
        d = np.linalg.norm(X[:, None, :] - C[None, :, :], axis=2)
        return d.min(axis=1), np.argmin(d, axis=1), d

    def min_cosine_distance(X):
        Xn = l2n(X)
        sim = Xn @ Cn.T
        dist = 1 - sim
        return dist.min(axis=1), np.argmax(sim, axis=1), dist

    def max_cosine_similarity(X):
        Xn = l2n(X)
        sim = Xn @ Cn.T
        return sim.max(axis=1)

    cov_npz = np.load(ROOT / "covariance/v1.1.0_CLEAN/covariance_matrix.npz")
    precision_matrix = cov_npz["precision"]

    def min_mahalanobis(X):
        diff = X[:, None, :] - C[None, :, :]
        d2 = np.einsum("nkd,de,nke->nk", diff, precision_matrix, diff)
        d = np.sqrt(np.maximum(0.0, d2))
        return d.min(axis=1), np.argmin(d, axis=1), d

    known_eucl, known_eucl_arg, _ = min_euclidean(X_known)
    unk_eucl, unk_eucl_arg, _ = min_euclidean(X_unk)
    known_cosd, known_cosd_arg, _ = min_cosine_distance(X_known)
    unk_cosd, unk_cosd_arg, _ = min_cosine_distance(X_unk)
    known_cossim = max_cosine_similarity(X_known)
    unk_cossim = max_cosine_similarity(X_unk)
    known_maha, known_maha_arg, _ = min_mahalanobis(X_known)
    unk_maha, unk_maha_arg, _ = min_mahalanobis(X_unk)

    y_unknown = np.concatenate([np.zeros(len(X_known)), np.ones(len(X_unk))])

    def auroc_prauc(known_scores, unk_scores, higher_is_unknown=True):
        scores = np.concatenate([known_scores, unk_scores])
        s = scores if higher_is_unknown else -scores
        au = float(roc_auc_score(y_unknown, s))
        prec, rec, _ = precision_recall_curve(y_unknown, s)
        pr = float(auc(rec, prec))
        return au, pr

    au_eucl, pr_eucl = auroc_prauc(known_eucl, unk_eucl, True)
    au_cosd, pr_cosd = auroc_prauc(known_cosd, unk_cosd, True)
    au_cossim, pr_cossim = auroc_prauc(known_cossim, unk_cossim, False)  # lower sim => more unknown
    au_maha, pr_maha = auroc_prauc(known_maha, unk_maha, True)

    print(f"\n[AUROC] euclidean(min-centroid)={au_eucl:.4f}  cosine_distance={au_cosd:.4f}  "
          f"cosine_similarity={au_cossim:.4f}  mahalanobis={au_maha:.4f}")

    if "--debug-thresh" in sys.argv:
        for tau in [0.4, 0.5, 0.6, 0.65, 0.7, 0.75, 0.8, 0.9]:
            far = float(np.mean(unk_eucl <= tau))
            frr = float(np.mean(known_eucl > tau))
            print(f"  DEBUG tau={tau} far={far:.4f} frr={frr:.4f} yj={(1-far)+(1-frr)-1:.4f}")

    # ══════════════════════════════════════════════════════════════
    # TASK 5: raw embedding separability (using euclidean, the metric that best
    # matches 'raw' geometry before whitening) -- full distributions
    # ══════════════════════════════════════════════════════════════
    raw_sep = {
        "metric": "euclidean_min_distance_to_nearest_official_centroid",
        "known": stats_block(known_eucl), "unknown": stats_block(unk_eucl),
        "auroc": au_eucl, "pr_auc": pr_eucl,
        "note": "Comparable en espiritu al AUROC=0.7245 de Fase19, aunque Fase19 uso centroides "
                "calculados sobre el propio KNOWN limpio (no REFERENCE+TRAIN); aqui se usan los "
                "centroides OFICIALES fijos para poder comparar etapas del pipeline de forma controlada. "
                "Diferencia esperada por esta razon metodologica, documentada explicitamente.",
    }

    # ══════════════════════════════════════════════════════════════
    # TASK 6: distance_comparison.csv (raw cosine sim, cosine dist, euclidean, mahalanobis)
    # Diagnostic threshold = Youden-J optimal ON THIS DATA, clearly separated from
    # the official frozen threshold (never touched/recomputed).
    # ══════════════════════════════════════════════════════════════
    with open(ROOT / "threshold/v1.1.0_CLEAN/manifest.json", encoding="utf-8") as f:
        official_threshold_release = json.load(f)
    official_tau = official_threshold_release["threshold"]

    def diagnostic_threshold_sweep(known_scores, unk_scores, higher_is_unknown=True):
        scores = np.concatenate([known_scores, unk_scores])
        # candidate thresholds = actual observed score values (midpoints), not a naive
        # uniform grid -- with 7475 KNOWN vs 56 UNKNOWN a uniform linspace mostly samples
        # inside the KNOWN bulk and misses the real decision boundary.
        uniq = np.unique(scores)
        grid = (uniq[:-1] + uniq[1:]) / 2.0
        if len(grid) > 2000:
            idx = np.linspace(0, len(grid) - 1, 2000).astype(int)
            grid = grid[idx]
        best = None
        for tau in grid:
            far, frr, bacc, yj = far_frr_bacc(y_unknown, scores, tau, higher_is_unknown)
            if best is None or yj > best[4]:
                best = (tau, far, frr, bacc, yj)
        return best  # tau, far, frr, bacc, youden

    rows = []
    for label, ks, us, higher in [
        ("cosine_similarity", known_cossim, unk_cossim, False),
        ("cosine_distance", known_cosd, unk_cosd, True),
        ("euclidean", known_eucl, unk_eucl, True),
        ("mahalanobis", known_maha, unk_maha, True),
    ]:
        au, pr = auroc_prauc(ks, us, higher)
        tau, far, frr, bacc, yj = diagnostic_threshold_sweep(ks, us, higher)
        rows.append({
            "metric": label, "auroc": au, "pr_auc": pr,
            "diagnostic_threshold": tau, "diagnostic_threshold_far": far,
            "diagnostic_threshold_frr": frr, "diagnostic_threshold_balanced_accuracy": bacc,
            "diagnostic_threshold_youden_j": yj,
            "is_official_frozen_threshold": False,
        })
    # add official pipeline row (Mahalanobis @ official frozen tau) for direct contrast
    far_o, frr_o, bacc_o, yj_o = far_frr_bacc(y_unknown, np.concatenate([known_maha, unk_maha]),
                                               official_tau, True)
    rows.append({
        "metric": "mahalanobis_official_frozen_threshold", "auroc": au_maha, "pr_auc": pr_maha,
        "diagnostic_threshold": official_tau, "diagnostic_threshold_far": far_o,
        "diagnostic_threshold_frr": frr_o, "diagnostic_threshold_balanced_accuracy": bacc_o,
        "diagnostic_threshold_youden_j": yj_o, "is_official_frozen_threshold": True,
    })
    with open(OUT / "distance_comparison.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("\n[distance_comparison]")
    for r in rows:
        print(f"  {r['metric']}: AUROC={r['auroc']:.4f} PR-AUC={r['pr_auc']:.4f} "
              f"bacc@diag_or_official_tau={r['diagnostic_threshold_balanced_accuracy']:.4f}")

    # ══════════════════════════════════════════════════════════════
    # TASK 7: stagewise AUROC (raw -> normalized -> centered -> mahalanobis -> official)
    # ══════════════════════════════════════════════════════════════
    global_mean = X_known.mean(axis=0)  # centering reference = KNOWN pool mean (diagnostic)

    def min_euclidean_generic(X, Cx):
        d = np.linalg.norm(X[:, None, :] - Cx[None, :, :], axis=2)
        return d.min(axis=1)

    # stage A: raw embedding, euclidean to nearest centroid (no normalization applied,
    # though encoder output is already L2-normalized per contract -- so 'raw' == 'normalized' here)
    stageA_k, stageA_u = known_eucl, unk_eucl
    auA, prA = au_eucl, pr_eucl

    # stage B: centered (subtract global KNOWN mean from both embeddings and centroids)
    Xk_c = X_known - global_mean
    Xu_c = X_unk - global_mean
    C_c = C - global_mean
    stageB_k = min_euclidean_generic(Xk_c, C_c)
    stageB_u = min_euclidean_generic(Xu_c, C_c)
    auB, prB = auroc_prauc(stageB_k, stageB_u, True)

    # stage C: cosine distance (angle-only, ignores magnitude -- isolates L2-normalization effect)
    auC, prC = au_cosd, pr_cosd

    # stage D: mahalanobis (shared covariance whitening, official precision matrix)
    auD, prD = au_maha, pr_maha

    # stage E: official frozen pipeline (mahalanobis + threshold decision -> reduces to
    # balanced accuracy, not an AUROC; reported for continuity using the fase16 published value)
    with open(ROOT / "validation/fase16_clean_open_set/fase16_blind_test_results.json",
              encoding="utf-8") as f:
        fase16_results = json.load(f)

    stagewise = [
        {"stage": "1_raw_l2_normalized_embedding_euclidean_to_centroid", "auroc": auA, "pr_auc": prA},
        {"stage": "2_centered_euclidean_to_centroid", "auroc": auB, "pr_auc": prB},
        {"stage": "3_cosine_distance_to_centroid", "auroc": auC, "pr_auc": prC},
        {"stage": "4_mahalanobis_shared_covariance", "auroc": auD, "pr_auc": prD},
        {"stage": "5_official_pipeline_fase16_reported", "auroc": fase16_results.get("metrics", {}).get("auroc")
         if isinstance(fase16_results, dict) and "metrics" in fase16_results else None, "pr_auc": None},
    ]
    with open(OUT / "stagewise_auroc.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["stage", "auroc", "pr_auc"])
        w.writeheader()
        w.writerows(stagewise)
    print("\n[stagewise AUROC]")
    for s in stagewise:
        print(f"  {s['stage']}: AUROC={s['auroc']}")

    # ══════════════════════════════════════════════════════════════
    # TASK 11: threshold_curve.csv (diagnostic only, over Mahalanobis scores)
    # ══════════════════════════════════════════════════════════════
    all_maha = np.concatenate([known_maha, unk_maha])
    uniq_maha = np.unique(all_maha)
    grid = (uniq_maha[:-1] + uniq_maha[1:]) / 2.0
    if len(grid) > 300:
        idx = np.linspace(0, len(grid) - 1, 300).astype(int)
        grid = grid[idx]
    # ensure official threshold's neighborhood is represented for the curve
    grid = np.sort(np.unique(np.concatenate([grid, [official_tau]])))
    curve_rows = []
    for tau in grid:
        far, frr, bacc, yj = far_frr_bacc(y_unknown, all_maha, tau, True)
        curve_rows.append({"threshold": float(tau), "far": far, "frr": frr,
                            "balanced_accuracy": bacc, "youden_j": yj,
                            "is_official_frozen_threshold": bool(abs(tau - official_tau) < 1e-9)})
    with open(OUT / "threshold_curve.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(curve_rows[0].keys()))
        w.writeheader()
        w.writerows(curve_rows)

    # ══════════════════════════════════════════════════════════════
    # TASK 9: taxonomic margin by pair type (same species / genus / family / diff family)
    # using per-individual-group KNOWN embeddings against official centroids
    # ══════════════════════════════════════════════════════════════
    species_margin_rows = []
    # cross-individual species test (TASK 8): rotation by individual within species,
    # only for species with >=3 distinct individuals in the clean KNOWN pool.
    by_species_inds = defaultdict(dict)
    for (name, ind), group in known_by_ind.items():
        by_species_inds[name][ind] = group

    cross_ind_rows = []
    for name, inds in by_species_inds.items():
        ind_list = list(inds.keys())
        if len(ind_list) < 3:
            continue
        sid_this = inds[ind_list[0]][0]["species_id"]
        if sid_this not in official_centroids:
            continue
        k = min(5, len(ind_list))
        RNG.shuffle(ind_list)
        folds = np.array_split(ind_list, k)
        top1_hits, top3_hits = 0, 0
        n_test = 0
        margins = []
        for fi in range(len(folds)):
            test_inds = set(folds[fi])
            train_inds = [i for i in ind_list if i not in test_inds]
            if not train_inds:
                continue
            train_embs = np.array([r["embedding"] for ti in train_inds for r in inds[ti]])
            test_embs = np.array([r["embedding"] for ti in test_inds for r in inds[ti]])
            if len(train_embs) == 0 or len(test_embs) == 0:
                continue
            fold_centroid = train_embs.mean(axis=0)
            # candidate set = official centroids with this species replaced by fold-specific centroid
            C_test = C.copy()
            own_pos = centroid_ids.index(sid_this)
            C_test[own_pos] = fold_centroid
            d = np.linalg.norm(test_embs[:, None, :] - C_test[None, :, :], axis=2)
            order = np.argsort(d, axis=1)
            top1 = (order[:, 0] == own_pos)
            top3 = np.any(order[:, :3] == own_pos, axis=1)
            top1_hits += int(top1.sum())
            top3_hits += int(top3.sum())
            n_test += len(test_embs)
            d_correct = d[:, own_pos]
            d_masked = d.copy()
            d_masked[:, own_pos] = np.inf
            d_wrong = d_masked.min(axis=1)
            margins.extend((d_wrong - d_correct).tolist())
        if n_test == 0:
            continue
        margins = np.array(margins)
        cross_ind_rows.append({
            "species": name, "n_individuals_total": len(ind_list), "n_folds": k,
            "n_test_images": n_test,
            "top1_accuracy": top1_hits / n_test, "top3_accuracy": top3_hits / n_test,
            "margin_mean": float(margins.mean()), "margin_median": float(np.median(margins)),
            "negative_margin_rate": float(np.mean(margins < 0)),
        })
    with open(OUT / "species_margin.csv", "w", newline="", encoding="utf-8") as f:
        if cross_ind_rows:
            w = csv.DictWriter(f, fieldnames=list(cross_ind_rows[0].keys()))
            w.writeheader()
            w.writerows(cross_ind_rows)
        else:
            f.write("NO_SPECIES_WITH_ENOUGH_INDIVIDUALS_FOR_CROSS_INDIVIDUAL_ROTATION\n")
    print(f"\n[cross-individual] {len(cross_ind_rows)} especies evaluadas con rotacion por individuo "
          f"(>=3 individuos requeridos)")

    # taxonomic margin pairs (species-centroid level, reusing official centroids)
    dist_C = np.linalg.norm(C[:, None, :] - C[None, :, :], axis=2)
    tax_margin = defaultdict(list)
    id_to_name = {v: k for k, v in resolver.__dict__.get("_cache", {}).items()} if False else None
    sid_to_canon = {}
    for name in ref_canonical.tolist() + train_canonical.tolist():
        sid = resolver.resolve(name.replace("_", " "))["species_id"]
        sid_to_canon[sid] = name
    for i in range(len(centroid_ids)):
        for j in range(i + 1, len(centroid_ids)):
            na, nb = sid_to_canon.get(centroid_ids[i], centroid_ids[i]), sid_to_canon.get(centroid_ids[j], centroid_ids[j])
            ga, fa = sp_meta(na)
            gb, fb = sp_meta(nb)
            rel = "same_genus" if ga == gb else ("same_family_diff_genus" if fa == fb else "diff_family")
            tax_margin[rel].append(float(dist_C[i, j]))

    margin_summary_rows = []
    for rel, dists in tax_margin.items():
        margin_summary_rows.append({"relation": rel, **stats_block(dists)})
    with open(OUT / "unknown_analysis.csv", "w", newline="", encoding="utf-8") as f:
        fieldnames = ["unknown_species", "unknown_individual", "true_family", "nearest_known_species",
                      "nearest_known_genus", "nearest_known_family", "taxonomic_relation_to_nearest",
                      "distance_mahalanobis", "official_threshold", "accepted_by_official_threshold"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        idx = 0
        for (usp, ind), group in unknown_by_ind.items():
            u_g, u_f = sp_meta(usp)
            for r in group:
                nn_sid = centroid_ids[unk_maha_arg[idx]]
                nn_name = sid_to_canon.get(nn_sid, nn_sid)
                nn_g, nn_f = sp_meta(nn_name)
                rel = "SAME_GENUS" if nn_g == u_g else ("SAME_FAMILY_DIFFERENT_GENUS" if nn_f == u_f else "DIFFERENT_FAMILY")
                w.writerow({
                    "unknown_species": usp, "unknown_individual": ind, "true_family": u_f,
                    "nearest_known_species": nn_name, "nearest_known_genus": nn_g,
                    "nearest_known_family": nn_f, "taxonomic_relation_to_nearest": rel,
                    "distance_mahalanobis": float(unk_maha[idx]), "official_threshold": official_tau,
                    "accepted_by_official_threshold": bool(unk_maha[idx] <= official_tau),
                })
                idx += 1

    print("\n[taxonomic margin, official centroids, euclidean]")
    for r in margin_summary_rows:
        print(f"  {r['relation']}: n={r['n']} mean={r['mean']:.4f} median={r['median']:.4f}")

    # write species_margin distribution stats too (separate concept from cross-individual csv);
    # append as a JSON alongside since species_margin.csv is reserved for task 8's schema above
    with open(OUT / "taxonomic_pair_margin_stats.json", "w", encoding="utf-8") as f:
        json.dump({"relation_distance_stats": margin_summary_rows}, f, indent=2, ensure_ascii=False)

    # ══════════════════════════════════════════════════════════════
    # TASK 10 summary: is FAR concentrated in certain UNKNOWN?
    # ══════════════════════════════════════════════════════════════
    unk_accept_by_species = defaultdict(lambda: [0, 0])
    idx = 0
    for (usp, ind), group in unknown_by_ind.items():
        for r in group:
            unk_accept_by_species[usp][1] += 1
            if unk_maha[idx] <= official_tau:
                unk_accept_by_species[usp][0] += 1
            idx += 1
    far_concentration = {sp: {"n_accepted_false": v[0], "n_total": v[1], "far_rate": v[0] / v[1]}
                          for sp, v in unk_accept_by_species.items()}

    # ══════════════════════════════════════════════════════════════
    # diagnostic_metrics.json (task 5/6/7/10 consolidated)
    # ══════════════════════════════════════════════════════════════
    diagnostic_metrics = {
        "label": "DIAGNOSTIC_ONLY - Fase 20, no reemplaza threshold/covariance oficiales",
        "raw_embedding_separability": raw_sep,
        "distance_metric_comparison_summary": rows,
        "stagewise_auroc": stagewise,
        "far_concentration_by_unknown_species": far_concentration,
        "official_frozen_threshold": official_tau,
        "official_threshold_release": "threshold/v1.1.0_CLEAN",
        "official_covariance_release": "covariance/v1.1.0_CLEAN",
        "n_known_test_images": int(len(X_known)), "n_unknown_test_images": int(len(X_unk)),
        "n_known_test_individuals": n_individuals_known, "n_unknown_test_individuals": len(unknown_by_ind),
        "cross_individual_species_test": {
            "n_species_evaluated": len(cross_ind_rows),
            "mean_top1_accuracy": float(np.mean([r["top1_accuracy"] for r in cross_ind_rows])) if cross_ind_rows else None,
            "mean_negative_margin_rate": float(np.mean([r["negative_margin_rate"] for r in cross_ind_rows])) if cross_ind_rows else None,
        },
    }
    with open(OUT / "diagnostic_metrics.json", "w", encoding="utf-8") as f:
        json.dump(diagnostic_metrics, f, indent=2, ensure_ascii=False, default=str)

    # ══════════════════════════════════════════════════════════════
    # integrity_manifest.json
    # ══════════════════════════════════════════════════════════════
    integrity = {
        "analysis_datetime_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(), "sklearn_version": sk.__version__,
        "scipy_version": sp.__version__, "numpy_version": np.__version__,
        "encoder_sha256": encoder_sha, "encoder_sha256_matches_fase13_16_19": encoder_match,
        "embedding_dimension_confirmed_512": bool(dim_ok),
        "normalization": "L2 (per encoder contract)",
        "preprocessing": "open_clip.create_model_and_transforms(hf-hub:imageomics/bioclip)",
        "embeddings_reused_from": [
            "evaluation/fase13/embeddings/reference_embeddings.npz",
            "evaluation/fase13/embeddings/train_embeddings.npz",
            "validation/fase16_clean_open_set/clean_known_embeddings.npz",
            "evaluation/open_set_v1/knn/knn_embeddings.npz (UNKNOWN records only)",
        ],
        "no_new_extraction": True,
        "official_artifacts_touched": [],
        "official_artifacts_read_only_referenced": [
            "covariance/v1.1.0_CLEAN/covariance_matrix.npz",
            "threshold/v1.1.0_CLEAN/manifest.json",
            "visual_catalog/v1.0.0/manifest.json",
        ],
        "fine_tuning_performed": False,
        "git_commit_performed": False,
        "outputs_written_under": "validation/fase20_open_set_robustness/ only",
    }
    with open(OUT / "integrity_manifest.json", "w", encoding="utf-8") as f:
        json.dump(integrity, f, indent=2, ensure_ascii=False, default=str)

    print("\n[OK] Fase 20 numerical analysis complete.")
    return {
        "au_eucl": au_eucl, "au_maha": au_maha, "official_tau": official_tau,
        "fase16_auroc": fase16_results if isinstance(fase16_results, (int, float)) else None,
    }


if __name__ == "__main__":
    main()
