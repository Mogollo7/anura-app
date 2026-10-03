# Open Set + contexto topográfico v1

**Estado:** `NO_GO — sin mejora operacional demostrada`  
**Fecha:** 2026-09-14  
**Código:** `run_topographic_context.py`  
**Regla visual reutilizada:** dos prototipos por especie + distancia/margen, congelada desde `open_set_calibration_v1`.

## Protocolo

- El encoder, pesos, embeddings fuente, catálogo, priors GEO y artefactos de Fase 23A no se modificaron.
- Los sobres topográficos se ajustaron exclusivamente con 1,678 localidades independientes de Fase 13 `TRAIN`.
- La calibración mixta fue la misma de v1: 2,545 KNOWN y 130 UNKNOWN. Fase 23A se abrió solamente después de congelar el umbral.
- La topografía se obtuvo de OpenTopoData `srtm30m`, interpolación bilinear, en el punto y una vecindad cardinal de 90 m. La caché de respuestas tiene SHA-256 `cf1a6abaaee7b2d927b8a5aaee2a7e42e7da94c46068ae1b1ded4acce287905c`.
- El vector por observación es: latitud, longitud, elevación, pendiente, seno/coseno de orientación, relieve local y rugosidad.
- Si no hay coordenadas o perfil válido, no se rechaza: se conserva la decisión visual. Contexto nunca acepta una imagen que el Open Set visual rechazó.

## Cobertura real

| Cohorte | Imágenes | Con topografía válida |
|---|---:|---:|
| Calibración KNOWN | 2,545 | 2,429 |
| Calibración UNKNOWN | 130 | 100 |
| Fase 23A blind | 620 | 429 |

Fase 23A contiene 191 imágenes sin contexto topográfico utilizable; no se les imputó una ubicación ni se las consideró incompatibles.

## Resultado congelado

El umbral de distancia al sobre topográfico, seleccionado en calibración sin Fase 23A, fue `72.52993353344644`. Se habilitaron perfiles para 38 especies del catálogo, con mínimo de 10 localidades TRAIN por especie.

| Evaluación | FAR | UDR | Falsos aceptados |
|---|---:|---:|---:|
| Visual congelado, Fase 23A completa | 36.94% | 63.06% | 229 / 620 |
| Visual + topografía, Fase 23A completa | **36.77%** | **63.23%** | **228 / 620** |
| Visual congelado, solo cubierta topográfica | 45.92% | 54.08% | 197 / 429 |
| Visual + topografía, solo cubierta topográfica | **45.69%** | **54.31%** | **196 / 429** |

La calibración no cambió: FAR 4.62%, UDR 95.38%, KAR 44.95% y FRR 55.05%, antes y después de aplicar el perfil. Por ello, la disminución blind es **un único caso**, equivalente a 0.16 puntos porcentuales globales (0.23 puntos en la población cubierta). No es evidencia suficiente para desplegar el gate.

## Interpretación

La hipótesis de que topografía/elevación resolvería materialmente el FAR no se confirma con estos datos. El valor de contexto es adecuado para trazabilidad y para futuros modelos de distribución, pero no corrige el solapamiento visual Open Set actual.

No se puede evaluar KAR, FRR ni AUROC en Fase 23A aislada porque contiene solo UNKNOWN. Por eso la decisión se mantiene en `NO_GO`: FAR sigue muy por encima del objetivo ≤5%.

## Archivos

- `summary.json`: métricas, cobertura, parámetros congelados e invariantes.
- `opentopodata_cache.json`: elevaciones de entrada reproducibles.
- `fase23a_false_accepts_context_frozen.json`: los 228 falsos aceptados, con distancia topográfica y cobertura por fila.

## Siguiente intervención justificada

No endurecer el umbral topográfico contra Fase 23A. Primero ampliar la calibración con UNKNOWN de elevación, relieve y zonas distintas, y añadir una prueba KNOWN independiente con las mismas covariables. Si un futuro gate reduce FAR sin degradar KAR/FRR en esos estratos, se congela y se vuelve a medir Fase 23A. Si no, la siguiente intervención sigue siendo un rejector aprendido o mejora del embedding mediante hard negatives/fine-tuning bajo un protocolo nuevo.
