# CLOSURE_MATRIX -- Estado de cierre por parte del encargo

| # | Parte | Estado | Evidencia |
|---|---|---|---|
| 1.1 | Masivas (imagen->embedding->ranking->OpenSet), 300 reales | PASS | `mass_inference_results.json` -- 300/300 exito, 0 fallos/NaN/dim invalida |
| 1.2 | Determinismo, 5 corridas x 2 imagenes | PASS | `determinism_results.json` -- embedding bit-identico, decision/score/ranking identicos; JSON completo solo difiere en observation_id/timing (documentado) |
| 1.3 | Entradas anomalas (16 casos sinteticos PIL) | PASS_WITH_GAP | `adversarial_inputs_results.json` -- 13/16 controlado (NO_CONCLUYENTE), 3/16 excepcion no controlada (archivo vacio/corrupto/bytes aleatorios); gap de contrato ERROR_DE_ENTRADA documentado, no implementado |
| 1.4 | Memoria/repeticion, 300 inferencias, psutil RSS | PASS | `memory_stability_results.json` -- RSS delta -2.83MB, pendiente ~0, sin degradacion de tiempo; cifras de Android quedan NOT_VERIFIED (sin dispositivo) |
| 2 | Regresion Open Set (threshold intacto) | PASS | `openset_regression_metrics.json` -- AUROC=0.538042/FAR=0.85 identicos a handoff previo; 5 configuraciones de catalogo activo probadas bajo carga completa (7475+620) |
| 3 | Elegibilidad Dendrobates truncatus | PASS | `dendrobates_truncatus_eligibility.json/.md` -- Tier B (n=49 individuos, piso), sin leakage cruzado, YA DEPLOYED; `DENDROBATES_TRUNCATUS_ELIGIBLE=YES` |
| 4 | Reproduccion bug DYNAMIC_REMOVE_SPECIES_FAIL, evidencia fresca | PASS | `bug_reproduction_v2.json` -- 17/17 pasos PASS, numeros identicos a fase previa (25.0126/38.8330), corrida NUEVA no reciclada |
| 5 | Mapa de distribucion por especie | PASS_WITH_GAP | `species_distribution_maps_v1.json` -- 33/41 especies con >=1 registro en records_v1.csv (Antioquia); 9/41 con 0 registros (fuera del alcance geografico de esa fuente, documentado) |
| 6 | Regla de arquitectura (visual primero, geo/alt despues) | PASS | Confirmado por diseno en `runtime_adapters.py`/`merlin_flow.py` (no modificados) y en todos los scripts nuevos: geo/alt nunca entran a `OpenSetReleaseAdapter.assess` ni modifican `embedding` |
| 7 | Rangos de altitud | PASS_WITH_GAP | `elevation_ranges_v1.json` -- 29/41 especies con datos suficientes (>=3 registros); 12/41 insuficientes |
| 8 | Combinacion de evidencias, separada | PASS | Scores visual/geo/altitud reportados SIEMPRE por separado en `context_ablation_results.json` y en el annex; combinacion opcional documentada con pesos explicitos (w_geo=0.3, w_alt=0.15) |
| 9 | Prohibicion de oracle | PASS | `grep ground_truth` sobre todo el codigo nuevo -- unico uso es el flag `ground_truth_used: False` (declaracion, no consumo) y `true_species` usado SOLO post-hoc para medir accuracy, nunca dentro de geo_score/alt_score/visual ranking |
| 10 | Ablacion A/B/C/D general | NOT_VERIFIED (protocolo completo) / PASS (version reducida honesta) | `context_ablation_results.json` -- pool oficial KNOWN (7475) no tiene coordenadas por diseno (0% cobertura, verificado); version reducida real n=38 (multiples especies) ejecutada con bootstrap 1000/seed=42: geo/altitud no mejoran Top1/Top3 sobre visual solo |
| 11 | Regla de similitud visual excluye R. marina | PASS | `rmarina_exclusion_test.json` -- confirmado estructuralmente (sin species_id, sin centroide) + test end-to-end con embedding real |
| 12 | Paquetes + contexto (extension) | PASS | `package_context_extension_test.json` -- geography.json/elevation.json opcionales, reempaquetado real v1.0.2, ciclo completo install/validate/activate/deactivate/reactivate + compat retro con v1.0.0 |
| 13 | Estres de paquetes (10 casos adversariales) | PASS | `package_stress_test_results.json` -- 10/10 casos con comportamiento esperado, 0 excepciones no controladas |
| Anexo | Auditoria P. paisa/taeniatus | PASS (metricas) / NOT_VERIFIED (ablacion especifica) | `PRISTIMANTIS_PAISA_TAENIATUS_AUDIT.json/.md` -- distancia 0.1944 confirmada (percentil 0/820), varianza intra, overlap cruzado ~21-22%, k-means k=2 medido; ablacion geo/alt especifica sin cobertura de coordenadas (0/159) -> NOT_VERIFIED; veredicto `SEPARATION_DIFFICULT` |

## Reglas duras -- verificacion final

| Regla | Estado |
|---|---|
| Encoder/checkpoint no tocados | PASS -- SHA256 verificado en cada corrida (`219e860e...`/`98a6c54d...`), sin escritura a `bioclip/checkpoints/` |
| Threshold no recalibrado | PASS -- `39.35406371422803` constante en todos los scripts, nunca reasignado |
| Artefactos congelados no modificados | PASS -- ver `git status` en el reporte final; solo `package_manager.py` (extension permitida) y archivos nuevos bajo `stress_test_v1/` |
| Sin ground_truth en inferencia | PASS -- ver Parte 9 |
| Sin multiples prototipos automaticos por especie | PASS -- k-means k=2 solo MEDIDO (silhouette), nunca aplicado al runtime |
| Sin mover centroides | PASS -- `VisualRankingAdapter`/`OpenSetReleaseAdapter` no modificados |
| Sin commit/push | PASS -- ningun `git add`/`git commit` ejecutado en esta sesion |
