"""
phase_clean_prior.py — Reconstruye prior_zone_taxon_v1.csv EXCLUYENDO los 1214
observation_id contaminados (aparecen tanto como fuente del prior geografico
como en el conjunto evaluado en fase23a_geographic_context).

Replica EXACTAMENTE el metodo de suavizado de
pipeline_dataset/zonas_finales_y_prior.py:
  - N(s,z) = suma sobre celdas de min(n(s,c), tope), tope = percentil90 de n(s,c)>0
  - alpha elegido por maxima log-verosimilitud media, validacion leave-one-cell-out
    dentro de cada zona (misma grilla GRID_ALPHA, mismo K=291)
  - P(s|z) = (N(s,z) + alpha) / (N(z) + alpha*K)

NO recalcula la geometria de zonas (zone_original/zone_final/fusiones/beta-sim):
esa asignacion celda->zona es independiente de que registros individuales se usen
para contar especies, y se reutiliza tal cual desde
COLOMBIA_ANURA/ANTIOQUIA/zones/cell_zone_map_v1.csv (columna zone_final), que es
un artefacto YA CONGELADO y no se modifica.

NO escribe ni modifica ningun archivo bajo COLOMBIA_ANURA/ANTIOQUIA/priors/
(el v1 original queda intacto). Solo escribe en validation/fase23a_geographic_context/.
"""
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

BASE = Path("D:/Anura")
OUT = BASE / "validation/fase23a_geographic_context"

PERCENTIL_TOPE = 90
GRID_ALPHA = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]


def load_contaminated_obs_ids():
    inat_ids = set()
    with open(BASE / "COLOMBIA_ANURA/ANTIOQUIA/occurrences/records_v1.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        if row["source"] == "inaturalist":
            inat_ids.add(row["record_id"].split(":", 1)[1])

    eval_ids = set()
    with open(OUT / "per_sample_results.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            eval_ids.add(row["individual_id"])

    overlap = inat_ids & eval_ids
    return rows, overlap, len(inat_ids), len(eval_ids)


def main():
    rows, contaminated_obs_ids, n_inat_source, n_eval = load_contaminated_obs_ids()
    assert len(contaminated_obs_ids) == 1214, f"Expected 1214 overlap, got {len(contaminated_obs_ids)}"
    print(f"inat source records (unique obs_id): {n_inat_source}")
    print(f"eval unique individual_id: {n_eval}")
    print(f"contaminated obs_id to purge: {len(contaminated_obs_ids)}")

    # ---------- Purge contaminated records (any source: only inaturalist obs_ids can match
    # by construction, but we filter defensively on the full record set) ----------
    purged_records = []
    n_excluded = 0
    excluded_zones = Counter()
    excluded_species = Counter()
    for r in rows:
        obs_id = r["record_id"].split(":", 1)[1] if r["source"] == "inaturalist" else None
        if obs_id is not None and obs_id in contaminated_obs_ids:
            n_excluded += 1
            excluded_zones[r["cell_id"]] += 1
            excluded_species[r["taxon_id"]] += 1
            continue
        purged_records.append(r)

    print(f"Records original: {len(rows)}  ->  purged: {len(purged_records)}  (excluded: {n_excluded})")

    # ---------- Reuse frozen zone geometry (cell -> zone_final) ----------
    zone_final = {}
    with open(BASE / "COLOMBIA_ANURA/ANTIOQUIA/zones/cell_zone_map_v1.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["zone_final"]:
                zone_final[(int(row["row"]), int(row["col"]))] = row["zone_final"]

    with open(BASE / "COLOMBIA_ANURA/ANTIOQUIA/catalog/catalog_v1.json", encoding="utf-8") as f:
        catalogo = json.load(f)
    taxa = sorted(t["taxon_id"] for t in catalogo["taxa"])
    K = len(taxa)
    nombre_taxon = {t["taxon_id"]: t["scientific_name"] for t in catalogo["taxa"]}
    assert K == 291, K

    finales = sorted(set(zone_final.values()))

    # ---------- Counts per (cell, species), using PURGED records ----------
    n_sc = defaultdict(Counter)
    sin_zona = []
    for r in purged_records:
        c = (int(r["cell_row"]), int(r["cell_col"]))
        z = zone_final.get(c)
        if z is None:
            sin_zona.append(r["record_id"])
            continue
        n_sc[c][r["taxon_id"]] += 1

    todos_n = [n for cnt in n_sc.values() for n in cnt.values()]
    tope = int(math.ceil(np.percentile(todos_n, PERCENTIL_TOPE)))
    print(f"Effort cap (tope) recomputed on purged data: {tope} (percentile {PERCENTIL_TOPE})")

    celdas_zona = defaultdict(set)
    for c, z in zone_final.items():
        celdas_zona[z].add(c)

    N_raw, N_cap = defaultdict(Counter), defaultdict(Counter)
    for c, cnt in n_sc.items():
        z = zone_final.get(c)
        if z is None:
            continue
        for s, n in cnt.items():
            N_raw[z][s] += n
            N_cap[z][s] += min(n, tope)

    # ---------- alpha selection via leave-one-cell-out mean held-out log-likelihood ----------
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
    print(f"alpha elegido (purged) = {alpha}  (edge={en_borde})")
    for p in curva:
        marker = "  <" if p["alpha"] == alpha else ""
        print(f"  alpha={p['alpha']:>8}  loglik={p['mean_heldout_loglik']:>10.4f}{marker}")

    # ---------- Final priors P(s|z) ----------
    filas_prior = []
    diagnostico = {}
    for z in finales:
        total_cap = sum(N_cap[z].values())
        total_raw = sum(N_raw[z].values())
        denom = total_cap + alpha * K
        p = {s: (N_cap[z][s] + alpha) / denom for s in taxa}
        for s in taxa:
            filas_prior.append({
                "zone_id": z, "taxon_id": s, "scientific_name": nombre_taxon[s],
                "n_records": N_raw[z][s], "n_effective": N_cap[z][s], "p": format(p[s], ".17g"),
            })
        observadas = [s for s in taxa if N_raw[z][s] > 0]
        rho_inc = None
        diagnostico[z] = {
            "records": total_raw, "effective_records": total_cap,
            "species_observed": len(observadas),
            "p_unobserved": alpha / denom,
        }

    out_csv = OUT / "prior_zone_taxon_v2_clean.csv"
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["zone_id", "taxon_id", "scientific_name", "n_records", "n_effective", "p"])
        w.writeheader()
        w.writerows(filas_prior)
    print(f"Wrote {out_csv} ({len(filas_prior)} rows)")

    manifest = {
        "source": "prior_zone_taxon_v2_clean.csv (derived, NOT overwriting v1)",
        "original_prior": "COLOMBIA_ANURA/ANTIOQUIA/priors/prior_zone_taxon_v1.csv (untouched)",
        "purge_rule": "exclude any source record whose iNaturalist observation_id appears in "
                      "the eval set (validation/fase23a_geographic_context/per_sample_results.csv, "
                      "column individual_id) — i.e. observations later scored by the visual+geo "
                      "evaluation must not also feed the geographic prior.",
        "n_records_original": len(rows),
        "n_records_purged_total": len(purged_records),
        "n_records_excluded": n_excluded,
        "n_contaminated_obs_ids": len(contaminated_obs_ids),
        "n_source_inaturalist_records_original": n_inat_source,
        "n_records_no_zone_after_purge": len(sin_zona),
        "excluded_records_by_cell_top10": excluded_zones.most_common(10),
        "excluded_records_by_species_top10": [
            {"taxon_id": t, "scientific_name": nombre_taxon.get(t, "?"), "n_excluded": n}
            for t, n in excluded_species.most_common(10)
        ],
        "effort_cap_tope": tope,
        "alpha_selected": alpha,
        "alpha_at_grid_edge": en_borde,
        "alpha_curve": curva,
        "K_taxa": K,
        "n_zones": len(finales),
        "zones": finales,
        "zone_geometry_reused_from": "COLOMBIA_ANURA/ANTIOQUIA/zones/cell_zone_map_v1.csv (frozen, not modified)",
        "method_reference": "pipeline_dataset/zonas_finales_y_prior.py (alpha via leave-one-cell-out CV, "
                             "same GRID_ALPHA, same effort-cap rule at percentile 90, same formula "
                             "P(s|z)=(N(s,z)+alpha)/(N(z)+alpha*K))",
        "diagnostics_by_zone": diagnostico,
    }
    out_manifest = OUT / "prior_zone_taxon_v2_clean_manifest.json"
    with open(out_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"Wrote {out_manifest}")


if __name__ == "__main__":
    main()
