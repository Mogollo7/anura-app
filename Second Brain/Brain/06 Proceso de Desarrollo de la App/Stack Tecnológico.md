---
title: "Stack Tecnológico"
proyecto: Anura
tipo: proceso-desarrollo
estado: propuesta
tags: [anura, proceso, stack, tecnologías]
---

# Stack Tecnológico

[[Anura â€” àndice General]] · [[Proceso de Desarrollo â€” àndice]] · [[App Móvil]] · [[API Backend]] · [[Infraestructura]]

Vista àºnica de todas las tecnologías del proyecto, con el motivo de cada elección. Cuando una decisión sigue abierta, se marca como tal en vez de fingir que está cerrada.

## 1. Machine Learning

| Componente | Elección | Alternativa | Estado |
| --- | --- | --- | --- |
| Framework | **PyTorch** | TensorFlow | âœ… Fijado (BioCLIP y YOLO son PyTorch) |
| Modelo de visión (servidor, teacher) | **BioCLIP ViT-B/16 (v1)** | BioCLIP 2 (ViT-L/14) | âœ… v1 fijado para el sprint del prototipo (2026-09-05); pesos revisados 2026-09-08. Rol revisado 2026-09-08: solo servidor, ya no en dispositivo |
| Modelo de visión (dispositivo, student) | **EdgeNeXt-Tiny**, destilado de BioCLIP (Multi-Head Loss) | BioCLIP-INT8 directo | âœ… Fijado 2026-09-08 (C-5) â€” INT8 sobre BioCLIP fracasó en pruebas reales (~0,2 % exactitud) |
| Segmentación | **YOLO-seg** (Ultralytics) | Mask R-CNN, SAM | ðŸŸ¡ Por confirmar |
| Modelo acàºstico | **Modelo propio dedicado** (CNN pequeña, 1-3 MB, arquitectura por definir) | Reutilizar backbone EdgeNeXt-Tiny | âœ… Fijado 2026-09-08 (C-7) â€” modelo propio por facilidad de implementación; condicionado a confirmar cobertura de dataset de audio |
| Metric learning | Triplet loss (batch-hard) | ArcFace, SupCon, ninguno | ðŸŸ¡ Medir antes de decidir |
| Anotación | **CVAT** | Roboflow (usado antes) | âœ… Fijado â€” guía v1.0 |
| Augmentación | **Albumentations** | torchvision | âœ… Ya especificada en el dataset |
| Audio | librosa / torchaudio | | âœ… |
| Seguimiento | MLflow | Weights & Biases | ðŸ”´ Abierto |
| Versionado de datos | DVC | Git LFS | ðŸ”´ Abierto |

## 2. Backend

| Componente | Elección | Motivo |
| --- | --- | --- |
| API | **FastAPI** (Python) | El modelo es Python; evita un servicio puente |
| Base de datos | **PostgreSQL** vía **Supabase** | Ya decidido; aporta auth y storage |
| Vectores (servidor) | Qdrant **o** pgvector | ðŸ”´ Decisión abierta â†’ [[API Backend]] §2 |
| Almacenamiento | Supabase Storage | S3-compatible |
| Auth | Supabase Auth (JWT) | Roles: usuario / investigador / validador |
| Tareas asíncronas | Celery + Redis | Reindexado, paquetes, exportación DwC |
| Contenedores | Docker | Reproducibilidad entre entornos |

## 3. Móvil

| Componente | Elección | Motivo |
| --- | --- | --- |
| Plataforma | **Android** | Fijado en el alcance |
| Lenguaje | **Kotlin** | |
| UI | **Jetpack Compose** | Temas (oscuro/alto contraste) sin duplicar layouts |
| Inferencia | **LiteRT** (ex-TensorFlow Lite) | Estándar en Android; acepta modelos PyTorch |
| Alternativa inferencia | ONNX Runtime Mobile | Probar ambas con el ViT |
| Persistencia | **Room** (SQLite) | RNF-11 |
| Vectores (dispositivo) | **SQLite + sqlite-vec** | âœ… Firmado como ruta de producción (C-15, 2026-09-13) â†’ [[Base Vectorial (SQLite-vec)]] §2 â€” Qdrant **no** sirve embebido; reemplaza a la recomendación anterior (ObjectBox), por portabilidad de paquetes regionales `.sqlite` independientes estilo Merlin |
| Sincronización | **WorkManager** | Reintentos y restricciones gestionados por el sistema |
| Cámara | CameraX | |
| Audio | AudioRecord (PCM) | `MediaRecorder` comprime y arruina el análisis |
| Red | Retrofit + OkHttp | |
| Mapas | MapLibre / OSM | Evita costes de licencia de mapas comerciales |

## 4. Web (Fase 1)

| Componente | Elección | Motivo |
| --- | --- | --- |
| Framework | React o SvelteKit | ðŸ”´ Abierto â€” cualquiera sirve para el alcance |
| Mapas | MapLibre + Leaflet | Coherente con la app |
| Gráficos | Recharts / Observable Plot | Métricas y distribuciones |
| Hosting | Vercel / Netlify (capa gratuita) | |

## 5. Soporte

| àrea | Herramienta |
| --- | --- |
| Repositorio | GitHub |
| CI/CD | GitHub Actions |
| Errores | Sentry |
| Documentación | **Esta bóveda de Obsidian** |
| Gestión de tareas | GitHub Projects o Notion |
| Diagramas | Mermaid dentro de las notas |

## 6. Criterios que guiaron las elecciones

Vale la pena dejarlos escritos, porque justifican decisiones que de otro modo parecen arbitrarias:

1. **Capa gratuita o coste cercano a cero.** Es un proyecto universitario; una dependencia de pago mensual es un riesgo de continuidad, no solo de presupuesto.
2. **Un solo lenguaje donde se pueda.** Python en todo el lado del modelo y el backend evita reimplementar el preprocesado â€” que es donde aparecen las discrepancias silenciosas entre entrenamiento e inferencia.
3. **Preferir lo aburrido y probado.** PostgreSQL, SQLite, Room, Retrofit: tecnologías con documentación abundante y respuestas fáciles de encontrar. Un TFG no es el lugar para estrenar tecnología.
4. **Nada que impida funcionar sin red.** Cualquier componente que exija conexión en tiempo de inferencia queda descartado para la Fase 2 por definición.
5. **Formatos abiertos y exportables.** Darwin Core, COCO, ONNX, SQLite: si el proyecto se detiene, los datos siguen siendo utilizables por otros.

## 7. Decisiones abiertas

Reunidas en [[Inconsistencias y Decisiones Pendientes]]:

- [x] Versión de BioCLIP â†’ **v1**, resuelto 2026-09-05; revisado 2026-09-08: v1 solo como teacher en servidor, ya no en móvil (C-5)
- [x] Backbone on-device â†’ **EdgeNeXt-Tiny** destilado, resuelto 2026-09-08 (C-5) â€” INT8 sobre BioCLIP fracasó
- [ ] Motor vectorial en servidor (Qdrant vs. pgvector)
- [x] Motor vectorial en dispositivo â†’ **SQLite + sqlite-vec**, revisado 2026-09-08 (C-6, reemplaza a ObjectBox) â€” pendiente solo la validación empírica en el Galaxy A30
- [ ] Modelo de segmentación concreto
- [x] Backbone acàºstico â†’ **modelo propio dedicado**, resuelto 2026-09-08 (C-7, reemplaza la idea de reutilizar backbone compartido)
- [ ] Framework web
- [ ] Herramienta de seguimiento de experimentos



