---
title: "Curación e Ingesta"
tags: [admin, anura, curacion]
created: 2026-09-25
status: draft
---

# Curación e Ingesta

Fase 2 de [[Plan de Construccion del Admin]], más las reglas de la fase 1 del [[Roadmap Fase 1 y Fase 2]]. Pantallas: `/admin/datasets` y `/admin/curation`.

## Qué hace la persona

- Crear o importar un dataset y subir imágenes.
- Atar taxonomía, observación, individuo y fotografías según [[Modelo de Datos del Admin]].
- Marcar estadio y, si la ficha lo pide, el morph id.
- Detectar duplicados y fotos malas.
- Sacar una imagen del entrenamiento sin borrar la observación.
- Invalidar la observación completa, con motivo.
- Dejar trazabilidad de cada descarte.

## Filtros del primer ciclo, sin un detector entrenado

Todavía no hay YOLOv8 ni servidor Nuclio. La fuente lo deja para una fase posterior.

- **pHash:** quita duplicados y ráfagas.
- **Varianza del Laplaciano:** descarte por desenfoque si `Var < 100`.
- **CVAT manual:** el anotador dibuja el bounding box y el polígono de LRC en milímetros. La guía ya existente en el cerebro es [[Guía CVAT — Índice]].
- Especímenes de museo en formol y fotos inservibles se descartan. Esas especies, si no quedan fotos vivas, siguen el camino de [[Especies Entrenables y Huerfanas]].

## Lo que el diagrama promete y esta fase no exige

> [!WARNING] Contradicción detectada: scraping como si ya fuera el núcleo
> El cuadro del módulo administrativo lista conectores de GBIF, iNaturalist y SiB. El plan de construcción no los pone como requisito de la fase 2: primero se importa y se cura.
> **Decisión:** el scraper, cuando exista, propone filas y no publica. No bloquea datasets, fichas ni paquetes. Ver [[Decisiones de Escalabilidad del Admin]].

GPS, municipio y paquete se rellenan solos y se pueden corregir. OpenTopoData, en el prototipo, es un mock. Ver [[Modelo de Datos del Admin]].

## Huérfanas

El Admin necesita un control de especies sin foto utilizable (literatura, holotipo, menos de 10–15 fotos públicas). No entran al centroide. Entran al rechazo de campo como desconocidas, y una captura nueva puede convertirse en el primer material del centroide. El alta sigue siendo una decisión humana, no un publish automático. Ver [[Worker Releases y Sandbox]].
