# Primera evaluación — Umbral "rana vs. no-rana" (far-OOD)

> Nota puente. Código y artefactos viven en el repositorio
> (`evaluation/no_rana_v1/`), no en el vault. Esta nota enlaza ambos mundos.

**Repositorio**: [anura-app](https://github.com/Mogollo7/anura-app) — `evaluation/no_rana_v1/`
**Status**: `EXPLORATORY` (no `READY_FOR_PRODUCTION`) — n pequeño, un solo punto de referencia near-OOD
**Fecha**: 2026-09-22

## De dónde sale esto

[[05_OPEN_SET/INDEX|05_OPEN_SET/INDEX]] señala como brecha abierta que Fase 13 nunca separó
**near-OOD** (otro anuro no catalogado) de **far-OOD** (objeto/organismo que no es un anuro
en absoluto) — ver también la tabla de los 4 casos de "desconocido" en
[[02 Metodología/Open-Set Recognition|Open-Set Recognition]]. Esta nota documenta el primer
intento de cerrar esa brecha, específicamente para el caso far-OOD "no hay ningún anuro en
la foto", como filtro previo a la clasificación de especie — no como reemplazo del mecanismo
Open Set existente.

## Pregunta que responde

¿El mismo mecanismo Mahalanobis (`min_mahalanobis` + centroides + `precision_matrix`
compartida, congelado en Fase 13/[[05_OPEN_SET/FASE_13_CALIBRACION_INDEPENDIENTE|Fase 13]])
separa limpiamente "no es un anuro" de "es un anuro pero de especie no catalogada", o ambos
casos caen igual de lejos de los centroides y se necesitaría un detector aparte?

## Método

- **Encoder**: mismo BioCLIP v1 congelado (`bioclip_anura_v1`, mismo sha256 que el catálogo).
- **Precisión y centroides**: `covariance/v1.1.0_CLEAN/covariance_matrix.npz` +
  centroides de las 41 especies reconstruidos desde
  `evaluation/fase13/embeddings/{reference,train}_embeddings.npz` — el mismo código que
  `tools/catalog/run_open_set_evaluation.py::min_mahalanobis`, no una reimplementación.
- **Negativos (far-OOD)**: 30 imágenes genéricas descargadas de Wikimedia Commons (dominio
  público/CC) — perro, gato, planta, insectos, ave, objetos domésticos, paisajes, otra
  fauna (tortuga, lagartija, caballo, oveja, elefante). Script:
  `evaluation/no_rana_v1/descargar_negativos.py`, imágenes en `evaluation/no_rana_v1/negativos/`.
- **Referencia near-OOD**: los únicos scores de "rana real pero fuera de catálogo" con
  datos ya calculados — *Hyloxalus picachos* (n=15) de `FASE13_FINAL_METRICS.json`.
- **Umbral de referencia**: τ=39.354 (congelado, KAR95%, `threshold/v1.0.0`).
- Script completo: `evaluation/no_rana_v1/evaluar_umbral_no_rana.py`.
  Resultado crudo: `evaluation/no_rana_v1/resultado_umbral_no_rana.json`.

## Resultado

| Grupo | n | media | min | max | rechazo con τ=39.35 |
| --- | --- | --- | --- | --- | --- |
| No-rana (far-OOD) | 30 | 65.27 | **49.99** | 74.10 | **100 %** |
| Rana desconocida real (near-OOD, *H. picachos*) | 15 | 32.64 | 27.22 | **46.65** | 13.3 % |

> [!important] Hallazgo
> Hay un **hueco limpio** entre ambos grupos: el score mínimo de no-rana (49.99) queda por
> encima del score máximo de rana-desconocida-real (46.65). Contradice la hipótesis inicial
> de que ambos casos se confundirían por estar "lejos de los centroides" por igual — en la
> práctica, BioCLIP separa bastante bien "no es un anuro" de "es un anuro nuevo".

## Consecuencia práctica

El τ=39.35 ya congelado **rechaza el 100 % de las negativas de esta prueba** sin ningún
cambio — el mecanismo Open Set existente ya actúa como filtro no-rana de facto (ambos casos
caen en `REJECT`). Para dar un mensaje distinto al usuario ("no detectamos un anfibio" vs.
"especie no registrada, pero es un Anura"), se introdujo un **segundo umbral provisional**
`NotAnuroTau = 48.0` (a medio camino entre 46.65 y 49.99, con margen hacia el lado no-rana
para minimizar falsos "no es rana" sobre especies nuevas reales) en
`AnuraIdentifier.kt` (`anura-android/app/src/main/java/me/juanlabs/anura/core/inference/`),
con un nuevo caso `IdentificationOutcome.NotAnuro` propagado hasta `AnalyzingScreen` y
`AnuraNavHost` (mensaje `identification_not_anuro` en `strings.xml`). Pendiente de probar en
dispositivo real — el teléfono de prueba está desconectado al momento de esta nota.

## Limitaciones (no se me escapan, quedan explícitas)

- **n=30 negativos genéricos**, no adversariales ni "cercanos al dominio" (p. ej. salamandras
  o sapos, que la tabla de 4 casos de Open-Set Recognition trata como su propia categoría
  "otro anfibio" — no se probaron aquí).
- **Un solo punto de referencia near-OOD** (una especie, 15 fotos) — no hay evidencia de que
  el hueco se mantenga con más especies desconocidas o con anfibios no-anuro reales.
- El umbral `NotAnuroTau=48.0` es una elección manual sobre esta muestra pequeña, **no una
  calibración formal** (no sigue el procedimiento de validación/test separado que exige
  [[02 Metodología/Open-Set Recognition|Open-Set Recognition §3]]).
- No integra el enfoque de exposición a datos externos (*outlier exposure*) ya planificado en
  la metodología — esto es un umbral post-hoc sobre el mismo espacio de embeddings, no un
  reentrenamiento.

## Qué falta por decidir o medir

- [ ] Ampliar negativos con otros anfibios no-anuro (salamandra, cecilia) — el caso que la
  tabla de 4 casos distingue explícitamente y que esta prueba no cubrió.
- [ ] Sumar más especies near-OOD si aparecen en validaciones futuras (fase16–23a tienen más
  casos open-set en `validation/`).
- [ ] Calibrar `NotAnuroTau` con el procedimiento formal (validación/test separados) en vez del
  punto medio elegido a mano.
- [ ] Validar en el teléfono de prueba (pendiente — dispositivo desconectado al momento de
  esta nota).

## Fuentes

[[02 Metodología/Open-Set Recognition|Open-Set Recognition]] ·
[[05_OPEN_SET/FASE_13_CALIBRACION_INDEPENDIENTE|Fase 13 — Calibración Independiente]] ·
[[05_OPEN_SET/INDEX|05_OPEN_SET/INDEX]]
