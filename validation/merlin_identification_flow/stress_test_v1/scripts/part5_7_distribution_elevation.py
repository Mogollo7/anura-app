"""PARTE 5 y 7 -- Mapas de distribucion por especie + rangos de elevacion.

Fuente: COLOMBIA_ANURA/ANTIOQUIA/occurrences/records_v1.csv (15,081 registros,
lat/lon/elevation_m/cell_id ya extraidos -- reutilizado, no reconstruido).

Para cada una de las 41 especies del catalogo (via species_registry.json ->
canonical_name -> match contra records_v1.csv['input_name']):
  - distribution_area: celdas G025 (grid 0.25 grados) con conteo de registros.
  - elevation stats: percentiles de elevation_m no nulo.

No se generan poligonos nuevos (serian inventados sin evidencia adicional); se
usan celdas+conteos agregados, formato documentado en el JSON de salida.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[2]
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from runtime_adapters import canonical_name  # noqa: E402

RECORDS = ROOT / "COLOMBIA_ANURA/ANTIOQUIA/occurrences/records_v1.csv"
OUT_DIST = HERE / "stress_test_v1/species_distribution_maps_v1.json"
OUT_ELEV = HERE / "stress_test_v1/elevation_ranges_v1.json"


def main() -> None:
    registry = json.loads((ROOT / "taxonomy/species/species_registry.json").read_text(encoding="utf-8"))
    catalog_names = {canonical_name(s["scientific_name"]): s["species_id"] for s in registry["species"]}

    by_species_cells: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    by_species_elev: dict[str, list[float]] = defaultdict(list)
    by_species_points: dict[str, list[tuple[float, float]]] = defaultdict(list)
    n_rows = 0
    n_matched = 0

    with RECORDS.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            n_rows += 1
            name = canonical_name(row["input_name"])
            if name not in catalog_names:
                continue
            n_matched += 1
            by_species_cells[name][row["cell_id"]] += 1
            try:
                lat, lon = float(row["latitude"]), float(row["longitude"])
                by_species_points[name].append((lat, lon))
            except (ValueError, KeyError):
                pass
            elev = row.get("elevation_m", "")
            if elev:
                try:
                    v = float(elev)
                    by_species_elev[name].append(v)
                except ValueError:
                    pass

    distribution = {
        "schema_version": "anura.species-distribution-maps/1.0.0",
        "format": (
            "Por especie: 'cells' es un dict {cell_id (grid G025, 0.25 grados, definido en "
            "cell_zone_map_v1.csv/records_v1.csv): count} agregando registros de "
            "records_v1.csv. NO son poligonos -- son celdas de ocurrencia con frecuencia, "
            "suficiente para comparar una coordenada nueva contra el area conocida sin "
            "inventar geometria adicional."
        ),
        "source": str(RECORDS.relative_to(ROOT)),
        "total_records_in_source": n_rows,
        "records_matched_to_catalog_species": n_matched,
        "species": {},
    }

    for name, species_id in sorted(catalog_names.items()):
        cells = dict(by_species_cells.get(name, {}))
        points = by_species_points.get(name, [])
        entry = {
            "species_id": species_id,
            "n_records": sum(cells.values()),
            "n_unique_cells": len(cells),
            "cells": cells,
        }
        if points:
            lats = [p[0] for p in points]
            lons = [p[1] for p in points]
            entry["bbox"] = {"lat_min": min(lats), "lat_max": max(lats), "lon_min": min(lons), "lon_max": max(lons)}
        distribution["species"][name] = entry

    n_with_data = sum(1 for e in distribution["species"].values() if e["n_records"] > 0)
    distribution["summary"] = {
        "species_with_at_least_1_record": n_with_data,
        "species_with_zero_records": len(catalog_names) - n_with_data,
        "species_with_zero_records_list": sorted(
            n for n, e in distribution["species"].items() if e["n_records"] == 0
        ),
    }
    OUT_DIST.parent.mkdir(parents=True, exist_ok=True)
    OUT_DIST.write_text(json.dumps(distribution, indent=2, ensure_ascii=False), encoding="utf-8")

    elevation = {
        "schema_version": "anura.elevation-ranges/1.0.0",
        "source": str(RECORDS.relative_to(ROOT)),
        "method": (
            "Percentiles de 'elevation_m' (no nulo) de records_v1.csv por especie, filtrado a las "
            "41 del catalogo activo. Especies sin registros de elevacion quedan UNKNOWN."
        ),
        "species": {},
    }
    for name, species_id in sorted(catalog_names.items()):
        vals = by_species_elev.get(name, [])
        if len(vals) >= 3:
            arr = np.array(vals)
            elevation["species"][name] = {
                "species_id": species_id,
                "n_elevation_records": len(vals),
                "min": float(arr.min()),
                "p5": float(np.percentile(arr, 5)),
                "p25": float(np.percentile(arr, 25)),
                "median": float(np.percentile(arr, 50)),
                "p75": float(np.percentile(arr, 75)),
                "p95": float(np.percentile(arr, 95)),
                "max": float(arr.max()),
            }
        else:
            elevation["species"][name] = {
                "species_id": species_id,
                "n_elevation_records": len(vals),
                "status": "INSUFFICIENT_DATA (<3 registros con elevation_m)",
            }
    n_with_elev = sum(1 for e in elevation["species"].values() if "min" in e)
    elevation["summary"] = {
        "species_with_sufficient_elevation_data": n_with_elev,
        "species_without_sufficient_elevation_data": len(catalog_names) - n_with_elev,
    }
    OUT_ELEV.write_text(json.dumps(elevation, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(distribution["summary"], indent=2, ensure_ascii=False))
    print(json.dumps(elevation["summary"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
