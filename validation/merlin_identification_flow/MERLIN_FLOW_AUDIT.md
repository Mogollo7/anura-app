# Auditoría del flujo Merlin de identificación

**Estado:** auditado antes de implementar.  
**Alcance:** prototipo de flujo de datos; no modifica producción ni artefactos históricos.

## 1. EXISTENTE

| Área | Evidencia localizada | Estado |
|---|---|---|
| BioCLIP y embeddings | `bioclip/scripts/fase_6_extraer_encoder.py`, `evaluation/fase13/embeddings/*.npz`, `validation/fase23a_open_set_automatic/fase23a_final.py` | Encoder y contrato de embedding existentes, congelados. |
| Catálogo/taxonomía | `taxonomy/species/species_registry.json`, `training/taxonomia.py`, `COLOMBIA_ANURA/ANTIOQUIA/catalog/catalog_v1.json` | IDs y metadata de especie, género y familia disponibles. |
| Paquetes/regiones/prior | `regional_packages/`, `COLOMBIA_ANURA/ANTIOQUIA/`, `validation/fase23a_geographic_context/prior_zone_taxon_v2_clean.csv` | Prior por especie y zona existente. |
| Ranking GEO-6 | `validation/fase23a_geographic_context/scripts/phase_geo6_two_stage.py`, `GEO6_RANKING_RESULTS.json` | Ranking de 41 candidatas, normalización por fila y `w_geo_rank=0.3` experimental documentados. |
| Open Set | `validation/fase23a_open_set_automatic/`, `validation/fase23a_geographic_context/GEO6_OPENSET_DECISION_SUMMARY.json` | Infraestructura y thresholds diagnósticos existentes. |
| Corrección GEO-2/GEO-3 | `validation/fase23a_geographic_context/GEO2_GEO3_CORRECTION_NOTE.md` | AUROC geográfico sin oracle ≈0.617; 0.701 histórico/diagnóstico únicamente. |
| Segmentación | Directorio `segmentacion/` y scripts `bioclip/scripts/detectar_*.py` | Hay investigación/artefactos de visión, pero no un contrato estable de rasgos para inferencia. |
| API/app Android | No se encontraron directorios backend/API/Kotlin/Gradle en el checkout auditado. | No integrable todavía. |

## 2. REUTILIZABLE

- La fórmula de ranking GEO-6: `0.7 * visual_score + 0.3 * geographic_score`, solo cuando ambos scores normalizados están disponibles. El peso queda marcado como `EXPERIMENTAL_GEO6_W_GEO_RANK_0_3`.
- El catálogo de especies para resolver `species_id`, nombre científico, género y familia. Los nombres comunes no se inventan: se emiten como `null` si el catálogo no los ofrece.
- El patrón de GEO-6 de separar **ranking** de **Open Set**. El adaptador acepta evidencia Open Set producida por Fase 23A/GEO-6, sin recalibrar thresholds.
- Las decisiones y limitación de GEO-6: con thresholds diagnósticos se permite `ESPECIE_CONOCIDA` o `NO_CONCLUYENTE`; una incompatibilidad fuerte se conserva como `NO_CONCLUYENTE`, no como `NO_REGISTRADA`.

## 3. FALTANTE

- Un contrato central, estable y consumible por cliente para observación, candidatos, evidencia y decisión.
- Un orquestador que aplique ranking y Open Set como etapas independientes sin ejecutar experimentos.
- Explicaciones estructuradas que digan qué contexto se usó/no estaba disponible y por qué Top-1 no implica aceptación.
- Pruebas deterministas de los casos de producto solicitados.
- Un adaptador de producción que obtenga por imagen la evidencia visual y la evidencia Open Set desde el runtime BioCLIP congelado.

## 4. BLOQUEADO

- No existe en este checkout una API/backend ni una aplicación Android/Kotlin a la cual conectar el flujo.
- No hay un contrato de segmentación validado para declarar rasgos anatómicos. El prototipo solo transporta observaciones con `PRESENTE`, `AUSENTE` o `NO_EVALUABLE`; no infiere ni inventa rasgos.
- Los thresholds GEO-6 son explícitamente `DIAGNOSTIC`, calibrados sobre TEST, por lo que no son aptos para producción.
- La evidencia actual no distingue de forma científica `NO_REGISTRADA` de una observación ambigua; el fallback obligatorio es `NO_CONCLUYENTE`.

## 5. PROPUESTA DE INTEGRACIÓN

Crear `validation/merlin_identification_flow/` como capa de integración aislada:

1. Un adaptador runtime entrega `VisualEvidence` (candidatas visuales y evidencia de validación de anuro) y, opcionalmente, `GeographicEvidence` y `OpenSetEvidence` desde infraestructura congelada.
2. El orquestador resuelve taxonomía desde el registro existente, produce Top-K configurable (por defecto 3) y solo mezcla geo-especie disponible con el peso GEO-6 experimental 0.3.
3. El Open Set recibe la evidencia ya calculada y decide de forma independiente. Nunca acepta un Top-1 por su rango.
4. El resultado cumple `IDENTIFICATION_RESULT_SCHEMA.json`, es serializable y apto para un futuro adaptador móvil/API.

No se reutilizan ni se reejecutan scripts experimentales como parte de la inferencia del prototipo; se respeta el estado congelado de Fase 23A y GEO-2 a GEO-6.
