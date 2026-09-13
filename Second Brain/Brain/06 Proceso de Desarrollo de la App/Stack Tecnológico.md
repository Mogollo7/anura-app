---
title: "Stack TecnolÃ³gico"
proyecto: Anura
tipo: proceso-desarrollo
estado: propuesta
tags: [anura, proceso, stack, tecnologÃ­as]
---

# Stack TecnolÃ³gico

[[Anura â€” Ãndice General]] Â· [[Proceso de Desarrollo â€” Ãndice]] Â· [[App MÃ³vil]] Â· [[API Backend]] Â· [[Infraestructura]]

Vista Ãºnica de todas las tecnologÃ­as del proyecto, con el motivo de cada elecciÃ³n. Cuando una decisiÃ³n sigue abierta, se marca como tal en vez de fingir que estÃ¡ cerrada.

## 1. Machine Learning

| Componente | ElecciÃ³n | Alternativa | Estado |
| --- | --- | --- | --- |
| Framework | **PyTorch** | TensorFlow | âœ… Fijado (BioCLIP y YOLO son PyTorch) |
| Modelo de visiÃ³n (servidor, teacher) | **BioCLIP ViT-B/16 (v1)** | BioCLIP 2 (ViT-L/14) | âœ… v1 fijado para el sprint del prototipo (2026-09-05); pesos revisados 2026-09-08. Rol revisado 2026-09-08: solo servidor, ya no en dispositivo |
| Modelo de visiÃ³n (dispositivo, student) | **EdgeNeXt-Tiny**, destilado de BioCLIP (Multi-Head Loss) | BioCLIP-INT8 directo | âœ… Fijado 2026-09-08 (C-5) â€” INT8 sobre BioCLIP fracasÃ³ en pruebas reales (~0,2 % exactitud) |
| SegmentaciÃ³n | **YOLO-seg** (Ultralytics) | Mask R-CNN, SAM | ðŸŸ¡ Por confirmar |
| Modelo acÃºstico | **Modelo propio dedicado** (CNN pequeÃ±a, 1-3 MB, arquitectura por definir) | Reutilizar backbone EdgeNeXt-Tiny | âœ… Fijado 2026-09-08 (C-7) â€” modelo propio por facilidad de implementaciÃ³n; condicionado a confirmar cobertura de dataset de audio |
| Metric learning | Triplet loss (batch-hard) | ArcFace, SupCon, ninguno | ðŸŸ¡ Medir antes de decidir |
| AnotaciÃ³n | **CVAT** | Roboflow (usado antes) | âœ… Fijado â€” guÃ­a v1.0 |
| AugmentaciÃ³n | **Albumentations** | torchvision | âœ… Ya especificada en el dataset |
| Audio | librosa / torchaudio | | âœ… |
| Seguimiento | MLflow | Weights & Biases | ðŸ”´ Abierto |
| Versionado de datos | DVC | Git LFS | ðŸ”´ Abierto |

## 2. Backend

| Componente | ElecciÃ³n | Motivo |
| --- | --- | --- |
| API | **FastAPI** (Python) | El modelo es Python; evita un servicio puente |
| Base de datos | **PostgreSQL** vÃ­a **Supabase** | Ya decidido; aporta auth y storage |
| Vectores (servidor) | Qdrant **o** pgvector | ðŸ”´ DecisiÃ³n abierta â†’ [[API Backend]] Â§2 |
| Almacenamiento | Supabase Storage | S3-compatible |
| Auth | Supabase Auth (JWT) | Roles: usuario / investigador / validador |
| Tareas asÃ­ncronas | Celery + Redis | Reindexado, paquetes, exportaciÃ³n DwC |
| Contenedores | Docker | Reproducibilidad entre entornos |

## 3. MÃ³vil

| Componente | ElecciÃ³n | Motivo |
| --- | --- | --- |
| Plataforma | **Android** | Fijado en el alcance |
| Lenguaje | **Kotlin** | |
| UI | **Jetpack Compose** | Temas (oscuro/alto contraste) sin duplicar layouts |
| Inferencia | **LiteRT** (ex-TensorFlow Lite) | EstÃ¡ndar en Android; acepta modelos PyTorch |
| Alternativa inferencia | ONNX Runtime Mobile | Probar ambas con el ViT |
| Persistencia | **Room** (SQLite) | RNF-11 |
| Vectores (dispositivo) | **SQLite + sqlite-vec** | âœ… Firmado como ruta de producciÃ³n (C-15, 2026-09-13) â†’ [[Base Vectorial (SQLite-vec)]] Â§2 â€” Qdrant **no** sirve embebido; reemplaza a la recomendaciÃ³n anterior (ObjectBox), por portabilidad de paquetes regionales `.sqlite` independientes estilo Merlin |
| SincronizaciÃ³n | **WorkManager** | Reintentos y restricciones gestionados por el sistema |
| CÃ¡mara | CameraX | |
| Audio | AudioRecord (PCM) | `MediaRecorder` comprime y arruina el anÃ¡lisis |
| Red | Retrofit + OkHttp | |
| Mapas | MapLibre / OSM | Evita costes de licencia de mapas comerciales |

## 4. Web (Fase 1)

| Componente | ElecciÃ³n | Motivo |
| --- | --- | --- |
| Framework | React o SvelteKit | ðŸ”´ Abierto â€” cualquiera sirve para el alcance |
| Mapas | MapLibre + Leaflet | Coherente con la app |
| GrÃ¡ficos | Recharts / Observable Plot | MÃ©tricas y distribuciones |
| Hosting | Vercel / Netlify (capa gratuita) | |

## 5. Soporte

| Ãrea | Herramienta |
| --- | --- |
| Repositorio | GitHub |
| CI/CD | GitHub Actions |
| Errores | Sentry |
| DocumentaciÃ³n | **Esta bÃ³veda de Obsidian** |
| GestiÃ³n de tareas | GitHub Projects o Notion |
| Diagramas | Mermaid dentro de las notas |

## 6. Criterios que guiaron las elecciones

Vale la pena dejarlos escritos, porque justifican decisiones que de otro modo parecen arbitrarias:

1. **Capa gratuita o coste cercano a cero.** Es un proyecto universitario; una dependencia de pago mensual es un riesgo de continuidad, no solo de presupuesto.
2. **Un solo lenguaje donde se pueda.** Python en todo el lado del modelo y el backend evita reimplementar el preprocesado â€” que es donde aparecen las discrepancias silenciosas entre entrenamiento e inferencia.
3. **Preferir lo aburrido y probado.** PostgreSQL, SQLite, Room, Retrofit: tecnologÃ­as con documentaciÃ³n abundante y respuestas fÃ¡ciles de encontrar. Un TFG no es el lugar para estrenar tecnologÃ­a.
4. **Nada que impida funcionar sin red.** Cualquier componente que exija conexiÃ³n en tiempo de inferencia queda descartado para la Fase 2 por definiciÃ³n.
5. **Formatos abiertos y exportables.** Darwin Core, COCO, ONNX, SQLite: si el proyecto se detiene, los datos siguen siendo utilizables por otros.

## 7. Decisiones abiertas

Reunidas en [[Inconsistencias y Decisiones Pendientes]]:

- [x] VersiÃ³n de BioCLIP â†’ **v1**, resuelto 2026-09-05; revisado 2026-09-08: v1 solo como teacher en servidor, ya no en mÃ³vil (C-5)
- [x] Backbone on-device â†’ **EdgeNeXt-Tiny** destilado, resuelto 2026-09-08 (C-5) â€” INT8 sobre BioCLIP fracasÃ³
- [ ] Motor vectorial en servidor (Qdrant vs. pgvector)
- [x] Motor vectorial en dispositivo â†’ **SQLite + sqlite-vec**, revisado 2026-09-08 (C-6, reemplaza a ObjectBox) â€” pendiente solo la validaciÃ³n empÃ­rica en el Galaxy A30
- [ ] Modelo de segmentaciÃ³n concreto
- [x] Backbone acÃºstico â†’ **modelo propio dedicado**, resuelto 2026-09-08 (C-7, reemplaza la idea de reutilizar backbone compartido)
- [ ] Framework web
- [ ] Herramienta de seguimiento de experimentos



