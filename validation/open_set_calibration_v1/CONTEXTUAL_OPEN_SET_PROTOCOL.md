# Protocolo contextual Open Set v1 — GEO + taxonomía

**Estado:** diseño de experimento; no cambia el encoder, los embeddings, el catálogo, los priors GEO-6 ni los thresholds ya reportados.

Este documento sustituye únicamente la recomendación de la sección 11 de `OPEN_SET_CALIBRATION_REPORT.md`: a partir de la instrucción del responsable del producto, la evaluación siguiente debe incluir ubicación, género y familia como evidencia contextual auditada.

## Regla de seguridad

La aplicación solo puede devolver `ESPECIE_CONOCIDA` cuando pasan simultáneamente la evidencia visual Open Set congelada y las reglas contextuales disponibles. La ubicación, género o familia no pueden, por sí solos, convertir `NO_CONCLUYENTE` en `ESPECIE_CONOCIDA`.

Consecuencias:

- ubicación incompatible puede rechazar o reducir candidatos;
- ubicación compatible solo permite conservar la decisión visual, no elevarla;
- si la especie no queda identificada de forma segura, el resultado sigue siendo `NO_CONCLUYENTE`, aunque se muestre `género probable` o `familia probable` como hipótesis separada;
- nunca se consulta `true_species`, `true_genus` ni `true_family` durante inferencia; solo se usan después para métricas.

## Evidencia autorizada en tiempo de consulta

| Fuente | Uso permitido | Límite |
|---|---|---|
| Coordenadas de la solicitud | Resolver celda y zona con `cell_zone_map_v1.csv` | GEO actual cubre únicamente zonas congeladas de Antioquia. |
| Prior especie/zona GEO-6 | Compatibilidad o incompatibilidad de cada especie candidata | Es `prior_zone_taxon_v2_clean`, con AUROC honesto histórico aproximado de 0.617; se debe recalibrar, no tratar como certeza biológica. |
| Registro taxonómico | Agrupar candidatos por familia y género | No es un clasificador independiente y no puede usar la etiqueta real. |
| Ranking visual congelado | Evidencia por especie, género y familia | No se reentrena el encoder. |

Si no hay coordenadas, son imprecisas, o están fuera de cobertura, el sistema declara `GEO_NOT_APPLIED` y conserva el flujo visual. La ausencia de GEO no es evidencia negativa.

## Scores taxonómicos observables

Con las distancias visuales a todos los candidatos activos, convertir las distancias en pesos relativos con una temperatura fijada únicamente durante calibración. Sumar esos pesos por género y por familia:

```text
species_support(s) = weight(s)
genus_support(g)  = sum(weight(s) for s in genus g)
family_support(f) = sum(weight(s) for s in family f)
```

Los tres soportes se calculan antes de filtrar y se guardan para auditoría. Un alto `genus_support` con baja separación entre especies del mismo género significa evidencia taxonómica parcial, no evidencia suficiente de especie: emitir `NO_CONCLUYENTE` con `GENUS_LEVEL_AMBIGUITY`.

## Regla contextual que se debe calibrar

Para cada consulta con GEO válido, generar candidatos visuales y el prior GEO por especie. La regla propuesta es una intersección conservadora:

```text
accept_species = visual_open_set_pass
                 AND species_geo_compatible
                 AND species_margin_pass
                 AND NOT genus_level_ambiguity
                 AND NOT family_level_ambiguity
```

`species_geo_compatible`, los umbrales de soporte y de ambigüedad no están definidos aún. Deben elegirse exclusivamente en una calibración mixta KNOWN + UNKNOWN con coordenadas de captura verificadas. La compatibilidad se mide con el prior sin normalización por cohorte: la normalización fila-minmax de GEO-6 no es válida como umbral individual.

La salida debe conservar `geo_zone_id`, versión de prior, cobertura, score bruto, soporte de especie/género/familia, umbrales congelados y razón de rechazo. No exponer esos scores como probabilidades al usuario.

## Diseño de evaluación obligatorio

1. Construir el split `reference/train -> calibration -> freeze -> Fase23A blind`, manteniendo individuos separados.
2. Para cada imagen de calibración y blind, enlazar de forma determinista imagen/observación/coordenadas. Si no existe ese enlace, excluirla de la métrica contextual y reportar cobertura; nunca imputar coordenadas por especie.
3. Estratificar por `GEO_IN_COVERAGE`, `GEO_OUT_OF_COVERAGE`, mismo género, misma familia y familia ausente. Las etiquetas taxonómicas reales se usan solo para reportar estratos tras la inferencia.
4. Comparar, con los mismos casos cubiertos: visual puro, visual + GEO, visual + taxonomía agregada y visual + GEO + taxonomía agregada.
5. Seleccionar la regla por máxima KAR sujeto a `FAR <= 5%`, `UDR >= 95%`, `FRR <= 20%` y sin degradar de forma material ningún estrato cubierto. Congelar parámetros antes de abrir Fase23A.
6. En Fase23A, informar por separado cobertura GEO, FAR/UDR cubiertos, FAR/UDR sin GEO y resultados por especie UNKNOWN. No mezclar las poblaciones para ocultar fallos fuera de cobertura.

## Criterios de rechazo de la hipótesis contextual

No desplegar la regla contextual si ocurre cualquiera de estos casos:

- mejora global obtenida solo porque excluye sistemáticamente KNOWN;
- mejora solo en coordenadas fuera de la distribución real de la app;
- el umbral fue elegido tras observar Fase23A;
- la familia/género real se filtró al runtime;
- el prior GEO es usado para aceptar una especie que no superó visual Open Set;
- no existe trazabilidad imagen -> coordenada -> celda/zona.

## Perfil topográfico y rango de habitabilidad

La ubicación debe enriquecerse con topografía abierta mediante **OpenTopoData**. Se usará el dataset global `srtm30m` para Colombia, con coordenadas WGS-84 (`EPSG:4326`), y se registrarán dataset, URL/endpoint, interpolación, fecha de consulta, respuesta original y hash del lote. OpenTopoData admite lotes de hasta 100 coordenadas; las consultas se harán en lotes reproducibles y se almacenarán localmente antes de cualquier calibración. La API publica la elevación del punto, no una etiqueta de hábitat; por tanto el rango de habitabilidad se deriva y se valida dentro del protocolo, no se presupone.

Para cada observación con coordenadas verificadas se construirá un vector ambiental topográfico:

```text
latitud, longitud, zona GEO congelada,
elevación del punto,
pendiente, orientación,
relieve local, rugosidad topográfica,
completitud/calidad de coordenada
```

La elevación se consulta en el punto y en una vecindad geodésica fija de ocho puntos. Pendiente, orientación, relieve y rugosidad se calculan desde esa vecindad; radio, dataset e interpolación quedan congelados antes del blind. Si alguna elevación devuelve `null`, el vector se marca incompleto y no produce una penalización.

Para cada especie del catálogo se ajusta exclusivamente con observaciones `reference/train` de coordenadas únicas un **sobre de habitabilidad** en este espacio multidimensional. Solo se habilita si tiene un mínimo predefinido de localidades independientes y estabilidad mediante validación interna. El sobre debe ser robusto a repeticiones de la misma localidad; la unidad de split es localidad/individuo, no foto.

La regla operativa adicional es conservadora:

```text
habitat_incompatible = profile_available
                       AND species_profile_validated
                       AND outside_frozen_habitat_envelope

accept_species = prior_accept_rule
                 AND NOT habitat_incompatible
```

Estar dentro del sobre de distribución o altura **no acepta** una especie; solo evita descartarla. Estar fuera puede generar `NO_CONCLUYENTE` únicamente si la cobertura y calidad de coordenadas son válidas. La incertidumbre de GPS, observaciones históricas sesgadas y especies con muy pocas localidades deshabilitan la regla para ese candidato.

La calibración debe comparar: visual puro; visual + GEO; visual + elevación; visual + perfil topográfico; y la intersección de todos. Se reportan FAR, UDR, KAR y FRR por cobertura GEO, por banda altitudinal, por especie y por tipo taxonómico. Ningún parámetro topográfico se selecciona tras abrir Fase23A.

## Estado actual

El experimento Open Set visual v1 permanece `NO_GO`; sus métricas no cambian. Los artefactos existentes confirman que el conjunto UNKNOWN origen contiene coordenadas en su manifiesto de descarga, pero esta verificación todavía no demuestra un enlace completo y ciego de las 620 filas de Fase23A al prior GEO individual. Por eso no se comunica todavía una mejora numérica de ubicación, género o familia.
