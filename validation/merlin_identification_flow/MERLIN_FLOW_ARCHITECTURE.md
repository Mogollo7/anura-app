# Arquitectura del flujo Merlin para ANURA/SITRana

## Flujo ejecutable

```text
Observación + foto
        |
        v
Adaptador de validación inicial (is_anuran + evidencia)
        |--- no confirmada ---> NO_CONCLUYENTE
        v
Adaptador BioCLIP congelado -> VisualEvidence (candidatas + visual_score)
        |
        v
Adaptador de contexto geográfico opcional -> geographic_score por especie
        |
        v
Ranking: visual; visual + 0.3*geo_especie únicamente cuando el score existe
        |
        v
Top-K configurable (3 por defecto) + metadata taxonómica
        |
        v
Adaptador Open Set Fase 23A/GEO-6 -> unknownness_score
        |
        v
Decisión independiente: ESPECIE_CONOCIDA / NO_CONCLUYENTE / NO_REGISTRADA
        |
        v
IdentificationResult + explicación + limitaciones
```

## Límites de responsabilidad

| Componente | Responsabilidad | No hace |
|---|---|---|
| App móvil futura | Captura foto, permisos, EXIF/ubicación consentida, muestra `IdentificationResult`. | No decide la especie ni recalibra scores. |
| Adaptador BioCLIP | Produce candidatos visuales ya normalizados según el contrato del runtime congelado. | No acepta la especie ni llama los scores probabilidades. |
| Adaptador geográfico | Resuelve región y devuelve score por especie cuando hay contexto válido. | No bloquea el flujo si falta ubicación; no usa género/familia en el score. |
| `MerlinFlow` | Ranking Top-K, taxonomía, decisión Open Set y explicación. | No carga modelos, no modifica artefactos, no inventa evidencia biológica. |
| Adaptador Open Set | Aporta `unknownness_score` y provenance de Fase 23A/GEO-6. | No convierte un ranking Top-1 en especie aceptada. |

## Contrato para la futura app móvil

La pantalla o API debe construir esta entrada mínima hacia `MerlinFlow.identify`:

```json
{
  "observation_id": "uuid",
  "input_metadata": {"photo_uri": "local opaque reference", "location_consent": true},
  "is_anuran": true,
  "anuran_evidence": {"source": "anuran-validation-adapter"},
  "visual_candidates": [{"scientific_name": "Boana boans", "visual_score": 0.82}],
  "geographic_context_available": true,
  "geographic_scores": {"Boana boans": 0.74},
  "open_set_unknownness_score": 0.61
}
```

`visual_candidates`, `geographic_scores` y `open_set_unknownness_score` son la frontera de adaptadores: hoy los proveen fixtures; mañana los proveerán los runtimes móviles o un backend. La respuesta está definida por `IDENTIFICATION_RESULT_SCHEMA.json` y no expone probabilidades.

## Reglas invariables de integración móvil

- Renderizar `candidates` como **posibles identificaciones**, nunca como una afirmación automática.
- Mostrar `decision` por separado del primer candidato.
- Si `geographic_context_available` es falso, mostrar que la ubicación no aportó contexto, sin degradar la compatibilidad visual.
- Si aparecen `OPEN_SET_THRESHOLDS_DIAGNOSTIC` o `NO_REGISTRADA_NOT_ASSERTED`, la interfaz debe presentar `NO_CONCLUYENTE`; no ofrecer “no registrada” como diagnóstico automático.
- `segmentation_evidence` solo puede presentar los estados `PRESENTE`, `AUSENTE` y `NO_EVALUABLE`; el último significa ausencia de evidencia, no ausencia del rasgo.
- Conservar `model_version`, `catalog_version` y `experimental_flags` junto a cada resultado para trazabilidad offline/sincronizada.

## Extensibilidad sin rediseño

Audio, contexto adicional o un nuevo modelo visual se añaden como adaptadores que aportan evidencia adicional versionada. El orquestador y `IdentificationResult` se mantienen; cualquier nueva señal requiere una política de ranking/Open Set validada antes de habilitarse.

## Referencias experimentales conservadas

- Ranking GEO-6: `w_geo_rank=0.3`, experimental, únicamente para geo-especie moderado.
- Open Set geográfico honesto sin oracle: AUROC aproximadamente 0.617.
- El 0.701 es histórico/diagnóstico afectado por oracle information y no debe aparecer como rendimiento reproducible de inferencia.
- Los thresholds GEO-6 son diagnósticos y no aptos para producción.
