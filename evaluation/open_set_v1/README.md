# ANURA Open Set Validation — Evaluation Directory

**Phase 1 Status**: ✅ AUDIT COMPLETE

**Evaluation Date**: 2026-09-13  
**Evaluation Scope**: Open Set detection capability of ANURA classifier

---

## Directory Structure

```
evaluation/open_set_v1/
├── README.md                             (this file)
├── pipeline_audit.md                     (Fase 1: complete pipeline inspection)
├── hashes_sha256.txt                     (reproducibility: artifact checksums)
├── dataset_manifest.csv                  (Fase 2: Open Set images + metadata)
├── leakage_report.md                     (Fase 2: contamination audit)
├── closed_set_control.csv                (Fase 3: known species control)
├── open_set_predictions.csv              (Fase 4: Open Set predictions)
├── open_set_prior_ablation.csv           (Fase 5a: vision only vs vision+prior)
├── open_set_prior_adversarial.csv        (Fase 5b: GPS perturbation)
├── segmentation_ablation.csv             (Fase 5c: if segmentation used)
├── metrics.json                          (Fase 6: all computed metrics)
├── confidence_distribution.png           (Fase 6: Top-1 prob histograms)
├── margin_distribution.png               (Fase 6: Top1-Top2 margin histograms)
├── embedding_distance_distribution.png   (Fase 6: cosine distance histograms)
├── score_distribution.png                (Fase 6: final score histograms)
├── threshold_analysis.csv                (Fase 6: FPR/TPR sweep)
├── calibration_metrics.json              (Fase 6: ECE, Brier Score)
├── open_set_hard_cases.md                (Fase 6: most dangerous false positives)
└── FINAL_OPEN_SET_REPORT.md              (Fase 7: complete findings + decision)
```

---

## Phase 1: Pipeline Audit (COMPLETE ✅)

All critical components of the ANURA inference pipeline have been inspected and documented in `pipeline_audit.md`.

**Key Findings**:
- ✅ 41 visual classes (species) identified
- ✅ BioCLIP encoder located (ViT 768-dim L2-normalized)
- ✅ Route A: Multi-head softmax classifier (41 classes)
- ✅ Route B: k-NN k=5 with geographic prior
- ✅ Geographic prior: 50km radius, α=0.5, weight=0.75
- ✅ No segmentation active in current pipeline
- ✅ No rejection mechanism (all images forced to 41 classes)
- ✅ Training/test partitions isolated in manifiesto.json

**No Blocking Issues**: All components ready for evaluation.

---

## Phase 2: Dataset Construction (PENDING)

### Objective

Build a manifest of Open Set images:
- CATALOG_ONLY species (in catalog, not visual classes)
- Colombian species NOT in visual classes
- Visually similar to visual classes (hardest negatives)
- External species (optional)

### Deliverable

File: `dataset_manifest.csv`

Columns:
```
image_id, path, obs_id, individual_id, hash, true_species, true_taxon_id,
catalog_status, group, country, department, municipality, latitude, longitude, source
```

### Constraints

- NO manual selection of "easy" examples only
- NO deletion of difficult cases
- Reproducible selection logic (documented)
- Full traceability (image hashes verified against source)

---

## Phase 3: Leakage Audit (PENDING)

### Objective

Verify no image/individual contamination between train and evaluation sets.

### Checks

- obs_id collision
- individual_id collision
- Perceptual hash duplicates
- Geographic clustering (same coordinates)
- Same file paths

### Deliverable

File: `leakage_report.md`

List of:
- No leakage (clear)
- Potential leakage (species, image_id, type, exclusion action)

---

## Phase 4: Closed-Set Control (PENDING)

### Objective

Establish baseline: system behavior on **known species** (not the 41, but a held-out independent test set).

### Deliverable

File: `closed_set_control.csv`

Columns:
```
image_id, true_species, true_taxon_id,
top1_species, top1_probability,
top2_species, top2_probability,
top3_species, top3_probability,
margin_top1_top2, embedding_distance, predicted_zone,
prior_top1, prior_top2, final_score
```

### Purpose

Establish natural distribution of confidence, margin, distance on known species.

---

## Phase 5: Open Set Real (PENDING)

### Objective

Run EXACT same pipeline on Open Set images (species NOT in the 41 visual classes).

### Constraints

✋ **DO NOT MODIFY**:
- Model weights
- Encoder checkpoint
- Classes
- Preprocessing
- Temperature
- Threshold
- Geographic prior (used as-is)

### Deliverable

File: `open_set_predictions.csv`

Same columns as closed_set_control.csv, but for Open Set images.

---

## Phase 6: Ablations & Analysis (PENDING)

### Ablation 1: Vision Only vs Vision+Prior

File: `open_set_prior_ablation.csv`

Compare:
- Unknown Detection Rate (UDR)
- False Acceptance Rate (FAR)
- AUROC
- FPR@95TPR

### Ablation 2: Prior Adversarial

File: `open_set_prior_adversarial.csv`

For each Open Set image:
- Condition 1: Real GPS
- Condition 2: GPS from a zone with visually similar species
- Condition 3: GPS from another zone

Measure whether prior causes false acceptance.

### Ablation 3: Segmentation (Optional)

File: `segmentation_ablation.csv`

If segmentation is used:
- Full image vs segmented image
- Same metrics as prior ablation

---

## Phase 7: Metrics & Hard Cases (PENDING)

### Metrics File: `metrics.json`

```json
{
  "known_top1": 0.XX,
  "known_top3": 0.XX,
  "known_acceptance": 0.XX,
  "unknown_detection_rate": 0.XX,
  "false_acceptance_rate": 0.XX,
  "auroc": 0.XX,
  "fpr_at_95tpr": 0.XX,
  "oscr": 0.XX,
  "ece": 0.XX,
  "brier_score": 0.XX
}
```

### Distributions: PNG Files

- `confidence_distribution.png`: Top-1 probability histogram (KNOWN vs UNKNOWN)
- `margin_distribution.png`: Top1-Top2 margin histogram
- `embedding_distance_distribution.png`: Cosine distance histogram
- `score_distribution.png`: Final score histogram

### Hard Cases: `open_set_hard_cases.md`

List top 10:
- False acceptances (Open Set mistaken for known species)
- False rejections (Known species rejected)
- Hardest Open Set cases (high confidence but wrong)

---

## Phase 8: Final Report (PENDING)

### Deliverable: `FINAL_OPEN_SET_REPORT.md`

Contains:
- Question: Can ANURA detect unknown species?
- Dataset summary
- Integrity artifacts (hashes, git, leakage)
- Results table (all metrics)
- Vision vs Prior comparison
- Threshold recommendation (candidato, NOT applied)
- Top 5 false acceptances
- Top 5 problems
- Calibration analysis
- Decision: FUNCTIONAL / PARTIAL / NOT FUNCTIONAL

---

## Reproducibility

All artifacts are in `evaluation/open_set_v1/`.

Critical files hashed in `hashes_sha256.txt`:
- Model checkpoint: bioclip_anura_mejor.pt
- Encoder: encoder_anura_fp16.onnx
- Geographic prior: prior_geografico_movil.json
- Vocabulary: vocabulario.json
- Training taxonomy: taxonomia.py
- Dataset manifest: manifiesto.json

No modifications to these files are permitted during evaluation.

---

## Constraints

### Always Enforced

- ✋ NO model retraining
- ✋ NO weight modification
- ✋ NO class replacement
- ✋ NO embedding index regeneration
- ✋ NO threshold application
- ✋ NO temperature tuning
- ✋ NO hard-negative mining
- ✋ NO selective sampling of easy cases
- ✋ NO use of ground truth during inference

### Observations

- Both Route A and Route B always output a species from the 41 classes
- No built-in rejection mechanism
- Geographic prior can mask Open Set signals (evaluated separately)
- k-NN always succeeds (k=5 on finite dataset)

---

## Timeline

| Phase | Task | Status | Est. Completion |
|-------|------|--------|-----------------|
| 1 | Pipeline Audit | ✅ DONE | 2026-09-13 |
| 2 | Dataset Construction | ⏳ TODO | TBD |
| 3 | Leakage Audit | ⏳ TODO | TBD |
| 4 | Closed-Set Control | ⏳ TODO | TBD |
| 5 | Open Set Evaluation | ⏳ TODO | TBD |
| 6 | Ablations | ⏳ TODO | TBD |
| 7 | Metrics & Analysis | ⏳ TODO | TBD |
| 8 | Final Report | ⏳ TODO | TBD |

---

## References

- Protocol: `PROMPT.md` (full experimental protocol)
- Pipeline details: `pipeline_audit.md`
- Memory: Anura architecture + prior decisions in user's .claude/projects/D--Anura/memory/

---

*Evaluation Framework for ANURA/SITRana Open Set Capability Assessment*
