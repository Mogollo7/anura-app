---
title: "Entradas y Ficha de Especie"
tags: [admin, anura, datos]
created: 2026-09-25
status: draft
---

# Entradas y Ficha de Especie

Lo que el herpetólogo o el administrador tienen que poder entregar para que el worker calcule centroides, barreras y el JSON. Texto íntegro: [[Fuente - Entradas del Administrador]]. La ficha en pantalla es la fase 3 de [[Plan de Construccion del Admin]].

Los cinco bloques no piden los mismos campos a todas las especies. Si la ficha dice que no hay morfos, ni juveniles, ni complejo, esos bloques quedan vacíos a propósito. Ver [[Modelo de Datos del Admin]].

## 1. Imágenes y taxonomía

- Fotos curadas de adultos. Mínimo de referencia: **10–15**, sin desenfoque extremo ni duplicados. El criterio fino de individuos está en [[Centroides y Muestras]].
- Nomenclatura: familia, género, `taxon_id`, nombre común. Ejemplos de la fuente, no altas automáticas: Strabomantidae, *Pristimantis*, `Pristimantis_illex`, «rana de lluvia de montaña».
- Estadio: adulto, juvenil, metamorfosis, larva.
- `morph_id` si es polimórfica (`red_morph`, `yellow_morph`).
- Export de CVAT / COCO: polígono o línea de longitud rostro-cloaca en milímetros, y bounding box.

## 2. Ficha ecológica y territorio

Sirve a la capa 3 de [[OSR en Tres Capas]] y a la asignación de paquetes.

- Altitud: media, desviación, o rango mínimo–máximo.
- Prior de sustrato entre **0,01** y **1,0**. Ejemplo de la fuente, no valor universal: hojarasca 0,90; vegetación 0,70; quebrada 0,05; roca 0,10.
- Lista de subregiones donde está confirmada. Ejemplo: `02_oriente` y `05_norte`.
- Pesos `wv + wg + wm = 1`. Son por especie y por paquete. Ver [[Contexto Ecologico y Pesos]].

## 3. Clúster críptico

- `cluster_id`. Ejemplo: `pristimantis_altiplano_cluster`.
- Miembros. Ejemplo: `Pristimantis_illex` y `Pristimantis_penelopus`.
- ArcFace: margen **0,35**, escala **30**, **20–50** épocas en la GPU local, y learning rate (la fuente lo nombra, no fija el número en este bloque).

## 4. Calibración OSR

- Factor de elasticidad **alfa** para el radio de rechazo de la especie.
- Tolerancia de reconstrucción **épsilon** del clúster.
- Umbrales de super-centroide que la persona valida: género alrededor de **0,62–0,65**, familia alrededor de **0,52–0,55**. Esos rangos son más estrechos que los de [[Cascada Taxonomica y Supercentroides]]. No unificarlos a ciegas: [[Contradicciones del Modo Administrativo]].

## 5. Metadatos del paquete

- Versión. Ejemplo: `v3.2.0`.
- Id. Ejemplo: `09_uraba_antioqueno`.
- Cuantización: **FP16** para pesar menos, o **FP32** para precisión completa. El cerebro ya adoptó FP16 para el ONNX en [[DECISION_LOG]]. El JSON de vectores debe declarar cuál usa.

## Salida esperada

Esos cinco bloques entran al worker del PC y sale un JSON por zona, pensado por debajo de **1 MB**. El esquema de campos está en [[Esquema JSON del Paquete]].
