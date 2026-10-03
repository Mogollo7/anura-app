---
title: "Anura â€” àndice General"
proyecto: Anura
tipo: índice
tags: [anura, moc, índice]
---

# ðŸ¸ Anura â€” àndice General

Aplicación móvil con IA para la identificación de anfibios del orden *Anura* en Colombia, mediante visión por computador, segmentación anatómica, bioacàºstica y contexto geográfico, con funcionamiento **offline** en campo.

> [!tip] Por dónde empezar
> - ¿Qué es el proyecto? â†’ [[Introducción y Justificación]] · [[Objetivos y Alcance]]
> - ¿Cómo se construye la app? â†’ [[Roadmap y Fases]]
> - ¿Qué hay que decidir ya? â†’ [[Inconsistencias y Decisiones Pendientes]] ðŸ”´
> - ¿Cómo se anotan las imágenes? â†’ [[Guía CVAT â€” àndice]]

> [!important] Prototipo debido el 27 de septiembre de 2026
> Sprint de 22 días fijado el 2026-09-05, desde hoy hasta un APK + demo web funcionando de extremo a extremo sobre el catálogo de **28 especies**. Ruta semana a semana en [[Cronograma y Plan de Trabajo]] §0. El piloto de campo, el documento final y la sustentación quedan secuenciados después del 27.

---

## 01 · Proyecto

Fundamentos, alcance y gestión.

| Nota | Contenido |
| --- | --- |
| [[Introducción y Justificación]] | Contexto ecológico, problema y justificación |
| [[Referente Teórico]] | Anfibios, bioacàºstica, IA, visión por computador, BioCLIP |
| [[Objetivos y Alcance]] | Objetivos, requisitos funcionales y no funcionales, delimitaciones |
| [[Historias de Usuario]] | HU-01 a HU-05 con criterios de aceptación |
| [[Cronograma y Plan de Trabajo]] | Hitos, ruta crítica, puntos de decisión |
| [[Riesgos del Proyecto]] | Riesgos técnicos, de datos, de alcance y éticos |
| [[Consideraciones Ecológicas y Éticas]] | Bioseguridad, manejo, permisos, datos sensibles |
| [[Bibliografía]] | Referencias del proyecto |

## 02 · Metodología

Cómo funciona el sistema. â†’ [[Metodología â€” àndice]]

| Nota | Contenido |
| --- | --- |
| [[Estrategia de Construcción del Dataset]] | Fuentes, calidad, augmentación, splits, open-set |
| [[Dataset Jerárquico de Colombia â€” Paquetes Departamentales]] | Colombiaâ†’Departamentoâ†’Especieâ†’Zonas · `taxon_id` estables · point-in-polygon DANE |
| [[Listado de Individuos y Arreglo Taxonómico]] | Familias, géneros y especies del dataset |
| [[Pipeline del Sistema]] | Recorrido completo de una observación |
| [[Arquitectura Multimodal]] | Visión + audio + contexto y su fusión |
| [[Open-Set Recognition]] | Detección de especies no registradas |
| [[Infraestructura]] | Servidor vs. dispositivo, entornos, monitorización |
| [[Escalabilidad]] | Añadir especies, versionado, crecimiento del índice |

## 03 · Anotación y Segmentación

El esquema que enseña al modelo qué mirar.

| Nota | Contenido |
| --- | --- |
| [[Guía CVAT â€” àndice]] | **Manual completo de anotación (v1.0)** â€” 11 secciones, 44 figuras |
| [[Guía de Anotación Roboflow (histórico)]] | Esquema anterior de 8 clases (sustituido) |

## 04 · Desarrollo Técnico

Los modelos y servicios.

| Nota | Contenido |
| --- | --- |
| [[Plan de Acción y Arquitectura Conceptual]] | Idea general y tecnologías (documento original, parcialmente superado) |
| [[Modelo de Visión â€” BioCLIP]] | **àšnico backbone del proyecto** â€” visión y, reutilizado, audio |
| [[Implementación de Triplet Loss]] | Metric learning sobre el espacio de embeddings |
| [[Base Vectorial (SQLite-vec)]] | Memoria de ejemplares · motor móvil firmado: k-NN + SQLite-vec (C-15, patrón Merlin) |
| [[API Backend]] | Endpoints, modelo de datos, sincronización |
| [[App Móvil]] | Android, offline, presupuestos |
| [[Optimización para Inferencia en Móvil]] | Cuantización, LiteRT, latencia |
| [[Automatización del Entrenamiento de Segmentación]] | Pipeline con supervisión, sin entrenamiento manual |

## 05 · Evaluación y Métricas

â†’ [[Evaluación y Métricas â€” àndice]]

| Nota | Contenido |
| --- | --- |
| [[Métricas Offline]] | Tablas de resultados en test |
| [[Matrices de Confusión]] | Análisis de errores por nivel taxonómico |
| [[Evaluación en Campo Real]] | Protocolo del piloto |
| [[Reportes de Pruebas Piloto]] | Plantilla y consolidado por salida |
| [[Experimentos y Resultados]] | Bitácora y cola de experimentos |

## 06 · Proceso de Desarrollo de la App

â†’ [[Proceso de Desarrollo â€” àndice]]

| Nota | Contenido |
| --- | --- |
| [[Roadmap y Fases]] | De hoy a la app en campo |
| [[Stack Tecnológico]] | Todas las tecnologías y por qué |
| [[Arquitectura de la Aplicación]] | Capas, módulos, dominio, pantallas |
| [[Diseño de Interfaz (Penpot)]] | Sistema de componentes, pantallas, navegación, trazabilidad RF/RNF |
| [[Flujo de Datos y Sincronización]] | Offline-first, colas, paquetes regionales |
| [[Ciclo de Vida del Modelo (MLOps)]] | Versionado, trazabilidad, reentrenamiento |
| [[Entorno de Trabajo y MCP]] | Penpot vía MCP, método de trabajo y trampas del API |

## 07 · Notas de Trabajo

| Nota | Contenido |
| --- | --- |
| [[Inconsistencias y Decisiones Pendientes]] | ðŸ”´ Contradicciones detectadas entre documentos |

## 00 · Fuentes Originales

Material del autor, conservado sin modificar.

- [[Notas Originales â€” Segmentación Semántica y Metodología Anura]]
- [[Notas Originales â€” Método de Anotación y Plantillas Taxonómicas]]
- [[Notas Originales â€” Añadir Nueva Información]]

## 99 · Recursos

`99 Recursos/Attachments/` â€” 45 imágenes (44 figuras de la guía CVAT + esquema conceptual)
`99 Recursos/Guia_CVAT_Anuro v1.0.docx` â€” documento original

---

## Estado del proyecto de un vistazo

| àrea | Estado |
| --- | --- |
| Marco teórico y metodológico | âœ… Muy avanzado |
| Requisitos e historias de usuario | âœ… Definidos |
| Esquema de anotación (16 etiquetas) | âœ… Guía v1.0 completa |
| Dataset | ðŸŸ¡ En construcción; split por reevaluar |
| Anotación en volumen | ðŸ”´ Por ejecutar |
| Modelos | ðŸ”´ Por entrenar |
| Diseño de interfaz (mockup) | ðŸŸ¢ ~42 pantallas en Penpot, navegación cableada â†’ [[Diseño de Interfaz (Penpot)]] |
| Backend / App | ðŸ”´ Diseñados, no implementados |
| Decisiones de arquitectura | ðŸŸ¢ 6 resueltas, 1 parcial (segmentación concreta), 1 abierta (Qdrant vs. pgvector en servidor) |

## Decisiones ya resueltas

- âœ… **BioCLIP es el àºnico modelo del proyecto** â€” visión y audio (mismo codificador reutilizado sobre el espectrograma). Se retiró EfficientNet como alternativa de arquitectura.
- âœ… **BioCLIP v1 (ViT-B/16), en dispositivo y servidor**, para el sprint del prototipo â€” evita el problema de espacios de embedding incompatibles entre v1/v2 dentro de los 22 días.
- âœ… **Motor vectorial embebido para el móvil: ObjectBox** â€” Qdrant sigue en el servidor; el dispositivo usa ObjectBox (HNSW nativo para Android/Kotlin).
- âœ… **El ~99 % de la Etapa I es un resultado legítimo**, no fuga de información: se explica por segmentación binaria (individuo vs. fondo) antes de BioCLIP + `GroupSplit` por individuo. Ver [[Modelo de Visión â€” BioCLIP]] §7.
- âœ… **Catálogo oficial: 28 especies** para el prototipo â€” coincide con la recolección de campo ya organizada por equipos y con `anuro_labels.json`.
- âœ… **Alcance mínimo del prototipo (27 sep) fijado** â†’ [[Cronograma y Plan de Trabajo]] §0.

## Los frentes que siguen abiertos

1. **Copias de seguridad** de fotos y anotaciones (riesgo sin plan B)
2. **Validar ObjectBox empíricamente** en el dispositivo de referencia (latencia, memoria)
3. **Modelo de segmentación concreto** â€” tamaño de YOLO-seg (n vs. s) por confirmar con los datos reales de la semana del 9â€“11 sep
4. **Cobertura real de audio** en AnuraSet/Xeno-canto para las 28 especies â€” decide si la rama acàºstica entra al prototipo o queda como trabajo futuro
5. **Alcance mínimo defendible del trabajo de grado completo** (distinto del alcance del prototipo, ya resuelto) â€” sigue pendiente para cuando se fije la fecha de sustentación

Detalle en [[Inconsistencias y Decisiones Pendientes]] y [[Riesgos del Proyecto]].



