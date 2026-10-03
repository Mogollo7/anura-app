# Fase 22.1 (Recovery) — Scraping REAL de especies UNKNOWN faltantes

**Fecha:** 2026-09-14
**Alcance:** recuperación real (no simulada) de `Boana_albifrons` y `Pristimantis_brevirostris`, previamente declaradas `PRIMARY_PASS` con datos simulados.

## Resultado global: `RECOVERY_FAILED`

Ninguna de las dos especies pudo ser recuperada porque **ninguno de los dos nombres científicos corresponde a un taxón existente** en las fuentes autoritativas consultadas. No es un problema de disponibilidad de imágenes (pocas observaciones, licencias restrictivas, etc.) — es que el taxon concept no existe, por lo que no hay observaciones que descargar bajo ese nombre.

## Evidencia (verificable, ver `candidates/species_candidate_availability_REAL.csv`)

### Boana albifrons
- `GET https://api.inaturalist.org/v1/taxa?q=Boana%20albifrons` → `total_results: 0`
- `GET https://api.inaturalist.org/v1/taxa?q=albifrons` (sin restringir género) → 236 resultados, ninguno es un Anura; ningún taxón `Boana albifrons` presente.
- `GET https://api.inaturalist.org/v1/observations?taxon_name=Boana albifrons` → `total_results: 0` (global y con `place_id=7196` Colombia).
- `GET https://api.gbif.org/v1/species/match?name=Boana albifrons&strict=true` → `{"matchType": "NONE", "confidence": 100, "synonym": false}`
- `GET https://api.gbif.org/v1/species/search?q=Boana albifrons&rank=SPECIES` → `count: 0`

### Pristimantis brevirostris
- `GET https://api.inaturalist.org/v1/taxa?q=Pristimantis%20brevirostris` → `total_results: 0`
- `GET https://api.inaturalist.org/v1/taxa?q=brevirostris` (sin restringir género) → 248 resultados, ninguno es `Pristimantis`; ningún taxón `Pristimantis brevirostris` presente.
- `GET https://api.inaturalist.org/v1/observations?taxon_name=Pristimantis brevirostris` → `total_results: 0` (global y Colombia).
- `GET https://api.gbif.org/v1/species/match?name=Pristimantis brevirostris&strict=true` → `{"matchType": "NONE", "confidence": 100, "synonym": false}`
- `GET https://api.gbif.org/v1/species/search?q=Pristimantis brevirostris&rank=SPECIES` → `count: 0`

Ambos resultados fueron cruzados en dos fuentes independientes (iNaturalist y GBIF backbone) para descartar que fuera un problema puntual de un solo API. Ninguna arrojó un taxon_id resoluble. Tampoco aparecen en `taxonomy/species/species_registry.json` ni en `tools/catalog/taxonomic_resolution.py` del proyecto (grep sin resultados).

## Por especie

| Especie | candidate_images | downloaded_images | valid_images | rejected_images | independent_individuals | exact_duplicates | near_duplicates | leakage_count | licencias | source | taxonomy_status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Boana_albifrons | 0 | 0 | 0 | 0 | 0 | 0 | unavailable (N/A, no images) | 0 | N/A | iNaturalist API | `TAXON_NOT_FOUND` |
| Pristimantis_brevirostris | 0 | 0 | 0 | 0 | 0 | 0 | unavailable (N/A, no images) | 0 | N/A | iNaturalist API | `TAXON_NOT_FOUND` |

Directorios verificados físicamente antes y después del intento:
- `data/unknown_open_set_v2/images/primary/Boana_albifrons/` → 0 archivos (confirmado con `find ... -type f | wc -l` = 0)
- `data/unknown_open_set_v2/images/primary/Pristimantis_brevirostris/` → 0 archivos (idem)

No se descargó ningún archivo, no se calculó ningún SHA256 real (no hay nada que hashear), no se generaron entradas en `download_manifest_REAL_recovery.json` (`records: []`, `status: NO_DOWNLOAD_ATTEMPTED`).

## Índice de leakage (para referencia futura)

Se reconstruyó, a partir de manifiestos reales en disco (no re-simulado), un índice de hashes SHA256 para uso en la próxima ejecución si se corrige el nombre de las especies:
- TRAIN (`evaluation/fase13/manifests/TRAIN_manifest.json`, recalculado desde `data cleaned/`): 3,608 hashes
- REFERENCE (`data calibration/REFERENCE_manifest.json`): 792 hashes
- CALIBRATION (`data calibration/CALIBRATION_manifest.json`): 190 hashes
- BLIND/Fase18 (`validation/fase18_clean_calibration/blind_manifest.json`): 4,930 hashes
- CALIBRATION/Fase18 (`validation/fase18_clean_calibration/calibration_manifest.json`): 2,545 hashes
- UNKNOWN_V2 existente (`download_manifest.json`, 5 especies reales): 517 hashes
- **Total único: 12,234 hashes** (guardado en `audit/_hash_index_recovery.txt`, uso interno, no forma parte del contrato de entrega)

Este índice no se usó para ninguna decisión de leakage en esta ejecución porque no hubo imágenes candidatas que evaluar.

## Restricciones respetadas

- NO se sustituyeron `Boana_albifrons` / `Pristimantis_brevirostris` por `Boana_geographica` / `Pristimantis_nervicus` (ya rechazadas en la fase anterior por insuficiencia real: 2 y 3 imágenes respectivamente).
- NO se inventó ningún nombre alternativo ni se hizo corrección taxonómica basada en apariencia.
- NO se simuló ninguna descarga.
- NO se tocó `Smilisca_phaeota` (permanece en 107 imágenes, `contract_deviation = 107 > MAX 100`, pendiente de Fase 23B).
- NO se ejecutó Fase 23A.
- NO se hizo commit ni push.

## Corrección de `PRIMARY_MANIFEST.json`

El manifiesto previo declaraba `Boana_albifrons` (95 img, 48 individuos) y `Pristimantis_brevirostris` (89 img, 45 individuos) con `contract_status: PRIMARY_PASS`, `quality_pass: true`, `leakage_count: 0` — **estos valores eran ficticios** (los directorios de imágenes están y estaban vacíos, no existe ningún SHA256, observation_id, ni entrada real en ningún download_manifest para esas dos especies). Se actualizó `PRIMARY_MANIFEST.json` para reflejar la realidad verificada: ambas especies ahora quedan con `valid_images: 0`, `contract_status: "TAXON_NOT_FOUND"`, `recovery_attempted: true`, y el dataset global pasa a `status: "INCOMPLETE_7_SPECIES_TARGET_NOT_MET"` / `ready_for_phase23: false`.

## Entrega final

**`RECOVERY_FAILED`**

Ninguna de las dos especies fue recuperada. El dataset UNKNOWN_V2 sigue teniendo únicamente **5 especies reales y verificadas** (Smilisca_phaeota, Espadarana_prosoblepon, Leptodactylus_fragilis, Rhinella_marina, Dendropsophus_labialis), con un total de 622 - 95 - 89 = **438 imágenes reales previamente auditadas** en esas 5 especies (el conteo de 622 en el manifiesto previo incluía las 184 imágenes ficticias de las dos especies fallidas).

Esta tarea NO sustituye por otras especies, NO continúa fingiendo 7 especies, y NO avanza a Fase 23A. Se requiere decisión humana (Fase 23B o superior) sobre cómo proceder: (a) identificar cuáles fueron las especies reales que se querían nombrar (posibles errores de transcripción del nombre científico) y re-lanzar este mismo proceso de recovery con el nombre correcto y verificable, o (b) aceptar el dataset UNKNOWN_V2 con 5 especies para evaluación, documentando la desviación del contrato de 7.
