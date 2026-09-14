---
title: "Metodología â€” àndice"
proyecto: Anura
tipo: índice
tags: [anura, metodología, índice]
---

# Metodología â€” àndice

[[Anura â€” àndice General]]

Cómo funciona Anura: del dato de campo a la identificación explicada.

## Datos

| Nota | Qué cubre |
| --- | --- |
| [[Estrategia de Construcción del Dataset]] | Objetivos del dataset, fuentes primarias y secundarias, criterios de calidad y exclusión, augmentación, splits sin fuga, conjunto open-set |
| [[Listado de Individuos y Arreglo Taxonómico]] | Jerarquía Familia â†’ Género â†’ Especie del dataset y su procedencia geográfica |
| [[Estrategia para Especies con Cobertura Insuficiente]] | Qué hacer con las 8 especies por debajo de 70 individuos: techo de resolución por especie, cascada Familia â†’ Género â†’ Especie y reparto entre cabezas softmax y k-NN en sqlite-vec |

## Sistema

| Nota | Qué cubre |
| --- | --- |
| [[Pipeline del Sistema]] | Recorrido completo: captura â†’ segmentación â†’ embedding â†’ evidencia â†’ fusión â†’ open-set â†’ resultado |
| [[Arquitectura Multimodal]] | Las tres ramas (visión, audio, contexto) y cómo se fusionan |
| [[Open-Set Recognition]] | Cómo se responde "no está en mi catálogo" y cómo se evalàºa |

## Operación

| Nota | Qué cubre |
| --- | --- |
| [[Infraestructura]] | Servidor vs. dispositivo, entornos, costes, monitorización, copias de seguridad |
| [[Escalabilidad]] | Añadir especies sin reentrenar, versionado, crecimiento del índice y del catálogo |

## Hilo conductor

```
Dataset â”€â”€â–¶ Anotación â”€â”€â–¶ Segmentación â”€â”€â–¶ Embedding â”€â”€â–¶ Clasificación
   â”‚                                            â”‚              â”‚
   â”‚                                            â–¼              â–¼
   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¶ Base vectorial â—€â”€â”€â”€â”€â”€ Bàºsqueda        Open-set
                                       por similitud
                                            â”‚
                                            â–¼
                                   Fusión multimodal
                                            â–¼
                                    Identificación
                                       explicada
```

Las decisiones metodológicas que siguen abiertas están recogidas en [[Inconsistencias y Decisiones Pendientes]].



