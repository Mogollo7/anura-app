---
title: "Contexto Ecológico y Pesos"
tags: [admin, anura, contexto]
created: 2026-09-25
status: draft
---

# Contexto Ecológico y Pesos

El contexto no entra al encoder. Llega después, como prior. Fuentes: [[Fuente - Contexto Multimodal]], [[Fuente - Pesos Variables por Especie]], y las secciones de pesos del documento maestro.

## Variables

| Variable | Importancia en la fuente | Cómo se captura | Papel |
| --- | --- | --- | --- |
| GPS | 10/10 | Sensor, también offline si ya hay fix | Elige el paquete |
| Altitud | 10/10 | DEM offline, barómetro o servicio de elevación | Gaussiana de la especie |
| Hora y temporada | 8/10 | Reloj del teléfono | Actividad diurna o nocturna, lluvias |
| Microhábitat | 8/10 | Chip de un toque | Prior de sustrato |
| Canto | 10/10 para gemelas | 3–5 segundos | Desempate. **Fase 2**, no bloquea el primer ciclo |
| LRC aproximada | 6/10 | Categoría o slider | Juvenil de especie grande frente a adulto pigmeo. **Fase 2** como filtro activo |

Chips de sustrato citados: hoja o vegetación, hojarasca o suelo, cerca de quebrada, roca, bajo corteza. La ficha de entradas usa hojarasca, vegetación, quebrada y roca. Unificar la lista en la ficha, sin perder opciones: el enum del Admin debe cubrir las cinco y permitir prior 0.

## Por qué el peso no es global

Un generalista (*Rhinella horribilis* en el ejemplo: mar a 2000 m, potrero, jardín, borde) no puede usar el mismo castigo geográfico que una *Pristimantis* de páramo citada entre 2800 y 3200 m. Si el GPS cae a 500 m, esa endémica tiene que colapsar aunque la foto se parezca.

| Perfil | Visual | Geo / altitud | Microhábitat | Notas de la fuente |
| --- | --- | --- | --- | --- |
| Generalista | 70–80, o 80 fijo | 10–15, o 10; σ = 1000 m | 5–10, o 10 | Manda la imagen |
| Endémica de montaña | 30–40, o 30 | 50–60, o 60; σ = 120 m | 10 | Corta si la cota no cuadra |
| Par críptico | 35 | 35 | 30, o canto | El contexto desempata |
| Especialista de quebrada | 50 | 20 | 30 | Solo en la nota de pesos variables |
| Aposemática muy distinta | alto en la imagen | bajo | bajo | Ejemplo *Oophaga histrionica* a 0,98 de similitud |

> [!WARNING] Contradicción detectada: tres tablas y un experimento viejo
> El maestro fija 80/10/10. La otra nota da rangos y añade el perfil de quebrada. El JSON de Oophaga usa 0,85/0,10/0,05. El EXP-007 del cerebro usó un prior geográfico único de 0,75.
> **Decisión:** plantillas, no ley. Calculado, manual y efectivo por especie y paquete. El 0,75 no se guarda en `wg`. El corte de altitud es `umbral_geo`, configurable por paquete. 0,05 es el valor inicial. Ver [[Decisiones de Escalabilidad del Admin]].

## Cómo se calcula sin una cadena de if

Cada especie en el JSON guarda `altitude_mean_msnm`, `altitude_std_dev` y priors de hábitat. La altitud entra como gaussiana. σ pequeño (120 m) tira el puntaje a cero lejos de la media. σ grande (1000 m) deja mandar a la similitud visual.

La suma `wv + wg + wm` es 1. El corte de altitud no es el número fijo 0,05: es `umbral_geo` del paquete, y la política dice si eso rechaza o solo penaliza. El hábitat pondera aparte. Ver [[Decisiones de Escalabilidad del Admin]].

El Admin puede estimar la gaussiana desde los registros y, además, ofrecer sliders de override. Caso de la fuente: especie riparia con `wm = 0,50` si no hay agua. El override es visible. No sustituye al valor manual en silencio.

Los pesos de *Oriente* y de *Urabá* para la misma especie pueden diferir. Ejemplo de la fuente: especie A en Oriente 0,70 / 0,20 / 0,10; especie C en Urabá 0,60 / 0,10 / 0,30.

Hora y temporada están descritas y todavía no tienen campo en el JSON de ejemplo. Reservarlas en la ficha; no bloquear el compilador del primer ciclo.
