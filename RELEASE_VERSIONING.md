# RELEASE_VERSIONING.md

Esquema de versionado para que el threshold, los centroides y la covarianza nunca se traten
como "universales", sino ligados a un release específico e inmutable una vez congelado.

## Cadena de dependencia

```
visual_catalog_1.0.0
    ↓ (41 especies: 9 Group A + 32 Group B)
centroids_1.0.0
    ↓
covariance_1.0.0 (Ledoit-Wolf, shared, fit sobre REFERENCE 798)
    ↓
threshold_1.0.0 (τ=39.354064, congelado @95% KAR sobre CALIBRATION 192)
    ↓
validation_1.0.0 (blind sobre F3 766 + F4 56)
```

Si en el futuro se agregan especies:

```
visual_catalog_1.1.0
    ↓ (41 + N especies nuevas)
centroids_1.1.0        ← recalculado, incluye los 41 anteriores + N nuevos
covariance_1.1.0       ← recalculado (la covarianza compartida cambia con el catálogo)
threshold_1.1.0        ← nueva calibración, nuevo τ si corresponde
validation_1.1.0       ← nueva evaluación blind
```

**`visual_catalog_1.0.0` nunca se modifica retroactivamente.** `1.1.0` es un release nuevo que
coexiste con `1.0.0`, no lo reemplaza en el historial.

## Regla dura

Un `threshold_X.Y.Z` solo es válido para el `centroids_X.Y.Z` y `covariance_X.Y.Z` con el mismo
número de versión. Usar `threshold_1.0.0` contra `centroids_1.1.0` es un error de release, no una
operación válida — el validation_gate debe rechazarlo (`FAIL`, causa: `RELEASE_MISMATCH`).

## Regional packages apuntan a un catalog_release, nunca a "el catálogo actual"

```json
{
  "package_id": "ANTIOQUIA",
  "package_version": "1.0.0",
  "catalog_release": "visual_catalog_1.0.0",
  "validation_status": "PILOT"
}
```

Esto permite que `ANTIOQUIA v1.0` siga funcionando con 41 especies aunque exista
`visual_catalog_1.1.0` con más especies — un paquete regional nuevo (`ANTIOQUIA v1.1`) puede
apuntar al catálogo nuevo sin destruir `v1.0`.

## Estado real de versionado hoy (auditado, no inventado)

| Componente | ¿Versionado hoy? | Evidencia |
|---|---|---|
| Manifest regional (`ANTIOQUIA_v1.0.0_manifest.json`) | SÍ | campo `"version": "1.0.0"` |
| Paquete `.sqlite` regional | SÍ | `COLOMBIA_ANURA/ANTIOQUIA/packages/v1.0.0/` + `CHECKSUMS.sha256` |
| Checkpoints de encoder (`bioclip_anura_mejor.pt`, etc.) | **NO** | nombres fijos, sin sufijo de versión, se sobrescriben |
| Centroides de Fase 13 | **NO** | se recalculan desde `.npz` en cada ejecución, no se persisten como artefacto con nombre versionado |
| Threshold (`frozen_rejection_config.json`) | Parcial | tiene `timestamp_utc`, pero no hash/versión del catálogo que calibró |

## Corrección aplicada: membership por release vía species_id (no por nombre)

**Hallazgo original**: la primera versión de `build_regional_package.py` cruzaba especies
regionales contra el `species_registry.json` global por string de nombre científico, sin
verificar si esas especies realmente pertenecían al `catalog_release` solicitado. Esto
funcionaba mientras existiera un solo release, pero no habría distinguido `visual_catalog_1.0.0`
de un futuro `visual_catalog_1.1.0` con más especies.

**Corrección**: `visual_catalog/{release}/manifest.json` ahora incluye `"species_ids": [...]`
explícito (resuelto vía `tools/catalog/taxonomic_resolution.py`, que reutiliza
`taxonomia.canonico()` — el mismo mecanismo de alias que ya existía, incluyendo
`acanthinus→achatinus`). El join en `build_regional_package.py` es ahora una intersección de
conjuntos de `species_id`, nunca una comparación de strings de nombre.

**Verificado con TEST 3** (`tools/catalog/tests/test_release_membership.py`): una especie
simulada presente en un release 1.1.0 ficticio queda correctamente excluida al construir
contra el release real 1.0.0, y correctamente incluida al construir contra el 1.1.0 simulado.

## Mapeo del baseline actual a este esquema (sin migrar archivos)

Este esquema se aplica **hacia adelante**. El baseline existente (Fase 13) se referencia, no se
mueve — ver `visual_catalog/v1.0.0/manifest.json`, que apunta por ruta relativa a los archivos
reales en `evaluation/fase13/`, sin copiarlos ni moverlos.
