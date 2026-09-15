# OPEN_SET_PACKAGE_ISOLATION — Informe

Fecha: 2026-09-15 · Resultado: **`OPEN_SET_PACKAGE_ISOLATION_FIXED`**
Threshold usado: 39.35406371422803 (intacto). BioCLIP/ONNX, GEO4, familia, género, elevación, UI y Kotlin: sin cambios.

## 1. Causa raíz

Tras el bugfix `DYNAMIC_REMOVE_SPECIES_FAIL`, la única vía real por la que una especie de un paquete desactivado
seguía produciendo `ESPECIE_CONOCIDA` era **estado de catálogo obsoleto en memoria**:

- `LocalPackageManager.state` se leía de `state.json` una sola vez (`__init__`). Todas las consultas de catálogo
  usaban esa copia. Una desactivación hecha desde otra instancia/proceso era invisible para el runtime vivo:
  los 28 prototipos de Antioquia seguían en la matriz Open Set → centroide propio de *D. truncatus* a 25.01 ≤ 39.354
  → `ESPECIE_CONOCIDA = ANU_COL_DEND_TRU_001`, con `catalog_state` informando Antioquia como activo.
- `_save_state` volcaba el diccionario obsoleto completo: cualquier escritura posterior desde esa instancia
  **reactivaba Antioquia en disco**.

Agravante: la pertenencia al catálogo activo nunca fue una precondición independiente. `OpenSetReleaseAdapter`
aceptaba cualquier centroide cercano que recibiera (incluidos prototipos sin catálogo declarado o un centroide
residual del release), `MerlinFlow` aceptaba `ESPECIE_CONOCIDA` sin verificar `nearest_species_id`, y los candidatos
solo se filtraban contra el registro taxonómico estático.

**No es fuga (medido, sin cambios):** con catálogo correcto, la imagen de *D. truncatus* sin Antioquia se acepta como
*Dendropsophus triangulum* (Cauca, activa) con 38.83 < 39.354. Las 17 especies exclusivas de Antioquia nunca aparecen
como conocidas tras desactivarlo. Es permisividad del threshold, no pertenencia.

## 2. Cambios

| Archivo | Cambio |
|---|---|
| `package_manager.py` | `ActiveCatalogSnapshot` inmutable (+ `fingerprint`). `_refresh_state()` relee `state.json` en toda consulta/mutación. `active_catalog_snapshot()`: una lectura; prototipos/metadata solo de especies activas **y** declaradas en el manifest. `active_species/prototypes/species_metadata` delegan en la instantánea (mismo orden y desempate). |
| `runtime_adapters.py` | `OpenSetReleaseAdapter.assess`: pertenencia **antes** del threshold. Sin catálogo declarado → `CATALOG_MEMBERSHIP_UNDECLARED`; centroide más cercano fuera del catálogo → `NEAREST_CENTROID_NOT_IN_ACTIVE_CATALOG`. Evidencia `catalog_membership`. Modo sin gestor: catálogo = release congelado (sin cambio). |
| `merlin_runtime_pipeline.py` | Una instantánea por inferencia; candidatos filtrados por catálogo activo antes de geo; grupos desde la instantánea; `active_species_ids` al flow; `catalog_fingerprint`. `_active_catalog()` conserva su firma de 4 valores. |
| `merlin_flow.py` | `identify(active_species_ids=None)`: si se declara, candidatos fuera del catálogo se descartan y `ESPECIE_CONOCIDA` con especie aceptada fuera del catálogo → `NO_CONCLUYENTE` + `OPEN_SET_ACCEPTED_SPECIES_NOT_IN_ACTIVE_CATALOG`. Sin él (fixtures): idéntico. |
| `MOBILE_IDENTIFICATION_CONTRACT.md` | Regla documentada (aditiva). |
| `test_open_set_package_isolation.py` | Prueba nueva (8 escenarios + 8 inyecciones de fuga). |

## 3. Evidencia

- Antes del fix: `open_set_package_isolation_repro_before_fix.json` → 11 PASS / **6 FAIL** / 2 OBSERVED.
- Después: `open_set_package_isolation_result.json` → **17 PASS / 0 FAIL** / 2 OBSERVED.
- Regresión: `isolation_fix_regression_20260915/regression_comparison.json` (16 suites; salidas re-ejecutadas archivadas,
  artefactos históricos restaurados byte a byte).

Reproducir:

```
.\.venv-train\Scripts\python.exe validation\merlin_identification_flow\test_open_set_package_isolation.py
```

## 4. Riesgos restantes

1. Threshold permisivo (FAR 0.85, AUROC 0.538): la imagen de una especie desactivada puede aceptarse como **otra especie activa**.
2. Modo sin gestor (`MerlinRuntimePipeline()` / `assess()` sin catálogo) usa los 41 centroides del release: fuera del aislamiento por diseño histórico; producción debe exigir gestor.
3. `state.json` sin bloqueo ni escritura atómica: escrituras concurrentes pueden perder una actualización; una lectura truncada falla con excepción (fail-closed).
4. La especie aceptada (`open_set_evidence.nearest_species_id`) puede no coincidir con `candidates[0]`.
5. El ranking visual usa centroides del release filtrados por nombre, no los prototipos del paquete (hoy idénticos, Δ=0.0); un paquete futuro con prototipos distintos o especies fuera del pool de 41 divergiría.
