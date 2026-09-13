# SPECIES_LIFECYCLE.md

Estados por los que pasa una especie desde su descubrimiento hasta su despliegue (o rechazo).
Una especie con centroide **no** está automáticamente `DEPLOYED`.

## Estados

```
DISCOVERED
    → especie observada/catalogada, sin verificación taxonómica formal en el proyecto.

TAXONOMICALLY_VERIFIED
    → species_id asignado, family/genus confirmados contra fuente taxonómica
      (ej. taxon_info.json de iNaturalist, como ya se hizo para Pristimantis→Craugastoridae).

DATA_COLLECTING
    → recolección de observaciones/imágenes en curso, sin evaluación de suficiencia todavía.

DATA_READY
    → pasó data_sufficiency_policy (ver más abajo) para el propósito declarado
      (ej. "candidate" o "adequate", según política vigente al momento del release).

EMBEDDED
    → embeddings generados con el encoder congelado vigente, contrato de embedding registrado
      (encoder_sha256, dim, preprocessing_version — ver EMBEDDING_CONTRACT.md).

CENTROID_READY
    → centroide calculado y con metadata completa (source_split, image_count, etc.)
      *** ESTE ESTADO NO IMPLICA DEPLOYED. Es un artefacto intermedio. ***

VALIDATION
    → en proceso a través del VALIDATION_GATE.md (contaminación, Open Set, blind test).

APPROVED
    → el gate emitió PASS para esta especie dentro de un catalog_release candidato.

DEPLOYED
    → incluida en un catalog_release con status FROZEN, referenciada por al menos
      un regional_package.

REJECTED
    → el gate emitió FAIL, o suficiencia de datos insuficiente, o contaminación detectada.
      Queda registrada (no se elimina el historial) con la razón del rechazo.
```

## Transición obligatoria

```
CENTROID_READY ──X──> DEPLOYED   (PROHIBIDO saltar directo)
CENTROID_READY ──✓──> VALIDATION ──✓──> APPROVED ──✓──> DEPLOYED
```

Esto es exactamente el principio de la Regla 11 de la tarea: *"NO declarar una especie como
desplegable simplemente porque tenga un centroide."*

## Suficiencia de datos — política configurable, no una regla fija

No se impone aquí un número mínimo de individuos (ej. 70) como constante universal del sistema,
porque **no existe una política formal documentada en el proyecto que lo establezca como regla
matemática** — el número 70 aparece en memoria de proyecto (`anura_cola_larga_taxonomica.md`) como
observación empírica sobre especies problemáticas, no como umbral codificado en ningún script.

En su lugar, se deja preparado (no implementado con valores) el concepto:

```json
{
  "data_sufficiency_policy_version": "UNDEFINED",
  "criteria": {
    "individual_count": null,
    "observation_count": null,
    "image_count": null,
    "quality_threshold": null
  },
  "resulting_categories": ["insufficient", "limited", "candidate", "adequate"],
  "status": "POLICY_NOT_YET_FORMALIZED"
}
```

Cuando el proyecto formalice esta política, debe registrarse con su propia versión
(`data_sufficiency_policy_v1`, etc.) y aplicarse de forma trazable — no como criterio ad-hoc
por especie.

## Ejemplo real usando el estado actual del proyecto (sin inventar)

| Especie | Estado actual real | Evidencia |
|---|---|---|
| Las 9 especies Group A | `DEPLOYED` (vía visual_catalog_1.0.0) | REFERENCE + centroid + Fase 13 blind eval |
| Las 32 especies Group B | `DEPLOYED` (vía visual_catalog_1.0.0), pero `INDEPENDENT_CALIBRATION=NO` | TRAIN + centroid estructural |
| Hyloxalus_picachos | `REJECTED` (huérfana, datos insuficientes + contaminación de duplicados) | comentario en `taxonomia.py` |
| Sachatamia_electrops | `REJECTED` (huérfana, mismo motivo) | comentario en `taxonomia.py` |
| Leucostethus fraterdanieli | Ni siquiera `DISCOVERED` en `taxonomia.py` — existe solo en REFERENCE, fuera del catálogo taxonómico activo | ausencia confirmada en `GENERO_A_FAMILIA`/`ESPECIES` |
