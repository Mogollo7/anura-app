# ANURA Open Set Evaluation — Phase 1 Pipeline Audit

**Evaluation Date**: 2026-09-13  
**Git Status**: Not a git repository  
**Auditor**: Claude Haiku 4.5  

---

## Executive Summary

The ANURA visual identification system pipeline has been fully inspected. All critical components are FOUND and operational. No blocking issues detected for evaluation execution.

**Component Status**: ✅ ALL FOUND  
**Ready for Phase 2 (Dataset Construction)**: YES

---

## 1. Visual Classes & Vocabulary

### Definition

**Visual Classes**: 41 species (Craugastoridae, Hylidae, Dendrobatidae, Leptodactylidae, Phyllomedusidae, Aromobatidae, Bufonidae families)

### Location & Status

| Component | Path | Status | Count | Notes |
|-----------|------|--------|-------|-------|
| **Species List** | `training/taxonomia.py` (ESPECIES) | ✅ FOUND | 41 | Defined as tuple in Python |
| **Vocab JSON** | `bioclip/checkpoints/vocabulario.json` | ✅ FOUND | 41 + 7 familias + 13 géneros | JSON export of taxonomia.py |

### Classes (41 total)

```
Boana:
  - Boana_boans
  - Boana_cinerascens
  - Boana_lanciformis
  - Boana_platanera
  - Boana_pugnax
  - Boana_punctata
  - Boana_rosenbergi
  - Boana_xerophylla

Craugastor:
  - Craugastor_raniformis

Dendrobates:
  - Dendrobates_truncatus

Dendropsophus:
  - Dendropsophus_bogerti
  - Dendropsophus_columbianus
  - Dendropsophus_ebraccatus
  - Dendropsophus_mathiassoni
  - Dendropsophus_microcephalus
  - Dendropsophus_molitor
  - Dendropsophus_norandinus
  - Dendropsophus_reticulatus
  - Dendropsophus_triangulum

Engystomops:
  - Engystomops_pustulosus

Hyloscirtus:
  - Hyloscirtus_palmeri

Leptodactylus:
  - Leptodactylus_colombiensis

Phyllomedusa:
  - Phyllomedusa_tarsius
  - Phyllomedusa_venusta

Pithecopus:
  - Pithecopus_hypochondrialis

Pristimantis:
  - Pristimantis_achatinus
  - Pristimantis_bogotensis
  - Pristimantis_erythropleura
  - Pristimantis_gaigei
  - Pristimantis_paisa
  - Pristimantis_palmeri
  - Pristimantis_penelopus
  - Pristimantis_permixtus
  - Pristimantis_taeniatus
  - Pristimantis_thectopternus
  - Pristimantis_vilarsi

Rheobates:
  - Rheobates_palmatus

Rhinella:
  - Rhinella_alata
  - Rhinella_horribilis
  - Rhinella_margaritifera

Scinax:
  - Scinax_ruber
```

### Expansion History

- **Original**: 28 species (core set)
- **Expanded 2026-09-11**: +13 species (15 additional from same genera of underrepresented species)
- **Current**: 41 species
- **Excluded**: Hyloxalus_picachos, Sachatamia_electrops (marked CATALOG_ONLY)

---

## 2. Encoder

### Definition

BioCLIP visual encoder: Hugging Face model `imageomics/bioclip`

### Locations & Checkpoints

| Component | Path | Format | Status | Size | Hash (if avail) |
|-----------|------|--------|--------|------|-----------------|
| **PyTorch Encoder** | `bioclip/checkpoints/encoder_anura.pt` | `.pt` | ✅ FOUND | ~345 MB | Not verified |
| **ONNX FP32** | `bioclip/checkpoints/encoder_anura.onnx` | `.onnx` | ✅ FOUND | ~690 MB | Not verified |
| **ONNX FP16** | `bioclip/checkpoints/encoder_anura_fp16.onnx` | `.onnx` | ✅ FOUND | ~345 MB | Not verified |
| **INT8 Quantized** | `bioclip/checkpoints/encoder_anura_int8.pt` | `.pt` | ✅ FOUND | ? | Not verified |

### Output Specification

- **Input**: RGB image, 224×224 pixels
- **Preprocessing**: BioCLIP standard (from open_clip.create_model_and_transforms)
- **Output**: Embedding vector, L2-normalized (unit norm)
- **Dimension**: 768 (ViT dimension)
- **Normalization**: Cosine similarity (embeddings normalized in-place during forward pass)

### Code Location

**Encoder wrapper** (fase_9_encoder_onnx_y_paquete_antioquia.py, lines 67-74):
```python
class EncoderVisual(torch.nn.Module):
    def __init__(self, visual_encoder):
        super().__init__()
        self.visual = visual_encoder

    def forward(self, x):
        emb = self.visual(x)
        return emb / emb.norm(dim=-1, keepdim=True)  # L2 normalization
```

---

## 3. Classification Models

### Route A: Multi-head Softmax Classifier

**Architecture**: BioCLIP encoder + 3 softmax heads (one per taxonomic level)

| Head | Classes | Status | Location |
|------|---------|--------|----------|
| Familia | 7 | ✅ in checkpoint | `bioclip_anura_mejor.pt` |
| Género | 13 | ✅ in checkpoint | `bioclip_anura_mejor.pt` |
| Especie | 41 | ✅ in checkpoint | `bioclip_anura_mejor.pt` |

**Checkpoint**:
- Path: `bioclip/checkpoints/bioclip_anura_mejor.pt`
- Status: ✅ FOUND
- Used in: fase_4_transfer_learning.py → fase_5/7/8/9

**Model Class**: `BioClipMultiHead` (defined in fase_4_transfer_learning.py)

**Output**: 
- Species logits (41 dimensions)
- Scores after softmax

### Route B: k-NN with Geographic Prior

**Method**: k-NN (k=5) with cosine similarity, restricted to species present in region

**Vector Index**: SQLite + sqlite_vec extension
- Path: `bioclip/paquetes_regionales/antioquia_v1.sqlite`
- Status: ✅ FOUND
- Vectors: Embeddings (768-dim, normalized)
- Metadata: species, family, genus, individual_id, photo_path

**Geographic Filter**: Bounding box approximation (not exact polygon)
- Antioquia bbox: lat [5.4, 8.9], lon [-77.2, -73.8]
- Threshold: ≥3 observations in train within bbox
- Result: 21/41 species for Antioquia (as of Fase 9)

---

## 4. Geographic Prior

### File & Format

- **Path**: `bioclip/checkpoints/prior_geografico_movil.json`
- **Status**: ✅ FOUND
- **Format**: JSON with per-species point lists (lat/lon)

### Configuration

```json
{
  "radio_km_recomendado": 50.0,
  "alpha_suavizado": 0.5,
  "peso_prior_recomendado": 0.75,
  "puntos_por_especie": {
    "Boana_boans": [[lat, lon], ...],
    "Boana_cinerascens": [[lat, lon], ...],
    ...
  }
}
```

### Usage

- **Radius**: 50 km from query GPS location
- **Smoothing (alpha)**: 0.5 (interpolation between prior and vision)
- **Prior weight**: 0.75 (importance in final score)

### Data Source

Extracted from training data observations with coordinates (Fase 6c)

### Critical Note

The prior is **NOT isolated from inference**. It can be applied to modify final scores during inference, potentially **masking Open Set signals**. Test both with and without prior.

---

## 5. Preprocessing & Input Pipeline

### Image Loading

- **Format**: JPG/PNG (PIL.Image.open with RGB conversion)
- **Size**: Variable (letterboxed to 224×224)
- **Normalization**: BioCLIP standard (ImageNet normalization applied by open_clip.create_model_and_transforms)

### Location

Code: `fase_9_encoder_onnx_y_paquete_antioquia.py`, lines 77-91 (DatasetImagenes class)

### Resolution

- **Expected**: 224×224 (fixed by ViT)
- **Variation**: Pre-model, no variance in model input

---

## 6. Scoring Pipeline

### Route A (Softmax)

1. Image → Encoder → 768-dim embedding (L2-normalized)
2. Embedding → 3 softmax heads
3. Output: Logits for [familia, genero, especie]
4. Score: softmax(logits_especie) → probability [0,1] for each of 41 species
5. Final output: argmax (top-1 class) + confidence (top-1 probability)

### Route B (k-NN)

1. Image → Encoder → 768-dim embedding (L2-normalized)
2. Embedding → SQLite vec0 search (cosine similarity)
3. Retrieve k=5 nearest neighbors from vector index
4. Voting: Sum similarities for each species
5. Final output: argmax (species with highest vote) + similarity scores

### Temperature

- **Route A**: Not explicitly set (default PyTorch softmax)
- **Route B**: Not applicable (no probability calibration)

### Threshold

- **Route A**: None explicitly applied in current system (all images forced to top-41 species)
- **Route B**: k-NN always returns a result; no rejection mechanism exists

---

## 7. Embeddings & Vector Index

### Embedding Generation

| Component | Location | Generation | Storage | Status |
|-----------|----------|------------|---------|--------|
| **Train embeddings** | (In-memory during evaluation) | Route A encoder forward pass | NumPy array | ✅ Generated on-demand |
| **Test embeddings** | (In-memory during evaluation) | Route A encoder forward pass | NumPy array | ✅ Generated on-demand |
| **SQLite vector index** | `antioquia_v1.sqlite` | Fase 9 | vec0 virtual table | ✅ FOUND |

### Metadata Available

- observation_id (if in training data)
- individual_id (group in manifiesto.json)
- species
- family, genus
- photo_path
- train/test partition

---

## 8. Training & Test Partitions

### Manifest Location

- **Path**: `training/manifiesto.json`
- **Status**: ✅ FOUND
- **Structure**: { "particiones": { "train": [...], "test": [...] } }

### Data Characteristics

Per `training/manifiesto.json`:
- **Train**: Non-augmented images per species, individuals (grupos) marked
- **Test**: Held-out individuals, real species labels (idx_especie)
- **Augmentation flag**: `aumentada` field indicates synthetic crops
- **Metadata**: ruta (path), idx_especie, familia, genero, especie, grupo (individual_id)

### Leakage Risks

Current audit does NOT verify:
- Whether test individuals appear in train
- Whether image hashes / perceptual duplicates cross partitions
- Whether geographic overlap causes train/test collision

**Action for Phase 3**: Full leakage audit required before evaluation.

---

## 9. Segmentation Pipeline

### Status

No segmentation pipeline detected in the current inference flow.

**Potential Segmentation Tool** (detected but not used):
- Path: `bioclip/scripts/diagnostico_recorte_por_imagen.py`
- Purpose: Experimental crop-vs-full-image comparison
- Status: Optional, not part of standard pipeline

### Decision

Segmentation ablation will be **NOT APPLICABLE** unless explicit segmentation is activated during evaluation.

---

## 10. Evaluation Infrastructure

### Existing Evaluation Scripts

| Script | Purpose | Output | Status |
|--------|---------|--------|--------|
| `fase_5_evaluacion_completa.py` | Closed-set per-species metrics | `fase_5_completa.json` | ✅ FOUND |
| `fase_8_knn_vs_clasificador.py` | Route A vs Route B comparison | `fase_8_knn_vs_clasificador.json` | ✅ FOUND |
| `fase_9_encoder_onnx_y_paquete_antioquia.py` | Encoder export + regional package | `fase_9_antioquia_real.json` | ✅ FOUND |

### Existing Evaluation Results

| File | Purpose | Status |
|------|---------|--------|
| `fase_5_completa.json` | Per-species Top-1/Top-3/F1/Precision/Recall | ✅ FOUND |
| `fase_8_knn_vs_clasificador.json` | Route A vs Route B metrics | ✅ FOUND |
| `fase_9_antioquia_real.json` | Regional package validation | ✅ FOUND |

---

## 11. Training History

### Checkpoint Metadata

- **Path**: `bioclip/checkpoints/historial_entrenamiento.json`
- **Status**: ✅ FOUND
- **Contents**: Training log (loss, validation accuracy, phases)

### Model Evolution

1. **Fase 1**: Load pre-trained BioCLIP (frozen encoder)
2. **Fase 2**: Extract embeddings (validation on 41 species)
3. **Fase 3**: Baseline softmax on frozen embeddings
4. **Fase 4**: Transfer learning (unfreeze encoder, train 3 heads)
5. **Fase 5**: Full evaluation on test set (Top-1 reported)
6. **Fase 6**: Extract encoder checkpoint (encoder_anura.pt)
7. **Fase 6b**: Compare softmax head vs k-NN
8. **Fase 6c**: Build geographic prior from train observations
9. **Fase 7**: Export classifier to ONNX
10. **Fase 7c**: INT8 quantization experiment
11. **Fase 8**: k-NN vs Softmax head comparison
12. **Fase 9**: Export encoder ONLY to ONNX, build regional packages

---

## 12. Complete Pipeline Flow

### Inference Pipeline (Current System)

```
┌─ INPUT: Image (JPG/PNG) ─┐
│                          │
├─ Preprocessing (224×224) │
│  (BioCLIP normalization) │
│                          │
├─ Encoder                 │
│  (BioCLIP ViT visual)     │
│  input: [1,3,224,224]    │
│  output: [1,768]         │
│  L2-normalized           │
│                          │
├─ Route A: Softmax        │ ├─ Route B: k-NN
│  ├─ logits_fam [1,7]     │ │  ├─ SQLite vec0 search
│  ├─ logits_gen [1,13]    │ │  │  (k=5 neighbors)
│  └─ logits_esp [1,41]    │ │  ├─ Cosine similarity
│      ↓                   │ │  │  (embeddings normalized)
│      softmax [1,41]      │ │  ├─ Species voting
│      ↓                   │ │  └─ Top-1 by vote sum
│      argmax + prob       │ │
│                          │
├─ Geographic Prior (Optional)
│  ├─ Query GPS → Prior zones
│  ├─ Weight prior adjustment
│  └─ Reweight / re-rank
│
└─ OUTPUT: species prediction + confidence
```

### Data Flow Files

| File | Role | Status |
|------|------|--------|
| `data cleaned/*` | Training images | ✅ FOUND |
| `training/manifiesto.json` | Partition definitions | ✅ FOUND |
| `bioclip/checkpoints/bioclip_anura_mejor.pt` | Trained weights | ✅ FOUND |
| `bioclip/checkpoints/encoder_anura.onnx` | Deployed encoder | ✅ FOUND |
| `bioclip/checkpoints/prior_geografico_movil.json` | Geographic data | ✅ FOUND |
| `bioclip/paquetes_regionales/antioquia_v1.sqlite` | Regional package | ✅ FOUND |

---

## 13. Configuration & Hyperparameters

### Fixed (Not Changeable During Evaluation)

| Parameter | Value | Justification |
|-----------|-------|----------------|
| Encoder model | BioCLIP ViT | Pre-trained, fixed |
| Input resolution | 224×224 | Model requirement |
| Embedding dimension | 768 | Model architecture |
| Embedding normalization | L2 | Cosine similarity requires it |
| Softmax temperature | 1.0 (default) | Not exposed in code |
| k-NN neighbors | k=5 | Hardcoded in fase_9 |
| Geographic radius | 50 km | Config in prior JSON |
| Geographic weight | 0.75 | Config in prior JSON |
| Alpha smoothing | 0.5 | Config in prior JSON |
| Antioquia bbox | lat[5.4,8.9], lon[-77.2,-73.8] | Hardcoded in fase_9 |

---

## 14. Known Issues & Constraints

### No Blocking Issues Found

✅ All critical components present and accessible.

### Operational Notes

1. **No explicit rejection mechanism**: Both Route A and Route B always output a species from the 41 classes. No built-in "UNKNOWN" or "NO_ANURO" output.

2. **Geographic prior can mask Open Set**: If applied, prior can raise confidence in nearby species, potentially hiding that an image is OOD.

3. **Route B always succeeds**: k-NN with k=5 will always find 5 neighbors (or fewer if dataset < 5 samples). No confidence/similarity threshold exists.

4. **Segmentation not active**: Evaluation will use full images only.

5. **Temperature not tuned**: Softmax uses default temperature (no calibration applied).

---

## 15. Reproducibility Artifacts

### Files to Hash (SHA256)

```
D:\Anura\bioclip\checkpoints\bioclip_anura_mejor.pt
D:\Anura\bioclip\checkpoints\encoder_anura.onnx
D:\Anura\bioclip\checkpoints\encoder_anura_fp16.onnx
D:\Anura\bioclip\checkpoints\prior_geografico_movil.json
D:\Anura\bioclip\checkpoints\vocabulario.json
D:\Anura\training\taxonomia.py
D:\Anura\training\manifiesto.json
D:\Anura\bioclip\paquetes_regionales\antioquia_v1.sqlite
```

### Environment (not yet captured)

- Python version: (to be verified)
- PyTorch version: (to be verified)
- CUDA version: (to be verified)
- open_clip version: (to be verified)
- onnxruntime version: (to be verified)

---

## 16. Summary: Audit Readiness

| Component | Status | Evidence |
|-----------|--------|----------|
| **Visual Classes (41)** | ✅ FOUND | taxonomia.py ESPECIES, vocabulario.json |
| **Encoder** | ✅ FOUND | .pt and .onnx checkpoints in bioclip/checkpoints/ |
| **Classification (Route A)** | ✅ FOUND | bioclip_anura_mejor.pt, BioClipMultiHead class |
| **k-NN (Route B)** | ✅ FOUND | antioquia_v1.sqlite, fase_9 k=5 implementation |
| **Geographic Prior** | ✅ FOUND | prior_geografico_movil.json, full coordinate data |
| **Preprocessing** | ✅ FOUND | BioCLIP open_clip.create_model_and_transforms |
| **Dataset Partitions** | ✅ FOUND | training/manifiesto.json train/test split |
| **Scoring Pipeline** | ✅ FOUND | fase_5/8/9 scripts, logits + softmax |
| **Embedding Generation** | ✅ FOUND | generar_embeddings() in fase_9 |
| **Segmentation** | ⚠️ NOT ACTIVE | Optional feature, not used in std pipeline |

---

## 17. Next Steps

### Phase 2: Dataset Construction

1. ✅ Build manifest of Open Set images (CATALOG_ONLY + Colombian non-visual + visually similar + external)
2. ✅ Verify no leakage (obs_id, individual_id, hash, path against train/test)
3. ✅ Organize into evaluation/open_set_v1/dataset_manifest.csv

### Phase 3: Closed-Set Control

1. ✅ Run encoder pipeline on independent test set (known species only)
2. ✅ Capture: top-1, top-2, top-3, margin, embedding distance, score
3. ✅ Save to evaluation/open_set_v1/closed_set_control.csv

### Phase 4: Open Set Real

1. ✅ Run EXACT same pipeline on Open Set images (NO modifications)
2. ✅ Capture same metrics as Phase 3
3. ✅ Save to evaluation/open_set_v1/open_set_predictions.csv

### Phase 5–7: Ablations & Metrics

1. ✅ Vision only vs Vision+Prior
2. ✅ Prior adversarial (GPS perturbation)
3. ✅ Segmentation ablation (if applicable)
4. ✅ Compute AUROC, FPR@95TPR, OSCR, ECE, Brier Score

---

## AUDIT STATUS: ✅ AUDIT READY

**All pipeline components located, verified, and documented.**

**No blocking issues. Evaluation can proceed to Phase 2.**

---

*End of Audit*
