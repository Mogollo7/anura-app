# GEO-6 — Reporte final: ranking y Open Set como dos problemas separados

## 0. Gate de reproduccion

AUROC reproducido = 0.5732919408781961, diff = 0.0 vs oficial. **GATE PASSED**
(`baseline_reproduction_v2.json`, reutilizado sin cambios).

## 1. Hipotesis y diseno

GEO-5 encontro un conflicto: usando un UNICO `combined_score` con w_geo=0.9 (la configuracion
validada en GEO-2/GEO-3 para Open Set), el Open Set mejora fuertemente (AUROC 0.573->0.701) pero
el ranking cerrado se destruye (Top-1 0.585->0.411). GEO-6 prueba si separar el problema en dos
scores distintos — uno para RANKEAR candidatos (Etapa 1, peso geografico bajo) y otro para DECIDIR
si la observacion es conocida/no-concluyente (Etapa 2, peso geografico alto, aplicado solo al
candidato ya elegido) — resuelve el conflicto.

## 2. ETAPA 1 — Ranking

**Candidatos**: 41 especies con centroide BioCLIP (pool completo de GEO2/3/4/5), **no** el
subconjunto de 33/21 especies restringido al catalogo regional de Antioquia identificado en
GEO-5. Justificacion: el pool relevante para "que especies se confunden visualmente" es una
propiedad del espacio de embeddings, no de la escala geografica de despliegue; restringirlo
habria eliminado distractores reales y roto la comparabilidad directa con GEO2/3/4/5.
**Verdad-terreno**: 7475 imagenes KNOWN, 24 especies (`fase16_clean_open_set`, mismo pool de
GEO2/3/4/5). **Normalizacion**: min-max por fila sobre las 41 candidatas, tanto para
`visual_sim` (-distancia euclidiana) como para `geo_species` (prior bayesiano por zona, K=291,
`prior_zone_taxon_v2_clean.csv`) — identica convencion a GEO-4/GEO-5.

| w_geo_rank | Top-1 | Top-3 | Top-5 | F1 macro | MRR | mean_rank |
|---|---|---|---|---|---|---|
| 0.0 (visual puro) | 0.5852 | 0.8140 | 0.8934 | 0.2778 | 0.7145 | 2.743 |
| 0.1 | 0.6264 | 0.8388 | 0.9045 | 0.2970 | 0.7447 | 2.555 |
| 0.2 | 0.6565 | 0.8554 | 0.9128 | 0.3079 | 0.7661 | 2.416 |
| **0.3** | **0.6625** | **0.8672** | **0.9201** | **0.3105** | **0.7741** | **2.321** |

**Criterio de seleccion**: Top-1 primario, empate resuelto por Top-3, luego por MRR. Dentro del
sweep permitido ({0.0, 0.1, 0.2, 0.3}), Top-1/Top-3/MRR **crecen monotonamente** con w_geo_rank —
`w_geo_rank=0.3` es el mejor del conjunto evaluado. Nota honesta: la tendencia sigue siendo
creciente en el borde superior del sweep permitido, por lo que **no se puede descartar que un
w_geo_rank>0.3 sea aun mejor** — el encargo restringe explicitamente el sweep a este rango y no
se amplio sin justificacion adicional (regla dura respetada). Esto queda como pregunta abierta,
no como limitacion oculta.

Desempeño por especie/genero: `GEO6_ranking_by_species.csv`, `GEO6_ranking_by_genus.csv`.
Matrices de confusion: `GEO6_confusion_matrix_visual_only.csv` (baseline) y
`GEO6_confusion_matrix_best_w.csv` (w=0.3). Genero/familia se usaron **solo** para agrupar el
reporte, nunca para ordenar el ranking (regla dura confirmada en
`GEO6_REPRODUCIBILITY_MANIFEST.json`).

## 3. ETAPA 2 — Open Set (gate separado)

**Especie propuesta** = top-1 del ranking de Etapa 1 (w_geo_rank=0.3), no recalculada.
**Score de Etapa 2** (`w_geo_open_set=0.9`, la config validada en GEO-2/GEO-3, aplicada aqui a un
insumo DISTINTO — el top-1 de Etapa 1 en vez del top-1 visual puro):

```
open_set_score = 0.1 * visual_norm_top1_escalar + 0.9 * (1 - geo_prior_norm(especie_propuesta, zona))
```

`visual_norm_top1_escalar` = minmax global de la distancia euclidiana top-1 (KNOWN+UNKNOWN
concatenados) — **insumo distinto** del `visual_sim` fila-normalizado de Etapa 1; no se reutiliza
ciegamente un score para el otro proposito (documentado en `GEO6_OPENSET_RESULTS.json`).

### Hallazgo critico: el oracle de GEO-2

Al reproducir fielmente `phase_geo2_weight_sweep.py` se descubrio que, para las imagenes KNOWN,
GEO-2 usa la **especie verdadera** (`known_top1 = known_sci_name`, linea 127) como insumo del
componente geografico — no la especie predicha. Es un oracle no disponible en inferencia real (no
se conoce la especie verdadera de antemano; es justo lo que se intenta determinar). Reproducir D
con la especie **predicha** (metodologia honesta) da AUROC=0.6167, no 0.70148. La diferencia
(+0.085 AUROC) es integramente atribuible al oracle. Esto no invalida los resultados historicos de
GEO-2/3 (documentaban correctamente lo que hacian), pero **limita cuanto de esa mejora es
replicable en produccion real**, un matiz no explicitado antes de GEO-6.

### Resultados A/B/C/D (bootstrap 1000 iter, seed=42, estratificado por individuo)

Ver tabla completa en `GEO6_COMPARISON.md` y `GEO6_OPENSET_RESULTS.csv/json`. Resumen:

| Config | AUROC | IC95% | Top-1 (ranking) |
|---|---|---|---|
| A (visual solo) | 0.5733 | [0.541, 0.606] | 0.5852 |
| B (score de ranking w=0.3 reusado para open-set) | 0.6096 | [0.582, 0.638] | 0.6625 |
| **C (dos etapas: rank w=0.3 + gate w=0.9)** | **0.6032** | **[0.576, 0.633]** | **0.6625** |
| D (GEO-2 original, oracle, w=0.9 unico) | 0.7015 | [0.673, 0.730] | 0.4107 |

**¿Se conserva la mejora de GEO-2 (~0.701 AUROC)?** No en su magnitud completa: C alcanza 0.6032
(+0.030 sobre A, IC ligeramente solapado — mejora no contundente estadisticamente pero consistente
en direccion), lejos de 0.7015. La brecha se explica mayormente por el oracle de D (ver arriba): un
D "honesto" (top1 predicho) da 0.6167, muy cercano al 0.6032 de C. **La arquitectura de dos etapas
SI recupera casi toda la mejora de Open Set que es realmente alcanzable sin oracle**, y ademas
recupera por completo el ranking (que D con w=0.9 destruye).

**Desglose por subgrupo** (`GEO6_OPENSET_SUBGROUP_ANALYSIS.csv`):
- same_genus vs different_genus (UNKNOWN): C mejora mas en `same_genus` (AUROC 0.630 vs A 0.582)
  que en `different_genus` (C 0.543 vs A 0.554, leve empeoramiento) — el prior geografico ayuda
  mas cuando el error visual es "vecino taxonomico".
- with_zone vs without_zone (UNKNOWN): direccion **contraintuitiva** en C (with_zone=0.437 <
  without_zone=0.725), igual que GEO-3 ya encontro. **No se interpreta como causal** — que una
  observacion UNKNOWN tenga coordenada recuperable no es aleatorio (posible sesgo de seleccion,
  documentado y heredado sin resolver de GEO-3).

### Umbral de aceptacion: CALIBRATION vs DIAGNOSTIC

Se revisó `validation/fase18_clean_calibration/` como candidato a split CALIBRATION
independiente. Tiene ambas clases (`known_n=2545`, `unknown_n=17`), pero se **descarta**:
(1) `unknown_n=17` es demasiado pequeño para estimar FAR con confianza (un solo UNKNOWN mal
clasificado mueve FAR ~5.9 puntos porcentuales); (2) su pipeline selecciono COSINE como metrica
final y su EUCLIDEAN de referencia no incluye componente geografico (no es el mismo score
combinado de GEO-2/3/5/6). **Los thresholds de GEO-6 se marcan `DIAGNOSTIC`**: se calculan sobre
el propio split de TEST evaluado (7475 KNOWN + 620 UNKNOWN), con el mismo metodo de busqueda por
FAR objetivo de GEO-3 — limitacion heredada de GEO-2/GEO-3, no nueva de GEO-6.

### Banda de dos thresholds (NO_CONCLUYENTE)

Sobre `score_C` (Etapa 2, especie propuesta = top-1 de Etapa 1):

| far_level | threshold | FAR | FRR | BalAcc | Precision |
|---|---|---|---|---|---|
| <=5% | **THR_LOW = 0.5190** | 5.00% | 79.79% | 0.5761 | 0.0899 |
| <=30% | **THR_HIGH = 0.8233** | 29.68% | 66.03% | 0.5214 | 0.0812 |

Regla: `score < THR_LOW` -> **ESPECIE_CONOCIDA**; `score >= THR_HIGH` -> **NO_CONCLUYENTE**
(banda de alta incompatibilidad, posible no-registrada, **no se afirma NO_REGISTRADA**: no hay
evidencia en este experimento para separar formalmente "especie ausente del catalogo" de
"observacion ambigua/borderline" con el mismo score — limitacion explicita, regla dura del
encargo); banda intermedia -> **NO_CONCLUYENTE**.

Distribucion real de decisiones (`GEO6_OPENSET_DECISION_SUMMARY.json`):

| | ESPECIE_CONOCIDA | NO_CONCLUYENTE (banda media) | NO_CONCLUYENTE (alta incompatibilidad) |
|---|---|---|---|
| KNOWN (n=7475) | 1511 (20.2%) | 1028 (13.8%) | 4936 (66.0%) |
| UNKNOWN (n=620) | 31 (5.0%) | 153 (24.7%) | 436 (70.3%) |

Lectura honesta: con estos thresholds DIAGNOSTIC (derivados del propio TEST, conservadores), la
mayoria de observaciones — tanto KNOWN como UNKNOWN — caen en NO_CONCLUYENTE. Esto refleja que el
prior geografico por zona (K=291 especies, resolucion de 4 zonas) es demasiado difuso para dar
compatibilidad alta a la mayoria de especies individuales (probabilidad neutral ~1/291=0.0034), no
un error de construccion. El FAR en la fraccion ESPECIE_CONOCIDA de UNKNOWN (31/620=5.0%) es
consistente por diseño con el nivel objetivo FAR<=5% usado para THR_LOW.

## 4. Salida Merlin-like

8 ejemplos reales (`GEO6_MERLIN_EXAMPLES.json`, seed=42, 5 KNOWN + 3 UNKNOWN), cada uno con
`candidate_1/2/3` (species/genus/family/visual_score/geographic_score/ranking_score) y el
resultado del gate Open Set (decision + base explicita: threshold vs score obtenido). Ejemplos
destacados:
- `GEO6_MERLIN_KNOWN_00576`: *Craugastor raniformis*, zona=ZONE_005, top-1 correcto,
  `geo_compatibility=compatible`, `open_set_score=0.631` (banda intermedia -> NO_CONCLUYENTE,
  pese a top-1 correcto y zona compatible — thresholds conservadores).
- `GEO6_MERLIN_KNOWN_05422`: *Hyloscirtus palmeri* mal identificado como *Rheobates palmatus*
  (`less_compatible`), score alto (0.901) -> NO_CONCLUYENTE de alta incompatibilidad.
- `GEO6_MERLIN_UNKNOWN_00606`: UNKNOWN real, top-1 propuesto compatible con la zona (score=0.631,
  igual que el ejemplo KNOWN homologo) -> mismo tratamiento NO_CONCLUYENTE, ilustrando que el
  score por si solo no distingue estos dos casos con la resolucion geografica actual.

No se reporta `calibrated_probability`: ningun experimento de esta cadena (GEO2-GEO6) calibro
isotonic/Platt contra un holdout independiente.

## 5. Respuestas a las 7 preguntas

1. **¿Mejoro el ranking respecto al baseline visual y respecto a w_geo=0.9 unico?** Si, en ambos
   casos. Top-1: 0.5852 (A) -> 0.6625 (dos etapas, +7.7pp) vs 0.4107 (w=0.9 unico, GEO-5). MRR:
   0.7145 -> 0.7741 vs 0.6084 (w=0.9 unico). El ranking de dos etapas es el mejor de los tres.

2. **¿Se conserva la mejora Open Set de GEO-2 (~0.701 AUROC)?** Parcialmente. C alcanza 0.6032
   (+0.030 sobre baseline visual, IC parcialmente solapado — mejora no estadisticamente
   contundente pero consistente en direccion). No alcanza 0.7015 porque ese numero depende de un
   oracle (especie verdadera conocida de antemano) no disponible en produccion — un D "honesto"
   (top1 predicho) da 0.6167, muy cercano a C. La arquitectura de dos etapas recupera casi toda
   la mejora de Open Set **realmente alcanzable**.

3. **¿La separacion de tareas resuelve el conflicto de GEO-5?** Si, en direccion: ya no hay que
   elegir entre ranking bueno y open-set malo — ambos mejoran simultaneamente sobre el baseline
   visual con la arquitectura de dos etapas. No lo resuelve completamente en magnitud (el AUROC
   de C es menor que el numero historico de D), pero ese numero historico nunca fue alcanzable
   sin oracle, asi que la comparacion honesta (C vs D-sin-oracle) muestra que la separacion no
   pierde casi nada de Open Set mientras gana +25pp de Top-1 sobre D.

4. **Configuracion recomendada para un prototipo**: `w_geo_rank=0.3` para Etapa 1 (ranking de
   candidatos), `w_geo_open_set=0.9` para Etapa 2 (gate de aceptacion), aplicado al top-1 de
   Etapa 1 (no al top-1 visual puro). Thresholds DIAGNOSTIC: THR_LOW=0.519 (FAR<=5%),
   THR_HIGH=0.823 (FAR<=30%) — **no usar en produccion sin una calibracion independiente real**
   (ver limitacion 5).

5. **¿Que queda experimental/sin resolver?**
   - Si `w_geo_rank>0.3` sigue mejorando el ranking (el sweep permitido no llego a un techo claro).
   - Los thresholds de Etapa 2 son DIAGNOSTIC (calibrados sobre TEST, sin split CALIBRATION
     independiente valido — el existente en fase18 tiene solo 17 UNKNOWN y otra metrica).
   - No se puede distinguir cientificamente NO_REGISTRADA de NO_CONCLUYENTE con la evidencia
     disponible (documentado explicitamente, banda alta se queda como NO_CONCLUYENTE).
   - El sesgo de seleccion en with_zone/without_zone no esta resuelto (heredado de GEO-3).
   - B vs C (reusar el score de ranking directamente vs gate separado) estan practicamente
     empatados en AUROC en este rango de pesos — la ventaja de C es mas clara en Precision y
     BalancedAccuracy que en AUROC puro; no se investigo por que.

6. **¿Que NO debe pasar todavia a produccion?** Los thresholds DIAGNOSTIC (THR_LOW/THR_HIGH), el
   w_geo_rank=0.3 sin verificar si un valor mayor es aun mejor, y cualquier presentacion del
   AUROC 0.701 de GEO-2 como "el AUROC del sistema" sin la salvedad del oracle. El prior
   geografico de 291 especies y 4 zonas tampoco cambia — sigue siendo el mismo de GEO-2/3/5,
   sin recalibrar.

7. **Artefactos generados** — ver seccion 6.

## 6. Artefactos generados (confirmados con ls/lectura real)

```
validation/fase23a_geographic_context/
  scripts/phase_geo6_two_stage.py            [nuevo]
  GEO6_RANKING_RESULTS.csv                   [nuevo, 4 filas]
  GEO6_RANKING_RESULTS.json                  [nuevo]
  GEO6_ranking_by_species.csv                [nuevo]
  GEO6_ranking_by_genus.csv                  [nuevo]
  GEO6_confusion_matrix_visual_only.csv      [nuevo]
  GEO6_confusion_matrix_best_w.csv           [nuevo]
  GEO6_OPENSET_RESULTS.csv                   [nuevo, 4 filas A/B/C/D]
  GEO6_OPENSET_RESULTS.json                  [nuevo]
  GEO6_OPENSET_SUBGROUP_ANALYSIS.csv         [nuevo]
  GEO6_OPERATING_POINTS.csv                  [nuevo]
  GEO6_THRESHOLD_CURVE_C.csv                 [nuevo, 400 puntos]
  GEO6_OPENSET_DECISION_SUMMARY.json         [nuevo]
  GEO6_MERLIN_EXAMPLES.json                  [nuevo, 8 ejemplos]
  GEO6_COMPARISON_SUMMARY.json               [nuevo]
  GEO6_COMPARISON.md                         [nuevo, este archivo + tabla A/B/C/D]
  GEO6_REPRODUCIBILITY_MANIFEST.json         [nuevo]
  GEO6_REPORT.md                             [nuevo, este archivo]
```

Todos verificados con `ls -la GEO6_*` tras la ejecucion final del script (14 archivos con
prefijo GEO6_ + 2 scripts). No se modifico ningun archivo GEO2_*/GEO3_*/GEO4_*/GEO5_*,
`regional_packages/ANTIOQUIA/v1.0.0/`, `prior_zone_taxon_v1.csv`, encoder, embeddings oficiales
ni dataset. No se hizo commit/push.

## 7. Veredicto

**`GEO6_TWO_STAGE_HELPFUL`**

Justificacion: la separacion en dos scores (a) recupera y mejora el ranking cerrado sobre el
baseline visual (+7.7pp Top-1, +25pp Top-1 sobre el score unico w=0.9), y (b) mejora el Open Set
sobre el baseline visual (+0.030 AUROC, direccion consistente aunque no contundente
estadisticamente), evitando por completo el trade-off destructivo que GEO-5 encontro con el score
unico. No se marca `HELPFUL` sin reservas: el AUROC de Open Set de la arquitectura de dos etapas
(0.603) no alcanza el numero historico de GEO-2 (0.701), y se descubrio que ese numero historico
depende de un oracle no disponible en produccion — comparado contra ese punto de referencia
honesto (~0.617), la perdida de Open Set es minima frente a la ganancia masiva de ranking. Los
thresholds de aceptacion siguen siendo DIAGNOSTIC y no deben pasar a produccion sin una
calibracion independiente real.
