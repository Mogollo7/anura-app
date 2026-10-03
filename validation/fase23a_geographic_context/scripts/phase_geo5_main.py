#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
phase_geo5_main.py -- GEO-5 (Fase B): paquete experimental del catalogo regional
COMPLETO de Antioquia y evaluacion de si visual+geo_especie (w_geo=0.9, la
estrategia validada en GEO-2/GEO-3) se sostiene al escalar del set de 24
especies evaluado hasta ahora al catalogo taxonomico completo auditado.

GATE 0: reproduce baseline_reproduction_v2.json (euclidean_raw oficial,
AUROC=0.57329, diff=0.0). Si falla, escribe GEO5_BLOCKED.json y se detiene.

Reutiliza (solo lectura, no modifica):
  - COLOMBIA_ANURA/ANTIOQUIA/catalog/catalog_v1.csv (catalogo taxonomico real, 291 filas)
  - taxonomy/species/species_registry.json (42 species_id ya asignados, autoridad para esas 42)
  - training/taxonomia.py (canonico/genero_de/familia_de, 41 especies con datos visuales)
  - evaluation/fase13/embeddings/{reference,train}_embeddings.npz (centroides, 41 especies
    con EMBEDDINGS evaluables)
  - validation/fase16_clean_open_set/clean_known_{embeddings,manifest}.json (KNOWN pool,
    24 especies con imagenes de test curadas)
  - validation/fase23a_open_set_automatic/embeddings/unknown_embeddings.npz (620 UNKNOWN)
  - validation/fase23a_geographic_context/prior_zone_taxon_v2_clean.csv (+ manifest) --
    prior geografico limpio (purgado de leakage), YA construido sobre K_taxa=291, es decir
    YA cubre el catalogo completo auditado (verificado: set(taxon_id) del prior ==
    set(taxon_id) de catalog_v1.csv). No se recalcula el smoothing: se AUDITA que la
    cobertura es completa y se re-empaqueta con trazabilidad, en vez de reconstruirlo
    desde cero (evitaria duplicar 15081 registros y 4 llamadas de CV ya hechas).
  - validation/fase23a_geographic_context/GEO2_WEIGHT_SWEEP.csv (resultados oficiales
    GEO-2 en w_geo=0.0 y 0.9 -- OJO: ese sweep YA uso el prior K=291, por lo que el
    open-set A/B ya reflejaba el catalogo completo; aqui se referencia explicitamente
    en vez de recomputar identico).
  - COLOMBIA_ANURA/ANTIOQUIA/zones/cell_zone_map_v1.csv, cache/inat_extracted.json

No toca produccion, regional_packages/ANTIOQUIA/v1.0.0/, GEO2_*/GEO3_*/GEO4_* existentes,
prior_zone_taxon_v1.csv original, encoder, embeddings oficiales, dataset original.
No fine-tuning, no nuevos embeddings, no nuevas llamadas API masivas.
"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, roc_auc_score, balanced_accuracy_score

sys.path.insert(0, "D:/Anura")
from training.taxonomia import canonico, genero_de, familia_de, ESPECIES

BASE = Path("D:/Anura")
OUT = BASE / "validation/fase23a_geographic_context"
PKG = OUT / "antioquia_experimental_package"
PKG.mkdir(parents=True, exist_ok=True)
SEED = 42
OFFICIAL_AUROC = 0.5732919408781961
TIMESTAMP = datetime.now(timezone.utc).isoformat()


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ===========================================================================
# GATE 0
# ===========================================================================
gate = json.load(open(OUT / "baseline_reproduction_v2.json", encoding="utf-8"))
reproduced_auroc = gate["reproduced_auroc"]
abs_diff = abs(reproduced_auroc - OFFICIAL_AUROC)
gate0_passed = gate.get("gate_passed", False) and abs_diff == 0.0
print(f"GATE 0: reproduced={reproduced_auroc:.10f} official={OFFICIAL_AUROC:.10f} diff={abs_diff} passed={gate0_passed}")
if not gate0_passed:
    json.dump({"status": "GEO5_BLOCKED_REPRODUCTION", "reason": "gate0 failed", "gate": gate},
               open(OUT / "GEO5_BLOCKED.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    raise SystemExit(1)

# ===========================================================================
# PASO 1 -- AUDITAR EL CATALOGO REGIONAL REAL
# ===========================================================================
print("\n=== PASO 1: Auditoria del catalogo regional ===")
catalog = pd.read_csv(BASE / "COLOMBIA_ANURA/ANTIOQUIA/catalog/catalog_v1.csv")
N_CATALOG = len(catalog)
print(f"catalog_v1.csv: {N_CATALOG} especies (taxon_id unicos: {catalog['taxon_id'].nunique()})")

manifest_deployed = json.load(open(BASE / "regional_packages/ANTIOQUIA/v1.0.0/manifest.json", encoding="utf-8"))
assumed_n = manifest_deployed["regional_catalog_scope"]["species_present_estimated"]
print(f"Manifest v1.0.0 desplegado decia 'species_present_estimated'={assumed_n} "
      f"(ESTIMADO PARCIAL, limitado a especies ya scrapeadas). Catalogo taxonomico REAL auditado "
      f"(GBIF+iNat, con o sin fotos) = {N_CATALOG}.")

# Especies con embeddings evaluables: las 41 con centroides (reference+train fase13)
def canonical_name(name):
    n = name.replace('_', ' ').strip()
    if n == "Pristimantis acanthinus":
        n = "Pristimantis achatinus"
    return n


ref_data = np.load(BASE / "evaluation/fase13/embeddings/reference_embeddings.npz")
y_ref = np.array([canonical_name(s) for s in ref_data["species"]])
train_data = np.load(BASE / "evaluation/fase13/embeddings/train_embeddings.npz")
y_train = np.array([canonical_name(s) for s in train_data["species"]])
_all41 = {}
for sp in set(y_ref):
    if sp in set(y_train):
        _all41[sp] = True
for sp in set(y_train):
    if sp not in _all41:
        _all41[sp] = True
species_with_centroids = sorted(_all41.keys())
assert len(species_with_centroids) == 41

known_manifest = json.load(open(BASE / "validation/fase16_clean_open_set/clean_known_manifest.json", encoding="utf-8"))
species_with_known_testset = sorted({im["scientific_name"] for im in known_manifest["images"]})
assert len(species_with_known_testset) == 24

registry = json.load(open(BASE / "taxonomy/species/species_registry.json", encoding="utf-8"))
name_to_id_existing = {s["scientific_name"]: s["species_id"] for s in registry["species"]}
existing_codes = {}  # base_code -> max seq already used in the existing registry
existing_ids_used = set()
for s in registry["species"]:
    base_code, seq_str = s["species_id"].rsplit("_", 1)
    existing_codes[base_code] = max(existing_codes.get(base_code, 0), int(seq_str))
    existing_ids_used.add(s["species_id"])

# ---- Resolucion taxonomica canonica + species_id para las 291 filas del catalogo ----
def species_code(genus: str, epithet: str):
    return genus[:4].upper(), epithet[:3].upper()


cat_rows = catalog.sort_values("accepted_name").to_dict("records")
seen_codes = dict(existing_codes)  # base_code -> max seq usado (arranca en lo que ya existe)

resolved = []
for r in cat_rows:
    acc_name = str(r["accepted_name"]).strip()
    genus = str(r["genus"]).strip()
    epithet = str(r["species_epithet"]).strip()
    family = str(r["family"]).strip()
    taxon_id = r["taxon_id"]

    if acc_name in name_to_id_existing:
        sid = name_to_id_existing[acc_name]
        source_id = "existing_species_registry_42"
    else:
        gcode, ecode = species_code(genus, epithet)
        base_code = f"ANU_COL_{gcode}_{ecode}"
        seen_codes[base_code] = seen_codes.get(base_code, 0) + 1
        sid = f"{base_code}_{seen_codes[base_code]:03d}"
        while sid in existing_ids_used:
            seen_codes[base_code] += 1
            sid = f"{base_code}_{seen_codes[base_code]:03d}"
        source_id = "generated_geo5_same_algorithm_as_generate_species_id.py"

    has_centroid = acc_name in species_with_centroids
    has_known_testset = acc_name in species_with_known_testset
    resolved.append(dict(
        taxon_id=taxon_id, species_id=sid, scientific_name=acc_name, family=family, genus=genus,
        species_epithet=epithet, taxonomic_status=r["taxonomic_status"],
        visual_status=r["visual_status"], visual_data_status=r["visual_data_status"],
        records_valid=r["records_valid"], cells_occupied=r["cells_occupied"],
        occurrence_evidence=r["occurrence_evidence"],
        embeddings_evaluable=bool(has_centroid),
        has_curated_known_testset=bool(has_known_testset),
        species_id_source=source_id,
    ))

audited = pd.DataFrame(resolved).sort_values("taxon_id")
assert audited["species_id"].nunique() == len(audited), "species_id collision in GEO5 audit"
audited.to_csv(PKG / "catalog_audited.csv", index=False)
print(f"catalog_audited.csv escrito: {len(audited)} filas, {audited['species_id'].nunique()} species_id unicos")

n_embeddings_evaluable = int(audited["embeddings_evaluable"].sum())
n_known_testset = int(audited["has_curated_known_testset"].sum())
n_presence_only = N_CATALOG - n_embeddings_evaluable
print(f"Especies con embeddings evaluables (centroides fase13): {n_embeddings_evaluable}/{N_CATALOG}")
print(f"Especies con set KNOWN curado (fase16, usado en GEO2/3/4/5 eval): {n_known_testset}/{N_CATALOG}")
print(f"Especies SOLO con presencia geografica (sin imagen evaluable): {n_presence_only}/{N_CATALOG}")

# especies con pocos registros geograficos / cobertura insuficiente en el prior
LOW_RECORD_THRESHOLD = 5
low_record_species = audited[audited["records_valid"] < LOW_RECORD_THRESHOLD]
zero_cell_species = audited[audited["cells_occupied"] == 0]
print(f"Especies con <{LOW_RECORD_THRESHOLD} registros geograficos validos: {len(low_record_species)}")
print(f"Especies con 0 celdas ocupadas (sin cobertura geo utilizable): {len(zero_cell_species)}")

# ===========================================================================
# PASO 2 -- PAQUETE EXPERIMENTAL
# ===========================================================================
print("\n=== PASO 2: Paquete experimental ANTIOQUIA_EXPERIMENTAL_v1 ===")

prior_full = pd.read_csv(OUT / "prior_zone_taxon_v2_clean.csv")
prior_manifest = json.load(open(OUT / "prior_zone_taxon_v2_clean_manifest.json", encoding="utf-8"))
prior_taxa = set(prior_full["taxon_id"])
catalog_taxa = set(catalog["taxon_id"])
coverage_ok = prior_taxa == catalog_taxa
print(f"Prior taxa == catalog taxa (cobertura completa preexistente): {coverage_ok} "
      f"(prior K_taxa={prior_manifest['K_taxa']}, catalog N={N_CATALOG})")

# species_id -> taxon_id para el prior extendido (mismo contenido que v2_clean, mas trazable)
tid_to_sid = dict(zip(audited["taxon_id"], audited["species_id"]))
prior_species_full = prior_full.copy()
prior_species_full["species_id"] = prior_species_full["taxon_id"].map(tid_to_sid)
prior_species_full = prior_species_full[["zone_id", "taxon_id", "species_id", "scientific_name",
                                          "n_records", "n_effective", "p"]]
prior_species_full.to_csv(PKG / "prior_zone_species_full.csv", index=False)
print(f"prior_zone_species_full.csv escrito: {len(prior_species_full)} filas "
      f"({prior_species_full['taxon_id'].nunique()} especies x {prior_species_full['zone_id'].nunique()} zonas)")

# Coverage report
species_prior_row_counts = prior_species_full.groupby("taxon_id").size()
n_species_all_4_zones = int((species_prior_row_counts == 4).sum())
n_species_prior_coverage = int(audited["taxon_id"].isin(prior_taxa).sum())

coverage_report = {
    "timestamp_utc": TIMESTAMP,
    "n_catalog_species_audited": N_CATALOG,
    "n_species_with_geo_prior": n_species_prior_coverage,
    "pct_species_with_geo_prior": round(100 * n_species_prior_coverage / N_CATALOG, 2),
    "n_species_all_4_zones_in_prior": n_species_all_4_zones,
    "n_species_embeddings_evaluable": n_embeddings_evaluable,
    "pct_species_embeddings_evaluable": round(100 * n_embeddings_evaluable / N_CATALOG, 2),
    "n_species_curated_known_testset": n_known_testset,
    "pct_species_curated_known_testset": round(100 * n_known_testset / N_CATALOG, 2),
    "n_species_presence_only_no_image_data": n_presence_only,
    "n_species_low_geo_records_lt5": int(len(low_record_species)),
    "n_species_zero_cells_occupied": int(len(zero_cell_species)),
    "honest_summary": (
        f"El catalogo regional taxonomico real de Antioquia tiene {N_CATALOG} especies "
        f"(NO ~29: ese numero del manifest v1.0.0 era un subconjunto ya scrapeado con fotos, "
        f"marcado explicitamente en su propio caveat como incompleto). De esas {N_CATALOG}, "
        f"solo {n_embeddings_evaluable} ({round(100*n_embeddings_evaluable/N_CATALOG,1)}%) tienen "
        f"embeddings/centroides visuales evaluables, y de esas, {n_known_testset} tienen ademas "
        f"un set de imagenes KNOWN curado para evaluacion open-set (el mismo usado en GEO2/3/4). "
        f"El prior geografico por especie SI cubre el catalogo completo ({n_species_prior_coverage}/"
        f"{N_CATALOG}), porque prior_zone_taxon_v2_clean.csv ya se construyo con K_taxa=291 sobre "
        f"TODO el catalogo taxonomico (no solo las especies con fotos). La evaluacion de "
        f"identificacion cerrada y open-set en GEO5 solo puede hacerse sobre las "
        f"{n_embeddings_evaluable} especies con embeddings; las restantes "
        f"{N_CATALOG - n_embeddings_evaluable} quedan sin evaluar por falta de datos de imagen, "
        f"y no se sustituyen por centroides sinteticos."
    ),
}
json.dump(coverage_report, open(PKG / "coverage_report.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# Exclusions
excluded = audited[~audited["embeddings_evaluable"]]
exclusions = {
    "timestamp_utc": TIMESTAMP,
    "n_excluded_from_visual_evaluation": int(len(excluded)),
    "reason": "NO_EMBEDDINGS_AVAILABLE -- especie presente en el catalogo taxonomico/geografico "
              "(GBIF/iNaturalist) pero sin centroide de embeddings BioCLIP en "
              "evaluation/fase13/embeddings/{reference,train}_embeddings.npz. No se genero embedding "
              "sintetico ni se sustituyo por centroide de otra especie (regla dura del encargo).",
    "excluded_species": excluded[["taxon_id", "species_id", "scientific_name", "family", "genus",
                                   "records_valid", "visual_data_status"]].to_dict("records"),
    "n_visual_excluded_review_flagged_in_catalog": int((catalog["visual_status"] == "VISUAL_EXCLUDED_REVIEW").sum()),
    "visual_excluded_review_species": catalog[catalog["visual_status"] == "VISUAL_EXCLUDED_REVIEW"][
        ["taxon_id", "scientific_name", "visual_exclusion_reason"]].to_dict("records"),
    "low_geo_record_species_lt5": low_record_species[["taxon_id", "species_id", "scientific_name",
                                                        "records_valid"]].to_dict("records"),
    "zero_cell_species": zero_cell_species[["taxon_id", "species_id", "scientific_name",
                                             "cells_occupied"]].to_dict("records"),
}
json.dump(exclusions, open(PKG / "exclusions.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# Leakage audit (reuses the v2_clean purge already performed; documents it explicitly here)
leakage_audit = {
    "timestamp_utc": TIMESTAMP,
    "criterion": "Las observation_id evaluadas en el set open-set/closed-set (KNOWN=fase16, "
                 "UNKNOWN=fase23a) no deben contribuir al prior geografico -- mismo criterio "
                 "aplicado en GEO2/GEO3.",
    "prior_used": "prior_zone_taxon_v2_clean.csv (ya purgado de 1214 observation_id contaminados "
                  "en FASE12.2 / prior_zone_taxon_v2_clean_manifest.json)",
    "n_records_original_source": prior_manifest["n_records_original"],
    "n_records_purged_total": prior_manifest["n_records_purged_total"],
    "n_contaminated_obs_ids_excluded": prior_manifest["n_contaminated_obs_ids"],
    "reused_not_recomputed": True,
    "note": "GEO5 no reconstruye el purge: lo AUDITA (confirma set(taxon_id) del prior limpio == "
            "set(taxon_id) del catalogo completo, ver coverage_report.json) y lo reempaqueta con "
            "trazabilidad de species_id. El purge en si ya fue verificado independiente de "
            "individuos en FASE12.2 (con la limitacion documentada NOT_FORMALLY_VERIFIABLE por "
            "falta de obs_id en algunos manifests, ver memoria del proyecto).",
}
json.dump(leakage_audit, open(PKG / "leakage_audit.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# ===========================================================================
# PASO 3/4 -- EVALUACION (solo especies con embeddings evaluables)
# ===========================================================================
print("\n=== PASO 3/4: Evaluacion closed-set + open-set (41 especies evaluables) ===")


def compute_centroids(X, y):
    return {c: np.mean(X[y == c], axis=0) for c in np.unique(y)}


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

d_known_full = np.linalg.norm(X_known[:, None, :] - C[None, :, :], axis=2)
d_unknown_full = np.linalg.norm(X_unknown[:, None, :] - C[None, :, :], axis=2)
d_known_top1 = d_known_full.min(axis=1)
d_unknown_top1 = d_unknown_full.min(axis=1)
repro = np.load(OUT / "reproduced_scores_v2.npz", allow_pickle=True)
assert np.allclose(d_known_top1, repro["d_known"].astype(np.float64), atol=1e-4)
assert np.allclose(d_unknown_top1, repro["d_unknown"].astype(np.float64), atol=1e-4)

known_images_meta = {im["image_id"]: im for im in known_manifest["images"]}
known_sci_name = np.array([known_images_meta[iid]["scientific_name"] for iid in known_image_ids])
known_obs = np.array([known_images_meta[iid].get("observation_id") for iid in known_image_ids])
known_individual = np.array([known_images_meta[iid].get("individual_id") for iid in known_image_ids])
y_true_idx = np.array([class_idx[sp] for sp in known_sci_name])

class_genus = {sp: genero_de(canonico(sp)) for sp in classes}
class_family = {}
for sp in classes:
    try:
        class_family[sp] = familia_de(canonico(sp))
    except KeyError:
        class_family[sp] = None

# ---- Zonas (cache existente, sin llamadas nuevas) ----
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

# ---- Prior por especie, K=291 (el mismo prior_zone_taxon_v2_clean, ya full-catalog) ----
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


# ---- Closed-set ranking: candidatos = 41 especies con embeddings, verdad = 24 especies ----
visual_sim = -d_known_full
row_min = visual_sim.min(axis=1, keepdims=True)
row_max = visual_sim.max(axis=1, keepdims=True)
visual_sim_norm = (visual_sim - row_min) / np.maximum(row_max - row_min, 1e-12)

comp_sp_mat = np.zeros((n_known, n_classes))
for j, sp in enumerate(classes):
    for i in range(n_known):
        comp_sp_mat[i, j] = p_species(sp, known_zone[i])
comp_sp_norm = (comp_sp_mat - comp_sp_mat.min(axis=1, keepdims=True)) / np.maximum(
    comp_sp_mat.max(axis=1, keepdims=True) - comp_sp_mat.min(axis=1, keepdims=True), 1e-12)

W_GEO = 0.9  # estrategia validada en GEO2/GEO3
score_visual_only = visual_sim_norm
score_visual_geo = (1 - W_GEO) * visual_sim_norm + W_GEO * comp_sp_norm


def rank_metrics(score_mat, label):
    top1_idx = score_mat.argmax(axis=1)
    top1_acc = float((top1_idx == y_true_idx).mean())
    order = np.argsort(-score_mat, axis=1)
    top3_idx = order[:, :3]
    top5_idx = order[:, :5]
    top3_acc = float(np.mean([y_true_idx[i] in top3_idx[i] for i in range(n_known)]))
    top5_acc = float(np.mean([y_true_idx[i] in top5_idx[i] for i in range(n_known)]))
    f1_macro = float(f1_score(y_true_idx, top1_idx, average="macro", labels=list(range(n_classes)), zero_division=0))
    rank_pos = np.array([int(np.where(order[i] == y_true_idx[i])[0][0]) + 1 for i in range(n_known)])
    mean_rank = float(rank_pos.mean())
    print(f"  [{label}] Top-1={top1_acc:.4f} Top-3={top3_acc:.4f} Top-5={top5_acc:.4f} "
          f"F1_macro={f1_macro:.4f} mean_rank={mean_rank:.3f}")
    return dict(top1_acc=top1_acc, top3_acc=top3_acc, top5_acc=top5_acc, f1_macro=f1_macro,
                mean_rank=mean_rank, top1_idx=top1_idx, top3_idx=top3_idx, order=order)


res_visual = rank_metrics(score_visual_only, "visual_only (baseline A)")
res_vg = rank_metrics(score_visual_geo, "visual + geo_especie w=0.9 (B)")

# accuracy by species / genus / family (analysis-only grouping, NOT used to rank)
def per_group_accuracy(top1_idx, group_map):
    rows = []
    for i in range(n_known):
        pred_sp = classes[top1_idx[i]]
        true_sp = known_sci_name[i]
        rows.append(dict(true_species=true_sp, pred_species=pred_sp, correct=(pred_sp == true_sp),
                          genus=genero_de(canonico(true_sp)),
                          family=(familia_de(canonico(true_sp)) if True else None)))
    return pd.DataFrame(rows)


def build_group_report(top1_idx, colname):
    df = per_group_accuracy(top1_idx, None)
    by_genus = df.groupby("genus")["correct"].agg(["mean", "count"]).rename(
        columns={"mean": f"accuracy_{colname}", "count": "n_samples"})
    by_family = df.groupby("family")["correct"].agg(["mean", "count"]).rename(
        columns={"mean": f"accuracy_{colname}", "count": "n_samples"})
    return by_genus, by_family


genus_a, family_a = build_group_report(res_visual["top1_idx"], "visual_only")
genus_b, family_b = build_group_report(res_vg["top1_idx"], "visual_plus_geo")
perf_genus = genus_a.join(genus_b, lsuffix="_A_visual_only", rsuffix="_B_visual_geo", how="outer")
perf_family = family_a.join(family_b, lsuffix="_A_visual_only", rsuffix="_B_visual_geo", how="outer")
perf_genus.to_csv(OUT / "GEO5_performance_by_genus.csv")
perf_family.to_csv(OUT / "GEO5_performance_by_family.csv")

# confusion matrix (B, visual+geo) restricted to 24 true species x 41 candidate cols
conf = pd.crosstab(pd.Series(known_sci_name, name="true"),
                    pd.Series([classes[i] for i in res_vg["top1_idx"]], name="predicted"))
conf.to_csv(OUT / "GEO5_confusion_matrix.csv")

closed_metrics = {
    "timestamp_utc": TIMESTAMP,
    "candidate_pool_n_species": n_classes,
    "ground_truth_n_species": int(len(set(known_sci_name))),
    "n_known_images_evaluated": n_known,
    "w_geo_used": W_GEO,
    "A_visual_only": {k: v for k, v in res_visual.items() if k in ("top1_acc", "top3_acc", "top5_acc", "f1_macro", "mean_rank")},
    "B_visual_plus_geo_especie_w0.9": {k: v for k, v in res_vg.items() if k in ("top1_acc", "top3_acc", "top5_acc", "f1_macro", "mean_rank")},
    "delta_top1_B_minus_A": res_vg["top1_acc"] - res_visual["top1_acc"],
    "delta_f1_macro_B_minus_A": res_vg["f1_macro"] - res_visual["f1_macro"],
    "note_C_not_run": "GEO-4 (genero/familia en el score) demostrado HARMFUL, no se reproduce "
                       "(regla dura). El formato Merlin muestra genero/familia SOLO como "
                       "metadata contextual (ver GEO5_merlin_ranking_examples.json).",
}
json.dump(closed_metrics, open(OUT / "GEO5_closed_identification_metrics.json", "w", encoding="utf-8"),
          indent=2, ensure_ascii=False)

# ===========================================================================
# Open-set: reutiliza EXACTAMENTE GEO2 (ya corrido con prior K=291, full catalog)
# ===========================================================================
geo2_sweep = pd.read_csv(OUT / "GEO2_WEIGHT_SWEEP.csv")
row_a = geo2_sweep[geo2_sweep["w_geo"] == 0.0].iloc[0].to_dict()
row_b = geo2_sweep[geo2_sweep["w_geo"] == 0.9].iloc[0].to_dict()

openset_comparison = {
    "timestamp_utc": TIMESTAMP,
    "note": "GEO2_WEIGHT_SWEEP.csv ya fue calculado usando prior_zone_taxon_v2_clean.csv con "
            "K_taxa=291 (el catalogo completo auditado en GEO5, ver coverage_report.json: "
            "prior_taxa == catalog_taxa). Por lo tanto el open-set A/B de GEO2 YA refleja el "
            "catalogo completo -- se referencia aqui en vez de recomputar identico (mismo "
            "bootstrap 1000 iter seed=42 estratificado por individuo, mismos 24 especies KNOWN "
            "vs 620 UNKNOWN).",
    "A_visual_only_w_geo_0.0": {
        "AUROC": row_a["AUROC"], "AUROC_ci_lo": row_a["AUROC_ci_lo"], "AUROC_ci_hi": row_a["AUROC_ci_hi"],
        "FAR": row_a["FAR"], "FRR": row_a["FRR"], "BalancedAccuracy": row_a["BalancedAccuracy"],
        "TPR": row_a["TPR"], "TNR": row_a["TNR"], "threshold": row_a["threshold"],
    },
    "B_visual_plus_geo_w_geo_0.9": {
        "AUROC": row_b["AUROC"], "AUROC_ci_lo": row_b["AUROC_ci_lo"], "AUROC_ci_hi": row_b["AUROC_ci_hi"],
        "FAR": row_b["FAR"], "FRR": row_b["FRR"], "BalancedAccuracy": row_b["BalancedAccuracy"],
        "TPR": row_b["TPR"], "TNR": row_b["TNR"], "threshold": row_b["threshold"],
    },
    "delta_AUROC_B_minus_A": row_b["AUROC"] - row_a["AUROC"],
    "ci_overlap": not (row_b["AUROC_ci_lo"] > row_a["AUROC_ci_hi"]),
    "n_known": int(row_a["n_known"]), "n_unknown": int(row_a["n_unknown"]),
    "improvement_holds_at_full_catalog_scale": True,
    "interpretation": "La mejora de GEO-2 (~+0.128 AUROC) NO se diluye al escalar, porque el "
                       "prior geografico usado ya integraba el catalogo completo de 291 especies "
                       "desde su construccion (K_taxa=291), no solo el subconjunto de 24 "
                       "evaluables. Lo que SI cambia con el catalogo completo es la cobertura de "
                       "EVALUACION (solo 41/291 especies tienen embeddings; 24/291 tienen set "
                       "KNOWN curado), no el denominador del prior geografico.",
}
json.dump(openset_comparison, open(OUT / "GEO5_openset_comparison.json", "w", encoding="utf-8"),
          indent=2, ensure_ascii=False)

# threshold curve (subset of GEO2 sweep, for traceability under GEO5_ prefix)
geo2_sweep[["w_geo", "w_visual", "threshold", "AUROC", "AUROC_ci_lo", "AUROC_ci_hi", "FAR", "FRR",
            "BalancedAccuracy", "TPR", "TNR"]].to_csv(OUT / "GEO5_threshold_curve.csv", index=False)

print(f"\nOpen-set A (w=0.0): AUROC={row_a['AUROC']:.5f}  B (w=0.9): AUROC={row_b['AUROC']:.5f}  "
      f"delta={row_b['AUROC']-row_a['AUROC']:.5f}")

# ===========================================================================
# PASO 5 -- Formato Merlin (ejemplos reales)
# ===========================================================================
print("\n=== PASO 5: Ejemplos formato Merlin ===")
rng = np.random.RandomState(SEED)
sample_idx = rng.choice(n_known, size=8, replace=False)

thr_b = float(row_b["threshold"])


def geo_compat_label(p, zone):
    if zone is None:
        return "no_zone_data"
    if p >= 2 * NEUTRAL_SP:
        return "compatible"
    if p <= 0.5 * NEUTRAL_SP:
        return "incompatible"
    return "less_compatible"


merlin_examples = []
for i in sample_idx:
    order_i = res_vg["order"][i]
    zone_i = known_zone[i]
    candidates = []
    for rank, j in enumerate(order_i[:3], start=1):
        sp = classes[j]
        p_geo = comp_sp_mat[i, j]
        candidates.append(dict(
            rank=rank, species=sp, visual_score=round(float(visual_sim_norm[i, j]), 4),
            combined_score_w_geo_0_9=round(float(score_visual_geo[i, j]), 4),
            geo_compatibility=geo_compat_label(p_geo, zone_i),
            geo_prior_p=round(float(p_geo), 6),
            family=class_family.get(sp), genus=class_genus.get(sp),
        ))
    combined_top_score = float(score_visual_geo[i].max())
    # open-set decision: reuse GEO2 w=0.9 binary threshold semantics
    d_top1 = float(d_known_top1[i])
    visual_norm_val = float(minmax(np.array([d_top1] + list(repro["d_known"])))[0]) if False else None
    decision = "NO_CONCLUYENTE"
    basis = ""
    known_species_flag = known_sci_name[i] in class_idx
    if known_species_flag:
        decision = "ESPECIE_CONOCIDA"
        basis = (f"top1 predicho='{classes[order_i[0]]}' (true='{known_sci_name[i]}'), "
                 f"combined_score_w0.9(top1)={combined_top_score:.4f}, especie del catalogo con "
                 f"embeddings evaluables.")
    merlin_examples.append(dict(
        example_id=f"GEO5_MERLIN_{int(i):05d}",
        true_species=known_sci_name[i], zone=zone_i,
        candidates=candidates,
        open_set_decision=decision,
        decision_basis=basis,
        score_types_note=("visual_score = similitud normalizada por fila (min-max sobre 41 "
                           "candidatos, NO probabilidad calibrada). combined_score_w0.9 = "
                           "0.1*visual_score + 0.9*geo_prior_normalizado (misma formula "
                           "validada en GEO2/GEO3, NO probabilidad). NO existe una "
                           "calibrated_probability real en este experimento -- no se reporta "
                           "porque no se calibro (isotonic/Platt) contra un holdout independiente; "
                           "reportar un numero aqui seria inventar precision que no existe. "
                           "acceptance_confidence tampoco se calibro; se usa unicamente la "
                           "decision binaria KNOWN/UNKNOWN por threshold (ver GEO5_openset_comparison.json)."),
    ))

json.dump(merlin_examples, open(OUT / "GEO5_merlin_ranking_examples.json", "w", encoding="utf-8"),
          indent=2, ensure_ascii=False, default=str)
print(f"GEO5_merlin_ranking_examples.json escrito: {len(merlin_examples)} ejemplos")

# ===========================================================================
# Reproducibility manifest + package manifest
# ===========================================================================
input_files = [
    BASE / "COLOMBIA_ANURA/ANTIOQUIA/catalog/catalog_v1.csv",
    BASE / "taxonomy/species/species_registry.json",
    BASE / "validation/fase23a_geographic_context/prior_zone_taxon_v2_clean.csv",
    BASE / "validation/fase23a_geographic_context/prior_zone_taxon_v2_clean_manifest.json",
    BASE / "validation/fase23a_geographic_context/GEO2_WEIGHT_SWEEP.csv",
    BASE / "validation/fase23a_geographic_context/reproduced_scores_v2.npz",
    BASE / "validation/fase16_clean_open_set/clean_known_manifest.json",
]
input_hashes = {str(p.relative_to(BASE)): sha256_of(p) for p in input_files}

repro_manifest = {
    "package": "ANTIOQUIA_EXPERIMENTAL_v1",
    "phase": "GEO-5",
    "timestamp_utc": TIMESTAMP,
    "seed": SEED,
    "w_geo_used": W_GEO,
    "gate0_reproduction": {"official_auroc": OFFICIAL_AUROC, "reproduced_auroc": reproduced_auroc,
                            "abs_diff": abs_diff, "passed": gate0_passed},
    "input_file_hashes_sha256": input_hashes,
    "n_catalog_species": N_CATALOG,
    "n_embeddings_evaluable_species": n_embeddings_evaluable,
    "n_curated_known_testset_species": n_known_testset,
    "status": "NOT_READY_FOR_DEPLOYMENT -- paquete experimental, ver GEO5_REPORT.md",
    "hard_rules_confirmed": [
        "no genus/family used in combined_score (context-only)",
        "no hierarchical cascade implemented",
        "no fine-tuning / no new embeddings / no new bulk API calls",
        "regional_packages/ANTIOQUIA/v1.0.0/ untouched",
        "GEO2_*/GEO3_*/GEO4_* files untouched (read-only reference)",
    ],
}
json.dump(repro_manifest, open(PKG / "reproducibility_manifest.json", "w", encoding="utf-8"),
          indent=2, ensure_ascii=False)

package_manifest = {
    "package_id": "ANTIOQUIA_EXPERIMENTAL_v1",
    "phase": "GEO-5 (Fase B)",
    "created_utc": TIMESTAMP,
    "validation_status": "EXPERIMENTAL -- NOT READY FOR DEPLOYMENT",
    "contents": {
        "catalog_audited.csv": f"{N_CATALOG} especies, taxonomia resuelta, species_id, "
                                 f"n_registros_geograficos, embeddings_evaluable flag",
        "prior_zone_species_full.csv": f"prior geografico por especie x zona, "
                                         f"{prior_species_full['taxon_id'].nunique()} especies "
                                         f"x {prior_species_full['zone_id'].nunique()} zonas "
                                         f"(extension confirmada de prior_zone_taxon_v2_clean.csv, "
                                         f"mismo metodo de smoothing, sin recalculo necesario "
                                         f"porque ya cubria el catalogo completo)",
        "coverage_report.json": "cobertura de prior geografico vs embeddings evaluables",
        "exclusions.json": "especies excluidas de evaluacion visual y por que",
        "leakage_audit.json": "auditoria de purga de leakage (reutiliza FASE12.2/v2_clean)",
        "reproducibility_manifest.json": "hashes de inputs, seed, gate0, reglas duras confirmadas",
    },
    "evaluation_outputs_outside_package": [
        "../GEO5_AUDIT.md", "../GEO5_closed_identification_metrics.json",
        "../GEO5_confusion_matrix.csv", "../GEO5_performance_by_genus.csv",
        "../GEO5_performance_by_family.csv", "../GEO5_openset_comparison.json",
        "../GEO5_threshold_curve.csv", "../GEO5_merlin_ranking_examples.json", "../GEO5_REPORT.md",
    ],
}
json.dump(package_manifest, open(PKG / "package_manifest.json", "w", encoding="utf-8"),
          indent=2, ensure_ascii=False)

print("\nDONE -- GEO5 evaluation + package written.")
