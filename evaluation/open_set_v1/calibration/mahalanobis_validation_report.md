# Fase 10 — Mahalanobis validation

## STATUS
STATUS=NO_INDEPENDENT_REFERENCE_AVAILABLE
INDEPENDENT_REFERENCE=false
REFERENCE_SIZE=0
REFERENCE_SPECIES=[]
COVARIANCE_METHOD=NOT_RUN
REGULARIZATION=NOT_RUN
THRESHOLD_SOURCE=NOT_RUN

## Alcance y salvaguardas
No se modificó ningún modelo, checkpoint, encoder, peso, embedding original, dataset, F3/F4, SQLite-vec, prior, app ni producción. Solo se escribieron artefactos en `evaluation/open_set_v1/calibration/`.
TRAIN se etiqueta TRAIN_REFERENCE y VAL VALIDATION_REFERENCE; ninguno es independiente. TEST/F3 y F4 son evaluación, nunca ajuste.

## Auditoría exhaustiva de independencia
- `data cleaned/dataset_limpio.json`: 12254 imágenes; 7531 no están en una partición declarada.
- Las imágenes no asignadas no se aceptan: pertenecen al mismo corpus limpio y no tienen declaración de split/proveniencia independiente.
- El cache de embeddings existente es mixto y carece de metadatos de split; por tanto no puede certificar referencia independiente.
- Manifest F3/F4: 56 UNKNOWN CATALOG_ONLY (F4=56), sin referencia KNOWN independiente.
- Evidencia completa path/obs_id/SHA/individual/perceptual hash está en `calibration_inventory.json`.

## Métricas
No se ejecutó ajuste ni evaluación out-of-sample. AUROC, AUPR, FAR/UDR/KAR/FNR, bootstrap CI y casos extremos: NO ESTIMABLES (evita validación falsa). UNKNOWN F4 por especie (solo inventario, no desempeño): Hyloxalus_picachos=15; Sachatamia_electrops=41.

## Comparación Fase 9 in-sample vs Fase 10 out-of-sample
Fase 9 reportó Mahalanobis AUROC=1.0 con covarianza ajustada sobre F3 y evaluada sobre F3: resultado optimista in-sample. Fase 10 out-of-sample no es estimable.

## Viabilidad y referencia futura
Se requiere un conjunto KNOWN explícitamente retenido, con especies conocidas, separado de TRAIN/VAL/TEST/F3 por path, obs_id, SHA256, individual_id y perceptual hash. Además, una calibración independiente para fijar threshold. La covarianza/regularización se congela antes de tocar F3/F4; después F3=766 y F4=56 se evalúan una sola vez.

## CONCLUSION
No hay evidencia suficiente de referencia independiente legítima. No se ejecuta una falsa validación out-of-sample.
## NEXT_PHASE
Obtener y documentar referencia KNOWN independiente + calibración independiente; repetir Fase 10 sin mirar F3/F4.

## Integridad
Hashes SHA256 de artefactos externos antes de la ejecución están en `calibration_inventory.json` y se deben comparar con la lista posterior.
