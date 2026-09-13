# Fase 9 — Rejection analysis

STATUS: FASE_9_COMPLETE; official F3=766, F4=56.

BEST_METHOD (exploratory, in-sample): `mahalanobis_distance`; AUROC=1.000000; FAR@95% known acceptance=0.000000.

## Method coverage
Centroid geometry, nearest-neighbor, kNN profiles k=1/3/5/10 (k=10 only if SQLite-vec query returned 10), confidence and fixed 50/50 rank combination were evaluated. Energy/logit: NOT_AVAILABLE. NUMERICALLY_STABLE_IN_SAMPLE.

## Difficult unknown cases
Top unknown scores are in `rejection_cases.csv`; species-stratified counts and the Hyloxalus_picachos/Sachatamia_electrops split are retained in the CSV.

## Interpretation
Thresholds are descriptive EVALUATION ONLY and were not calibrated or selected on F3/F4. Mahalanobis is numerically stable but was fitted on the same F3 KNOWN embeddings used for evaluation, so its AUROC=1.0 and FAR=0.0 are optimistic in-sample results, not independent validation. No GPS/prior, sound, segmentation, masks, artificial metadata, new images, or production changes were used.

## Prior-phase comparison
F5/F6/F8B source artefacts were audited for contextual comparison only; their reported metrics are not merged into this uncalibrated analysis.

## Scientific conclusion
Resultado PARCIAL/INCONCLUSO para producción. Las señales centroid y nearest-neighbor no separan suficientemente UNKNOWN. El resultado perfecto de Mahalanobis no es defendible como validación externa porque el modelo de distancia fue estimado con el mismo F3 usado para medir aceptación KNOWN. Se necesita una referencia independiente para calibrar y ajustar el detector antes de recomendar un umbral.
