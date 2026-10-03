# FASE 20 — Open Set Robustness / Cross-Individual: Reporte Final

**Fecha**: 2026-09-13. **Puramente diagnostico. No se hizo commit ni push. No se reentreno ni recalibro nada oficial.**

Todos los artefactos de esta fase estan bajo `validation/fase20_open_set_robustness/`. Ningun
archivo de `evaluation/fase13/`, `validation/fase16_clean_open_set/`, `validation/fase19_embedding_separability/`,
`visual_catalog/v1.0.0/`, `covariance/`, `threshold/` ni el checkpoint BioCLIP fue modificado.

---

## 1. Unidad de independencia (Tarea 1)

Fuentes inventariadas: `evaluation/fase13/embeddings/{reference,train}_embeddings.npz` (sin
`individual_id`), `validation/fase16_clean_open_set/clean_known_manifest.json` (KNOWN blind, con
`individual_id` = id de observacion iNaturalist), `evaluation/open_set_v1/knn/knn_open_set_results.json`
(F3/F4, `individual_id` reconstruido via regex `col_obs_<id>_photo` sobre el path, solo disponible
para F4/UNKNOWN).

| Pool | n_images | n_individuals (=observaciones) | n_species | n_genera | n_families |
|---|---|---|---|---|---|
| KNOWN blind (clean, Fase16 reutilizado) | 7475 | 4103 | 24 | 11 | 5 |
| UNKNOWN (F4) | 56 | 35 | 2 | 2 | 2 |
| REFERENCE (centroides Grupo A) | 798 | N/D (sin individual_id) | 9 | — | — |
| TRAIN (centroides Grupo B) | 4724 | N/D (sin individual_id) | 32 | — | — |

**Limitacion heredada de Fase 12.2, no resuelta aqui**: `individual_id` = observation_id de
iNaturalist, no un identificador biologico verificado de individuo fisico. Independencia real de
individuos entre observaciones sigue **NOT_FORMALLY_VERIFIABLE**. REFERENCE/TRAIN no tienen
`individual_id` en sus `.npz`, por lo que la independencia cross-individual entre ellos y el KNOWN
blind se apoya en la verificacion indirecta ya hecha en Fase 16 (0 imagenes del KNOWN limpio
comparten `individual_id` con TRAIN, ver `clean_known_rejected_by_individual.json`, longitud 0).

## 2. KNOWN cross-individual (Tarea 2)

`known_cross_individual_manifest.json` reutiliza integramente el KNOWN limpio de Fase 16 (7475
imagenes / 4103 individuos / 24 especies), que por construccion ya excluye por SHA256 toda imagen
usada en TRAIN/REFERENCE/CALIBRATION/F3/F4 y fue verificado sin overlap de `individual_id` con
TRAIN. **17 de 41 especies del catalogo no tienen ningun KNOWN cross-individual disponible** (ya
consumieron el 100% de sus datos reales en splits previos) — no se fabrico ninguna imagen para
cubrir ese hueco.

## 3. Diversidad UNKNOWN (Tarea 3)

Se busco en todo el repositorio (evaluation/, validation/, data cleaned/) cualquier registro
UNKNOWN adicional a F3/F4. **No se encontro ninguno.** `unknown_taxonomic_strata_manifest.json`:
2 especies reales (`Hyloxalus_picachos`, `Sachatamia_electrops`), 56 imagenes, 35 individuos,
estratificadas como `SAME_FAMILY_DIFFERENT_GENUS` y `DIFFERENT_FAMILY` respecto al catalogo KNOWN
(ninguna UNKNOWN cae en `SAME_GENUS`). **Diversidad UNKNOWN: INSUFICIENTE.** No se fabrico
diversidad adicional.

## 4. Embedding crudo (Tarea 4)

Encoder verificado por SHA256 (`219e860e6f...446b2a`), identico al usado en Fases 13/16/19.
Dimension confirmada = 512 en las 4 fuentes cargadas. `normalization=L2`,
`preprocessing=open_clip...bioclip`. **No se reextrajo ningun embedding** — se reutilizaron
integramente los `.npz` existentes (`integrity_manifest.json`).

## 5. Separabilidad del embedding crudo (Tarea 5)

Usando distancia euclidiana minima al centroide oficial mas cercano (centroides fijos,
REFERENCE+TRAIN, 41/41 especies del release — 9 Grupo A + 32 Grupo B):

| | n | mean | median | std | p10 | p25 | p50 | p75 | p90 | p95 | p99 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| KNOWN | 7475 | 0.649 | 0.645 | 0.158 | 0.439 | 0.530 | 0.645 | 0.761 | 0.857 | 0.913 | 1.033 |
| UNKNOWN | 56 | 0.743 | 0.724 | 0.093 | 0.622 | 0.689 | 0.724 | 0.815 | 0.874 | 0.897 | 0.917 |

**AUROC = 0.6936, PR-AUC = 0.0115** (ver `distance_comparison.csv`, `diagnostic_metrics.json`).

Nota metodologica importante: Fase 19 reporto AUROC=0.7245 para una comparacion similar, pero
usando centroides calculados sobre el propio KNOWN limpio (no sobre REFERENCE+TRAIN). Aqui se
fijaron los centroides OFICIALES en todas las etapas para poder aislar el efecto de
metrica/normalizacion en la Tarea 7. La diferencia (0.7245 vs 0.6936) es metodologica y esperada,
no una contradiccion.

## 6. Comparacion de metricas de distancia (Tarea 6)

Ver `distance_comparison.csv`. `diagnostic_threshold` = Youden-J optimo calculado **solo para
reporte diagnostico**, nunca escrito ni usado para reemplazar el threshold oficial congelado.

| Metrica | AUROC | PR-AUC | balanced_acc @ threshold diagnostico |
|---|---|---|---|
| cosine_similarity | 0.6892 | 0.0112 | 0.7005 |
| cosine_distance | 0.6892 | 0.0112 | 0.7004 |
| euclidean | 0.6936 | 0.0115 | 0.7028 |
| mahalanobis (covarianza compartida) | 0.5920 | 0.0082 | 0.6716 (a su propio optimo diagnostico) |
| mahalanobis @ **threshold oficial congelado** (39.354, `threshold/v1.1.0_CLEAN`) | 0.5920 | 0.0082 | **0.4566 (peor que azar)** |

## 7. Diagnostico de la perdida 0.72→0.59 (Tarea 7)

`stagewise_auroc.csv`, centroides fijos en todas las etapas:

| Etapa | AUROC |
|---|---|
| 1. Embedding crudo L2-normalizado, euclidiana al centroide | 0.6936 |
| 2. Centrado (resta de media global KNOWN) | 0.6936 (identico — centrar no cambia distancias relativas cuando se resta la misma constante a embeddings y centroides) |
| 3. Distancia coseno al centroide (solo angulo) | 0.6892 |
| 4. Mahalanobis con covarianza compartida (Ledoit-Wolf, `covariance/v1.1.0_CLEAN`) | 0.5920 |
| 5. Pipeline oficial completo (Fase 16, reportado) | 0.5928 |

**El AUROC reproducido en la etapa 4 (0.5920) coincide con el valor oficial reportado en Fase 16
(0.5928)** dentro de un margen atribuible a diferencias de precision numerica/version de
covarianza — confirma que el pipeline se reprodujo correctamente. **La perdida de senal ocurre
mayoritariamente en la etapa 3→4: al introducir el whitening de covarianza compartida
(Mahalanobis), el AUROC cae de 0.69 a 0.59.** El centrado no aporta ni resta nada por si solo, y
el paso de coseno vs euclidiana es marginal (0.6936→0.6892). El threshold en si no reduce mas el
AUROC (es una decision binaria, no cambia el ranking) pero **si convierte una separacion ya
debil en un resultado peor que el azar en accuracy balanceada** (0.4566), porque el threshold
congelado esta calibrado en una region del espacio de distancias Mahalanobis donde FAR es muy alto
(91%).

**Conclusion permitida aplicable: POSTPROCESSING_DEGRADES_SEPARABILITY** (la etapa de
whitening/Mahalanobis es la principal responsable de la caida, no la extraccion embebida ni el
centrado).

## 8. Cross-individual species test (Tarea 8)

`species_margin.csv`: 24 especies con >=3 individuos evaluadas con rotacion de individuos (k=5
folds, centroide reconstruido excluyendo los individuos de test, evaluado contra los centroides
oficiales del resto de especies).

- **Top-1 accuracy media = 0.535, negative-margin rate media = 0.465** — es decir, en promedio casi
  la mitad de las imagenes de test quedan mas cerca de un centroide de especie incorrecta que del
  propio, incluso cuando el individuo de test nunca fue visto al construir el centroide de su
  propia especie.
- Rango observado: desde especies con buen comportamiento (`Boana_boans` top1=0.833) hasta
  especies con generalizacion pobre entre individuos (`Boana_platanera` top1=0.444,
  negative-margin=0.556).
- **Conclusion permitida aplicable: CROSS_INDIVIDUAL_GENERALIZATION_INSUFFICIENT** para el
  conjunto agregado (top1 medio <0.6, negative-margin medio >0.4), aunque con heterogeneidad
  fuerte entre especies — no es un fallo uniforme.

## 9. Margen taxonomico (Tarea 9)

Distancia euclidiana entre centroides oficiales, agrupada por relacion taxonomica
(`taxonomic_pair_margin_stats.json`):

| Relacion | n pares | mean dist | median |
|---|---|---|---|
| same_genus | 123 | 0.541 | 0.556 |
| same_family_diff_genus | 178 | 0.927 | 0.929 |
| diff_family | 519 | 1.149 | 1.168 |

La jerarquia es consistente con la taxonomia (genero < familia < diff-familia), igual que en
Fase 19. PCA no se uso como evidencia estadistica (no se genero aqui; Fase 19 ya cubrio la
proyeccion visual).

## 10. UNKNOWN robustness (Tarea 10)

`unknown_analysis.csv` (56 filas, una por imagen UNKNOWN): especie/familia real, especie/genero/
familia KNOWN mas cercano por Mahalanobis, relacion taxonomica, distancia, threshold oficial,
decision.

**El FAR alto SI esta concentrado, pero en ambas especies UNKNOWN disponibles, no en una sola:**

| Especie UNKNOWN | Aceptadas erroneamente / total | FAR especifico |
|---|---|---|
| Hyloxalus_picachos | 13/15 | 86.7% |
| Sachatamia_electrops | 38/41 | 92.7% |

No hay una especie "responsable" del FAR global (93.9% reportado en Fase 16) — ambas contribuyen
de forma similar y consistentemente alta.

## 11. Threshold curve (Tarea 11, diagnostico)

`threshold_curve.csv` (302 puntos, sobre scores Mahalanobis). El threshold oficial congelado
(39.354) esta **fuera** de la region de mejor Youden-J observada en este KNOWN/UNKNOWN blind
(mejor Youden-J diagnostico = 0.340 en tau≈27.12, vs Youden-J = -0.087 en el threshold oficial).
Esto es **evidencia diagnostica**, no una recomendacion de recalibrar — el threshold oficial fue
calibrado en Fase 13/16 sobre CALIBRATION (192 imgs), un conjunto distinto de este KNOWN/UNKNOWN
blind, por lo que cierto grado de desajuste es esperable; no se recalibra aqui.

---

## Limitaciones explicitas (declaradas, no aproximadas)

1. **UNKNOWN**: 2 especies reales, 35 individuos, 56 imagenes en todo el repositorio. Insuficiente
   para cualquier conclusion general sobre "capacidad de rechazo Open Set frente a especies
   desconocidas arbitrarias". Las conclusiones sobre UNKNOWN aplican solo a estos 2 casos.
2. **Independencia biologica de individuo**: `individual_id` = observation_id de iNaturalist, no
   verificado biologicamente como "un unico animal fisico". NOT_FORMALLY_VERIFIABLE, heredado de
   Fase 12.2/16, no resuelto en esta fase.
3. **REFERENCE/TRAIN sin individual_id**: la independencia cross-individual entre esos pools y el
   KNOWN blind depende de la verificacion indirecta de Fase 16 (0 overlaps), no de una
   comprobacion directa por `individual_id` en esta fase.
4. **Cross-individual species test**: 17/41 especies del catalogo no tienen suficientes
   individuos KNOWN limpios para participar (quedan fuera de `species_margin.csv`).
5. **Centrado (etapa 2)**: la version de "centrado" evaluada aqui es diagnostica y simplificada
   (resta de la media del propio KNOWN pool); no reproduce necesariamente cualquier centrado
   interno no documentado del pipeline oficial de Mahalanobis (Ledoit-Wolf ya centra
   internamente). Se declara como aproximacion, no como replica exacta de una etapa interna del
   codigo oficial.

---

# FASE 20 STATUS

```
Cross-individual KNOWN:
PARTIAL — 4103 individuos / 24 de 41 especies cubiertas (17 especies sin remanente
real disponible). Top-1 cross-individual medio = 53.5%, negative-margin medio = 46.5%.

UNKNOWN diversity:
INSUFFICIENT — 2 especies reales, 35 individuos, 56 imagenes (sin datos adicionales
en el repositorio; no fabricados).

Raw embedding separability AUROC:
0.6936 (euclidiana, centroides oficiales fijos) / 0.7245 (referencia Fase19, centroides
distintos — ver nota metodologica seccion 5)

Post-processing separability AUROC:
0.5920 (Mahalanobis + covarianza compartida, reproduce el 0.5928 oficial de Fase16)

Signal lost at:
Etapa Mahalanobis / whitening de covarianza compartida (0.69 -> 0.59). El centrado y el
cambio euclidiana->coseno no explican la caida por si solos.

Best diagnostic distance:
Euclidiana cruda al centroide (AUROC=0.6936, balanced_accuracy=0.70 a su propio umbral
diagnostico) — supera a Mahalanobis en este blind test. NO se recomienda reemplazar el
metodo oficial sin una recalibracion formal fuera del alcance de esta fase.

Global threshold:
GLOBAL_THRESHOLD_NOT_SUPPORTED — el threshold oficial congelado (39.354) produce
balanced_accuracy=0.4566 (peor que azar) en este blind test independiente.

BioCLIP:
FROZEN

Fine-tuning:
NOT PERFORMED

Open Set:
NOT SUPPORTED — con los datos disponibles (AUROC post-pipeline=0.59, threshold oficial
peor que azar, UNKNOWN cubriendo solo 2 especies), no hay evidencia de que el mecanismo
Open Set actual discrimine KNOWN/UNKNOWN de forma confiable. No se declara "validado".

Main scientific finding:
El encoder BioCLIP SI organiza el espacio segun taxonomia (jerarquia genero<familia<
diff-familia consistente, BIOCLIP_SIGNAL_PRESENT) y la separacion cruda KNOWN/UNKNOWN
es moderada (AUROC~0.69-0.72 segun centroides usados) pero el pipeline de post-procesamiento
(Mahalanobis + covarianza compartida + threshold congelado) degrada esa senal hasta
peor-que-azar (POSTPROCESSING_DEGRADES_SEPARABILITY). Ademas, la generalizacion
cross-individual dentro de especies KNOWN es heterogenea e insuficiente en promedio
(CROSS_INDIVIDUAL_GENERALIZATION_INSUFFICIENT), y la cobertura UNKNOWN real sigue siendo
demasiado pequena para cualquier conclusion fuerte (UNKNOWN_COVERAGE_INSUFFICIENT).

Next recommended experiment:
Recolectar UNKNOWN real adicional (mas especies fuera del catalogo, no fabricado) antes de
cualquier recalibracion; en paralelo, evaluar formalmente (fuera de este diagnostico) si un
metodo de distancia mas simple (euclidiana o coseno sin whitening) generaliza mejor que
Mahalanobis en un split de calibracion independiente, dado que aqui supero a Mahalanobis en
todas las comparaciones. No se recomienda fine-tuning como siguiente paso automatico.
```

## Entregables

- `known_cross_individual_manifest.json`
- `unknown_taxonomic_strata_manifest.json`
- `distance_comparison.csv`
- `stagewise_auroc.csv`
- `threshold_curve.csv`
- `species_margin.csv`
- `taxonomic_pair_margin_stats.json` (complemento de margen taxonomico par-a-par, Tarea 9)
- `unknown_analysis.csv`
- `diagnostic_metrics.json`
- `integrity_manifest.json`
- `scripts/run_fase20_analysis.py` (script reproducible completo)
- `FASE20_REPORT.md` (este documento)
