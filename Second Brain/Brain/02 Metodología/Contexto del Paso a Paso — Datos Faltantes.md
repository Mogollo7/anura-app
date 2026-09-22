---
title: "Contexto del Paso a Paso — Datos Faltantes"
proyecto: Anura
tipo: metodología
estado: redactado
tags: [anura, contexto, paso-a-paso, scraping, pendiente]
---

# Contexto del Paso a Paso — Datos Faltantes

> Nota puente + hoja de ruta. Registra qué campos del wizard de captura (`06 Proceso de
> Desarrollo de la App`) **ya tienen datos reales para usarse como prior de identificación** y
> cuáles no, con instrucciones concretas para cuando se ejecute la recolección pendiente.
> Motivada por una auditoría del 2026-09-22 sobre los 6 pasos del wizard Android.

## Ya integrado (no repetir)

| Campo (paso) | Estado | Dónde vive |
| --- | --- | --- |
| Ubicación + zona geográfica (Paso 1) | ✅ Integrado 2026-09-22 | `PackageVectorIndex.zoneIdFor()`, tabla `grid_cells` en `package.sqlite` |
| Altitud (Paso 1) | ✅ Integrado 2026-09-22 (mediana/p10/p90 por zona, no por punto exacto) | tabla `zones`/`zone_prior_meta` en `package.sqlite` |
| Temperatura/Humedad (Paso 2) | ✅ Integrado 2026-09-22, con reserva — ver abajo | tabla `weather_prior`/`weather_prior_meta` en `package.sqlite` + llamada en vivo a Open-Meteo |

**No repetir**: usar OpenTopoData por punto exacto (elevación/pendiente en tiempo real) para
mejorar el *rechazo* Open Set ya se probó y dio `NO_GO`
(`validation/open_set_topography_v1/TOPOGRAPHIC_CONTEXT_REPORT.md`). Ver
[[Arquitectura Multimodal]] §5.1.

### Temperatura/Humedad — integrado con reserva explícita (2026-09-22)

Fechas reales para observaciones iNaturalist **ya estaban en `records_v1.csv`** (nadie las había
unido a las imágenes); no se necesitó scraping nuevo, solo el join. Pipeline completo en
`evaluation/geo_weather_v1/` (`fetch_weather.py` + `evaluate_weather_prior.py`), clima histórico
vía Open-Meteo (gratis, sin API key).

**Resultado de la evaluación con control de fuga** (n=129 imágenes de prueba con clima
resuelto — techo real de cobertura, no muestra parcial): Top-1 61.2%→65.1% (+3.9pp), Top-3
81.4%→82.9% (+1.5pp), mejor con el peso más bajo probado (w=0.2) y decreciente al subir el peso.

**Se integró de todos modos, a pedido explícito**, pese a que la muestra es pequeña y la señal
mucho más frágil que el prior de zona (+9.6pp sobre 167 imágenes) — la recomendación registrada
en su momento fue no integrar sin ampliar la evidencia. Queda documentado para que quien revise
el comportamiento en campo sepa que esta pieza específica **no pasó la misma barra de
confiabilidad** que el prior de zona.

**Diferencia arquitectónica importante**: a diferencia del prior de zona (dato horneado, 100%
offline), el clima requiere una **llamada de red en el momento de identificar** (Open-Meteo,
timeout 4s) — rompe parcialmente el diseño "funciona sin conexión" del resto del pipeline. Si
falla o no hay red, cae a neutro (voto puramente visual), nunca bloquea, pero en campo sin señal
esta pieza simplemente no aporta nada.

Notas de implementación:
- Encontrar cobertura de red de datos: solo 790/1023 observaciones con fecha+coords resueltas
  tuvieron clima recuperado (77%) — el resto son huecos de Open-Meteo o consultas no completadas.
- Solo 21/25 especies visuales con datos de clima tuvieron ≥3 observaciones en train — mínimo
  arbitrario, no calibrado.
- El fetch de clima sufrió cuelgues de red intermitentes y sistemáticos en este entorno de
  desarrollo (`urllib`, luego `requests`, ambos se colgaban tras un número variable de llamadas
  sin error visible); se resolvió invocando `curl` por subprocess, que fue estable. Si se repite
  este tipo de scraping, preferir `curl`/proceso externo sobre las librerías HTTP de Python en
  este entorno.

## Sin ningún dato de origen — instrucciones para cuando se ejecute

Ninguno de estos tiene una sola fila de datos en el proyecto hoy (auditado con `grep` exhaustivo
sobre `COLOMBIA_ANURA/`, `bioclip/`, `taxonomy/` — cero coincidencias). No se deben inventar
valores plausibles: degradaría la precisión en vez de mejorarla.

### Ecosistema (Paso 1)

**Es el más barato de los cuatro** porque, a diferencia de microhábitat/SVL, **no necesita
scraping de observaciones** — es un dato espacial como la altitud: un mapa de ecosistemas de
Colombia (p. ej. el mapa de ecosistemas continentales del IDEAM/IAvH, o Corine Land Cover) unido
por punto-en-polígono a la misma malla de celdas de 0.25° que ya existe (`cell_zone_map_v1.csv`).

Pasos:
1. Conseguir el shapefile/raster de ecosistemas de IDEAM o IAvH para Antioquia (dominio público,
   normalmente vía el SIAC o el visor de IDEAM).
2. Point-in-polygon de cada celda de la malla existente contra ese mapa → `ecosystem_id` por celda,
   igual que `zone_id`.
3. Construir `P(especie|ecosistema)` con el mismo formato/suavizado que
   `pipeline_dataset/paquetes_zonales.py` (Laplace, control de fuga).
4. Evaluar igual que el prior de zona antes de tocar el paquete — puede que ecosistema y zona
   geográfica estén tan correlacionados que no aporten nada nuevo (hipótesis a probar, no asumir).

### Microhábitat (Paso 1)

**Sí necesita datos nuevos por observación**, no solo un mapa. Dos rutas posibles:
1. **Minería de texto sobre iNaturalist**: muchas observaciones tienen descripción libre
   (`description` en la API de observaciones) que a veces menciona "bajo hojarasca", "en el
   agua", etc. Requiere: (a) scraping del campo `description` para las ~3.253 observaciones ya
   identificadas en `evaluation/geo_weather_v1/` (mismo `obs_id` que ya se resolvió para clima),
   (b) clasificación por palabras clave o un LLM pequeño a las 4 categorías del wizard
   (Hojarasca/Vegetación baja/Cuerpo de agua/Roca), (c) validar manualmente una muestra antes de
   confiar en la clasificación automática — el texto libre es ruidoso.
2. **Literatura por especie**: AmphibiaWeb o descripciones originales suelen mencionar el
   microhábitat típico de la especie (no del individuo observado) — más grueso pero más confiable
   que la ruta 1. 291 especies, requiere curación manual o scraping dirigido de AmphibiaWeb.

Ninguna ruta es una tarde de trabajo; ambas requieren validación antes de usarse como prior.

### SVL / talla (Paso 3)

**El más difícil de los cuatro.** No hay atajo espacial ni de texto libre confiable: se necesita
el rango de longitud hocico-cloaca por especie, que típicamente solo está en:
- AmphibiaWeb (campo "size" en la ficha de cada especie, texto libre, requiere parseo).
- Descripciones taxonómicas originales (PDFs, no scrapeables en bloque).
- Bases de museos con especímenes medidos (algunas ocurrencias de GBIF traen
  `MeasurementOrFact`, pero la cobertura para anuros colombianos es baja — verificar antes de
  invertir tiempo).

Instrucción concreta: antes de scrapear, correr un chequeo rápido de cobertura de
`MeasurementOrFact` en las descargas de GBIF ya existentes (`COLOMBIA_ANURA/ANTIOQUIA/occurrences/`)
— si la cobertura es baja (probable), la única ruta realista es AmphibiaWeb por especie (291
consultas, scraping dirigido + parseo de texto libre tipo "SVL 25-38 mm males, 30-45 mm females").

### Franja del día / hora (Paso 2)

**Parcialmente accionable ya**: las ~3.253 observaciones de iNaturalist identificadas en
`evaluation/geo_weather_v1/fetch_weather.py` (mismo `obs_id`) tienen fecha completa en
`records_v1.csv`, pero **no hora**. La hora exacta (`time_observed_at`) solo está en la API de
iNaturalist, no en el CSV local — requiere un scraping nuevo pero acotado y ya con la lista de
IDs lista:

1. Reusar la lista de `obs_id` ya resueltos en `evaluation/geo_weather_v1/obs_clima.json`.
2. Pedir a `https://api.inaturalist.org/v1/observations/{id}` (o en lotes por `?id=1,2,3`, igual
   patrón que `validation/fase23a_geographic_context/scripts/phase0_fetch_inat.py`) el campo
   `time_observed_at` — mismo mecanismo de caché/reintentos que ese script.
3. Cobertura esperada baja: muchos observadores no registran hora, solo fecha — medir antes de
   invertir en el prior.
4. Si hay cobertura suficiente, construir un prior de actividad diel por especie (Amanecer/Día/
   Atardecer/Noche) con el mismo formato Laplace + control de fuga.

## Regla general para cualquiera de estos

Seguir siempre el protocolo ya validado en `pipeline_dataset/paquetes_zonales.py`: separar
train/test con el split congelado (`training/manifiesto.json`), calcular el prior **solo** con
train, evaluar Top-1/Top-3 en test, y **no integrar al paquete ni a la app si no hay mejora
medida**. El prior geográfico de zona (§ arriba) es el único que pasó ese filtro hasta ahora.

## Fuentes

[[Arquitectura Multimodal]] · [[Open-Set Recognition]] ·
[[05_OPEN_SET/PRIMERA_EVALUACION_UMBRAL_NO_RANA]]
