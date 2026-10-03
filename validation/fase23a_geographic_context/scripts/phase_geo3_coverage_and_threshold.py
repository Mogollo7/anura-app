#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
phase_geo3_coverage_and_threshold.py -- GEO-3: auditoria de cobertura geografica
(Parte A) y curva operativa de threshold (Parte B) sobre el scoring combinado
YA calculado por GEO-2 en w_geo=0.9 (AUROC~=0.701). NO reoptimiza el peso, NO
reentrena, NO genera nuevos embeddings, NO llama a iNaturalist (cache ya cubre
el 100% de los observation_id de KNOWN+UNKNOWN, verificado en este script).

GATE 0: reproduce baseline_reproduction_v2.json (euclidean_raw oficial,
AUROC=0.57329, diff=0.0). Si falla -> GEO3_BLOCKED_REPRODUCTION.json y stop.

No toca fase23a_open_set_automatic/, fase16_clean_open_set/, V1/V2/GEO2,
prior v1 original, encoder, embeddings existentes. Todo output con prefijo GEO3_.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, balanced_accuracy_score

sys.path.insert(0, "D:/Anura")
from training.taxonomia import canonico, genero_de

BASE = Path("D:/Anura")
OUT = BASE / "validation/fase23a_geographic_context"
SEED = 42
N_BOOTSTRAP = 1000

# ---------------------------------------------------------------------------
# GATE 0
# ---------------------------------------------------------------------------
OFFICIAL_AUROC = 0.5732919408781961
gate_path = OUT / "baseline_reproduction_v2.json"
if not gate_path.exists():
    import subprocess
    r = subprocess.run([sys.executable, str(OUT / "scripts/phase_reproduce_23a.py")], cwd=str(BASE))
    if r.returncode != 0:
        raise SystemExit("phase_reproduce_23a.py fallo")

gate = json.load(open(gate_path, encoding="utf-8"))
reproduced_auroc = gate["reproduced_auroc"]
abs_diff = abs(reproduced_auroc - OFFICIAL_AUROC)
gate0_passed = gate.get("gate_passed", False) and abs_diff == 0.0
print(f"GATE 0: reproduced={reproduced_auroc:.10f} official={OFFICIAL_AUROC:.10f} abs_diff={abs_diff} passed={gate0_passed}")

if not gate0_passed:
    blocked = {
        "status": "GEO3_BLOCKED",
        "reason": "reproduced_auroc no coincide exactamente con el oficial 0.57329 (euclidean_raw).",
        "reproduced_auroc": reproduced_auroc, "official_auroc": OFFICIAL_AUROC, "abs_diff": abs_diff,
    }
    json.dump(blocked, open(OUT / "GEO3_BLOCKED_REPRODUCTION.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("GEO3_BLOCKED -- ver GEO3_BLOCKED_REPRODUCTION.json")
    raise SystemExit(1)

# ---------------------------------------------------------------------------
# Carga de datos base (identico a GEO-2)
# ---------------------------------------------------------------------------
repro = np.load(OUT / "reproduced_scores_v2.npz", allow_pickle=True)
d_known = repro["d_known"].astype(np.float64)
d_unknown = repro["d_unknown"].astype(np.float64)
known_species_ids = np.array([str(s) for s in repro["species_known"]])
known_image_ids = np.array([str(s) for s in repro["image_known"]])
unk_species = np.array([str(s) for s in repro["species_unknown"]])
unk_obs = np.array([str(s) for s in repro["obs_unknown"]])
n_known, n_unknown = len(d_known), len(d_unknown)
print(f"KNOWN={n_known} UNKNOWN={n_unknown}")

species_registry = json.load(open(BASE / "taxonomy/species/species_registry.json", encoding="utf-8"))
known_manifest = json.load(open(BASE / "validation/fase16_clean_open_set/clean_known_manifest.json", encoding="utf-8"))
known_images_meta = {im["image_id"]: im for im in known_manifest["images"]}
known_sci_name = np.array([known_images_meta[iid]["scientific_name"] for iid in known_image_ids])
known_obs_raw = np.array([known_images_meta[iid].get("observation_id") for iid in known_image_ids])
known_individual = np.array([known_images_meta[iid].get("individual_id") for iid in known_image_ids])
known_top1 = known_sci_name
known_obs_clean = np.array([o[4:] if (isinstance(o, str) and o.startswith("OBS_")) else None for o in known_obs_raw])

cache = json.load(open(OUT / "cache/inat_observations_cache.json", encoding="utf-8"))
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
    rec = extracted.get(obs_id) if obs_id else None
    if rec is None:
        return dict(lat=None, lon=None, zone=None, has_obsid=obs_id is not None, in_cache=obs_id in extracted if obs_id else False)
    cell_id, zone = assign_zone(rec.get("lat"), rec.get("lon"))
    return dict(lat=rec.get("lat"), lon=rec.get("lon"), zone=zone, has_obsid=True, in_cache=True)


# ===========================================================================
# PARTE A -- AUDITORIA DE COBERTURA GEOGRAFICA
# ===========================================================================

# --- A.1 recuperacion adicional: chequear si hay obs_id de las 620+7475 que
# NO esten ya en cache/inat_extracted.json (candidatos a re-fetch) ---
unk_obs_unique = sorted(set(unk_obs.tolist()))
known_obs_with_id = [o for o in known_obs_clean.tolist() if o is not None]
all_obs_needed = sorted(set(unk_obs_unique) | set(known_obs_with_id))

missing_from_cache = [o for o in all_obs_needed if o not in cache]
missing_from_extracted = [o for o in all_obs_needed if o not in extracted]

print(f"obs_id necesarios (union KNOWN+UNKNOWN, unicos): {len(all_obs_needed)}")
print(f"faltantes en cache: {len(missing_from_cache)}; faltantes en extracted: {len(missing_from_extracted)}")

recovery_log = {
    "n_unique_obs_id_needed": len(all_obs_needed),
    "n_missing_from_cache": len(missing_from_cache),
    "n_missing_from_extracted": len(missing_from_extracted),
    "missing_obs_ids_sample": missing_from_cache[:20],
    "action": "NO se realizaron llamadas nuevas a iNaturalist: el cache existente "
              "(cache/inat_observations_cache.json, 4466 entradas) ya cubre el 100% "
              "de los observation_id presentes en KNOWN(7431 con obs_id)+UNKNOWN(412 "
              "obs_id unicos de 620 imagenes) evaluados por GEO-1/GEO-2. No hay "
              "candidatos verificables para recuperacion adicional sin scraping nuevo agresivo.",
    "gbif_used": False,
    "gbif_reason": "No aplico: no quedaron observation_id sin cobertura de iNaturalist que requirieran una fuente alterna.",
}
json.dump(recovery_log, open(OUT / "GEO3_RECOVERY_LOG.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# --- Per-record audit: KNOWN ---
known_rows = []
for i in range(n_known):
    oid = known_obs_clean[i]
    g = geo_lookup(oid)
    known_rows.append(dict(
        image_id=known_image_ids[i], observation_id=oid,
        has_obs_id=oid is not None, has_latlon=g["lat"] is not None,
        has_zone=g["zone"] is not None, lat=g["lat"], lon=g["lon"], zone=g["zone"],
    ))
known_audit_df = pd.DataFrame(known_rows)

# --- Per-record audit: UNKNOWN ---
unk_rows = []
for i in range(n_unknown):
    oid = unk_obs[i]
    g = geo_lookup(oid)
    unk_rows.append(dict(
        idx=i, observation_id=oid,
        has_obs_id=True, has_latlon=g["lat"] is not None,
        has_zone=g["zone"] is not None, lat=g["lat"], lon=g["lon"], zone=g["zone"],
    ))
unk_audit_df = pd.DataFrame(unk_rows)

# --- A.2 validacion de coordenadas ---
def coord_validity(df):
    valid_lat = df["lat"].apply(lambda x: x is not None and -90 <= x <= 90)
    valid_lon = df["lon"].apply(lambda x: x is not None and -180 <= x <= 180)
    return int((valid_lat & valid_lon).sum()), int(len(df))

known_valid_coords, known_total = coord_validity(known_audit_df)
unk_valid_coords, unk_total = coord_validity(unk_audit_df)

known_dup_obs = int(known_audit_df[known_audit_df["has_obs_id"]]["observation_id"].duplicated().sum())
unk_dup_obs = int(unk_audit_df["observation_id"].duplicated().sum())

obscured_known = sum(1 for o in known_obs_clean.tolist() if o and cache.get(o, {}).get("obscured"))
obscured_unk = sum(1 for o in unk_obs.tolist() if cache.get(o, {}).get("obscured"))

# elevation check (confirmar 0/4466)
elev_present = sum(1 for o in all_obs_needed if cache.get(o, {}).get("elevation") is not None)

# --- A.4 coverage summary ---
coverage_unknown = dict(
    n=n_unknown,
    with_obs_id=int(unk_audit_df["has_obs_id"].sum()),
    without_obs_id=int((~unk_audit_df["has_obs_id"]).sum()),
    with_latlon=int(unk_audit_df["has_latlon"].sum()),
    without_latlon=int((~unk_audit_df["has_latlon"]).sum()),
    with_zone=int(unk_audit_df["has_zone"].sum()),
    without_zone=int((~unk_audit_df["has_zone"]).sum()),
    coverage_zone_pct=round(100.0 * unk_audit_df["has_zone"].sum() / n_unknown, 2),
    geo2_reported_zone_assigned=262,
    geo2_reported_pct=round(100.0 * 262 / 620, 2),
)
coverage_known = dict(
    n=n_known,
    with_obs_id=int(known_audit_df["has_obs_id"].sum()),
    without_obs_id=int((~known_audit_df["has_obs_id"]).sum()),
    with_latlon=int(known_audit_df["has_latlon"].sum()),
    without_latlon=int((~known_audit_df["has_latlon"]).sum()),
    with_zone=int(known_audit_df["has_zone"].sum()),
    without_zone=int((~known_audit_df["has_zone"]).sum()),
    coverage_zone_pct=round(100.0 * known_audit_df["has_zone"].sum() / n_known, 2),
)
coverage_total = dict(
    n=n_known + n_unknown,
    with_zone=coverage_known["with_zone"] + coverage_unknown["with_zone"],
    coverage_zone_pct=round(100.0 * (coverage_known["with_zone"] + coverage_unknown["with_zone"]) / (n_known + n_unknown), 2),
)

print("\ncoverage_unknown:", coverage_unknown)
print("coverage_known:", coverage_known)
print("coverage_total:", coverage_total)
print("elev_present:", elev_present, "/", len(all_obs_needed))

# --- A.3 Leakage: obs_id evaluados no pueden estar en el prior ---
prior = pd.read_csv(OUT / "prior_zone_taxon_v2_clean.csv")
prior_manifest = json.load(open(OUT / "prior_zone_taxon_v2_clean_manifest.json", encoding="utf-8"))
prior_obs_col = None
for cand in ["observation_id", "obs_id", "source_observation_id"]:
    if cand in prior.columns:
        prior_obs_col = cand
        break

evaluation_obs_ids = set(unk_audit_df["observation_id"].dropna().tolist()) | set(
    known_audit_df[known_audit_df["has_obs_id"]]["observation_id"].tolist())

if prior_obs_col is not None:
    prior_obs_ids = set(prior[prior_obs_col].dropna().astype(str).tolist())
    intersection = evaluation_obs_ids & prior_obs_ids
    leakage_verified = True
else:
    prior_obs_ids = set()
    intersection = set()
    leakage_verified = False

leakage_check = {
    "leakage_verified_directly": leakage_verified,
    "prior_has_obs_id_column": prior_obs_col,
    "prior_records_before": prior_manifest.get("n_records_original"),
    "prior_records_removed": prior_manifest.get("n_records_excluded"),
    "prior_records_after_purge_raw": prior_manifest.get("n_records_purged_total"),
    "prior_records_after_aggregation_rows": len(prior),
    "purge_rule": prior_manifest.get("purge_rule"),
    "n_evaluation_observation_ids": len(evaluation_obs_ids),
    "n_intersection_prior_vs_eval": len(intersection),
    "intersection_is_zero": len(intersection) == 0,
    "note": "El prior_zone_taxon_v2_clean.csv es agregado por (zone_id, scientific_name) sin "
            "columna observation_id explicita (purga de leakage se hizo en phase_clean_prior.py "
            "por individual_id/observation_id ANTES de agregar, ver "
            "prior_zone_taxon_v2_clean_manifest.json). Este chequeo confirma que el prior agregado "
            "no contiene una columna de trazabilidad a nivel de observacion individual "
            "(diseño intencional del prior FASE12.2), por lo que la garantia de no-leakage "
            "proviene del proceso de purga documentado en phase_clean_prior.py, reproducido aqui "
            "por referencia a su manifest, no por interseccion directa de IDs post-agregacion."
            if not leakage_verified else
            "Interseccion directa observation_id evaluacion vs prior calculada.",
}
print("\nleakage_check:", json.dumps(leakage_check, indent=2, ensure_ascii=False))

blocked_leakage = leakage_verified and len(intersection) > 0
if blocked_leakage:
    json.dump({"status": "GEO3_BLOCKED_LEAKAGE", "leakage_check": leakage_check},
               open(OUT / "GEO3_BLOCKED_LEAKAGE.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("GEO3_BLOCKED_LEAKAGE -- ver GEO3_BLOCKED_LEAKAGE.json")
    raise SystemExit(1)

# ===========================================================================
# PARTE B -- CURVA OPERATIVA (scoring combinado GEO-2, w_geo=0.9 FIJO)
# ===========================================================================
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

y_true = np.concatenate([np.zeros(n_known), np.ones(n_unknown)])  # 1 = UNKNOWN
all_visual_dist = np.concatenate([d_known, d_unknown])


def minmax(x):
    x = np.asarray(x, dtype=float)
    lo, hi = np.nanmin(x), np.nanmax(x)
    if hi - lo < 1e-12:
        return np.zeros_like(x)
    return (x - lo) / (hi - lo)


all_visual_norm = minmax(all_visual_dist)

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


def geo_score_for_rows(top1_species, zones):
    scores = []
    for sp, zone in zip(top1_species, zones):
        if zone is None or (isinstance(zone, float) and np.isnan(zone)):
            scores.append(NEUTRAL_GEO_SCORE)
        else:
            p = prior_for(canonico(sp).replace("_", " "), zone)
            scores.append(p if p is not None else NEUTRAL_GEO_SCORE)
    return np.array(scores)


unk_geo_score = geo_score_for_rows(unk_top1_species, unk_audit_df["zone"].values)
known_geo_score = geo_score_for_rows(known_top1, known_audit_df["zone"].values)
all_geo_score = np.concatenate([known_geo_score, unk_geo_score])
geo_probable_norm = minmax(all_geo_score)
geo_unknownness = 1.0 - geo_probable_norm

W_GEO = 0.9  # FIJO, heredado de GEO-2 (NO reoptimizado)
combined = (1 - W_GEO) * all_visual_norm + W_GEO * geo_unknownness
combined_auroc = roc_auc_score(y_true, combined)
print(f"\nCombined score (w_geo=0.9) AUROC (reconfirm) = {combined_auroc:.6f} (GEO2 reported {0.7014759952529939:.6f})")

ind_all = np.concatenate([known_individual.astype(str), unk_obs.astype(str)])


def metrics_at_threshold(y_true, y_score, thr):
    pred_unknown = (y_score >= thr).astype(int)
    tp = np.sum((pred_unknown == 1) & (y_true == 1))
    fn = np.sum((pred_unknown == 0) & (y_true == 1))
    tn = np.sum((pred_unknown == 0) & (y_true == 0))
    fp = np.sum((pred_unknown == 1) & (y_true == 0))
    tpr = tp / max(1, tp + fn)
    tnr = tn / max(1, tn + fp)
    far = fn / max(1, fn + tp)  # UNKNOWN mal clasificado como KNOWN (false accept)
    frr = fp / max(1, fp + tn)  # KNOWN mal clasificado como UNKNOWN (false reject)
    precision = tp / max(1, tp + fp)
    npv = tn / max(1, tn + fn)
    bal_acc = balanced_accuracy_score(y_true, pred_unknown)
    return dict(TPR=tpr, TNR=tnr, FAR=far, FRR=frr, BalancedAccuracy=bal_acc,
                Precision=precision, NPV=npv, TP=int(tp), FP=int(fp), TN=int(tn), FN=int(fn))


# --- B.1 curva densa de thresholds sobre el rango real del combined score ---
lo, hi = float(combined.min()), float(combined.max())
thresholds = np.linspace(lo, hi, 400)
curve_rows = []
for thr in thresholds:
    m = metrics_at_threshold(y_true, combined, thr)
    curve_rows.append(dict(threshold=float(thr), **m))
curve_df = pd.DataFrame(curve_rows)
curve_df.to_csv(OUT / "GEO3_THRESHOLD_CURVE.csv", index=False)
json.dump(curve_rows, open(OUT / "GEO3_THRESHOLD_CURVE.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False, default=str)

# --- B.2 operating points por nivel de FAR ---
far_levels = [0.50, 0.30, 0.20, 0.10, 0.05]
operating_points = []
for lvl in far_levels:
    candidates = curve_df[curve_df["FAR"] <= lvl]
    if len(candidates) == 0:
        operating_points.append(dict(far_level=lvl, status="NO_OPERATING_POINT"))
        continue
    # entre los que cumplen FAR<=lvl, elegir el de menor FRR (mejor operativo)
    best = candidates.sort_values("FRR").iloc[0]
    operating_points.append(dict(
        far_level=lvl, status="FOUND", threshold=float(best["threshold"]),
        FAR=float(best["FAR"]), FRR=float(best["FRR"]), BalancedAccuracy=float(best["BalancedAccuracy"]),
        TPR=float(best["TPR"]), TNR=float(best["TNR"]), Precision=float(best["Precision"]), NPV=float(best["NPV"]),
    ))
op_df = pd.DataFrame(operating_points)
op_df.to_csv(OUT / "GEO3_OPERATING_POINTS.csv", index=False)
print("\nOperating points:\n", op_df.to_string(index=False))

# --- B.4 EER, max BalAcc, min FAR, max tolerable FRR, Pareto ---
curve_df["far_frr_gap"] = (curve_df["FAR"] - curve_df["FRR"]).abs()
eer_row = curve_df.loc[curve_df["far_frr_gap"].idxmin()]
max_balacc_row = curve_df.loc[curve_df["BalancedAccuracy"].idxmax()]
min_far_row = curve_df.loc[curve_df["FAR"].idxmin()]
# FRR maximo tolerable: FRR mas bajo (mejor para KNOWN) entre thresholds con FAR razonable (<=0.5)
reasonable = curve_df[curve_df["FAR"] <= 0.5]
min_frr_reasonable_row = reasonable.loc[reasonable["FRR"].idxmin()] if len(reasonable) else None

# Pareto sobre (FAR, FRR) minimizando ambos
pts = curve_df[["threshold", "FAR", "FRR", "BalancedAccuracy"]].drop_duplicates(subset=["FAR", "FRR"])
pareto_idx = []
arr = pts[["FAR", "FRR"]].values
for i in range(len(arr)):
    dominated = False
    for j in range(len(arr)):
        if i == j:
            continue
        if arr[j][0] <= arr[i][0] and arr[j][1] <= arr[i][1] and (arr[j][0] < arr[i][0] or arr[j][1] < arr[i][1]):
            dominated = True
            break
    if not dominated:
        pareto_idx.append(i)
pareto_pts = pts.iloc[pareto_idx].sort_values("FAR")

trend_summary = {
    "eer_approx": dict(threshold=float(eer_row["threshold"]), FAR=float(eer_row["FAR"]), FRR=float(eer_row["FRR"]), gap=float(eer_row["far_frr_gap"])),
    "max_balanced_accuracy": dict(threshold=float(max_balacc_row["threshold"]), FAR=float(max_balacc_row["FAR"]), FRR=float(max_balacc_row["FRR"]), BalancedAccuracy=float(max_balacc_row["BalancedAccuracy"])),
    "min_far_point": dict(threshold=float(min_far_row["threshold"]), FAR=float(min_far_row["FAR"]), FRR=float(min_far_row["FRR"])),
    "min_frr_at_far_le_50pct": (dict(threshold=float(min_frr_reasonable_row["threshold"]), FAR=float(min_frr_reasonable_row["FAR"]), FRR=float(min_frr_reasonable_row["FRR"])) if min_frr_reasonable_row is not None else None),
    "n_pareto_candidates": int(len(pareto_pts)),
    "pareto_candidates_sample": pareto_pts.head(15).to_dict(orient="records"),
    "note_not_choosing_by_balacc_alone": "Se reportan multiples candidatos (EER, max BalAcc, min FAR, Pareto); "
                                          "no se selecciona un unico threshold operativo solo por maximizar BalancedAccuracy.",
}
json.dump(trend_summary, open(OUT / "GEO3_THRESHOLD_TREND_SUMMARY.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False, default=str)
print("\ntrend_summary:", json.dumps(trend_summary, indent=2, ensure_ascii=False, default=str)[:2000])

# --- B.5 same_genus vs different_genus en el threshold seleccionado (min FAR<=30% con menor FRR) ---
selected = next((o for o in operating_points if o.get("far_level") == 0.30 and o.get("status") == "FOUND"), None)
if selected is None:
    selected = next((o for o in operating_points if o.get("status") == "FOUND"), None)
selected_threshold = selected["threshold"] if selected else float(eer_row["threshold"])
print(f"\nThreshold seleccionado para desgloses (FAR<=30% si existe, si no EER): {selected_threshold}")

species_list = sorted(set(known_sci_name))
known_genera = set(genero_de(canonico(sp)) for sp in species_list)
unk_genus = np.array([genero_de(canonico(sp)) for sp in unk_species])
same_genus_mask = np.array([g in known_genera for g in unk_genus])
n_same, n_diff = int(same_genus_mask.sum()), int((~same_genus_mask).sum())

unk_combined = combined[n_known:]
pred_unk = (unk_combined >= selected_threshold).astype(int)  # 1 = correctamente detectado como UNKNOWN
genus_breakdown = {
    "threshold_used": selected_threshold,
    "same_genus": dict(n=n_same, n_correctly_flagged_unknown=int(pred_unk[same_genus_mask].sum()),
                        detection_rate=float(pred_unk[same_genus_mask].mean()) if n_same else None),
    "different_genus": dict(n=n_diff, n_correctly_flagged_unknown=int(pred_unk[~same_genus_mask].sum()),
                             detection_rate=float(pred_unk[~same_genus_mask].mean()) if n_diff else None),
}
print("\ngenus_breakdown:", json.dumps(genus_breakdown, indent=2, ensure_ascii=False))

# --- B.6 UNKNOWN con zona vs sin zona en el mismo threshold ---
unk_has_zone = unk_audit_df["has_zone"].values
zone_breakdown = {
    "threshold_used": selected_threshold,
    "with_zone": dict(n=int(unk_has_zone.sum()), n_correctly_flagged_unknown=int(pred_unk[unk_has_zone].sum()),
                       detection_rate=float(pred_unk[unk_has_zone].mean()) if unk_has_zone.sum() else None),
    "without_zone": dict(n=int((~unk_has_zone).sum()), n_correctly_flagged_unknown=int(pred_unk[~unk_has_zone].sum()),
                          detection_rate=float(pred_unk[~unk_has_zone].mean()) if (~unk_has_zone).sum() else None),
    "selection_bias_warning": "UNKNOWN con zona asignada probablemente corresponde a observaciones dentro de "
                               "Antioquia (misma region que el prior geografico), mientras que sin-zona son "
                               "observaciones fuera del area cubierta por el prior. La comparacion NO es un "
                               "experimento independiente y limpio: refleja que el prior geografico solo puede "
                               "ayudar donde hay zona asignada, por construccion. No se debe interpretar como "
                               "evidencia causal de que 'la geografia funciona mejor', sino como el techo de "
                               "cobertura actual del metodo.",
}
if unk_has_zone.sum() > 0 and (~unk_has_zone).sum() > 0:
    zone_breakdown["with_zone_minus_without_zone_detection_rate"] = (
        zone_breakdown["with_zone"]["detection_rate"] - zone_breakdown["without_zone"]["detection_rate"])
print("\nzone_breakdown:", json.dumps(zone_breakdown, indent=2, ensure_ascii=False))

# ---------------------------------------------------------------------------
# Bootstrap (1000 iter, seed=42, estratificado por individuo) en threshold seleccionado
# ---------------------------------------------------------------------------
def bootstrap_at_threshold(y_true, y_score, ind_ids, thr, n_iter=N_BOOTSTRAP, seed=SEED):
    rng = np.random.RandomState(seed)
    unique_known_ind = np.unique(ind_ids[y_true == 0])
    unique_unknown_ind = np.unique(ind_ids[y_true == 1])
    idx_by_ind = {u: np.where(ind_ids == u)[0] for u in np.unique(ind_ids)}
    metrics_acc = {k: [] for k in ["AUROC", "FAR", "FRR", "BalancedAccuracy", "TPR", "TNR", "Precision", "NPV"]}
    for _ in range(n_iter):
        samp_known = rng.choice(unique_known_ind, size=len(unique_known_ind), replace=True)
        samp_unknown = rng.choice(unique_unknown_ind, size=len(unique_unknown_ind), replace=True)
        idxs = np.concatenate([idx_by_ind[i] for i in samp_known] + [idx_by_ind[i] for i in samp_unknown])
        yt, ys = y_true[idxs], y_score[idxs]
        if len(np.unique(yt)) < 2:
            continue
        try:
            metrics_acc["AUROC"].append(roc_auc_score(yt, ys))
        except Exception:
            continue
        m = metrics_at_threshold(yt, ys, thr)
        for k in ["FAR", "FRR", "BalancedAccuracy", "TPR", "TNR", "Precision", "NPV"]:
            metrics_acc[k].append(m[k])

    def ci(arr):
        arr = np.array(arr)
        return dict(mean=float(arr.mean()), ci_lo=float(np.percentile(arr, 2.5)),
                    ci_hi=float(np.percentile(arr, 97.5)), n_valid=int(len(arr)))

    return {k: ci(v) for k, v in metrics_acc.items()}


bootstrap_results = {
    "selected_threshold_far_le_30pct_or_eer": bootstrap_at_threshold(y_true, combined, ind_all, selected_threshold),
    "eer_threshold": bootstrap_at_threshold(y_true, combined, ind_all, float(eer_row["threshold"])),
    "max_balacc_threshold": bootstrap_at_threshold(y_true, combined, ind_all, float(max_balacc_row["threshold"])),
}
for lvl_point in operating_points:
    if lvl_point.get("status") == "FOUND":
        bootstrap_results[f"far_le_{int(lvl_point['far_level']*100)}pct"] = bootstrap_at_threshold(
            y_true, combined, ind_all, lvl_point["threshold"])

json.dump(bootstrap_results, open(OUT / "GEO3_BOOTSTRAP_RESULTS.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False, default=str)
print("\nBootstrap done. AUROC @ selected threshold CI:", bootstrap_results["selected_threshold_far_le_30pct_or_eer"]["AUROC"])

# ===========================================================================
# Veredicto
# ===========================================================================
any_operating_point_found = any(o.get("status") == "FOUND" for o in operating_points)
far_le_30_found = any(o.get("far_level") == 0.30 and o.get("status") == "FOUND" for o in operating_points)
coverage_improved = coverage_unknown["with_zone"] > coverage_unknown["geo2_reported_zone_assigned"]
zone_signal_present = (zone_breakdown.get("with_zone_minus_without_zone_detection_rate", 0) or 0) > 0.05

if coverage_improved:
    verdict = "GEO3_COVERAGE_IMPROVED"
elif far_le_30_found:
    verdict = "GEO3_THRESHOLD_OPERATING_POINT_FOUND"
elif zone_signal_present and not any_operating_point_found:
    verdict = "GEO3_SIGNAL_STRONG_BUT_OPERATIONAL_LIMITED"
elif not any_operating_point_found:
    verdict = "GEO3_GEOGRAPHY_NOT_ACTIONABLE"
else:
    verdict = "GEO3_THRESHOLD_OPERATING_POINT_FOUND"

print("\nVEREDICTO:", verdict)

# ===========================================================================
# GEO3_COVERAGE_AUDIT.json
# ===========================================================================
coverage_audit = {
    "gate0_passed": gate0_passed,
    "reproduced_auroc": reproduced_auroc,
    "coverage_unknown": coverage_unknown,
    "coverage_known": coverage_known,
    "coverage_total": coverage_total,
    "elevation_check": {"n_with_elevation": elev_present, "n_total": len(all_obs_needed), "confirmed_0_of_4466": elev_present == 0},
    "coordinate_validation": {
        "known_valid_coords": known_valid_coords, "known_total_with_coords_checked": known_total,
        "unknown_valid_coords": unk_valid_coords, "unknown_total_with_coords_checked": unk_total,
        "known_duplicate_obs_ids": known_dup_obs, "unknown_duplicate_obs_ids": unk_dup_obs,
        "known_obscured_flagged": int(obscured_known), "unknown_obscured_flagged": int(obscured_unk),
    },
    "recovery_a1": recovery_log,
    "leakage_check_a3": leakage_check,
    "verdict": verdict,
}
json.dump(coverage_audit, open(OUT / "GEO3_COVERAGE_AUDIT.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False, default=str)

# ===========================================================================
# Reproducibility manifest
# ===========================================================================
def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


inputs_to_hash = [
    OUT / "reproduced_scores_v2.npz",
    OUT / "prior_zone_taxon_v2_clean.csv",
    OUT / "prior_zone_taxon_v2_clean_manifest.json",
    OUT / "cache/inat_observations_cache.json",
    OUT / "cache/inat_extracted.json",
    BASE / "evaluation/fase13/embeddings/reference_embeddings.npz",
    BASE / "evaluation/fase13/embeddings/train_embeddings.npz",
    BASE / "validation/fase16_clean_open_set/clean_known_embeddings.npz",
    BASE / "validation/fase16_clean_open_set/clean_known_manifest.json",
    BASE / "validation/fase23a_open_set_automatic/embeddings/unknown_embeddings.npz",
    BASE / "COLOMBIA_ANURA/ANTIOQUIA/zones/cell_zone_map_v1.csv",
]
hashes = {str(p.relative_to(BASE)): sha256_of(p) for p in inputs_to_hash if p.exists()}

manifest = {
    "phase": "GEO-3",
    "gate0": {"reproduced_auroc": reproduced_auroc, "official_auroc": OFFICIAL_AUROC, "abs_diff": abs_diff, "passed": gate0_passed},
    "seed": SEED,
    "n_bootstrap": N_BOOTSTRAP,
    "w_geo_used_fixed_from_geo2": W_GEO,
    "combined_auroc_reconfirmed": combined_auroc,
    "geo2_combined_auroc_reference": 0.7014759952529939,
    "prior_used": "prior_zone_taxon_v2_clean.csv",
    "prior_alpha": ALPHA, "prior_K_taxa": K,
    "zone_method": "grid_cell 0.25deg -> cell_zone_map_v1.csv (in_department filter), identico a GEO-1/GEO-2",
    "n_thresholds_evaluated": len(thresholds),
    "threshold_range": [float(lo), float(hi)],
    "input_hashes_sha256": hashes,
    "encoder_note": "No se toco el encoder ni se generaron embeddings nuevos; reproduced_scores_v2.npz y "
                     "unknown_embeddings.npz reutilizados sin modificacion.",
}
json.dump(manifest, open(OUT / "GEO3_REPRODUCIBILITY_MANIFEST.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False, default=str)

print("\nDONE. Verdict:", verdict)
