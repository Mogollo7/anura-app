"""PARTE 2 -- Regresion de Open Set con threshold intacto (39.35406371422803).

Reutiliza exactamente la metodologia de run_open_set_post_bugfix_audit.py
(Mahalanobis min-distancia al centroide ACTIVO mas cercano) pero agrega:
  - matriz de errores KNOWN_ACCEPT/KNOWN_REJECT/UNKNOWN_ACCEPT/UNKNOWN_REJECT
  - percentiles de distancia Mahalanobis (KNOWN y UNKNOWN)
  - mas configuraciones de catalogo activo (incluye desactivaciones puntuales)

NO se recalibra el threshold. NO se generan embeddings nuevos.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[2]  # .../merlin_identification_flow
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from runtime_adapters import OpenSetReleaseAdapter  # noqa: E402

THRESHOLD = 39.35406371422803
KNOWN = ROOT / "validation/fase16_clean_open_set/clean_known_embeddings.npz"
UNKNOWN = ROOT / "validation/fase23a_open_set_automatic/embeddings/unknown_embeddings.npz"
OUT = HERE / "stress_test_v1/openset_regression_metrics.json"


def mahalanobis_min(embeddings, centroids, precision):
    out = np.empty(embeddings.shape[0], dtype=np.float64)
    step = 256
    for start in range(0, embeddings.shape[0], step):
        chunk = embeddings[start : start + step]
        diffs = centroids[None, :, :] - chunk[:, None, :]
        squared = np.einsum("nkd,de,nke->nk", diffs, precision, diffs)
        out[start : start + step] = np.sqrt(np.maximum(0.0, squared)).min(axis=1)
    return out


def auroc(known_scores, unknown_scores) -> float:
    labels = np.concatenate([np.zeros(known_scores.size), np.ones(unknown_scores.size)])
    scores = np.concatenate([known_scores, unknown_scores])
    order = np.argsort(scores, kind="mergesort")
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(1, scores.size + 1)
    unique, inverse, counts = np.unique(scores, return_inverse=True, return_counts=True)
    sums = np.zeros(unique.size)
    np.add.at(sums, inverse, ranks)
    ranks = (sums / counts)[inverse]
    n_pos, n_neg = labels.sum(), labels.size - labels.sum()
    return float((ranks[labels == 1].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def percentiles(x: np.ndarray) -> dict:
    ps = [0, 1, 5, 10, 25, 50, 75, 90, 95, 99, 100]
    return {f"p{p}": round(float(np.percentile(x, p)), 4) for p in ps}


def main() -> None:
    adapter = OpenSetReleaseAdapter()
    precision = adapter.precision.astype(np.float64)

    known = np.load(KNOWN, allow_pickle=False)
    unknown = np.load(UNKNOWN, allow_pickle=False)
    known_x = known["embeddings"].astype(np.float64)
    known_species = np.array([str(s) for s in known["species_ids"]])
    unknown_x = unknown["embeddings"].astype(np.float64)

    release_ids = list(adapter.release_species_ids)
    antioquia = json.loads((HERE / "package_repository/anura_antioquia_visual/v1.0.0/manifest.json").read_text(encoding="utf-8"))["species_ids"]
    cauca = json.loads((HERE / "package_repository/anura_cauca_visual/v1.0.0/manifest.json").read_text(encoding="utf-8"))["species_ids"]

    truncatus_id = "ANU_COL_DEND_TRU_001"
    paisa_taeniatus = [s for s in release_ids if s in {"ANU_COL_PRIS_PAI_001", "ANU_COL_PRIS_TAE_001"}]

    configurations = {
        "FULL_41": release_ids,
        "ACTIVE_ANTIOQUIA_plus_CAUCA_34": sorted(set(antioquia) | set(cauca)),
        "ACTIVE_CAUCA_ONLY_17": sorted(cauca),
        "FULL_41_MINUS_TRUNCATUS": [s for s in release_ids if s != truncatus_id],
        "FULL_41_MINUS_PAISA_TAENIATUS_PAIR": [s for s in release_ids if s not in set(paisa_taeniatus)],
    }

    report = {
        "threshold": THRESHOLD,
        "threshold_recalibrated": False,
        "known_source": str(KNOWN.relative_to(ROOT)),
        "unknown_source": str(UNKNOWN.relative_to(ROOT)),
        "known_n_total_pool": int(known_x.shape[0]),
        "unknown_n_total_pool": int(unknown_x.shape[0]),
        "prior_handoff_reference": {
            "AUROC_full_41": 0.538,
            "FAR_full_41": 0.850,
            "source": "AI_TO_ANDROID_HANDOFF.md / OPEN_SET_POST_BUGFIX_AUDIT.md",
        },
        "configurations": {},
    }

    for label, active_ids in configurations.items():
        ids = [s for s in release_ids if s in set(active_ids)]
        centroids = np.stack([adapter.centroid_by_species[s] for s in ids]).astype(np.float64)
        mask = np.isin(known_species, ids)
        known_active = known_x[mask]
        known_scores = mahalanobis_min(known_active, centroids, precision)
        unknown_scores = mahalanobis_min(unknown_x, centroids, precision)

        known_accept = int((known_scores <= THRESHOLD).sum())
        known_reject = int((known_scores > THRESHOLD).sum())
        unknown_accept = int((unknown_scores <= THRESHOLD).sum())
        unknown_reject = int((unknown_scores > THRESHOLD).sum())

        kar = known_accept / known_scores.size if known_scores.size else None
        far = unknown_accept / unknown_scores.size if unknown_scores.size else None

        report["configurations"][label] = {
            "active_centroids": len(ids),
            "known_evaluated": int(mask.sum()),
            "known_excluded_inactive_species": int((~mask).sum()),
            "confusion_matrix": {
                "KNOWN_ACCEPT": known_accept,
                "KNOWN_REJECT": known_reject,
                "UNKNOWN_ACCEPT": unknown_accept,
                "UNKNOWN_REJECT": unknown_reject,
            },
            "KAR": round(kar, 6) if kar is not None else None,
            "FAR": round(far, 6) if far is not None else None,
            "TAR_equals_KAR": round(kar, 6) if kar is not None else None,
            "FNR_equals_1_minus_KAR": round(1 - kar, 6) if kar is not None else None,
            "UDR_equals_1_minus_FAR": round(1 - far, 6) if far is not None else None,
            "AUROC": round(auroc(known_scores, unknown_scores), 6),
            "known_distance_percentiles": percentiles(known_scores),
            "unknown_distance_percentiles": percentiles(unknown_scores),
        }
        print(label, json.dumps(report["configurations"][label]["confusion_matrix"]), "AUROC=", report["configurations"][label]["AUROC"])

    full = report["configurations"]["FULL_41"]
    report["verdict"] = {
        "AUROC_full_41_this_run": full["AUROC"],
        "FAR_full_41_this_run": full["FAR"],
        "matches_handoff_reference": (
            round(full["AUROC"], 3) == 0.538 and round(full["FAR"], 3) == 0.850
        ),
        "statement": (
            "Metricas recalculadas en esta corrida con el pool completo KNOWN=7475/UNKNOWN=620 y "
            "threshold intacto 39.35406371422803. El filtro por catalogo activo se ejercito bajo "
            "carga completa (7475+620 embeddings) en 5 configuraciones distintas, no solo en el "
            "test aislado de 13 pasos."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report["verdict"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
