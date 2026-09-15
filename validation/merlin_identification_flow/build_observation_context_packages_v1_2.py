"""Build v1.2 packages with observation-level iNaturalist context provenance."""
from __future__ import annotations

import json
import shutil
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPOSITORY = HERE / "package_repository"
GEO_CACHE = ROOT / "validation/fase23a_geographic_context/cache/inat_observations_cache.json"
TOPO_CACHE = ROOT / "validation/open_set_topography_v1/opentopodata_cache.json"
from package_manager import PACKAGE_SCHEMA_VERSION, compute_payload_sha256


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def key(lat: float, lon: float) -> str:
    return f"{lat:.7f},{lon:.7f}"


def package_species(package_dir: Path) -> dict[str, str]:
    return {
        row["species_id"]: row["scientific_name"]
        for row in load(package_dir / "species.json")["species"]
    }


def occurrence_rows(scientific_name: str, department: str) -> list[dict]:
    species_files = ROOT.glob(f"COLOMBIA_ANURA/{department}/SPECIES/*/species.json")
    for species_file in species_files:
        species = load(species_file)
        if species.get("scientific_name") != scientific_name:
            continue
        occurrence_file = species_file.parent / "occurrences.json"
        return load(occurrence_file) if occurrence_file.exists() else []
    return []


def build_context(package_dir: Path, department: str) -> tuple[dict, dict, dict]:
    geo_cache = load(GEO_CACHE)
    topo_cache = load(TOPO_CACHE)
    species = package_species(package_dir)
    observations: dict[str, list[dict]] = {}
    elevations: dict[str, list[float]] = defaultdict(list)
    geography: dict[str, dict] = {}
    elevation: dict[str, dict] = {}

    for species_id, scientific_name in sorted(species.items()):
        rows = []
        for row in occurrence_rows(scientific_name, department):
            observation_id = str(row["observation_id"])
            cached = geo_cache.get(observation_id)
            lat = float(cached["lat"]) if cached and cached.get("lat") is not None else float(row["latitude"])
            lon = float(cached["lon"]) if cached and cached.get("lon") is not None else float(row["longitude"])
            topo = topo_cache.get(key(lat, lon), {})
            elevation_m = topo.get("elevation_m")
            record = {
                "observation_id": observation_id,
                "latitude": lat,
                "longitude": lon,
                "coordinate_source": "inat_observations_cache" if cached else "occurrence_manifest",
                "geoprivacy": cached.get("geoprivacy") if cached else None,
                "positional_accuracy_m": cached.get("positional_accuracy") if cached else row.get("positional_accuracy"),
                "elevation_m": elevation_m,
                "elevation_source": "opentopodata_cache" if elevation_m is not None else None,
                "observation_url": row.get("url"),
            }
            rows.append(record)
            if elevation_m is not None:
                elevations[species_id].append(float(elevation_m))
        observations[species_id] = rows
        cells = defaultdict(int)
        for row in rows:
            cells[f"G025_{int(round(row['latitude'] / 0.25))}_{int(round(row['longitude'] / 0.25))}"] += 1
        geography[species_id] = {
            "species_id": species_id,
            "scientific_name": scientific_name,
            "n_observations": len(rows),
            "n_unique_cells": len(cells),
            "cells": dict(cells),
            "observation_ids": [row["observation_id"] for row in rows],
        }
        values = np.asarray(elevations[species_id], dtype=np.float64)
        elevation[species_id] = {
            "species_id": species_id,
            "n_elevation_records": int(values.size),
            **(
                {
                    "min": float(values.min()),
                    "p5": float(np.percentile(values, 5)),
                    "p25": float(np.percentile(values, 25)),
                    "median": float(np.percentile(values, 50)),
                    "p75": float(np.percentile(values, 75)),
                    "p95": float(np.percentile(values, 95)),
                    "max": float(values.max()),
                }
                if values.size >= 3
                else {"status": "INSUFFICIENT_DATA (<3 records)"}
            ),
        }

    return (
        {
            "schema_version": "anura.species-package-geography/1.1.0",
            "source": "iNaturalist observation cache keyed by observation_id",
            "department": department,
            "species": geography,
        },
        {
            "schema_version": "anura.species-package-elevation/1.1.0",
            "source": "OpenTopoData cache resolved at iNaturalist observation coordinates",
            "department": department,
            "species": elevation,
        },
        {
            "schema_version": "anura.species-package-observations/1.0.0",
            "source": "iNaturalist observation IDs and cached coordinates",
            "department": department,
            "species": observations,
        },
    )


def build(package_id: str, department: str) -> dict:
    source = REPOSITORY / package_id / "v1.1.0"
    target = REPOSITORY / package_id / "v1.2.0"
    if target.exists():
        raise RuntimeError(f"Refusing to overwrite existing package: {target}")
    shutil.copytree(source, target)
    geography, elevation, observations = build_context(target, department)
    for name, data in (("geography.json", geography), ("elevation.json", elevation), ("observations.json", observations)):
        (target / name).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    manifest = load(target / "manifest.json")
    manifest["package_version"] = "v1.2.0"
    manifest["schema_version"] = PACKAGE_SCHEMA_VERSION
    payload_sha, files = compute_payload_sha256(target)
    manifest["checksum"] = {"algorithm": "sha256", "payload_sha256": payload_sha, "files": files}
    manifest["context_extension"] = {
        "geography_json": True,
        "elevation_json": True,
        "observations_json": True,
        "observation_level_provenance": True,
        "coordinate_source": "inat_observations_cache",
        "topography_source": "opentopodata_cache",
        "source_version_untouched": "v1.1.0",
        "note": "Contexto por observation_id; no modifica score visual ni Open Set automáticamente.",
    }
    (target / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return {
        "package": f"{package_id}@v1.2.0",
        "species": len(manifest["species_ids"]),
        "observations": sum(len(rows) for rows in observations["species"].values()),
        "coordinates_from_inat_cache": sum(
            sum(row["coordinate_source"] == "inat_observations_cache" for row in rows)
            for rows in observations["species"].values()
        ),
        "elevations_from_topography_cache": sum(
            sum(row["elevation_m"] is not None for row in rows)
            for rows in observations["species"].values()
        ),
        "payload_sha256": payload_sha,
    }


def main() -> None:
    print(json.dumps([
        build("anura_antioquia_visual", "ANTIOQUIA"),
        build("anura_cauca_visual", "CAUCA"),
    ], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
