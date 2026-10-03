# GEO-4 FASE A — Auditoría previa (PASO 0)

## 1. ¿Existía ya un prior a nivel género o familia?

**NO.** Se confirmó por inspección de `COLOMBIA_ANURA/ANTIOQUIA/priors/` y del
pipeline_dataset: el único prior geográfico existente es `prior_zone_taxon_v1.csv`
(especie × zona), y su derivado purgado de leakage `prior_zone_taxon_v2_clean.csv`
(usado por GEO-2/GEO-3). No existe ningún artefacto `prior_zone_genus_*` ni
`prior_zone_family_*` en el repo. Se construyeron ambos desde cero en este trabajo
(PASO 1), replicando el método exacto de `pipeline_dataset/zonas_finales_y_prior.py`
(vía `scripts/phase_clean_prior.py`, que ya lo replica para especie).

## 2. Gate de reproducción (visual puro)

`baseline_reproduction_v2.json` → `reproduced_auroc = 0.5732919408781961`,
`official_auroc = 0.5732919408781961`, `abs_diff = 0.0`, `gate_passed = True`.
**GATE 0 PASSED** — confirmado antes de construir cualquier artefacto nuevo, y
re-verificado en runtime al inicio de `phase_geo4_hierarchical_priors.py` y
`phase_geo4_main.py` (ambos abortan con `GEO4_BLOCKED.json` si el gate falla).

## Qué se reutilizó exactamente (sin modificar)

- `reproduced_scores_v2.npz`, `baseline_reproduction_v2.json` (gate visual puro)
- `prior_zone_taxon_v2_clean.csv` + su manifest (prior especie|zona purgado)
- `cache/inat_extracted.json` (coordenadas iNaturalist ya recuperadas — **cero
  llamadas nuevas a la API**)
- `COLOMBIA_ANURA/ANTIOQUIA/zones/cell_zone_map_v1.csv` (geometría de zonas congelada)
- `COLOMBIA_ANURA/ANTIOQUIA/occurrences/records_v1.csv` (fuente cruda de registros,
  misma que usa `prior_zone_taxon_v2_clean.csv`)
- `validation/fase16_clean_open_set/clean_known_manifest.json` +
  `clean_known_embeddings.npz` (KNOWN pool, 24 especies, 7475 imágenes)
- `validation/fase23a_open_set_automatic/embeddings/unknown_embeddings.npz` (620 UNKNOWN)
- `evaluation/fase13/embeddings/{reference,train}_embeddings.npz` (centroides 41 especies:
  9 Group A + 32 Group B)
- `training/taxonomia.py` (`canonico`, `genero_de`, `familia_de`) — usado para el
  desglose same/different-genus (idéntico a `GEO2_SUBGROUP_ANALYSIS.csv`)
- `COLOMBIA_ANURA/ANTIOQUIA/catalog/catalog_v1.json` — fuente de `genus`/`family` por
  `taxon_id` para los **291** taxa del catálogo departamental (más amplio que
  `training/taxonomia.py`, que solo cubre las 41 especies entrenadas; se usó
  exclusivamente para construir los priors jerárquicos de PASO 1, no para las 41
  clases candidatas de PASO 3/4, donde `taxonomia.py` sí cubre el 100%)

## Qué se construyó nuevo

- `prior_zone_genus_v1.csv` / `GEO4_prior_zone_genus_v1_manifest.json`
- `prior_zone_family_v1.csv` / `GEO4_prior_zone_family_v1_manifest.json`
- `scripts/phase_geo4_hierarchical_priors.py` (PASO 0+1)
- `scripts/phase_geo4_main.py` (PASO 2-4: fórmula jerárquica, precisión de especie,
  impacto en Open Set)
- Todos los `GEO4_*.json/.csv` listados en el reporte final.

No se tocó `prior_zone_taxon_v1.csv`, ningún archivo `GEO2_*`/`GEO3_*`,
`fase16_clean_open_set/`, `fase23a_open_set_automatic/`, `regional_packages/ANTIOQUIA/v1.0.0/`,
encoder ni embeddings oficiales. No hubo reentrenamiento ni nuevos embeddings.
