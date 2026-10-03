# GEO-4 FASE A — Reporte

Score jerárquico (especie+género+familia) extendiendo GEO-2/GEO-3, evaluado en
precisión de ranking de especie (nuevo) y en Open Set (repitiendo protocolo GEO-2/GEO-3).

## 1. Reutilizado / 2. Construido

Ver `GEO4_AUDIT.md` (detalle completo, PASO 0).

## 3. Fórmula exacta

```
combined_score = w_visual * visual_score_norm
                + w_geo_species * geo_species_component_norm
                + w_geo_genus   * geo_genus_component_norm
                + w_geo_family  * geo_family_component_norm
```

**Normalización:**
- `visual_score_norm`: para el score escalar de Open Set (PASO 4), idéntico a GEO2/GEO3
  — `minmax` global de la distancia euclídea top-1 a los 41 centroides, sobre
  KNOWN+UNKNOWN concatenados (`all_visual_norm`). Para el ranking de especie (PASO 3,
  nuevo), min-max **por fila** (por imagen, sobre las 41 clases candidatas), porque
  ahí se necesita una distribución de similitud por muestra, no un escalar — no existía
  en GEO2/GEO3 porque nunca hicieron ranking, solo la decisión binaria.
- `geo_species_component`, `geo_genus_component`, `geo_family_component`: ver fórmula
  de shrinkage jerárquico abajo, luego normalizados igual que `visual_score_norm`
  (minmax global para el score escalar de Open Set; minmax por fila para el ranking).
- Dirección para Open Set: se usa "unknownness" = `1 - minmax(P)` (igual que
  `geo_unknownness` de GEO2), de modo que score alto = más probable UNKNOWN.

## 4. Cómo se evita el doble conteo (justificación)

Los tres priors (especie/género/familia) se construyen **de los mismos registros
geográficos purgados** (`records_v1.csv` menos 1214 obs_id contaminados) — no son
evidencia independiente, son la misma observación agregada a distinta resolución
taxonómica. Sumarlos con pesos fijos e independientes inflaría artificialmente la
señal (la misma coordenada contaría 3 veces).

Se implementó en su lugar un **fallback jerárquico con shrinkage empírico-Bayes**,
basado en `n_effective` (evidencia disponible tras el effort-cap) del nivel más fino
disponible para el par (especie candidata, zona):

```
lambda_s = n_eff_species(zone, sp) / (n_eff_species(zone, sp) + K_SHRINK)
lambda_g = n_eff_genus(zone, genus(sp)) / (n_eff_genus(zone, genus(sp)) + K_SHRINK)

geo_species_component = lambda_s * P_species(sp | zone)
geo_genus_component   = (1 - lambda_s) * lambda_g * P_genus(genus(sp) | zone)
geo_family_component  = (1 - lambda_s) * (1 - lambda_g) * P_family(family(sp) | zone)
```

con `K_SHRINK = 5.0` (documentado, no barrido). Cuando hay suficiente evidencia de
especie en la zona (`lambda_s → 1`), los componentes de género/familia colapsan a
~0 y no aportan — la jerarquía actúa como *relleno* cuando la especie es escasa, no
como una tercera fuente sumada. Los pesos `w_geo_species/genus/family` del PASO 2 se
aplican **sobre estos componentes ya des-solapados**, no sobre las probabilidades crudas.

Nota importante: para el **variante B** (visual+geo_species, replicando el punto óptimo
de GEO-2) se usó deliberadamente la probabilidad de especie **cruda** (sin shrinkage),
porque B no involucra género/familia y debe reproducir exactamente el baseline de GEO-2
— el shrinkage solo tiene sentido cuando hay una jerarquía de fallback activa (variante C).

**Pesos:** `w_geo_total = 0.9` (óptimo GEO-2). Repartido en 3 esquemas (sensibilidad,
no barrido exhaustivo):

| Esquema | w_visual | w_especie | w_género | w_familia |
|---|---|---|---|---|
| C_main | 0.10 | 0.54 (0.9×0.60) | 0.225 (0.9×0.25) | 0.135 (0.9×0.15) |
| C_alt_species_heavy | 0.10 | 0.72 (0.9×0.80) | 0.135 (0.9×0.15) | 0.045 (0.9×0.05) |
| C_alt_balanced | 0.10 | 0.405 (0.9×0.45) | 0.315 (0.9×0.35) | 0.18 (0.9×0.20) |

## 5. Métricas antes/después

### Precisión de especie (ranking Top-k, 7475 imágenes KNOWN, 24 especies, 41 clases candidatas)

| Variante | Top-1 | Top-3 | F1 macro |
|---|---|---|---|
| Visual solo | 0.5852 | 0.8140 | 0.2778 |
| Visual + geo_species (GEO-2 style) | **0.6338** | **0.8673** | **0.3083** |
| Visual + geo_species + género + familia (C_main) | 0.4107 | 0.7782 | 0.2265 |

Ver `GEO4_species_precision_metrics.json`, `GEO4_confusion_matrix.csv`,
`GEO4_performance_by_family.csv`, `GEO4_performance_by_genus.csv`.

### Open Set (AUROC, bootstrap 1000 iter, seed=42, estratificado por individuo)

| Variante | AUROC | CI 95% | FAR | FRR | BalAcc |
|---|---|---|---|---|---|
| A — visual solo | 0.57329 | [0.5408, 0.6055] | 0.9339 | 0.0500 | 0.5080 |
| B — visual + geo_species | **0.70148** | [0.6728, 0.7302] | 0.7419 | 0.0500 | 0.6040 |
| C_main — + género + familia | 0.57087 | [0.5430, 0.6023] | 0.9290 | 0.0500 | 0.5105 |
| C_alt_species_heavy | 0.57140 | [0.5445, 0.6029] | 0.9290 | 0.0500 | 0.5105 |
| C_alt_balanced | 0.56900 | [0.5408, 0.6010] | 0.9274 | 0.0500 | 0.5113 |

A reproduce el gate exacto (0.57329). B reproduce el punto óptimo de GEO-2 (~0.701,
documentado en `GEO2_WEIGHT_SWEEP.csv` w_geo=0.9). Ver `GEO4_openset_comparison.json`
para el detalle con bootstrap CI y desglose same/different genus.

## 6. ¿Mejora realmente el ranking de candidatos?

**NO.** Añadir género/familia (C_main y las dos variantes alternativas de pesos)
**degrada** tanto el ranking de especie (Top-1 baja de 0.634 a 0.411, un retroceso de
22 puntos porcentuales frente a B) como el Open Set (AUROC cae de 0.701 a ~0.57,
prácticamente indistinguible del baseline puramente visual A). Se probó sensibilidad
con 3 repartos de peso distintos (60/25/15, 80/15/5, 45/35/20 sobre especie/género/familia)
y en los tres casos el resultado es consistentemente peor que B — no es un artefacto
de la elección de pesos, la degradación persiste incluso reduciendo el peso de
género/familia al mínimo probado (C_alt_species_heavy).

**Razón más probable:** el prior de género/familia es mucho menos informativo que el de
especie porque agrega demasiado (K=58 géneros, K=14 familias vs K=291 especies) — un
género frecuente en una zona (p.ej. *Pristimantis*, altamente diverso) no discrimina
entre sus propias especies, y puede incluso *empujar* la predicción hacia la especie
más común del género en esa zona aunque la evidencia visual apunte a otra. Esto es
consistente con la tabla por género: `Pristimantis` (n=1897, la más numerosa) tiene
`acc_hier=0.098` vs `acc_visual=0.196` — el prior geográfico jerárquico literalmente
empeora la especie más difícil y más representada del dataset.

## 7. Impacto en errores intra-género vs inter-género

Con la variante jerárquica (C_main), de los errores del predictor top-1:
- **Intra-género** (especie equivocada, mismo género correcto): 14.82% del total de
  muestras (fracción de todos los errores, no solo entre errores).
- **Inter-género** (género también equivocado): 44.11% del total de muestras.

Por familia, el efecto es muy desigual: `Dendrobatidae` tiene accuracy visual altísima
(0.976) que colapsa a 0.719 con la jerarquía (todo el daño es inter-género, 28.1%);
`Hylidae` (dominada por `Dendropsophus`, alta diversidad) cae de 0.486 a 0.289 con
55.99% de error inter-género. El patrón es sistemático: cuantas más especies comparten
género/familia en la zona, más ruido introduce el prior agregado — exactamente el
mecanismo de degradación esperado cuando se sube de resolución taxonómica sin
segmentar por disponibilidad real de evidencia fina.

## 8. Veredicto: **HARMFUL** (para esta formulación específica)

Justificación honesta: la extensión jerárquica de género/familia, implementada como
señal de shrinkage-fallback sobre el prior geográfico ya validado de GEO-2, **no aporta
valor y activamente degrada tanto el ranking de especie como el Open Set** frente al
baseline visual+geo_species de GEO-2 (que sigue siendo el mejor punto operativo
encontrado, AUROC≈0.701, Top-1≈0.634). No se observó ningún esquema de pesos (de los
3 probados) donde género/familia mejoraran sobre B. La causa raíz identificada es que
la resolución de género/familia es demasiado gruesa frente a la diversidad real de
especies por zona (particularmente en `Pristimantis`/`Craugastoridae` y
`Dendropsophus`/`Hylidae`, los grupos más numerosos y taxonómicamente más densos del
dataset), por lo que el prior agregado arrastra la predicción hacia la especie más
frecuente del género/familia en la zona en vez de aportar señal discriminativa
adicional.

Esto **no invalida** la arquitectura de shrinkage en sí (matemáticamente evita bien el
doble conteo, como pide el PASO 2) — el problema es de contenido informativo: género y
familia simplemente no discriminan lo suficiente en un dataset con géneros muy
desbalanceados y diversos. No se recomienda avanzar con la cascada
Familia→Género→Especie como mecanismo de decisión (tal como la tarea ya anticipaba);
esta evaluación confirma que no hay evidencia de valor para justificarla en esta fase.

## 9. Artefactos generados (confirmados con ls/lectura real)

```
GEO4_AUDIT.md
GEO4_REPORT.md (este archivo)
GEO4_REPRODUCIBILITY_MANIFEST.json
GEO4_priors_genus_family_manifest.json
GEO4_prior_zone_genus_v1_manifest.json
GEO4_prior_zone_family_v1_manifest.json
prior_zone_genus_v1.csv
prior_zone_family_v1.csv
GEO4_species_precision_metrics.json
GEO4_confusion_matrix.csv
GEO4_performance_by_family.csv
GEO4_performance_by_genus.csv
GEO4_openset_comparison.json
GEO4_per_sample_results.csv
scripts/phase_geo4_hierarchical_priors.py
scripts/phase_geo4_main.py
```

Ninguno de estos artefactos está marcado `READY_FOR_DEPLOYMENT`. No hubo commit/push.
