---
title: "Roadmap y Fases"
proyecto: Anura
tipo: proceso-desarrollo
estado: propuesta
tags: [anura, proceso, roadmap, fases, producto]
---

# Roadmap y Fases

[[Anura â€” Ãndice General]] Â· [[Proceso de Desarrollo â€” Ãndice]] Â· [[Cronograma y Plan de Trabajo]] Â· [[Stack TecnolÃ³gico]] Â· [[Riesgos del Proyecto]]

> [!abstract] QuÃ© es esta nota
> El recorrido de Anura desde el estado actual hasta una app funcionando en campo, ordenado por **dependencias reales** y no por deseos. Las fases 1 y 2 estÃ¡n fijadas en [[Objetivos y Alcance]]; aquÃ­ se descomponen en incrementos entregables.

> [!important] Sprint al 27 de septiembre de 2026
> El autor fijÃ³ fecha lÃ­mite de prototipo el 2026-09-05: 22 dÃ­as para llegar a la Fase 2 (incrementos 3.1â€“3.3 al menos) desplegada, en paralelo a la Fase 1 web como respaldo. La ruta dÃ­a a dÃ­a estÃ¡ en [[Cronograma y Plan de Trabajo]] Â§0 â€” es una versiÃ³n con fechas reales y alcance recortado de las fases descritas abajo. La Fase 4 (piloto de campo) y el resto de la Fase 3 quedan para despuÃ©s del 27.

## 1. Estado actual

| Ãrea | Estado |
| --- | --- |
| Marco teÃ³rico y metodolÃ³gico | âœ… Muy avanzado |
| Requisitos (RF/RNF) e historias de usuario | âœ… Definidos |
| Esquema de anotaciÃ³n (guÃ­a CVAT, 16 etiquetas) | âœ… v1.0 completa |
| Dataset | ðŸŸ¡ En construcciÃ³n; Etapa I evaluada, pendiente reevaluar el split |
| AnotaciÃ³n en CVAT | ðŸ”´ Por ejecutar en volumen |
| Modelo de segmentaciÃ³n | ðŸ”´ No entrenado |
| Modelo de identificaciÃ³n | ðŸŸ¡ Prueba de Etapa I; falta pipeline con BioCLIP |
| Backend / API | ðŸ”´ DiseÃ±ado, no implementado |
| App mÃ³vil | ðŸ”´ No iniciada |
| Decisiones de arquitectura | ðŸ”´ Varias abiertas â†’ [[Inconsistencias y Decisiones Pendientes]] |

## 2. Principio que ordena todo el roadmap

> **Que funcione de extremo a extremo antes que funcione bien.**

La tentaciÃ³n natural es perfeccionar el modelo antes de tocar la app. Es un error de orden: el mayor riesgo del proyecto no es que el modelo tenga 82 % en vez de 88 %, sino **llegar sin app**. Un recorrido completo â€” foto â†’ inferencia â†’ resultado â†’ guardado â†’ sincronizaciÃ³n â€” aunque sea con un modelo mediocre, elimina de golpe la mayor parte de la incertidumbre tÃ©cnica y deja el resto del tiempo para mejorar sobre algo que ya existe.

## 3. Fases

### Fase 0 â€” Cimientos (bloqueante)

Nada de lo demÃ¡s es fiable sin esto.

| Entregable | Nota |
| --- | --- |
| Decisiones de arquitectura cerradas | [[Inconsistencias y Decisiones Pendientes]] |
| Copias de seguridad de fotos y anotaciones | Riesgo D-6, sin plan B |
| Split congelado y verificado sin fuga | Riesgo D-1 |
| Repositorio, entornos y versionado de datos | [[Infraestructura]] |
| Permisos en trÃ¡mite | Tiempos administrativos largos |

### Fase 1 â€” NÃºcleo de visiÃ³n (el corazÃ³n del trabajo)

| Incremento | Entregable | Criterio de salida |
| --- | --- | --- |
| 1.1 | AnotaciÃ³n CVAT de 400â€“600 imÃ¡genes | Consistencia entre anotadores verificada |
| 1.2 | Modelo de segmentaciÃ³n v1 | Detecta `anuro_completo` de forma fiable |
| 1.3 | ExtracciÃ³n de embeddings BioCLIP | Embeddings cacheados para todo el dataset |
| 1.4 | Cabezas jerÃ¡rquicas + lÃ­nea base | MÃ©tricas de [[MÃ©tricas Offline]] rellenas |
| 1.5 | Open-set operativo | AUROC reportado, near y far separados |
| 1.6 | PreanotaciÃ³n del resto + correcciÃ³n | Dataset v2 completo |

### Fase 2 â€” Plataforma web (validaciÃ³n y demostraciÃ³n)

| Incremento | Entregable |
| --- | --- |
| 2.1 | API `/identify` funcionando (RNF-01: â‰¤ 3 s) |
| 2.2 | Base vectorial + bÃºsqueda por similitud |
| 2.3 | Fichas tÃ©cnicas de especie (RF-10) |
| 2.4 | Web de carga y resultado con evidencia anatÃ³mica (RF-06) |
| 2.5 | Repositorio de observaciones y mapa (RF-09, RF-11) |

### Fase 3 â€” App mÃ³vil offline (el diferencial)

| Incremento | Entregable | Criterio de salida |
| --- | --- | --- |
| 3.1 | Esqueleto Android: captura, guardado local, listado | Funciona sin red, sin modelo |
| 3.2 | Modelos cuantizados embarcados | â‰¤ 150 MB (RNF-05) |
| 3.3 | Inferencia local completa | â‰¤ 4 s p95 (RNF-02) |
| 3.4 | Paquete regional + bÃºsqueda vectorial local | Top-K sin red |
| 3.5 | SincronizaciÃ³n diferida | Sin pÃ©rdida ni duplicados (RF-13) |
| 3.6 | Captura y anÃ¡lisis de audio | RF-14 |
| 3.7 | Modo campo (una mano, oscuro, baterÃ­a) | RNF-07 a RNF-09 |

> [!tip] 3.1 primero, y pronto
> El esqueleto de la app **no depende del modelo**. Se puede construir en paralelo a la Fase 1 usando un modelo provisional o resultados simulados. Es la mejor defensa contra el riesgo P-2 (quedarse sin tiempo para la Fase 2).

### Fase 4 â€” ValidaciÃ³n en campo

| Incremento | Entregable |
| --- | --- |
| 4.1 | Piloto en â‰¥ 2 localidades â†’ [[EvaluaciÃ³n en Campo Real]] |
| 4.2 | AnÃ¡lisis de resultados y errores |
| 4.3 | IteraciÃ³n correctiva sobre los hallazgos |
| 4.4 | Documento final y sustentaciÃ³n |

### Fase 5 â€” MÃ¡s allÃ¡ del trabajo de grado

ExplÃ­citamente fuera del alcance actual, Ãºtil para la secciÃ³n de trabajo futuro: ampliaciÃ³n del catÃ¡logo de especies, versiÃ³n iOS, exportaciÃ³n Darwin Core en producciÃ³n (HU-05), mÃ³dulo comunitario tipo iNaturalist a escala, reentrenamiento continuo con datos de la comunidad, publicaciÃ³n cientÃ­fica.

## 4. Alcance mÃ­nimo defendible

Si el tiempo se agota, esto es lo que **no** se puede recortar sin perder el trabajo:

1. Dataset verificado con split sin fuga.
2. SegmentaciÃ³n anatÃ³mica funcionando.
3. IdentificaciÃ³n jerÃ¡rquica con mÃ©tricas honestas.
4. Open-set (es un objetivo especÃ­fico declarado).
5. App Android que identifica **sin conexiÃ³n**.
6. EvaluaciÃ³n de campo, aunque sea reducida.

Prescindible bajo presiÃ³n, declarÃ¡ndolo como trabajo futuro: rama de audio, mÃ³dulo comunitario web, exportaciÃ³n DwC, multi-individuo, fusiÃ³n con variables ambientales en vivo.

## 5. Ritmo de trabajo sugerido

- **Iteraciones cortas** (1â€“2 semanas) con algo demostrable al final de cada una.
- **Una decisiÃ³n arquitectÃ³nica a la vez**, registrada al tomarla en [[Inconsistencias y Decisiones Pendientes]].
- **Medir antes de optimizar**: casi todas las intuiciones sobre quÃ© es lento o quÃ© mejora la precisiÃ³n resultan equivocadas.
- **Escribir el documento en paralelo**, no al final. Cada experimento cerrado es una secciÃ³n redactada.



