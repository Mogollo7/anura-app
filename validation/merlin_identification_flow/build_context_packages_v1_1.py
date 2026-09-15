"""Build context-enriched Merlin-like packages without changing historical versions."""
from __future__ import annotations

import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPOSITORY = HERE / "package_repository"
GEO_CACHE = ROOT / "validation/fase23a_geographic_context/cache/inat_observations_cache.json"
TOPO_CACHE = ROOT / "validation/open_set_topography_v1/opentopodata_cache.json"
from package_manager import compute_payload_sha256, PACKAGE_SCHEMA_VERSION


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def coordinate_key(lat: float, lon: float) -> str:
    return f"{lat:.7f},{lon:.7f}"


def percentile_summary(values: list[float]) -> dict:
    if len(values) < 3:
        return {"n_elevation_records": len(values), "status": "INSUFFICIENT_DATA (<3 records)"}
    arr = np.asarray(values, dtype=np.float64)
    return {
        "n_elevation_records": int(arr.size),
        "min": float(arr.min()),
        "p5": float(np.percentile(arr, 5)),
        "p25": float(np.percentile(arr, 25)),
        "median": float(np.percentile(arr, 50)),
        "p75": float(np.percentile(arr, 75)),
        "p95": float(np.percentile(arr, 95)),
        "max": float(arr.max()),
    }


def context_from_cauca(package_dir: Path, species_ids: set[str]) -> tuple[dict, dict]:
    resolution = load(ROOT / "COLOMBIA_ANURA/CAUCA/metadata/species_id_resolution.json")
    geo_cache = load(GEO_CACHE)
    topo_cache = load(TOPO_CACHE)
    by_id = {row["species_id"]: row["scientific_name"] for row in resolution["resolutions"]}
    points: dict[str, list[tuple[float, float]]] = defaultdict(list)
    elevations: dict[str, list[float]] = defaultdict(list)

    for species_id, scientific_name in by_id.items():
        if species_id not in species_ids:
            continue
        species_dir = next(
            ROOT.glob(f"COLOMBIA_ANURA/CAUCA/SPECIES/*/species.json"),
            None,
        )
        # Resolve the occurrence file through the taxon_id in the resolution.
        resolution_row = next(r for r in resolution["resolutions"] if r["species_id"] == species_id)
        occurrence_path = ROOT / "COLOMBIA_ANURA/CAUCA/SPECIES" / resolution_row["taxon_id"] / "occurrences.json"
        if not occurrence_path.exists():
            continue
        for row in load(occurrence_path):
            lat, lon = float(row["latitude"]), float(row["longitude"])
            points[species_id].append((lat, lon))
            cached = geo_cache.get(str(row["observation_id"]))
            if cached:
                lat, lon = float(cached["lat"]), float(cached["lon"])
            elevation = topo_cache.get(coordinate_key(lat, lon), {}).get("elevation_m")
            if elevation is not None:
                elevations[species_id].append(float(elevation))

    geography = {
        "schema_version": "anura.species-package-geography/1.0.0",
        "source": "COLOMBIA_ANURA/CAUCA/SPECIES/*/occurrences.json + GEO cache",
        "method": "Observed points and 0.25-degree cells; no inferred polygons.",
        "species": {},
    }
    elevation = {
        "schema_version": "anura.species-package-elevation/1.0.0",
        "source": "open_set_topography_v1/opentopodata_cache.json at observed coordinates",
        "method": "Percentiles of cached SRTM elevation values; missing values remain explicit.",
        "species": {},
    }
    names = {row["species_id"]: row["scientific_name"] for row in resolution["resolutions"]}
    for species_id in sorted(species_ids):
        pts = points.get(species_id, [])
        cells = defaultdict(int)
        for lat, lon in pts:
            cells[f"G025_{int(round(lat / 0.25))}_{int(round(lon / 0.25))}"] += 1
        entry = {"species_id": species_id, "scientific_name": names.get(species_id), "n_records": len(pts), "n_unique_cells": len(cells), "cells": dict(cells)}
        if pts:
            entry["bbox"] = {
                "lat_min": min(p[0] for p in pts), "lat_max": max(p[0] for p in pts),
                "lon_min": min(p[1] for p in pts), "lon_max": max(p[1] for p in pts),
            }
        geography["species"][species_id] = entry
        elevation["species"][species_id] = {"species_id": species_id, **percentile_summary(elevations.get(species_id, []))}
    return geography, elevation


def context_from_antioquia(package_dir: Path, species_ids: set[str]) -> tuple[dict, dict]:
    distribution = load(HERE / "stress_test_v1/species_distribution_maps_v1.json")
    elevation = load(HERE / "stress_test_v1/elevation_ranges_v1.json")
    name_by_id = {value["species_id"]: name for name, value in distribution["species"].items()}
    geo = {"schema_version": "anura.species-package-geography/1.0.0", "source": "stress_test_v1/species_distribution_maps_v1.json", "species": {}}
    elev = {"schema_version": "anura.species-package-elevation/1.0.0", "source": "stress_test_v1/elevation_ranges_v1.json", "species": {}}
    for species_id in sorted(species_ids):
        name = name_by_id.get(species_id)
        if name is not None:
            geo["species"][species_id] = distribution["species"][name]
            elev["species"][species_id] = elevation["species"].get(name, {"species_id": species_id, "status": "MISSING_SOURCE_ENTRY"})
        else:
            geo["species"][species_id] = {"species_id": species_id, "status": "MISSING_SOURCE_ENTRY"}
            elev["species"][species_id] = {"species_id": species_id, "status": "MISSING_SOURCE_ENTRY"}
    return geo, elev


def build(package_id: str, source_version: str = "v1.0.0") -> dict:
    source = REPOSITORY / package_id / source_version
    target = REPOSITORY / package_id / "v1.1.0"
    if target.exists():
        raise RuntimeError(f"Refusing to overwrite existing package: {target}")
    shutil.copytree(source, target)
    manifest = load(source / "manifest.json")
    species_ids = set(manifest["species_ids"])
    if package_id == "anura_cauca_visual":
        geography, elevation = context_from_cauca(target, species_ids)
    else:
        geography, elevation = context_from_antioquia(target, species_ids)
    (target / "geography.json").write_text(json.dumps(geography, indent=2, ensure_ascii=False), encoding="utf-8")
    (target / "elevation.json").write_text(json.dumps(elevation, indent=2, ensure_ascii=False), encoding="utf-8")
    manifest["package_version"] = "v1.1.0"
    manifest["schema_version"] = PACKAGE_SCHEMA_VERSION
    payload_sha, files = compute_payload_sha256(target)
    manifest["checksum"] = {"algorithm": "sha256", "payload_sha256": payload_sha, "files": files}
    manifest["context_extension"] = {
        "geography_json": True,
        "elevation_json": True,
        "geography_species_count": len(geography["species"]),
        "elevation_species_count": len(elevation["species"]),
        "source_version_untouched": source_version,
        "note": "Contexto opcional por especie; no modifica ranking ni Open Set automáticamente.",
    }
    (target / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return {
        "package_id": package_id,
        "version": "v1.1.0",
        "species_count": len(species_ids),
        "geography_species_count": len(geography["species"]),
        "elevation_species_count": len(elevation["species"]),
        "payload_sha256": payload_sha,
    }


def main() -> None:
    results = [build("anura_antioquia_visual"), build("anura_cauca_visual")]
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
