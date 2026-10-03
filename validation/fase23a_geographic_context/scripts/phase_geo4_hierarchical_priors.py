#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
phase_geo4_hierarchical_priors.py -- GEO-4 PASO 0 + PASO 1.

PASO 0: Gate check (reproduce baseline_reproduction_v2.json, AUROC=0.57329 exacto).
PASO 1: Construye prior_zone_genus_v1.csv y prior_zone_family_v1.csv, agregando
        los MISMOS registros purgados de leakage (misma fuente que
        prior_zone_taxon_v2_clean.csv: COLOMBIA_ANURA/ANTIOQUIA/occurrences/records_v1.csv
        menos los 1214 obs_id contaminados), con EXACTAMENTE el mismo metodo de
        suavizado de pipeline_dataset/zonas_finales_y_prior.py (replicado en
        phase_clean_prior.py): effort-cap a percentil90, alpha elegido por
        maxima log-verosimilitud media leave-one-cell-out, P = (N_cap+alpha)/(N+alpha*K),
        ahora con K = numero de generos / numero de familias en vez de especies.

No toca prior_zone_taxon_v1.csv, prior_zone_taxon_v2_clean.csv, ni ningun archivo
bajo COLOMBIA_ANURA/ANTIOQUIA/priors/. Todo output con prefijo GEO4_ o
prior_zone_{genus,family}_v1.csv.
"""
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

BASE = Path("D:/Anura")
OUT = BASE / "validation/fase23a_geographic_context"

PERCENTIL_TOPE = 90
GRID_ALPHA = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]

OFFICIAL_AUROC = 0.5732919408781961


def gate0():
    gate_path = OUT / "baseline_reproduction_v2.json"
    if not gate_path.exists():
        return False, None
    gate = json.load(open(gate_path, encoding="utf-8"))
    reproduced = gate["reproduced_auroc"]
    diff = abs(reproduced - OFFICIAL_AUROC)
    passed = gate.get("gate_passed", False) and diff == 0.0
    return passed, dict(reproduced_auroc=reproduced, official_auroc=OFFICIAL_AUROC, abs_diff=diff, gate_passed=passed)


def load_contaminated_obs_ids():
    with open(BASE / "COLOMBIA_ANURA/ANTIOQUIA/occurrences/records_v1.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    inat_ids = set()
    for row in rows:
        if row["source"] == "inaturalist":
            inat_ids.add(row["record_id"].split(":", 1)[1])
    eval_ids = set()
    with open(OUT / "per_sample_results.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            eval_ids.add(row["individual_id"])
    overlap = inat_ids & eval_ids
    return rows, overlap


def build_prior(rows, contaminated_obs_ids, catalog_taxa, level, level_key, out_csv_name, out_manifest_name):
    """level_key: function taxon_id -> level label (genus or family)."""
    # ---------- purge ----------
    purged = []
    n_excluded = 0
    for r in rows:
        obs_id = r["record_id"].split(":", 1)[1] if r["source"] == "inaturalist" else None
        if obs_id is not None and obs_id in contaminated_obs_ids:
            n_excluded += 1
            continue
        purged.append(r)

    # ---------- zone geometry (frozen, reused) ----------
    zone_final = {}
    with open(BASE / "COLOMBIA_ANURA/ANTIOQUIA/zones/cell_zone_map_v1.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["zone_final"]:
                zone_final[(int(row["row"]), int(row["col"]))] = row["zone_final"]
    finales = sorted(set(zone_final.values()))
    celdas_zona = defaultdict(set)
    for c, z in zone_final.items():
        celdas_zona[z].add(c)

    # ---------- taxon_id -> level label ----------
    taxon_to_level = {}
    for t in catalog_taxa:
        lab = t.get(level)
        if lab:
            taxon_to_level[t["taxon_id"]] = lab
    levels = sorted(set(taxon_to_level.values()))
    K = len(levels)

    # ---------- counts per (cell, level_label) ----------
    n_sc = defaultdict(Counter)
    for r in purged:
        c = (int(r["cell_row"]), int(r["cell_col"]))
        z = zone_final.get(c)
        if z is None:
            continue
        lab = taxon_to_level.get(r["taxon_id"])
        if lab is None:
            continue
        n_sc[c][lab] += 1

    todos_n = [n for cnt in n_sc.values() for n in cnt.values()]
    tope = int(math.ceil(np.percentile(todos_n, PERCENTIL_TOPE))) if todos_n else 1

    N_raw, N_cap = defaultdict(Counter), defaultdict(Counter)
    for c, cnt in n_sc.items():
        z = zone_final.get(c)
        if z is None:
            continue
        for s, n in cnt.items():
            N_raw[z][s] += n
            N_cap[z][s] += min(n, tope)

    def log_verosimilitud(alpha):
        ll = peso = 0.0
        for z in finales:
            total = sum(N_cap[z].values())
            for c in celdas_zona[z]:
                if c not in n_sc:
                    continue
                w = {s: min(n, tope) for s, n in n_sc[c].items()}
                wc = sum(w.values())
                denom = total - wc + alpha * K
                for s, ws in w.items():
                    ll += ws * math.log((N_cap[z][s] - ws + alpha) / denom)
                peso += wc
        return ll / peso if peso > 0 else float("-inf")

    curva = [{"alpha": a, "mean_heldout_loglik": log_verosimilitud(a)} for a in GRID_ALPHA]
    mejor = max(curva, key=lambda x: x["mean_heldout_loglik"])
    alpha = mejor["alpha"]
    en_borde = alpha in (GRID_ALPHA[0], GRID_ALPHA[-1])

    filas = []
    diagnostico = {}
    for z in finales:
        total_cap = sum(N_cap[z].values())
        total_raw = sum(N_raw[z].values())
        denom = total_cap + alpha * K
        p = {s: (N_cap[z][s] + alpha) / denom for s in levels}
        for s in levels:
            filas.append({"zone_id": z, level: s, "n_records": N_raw[z][s],
                           "n_effective": N_cap[z][s], "p": format(p[s], ".17g")})
        diagnostico[z] = {"records": total_raw, "effective_records": total_cap,
                           f"{level}_observed": len([s for s in levels if N_raw[z][s] > 0]),
                           "p_unobserved": alpha / denom}

    out_csv = OUT / out_csv_name
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["zone_id", level, "n_records", "n_effective", "p"])
        w.writeheader()
        w.writerows(filas)

    manifest = {
        "level": level, "K": K, "levels": levels, "alpha_selected": alpha,
        "alpha_at_grid_edge": en_borde, "alpha_curve": curva,
        "effort_cap_tope": tope, "n_records_purged_total": len(purged),
        "n_records_excluded": n_excluded, "n_zones": len(finales), "zones": finales,
        "method_reference": "identico a phase_clean_prior.py (prior_zone_taxon_v2_clean.csv), "
                             "agregado a nivel " + level + " via catalog_v1.json[taxon_id]." + level,
        "diagnostics_by_zone": diagnostico,
    }
    out_manifest = OUT / out_manifest_name
    with open(out_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    return dict(csv=str(out_csv), manifest=str(out_manifest), alpha=alpha, K=K, tope=tope, n_excluded=n_excluded)


def main():
    passed, gate_info = gate0()
    print("GATE 0:", gate_info)
    if not passed:
        blocked = {"status": "GEO4_BLOCKED", "reason": "AUROC visual puro no reproduce 0.57329 exacto.",
                   "gate_info": gate_info}
        with open(OUT / "GEO4_BLOCKED.json", "w", encoding="utf-8") as f:
            json.dump(blocked, f, indent=2, ensure_ascii=False)
        print("GEO4_BLOCKED -- ver GEO4_BLOCKED.json")
        raise SystemExit(1)
    print("GATE 0 PASSED\n")

    rows, contaminated = load_contaminated_obs_ids()
    assert len(contaminated) == 1214, len(contaminated)
    catalog = json.load(open(BASE / "COLOMBIA_ANURA/ANTIOQUIA/catalog/catalog_v1.json", encoding="utf-8"))
    catalog_taxa = catalog["taxa"]

    print("Building genus prior...")
    genus_info = build_prior(rows, contaminated, catalog_taxa, "genus", "genus",
                              "prior_zone_genus_v1.csv", "GEO4_prior_zone_genus_v1_manifest.json")
    print("  ", genus_info)

    print("Building family prior...")
    family_info = build_prior(rows, contaminated, catalog_taxa, "family", "family",
                               "prior_zone_family_v1.csv", "GEO4_prior_zone_family_v1_manifest.json")
    print("  ", family_info)

    combined = {
        "gate0": gate_info,
        "reused_source_records": "COLOMBIA_ANURA/ANTIOQUIA/occurrences/records_v1.csv (same purged set as GEO2/prior_zone_taxon_v2_clean.csv, 1214 contaminated obs_id excluded)",
        "reused_zone_geometry": "COLOMBIA_ANURA/ANTIOQUIA/zones/cell_zone_map_v1.csv (frozen)",
        "taxon_to_genus_family_source": "COLOMBIA_ANURA/ANTIOQUIA/catalog/catalog_v1.json (genus/family fields per taxon_id, 291 taxa, authoritative for full COL set -- broader coverage than training/taxonomia.py which only covers the 41 trained species)",
        "genus_prior": genus_info,
        "family_prior": family_info,
        "note_alpha_may_differ_from_species": "alpha se reselecciona independientemente por nivel via la misma CV leave-one-cell-out; K distinto (num generos / num familias vs 291 especies) cambia el termino alpha*K, es esperado que difiera.",
    }
    with open(OUT / "GEO4_priors_genus_family_manifest.json", "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    print("\nWrote GEO4_priors_genus_family_manifest.json")
    print("DONE PASO 0 + PASO 1.")


if __name__ == "__main__":
    main()
