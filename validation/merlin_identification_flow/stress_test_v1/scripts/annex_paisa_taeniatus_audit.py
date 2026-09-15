"""ANEXO -- Auditoria Pristimantis paisa / taeniatus (par mas cercano de los 41, d=0.1944).

No reentrena, no mueve centroides, no autoriza fine-tuning. Solo mide.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[2]
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from runtime_adapters import VisualRankingAdapter, canonical_name  # noqa: E402

OUT_JSON = HERE / "stress_test_v1/PRISTIMANTIS_PAISA_TAENIATUS_AUDIT.json"
OUT_MD = HERE / "stress_test_v1/PRISTIMANTIS_PAISA_TAENIATUS_AUDIT.md"

A = "Pristimantis paisa"
B = "Pristimantis taeniatus"


def load_all_embeddings(name: str) -> np.ndarray:
    parts = []
    for split in ["reference_embeddings", "train_embeddings", "calibration_embeddings"]:
        d = np.load(ROOT / f"evaluation/fase13/embeddings/{split}.npz", allow_pickle=True)
        sp = np.array([canonical_name(str(x)) for x in d["species"]])
        mask = sp == name
        if mask.sum():
            parts.append(d["embeddings"][mask])
    return np.concatenate(parts, axis=0) if parts else np.zeros((0, 512))


def main() -> None:
    ranking = VisualRankingAdapter()
    names = ranking.names
    centroids = {n: ranking.centroids[i] for i, n in enumerate(names)}

    # 1. all 820 pairwise centroid distances
    pair_dists = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            pair_dists.append(float(np.linalg.norm(centroids[names[i]] - centroids[names[j]])))
    pair_dists = np.array(pair_dists)
    centroid_distance_ab = float(np.linalg.norm(centroids[A] - centroids[B]))
    percentile_rank = float((pair_dists < centroid_distance_ab).mean() * 100)

    emb_a = load_all_embeddings(A)
    emb_b = load_all_embeddings(B)

    def intra_variance(emb: np.ndarray, centroid: np.ndarray) -> dict:
        d = np.linalg.norm(emb - centroid[None, :], axis=1)
        return {
            "n": int(emb.shape[0]),
            "mean_dist_to_centroid": float(d.mean()),
            "std_dist_to_centroid": float(d.std()),
            "max_dist_to_centroid": float(d.max()),
        }

    intra_a = intra_variance(emb_a, centroids[A])
    intra_b = intra_variance(emb_b, centroids[B])

    # cross-species nearest-neighbor overlap: for each A embedding, is nearest of {own centroid, other centroid} the OWN one?
    def cross_overlap(emb_self: np.ndarray, c_self: np.ndarray, c_other: np.ndarray) -> dict:
        d_self = np.linalg.norm(emb_self - c_self[None, :], axis=1)
        d_other = np.linalg.norm(emb_self - c_other[None, :], axis=1)
        closer_to_other = d_self > d_other
        return {"n": int(emb_self.shape[0]), "n_closer_to_other_species": int(closer_to_other.sum()),
                "fraction_misassigned": float(closer_to_other.mean())}

    overlap_a_to_b = cross_overlap(emb_a, centroids[A], centroids[B])
    overlap_b_to_a = cross_overlap(emb_b, centroids[B], centroids[A])

    # 5. k-means k=2 on each species' own embeddings, silhouette score
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    def kmeans_split(emb: np.ndarray, other_centroid: np.ndarray, self_centroid: np.ndarray) -> dict:
        if emb.shape[0] < 10:
            return {"status": "INSUFFICIENT_DATA"}
        km = KMeans(n_clusters=2, random_state=42, n_init=10).fit(emb)
        sil = float(silhouette_score(emb, km.labels_))
        sub_centroids = km.cluster_centers_
        # does splitting improve separation from the OTHER species' centroid?
        dist_sub_to_other = np.linalg.norm(sub_centroids - other_centroid[None, :], axis=1)
        dist_full_to_other = float(np.linalg.norm(self_centroid - other_centroid))
        min_sub_dist = float(dist_sub_to_other.min())
        return {
            "silhouette_score": round(sil, 4),
            "cluster_sizes": [int((km.labels_ == 0).sum()), int((km.labels_ == 1).sum())],
            "full_centroid_dist_to_other_species": round(dist_full_to_other, 4),
            "closest_sub_centroid_dist_to_other_species": round(min_sub_dist, 4),
            "splitting_improves_separation": min_sub_dist > dist_full_to_other,
            "justified": sil > 0.25 and min_sub_dist > dist_full_to_other * 1.05,
        }

    kmeans_a = kmeans_split(emb_a, centroids[B], centroids[A])
    kmeans_b = kmeans_split(emb_b, centroids[A], centroids[B])

    # 3. geography/altitude overlap using Parte 5/7 artifacts
    distribution = json.loads((HERE / "stress_test_v1/species_distribution_maps_v1.json").read_text(encoding="utf-8"))
    elevation = json.loads((HERE / "stress_test_v1/elevation_ranges_v1.json").read_text(encoding="utf-8"))
    dist_a = distribution["species"].get(A, {})
    dist_b = distribution["species"].get(B, {})
    cells_a = set(dist_a.get("cells", {}).keys())
    cells_b = set(dist_b.get("cells", {}).keys())
    cell_overlap = cells_a & cells_b
    elev_a = elevation["species"].get(A, {})
    elev_b = elevation["species"].get(B, {})
    elev_overlap = None
    if "min" in elev_a and "min" in elev_b:
        lo = max(elev_a["p5"], elev_b["p5"])
        hi = min(elev_a["p95"], elev_b["p95"])
        elev_overlap = {
            "species_a_p5_p95": [elev_a["p5"], elev_a["p95"]],
            "species_b_p5_p95": [elev_b["p5"], elev_b["p95"]],
            "overlap_range": [lo, hi] if hi > lo else None,
            "distinguishable_by_altitude": hi <= lo,
        }

    geo_alt = {
        "geography": {
            "species_a_cells": len(cells_a), "species_b_cells": len(cells_b),
            "cell_overlap_count": len(cell_overlap),
            "distinguishable_by_geography": len(cell_overlap) == 0 and (len(cells_a) > 0 or len(cells_b) > 0),
        },
        "elevation": elev_overlap or {"status": "INSUFFICIENT_DATA_FOR_ONE_OR_BOTH_SPECIES"},
    }

    # 4/10 (annex-scoped ablation): visual-only vs +geo vs +altitude vs +both, RESTRICTED
    # to distinguishing THIS PAIR. Honest scope note: full bootstrap 1000/seed42 stratified
    # by individuo sobre el pool GEO completo no es reproducible aqui porque el pool de
    # regresion Open Set (clean_known_embeddings, 7475) usa image_ids anonimizados SIN
    # obs_id/coordenadas (ver limitacion documentada en openset_regression_metrics.json /
    # el propio artefacto npz: fields=['embeddings','image_ids','species_ids']). Se mide
    # aqui con el pool de embeddings CON identidad geografica que SI tiene esta pareja disponible
    # via train_embeddings (paths con obs_id) cruzado contra
    # validation/fase23a_geographic_context/cache/inat_observations_cache.json.
    inat_cache = json.loads((ROOT / "validation/fase23a_geographic_context/cache/inat_observations_cache.json").read_text(encoding="utf-8"))
    d_train = np.load(ROOT / "evaluation/fase13/embeddings/train_embeddings.npz", allow_pickle=True)
    sp_train = np.array([canonical_name(str(x)) for x in d_train["species"]])
    import re

    def gather_pair_samples(name: str) -> list[dict]:
        mask = sp_train == name
        out = []
        for path, emb in zip(d_train["paths"][mask], d_train["embeddings"][mask]):
            m = re.search(r"obs_(\d+)", str(path))
            obs_id = m.group(1) if m else None
            coord = inat_cache.get(obs_id) if obs_id else None
            out.append({"obs_id": obs_id, "embedding": emb, "coord": coord, "true_species": name})
        return out

    samples = gather_pair_samples(A) + gather_pair_samples(B)
    samples_with_coords = [s for s in samples if s["coord"] and s["coord"].get("lat") is not None]

    def visual_top1(embedding: np.ndarray) -> str:
        d_a = np.linalg.norm(embedding - centroids[A])
        d_b = np.linalg.norm(embedding - centroids[B])
        return A if d_a < d_b else B

    def geo_score(name: str, lat: float, lon: float) -> float:
        # simple support: 1 if any occurrence cell within the department grid distance, else 0
        cell_id = f"G025_{int(round(lat / 0.25))}_{int(round(lon / 0.25))}"
        cells = distribution["species"].get(name, {}).get("cells", {})
        if cell_id in cells:
            return 1.0
        # neighboring cell tolerance
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

    def alt_score(name: str, elev_m: float | None) -> float:
        e = elevation["species"].get(name, {})
        if elev_m is None or "p5" not in e:
            return 0.5  # neutral, unknown
        if e["p5"] <= elev_m <= e["p95"]:
            return 1.0
        return 0.0

    variants = {"A_visual_only": [], "B_visual_geo": [], "C_visual_altitude": [], "D_visual_geo_altitude": []}
    w_geo = 0.3
    w_alt = 0.15  # conservador, documentado: menor que geo por ausencia de evidencia previa que lo justifique

    correct = {k: 0 for k in variants}
    n_eval = 0
    for s in samples_with_coords:
        lat, lon = s["coord"]["lat"], s["coord"]["lon"]
        elev_m = None  # elevation not directly cached per obs in this quick pass; handled as neutral (0.5) via alt_score fallback
        top1_visual = visual_top1(s["embedding"])
        gA, gB = geo_score(A, lat, lon), geo_score(B, lat, lon)
        aA, aB = alt_score(A, elev_m), alt_score(B, elev_m)
        # visual base score: negative distance normalized within the pair
        dA, dB = np.linalg.norm(s["embedding"] - centroids[A]), np.linalg.norm(s["embedding"] - centroids[B])
        vA, vB = -dA, -dB
        lo_v, hi_v = min(vA, vB), max(vA, vB)
        vA_n = 0.0 if hi_v == lo_v else (vA - lo_v) / (hi_v - lo_v)
        vB_n = 0.0 if hi_v == lo_v else (vB - lo_v) / (hi_v - lo_v)

        pick = {}
        pick["A_visual_only"] = A if vA_n >= vB_n else B
        sA_geo, sB_geo = (1 - w_geo) * vA_n + w_geo * gA, (1 - w_geo) * vB_n + w_geo * gB
        pick["B_visual_geo"] = A if sA_geo >= sB_geo else B
        sA_alt, sB_alt = (1 - w_alt) * vA_n + w_alt * aA, (1 - w_alt) * vB_n + w_alt * aB
        pick["C_visual_altitude"] = A if sA_alt >= sB_alt else B
        wsum = w_geo + w_alt
        sA_both = (1 - wsum) * vA_n + w_geo * gA + w_alt * aA
        sB_both = (1 - wsum) * vB_n + w_geo * gB + w_alt * aB
        pick["D_visual_geo_altitude"] = A if sA_both >= sB_both else B

        n_eval += 1
        for k in variants:
            if pick[k] == s["true_species"]:
                correct[k] += 1

    ablation = {
        "n_eval_samples_with_real_coords": n_eval,
        "n_total_pair_samples_in_train_split": len(samples),
        "coverage_note": (
            "Solo train_embeddings.npz conserva obs_id en el path para esta pareja; "
            f"{n_eval}/{len(samples)} tenian coordenadas en el cache de iNaturalist ya existente. "
            "Elevacion por muestra NO se recupero en esta pasada (neutral=0.5 en alt_score) -- "
            "usar elevation por observacion individual requeriria mas llamadas nuevas a "
            "OpenTopoData de las que caben en el presupuesto de esta corrida; el ANALISIS "
            "a nivel de POBLACION (rango p5-p95 por especie, calculado arriba) SI esta completo."
        ),
        "weights": {"w_geo_rank": w_geo, "w_altitude": w_alt, "altitude_weight_note": "conservador, menor que geo por falta de evidencia previa que lo justifique (regla del encargo)"},
        "accuracy_by_variant": {k: round(correct[k] / n_eval, 4) if n_eval else None for k in variants},
    }

    # 6. verdict
    if percentile_rank <= 5:
        sep_level = "SEPARATION_DIFFICULT"
    elif percentile_rank <= 20:
        sep_level = "SEPARATION_PARTIAL"
    else:
        sep_level = "SEPARATION_ACCEPTABLE"

    verdict = {
        "CENTROID_DISTANCE": round(centroid_distance_ab, 6),
        "CENTROID_DISTANCE_PERCENTILE_AMONG_820_PAIRS": round(percentile_rank, 2),
        "INTRA_SPECIES_VARIANCE": {A: intra_a, B: intra_b},
        "CROSS_SPECIES_OVERLAP": {
            f"{A}_embeddings_closer_to_{B}_centroid": overlap_a_to_b,
            f"{B}_embeddings_closer_to_{A}_centroid": overlap_b_to_a,
        },
        "VISUAL_ONLY_PERFORMANCE": ablation["accuracy_by_variant"]["A_visual_only"] if ablation["n_eval_samples_with_real_coords"] else "NOT_VERIFIED",
        "VISUAL_GEO_PERFORMANCE": ablation["accuracy_by_variant"]["B_visual_geo"] if ablation["n_eval_samples_with_real_coords"] else "NOT_VERIFIED",
        "VISUAL_ALTITUDE_PERFORMANCE": ablation["accuracy_by_variant"]["C_visual_altitude"] if ablation["n_eval_samples_with_real_coords"] else "NOT_VERIFIED",
        "VISUAL_GEO_ALTITUDE_PERFORMANCE": ablation["accuracy_by_variant"]["D_visual_geo_altitude"] if ablation["n_eval_samples_with_real_coords"] else "NOT_VERIFIED",
        "ablation_not_verified_reason": (
            None if ablation["n_eval_samples_with_real_coords"] else
            f"0 de {ablation['n_total_pair_samples_in_train_split']} muestras de este par en "
            "train_embeddings.npz tienen obs_id presente en "
            "fase23a_geographic_context/cache/inat_observations_cache.json -- ese cache se "
            "construyo especificamente para el pool de evaluacion GEO (KNOWN con coords 0 por "
            "diseno, UNKNOWN 412/412), no para el split de entrenamiento general. No se hizo "
            "ninguna llamada nueva a la API de iNaturalist para rellenar esto (fuera del alcance "
            "de la regla de reutilizar cache de OpenTopoData/iNaturalist ya congelada)."
        ),
        "SEPARATION_CONCLUSION": sep_level,
        "VISUAL_HARD_PAIR": sep_level in ("SEPARATION_DIFFICULT", "SEPARATION_PARTIAL"),
    }

    report = {
        "pair": [A, B],
        "prior_measurement_confirmed": {"distance_prior_phase": 0.1944, "distance_this_run": round(centroid_distance_ab, 6),
                                          "matches": abs(centroid_distance_ab - 0.1944) < 0.001},
        "pairwise_distance_percentile": {
            "n_pairs": int(pair_dists.size), "min": float(pair_dists.min()), "mean": float(pair_dists.mean()),
            "max": float(pair_dists.max()), "ab_distance": centroid_distance_ab, "ab_percentile": percentile_rank,
        },
        "intra_species_variance": {A: intra_a, B: intra_b},
        "cross_species_nearest_neighbor_overlap": {
            f"{A}_closer_to_other": overlap_a_to_b, f"{B}_closer_to_other": overlap_b_to_a,
        },
        "kmeans_k2_silhouette": {A: kmeans_a, B: kmeans_b},
        "geography_altitude_overlap": geo_alt,
        "ablation": ablation,
        "verdict": verdict,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    md = f"""# Auditoria Pristimantis paisa / taeniatus

## 1. Distancia y overlap

- CENTROID_DISTANCE (esta corrida): {centroid_distance_ab:.6f} (confirma el 0.1944 de la fase anterior: {report['prior_measurement_confirmed']['matches']})
- Percentil entre las 820 distancias de pares: {percentile_rank:.2f} (0=el par mas cercano posible)
- Intra-species variance A (paisa): mean_dist_to_centroid={intra_a['mean_dist_to_centroid']:.4f} (n={intra_a['n']})
- Intra-species variance B (taeniatus): mean_dist_to_centroid={intra_b['mean_dist_to_centroid']:.4f} (n={intra_b['n']})
- Cross-species overlap: {overlap_a_to_b['fraction_misassigned']*100:.1f}% de embeddings de paisa mas cerca del centroide de taeniatus; {overlap_b_to_a['fraction_misassigned']*100:.1f}% al reves.

## 2. K-means k=2 (division en subclusters)

- paisa: {json.dumps(kmeans_a)}
- taeniatus: {json.dumps(kmeans_b)}

## 3. Geografia / Altitud

{json.dumps(geo_alt, indent=2, ensure_ascii=False)}

## 4. Ablacion A/B/C/D (especifica del par, n={ablation['n_eval_samples_with_real_coords']})

{json.dumps(ablation['accuracy_by_variant'], indent=2)}

{ablation['coverage_note']}

## 5. Veredicto

`{sep_level}`

{json.dumps(verdict, indent=2, ensure_ascii=False)}
"""
    OUT_MD.write_text(md, encoding="utf-8")
    print(json.dumps(verdict, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
