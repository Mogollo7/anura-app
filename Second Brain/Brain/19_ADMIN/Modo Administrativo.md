---
title: "Modo Administrativo"
tags: [admin, anura, plan]
created: 2026-09-25
status: draft
---

# Modo Administrativo

Nodo para **construir** el módulo administrativo de ANURA. La fuente de verdad son las notas de `Second Brain/notes`. Su texto completo está en la carpeta `fuentes` de este mismo mapa: [[00_Indice_Principal]]. Este nodo unifica esa lectura para planificar. No reescribe [[DECISION_LOG]] ni da por ejecutado lo que el vault marca como pendiente.

El módulo administrativo es la suite del **servidor y del PC local**. No es la app de campo.

Hace seis cosas: curar datos, calcular representaciones, calibrar el rechazo, compilar paquetes, simular una identificación y publicar solo con aprobación humana. El teléfono ejecuta **BioCLIP 1 congelado** más el JSON del paquete. No reentrena el encoder en el dispositivo.

## Doctrina de construcción

Cuando las notas chocan, manda [[Decisiones de Escalabilidad del Admin]]. El texto original sigue en las fuentes. El relato de cada choque está en [[Contradicciones del Modo Administrativo]].

1. **El encoder y el catálogo van separados.** `bioclip_v1.onnx` se instala una vez. Una especie nueva viaja en un JSON de kilobytes, hasta alrededor de 1,2 MB. Ver [[Arquitectura Desacoplada]].
2. **No se reentrena el ONNX del móvil.** ArcFace (margen **0,35**, escala **30**) entrena solo la matriz del clúster críptico. Las notas que piden fine-tuning de las últimas capas del ViT quedan como antecedente, no como plan. Ver [[Microadaptadores y Transfer Learning]].
3. **El entrenamiento manual actual se abandona.** La nota de trabajo lo trata como fracaso. Los paquetes y el reentrenamiento salen de este módulo. Ver [[Fuente - Estrategias OSR Alternativas]].
4. **Dos roles y permisos por acción.** Administrador técnico y herpetólogo. En el prototipo, un wizard simula el rol, sin autenticación real. Publicar exige primero aval científico y después aval técnico. Ver [[Roles del Admin]].
5. **El sistema alerta y no decide ciencia.** No crea un complejo críptico solo, no pisa un peso escrito por el herpetólogo, no publica solo y no inventa métricas.
6. **Hay tres centroides, no uno.** Global, regional por paquete, y sub-centroide de morfo. Un morfo puede existir en un paquete y no en otro. No se promedian morfos de color opuesto. Ver [[Morfos y Especiacion Regional]] y [[Centroides y Muestras]].
7. **Jerarquía a implementar:** el dataset versionado es una membresía; la cadena biológica es **Individuo → Observación → Fotografía**. El diagrama de la fase 1 que invierte individuo y observación no se implementa. Ver [[Modelo de Datos del Admin]].
8. **Territorio:** raíz Antioquia y **9 paquetes**, uno por subregión. El piso térmico filtra en memoria. No hay 36 paquetes. Una especie puede estar en varios, con contexto distinto. Ver [[Paquetes Geograficos de Antioquia]].
9. **En el teléfono solo hay coseno.** El Admin calibra en el PC y entrega el corte ya convertido. La altitud usa el `umbral_geo` del paquete. 0,05 es el valor inicial, no una ley. El resultado es un `IdentificationResult` que explica el desenlace. Ver [[OSR en Tres Capas]].
10. **El primer ciclo es visual y manual.** Audio, YOLO, CVAT automático, juveniles, OTA real y la conexión con la app no bloquean estas 15 fases. Los campos sí se reservan. Ver [[Roadmap Fase 1 y Fase 2]].

## Qué construir, y en qué orden

El detalle operativo está en [[Plan de Construccion del Admin]]. Resumen:

| Fase | Se construye | Todavía no |
| --- | --- | --- |
| 1 | Modelo de datos | Entrenamiento real |
| 2 | Datasets y curación | Scraper como requisito |
| 3 | Ficha de especie | |
| 4 | Paquetes regionales | |
| 5 | Worker: primero mock, luego el PC | |
| 6 | Centroides y morfos | Juvenil automático |
| 7 | Clústeres y micro-adaptadores | |
| 8 | Contexto y pesos | |
| 9 | Calibración OSR | |
| 10 | Simulador de identificación | |
| 11 | Validación | Métricas inventadas |
| 12 | Compilador JSON, manifest y checksum | |
| 13 | Releases con aprobación humana | Publicación automática |
| 14 | Sandbox aislado de producción | |
| 15 | Debug del worker | Debug de la app |

Quedan fuera de este ciclo, dicho por la propia fuente: audio, CVAT real, YOLO, OTA real y la aplicación móvil.

## Estados que la interfaz debe poder mostrar

**Por especie:** `DRAFT`, `DATASET_READY`, `EMBEDDINGS_READY`, `CENTROID_READY`, `VALIDATING`, `VALIDATED`, `WARNING`, `BLOCKED`, `PUBLISHED`.

**Por release:** `DRAFT` → `VALIDATING` → `READY` → `APPROVED` → `PUBLISHED`, más `ROLLED_BACK`.

**Procedencia de cada centroide:** identificador, especie, paquete, versión del dataset, número de individuos, número de imágenes, fecha, experimento, versión del encoder y estado de validación. Tiene que poder responder de dónde salió el centroide que está en producción.

## Cómo se reparte el trabajo dentro del módulo

El cuadro repetido en las fuentes parte el Admin en cuatro bloques. La columna 4 se lee como **entrenamiento del micro-adaptador y compilador**, no como fine-tuning del ViT. El choque está marcado en [[Contradicciones del Modo Administrativo]].

| Bloque | Qué entra | Qué sale |
| --- | --- | --- |
| Ingesta | Fotos, taxonomía, duplicados, huérfanas | Dataset curado |
| Anotación | CVAT manual, LRC, estadio, morfo | Medición y etiquetas |
| Contexto | Gaussiana de altitud, pesos, sustrato | Ficha ecológica por especie y paquete |
| Empaquetado | Centroides L2, ArcFace del clúster, JSON | Paquete listo para aprobación |

## Piezas de este mapa

- [[Decisiones de Escalabilidad del Admin]]
- [[Modelo de Datos del Admin]]
- [[Roles del Admin]]
- [[Entradas y Ficha de Especie]]
- [[Curacion e Ingesta]]
- [[Centroides y Muestras]]
- [[Morfos y Especiacion Regional]]
- [[Microadaptadores y Transfer Learning]]
- [[Contexto Ecologico y Pesos]]
- [[OSR en Tres Capas]]
- [[Cascada Taxonomica y Supercentroides]]
- [[Paquetes Geograficos de Antioquia]]
- [[Especies Entrenables y Huerfanas]]
- [[Esquema JSON del Paquete]]
- [[Arquitectura Desacoplada]]
- [[Worker Releases y Sandbox]]
- [[Observabilidad y Simulador]]
- [[Roadmap Fase 1 y Fase 2]]
- [[Contradicciones del Modo Administrativo]]

## Qué ya midió el cerebro, y estas notas no incorporan

Antes de fijar un número en código, contrastar:

- [[DECISION_LOG]]: BioCLIP como backbone, FP16, prior geográfico del EXP-007 con peso **0,75**, ONNX de **165,6 MB**, **403 ms** a 1 hilo y **154 ms** a 4 hilos, umbral Mahalanobis C-16.
- [[Open-Set Recognition]] y [[FASE_13_CALIBRACION_INDEPENDIENTE]]
- [[Modelo de Visión — BioCLIP]]
- [[Ciclo de Vida del Modelo (MLOps)]]
- [[Guía CVAT — Índice]]
- [[00_CONTRADICTIONS]]

Las tablas que dicen «Fase 1 (Listo)» describen un deseo de diseño. En este vault, una fase sin evidencia sigue en **NOT_EXECUTED**. Los ~100 MB y los menos de 150 ms de las notas son objetivo, no la medición ya registrada.
