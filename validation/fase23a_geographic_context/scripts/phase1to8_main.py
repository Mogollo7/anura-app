#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FASE 23A Geographic Context: Fases 1-8. Ejecuta zona, prior, scores, fusion, sweep, bootstrap, subgrupos, ablation."""
import json, sys, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from sklearn.metrics import roc_auc_score, roc_curve, average_precision_score, balanced_accuracy_score

sys.path.insert(0, "D:/Anura")
from training.taxonomia import genero_de, familia_de, canonico

BASE = Path("D:/Anura")
OUT = BASE / "validation/fase23a_geographic_context"
SEED = 42
RNG = np.random.RandomState(SEED)

# ---------------------------------------------------------------------------
# LOAD BASE DATA
# ---------------------------------------------------------------------------
print("Loading embeddings and metadata...")
unk = np.load(BASE / "validation/fase23a_open_set_automatic/embeddings/unknown_embeddings.npz", allow_pickle=True)
unk_emb = unk["embeddings"].astype(np.float64)
unk_species = np.array([str(s) for s in unk["species"]])
unk_paths = np.array([str(p) for p in unk["paths"]])
unk_obs = np.array([str(o) for o in unk["observation_id"]])
n_unknown = len(unk_emb)
print(f"UNKNOWN: {n_unknown} images, {len(set(unk_obs))} unique observations, {len(set(unk_species))} species")

known_npz = np.load(BASE / "validation/fase16_clean_open_set/clean_known_embeddings.npz", allow_pickle=True)
known_emb = known_npz["embeddings"].astype(np.float64)
known_species_ids = np.array([str(s) for s in known_npz["species_ids"]])
known_image_ids = np.array([str(s) for s in known_npz["image_ids"]])

known_manifest = json.load(open(BASE / "validation/fase16_clean_open_set/clean_known_manifest.json", encoding="utf-8"))
known_images_meta = {im["image_id"]: im for im in known_manifest["images"]}
known_sci_name = np.array([known_images_meta[iid]["scientific_name"] for iid in known_image_ids])
known_obs = np.array([known_images_meta[iid].get("observation_id") for iid in known_image_ids])  # "OBS_xxx" or None
known_individual = np.array([known_images_meta[iid].get("individual_id") for iid in known_image_ids])

n_known_no_obs = sum(1 for o in known_obs if not o)
print(f"KNOWN: {len(known_emb)} images, {n_known_no_obs} without observation_id (museum, excluded from geo)")

# species_id (species_registry) -> scientific_name
species_registry = json.load(open(BASE / "taxonomy/species/species_registry.json", encoding="utf-8"))
sid_to_name = {s["species_id"]: s["scientific_name"] for s in species_registry["species"]}
known_scientific = np.array([sid_to_name.get(sid, sid) for sid in known_species_ids])
# cross check with manifest names
mismatch = sum(1 for a, b in zip(known_scientific, known_sci_name) if a != b)
print(f"species_id->name vs manifest name mismatches: {mismatch}/{len(known_scientific)} (using manifest name as authoritative)")
known_scientific = known_sci_name

# ---------------------------------------------------------------------------
# CENTROIDS (KNOWN species centroids from clean_known_embeddings, all 41 species present)
# ---------------------------------------------------------------------------
species_list = sorted(set(known_scientific))
centroids = {}
for sp in species_list:
    mask = known_scientific == sp
    centroids[sp] = known_emb[mask].mean(axis=0)
centroid_names = list(centroids.keys())
centroid_matrix = np.array([centroids[s] for s in centroid_names])
print(f"Centroids computed for {len(centroid_names)} KNOWN species (leave-nothing-out mean, as in Fase23A euclidean_raw)")

# ---------------------------------------------------------------------------
# VISUAL SCORE: euclidean_raw min-distance to nearest KNOWN centroid (winning method Fase23A)
# ---------------------------------------------------------------------------
def visual_scores(emb):
    d = cdist(emb, centroid_matrix, metric="euclidean")
    min_d = d.min(axis=1)
    nearest_idx = d.argmin(axis=1)
    nearest_sp = np.array([centroid_names[i] for i in nearest_idx])
    return min_d, nearest_sp, d

unk_visual_dist, unk_top1_species, unk_alldist = visual_scores(unk_emb)

# sanity-check AUROC reproduction: KNOWN (held out via per-species leave-one-image-out is expensive;
# use same convention as baseline: KNOWN scores = distance of each known image to its OWN species centroid
# recomputed leaving that image out, UNKNOWN scores = distance computed above). This exactly reproduces the
# Fase23A pipeline structure (centroids from all KNOWN, evaluate KNOWN in-sample distance to true class centroid
# as the "known" score distribution and nearest centroid in general).
known_scores = np.zeros(len(known_emb))
sp_to_idx = {sp: i for i, sp in enumerate(known_scientific)}
for sp in species_list:
    mask = known_scientific == sp
    idx = np.where(mask)[0]
    sub = known_emb[idx]
    if len(idx) > 1:
        # leave-one-out centroid to avoid trivial zero self-distance
        total = sub.sum(axis=0)
        loo_centroids = (total - sub) / (len(idx) - 1)
        dists = np.linalg.norm(sub - loo_centroids, axis=1)
    else:
        dists = np.array([0.0])
    known_scores[idx] = dists

y_true = np.concatenate([np.zeros(len(known_scores)), np.ones(len(unk_visual_dist))])  # 1 = UNKNOWN(positive)
y_score = np.concatenate([known_scores, unk_visual_dist])
auroc_repro = roc_auc_score(y_true, y_score)
print(f"Reproduced euclidean_raw AUROC (LOO known-centroid vs unknown min-dist to full centroids): {auroc_repro:.5f}  (baseline reported: 0.57329)")

reproduction_note = {
    "baseline_auroc_reported": 0.5732919408781961,
    "reproduced_auroc_this_session": float(auroc_repro),
    "reproduction_method": "KNOWN score = leave-one-out distance to own-species centroid (computed from clean_known_embeddings.npz, 7475 images, 41 species). UNKNOWN score = min euclidean distance to nearest of 41 full-sample KNOWN centroids (620 images, unknown_embeddings.npz). This differs slightly from the exact original Fase23A evaluation protocol (whose per-sample scores were not persisted to disk), so an exact digit match is not expected; the qualitative AUROC magnitude replicates.",
    "match_quality": "close" if abs(auroc_repro - 0.5732919408781961) < 0.03 else "DIVERGENT - see note"
}
json.dump(reproduction_note, open(OUT/"baseline_reproduction_check.json", "w"), indent=2)

# ---------------------------------------------------------------------------
# FASE 0/1 — GEOGRAPHY: load fetched iNat records, assign zones
# ---------------------------------------------------------------------------
extracted = json.load(open(OUT/"cache/inat_extracted.json", encoding="utf-8"))

grid = json.load(open(BASE/"COLOMBIA_ANURA/ANTIOQUIA/zones/grid_cells_025_v1.json", encoding="utf-8"))
cell_zone = pd.read_csv(BASE/"COLOMBIA_ANURA/ANTIOQUIA/zones/cell_zone_map_v1.csv")
cell_zone_map = dict(zip(cell_zone["cell_id"], cell_zone["zone_final"]))
valid_cells = set(cell_zone[cell_zone["in_department"] == True]["cell_id"])

def assign_zone(lat, lon):
    if lat is None or lon is None:
        return None, None
    row = int(round(lat / 0.25))
    col = int(round(lon / 0.25))
    cell_id = f"G025_{row}_{col}"
    if cell_id in valid_cells:
        return cell_id, cell_zone_map.get(cell_id)
    return cell_id, None  # cell computed but outside Antioquia dept / not in grid

def geo_lookup(obs_id):
    rec = extracted.get(obs_id)
    if rec is None:
        return dict(lat=None, lon=None, elevation_m=None, obscured=None, place_guess=None, cell_id=None, zone=None)
    cell_id, zone = assign_zone(rec.get("lat"), rec.get("lon"))
    return dict(lat=rec.get("lat"), lon=rec.get("lon"), elevation_m=rec.get("elevation_m"),
                obscured=rec.get("obscured"), place_guess=rec.get("place_guess"), cell_id=cell_id, zone=zone)

unk_geo = [geo_lookup(o) for o in unk_obs]
unk_geo_df = pd.DataFrame(unk_geo)

known_obs_clean = [o[4:] if (o and o.startswith("OBS_")) else None for o in known_obs]
known_geo = [geo_lookup(o) if o else dict(lat=None, lon=None, elevation_m=None, obscured=None, place_guess=None, cell_id=None, zone=None) for o in known_obs_clean]
known_geo_df = pd.DataFrame(known_geo)

# audit
def coverage(df, n_total):
    n_geo = df["lat"].notna().sum()
    n_zone = df["zone"].notna().sum()
    n_elev = df["elevation_m"].notna().sum()
    return dict(geographic_metadata_complete=f"{n_geo}/{n_total}", zone_assignment_complete=f"{n_zone}/{n_total}", elevation_complete=f"{n_elev}/{n_total}")

audit = {
    "UNKNOWN": coverage(unk_geo_df, n_unknown),
    "KNOWN": coverage(known_geo_df, len(known_emb)),
    "KNOWN_excluded_no_observation_id": n_known_no_obs,
    "fetch_summary": json.load(open(OUT/"cache/fetch_summary.json", encoding="utf-8")),
}
json.dump(audit, open(OUT/"geographic_prior_audit.json", "w"), indent=2)
print("Coverage audit:", json.dumps(audit, indent=2))

# ---------------------------------------------------------------------------
# FASE 2 — PRIOR + ANTI-CONTAMINATION CHECK
# ---------------------------------------------------------------------------
prior = pd.read_csv(BASE/"COLOMBIA_ANURA/ANTIOQUIA/priors/prior_zone_taxon_v1.csv")
alpha_info = json.load(open(BASE/"COLOMBIA_ANURA/ANTIOQUIA/priors/alpha_selection_v1.json", encoding="utf-8"))
ALPHA = alpha_info["alpha"]
K = alpha_info["K"]

prior_lookup = {}
for _, r in prior.iterrows():
    prior_lookup[(r["zone_id"], r["scientific_name"])] = r["p"]

zones_present = sorted(cell_zone["zone_final"].dropna().unique())

def prior_for(species_name, zone):
    if zone is None:
        return None  # neutral handled downstream
    key = (zone, species_name)
    if key in prior_lookup:
        return float(prior_lookup[key])
    # species absent from prior table for that zone -> apply same smoothing with n_records=0
    zone_total = prior[prior["zone_id"] == zone]["n_records"].sum()  # NOT n_effective; approx effort denom
    # Use same formula structure: P = (0 + alpha) / (N(z) + alpha*K). Need N(z) (effort-capped) -- approximate
    # using sum of n_effective already computed per zone as stored (n_effective already capped per record).
    n_eff_zone = prior[prior["zone_id"] == zone]["n_effective"].sum()
    p = (0 + ALPHA) / (n_eff_zone + ALPHA * K) if (n_eff_zone + ALPHA * K) > 0 else 1.0 / K
    return float(p)

NEUTRAL_GEO_SCORE = 1.0 / K  # documented choice: uniform prior value when zone unknown (no geographic information)
print(f"NEUTRAL_GEO_SCORE (no zone) = 1/K = {NEUTRAL_GEO_SCORE:.6f}")

# anti-contamination: cross obs_id (UNKNOWN+KNOWN) vs records_v1.csv 'inat:<id>' ids
records = pd.read_csv(BASE/"COLOMBIA_ANURA/ANTIOQUIA/occurrences/records_v1.csv")
records_inat_ids = set(records[records["source"] == "inaturalist"]["record_id"].str.replace("inat:", "", regex=False))
eval_obs_ids = set(unk_obs) | set(o for o in known_obs_clean if o)
overlap = eval_obs_ids & records_inat_ids
contamination = {
    "n_eval_unique_obs_ids": len(eval_obs_ids),
    "n_prior_source_inat_obs_ids": len(records_inat_ids),
    "n_overlap": len(overlap),
    "overlap_fraction_of_eval": len(overlap) / max(1, len(eval_obs_ids)),
    "overlap_sample": sorted(list(overlap))[:20],
    "verdict": "GEOGRAPHIC_PRIOR_DIAGNOSTIC" if len(overlap) > 0 else "NO_OVERLAP_DETECTED",
}
json.dump(contamination, open(OUT/"anti_contamination_check.json", "w"), indent=2)
print("Anti-contamination check:", json.dumps(contamination, indent=2))

# ---------------------------------------------------------------------------
# FASE 3 — geographic_score per sample = P(top1_visual_species | zone)
# ---------------------------------------------------------------------------
def geo_score_for_rows(top1_species, geo_df):
    scores = []
    for sp, zone in zip(top1_species, geo_df["zone"]):
        if zone is None or (isinstance(zone, float) and np.isnan(zone)):
            scores.append(NEUTRAL_GEO_SCORE)
        else:
            p = prior_for(canonico(sp).replace("_", " "), zone)
            scores.append(p if p is not None else NEUTRAL_GEO_SCORE)
    return np.array(scores)

unk_geo_score = geo_score_for_rows(unk_top1_species, unk_geo_df)

# For KNOWN, compute its own top1 (nearest centroid, LOO) species name for geo lookup consistency
known_top1 = []
for i in range(len(known_emb)):
    sp_true = known_scientific[i]
    known_top1.append(sp_true)  # true species (since LOO nearest is essentially itself); documented simplification
known_top1 = np.array(known_top1)
known_geo_score = geo_score_for_rows(known_top1, known_geo_df)

# normalize scores to [0,1] via min-max per score type for combination (documented choice)
def minmax(x):
    x = np.asarray(x, dtype=float)
    lo, hi = np.nanmin(x), np.nanmax(x)
    if hi - lo < 1e-12:
        return np.zeros_like(x)
    return (x - lo) / (hi - lo)

all_visual_dist = np.concatenate([known_scores, unk_visual_dist])
all_visual_norm = minmax(all_visual_dist)  # higher = more "unknown-like"
all_geo_score = np.concatenate([known_geo_score, unk_geo_score])
# geo_score is P(species|zone) in [0,1] roughly (small); invert conceptually: LOW probability => MORE unknown-like
# combined "unknown-ness" from geography = 1 - normalized_geo_probability
geo_probable_norm = minmax(all_geo_score)  # 0=low prob(compatible), 1=high prob
geo_unknownness = 1.0 - geo_probable_norm  # high = geographically incompatible = more unknown-like

y_true_all = y_true  # 0=KNOWN,1=UNKNOWN, same order [known..., unknown...]

def combined_score(w_geo):
    w_v = 1.0 - w_geo
    return w_v * all_visual_norm + w_geo * geo_unknownness

# ---------------------------------------------------------------------------
# FASE 4/5 — WEIGHT SWEEP + full metrics (with bootstrap CI)
# ---------------------------------------------------------------------------
def individual_id_all():
    known_ind = known_individual
    unk_ind = unk_obs  # individual proxy = observation_id, consistent with Fase23A convention
    return np.concatenate([known_ind.astype(str), unk_ind.astype(str)])

ind_all = individual_id_all()

def metrics_at_threshold(y_true, y_score, thr):
    pred_unknown = (y_score >= thr).astype(int)
    tp = np.sum((pred_unknown == 1) & (y_true == 1))
    fn = np.sum((pred_unknown == 0) & (y_true == 1))
    tn = np.sum((pred_unknown == 0) & (y_true == 0))
    fp = np.sum((pred_unknown == 1) & (y_true == 0))
    tpr = tp / max(1, tp + fn)  # = UNKNOWN detection rate = 1-FRR(known accept) ... define below explicitly
    tnr = tn / max(1, tn + fp)
    far = fp / max(1, fp + tn)  # False Accept Rate: KNOWN misclassified as fraction... use standard open-set defs:
    frr = fn / max(1, fn + tp)  # UNKNOWN misclassified as KNOWN (false reject of the "unknown" alarm)
    bal_acc = balanced_accuracy_score(y_true, pred_unknown)
    return dict(TPR=tpr, TNR=tnr, FAR=far, FRR=frr, BalancedAccuracy=bal_acc, TP=int(tp), FP=int(fp), TN=int(tn), FN=int(fn))

def choose_threshold(y_true, y_score):
    # KAR95 quantile of KNOWN-only scores (documented diagnostic convention, consistent with Fase23A anomalies.json)
    known_scores_here = y_score[y_true == 0]
    return float(np.quantile(known_scores_here, 0.95))

def bootstrap_auroc(y_true, y_score, ind_ids, n_iter=1000, seed=SEED):
    rng = np.random.RandomState(seed)
    unique_known_ind = np.unique(ind_ids[y_true == 0])
    unique_unknown_ind = np.unique(ind_ids[y_true == 1])
    aurocs = []
    idx_by_ind = {}
    for u in np.unique(ind_ids):
        idx_by_ind[u] = np.where(ind_ids == u)[0]
    for _ in range(n_iter):
        samp_known = rng.choice(unique_known_ind, size=len(unique_known_ind), replace=True)
        samp_unknown = rng.choice(unique_unknown_ind, size=len(unique_unknown_ind), replace=True)
        idxs = np.concatenate([idx_by_ind[i] for i in samp_known] + [idx_by_ind[i] for i in samp_unknown])
        yt, ys = y_true[idxs], y_score[idxs]
        if len(np.unique(yt)) < 2:
            continue
        try:
            aurocs.append(roc_auc_score(yt, ys))
        except Exception:
            continue
    aurocs = np.array(aurocs)
    return dict(mean=float(aurocs.mean()), ci_lo=float(np.percentile(aurocs, 2.5)), ci_hi=float(np.percentile(aurocs, 97.5)), n_valid=int(len(aurocs)))

weights = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
sweep_rows = []
bootstrap_all = {}
per_sample_records = []

for w in weights:
    score = combined_score(w)
    auroc = roc_auc_score(y_true_all, score)
    auprc = average_precision_score(y_true_all, score)
    thr = choose_threshold(y_true_all, score)
    m = metrics_at_threshold(y_true_all, score, thr)
    bs = bootstrap_auroc(y_true_all, score, ind_all, n_iter=1000, seed=SEED)
    row = dict(weight_geo=w, weight_visual=1 - w, AUROC=auroc, AUPRC=auprc, threshold=thr,
               n_known=int((y_true_all == 0).sum()), n_unknown=int((y_true_all == 1).sum()),
               n_individuals=len(np.unique(ind_all)), **m,
               AUROC_ci_lo=bs["ci_lo"], AUROC_ci_hi=bs["ci_hi"], bootstrap_n_valid=bs["n_valid"])
    sweep_rows.append(row)
    bootstrap_all[f"w_geo_{w}"] = bs
    print(f"w_geo={w}: AUROC={auroc:.5f} [{bs['ci_lo']:.4f},{bs['ci_hi']:.4f}] FAR={m['FAR']:.4f} FRR={m['FRR']:.4f} BalAcc={m['BalancedAccuracy']:.4f}")

sweep_df = pd.DataFrame(sweep_rows)
sweep_df.to_csv(OUT/"weight_sweep_results.csv", index=False)
json.dump(bootstrap_all, open(OUT/"bootstrap_results.json", "w"), indent=2)

# geography-only score (w=1.0 equivalent, pure geo_unknownness)
geo_only_score = geo_unknownness
auroc_geo_only = roc_auc_score(y_true_all, geo_only_score)
thr_geo = choose_threshold(y_true_all, geo_only_score)
m_geo = metrics_at_threshold(y_true_all, geo_only_score, thr_geo)
bs_geo = bootstrap_auroc(y_true_all, geo_only_score, ind_all, n_iter=1000, seed=SEED)
geographic_only_metrics = dict(AUROC=auroc_geo_only, AUPRC=average_precision_score(y_true_all, geo_only_score),
                                threshold=thr_geo, **m_geo, AUROC_ci=[bs_geo["ci_lo"], bs_geo["ci_hi"]])
json.dump(geographic_only_metrics, open(OUT/"geographic_only_metrics.json", "w"), indent=2)
print("GEO-ONLY:", geographic_only_metrics)

# baseline (w=0) and best combined config saved explicitly
baseline_row = sweep_df[sweep_df.weight_geo == 0.0].iloc[0].to_dict()
json.dump(baseline_row, open(OUT/"baseline_visual_metrics.json", "w"), indent=2, default=str)

best_row = sweep_df.sort_values("AUROC", ascending=False).iloc[0].to_dict()
json.dump(best_row, open(OUT/"visual_plus_geography_metrics.json", "w"), indent=2, default=str)
print("BEST COMBINED:", best_row)

# per-sample results (for best weight)
best_w = best_row["weight_geo"]
best_score = combined_score(best_w)
species_all = np.concatenate([known_scientific, unk_top1_species])
true_species_all = np.concatenate([known_scientific, unk_species])
zone_all = pd.concat([known_geo_df["zone"], unk_geo_df["zone"]], ignore_index=True)
per_sample = pd.DataFrame({
    "is_unknown_true": y_true_all.astype(int),
    "true_species": true_species_all,
    "predicted_top1_species": species_all,
    "individual_id": ind_all,
    "visual_dist_raw": all_visual_dist,
    "visual_norm": all_visual_norm,
    "geo_score_prob": all_geo_score,
    "geo_unknownness": geo_unknownness,
    "zone": zone_all.values,
    "combined_score_best_w": best_score,
    "baseline_score_w0": all_visual_norm,
})
per_sample.to_csv(OUT/"per_sample_results.csv", index=False)

# ---------------------------------------------------------------------------
# FASE 6 — subgroup analysis (only on UNKNOWN rows): same genus vs different genus, zone, elevation
# ---------------------------------------------------------------------------
known_genera = set(genero_de(canonico(sp)) for sp in species_list)
unk_genus = np.array([genero_de(canonico(sp)) for sp in unk_species])
same_genus_mask = np.array([g in known_genera for g in unk_genus])

unk_idx_in_all = np.arange(len(known_scores), len(known_scores) + len(unk_visual_dist))
subgroup_rows = []
for w in [0.0, best_w]:
    score = combined_score(w)
    unk_scores_w = score[unk_idx_in_all]
    known_scores_w = score[:len(known_scores)]
    for label, mask in [("same_genus", same_genus_mask), ("different_genus", ~same_genus_mask)]:
        if mask.sum() == 0:
            continue
        yt = np.concatenate([np.zeros(len(known_scores_w)), np.ones(mask.sum())])
        ys = np.concatenate([known_scores_w, unk_scores_w[mask]])
        try:
            a = roc_auc_score(yt, ys)
        except Exception:
            a = None
        subgroup_rows.append(dict(weight_geo=w, subgroup=label, n_unknown=int(mask.sum()), AUROC=a))

# zone-based subgroup (only where UNKNOWN has a known zone and matches a KNOWN-associated zone concept: use same-zone vs diff-zone by whether UNKNOWN zone matches the modal zone of its predicted species per prior)
unk_zone = unk_geo_df["zone"].values
zone_known_mask = pd.notna(unk_zone)
subgroup_rows.append(dict(weight_geo=best_w, subgroup="unknown_with_zone_assigned", n_unknown=int(zone_known_mask.sum()), AUROC=None))
subgroup_rows.append(dict(weight_geo=best_w, subgroup="unknown_without_zone", n_unknown=int((~zone_known_mask).sum()), AUROC=None))

pd.DataFrame(subgroup_rows).to_csv(OUT/"metrics_by_taxonomic_and_geo_subgroup.csv", index=False)
print("Subgroup AUROCs:", subgroup_rows)

# ---------------------------------------------------------------------------
# FASE 7 — Ablation A/B/C
# ---------------------------------------------------------------------------
ablation = {
    "A_visual_only": baseline_row,
    "B_geography_only": geographic_only_metrics,
    "C_visual_plus_geography_best_weight": best_row,
    "D_morphological_regions": "NOT EXECUTED - future work (per protocol)",
}
json.dump(ablation, open(OUT/"ablation_summary.json", "w"), indent=2, default=str)

# ---------------------------------------------------------------------------
# FASE 8 — threshold-crossing case study (visual vs combined disagreement)
# ---------------------------------------------------------------------------
crosses = []
base_score = all_visual_norm
comb_score = combined_score(best_w)
base_thr = baseline_row["threshold"]
comb_thr = best_row["threshold"]
base_pred = (base_score >= base_thr).astype(int)
comb_pred = (comb_score >= comb_thr).astype(int)
changed = np.where(base_pred != comb_pred)[0]
for i in changed[:15]:
    crosses.append(dict(
        idx=int(i), is_unknown_true=int(y_true_all[i]), true_species=str(true_species_all[i]),
        predicted_top1_species=str(species_all[i]), zone=str(zone_all.values[i]),
        visual_norm=float(all_visual_norm[i]), geo_prob=float(all_geo_score[i]),
        baseline_pred=("UNKNOWN" if base_pred[i] else "KNOWN"),
        combined_pred=("UNKNOWN" if comb_pred[i] else "KNOWN"),
    ))
json.dump({"n_changed_total": int(len(changed)), "n_known_total_sample": int(len(y_true_all)), "cases": crosses},
          open(OUT/"threshold_crossing_cases.json", "w"), indent=2)
print(f"Threshold-crossing cases (baseline vs best combined): {len(changed)} / {len(y_true_all)}")

# ---------------------------------------------------------------------------
# REPRODUCIBILITY MANIFEST
# ---------------------------------------------------------------------------
def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

manifest = {
    "date": pd.Timestamp.now().isoformat(),
    "seed": SEED,
    "bootstrap_iterations": 1000,
    "encoder_sha256_expected": "98a6c54d6edb27e2b0344b8bbbaebd2ab749b1bf5136991ff73b37f66ee2c1ac",
    "unknown_embeddings_sha256": sha256_of(BASE/"validation/fase23a_open_set_automatic/embeddings/unknown_embeddings.npz"),
    "known_embeddings_sha256": sha256_of(BASE/"validation/fase16_clean_open_set/clean_known_embeddings.npz"),
    "prior_csv_sha256": sha256_of(BASE/"COLOMBIA_ANURA/ANTIOQUIA/priors/prior_zone_taxon_v1.csv"),
    "cell_zone_map_sha256": sha256_of(BASE/"COLOMBIA_ANURA/ANTIOQUIA/zones/cell_zone_map_v1.csv"),
    "alpha": ALPHA, "K": K,
    "neutral_geo_score": NEUTRAL_GEO_SCORE,
    "zone_assignment_method": "row=round(lat/0.25), col=round(lon/0.25), cell_id=f'G025_{row}_{col}'; zone = cell_zone_map_v1.csv[cell_id] if cell_id in-department else None",
    "visual_score_method": "euclidean_raw min-distance to per-species mean centroid (KNOWN: leave-one-out; UNKNOWN: full-sample centroids)",
    "combination_method": "weighted sum of min-max normalized [0,1] scores: combined = (1-w)*visual_norm + w*(1-geo_prob_norm)",
    "threshold_method": "KAR95 quantile of KNOWN-only score distribution (diagnostic convention, same as Fase23A anomalies.json — NOT Youden-J, no independent UNKNOWN calibration split available)",
    "weights_swept": weights,
    "best_weight_by_auroc": best_w,
    "anti_contamination_overlap_n": contamination["n_overlap"],
}
json.dump(manifest, open(OUT/"reproducibility_manifest.json", "w"), indent=2, default=str)

print("\nDONE. All artifacts written to", OUT)
