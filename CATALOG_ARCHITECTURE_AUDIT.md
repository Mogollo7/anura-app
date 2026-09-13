# CATALOG_ARCHITECTURE_AUDIT.md

Auditoría de solo lectura previa al diseño de arquitectura de crecimiento.
Ningún archivo existente fue modificado, movido ni eliminado para producir este documento.

Fecha: 2026-09-13

---

## 1. Estructura actual real (verificada)

```
D:\Anura\
├── bioclip/checkpoints/          — encoder + clasificador (.pt/.onnx, SIN versión en el nombre)
├── training/
│   ├── taxonomia.py               — módulo Python: GENERO_A_FAMILIA, ESPECIES (41), ALIAS
│   └── manifiesto.json            — 3609 registros train/val/test, campo "grupo"="Especie::obs_id"
├── data calibration/
│   ├── REFERENCE_manifest.json    — 798 registros, 10 especies, campos: Species/Genero/Familia/
│   │                                 OriginalPath/FileName/SHA256/Dataset — SIN obs_id/grupo
│   ├── CALIBRATION_manifest.json  — 192 registros, misma estructura, SIN obs_id/grupo
│   ├── FASE12_1_INDEPENDENCE_AUDIT.md — documenta ausencia formal de individual_id/obs_id
│   └── FASE12_2_DUPLICATE_CORRECTION.json — corrección de 3 duplicados cross-split (aplicada)
├── evaluation/
│   ├── open_set_v1/               — Fases 2-11 (dataset, closed-set, kNN, ensemble, calibración)
│   └── fase13/                    — BASELINE CONGELADO (ver sección 3)
├── COLOMBIA_ANURA/ANTIOQUIA/
│   ├── SPECIES/COL_ANURA_00NN/species.json  — catálogo regional GBIF/iNaturalist (taxón, NO visual)
│   └── packages/v1.0.0/           — paquete regional versionado (.sqlite + CHECKSUMS.sha256)
├── pipeline_dataset/
│   └── construir_paquete_departamental.py  — YA acepta --departamento (genérico, reutilizable)
└── Second Brain/Brain/            — vault Obsidian, ya enlazado con 05_OPEN_SET y 15_DECISIONS
```

## 2. Hechos verificados (sin inventar)

| Hecho | Valor | Fuente |
|---|---|---|
| Especies visuales activas en `taxonomia.py` | 41 | conteo directo de `ESPECIES` |
| Especies excluidas explícitamente (huérfanas) | Hyloxalus_picachos, Sachatamia_electrops | comentarios inline en `taxonomia.py`, con razón documentada |
| Mecanismo de alias ya existente | `ALIAS` dict en `taxonomia.py`, incluye `"Pristimantis acanthinus": "Pristimantis_achatinus"` | `training/taxonomia.py:84-90` |
| Encoder SHA256 verificado | `219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad` | `fase13_pre_audit.py`, `generar_manifest_antioquia.py` |
| Dimensión de embedding | 512 | `reference_embeddings.npz['embeddings'].shape[1]` (verificado en Fase 13) |
| Método Open Set congelado | `M5_LedoitWolf_Shared` | `frozen_rejection_config.json` |
| Threshold congelado | `39.354064` (@95% KAR) | `frozen_rejection_config.json` |
| Centroides release baseline | 41 (Group A=9, Group B=32) | `centroid_source_audit.json` |
| REFERENCE / CALIBRATION / TRAIN | 798 / 192 / 3608 imágenes | `.npz` de Fase 13 |
| Campo obs_id/grupo en REFERENCE/CALIBRATION | **NO EXISTE** | lectura directa de un registro (ver abajo) |
| Campo grupo (individuo) en `training/manifiesto.json` | SÍ existe: `"grupo": "Boana_boans::348295256"` | lectura directa de un registro |

Registro real de `REFERENCE_manifest.json` (evidencia, no inventado):
```json
{"Species": "Dendrobates truncatus", "Genero": "Dendrobates", "Familia": "Dendrobatidae",
 "OriginalPath": "...", "FileName": "...", "SHA256": "...", "Dataset": "REFERENCE"}
```

## 3. Qué debe permanecer congelado (BASELINE, no se toca)

```
BASELINE RELEASE
-----------------
catalog:            41 especies (9 Group A / 32 Group B)
method:             M5_LedoitWolf_Shared
embedding_dim:      512
threshold_frozen:   39.354064 (@95% KAR)
encoder_sha256:     219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad
status:             FROZEN
```

Archivos que esta tarea NO modifica, NO mueve, NO elimina:
`evaluation/fase13/**`, `bioclip/checkpoints/*.onnx`, `bioclip/checkpoints/*.pt`,
`data calibration/REFERENCE_manifest.json`, `data calibration/CALIBRATION_manifest.json`,
`training/manifiesto.json`, `evaluation/fase13/ANTIOQUIA_v1.0.0_manifest.json`.

## 4. Qué puede reutilizarse tal cual

- `compute_centroids(X, y)` — genérico sobre `np.unique(y)`, no requiere reescritura para N especies.
- `training/taxonomia.py` — ya tiene el mecanismo de alias que habría prevenido el bug
  `acanthinus`/`achatinus` si `evaluation/fase13/` lo hubiera importado en vez de reimplementar
  su propia función `canonical_species_name()` local. **Ver WARNING en sección 6.**
- `pipeline_dataset/construir_paquete_departamental.py` — ya parametrizado por `--departamento`.
- Mecanismo de contaminación por SHA256 + obs_id (existe, pero disperso en ≥4 scripts distintos
  con lógica ligeramente distinta cada uno).

## 5. Qué falta (gaps reales, no especulativos)

1. **Sin `species_id` estable** — todo el sistema usa el nombre científico como clave primaria.
2. **Sin modelo de observación separado de imagen** — solo `training/manifiesto.json` distingue
   individuo (`grupo`) de imagen; REFERENCE/CALIBRATION no.
3. **Sin contrato de encoder versionado** — el SHA256 se verifica ad-hoc en un script, no está
   embebido como metadata en los `.npz` de embeddings.
4. **Sin versionado de release de catálogo** — "41 especies" vive implícitamente en `taxonomia.py`
   y en los `assert` de `fase13_final_evaluation.py`, no como artefacto de release explícito.
5. **Sin gate reutilizable** — `run_fase13_pipeline.py` es un runner lineal de scripts standalone.
6. **Dos generadores de paquete regional divergentes** (uno genérico, uno hardcodeado a Antioquia).

## 6. Inconsistencias detectadas (reportadas, NO corregidas)

**WARNING-1**: `training/taxonomia.py` ya contiene el alias
`"Pristimantis acanthinus": "Pristimantis_achatinus"` (línea 88), pero
`evaluation/fase13/fase13_final_evaluation.py` reimplementó su propia normalización local
(`canonical_species_name()`) sin importar `taxonomia.py`. El bug que corregimos manualmente en esta
sesión ya tenía una solución existente en el código, simplemente no conectada. No se corrige aquí
(tocaría Fase 13); se deja documentado para la migración futura.

**WARNING-2**: `GENERO_A_FAMILIA` en `taxonomia.py` incluye géneros `Hyloxalus` y `Sachatamia`
cuyas especies están excluidas de `ESPECIES`. Esto es intencional (preparación para reingreso vía
gate), no un error, pero debe tenerse en cuenta al generar `species_registry.json`: esos géneros
existen en el diccionario de familias sin especie activa asociada todavía.

**WARNING-3**: `Leucostethus fraterdanieli` (huérfana en REFERENCE, ver Fase 13) **no aparece en
absoluto** en `taxonomia.py` — ni en `ESPECIES` ni en `GENERO_A_FAMILIA` (género `Leucostethus`
ausente). Esto confirma independientemente, desde una fuente distinta a Fase 13, que su exclusión
de los 41 centroides es correcta y consistente con el catálogo taxonómico declarado.

## 7. Riesgos de migración

- Cualquier migración física de `data cleaned/`, `data dirty/`, o manifests existentes rompería
  las rutas relativas usadas por scripts de Fase 13 ya congelados. **Por esto, la arquitectura
  propuesta usa manifiestos de referencia (paths + hash), no copia ni mueve archivos.**
- Asignar `species_id` a las 41 especies actuales es seguro (datos ya conocidos, sin inventar
  taxonomía). Asignar `species_id` a especies *nuevas* requiere primero verificación taxonómica
  real — el mecanismo se deja preparado pero no se ejecuta para especies hipotéticas.
