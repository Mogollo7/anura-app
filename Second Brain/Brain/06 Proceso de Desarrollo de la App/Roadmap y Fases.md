---
title: "Roadmap y Fases"
proyecto: Anura
tipo: proceso-desarrollo
estado: propuesta
tags: [anura, proceso, roadmap, fases, producto]
---

# Roadmap y Fases

[[Anura â€” àndice General]] · [[Proceso de Desarrollo â€” àndice]] · [[Cronograma y Plan de Trabajo]] · [[Stack Tecnológico]] · [[Riesgos del Proyecto]]

> [!abstract] Qué es esta nota
> El recorrido de Anura desde el estado actual hasta una app funcionando en campo, ordenado por **dependencias reales** y no por deseos. Las fases 1 y 2 están fijadas en [[Objetivos y Alcance]]; aquí se descomponen en incrementos entregables.

> [!important] Sprint al 27 de septiembre de 2026
> El autor fijó fecha límite de prototipo el 2026-09-05: 22 días para llegar a la Fase 2 (incrementos 3.1â€“3.3 al menos) desplegada, en paralelo a la Fase 1 web como respaldo. La ruta día a día está en [[Cronograma y Plan de Trabajo]] §0 â€” es una versión con fechas reales y alcance recortado de las fases descritas abajo. La Fase 4 (piloto de campo) y el resto de la Fase 3 quedan para después del 27.

## 1. Estado actual

| àrea | Estado |
| --- | --- |
| Marco teórico y metodológico | âœ… Muy avanzado |
| Requisitos (RF/RNF) e historias de usuario | âœ… Definidos |
| Esquema de anotación (guía CVAT, 16 etiquetas) | âœ… v1.0 completa |
| Dataset | ðŸŸ¡ En construcción; Etapa I evaluada, pendiente reevaluar el split |
| Anotación en CVAT | ðŸ”´ Por ejecutar en volumen |
| Modelo de segmentación | ðŸ”´ No entrenado |
| Modelo de identificación | ðŸŸ¡ Prueba de Etapa I; falta pipeline con BioCLIP |
| Backend / API | ðŸ”´ Diseñado, no implementado |
| App móvil | ðŸ”´ No iniciada |
| Decisiones de arquitectura | ðŸ”´ Varias abiertas â†’ [[Inconsistencias y Decisiones Pendientes]] |

## 2. Principio que ordena todo el roadmap

> **Que funcione de extremo a extremo antes que funcione bien.**

La tentación natural es perfeccionar el modelo antes de tocar la app. Es un error de orden: el mayor riesgo del proyecto no es que el modelo tenga 82 % en vez de 88 %, sino **llegar sin app**. Un recorrido completo â€” foto â†’ inferencia â†’ resultado â†’ guardado â†’ sincronización â€” aunque sea con un modelo mediocre, elimina de golpe la mayor parte de la incertidumbre técnica y deja el resto del tiempo para mejorar sobre algo que ya existe.

## 3. Fases

### Fase 0 â€” Cimientos (bloqueante)

Nada de lo demás es fiable sin esto.

| Entregable | Nota |
| --- | --- |
| Decisiones de arquitectura cerradas | [[Inconsistencias y Decisiones Pendientes]] |
| Copias de seguridad de fotos y anotaciones | Riesgo D-6, sin plan B |
| Split congelado y verificado sin fuga | Riesgo D-1 |
| Repositorio, entornos y versionado de datos | [[Infraestructura]] |
| Permisos en trámite | Tiempos administrativos largos |

### Fase 1 â€” Nàºcleo de visión (el corazón del trabajo)

| Incremento | Entregable | Criterio de salida |
| --- | --- | --- |
| 1.1 | Anotación CVAT de 400â€“600 imágenes | Consistencia entre anotadores verificada |
| 1.2 | Modelo de segmentación v1 | Detecta `anuro_completo` de forma fiable |
| 1.3 | Extracción de embeddings BioCLIP | Embeddings cacheados para todo el dataset |
| 1.4 | Cabezas jerárquicas + línea base | Métricas de [[Métricas Offline]] rellenas |
| 1.5 | Open-set operativo | AUROC reportado, near y far separados |
| 1.6 | Preanotación del resto + corrección | Dataset v2 completo |

### Fase 2 â€” Plataforma web (validación y demostración)

| Incremento | Entregable |
| --- | --- |
| 2.1 | API `/identify` funcionando (RNF-01: â‰¤ 3 s) |
| 2.2 | Base vectorial + bàºsqueda por similitud |
| 2.3 | Fichas técnicas de especie (RF-10) |
| 2.4 | Web de carga y resultado con evidencia anatómica (RF-06) |
| 2.5 | Repositorio de observaciones y mapa (RF-09, RF-11) |

### Fase 3 â€” App móvil offline (el diferencial)

| Incremento | Entregable | Criterio de salida |
| --- | --- | --- |
| 3.1 | Esqueleto Android: captura, guardado local, listado | Funciona sin red, sin modelo |
| 3.2 | Modelos cuantizados embarcados | â‰¤ 150 MB (RNF-05) |
| 3.3 | Inferencia local completa | â‰¤ 4 s p95 (RNF-02) |
| 3.4 | Paquete regional + bàºsqueda vectorial local | Top-K sin red |
| 3.5 | Sincronización diferida | Sin pérdida ni duplicados (RF-13) |
| 3.6 | Captura y análisis de audio | RF-14 |
| 3.7 | Modo campo (una mano, oscuro, batería) | RNF-07 a RNF-09 |

> [!tip] 3.1 primero, y pronto
> El esqueleto de la app **no depende del modelo**. Se puede construir en paralelo a la Fase 1 usando un modelo provisional o resultados simulados. Es la mejor defensa contra el riesgo P-2 (quedarse sin tiempo para la Fase 2).

### Fase 4 â€” Validación en campo

| Incremento | Entregable |
| --- | --- |
| 4.1 | Piloto en â‰¥ 2 localidades â†’ [[Evaluación en Campo Real]] |
| 4.2 | Análisis de resultados y errores |
| 4.3 | Iteración correctiva sobre los hallazgos |
| 4.4 | Documento final y sustentación |

### Fase 5 â€” Más allá del trabajo de grado

Explícitamente fuera del alcance actual, àºtil para la sección de trabajo futuro: ampliación del catálogo de especies, versión iOS, exportación Darwin Core en producción (HU-05), módulo comunitario tipo iNaturalist a escala, reentrenamiento continuo con datos de la comunidad, publicación científica.

## 4. Alcance mínimo defendible

Si el tiempo se agota, esto es lo que **no** se puede recortar sin perder el trabajo:

1. Dataset verificado con split sin fuga.
2. Segmentación anatómica funcionando.
3. Identificación jerárquica con métricas honestas.
4. Open-set (es un objetivo específico declarado).
5. App Android que identifica **sin conexión**.
6. Evaluación de campo, aunque sea reducida.

Prescindible bajo presión, declarándolo como trabajo futuro: rama de audio, módulo comunitario web, exportación DwC, multi-individuo, fusión con variables ambientales en vivo.

## 5. Ritmo de trabajo sugerido

- **Iteraciones cortas** (1â€“2 semanas) con algo demostrable al final de cada una.
- **Una decisión arquitectónica a la vez**, registrada al tomarla en [[Inconsistencias y Decisiones Pendientes]].
- **Medir antes de optimizar**: casi todas las intuiciones sobre qué es lento o qué mejora la precisión resultan equivocadas.
- **Escribir el documento en paralelo**, no al final. Cada experimento cerrado es una sección redactada.



