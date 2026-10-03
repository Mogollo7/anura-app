# Prueba de Escalabilidad End-to-End: Incorporación de Nueva Especie (41 → 42)

**Fecha**: 2026-09-13
**Ejecutado por**: sesión de validación arquitectónica, sin commit/push (pendiente de revisión)

---

## A. Especie utilizada

| Campo | Valor |
|---|---|
| `scientific_name` declarado | `Testus syntheticus` |
| `canonical_name` | `Testus_syntheticus` |
| `species_id` | `ANU_COL_TEST_SYN_001` |
| Real o sintético | **SYNTHETIC_TEST_ONLY** |
| Fuente de imágenes | 25 fotografías **reales** de `data cleaned/Dendrobates_truncatus/` (reutilizadas explícitamente, no inventadas — ver `validation/new_species_test/fixture/FIXTURE_DECLARATION.json`) |

**Justificación del fixture sintético**: se auditaron todas las carpetas de `data cleaned/` fuera de las 41 especies visuales. Solo existen 2 candidatas reales (`Hyloxalus_picachos`: 15 imgs, `Sachatamia_electrops`: 41 imgs), ambas ya documentadas en `training/taxonomia.py` como excluidas por **integridad de datos** (duplicados exactos), no por cantidad. Ninguna permite demostrar honestamente el camino positivo completo (embedding → centroide → release aprobado). Por la regla 8 del encargo, se usó un fixture sintético, con imágenes reales prestadas y declaración explícita de su naturaleza no biológica.

---

## B. Pipeline ejecutado

```
taxonomy (taxonomia_v1_1_0_candidate.py, extensión aditiva)
  → species_id (generate_species_id.py, determinista, 0 colisiones)
  → data (25 imágenes → 15 individuos, distinción observation/image respetada)
  → embedding (BioCLIP congelado real, encoder_sha256 verificado idéntico a Fase 13)
  → centroid (compute_centroids() idéntica a Fase 13)
  → validation gate (7 pasos evaluados individualmente)
  → release candidato v1.1.0 (aislado, NO promovido a visual_catalog/ real)
  → regional package (fixture regional, join por species_id)
```

---

## C. Resultados

| Etapa | Resultado | Evidencia |
|---|---|---|
| species_id | **PASS** | `ANU_COL_TEST_SYN_001`, determinismo confirmado (diff byte-a-byte idéntico en 2 ejecuciones), 0 colisiones, las 41 especies originales conservaron su ID exacto |
| taxonomy | **FAIL (esperado)** | La especie es sintética por diseño — no existe en ninguna fuente taxonómica real. El gate rechaza correctamente, no inventa un PASS |
| data quality | **PASS** | 25/25 imágenes cargadas sin error; 15 individuos correctamente distinguidos de 25 imágenes (multi-foto por observación NO cuenta como individuos independientes) |
| embedding | **PASS** | `encoder_sha256=219e860e...` idéntico al usado en Fase 13; dimensión 512; mismo preprocessing (`create_model_and_transforms(hf-hub:imageomics/bioclip)`) |
| centroid | **PASS** | Calculado con la misma función `compute_centroids()` de Fase 13; hash determinista verificado en 2 ejecuciones |
| covariance/threshold | **PASS (heredado, no recalculado)** | v1.1.0 usa la covarianza Ledoit-Wolf y τ=39.354064 de v1.0.0 sin modificarlos — decisión documentada en `open_set_v1_1_0_decision.json`, con limitación científica explícitamente declarada (no resuelta) |
| open_set_evaluation | **PENDING** | No existe evidencia de AUROC/KAR/UDR/FAR específica para esta especie — no se generó un conjunto de evaluación análogo a F3/F4 |
| blind_test | **PENDING** | No existe conjunto ciego para esta especie específica |
| release (v1.1.0) | **PASS (candidato, no promovido)** | 41→42 especies demostrado; nueva especie ausente en v1.0.0 y presente en v1.1.0; especies antiguas presentes en ambos |
| regional package | **PASS** | Fixture regional con la especie sintética presente: ausente contra v1.0.0, presente contra v1.1.0; join exclusivamente por `species_id` |

**`gate_result` global: FAIL`** — correcto y esperado, documentado en `validation_report_v1.1.0_candidate.json`. No se declaró `READY_FOR_PRODUCTION` ni `PASS` artificial en ningún punto.

---

## D. Inmutabilidad

```
Fase 13 (evaluation/fase13/)     = UNCHANGED  (44/44 hashes SHA256 idénticos antes/después; git status vacío)
visual_catalog/v1.0.0/           = UNCHANGED  (incluido en el mismo chequeo de hashes)
bioclip/checkpoints/ (encoder)   = UNCHANGED  (incluido en el mismo chequeo de hashes)
```

Verificación doble: hash SHA256 de 44 archivos (evaluation/fase13/ + visual_catalog/v1.0.0/ + bioclip/checkpoints/) capturado antes de iniciar la prueba y comparado al final — `diff` exit code 0. Confirmado independientemente con `git status --short` sobre las 3 rutas — salida vacía en las tres.

```
modified = 0
deleted  = 0
moved    = 0
```

---

## E. Escalabilidad — Respuestas objetivas

**¿Puede ANURA incorporar una nueva especie sin reentrenar BioCLIP?**
Sí, demostrado con evidencia real: el encoder se usó exactamente igual (mismo SHA256, mismo checkpoint) para generar embeddings de la especie de prueba. El pipeline mecánico (`species_id → embedding → centroid`) no requiere ni invoca ningún paso de entrenamiento.

**¿Puede crear un nuevo release sin modificar releases anteriores?**
Sí, demostrado: `visual_catalog_1.0.0` permaneció con 41 especies, hash-idéntico antes/después; el candidato `v1.1.0` (42 especies) se construyó en un espacio completamente separado.

**¿Puede un paquete regional utilizar un release visual específico?**
Sí, demostrado en Fase 12: el mismo departamento de prueba produjo resultados distintos y correctos según el `--catalog-release` pasado como parámetro (28/29 contra v1.0.0 real vs. incluyendo la especie de prueba contra v1.1.0 candidato).

**¿Puede una especie estar presente regionalmente pero no tener soporte visual?**
Sí, demostrado con datos reales en producción, no solo en el fixture: `Sachatamia electrops` está presente en Antioquia (biodiversidad confirmada) pero sin `species_id` en el registry visual — reportado explícitamente como `regional_species_taxonomically_unresolved`, nunca ocultado ni fusionado con las especies soportadas.

**¿Puede una futura v1.1.0 coexistir con v1.0.0?**
Sí, demostrado explícitamente con asserts (Fase 14): `species_new ∉ v1.0.0`, `species_new ∈ v1.1.0`, `species_old ∈ v1.0.0`, `species_old ∈ v1.1.0`, simultáneamente.

**¿Existen límites arquitectónicos para pasar de 41 a 100+ especies?**

| Componente | 42 | 50 | 100 | 200 | 500 | Clasificación |
|---|---|---|---|---|---|---|
| `generate_species_id.py` | SAFE | SAFE | SAFE | SAFE | WARNING* | genérico sobre `np.unique`; *colisión posible si >999 especies comparten género+3 letras de epíteto |
| `build_catalog_release_manifest.py` | SAFE | SAFE | SAFE | SAFE | SAFE | genérico, sin límite de tamaño ni nombres hardcodeados |
| `build_regional_package.py` | SAFE | SAFE | SAFE | SAFE | SAFE | join por sets, sin límite; probado con 2 departamentos reales |
| `resolve_regional_species_ids.py` | SAFE | SAFE | SAFE | SAFE | SAFE | genérico sobre archivos existentes |
| `evaluation/fase13/fase13_final_evaluation.py` | **BLOCKER** | BLOCKER | BLOCKER | BLOCKER | BLOCKER | `assert ==41, ==9, ==32` — pero es intencional: este script es el baseline **congelado**, nunca debe reutilizarse para releases futuros |
| `tools/catalog/validation_gate.py` (línea 40, modo retrofit) | WARNING | WARNING | WARNING | WARNING | WARNING | `== 41` hardcodeado; el modo retrofit es específico de v1.0.0 por diseño, pero el valor debería derivarse de `centroid_audit`, no estar fijo — riesgo de copiar el script sin adaptarlo |
| Covarianza Ledoit-Wolf compartida | WARNING | WARNING | **BLOCKER** | BLOCKER | BLOCKER | heredada sin recalcular (decisión de esta prueba); estimada sobre solo 9 especies (798 imgs) — válida científicamente para 1-2 especies adicionales, cuestionable estadísticamente a partir de ~50, sin resolver el mecanismo real |
| Threshold congelado (39.354064) | WARNING | WARNING | **BLOCKER** | BLOCKER | BLOCKER | mismo problema: calibrado sobre 10 especies en CALIBRATION; no re-evaluado al crecer el catálogo |
| `covariance_release`/`threshold_release` como artefactos versionados | — | — | — | — | — | **GAP DE DISEÑO**: `RELEASE_VERSIONING.md` los documenta conceptualmente, pero no existe implementación real — hoy solo viven dentro de `frozen_rejection_config.json` de Fase 13, no versionados independientemente |
| Incorporación batch (N especies a la vez) | WARNING | WARNING | WARNING | WARNING | WARNING | el flujo probado es "una especie a la vez"; agregar decenas simultáneamente es conceptualmente igual (`species_ids` es una unión de conjuntos) pero no existe script de batch — trabajo manual repetido N veces |
| `pipeline_dataset/construir_paquete_departamental.py` | SAFE | SAFE | SAFE | SAFE | SAFE | ya parametrizado por departamento, sin límite de especies en su lógica |

---

## Conclusión objetiva

**El pipeline de ingeniería (species_id → embedding → centroid → release manifest → regional package) es genuinamente escalable de 41 a cientos de especies sin reentrenar BioCLIP y sin modificar releases anteriores.** Esto quedó demostrado con evidencia real (hashes, asserts, ejecución doble para determinismo), no solo declarado.

**La escalabilidad científica del método Open Set (Mahalanobis + Ledoit-Wolf + threshold) es la limitación real, no la ingeniería.** Agregar 1 especie heredando covarianza/threshold es una decisión defendible (documentada explícitamente como tal). Agregar decenas o cientos de especies sin recalibrar la covarianza compartida — estimada sobre solo 9 especies de las 41+N — no tiene ninguna garantía estadística y se clasifica como **BLOCKER** a partir de escalas moderadas (~50 especies en adelante), no por falta de código, sino porque el propio Fase 13 nunca fue diseñado para eso.

**No se recomienda** interpretar el resultado de esta prueba como "ANURA está listo para 100+ especies". Está listo para **agregar releases nuevos mecánicamente**; la validez científica de cada release nuevo (más allá de 1-2 especies) requiere una nueva ronda de calibración tipo Fase 13, no solo una nueva ejecución de `build_catalog_release_manifest.py`.
