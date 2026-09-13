---
title: "MetodologÃ­a â€” Ãndice"
proyecto: Anura
tipo: Ã­ndice
tags: [anura, metodologÃ­a, Ã­ndice]
---

# MetodologÃ­a â€” Ãndice

[[Anura â€” Ãndice General]]

CÃ³mo funciona Anura: del dato de campo a la identificaciÃ³n explicada.

## Datos

| Nota | QuÃ© cubre |
| --- | --- |
| [[Estrategia de ConstrucciÃ³n del Dataset]] | Objetivos del dataset, fuentes primarias y secundarias, criterios de calidad y exclusiÃ³n, augmentaciÃ³n, splits sin fuga, conjunto open-set |
| [[Listado de Individuos y Arreglo TaxonÃ³mico]] | JerarquÃ­a Familia â†’ GÃ©nero â†’ Especie del dataset y su procedencia geogrÃ¡fica |
| [[Estrategia para Especies con Cobertura Insuficiente]] | QuÃ© hacer con las 8 especies por debajo de 70 individuos: techo de resoluciÃ³n por especie, cascada Familia â†’ GÃ©nero â†’ Especie y reparto entre cabezas softmax y k-NN en sqlite-vec |

## Sistema

| Nota | QuÃ© cubre |
| --- | --- |
| [[Pipeline del Sistema]] | Recorrido completo: captura â†’ segmentaciÃ³n â†’ embedding â†’ evidencia â†’ fusiÃ³n â†’ open-set â†’ resultado |
| [[Arquitectura Multimodal]] | Las tres ramas (visiÃ³n, audio, contexto) y cÃ³mo se fusionan |
| [[Open-Set Recognition]] | CÃ³mo se responde "no estÃ¡ en mi catÃ¡logo" y cÃ³mo se evalÃºa |

## OperaciÃ³n

| Nota | QuÃ© cubre |
| --- | --- |
| [[Infraestructura]] | Servidor vs. dispositivo, entornos, costes, monitorizaciÃ³n, copias de seguridad |
| [[Escalabilidad]] | AÃ±adir especies sin reentrenar, versionado, crecimiento del Ã­ndice y del catÃ¡logo |

## Hilo conductor

```
Dataset â”€â”€â–¶ AnotaciÃ³n â”€â”€â–¶ SegmentaciÃ³n â”€â”€â–¶ Embedding â”€â”€â–¶ ClasificaciÃ³n
   â”‚                                            â”‚              â”‚
   â”‚                                            â–¼              â–¼
   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¶ Base vectorial â—€â”€â”€â”€â”€â”€ BÃºsqueda        Open-set
                                       por similitud
                                            â”‚
                                            â–¼
                                   FusiÃ³n multimodal
                                            â–¼
                                    IdentificaciÃ³n
                                       explicada
```

Las decisiones metodolÃ³gicas que siguen abiertas estÃ¡n recogidas en [[Inconsistencias y Decisiones Pendientes]].



