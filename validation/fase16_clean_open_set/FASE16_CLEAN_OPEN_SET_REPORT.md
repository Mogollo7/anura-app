# FASE 16 — Open Set Clean Evaluation: Reporte Final

**Fecha**: 2026-09-13. **No se hizo commit ni push.**

---

## 1. Objetivo

Construir una evaluación Open Set **completamente independiente de Fase 13**, tras confirmar
que el blind test original (F3/F4) tenía leakage total del lado KNOWN, para determinar si
ANURA tiene evidencia científica válida de capacidad de rechazo Open Set.

## 2. Leakage descubierto en Fase 13 (recordatorio, no modificado)

```
Group A KNOWN: 197/197 imágenes ∩ TRAIN
Group B KNOWN: 569/569 imágenes ∩ TRAIN
UNKNOWN (F4):    0/56  imágenes ∩ TRAIN
```
F3 completo es un subconjunto exacto (mismo `path`) de TRAIN. Fase 13 **no se modificó**;
sus artefactos permanecen protegidos e inmutables (verificado en Fase 16.14).

## 3. Datos utilizados

| Conjunto | Origen | Tamaño | Rol en Fase 16 |
|---|---|---|---|
| KNOWN limpio | `data cleaned/` — imágenes reales NO usadas en TRAIN/REFERENCE/CALIBRATION/F3 | 7475 imágenes, 4103 individuos, 24 especies | Blind KNOWN (nuevo) |
| UNKNOWN | F4 (Fase 13), re-verificado | 56 imágenes, 2 especies | Blind UNKNOWN (reutilizado, ya limpio) |
| REFERENCE | Fase 13, sin modificar | 798 imágenes | Fuente de covarianza y centroides Group A |
| CALIBRATION | Fase 13, sin modificar | 192 imágenes | Fuente del threshold |
| TRAIN | Fase 13, sin modificar | 4724 imágenes | Fuente de centroides Group B |

**No se fabricaron datos biológicos ni especies.** Las 7475 imágenes son fotografías reales
existentes en el repositorio, simplemente no habían sido consumidas por ningún split previo.

## 4. Contamination Audit (Fase 16.1)

```
TRAIN ∩ CALIBRATION = 0        (SHA256)
TRAIN ∩ REFERENCE   = 0        (SHA256)
TRAIN ∩ BLIND(F4)   = 0        (path)
TRAIN ∩ BLIND(F3)   = 766      (path — YA CONOCIDO, F3 NO se reutiliza)
CALIBRATION ∩ BLIND(F4) = 0    (filename)
REFERENCE ∩ BLIND(F4)   = 0    (filename)
individual_id(CALIBRATION) ∩ BLIND = UNKNOWN (campo no disponible, declarado explícitamente, no asumido 0)
```
Ver `contamination_audit.json`.

## 5. Calibration

Covarianza: `REFERENCE` (798 imgs, Ledoit-Wolf). Threshold: `CALIBRATION` (192 imgs, KAR 95%).
Ninguno de los dos participa en el blind test limpio — verificado por construcción (el pool
KNOWN excluye explícitamente REFERENCE/CALIBRATION por hash) y confirmado en la auditoría.

## 6. Centroid Independence (Fase 16.4 — obligatorio)

```
CENTROID_SOURCE(REFERENCE) ∩ CLEAN_KNOWN = 0   (SHA256)
CENTROID_SOURCE(TRAIN)     ∩ CLEAN_KNOWN = 0   (path completo)
```
**Conclusión: OUT_OF_SAMPLE.** El KNOWN limpio nunca fue visto por los centroides que lo
evalúan. Ver `centroid_independence_check.json`.

Adicionalmente, se filtró por `individual_id` (obs_id): de las 7475 imágenes candidatas por
archivo, **0 fueron rechazadas** por compartir individuo con TRAIN — el proceso de split
original de TRAIN agrupa por observación de forma "todo o nada" (nunca deja fotos sueltas
del mismo individuo fuera), lo cual se confirmó empíricamente, no se asumió.

## 7. Covariance

`covariance/v1.1.0_CLEAN/` — Ledoit-Wolf shared, formalizada independientemente para Fase 16.
Matriz **idéntica** (mismo SHA256) a `covariance/v1.0.0/`, ya que se calcula sobre el mismo
REFERENCE (no contaminado). Reproducibilidad interna verificada (2 cálculos idénticos).

**Nota sobre regresión externa detectada**: `training/taxonomia.py` fue modificado fuera de
esta sesión durante esta tarea — perdió la función `canonico()` y el `ALIAS` (incluido
`acanthinus→achatinus`). Esto redujo la resolución de `species_ids` en la covarianza de 9 a 8
especies (Leucostethus y ahora también "Pristimantis acanthinus" quedan huérfanas de
`species_id`), aunque **la matriz numérica es idéntica** — solo cambió el metadata de qué
especies se listan como resueltas. Se hizo el código resiliente (fallback sin alias) sin
modificar `taxonomia.py`, que no está bajo control de esta auditoría.

## 8. Threshold

`threshold/v1.1.0_CLEAN/`: `39.35406371422803` — **mismo valor histórico, sin recalibrar**,
congelado explícitamente antes de ejecutar el blind test (ver Freeze). Determinismo del hash
verificado tras corregir la exclusión de `created_at` del contenido hasheado.

## 9. Freeze Manifest

`fase16_freeze_manifest.json` — hashes de encoder, catalog_release, covariance (npz+manifest),
threshold_release, REFERENCE/TRAIN embeddings, CALIBRATION manifest, y el blind manifest
(KNOWN limpio + F4), capturados **antes** de ejecutar el blind test. Ningún artefacto listado
se modificó después del freeze.

## 10. Blind Test

Ejecutado **después** del freeze, clasificando en 5 categorías (margen ±5% del threshold para
`NO_CONCLUSIVE`):

```
KNOWN_ACCEPTED:           5727
KNOWN_REJECTED:            960
UNKNOWN_REJECTED:            3
UNKNOWN_FALSE_ACCEPTED:     46
NO_CONCLUSIVE (known):      788
NO_CONCLUSIVE (unknown):      7
```

## 11. Métricas

| Métrica | Fase 16 (limpio) | Fase 13 (contaminado) |
|---|---|---|
| KAR | **85.64%** | 85.38% |
| FRR | 14.36% | 14.62% |
| UDR | **6.12%** | 8.93% |
| FAR | **93.88%** | 91.07% |
| Precision (unknown) | 0.38% | 4.27% |
| Recall (unknown) | 8.93% | 8.93% |
| F1 (unknown) | 0.73% | 5.78% |
| Balanced accuracy | **45.73%** | (no reportado en Fase 13) |
| AUROC | **59.28%** | 62.48% |

`n_images`: 7475 KNOWN / 56 UNKNOWN. `n_individuals`: 4103 KNOWN. `n_species`: 24 KNOWN / 2 UNKNOWN.

**No se llamó "accuracy" a ninguna métrica que no lo sea** — se reporta `balanced_accuracy`
explícitamente como tal, distinta de una accuracy simple.

## 12. Comparación Fase 13 vs Fase 16

Ver `fase13_vs_fase16_comparison.json`. Hallazgo central:

> KAR se mantiene similar (85.6% vs 85.4%) — la aceptación de KNOWN generaliza razonablemente
> incluso sin leakage. **Pero AUROC empeora (0.593 vs 0.625) y FAR empeora (93.9% vs 91.1%)
> al eliminar el leakage.** Esto indica que el leakage de Fase 13 estaba, si acaso, **inflando**
> artificialmente la separación KNOWN/UNKNOWN aparente — no ocultando un resultado peor del
> que realmente existe. `balanced_accuracy=0.457` es **peor que un clasificador aleatorio**.

```
Fase 13: SCIENTIFIC_STATUS = COMPROMISED_BY_LEAKAGE
Fase 16: SCIENTIFIC_STATUS = CLEAN_NO_LEAKAGE_VERIFIED (pero cobertura parcial: 24/41 especies)
```

## 13. Determinismo

- Covarianza: 2 cálculos independientes con mismos inputs → idénticos (verificado en `build_covariance_release.py`)
- Threshold: hash de contenido científico (excluyendo `created_at`) idéntico en 2 ejecuciones
- Scores Mahalanobis: idénticos byte-a-byte en 2 ejecuciones sobre la misma muestra (SHA256 `02c8ff29...` ambas)
- `species_id`: heredado de la sesión previa, ya verificado determinista

## 14. Inmutabilidad

44 archivos de `evaluation/fase13/`, `visual_catalog/v1.0.0/`, `bioclip/checkpoints/`
verificados con SHA256 antes (Fase 15) y después de Fase 16 completa — `diff` exit code 0.
`git status --short` sobre las tres rutas: vacío.

```
modified = 0
deleted  = 0
moved    = 0
```

## 15. Limitaciones

**De ingeniería**: ninguna nueva — el pipeline de artefactos versionados (covariance_release,
threshold_release, compatibility gate) funcionó correctamente para construir Fase 16 sin
modificar nada protegido.

**De datos**: solo 24/41 especies tienen imágenes reales sin usar en ningún split previo — las
17 especies restantes consumieron el 100% de sus datos disponibles en TRAIN/REFERENCE/CALIBRATION,
por lo que no tienen KNOWN limpio posible sin recolectar más datos. UNKNOWN sigue limitado a
solo 2 especies (`Hyloxalus_picachos`, `Sachatamia_electrops`), insuficiente para generalizar
sobre "cualquier especie fuera del catálogo".

**Científica**: con los datos limpios disponibles, `AUROC=0.593` y `balanced_accuracy=0.457`
indican que el mecanismo Open Set actual (Mahalanobis + Ledoit-Wolf + threshold heredado de
Fase 13) **no demuestra separación KNOWN/UNKNOWN confiablemente por encima del azar** en un
escenario genuinamente held-out. Esto no es un fallo del pipeline de esta auditoría — es
evidencia real sobre el método.

**Externa (no controlada por esta tarea)**: `training/taxonomia.py` fue modificado por otro
proceso durante esta sesión, perdiendo `canonico()`/`ALIAS`. Se documentó y se hizo el código
resiliente sin revertir ni modificar ese archivo.

## 16. Conclusión científica

```
SCIENTIFIC OPEN-SET VALIDATION:
PENDING — INSUFFICIENT CLEAN DATA
```

El pipeline metodológico es correcto: split limpio verificado, calibración sin contaminación,
centroides confirmados out-of-sample, freeze antes de blind test, determinismo confirmado. Pero
la cobertura (24/41 especies KNOWN, 2 especies UNKNOWN) es insuficiente para una conclusión
fuerte, y el resultado obtenido con los datos disponibles (AUROC≈0.59, balanced accuracy por
debajo de 0.5) tampoco permite afirmar que el mecanismo funciona. **No se declara PASS** porque
eso requeriría cobertura completa y métricas que demuestren separación real. **No se declara
FAIL por leakage** porque no hay leakage en este conjunto — el FAIL, de existir, sería sobre el
método en sí, no sobre la metodología de evaluación, y la muestra UNKNOWN (2 especies) es
demasiado pequeña para esa afirmación con confianza.

---

# FASE 16 FINAL STATUS

```
Clean split:
PASS

No leakage:
PASS

Centroid independence:
PASS

Covariance:
PASS

Threshold:
PASS

Blind test:
PASS  (ejecutado correctamente tras freeze; el RESULTADO obtenido es débil, pero la
       EJECUCIÓN del blind test en sí — sin contaminación, con freeze previo — es válida)

BioCLIP:
FROZEN

Historical releases:
IMMUTABLE

Determinism:
PASS

Engineering scalability:
PASS

Scientific Open Set:
PENDING

Scientific scalability:
NOT YET SUPPORTED

Main blockers:
1. Cobertura KNOWN limpia incompleta: 24/41 especies (17 especies consumieron el 100%
   de sus datos reales en TRAIN/REFERENCE/CALIBRATION, sin remanente held-out).
2. Cobertura UNKNOWN insuficiente: solo 2 especies, no representativo del espacio de
   especies desconocidas.
3. Con los datos limpios disponibles, AUROC=0.593 y balanced_accuracy=0.457 (por debajo
   de azar) — no hay evidencia de que el mecanismo Open Set actual discrimine KNOWN/UNKNOWN
   confiablemente.
4. training/taxonomia.py fue modificado externamente durante esta tarea, perdiendo el
   mecanismo de alias — mitigado con fallback resiliente, no resuelto de raíz.

Evidence:
- validation/fase16_clean_open_set/contamination_audit.json
- validation/fase16_clean_open_set/clean_known_manifest.json (7475 imgs, 4103 individuos)
- validation/fase16_clean_open_set/centroid_independence_check.json (OUT_OF_SAMPLE)
- validation/fase16_clean_open_set/fase16_freeze_manifest.json
- validation/fase16_clean_open_set/fase16_blind_test_results.json
- validation/fase16_clean_open_set/fase13_vs_fase16_comparison.json
- validation/fase16_clean_open_set/blind_test_leakage_audit.json
- validation/fase16_clean_open_set/hashes_after_fase16.txt (vs. _baseline_pre_v1.1.0_test/hashes_before.txt)
```
