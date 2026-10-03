#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
phase_geo2_weight_sweep.py — GEO-2: extension quirurgica del barrido de pesos
visual+geo de phase_reevaluate_clean.py (Problema 3) a un rango mas amplio de
w_geo (0.0-0.8, +0.9/1.0), con analisis Pareto y por subgrupo taxonomico
(same_genus / different_genus). Reutiliza EXACTAMENTE la misma combinacion,
normalizacion, prior limpio v2, bootstrap (1000 iter, seed=42, estratificado
por individuo) y definicion de FAR/FRR que phase_reevaluate_clean.py.

GATE 0: reproduce baseline_reproduction_v2.json (euclidean_raw oficial,
AUROC=0.57329, diff=0.0). Si falla, escribe GEO2_BLOCKED.json y se detiene.

No toca fase23a_open_set_automatic/, fase16_clean_open_set/, priors v1,
encoder, embeddings existentes. No fine-tuning, no nuevos embeddings, no
llamadas a iNaturalist, no nuevos priors. Todo output con prefijo GEO2_.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, balanced_accuracy_score

sys.path.insert(0, "D:/Anura")
from training.taxonomia import canonico, genero_de

BASE = Path("D:/Anura")
OUT = BASE / "validation/fase23a_geographic_context"
SEED = 42

# ---------------------------------------------------------------------------
# GATE 0 — Integridad: reproducir 0.57329 antes de cualquier otra cosa
# ---------------------------------------------------------------------------
OFFICIAL_AUROC = 0.5732919408781961
gate_path = OUT / "baseline_reproduction_v2.json"
if not gate_path.exists():
    print("baseline_reproduction_v2.json no existe -- re-ejecutando phase_reproduce_23a.py")
    import subprocess
    r = subprocess.run([sys.executable, str(OUT / "scripts/phase_reproduce_23a.py")], cwd=str(BASE))
    if r.returncode != 0:
        raise SystemExit("phase_reproduce_23a.py fallo")

gate = json.load(open(gate_path, encoding="utf-8"))
reproduced_auroc = gate["reproduced_auroc"]
abs_diff = abs(reproduced_auroc - OFFICIAL_AUROC)
gate0_passed = gate.get("gate_passed", False) and abs_diff == 0.0

print(f"GATE 0: reproduced_auroc={reproduced_auroc:.5f} official={OFFICIAL_AUROC:.5f} "
      f"abs_diff={abs_diff} gate0_passed={gate0_passed}")

if not gate0_passed:
    blocked = {
        "status": "GEO2_BLOCKED",
        "reason": "El AUROC del scoring visual puro reproducido no coincide exactamente (diff=0.0) "
                  "con el oficial 0.57329 (euclidean_raw, method_comparison.csv de fase23a_open_set_automatic).",
        "reproduced_auroc": reproduced_auroc,
        "official_auroc": OFFICIAL_AUROC,
        "abs_diff": abs_diff,
        "gate_json": gate,
    }
    with open(OUT / "GEO2_BLOCKED.json", "w", encoding="utf-8") as f:
        json.dump(blocked, f, indent=2, ensure_ascii=False)
    print("\nGEO2_BLOCKED -- ver GEO2_BLOCKED.json")
    raise SystemExit(1)

print("GATE 0 PASSED -- continuando al barrido GEO-2.\n")

# ---------------------------------------------------------------------------
# 1. VISUAL SCORE (identico a phase_reevaluate_clean.py)
# ---------------------------------------------------------------------------
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
assert np.allclose(d_all_unk.min(axis=1), d_unknown, atol=1e-4), "unknown distances mismatch vs persisted gate scores"

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


all_visual_norm = minmax(all_visual_dist)

# ---------------------------------------------------------------------------
# 2. GEOGRAPHIC SCORE from prior_zone_taxon_v2_clean.csv (identico)
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
# 3. Sweep + bootstrap (identico protocolo, misma funcion)
# ---------------------------------------------------------------------------
ind_all = np.concatenate([known_individual.astype(str), unk_obs.astype(str)])


def metrics_at_threshold(y_true, y_score, thr):
    pred_unknown = (y_score >= thr).astype(int)
    tp = np.sum((pred_unknown == 1) & (y_true == 1))
    fn = np.sum((pred_unknown == 0) & (y_true == 1))
    tn = np.sum((pred_unknown == 0) & (y_true == 0))
    fp = np.sum((pred_unknown == 1) & (y_true == 0))
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


weights = [0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]

sweep_rows = []
bootstrap_all = {}
for w in weights:
    score = combined_score(w)
    auroc = roc_auc_score(y_true, score)
    auprc = average_precision_score(y_true, score)
    thr = choose_threshold(y_true, score)
    m = metrics_at_threshold(y_true, score, thr)
    bs = bootstrap_metric(y_true, score, ind_all, n_iter=1000, seed=SEED)
    row = dict(w_geo=w, w_visual=round(1 - w, 2), threshold=thr, AUROC=auroc,
               AUROC_ci_lo=bs["auroc"]["ci_lo"], AUROC_ci_hi=bs["auroc"]["ci_hi"],
               FAR=m["FAR"], FRR=m["FRR"], BalancedAccuracy=m["BalancedAccuracy"],
               TPR=m["TPR"], TNR=m["TNR"], AUPRC=auprc,
               n_known=n_known, n_unknown=n_unknown, n_individuals=len(np.unique(ind_all)),
               FAR_ci_lo=bs["far"]["ci_lo"], FAR_ci_hi=bs["far"]["ci_hi"],
               FRR_ci_lo=bs["frr"]["ci_lo"], FRR_ci_hi=bs["frr"]["ci_hi"],
               bootstrap_n_valid=bs["auroc"]["n_valid"])
    sweep_rows.append(row)
    bootstrap_all[f"w_geo_{w:.2f}"] = bs
    print(f"w_geo={w:.2f}: AUROC={auroc:.5f} [{bs['auroc']['ci_lo']:.4f},{bs['auroc']['ci_hi']:.4f}] "
          f"FAR={m['FAR']:.4f} FRR={m['FRR']:.4f} BalAcc={m['BalancedAccuracy']:.4f}")

sweep_df = pd.DataFrame(sweep_rows)
sweep_cols = ["w_geo", "w_visual", "threshold", "AUROC", "AUROC_ci_lo", "AUROC_ci_hi",
              "FAR", "FRR", "BalancedAccuracy", "TPR", "TNR"]
sweep_df.to_csv(OUT / "GEO2_WEIGHT_SWEEP.csv", index=False, columns=sweep_cols + [c for c in sweep_df.columns if c not in sweep_cols])
with open(OUT / "GEO2_WEIGHT_SWEEP.json", "w", encoding="utf-8") as f:
    json.dump(sweep_rows, f, indent=2, ensure_ascii=False, default=str)
with open(OUT / "GEO2_BOOTSTRAP_RESULTS.json", "w", encoding="utf-8") as f:
    json.dump(bootstrap_all, f, indent=2, ensure_ascii=False, default=str)

# ---------------------------------------------------------------------------
# 4. Analisis Pareto: A domina B si AUROC_A>=AUROC_B, FAR_A<=FAR_B, FRR_A<=FRR_B,
#    y al menos una estrictamente mejor.
# ---------------------------------------------------------------------------
def dominates(a, b):
    ge = (a["AUROC"] >= b["AUROC"]) and (a["FAR"] <= b["FAR"]) and (a["FRR"] <= b["FRR"])
    strictly = (a["AUROC"] > b["AUROC"]) or (a["FAR"] < b["FAR"]) or (a["FRR"] < b["FRR"])
    return ge and strictly


pareto_front = []
for i, a in enumerate(sweep_rows):
    dominated = False
    for j, b in enumerate(sweep_rows):
        if i == j:
            continue
        if dominates(b, a):
            dominated = True
            break
    if not dominated:
        pareto_front.append(a)

pareto_df = pd.DataFrame(pareto_front)[["w_geo", "w_visual", "AUROC", "AUROC_ci_lo", "AUROC_ci_hi", "FAR", "FRR", "BalancedAccuracy"]]
pareto_df = pareto_df.sort_values("w_geo")
pareto_df.to_csv(OUT / "GEO2_PARETO_FRONT.csv", index=False)
print("\nPareto front (no-dominados):")
print(pareto_df.to_string(index=False))

# ---------------------------------------------------------------------------
# 5. Subgroup analysis: same_genus vs different_genus (identico a phase1to8_main.py)
# ---------------------------------------------------------------------------
species_list = sorted(set(known_sci_name))
known_genera = set(genero_de(canonico(sp)) for sp in species_list)
unk_genus = np.array([genero_de(canonico(sp)) for sp in unk_species])
same_genus_mask = np.array([g in known_genera for g in unk_genus])
n_same, n_diff = int(same_genus_mask.sum()), int((~same_genus_mask).sum())
print(f"\nUNKNOWN same_genus={n_same}, different_genus={n_diff}")

subgroup_rows = []
for w in weights:
    score = combined_score(w)
    known_scores_w = score[:n_known]
    unk_scores_w = score[n_known:]
    for label, mask in [("same_genus", same_genus_mask), ("different_genus", ~same_genus_mask)]:
        if mask.sum() == 0:
            continue
        yt = np.concatenate([np.zeros(n_known), np.ones(int(mask.sum()))])
        ys = np.concatenate([known_scores_w, unk_scores_w[mask]])
        try:
            a = roc_auc_score(yt, ys)
        except Exception:
            a = None
        thr = choose_threshold(yt, ys)
        m = metrics_at_threshold(yt, ys, thr) if a is not None else {}
        subgroup_rows.append(dict(
            w_geo=w, subgroup=label, n_unknown=int(mask.sum()), n_known=n_known,
            AUROC=a, FAR=m.get("FAR"), FRR=m.get("FRR"), BalancedAccuracy=m.get("BalancedAccuracy"),
        ))

subgroup_df = pd.DataFrame(subgroup_rows)
subgroup_df.to_csv(OUT / "GEO2_SUBGROUP_ANALYSIS.csv", index=False)

# ---------------------------------------------------------------------------
# 6. Analisis de contribucion geografica (zona, frecuencia de especie -- sin elevacion)
# ---------------------------------------------------------------------------
unk_zone = unk_geo_df["zone"].values
zone_assigned_mask = pd.notna(unk_zone)
n_zone_assigned = int(zone_assigned_mask.sum())
n_zone_missing = int((~zone_assigned_mask).sum())

zone_counts = pd.Series(unk_zone[zone_assigned_mask]).value_counts().to_dict()
species_freq = pd.Series(unk_species).value_counts().to_dict()

geo_contribution = {
    "n_unknown_with_zone_assigned": n_zone_assigned,
    "n_unknown_without_zone": n_zone_missing,
    "zone_distribution_assigned": zone_counts,
    "unknown_species_frequency_top10": dict(list(sorted(species_freq.items(), key=lambda x: -x[1]))[:10]),
    "elevation_note": "NO se uso elevacion (0/4466 recuperable, confirmado en experimento anterior; no reintroducida).",
    "no_new_inaturalist_calls": True,
    "cache_source": "validation/fase23a_geographic_context/cache/inat_extracted.json (existente, sin llamadas nuevas)",
}
with open(OUT / "GEO2_GEO_CONTRIBUTION.json", "w", encoding="utf-8") as f:
    json.dump(geo_contribution, f, indent=2, ensure_ascii=False, default=str)

# ---------------------------------------------------------------------------
# 7. Interpretacion
# ---------------------------------------------------------------------------
baseline_row = next(r for r in sweep_rows if r["w_geo"] == 0.0)
best_auroc_row = max(sweep_rows, key=lambda r: r["AUROC"])

ci_overlap_best_vs_base = not (best_auroc_row["AUROC_ci_lo"] > baseline_row["AUROC_ci_hi"])
delta_best = best_auroc_row["AUROC"] - baseline_row["AUROC"]

# FAR "aceptable" heuristic (documentado, no forzado): FAR del mejor punto AUROC vs baseline
far_at_best = best_auroc_row["FAR"]
far_baseline = baseline_row["FAR"]

# monotonicidad mas alla de 0.5
weights_after_05 = [r for r in sweep_rows if r["w_geo"] > 0.5]
auroc_after_05 = [r["AUROC"] for r in weights_after_05]
auroc_at_05 = next(r["AUROC"] for r in sweep_rows if r["w_geo"] == 0.5)
still_improving_after_05 = any(a > auroc_at_05 + 0.005 for a in auroc_after_05)

if not gate0_passed:
    classification = "GEO2_BLOCKED"
elif delta_best <= 0.005 or ci_overlap_best_vs_base:
    classification = "GEO2_GEOGRAPHY_NOT_ROBUST"
elif far_at_best > 0.6:
    classification = "GEO2_AUROC_IMPROVES_BUT_FAR_UNACCEPTABLE"
elif len(pareto_front) > 1 and not (pareto_df["w_geo"].iloc[-1] == best_auroc_row["w_geo"]):
    classification = "GEO2_NO_CLEAR_OPTIMUM"
else:
    classification = "GEO2_OPTIMAL_WEIGHT_FOUND"

interpretation = {
    "classification": classification,
    "gate0_passed": gate0_passed,
    "baseline_w0": baseline_row,
    "best_auroc_row": best_auroc_row,
    "delta_auroc_best_vs_baseline": delta_best,
    "ci_overlap_best_vs_baseline": ci_overlap_best_vs_base,
    "pareto_front_weights": pareto_df["w_geo"].tolist(),
    "still_improving_after_w05": still_improving_after_05,
    "far_at_best_auroc": far_at_best,
    "far_baseline": far_baseline,
}
with open(OUT / "GEO2_INTERPRETATION.json", "w", encoding="utf-8") as f:
    json.dump(interpretation, f, indent=2, ensure_ascii=False, default=str)

print("\nCLASSIFICATION:", classification)
print("BEST AUROC ROW:", best_auroc_row)
print("BASELINE (w=0):", baseline_row)
print("PARETO FRONT weights:", pareto_df["w_geo"].tolist())
print("\nDONE.")
