---
title: "Anura â€” Ãndice General"
proyecto: Anura
tipo: Ã­ndice
tags: [anura, moc, Ã­ndice]
---

# ðŸ¸ Anura â€” Ãndice General

AplicaciÃ³n mÃ³vil con IA para la identificaciÃ³n de anfibios del orden *Anura* en Colombia, mediante visiÃ³n por computador, segmentaciÃ³n anatÃ³mica, bioacÃºstica y contexto geogrÃ¡fico, con funcionamiento **offline** en campo.

> [!tip] Por dÃ³nde empezar
> - Â¿QuÃ© es el proyecto? â†’ [[IntroducciÃ³n y JustificaciÃ³n]] Â· [[Objetivos y Alcance]]
> - Â¿CÃ³mo se construye la app? â†’ [[Roadmap y Fases]]
> - Â¿QuÃ© hay que decidir ya? â†’ [[Inconsistencias y Decisiones Pendientes]] ðŸ”´
> - Â¿CÃ³mo se anotan las imÃ¡genes? â†’ [[GuÃ­a CVAT â€” Ãndice]]

> [!important] Prototipo debido el 27 de septiembre de 2026
> Sprint de 22 dÃ­as fijado el 2026-09-05, desde hoy hasta un APK + demo web funcionando de extremo a extremo sobre el catÃ¡logo de **28 especies**. Ruta semana a semana en [[Cronograma y Plan de Trabajo]] Â§0. El piloto de campo, el documento final y la sustentaciÃ³n quedan secuenciados despuÃ©s del 27.

---

## 01 Â· Proyecto

Fundamentos, alcance y gestiÃ³n.

| Nota | Contenido |
| --- | --- |
| [[IntroducciÃ³n y JustificaciÃ³n]] | Contexto ecolÃ³gico, problema y justificaciÃ³n |
| [[Referente TeÃ³rico]] | Anfibios, bioacÃºstica, IA, visiÃ³n por computador, BioCLIP |
| [[Objetivos y Alcance]] | Objetivos, requisitos funcionales y no funcionales, delimitaciones |
| [[Historias de Usuario]] | HU-01 a HU-05 con criterios de aceptaciÃ³n |
| [[Cronograma y Plan de Trabajo]] | Hitos, ruta crÃ­tica, puntos de decisiÃ³n |
| [[Riesgos del Proyecto]] | Riesgos tÃ©cnicos, de datos, de alcance y Ã©ticos |
| [[Consideraciones EcolÃ³gicas y Ã‰ticas]] | Bioseguridad, manejo, permisos, datos sensibles |
| [[BibliografÃ­a]] | Referencias del proyecto |

## 02 Â· MetodologÃ­a

CÃ³mo funciona el sistema. â†’ [[MetodologÃ­a â€” Ãndice]]

| Nota | Contenido |
| --- | --- |
| [[Estrategia de ConstrucciÃ³n del Dataset]] | Fuentes, calidad, augmentaciÃ³n, splits, open-set |
| [[Dataset JerÃ¡rquico de Colombia â€” Paquetes Departamentales]] | Colombiaâ†’Departamentoâ†’Especieâ†’Zonas Â· `taxon_id` estables Â· point-in-polygon DANE |
| [[Listado de Individuos y Arreglo TaxonÃ³mico]] | Familias, gÃ©neros y especies del dataset |
| [[Pipeline del Sistema]] | Recorrido completo de una observaciÃ³n |
| [[Arquitectura Multimodal]] | VisiÃ³n + audio + contexto y su fusiÃ³n |
| [[Open-Set Recognition]] | DetecciÃ³n de especies no registradas |
| [[Infraestructura]] | Servidor vs. dispositivo, entornos, monitorizaciÃ³n |
| [[Escalabilidad]] | AÃ±adir especies, versionado, crecimiento del Ã­ndice |

## 03 Â· AnotaciÃ³n y SegmentaciÃ³n

El esquema que enseÃ±a al modelo quÃ© mirar.

| Nota | Contenido |
| --- | --- |
| [[GuÃ­a CVAT â€” Ãndice]] | **Manual completo de anotaciÃ³n (v1.0)** â€” 11 secciones, 44 figuras |
| [[GuÃ­a de AnotaciÃ³n Roboflow (histÃ³rico)]] | Esquema anterior de 8 clases (sustituido) |

## 04 Â· Desarrollo TÃ©cnico

Los modelos y servicios.

| Nota | Contenido |
| --- | --- |
| [[Plan de AcciÃ³n y Arquitectura Conceptual]] | Idea general y tecnologÃ­as (documento original, parcialmente superado) |
| [[Modelo de VisiÃ³n â€” BioCLIP]] | **Ãšnico backbone del proyecto** â€” visiÃ³n y, reutilizado, audio |
| [[ImplementaciÃ³n de Triplet Loss]] | Metric learning sobre el espacio de embeddings |
| [[Base Vectorial (SQLite-vec)]] | Memoria de ejemplares Â· motor mÃ³vil firmado: k-NN + SQLite-vec (C-15, patrÃ³n Merlin) |
| [[API Backend]] | Endpoints, modelo de datos, sincronizaciÃ³n |
| [[App MÃ³vil]] | Android, offline, presupuestos |
| [[OptimizaciÃ³n para Inferencia en MÃ³vil]] | CuantizaciÃ³n, LiteRT, latencia |
| [[AutomatizaciÃ³n del Entrenamiento de SegmentaciÃ³n]] | Pipeline con supervisiÃ³n, sin entrenamiento manual |

## 05 Â· EvaluaciÃ³n y MÃ©tricas

â†’ [[EvaluaciÃ³n y MÃ©tricas â€” Ãndice]]

| Nota | Contenido |
| --- | --- |
| [[MÃ©tricas Offline]] | Tablas de resultados en test |
| [[Matrices de ConfusiÃ³n]] | AnÃ¡lisis de errores por nivel taxonÃ³mico |
| [[EvaluaciÃ³n en Campo Real]] | Protocolo del piloto |
| [[Reportes de Pruebas Piloto]] | Plantilla y consolidado por salida |
| [[Experimentos y Resultados]] | BitÃ¡cora y cola de experimentos |

## 06 Â· Proceso de Desarrollo de la App

â†’ [[Proceso de Desarrollo â€” Ãndice]]

| Nota | Contenido |
| --- | --- |
| [[Roadmap y Fases]] | De hoy a la app en campo |
| [[Stack TecnolÃ³gico]] | Todas las tecnologÃ­as y por quÃ© |
| [[Arquitectura de la AplicaciÃ³n]] | Capas, mÃ³dulos, dominio, pantallas |
| [[DiseÃ±o de Interfaz (Penpot)]] | Sistema de componentes, pantallas, navegaciÃ³n, trazabilidad RF/RNF |
| [[Flujo de Datos y SincronizaciÃ³n]] | Offline-first, colas, paquetes regionales |
| [[Ciclo de Vida del Modelo (MLOps)]] | Versionado, trazabilidad, reentrenamiento |
| [[Entorno de Trabajo y MCP]] | Penpot vÃ­a MCP, mÃ©todo de trabajo y trampas del API |

## 07 Â· Notas de Trabajo

| Nota | Contenido |
| --- | --- |
| [[Inconsistencias y Decisiones Pendientes]] | ðŸ”´ Contradicciones detectadas entre documentos |

## 00 Â· Fuentes Originales

Material del autor, conservado sin modificar.

- [[Notas Originales â€” SegmentaciÃ³n SemÃ¡ntica y MetodologÃ­a Anura]]
- [[Notas Originales â€” MÃ©todo de AnotaciÃ³n y Plantillas TaxonÃ³micas]]
- [[Notas Originales â€” AÃ±adir Nueva InformaciÃ³n]]

## 99 Â· Recursos

`99 Recursos/Attachments/` â€” 45 imÃ¡genes (44 figuras de la guÃ­a CVAT + esquema conceptual)
`99 Recursos/Guia_CVAT_Anuro v1.0.docx` â€” documento original

---

## Estado del proyecto de un vistazo

| Ãrea | Estado |
| --- | --- |
| Marco teÃ³rico y metodolÃ³gico | âœ… Muy avanzado |
| Requisitos e historias de usuario | âœ… Definidos |
| Esquema de anotaciÃ³n (16 etiquetas) | âœ… GuÃ­a v1.0 completa |
| Dataset | ðŸŸ¡ En construcciÃ³n; split por reevaluar |
| AnotaciÃ³n en volumen | ðŸ”´ Por ejecutar |
| Modelos | ðŸ”´ Por entrenar |
| DiseÃ±o de interfaz (mockup) | ðŸŸ¢ ~42 pantallas en Penpot, navegaciÃ³n cableada â†’ [[DiseÃ±o de Interfaz (Penpot)]] |
| Backend / App | ðŸ”´ DiseÃ±ados, no implementados |
| Decisiones de arquitectura | ðŸŸ¢ 6 resueltas, 1 parcial (segmentaciÃ³n concreta), 1 abierta (Qdrant vs. pgvector en servidor) |

## Decisiones ya resueltas

- âœ… **BioCLIP es el Ãºnico modelo del proyecto** â€” visiÃ³n y audio (mismo codificador reutilizado sobre el espectrograma). Se retirÃ³ EfficientNet como alternativa de arquitectura.
- âœ… **BioCLIP v1 (ViT-B/16), en dispositivo y servidor**, para el sprint del prototipo â€” evita el problema de espacios de embedding incompatibles entre v1/v2 dentro de los 22 dÃ­as.
- âœ… **Motor vectorial embebido para el mÃ³vil: ObjectBox** â€” Qdrant sigue en el servidor; el dispositivo usa ObjectBox (HNSW nativo para Android/Kotlin).
- âœ… **El ~99 % de la Etapa I es un resultado legÃ­timo**, no fuga de informaciÃ³n: se explica por segmentaciÃ³n binaria (individuo vs. fondo) antes de BioCLIP + `GroupSplit` por individuo. Ver [[Modelo de VisiÃ³n â€” BioCLIP]] Â§7.
- âœ… **CatÃ¡logo oficial: 28 especies** para el prototipo â€” coincide con la recolecciÃ³n de campo ya organizada por equipos y con `anuro_labels.json`.
- âœ… **Alcance mÃ­nimo del prototipo (27 sep) fijado** â†’ [[Cronograma y Plan de Trabajo]] Â§0.

## Los frentes que siguen abiertos

1. **Copias de seguridad** de fotos y anotaciones (riesgo sin plan B)
2. **Validar ObjectBox empÃ­ricamente** en el dispositivo de referencia (latencia, memoria)
3. **Modelo de segmentaciÃ³n concreto** â€” tamaÃ±o de YOLO-seg (n vs. s) por confirmar con los datos reales de la semana del 9â€“11 sep
4. **Cobertura real de audio** en AnuraSet/Xeno-canto para las 28 especies â€” decide si la rama acÃºstica entra al prototipo o queda como trabajo futuro
5. **Alcance mÃ­nimo defendible del trabajo de grado completo** (distinto del alcance del prototipo, ya resuelto) â€” sigue pendiente para cuando se fije la fecha de sustentaciÃ³n

Detalle en [[Inconsistencias y Decisiones Pendientes]] y [[Riesgos del Proyecto]].



