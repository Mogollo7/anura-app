"""PARTE 1.1 (masivas, re-encodeando una muestra real) y PARTE 1.4 (memoria/repeticion).

Muestra: 300 imagenes reales.
  - 240 KNOWN: muestreo estratificado por especie (round-robin sobre las 43 carpetas de
    "data cleaned/<especie>/", tomando ceil(240/43) por especie hasta completar 240, orden
    alfabetico de especie y de archivo dentro de especie para reproducibilidad -- semilla no
    aplica porque no hay aleatoriedad, es determinista por orden).
  - 60 UNKNOWN: muestreo estratificado por subcarpeta de
    "data/unknown_open_set_v2/images/{final,historical,new,primary,supplementary_historical}/",
    mismo criterio round-robin determinista.
Total = 300, criterio documentado arriba (no aleatorio: reproducible sin semilla).

Para cada imagen se corre el pipeline real completo (imagen->preprocessing->ONNX->
embedding->ranking->OpenSet->IdentificationResult) y se registra: exito/fallo, tipo de
fallo, NaN/Inf en embedding, dimension del embedding, score valido, tiempo de inferencia,
y RSS del proceso (psutil) tras cada imagen -- esto cubre 1.1 y 1.4 en la misma corrida
(300 >= el rango 50-100 pedido para memoria).
"""
from __future__ import annotations

import gc
import json
import sys
import time
from itertools import islice
from pathlib import Path

import numpy as np
import psutil

HERE = Path(__file__).resolve().parents[2]
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from merlin_runtime_pipeline import MerlinRuntimePipeline  # noqa: E402

OUT = HERE / "stress_test_v1/mass_inference_results.json"
OUT_MEM = HERE / "stress_test_v1/memory_stability_results.json"

KNOWN_ROOT = ROOT / "data cleaned"
UNKNOWN_ROOTS = [
    ROOT / "data/unknown_open_set_v2/images/final",
    ROOT / "data/unknown_open_set_v2/images/historical",
    ROOT / "data/unknown_open_set_v2/images/new",
    ROOT / "data/unknown_open_set_v2/images/primary",
    ROOT / "data/unknown_open_set_v2/images/supplementary_historical",
]

N_KNOWN = 240
N_UNKNOWN = 60


def round_robin_sample(groups: list[list[Path]], n: int) -> list[Path]:
    iters = [iter(g) for g in groups]
    out: list[Path] = []
    while len(out) < n and iters:
        alive = []
        for it in iters:
            try:
                out.append(next(it))
                if len(out) >= n:
                    break
            except StopIteration:
                continue
            alive.append(it)
        iters = alive
        if not iters:
            break
    return out[:n]


def build_sample() -> list[tuple[str, Path]]:
    species_dirs = sorted([d for d in KNOWN_ROOT.iterdir() if d.is_dir()])
    known_groups = [sorted(d.glob("*.jpg")) + sorted(d.glob("*.JPG")) for d in species_dirs]
    known_groups = [g for g in known_groups if g]
    known_sample = round_robin_sample(known_groups, N_KNOWN)

    unknown_groups = []
    for r in UNKNOWN_ROOTS:
        if r.exists():
            files = sorted(r.rglob("*.jpg")) + sorted(r.rglob("*.jpeg"))
            if files:
                unknown_groups.append(files)
    unknown_sample = round_robin_sample(unknown_groups, N_UNKNOWN)

    sample = [("KNOWN", p) for p in known_sample] + [("UNKNOWN", p) for p in unknown_sample]
    return sample


def main() -> None:
    sample = build_sample()
    pipeline = MerlinRuntimePipeline()
    process = psutil.Process()

    counters = {
        "total_images": len(sample),
        "successful_inference": 0,
        "failed_inference": 0,
        "timeouts": 0,  # no hard timeout wrapper used (single-process, sequential); 0 by construction
        "nan_or_inf_embedding": 0,
        "empty_embeddings": 0,
        "invalid_dimensions": 0,
        "invalid_scores": 0,
        "contract_errors": 0,
    }
    failures = []
    per_image_records = []
    rss_samples = []
    timing_ms = []

    gc.collect()
    rss_start = process.memory_info().rss

    for i, (pool, path) in enumerate(sample):
        rec = {"index": i, "pool": pool, "path": str(path.relative_to(ROOT))}
        t0 = time.perf_counter()
        try:
            embedding, meta = pipeline.bioclip.embed_image(path)
            dim_ok = embedding.shape == (512,)
            finite_ok = bool(np.all(np.isfinite(embedding)))
            if not dim_ok:
                counters["invalid_dimensions"] += 1
            if not finite_ok:
                counters["nan_or_inf_embedding"] += 1
            if embedding.size == 0:
                counters["empty_embeddings"] += 1

            active_ids, active_prototypes, active_names, catalog_state = pipeline._active_catalog()
            visual_rows, visual_metadata = pipeline.ranking.rank_visual(embedding, active_names)
            known_visual_rows = [(n, s) for n, s in visual_rows if n in pipeline.flow.catalog]
            score_ok = all(np.isfinite(s) for _, s in known_visual_rows)
            if not score_ok:
                counters["invalid_scores"] += 1
            decision, evidence = pipeline.open_set.assess(embedding, active_species_ids=active_ids, active_prototypes=active_prototypes)
            if evidence.get("score") is not None and not np.isfinite(evidence["score"]):
                counters["invalid_scores"] += 1
            if decision not in {"ESPECIE_CONOCIDA", "NO_CONCLUYENTE"}:
                counters["contract_errors"] += 1

            rec["status"] = "SUCCESS"
            rec["decision"] = decision
            rec["embedding_dim"] = int(embedding.shape[0])
            rec["finite"] = finite_ok
            counters["successful_inference"] += 1
        except Exception as exc:  # noqa: BLE001
            rec["status"] = "FAILURE"
            rec["exception_type"] = type(exc).__name__
            rec["exception_message"] = str(exc)[:200]
            counters["failed_inference"] += 1
            failures.append(rec)
        rec["inference_ms"] = round((time.perf_counter() - t0) * 1000, 3)
        timing_ms.append(rec["inference_ms"])
        per_image_records.append(rec)

        if (i + 1) % 5 == 0 or i == len(sample) - 1:
            rss = process.memory_info().rss
            rss_samples.append({"after_n_images": i + 1, "rss_mb": round(rss / (1024 * 1024), 2)})

        if (i + 1) % 25 == 0:
            print(f"{i+1}/{len(sample)} done, last rss_mb={rss_samples[-1]['rss_mb']}")

    rss_end = process.memory_info().rss

    mass_report = {
        "sample_criterion": (
            "300 imagenes reales: 240 KNOWN muestreadas round-robin determinista sobre las 43 "
            "carpetas de especie en 'data cleaned/', 60 UNKNOWN round-robin determinista sobre "
            "5 subcarpetas de 'data/unknown_open_set_v2/images/'. Sin aleatoriedad (reproducible)."
        ),
        **counters,
        "failure_examples": failures[:20],
        "timing_ms": {
            "mean": round(float(np.mean(timing_ms)), 3),
            "p50": round(float(np.percentile(timing_ms, 50)), 3),
            "p95": round(float(np.percentile(timing_ms, 95)), 3),
            "max": round(float(np.max(timing_ms)), 3),
            "min": round(float(np.min(timing_ms)), 3),
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(mass_report, indent=2, ensure_ascii=False), encoding="utf-8")

    # crude monotonic-growth check: linear regression slope of rss over image index
    xs = np.array([s["after_n_images"] for s in rss_samples], dtype=np.float64)
    ys = np.array([s["rss_mb"] for s in rss_samples], dtype=np.float64)
    slope = float(np.polyfit(xs, ys, 1)[0]) if len(xs) > 1 else 0.0
    # crude timing degradation check: slope of inference_ms over index (successful only)
    idxs = np.array([r["index"] for r in per_image_records if r["status"] == "SUCCESS"], dtype=np.float64)
    tvals = np.array([r["inference_ms"] for r in per_image_records if r["status"] == "SUCCESS"], dtype=np.float64)
    time_slope = float(np.polyfit(idxs, tvals, 1)[0]) if len(idxs) > 1 else 0.0

    mem_report = {
        "n_images": len(sample),
        "measurement_method": "psutil.Process().memory_info().rss, sampled every 5 images",
        "rss_start_mb": round(rss_start / (1024 * 1024), 2),
        "rss_end_mb": round(rss_end / (1024 * 1024), 2),
        "rss_delta_mb": round((rss_end - rss_start) / (1024 * 1024), 2),
        "rss_samples": rss_samples,
        "rss_linear_slope_mb_per_image": round(slope, 5),
        "inference_time_linear_slope_ms_per_image": round(time_slope, 5),
        "interpretation": (
            "Pendiente RSS ~0 o negativa => sin crecimiento monotono anomalo. Pendiente de "
            "tiempo de inferencia ~0 => sin degradacion progresiva. Ambas medidas SOLO en "
            "proceso Python de escritorio (CPU, onnxruntime); NO son cifras de Android -- eso "
            "queda NOT_VERIFIED (requiere dispositivo real)."
        ),
        "android_memory_status": "NOT_VERIFIED: requiere dispositivo Android real, no disponible en esta maquina.",
    }
    OUT_MEM.write_text(json.dumps(mem_report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(counters, indent=2))
    print(json.dumps({"rss_delta_mb": mem_report["rss_delta_mb"], "rss_slope": mem_report["rss_linear_slope_mb_per_image"], "time_slope": mem_report["inference_time_linear_slope_ms_per_image"]}, indent=2))


if __name__ == "__main__":
    main()
