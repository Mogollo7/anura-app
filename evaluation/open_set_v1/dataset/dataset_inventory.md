# Open Set Dataset Inventory

## Summary

- **Visual Classes**: 41
- **Evaluation Date**: 2026-09-13

## Dataset Composition

### Grupo A: CATALOG_ONLY

Especies en el catálogo pero NO entre las 41 clases visuales:

| Species | Images | Status | Family | Notes |
|---------|--------|--------|--------|-------|
| Hyloxalus_picachos | 15 | ✅ CLEAN | Dendrobatidae | Especie huérfana |
| Sachatamia_electrops | 41 | ✅ CLEAN | Centrolenidae | Especie huérfana |

**Subtotal CATALOG_ONLY**: 56 imágenes

### Leakage Status

| Status | Count | Details |
|--------|-------|---------|
| CLEAN | 56 | No contamination with training |
| OPEN_SET_LEAKAGE | 0 | obs_id appears in train/test |
| DUPLICATE_EXACT | 0 | SHA256 hash matches another image |
| UNKNOWN | 0 | Unable to determine status |

## Specification Verification

✅ 41 Visual Classes Confirmed
✅ CATALOG_ONLY != Visual Classes
✅ No Training Contamination
✅ Dataset Integrity Verified

## Files Generated

- `open_set_manifest.json` — Complete image metadata
- `leakage_report.json` — Contamination audit
- `dataset_inventory.md` — This document

## Next Steps

Fase 3: Closed-Set Control Evaluation
Fase 4: Open Set Real Evaluation
