# Fase 7 — Evaluación controlada del prior geográfico

## Objetivo

Evaluar el efecto del prior existente sin modificar modelo, checkpoint, dataset, catálogo, SQLite-vec ni producción.

## Configuración real auditada

- Fórmula: `log P(final) = log P(visual) + w * log P(prior)`.
- Radio: 50.0 km.
- Suavizado alpha: 0.5.
- Peso recomendado: 0.75.
- Distancia: Haversine.
- Prior: conteos de puntos del archivo exportado, add-alpha, normalización por suma.
- No hay clipping adicional, threshold ni rechazo.

## Dataset y GPS

- KNOWN: 766 imágenes.
- UNKNOWN: 56 imágenes; 15 Hyloxalus_picachos y 41 Sachatamia_electrops.
- GPS real F3: 680/766.
- GPS real F4: 35/56.
- Las imágenes sin GPS real se marcaron `GPS_REAL_UNAVAILABLE`.

## Resultados

- VISION_ONLY: Top-1 KNOWN=0.5691906005221932; UNKNOWN→KNOWN=56/56; flips=0.
- REAL_GPS: Top-1 KNOWN=0.7911227154046997; UNKNOWN→KNOWN=56/56; flips=302.
- ADVERSARIAL_GPS: Top-1 KNOWN=0.27154046997389036; UNKNOWN→KNOWN=56/56; flips=585.
- ALTERNATIVE_GPS: Top-1 KNOWN=0.3629242819843342; UNKNOWN→KNOWN=56/56; flips=438.
- VISION_ONLY_UNKNOWN: Top-1 KNOWN=None; UNKNOWN→KNOWN=56/56; flips=0.
- REAL_GPS_UNKNOWN: Top-1 KNOWN=None; UNKNOWN→KNOWN=56/56; flips=29.
- ADVERSARIAL_GPS_UNKNOWN: Top-1 KNOWN=None; UNKNOWN→KNOWN=56/56; flips=50.
- ALTERNATIVE_GPS_UNKNOWN: Top-1 KNOWN=None; UNKNOWN→KNOWN=56/56; flips=34.

## Escenarios controlados

- GPS adversarial: {'gps': [4.6485, -73.8864], 'favored_species': 'Pristimantis_bogotensis', 'prior_max': 0.3862433862433862}.
- GPS alternativo: {'gps': [-4.218, -69.9435], 'favored_species': 'Boana_punctata', 'distance_from_adversarial_km': 1078.8201615397645}.
- UNKNOWN con consenso de prior registrado: 56/56.

## Interpretación

El sistema sigue siendo un clasificador cerrado: sin rechazo, toda imagen UNKNOWN termina en una de las 41 clases. El prior solo puede cambiar el ranking o la clase conocida final; no crea capacidad de rechazo Open Set.

Los casos de cambio UNKNOWN bajo GPS controlado se reportan como riesgo de influencia del prior, no como error de un threshold productivo.

## Limitaciones

El GPS real no está disponible para todas las imágenes. Los escenarios adversarial y alternativo usan coordenadas reales presentes en el prior, pero son experimentos retrospectivos. El Open Set contiene solo 56 imágenes de 2 especies y no representa todas las especies no visuales.

No se creó score combinado, no se aplicó threshold, no se implementó rechazo y no se modificó producción.

Artefactos y hashes: ver `prior_discrimination_metrics.json`. Generado: 2026-09-13T06:42:31.062463+00:00.
