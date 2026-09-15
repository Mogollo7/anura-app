# MERLIN_RUNTIME_INTEGRATION_AUDIT

**Fecha:** 2026-09-14  
**Alcance:** lectura de artefactos existentes, sin modificar datasets, experimentos, pesos ni thresholds.

| Componente | Archivo / función | Estado | Qué falta / riesgo | Acción propuesta |
|---|---|---|---|---|
| BioCLIP | `bioclip/checkpoints/encoder_anura_fp16.onnx`; `fase_9_encoder_onnx_y_paquete_antioquia.py` | REUTILIZABLE | Runtime no está expuesto como módulo de inferencia individual. | Adaptador nuevo ONNX que replique el preprocessing BioCLIP existente y verifique SHA256 `219e…b2ad`, el contrato de releases. |
| Checkpoint/origen | `bioclip/checkpoints/bioclip_anura_mejor.pt` | TRAZABILIDAD DISPONIBLE | SHA256 real `98a6c54d…66ee2c1ac`; es el checkpoint PyTorch del cual Fase 9 exportó el ONNX. No es el hash del artefacto ONNX. | Registrar ambos hashes y usar el ONNX FP16 para inferencia/release; no intercambiarlos. |
| Espacio visual/ranking | `evaluation/fase13/embeddings/{reference,train}_embeddings.npz`; `phase_geo6_two_stage.py` | REUTILIZABLE | No hay clase runtime reutilizable; el script GEO-6 se ejecuta al importarse. | Adaptador nuevo de lectura que construya los 41 centroides existentes y aplique la misma distancia/normalización de ranking. |
| GEO | `prior_zone_taxon_v2_clean.csv`, `prior_zone_taxon_v2_clean_manifest.json`, `COLOMBIA_ANURA/ANTIOQUIA/zones/cell_zone_map_v1.csv` | REUTILIZABLE | No existe API runtime aislada. Cobertura limitada a celdas/zona de Antioquia. | Adaptador de coordenadas a zona y prior por especie derivado de los archivos congelados; fuera de cobertura = no aplicar GEO. |
| GEO-6 | `GEO6_RANKING_RESULTS.json`, `GEO6_OPENSET_DECISION_SUMMARY.json` | REUTILIZABLE CON RESTRICCIÓN | `w_geo_rank=0.3` es experimental; thresholds son diagnósticos. AUROC honesto sin oracle ≈0.617. | Usar solo el peso de ranking y declarar flags; nunca usar 0.701 ni usar GEO como aceptación positiva. |
| Open Set release | `tools/catalog/run_open_set_evaluation.py`, `covariance/v1.1.0_CLEAN`, `threshold/v1.1.0_CLEAN` | REUTILIZABLE CON RESTRICCIÓN | El contrato `219e…` corresponde al ONNX FP16 existente y verificado, no al archivo PyTorch. Los thresholds se mantienen como release histórico; no son los thresholds GEO-6. | Integrar min-Mahalanobis por centroides con el ONNX compatible y el threshold congelado; marcar procedencia y no declarar `NO_REGISTRADA`. |
| Open Set Fase23A/GEO-6 | `fase23a_final.py`; `phase_geo6_two_stage.py` | NO DESPLEGABLE POR MUESTRA | GEO-6 normaliza sobre el cohorte completo KNOWN+UNKNOWN de evaluación; eso no es una función de inferencia individual y usarlo en móvil sería metodológicamente inválido. | Exponer solo evidencia diagnóstica si existe un score precomputado compatible. Para foto en vivo, devolver `NO_CONCLUYENTE` con `OPEN_SET_RUNTIME_BLOCKED`. |
| Catálogo | `taxonomy/species/species_registry.json` | REUTILIZABLE | Ninguno para metadata. | Resolver species_id, género, familia; common_name permanece `null` si no existe. |
| API / Android | búsqueda de directorios y archivos Kotlin/Gradle | AUSENTE | No hay backend ni proyecto Android en el checkout. | Entregar contrato JSON y una interfaz de adaptadores; integración concreta queda bloqueada hasta que exista cliente/API. |

## Conclusión de auditoría

Es viable integrar y ejecutar realmente **foto → BioCLIP ONNX → embedding → ranking visual → GEO → Open Set release → IdentificationResult**, siempre que las dependencias de BioCLIP/ONNX estén disponibles localmente. GEO-6 sigue sin ser una función de Open Set por muestra individual; se usa solo su peso de ranking experimental. La decisión Open Set reutiliza el release compatible versionado y nunca declara automáticamente `NO_REGISTRADA`.

La implementación posterior debe conservar esa frontera y no usar ground truth en ninguna ruta de inferencia.
