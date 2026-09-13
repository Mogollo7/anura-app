# Fase 13 — Calibración Independiente del Rechazo Open Set

> Nota puente. El contenido completo, código y artefactos viven en el repositorio
> (`evaluation/fase13/`), no en el vault. Esta nota enlaza ambos mundos.

**Repositorio**: [anura-app](https://github.com/Mogollo7/anura-app)
**Status**: `FASE13_COMPLETE` (no `READY_FOR_PRODUCTION`)
**Fecha**: 2026-09-13

## Resumen

Calibración del mecanismo de rechazo Open Set mediante Mahalanobis con
regularización Ledoit-Wolf (`M5_LedoitWolf_Shared`), evaluado en condiciones
ciegas sobre F3 (766 KNOWN, 41 especies) + F4 (56 UNKNOWN, 2 especies).

## Arquitectura de centroides

- **Grupo A** (9 especies): calibración independiente, fuente `REFERENCE` (798 imágenes)
- **Grupo B** (32 especies): referencia estructural, fuente `TRAIN` (3608 imágenes)
- **Orphaned**: `Leucostethus fraterdanieli` — presente en REFERENCE pero ausente
  de TRAIN/clases visuales. Excluida de los 41 centroides.

## Resultados (blind F3+F4)

| Métrica | Valor |
|---|---|
| AUROC | 0.6248 |
| KAR (Known Acceptance Rate) | 85.38% |
| UDR (Unknown Detection Rate) | 8.93% |
| FAR (False Acceptance Rate) | **91.07%** ⚠️ |
| KAR Grupo A | 87.31% |
| KAR Grupo B | 84.71% |

⚠️ **FAR=91% es el hallazgo crítico pendiente**: el sistema es muy permisivo
con especies desconocidas. Threshold candidato alternativo: τ@90%KAR=35.36
(vs. el congelado τ@95%KAR=39.35).

## Bugs corregidos durante Fase 13

1. **Embedding extractor divergente**: el script de extracción de
   REFERENCE/CALIBRATION construía el modelo BioCLIP de forma distinta a
   F3/F4 (`create_model('ViT-B-16', pretrained=False)` + preprocessing manual
   vs. `create_model_and_transforms("hf-hub:imageomics/bioclip")`). Causaba
   embeddings incompatibles y KAR Grupo A = 0%.
2. **Leakage en Fase E**: los centroides de Grupo B se construían desde F3
   KNOWN (in-sample), violando la separación ciega. Corregido usando TRAIN
   (3608 imágenes verificadas, sin contaminación cruzada).
3. **Typo taxonómico**: "Pristimantis acanthinus" (REFERENCE) vs.
   "Pristimantis achatinus" (nombre real, usado en TRAIN/taxonomía).

## Artefactos en el repositorio

- `evaluation/fase13/final_evaluation/FASE13_FINAL_REPORT.md`
- `evaluation/fase13/final_evaluation/centroid_source_audit.json`
- `evaluation/fase13/selection/frozen_rejection_config.json`
- `evaluation/fase13/AUDITORIA_FINAL_FASE13.py`
- `evaluation/fase13/ANTIOQUIA_v1.0.0_manifest.json`

## Ver también (vault)

- [[05_OPEN_SET/INDEX|Open Set — Índice]]
- [[06_EVALUATION/INDEX|Evaluación — Índice]]
- [[15_DECISIONS/DECISION_LOG|Registro de Decisiones]]
- [[02 Metodología/Open-Set Recognition|Open-Set Recognition (metodología original)]]

## Próximo paso

Decisión pendiente sobre threshold de producción (39.35 vs 35.36) tras
validación de campo en Antioquia. No iniciar Fase 14 sin ese gate.
