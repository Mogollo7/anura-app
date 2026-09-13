# Fase 5 — Métricas y discriminación Open Set

**Estado:** `FASE_5_COMPLETE`

## Alcance y fuentes

- KNOWN: 766 imágenes de Fase 3, pertenecientes a 41 especies visuales.
- UNKNOWN: 56 imágenes de Fase 4, de 2 especies no visuales.
- Fuentes: `closed_set_results.json`, `closed_set_metrics.json`, `open_set_results.json`, `open_set_metrics.json`.
- No se volvió a ejecutar inferencia.

## Validación

F3=766, F4=56, UNKNOWN=56, UNKNOWN species=2, leakage=0. No hubo duplicados, nulos ni valores fuera de rango en los scores disponibles.

## Scores disponibles

Se analizaron `top1_probability`, `top2_probability`, `top3_probability` y `margin_top1_top2`. No se calcularon entropía ni distancia porque los artefactos no contienen probabilidades completas ni embeddings/distancias.

## AUROC

- top1_probability: **0.585812** (KNOWN es la clase positiva; score alto = más KNOWN).
- top2_probability: **0.488134** (KNOWN es la clase positiva; score alto = más KNOWN).
- top3_probability: **0.539771** (KNOWN es la clase positiva; score alto = más KNOWN).
- margin_top1_top2: **0.584647** (KNOWN es la clase positiva; score alto = más KNOWN).

## FPR @ 95% TPR

- Threshold analítico: **0.098173**.
- TPR: **0.954308**; FPR/FAR: **0.892857**.
- KNOWN aceptados: 731/766.
- UNKNOWN aceptados: 50/56.
- Este threshold es retrospectivo y no se aplicó al sistema.

## FAR en la cuadrícula analítica

- FAR más cercana a 5%: threshold **0.35**, FAR **7.14%**, Known Acceptance **23.11%**.
- FAR más cercana a 1%: threshold **0.40**, FAR **1.79%**, Known Acceptance **17.89%**.
- Son puntos de análisis retrospectivo; no son thresholds productivos.

## OSCR

- Área OSCR: **0.396401**.
- Definición: eje X = FPR de UNKNOWN; eje Y = CCR de KNOWN correctamente clasificados; barrido por `top1_probability` descendente.

## Calibración

- ECE KNOWN: **0.303077**, 10 bins uniformes en [0,1].
- Brier multiclase KNOWN: **NOT COMPUTABLE**; no están disponibles las probabilidades completas.

## UNKNOWN de alta confianza

- `top1_probability >= 0.90`: 0.
- `top1_probability >= 0.80`: 0.
- `top1_probability >= 0.70`: 0.
Estos casos se denominan `HIGH_CONFIDENCE_OPEN_SET_PREDICTION`; no son errores de threshold oficial.

## UNKNOWN por especie

- **Hyloxalus_picachos**: `Rheobates_palmatus`=5, `Pristimantis_achatinus`=4, `Craugastor_raniformis`=4, `Dendropsophus_microcephalus`=1, `Dendropsophus_columbianus`=1
- **Sachatamia_electrops**: `Boana_cinerascens`=18, `Hyloscirtus_palmeri`=11, `Dendropsophus_mathiassoni`=8, `Dendropsophus_molitor`=2, `Dendropsophus_bogerti`=1, `Scinax_ruber`=1

## Interpretación

La mejor señal univariada por AUROC fue `top1_probability`. Esto indica separación estadística en este experimento, pero no constituye un detector Open Set ni autoriza un threshold productivo.
Con TPR aproximadamente 95% de KNOWN, la FAR observada fue 89.29%.

El conjunto Open Set actual contiene únicamente 56 imágenes de 2 especies UNKNOWN. Por tanto, los resultados son una evaluación piloto y no permiten afirmar generalización a todas las especies no visuales de Colombia.

No se modificó el modelo, no se entrenó, no se aplicó threshold, no se implementó rechazo, no se utilizó k-NN ni prior geográfico.
