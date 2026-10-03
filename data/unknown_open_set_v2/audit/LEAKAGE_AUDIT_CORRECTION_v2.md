# Corrección al leakage audit oficial — contaminación de etiquetado Dendropsophus_labialis / Dendropsophus_molitor

Fecha: 2026-09-14
Alcance: `data/unknown_open_set_v2/` (Fase 23A UNKNOWN pool) vs `data cleaned/Dendropsophus_molitor/` (KNOWN pool completo, 111 archivos)

## Resumen ejecutivo

El `leakage_audit.csv` oficial de Fase 23A compara imágenes UNKNOWN contra el pool KNOWN por **hash SHA-256 exacto**. Esa comparación es ciega a un caso real presente en el dataset: la **misma observación de iNaturalist** (mismo `observation_id`) fue descargada dos veces en momentos distintos — una vez etiquetada como *Dendropsophus_labialis* (para el pool UNKNOWN de open-set) y otra como *Dendropsophus_molitor* (para el pool KNOWN de entrenamiento/evaluación) — porque el consenso de identificación de la comunidad de iNaturalist para esa observación cambió entre labialis y molitor en distintos momentos de scraping. Los archivos resultantes tienen bytes distintos (re-codificación/re-descarga: distinta compresión JPEG, distinto tamaño, posible reprocesamiento), por lo que el hash SHA-256 no coincide y la observación pasa como `CLEAN` en la auditoría oficial. Es un **falso negativo** de esa auditoría, no un error del método SHA-256 en sí — el método simplemente no está diseñado para detectar duplicación a nivel de "misma observación real", solo a nivel de "mismo archivo de bytes".

## Causa raíz

1. `data/unknown_open_set_v2/images/primary/Dendropsophus_labialis/` fue poblado con observaciones etiquetadas por iNaturalist como *Dendropsophus labialis* en el momento de la descarga para el pool "UNKNOWN" (especie fuera del catálogo de 41 especies conocidas).
2. `data cleaned/Dendropsophus_molitor/` (pool KNOWN, especie #within catálogo) fue poblado independientemente, en otro momento de scraping, con observaciones etiquetadas como *Dendropsophus molitor*.
3. iNaturalist usa un sistema de consenso comunitario para el `taxon_id` de una observación: el mismo `observation_id` puede mostrar una especie distinta según cuándo se consulta, si la comunidad revisa/cambia el ID. *D. labialis* y *D. molitor* son especies morfológicamente muy similares y con historial taxonómico confuso en Colombia — un candidato natural a re-identificación comunitaria.
4. Resultado: 34 `observation_id` únicos terminaron representados en AMBOS pools con la etiqueta de especie del momento de cada descarga, y con archivos JPEG de bytes distintos por cada descarga (por eso `leakage_audit.csv` no los marca).

## Alcance real (recalculado en esta sesión, comparación completa)

- Pool UNKNOWN *Dendropsophus_labialis* original (congelado en `unknown_embeddings.npz`, extraído antes de cualquier limpieza manual): **74 imágenes**, **43 `observation_id` únicos**.
- Contra **TODO** `data cleaned/Dendropsophus_molitor/` (111 archivos, 77 `observation_id` únicos — no solo el subconjunto evaluado en Fase 13/16).
- Intersección: **34 de 43 `observation_id`** de labialis (**79.1%**) coinciden con un `observation_id` presente en el pool KNOWN de molitor.
- Esos 34 `observation_id` corresponden a **56 de las 74 imágenes** originales de labialis (**75.7%**).
- Nota: una revisión preliminar anterior (informal, sobre un subconjunto del pool KNOWN) había estimado 31 `observation_id` afectados. La comparación exhaustiva contra el pool KNOWN completo realizada en esta sesión eleva la cifra a **34**. Se documenta aquí el número verificado y reproducible; el detalle observation_id por observation_id está en `LEAKAGE_AUDIT_CORRECTION_v2.csv`.

## Estado actual en disco (al momento de esta auditoría)

De las 56 imágenes contaminadas originales:
- **50 siguen en disco** en `data/unknown_open_set_v2/images/primary/Dendropsophus_labialis/` (contaminan cualquier evaluación que use ese directorio tal cual).
- **6 ya fueron borradas manualmente por el usuario** durante su limpieza de calidad previa (sin saber del bug) — ver `USER_MANUAL_DELETIONS_RECONCILIATION.md` para el detalle exacto.

Los embeddings congelados de Fase 23A (`unknown_embeddings.npz`) contienen las 74 imágenes originales (incluidas las 56 contaminadas), extraídos antes de cualquier deleción manual — por lo tanto todos los resultados ya reportados de Fase 23A/GEO-1→6/`open_set_topography_v1` **incluyen** esta contaminación tal como fueron calculados, y siguen siendo válidos como registro histórico, pero deben leerse con esta advertencia: una fracción sustancial (20.6% de los falsos aceptados totales, según `TOPOGRAPHIC_CONTEXT_REPORT.md`) del par de confusión labialis→molitor es en realidad la misma observación biológica etiquetada dos veces, no una confusión visual entre dos especies genuinamente distintas.

## Por qué el audit oficial no lo detectó

`leakage_audit.csv` fue diseñado para detectar **fugas de datos por duplicación exacta de archivo** (mismo binario en ambos splits/pools), un problema de pipeline de descarga/copiado. No fue diseñado para detectar **duplicación semántica de observación con etiqueta de especie inconsistente entre dos descargas separadas en el tiempo**, que es un problema de fuente de verdad taxonómica (iNaturalist), no de manejo de archivos. Ambos son fugas de datos reales pero de naturaleza distinta; el primero se detecta con SHA-256, el segundo requiere comparar `observation_id` (metadato extraído del nombre de archivo `col_obs_<id>_photo_<id>.jpg`) entre pools, cruzando por especie candidata a confusión.

## Archivos de esta corrección

- `LEAKAGE_AUDIT_CORRECTION_v2.csv` — 56 filas, una por imagen UNKNOWN contaminada: `observation_id`, archivo UNKNOWN, si sigue en disco o fue borrado, archivo(s) KNOWN correspondiente(s) en `Dendropsophus_molitor/`.
- Este archivo (`LEAKAGE_AUDIT_CORRECTION_v2.md`).

## No se modificó ningún artefacto original

No se tocó `leakage_audit.csv`, `PRIMARY_MANIFEST.json`, `unknown_embeddings.npz`, ni ningún artefacto de Fase 23A/GEO-1→6/`open_set_topography_v1`/`merlin_identification_flow`/`fase23a_geographic_context`. Esta corrección es un documento nuevo y separado.
