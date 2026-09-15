# Contrato Kotlin/Android — Merlin Identification

**Versión de contrato: v0.2.0** (schema `anura://schemas/identification-result/v0.2.0`).
Cambio respecto a v0.1.0: **aditivo y compatible hacia atrás**. Se añaden dos campos
opcionales — `visual_similarity_warnings` y `catalog_state` — sin modificar el tipo ni la
semántica de ningún campo existente. Un cliente v0.1.0 sigue funcionando ignorándolos.

La app no conoce BioCLIP, GEO ni Open Set. Solo serializa una solicitud y renderiza `IdentificationResult` conforme a `IDENTIFICATION_RESULT_SCHEMA.json`.

```kotlin
data class IdentificationRequest(
    val observationId: String,
    val imageUri: String,
    val latitude: Double? = null,
    val longitude: Double? = null,
    val isAnuran: Boolean? = null,
    val anuranEvidence: Map<String, String>
)
```

La implementación del motor puede ser un backend, ONNX Runtime móvil u otra capa offline, pero debe devolver el schema central sin cambiar su semántica.

Reglas de presentación:

- `candidates` = “Posibles identificaciones”.
- `decision` se muestra por separado de `candidates[0]`.
- Nunca mostrar `visual_score`, `geographic_score` o `ranking_score` como porcentaje/probabilidad.
- Si falta ubicación, renderizar la limitación sin impedir el ranking visual.
- Si el Open Set rechaza, mostrar `NO_CONCLUYENTE`; no traducirlo a `NO_REGISTRADA`.
- Mantener `model_version`, `catalog_version` y `experimental_flags` para soporte y trazabilidad.

## `visual_similarity_warnings` (nuevo en v0.2.0)

```kotlin
data class VisualSimilarityWarning(
    val groupId: String,
    val label: String,          // "ESPECIES VISUALMENTE MUY PARECIDAS"
    val description: String,
    val matchedSpeciesIds: List<String>,
    val matchedScientificNames: List<String>,
    val advisoryOnly: Boolean   // siempre true
)
```

Se emite cuando **dos o más especies del mismo grupo** aparecen en el Top-K
(K = `presentation_rule.top_k` de `visual_similarity_groups.json`, por defecto **3**).

Reglas de presentación **obligatorias**:

- Es una **capa de interpretación**. La app la muestra como aviso junto a la lista.
- **NO** modifica los porcentajes/scores, **NO** reordena candidatos, **NO** elige ganador
  y **NO** cambia `decision`. Los scores se siguen mostrando exactamente igual que sin el aviso.
- Los grupos son **configurables** y vienen de `visual_similarity_groups.json` y/o de los
  paquetes instalados. Ninguna pareja está fija en el código.

## `catalog_state` (nuevo en v0.2.0)

Trazabilidad del **catálogo activo** que produjo el resultado: paquetes instalados y activos,
número de especies activas y especies desactivadas. `network_required` es siempre `false`:
una vez instalado el paquete, la identificación es completamente offline.

El ranking y el Open Set operan **solo sobre el catálogo activo**. Una especie inactiva no
aparece en `candidates` ni aporta centroide a `open_set_evidence`. Si no hay ninguna especie
activa, `decision` es `NO_CONCLUYENTE` con `open_set_evidence.reason = "NO_ACTIVE_SPECIES_IN_CATALOG"`.

`open_set_evidence` incluye ahora `nearest_species_id`, `active_centroid_count` y
`centroid_source` para auditar qué centroides participaron.

### Aislamiento de paquetes (`OPEN_SET_PACKAGE_ISOLATION`)

Aditivo y compatible hacia atrás; ningún campo existente cambia de tipo.

- El catálogo activo se lee del **estado persistido** en cada inferencia, como una
  instantánea inmutable. Desactivar/desinstalar un paquete desde cualquier componente
  surte efecto en la siguiente inferencia, sin reiniciar el motor.
- La **pertenencia al catálogo activo es una precondición independiente del threshold**.
  Si el centroide más cercano no pertenece al catálogo activo → `NO_CONCLUYENTE` con
  `open_set_evidence.reason = "NEAREST_CENTROID_NOT_IN_ACTIVE_CATALOG"`. Si la
  verificación final del flujo rechaza la especie aceptada → limitación
  `OPEN_SET_ACCEPTED_SPECIES_NOT_IN_ACTIVE_CATALOG`. El threshold nunca se ajusta para esto.
- `ESPECIE_CONOCIDA` = aceptada como `open_set_evidence.nearest_species_id`, que pertenece
  al catálogo activo. Puede no coincidir con `candidates[0]` (se siguen mostrando por separado).
- Trazabilidad: `open_set_evidence.catalog_membership` y
  `catalog_state.catalog_fingerprint` (sha256 de paquetes activos + payload + especies
  desactivadas).
- Una implementación nativa debe replicar las tres reglas: instantánea desde estado
  persistido, pertenencia antes del threshold y ningún candidato fuera del catálogo activo.

## Estado de los adaptadores

El ONNX FP16 actual puede implementarse offline con ONNX Runtime y un preprocesamiento nativo equivalente al constructor `open_clip` validado. La presente integración ejecuta ese ONNX en desktop; no hay proyecto Android en este checkout que permita compilar o validar el adaptador Kotlin todavía.
