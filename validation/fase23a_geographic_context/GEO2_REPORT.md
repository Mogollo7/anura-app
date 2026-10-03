# GEO-2 — Extensión del barrido de pesos visual+geo (w_geo 0.0–1.0)

## Gate 0 — Integridad

Reproducción del scoring visual puro (`euclidean_raw`) reutilizando exactamente
`baseline_reproduction_v2.json` / `reproduced_scores_v2.npz`:

- AUROC reproducido: **0.57329** (0.5732919408781961)
- AUROC oficial (`fase23a_open_set_automatic/method_comparison.csv`, euclidean_raw): **0.57329**
- `abs_diff = 0.0` → **GATE 0 PASSED**

Dataset y protocolo verificados idénticos a V2: 620 UNKNOWN
(`fase23a_open_set_automatic/embeddings/unknown_embeddings.npz`), 7475 KNOWN
(`fase16_clean_open_set/clean_known_embeddings.npz`), centroides de
`reference_embeddings.npz` (Group A, 9) + `train_embeddings.npz` (Group B, 32),
encoder sin tocar (ya embebido), método euclidean_raw, seed=42, bootstrap 1000
iter estratificado por individuo, prior limpio `prior_zone_taxon_v2_clean.csv`.

## Barrido de pesos (w_geo = 0.0 → 1.0)

Ver `GEO2_WEIGHT_SWEEP.csv` / `.json` (tabla completa) y `GEO2_BOOTSTRAP_RESULTS.json`
(distribuciones bootstrap completas por peso).

| w_geo | AUROC | IC95% | FAR | FRR | BalAcc |
|---|---|---|---|---|---|
| 0.00 (baseline visual puro) | 0.57329 | [0.5408, 0.6055] | 0.9339 | 0.0500 | 0.5080 |
| 0.10 | 0.60005 | [0.5686, 0.6318] | 0.9161 | 0.0500 | 0.5169 |
| 0.20 | 0.62803 | [0.5977, 0.6588] | 0.9048 | 0.0500 | 0.5226 |
| 0.30 | 0.65297 | [0.6245, 0.6821] | 0.9016 | 0.0500 | 0.5242 |
| 0.40 | 0.67006 | [0.6431, 0.6975] | 0.8968 | 0.0500 | 0.5266 |
| 0.50 | 0.67820 | [0.6516, 0.7048] | 0.8903 | 0.0500 | 0.5298 |
| 0.60 | 0.68071 | [0.6537, 0.7070] | 0.8742 | 0.0500 | 0.5379 |
| 0.70 | 0.68383 | [0.6568, 0.7117] | 0.8452 | 0.0500 | 0.5524 |
| 0.80 | 0.69259 | [0.6645, 0.7217] | 0.7952 | 0.0500 | 0.5774 |
| **0.90 (máximo AUROC)** | **0.70148** | **[0.6728, 0.7302]** | **0.7419** | **0.0500** | **0.6040** |
| 1.00 (geo puro) | 0.67459 | [0.6507, 0.6978] | 0.2097 | 0.6329 | 0.5787 |

Threshold en cada peso: cuantil 0.95 de los scores KNOWN del pool de evaluación
(misma convención KAR95-de-eval-KNOWN usada en `phase_reevaluate_clean.py` para
w=0.0–0.5; documentado que difiere de la convención CALIBRATION-KAR95 oficial
por falta de coordenadas en el split CALIBRATION — ver limitación heredada de V2).

**Observación clave:** el AUROC sube de forma prácticamente monótona hasta
w_geo=0.90 (máximo, 0.70148) y luego cae en w_geo=1.00 (geo puro, 0.67459) —
hay un techo/inflexión claro en 0.90, no en 0.50. Sin embargo el FAR, aunque
mejora con w_geo creciente, se mantiene por encima de 0.74 en el punto de
máximo AUROC — muy lejos de un rango operativamente aceptable. Solo en
w_geo=1.00 (geo puro, sin componente visual) el FAR cae a 0.21, pero a costa de
que el FRR se dispare a 0.63 (el geo-score solo, sin visual, rechaza como
"unknown" a más de 6 de cada 10 KNOWN reales) — un trade-off inaceptable en la
otra dirección.

## Análisis Pareto

Regla: A domina a B si AUROC_A≥AUROC_B, FAR_A≤FAR_B, FRR_A≤FRR_B, y al menos
una estrictamente mejor.

Frente no-dominado (`GEO2_PARETO_FRONT.csv`): **w_geo ∈ {0.90, 1.00}** — todos
los pesos intermedios (0.0–0.8) quedan dominados por w_geo=0.90 (mejor AUROC
Y mejor FAR con el mismo FRR). w_geo=1.00 se mantiene en el frente solo porque
tiene el FAR más bajo de todo el barrido (0.2097), aunque su FRR (0.6329) es
inaceptable — por eso el frente Pareto por sí solo NO identifica un único
"mejor" punto: hay que decidir con criterio operativo.

- **Mejor punto Pareto por compromiso operativo: w_geo=0.90.** Es el único
  punto Pareto con FRR=0.0500 (igual al baseline, no sacrifica nada en KNOWN),
  con el AUROC máximo y el segundo mejor FAR del barrido (0.7419). w_geo=1.00
  queda descartado como opción práctica porque dispara el FRR 12.6x.

## Análisis por tipo de UNKNOWN (same_genus vs different_genus)

n=426 UNKNOWN same_genus, n=194 UNKNOWN different_genus (clasificación
idéntica a la usada en V1: género del top-1 predicho está o no en el
conjunto de géneros KNOWN, vía `training/taxonomia.genero_de`/`canonico`).
Ver `GEO2_SUBGROUP_ANALYSIS.csv` para la tabla completa por peso.

| w_geo | AUROC same_genus | AUROC different_genus |
|---|---|---|
| 0.0 | 0.5823 | 0.5535 |
| 0.5 | 0.6692 | 0.6980 |
| 0.8 | 0.6748 | 0.7316 |
| **0.9** | **0.6759** | **0.7576** |
| 1.0 | 0.6357 | 0.7600 |

La geografía ayuda a **ambos** subgrupos de forma consistente hasta w_geo=0.9,
pero el efecto es marcadamente **más fuerte en different_genus** (+0.204 desde
baseline a w_geo=0.9) que en **same_genus** (+0.094). Esto es plausible: un
UNKNOWN de género distinto ya es visualmente "raro" respecto a las 41 especies
conocidas, así que el prior geográfico aporta señal casi independiente; un
UNKNOWN del mismo género es visualmente más parecido a una especie conocida, y
el score visual domina más ese caso — la geografía ayuda menos porque el
encoder ya está compitiendo con confusión intra-género. En w_geo=1.0 (geo
puro) el patrón se invierte para same_genus (cae a 0.6357), consistente con
que sin señal visual el sistema pierde la capacidad de distinguir especies
visualmente próximas del mismo género.

## Contribución geográfica

De 620 UNKNOWN, solo **262 (42%)** tienen zona biogeográfica asignada (cell→zone
lookup contra `cell_zone_map_v1.csv`); 358 (58%) quedan con `NEUTRAL_GEO_SCORE`
(1/K) por no caer en una celda válida de Antioquia o no tener coordenadas
extraíbles del cache. De los 262 con zona, la distribución está muy concentrada:
ZONE_005 (221, 84%), ZONE_006 (20), ZONE_001 (20), ZONE_002 (1) — es decir, la
señal geográfica que sí existe viene mayoritariamente de una sola zona. Las
especies UNKNOWN más frecuentes (`Smilisca_phaeota`, `Scinax_rostratus`,
`Espadarana_prosoblepon`, …) concentran buena parte de la mejora observada.
No se usó elevación (0/4466 recuperable, confirmado en el experimento anterior,
no reintroducida). No se hicieron llamadas nuevas a iNaturalist — todo desde
`cache/inat_extracted.json` ya existente.

## Clasificación del resultado

**`GEO2_AUROC_IMPROVES_BUT_FAR_UNACCEPTABLE`**

El AUROC mejora de forma robusta y estadísticamente no-solapada (IC95% de
w_geo=0.9 no se superpone con el de baseline: [0.6728,0.7302] vs
[0.5408,0.6055], Δ=+0.128), y el frente Pareto identifica w_geo=0.9 como el
mejor compromiso disponible. Pero incluso en ese punto óptimo el FAR sigue en
**0.7419** — es decir, ~74% de los UNKNOWN reales seguirían siendo aceptados
como si fueran una de las 41 especies conocidas. Para el uso previsto (filtro
de open-set en campo) ese nivel de FAR no es operativamente aceptable, por más
que sea una mejora sustancial sobre el 0.9339 del baseline visual puro.

## Resumen ejecutivo

1. **¿El baseline reprodujo exactamente 0.57329?** Sí — AUROC=0.5732919408781961, abs_diff=0.0. Gate 0 pasó.
2. **AUROC máximo obtenido y con qué w_geo:** 0.70148 en **w_geo=0.90**.
3. **Su IC95%:** [0.6728, 0.7302] (bootstrap 1000 iter, seed=42, estratificado por individuo).
4. **FAR/FRR en ese punto:** FAR=0.7419, FRR=0.0500 (FRR igual al baseline — el threshold KAR95 fija FRR≈5% por construcción en todos los pesos salvo w=1.0).
5. **Mejor punto Pareto:** w_geo=0.90 (coincide con el de mayor AUROC en este caso; w_geo=1.00 también queda en el frente pero por un trade-off inaceptable en FRR).
6. **Qué peso ofrece el mejor compromiso, y por qué:** w_geo=0.90 — domina a todos los pesos intermedios (0.0–0.8) en AUROC y FAR simultáneamente, sin sacrificar FRR; w_geo=1.00 se descarta porque dispara el FRR a 0.63.
7. **¿Ayuda a UNKNOWN del mismo género?** Sí pero moderadamente: AUROC same_genus sube de 0.5823 (w=0) a 0.6759 (w=0.9), +0.094.
8. **¿Ayuda a UNKNOWN de género diferente?** Sí y más fuerte: AUROC different_genus sube de 0.5535 (w=0) a 0.7576 (w=0.9), +0.204.
9. **¿Sigue mejorando más allá de w_geo=0.5, o hay techo/inflexión?** Sigue mejorando monótonamente hasta w_geo=0.90 (techo real, no en 0.5); a w_geo=1.00 el AUROC cae (0.67459) y el FRR se dispara — la inflexión de la curva completa está en w_geo≈0.9, no en 0.5 como sugería el barrido V2 truncado.
10. **Configuración recomendada para la siguiente fase:** w_geo=0.90 / w_visual=0.10 como punto de partida para validación independiente, PERO con la advertencia explícita de que el FAR resultante (0.74) sigue siendo operativamente inaceptable — la siguiente fase debería enfocarse en reducir FAR (mejor cobertura geográfica: solo 42% de UNKNOWN tiene zona asignada; o un threshold distinto, no solo el peso) antes de considerar cualquier despliegue.
11. **¿Integrar ya en producción?** **NO.** La mejora de AUROC es real y robusta, pero el FAR resultante en el mejor punto Pareto (0.74) está muy lejos de ser aceptable para un filtro open-set en campo, y solo 42% de las observaciones UNKNOWN tienen contexto geográfico útil (el resto cae en score neutro). Se requiere validación independiente y trabajo adicional de cobertura/threshold antes de integrar.
12. **Artefactos generados (confirmados con `ls`):**
    - `GEO2_WEIGHT_SWEEP.csv`, `GEO2_WEIGHT_SWEEP.json`
    - `GEO2_BOOTSTRAP_RESULTS.json`
    - `GEO2_PARETO_FRONT.csv`
    - `GEO2_SUBGROUP_ANALYSIS.csv`
    - `GEO2_GEO_CONTRIBUTION.json` (contribución geográfica: zonas, frecuencia de especie, sin elevación)
    - `GEO2_INTERPRETATION.json` (clasificación y racional)
    - `GEO2_REPORT.md` (este archivo)
    - Script nuevo: `scripts/phase_geo2_weight_sweep.py`
