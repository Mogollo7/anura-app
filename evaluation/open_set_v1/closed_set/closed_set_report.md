# Closed-Set Control Report

## Evaluation Date
2026-09-13 01:03:13

## Dataset
- Test images: 766
- Species: 41
- Leakage detected: 0
- Status: ✅ ALL CLEAN

## Model Specifications
- Checkpoint: bioclip_anura_mejor.pt
- Route A (Softmax): Implemented
- Route B (k-NN): Not implemented in Fase 3
- Geographic prior: Not applied
- Rejection threshold: Not applied

## Metrics
- Top-1 Accuracy: 56.92%
- Top-3 Accuracy: 82.38%
- Images correctly classified (Top-1): 436/766
- Images correctly classified (Top-3): 631/766

## Error Analysis
- High-confidence errors (>0.9 probability): 0
- Error rate (Top-1): 43.08%

## Distribution
Accuracy by species: (see closed_set_results.json for detailed breakdown)

## Next Steps
Fase 4: Open Set Real Evaluation
- Use same pipeline on 56 CATALOG_ONLY images
- Compare confidence/margin/score distributions
