# GEO-5 (Fase B) — Reporte final

Paquete experimental del catalogo regional completo de Antioquia y evaluacion de si
visual+geo_especie (w_geo=0.9) escala mas alla de las 24 especies evaluadas en GEO-2/GEO-3.

## 0. Gate de reproduccion

AUROC reproducido = 0.5732919408781961, diff = 0.0 vs oficial (0.5732919408781961).
**GATE PASSED.** (`baseline_reproduction_v2.json`, recalculado en esta sesion sin cambios.)

## 1. Numero real de especies en el catalogo regional auditado

**291 especies** (`COLOMBIA_ANURA/ANTIOQUIA/catalog/catalog_v1.csv`, 291 `taxon_id` unicos),
NO ~29. El "29" del manifest desplegado `regional_packages/ANTIOQUIA/v1.0.0/manifest.json`
es un campo `species_present_estimated` que, segun su propio `caveat`, es un subconjunto
ya scrapeado con fotos — el catalogo taxonomico completo (GBIF + iNaturalist, con y sin
fotos) es ~10x mas grande. Ver `GEO5_AUDIT.md` para el desglose completo.

## 2. Especies con embeddings evaluables vs solo presencia geografica

- **33/291 (11.3%)** especies del catalogo de Antioquia tienen centroides de embeddings
  BioCLIP evaluables (cruce por nombre cientifico canonico contra las 41 especies con
  centroides en `evaluation/fase13/embeddings/`; 8 de esas 41 no tienen ocurrencia
  registrada en el catalogo de Antioquia y quedan fuera del alcance regional).
- **21/291 (7.2%)** tienen ademas un set de imagenes KNOWN curado (fase16, usado en GEO2/3/4).
- **258/291 (88.7%)** son presencia geografica pura, sin ningun dato de imagen evaluable.

Ninguna especie sin embeddings fue sustituida por un centroide sintetico; simplemente quedan
fuera de la evaluacion visual (ver `antioquia_experimental_package/exclusions.json`).

## 3. Cobertura del prior geografico ampliado

`prior_zone_taxon_v2_clean.csv` (ya purgado de leakage en FASE12.2) **ya cubria el catalogo
completo**: `set(taxon_id)` del prior == `set(taxon_id)` de `catalog_v1.csv`, ambos con
K_taxa=291. No fue necesario recalcular el smoothing (alpha=2.0, mismo metodo Bayesiano por
zona) porque ya se habia construido sobre las 291 especies, no solo sobre las 24 evaluables.
Esto se re-empaqueta con trazabilidad (species_id) en
`antioquia_experimental_package/prior_zone_species_full.csv` (1164 filas = 291 especies x 4
zonas). Cobertura: **100% (291/291) de las especies del catalogo tienen prior en las 4 zonas.**
109/291 especies tienen <5 registros geograficos validos (prior delgado, cercano al neutral
1/291); 4/291 tienen 0 celdas ocupadas.

## 4. Identificacion cerrada: baseline visual vs visual+geo_especie (w=0.9), sobre 33 especies evaluables

Evaluado sobre las 7475 imagenes KNOWN (24 especies verdad-terreno, de las cuales 21 estan en
el catalogo de Antioquia), rankeando contra las 41 clases candidatas con centroide (33 de
ellas en el catalogo de Antioquia):

| | Top-1 | Top-3 | Top-5 | F1 macro | rank promedio |
|---|---|---|---|---|---|
| A) visual solo | 0.5852 | 0.8140 | 0.8934 | 0.2778 | 2.743 |
| B) visual + geo_especie w=0.9 | 0.4107 | 0.7549 | 0.9045 | 0.2265 | 3.120 |
| Delta B-A | **-0.1744** | -0.0591 | +0.0111 | -0.0513 | +0.377 |

**w_geo=0.9 EMPEORA la identificacion cerrada Top-1 y F1 macro**, en todos los generos y
familias evaluados sin excepcion (`GEO5_performance_by_genus.csv`, `GEO5_performance_by_family.csv`
— ej. Dendrobatidae cae de 0.976 a 0.719, Pristimantis de 0.196 a 0.098, Dendropsophus de 0.403
a 0.155). Esto coincide numericamente (exactamente, hasta 15 decimales) con el resultado
`visual_plus_geo_hierarchical_C_main` de GEO-4 (Top-1=0.4107), porque a w_visual=0.1 el
componente de especie domina la mezcla en ambos experimentos y produce el mismo orden de
ranking por fila. **Esto NO es una reproduccion de GEO-4** (aqui no se usa genero/familia en
el score, solo especie) — es una observacion nueva: incluso el prior de especie puro, con
peso 0.9, es perjudicial para el RANKING cerrado, aunque sea beneficioso para la deteccion
open-set binaria (ver seccion 5). GEO-4's propio experimento con w_geo=0.5 (llamado
`visual_plus_geo_species` alli) SI mejoraba el Top-1 (0.585->0.634) — es decir, el peso
optimo para ranking cerrado (~0.5) es distinto del peso optimo para open-set (0.9). El
encargo pidio explicitamente usar w_geo=0.9 (la estrategia validada en GEO2/3); se reporta
el resultado tal cual, sin forzar una conclusion positiva.

## 5. Open Set: baseline vs visual+geo_especie (w=0.9), sobre el catalogo completo (K=291)

`GEO2_WEIGHT_SWEEP.csv` **ya fue calculado usando el prior de 291 especies** (verificado:
`prior_zone_taxon_v2_clean_manifest.json.K_taxa == 291 == len(catalog_v1)`), es decir el
open-set A/B de GEO-2/GEO-3 ya reflejaba el catalogo completo desde su construccion original,
no solo el subconjunto de 24 especies evaluables. Se referencia (no se recomputa identico):

| | AUROC | IC95% | FAR | FRR | BalAcc |
|---|---|---|---|---|---|
| A) visual solo (w=0.0) | 0.57329 | [0.5408, 0.6055] | 0.9339 | 0.0500 | 0.5080 |
| B) visual+geo w=0.9 | 0.70148 | [0.6728, 0.7302] | 0.7419 | 0.0500 | 0.6040 |
| Delta | **+0.12818** | IC no se solapa | -0.192 | ~0 | +0.096 |

**La mejora de GEO-2 (+0.128 AUROC) SE SOSTIENE al escalar al catalogo completo auditado**,
porque el denominador del prior geografico (K=291) ya era el catalogo completo desde antes de
GEO-5 — lo que escalo en GEO-5 fue la AUDITORIA y trazabilidad del catalogo (291 especies con
species_id, prior extendido re-empaquetado), no el prior en si. Lo que SI queda acotado por
el catalogo completo es la cobertura de EVALUACION: solo 33/291 (11.3%) especies tienen
embeddings para siquiera participar en este numero.

## 6. Errores por genero/familia (analisis, no filtro de score)

Ver tablas completas en `GEO5_performance_by_genus.csv` / `GEO5_performance_by_family.csv` y
matriz de confusion en `GEO5_confusion_matrix.csv` (24 especies verdad x 41 candidatas,
prediccion B=visual+geo w=0.9). Todos los generos evaluados pierden precision con w_geo=0.9
respecto a visual puro; la caida es mas severa en generos con muchas especies simpatricas del
mismo genero en pocas zonas (Pristimantis: 0.196->0.098; Dendropsophus: 0.403->0.155), donde
el prior geografico de zona no discrimina bien entre especies co-ocurrentes del mismo genero
(la resolucion geografica de las 4 zonas es demasiado gruesa para diferenciarlas). Genero/familia
se usaron unicamente para AGRUPAR este analisis, nunca para modificar el ranking o el
combined_score (regla dura respetada).

## 7. Ejemplos formato Merlin

3 ejemplos de `GEO5_merlin_ranking_examples.json` (8 generados en total, seed=42):

- `GEO5_MERLIN_01297`: verdad = *Dendrobates truncatus*, sin coordenada recuperable
  (`zone=null`) -> `geo_compatibility="no_zone_data"` para los 3 candidatos, decision basada
  solo en visual_score (top1 correcto, visual_score=1.0).
- Los demas ejemplos muestran candidato 1/2/3 con `visual_score` (similitud min-max por fila,
  NO probabilidad), `combined_score_w_geo_0_9` (misma formula validada en GEO2/3, tampoco
  probabilidad), `geo_compatibility` categorico (`compatible/less_compatible/incompatible/
  no_zone_data`) y `family`/`genus` como metadata de contexto (nunca usados para ordenar).
- **No se reporta `calibrated_probability`**: no existe una calibracion real (isotonic/Platt
  contra holdout independiente) en ningun experimento de esta fase ni las anteriores — se
  documenta explicitamente su ausencia en cada ejemplo (`score_types_note`) en vez de
  inventar un numero.

## 8. Decision final

**`ANTIOQUIA_EXPERIMENTAL_NEUTRAL`** (mixta, no forzada a positiva):

- **Open-set (deteccion KNOWN vs UNKNOWN)**: la ganancia de GEO-2 (+0.128 AUROC, w_geo=0.9)
  **se sostiene** al catalogo completo auditado — HELPFUL para esta tarea especifica.
- **Identificacion cerrada (ranking de especie)**: el mismo w_geo=0.9 **es perjudicial**
  (Top-1 -0.174, F1 macro -0.051, consistente en todos los generos/familias) — HARMFUL para
  esta tarea especifica con ese peso. Un peso menor (~0.5, ya observado en GEO-4) es mejor
  para ranking, pero re-optimizar el peso por tarea esta fuera del alcance de GEO-5 (el
  encargo fijo w_geo=0.9 explicitamente).
- **Cobertura del catalogo**: la auditoria revela que el catalogo real (291 especies) es
  ~9x mas grande que lo asumido (~29), y que solo 11.3% (33/291) tiene siquiera datos de
  imagen evaluables — esto es informacion de planificacion valiosa (no un fracaso del
  experimento), y limita severamente cuanto de "el catalogo completo" puede realmente
  evaluarse con visual+geo hoy.

No se marca nada como `READY_FOR_DEPLOYMENT`. La recomendacion practica (fuera del alcance
formal de clasificacion pero relevante) es: usar w_geo alto (~0.9) SOLO para el gate binario
open-set, y un w_geo mas bajo (o el ranking visual puro) para presentar el Top-3 de candidatos
al usuario tipo Merlin — no usar el mismo peso para ambas decisiones.

## 9. Artefactos generados (confirmados con ls/lectura real)

```
validation/fase23a_geographic_context/
  scripts/phase_geo5_main.py                         [nuevo]
  antioquia_experimental_package/
    package_manifest.json                            [nuevo]
    catalog_audited.csv            (291 filas)        [nuevo]
    prior_zone_species_full.csv    (1164 filas)       [nuevo]
    coverage_report.json                              [nuevo]
    exclusions.json                                   [nuevo]
    leakage_audit.json                                [nuevo]
    reproducibility_manifest.json                     [nuevo]
  GEO5_AUDIT.md                                       [nuevo]
  GEO5_closed_identification_metrics.json             [nuevo]
  GEO5_confusion_matrix.csv                           [nuevo]
  GEO5_performance_by_genus.csv                       [nuevo]
  GEO5_performance_by_family.csv                      [nuevo]
  GEO5_openset_comparison.json                        [nuevo]
  GEO5_threshold_curve.csv                            [nuevo]
  GEO5_merlin_ranking_examples.json  (8 ejemplos)      [nuevo]
  GEO5_REPORT.md                                      [nuevo, este archivo]
```

No se modifico ningun archivo de produccion, `regional_packages/ANTIOQUIA/v1.0.0/`, ni
GEO2_*/GEO3_*/GEO4_* existentes (solo lectura). `baseline_reproduction_v2.json` y
`reproduced_scores_v2.npz` se regeneraron en esta sesion desde el mismo script existente
(`phase_reproduce_23a.py`) sin cambios de contenido (bit-identicos al valor oficial).
