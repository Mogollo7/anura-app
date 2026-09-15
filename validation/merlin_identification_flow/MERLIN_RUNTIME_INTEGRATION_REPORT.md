# Integración runtime Merlin — resultado

**Estado:** `MERLIN_RUNTIME_INTEGRATION_PARTIAL`

## Runtimes conectados

- **Visual real:** `encoder_anura_fp16.onnx` (Fase 9, FP16 móvil), ejecutado por ONNX Runtime CPU. SHA256 verificado: `219e860e…b2ad`. El checkpoint PyTorch de origen `bioclip_anura_mejor.pt` también se verifica (`98a6c54d…e2c1ac`), pero no se usa para inferencia.
- **Preprocesamiento:** exactamente el constructor de preprocessing utilizado por Fase 9/Fase 13: `open_clip.create_model_and_transforms("hf-hub:imageomics/bioclip)`. BioCLIP PyTorch no hace inferencia.
- **Ranking:** 41 centroides de Fase 13, con la regla exacta GEO-6 (REFERENCE solo si también existe en TRAIN; TRAIN completa el pool). Similaridad = distancia euclidiana negativa normalizada por fila.
- **GEO real:** `cell_zone_map_v1.csv` y `prior_zone_taxon_v2_clean.csv`; sin ubicación o fuera de cobertura, no aporta score ni penaliza la evidencia visual. Con cobertura, usa únicamente `w_geo_rank=0.3`, marcado experimental.
- **Open Set real:** releases congelados `covariance_1.0.0` y `threshold_1.0.0`; min-distancia Mahalanobis contra centroides del release. Un rechazo devuelve `NO_CONCLUYENTE`, nunca `NO_REGISTRADA`.

## Resultados de pruebas

| Prueba | Resultado |
|---|---|
| `run_tests.py` | 10/10 PASS |
| `run_runtime_e2e.py` | 1/1 PASS: imagen → ONNX FP16 → ranking → GEO → Open Set → `IdentificationResult` |
| `run_runtime_e2e_suite.py` | 6/6 PASS |

La suite E2E no entrega etiquetas al runtime. La imagen UNKNOWN fue rechazada por Open Set (`44.406 > 39.354`) y produjo `NO_CONCLUYENTE` aun con un Top-1 visual. Para el caso geográfico, la misma especie visual obtuvo `geographic_score` 0.396 en ZONE_005 y 0.018 en ZONE_001; GEO no cambió por sí solo la decisión Open Set.

## Métricas y thresholds

- **Histórica/diagnóstica GEO-2/GEO-3:** 0.701 es resultado afectado por oracle information; no se usa en inferencia.
- **Referencia geográfica honesta sin oracle:** AUROC ≈ **0.617**.
- **Ranking GEO-6:** `w_geo_rank=0.3`, experimental; no es una configuración definitiva de producción.
- **Open Set runtime:** `threshold_1.0.0 = 39.35406371422803`, Mahalanobis, calibración histórica `CALIBRATION`, KAR 95%. La salida lo marca `thresholds_production_ready=false`; no se recalibró ni se presenta como threshold de producción.
- **Métricas nuevas:** no se reportan métricas de calidad nuevas a partir de 6 imágenes E2E; son pruebas funcionales, no un experimento.

## Limitaciones y bloqueos reales

- No existe un clasificador/validador inicial de **anuro vs no-anuro** reutilizable. El runtime requiere `is_anuran` y su evidencia de una capa externa; si no se confirma, responde `NO_CONCLUYENTE`.
- No hay proyecto Android/Kotlin ni API en este checkout. El contrato está preparado pero no puede compilarse ni probarse contra una app inexistente.
- GEO cubre las zonas congeladas de Antioquia; fuera de esa cobertura el flujo es visual/Open Set sin GEO.
- GEO-6 Open Set por cohorte no se usa para inferencia individual porque su normalización de evaluación no es desplegable sin introducir sesgo.
- Segmentación no se conecta: no hay contrato de rasgos estable para inferencia real.
- Ninguna ruta declara automáticamente `NO_REGISTRADA`.

## Trazabilidad y seguridad metodológica

No se modificaron BioCLIP, embeddings, datasets, Fase 23A, GEO-2/GEO-3/GEO-4/GEO-5/GEO-6, priors ni thresholds. Las rutas de inferencia no reciben `ground_truth_species`; las etiquetas solo se consultan después para evaluación de la suite.
