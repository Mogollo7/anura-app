# Auditoria de Contaminacion por Limpieza Manual (data dirty -> data cleaned)

Solo lectura. Ningun archivo de imagen, embedding, manifest o prior fue modificado, movido o borrado.

## Resumen ejecutivo

- Se comparo `data dirty/<especie>/fotos/` (17248 imagenes en 43 especies comunes) contra `data cleaned/<especie>/` (12254 imagenes) por nombre de archivo (busqueda recursiva, ya que `data dirty` anida las fotos en una subcarpeta `fotos/` y `data cleaned` las tiene planas).
- Archivos presentes en dirty y ausentes en cleaned (eliminados por el usuario): **4998** archivos, **2810** observation_id distintos.
- De esos, **2581** observation_id fueron eliminados COMPLETAMENTE (0 fotos de esa observacion quedaron en data cleaned) — rechazo total del usuario. Los **229** restantes son eliminaciones parciales (el usuario boto alguna(s) foto(s) del individuo pero conservo otra(s) foto(s) del mismo individuo/observacion).

## Resultado del cruce contra artefactos de evaluacion/entrenamiento

### 1. `validation/fase16_clean_open_set/clean_known_manifest.json` (KNOWN evaluado, 7475 imagenes)

- **0 observation_id completamente rechazados** aparecen en este manifest.
- Se encontraron 101 imagenes del manifest cuyo observation_id tuvo ALGUNA foto eliminada en la limpieza dirty->cleaned, pero en todos los 101 casos la foto especifica que permanece en el manifest **es una foto distinta** (mismo individuo/observacion, archivo diferente) que SI sigue existiendo fisicamente en `data cleaned/`. Esto es limpieza normal a nivel de foto individual (ej. remover una foto borrosa y conservar otra nitida del mismo sapo), no contaminacion. **Conclusion: el manifest KNOWN de evaluacion esta limpio respecto a rechazos totales del usuario.**

### 2. `COLOMBIA_ANURA/ANTIOQUIA/occurrences/records_v1.csv` (prior geografico)

- Este CSV contiene registros de ocurrencia (presencia especie/lat/lon) de GBIF e iNaturalist, no fotos. Los registros `inat:<observation_id>` son cruzables por observation_id.
- **870 de los 2581 observation_id completamente rechazados por el usuario** (limpieza de fotos) todavia aparecen como registro de ocurrencia en `records_v1.csv`, alimentando potencialmente `prior_zone_taxon_v2_clean.csv` / el prior geografico.
- **Interpretacion — no es contaminacion automatica**: `records_v1.csv` registra presencia geografica de la especie (dato de ocurrencia GBIF/iNat), independiente de si el usuario juzgo la(s) foto(s) de esa observacion como no aptas para el dataset de imagenes (borrosa, duplicada, mal encuadre, etc). Rechazar fotos no implica necesariamente que la identificacion/ubicacion de la observacion sea incorrecta. **Sin embargo**, si alguna de esas 870 observaciones fue rechazada por el usuario especificamente porque la identificacion de especie era dudosa o incorrecta (no solo por calidad de foto), entonces si contaminaria el prior geografico con presencia falsa. Esto **no se puede determinar automaticamente** porque no hay un campo que registre el motivo de eliminacion del usuario. Se listan como candidatos para revision manual, no como contaminacion confirmada.
- Ver columna `observation_id` en `CLEANUP_LINKED_PURGE_CANDIDATES_geographic_prior_candidates.csv` para la lista completa de los 870 casos (generado por separado, ver seccion Artefactos).

### 3. Embeddings de Fase 13 (`evaluation/fase13/embeddings/*.npz`) — CONTAMINACION CONFIRMADA

Metodologia: se calcularon SHA256 de los 4998 archivos eliminados (dirty->cleaned) y se compararon contra los SHA256 almacenados en `reference_embeddings.npz`, `train_embeddings.npz`, `calibration_embeddings.npz` y `data calibration/CALIBRATION_manifest.json` (comparacion por contenido exacto de bytes, no por nombre de archivo, ya que `data calibration/` usa nombres renombrados secuenciales tipo `Rhinella_alata_096.jpg`).

| Artefacto | Hits SHA256 |
|---|---|
| `evaluation/fase13/embeddings/reference_embeddings.npz` (798 img, centroides de 41 especies) | 0 |
| `evaluation/fase13/embeddings/train_embeddings.npz` | 0 |
| `evaluation/fase13/embeddings/calibration_embeddings.npz` (192 img KNOWN) | **15** |
| `data calibration/CALIBRATION_manifest.json` (192 img, fuente de calibration_embeddings.npz) | **15** (mismos 15) |

**HALLAZGO CONFIRMADO — CONTAMINACION REAL:** 15 imagenes en `calibration_embeddings.npz` / `data calibration/` son **identicas byte-a-byte (SHA256 exacto)** a imagenes que el usuario elimino de `data dirty` -> `data cleaned`:

- **11 imagenes de severidad ALTA**: pertenecen a **6 observation_id de Rhinella alata que el usuario rechazo POR COMPLETO** (0 fotos de esas observaciones quedaron en `data cleaned/Rhinella_alata/`). Rhinella alata tiene 21 imagenes en el set de calibracion — **11 de esas 21 (52%)** son fotos que el usuario juzgo no aptas para el dataset y elimino enteramente de su observacion, pero siguen siendo usadas para calibrar el umbral de decision (τ) del sistema.
- **4 imagenes de severidad MEDIA**: pertenecen a 1 observation_id de Dendrobates truncatus (161382931) donde el usuario elimino estas 4 fotos especificas pero conservo otras fotos del mismo individuo en `data cleaned/`. Dendrobates truncatus tiene 18 imagenes en el set de calibracion — 4 de 18 (22%) son fotos especificamente descartadas por el usuario (aunque el individuo/observacion en si no fue rechazado del todo).

**Por que esto importa**: segun `validation/fase23a_open_set_automatic/FASE23A_REPORT.md` (lineas 61-70), `calibration_embeddings.npz` es el unico split usado para calibrar el umbral operativo (`CALIBRATED_DIAGNOSTIC_KAR95_QUANTILE_KNOWN_ONLY`, cuantil KAR-95%) de los metodos Euclidean Raw, Cosine y Normalized Euclidean. Este mismo archivo se carga activamente en Fase16, Fase17, Fase18, Fase19, Fase20, Fase21, GEO1-6, `open_set_topography_v1`, `open_set_calibration_v1` y `merlin_identification_flow` (confirmado por grep de codigo, no es un artefacto legado). Es decir: **el umbral de decision que separa KNOWN de UNKNOWN en todo el pipeline actual de evaluacion open-set se calibro en parte con imagenes que el propio usuario juzgo no aptas para el dataset, incluyendo 11 fotos de observaciones que rechazo por completo.**

## Lista completa de candidatos a purgar

Ver `CLEANUP_LINKED_PURGE_CANDIDATES.csv` (15 filas) con: observation_id, especie, nombre de archivo eliminado, ruta original en `data dirty`, sha256, donde se encontro la contaminacion, y severidad.

| observation_id | especie | archivo eliminado (data dirty) | encontrado como (data calibration) | severidad |
|---|---|---|---|---|
| 195723558 | Rhinella alata | `col_obs_195723558_photo_344404409.jpg` | `Rhinella_alata_096.jpg` | ALTA |
| 195723558 | Rhinella alata | `col_obs_195723558_photo_344404451.jpg` | `Rhinella_alata_097.jpg` | ALTA |
| 199403508 | Rhinella alata | `col_obs_199403508_photo_351650990.jpg` | `Rhinella_alata_098.jpg` | ALTA |
| 150126953 | Rhinella alata | `col_obs_150126953_photo_258804016.jpg` | `Rhinella_alata_099.jpg` | ALTA |
| 203765608 | Rhinella alata | `col_obs_203765608_photo_360060679.jpg` | `Rhinella_alata_100.jpg` | ALTA |
| 231459279 | Rhinella alata | `col_obs_231459279_photo_411093820.jpg` | `Rhinella_alata_102.jpg` | ALTA |
| 222401291 | Rhinella alata | `col_obs_222401291_photo_393957523.jpg` | `Rhinella_alata_103.jpg` | ALTA |
| 195723558 | Rhinella alata | `col_obs_195723558_photo_344404249.jpg` | `Rhinella_alata_104.jpg` | ALTA |
| 195723558 | Rhinella alata | `col_obs_195723558_photo_344404275.jpg` | `Rhinella_alata_105.jpg` | ALTA |
| 195723558 | Rhinella alata | `col_obs_195723558_photo_344404298.jpg` | `Rhinella_alata_106.jpg` | ALTA |
| 195723558 | Rhinella alata | `col_obs_195723558_photo_344404352.jpg` | `Rhinella_alata_107.jpg` | ALTA |
| 161382931 | Dendrobates truncatus | `col_obs_161382931_photo_278937567.jpg` | `Dendrobates_truncatus_081.jpg` | MEDIA |
| 161382931 | Dendrobates truncatus | `col_obs_161382931_photo_278937655.jpg` | `Dendrobates_truncatus_082.jpg` | MEDIA |
| 161382931 | Dendrobates truncatus | `col_obs_161382931_photo_278940918.jpg` | `Dendrobates_truncatus_085.jpg` | MEDIA |
| 161382931 | Dendrobates truncatus | `col_obs_161382931_photo_278941020.jpg` | `Dendrobates_truncatus_087.jpg` | MEDIA |

## Que NO se encontro (confirmado limpio)

- El manifest KNOWN de evaluacion Fase16 (`clean_known_manifest.json`, 7475 imagenes, usado en Fase16-23A/GEO1-6/topography como pool KNOWN) **no contiene ninguna imagen de una observacion completamente rechazada por el usuario**.
- `reference_embeddings.npz` (centroides de 41 especies, Group A) y `train_embeddings.npz` (Group B) **no tienen coincidencias SHA256** con ningun archivo eliminado en la limpieza dirty->cleaned. Los centroides de referencia no estan contaminados por esta via.
- `TRAIN_manifest.json` (Fase13, 3608 entradas) no tiene coincidencias por nombre de archivo (no tiene SHA256 poblado para comparar por contenido).

## Metodologia detallada

1. **Diff dirty vs cleaned**: recorrido recursivo de `data dirty/<especie>/` (incluyendo subcarpeta `fotos/`) y `data cleaned/<especie>/`, comparando por nombre de archivo. 43 especies en comun (la carpeta `_cuarentena` en dirty no tiene contraparte en cleaned y se excluyo del diff, no es un caso especie x especie).
2. **Extraccion de observation_id**: patron `col_obs_<obsid>_photo_<photoid>.jpg` (formato dominante). Los 4998 archivos eliminados se resolvieron 100% (0 fallos de parseo).
3. **Clasificacion fully vs partially removed**: para cada (especie, observation_id) se conto cuantas fotos existen en dirty vs cuantas quedan en cleaned. 2581 observaciones perdieron el 100% de sus fotos (rechazo total); 229 conservaron al menos una foto (limpieza parcial a nivel de foto).
4. **Cruce por observation_id** contra `clean_known_manifest.json` y `records_v1.csv` (campo `record_id` con prefijo `inat:`).
5. **Cruce por SHA256 exacto** (no por nombre, dado que `data calibration/` usa nombres renombrados) entre los 4998 archivos eliminados (hasheados individualmente, ~5.7GB) y los campos `sha256` almacenados en `reference_embeddings.npz`, `train_embeddings.npz`, `calibration_embeddings.npz` y `CALIBRATION_manifest.json`. Esto detecta duplicados/copias exactas incluso si fueron renombrados durante la curacion del set de calibracion.
