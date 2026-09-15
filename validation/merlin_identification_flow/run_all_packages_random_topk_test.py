"""Evaluate all active packages with one reproducible random photo per species."""
from __future__ import annotations

import json
import random
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
OUTPUT = HERE / "all_packages_random_topk_test_20260914.json"
VERSION = "v1.2.0"
PACKAGE_IDS = ("anura_antioquia_visual", "anura_cauca_visual")
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
SEED = 42


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def random_image(name: str, rng: random.Random) -> Path | None:
    folder = ROOT / "data cleaned" / name.replace(" ", "_")
    if not folder.exists():
        return None
    images = sorted(path for path in folder.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES)
    return rng.choice(images) if images else None


def main() -> None:
    source = FilesystemPackageSource(REPOSITORY)
    refs = {ref.key: ref for ref in source.list_available()}
    package_species: dict[str, str] = {}
    for package_id in PACKAGE_IDS:
        for item in load(REPOSITORY / package_id / VERSION / "species.json")["species"]:
            package_species[item["scientific_name"]] = item["species_id"]

    rng = random.Random(SEED)
    samples = []
    for name, species_id in sorted(package_species.items()):
        image = random_image(name, rng)
        if image is not None:
            samples.append({"species_id": species_id, "expected": name, "image": image})

    temp_root = Path(tempfile.mkdtemp(prefix="merlin-all-packages-"))
    rows = []
    try:
        manager = LocalPackageManager(temp_root / "packages_root")
        for package_id in PACKAGE_IDS:
            manager.install(source, refs[f"{package_id}@{VERSION}"])
            manager.activate(package_id, VERSION)
        pipeline = MerlinRuntimePipeline(manager)
        for index, sample in enumerate(samples):
            result = pipeline.identify_image(
                sample["image"],
                f"all-packages-random:{index}:{sample['species_id']}",
                is_anuran=True,
                anuran_evidence={"source": "all_packages_random_topk_test", "ground_truth_used": False},
                top_k=4,
            )
            names = [row["scientific_name"] for row in result["candidates"]]
            rows.append({
                "species_id": sample["species_id"],
                "expected": sample["expected"],
                "image": str(sample["image"].relative_to(ROOT)),
                "top1": names[:1],
                "top3": names[:3],
                "top4": names[:4],
                "top1_match": sample["expected"] in names[:1],
                "top3_match": sample["expected"] in names[:3],
                "top4_match": sample["expected"] in names[:4],
                "decision": result["decision"],
                "open_set_score": result["open_set_evidence"].get("score"),
            })
        report = {
            "status": "COMPLETED",
            "date": "2026-09-14",
            "protocol": {
                "active_packages": [f"{package_id}@{VERSION}" for package_id in PACKAGE_IDS],
                "unique_species_in_union": len(package_species),
                "images_per_species": 1,
                "selection": "random reproducible",
                "random_seed": SEED,
                "top_k_requested": 4,
                "ground_truth_used_for_inference": False,
                "context_used_in_score": False,
            },
            "active_species": len(manager.active_species()),
            "images_tested": len(rows),
            "images_missing": sorted(set(package_species) - {row["expected"] for row in rows}),
            "top1_matches": sum(row["top1_match"] for row in rows),
            "top3_matches": sum(row["top3_match"] for row in rows),
            "top4_matches": sum(row["top4_match"] for row in rows),
            "top1_accuracy": sum(row["top1_match"] for row in rows) / len(rows),
            "top3_accuracy": sum(row["top3_match"] for row in rows) / len(rows),
            "top4_accuracy": sum(row["top4_match"] for row in rows) / len(rows),
            "results": rows,
            "historical_artifacts_modified": False,
        }
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT),
        "active_species": report["active_species"],
        "images_tested": report["images_tested"],
        "top1": f"{report['top1_matches']}/{report['images_tested']} ({report['top1_accuracy']:.2%})",
        "top3": f"{report['top3_matches']}/{report['images_tested']} ({report['top3_accuracy']:.2%})",
        "top4": f"{report['top4_matches']}/{report['images_tested']} ({report['top4_accuracy']:.2%})",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
