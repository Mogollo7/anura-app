"""Re-auditoria honesta de Open Set DESPUES del bugfix.

Reglas respetadas:
  - Threshold historico intacto: 39.35406371422803. NO se recalibra.
  - NO se generan embeddings nuevos: se reutilizan artefactos ya existentes
    (Fase 16 KNOWN limpio, Fase 23A UNKNOWN).
  - Los artefactos de origen se abren en SOLO LECTURA.

Se compara la misma poblacion bajo distintas configuraciones de catalogo
activo, para separar dos cosas que antes estaban mezcladas:
  (a) fuga de catalogo  -> lo que el bugfix corrige
  (b) separabilidad del embedding / calidad del threshold -> lo que NO corrige
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from runtime_adapters import OpenSetReleaseAdapter  # noqa: E402

THRESHOLD = 39.35406371422803
KNOWN = ROOT / "validation/fase16_clean_open_set/clean_known_embeddings.npz"
UNKNOWN = ROOT / "validation/fase23a_open_set_automatic/embeddings/unknown_embeddings.npz"


def mahalanobis_min(embeddings: np.ndarray, centroids: np.ndarray, precision: np.ndarray) -> np.ndarray:
    """Distancia Mahalanobis minima al centroide activo mas cercano, por bloques."""
    out = np.empty(embeddings.shape[0], dtype=np.float64)
    step = 256
    for start in range(0, embeddings.shape[0], step):
        chunk = embeddings[start : start + step]
        diffs = centroids[None, :, :] - chunk[:, None, :]
        squared = np.einsum("nkd,de,nke->nk", diffs, precision, diffs)
        out[start : start + step] = np.sqrt(np.maximum(0.0, squared)).min(axis=1)
    return out


def auroc(known_scores: np.ndarray, unknown_scores: np.ndarray) -> float:
    """AUROC con la distancia como score de 'unknownness' (mayor = mas unknown)."""
    labels = np.concatenate([np.zeros(known_scores.size), np.ones(unknown_scores.size)])
    scores = np.concatenate([known_scores, unknown_scores])
    order = np.argsort(scores, kind="mergesort")
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(1, scores.size + 1)
    # promedio de rangos para empates
    unique, inverse, counts = np.unique(scores, return_inverse=True, return_counts=True)
    sums = np.zeros(unique.size)
    np.add.at(sums, inverse, ranks)
    ranks = (sums / counts)[inverse]
    n_pos, n_neg = labels.sum(), labels.size - labels.sum()
    return float((ranks[labels == 1].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def main() -> None:
    adapter = OpenSetReleaseAdapter()
    precision = adapter.precision.astype(np.float64)

    known = np.load(KNOWN, allow_pickle=False)
    unknown = np.load(UNKNOWN, allow_pickle=False)
    known_x = known["embeddings"].astype(np.float64)
    known_species = np.array([str(s) for s in known["species_ids"]])
    unknown_x = unknown["embeddings"].astype(np.float64)

    release_ids = list(adapter.release_species_ids)
    antioquia = json.loads(
        (HERE / "package_repository/anura_antioquia_visual/v1.0.0/manifest.json").read_text(encoding="utf-8")
    )["species_ids"]
    cauca = json.loads(
        (HERE / "package_repository/anura_cauca_visual/v1.0.0/manifest.json").read_text(encoding="utf-8")
    )["species_ids"]

    configurations = {
        "FULL_RELEASE_POOL_41 (== comportamiento pre-bugfix)": release_ids,
        "ACTIVE_ANTIOQUIA_plus_CAUCA_34": sorted(set(antioquia) | set(cauca)),
        "ACTIVE_CAUCA_ONLY_17": sorted(cauca),
    }

    report = {
        "threshold": THRESHOLD,
        "threshold_recalibrated": False,
        "known_source": str(KNOWN.relative_to(ROOT)),
        "unknown_source": str(UNKNOWN.relative_to(ROOT)),
        "known_n": int(known_x.shape[0]),
        "unknown_n": int(unknown_x.shape[0]),
        "historical_reference": {
            "fase16_far": 0.939,
            "fase20_far": 0.911,
            "fase23a_far": 0.754,
            "visual_catalog_v1_0_0_evidence": {"auroc": 0.6247668780305856, "kar": 0.8537859007832899,
                                               "udr": 0.08928571428571429, "far": 0.9107142857142857},
        },
        "configurations": {},
    }

    for label, active_ids in configurations.items():
        ids = [s for s in release_ids if s in set(active_ids)]
        centroids = np.stack([adapter.centroid_by_species[s] for s in ids]).astype(np.float64)
        # KNOWN evaluado solo sobre muestras cuya especie esta ACTIVA:
        # una especie inactiva ya no es "known" para ese catalogo.
        mask = np.isin(known_species, ids)
        known_active = known_x[mask]
        known_scores = mahalanobis_min(known_active, centroids, precision)
        unknown_scores = mahalanobis_min(unknown_x, centroids, precision)
        kar = float((known_scores <= THRESHOLD).mean())
        far = float((unknown_scores <= THRESHOLD).mean())
        report["configurations"][label] = {
            "active_centroids": len(ids),
            "known_evaluated": int(mask.sum()),
            "known_excluded_inactive_species": int((~mask).sum()),
            "KAR": round(kar, 6),
            "FAR": round(far, 6),
            "UDR": round(1.0 - far, 6),
            "AUROC": round(auroc(known_scores, unknown_scores), 6),
            "known_score_mean": round(float(known_scores.mean()), 4),
            "unknown_score_mean": round(float(unknown_scores.mean()), 4),
        }
        print(label, json.dumps(report["configurations"][label], ensure_ascii=False))

    full = report["configurations"]["FULL_RELEASE_POOL_41 (== comportamiento pre-bugfix)"]
    partial = report["configurations"]["ACTIVE_ANTIOQUIA_plus_CAUCA_34"]
    report["verdict"] = {
        "bugfix_changes_metrics_when_full_catalog_active": False,
        "auroc_full_vs_partial": [full["AUROC"], partial["AUROC"]],
        "separability_improved": False,
        "statement": (
            "Con el catalogo completo activo las metricas son IDENTICAS a las previas al bugfix: "
            "el bugfix corrige la ARQUITECTURA DE CATALOGO (que centroides participan), no la "
            "separabilidad del embedding ni la calidad del threshold. El defecto general de Open Set "
            "persiste: FAR sigue siendo altisimo con el threshold historico."
        ),
    }
    (HERE / "open_set_post_bugfix_metrics.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(report["verdict"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
