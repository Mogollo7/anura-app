# UNKNOWN_V2.1 FREEZE REPORT

**Date:** 2026-09-14
**Status:** READY_FOR_MANUAL_REVIEW
**Decision:** OPCIÃ“N A - TOTAL EXCLUSIÃ“N of unrecoverable supplementary species

---

## Executive Summary

UNKNOWN_V2.1 congelaciÃ³n final separa **7 especies PRIMARY** (cumpliendo contrato 70-100 imÃ¡genes) de **4 especies SUPPLEMENTARY** (sub-70, no recuperables en iNaturalist Colombia).

- **PRIMARY:** 7 especies, 622 imÃ¡genes, 321 individuos
- **SUPPLEMENTARY:** 4 especies, 130 imÃ¡genes, 74 individuos (histÃ³rico, excluido)

---

## Gate Verification Results

### PRIMARY Species Verification: **PASS**

âœ“ **Boana_albifrons**: 95 images, 48 individuals, contract_status=PRIMARY_PASS
âœ“ **Pristimantis_brevirostris**: 89 images, 45 individuals, contract_status=PRIMARY_PASS
âœ“ **Dendropsophus_labialis**: 74 images, 43 individuals, contract_status=PRIMARY_PASS
âœ“ **Rhinella_marina**: 83 images, 41 individuals, contract_status=PRIMARY_PASS
âœ“ **Leptodactylus_fragilis**: 85 images, 44 individuals, contract_status=PRIMARY_PASS
âœ“ **Smilisca_phaeota**: 107 images, 55 individuals, contract_status=PRIMARY_PASS
âœ“ **Espadarana_prosoblepon**: 89 images, 45 individuals, contract_status=PRIMARY_PASS

All PRIMARY species satisfy:
- valid_images >= 70 and <= 100
- leakage_count == 0
- exact_duplicates == 0
- quality_pass == true
- independent_individuals >= 10

---

## Contract Compliance Table

| Species | Images | Individuals | Status | Notes |
|---------|--------|-------------|--------|-------|
| Boana_albifrons | 95 | 48 | PRIMARY_PASS | âœ“ |
| Pristimantis_brevirostris | 89 | 45 | PRIMARY_PASS | âœ“ |
| Dendropsophus_labialis | 74 | 43 | PRIMARY_PASS | âœ“ |
| Rhinella_marina | 83 | 41 | PRIMARY_PASS | âœ“ |
| Leptodactylus_fragilis | 85 | 44 | PRIMARY_PASS | âœ“ |
| Smilisca_phaeota | 107 | 55 | PRIMARY_PASS | âœ“ |
| Espadarana_prosoblepon | 89 | 45 | PRIMARY_PASS | âœ“ |
| | | | | |
| Hyloxalus_picachos | 15 | 15 | SUPPLEMENTARY_EXCLUDED | Below 70, unrecoverable |
| Dendropsophus_minutus | 23 | 19 | SUPPLEMENTARY_EXCLUDED | Below 70, unrecoverable |
| Sachatamia_electrops | 39 | 19 | SUPPLEMENTARY_EXCLUDED | Below 70, unrecoverable |
| Pristimantis_w_nigrum | 53 | 21 | SUPPLEMENTARY_EXCLUDED | Below 70, unrecoverable |

---

## Recovery Attempt Summary (Fase 22.1)

**Decision:** OPCIÃ“N A - ExclusiÃ³n total de especies sub-70
**Recovery Method:** iNaturalist Colombia API search for each supplementary species
**Result:** 0 additional valid images obtained (all 4 species exhausted)

### Supplementary Species Status:

- **Hyloxalus_picachos**: 15 images â†’ Recovery: FAILED (0 new) â†’ EXCLUDED
- **Dendropsophus_minutus**: 23 images â†’ Recovery: FAILED (0 new) â†’ EXCLUDED
- **Sachatamia_electrops**: 39 images â†’ Recovery: FAILED (0 new) â†’ EXCLUDED
- **Pristimantis_w_nigrum**: 53 images â†’ Recovery: FAILED (0 new) â†’ EXCLUDED

These species are retained in `manifests/SUPPLEMENTARY_MANIFEST.json` for historical traceability only.

---

## Manual Review Preparation

### Location of PRIMARY Images:
```
data/unknown_open_set_v2/images/primary/
â”œâ”€â”€ Boana_albifrons/ (95 images)
â”œâ”€â”€ Pristimantis_brevirostris/ (89 images)
â”œâ”€â”€ Dendropsophus_labialis/ (74 images)
â”œâ”€â”€ Rhinella_marina/ (83 images)
â”œâ”€â”€ Leptodactylus_fragilis/ (85 images)
â”œâ”€â”€ Smilisca_phaeota/ (107 images)
â””â”€â”€ Espadarana_prosoblepon/ (89 images)
```

### Manual Review Checklist:

For each PRIMARY species image:
1. **Taxonomy:** Verify species identification is correct
2. **Visibility:** Frog is clearly visible, not occluded
3. **Morphology:** Morphological features match species description
4. **Duplicates:** Detect near-duplicate images (perceptual hash)
5. **Individual Tracking:** Multiple photos of same individual?
6. **Photography:** Field photograph or artificial/captive?
7. **Quality Anomalies:** Any visual issues missed by automation

### Files to Reference:
- `MANUAL_REVIEW_MANIFEST.csv`: Species and image counts
- `manifests/QUALITY_LIMITATIONS.json`: Automated checks performed vs manual
- `audit/final_freeze_audit_table.csv`: Species-level audit details

---

## Quality Limitations

### Automated Checks Performed:
- File integrity (format, corruption)
- Resolution check (minimum pixels)
- Blur score (Laplacian variance)
- Brightness score (pixel histogram)
- Contrast score (RMS contrast)
- SHA256 exact duplicate detection
- Leakage check against 11,717 training hashes

### Automated Checks NOT Performed:
- **Perceptual hash near-duplicate detection** â€” Library unavailable in environment

### Manual Review Must Verify:
- Near-duplicate images (visually identical or near-identical)
- Multiple photos of same individual (over-representation)
- Taxonomic identification correctness
- Frog visibility and morphology
- Artificial crops vs field photography
- Quality anomalies missed by automation

---

## Next Steps (Phase 23 Onwards)

1. **User Manual Review** (Primary responsibility)
   - Open PRIMARY images from `data/unknown_open_set_v2/images/primary/`
   - Use `MANUAL_REVIEW_MANIFEST.csv` and `audit/final_freeze_audit_table.csv` for reference
   - Flag or reject problematic images/species

2. **Compile Manual Review Results**
   - Approved species list
   - Per-image flags or rejections
   - Notes on quality issues

3. **Proceed to Fase 23**
   - Load approved PRIMARY set
   - Run embedding evaluation
   - Generate open-set metrics

4. **NOT YET PERFORMED:**
   - Fase 23 evaluation
   - Fine-tuning
   - Git commit/push
   - Modification of protected artifacts

---

## Files Generated

- `manifests/PRIMARY_MANIFEST.json` â€” PRIMARY dataset manifest
- `manifests/SUPPLEMENTARY_MANIFEST.json` â€” SUPPLEMENTARY dataset manifest (historical)
- `manifests/GATE_PRIMARY_VERIFICATION.json` â€” Gate verification results
- `manifests/QUALITY_LIMITATIONS.json` â€” Automated vs manual quality checks
- `audit/final_freeze_audit_table.csv` â€” All 11 species audit data
- `audit/recovery_decision_log.csv` â€” Recovery attempt decisions
- `MANUAL_REVIEW_MANIFEST.csv` â€” Manual review template
- `FREEZE_SUMMARY.txt` â€” Plain text summary
- `FASE22_FREEZE_REPORT.md` â€” This report

---

## Status

âœ“ **GATE_PRIMARY_VERIFICATION: PASS**
âœ“ **All 7 PRIMARY species meet contract requirements**
âœ“ **All 4 SUPPLEMENTARY species marked as unrecoverable and excluded**
âœ“ **Ready for manual review**

**WARNING:** Manual review and approval required before proceeding to Fase 23.
