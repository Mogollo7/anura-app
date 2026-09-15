"""Species-by-species and cross-package test for context-enriched packages."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from merlin_runtime_pipeline import MerlinRuntimePipeline  # noqa: E402
from package_manager import FilesystemPackageSource, LocalPackageManager  # noqa: E402

REPOSITORY = HERE / "package_repository"
PACKAGE_ROOT = HERE / "packages_root"
OUTPUT = HERE / "context_package_species_test_20260914.json"
PACKAGE_IDS = {
    "antioquia": "anura_antioquia_visual",
    "cauca": "anura_cauca_visual",
}
PACKAGE_VERSIONS = {"antioquia": "v1.1.0", "cauca": "v1.1.0"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def package_species(package_id: str, version: str) -> list[dict]:
    return load(REPOSITORY / package_id / version / "species.json")["species"]


def image_for(scientific_name: str) -> Path | None:
    directory = ROOT / "data cleaned" / scientific_name.replace(" ", "_")
    if not directory.exists():
        return None
    images = sorted(
        p for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    )
    return images[0] if images else None


def make_manager(tmp: Path, modes: tuple[str, ...], refs: dict):
    manager = LocalPackageManager(tmp / "packages_root")
    source = FilesystemPackageSource(REPOSITORY)
    for mode in modes:
        package_id = PACKAGE_IDS[mode]
        version = PACKAGE_VERSIONS[mode]
        manager.install(source, refs[f"{package_id}@{version}"])
        manager.activate(package_id, version)
    return manager


def run_one(manager: LocalPackageManager, image: Path, case_id: str) -> dict:
    pipeline = MerlinRuntimePipeline(manager)
    result = pipeline.identify_image(
        image,
        case_id,
        is_anuran=True,
        anuran_evidence={"source": "context_package_species_test", "ground_truth_used": False},
        top_k=3,
    )
    evidence = result["open_set_evidence"]
    return {
        "image": str(image.relative_to(ROOT)),
        "decision": result["decision"],
        "top1": result["candidates"][0]["scientific_name"] if result["candidates"] else None,
        "top3": [row["scientific_name"] for row in result["candidates"]],
        "candidate_count": len(result["candidates"]),
        "nearest_species_id": evidence.get("nearest_species_id"),
        "open_set_score": evidence.get("score"),
        "active_centroid_count": evidence.get("active_centroid_count"),
        "geo_available": result["input_metadata"]["runtime"]["geographic"]["available"],
        "encoder_sha256": result["input_metadata"]["runtime"]["bioclip"]["encoder_sha256"],
    }


def species_matrix(refs: dict) -> dict:
    output: dict = {}
    for mode in ("antioquia", "cauca"):
        package_id = PACKAGE_IDS[mode]
        version = PACKAGE_VERSIONS[mode]
        species_rows = package_species(package_id, version)
        tmp = Path(tempfile.mkdtemp(prefix=f"merlin-{mode}-"))
        try:
            manager = make_manager(tmp, (mode,), refs)
            context_geo = manager.active_geography()
            context_elev = manager.active_elevation()
            rows = []
            missing_images = []
            for species in species_rows:
                name = species["scientific_name"]
                image = image_for(name)
                if image is None:
                    missing_images.append(name)
                    continue
                result = run_one(manager, image, f"species:{mode}:{species['species_id']}")
                result.update({
                    "species_id": species["species_id"],
                    "expected_species": name,
                    "expected_in_active_package": True,
                    "context_geography_present": species["species_id"] in context_geo,
                    "context_elevation_present": species["species_id"] in context_elev,
                    "top1_matches_expected": result["top1"] == name,
                })
                rows.append(result)
            output[mode] = {
                "package": f"{package_id}@{version}",
                "active_species": len(manager.active_species()),
                "geography_entries": len(context_geo),
                "elevation_entries": len(context_elev),
                "images_tested": len(rows),
                "images_missing": missing_images,
                "top1_matches": sum(row["top1_matches_expected"] for row in rows),
                "results": rows,
            }
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return output


def cross_package_matrix(refs: dict) -> dict:
    samples = {
        "antioquia_exclusive": image_for("Dendrobates truncatus"),
        "cauca_exclusive": image_for("Boana cinerascens"),
        "shared": image_for("Boana boans"),
    }
    output: dict = {}
    for label, modes in (
        ("antioquia_only", ("antioquia",)),
        ("cauca_only", ("cauca",)),
        ("both", ("antioquia", "cauca")),
    ):
        tmp = Path(tempfile.mkdtemp(prefix=f"merlin-cross-{label}-"))
        try:
            manager = make_manager(tmp, modes, refs)
            output[label] = {
                "active_packages": [f"{p.package_id}@{p.package_version}" for p in manager.active_packages()],
                "active_species": len(manager.active_species()),
                "results": {
                    sample: run_one(manager, image, f"cross:{label}:{sample}")
                    for sample, image in samples.items()
                    if image is not None
                },
            }
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return output


def main() -> None:
    source = FilesystemPackageSource(REPOSITORY)
    refs = {ref.key: ref for ref in source.list_available()}
    report = {
        "status": "COMPLETED",
        "date": "2026-09-14",
        "encoder": "bioclip/checkpoints/encoder_anura_fp16.onnx",
        "package_versions": PACKAGE_VERSIONS,
        "context_is_read_only_metadata": True,
        "context_is_used_in_score": False,
        "species_by_species": species_matrix(refs),
        "cross_package_reproduction": cross_package_matrix(refs),
        "historical_artifacts_modified": False,
    }
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    summary = {
        mode: {
            "images_tested": data["images_tested"],
            "top1_matches": data["top1_matches"],
            "missing": data["images_missing"],
        }
        for mode, data in report["species_by_species"].items()
    }
    print(json.dumps({"output": str(OUTPUT), "summary": summary, "cross": report["cross_package_reproduction"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
