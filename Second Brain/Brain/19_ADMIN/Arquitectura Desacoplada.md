---
title: "Arquitectura Desacoplada"
tags: [admin, anura, arquitectura]
created: 2026-09-25
status: draft
---

# Arquitectura Desacoplada

Principio que ordena al [[Modo Administrativo]]: el extractor visual y el catálogo no viajan juntos. Fuentes literales: [[Fuente - Documento Maestro de Arquitectura]] y [[Fuente - Estrategia de Arquitectura y Transfer Learning]]. Son casi el mismo documento; el maestro es la variante más completa. Los choques numéricos están en [[Contradicciones del Modo Administrativo]].

## Dos sitios

**Teléfono, sin red.** Foto, y si hay sensor, GPS, altitud y microhábitat. BioCLIP 1 congelado en ONNX produce un vector de **512**. El paquete JSON local hace la cascada: especie o clúster, género, familia, o rechazo. Inferencia en el dispositivo, costo de consulta **0 USD** en APIs. Instalación del encoder, una sola vez.

**PC local, cuando hay red.** Una cola (la fuente nombra Hostinger, del orden de **3–8 USD/mes**) recibe capturas. El trabajo pesado corre en un PC con GPU NVIDIA: auditoría con **BioCLIP 2.5** (ViT-H/14, **1024** dimensiones), entrenamiento del micro-adaptador y compilación del JSON. El 1024 no se mezcla con el 512 del paquete. Ver [[OSR en Tres Capas]].

## Cuatro reglas

- El ONNX móvil no se reentrena ni se vuelve a descargar para añadir una especie.
- Lo que cambia es el JSON de la subregión.
- El transfer clásico sobre todo el ViT se considera olvido catastrófico. La alternativa adoptada es el micro-adaptador: [[Microadaptadores y Transfer Learning]].
- Especie visualmente clara: se añade el centroide (~2 KB). Especie de un complejo: se reentrena solo la matriz de ese complejo.

## El módulo administrativo, en una frase

Es el lugar del PC donde se ingiere, se anota, se fijan pesos, se calculan centroides L2 y se compila el paquete. No es una pantalla más de la app de campo. El despiece en fases está en [[Plan de Construccion del Admin]].

## Cifras de las fuentes que no debes copiar como medición

ONNX «~100 MB» o «100–150 MB», latencia menor de 100 o 150 ms, y «filtra el 90 % de especies no viables por GPS». El vault midió otro artefacto: **165,6 MB** y **154 ms** a 4 hilos, **403 ms** a 1 hilo ([[DECISION_LOG]]). El Admin muestra la medición del experimento, y deja estas frases como objetivo.
