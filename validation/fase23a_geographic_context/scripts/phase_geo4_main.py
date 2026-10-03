#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
phase_geo4_main.py -- GEO-4 FASE A, PASO 0 (gate) + PASO 2 (formula jerarquica) +
PASO 3 (precision de especie, Top-1/Top-3/F1) + PASO 4 (impacto en Open Set A/B/C).

Reutiliza EXACTAMENTE:
  - reproduced_scores_v2.npz / baseline_reproduction_v2.json (gate visual puro)
  - prior_zone_taxon_v2_clean.csv (prior especie|zona, purgado de leakage)
  - cache/inat_extracted.json (coordenadas ya recuperadas, sin llamadas nuevas)
  - COLOMBIA_ANURA/ANTIOQUIA/zones/cell_zone_map_v1.csv (geometria de zonas congelada)
  - clean_known_manifest.json / clean_known_embeddings.npz (KNOWN pool, 24 especies)
  - evaluation/fase13/embeddings/{reference,train}_embeddings.npz (centroides 41 especies)
  - validation/fase23a_open_set_automatic/embeddings/unknown_embeddings.npz (620 UNKNOWN)
  - training/taxonomia.py (genero_de/familia_de/canonico) para el desglose same/diff genus
  - COLOMBIA_ANURA/ANTIOQUIA/catalog/catalog_v1.json (genus/family por taxon_id, fuente para
    los priors jerarquicos nuevos de GEO4, mas amplia que taxonomia.py que solo cubre 41 spp)

Construye (nuevo, prefijo GEO4_):
  prior_zone_genus_v1.csv / prior_zone_family_v1.csv -- ya generados por
  phase_geo4_hierarchical_priors.py (PASO 1), este script solo los consume.

No toca produccion, GEO2_*/GEO3_* existentes, priors v1 originales, encoder, embeddings
oficiales. No fine-tuning, no nuevos embeddings, no llamadas API nuevas.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, balanced_accuracy_score, f1_score

sys.path.insert(0, "D:/Anura")
from training.taxonomia import canonico, genero_de, familia_de

BASE = Path("D:/Anura")
OUT = BASE / "validation/fase23a_geographic_context"
SEED = 42
OFFICIAL_AUROC = 0.5732919408781961

# ---------------------------------------------------------------------------
# GATE 0
# ---------------------------------------------------------------------------
gate = json.load(open(OUT / "baseline_reproduction_v2.json", encoding="utf-8"))
reproduced_auroc = gate["reproduced_auroc"]
abs_diff = abs(reproduced_auroc - OFFICIAL_AUROC)
gate0_passed = gate.get("gate_passed", False) and abs_diff == 0.0
print(f"GATE 0: reproduced={reproduced_auroc:.10f} official={OFFICIAL_AUROC:.10f} diff={abs_diff} passed={gate0_passed}")
if not gate0_passed:
    json.dump({"status": "GEO4_BLOCKED", "reason": "gate0 failed", "gate": gate},
               open(OUT / "GEO4_BLOCKED.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    raise SystemExit(1)

# ---------------------------------------------------------------------------
# 1. Centroides 41 especies + KNOWN pool completo (matriz de distancias) + UNKNOWN
# ---------------------------------------------------------------------------
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
classes = sorted(all_41_centroids.keys())  # 41 scientific names, space-separated
C = np.array([all_41_centroids[c] for c in classes])
n_classes = len(classes)
assert n_classes == 41

known_npz = np.load(BASE / "validation/fase16_clean_open_set/clean_known_embeddings.npz", allow_pickle=True)
X_known = known_npz["embeddings"].astype(np.float64)
known_species_ids = np.array([str(s) for s in known_npz["species_ids"]])
known_image_ids = np.array([str(s) for s in known_npz["image_ids"]])
n_known = len(X_known)

unk_npz = np.load(BASE / "validation/fase23a_open_set_automatic/embeddings/unknown_embeddings.npz", allow_pickle=True)
X_unknown = unk_npz["embeddings"].astype(np.float64)
unk_species = np.array([str(s) for s in unk_npz["species"]])
unk_obs = np.array([str(s) for s in unk_npz["observation_id"]])
n_unknown = len(X_unknown)

# full distance matrices to all 41 centroids (KNOWN needed for ranking; UNKNOWN for gate reuse)
d_known_full = np.linalg.norm(X_known[:, None, :] - C[None, :, :], axis=2)   # (n_known, 41)
d_unknown_full = np.linalg.norm(X_unknown[:, None, :] - C[None, :, :], axis=2)  # (n_unknown, 41)
d_known_top1 = d_known_full.min(axis=1)
d_unknown_top1 = d_unknown_full.min(axis=1)

# sanity vs persisted gate scores (reproduced_scores_v2.npz), same order guaranteed by same source files
repro = np.load(OUT / "reproduced_scores_v2.npz", allow_pickle=True)
assert np.allclose(d_known_top1, repro["d_known"].astype(np.float64), atol=1e-4), "KNOWN top1 mismatch vs gate"
assert np.allclose(d_unknown_top1, repro["d_unknown"].astype(np.float64), atol=1e-4), "UNKNOWN top1 mismatch vs gate"
print(f"KNOWN={n_known} UNKNOWN={n_unknown} classes={n_classes}  (matches gate scores exactly)")

# ---------------------------------------------------------------------------
# 2. Metadata: manifest KNOWN (24 species, coords via obs) + genero/familia por especie
# ---------------------------------------------------------------------------
known_manifest = json.load(open(BASE / "validation/fase16_clean_open_set/clean_known_manifest.json", encoding="utf-8"))
known_images_meta = {im["image_id"]: im for im in known_manifest["images"]}
known_sci_name = np.array([known_images_meta[iid]["scientific_name"] for iid in known_image_ids])
known_obs = np.array([known_images_meta[iid].get("observation_id") for iid in known_image_ids])
known_individual = np.array([known_images_meta[iid].get("individual_id") for iid in known_image_ids])
species24 = sorted(set(known_sci_name))
assert len(species24) == 24, len(species24)
print(f"KNOWN 24 species (truth labels): {len(species24)}")

# genero/familia por cada una de las 41 clases candidatas, via training/taxonomia.py
class_genus = {}
class_family = {}
for sp in classes:
    sp_us = canonico(sp)
    class_genus[sp] = genero_de(sp_us)
    try:
        class_family[sp] = familia_de(sp_us)
    except KeyError:
        class_family[sp] = None
missing_family = [sp for sp in classes if class_family[sp] is None]
print(f"Classes without family in taxonomia.py: {missing_family}")

# ---------------------------------------------------------------------------
# 3. Zonas geograficas (identico a GEO2/GEO3: cache existente, sin llamadas nuevas)
# ---------------------------------------------------------------------------
extracted = json.load(open(OUT / "cache/inat_extracted.json", encoding="utf-8"))
cell_zone = pd.read_csv(BASE / "COLOMBIA_ANURA/ANTIOQUIA/zones/cell_zone_map_v1.csv")
cell_zone_map = dict(zip(cell_zone["cell_id"], cell_zone["zone_final"]))
valid_cells = set(cell_zone[cell_zone["in_department"] == True]["cell_id"])


def assign_zone(lat, lon):
    if lat is None or lon is None:
        return None
    row = int(round(lat / 0.25))
    col = int(round(lon / 0.25))
    cell_id = f"G025_{row}_{col}"
    if cell_id in valid_cells:
        return cell_zone_map.get(cell_id)
    return None


def zone_for_obs(obs_id):
    rec = extracted.get(obs_id)
    if rec is None:
        return None
    return assign_zone(rec.get("lat"), rec.get("lon"))


unk_zone = np.array([zone_for_obs(o) for o in unk_obs])
known_obs_clean = [o[4:] if (o and o.startswith("OBS_")) else None for o in known_obs]
known_zone = np.array([zone_for_obs(o) if o else None for o in known_obs_clean])
n_known_with_zone = int(sum(z is not None for z in known_zone))
n_unk_with_zone = int(sum(z is not None for z in unk_zone))
print(f"KNOWN with zone assigned: {n_known_with_zone}/{n_known}   UNKNOWN with zone: {n_unk_with_zone}/{n_unknown}")

# ---------------------------------------------------------------------------
# 4. Priors: especie (v2 clean, reutilizado) + genero/familia (GEO4, nuevos)
# ---------------------------------------------------------------------------
prior_sp = pd.read_csv(OUT / "prior_zone_taxon_v2_clean.csv")
prior_sp_manifest = json.load(open(OUT / "prior_zone_taxon_v2_clean_manifest.json", encoding="utf-8"))
ALPHA_SP, K_SP = prior_sp_manifest["alpha_selected"], prior_sp_manifest["K_taxa"]
prior_sp_lookup = {(r["zone_id"], r["scientific_name"]): (float(r["p"]), float(r["n_effective"])) for _, r in prior_sp.iterrows()}
n_eff_zone_sp = prior_sp.groupby("zone_id")["n_effective"].sum().to_dict()

prior_ge = pd.read_csv(OUT / "prior_zone_genus_v1.csv")
ge_manifest = json.load(open(OUT / "GEO4_prior_zone_genus_v1_manifest.json", encoding="utf-8"))
ALPHA_GE, K_GE = ge_manifest["alpha_selected"], ge_manifest["K"]
prior_ge_lookup = {(r["zone_id"], r["genus"]): (float(r["p"]), float(r["n_effective"])) for _, r in prior_ge.iterrows()}

prior_fa = pd.read_csv(OUT / "prior_zone_family_v1.csv")
fa_manifest = json.load(open(OUT / "GEO4_prior_zone_family_v1_manifest.json", encoding="utf-8"))
ALPHA_FA, K_FA = fa_manifest["alpha_selected"], fa_manifest["K"]
prior_fa_lookup = {(r["zone_id"], r["family"]): (float(r["p"]), float(r["n_effective"])) for _, r in prior_fa.iterrows()}

NEUTRAL_SP, NEUTRAL_GE, NEUTRAL_FA = 1.0 / K_SP, 1.0 / K_GE, 1.0 / K_FA


def p_species(sp, zone):
    if zone is None:
        return NEUTRAL_SP, 0.0
    key = (zone, canonico(sp).replace("_", " "))
    if key in prior_sp_lookup:
        return prior_sp_lookup[key]
    denom = n_eff_zone_sp.get(zone, 0) + ALPHA_SP * K_SP
    return (ALPHA_SP / denom if denom > 0 else NEUTRAL_SP), 0.0


def p_genus(genus, zone):
    if zone is None or genus is None:
        return NEUTRAL_GE, 0.0
    key = (zone, genus)
    if key in prior_ge_lookup:
        return prior_ge_lookup[key]
    return NEUTRAL_GE, 0.0


def p_family(fam, zone):
    if zone is None or fam is None:
        return NEUTRAL_FA, 0.0
    key = (zone, fam)
    if key in prior_fa_lookup:
        return prior_fa_lookup[key]
    return NEUTRAL_FA, 0.0


# ---------------------------------------------------------------------------
# PASO 2 -- Formula jerarquica con shrinkage (evita doble conteo)
#
# Los tres priors (especie/genero/familia) vienen de LOS MISMOS registros
# geograficos -- no son evidencia independiente, son agregaciones jerarquicas
# de la misma fuente (misma coordenada/observacion). Sumarlos como si fueran 3
# fuentes independientes inflaria artificialmente la señal geografica.
#
# En su lugar: fallback jerarquico con "shrinkage" empirico-Bayes basado en el
# n_effective (evidencia disponible tras el effort-cap) del nivel mas fino:
#   lambda_s = n_eff_species(zone,candidate) / (n_eff_species(zone,candidate) + K_SHRINK)
#   lambda_g = n_eff_genus(zone,candidate)   / (n_eff_genus(zone,candidate)   + K_SHRINK)
# geo_species_component = lambda_s * P_species
# geo_genus_component   = (1-lambda_s) * lambda_g * P_genus
# geo_family_component  = (1-lambda_s) * (1-lambda_g) * P_family
# Estos 3 componentes SUMAN <= la probabilidad total de la jerarquia (no se
# duplican): cuando hay suficiente evidencia de especie en esa zona, lambda_s->1
# y genus/family colapsan a ~0 (no aportan). Cuando la especie tiene poca/ninguna
# evidencia en esa zona (lambda_s->0), el peso migra a genero, y si el genero
# tambien es escaso, a familia. Los pesos w_geo_species/genus/family del PASO 2
# se aplican SOBRE estos componentes ya des-solapados, no sobre las P crudas.
# ---------------------------------------------------------------------------
K_SHRINK = 5.0  # umbral de n_effective para confiar en el nivel mas fino (documentado, no barrido)


def hierarchical_geo_components(sp, zone):
    genus, fam = class_genus.get(sp), class_family.get(sp)
    p_sp, neff_sp = p_species(sp, zone)
    p_ge, neff_ge = p_genus(genus, zone)
    p_fa, neff_fa = p_family(fam, zone)
    lam_s = neff_sp / (neff_sp + K_SHRINK)
    lam_g = neff_ge / (neff_ge + K_SHRINK)
    comp_sp = lam_s * p_sp
    comp_ge = (1 - lam_s) * lam_g * p_ge
    comp_fa = (1 - lam_s) * (1 - lam_g) * p_fa
    return comp_sp, comp_ge, comp_fa, dict(p_sp=p_sp, p_ge=p_ge, p_fa=p_fa, lam_s=lam_s, lam_g=lam_g,
                                            genus=genus, family=fam)


def minmax(x):
    x = np.asarray(x, dtype=float)
    lo, hi = np.nanmin(x), np.nanmax(x)
    if hi - lo < 1e-12:
        return np.zeros_like(x)
    return (x - lo) / (hi - lo)


# Weight proposals: w_geo_total=0.9 (mejor punto GEO2), repartido especie/genero/familia.
WEIGHT_SCHEMES = {
    "B_species_only": dict(w_v=0.10, w_sp=0.90, w_ge=0.00, w_fa=0.00),  # == GEO2 w=0.9 baseline
    "C_main": dict(w_v=0.10, w_sp=0.90 * 0.60, w_ge=0.90 * 0.25, w_fa=0.90 * 0.15),
    "C_alt_species_heavy": dict(w_v=0.10, w_sp=0.90 * 0.80, w_ge=0.90 * 0.15, w_fa=0.90 * 0.05),
    "C_alt_balanced": dict(w_v=0.10, w_sp=0.90 * 0.45, w_ge=0.90 * 0.35, w_fa=0.90 * 0.20),
}

print("\nWeight schemes (sensitivity, max 2-3 as instructed):")
for k, v in WEIGHT_SCHEMES.items():
    print(" ", k, v)

# ---------------------------------------------------------------------------
# PASO 3 -- Precision de especie (ranking Top-k sobre las 41 clases candidatas),
# evaluado sobre las 7475 imagenes KNOWN (24 especies verdad-terreno).
# Nuevo respecto a GEO-1/2/3 (que solo evaluaban Open Set KNOWN-vs-UNKNOWN binario).
# ---------------------------------------------------------------------------
print("\n=== PASO 3: Species precision (ranking) ===")

# visual similarity per row, per-row min-max normalized (documented extension: GEO2/GEO3
# only normalized a single scalar top-1 score globally; ranking Top-k needs a per-query
# distribution over the 41 candidates, so normalization here is per row, consistent in
# direction (higher = more similar) with GEO2's "higher score = more likely known").
visual_sim = -d_known_full  # (n_known, 41), higher = closer
row_min = visual_sim.min(axis=1, keepdims=True)
row_max = visual_sim.max(axis=1, keepdims=True)
visual_sim_norm = (visual_sim - row_min) / np.maximum(row_max - row_min, 1e-12)

# hierarchical geo components per (image, candidate class)
comp_sp_mat = np.zeros((n_known, n_classes))
comp_ge_mat = np.zeros((n_known, n_classes))
comp_fa_mat = np.zeros((n_known, n_classes))
for j, sp in enumerate(classes):
    for i in range(n_known):
        zone = known_zone[i]
        csp, cge, cfa, _ = hierarchical_geo_components(sp, zone)
        comp_sp_mat[i, j] = csp
        comp_ge_mat[i, j] = cge
        comp_fa_mat[i, j] = cfa

# per-row min-max normalize each geo component matrix (same convention as visual)
def rownorm(mat):
    lo = mat.min(axis=1, keepdims=True)
    hi = mat.max(axis=1, keepdims=True)
    return (mat - lo) / np.maximum(hi - lo, 1e-12)


comp_sp_norm = rownorm(comp_sp_mat)
comp_ge_norm = rownorm(comp_ge_mat)
comp_fa_norm = rownorm(comp_fa_mat)

class_idx = {c: i for i, c in enumerate(classes)}
y_true_idx = np.array([class_idx[sp] for sp in known_sci_name])


def rank_metrics(score_mat, label):
    top1_idx = score_mat.argmax(axis=1)
    top1_acc = float((top1_idx == y_true_idx).mean())
    top3_idx = np.argsort(-score_mat, axis=1)[:, :3]
    top3_acc = float(np.mean([y_true_idx[i] in top3_idx[i] for i in range(n_known)]))
    f1_macro = float(f1_score(y_true_idx, top1_idx, average="macro", labels=list(range(n_classes)), zero_division=0))
    print(f"  [{label}] Top-1={top1_acc:.4f}  Top-3={top3_acc:.4f}  F1_macro={f1_macro:.4f}")
    return dict(top1_acc=top1_acc, top3_acc=top3_acc, f1_macro=f1_macro, top1_idx=top1_idx, top3_idx=top3_idx)


score_visual_only = visual_sim_norm
score_visual_geo_species = 0.5 * visual_sim_norm + 0.5 * comp_sp_norm  # simple visual+species-geo baseline (GEO2-style, ranking form)
score_hierarchical_main = (WEIGHT_SCHEMES["C_main"]["w_v"] * visual_sim_norm
                            + WEIGHT_SCHEMES["C_main"]["w_sp"] * comp_sp_norm
                            + WEIGHT_SCHEMES["C_main"]["w_ge"] * comp_ge_norm
                            + WEIGHT_SCHEMES["C_main"]["w_fa"] * comp_fa_norm)

res_visual = rank_metrics(score_visual_only, "visual_only")
res_vg_species = rank_metrics(score_visual_geo_species, "visual+geo_species")
res_hier = rank_metrics(score_hierarchical_main, "visual+geo_species+genus+family (C_main)")

species_precision_metrics = {
    "n_known_images": n_known, "n_species": 24, "n_candidate_classes": n_classes,
    "visual_only": {k: v for k, v in res_visual.items() if k in ("top1_acc", "top3_acc", "f1_macro")},
    "visual_plus_geo_species": {k: v for k, v in res_vg_species.items() if k in ("top1_acc", "top3_acc", "f1_macro")},
    "visual_plus_geo_hierarchical_C_main": {k: v for k, v in res_hier.items() if k in ("top1_acc", "top3_acc", "f1_macro")},
    "weight_scheme_C_main": WEIGHT_SCHEMES["C_main"],
    "note": "Ranking Top-k sobre 41 clases candidatas (centroides), verdad-terreno restringida "
            "a las 24 especies KNOWN de fase16_clean_open_set. Distinto de la decision binaria "
            "Open Set (KNOWN vs UNKNOWN) del PASO 4.",
}
json.dump(species_precision_metrics, open(OUT / "GEO4_species_precision_metrics.json", "w", encoding="utf-8"),
           indent=2, ensure_ascii=False, default=str)

# Confusion matrix (top1, C_main) restricted to true 24-species rows x 41 candidate cols
conf = pd.crosstab(pd.Series([classes[i] for i in y_true_idx], name="true"),
                    pd.Series([classes[i] for i in res_hier["top1_idx"]], name="predicted"))
conf.to_csv(OUT / "GEO4_confusion_matrix.csv")

# Performance by family / genus (C_main)
per_row = pd.DataFrame({
    "true_species": known_sci_name,
    "pred_species_visual": [classes[i] for i in res_visual["top1_idx"]],
    "pred_species_hier": [classes[i] for i in res_hier["top1_idx"]],
    "true_genus": [genero_de(canonico(sp)) for sp in known_sci_name],
    "true_family": [class_family.get(sp) or familia_de(canonico(sp)) for sp in known_sci_name],
})
per_row["correct_visual"] = per_row["true_species"] == per_row["pred_species_visual"]
per_row["correct_hier"] = per_row["true_species"] == per_row["pred_species_hier"]
per_row["pred_genus_hier"] = per_row["pred_species_hier"].map(class_genus)
per_row["pred_family_hier"] = per_row["pred_species_hier"].map(class_family)
per_row["intra_genus_error_hier"] = (~per_row["correct_hier"]) & (per_row["true_genus"] == per_row["pred_genus_hier"])
per_row["inter_genus_error_hier"] = (~per_row["correct_hier"]) & (per_row["true_genus"] != per_row["pred_genus_hier"])

by_family = per_row.groupby("true_family").agg(
    n=("true_species", "size"), acc_visual=("correct_visual", "mean"), acc_hier=("correct_hier", "mean"),
    intra_genus_err_rate=("intra_genus_error_hier", "mean"), inter_genus_err_rate=("inter_genus_error_hier", "mean"),
).reset_index()
by_family.to_csv(OUT / "GEO4_performance_by_family.csv", index=False)

by_genus = per_row.groupby("true_genus").agg(
    n=("true_species", "size"), acc_visual=("correct_visual", "mean"), acc_hier=("correct_hier", "mean"),
    intra_genus_err_rate=("intra_genus_error_hier", "mean"), inter_genus_err_rate=("inter_genus_error_hier", "mean"),
).reset_index()
by_genus.to_csv(OUT / "GEO4_performance_by_genus.csv", index=False)

print(f"\nIntra-genus error rate (hier, of all): {per_row['intra_genus_error_hier'].mean():.4f}")
print(f"Inter-genus error rate (hier, of all): {per_row['inter_genus_error_hier'].mean():.4f}")

# ---------------------------------------------------------------------------
# PASO 4 -- Impacto en Open Set (A/B/C), mismo protocolo bootstrap de GEO2/GEO3
# ---------------------------------------------------------------------------
print("\n=== PASO 4: Open Set A/B/C ===")

unk_top1_idx = d_unknown_full.argmin(axis=1)
unk_top1_species = np.array([classes[i] for i in unk_top1_idx])
# IMPORTANT: replicate GEO2/phase_geo2_weight_sweep.py exactly -- for the KNOWN pool the
# geographic lookup uses the GROUND-TRUTH species label (known_sci_name), not the visual
# argmin prediction. This matches "known_top1 = known_sci_name" in phase_geo2_weight_sweep.py.
# (PASO 3's ranking task above is the one that legitimately uses the visual argmin prediction;
# this scalar Open-Set score in PASO 4 must match GEO2's own convention to be comparable.)
known_top1_species_visual = known_sci_name

all_visual_dist = np.concatenate([d_known_top1, d_unknown_top1])
all_visual_norm = minmax(all_visual_dist)


def hierarchical_scalar_components(top1_species_arr, zone_arr):
    comp_sp, comp_ge, comp_fa = [], [], []
    for sp, zone in zip(top1_species_arr, zone_arr):
        csp, cge, cfa, _ = hierarchical_geo_components(sp, zone)
        comp_sp.append(csp)
        comp_ge.append(cge)
        comp_fa.append(cfa)
    return np.array(comp_sp), np.array(comp_ge), np.array(comp_fa)


k_comp_sp, k_comp_ge, k_comp_fa = hierarchical_scalar_components(known_top1_species_visual, known_zone)
u_comp_sp, u_comp_ge, u_comp_fa = hierarchical_scalar_components(unk_top1_species, unk_zone)
all_comp_sp = np.concatenate([k_comp_sp, u_comp_sp])
all_comp_ge = np.concatenate([k_comp_ge, u_comp_ge])
all_comp_fa = np.concatenate([k_comp_fa, u_comp_fa])

# "unknownness" convention (higher = more UNKNOWN-like), identical direction to GEO2's geo_unknownness=1-minmax(P)
unknownness_sp = 1.0 - minmax(all_comp_sp)  # shrunk species component (used only inside C, where genus/family also enter)
unknownness_ge = 1.0 - minmax(all_comp_ge)
unknownness_fa = 1.0 - minmax(all_comp_fa)

# RAW (unshrunk) P_species, identical to GEO2's geo_unknownness -- used for variant B so that
# B reproduces the GEO2 w=0.9 species-only baseline exactly (shrinkage must NOT apply when
# genus/family are not in the combination, otherwise B is not a fair "GEO2-equivalent" baseline).
def raw_p_species_scalar(top1_species_arr, zone_arr):
    out = []
    for sp, zone in zip(top1_species_arr, zone_arr):
        p, _ = p_species(sp, zone)
        out.append(p)
    return np.array(out)


all_p_species_raw = np.concatenate([
    raw_p_species_scalar(known_top1_species_visual, known_zone),
    raw_p_species_scalar(unk_top1_species, unk_zone),
])
unknownness_sp_raw = 1.0 - minmax(all_p_species_raw)

y_true_os = np.concatenate([np.zeros(n_known), np.ones(n_unknown)])  # 1=UNKNOWN
ind_all = np.concatenate([known_individual.astype(str), unk_obs.astype(str)])


def metrics_at_threshold(y_true, y_score, thr):
    pred_unknown = (y_score >= thr).astype(int)
    tp = np.sum((pred_unknown == 1) & (y_true == 1))
    fn = np.sum((pred_unknown == 0) & (y_true == 1))
    tn = np.sum((pred_unknown == 0) & (y_true == 0))
    fp = np.sum((pred_unknown == 1) & (y_true == 0))
    far = fn / max(1, fn + tp)
    frr = fp / max(1, fp + tn)
    bal_acc = balanced_accuracy_score(y_true, pred_unknown)
    return dict(FAR=far, FRR=frr, BalancedAccuracy=bal_acc, TP=int(tp), FP=int(fp), TN=int(tn), FN=int(fn))


def choose_threshold(y_true, y_score):
    return float(np.quantile(y_score[y_true == 0], 0.95))


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
        fars.append(m["FAR"]); frrs.append(m["FRR"])

    def ci(arr):
        arr = np.array(arr)
        return dict(mean=float(arr.mean()), ci_lo=float(np.percentile(arr, 2.5)), ci_hi=float(np.percentile(arr, 97.5)), n_valid=int(len(arr)))
    return dict(auroc=ci(aurocs), far=ci(fars), frr=ci(frrs))


species_list24 = sorted(set(known_sci_name))
known_genera24 = set(genero_de(canonico(sp)) for sp in species_list24)
unk_genus_arr = np.array([genero_de(canonico(sp)) for sp in unk_species])
same_genus_mask = np.array([g in known_genera24 for g in unk_genus_arr])


def evaluate_variant(name, score_all):
    auroc = roc_auc_score(y_true_os, score_all)
    thr = choose_threshold(y_true_os, score_all)
    m = metrics_at_threshold(y_true_os, score_all, thr)
    bs = bootstrap_metric(y_true_os, score_all, ind_all)
    # subgroup same/diff genus
    known_scores = score_all[:n_known]
    unk_scores = score_all[n_known:]
    sub = {}
    for label, mask in [("same_genus", same_genus_mask), ("different_genus", ~same_genus_mask)]:
        if mask.sum() == 0:
            continue
        yt = np.concatenate([np.zeros(n_known), np.ones(int(mask.sum()))])
        ys = np.concatenate([known_scores, unk_scores[mask]])
        a = roc_auc_score(yt, ys)
        t = choose_threshold(yt, ys)
        mm = metrics_at_threshold(yt, ys, t)
        sub[label] = dict(AUROC=a, FAR=mm["FAR"], FRR=mm["FRR"], BalancedAccuracy=mm["BalancedAccuracy"], n=int(mask.sum()))
    result = dict(name=name, AUROC=float(auroc), threshold=thr, FAR=m["FAR"], FRR=m["FRR"],
                  BalancedAccuracy=m["BalancedAccuracy"], bootstrap=bs, subgroup=sub)
    print(f"  [{name}] AUROC={auroc:.5f} [{bs['auroc']['ci_lo']:.4f},{bs['auroc']['ci_hi']:.4f}] "
          f"FAR={m['FAR']:.4f} FRR={m['FRR']:.4f} BalAcc={m['BalancedAccuracy']:.4f}")
    return result


score_A_visual = all_visual_norm  # 100% visual (should reproduce 0.57329 when using -d directly; here as combined w=0 form)
# Note: score_A here is the *unknownness*, direction must match all_visual_norm (higher=less known).
# Sanity: roc_auc_score(y_true_os, all_visual_norm) must equal official reproduction.
auroc_check = roc_auc_score(y_true_os, all_visual_norm)
print(f"Sanity visual-only AUROC (via all_visual_norm) = {auroc_check:.10f} (official {OFFICIAL_AUROC:.10f})")
assert abs(auroc_check - OFFICIAL_AUROC) < 1e-6, "Visual-only reproduction broken in GEO4 pipeline!"

w = WEIGHT_SCHEMES["B_species_only"]
score_B = w["w_v"] * all_visual_norm + w["w_sp"] * unknownness_sp_raw  # w_ge=w_fa=0, RAW species prior (== GEO2 w=0.9)
w = WEIGHT_SCHEMES["C_main"]
score_C_main = w["w_v"] * all_visual_norm + w["w_sp"] * unknownness_sp + w["w_ge"] * unknownness_ge + w["w_fa"] * unknownness_fa

results_A = evaluate_variant("A_visual_only", all_visual_norm)
results_B = evaluate_variant("B_visual_plus_geo_species", score_B)
results_C_main = evaluate_variant("C_main_hierarchical", score_C_main)

variant_results = {"A_visual_only": results_A, "B_visual_plus_geo_species": results_B, "C_main_hierarchical": results_C_main}
for scheme_name in ["C_alt_species_heavy", "C_alt_balanced"]:
    w = WEIGHT_SCHEMES[scheme_name]
    score_alt = w["w_v"] * all_visual_norm + w["w_sp"] * unknownness_sp + w["w_ge"] * unknownness_ge + w["w_fa"] * unknownness_fa
    variant_results[scheme_name] = evaluate_variant(scheme_name, score_alt)

openset_comparison = {
    "gate0_check_visual_only_matches_official": bool(abs(auroc_check - OFFICIAL_AUROC) < 1e-9),
    "GEO2_reference_w0.9_species_only_auroc": 0.701,  # documented from GEO2_WEIGHT_SWEEP.csv
    "variants": variant_results,
    "weight_schemes": WEIGHT_SCHEMES,
    "protocol": "identico a GEO2/GEO3: bootstrap 1000 iter seed=42 estratificado por individuo, "
                "threshold=percentil95 de known_scores, FAR/FRR/BalancedAccuracy como en phase_geo2_weight_sweep.py",
}
json.dump(openset_comparison, open(OUT / "GEO4_openset_comparison.json", "w", encoding="utf-8"),
           indent=2, ensure_ascii=False, default=str)

# ---------------------------------------------------------------------------
# per-sample results (todas las filas KNOWN+UNKNOWN), con discrepancia visual vs genero/familia
# ---------------------------------------------------------------------------
rows_out = []
for i in range(n_known):
    sp = known_top1_species_visual[i]
    genus, fam = class_genus.get(sp), class_family.get(sp)
    zone = known_zone[i]
    _, _, _, dbg = hierarchical_geo_components(sp, zone)
    top_genus_by_prior = None
    top_fam_by_prior = None
    if zone is not None:
        cand_ge = prior_ge[prior_ge["zone_id"] == zone].sort_values("p", ascending=False)
        if len(cand_ge): top_genus_by_prior = cand_ge.iloc[0]["genus"]
        cand_fa = prior_fa[prior_fa["zone_id"] == zone].sort_values("p", ascending=False)
        if len(cand_fa): top_fam_by_prior = cand_fa.iloc[0]["family"]
    rows_out.append(dict(
        pool="KNOWN", sample_id=known_image_ids[i], true_species=known_sci_name[i],
        visual_top1_species=sp, zone=zone,
        discrepancy_genus=bool(top_genus_by_prior is not None and top_genus_by_prior != genus),
        discrepancy_family=bool(top_fam_by_prior is not None and top_fam_by_prior != fam),
        score_A=float(all_visual_norm[i]), score_B=float(score_B[i]), score_C=float(score_C_main[i]),
        lambda_s=dbg["lam_s"], lambda_g=dbg["lam_g"],
    ))
for j in range(n_unknown):
    sp = unk_top1_species[j]
    genus, fam = class_genus.get(sp), class_family.get(sp)
    zone = unk_zone[j]
    _, _, _, dbg = hierarchical_geo_components(sp, zone)
    top_genus_by_prior = None
    top_fam_by_prior = None
    if zone is not None:
        cand_ge = prior_ge[prior_ge["zone_id"] == zone].sort_values("p", ascending=False)
        if len(cand_ge): top_genus_by_prior = cand_ge.iloc[0]["genus"]
        cand_fa = prior_fa[prior_fa["zone_id"] == zone].sort_values("p", ascending=False)
        if len(cand_fa): top_fam_by_prior = cand_fa.iloc[0]["family"]
    i = n_known + j
    rows_out.append(dict(
        pool="UNKNOWN", sample_id=unk_obs[j], true_species=unk_species[j],
        visual_top1_species=sp, zone=zone,
        discrepancy_genus=bool(top_genus_by_prior is not None and top_genus_by_prior != genus),
        discrepancy_family=bool(top_fam_by_prior is not None and top_fam_by_prior != fam),
        score_A=float(all_visual_norm[i]), score_B=float(score_B[i]), score_C=float(score_C_main[i]),
        lambda_s=dbg["lam_s"], lambda_g=dbg["lam_g"],
    ))
pd.DataFrame(rows_out).to_csv(OUT / "GEO4_per_sample_results.csv", index=False)

print("\nDONE PASO 2-4.")

