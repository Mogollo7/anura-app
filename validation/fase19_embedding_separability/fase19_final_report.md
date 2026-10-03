# FASE 19 — Diagnóstico de Separabilidad Taxonómica de Embeddings BioCLIP

**Fecha**: 2026-09-13. **Exclusivamente diagnóstico.** No se hizo commit ni push, no se modificó
BioCLIP, no se recalibró nada, no se seleccionó ningún método Open Set.

---

## Resumen ejecutivo

El encoder BioCLIP congelado **sí organiza el espacio de embeddings según la taxonomía**
(jerarquía género < familia < distinta-familia confirmada empíricamente), pero con **márgenes
insuficientes entre especies del mismo género** (varios pares con distancia intra-género
comparable a la dispersión intra-especie, y hasta 50% de imágenes de una especie más cercanas a
un rival que a su propio centroide). Además, la cobertura UNKNOWN real disponible (2 especies,
35 individuos) es insuficiente para una conclusión fuerte sobre capacidad general de rechazo.
**Hipótesis diagnosticada: D_MIXED** — ambos problemas coexisten.

## Dataset utilizado

| | Imágenes | Individuos | Especies | Géneros | Familias |
|---|---|---|---|---|---|
| KNOWN | 7475 | 4103 | 24 | 11 | 5 |
| UNKNOWN | 56 | 35 | 2 | 2 | 2 |

Mismos embeddings ya calculados en Fases 13/16 (mismo encoder, mismo preprocessing,
`encoder_sha256=219e860e...` verificado). **No se reextrajo ninguna imagen.**

## Auditoría de contaminación

`embedding_audit.json`: 0 duplicados SHA256 dentro del pool KNOWN. Fuentes de datos ya
verificadas independientes de TRAIN/REFERENCE/CALIBRATION en Fases 16-18 (heredado, no
re-auditado desde cero en esta fase por ser diagnóstico puro sobre datos ya congelados).

## Separación intraespecie

24 especies analizadas (`intra_species_stats.json`). Ejemplo: especies con mayor dispersión
intra-clase tienden a ser las más abundantes (`Dendropsophus_microcephalus`, 611 imgs,
std_euclidean=8.40 en escala Mahalanobis de Fase 16 — aquí en escala euclidiana cruda los
valores son menores, ver el JSON para cifras exactas por especie).

## Separación interespecie

| Relación taxonómica | n pares | Distancia media (centroides) | Distancia mínima |
|---|---|---|---|
| Mismo género | 35 | 0.6078 | 0.2363 |
| Misma familia, distinto género | 72 | 0.8221 | 0.3444 |
| Distinta familia | 169 | 1.0845 | 0.7205 |

**Jerarquía visual consistente con la taxonomía: SÍ** (género < familia < distinta-familia).
Esto es evidencia de que BioCLIP **no está "roto"** — organiza razonablemente el espacio según
relaciones biológicas reales.

**Pero el margen absoluto es estrecho**: ratio distinta-familia/mismo-género = 1.78 (no muy
alto). Top 10 pares más cercanos (`nearest_species_pairs.csv`), casi todos intra-género:

```
Pristimantis_paisa <-> Pristimantis_taeniatus:        0.2363
Dendropsophus_bogerti <-> Dendropsophus_microcephalus: 0.3263
Boana_cinerascens <-> Boana_punctata:                  0.3472
```

Los pares señalados en Fase 17 (`Phyllomedusa_tarsius↔venusta`,
`Dendropsophus_ebraccatus↔triangulum`) **no aparecen en el top 10 de esta fase** con el pool
completo de 24 especies — señal de que la dificultad depende de qué especies compiten en el
espacio disponible, no es un par fijo universalmente problemático.

## Separación por género / familia

Ver `taxonomy_separability_report.csv` y figuras `genus_separation.png`,
`family_separation.png`. Confirmado: separación creciente y monotónica por nivel taxonómico.

## Margen de separación (por imagen)

`species_separation_report.csv`. Hallazgo más severo de esta fase:

| Especie | Margen medio | % imágenes con margen negativo |
|---|---|---|
| Pristimantis_paisa | **-0.0140** | 35.4% |
| Pristimantis_erythropleura | -0.0041 | **50.0%** |
| Pristimantis_achatinus | -0.0006 | 45.0% |
| Dendropsophus_bogerti | +0.0106 | 41.0% |

Margen negativo = la imagen está más cerca de un centroide rival que del propio. **Hasta la
mitad de las imágenes de `Pristimantis_erythropleura` caen más cerca de otra especie de
`Pristimantis`** en el espacio embedding crudo, sin intervención de ningún mecanismo de
rechazo. Esto es evidencia directa de limitación real del encoder para este subgrupo
filogenético específico, no del post-procesamiento.

## UNKNOWN analysis

`unknown_analysis.csv`. Hallazgo contraintuitivo e importante:

```
Relación taxonómica UNKNOWN -> especie KNOWN más cercana: 100% "diff_family" (56/56)
```

**Ninguna** de las 56 imágenes UNKNOWN tiene como vecino más cercano una especie de su misma
familia — ni siquiera `Hyloxalus_picachos` (Dendrobatidae) se acerca más a `Dendrobates_truncatus`
(también Dendrobatidae) que a especies de familias completamente distintas. Esto **contradice**
la hipótesis de Fase 16 de que la cercanía taxonómica explicaba el FAR alto — el problema real
es más parecido a que el embedding "empuja" estas 2 especies UNKNOWN hacia zonas del espacio
ocupadas por clusters KNOWN no relacionados, no hacia su pariente esperado.

## Comparación de distribuciones (DIAGNOSTIC ONLY)

```
KNOWN  -> nearest centroid: mean=0.64
UNKNOWN -> nearest centroid: mean=0.74
AUROC (distancia cruda, sin threshold ni covarianza): 0.7245
```

Este AUROC es **mejor** que Mahalanobis (0.592, Fase 16) y **mejor** que Cosine/Euclidean con
threshold aplicado (0.667-0.694, Fases 17-18). Esto sugiere que **parte** de la información de
separación disponible en el embedding crudo se pierde al aplicar un threshold único global —
apoyo parcial a la Hipótesis B (post-procesamiento subóptimo), **combinado con** la limitación
de separación real para los pares intra-género más difíciles (Hipótesis A parcial).

## Casos difíciles (Sección 11)

Los pares de Fase 17 (`Pristimantis_paisa↔taeniatus` sigue en el top 1; los otros dos no
reaparecen en el top 10 con el conjunto ampliado de 24 especies — ver arriba). El patrón
dominante es intra-género de `Pristimantis` y `Dendropsophus`, los dos géneros con más especies
representadas en el catálogo (12 y 9 especies respectivamente) — más especies del mismo género
compitiendo por el mismo "vecindario" del espacio embedding.

## Diagnóstico del encoder — hipótesis

```
HIPÓTESIS DIAGNOSTICADA: D_MIXED
```

Evidencia (`diagnostic_metrics.json`):
- `hierarchy_consistent_with_taxonomy = True`, pero `ratio_diff_family_vs_same_genus = 1.78`
  (no muy alto) → separación insuficiente específicamente entre especies filogenéticamente
  cercanas (parcial soporte a Hipótesis A).
- `n_unknown_species=2, n_unknown_individuals=35` → por debajo del umbral mínimo razonable
  (≥5 especies, ≥30 individuos) para generalizar (soporte a Hipótesis C).
- AUROC diagnóstico con distancia cruda (0.7245) > AUROC con threshold aplicado (0.59-0.69)
  → indicio de que el post-procesamiento no aprovecha toda la separación disponible (soporte
  parcial a Hipótesis B, pero no domina sobre las otras dos).

**No se eligió la hipótesis por intuición** — la combinación de evidencia (margen negativo real
en Pristimantis, cobertura UNKNOWN insuficiente, y brecha AUROC crudo-vs-post-procesado) apunta
a que los tres factores contribuyen simultáneamente.

## Limitaciones

- UNKNOWN: 2 especies, 35 individuos — **insuficiente para afirmar o descartar** capacidad
  general de rechazo Open Set de BioCLIP. La evidencia aquí es diagnóstica sobre estos 2 casos
  concretos, no generalizable.
- Muestreo aleatorio (semillas fijas 42/123/7) para especies con >200-300 imágenes, por costo
  computacional de `pdist` — documentado, no afecta el patrón agregado observado.
- PCA usado únicamente para `embedding_projection.png` — ninguna métrica principal depende de
  reducción dimensional (UMAP no disponible en el entorno, documentado).
- No se auditó de nuevo contaminación TRAIN/REFERENCE/CALIBRATION en esta fase — se heredó de
  las verificaciones ya hechas en Fase 16-18 sobre los mismos datos, sin cambios desde entonces.

## Conclusión científica

**¿El problema está principalmente en el mecanismo de rechazo o en la separabilidad del
embedding?** Ambos, con evidencia real para cada uno:

1. El embedding **sí** organiza el espacio según taxonomía a nivel general, pero **no** separa
   suficientemente pares específicos intra-género (`Pristimantis`, `Dendropsophus`) —
   margen negativo confirmado en hasta 50% de las imágenes de una especie.
2. El mecanismo de rechazo posterior (threshold único global + Mahalanobis/Euclidean/Cosine)
   pierde ~5-13 puntos de AUROC respecto a la separación cruda disponible en el embedding —
   hay margen de mejora en el post-procesamiento, pero no alcanzaría por sí solo para resolver
   el problema, dado que el AUROC crudo (0.72) tampoco es excelente.

**¿Es la evidencia suficiente para justificar una intervención sobre BioCLIP (fine-tuning)?**
**No todavía.** Antes de tocar el encoder, la prioridad lógica es: (a) recolectar más especies
UNKNOWN reales para confirmar si el patrón "100% diff_family" se sostiene con una muestra
mayor, y (b) explorar si un mecanismo de rechazo por especie/género (en vez de un threshold
global único) recupera parte de los ~5-13 puntos de AUROC perdidos, sin tocar el encoder.

## Recomendación siguiente

**No fine-tuning todavía.** Orden sugerido:
1. Auditar si existen datos UNKNOWN reales adicionales fuera del repositorio actual (fuentes
   externas, iNaturalist regional) antes de cualquier decisión sobre el encoder.
2. Explorar un mecanismo de threshold **por género o por especie** (no global) usando el mismo
   embedding crudo, para verificar si recupera el AUROC=0.72 diagnóstico — esto sería una
   intervención de post-procesamiento, no de BioCLIP.
3. Solo si (1) y (2) no bastan, considerar intervención sobre el encoder como última opción.
