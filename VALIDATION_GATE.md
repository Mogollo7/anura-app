# VALIDATION_GATE.md

Estructura formal que todo `catalog_release` candidato debe atravesar antes de poder marcarse
`APPROVED`/`DEPLOYED`. Generaliza — sin modificarlo — el proceso que Fase 13 ya ejecutó una vez
de forma manual y secuencial.

## Pasos del gate

```
DATA QUALITY
      ↓   ¿imágenes legibles, sin corrupción, resolución mínima?
TAXONOMIC VALIDATION
      ↓   ¿species_id resuelto sin ambigüedad? ¿alias conocido aplicado (ver taxonomia.py ALIAS)?
CONTAMINATION CHECK
      ↓   ¿cero solapamiento por file_hash/observation_id entre TRAIN/REFERENCE/CALIBRATION/BLIND?
EMBEDDING VALIDATION
      ↓   ¿encoder_sha256 + dim + preprocessing_version coinciden con el contrato vigente?
CENTROID VALIDATION
      ↓   ¿covarianza bien condicionada? ¿metadata completa (source_split, image_count)?
OPEN SET EVALUATION
      ↓   ¿AUROC/KAR/UDR/FAR calculados sobre un set no usado para calibrar?
BLIND TEST
      ↓   ¿evaluación final ejecutada sobre datos nunca vistos por el método/threshold?
GATE
      ↓   PASS / FAIL / PENDING
```

## Resultado del gate — 3 estados únicamente

```
PASS     → puede pasar a APPROVED → DEPLOYED
FAIL     → queda REJECTED, con razón documentada, sin eliminar el intento del historial
PENDING  → falta un paso (ej. blind test no ejecutado todavía); no puede avanzar
```

**Nunca** un estado automático de `READY_FOR_PRODUCTION` — esa es una decisión humana posterior
al gate, consistente con la Corrección 8 de Fase 13.

## Mapeo real: qué de esto ya existe hoy y qué es nuevo

| Paso del gate | Estado real en el repo hoy | Script existente |
|---|---|---|
| DATA QUALITY | Parcial — hay auditorías de coordenadas/fotos no representativas, no un check unificado | `bioclip/scripts/detectar_fotos_no_representativas.py` |
| TAXONOMIC VALIDATION | Parcial — `taxonomia.py` tiene `ALIAS`, pero no se invoca desde Fase 13 (ver WARNING-1 del audit) | `training/taxonomia.py` |
| CONTAMINATION CHECK | Sí existe, disperso en 4+ scripts distintos | `fase13_pre_audit.py`, `build_dataset_manifest.py`, `fase13_generate_train_manifest.py` |
| EMBEDDING VALIDATION | Manual, no automatizado como check reutilizable | verificación ad-hoc de SHA256 en `fase13_pre_audit.py` |
| CENTROID VALIDATION | Parcial — hay `assert` de conteo fijo, no validación de condicionamiento numérico como gate | `fase13_final_evaluation.py` |
| OPEN SET EVALUATION | Sí, completo | `fase13_cv_reference.py`, `fase13_calibrate_selection.py` |
| BLIND TEST | Sí, completo (F3/F4) | `fase13_final_evaluation.py` |
| GATE (orquestador) | **No existe como función reutilizable** — solo `run_fase13_pipeline.py`, runner lineal de subprocess | — |

## validation_report — formato de salida

Cada ejecución del gate debe producir, por release:

```json
{
  "catalog_release": "visual_catalog_1.0.0",
  "gate_result": "PASS",
  "steps": {
    "data_quality": "PASS",
    "taxonomic_validation": "PASS",
    "contamination_check": "PASS",
    "embedding_validation": "PASS",
    "centroid_validation": "PASS",
    "open_set_evaluation": "PASS",
    "blind_test": "PASS"
  },
  "evidence": {
    "auroc": 0.624767,
    "kar": 0.8538,
    "udr": 0.0893,
    "far": 0.9107
  },
  "warnings": [
    "FAR=91% — sistema muy permisivo con UNKNOWN, revisar antes de producción",
    "INDIVIDUAL_INDEPENDENCE=CONTROLLED_NOT_FORMALLY_VERIFIABLE"
  ],
  "generated_at": "..."
}
```

## Nota sobre visual_catalog_1.0.0 (baseline)

El baseline (Fase 13) **ya ejecutó** todos estos pasos, pero de forma manual/secuencial, no a
través de un gate programático. El `validation/v1.0.0/validation_report.json` que acompaña a esta
arquitectura es un **retrofit honesto**: reconstruye el resultado del gate a partir de la evidencia
ya generada por Fase 13, marcado explícitamente como tal (no se re-ejecuta nada, no se genera
evidencia nueva). Ver `validation/v1.0.0/validation_report.json`.
