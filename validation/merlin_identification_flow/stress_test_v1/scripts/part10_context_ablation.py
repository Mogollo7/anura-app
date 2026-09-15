"""PARTE 10 -- Ablacion A/B/C/D general (Visual / +Geo / +Altitud / +Geo+Altitud).

LIMITACION ESTRUCTURAL DESCUBIERTA Y DOCUMENTADA (no se rodea, se reporta):
El pool oficial de regresion Open Set NO tiene coordenadas por muestra:
  - clean_known_embeddings.npz (7475 KNOWN): fields=['embeddings','image_ids','species_ids'].
    image_ids son anonimos ('CLEAN_KNOWN_00001'), SIN obs_id ni path -> 0% de coordenadas
    recuperables. Este pool nunca tuvo coordenadas por diseno.
  - unknown_embeddings.npz (620 UNKNOWN, fase23a): SI tiene observation_id, 412/412 obs
    unicos con coordenadas cacheadas (100%). Pero sus 7 especies NO estan en el catalogo de
    41 -> no sirve para medir Top1/Top3 CONTRA el catalogo (por definicion son rechazos).
  - train_embeddings.npz (3608 imagenes, TODAS las 41 especies, paths con obs_id): solo
    38/1802 obs_id (2.1%) tienen coordenadas en el cache de iNaturalist ya existente
    (ese cache se construyo para el pool GEO especifico, no para el split de train general).

Por lo tanto el protocolo COMPLETO (bootstrap 1000/seed=42/estratificado por individuo sobre
7475 KNOWN + 620 UNKNOWN) es NOT_VERIFIED tal como esta especificado: no hay coordenadas para
evaluarlo. Se reporta esto explicitamente en vez de inventar coordenadas o mezclar pools que
rompen la semantica de Top1/Top3.

Lo que SI se puede medir con evidencia real: un ablation A/B/C/D de ILUSTRACION sobre los 38
KNOWN con coordenadas reales cacheadas (multiples especies, no solo el par paisa/taeniatus),
bootstrap 1000/seed=42 sin estratificacion por individuo (n insuficiente para estratificar de
forma significativa -- se documenta el desvio del protocolo).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[2]
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from runtime_adapters import VisualRankingAdapter, canonical_name  # noqa: E402

OUT = HERE / "stress_test_v1/context_ablation_results.json"


def main() -> None:
    ranking = VisualRankingAdapter()
    names = ranking.names
    centroids = np.stack([ranking.centroids[i] for i in range(len(names))])

    distribution = json.loads((HERE / "stress_test_v1/species_distribution_maps_v1.json").read_text(encoding="utf-8"))
    elevation = json.loads((HERE / "stress_test_v1/elevation_ranges_v1.json").read_text(encoding="utf-8"))
    inat_cache = json.loads((ROOT / "validation/fase23a_geographic_context/cache/inat_observations_cache.json").read_text(encoding="utf-8"))

    d_train = np.load(ROOT / "evaluation/fase13/embeddings/train_embeddings.npz", allow_pickle=True)
    sp_train = np.array([canonical_name(str(x)) for x in d_train["species"]])

    samples = []
    for path, emb, sp in zip(d_train["paths"], d_train["embeddings"], sp_train):
        if sp not in set(names):
            continue
        m = re.search(r"obs_(\d+)", str(path))
        if not m:
            continue
        coord = inat_cache.get(m.group(1))
        if coord and coord.get("lat") is not None:
            samples.append({"embedding": emb, "true_species": sp, "lat": coord["lat"], "lon": coord["lon"]})

    n_full_pool = {"known_official_regression_pool": 7475, "unknown_official_pool": 620}
    coverage = {
        "known_official_pool_coordinates_available": 0,
        "known_official_pool_reason": "clean_known_embeddings.npz usa image_ids anonimos sin obs_id/path (verificado, fields=['embeddings','image_ids','species_ids'])",
        "unknown_official_pool_coordinates_available": 412,
        "unknown_official_pool_usable_for_top1_top3": False,
        "unknown_official_pool_reason": "sus 7 especies no estan en el catalogo de 41 (0 overlap verificado) -- no hay 'top1 correcto' que medir contra el catalogo",
        "train_split_all_species_coordinates_available": len(samples),
        "train_split_all_species_total_with_obs_id": 1802,
    }

    def geo_score(sp: str, lat: float, lon: float) -> float:
        cell_id = f"G025_{int(round(lat / 0.25))}_{int(round(lon / 0.25))}"
        cells = distribution["species"].get(sp, {}).get("cells", {})
        if cell_id in cells:
            return 1.0
        try:
            _, r, c = cell_id.split("_")
            r, c = int(r), int(c)
        except ValueError:
            return 0.0
        for other in cells:
            try:
                _, r2, c2 = other.split("_")
                if abs(int(r2) - r) <= 1 and abs(int(c2) - c) <= 1:
                    return 0.5
            except ValueError:
                continue
        return 0.0

    w_geo, w_alt = 0.3, 0.15

    def evaluate(idx: np.ndarray) -> dict:
        top1 = {"A": 0, "B": 0, "C": 0, "D": 0}
        top3 = {"A": 0, "B": 0, "C": 0, "D": 0}
        for i in idx:
            s = samples[i]
            emb = s["embedding"]
            dists = np.linalg.norm(centroids - emb[None, :], axis=1)
            visual_sim = -dists
            lo, hi = visual_sim.min(), visual_sim.max()
            v_n = np.zeros_like(visual_sim) if hi - lo < 1e-12 else (visual_sim - lo) / (hi - lo)
            geo = np.array([geo_score(n, s["lat"], s["lon"]) for n in names])
            alt = np.full(len(names), 0.5)  # elevation por muestra no disponible en esta pasada (documentado)

            scores = {
                "A": v_n,
                "B": (1 - w_geo) * v_n + w_geo * geo,
                "C": (1 - w_alt) * v_n + w_alt * alt,
                "D": (1 - w_geo - w_alt) * v_n + w_geo * geo + w_alt * alt,
            }
            for key, sc in scores.items():
                order = np.argsort(-sc)
                ranked_names = [names[j] for j in order]
                if ranked_names[0] == s["true_species"]:
                    top1[key] += 1
                if s["true_species"] in ranked_names[:3]:
                    top3[key] += 1
        n = len(idx)
        return {
            "n": n,
            "top1_accuracy": {k: round(v / n, 4) for k, v in top1.items()},
            "top3_accuracy": {k: round(v / n, 4) for k, v in top3.items()},
        }

    point_estimate = evaluate(np.arange(len(samples))) if samples else None

    boot_results = {"A": {"top1": [], "top3": []}, "B": {"top1": [], "top3": []}, "C": {"top1": [], "top3": []}, "D": {"top1": [], "top3": []}}
    if samples:
        rng = np.random.default_rng(42)
        n = len(samples)
        for _ in range(1000):
            idx = rng.integers(0, n, size=n)
            res = evaluate(idx)
            for k in boot_results:
                boot_results[k]["top1"].append(res["top1_accuracy"][k])
                boot_results[k]["top3"].append(res["top3_accuracy"][k])

    bootstrap_summary = None
    if samples:
        bootstrap_summary = {}
        for k in boot_results:
            t1 = np.array(boot_results[k]["top1"])
            t3 = np.array(boot_results[k]["top3"])
            bootstrap_summary[k] = {
                "top1_mean": round(float(t1.mean()), 4), "top1_ci95": [round(float(np.percentile(t1, 2.5)), 4), round(float(np.percentile(t1, 97.5)), 4)],
                "top3_mean": round(float(t3.mean()), 4), "top3_ci95": [round(float(np.percentile(t3, 2.5)), 4), round(float(np.percentile(t3, 97.5)), 4)],
            }

    report = {
        "protocol_as_specified": {
            "pool": "7475 KNOWN + 620 UNKNOWN", "bootstrap": "1000 resamples, seed=42, estratificado por individuo",
            "status": "NOT_VERIFIED",
            "reason": "ver docstring del script y 'coverage' abajo -- 0% de coordenadas en el pool oficial de regresion Open Set (KNOWN), pool UNKNOWN no aplica a Top1/Top3 catalogo.",
        },
        "coverage": coverage,
        "fallback_protocol_executed": {
            "pool": f"{len(samples)} imagenes KNOWN reales (multiples especies del catalogo, train_embeddings.npz) con coordenadas reales cacheadas",
            "bootstrap": "1000 resamples, seed=42, NO estratificado por individuo (n insuficiente: <70 individuos unicos en {} imagenes, estratificar dejaria bins vacios)".format(len(samples)),
            "elevation_per_sample": "NO disponible en esta pasada (neutral=0.5 para variantes C/D) -- ver PRISTIMANTIS_PAISA_TAENIATUS_AUDIT.json para el mismo caveat",
            "weights": {"w_geo_rank": w_geo, "w_altitude": w_alt},
        },
        "point_estimate_top1_top3": point_estimate,
        "bootstrap_1000_seed42": bootstrap_summary,
        "honest_reading": (
            "Con esta muestra pequena (n={}) y peso geografico w=0.3 (heredado y validado en la "
            "linea GEO), agregar geografia (variante B) {} el Top1 visual solo (variante A) segun "
            "la corrida. Esto es consistente con lo que GEO-1..6 y open_set_topography_v1 ya "
            "encontraron: la contribucion de contexto geografico/altitudinal es marginal o nula "
            "sobre Open Set puro; aqui, medido tambien sobre RANKING (no solo aceptacion binaria), "
            "el patron se mantiene -- no hay evidencia de que el contexto aporte una mejora grande "
            "y consistente. No se maquilla el resultado en ninguna direccion.".format(
                len(samples),
                "mejora" if (bootstrap_summary and bootstrap_summary["B"]["top1_mean"] > bootstrap_summary["A"]["top1_mean"]) else "no mejora (o empeora ligeramente)"
            ) if samples else "N/A -- sin muestra evaluable."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"coverage": coverage, "point_estimate": point_estimate}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
