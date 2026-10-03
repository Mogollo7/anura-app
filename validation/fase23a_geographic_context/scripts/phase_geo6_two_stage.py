#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
phase_geo6_two_stage.py -- GEO-6: ranking de candidatos y decision Open Set como
DOS problemas separados, con DOS scores distintos, en vez de un combined_score
unico (que GEO-5 demostro que produce un conflicto: w_geo=0.9 es bueno para
open-set pero destruye el ranking cerrado).

ETAPA 1 (ranking): score = (1-w_geo_rank)*visual_sim_norm + w_geo_rank*geo_species_norm,
  w_geo_rank in {0.0, 0.1, 0.2, 0.3}, evaluado sobre las 7475 imagenes KNOWN (24 especies
  verdad-terreno) contra las 41 especies candidatas con centroide (mismo pool que
  GEO2/3/4/5, no el subconjunto de 33/21 restringido al catalogo de Antioquia -- el pool
  de candidatos relevante para "que especies se confunden visualmente" no debe limitarse
  a la escala geografica regional).

ETAPA 2 (open-set): usa el top-1 del ranking de Etapa 1 (mejor w_geo_rank) como especie
  propuesta, y aplica un SEGUNDO score (misma formula estructural de GEO-2, w_geo_open_set=0.9)
  para decidir ESPECIE_CONOCIDA / NO_CONCLUYENTE (banda de dos thresholds).

Comparacion A/B/C/D (mismo protocolo bootstrap de GEO-2: 1000 iter, seed=42, estratificado
por individuo) que muestra si separar ranking y open-set resuelve el conflicto de GEO-5.

GATE 0: reproduce baseline_reproduction_v2.json (AUROC=0.57329, diff=0.0). Si falla, se
detiene con GEO6_BLOCKED.json.

Reglas duras: no reentrena, no nuevos embeddings, no genero/familia en el score (solo
metadata), no toca GEO2/3/4/5 ni produccion, no commit/push. Todo output con prefijo GEO6_.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, roc_auc_score, average_precision_score, balanced_accuracy_score

sys.path.insert(0, "D:/Anura")
from training.taxonomia import canonico, genero_de, familia_de

BASE = Path("D:/Anura")
OUT = BASE / "validation/fase23a_geographic_context"
SEED = 42
OFFICIAL_AUROC = 0.5732919408781961
RNG_MERLIN = 42

# ===========================================================================
# GATE 0
# ===========================================================================
gate = json.load(open(OUT / "baseline_reproduction_v2.json", encoding="utf-8"))
reproduced_auroc = gate["reproduced_auroc"]
abs_diff = abs(reproduced_auroc - OFFICIAL_AUROC)
gate0_passed = gate.get("gate_passed", False) and abs_diff == 0.0
print(f"GATE 0: reproduced={reproduced_auroc:.10f} official={OFFICIAL_AUROC:.10f} "
      f"diff={abs_diff} passed={gate0_passed}")
if not gate0_passed:
    json.dump({"status": "GEO6_BLOCKED", "reason": "gate0 failed", "gate": gate},
               open(OUT / "GEO6_BLOCKED.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    raise SystemExit(1)

# ===========================================================================
# 1. DATOS BASE (identico a GEO2/GEO5)
# ===========================================================================
print("\n=== 1. Cargando datos base ===")


def canonical_name(name):
    n = name.replace('_', ' ').strip()
    if n == "Pristimantis acanthinus":
        n = "Pristimantis achatinus"
    return n


def compute_centroids(X, y):
    return {c: np.mean(X[y == c], axis=0) for c in np.unique(y)}


ref_data = np.load(BASE / "evaluation/fase13/embeddings/reference_embeddings.npz")
y_ref = np.array([canonical_name(s) for s in ref_data["species"]])
train_data = np.load(BASE / "evaluation/fase13/embeddings/train_embeddings.npz")
y_train = np.array([canonical_name(s) for s in train_data["species"]])

ref_centroids = compute_centroids(ref_data["embeddings"], y_ref)
train_centroids = compute_centroids(train_data["embeddings"], y_train)
all_41_centroids = {}
for sp, c in ref_centroids.items():
    if sp in train_centroids:
        all_41_centroids[sp] = c
for sp, c in train_centroids.items():
    if sp not in all_41_centroids:
        all_41_centroids[sp] = c
classes = sorted(all_41_centroids.keys())
C = np.array([all_41_centroids[c] for c in classes])
n_classes = len(classes)
class_idx = {c: i for i, c in enumerate(classes)}
assert n_classes == 41

known_npz = np.load(BASE / "validation/fase16_clean_open_set/clean_known_embeddings.npz", allow_pickle=True)
X_known = known_npz["embeddings"].astype(np.float64)
known_image_ids = np.array([str(s) for s in known_npz["image_ids"]])
n_known = len(X_known)

unk_npz = np.load(BASE / "validation/fase23a_open_set_automatic/embeddings/unknown_embeddings.npz", allow_pickle=True)
X_unknown = unk_npz["embeddings"].astype(np.float64)
unk_species = np.array([str(s) for s in unk_npz["species"]])
unk_obs = np.array([str(s) for s in unk_npz["observation_id"]])
n_unknown = len(X_unknown)

d_known_full = np.linalg.norm(X_known[:, None, :] - C[None, :, :], axis=2)
d_unknown_full = np.linalg.norm(X_unknown[:, None, :] - C[None, :, :], axis=2)
d_known_top1 = d_known_full.min(axis=1)
d_unknown_top1 = d_unknown_full.min(axis=1)

repro = np.load(OUT / "reproduced_scores_v2.npz", allow_pickle=True)
assert np.allclose(d_known_top1, repro["d_known"].astype(np.float64), atol=1e-4)
assert np.allclose(d_unknown_top1, repro["d_unknown"].astype(np.float64), atol=1e-4)
known_individual_repro = np.array([str(s) for s in repro["species_known"]])  # placeholder unused

known_manifest = json.load(open(BASE / "validation/fase16_clean_open_set/clean_known_manifest.json", encoding="utf-8"))
known_images_meta = {im["image_id"]: im for im in known_manifest["images"]}
known_sci_name = np.array([known_images_meta[iid]["scientific_name"] for iid in known_image_ids])
known_obs = np.array([known_images_meta[iid].get("observation_id") for iid in known_image_ids])
known_individual = np.array([known_images_meta[iid].get("individual_id") for iid in known_image_ids])
y_true_idx = np.array([class_idx[sp] for sp in known_sci_name])  # ground truth (24 especies, dentro de 41)
n_gt_species = len(set(known_sci_name))
print(f"KNOWN: {n_known} imagenes, {n_gt_species} especies verdad-terreno; "
      f"candidate pool: {n_classes} especies con centroide; UNKNOWN: {n_unknown}")

class_genus = {sp: genero_de(canonico(sp)) for sp in classes}
class_family = {}
for sp in classes:
    try:
        class_family[sp] = familia_de(canonico(sp))
    except KeyError:
        class_family[sp] = None

# ---- Zonas (cache existente, sin llamadas nuevas), identico a GEO2/GEO5 ----
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
n_known_with_zone = int(pd.notna(known_zone).sum())
n_unk_with_zone = int(pd.notna(unk_zone).sum())
print(f"Zonas asignadas: KNOWN {n_known_with_zone}/{n_known}, UNKNOWN {n_unk_with_zone}/{n_unknown}")

# ---- Prior por especie K=291 (identico a GEO5, prior_zone_taxon_v2_clean.csv) ----
prior_full = pd.read_csv(OUT / "prior_zone_taxon_v2_clean.csv")
prior_manifest = json.load(open(OUT / "prior_zone_taxon_v2_clean_manifest.json", encoding="utf-8"))
ALPHA_SP, K_SP = prior_manifest["alpha_selected"], prior_manifest["K_taxa"]
prior_lookup = {(r["zone_id"], r["scientific_name"]): float(r["p"]) for _, r in prior_full.iterrows()}
n_eff_zone_sp = prior_full.groupby("zone_id")["n_effective"].sum().to_dict()
NEUTRAL_SP = 1.0 / K_SP


def p_species(sp, zone):
    if zone is None:
        return NEUTRAL_SP
    key = (zone, canonico(sp).replace("_", " "))
    if key in prior_lookup:
        return prior_lookup[key]
    denom = n_eff_zone_sp.get(zone, 0) + ALPHA_SP * K_SP
    return ALPHA_SP / denom if denom > 0 else NEUTRAL_SP


def minmax(x):
    x = np.asarray(x, dtype=float)
    lo, hi = np.nanmin(x), np.nanmax(x)
    if hi - lo < 1e-12:
        return np.zeros_like(x)
    return (x - lo) / (hi - lo)


def prior_for_openset(species_name, zone):
    """Identico a GEO2's prior_for: usado para el score de open-set (single scalar por top1)."""
    if zone is None:
        return None
    key = (zone, species_name)
    if key in prior_lookup:
        return float(prior_lookup[key])
    n_eff_zone = prior_full[prior_full["zone_id"] == zone]["n_effective"].sum()
    denom = n_eff_zone + ALPHA_SP * K_SP
    return float(ALPHA_SP / denom) if denom > 0 else NEUTRAL_SP


def geo_score_for_rows(top1_species, zones):
    scores = []
    for sp, zone in zip(top1_species, zones):
        if zone is None or (isinstance(zone, float) and np.isnan(zone)):
            scores.append(NEUTRAL_SP)
        else:
            p = prior_for_openset(canonico(sp).replace("_", " "), zone)
            scores.append(p if p is not None else NEUTRAL_SP)
    return np.array(scores)


# ===========================================================================
# ETAPA 1 -- RANKING (candidatos, NO decide open-set)
# ===========================================================================
print("\n=== ETAPA 1: Ranking (w_geo_rank sweep) ===")

# visual_sim_norm: fila-wise min-max de -distancia sobre 41 candidatas (identico a GEO5)
visual_sim_known = -d_known_full
visual_sim_known_norm = (visual_sim_known - visual_sim_known.min(axis=1, keepdims=True)) / np.maximum(
    visual_sim_known.max(axis=1, keepdims=True) - visual_sim_known.min(axis=1, keepdims=True), 1e-12)

visual_sim_unk = -d_unknown_full
visual_sim_unk_norm = (visual_sim_unk - visual_sim_unk.min(axis=1, keepdims=True)) / np.maximum(
    visual_sim_unk.max(axis=1, keepdims=True) - visual_sim_unk.min(axis=1, keepdims=True), 1e-12)

# geo_species_norm: fila-wise min-max del prior de especie por zona, sobre 41 candidatas
comp_sp_known = np.zeros((n_known, n_classes))
for j, sp in enumerate(classes):
    for i in range(n_known):
        comp_sp_known[i, j] = p_species(sp, known_zone[i])
comp_sp_known_norm = (comp_sp_known - comp_sp_known.min(axis=1, keepdims=True)) / np.maximum(
    comp_sp_known.max(axis=1, keepdims=True) - comp_sp_known.min(axis=1, keepdims=True), 1e-12)

comp_sp_unk = np.zeros((n_unknown, n_classes))
for j, sp in enumerate(classes):
    for i in range(n_unknown):
        comp_sp_unk[i, j] = p_species(sp, unk_zone[i])
comp_sp_unk_norm = (comp_sp_unk - comp_sp_unk.min(axis=1, keepdims=True)) / np.maximum(
    comp_sp_unk.max(axis=1, keepdims=True) - comp_sp_unk.min(axis=1, keepdims=True), 1e-12)


def rank_metrics(score_mat, y_true_idx_local):
    n = score_mat.shape[0]
    top1_idx = score_mat.argmax(axis=1)
    top1_acc = float((top1_idx == y_true_idx_local).mean())
    order = np.argsort(-score_mat, axis=1)
    top3_idx = order[:, :3]
    top5_idx = order[:, :5]
    top3_acc = float(np.mean([y_true_idx_local[i] in top3_idx[i] for i in range(n)]))
    top5_acc = float(np.mean([y_true_idx_local[i] in top5_idx[i] for i in range(n)]))
    f1_macro = float(f1_score(y_true_idx_local, top1_idx, average="macro",
                               labels=list(range(n_classes)), zero_division=0))
    rank_pos = np.array([int(np.where(order[i] == y_true_idx_local[i])[0][0]) + 1 for i in range(n)])
    mrr = float(np.mean(1.0 / rank_pos))
    mean_rank = float(rank_pos.mean())
    return dict(top1_acc=top1_acc, top3_acc=top3_acc, top5_acc=top5_acc, f1_macro=f1_macro,
                mrr=mrr, mean_rank=mean_rank, top1_idx=top1_idx, top3_idx=top3_idx, order=order,
                rank_pos=rank_pos)


W_GEO_RANK_SWEEP = [0.0, 0.1, 0.2, 0.3]
ranking_results = {}
ranking_rows = []
per_species_records = []
per_genus_records = []
confusion_by_w = {}
unk_top1_idx_by_w = {}

for w in W_GEO_RANK_SWEEP:
    score_known = (1 - w) * visual_sim_known_norm + w * comp_sp_known_norm
    score_unk = (1 - w) * visual_sim_unk_norm + w * comp_sp_unk_norm
    res = rank_metrics(score_known, y_true_idx)
    ranking_results[w] = res
    unk_top1_idx_by_w[w] = score_unk.argmax(axis=1)
    print(f"  w_geo_rank={w:.1f}: Top-1={res['top1_acc']:.4f} Top-3={res['top3_acc']:.4f} "
          f"Top-5={res['top5_acc']:.4f} F1_macro={res['f1_macro']:.4f} MRR={res['mrr']:.4f} "
          f"mean_rank={res['mean_rank']:.3f}")
    ranking_rows.append(dict(w_geo_rank=w, w_visual=round(1 - w, 2), top1_acc=res["top1_acc"],
                              top3_acc=res["top3_acc"], top5_acc=res["top5_acc"],
                              f1_macro=res["f1_macro"], mrr=res["mrr"], mean_rank=res["mean_rank"],
                              n_known=n_known, n_gt_species=n_gt_species, n_candidate_species=n_classes))

    conf = pd.crosstab(pd.Series(known_sci_name, name="true"),
                        pd.Series([classes[i] for i in res["top1_idx"]], name="predicted"))
    confusion_by_w[w] = conf

    # per-species accuracy (grouping only)
    df_i = pd.DataFrame(dict(true_species=known_sci_name,
                              pred_species=[classes[i] for i in res["top1_idx"]],
                              rank_pos=res["rank_pos"]))
    df_i["correct"] = df_i["true_species"] == df_i["pred_species"]
    for sp, g in df_i.groupby("true_species"):
        per_species_records.append(dict(w_geo_rank=w, species=sp, genus=genero_de(canonico(sp)),
                                          family=class_family.get(sp), n=len(g), top1_acc=g["correct"].mean(),
                                          mean_rank=g["rank_pos"].mean(), mrr=(1.0 / g["rank_pos"]).mean()))
    df_i["genus"] = df_i["true_species"].map(lambda s: genero_de(canonico(s)))
    for gen, g in df_i.groupby("genus"):
        per_genus_records.append(dict(w_geo_rank=w, genus=gen, n=len(g), top1_acc=g["correct"].mean(),
                                       mean_rank=g["rank_pos"].mean(), mrr=(1.0 / g["rank_pos"]).mean()))

ranking_df = pd.DataFrame(ranking_rows)
ranking_df.to_csv(OUT / "GEO6_RANKING_RESULTS.csv", index=False)

# criterio de seleccion: Top-1 primero, empate -> Top-3, empate -> MRR (documentado explicitamente)
ranking_df_sorted = ranking_df.sort_values(["top1_acc", "top3_acc", "mrr"], ascending=False)
BEST_W_RANK = float(ranking_df_sorted.iloc[0]["w_geo_rank"])
print(f"\nMejor w_geo_rank por criterio (Top-1 > Top-3 > MRR): {BEST_W_RANK}")

per_species_df = pd.DataFrame(per_species_records)
per_genus_df = pd.DataFrame(per_genus_records)
per_species_df.to_csv(OUT / "GEO6_ranking_by_species.csv", index=False)
per_genus_df.to_csv(OUT / "GEO6_ranking_by_genus.csv", index=False)
confusion_by_w[BEST_W_RANK].to_csv(OUT / "GEO6_confusion_matrix_best_w.csv")
confusion_by_w[0.0].to_csv(OUT / "GEO6_confusion_matrix_visual_only.csv")

ranking_json = {
    "w_geo_rank_sweep": W_GEO_RANK_SWEEP,
    "candidate_pool": {
        "n_species": n_classes,
        "choice_justification": (
            "Se evalua sobre las 41 especies con centroide (pool completo de GEO2/3/4/5), NO "
            "el subconjunto de 33 (o 21 KNOWN) restringido al catalogo regional de Antioquia "
            "identificado en GEO-5. Razon: el pool de candidatos relevante para el problema de "
            "ranking es 'que especies pueden confundirse visualmente entre si segun el encoder', "
            "una propiedad del modelo/embedding, no de la escala geografica de despliegue. "
            "Restringir candidatos a 33/21 cambiaria artificialmente Top-1/Top-3 al eliminar "
            "distractores reales del espacio de embeddings, y rompe comparabilidad directa con "
            "GEO2/3/4/5 (que tambien usan 41). Se documenta explicitamente esta decision."
        ),
    },
    "ground_truth": {"n_images": n_known, "n_species": n_gt_species,
                      "source": "validation/fase16_clean_open_set/clean_known_{embeddings,manifest}.json (mismo pool KNOWN de GEO2/3/4/5)"},
    "normalization": "min-max por fila sobre las 41 candidatas, tanto para visual_sim (-distancia euclidiana) como para geo_species (prior bayesiano por zona, K=291, mismo prior_zone_taxon_v2_clean.csv de GEO2/3/5) -- misma normalizacion que GEO2/GEO4/GEO5.",
    "results_by_w": {str(w): {k: v for k, v in ranking_results[w].items() if k in
                               ("top1_acc", "top3_acc", "top5_acc", "f1_macro", "mrr", "mean_rank")}
                      for w in W_GEO_RANK_SWEEP},
    "selection_criterion": "Top-1 accuracy primario; empate resuelto por Top-3, luego por MRR (mayor MRR = candidato correcto en posiciones mas altas en promedio).",
    "best_w_geo_rank": BEST_W_RANK,
}
json.dump(ranking_json, open(OUT / "GEO6_RANKING_RESULTS.json", "w", encoding="utf-8"),
          indent=2, ensure_ascii=False, default=str)

print("ETAPA 1 escrita: GEO6_RANKING_RESULTS.csv/json, GEO6_ranking_by_species.csv, "
      "GEO6_ranking_by_genus.csv, GEO6_confusion_matrix_*.csv")

# ===========================================================================
# ETAPA 2 -- OPEN SET (decision de aceptacion, score SEPARADO del ranking)
# ===========================================================================
print("\n=== ETAPA 2: Open-set (gate separado del ranking) ===")

W_GEO_OPENSET = 0.9  # config GEO-2/GEO-3, DISTINTA del ranking (documentado explicitamente)
y_true_bin = np.concatenate([np.zeros(n_known), np.ones(n_unknown)])  # 1 = UNKNOWN
ind_all = np.concatenate([known_individual.astype(str), unk_obs.astype(str)])

# top1 del RANKING de Etapa 1 (mejor w), usado como "especie propuesta" para el gate open-set
top1_idx_known_etapa1 = ranking_results[BEST_W_RANK]["top1_idx"]
top1_species_known_etapa1 = np.array([classes[i] for i in top1_idx_known_etapa1])
top1_idx_unk_etapa1 = unk_top1_idx_by_w[BEST_W_RANK]
top1_species_unk_etapa1 = np.array([classes[i] for i in top1_idx_unk_etapa1])

# top1 puro visual (w=0), para A y D (reproduce exactamente el top1 de GEO2/GEO3)
top1_idx_known_visual = ranking_results[0.0]["top1_idx"]
top1_species_known_visual = np.array([classes[i] for i in top1_idx_known_visual])
top1_idx_unk_visual = unk_top1_idx_by_w[0.0]
top1_species_unk_visual = np.array([classes[i] for i in top1_idx_unk_visual])

# visual_norm para open-set: minmax de la distancia TOP-1 pura (escalar), identico a GEO2/GEO3
# (no la matriz fila-normalizada de 41 clases usada en el ranking -- son insumos distintos
# por construccion, documentado en el encargo).
all_visual_dist = np.concatenate([d_known_top1, d_unknown_top1])
all_visual_norm_openset = minmax(all_visual_dist)


def build_openset_score(top1_species_known, top1_species_unk, w_geo):
    known_geo_score = geo_score_for_rows(top1_species_known, known_zone)
    unk_geo_score = geo_score_for_rows(top1_species_unk, unk_zone)
    all_geo_score = np.concatenate([known_geo_score, unk_geo_score])
    geo_probable_norm = minmax(all_geo_score)
    geo_unknownness = 1.0 - geo_probable_norm
    score = (1 - w_geo) * all_visual_norm_openset + w_geo * geo_unknownness
    return score, known_geo_score, unk_geo_score


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
    precision = tp / max(1, tp + fp)
    bal_acc = balanced_accuracy_score(y_true, pred_unknown)
    return dict(TPR=tpr, TNR=tnr, FAR=far, FRR=frr, Precision=precision,
                BalancedAccuracy=bal_acc, TP=int(tp), FP=int(fp), TN=int(tn), FN=int(fn))


def choose_threshold_95(y_true, y_score):
    known_scores_here = y_score[y_true == 0]
    return float(np.quantile(known_scores_here, 0.95))


def tpr_at_far_le(y_true, y_score, far_target):
    """Mayor TPR (deteccion de UNKNOWN) tal que FAR <= far_target, buscando sobre umbrales unicos."""
    uniq_thr = np.unique(y_score)
    best_tpr, best_thr = None, None
    for thr in uniq_thr:
        m = metrics_at_threshold(y_true, y_score, thr)
        if m["FAR"] <= far_target:
            if best_tpr is None or m["TPR"] > best_tpr:
                best_tpr, best_thr = m["TPR"], thr
    return best_tpr, best_thr


def bootstrap_metric(y_true, y_score, ind_ids, n_iter=1000, seed=SEED):
    rng = np.random.RandomState(seed)
    unique_known_ind = np.unique(ind_ids[y_true == 0])
    unique_unknown_ind = np.unique(ind_ids[y_true == 1])
    idx_by_ind = {u: np.where(ind_ids == u)[0] for u in np.unique(ind_ids)}
    aurocs, fars, frrs, balaccs, precisions = [], [], [], [], []
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
        thr = choose_threshold_95(yt, ys)
        m = metrics_at_threshold(yt, ys, thr)
        fars.append(m["FAR"]); frrs.append(m["FRR"]); balaccs.append(m["BalancedAccuracy"])
        precisions.append(m["Precision"])

    def ci(arr):
        arr = np.array(arr)
        return dict(mean=float(arr.mean()), ci_lo=float(np.percentile(arr, 2.5)),
                    ci_hi=float(np.percentile(arr, 97.5)), n_valid=int(len(arr)))

    return dict(auroc=ci(aurocs), far=ci(fars), frr=ci(frrs), balacc=ci(balaccs), precision=ci(precisions))


def full_openset_eval(name, score, w_geo_label):
    auroc = roc_auc_score(y_true_bin, score)
    auprc = average_precision_score(y_true_bin, score)
    thr = choose_threshold_95(y_true_bin, score)
    m = metrics_at_threshold(y_true_bin, score, thr)
    tpr_far5, thr_far5 = tpr_at_far_le(y_true_bin, score, 0.05)
    tpr_far10, thr_far10 = tpr_at_far_le(y_true_bin, score, 0.10)
    bs = bootstrap_metric(y_true_bin, score, ind_all, n_iter=1000, seed=SEED)
    row = dict(config=name, w_geo=w_geo_label, AUROC=auroc, AUPRC=auprc, threshold_p95=thr,
               AUROC_ci_lo=bs["auroc"]["ci_lo"], AUROC_ci_hi=bs["auroc"]["ci_hi"],
               FAR=m["FAR"], FAR_ci_lo=bs["far"]["ci_lo"], FAR_ci_hi=bs["far"]["ci_hi"],
               FRR=m["FRR"], FRR_ci_lo=bs["frr"]["ci_lo"], FRR_ci_hi=bs["frr"]["ci_hi"],
               BalancedAccuracy=m["BalancedAccuracy"],
               BalancedAccuracy_ci_lo=bs["balacc"]["ci_lo"], BalancedAccuracy_ci_hi=bs["balacc"]["ci_hi"],
               Precision=m["Precision"], Precision_ci_lo=bs["precision"]["ci_lo"], Precision_ci_hi=bs["precision"]["ci_hi"],
               TPR_at_FAR_le_5pct=tpr_far5, TPR_at_FAR_le_10pct=tpr_far10,
               n_known=n_known, n_unknown=n_unknown, bootstrap_n_valid=bs["auroc"]["n_valid"])
    print(f"  [{name}] AUROC={auroc:.5f} [{bs['auroc']['ci_lo']:.4f},{bs['auroc']['ci_hi']:.4f}] "
          f"FAR={m['FAR']:.4f} FRR={m['FRR']:.4f} BalAcc={m['BalancedAccuracy']:.4f} "
          f"TPR@FAR<=5%={tpr_far5} TPR@FAR<=10%={tpr_far10}")
    return row, score, thr


# --- A: visual solo (recomputado exactamente igual que GEO2 w=0.0 para consistencia interna) ---
score_A, _, _ = build_openset_score(top1_species_known_visual, top1_species_unk_visual, 0.0)
row_A, score_A, thr_A = full_openset_eval("A_visual_only", score_A, 0.0)

# --- D: GEO-2 ORIGINAL w=0.9, reproducido FIELMENTE (incluye una particularidad metodologica
# de GEO-2 descubierta al reproducirlo: para las imagenes KNOWN, GEO-2 usa la especie
# VERDADERA (known_sci_name, oracle) como "top1_species" para el lookup geografico, NO la
# especie predicha por el visual (ver phase_geo2_weight_sweep.py linea 127: `known_top1 =
# known_sci_name`). Esto es NO REPLICABLE en inferencia real (no se conoce la especie
# verdadera de antemano -- es justo lo que se intenta determinar). Para UNKNOWN si usa la
# especie predicha (argmin), porque no hay verdad-terreno dentro del pool de 41 clases.
# D se reproduce aqui EXACTAMENTE con ese oracle (para poder citar el numero historico
# 0.70148 como contraste directo, tal como pide el encargo), pero se documenta la
# asimetria oracle/predicho explicitamente -- es un hallazgo relevante de GEO-6, no un error.
score_D, _, _ = build_openset_score(known_sci_name, top1_species_unk_visual, W_GEO_OPENSET)
row_D, score_D, thr_D = full_openset_eval("D_geo2_single_score_w0.9_ORACLE_KNOWN_TOP1", score_D, W_GEO_OPENSET)
D_oracle_caveat = (
    "IMPORTANTE: D reproduce fielmente la metodologia ORIGINAL de GEO-2, que para las "
    "imagenes KNOWN usa la especie VERDADERA (no la predicha por el visual) como insumo del "
    "componente geografico. Esto es un oracle que no esta disponible en inferencia real. Por "
    "eso el AUROC de D (~0.70, ver mas abajo) NO es directamente comparable en pie de igualdad "
    "con B/C, que usan la especie REALMENTE PREDICHA por Etapa 1 (metodologia honesta, "
    "replicable en produccion). Descubierto al intentar recomputar D con top1 predicho: se "
    "obtuvo AUROC=0.6167 (no 0.70148) -- la diferencia (~0.085 AUROC) es exactamente el efecto "
    "de usar oracle vs prediccion real para el componente geografico en las imagenes KNOWN."
)
print("\n" + D_oracle_caveat)

# --- B: ranking+geo (mejor w_geo_rank) usado DIRECTAMENTE como score open-set (score unico, sin gate separado) ---
score_B, _, _ = build_openset_score(top1_species_known_etapa1, top1_species_unk_etapa1, BEST_W_RANK)
row_B, score_B, thr_B = full_openset_eval(f"B_ranking_score_as_openset_w{BEST_W_RANK}", score_B, BEST_W_RANK)

# --- C: arquitectura de DOS ETAPAS -- candidato de Etapa 1 (w_geo_rank) + gate open-set separado (w=0.9) ---
score_C, known_geo_score_C, unk_geo_score_C = build_openset_score(
    top1_species_known_etapa1, top1_species_unk_etapa1, W_GEO_OPENSET)
row_C, score_C, thr_C = full_openset_eval("C_two_stage_rank_then_openset_gate", score_C, W_GEO_OPENSET)

# Consistencia interna: A y D deben reproducir (dentro de tolerancia numerica) el AUROC oficial de GEO2
geo2_sweep = pd.read_csv(OUT / "GEO2_WEIGHT_SWEEP.csv")
geo2_A = geo2_sweep[geo2_sweep["w_geo"] == 0.0].iloc[0]
geo2_D = geo2_sweep[geo2_sweep["w_geo"] == 0.9].iloc[0]
print(f"\nConsistencia interna vs GEO2_WEIGHT_SWEEP.csv: "
      f"A: recomputado={row_A['AUROC']:.5f} vs GEO2={geo2_A['AUROC']:.5f} "
      f"(diff={abs(row_A['AUROC']-geo2_A['AUROC']):.6f}); "
      f"D: recomputado={row_D['AUROC']:.5f} vs GEO2={geo2_D['AUROC']:.5f} "
      f"(diff={abs(row_D['AUROC']-geo2_D['AUROC']):.6f})")

openset_rows = [row_A, row_B, row_C, row_D]
openset_df = pd.DataFrame(openset_rows)
openset_df.to_csv(OUT / "GEO6_OPENSET_RESULTS.csv", index=False)

# --- Desglose UNKNOWN: same_genus vs different_genus, y con zona vs sin zona ---
known_genera = set(genero_de(canonico(sp)) for sp in set(known_sci_name))
unk_genus = np.array([genero_de(canonico(sp)) for sp in unk_species])
same_genus_mask = np.array([g in known_genera for g in unk_genus])
zone_mask = pd.notna(unk_zone)

subgroup_rows = []
for cfg_name, score in [("A_visual_only", score_A), ("C_two_stage", score_C), ("D_geo2_single", score_D)]:
    unk_score = score[n_known:]
    for label, mask in [("same_genus", same_genus_mask), ("different_genus", ~same_genus_mask),
                         ("with_zone", zone_mask), ("without_zone", ~zone_mask)]:
        if mask.sum() == 0:
            continue
        yt = np.concatenate([np.zeros(n_known), np.ones(int(mask.sum()))])
        ys = np.concatenate([score[:n_known], unk_score[mask]])
        try:
            a = roc_auc_score(yt, ys)
        except Exception:
            a = None
        thr_g = choose_threshold_95(yt, ys)
        m = metrics_at_threshold(yt, ys, thr_g) if a is not None else {}
        subgroup_rows.append(dict(config=cfg_name, subgroup=label, n_unknown=int(mask.sum()),
                                   AUROC=a, FAR=m.get("FAR"), FRR=m.get("FRR"),
                                   BalancedAccuracy=m.get("BalancedAccuracy")))
subgroup_df = pd.DataFrame(subgroup_rows)
subgroup_df.to_csv(OUT / "GEO6_OPENSET_SUBGROUP_ANALYSIS.csv", index=False)
print("\nNOTA: el desglose with_zone/without_zone puede tener sesgo de seleccion (que "
      "observaciones UNKNOWN tienen coordenada recuperable no es aleatorio) -- GEO-3 ya "
      "encontro una direccion contraintuitiva ahi. No se interpreta como causal.")

openset_json = {
    "w_geo_open_set": W_GEO_OPENSET,
    "note_distinct_from_ranking": (
        f"El score de open-set (w_geo_open_set={W_GEO_OPENSET}) es un score DISTINTO del score "
        f"de ranking de Etapa 1 (w_geo_rank={BEST_W_RANK}). Ambos usan la MISMA estructura "
        f"funcional ((1-w)*visual_norm + w*geo_unknownness) pero (a) pesos distintos y (b) el "
        f"insumo visual_norm de open-set es la distancia TOP-1 escalar (minmax global), mientras "
        f"que el de ranking es una matriz fila-normalizada sobre 41 candidatas -- no se reutiliza "
        f"ciegamente un score para el otro proposito."
    ),
    "configs": {
        "A_visual_only": row_A, "B_ranking_score_as_openset": row_B,
        "C_two_stage": row_C, "D_geo2_single_score": row_D,
    },
    "consistency_check_vs_GEO2": {
        "A_recomputed_auroc": row_A["AUROC"], "A_geo2_reference_auroc": float(geo2_A["AUROC"]),
        "D_recomputed_auroc": row_D["AUROC"], "D_geo2_reference_auroc": float(geo2_D["AUROC"]),
    },
    "subgroup_analysis_note": "with_zone/without_zone puede tener sesgo de seleccion, NO interpretar como causal (ver GEO-3).",
    "D_oracle_vs_predicted_caveat": D_oracle_caveat,
}
json.dump(openset_json, open(OUT / "GEO6_OPENSET_RESULTS.json", "w", encoding="utf-8"),
          indent=2, ensure_ascii=False, default=str)

# ===========================================================================
# Umbral de aceptacion (CALIBRATION vs DIAGNOSTIC) + banda NO_CONCLUYENTE (2 thresholds)
# ===========================================================================
print("\n=== Umbral de aceptacion: CALIBRATION vs DIAGNOSTIC ===")

calib_manifest = json.load(open(BASE / "validation/fase18_clean_calibration/calibration_results.json", encoding="utf-8"))
calib_euclidean = calib_manifest["EUCLIDEAN"]
CALIBRATION_VALID = False
calibration_rejection_reason = (
    f"validation/fase18_clean_calibration/ tiene un split CALIBRATION independiente con ambas "
    f"clases representadas (known_n={calib_euclidean['known_n']}, unknown_n={calib_euclidean['unknown_n']}), "
    f"pero se descarta para seleccionar el threshold de GEO-6 por dos razones: (1) unknown_n="
    f"{calib_euclidean['unknown_n']} es demasiado pequeno para estimar FAR de forma confiable "
    f"(un solo UNKNOWN mal clasificado mueve FAR en ~{round(100/calib_euclidean['unknown_n'],1)} "
    f"puntos porcentuales); (2) el pipeline de fase18 selecciono COSINE como metrica final "
    f"(method_selection.json), mientras que GEO-6 hereda el pipeline oficial euclidean_raw de "
    f"fase23a (Gate 0) -- aunque fase18 reporta tambien un EUCLIDEAN de referencia, ese EUCLIDEAN "
    f"no es el mismo score combinado visual+geo de GEO-2/3/5/6 (fase18 no incluye componente "
    f"geografico). Por lo tanto el threshold de aceptacion de GEO-6 se marca DIAGNOSTIC: se "
    f"selecciona con el mismo metodo de busqueda por FAR objetivo que GEO-3 (percentil 95 de "
    f"KNOWN + busqueda de umbral con FAR<=nivel), pero sobre el propio split de TEST (7475 "
    f"KNOWN + 620 UNKNOWN), la misma limitacion heredada que ya tenian GEO-2 y GEO-3 (documentada "
    f"alli, no nueva de GEO-6)."
)
print(calibration_rejection_reason)

# Threshold curve estilo GEO-3 (linspace sobre el rango real del score, 400 puntos, identico
# metodo a phase_geo3_coverage_and_threshold.py), recalculado sobre score_C (Etapa 2, top1 de Etapa 1)
lo_c, hi_c = float(score_C.min()), float(score_C.max())
thresholds_c = np.linspace(lo_c, hi_c, 400)
curve_rows = []
for thr in thresholds_c:
    m = metrics_at_threshold(y_true_bin, score_C, thr)
    curve_rows.append(dict(threshold=float(thr), **m))
curve_df = pd.DataFrame(curve_rows).sort_values("threshold")
curve_df.to_csv(OUT / "GEO6_THRESHOLD_CURVE_C.csv", index=False)

far_levels = [0.30, 0.10, 0.05]
operating_points = []
for lvl in far_levels:
    cand = curve_df[curve_df["FAR"] <= lvl]
    if len(cand) == 0:
        operating_points.append(dict(far_level=lvl, status="NO_OPERATING_POINT"))
        continue
    # entre los que cumplen FAR<=lvl, elegir el de MENOR FRR (mejor punto operativo dentro del
    # nivel de FAR permitido) -- identico criterio a phase_geo3_coverage_and_threshold.py
    best = cand.sort_values("FRR").iloc[0]
    operating_points.append(dict(far_level=lvl, status="FOUND", threshold=float(best["threshold"]),
                                  FAR=float(best["FAR"]), FRR=float(best["FRR"]),
                                  BalancedAccuracy=float(best["BalancedAccuracy"]),
                                  Precision=float(best["Precision"])))
op_df = pd.DataFrame(operating_points)
op_df.to_csv(OUT / "GEO6_OPERATING_POINTS.csv", index=False)
print(op_df.to_string(index=False))

op_far05 = next((o for o in operating_points if o["far_level"] == 0.05 and o["status"] == "FOUND"), None)
op_far30 = next((o for o in operating_points if o["far_level"] == 0.30 and o["status"] == "FOUND"), None)
THR_LOW = op_far05["threshold"] if op_far05 else float(np.quantile(score_C, 0.05))
THR_HIGH = op_far30["threshold"] if op_far30 else float(np.quantile(score_C, 0.5))

threshold_selection_note = (
    f"Banda de dos thresholds sobre score_C (Etapa 2, w_geo_open_set=0.9, especie propuesta = "
    f"top1 de Etapa 1 con w_geo_rank={BEST_W_RANK}): "
    f"THR_LOW={THR_LOW:.4f} (umbral con FAR<=5%, mismo nivel operativo que GEO-3 eligio como su "
    f"punto mas estricto) -> score < THR_LOW => ESPECIE_CONOCIDA (alta confianza, bajo riesgo de "
    f"aceptar una especie realmente no-registrada). THR_HIGH={THR_HIGH:.4f} (umbral con FAR<=30%, "
    f"el punto operativo que GEO-3 selecciono como su recomendacion central) -> score >= THR_HIGH "
    f"=> zona de fuerte incompatibilidad visual+geografica. Banda intermedia (THR_LOW<=score<"
    f"THR_HIGH) => NO_CONCLUYENTE. DIAGNOSTIC: ambos thresholds se calibraron sobre el mismo split "
    f"de TEST evaluado (no hay CALIBRATION independiente valida, ver arriba), por lo que estos "
    f"numeros NO deben tratarse como umbrales de produccion."
)
print(threshold_selection_note)

# ===========================================================================
# Decision Open-Set por observacion (score_C, banda de 2 thresholds)
# ===========================================================================
def openset_decision(score_val):
    if score_val < THR_LOW:
        return "ESPECIE_CONOCIDA"
    elif score_val >= THR_HIGH:
        return ("NO_CONCLUYENTE (alta incompatibilidad visual+geografica -- posible especie no "
                "registrada, pero no se afirma NO_REGISTRADA: no existe evidencia suficiente en "
                "este experimento para distinguir formalmente 'especie ausente del catalogo' de "
                "'observacion ambigua/borderline' con el mismo score. Ver limitacion en GEO6_REPORT.md)")
    else:
        return "NO_CONCLUYENTE"


decisions_known = np.array([openset_decision(s) for s in score_C[:n_known]])
decisions_unk = np.array([openset_decision(s) for s in score_C[n_known:]])

decision_summary = {
    "THR_LOW_FAR_le_5pct": THR_LOW, "THR_HIGH_FAR_le_30pct": THR_HIGH,
    "status": "DIAGNOSTIC",
    "calibration_rejection_reason": calibration_rejection_reason,
    "threshold_selection_note": threshold_selection_note,
    "known_set_decision_counts": {k: int(v) for k, v in pd.Series(decisions_known).value_counts().items()},
    "unknown_set_decision_counts": {k: int(v) for k, v in pd.Series(decisions_unk).value_counts().items()},
}
json.dump(decision_summary, open(OUT / "GEO6_OPENSET_DECISION_SUMMARY.json", "w", encoding="utf-8"),
          indent=2, ensure_ascii=False, default=str)
print("\nDecision counts (KNOWN):", decision_summary["known_set_decision_counts"])
print("Decision counts (UNKNOWN):", decision_summary["unknown_set_decision_counts"])

# ===========================================================================
# SALIDA MERLIN-LIKE (5-8 ejemplos reales)
# ===========================================================================
print("\n=== Ejemplos formato Merlin ===")
rng = np.random.RandomState(RNG_MERLIN)
# mezcla: algunos KNOWN correctos, algunos KNOWN con error de ranking, algunos UNKNOWN
n_known_ex = 5
n_unk_ex = 3
sample_known_idx = rng.choice(n_known, size=n_known_ex, replace=False)
sample_unk_idx = rng.choice(n_unknown, size=n_unk_ex, replace=False)

order_etapa1 = ranking_results[BEST_W_RANK]["order"]  # (n_known, n_classes), orden Etapa1 para KNOWN
# orden Etapa1 para UNKNOWN (recalculado con el mismo w)
score_unk_etapa1_mat = (1 - BEST_W_RANK) * visual_sim_unk_norm + BEST_W_RANK * comp_sp_unk_norm
order_unk_etapa1 = np.argsort(-score_unk_etapa1_mat, axis=1)


def geo_compat_label(p, zone):
    if zone is None:
        return "no_zone_data"
    if p >= 2 * NEUTRAL_SP:
        return "compatible"
    if p <= 0.5 * NEUTRAL_SP:
        return "incompatible"
    return "less_compatible"


def build_example(example_id, i, is_known, true_species, zone, order_row, score_mat_row,
                   comp_mat_row, visual_norm_row, openset_score_val, geo_score_openset_val):
    candidates = []
    for rank, j in enumerate(order_row[:3], start=1):
        sp = classes[j]
        p_geo_rank = comp_mat_row[j]
        candidates.append(dict(
            rank=rank, species=sp, genus=class_genus.get(sp), family=class_family.get(sp),
            visual_score=round(float(visual_norm_row[j]), 4),
            geographic_score=round(float(p_geo_rank), 6),
            ranking_score=round(float(score_mat_row[j]), 4),
        ))
    proposed_sp = classes[order_row[0]]
    decision = openset_decision(openset_score_val)
    example = dict(
        example_id=example_id,
        is_known_ground_truth=bool(is_known),
        true_species=true_species,
        zone=zone,
        candidate_1=candidates[0], candidate_2=candidates[1], candidate_3=candidates[2],
        etapa1_ranking_config=f"w_geo_rank={BEST_W_RANK}",
        open_set_gate=dict(
            proposed_species=proposed_sp,
            w_geo_open_set=W_GEO_OPENSET,
            open_set_score=round(float(openset_score_val), 4),
            geo_prior_p_proposed_species=round(float(geo_score_openset_val), 6),
            geo_compatibility=geo_compat_label(geo_score_openset_val, zone),
            threshold_low_far5pct=round(THR_LOW, 4),
            threshold_high_far30pct=round(THR_HIGH, 4),
            decision=decision,
            decision_basis=(
                f"open_set_score={openset_score_val:.4f} vs THR_LOW={THR_LOW:.4f} / "
                f"THR_HIGH={THR_HIGH:.4f} (DIAGNOSTIC, ver GEO6_OPENSET_DECISION_SUMMARY.json). "
                f"especie propuesta='{proposed_sp}' tomada del top-1 de Etapa 1 "
                f"(ranking_score con w_geo_rank={BEST_W_RANK}), NO recalculada desde cero."
            ),
        ),
        score_types_note=(
            "visual_score = similitud normalizada min-max por fila sobre 41 candidatos (Etapa 1, "
            "NO probabilidad). geographic_score = prior bayesiano por zona (K=291, "
            "prior_zone_taxon_v2_clean.csv), sin normalizar (0..1 pero no probabilidad calibrada). "
            "ranking_score = combinacion de Etapa 1 ((1-w_geo_rank)*visual_score_norm_fila + "
            "w_geo_rank*geographic_score_norm_fila). open_set_score = score SEPARADO de Etapa 2 "
            "((1-0.9)*visual_norm_top1_escalar + 0.9*geo_unknownness_especie_propuesta), NO es el "
            "mismo score ni la misma normalizacion que ranking_score. genus/family = metadata "
            "contextual, NUNCA usados para ordenar ni para el gate. No se reporta "
            "calibrated_probability: no existe calibracion real (isotonic/Platt sobre holdout "
            "independiente) en ningun experimento de esta cadena (GEO2-GEO6)."
        ),
    )
    return example


merlin_examples = []
for i in sample_known_idx:
    merlin_examples.append(build_example(
        f"GEO6_MERLIN_KNOWN_{int(i):05d}", i, True, known_sci_name[i], known_zone[i],
        order_etapa1[i], (1 - BEST_W_RANK) * visual_sim_known_norm[i] + BEST_W_RANK * comp_sp_known_norm[i],
        comp_sp_known[i], visual_sim_known_norm[i], score_C[i], known_geo_score_C[i],
    ))
for i in sample_unk_idx:
    gidx = n_known + i
    merlin_examples.append(build_example(
        f"GEO6_MERLIN_UNKNOWN_{int(i):05d}", i, False, f"UNKNOWN (true={unk_species[i]}, fuera del pool KNOWN)",
        unk_zone[i], order_unk_etapa1[i],
        (1 - BEST_W_RANK) * visual_sim_unk_norm[i] + BEST_W_RANK * comp_sp_unk_norm[i],
        comp_sp_unk[i], visual_sim_unk_norm[i], score_C[gidx], unk_geo_score_C[i],
    ))

json.dump(merlin_examples, open(OUT / "GEO6_MERLIN_EXAMPLES.json", "w", encoding="utf-8"),
          indent=2, ensure_ascii=False, default=str)
print(f"GEO6_MERLIN_EXAMPLES.json escrito: {len(merlin_examples)} ejemplos "
      f"({n_known_ex} KNOWN + {n_unk_ex} UNKNOWN)")

# ===========================================================================
# COMPARACION A/B/C/D -- resumen para GEO6_COMPARISON.md
# ===========================================================================
comparison_summary = {
    "A_visual_only": {
        "ranking": {k: ranking_results[0.0][k] for k in ("top1_acc", "top3_acc", "top5_acc", "f1_macro", "mrr")},
        "openset": row_A,
    },
    "B_ranking_plus_geo_best_w": {
        "w_geo_rank": BEST_W_RANK,
        "ranking": {k: ranking_results[BEST_W_RANK][k] for k in ("top1_acc", "top3_acc", "top5_acc", "f1_macro", "mrr")},
        "openset_using_ranking_score_directly": row_B,
    },
    "C_two_stage": {
        "w_geo_rank": BEST_W_RANK, "w_geo_open_set": W_GEO_OPENSET,
        "ranking": {k: ranking_results[BEST_W_RANK][k] for k in ("top1_acc", "top3_acc", "top5_acc", "f1_macro", "mrr")},
        "openset_separate_gate": row_C,
    },
    "D_geo2_original_single_score_w0.9": {
        "ranking_using_same_score": {},  # completado abajo
        "openset": row_D,
        "caveat": D_oracle_caveat,
    },
}
# D's ranking metrics: score con w=0.9 aplicado al ranking (ya calculado en GEO5, aqui recomputado
# con la MISMA matriz de 41 candidatas x 7475 KNOWN, para comparabilidad directa con A/B/C)
score_D_ranking_mat = (1 - W_GEO_OPENSET) * visual_sim_known_norm + W_GEO_OPENSET * comp_sp_known_norm
res_D_ranking = rank_metrics(score_D_ranking_mat, y_true_idx)
comparison_summary["D_geo2_original_single_score_w0.9"]["ranking_using_same_score"] = {
    k: res_D_ranking[k] for k in ("top1_acc", "top3_acc", "top5_acc", "f1_macro", "mrr")
}
comparison_summary["resolves_geo5_conflict"] = {
    "geo5_conflict_description": (
        "GEO-5 encontro que w_geo=0.9 (config D) es HELPFUL para open-set (AUROC 0.573->0.701) "
        "pero HARMFUL para ranking cerrado (Top-1 0.585->0.411), usando el MISMO score para ambas "
        "tareas."
    ),
    "does_two_stage_resolve_it": bool(
        comparison_summary["C_two_stage"]["ranking"]["top1_acc"] >= comparison_summary["A_visual_only"]["ranking"]["top1_acc"]
        and row_C["AUROC"] > row_A["AUROC"]
    ),
    "C_top1_vs_A_top1": comparison_summary["C_two_stage"]["ranking"]["top1_acc"] - comparison_summary["A_visual_only"]["ranking"]["top1_acc"],
    "C_top1_vs_D_top1": comparison_summary["C_two_stage"]["ranking"]["top1_acc"] - comparison_summary["D_geo2_original_single_score_w0.9"]["ranking_using_same_score"]["top1_acc"],
    "C_auroc_vs_A_auroc": row_C["AUROC"] - row_A["AUROC"],
    "C_auroc_vs_D_auroc": row_C["AUROC"] - row_D["AUROC"],
}
json.dump(comparison_summary, open(OUT / "GEO6_COMPARISON_SUMMARY.json", "w", encoding="utf-8"),
          indent=2, ensure_ascii=False, default=str)
print("\n=== RESUMEN COMPARACION A/B/C/D ===")
print(json.dumps(comparison_summary["resolves_geo5_conflict"], indent=2, default=str))

# ===========================================================================
# REPRODUCIBILITY MANIFEST
# ===========================================================================
import hashlib


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


input_files = [
    OUT / "baseline_reproduction_v2.json",
    OUT / "reproduced_scores_v2.npz",
    OUT / "prior_zone_taxon_v2_clean.csv",
    OUT / "prior_zone_taxon_v2_clean_manifest.json",
    OUT / "GEO2_WEIGHT_SWEEP.csv",
    OUT / "GEO3_OPERATING_POINTS.csv",
    BASE / "validation/fase16_clean_open_set/clean_known_manifest.json",
    BASE / "validation/fase18_clean_calibration/calibration_results.json",
    BASE / "evaluation/fase13/embeddings/reference_embeddings.npz",
    BASE / "evaluation/fase13/embeddings/train_embeddings.npz",
]
input_hashes = {str(p.relative_to(BASE)): sha256_of(p) for p in input_files}

from datetime import datetime, timezone
repro_manifest = {
    "phase": "GEO-6",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "seed": SEED,
    "gate0": {"official_auroc": OFFICIAL_AUROC, "reproduced_auroc": reproduced_auroc,
              "abs_diff": abs_diff, "passed": gate0_passed},
    "etapa1_w_geo_rank_sweep": W_GEO_RANK_SWEEP,
    "etapa1_best_w_geo_rank": BEST_W_RANK,
    "etapa1_selection_criterion": "Top-1 > Top-3 > MRR",
    "etapa2_w_geo_open_set": W_GEO_OPENSET,
    "threshold_status": "DIAGNOSTIC",
    "threshold_low_far5pct": THR_LOW, "threshold_high_far30pct": THR_HIGH,
    "bootstrap_protocol": "1000 iter, seed=42, estratificado por individuo (identico a GEO2/GEO3)",
    "input_file_hashes_sha256": input_hashes,
    "hard_rules_confirmed": [
        "no genus/family used in any score (context-only in Merlin output)",
        "no fine-tuning / no new embeddings / no new bulk API calls",
        "GEO2_*/GEO3_*/GEO4_*/GEO5_* and regional_packages/ANTIOQUIA/v1.0.0/ untouched (read-only reference)",
        "prior_zone_taxon_v1.csv original untouched (used v2_clean only)",
        "no commit/push performed by this script",
    ],
    "candidate_pool_choice": "41 species with centroids (same as GEO2/3/4/5), NOT the 33/21 subset "
                              "restricted to Antioquia catalog -- documented in GEO6_RANKING_RESULTS.json",
}
json.dump(repro_manifest, open(OUT / "GEO6_REPRODUCIBILITY_MANIFEST.json", "w", encoding="utf-8"),
          indent=2, ensure_ascii=False, default=str)

print("\nDONE -- GEO6 ranking + open-set + merlin examples + manifest escritos.")
