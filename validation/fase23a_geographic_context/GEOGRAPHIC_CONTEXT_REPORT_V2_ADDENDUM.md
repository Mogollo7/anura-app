# Fase 23A — Geographic Context, Addendum V2 (corrección quirúrgica)

Este addendum corrige dos defectos del experimento anterior
(`GEOGRAPHIC_CONTEXT_REPORT.md`, scripts `phase0_fetch_inat.py` /
`phase1to8_main.py`) sin reconstruir el pipeline completo. Todos los artefactos
nuevos viven en `validation/fase23a_geographic_context/` bajo nombres que no
pisan los scripts anteriores (`scripts/phase_reproduce_23a.py`,
`scripts/phase_clean_prior.py`, `scripts/phase_reevaluate_clean.py`). No se
modificó `validation/fase23a_open_set_automatic/`, `validation/fase16_clean_open_set/`,
embeddings, encoder, ni `COLOMBIA_ANURA/ANTIOQUIA/priors/prior_zone_taxon_v1.csv`.

## 1. Gate de reproducción del scoring oficial de 23A

El script real que generó `method_comparison.csv` (`fase23a_run.py`) no estaba
en el repo — solo quedó referenciado en
`validation/fase23a_open_set_automatic/reproducibility/config.json` como
ejecutado "from scratchpad". Se recuperó desde el scratchpad de la sesión
anterior (`.../856fbf50-.../scratchpad/fase23a_run.py`) y se confirmó que su
lógica es:

- Centroides de 41 especies construidos desde `evaluation/fase13/embeddings/reference_embeddings.npz`
  (Group A, intersección con train) + `train_embeddings.npz` (Group B, el resto). 9 + 32 = 41.
- KNOWN pool = `validation/fase16_clean_open_set/clean_known_embeddings.npz` (7475 imágenes),
  **sin leave-one-out**: los centroides provienen de un conjunto distinto (reference/train),
  no hay contaminación circular.
- UNKNOWN pool = `validation/fase23a_open_set_automatic/embeddings/unknown_embeddings.npz` (620 imágenes).
- Score = distancia euclidiana mínima a los 41 centroides.
- AUROC calculado sobre los 7475 KNOWN + 620 UNKNOWN juntos (`roc_auc_score(y_is_known, -distancia)`).

Este es exactamente el defecto del experimento V1: `phase1to8_main.py` calculaba el score KNOWN
con leave-one-out **sobre el propio `clean_known_embeddings.npz`** en vez de usar centroides de
`reference`/`train`, lo que dio AUROC=0.6181 en vez de 0.5733 (diferencia documentada en su propio
`geographic_prior_manifest.json`, campo `baseline_reproduction_caveat`, gap=0.0448).

**Resultado del gate** (`baseline_reproduction_v2.json`):

| | valor |
|---|---|
| AUROC oficial | 0.5732919408781961 |
| AUROC reproducido | 0.5732919408781961 |
| diferencia absoluta | **0.0** (match exacto) |
| n_known | 7475 (coincide con oficial) |
| n_unknown | 620 (coincide con oficial) |

**GATE PASADO.** Se continuó con los Problemas 2 y 3.

## 2. Prior geográfico limpio (sin contaminación)

Se recalculó `prior_zone_taxon_v1.csv` excluyendo los 1214 `observation_id`
contaminados identificados en `anti_contamination_check.json` (observaciones de
iNaturalist que son fuente del prior Y aparecen en el conjunto evaluado).

- Fuente de registros: `COLOMBIA_ANURA/ANTIOQUIA/occurrences/records_v1.csv` (15081 registros,
  6422 de iNaturalist). Se re-verificó el solapamiento desde cero (no solo la muestra de 20 IDs
  del JSON original): **1214 de 6422 IDs de iNaturalist están contaminados** (coincide exacto con
  el valor previamente reportado).
- Método de suavizado replicado exactamente desde `pipeline_dataset/zonas_finales_y_prior.py`:
  tope de esfuerzo = percentil 90 de n(especie,celda)>0 (recalculado sobre datos purgados: **17**,
  vs 18 en el original — cambia porque el percentil se recalcula sobre menos datos), α elegido por
  máxima log-verosimilitud media con validación leave-one-cell-out dentro de cada zona, misma
  malla `GRID_ALPHA`, K=291 taxones.
- **α seleccionado = 2.0** (idéntico al original, no está en el borde de la malla).
- Geometría de zonas (asignación celda→zona) se **reutilizó tal cual** desde
  `COLOMBIA_ANURA/ANTIOQUIA/zones/cell_zone_map_v1.csv` (congelado, no se recalculó la
  clusterización/fusión de zonas — es independiente de qué registros individuales se cuentan).

**Registros purgados**: 1214 de 15081 (13867 restantes). Top especies afectadas:
*Dendropsophus bogerti* (339), *Pristimantis achatinus* (234), *Dendrobates truncatus* (209),
*Engystomops pustulosus* (137), *Smilisca phaeota* (43), y 5 más con <45 registros excluidos
cada una. Detalle completo en `prior_zone_taxon_v2_clean_manifest.json`.

Artefacto: `validation/fase23a_geographic_context/prior_zone_taxon_v2_clean.csv` (1164 filas =
4 zonas × 291 taxones). El v1 original **no fue modificado**.

## 3. Re-evaluación: scoring oficial + prior limpio

Barrido de pesos w_geo ∈ {0.0, 0.1, 0.2, 0.3, 0.4, 0.5} (visual_weight = 1-w_geo), combinando:
- **visual_score**: el que reproduce 0.57329 (Problema 1), normalizado min-max.
- **geographic_score**: `P(especie_top1 | zona)` desde el prior LIMPIO (Problema 2), también
  normalizado min-max e invertido (`geo_unknownness = 1 - geo_prob_norm`).

Bootstrap: 1000 iteraciones, seed=42, estratificado por individuo (resample con reemplazo de
individuos KNOWN y UNKNOWN por separado), mismo protocolo que el experimento V1.

### Nota importante sobre el umbral (FAR/FRR)

El AUROC no depende del umbral y se reprodujo exacto. Para FAR/FRR sí se necesita un umbral (τ):

- El método oficial calibra τ con el split `CALIBRATION` (192 imágenes, KAR95% quantile) —
  **se replicó esto exactamente para el score visual puro (w=0)** y el resultado es un match
  exacto: **FAR=0.8113, FRR=0.1390** (idénticos a `method_comparison.csv`, columna `euclidean_raw`).
- Para el score combinado (visual+geo) **no existe una extensión directa de esa calibración**,
  porque las imágenes de `CALIBRATION` no tienen coordenadas/observation_id (no se puede calcular
  su `geo_score`). Se usó en su lugar KAR95% del propio pool KNOWN evaluado (misma convención
  documentada como `CALIBRATED_DIAGNOSTIC_KAR95_QUANTILE_KNOWN_ONLY` en
  `fase23a_open_set_automatic/reproducibility/anomalies.json`), aplicada consistentemente en los 6
  pesos del barrido para que sean comparables entre sí. Esto es una limitación explícita, no un error.

### Tabla final

| | AUROC | IC95% AUROC | FAR | FRR |
|---|---|---|---|---|
| **23A oficial** (τ=CALIBRATION-KAR95) | 0.5733 | [0.5426, 0.6041] | 0.8113 | 0.1390 |
| **Geo-clean, visual only (w=0)**, τ=CALIBRATION-KAR95 (comparación directa con oficial) | 0.5733 (idéntico) | [0.5408, 0.6055]* | 0.8113 | 0.1390 |
| **Geo-clean, visual only (w=0)**, τ=KAR95-eval-known | 0.5733 | [0.5408, 0.6055] | 0.9339 | 0.0500 |
| **Geo-clean, best combined (w=0.5)**, τ=KAR95-eval-known | **0.6782** | **[0.6516, 0.7048]** | 0.8903 | 0.0500 |

\* El IC95% del AUROC reportado aquí para el bootstrap propio (0.5408–0.6055) difiere levemente del
IC95% oficial (0.5426–0.6041) porque el resampling estratificado por individuo puede diferir
mínimamente en la definición de "individuo" para KNOWN (aquí `individual_id` del manifest de Fase16;
el original probablemente usó el mismo campo, pero no se pudo verificar el código exacto del
bootstrap oficial, que también estaba solo en scratchpad y no fue recuperado — el AUROC puntual
coincide exacto, la pequeña diferencia de IC es atribuible a semilla/implementación del bootstrap,
no al scoring).

**Delta AUROC (mejor combinado vs. visual solo) = +0.1049** (0.6782 vs 0.5733), IC95% del mejor
combinado [0.6516, 0.7048] **no se solapa** con el IC95% del visual-solo [0.5408, 0.6055] →
diferencia estadísticamente robusta bajo este bootstrap.

**Advertencia sobre el barrido**: el AUROC sigue subiendo monótonamente hasta el borde superior
del barrido solicitado (w_geo=0.5, AUROC=0.6782); no se observó un máximo interior. Esto sugiere
que el punto óptimo real podría estar en w_geo>0.5, fuera del rango 100/0–50/50 pedido. No se
extendió el barrido más allá de 0.5 por seguir estrictamente el protocolo solicitado, pero se deja
documentado para no sobre-interpretar 0.5 como "el mejor peso posible" en términos absolutos.

## 4. Veredicto actualizado

**GEOGRAPHY_HELPFUL.**

Justificación: con el scoring visual oficial reproducido exactamente (gate pasado, diff=0.0) y el
prior geográfico limpio (1214 observaciones contaminadas excluidas, mismo método de suavizado con
α=2.0 re-verificado), agregar la señal geográfica mejora el AUROC de 0.5733 a 0.6782
(+0.105, +18.3% relativo) con intervalos de confianza al 95% que no se solapan entre el mejor
peso combinado y el visual puro. Esto contrasta con el veredicto original
(`GEOGRAPHIC_PRIOR_DIAGNOSTIC` / mejora reportada como no confiable por la doble falla de scoring
+ contaminación): una vez corregidos ambos defectos, la mejora se sostiene y es más grande que la
observada en el experimento V1 con datos contaminados y scoring incorrecto (que había reportado
AUROC≈0.618 con visual-solo, ya inflado por el propio error de scoring).

Limitaciones que quedan abiertas:
- El umbral (τ) para el score combinado no tiene una calibración independiente equivalente a la
  del método oficial (CALIBRATION split no tiene coordenadas) — el FAR/FRR del score combinado usa
  una convención diagnóstica distinta a la oficial, documentada arriba.
- Solo 42.3% de las imágenes UNKNOWN y 37.0% de las KNOWN tienen zona asignada (el resto usa el
  score geográfico neutral 1/K=1/291); la mejora observada probablemente está impulsada
  principalmente por ese subconjunto con zona conocida.
- El barrido se detuvo en w_geo=0.5 por instrucción explícita; el óptimo real puede estar más alto.

## 5. Artefactos nuevos generados (verificados con ls/lectura real)

```
validation/fase23a_geographic_context/
├── scripts/
│   ├── phase_reproduce_23a.py         (Gate Problema 1)
│   ├── phase_clean_prior.py           (Problema 2)
│   └── phase_reevaluate_clean.py      (Problema 3)
├── baseline_reproduction_v2.json      (resultado del gate, PASSED, diff=0.0)
├── reproduced_scores_v2.npz           (scores visuales oficiales persistidos, reuso en Prob. 3)
├── prior_zone_taxon_v2_clean.csv      (prior limpio, 1164 filas)
├── prior_zone_taxon_v2_clean_manifest.json  (metodología, α, registros excluidos)
├── weight_sweep_results_v2_clean.csv  (barrido completo de pesos con IC95%)
├── geo_clean_reevaluation_v2.json     (resultado final: tabla, veredicto, bootstrap)
└── GEOGRAPHIC_CONTEXT_REPORT_V2_ADDENDUM.md  (este documento)
```
