# Independent GEO coverage audit (2026-09-14)

Command: `.venv-train\Scripts\python.exe` inline audit; observation IDs normalized by removing `OBS_`. `FOUND_GEO` means the existing `validation/fase23a_geographic_context/cache/inat_observations_cache.json` has finite, in-range `lat` and `lon`. No ground truth was used to construct scores.

- KNOWN: **7431 FOUND_GEO / 44 NOT_FOUND** of 7475.
- UNKNOWN: **620 FOUND_GEO / 0 NOT_FOUND** of 620 (412 unique observation IDs; repeated images are counted at image level).

The 7431/44 and 620/0 claims are therefore reproducible from the frozen manifests/NPZ plus the existing GEO cache. `coordenadas_auditoria.json` and `download_manifest.json` are not complete image-level authorities: they match only subsets (see JSON). `opentopodata_cache.json` is keyed by coordinate strings and is topography response cache, not an observation manifest; it cannot independently establish image coverage.

A complete ablation implementation already exists at `validation/fase23a_geographic_context/scripts/phase1to8_main.py`, with historical output `ablation_summary.json`. It was not rerun here to preserve historical artifacts, thresholds, encoder, dataset, and production.
