# Informe de validación del flujo Merlin

**Estado:** PASS — prototipo de lógica y datos, no despliegue de producción.

Se ejecutó `run_tests.py` con el entorno local y se obtuvieron **10/10 pruebas PASS**. El resultado detallado y reproducible quedó en `test_execution_result.json`.

| Caso | Resultado comprobado |
|---|---|
| Candidato claro | Candidato visual/geográfico y decisión `ESPECIE_CONOCIDA` solo tras Open Set. |
| Candidatos cercanos | Top-3 conservado y decisión `NO_CONCLUYENTE`. |
| UNKNOWN | Nunca se fuerza `NO_REGISTRADA`; se devuelve `NO_CONCLUYENTE`. |
| Sin contexto geográfico | Ranking visual, score geográfico `null`, limitación explícita. |
| Con contexto geográfico | Geo-especie se incorpora con el peso experimental 0.3. |
| Contexto incompatible | El ranking puede cambiar, pero Open Set sigue siendo una etapa separada. |
| Open Set ambiguo | Top-1 no implica aceptación. |
| Taxonomía | Se resuelven familia y género desde el registro existente. |
| Semántica de scores | El contrato contiene scores; no hay campo de probabilidad. |
| No aceptación automática | Top-1 alto con Open Set ambiguo produce `NO_CONCLUYENTE`. |

## Controles verificables

- El resultado marca `EXPERIMENTAL_GEO6_W_GEO_RANK_0_3` y `SCORES_ARE_NOT_PROBABILITIES`.
- Cuando se usan los valores por defecto de GEO-6, la salida declara `OPEN_SET_THRESHOLDS_DIAGNOSTIC` y `thresholds_production_ready: false`.
- Género y familia son metadata; no participan en `ranking_score`.
- La validación de segmentación solo admite `PRESENTE`, `AUSENTE` y `NO_EVALUABLE`.

## No validado aquí

No se ejecutó BioCLIP sobre fotos, no se recalculó prior geográfico, no se lanzó GEO-7 y no se modificaron artefactos de Fase 23A ni GEO-2 a GEO-6. El flujo se validó con adaptadores deterministas porque no hay app móvil ni API/backend en este checkout.
