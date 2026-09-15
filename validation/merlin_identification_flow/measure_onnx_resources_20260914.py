"""Measure host CPU/RAM and artifact size for the ONNX inference path."""
from __future__ import annotations

import json
import os
import random
import shutil
import sys
import tempfile
import time
from pathlib import Path

import psutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from merlin_runtime_pipeline import MerlinRuntimePipeline  # noqa: E402
from package_manager import FilesystemPackageSource, LocalPackageManager  # noqa: E402

OUTPUT = HERE / "onnx_resource_measurement_20260914.json"
REPOSITORY = HERE / "package_repository"
PACKAGE_IDS = ("anura_antioquia_visual", "anura_cauca_visual")
VERSION = "v1.2.0"
SEED = 42


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def images() -> list[Path]:
    names = {}
    for package_id in PACKAGE_IDS:
        for item in load(REPOSITORY / package_id / VERSION / "species.json")["species"]:
            names[item["scientific_name"]] = item["species_id"]
    rng = random.Random(SEED)
    result = []
    for name in sorted(names):
        folder = ROOT / "data cleaned" / name.replace(" ", "_")
        files = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})
        result.append(rng.choice(files))
    return result


def rss_mb(process: psutil.Process) -> float:
    return process.memory_info().rss / (1024 * 1024)


def directory_bytes(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def main() -> None:
    process = psutil.Process(os.getpid())
    source = FilesystemPackageSource(REPOSITORY)
    refs = {ref.key: ref for ref in source.list_available()}
    temp_root = Path(tempfile.mkdtemp(prefix="merlin-resource-"))
    samples = images()
    rows = []
    try:
        baseline = rss_mb(process)
        manager = LocalPackageManager(temp_root / "packages_root")
        for package_id in PACKAGE_IDS:
            manager.install(source, refs[f"{package_id}@{VERSION}"])
            manager.activate(package_id, VERSION)
        after_packages = rss_mb(process)
        pipeline = MerlinRuntimePipeline(manager)
        after_runtime = rss_mb(process)
        peak = after_runtime
        cpu_start = process.cpu_times()
        wall_start = time.perf_counter()
        for index, image in enumerate(samples):
            before = rss_mb(process)
            cpu_before = process.cpu_times()
            start = time.perf_counter()
            pipeline.identify_image(
                image,
                f"resource:{index}",
                is_anuran=True,
                anuran_evidence={"source": "onnx_resource_measurement", "ground_truth_used": False},
                top_k=4,
            )
            elapsed = time.perf_counter() - start
            cpu_after = process.cpu_times()
            cpu_elapsed = (cpu_after.user - cpu_before.user) + (cpu_after.system - cpu_before.system)
            after = rss_mb(process)
            peak = max(peak, before, after)
            rows.append({
                "image": str(image.relative_to(ROOT)),
                "elapsed_ms": round(elapsed * 1000, 3),
                "cpu_ms": round(cpu_elapsed * 1000, 3),
                "cpu_utilization_one_core_equivalent_percent": round(cpu_elapsed / elapsed * 100, 2),
                "rss_before_mb": round(before, 3),
                "rss_after_mb": round(after, 3),
                "rss_delta_mb": round(after - before, 3),
            })
        wall_elapsed = time.perf_counter() - wall_start
        cpu_end = process.cpu_times()
        cpu_seconds = (cpu_end.user - cpu_start.user) + (cpu_end.system - cpu_start.system)
        onnx_size = (ROOT / "bioclip/checkpoints/encoder_anura_fp16.onnx").stat().st_size
        package_sizes = {
            package_id: directory_bytes(REPOSITORY / package_id / VERSION)
            for package_id in PACKAGE_IDS
        }
        report = {
            "status": "COMPLETED",
            "date": "2026-09-14",
            "runtime": {
                "encoder": "encoder_anura_fp16.onnx",
                "provider": "CPUExecutionProvider",
                "active_packages": [f"{x}@{VERSION}" for x in PACKAGE_IDS],
                "images_tested": len(rows),
                "seed": SEED,
            },
            "host_measurement": {
                "process_rss_baseline_mb": round(baseline, 3),
                "process_rss_after_packages_mb": round(after_packages, 3),
                "process_rss_after_runtime_init_mb": round(after_runtime, 3),
                "process_rss_peak_mb": round(peak, 3),
                "process_rss_peak_over_baseline_mb": round(peak - baseline, 3),
                "cpu_process_seconds": round(cpu_seconds, 3),
                "wall_seconds": round(wall_elapsed, 3),
                "cpu_utilization_one_core_equivalent_percent": round(cpu_seconds / wall_elapsed * 100, 2),
                "cpu_times_scope": "this Python process, including model initialization and evaluations excluded from cpu_process_seconds label",
            },
            "artifact_storage": {
                "onnx_bytes": onnx_size,
                "onnx_mib": round(onnx_size / 1024**2, 3),
                "package_bytes": package_sizes,
                "package_mib": {key: round(value / 1024**2, 3) for key, value in package_sizes.items()},
                "combined_bytes": onnx_size + sum(package_sizes.values()),
                "combined_mib": round((onnx_size + sum(package_sizes.values())) / 1024**2, 3),
            },
            "per_image": rows,
            "limitations": [
                "Medición en Windows/CPU, no en un teléfono Android.",
                "RSS incluye Python, ONNX Runtime, OpenCLIP/PIL y cachés del proceso.",
                "No equivale directamente a memoria nativa de una app Android.",
                "El consumo Android debe confirmarse con Android Profiler en el dispositivo objetivo.",
            ],
            "historical_artifacts_modified": False,
        }
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT),
        "rss_peak_mb": report["host_measurement"]["process_rss_peak_mb"],
        "rss_over_baseline_mb": report["host_measurement"]["process_rss_peak_over_baseline_mb"],
        "cpu_seconds": report["host_measurement"]["cpu_process_seconds"],
        "wall_seconds": report["host_measurement"]["wall_seconds"],
        "combined_mib": report["artifact_storage"]["combined_mib"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
