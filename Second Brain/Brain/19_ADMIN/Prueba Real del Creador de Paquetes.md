---
title: "Prueba Real del Creador de Paquetes"
tags: [admin, anura, validacion, paquetes]
created: 2026-09-26
status: refined
---

# Prueba Real del Creador de Paquetes

Qué pasó al usar el Admin de punta a punta para crear un paquete, y qué da el método de este sector (19_ADMIN) con los **vectores reales** de Antioquia frente al paquete que corre hoy en el teléfono. El plan para volverlo real está en [[Plan del Backend Real]].

## 1. Recorrido por el Admin (2026-09-26)

Flujo usado: Imágenes → Ficha → Worker → Centroides → Clústeres → OSR → Validación → Release → avales → publicar → Simulador → Operación.

| # | Hallazgo | Gravedad | Estado |
| --- | --- | --- | --- |
| 1 | Las 41 especies del Admin eran inventadas o de otro catálogo: solo ~10 coincidían con las 30 del paquete del teléfono. No se podía armar el paquete de Antioquia. | Bloqueante | **Corregido.** El Admin lee `src/data/antioquia-real.json` (30 visuales + 4 en revisión), exportado por `tools/admin/export_admin_seed.py`. |
| 2 | "Especies por subregión" salía de solapar un rango de altitud aleatorio: Oriente tenía las 41. | Alta | **Corregido.** Presencia real: registro GBIF/iNaturalist dentro de un municipio DANE de la subregión (point-in-polygon). Oriente: 27. |
| 3 | El wizard de paquetes por departamento permitía editar LRC y patrón con valores aleatorios que nadie usaba ("cambiar el tamaño cloaca-cabeza"). También tenía su propio "Publicar". | Alta | **Eliminado.** El único creador es Release. |
| 4 | Operación → Actualizaciones tenía una cola propia con "Publicar ahora", sin los dos avales, y no veía los releases del creador. Incluía una "corrección de LRC" que ningún proceso hace. | Alta | **Corregido.** Muestra los releases reales y el paquete del teléfono; no publica. |
| 5 | La LRC en la Ficha parecía activa. Ningún paso la lee. | Media | **Marcada Fase 2**, sin efecto sobre el paquete. |
| 6 | Clústeres pedía margen, escala, épocas y learning rate de ArcFace. El entrenamiento no los usa: W sale de un LDA. | Media | **Corregido de verdad (2026-09-27).** ArcFace real, escrito desde cero: un prototipo unitario por especie entrenado por descenso de gradiente con margen angular aditivo (Deng 2019), usando esos cuatro números. Bug encontrado y corregido en la propia verificación: con el `lr` inicial (0,05) y decaimiento por época, el entrenamiento diverge y colapsa a un solo prototipo (precisión de entrenamiento cae a ~50 %, peor que sin adaptador) en cuanto el clúster tiene más de ~20-30 muestras por época. Corregido con decaimiento por paso (no por época) y `lr` por defecto 0,01. Medido en el Admin: *Pristimantis paisa* ↔ *P. palmeri* (coseno 0,938 entre centroides) pasa de 79,2 % a 87,5 % de acierto; un clúster de 4 especies pasa de 83,3 % a 85,4 %, con matriz de confusión diagonal-dominante. |
| 7 | Los ids de iNaturalist/GBIF de la Ficha eran enlaces a observaciones reales de otras personas con ids inventados. | Media | **Quitados.** |
| 8 | El encoder se llamaba `bioclip_v1.onnx` / "BioCLIP-1-frozen". El real es `encoder_anura_fp16.onnx`: BioCLIP 1 **con fine-tuning**. | Media | **Corregido.** Ver §3 y [[Contradicciones del Modo Administrativo]] #22. |
| 9 | "Inyectar un vector de BioCLIP 2.5 (1024-d)" confundía. BioCLIP 2.5 ViT-H/14 **sí existe** y corre en el `ai-service` del servidor; la opción es una prueba de que la compuerta lo rechaza. | Media | **Texto aclarado.** Contradicción #23. |
| 10 | El JSON compilado no traía centroide en los nodos de género y familia: el teléfono no podía hacer la cascada. | Alta | **Corregido** (campo `centroid` con la regla L2). |
| 11 | La app Android no lee ese JSON: lee `package.sqlite` (k-NN) y `openset_*.bin` (Mahalanobis). El paquete del creador no tiene quién lo use. | Bloqueante para campo | **Abierto.** Etapas M4 y C1 del plan. |
| 12 | Quien entrenaba un clúster lo validaba; quien daba el aval científico podía dar el técnico. | Media | **Corregido:** dos personas distintas. |
| 13 | Publicar no pedía confirmación. | Media | **Corregido** con diálogo que dice qué pasa y qué no pasa (no llega a teléfonos). |
| 14 | Con vectores simulados OSR mostraba FAR 20 % y AUROC 0,91. Con los reales: FAR 93 % y AUROC 0,65 en la capa 1. | Alta | **Corregido:** la tarjeta "Prueba con los datos reales" va arriba en OSR y Métricas; la tabla simulada queda marcada "optimista". |
| 15 | Cada pantalla tiene su propio selector de subregión: no hay un "paquete en construcción" que acompañe el flujo. | Media | Abierto (UX). |
| 16 | Curación no decía de dónde salen ni dónde viven las fotos; no hay subida manual con coordenada. | Media | **Explicado** en Curación (scraper, carpetas, particiones). Subida manual con coordenada: **hecha** en M1 (2026-09-27), validada por departamento con geo-service. |
| 17 | Texto terciario con contraste 2,2–2,8:1 y textos de 9–10 px. | Media (WCAG) | **Corregido:** terciario ≥ 4,5:1, mínimo 11 px. |

## 2. Viejo contra nuevo con vectores reales

Script: `evaluation/admin_v2_comparison/compare_packages.py`. Mismo encoder, mismas fotos.

- **Referencias:** las 4.028 del paquete del teléfono (el mismo muestreo de `paquetes_zonales.py`; el paquete dice 4.034, faltan 6 archivos en disco).
- **Calibración:** 501 fotos de la partición `val`.
- **Prueba:** 547 fotos de la partición `test` de las 30 especies.
- **Desconocidas:** 715 fotos de 11 especies que el paquete no trae (`unknown_open_set_v2`), vectores recalculados con el ONNX del teléfono (paridad coseno 1,00000 con la caché).
- **Altitud:** registros de `records_v1.csv` con elevación propia o la muestra SRTM90 en caché más cercana (≤ 6 km). Sin fuga: las observaciones de prueba no alimentan la gaussiana.

| | Teléfono hoy (k-NN k=5 + Mahalanobis τ 39,35) | Creador del Admin (tres capas) |
| --- | --- | --- |
| Especie correcta | 54,3 % | **59,4 %** |
| Especie equivocada | 32,5 % | **22,7 %** |
| Desconocida aceptada como especie (FAR) | 82,7 % | **75,7 %** |
| AUROC conocida/desconocida | 0,597 | **0,652** |
| Desconocida con respuesta segura | 17,3 % | **24,3 %** |
| Tamaño descargado (sin encoder) | 11,2 MB | **241 KB** |

A la misma exigencia (KAR 86,8 %), la capa 1 sola deja pasar 77,6 % de desconocidas contra 82,7 % del viejo.

Lo que aporta cada capa:
- **Capa 1 + cascada sola:** especie correcta 59,8 %, pero FAR 93 %. El radio Weibull calibrado en entrenamiento es holgado.
- **Capa 2 (clústeres):** es la que más baja la especie equivocada (36,4 % → 25,8 %) y el FAR (93 % → 80 %).
- **Capa 3 (altitud, `umbral_geo` 0,05):** ataja 31 desconocidas, pero **rechaza 25 fotos buenas** de 167 con altitud. Es el mismo riesgo que el campo ya mostró con el prior de zona (AnuraIdentifier.kt).

Lo que no mejoró:
- **Radio calibrado con las fotos apartadas (`val`):** AUROC 0,652 → 0,624. Se queda como dice el vault: radio con entrenamiento.
- **Clústeres sugeridos por la confusión en `val`** (umbral 10 %): salieron grupos de 12, 11 y 3 especies. Uno de 12 está en el límite de `MAX_CLUSTER_SPECIES`. Son sugerencias: el herpetólogo los tiene que armar.

**Lectura honesta:** el método nuevo es mejor que el del teléfono en todo lo que se midió y pesa 50 veces menos. Aun así sigue nombrando una especie en 3 de cada 4 desconocidas. El problema de rechazo no está resuelto.

## 3. ¿BioCLIP 1 puro o con fine-tuning?

Mismo método, mismas fotos, vectores de `hf-hub:imageomics/bioclip` sin fine-tuning (`embed_pure.py`, GPU).

| | Con fine-tuning (teléfono) | Puro |
| --- | --- | --- |
| Top-1 k-NN | 59,2 % | 59,0 % |
| Especie correcta (tres capas) | 59,4 % | 60,5 % |
| Especie equivocada | **22,7 %** | 24,1 % |
| FAR | **75,7 %** | 84,2 % |
| AUROC | **0,652** | 0,599 |
| Desconocidas con el nivel correcto (género, familia o rechazo) | **8,4 %** | 2,2 % |

**Decisión tomada:** se queda el encoder con fine-tuning. Identifica igual que el puro y separa mejor lo conocido de lo desconocido. Cambiarlo obligaría a mandar otro ONNX a los teléfonos. El fine-tuning casi no movió el top-1: su valor está en el rechazo.

## 4. Decisiones que quedan para el autor

1. **Formato del paquete v2** que lee el teléfono (hallazgo 11): SQLite con el esquema del [[Esquema JSON del Paquete]], o JSON + binario. El plan propone SQLite ([[Plan del Backend Real]] M4).
2. **Política de altitud:** rechazo (`OSR_GEO`) o solo penalización. Hoy cuesta 25 fotos buenas; el campo ya mostró el mismo problema.
3. **Clústeres de Antioquia:** revisar los grupos sugeridos y partir el de 12.

Relacionado: [[OSR en Tres Capas]], [[Centroides y Muestras]], [[Microadaptadores y Transfer Learning]], [[Auditoria de Implementacion del Admin]].
