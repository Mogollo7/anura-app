# GEO-5 — Auditoria del catalogo regional real de Antioquia

## Gate de reproduccion (PASO 0)

`baseline_reproduction_v2.json` reproducido en esta sesion: AUROC = 0.5732919408781961,
diff = 0.0 vs oficial. **GATE PASSED.**

## Numero real de especies en el catalogo

El manifest desplegado `regional_packages/ANTIOQUIA/v1.0.0/manifest.json` reporta
`regional_catalog_scope.species_present_estimated = 29`, pero ese campo — leido literalmente
en su propio `caveat` — es un **subconjunto ya scrapeado con fotos**, explicitamente marcado
como incompleto ("falta cruzar con Batrachia y GBIF para incorporar las especies con
ocurrencia documentada y sin fotos propias").

El catalogo taxonomico real auditado en `COLOMBIA_ANURA/ANTIOQUIA/catalog/catalog_v1.csv` tiene
**291 especies** (291 `taxon_id` unicos, sin duplicados), resueltas via GBIF + iNaturalist:

| campo | conteo |
|---|---|
| `taxonomic_status = ACCEPTED` | 289 |
| `taxonomic_status = UNRESOLVED` | 2 |
| `visual_status = VISUAL_ENABLED` | 30 |
| `visual_status = VISUAL_EXCLUDED_REVIEW` | 4 |
| `visual_status = CATALOG_ONLY` (sin datos visuales) | 257 |
| `visual_data_status = DATA_SUFFICIENT` | 32 |
| `visual_data_status = DATA_LIMITED` | 2 |
| `visual_data_status = NO_VISUAL_DATA` | 257 |
| `occurrence_evidence = OCCURRENCE_CONFIRMED` | 182 |
| `occurrence_evidence = OCCURRENCE_PROBABLE` | 54 |
| `occurrence_evidence = OCCURRENCE_MARGINAL` | 51 |
| `occurrence_evidence = UNVERIFIED_PRESENCE` | 4 |

**291 >> ~29** confirmado: el catalogo taxonomico completo es ~10x mas grande que el numero
citado en el manifest desplegado.

## Especies con embeddings evaluables vs solo presencia geografica

Cruce por nombre cientifico canonico (via `training/taxonomia.py:canonico`) entre
`catalog_v1.csv` (291 especies) y las fuentes de embeddings:

- **41** especies tienen centroides de embeddings BioCLIP construidos a partir de
  `evaluation/fase13/embeddings/{reference,train}_embeddings.npz` (9 Group A + 32 Group B,
  misma logica del gate oficial de Fase 23A).
- De esas 41, **solo 33 estan presentes en el catalogo de Antioquia** (`catalog_v1.csv`). Las
  8 restantes (`Boana cinerascens`, `Boana lanciformis`, `Boana punctata`,
  `Dendropsophus mathiassoni`, `Dendropsophus reticulatus`, `Dendropsophus triangulum`,
  `Pithecopus hypochondrialis`, `Pristimantis vilarsi`) tienen embeddings evaluables pero **no
  ocurrencia confirmada/registrada en el catalogo regional de Antioquia** — son parte del
  conjunto nacional de 41 especies del clasificador visual pero fuera del alcance geografico
  auditado aqui. No se cuentan como "evaluables en Antioquia".
- De las 24 especies con set KNOWN curado (`clean_known_manifest.json`, fase16, usado en
  GEO2/3/4), **21 estan en el catalogo de Antioquia**; las 3 restantes son
  `Boana cinerascens`, `Boana lanciformis`, `Boana punctata` (mismo motivo: fuera del catalogo
  regional).

| Metrica | n | % de 291 |
|---|---|---|
| Especies con embeddings evaluables Y presentes en catalogo Antioquia | 33 | 11.3% |
| Especies con set KNOWN curado Y presentes en catalogo Antioquia | 21 | 7.2% |
| Especies SOLO con presencia geografica (sin ningun dato de imagen) | 258 | 88.7% |

**Conclusion honesta**: el catalogo regional completo (291 especies) es ~7-12x mas grande que
el conjunto evaluable con embeddings (33, o 21 si se exige ademas set KNOWN curado). La
evaluacion de identificacion (Top-1/Top-3/F1, open-set) SOLO puede hacerse sobre esas 33/21
especies. El 88.7% del catalogo (258 especies) queda sin ninguna posibilidad de evaluacion
visual con los datos actuales — son presencia geografica pura, sin foto propia procesada.

## Especies con pocos registros geograficos / cobertura insuficiente

- **109/291** especies tienen menos de 5 registros geograficos validos (`records_valid`) en el
  catalogo — cobertura de prior muy delgada para esas especies (aunque el prior con smoothing
  Bayesiano `alpha=2.0` sigue produciendo un valor no-cero, es cercano al neutral `1/291`).
- **4/291** especies tienen 0 celdas ocupadas (`cells_occupied=0`) — sin ninguna coordenada
  utilizable para asignarlas a una zona; su prior es puramente el fallback neutral en las 4
  zonas.

## Manifest reproducible

`antioquia_experimental_package/catalog_audited.csv` (291 filas) y
`antioquia_experimental_package/reproducibility_manifest.json` (hashes SHA-256 de todos los
inputs, seed=42, gate0, reglas duras confirmadas) documentan esta auditoria de forma
reproducible. Generados por `scripts/phase_geo5_main.py`.
