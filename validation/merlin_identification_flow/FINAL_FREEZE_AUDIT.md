# Auditoría final de congelación — ANURA/SITRana

**Fecha:** 2026-09-14  
**Alcance:** inventario y ejecución de evidencia existente; no se reentrenaron modelos, no se modificaron pesos, datasets históricos, embeddings, centroides ni thresholds.

## Inventario comprobado

| Elemento | Evidencia comprobada | Estado auditado |
|---|---|---|
| Runtime visual desktop | `validation/merlin_identification_flow/runtime_adapters.py::BioClipOnnxAdapter` usa `onnxruntime` CPU | Disponible y ejecutado |
| Encoder móvil | `bioclip/checkpoints/encoder_anura_fp16.onnx`, 173,414,601 bytes | SHA-256 `219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad` verificado |
| Checkpoint fuente | `bioclip/checkpoints/bioclip_anura_mejor.pt` | SHA-256 `98a6c54d6edb27e2b0344b8bbbaebd2ab749b1bf5136991ff73b37f66ee2c1ac`; no usado para inferencia Merlin |
| Preprocesamiento | `open_clip.create_model_and_transforms("hf-hub:imageomics/bioclip")` en el adaptador desktop | Ejecutado; la equivalencia nativa Android aún no está validada con fixture de paridad |
| Embedding | `bioclip/evaluation/encoder_metadata.json` y chequeo runtime | 512D, L2 normalizado, salida Float32 del runtime |
| Generación de embeddings | `evaluation/fase13/fase13_compute_embeddings.py`, `fase13_compute_train_embeddings.py`, `bioclip/scripts/fase_9_encoder_onnx_y_paquete_antioquia.py` | Existe y fue localizado |
| Ranking visual | `VisualRankingAdapter`, embeddings Fase 13 REFERENCE/TRAIN | 41 centroides, distancia euclídea negativa y normalización por fila |
| GEO-6 | `prior_zone_taxon_v2_clean.csv`, `cell_zone_map_v1.csv`, `GeographicAdapter` | Local; Antioquia únicamente; `w_geo_rank=0.3` experimental |
| Métrica GEO válida | `GEO2_GEO3_CORRECTION_NOTE.md` | ≈0.617 sin oracle; 0.701 solo histórico/oracular |
| Open Set | `OpenSetReleaseAdapter`, `covariance/v1.0.0`, `threshold/v1.0.0` | Mahalanobis y threshold congelado 39.35406371422803 |
| Prototipos/centroides | Fase 13 y releases de catálogo/covarianza | Disponibles; el ranking contiene 41 y la covarianza release es versionada |
| Vector DB | `bioclip/paquetes_regionales/antioquia_v1.sqlite` (6,705,152 bytes); `COLOMBIA_ANURA/ANTIOQUIA/reports/vector_package.json` | Existe; 3,881 vectores, 512D, 8.72 MB; Merlin no lo consume en su ruta actual |
| Catálogo taxonómico | `taxonomy/species/species_registry.json` | Consumido por `MerlinFlow` para IDs y metadata |
| Contrato central | `IDENTIFICATION_RESULT_SCHEMA.json`, `merlin_flow.py` | Existe; decisiones y scores no probabilísticos conservados |
| Adaptadores Merlin | `runtime_adapters.py`, `merlin_runtime_pipeline.py` | Ejecutados E2E |
| Android/Kotlin | `android-merlin-identification/` | Scaffold de biblioteca creado, sin Gradle instalado ni APK/modelo empaquetado para compilar |
| Evaluaciones y tests | Fases 13, 16, 20, 23A; `run_tests.py`, `run_runtime_e2e_suite.py`, `tools/catalog/tests/*` | Localizados; subconjunto relevante ejecutado en esta auditoría |

## Ejecuciones de esta auditoría

- `run_tests.py`: **10/10 PASS**.
- `run_runtime_e2e_suite.py`: **6/6 PASS** con ONNX FP16 real. La suite no entrega `ground_truth_species` al runtime.
- La misma suite con `HF_HUB_OFFLINE=1` y `TRANSFORMERS_OFFLINE=1`: **6/6 PASS** desde los artefactos cacheados/locales.
- Tres repeticiones offline de la suite produjeron el mismo resultado serializado (condición de igualdad de hashes satisfecha; hash actual: `79A5B0B0E32C729CC5325603862EE53746A84B85468B531D548CECD599657050`).
- Tests aislados de catálogo: lifecycle, membership por release y tamaño dinámico (41/42/100/inconsistente): **PASS**.
- Eliminación real en memoria: se retiró `Dendrobates truncatus` de `pipeline.flow.catalog` y se procesó una de sus imágenes. Salida: `ESPECIE_CONOCIDA`, score Mahalanobis `25.012601852416992 < 39.35406371422803`; los candidatos ya no incluyeron la especie retirada. Esto es un fallo del gate de eliminación: el Open Set sigue usando centroides del release anterior.

## Hallazgos críticos

1. El Open Set congelado no es un mecanismo de rechazo suficientemente validado para congelación productiva. El blind test Fase 16 reporta UDR 0.0612, FAR 0.9388 y AUROC 0.5928; Fase 20 reproduce FAR 0.9107 con el threshold oficial. Fase 23A, con encoder correcto, también reporta FAR 0.754 para UNKNOWN automático. Ninguna de estas métricas fue recalibrada en esta auditoría.
2. El catálogo activo y los centroides Open Set no comparten una frontera de release efectiva durante la eliminación. Puede emitirse `ESPECIE_CONOCIDA` para una observación de una especie retirada.
3. Existe un adaptador Kotlin, pero no un runtime Android compilado/ejecutado ni una prueba de paridad del preprocesamiento. No debe confundirse con compatibilidad móvil validada.
