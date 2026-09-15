"""Compare Merlin-like package releases on the same species image matrix."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from merlin_runtime_pipeline import MerlinRuntimePipeline  # noqa: E402
from package_manager import FilesystemPackageSource, LocalPackageManager  # noqa: E402

REPOSITORY = HERE / "package_repository"
OUTPUT = HERE / "package_performance_comparison_20260914.json"
PACKAGES = {
    "antioquia": "anura_antioquia_visual",
    "cauca": "anura_cauca_visual",
}
VERSIONS = ("v1.0.0", "v1.1.0", "v1.2.0")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def image_for(scientific_name: str) -> Path | None:
    directory = ROOT / "data cleaned" / scientific_name.replace(" ", "_")
    if not directory.exists():
        return None
    images = sorted(
        p for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    )
    return images[0] if images else None


def make_manager(tmp: Path, package_id: str, version: str, refs: dict) -> LocalPackageManager:
    manager = LocalPackageManager(tmp / "packages_root")
    source = FilesystemPackageSource(REPOSITORY)
    ref = refs[f"{package_id}@{version}"]
    manager.install(source, ref)
    manager.activate(package_id, version)
    return manager


def context_stats(package_dir: Path) -> dict:
    result = {"geography_entries": 0, "elevation_entries": 0, "observations": 0,
              "inat_cache_coordinates": 0, "elevations": 0}
    for filename, field in (("geography.json", "geography_entries"), ("elevation.json", "elevation_entries")):
        path = package_dir / filename
        if path.exists():
            result[field] = len(load(path).get("species", {}))
    observations = package_dir / "observations.json"
    if observations.exists():
        rows = [row for species_rows in load(observations)["species"].values() for row in species_rows]
        result["observations"] = len(rows)
        result["inat_cache_coordinates"] = sum(
            row.get("coordinate_source") == "inat_observations_cache" for row in rows
        )
        result["elevations"] = sum(row.get("elevation_m") is not None for row in rows)
    return result


def compare_release(package_id: str, mode: str, version: str, refs: dict) -> dict:
    package_dir = REPOSITORY / package_id / version
    species = load(package_dir / "species.json")["species"]
    tmp = Path(tempfile.mkdtemp(prefix=f"merlin-perf-{mode}-{version}-"))
    started = time.perf_counter()
    rows = []
    missing = []
    try:
        manager = make_manager(tmp, package_id, version, refs)
        pipeline = MerlinRuntimePipeline(manager)
        for item in species:
            image = image_for(item["scientific_name"])
            if image is None:
                missing.append(item["scientific_name"])
                continue
            result = pipeline.identify_image(
                image,
                f"performance:{mode}:{version}:{item['species_id']}",
                is_anuran=True,
                anuran_evidence={"source": "package_performance_comparison", "ground_truth_used": False},
                top_k=3,
            )
            rows.append({
                "species_id": item["species_id"],
                "expected": item["scientific_name"],
                "top1": result["candidates"][0]["scientific_name"] if result["candidates"] else None,
                "top3": [candidate["scientific_name"] for candidate in result["candidates"]],
                "top1_match": bool(result["candidates"]) and result["candidates"][0]["scientific_name"] == item["scientific_name"],
                "decision": result["decision"],
                "open_set_score": result["open_set_evidence"].get("score"),
                "active_species": result["open_set_evidence"].get("active_species_count"),
            })
        elapsed = time.perf_counter() - started
        return {
            "package": f"{package_id}@{version}",
            "images_tested": len(rows),
            "images_missing": missing,
            "top1_matches": sum(row["top1_match"] for row in rows),
            "top1_accuracy": sum(row["top1_match"] for row in rows) / len(rows) if rows else None,
            "elapsed_seconds": round(elapsed, 3),
            "seconds_per_image": round(elapsed / len(rows), 4) if rows else None,
            "active_species": len(manager.active_species()),
            "context": context_stats(package_dir),
            "results": rows,
        }
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> None:
    source = FilesystemPackageSource(REPOSITORY)
    refs = {ref.key: ref for ref in source.list_available()}
    report = {
        "status": "COMPLETED",
        "date": "2026-09-14",
        "protocol": {
            "same_first_image_per_species": True,
            "same_encoder_and_threshold": True,
            "ground_truth_used_for_inference": False,
            "context_used_in_score": False,
            "comparison_scope": "visual ranking + Open Set; metadata coverage separately",
        },
        "releases": {
            mode: {
                version: compare_release(package_id, mode, version, refs)
                for version in VERSIONS
            }
            for mode, package_id in PACKAGES.items()
        },
        "historical_artifacts_modified": False,
    }
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    summary = {
        mode: {
            version: {
                "tested": result["images_tested"],
                "top1": f"{result['top1_matches']}/{result['images_tested']}",
                "accuracy": result["top1_accuracy"],
                "seconds": result["elapsed_seconds"],
                "context": result["context"],
            }
            for version, result in versions.items()
        }
        for mode, versions in report["releases"].items()
    }
    print(json.dumps({"output": str(OUTPUT), "summary": summary}, ensure_ascii=False))


if __name__ == "__main__":
    main()
