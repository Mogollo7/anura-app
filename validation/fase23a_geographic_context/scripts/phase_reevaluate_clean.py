#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
phase_reevaluate_clean.py — Problema 3: barrido de pesos visual+geo usando
(a) el visual_score que reproduce el 0.57329 oficial (Problema 1,
    validation/fase23a_geographic_context/scripts/phase_reproduce_23a.py,
    scores persistidos en reproduced_scores_v2.npz)
(b) el geographic_score derivado del prior LIMPIO (Problema 2,
    prior_zone_taxon_v2_clean.csv, sin los 1214 observation_id contaminados)

Reutiliza el mismo protocolo de combinacion / sweep / bootstrap de
scripts/phase1to8_main.py (Fases 4/5 del experimento anterior), pero
corrigiendo los dos defectos identificados. No modifica ningun archivo de
fase23a_open_set_automatic/, fase16_clean_open_set/, ni COLOMBIA_ANURA/.../
priors/prior_zone_taxon_v1.csv.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, balanced_accuracy_score

sys.path.insert(0, "D:/Anura")
from training.taxonomia import canonico

BASE = Path("D:/Anura")
OUT = BASE / "validation/fase23a_geographic_context"
SEED = 42

# ---------------------------------------------------------------------------
# 1. VISUAL SCORE (official euclidean_raw reproduction, from Problem 1 gate)
# ---------------------------------------------------------------------------
gate = json.load(open(OUT / "baseline_reproduction_v2.json", encoding="utf-8"))
assert gate["gate_passed"], "Gate 1 (baseline reproduction) did not pass — reevaluation must not proceed."

repro = np.load(OUT / "reproduced_scores_v2.npz", allow_pickle=True)
d_known = repro["d_known"].astype(np.float64)
d_unknown = repro["d_unknown"].astype(np.float64)
known_species_ids = np.array([str(s) for s in repro["species_known"]])
known_image_ids = np.array([str(s) for s in repro["image_known"]])
unk_species = np.array([str(s) for s in repro["species_unknown"]])
unk_obs = np.array([str(s) for s in repro["obs_unknown"]])

n_known = len(d_known)
n_unknown = len(d_unknown)
print(f"KNOWN (official visual score): {n_known}, UNKNOWN: {n_unknown}")

# Recover the 41-centroid matrix (same as phase_reproduce_23a.py) to get UNKNOWN top1 species
# (needed to look up P(species|zone) in the geographic prior).
def canonical_name(name):
    n = name.replace('_', ' ').strip()
    if n == "Pristimantis acanthinus":
        n = "Pristimantis achatinus"
    return n


def compute_centroids(X, y):
    return {c: np.mean(X[y == c], axis=0) for c in np.unique(y)}


ref_data = np.load(BASE / "evaluation/fase13/embeddings/reference_embeddings.npz")
X_ref, y_ref = ref_data["embeddings"], np.array([canonical_name(s) for s in ref_data["species"]])
ref_centroids = compute_centroids(X_ref, y_ref)
train_data = np.load(BASE / "evaluation/fase13/embeddings/train_embeddings.npz")
X_train, y_train = train_data["embeddings"], np.array([canonical_name(s) for s in train_data["species"]])
train_centroids = compute_centroids(X_train, y_train)

all_41_centroids = {}
for sp, c in ref_centroids.items():
    if sp in train_centroids:
        all_41_centroids[sp] = c
for sp, c in train_centroids.items():
    if sp not in all_41_centroids:
        all_41_centroids[sp] = c
classes = sorted(all_41_centroids.keys())
C = np.array([all_41_centroids[c] for c in classes])

unk_npz = np.load(BASE / "validation/fase23a_open_set_automatic/embeddings/unknown_embeddings.npz", allow_pickle=True)
X_unknown = unk_npz["embeddings"].astype(np.float64)
d_all_unk = np.linalg.norm(X_unknown[:, None, :] - C[None, :, :], axis=2)
unk_top1_species = np.array([classes[i] for i in d_all_unk.argmin(axis=1)])
# sanity: recompute min distance == d_unknown (persisted by phase_reproduce_23a.py)
assert np.allclose(d_all_unk.min(axis=1), d_unknown, atol=1e-4), "unknown distances mismatch vs persisted gate scores"

# KNOWN top1 species: same documented simplification as the prior experiment (true species),
# since the official visual score's KNOWN pool is compared against DIFFERENT centroids
# (reference/train), not leave-one-out on itself — there is no risk of trivial self-match here,
# but we keep true species as top1 for geo lookup consistency with the true observation.
species_registry = json.load(open(BASE / "taxonomy/species/species_registry.json", encoding="utf-8"))
sid_to_name = {s["species_id"]: s["scientific_name"] for s in species_registry["species"]}
known_manifest = json.load(open(BASE / "validation/fase16_clean_open_set/clean_known_manifest.json", encoding="utf-8"))
known_images_meta = {im["image_id"]: im for im in known_manifest["images"]}
known_sci_name = np.array([known_images_meta[iid]["scientific_name"] for iid in known_image_ids])
known_obs = np.array([known_images_meta[iid].get("observation_id") for iid in known_image_ids])
known_individual = np.array([known_images_meta[iid].get("individual_id") for iid in known_image_ids])
known_top1 = known_sci_name

y_true = np.concatenate([np.zeros(n_known), np.ones(n_unknown)])  # 1 = UNKNOWN
all_visual_dist = np.concatenate([d_known, d_unknown])


def minmax(x):
    x = np.asarray(x, dtype=float)
    lo, hi = np.nanmin(x), np.nanmax(x)
    if hi - lo < 1e-12:
        return np.zeros_like(x)
    return (x - lo) / (hi - lo)


all_visual_norm = minmax(all_visual_dist)  # higher = more unknown-like

# ---------------------------------------------------------------------------
# 2. GEOGRAPHIC SCORE from the CLEAN prior (Problem 2)
# ---------------------------------------------------------------------------
extracted = json.load(open(OUT / "cache/inat_extracted.json", encoding="utf-8"))
cell_zone = pd.read_csv(BASE / "COLOMBIA_ANURA/ANTIOQUIA/zones/cell_zone_map_v1.csv")
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
    return cell_id, None


def geo_lookup(obs_id):
    rec = extracted.get(obs_id)
    if rec is None:
        return dict(lat=None, lon=None, zone=None)
    cell_id, zone = assign_zone(rec.get("lat"), rec.get("lon"))
    return dict(lat=rec.get("lat"), lon=rec.get("lon"), zone=zone)


unk_geo_df = pd.DataFrame([geo_lookup(o) for o in unk_obs])
known_obs_clean = [o[4:] if (o and o.startswith("OBS_")) else None for o in known_obs]
known_geo_df = pd.DataFrame([geo_lookup(o) if o else dict(lat=None, lon=None, zone=None) for o in known_obs_clean])

prior = pd.read_csv(OUT / "prior_zone_taxon_v2_clean.csv")
prior_manifest = json.load(open(OUT / "prior_zone_taxon_v2_clean_manifest.json", encoding="utf-8"))
ALPHA = prior_manifest["alpha_selected"]
K = prior_manifest["K_taxa"]
NEUTRAL_GEO_SCORE = 1.0 / K

prior_lookup = {(r["zone_id"], r["scientific_name"]): r["p"] for _, r in prior.iterrows()}


def prior_for(species_name, zone):
    if zone is None:
        return None
    key = (zone, species_name)
    if key in prior_lookup:
        return float(prior_lookup[key])
    n_eff_zone = prior[prior["zone_id"] == zone]["n_effective"].sum()
    denom = n_eff_zone + ALPHA * K
    return float(ALPHA / denom) if denom > 0 else 1.0 / K


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
known_geo_score = geo_score_for_rows(known_top1, known_geo_df)
all_geo_score = np.concatenate([known_geo_score, unk_geo_score])
geo_probable_norm = minmax(all_geo_score)
geo_unknownness = 1.0 - geo_probable_norm


def combined_score(w_geo):
    w_v = 1.0 - w_geo
    return w_v * all_visual_norm + w_geo * geo_unknownness


# ---------------------------------------------------------------------------
# 3. Sweep + bootstrap (same protocol as phase1to8_main.py: 1000 iter, seed=42,
#    stratified by individual, separately for KNOWN and UNKNOWN pools)
# ---------------------------------------------------------------------------
ind_all = np.concatenate([known_individual.astype(str), unk_obs.astype(str)])


def metrics_at_threshold(y_true, y_score, thr):
    # y_true: 1=UNKNOWN, 0=KNOWN. pred_unknown=1 means the sample is predicted/rejected as UNKNOWN.
    # Official convention (matches fase23a_run.py / method_comparison.csv):
    #   FAR (False Accept Rate)  = fraction of true UNKNOWN samples wrongly ACCEPTED as known
    #                             = (pred_unknown==0 & y_true==1) / (y_true==1)
    #   FRR (False Reject Rate)  = fraction of true KNOWN samples wrongly REJECTED as unknown
    #                             = (pred_unknown==1 & y_true==0) / (y_true==0)
    # NOTE: an earlier version of this metric (phase1to8_main.py, the prior/flawed experiment)
    # had these two swapped under the same names — fixed here to match the official definition.
    pred_unknown = (y_score >= thr).astype(int)
    tp = np.sum((pred_unknown == 1) & (y_true == 1))  # unknown correctly rejected
    fn = np.sum((pred_unknown == 0) & (y_true == 1))  # unknown wrongly accepted (-> FAR numerator)
    tn = np.sum((pred_unknown == 0) & (y_true == 0))  # known correctly accepted
    fp = np.sum((pred_unknown == 1) & (y_true == 0))  # known wrongly rejected (-> FRR numerator)
    tpr = tp / max(1, tp + fn)
    tnr = tn / max(1, tn + fp)
    far = fn / max(1, fn + tp)
    frr = fp / max(1, fp + tn)
    bal_acc = balanced_accuracy_score(y_true, pred_unknown)
    return dict(TPR=tpr, TNR=tnr, FAR=far, FRR=frr, BalancedAccuracy=bal_acc,
                TP=int(tp), FP=int(fp), TN=int(tn), FN=int(fn))


def choose_threshold(y_true, y_score):
    known_scores_here = y_score[y_true == 0]
    return float(np.quantile(known_scores_here, 0.95))


def bootstrap_metric(y_true, y_score, ind_ids, n_iter=1000, seed=SEED):
    rng = np.random.RandomState(seed)
    unique_known_ind = np.unique(ind_ids[y_true == 0])
    unique_unknown_ind = np.unique(ind_ids[y_true == 1])
    idx_by_ind = {u: np.where(ind_ids == u)[0] for u in np.unique(ind_ids)}
    aurocs, fars, frrs = [], [], []
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
        thr = choose_threshold(yt, ys)
        m = metrics_at_threshold(yt, ys, thr)
        fars.append(m["FAR"])
        frrs.append(m["FRR"])
    def ci(arr):
        arr = np.array(arr)
        return dict(mean=float(arr.mean()), ci_lo=float(np.percentile(arr, 2.5)),
                    ci_hi=float(np.percentile(arr, 97.5)), n_valid=int(len(arr)))
    return dict(auroc=ci(aurocs), far=ci(fars), frr=ci(frrs))


# ---------------------------------------------------------------------------
# 2b. Official-comparable threshold: KAR95 quantile of the CALIBRATION split
#     (same convention actually used by fase23a_run.py / method_comparison.csv for
#     euclidean_raw), computed with the SAME 41 centroids. Calibration images have
#     no coordinates, so this can only be computed for the VISUAL-ONLY (w=0) score,
#     not for combined visual+geo scores. Reported alongside the eval-pool-KAR95
#     convention used for the sweep (documented limitation).
# ---------------------------------------------------------------------------
calib_data = np.load(BASE / "evaluation/fase13/embeddings/calibration_embeddings.npz")
X_calib = calib_data["embeddings"].astype(np.float64)
d_calib = np.linalg.norm(X_calib[:, None, :] - C[None, :, :], axis=2).min(axis=1)
tau_calib_raw = float(np.quantile(d_calib, 0.95))
# same threshold expressed in the min-max normalized visual score space used by combined_score()
lo_v, hi_v = np.nanmin(all_visual_dist), np.nanmax(all_visual_dist)
tau_calib_norm = (tau_calib_raw - lo_v) / (hi_v - lo_v) if (hi_v - lo_v) > 1e-12 else 0.0
m_calib_thr = metrics_at_threshold(y_true, all_visual_norm, tau_calib_norm)
print(f"\n[official-comparable] visual-only (w=0) at CALIBRATION-KAR95 tau={tau_calib_raw:.4f} "
      f"(norm={tau_calib_norm:.4f}): FAR={m_calib_thr['FAR']:.4f} FRR={m_calib_thr['FRR']:.4f} "
      f"(official CSV: FAR=0.8113 FRR=0.1390)")

weights = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
sweep_rows = []
bootstrap_all = {}
for w in weights:
    score = combined_score(w)
    auroc = roc_auc_score(y_true, score)
    auprc = average_precision_score(y_true, score)
    thr = choose_threshold(y_true, score)
    m = metrics_at_threshold(y_true, score, thr)
    bs = bootstrap_metric(y_true, score, ind_all, n_iter=1000, seed=SEED)
    row = dict(weight_geo=w, weight_visual=1 - w, AUROC=auroc, AUPRC=auprc, threshold=thr,
               n_known=n_known, n_unknown=n_unknown, n_individuals=len(np.unique(ind_all)),
               **m,
               AUROC_ci_lo=bs["auroc"]["ci_lo"], AUROC_ci_hi=bs["auroc"]["ci_hi"],
               FAR_ci_lo=bs["far"]["ci_lo"], FAR_ci_hi=bs["far"]["ci_hi"],
               FRR_ci_lo=bs["frr"]["ci_lo"], FRR_ci_hi=bs["frr"]["ci_hi"],
               bootstrap_n_valid=bs["auroc"]["n_valid"])
    sweep_rows.append(row)
    bootstrap_all[f"w_geo_{w}"] = bs
    print(f"w_geo={w}: AUROC={auroc:.5f} [{bs['auroc']['ci_lo']:.4f},{bs['auroc']['ci_hi']:.4f}] "
          f"FAR={m['FAR']:.4f} [{bs['far']['ci_lo']:.4f},{bs['far']['ci_hi']:.4f}] "
          f"FRR={m['FRR']:.4f} [{bs['frr']['ci_lo']:.4f},{bs['frr']['ci_hi']:.4f}]")

sweep_df = pd.DataFrame(sweep_rows)
sweep_df.to_csv(OUT / "weight_sweep_results_v2_clean.csv", index=False)

best_row = sweep_df.sort_values("AUROC", ascending=False).iloc[0].to_dict()
baseline_row = sweep_df[sweep_df.weight_geo == 0.0].iloc[0].to_dict()

# Official 23A comparison numbers
official = dict(
    auroc=0.5732919408781961, auroc_ci_lo=0.5425980488949688, auroc_ci_hi=0.6041284714269096,
    far=0.8112903225806452, frr=0.13899665551839466,
    n_known=7475, n_unknown=620,
)

result = {
    "gate1_passed": True,
    "official_23a": official,
    "geo_clean_visual_only_w0": baseline_row,
    "geo_clean_best_weight": best_row,
    "weight_sweep_full": sweep_rows,
    "bootstrap_by_weight": bootstrap_all,
    "prior_source": "validation/fase23a_geographic_context/prior_zone_taxon_v2_clean.csv "
                     "(1214 contaminated observation_id excluded)",
    "visual_score_source": "validation/fase23a_geographic_context/reproduced_scores_v2.npz "
                            "(official euclidean_raw, gate-verified AUROC diff=0.0 vs 0.57329)",
    "visual_only_official_comparable_threshold": {
        "tau_calibration_kar95_raw_distance": tau_calib_raw,
        "FAR": m_calib_thr["FAR"], "FRR": m_calib_thr["FRR"],
        "official_FAR": 0.8112903225806452, "official_FRR": 0.13899665551839466,
        "note": "Computed with the CALIBRATION split (same convention as official method_comparison.csv), "
                "unlike the sweep table below which uses a KAR95-of-eval-KNOWN-pool threshold (documented "
                "limitation: CALIBRATION images have no coordinates, so this convention cannot be extended "
                "to the combined visual+geo scores).",
    },
    "verdict": None,
}

# Verdict logic: compare best combined AUROC CI vs official/baseline AUROC CI
best_auroc = best_row["AUROC"]
baseline_auroc = baseline_row["AUROC"]
delta = best_auroc - baseline_auroc
ci_lo_best, ci_hi_best = best_row["AUROC_ci_lo"], best_row["AUROC_ci_hi"]
ci_lo_base, ci_hi_base = baseline_row["AUROC_ci_lo"], baseline_row["AUROC_ci_hi"]
non_overlapping_better = ci_lo_best > ci_hi_base

if best_row["weight_geo"] == 0.0:
    verdict = "GEOGRAPHY_NOT_HELPFUL"
elif non_overlapping_better and delta > 0.02:
    verdict = "GEOGRAPHY_HELPFUL"
elif delta > 0:
    verdict = "GEOGRAPHY_MARGINAL"
else:
    verdict = "GEOGRAPHY_NOT_HELPFUL"

result["verdict"] = verdict
result["verdict_rationale"] = {
    "best_weight_geo": best_row["weight_geo"],
    "delta_auroc_vs_visual_only": delta,
    "ci_overlap_best_vs_baseline": not non_overlapping_better,
}

with open(OUT / "geo_clean_reevaluation_v2.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False, default=str)

print("\nVERDICT:", verdict)
print("BEST ROW:", best_row)
print("BASELINE ROW (w=0, visual only, official score):", baseline_row)
print("\nDONE.")
