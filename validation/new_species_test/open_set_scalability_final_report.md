# Reporte Final: Cierre de Auditoría de Escalabilidad de ANURA

**Fecha**: 2026-09-13
**No se hizo commit ni push** (pendiente de revisión, según instrucción).

---

## A. Estado inicial (qué estaba mal)

1. `generate_species_id.py` marcaba **toda** especie nueva como `visual_lifecycle_status: DEPLOYED`, violando `SPECIES_LIFECYCLE.md` (que exige pasar por `VALIDATION → APPROVED` antes de `DEPLOYED`).
2. `tools/catalog/validation_gate.py:40` tenía `centroid_audit.get("total_centroids") == 41` hardcodeado — el gate fallaría incorrectamente ante cualquier catálogo de tamaño distinto a 41, incluso uno válido.
3. La covarianza Ledoit-Wolf se recalculaba **desde cero, sin persistir**, en 3 scripts distintos (`fase13_calibrate_selection.py`, `fase13_final_evaluation.py`, `fase13_cv_reference.py`) — ningún artefacto propio, ninguna versión, ninguna procedencia trazable de forma independiente.
4. El threshold congelado (`39.354064`) vivía solo dentro de `frozen_rejection_config.json`, sin hash de contenido ni referencia explícita a qué covarianza lo calibró.
5. No existía ningún mecanismo que impidiera combinar `catalog_release` + `covariance_release` + `threshold_release` incompatibles.

---

## B. Cambios realizados (archivo por archivo)

| Archivo | Cambio |
|---|---|
| `tools/catalog/generate_species_id.py` | Auto-detecta registry previo en `--out`; hereda `visual_lifecycle_status` de especies ya existentes; especies nuevas inician en `DISCOVERED`. Nuevos flags `--previous-registry`, `--no-inherit-lifecycle`. |
| `tools/catalog/validation_gate.py` | `centroid_validation` ahora deriva de la consistencia interna (`group_a_count + group_b_count == total_centroids`), no de la constante `41`. |
| `tools/catalog/build_covariance_release.py` | **Nuevo**. Formaliza la covarianza Ledoit-Wolf como artefacto versionado (`.npz` + manifest con procedencia). |
| `tools/catalog/build_threshold_release.py` | **Nuevo**. Formaliza el threshold como artefacto versionado, ligado a `covariance_release`. Corregido durante esta misma tarea: el hash inicial incluía `created_at` (no determinista) — corregido para excluirlo. |
| `tools/catalog/check_release_compatibility.py` | **Nuevo**. Valida compatibilidad catalog+covariance+threshold; falla explícitamente ante mismatch. |
| `tools/catalog/run_open_set_evaluation.py` | **Nuevo**. Evaluación Open Set reproducible usando artefactos versionados (no recálculo ad-hoc). |
| `schemas/covariance_release.schema.json`, `schemas/threshold_release.schema.json` | **Nuevos**. |
| `open_set_release_architecture.md` | **Nuevo**. Arquitectura completa documentada. |
| `covariance/v1.0.0/`, `threshold/v1.0.0/` | **Nuevos** artefactos formalizados para el baseline histórico (reproducen, no recalibran). |
| `covariance/v1.1.0_CANDIDATE/`, `threshold/v1.1.0_CANDIDATE/` | **Nuevos**, heredados sin recalcular, para el release candidato de prueba. |
| Todo lo anterior de la sesión previa (`validation/new_species_test/fixture/*`, etc.) | **No modificado**, conservado como evidencia. |

**Nada en `evaluation/fase13/`, `visual_catalog/v1.0.0/`, `bioclip/checkpoints/` fue tocado.**

---

## C. Tests (comando ejecutado + resultado)

| Test | Comando | Resultado |
|---|---|---|
| Lifecycle: regresión 41 | `tools/catalog/tests/test_lifecycle_correction.py` | **PASS** — registry regenerado byte-idéntico |
| Lifecycle: especie nueva | (mismo test) | **PASS** — nueva especie → `DISCOVERED`, histórica → `DEPLOYED` |
| Gate dinámico N=41 | `tools/catalog/tests/test_validation_gate_dynamic_size.py` | **PASS** |
| Gate dinámico N=42 consistente | (mismo test) | **PASS** |
| Gate dinámico N=100 consistente | (mismo test) | **PASS** |
| Gate dinámico N=42 inconsistente | (mismo test) | **PASS** (`FAIL` correcto, detecta inconsistencia real) |
| Covarianza: reproducibilidad interna | `build_covariance_release.py` (2 cálculos internos) | **PASS** — idénticos |
| Covarianza: reproducibilidad cruzada vs Fase 13 | verificación manual | **PASS** — SHA256 idéntico (`81e53e5b...`) |
| Open Set: regresión vs métricas oficiales | `tools/catalog/tests/test_open_set_evaluation_regression.py` | **PASS** — AUROC/KAR/UDR/FAR idénticos a 1e-6 |
| Compatibilidad: caso compatible | `check_release_compatibility.py` (v1.0.0 real) | **PASS** — `COMPATIBLE` |
| Compatibilidad: caso incompatible | (mismo script, fixture con catalog_release alterado) | **PASS** — detecta e informa `INCOMPATIBLE`, exit 1 |
| Blind test: leakage F3/F4 vs TRAIN | `tools/catalog/tests/test_blind_test_no_leakage.py` | **FAIL (esperado, hallazgo real)** — ver sección D |
| Threshold: determinismo | regeneración 2 veces | **PASS** tras corregir exclusión de `created_at` |
| Regresión Antioquia/Cauca | `build_regional_package.py` x2 | **PASS** — 28/29 y 17/17 sin cambio |
| Inmutabilidad | hash SHA256 44 archivos + `git status` | **PASS** — 0 modificados |
| Multi-release (heredado de sesión previa) | `visual_catalog_v1.1.0_manifest_CANDIDATE.json` | **PASS** — 41→42, especie vieja en ambos, nueva solo en 1.1.0 |

---

## D. Open Set — qué fue calibrado y con qué datos

**Nada fue recalibrado en esta tarea.** `covariance_1.0.0` y `threshold_1.0.0` son
**formalizaciones** del cálculo ya existente de Fase 13 (mismo REFERENCE, mismo
CALIBRATION, mismo método Ledoit-Wolf, mismo valor `39.354064`), verificadas
byte-idénticas al original.

### 🔴 Hallazgo crítico descubierto durante esta tarea (Fase 7 — Blind Test)

Al construir el chequeo de no-leakage exigido, se descubrió que **F3 (766 imágenes
KNOWN) es un subconjunto EXACTO de TRAIN** (mismo `path` completo, no solo mismo nombre
de archivo):

```
F4 UNKNOWN (56 imgs):        0/56   overlap con TRAIN   → LIMPIO
F3 KNOWN Group A (197 imgs): 197/197 overlap con TRAIN  → LEAKAGE
F3 KNOWN Group B (569 imgs): 569/569 overlap con TRAIN  → LEAKAGE DIRECTO
```

Para las 32 especies Group B, esto es leakage **directo y severo**: el centroide se
calculó con estas mismas imágenes de TRAIN, y la evaluación "ciega" se hizo sobre las
mismas imágenes. Para Group A, el leakage es más sutil: el centroide viene de REFERENCE
(no de TRAIN), pero el **encoder** fue fine-tuneado viendo estas mismas imágenes de TRAIN.

**Esto no fue introducido por esta tarea ni por las correcciones previas de Fase 13** —
es un gap preexistente en el chequeo de contaminación original (que verificaba
REFERENCE↔CALIBRATION↔TRAIN, pero nunca F3/F4↔TRAIN). Se reporta aquí porque el enunciado
exigía explícitamente construir este chequeo ("Registrar claramente... el reporte debe
demostrar que no existe leakage") y el chequeo, al construirse honestamente, lo encontró.

Ver `blind_test_leakage_report.json` para el detalle completo y la interpretación
científica.

---

## E. Compatibilidad — qué releases son compatibles

```
visual_catalog_1.0.0  + covariance_1.0.0        + threshold_1.0.0        → COMPATIBLE
visual_catalog_1.1.0_CANDIDATE + covariance_1.1.0_CANDIDATE + threshold_1.1.0_CANDIDATE → COMPATIBLE
visual_catalog_1.0.0  + covariance_1.0.0        + threshold_1.1.0_CANDIDATE → INCOMPATIBLE (probado explícitamente)
```

---

## F. Inmutabilidad — hashes antes/después

- Baseline capturado en `validation/_baseline_pre_v1.1.0_test/hashes_before.txt` (44 archivos: `evaluation/fase13/`, `visual_catalog/v1.0.0/`, `bioclip/checkpoints/`)
- Comparado al final de esta tarea en `validation/new_species_test/hashes_after_fase15_audit.txt`
- `diff` exit code: **0**
- `git status --short` sobre las tres rutas: **vacío**

```
modified = 0
deleted  = 0
moved    = 0
```

---

## G. Regresión — resultados exactos

```
ANTIOQUIA + visual_catalog_1.0.0: 28/29 especies con soporte visual (idéntico a antes)
CAUCA     + visual_catalog_1.0.0: 17/17 especies con soporte visual (idéntico a antes)
AUROC = 0.624767 (idéntico a FASE13_FINAL_METRICS.json, usando artefactos versionados)
KAR   = 0.853786 (idéntico)
UDR   = 0.089286 (idéntico)
FAR   = 0.910714 (idéntico)
```

---

## H. Escalabilidad — qué tamaños fueron realmente probados

| N | Probado con | Resultado |
|---|---|---|
| 41 | Datos reales (REFERENCE/CALIBRATION/TRAIN/F3/F4) | PASS — arquitectura completa, incluida la evaluación Open Set reproducida |
| 42 | Fixture sintético (`Testus syntheticus`, imágenes reales prestadas de `Dendrobates_truncatus`) | PASS mecánico — `species_id`, embedding, centroide, `catalog_release` candidato, `regional_package`; gate global `FAIL` correcto (taxonomía sintética) |
| 50, 75, 100 | **No ejecutado** | No existen datos reales adicionales; se clasificó por inspección arquitectónica en la auditoría previa (`new_species_scalability_test.md`): ingeniería SAFE, covarianza/threshold compartidos **BLOCKER científico** sin recalibración desde ~50 especies en adelante |
| `validation_gate.py` con N sintético | 41 (real), 42 y 100 (sintéticos consistentes), 42 (sintético inconsistente) | PASS en los 4 casos — confirma que el gate ya no depende de la constante 41 |

**No se fabricaron datos biológicos ni especies reales para llegar a 50-100.**

---

## I. Limitaciones — separadas por tipo

**Limitación de ingeniería** (resuelta en esta tarea):
- Lifecycle incorrecto — corregido.
- Hardcode `==41` en `validation_gate.py` — corregido.
- Ausencia de artefactos versionados de covarianza/threshold — corregido.
- Ausencia de contrato de compatibilidad — corregido.
- Determinismo de `threshold_release` afectado por timestamp en el hash — corregido durante esta misma tarea.

**Limitación de datos** (no resuelta, no resoluble sin nueva recolección):
- No existe ninguna especie real, taxonómicamente verificable, fuera de las 41, con datos limpios y suficientes para demostrar el camino positivo completo sin fixture sintético.
- No hay datos reales para probar N=50/75/100.

**Limitación científica** (no resuelta, la más grave, descubierta en esta tarea):
- **F3 (KNOWN, todo el conjunto) tiene leakage total contra TRAIN.** El KAR/AUROC oficiales de Fase 13 miden en gran parte ajuste in-sample para las especies Group B, y una forma más sutil de leakage vía fine-tuning del encoder para Group A. Solo el lado UNKNOWN (F4, limpio) es una medida confiable de rechazo genuino.
- La covarianza y el threshold compartidos fueron calibrados sobre solo 9-10 especies (REFERENCE); heredarlos sin recalcular es defendible para +1 especie de prueba, pero no está científicamente validado para escalar a decenas o cientos de especies.

---

## J. Pendientes (no ocultos)

- Generar un conjunto KNOWN genuinamente held-out (nunca visto por TRAIN ni por el fine-tuning del encoder) para poder reportar un KAR válido.
- Persistir centroides como artefacto versionado independiente (hoy se recalculan desde embeddings cada vez que se necesitan).
- Persistir `encoder_sha256`/`dim`/`preprocessing_version` dentro de cada `.npz` de embeddings, no solo verificarlo externamente.
- Implementar la categoría `NO_CONCLUSIVE` en la evaluación Open Set (zona ambigua de score).
- Corregir el chequeo de contaminación original de Fase 13 para incluir F3/F4 vs TRAIN (fuera del alcance de esta tarea — tocaría archivos protegidos).
- Automatizar incorporación batch de N especies simultáneas (hoy el flujo es una especie a la vez).

---

# FINAL STATUS

```
Engineering scalability:      PASS
Open Set calibration:         PENDING   (artefactos formalizados y reproducidos correctamente,
                                          pero el blind test KNOWN tiene leakage confirmado — la
                                          calibración en sí no es científicamente valida para KAR)
Blind test:                   FAIL      (F3 KNOWN: leakage total confirmado contra TRAIN;
                                          F4 UNKNOWN: limpio, PASS)
Historical regression:        PASS
Immutability:                 PASS
Determinism:                  PASS
BioCLIP unchanged:            PASS
41-hardcode removed:          PASS
Lifecycle corrected:          PASS

Scientific scalability claim:
NOT YET SUPPORTED

Remaining blockers:
1. Leakage F3(KNOWN)↔TRAIN — invalida KAR/AUROC oficiales como medida de generalización
   para las 32 especies Group B, y parcialmente para Group A vía fine-tuning del encoder.
2. Covarianza/threshold calibrados sobre solo 9-10 especies; heredarlos sin recalcular es
   defendible para +1 especie, no validado para escalar a 50-100+.
3. Sin datos reales para probar tamaños intermedios (50, 75, 100).
```

**Afirmación honesta correspondiente al criterio de éxito**: "La arquitectura está
preparada para la recalibración y el experimento de escalabilidad — species_id estable,
covarianza y threshold versionados con procedencia, contrato de compatibilidad, gate sin
dependencia de constantes de tamaño — pero la validación científica a N especies queda
pendiente, y el descubrimiento de leakage en el blind test existente significa que incluso
la validación de 41 especies actual requiere ser revisada antes de usarse como base de
comparación para futuros releases."
