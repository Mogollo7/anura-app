# CATALOG_SCHEMA.md

Modelo de datos separando taxonomía, observación, imagen, embedding, centroide y release.
Ver `schemas/*.schema.json` para las definiciones formales (JSON Schema).

## Principio: 3 capas nunca deben confundirse

```
CATÁLOGO TAXONÓMICO          → biodiversidad/presencia (qué existe en la naturaleza)
CATÁLOGO VISUAL (release)    → qué puede identificar el modelo hoy
CATÁLOGO REGIONAL            → qué especies presentes en una región tienen soporte visual
```

Una especie puede ser `PRESENT_IN_ANTIOQUIA=true` y `VISUAL_CLASSIFIER_SUPPORTED=false`
simultáneamente. Esto no es un error, es el estado esperado para la mayoría de la biodiversidad
real frente a lo que el modelo soporta en un momento dado.

## Entidades

### Species (taxonomía)
Identidad estable, independiente del nombre científico.
```json
{
  "species_id": "ANU_COL_DEND_TRU_001",
  "scientific_name": "Dendrobates truncatus",
  "family": "Dendrobatidae",
  "genus": "Dendrobates",
  "authority": null,
  "synonyms": [],
  "taxonomic_status": "ACCEPTED",
  "source": "training/taxonomia.py",
  "verified_at": "2026-09-13"
}
```
`species_id` es inmutable. Si `scientific_name` cambia de grafía en el futuro (ej. una corrección
taxonómica), las referencias históricas (centroides, embeddings, releases) siguen apuntando al
mismo `species_id` — solo se actualiza el atributo `scientific_name` y se agrega a `synonyms`.

### Observation
Unidad primaria de datos biológicos — un individuo/evento de avistamiento, no una foto.
```json
{
  "observation_id": "OBS_COL_348295256",
  "source": "iNaturalist",
  "source_id": "348295256",
  "species_id": "ANU_COL_BOAN_BOA_XXX",
  "latitude": null,
  "longitude": null,
  "date": null,
  "location_precision": "UNKNOWN",
  "taxonomic_status": "ACCEPTED",
  "quality_status": "PENDING"
}
```
`source_id` corresponde al `obs_id` ya extraído en `training/manifiesto.json` (campo `grupo`,
formato `"Especie::obs_id"`) y en el patrón de nombre de archivo `col_obs_<id>_photo_<n>.jpg`.

### Image
```json
{
  "image_id": "IMG_<sha256_short>",
  "observation_id": "OBS_COL_348295256",
  "file_hash": "sha256...",
  "path": "Boana_boans/col_obs_348295256_photo_635191725.jpg",
  "width": null,
  "height": null,
  "annotation_status": "NONE",
  "segmentation_status": "NONE",
  "quality_status": "PENDING"
}
```
`file_hash` ya se calcula hoy (`SHA256` en REFERENCE/CALIBRATION manifests, `sha256` en algunos
otros) — este esquema solo formaliza el nombre de campo, no introduce un cálculo nuevo.

### Embedding (ver EMBEDDING_CONTRACT.md)
```json
{
  "embedding_id": "EMB_<hash>",
  "observation_id": "OBS_COL_348295256",
  "image_id": "IMG_<sha256_short>",
  "encoder_id": "bioclip_anura_v1",
  "encoder_sha256": "219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad",
  "embedding_dim": 512,
  "preprocessing_version": "hf-hub:imageomics/bioclip@create_model_and_transforms",
  "normalization_version": "L2"
}
```

### Centroid (versionado, pertenece a un release — ver RELEASE_VERSIONING.md)
```json
{
  "species_id": "ANU_COL_DEND_TRU_001",
  "centroid_version": "visual_catalog_1.0.0",
  "encoder_version": "bioclip_anura_v1",
  "dataset_version": "REFERENCE_798_v1",
  "individual_count": null,
  "image_count": 88,
  "source_split": "REFERENCE",
  "validation_status": "INDEPENDENT_CALIBRATION"
}
```
`individual_count: null` es intencional cuando no hay `obs_id`/`grupo` disponible en la fuente
(caso real de REFERENCE/CALIBRATION hoy) — **no se inventa un número**.

### CatalogRelease
```json
{
  "catalog_release": "visual_catalog_1.0.0",
  "species_count": 41,
  "group_a_count": 9,
  "group_b_count": 32,
  "method": "M5_LedoitWolf_Shared",
  "threshold_frozen": 39.354064,
  "status": "FROZEN",
  "validation_report": "validation/v1.0.0/validation_report.json"
}
```

### RegionalPackage
```json
{
  "package_id": "ANTIOQUIA",
  "package_version": "1.0.0",
  "catalog_release": "visual_catalog_1.0.0",
  "validation_status": "PILOT"
}
```

## Lo que NO se declara todavía

- `individual_count` real para REFERENCE/CALIBRATION → `null` (dato no disponible, ver
  `anura_reference_calibration_independencia.md`).
- `data_sufficiency_policy` con umbrales numéricos → NO se define aquí (ver sección
  correspondiente en `SPECIES_LIFECYCLE.md`, queda como política configurable pendiente).
