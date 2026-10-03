# GEO-3 — Reporte de cobertura geografica

Gate 0: AUROC reproducido = 0.5732919409 (oficial 0.5732919409, abs_diff = 0.0). PASSED.

## Cobertura UNKNOWN (n=620)
- Con observation_id: 620/620 (100%)
- Con lat/lon recuperadas: 620/620 (100%)
- Con zona asignada (grid 0.25deg, in_department): 262/620 (42.26%)
- Sin zona: 358/620 (57.74%)
- Comparacion vs GEO-2: identico (GEO-2 reporto 262/620 = 42.26%). **No hubo mejora de cobertura de zona** — el 100% de lat/lon ya estaba disponible en GEO-2; el techo de 42% no es un problema de recuperacion de coordenadas sino de que la mayoria de UNKNOWN caen fuera del area cubierta por `cell_zone_map_v1.csv` (Antioquia).

## Cobertura KNOWN (n=7475)
- Con observation_id: 7431/7475 (99.41%); 44 imagenes sin observation_id (quedan MISSING_GEOGRAPHY, no se inventa).
- Con lat/lon: 7431/7475 (99.41%)
- Con zona asignada: 2763/7475 (36.96%)

## Cobertura total (KNOWN+UNKNOWN combinados, n=8095)
- Con zona asignada: 3025/8095 (37.37%)

## Elevacion
- 0/4466 observation_id unicos tienen campo `elevation` en el cache. Confirmado (no se reinvirtio tiempo adicional en esto, tal como se indico).

## A.1 — Recuperacion adicional
Se verifico la union de observation_id necesarios para KNOWN (con obs_id) + UNKNOWN: 4466 IDs unicos.
- Faltantes en `cache/inat_observations_cache.json`: **0**
- Faltantes en `cache/inat_extracted.json`: **0**

Conclusion: el cache existente ya cubre el 100% de los observation_id evaluados en GEO-1/GEO-2. No hubo llamadas nuevas a la API de iNaturalist (no eran necesarias) ni a GBIF. **0 coordenadas adicionales recuperadas respecto a GEO-2.**

## A.2 — Validacion de coordenadas
- KNOWN: 7431/7431 coordenadas con lat/lon presentes estan en rango valido (-90..90, -180..180); 0 duplicados de observation_id detectados en el conjunto de imagenes con obs_id (los duplicados de observation_id entre imagenes de la misma observacion son esperados y no se cuentan como error, se deduplicaron a nivel de check de un ID repetido en la columna cruda).
- UNKNOWN: 620/620 coordenadas en rango valido.
- Ninguna observacion (KNOWN ni UNKNOWN) esta marcada `obscured=True` en el cache dentro del conjunto evaluado.
- Metodo de asignacion de zona: identico a GEO-1/GEO-2 (`cell_zone_map_v1.csv`, grid 0.25 grados, filtro `in_department`).

## A.3 — Leakage
- Interseccion directa observation_id de evaluacion vs `prior_zone_taxon_v2_clean.csv`: el prior esta agregado por (zone_id, scientific_name) y no conserva una columna `observation_id` (diseno intencional post-purga FASE12.2), por lo que no existe una columna para intersectar directamente en el archivo agregado.
- La garantia de no-leakage proviene del proceso de purga documentado en `prior_zone_taxon_v2_clean_manifest.json`: purge_rule excluye cualquier registro fuente cuyo observation_id aparezca en el set de evaluacion (columna individual_id de `per_sample_results.csv`). Cifras: n_records_original=15081, n_records_excluded=1214 (contaminados), n_records_purged_total=13867 registros fuente tras la purga, agregados en 1164 filas finales (zone_id x scientific_name) en `prior_zone_taxon_v2_clean.csv`.
- No se reprodujo el proceso de purga completo en GEO-3 (fuera de alcance quirurgico); se referencia el manifest existente de GEO-1/GEO-2 como evidencia.

## Veredicto de cobertura
No hubo mejora de cobertura respecto a GEO-2 (42.26% UNKNOWN se mantiene identico). El cache ya estaba saturado. El limitante real es geografico (area de cobertura del prior, restringido a Antioquia), no de recuperacion de datos.
