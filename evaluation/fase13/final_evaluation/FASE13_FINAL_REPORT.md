# FASE 13 — Reporte Final de Calibración Independiente del Rechazo Open Set

**STATUS**: `STATUS: FASE13_COMPLETE`

## Métricas Finales Out-of-Sample (F3 KNOWN vs F4 UNKNOWN)

- **AUROC**: `0.624767`
- **AUPR**: `0.081335`
- **FAR @ 95% TPR**: `0.946429`
- **FAR @ 90% TPR**: `0.946429`
- **FAR @ 85% TPR**: `0.910714`

## Evaluación al Umbral Congelado τ (95% KAR en CALIBRATION)

- **Umbral Congelado τ**: `39.354064`
- **Known Acceptance Rate (KAR) F3**: `0.8538`
- **Unknown Detection Rate (UDR) F4**: `0.0893`
- **False Acceptance Rate (FAR) F4**: `0.9107`

## Desglose por Grupos de Especies

- **Grupo A (10 Especies Calibradas Independientemente)**: KAR = `0.8731`
  - Centroides extraídos de: REFERENCE (calibración independiente)
- **Grupo B (31 Especies Estructurales sin Calibración Independiente)**: KAR = `0.8471`
  - Centroides extraídos de: TRAIN (sin calibración independiente, solo estructura)

## Desglose por Especie UNKNOWN (F4)

| Especie UNKNOWN | Muestras Totales | Rechazadas (Correctas) | UDR | Distancia Media |
|---|---|---|---|---|
| `Hyloxalus_picachos` | 15 | 2 | `0.1333` | `32.6423` |
| `Sachatamia_electrops` | 41 | 3 | `0.0732` | `33.8426` |


## Declaraciones Obligatorias de Diseño

- `9_OF_41_INDEPENDENTLY_CALIBRATED`: `YES (Leucostethus fraterdanieli orphaned)`
- `32_OF_41_INDEPENDENTLY_CALIBRATED`: `NO`
- `INDIVIDUAL_INDEPENDENCE`: `CONTROLLED_NOT_FORMALLY_VERIFIABLE`
- `OBSERVATION_INDEPENDENCE`: `NOT_FORMALLY_VERIFIABLE`
- `CALIBRATION_AUROC`: `NOT_COMPUTABLE`


## Auditoría de Fuente de Centroides

Ver `centroid_source_audit.json` para detalles completos de origen de cada centroide.

## Second Brain (Obsidian)

Nota puente con contexto de metodología y decisiones relacionadas:
`Second Brain/Brain/05_OPEN_SET/FASE_13_CALIBRACION_INDEPENDIENTE.md`

Ver también: `Second Brain/Brain/15_DECISIONS/DECISION_LOG.md` (decisión C-16).
