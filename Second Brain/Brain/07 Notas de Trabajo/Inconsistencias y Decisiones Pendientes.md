---
title: "Inconsistencias y Decisiones Pendientes"
proyecto: Anura
tipo: nota-de-trabajo
estado: activo
tags: [anura, decisiones, inconsistencias, auditoría]
---

# Inconsistencias y Decisiones Pendientes

[[Anura â€” àndice General]] · [[Riesgos del Proyecto]] · [[Stack Tecnológico]] · [[Cronograma y Plan de Trabajo]]

> [!abstract] Qué es esto
> Resultado de cruzar todas las fuentes del proyecto â€”el export de Notion, la guía CVAT en Word y las notas de trabajo originalesâ€” buscando contradicciones entre documentos. Ninguna de estas contradicciones es fatal, pero varias afectan a decisiones que hay que tomar **antes** de escribir código o citar cifras en el documento de grado.
>
> Marcar cada punto como resuelto cuando se decida, y actualizar los documentos afectados.

---

## âœ… Resueltas por el autor

Estas tres eran las de mayor impacto en la lista original. Ya tienen decisión firme; se conservan aquí como registro de por qué se decidió así.

### C-1 (resuelto) · Motor vectorial embebido para el móvil â†’ **ObjectBox**

| | |
| --- | --- |
| **Problema original** | Qdrant es un servidor; no existe librería embebible pàºblica para Android (*Qdrant Edge* sigue en beta privada) |
| **Decisión** | **ObjectBox** en el dispositivo (soporte Kotlin/Android de primera clase, HNSW nativo, un solo almacén para objetos y vectores); Qdrant se mantiene en el servidor |
| **Detalle técnico** | Comparación completa contra sqlite-vec y USearch en [[Base Vectorial (SQLite-vec)]] §2 |
| **Pendiente** | Validar empíricamente latencia y memoria en el dispositivo de referencia â€” es una verificación, no una decisión abierta |
| **Documentos actualizados** | [[Base Vectorial (SQLite-vec)]], [[Stack Tecnológico]], [[Riesgos del Proyecto]] (T-2), [[Anura â€” àndice General]] |

### C-2 (resuelto) · BioCLIP es el àºnico backbone del proyecto

| | |
| --- | --- |
| **Problema original** | [[Plan de Acción y Arquitectura Conceptual]] proponía EfficientNet-B0 + Triplet Loss; otros documentos ya asumían BioCLIP; convivían sin resolver |
| **Decisión del autor** | **BioCLIP siempre** â€” para visión y, reutilizando el mismo codificador, también para audio (el espectrograma se trata como imagen). Se eliminó la nota "Modelo EfficientNet" de la bóveda |
| **Por qué BioCLIP y no EfficientNet** | Volumen de datos disponible. EfficientNet-B0 se entrena desde cero (o con transfer learning genérico de ImageNet) y necesita mucho más dato propio por especie para generalizar; BioCLIP ya viene preentrenado sobre TreeOfLife-10M con la jerarquía taxonómica incorporada, por lo que rinde bien con los volàºmenes reales de este proyecto (70 individuos/especie en el prototipo, ver [[Estrategia de Construcción del Dataset]]) â€” es precisamente el escenario de "pocos datos por clase" para el que BioCLIP fue diseñado ([[Modelo de Visión â€” BioCLIP]] §1) |
| **Consecuencia positiva no anticipada** | Al no necesitar un backbone de audio separado, se libera presupuesto de almacenamiento móvil (RNF-05) y se simplifica la cuantización a una sola ruta |
| **Detalle técnico** | [[Modelo de Visión â€” BioCLIP]] §8â€“9 (rol en audio + experimento de validación pendiente) |
| **Nota** | "BlockClip", mencionado en [[Notas Originales â€” Añadir Nueva Información]], no existe como modelo â€” era casi con certeza un error de transcripción de BioCLIP; queda confirmado por esta misma decisión |
| **Documentos actualizados** | [[Modelo de Visión â€” BioCLIP]], [[Arquitectura Multimodal]], [[Métricas Offline]], [[Optimización para Inferencia en Móvil]], [[App Móvil]], [[Stack Tecnológico]], [[Experimentos y Resultados]], [[Anura â€” àndice General]] |

### C-4 (resuelto/aclarado) · El ~99 % de la Etapa I es legítimo, no fuga de información

| | |
| --- | --- |
| **Problema original** | Se sospechaba fuga de información en el resultado alto de la Etapa I (documentado como 95,69 % en el export de Notion) |
| **Aclaración del autor** | El resultado real fue **~99 %**, y se sostiene en tres decisiones metodológicas ya aplicadas: (1) segmentación binaria individuo-vs-fondo antes de BioCLIP, (2) `GroupSplit` por individuo con 70 individuos à— 10 especies, (3) diversidad de individuos en vez de tomas repetidas del mismo ejemplar |
| **Detalle completo** | [[Modelo de Visión â€” BioCLIP]] §7 |
| **Pendiente real** | No es "verificar si hubo fuga" â€” es **repetir el mismo protocolo riguroso al escalar el catálogo** y documentar formalmente el modelo de segmentación binaria usado |
| **Documentos actualizados** | [[Modelo de Visión â€” BioCLIP]], [[Métricas Offline]], [[Experimentos y Resultados]], [[Riesgos del Proyecto]] (D-1), [[Anura â€” àndice General]] |

### C-5 (resuelto) · Backbone on-device: BioCLIP-INT8 descartado, EdgeNeXt-Tiny confirmado

| | |
| --- | --- |
| **Problema encontrado** | La cuantización INT8 sobre BioCLIP (ViT-B/16) que C-2 y [[Modelo de Visión â€” BioCLIP]] §6 daban por buena (pesos INT8 + activaciones FP16) fracasó en pruebas reales: los outliers de atención del ViT destruyen la geometría bajo INT8, resultando en ~0,2 % de exactitud â€” inutilizable |
| **Decisión del autor (2026-09-08)** | BioCLIP v1 deja de ser el backbone on-device. Se usa **destilación de conocimiento**: BioCLIP v1 como *teacher* (solo en servidor, fine-tuned, soft labels T=4) â†’ **EdgeNeXt-Tiny** como *student* on-device (~2-4M parámetros, <4 MB), entrenado con **Multi-Head Loss** (cross-entropy paralela Familia+Género+Especie + divergencia KL contra el teacher) |
| **Pesos de BioCLIP** | Revisados y con características óptimas ya definidas para su rol de *teacher* (ViT-B/16, ~86M parámetros, fine-tuned) â€” cierra la tarea del 06 sep en [[Cronograma y Plan de Trabajo]] |
| **Consecuencia sobre C-2** | La decisión "BioCLIP àºnico, incl. audio" queda **parcialmente revertida**: BioCLIP sigue siendo el àºnico extractor en el *servidor*, pero ya no viaja al dispositivo. La rama de audio pierde su justificación original de "reutilizar el mismo codificador" â€” ver C-7 |
| **BioCLIP full como opción de gama alta** | Solo se mantiene como candidato *si* demuestra caber en el presupuesto (latencia/RAM) de un dispositivo de 8 GB RAM, medido con el mismo protocolo que el dispositivo de referencia. Si no cumple, se descarta por completo â€” no solo para gama baja |
| **Dispositivo de referencia confirmado** | **Samsung Galaxy A30 (4 GB RAM)** â€” mínimo viable, es donde se emula y se miden latencia/RAM/batería (cerraba como pendiente en [[Optimización para Inferencia en Móvil]] §5) |
| **Consecuencia en presupuesto** | El presupuesto de 150 MB (RNF-05), calculado para BioCLIP (~85-90 MB) + segmentación, baja a **~15-30 MB** con EdgeNeXt-Tiny (~4 MB) + segmentación â€” libera margen considerable |
| **Documentos afectados** | [[Modelo de Visión â€” BioCLIP]], [[Arquitectura Multimodal]], [[Optimización para Inferencia en Móvil]], [[Anura â€” àndice General]] |

### C-6 (resuelto) · Motor vectorial local: SQLite (sqlite-vec) reemplaza a ObjectBox

| | |
| --- | --- |
| **Decisión anterior (C-1, 2026-09-04)** | ObjectBox como motor vectorial embebido en el móvil |
| **Decisión del autor (2026-09-08)** | **SQLite con extensión sqlite-vec** es el motor óptimo para la nueva arquitectura |
| **Justificación de ingeniería** | (1) Portabilidad absoluta: un `.sqlite` es un archivo autocontenido â€” descargar un paquete regional es bajar un solo archivo, abrirlo bajo demanda y borrarlo con `file.delete()`; ObjectBox gestiona un almacén àºnico vía mmap, no está pensado para montar/desmontar bases aisladas en caliente. (2) Consultas híbridas: metadatos relacionales (taxonomía) y vectores conviven en la misma base, permitiendo filtrar por región antes de calcular distancia en una sola consulta. (3) Footprint mínimo (~30 MB) sobre el motor C de SQLite, crítico para el Galaxy A30 |
| **Modelo operativo confirmado (estilo Merlin)** | El backbone (EdgeNeXt-Tiny) queda **congelado** en el APK; lo que varía por zona son los **embeddings**, descargados/editados/aplicados como paquetes `.sqlite` independientes por región â€” el mismo patrón que los paquetes regionales de especies de Merlin Bird ID (Cornell Lab), la referencia de diseño explícita del proyecto |
| **Detalle completo** | [[Base Vectorial (SQLite-vec)]] §1.1 y §2 (revisadas 2026-09-08) |
| **Documentos afectados** | [[Base Vectorial (SQLite-vec)]], [[Stack Tecnológico]], [[Riesgos del Proyecto]] (T-2), [[Anura â€” àndice General]] |

### C-7 (resuelto) · Rama de audio: modelo propio dedicado, no reutilización de backbone

| | |
| --- | --- |
| **Opción evaluada** | Reutilizar el backbone EdgeNeXt-Tiny (ya destilado con objetivo estrecho: morfología de rana en fotos) sobre mel-espectrogramas, análogo a como C-2 proponía reutilizar BioCLIP |
| **Decisión del autor (2026-09-08)** | **Modelo de audio propio y dedicado**, por facilidad de implementación â€” no se reutiliza el backbone visual. Se descarta la ruta de evaluación de transferencia (fine-tuning del backbone congelado sobre espectrogramas) antes de ejecutarla |
| **Por qué es razonable no forzar la reutilización** | A diferencia de BioCLIP (modelo fundacional con features generales de 10M imágenes), EdgeNeXt-Tiny fue destilado con un objetivo estrecho â€” el riesgo de mala transferencia a espectrogramas es alto. Además, el ahorro de MB de reutilizar ya no es crítico: un modelo de audio dedicado a esta escala (1-3 MB) es tan chico que no compromete el presupuesto total (~15-30 MB del RNF-05 revisado, ver C-5) |
| **Sigue condicionado a** | Confirmar cobertura de dataset de audio (grabación propia o AnuraSet/Xeno-canto) para las 28 especies â€” punto Go/No-Go ya fijado en [[Cronograma y Plan de Trabajo]] para el 18 sep |
| **Patrón de carga en dispositivo** | Sin cambios: carga perezosa on-demand (solo al grabar), liberación inmediata después â€” ver [[Optimización para Inferencia en Móvil]] §4 |
| **Documentos afectados** | [[Modelo de Visión â€” BioCLIP]] §8-9, [[Arquitectura Multimodal]] §1.2, [[Anura â€” àndice General]] |

### C-8 (resuelto) · Student on-device: MobileNetV3-Small reemplaza a EdgeNeXt-Tiny

| | |
| --- | --- |
| **Decisión anterior (C-5, 2026-09-08)** | EdgeNeXt-Tiny (~2-4M parámetros) como alumno destilado on-device |
| **Decisión del autor (2026-09-11)** | **MobileNetV3-Small** como alumno. El teacher no cambia: sigue siendo BioCLIP v1 (ViT-B/16) en servidor |
| **Justificación** | Soporte maduro en LiteRT/TFLite: MobileNetV3 es una arquitectura de primera clase en el conversor, mientras que EdgeNeXt (con sus bloques de atención por split-channel) es terreno menos probado. Con el pivote de INT8 ya costado una vez (C-5), reducir riesgo de conversión pesa más que los ~1-2 MB de diferencia |
| **Confirmado en esta corrida** | `docs_vision_model_plan/` ya especificaba MobileNetV3-Small â€” la contradicción con la bóveda queda resuelta a favor de ese documento en este punto concreto |
| **Corrección adicional** | Ese mismo documento cita "BioCLIP v2.5" como teacher: **ese modelo no existe** (solo hay BioCLIP v1 y BioCLIP 2). El teacher es v1, conforme a la decisión del 2026-09-05 |
| **Corrección (2026-09-26)** | BioCLIP 2.5 **sí existe**: `imageomics/bioclip-2.5-vith14` (ViT-H/14, 1024-d), en la caché local y cargado por `services/ai-service` del servidor. Lo que sigue en pie: el teacher y el encoder del teléfono son v1. Ver [[Contradicciones del Modo Administrativo]] #23 |
| **Dimensión del embedding** | Fijada en **512-d**, igual que BioCLIP v1, para que los paquetes regionales `.sqlite` sigan siendo comparables entre servidor y dispositivo (cierra el "por definir" de [[Plan de Acción y Arquitectura Conceptual]]) |
| **Implementación** | `training/train_student.py` (Multi-Head Loss, Î±=0.3, T=4.0, warm-up 5 épocas AdamW 1e-3 â†’ destilación AdamW 1e-4 con parada temprana) |
| **Documentos afectados** | [[Modelo de Visión â€” BioCLIP]], [[Optimización para Inferencia en Móvil]], [[Cronograma y Plan de Trabajo]] |

### C-9 (resuelto) · El entrenamiento de identificación espera al recorte segmentado

| | |
| --- | --- |
| **Problema** | H4 (anotación CVAT) no llegó el 09 sep, así que no hay modelo de segmentación y por tanto no hay recortes con máscara (variante C del §5 de [[Modelo de Visión â€” BioCLIP]]) |
| **Opción descartada** | Entrenar ya una línea base sobre la imagen completa (variante A) para desbloquear la semana 2 |
| **Decisión del autor (2026-09-11)** | **Esperar a segmentación.** No se entrena identificación hasta tener los recortes enmascarados |
| **Por qué es defendible** | La variante C es la que sostiene el ~99 % de la Etapa I (C-4). Una cifra obtenida sobre imagen completa no sería comparable con ese antecedente y habría que repetir el entrenamiento entero al llegar las máscaras â€” además de arriesgar *shortcut learning* sobre el sustrato |
| **Consecuencia sobre el cronograma** | Las tareas del 12â€“13 sep (cabezas jerárquicas, destilación) quedan **bloqueadas por H4**, no por falta de código. `training/train_student.py` exige `--masks-dir` y se niega a correr sin él salvo override explícito |
| **Lo que sí avanza sin H4** | El manifiesto de `GroupSplit` ya está construido y verificado (`training/manifiesto.json`): 3.258 imágenes, 1.706 individuos, 0 grupos repartidos entre particiones. Entorno de entrenamiento verificado end-to-end el 2026-09-11: Python 3.13 + PyTorch 2.11+cu128 en `D:\Anura\.venv-train`, CUDA operativa sobre RTX 4050. 30 comprobaciones de humo pasan (`test_cascada.py` 17/17, `test_modelo.py` 13/13 incl. descarga real de BioCLIP v1): alumno MobileNetV3-Small = 2,07M parámetros (7,89 MB FP32 / 3,95 MB FP16, dentro del presupuesto), embedding 512-d confirmado igual en teacher y student, gradiente de la Multi-Head Loss llega a las 148 capas del alumno, cascada jerárquica nunca predice taxonómicamente imposible y respeta el techo de resolución también a nivel de género |
| **Documentos afectados** | [[Cronograma y Plan de Trabajo]], [[Riesgos del Proyecto]] |

### C-11 (ejecutado y validado, 2026-09-12) · Arquitectura definitiva on-device: Transfer Learning + Image Encoder local

| | |
| --- | --- |
| **Decisiones revertidas** | C-5 (INT8 fracasó), C-8 (MobileNetV3 destilado), C-10 (destilación inviable) |
| **Decisión del autor (2026-09-11)** | **BioCLIP v1 oficial â†’ Transfer Learning â†’ extraer Image Encoder â†’ ONNX FP16 â†’ instalar en Android localmente** |
| **Separación modelo/datos** | El encoder (fp16, instalado una vez) y los paquetes regionales (embeddings + metadata por departamento, descargables/actualizables) son componentes separados. Agregar nuevas especies = actualizar paquetes, no re-entrenar el encoder |
| **Flujo on-device (revisado)** | No es solo el encoder: se exportó el **clasificador completo** (encoder + 3 cabezas familia/género/especie) â€” foto â†’ preprocesamiento 224à—224 â†’ ONNX fp16 â†’ probabilidades por especie â†’ combinar con prior GPS (opcional, §C-11 más abajo) â†’ resultado. La ruta "embedding + SQLite-vec + Top-K" queda como alternativa para bàºsqueda por similitud, no como ruta àºnica |
| **Cifra proyectada vs. medida** | La proyección original era "~173 MB FP16" â€” **medido: 165,6 MB**, cercano y confirmado empíricamente, no solo estimado |
| **Verificación obligatoria â€” cumplida y superada** | El criterio pedía cosine similarity > 0,99 PyTorch vs. ONNX; el resultado real fue **100 % de predicciones Top-1 idénticas** en 64 imágenes de validación, diferencia máxima de probabilidad de 1,16à—10â»³ (fp16) |
| **âš ï¸ Discrepancia de alcance a verificar** | Esta entrada original cita "28 especies" (coherente con C-3, el catálogo oficial del prototipo). **El entrenamiento ejecutado y todo lo documentado en [[Experimentos y Resultados]] y [[Optimización para Inferencia en Móvil]] usa 41 especies** (incluye especies fuera de las 28 originales, ej. `Sachatamia_electrops` con soporte parcial). Verificar con el autor si el catálogo de 28 quedó ampliado a 41, o si el checkpoint actual excede el alcance del prototipo y debe recortarse antes de integrar en la app |
| **BioCLIP v1 estado** | âœ… Descargado en caché: `C:\Users\user\.cache\huggingface\hub\models--imageomics--bioclip` (570.87 MB, commit `ce901ab3`) |
| **Cuando re-entrenar** | Solo si la discriminación entre especies similares es insuficiente; agregar especies o coordenadas no exige re-entrenamiento |
| **Extensión no contemplada en la decisión original: prior geográfico** | Se añadió y validó un prior bayesiano simple usando GPS (+15 a +25 pp de Top-1, segàºn distancia a datos conocidos) â€” no estaba en el diseño de C-11, se descubrió como oportunidad durante la validación. Detalle en [[Optimización para Inferencia en Móvil]] §6 |
| **Documentos afectados** | [[Cronograma y Plan de Trabajo]], [[Modelo de Visión â€” BioCLIP]], [[Arquitectura Multimodal]], [[Optimización para Inferencia en Móvil]], [[Experimentos y Resultados]] |

### C-12 (parcial, 2026-09-12) · Dispositivo de prueba actualizado: Redmi Note 13 Pro+

| | |
| --- | --- |
| **Decisión anterior (parte de C-5, 2026-09-08)** | Samsung Galaxy A30 (4 GB RAM) como dispositivo de referencia mínimo |
| **Contexto del cambio** | C-5 fijó el Galaxy A30 pensando en la arquitectura destilada (EdgeNeXt-Tiny / MobileNetV3-Small, <15 MB de modelo). Esa arquitectura fue descartada por C-10; la vigente (C-11) pesa 165,6 MB en disco y usa ~405 MB de RAM en ejecución â€” mucho más que el presupuesto original de esa nota |
| **Decisión del autor (2026-09-12)** | **Redmi Note 13 Pro+** como dispositivo de prueba para la arquitectura C-11 |
| **Estado de la validación** | ðŸŸ¡ **Parcial** â€” se emuló la gama de chip variando `intra_op_num_threads` (1/2/4 hilos) sobre hardware de desarrollo (PC), no sobre el Redmi físico. RAM medida (~405 MB) y latencia (150-400 ms) son representativas del comportamiento del modelo, pero **no sustituyen una medición en el dispositivo real** (ARM real, throttling térmico, RAM compartida con el resto del sistema Android/HyperOS) |
| **Pendiente real** | Repetir la medición de §5 de [[Optimización para Inferencia en Móvil]] directamente en el Redmi Note 13 Pro+ una vez exista un build de Android que cargue el ONNX; confirmar variante de RAM exacta del dispositivo físico disponible (existen versiones de 8 GB y 12 GB) |
| **¿El Galaxy A30 queda descartado?** | No necesariamente â€” si la arquitectura on-device vuelve a cambiar (por ejemplo, si se retoma la destilación con la variante C segmentada, segàºn deja abierto C-10), el Galaxy A30 podría volver a ser el piso de referencia. Por ahora, para C-11, el dispositivo de prueba es el Redmi Note 13 Pro+ |
| **Documentos afectados** | [[Optimización para Inferencia en Móvil]] §5, §7 |

### C-15 (FIRMADA, 2026-09-13) · Ruta de producción FINAL para 27 sep: k-NN + SQLite-vec (Ruta B, Merlin style) â€” NO clasificación directa

| | |
| --- | --- |
| **Decisión del autor (2026-09-13)** | **Ruta B (k-NN + paquetes regionales SQLite-vec)** es el flujo de producción para cumplir requerimientos â€” imita explícitamente el patrón de Merlin Bird ID (Cornell Lab). El clasificador completo ONNX (encoder+3 cabezas, Ruta A) queda como alternativa técnica, no como ruta primaria |
| **âœ… Comparación empírica DEFINITIVA (EXP-015, paquete regional real de Antioquia)** | Con el paquete filtrado a las 25 especies con presencia real en Antioquia (no las 41 completas): **Ruta B (k-NN k=5): 66,2 % Top-1 / 83,7 % Top-3. Ruta A (clasificador, mismo subconjunto de 467 imágenes de test): 54,4 % Top-1 / 79,9 % Top-3. Î” = +11,8 pp a favor de Ruta B.** La medición previa (EXP-014, paquete con las 41 especies completas) daba âˆ’0,7 pp â€” el resultado se **invierte** al filtrar por región: el clasificador de 41 clases desperdicia probabilidad en 16 especies que no viven en Antioquia; el k-NN sobre el paquete regional nunca compite contra ellas. Detalle en [[Experimentos y Resultados]] EXP-014/EXP-015 |
| **Artefactos de producción (firmados, 27 sep) â€” TODOS generados y validados** | 1. **`encoder_anura_fp16.onnx`** (165,4 MB, exportado 2026-09-13, similitud coseno 0,999999 vs. PyTorch en 64 imágenes reales) 2. **`antioquia_v1.sqlite`** (6,39 MB, 2.073 vectores, 25 especies reales â€” ver fila siguiente) 3. `vocabulario.json` 4. `prior_geografico_movil.json` |
| **Flujo FINAL de inferencia on-device (k-NN)** | Foto â†’ resize 224à—224 â†’ encoder ONNX fp16 â†’ embedding 512-d â†’ k-NN (k=5) en paquete `.sqlite` activo â†’ voto ponderado por similitud â†’ devolver especie + N ejemplares similares como evidencia |
| **Paquete SQLite-vec de Antioquia REAL, generado y medido (2026-09-13)** | `bioclip/paquetes_regionales/antioquia_v1.sqlite` â€” 6,39 MB, 2.073 vectores, **25/41 especies** filtradas por presencia geográfica real (â‰¥3 observaciones de train dentro del bbox del departamento, usando coordenadas ya auditadas de `prior_geografico_movil.json`). Reemplaza al paquete de prueba anterior (`antioquia_prueba_v1.sqlite`, simulado con las 41 especies completas) |
| **Modelo operativo** | Backbone congelado en APK; paquetes regionales descargables/reemplazables por zona (patrón Merlin Bird ID) |
| **SQLite-vec integración** | âœ… Confirmado funcional en Python (`sqlite_vec` cargable como extensión, tabla `vec0` operativa) â€” falta la integración Android nativa (`.so` de sqlite-vec para ARM) |
| **Catálogo** | Definido por paquete regional activo, NO por modelo (crece sin reentrenar) |
| **âœ… Pendiente de C-15 anterior â€” RESUELTO (2026-09-13)** | El encoder solo existía àºnicamente en `.pt` (PyTorch); ya se exportó a ONNX fp16 (165,4 MB) siguiendo el mismo patrón validado en Fase 7 (opset 18, batch fijo=1, consolidación de external data) |
| **ðŸ”´ Pendiente real para Android (14 sep)** | Integrar `sqlite-vec` nativo para Android (librería `.so` ARM) y `onnxruntime-android` â€” ambos existen como paquetes publicados, falta la integración Kotlin |
| **Presupuesto APK** | Encoder fp16 165,4 MB + código + runtime sqlite-vec â€” dentro de RNF-05 |
| **Validación de integridad del encoder ONNX** | âœ… Similitud coseno 0,999999 fp16 vs. PyTorch (64 imágenes reales de test), 1,000000 en fp32 |
| **Documentos afectados** | [[Base Vectorial (SQLite-vec)]], [[Optimización para Inferencia en Móvil]], [[Proceso de Crecimiento del Catálogo Post-Despliegue]], [[Arquitectura Multimodal]], [[Experimentos y Resultados]] |

### C-14 (DESCARTADA, 2026-09-13) · Variante C (segmentación binaria previa) no se utilizará en el prototipo del 27 sep

| | |
| --- | --- |
| **Estado** | âŒ **DESCARTADA â€” sin reentrenamiento** |
| **Decisión del autor (2026-09-12)** | La variante C (imagen recortada + máscara binaria antes de BioCLIP) **no es ruta de producción para este sprint**. Se mantiene como trabajo futuro post-27 sep |
| **Por qué se descarta** | Diagnóstico completo en [[Experimentos y Resultados]] (EXP-011/012/013): el segmentador binario entrenado en 9 especies empeora el resultado al escalar a 41 especies (+34 % de ruido en máscaras, âˆ’10 pp de Top-1 incluso tras fijar dos bugs). El àºnico experimento que podría revertir esta decisión es **reentrenar Fase 4 desde cero** sobre el recorte con máscara (variante C real, con ambos fixes aplicados) â€” pero **cronológicamente no cabe en 15 días** antes del 27 sep sin parar el desarrollo de Android |
| **Ruta adoptada** | Imagen completa (variante A, sin recorte ni máscara) â€” **Top-1 56,8 % fp32 / 56,7 % fp16 + prior GPS +15-25 pp = 81,4 % en sitios conocidos** |
| **Qué abre después del 27 sep** | (1) Reentrenar Fase 4 en variante C real con segmentador binario corregido, para cerrar la pregunta "¿mejora si se reentrena?". (2) Segmentación **semántica** (16 etiquetas anatómicas de CVAT) â€” trabajo en curso aparte, distinto del binario, para la evidencia "por qué" del resultado |
| **En términos de riesgo** | Cerrar esta rama ahora **simplifica el MVP**: un modelo, un preprocesamiento, un pipeline. Variante C volverá si la evidencia de campo sugiere que hay ganancia de 5-10 pp que justifique ese reentrenamiento |
| **Documentos afectados** | [[Cronograma y Plan de Trabajo]], [[Modelo de Visión â€” BioCLIP]], [[Experimentos y Resultados]], [[Optimización para Inferencia en Móvil]] |

### C-13 (aclaración del autor, 2026-09-12) · El fracaso de "variante C" del 11 sep fue con segmentación BINARIA, no semántica â€” y Android arranca el lunes

| | |
| --- | --- |
| **Ambigüedad que esto resuelve** | El diagnóstico de sprint del 2026-09-12 (ver [[Experimentos y Resultados]]) encontró que la corrida de variante C (segmentada) del 11 sep dio peor Top-1 que sin segmentar, sin poder explicar la causa exacta |
| **Aclaración del autor** | El modelo usado para producir las máscaras de esa corrida era el de **segmentación BINARIA** (individuo vs. fondo â€” el mismo tipo que sostiene el ~99 % de la Etapa I, ver arriba §"El ~99% de la Etapa I..."), y **ese fue el que fracasó** al escalar a 41 especies con datos de campo más heterogéneos. No fue un problema de la variante C como concepto, sino específicamente de ese segmentador binario en este dataset más amplio |
| **Segmentación SEMàNTICA (16 etiquetas anatómicas, CVAT)** | Sigue como trabajo en curso, **se retoma cuando sea posible** â€” no es bloqueante para el sprint actual. Es un modelo distinto del binario: divide la imagen en estructuras anatómicas (para la evidencia "por qué" del resultado), no solo separa individuo de fondo |
| **Implicación para C-9 / el pipeline de identificación** | La decisión de "esperar al recorte segmentado antes de entrenar identificación" (C-9) queda en tensión: el recorte binario disponible **empeora** el resultado en vez de mejorarlo. La variante A (imagen completa, sin segmentar) sigue siendo la que sostiene todo el trabajo de Fases 4-7 de esta sesión â€” no hay, por ahora, evidencia de que valga la pena bloquear el desarrollo esperando un segmentador binario mejor |
| **Diagnóstico completo (2026-09-12, mismo día)** | Causa raíz encontrada y confirmada: bug de diseño en el recorte (bbox de todos los píxeles marcados, no del componente conexo de la rana) + segmentador entrenado en 9 especies aplicado a 41. Fix aplicado en `fase_4_transfer_learning.py`. **Tras arreglarlo, sigue siendo peor que imagen completa** (60,7 %â†’50,7 % Top-1 en inferencia pareada, 150 imágenes) â€” porque el modelo de producción nunca vio recortes en entrenamiento. Pendiente real: probar si **reentrenar** sobre el recorte arreglado sí ayuda â€” no descartado, solo sin probar. Detalle en EXP-011/EXP-012, [[Experimentos y Resultados]] Hallazgo 4 |
| **Desarrollo Android** | Arranca el **lunes 14 de septiembre de 2026** â€” 3 días después de lo que el cronograma daba por hecho para el cierre de la Semana 1 (Room + Listado funcionando el 11 sep). El desfase es real y debe reflejarse en el resto del cronograma, no absorberse en silencio |
| **Documentos afectados** | [[Experimentos y Resultados]], [[Cronograma y Plan de Trabajo]], [[Automatización del Entrenamiento de Segmentación]] |

### ~~C-10 (INVIABLE)~~ · Destilación de conocimiento: BioCLIP v1 â†’ MobileNetV3-Small

| | |
| --- | --- |
| **Decisión anterior (C-5/C-8)** | Multi-Head Loss (CE + KL con T=4.0, Î±=0.3) para destilar el conocimiento de BioCLIP v1 (teacher, 86M params, ViT-B/16) en MobileNetV3-Small (student, 2,07M params) |
| **Prueba realizada** | Corrida diagnóstica completa: 2.230 imágenes de entrenamiento, GroupSplit por obs_id, variante A (imagen completa, sin máscara). Fases: (1) extracción de embeddings BioCLIP, (2) linear probe del teacher (300 épocas), (3) warm-up del alumno (5 épocas CE), (4) destilación conjunta (20 épocas Multi-Head Loss) |
| **Resultado cuantitativo** | **Degradación Top-1: 33,39 puntos** (teacher 57,7% â†’ student 24,3%). Objetivo estándar para destilación: <10 puntos. Esto es **inviable**. |
| **Análisis** | (1) Coherencia taxonómica: 79,7% vs 83,4% (apenas 3,6 puntos) â€” el alumno aprendió la estructura jerárquica. (2) Cascada: 43,6% affirmed at especie, 29,9% género, 26,5% familia â€” el alumno está degradando con gracia, no mintiendo. (3) Problema real: el alumno **no aprendió a discriminar especies dentro de género** â€” dicho de otro modo, no puede hacer la distinción fina que BioCLIP hace. |
| **Causa probable** | (1) Asimetría fundamental: el teacher se entrenó sobre millones de imágenes biológicas ya viendo ranas; el alumno entrena su backbone completo desde ImageNet en 2.230 imágenes donde la rana ocupa ~10% del encuadre. (2) Variante A (imagen completa) es intrínsecamente más dura â€” la rana es un objeto pequeño en un fondo ruidoso, y el alumno tiene que aprender "esto es una rana" Y "cuál rana" al mismo tiempo desde hojarasca. BioCLIP ya resolvió (1), solo necesita resolver (2). (3) Destilación se diseñó para pasos increméntales (5-10 puntos), no para cerrar un gap de esta magnitud. |
| **Decisión del autor (2026-09-11)** | **Destilación es inviable.** No se continuarán entrenamientos por esta ruta. |
| **Consecuencia** | Se descarta C-5 y C-8 completamente. El backbone on-device ya no es MobileNetV3-Small destilado; la arquitectura on-device queda **por decidir**. Opciones: (A) BioCLIP v1 cuantizado más agresivo (INT4, trade-off latencia vs. precisión), (B) backbone de propósito específico entrenado desde cero sin destilación (tiempo de GPU, riesgo de falta de convergencia antes del 27 sep), (C) aceptar que la variante A diagnóstica aquí requería segmentación para cerrar el gap â€” lo que C-9 ya asumía |
| **Lo que Sà se mantiene** | Multi-Head Loss y cascada jerárquica son válidos **cuando se tienen datos de entrada de calidad** (variante C con segmentación); el problema no es la pérdida ni la cascada, es que la imagen completa no da señal clara suficiente. La prueba de esto es que la coherencia taxonómica se transfiere bien (79,7 vs 83,4). |
| **Blocker real** | No es "destilación no funciona" â€” es "sin segmentación, ni el teacher LLegó a 57,7%, el punto de partida es mucho más bajo". La variante A diagnóstica aquí mide ambos modelos en condiciones desfavorables pero medibles. **La decisión correcta es esperar H4 y re-evaluar con variante C segmentada.** |
| **Documentos afectados** | [[Cronograma y Plan de Trabajo]] (destilación bloqueada hasta H4), [[Modelo de Visión â€” BioCLIP]], [[Optimización para Inferencia en Móvil]], [[Riesgos del Proyecto]] (nuevo riesgo: arquitectura on-device aàºn indefinida sin destilación) |

---

## ðŸ”´ Críticas â€” bloquean implementación

### C-3 (resuelto) · Nàºmero de especies: seis cifras distintas â†’ **28 especies** para el catálogo del prototipo

| Fuente | Cifra |
| --- | --- |
| [[Introducción y Justificación]] | 15 especies, ~70 fotografías por especie |
| [[Estrategia de Construcción del Dataset]] â€” Etapa I | 14 especies en el texto (**la cifra confirmada por el autor y por la tabla de resultados es 10**) |
| [[Notas Originales â€” Segmentación Semántica y Metodología Anura]] | 23 especies |
| [[Listado de Individuos y Arreglo Taxonómico]] | ~30 filas |
| [[Guía CVAT â€” àndice\|Guía CVAT]] | atributo `especie` con 30 opciones; Anexo C con 28 fichas |
| RNF-04 ([[Objetivos y Alcance]]) | "las 50 especies seleccionadas" |

| | |
| --- | --- |
| **Decisión (2026-09-05)** | El catálogo oficial del prototipo es de **28 especies**. Coincide exactamente con las 28 carpetas de recolección de campo ya organizadas por `equipo 1/2/3` y con las 28 opciones reales del atributo `especie` en `anuro_labels.json` (30 valores del selector menos los dos placeholders `otra_no_listada` y 
o_determinable`) |
| **RNF-04 ("50 especies")** | Queda como **meta de largo plazo** (Etapa III de [[Escalabilidad]] §4), no como el catálogo de este prototipo â€” corregir la redacción del RNF-04 en el documento de grado para no prometer 50 en la evaluación del 27 de septiembre |
| **Recolección de las 70 muestras/especie** | Método ya en marcha: recolección de campo distribuida en tres equipos (`equipo 1`, `equipo 2`, `equipo 3`) por especie/región, unificada a JPG con `unificar_para_cvat.py` (RAW y otros formatos â†’ JPG homogéneo para CVAT). Las especies que no lleguen a 70 individuos propios se completan con iNaturalist/GBIF filtrado por calidad y coordenadas verificables ([[Estrategia de Construcción del Dataset]]) |
| **Pendiente real** | Confirmar, especie por especie, cuáles de las 28 ya tienen â‰¥ 70 individuos y cuáles necesitan complemento de fuente secundaria â€” tarea de la semana 1 del sprint ([[Cronograma y Plan de Trabajo]] §0) |
| **Documentos afectados** | [[Estrategia de Construcción del Dataset]], [[Objetivos y Alcance]] (RNF-04), [[Cronograma y Plan de Trabajo]], [[Anura â€” àndice General]] |

---

## ðŸŸ¡ Importantes â€” afectan a coherencia del documento

### I-1 · Roboflow vs. CVAT

Las [[Notas Originales â€” Método de Anotación y Plantillas Taxonómicas|notas originales]] y la [[Guía de Anotación Roboflow (histórico)|guía de anotación de Notion]] describen el flujo en **Roboflow**; la [[Guía CVAT â€” àndice|guía CVAT v1.0]] describe el flujo definitivo en **CVAT**. La propia nota del autor lo dice: *"todo quedó para CVAT, en la guía CVAT quedó todo lo final"*.

**Resuelto en esta bóveda:** la guía CVAT es la fuente vigente; el material de Roboflow queda marcado como histórico. Falta actualizar las menciones a Roboflow en los documentos que irán al trabajo escrito.

### I-2 · Nàºmero de clases anatómicas: 8 / 13 / 16 / 18

| Fuente | Clases |
| --- | --- |
| [[Guía de Anotación Roboflow (histórico)]] | 8 (IDs 0â€“7) |
| [[Notas Originales â€” Método de Anotación y Plantillas Taxonómicas]] | 13 regiones principales |
| [[Guía CVAT â€” àndice\|Guía CVAT v1.0]] | **16 etiquetas** âœ… vigente |
| [[Notas Originales â€” Segmentación Semántica y Metodología Anura]] | 18 regiones anatómicas |

**Propuesta:** 16 etiquetas de la guía CVAT es el esquema vigente. Documentar la evolución 18 â†’ 13 â†’ 16 como decisión metodológica (la reducción tiene sentido: no todas las regiones son anotables de forma fiable).

### I-3 · Segmentación semántica vs. instancia, y qué modelo

Los [[Objetivos y Alcance|objetivos]] dicen "segmentación semántica basada en **YOLO**", pero YOLO-seg hace segmentación **de instancias**. Además el RF-03 exige distinguir varios individuos en una imagen, lo cual **requiere** instancias, no segmentación semántica.

**Propuesta:** el término correcto para lo que necesita Anura es *segmentación de instancias con partes anatómicas*. Ajustar la redacción en el documento; es un detalle terminológico que un jurado técnico notará.

### I-4 (resuelto) · MP3 permitido en requisitos, prohibido en la metodología

- **RF-01.2**: "carga/grabación de archivos de audio (WAV, **MP3**)"
- **[[Estrategia de Construcción del Dataset]]**: "Evita MP3 o AAC, ya que la compresión psicoacàºstica descarta armónicos finos"

**Decisión (2026-09-05):** formato óptimo = **WAV / PCM 16-bit, 44,1 kHz, mono** â€” es el àºnico exigido para la grabación propia de la app y para todo el material de entrenamiento/calibración. MP3 se acepta **àºnicamente** en la carga de archivos ya existentes del usuario, con una advertencia visible de que puede degradar la precisión del análisis bioacàºstico.

### I-5 (resuelto) · Individuos por especie: 70 vs. 20/30/40

La estrategia de dataset exige **mínimo 70 individuos por especie**; las notas originales hablan de 20 (mínimo) / 30 (recomendado) / 40+ (excelente) para el segmentador. Además, 550 imágenes originales de train no son compatibles con 70 individuos à— 30 especies.

**Confirmado por el autor (2026-09-05):** son, en efecto, requisitos de **dos modelos distintos**, tal como proponía la aclaración probable â€” **70 individuos/especie** para el modelo de identificación (28 especies, cumplido), y **25â€“30 imágenes/especie** para el modelo de segmentación anatómica, dentro del rango 20â€“40 previsto aquí para el segmentador universal. Las 550 imágenes son las anotadas para segmentación, no el total del dataset. No era una contradicción â€” eran dos datasets con dos requisitos de volumen distintos, ya reflejado en [[Estrategia de Construcción del Dataset]] y [[Riesgos del Proyecto]] (D-3).

### I-6 (resuelto) · "Anura" vs. "Anuro", y Notion como fuente

El proyecto se llama **Anura** en Notion y en el documento; la guía CVAT usa **Anuro** (proyecto, equipo, workspace). *Anura* es taxonómicamente el nombre del orden y el que aparece en los objetivos.

**Decisión (2026-09-05):** el nombre del producto es **Anura**, sin excepción en documentación nueva. "Anuro" queda **solo** donde ya existe creado dentro de CVAT (nombre de proyecto/equipo/workspace de la herramienta) â€” no se renombra ahí, no vale la pena el costo de migración. Además, el **proyecto de Notion queda deprecado como fuente**: es historia vieja, ya migrada a esta bóveda. De aquí en adelante, **esta bóveda de Obsidian es la àºnica fuente de verdad**; no se vuelve a consultar Notion para decisiones nuevas. Las notas que citan "fuente: Notion" (p. ej. [[Plan de Acción y Arquitectura Conceptual]], [[Estrategia de Construcción del Dataset]]) se conservan como registro histórico de dónde vino el contenido, no como indicación de que Notion siga activo.

### I-7 (resuelto) · Numeración de historias de usuario

En [[Historias de Usuario]], el diagrama mencionaba **HU-06 (Exportación DwC)** mientras la tabla resumen asignaba esa función a **HU-05**, y la fila de HU-05 se referenciaba a sí misma como entrada.

**Corregido (2026-09-05):** no existe HU-06 â€” el diagrama de [[Historias de Usuario]] ya quedó actualizado a **HU-05: Exportación DwC**, coherente con la tabla resumen y con la sección HU-05 completa del documento.

---

## ðŸŸ¢ Menores â€” precisión terminológica

| #   | Punto                                                                                              | Corrección                                                                                                                                                                                                                                                                                   |
| --- | -------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| M-1 | "TensorFlow Lite" (RF-12)                                                                          | Desde 2024 se llama **LiteRT**; dependencia `com.google.ai.edge.litert`                                                                                                                                                                                                                      |
| M-2 | "Core ML/TFLite" en las notas                                                                      | Core ML es exclusivo de iOS; el alcance es Android â†’ LiteRT/ONNX                                                                                                                                                                                                                             |
| M-3 | Cifra de especies de Colombia                                                                      | Se cita 911; conviene verificar contra la fuente vigente de *Amphibian Species of the World* / SiB Colombia y fechar el dato                                                                                                                                                                 |
| M-4 | "EfficientNet... escalamiento equilibrado" atribuido a BioCLIP en [[Introducción y Justificación]] | El escalado compuesto es de EfficientNet, no de BioCLIP. Corregir esa frase: describe una arquitectura y cita otra                                                                                                                                                                           |
| M-5 | Bases de datos vacías en Notion                                                                    | Cuatro CSV referenciados no tienen contenido: *Estrategia de organización del Dataset*, *Estrategia de Manejo de Imágenes*, *Estrategia de Manejo de Audio*, *Manejo de clases desconocidas*. El contenido está en el cuerpo del documento; los enlaces vacíos se eliminaron en la migración |

> [!note] M-4 conviene revisarlo con calma
> La frase de la justificación describe el escalado compuesto de profundidad/anchura/resolución â€”que es la aportación de EfficientNetâ€” y lo atribuye a BioCLIP citando a Stevens et al. Es el tipo de error que un jurado detecta y que resta credibilidad al marco teórico, aunque el resto esté bien construido. Con EfficientNet ya fuera de la arquitectura (C-2), esta frase queda todavía más fuera de lugar: describe una arquitectura que el proyecto ni siquiera usa.

---

## Decisiones a cerrar

| # | Decisión | Responsable | Fecha límite | Estado |
| --- | --- | --- | --- | --- |
| ~~1~~ | ~~Motor vectorial en el dispositivo~~ (C-1) | | | âœ… ObjectBox |
| ~~2~~ | ~~Backbone principal~~ (C-2) | | | ðŸŸ¡ Revisado por C-5: BioCLIP àºnico **en servidor** (teacher); on-device es EdgeNeXt-Tiny destilado |
| 3 | Nàºmero oficial de especies por etapa (C-3) | | | ðŸ”´ |
| ~~4~~ | ~~Reevaluar Etapa I~~ (C-4) | | | âœ… Confirmado ~99 %, sin fuga |
| ~~5~~ | ~~Versión de BioCLIP (v1 vs. v2) y coherencia móvil/servidor~~ | | 2026-09-05 | âœ… **v1 en ambos lados** para el sprint del prototipo (matiz: "ambos lados" ahora significa servidor + teacher de destilación, no el móvil directamente â€” ver C-5) |
| 6 | Qdrant vs. pgvector en el servidor | | | ðŸ”´ |
| 7 | Modelo de segmentación concreto | | | ðŸŸ¡ Ultralytics YOLO-seg como base de trabajo â†’ [[Automatización del Entrenamiento de Segmentación]]; tamaño exacto (n/s) por confirmar con datos reales |
| ~~8~~ | ~~Alcance mínimo defendible (riesgo P-1)~~ | | 2026-09-05 | âœ… Alcance mínimo **del prototipo al 27 sep** fijado â†’ [[Cronograma y Plan de Trabajo]] §0; el alcance mínimo defendible del trabajo de grado completo (con piloto de campo y documento) sigue abierto y se decide por separado |
| ~~9~~ | ~~Backbone on-device tras fracaso de INT8~~ (C-5) | | 2026-09-08 | âœ… EdgeNeXt-Tiny destilado, Multi-Head Loss |
| ~~10~~ | ~~Motor vectorial local~~ â€” revisión de C-1 (C-6) | | 2026-09-08 | âœ… SQLite (sqlite-vec), reemplaza ObjectBox |
| ~~11~~ | ~~Rama de audio: reutilizar backbone o modelo propio~~ (C-7) | | 2026-09-08 | âœ… Modelo de audio propio y dedicado |
| ~~12~~ | ~~Student on-device~~ â€” revisión de C-5 (C-8) | | 2026-09-11 | âœ… MobileNetV3-Small, embedding 512-d |
| ~~13~~ | ~~¿Entrenar línea base sin segmentación?~~ (C-9) | | 2026-09-11 | âœ… No: se espera a H4 y a la variante C |
| ~~14~~ | ~~Destilación de BioCLIP â†’ MobileNetV3 como backbone on-device~~ (C-10) | | 2026-09-11 | ðŸ”´ **INVIABLE** â€” degradación Top-1 de 33 puntos (objetivo <10); sin segmentación no hay señal suficiente; re-evaluar con H4 |
| ~~15~~ | ~~Arquitectura on-device definitiva: Transfer Learning + encoder local~~ (C-11) | | 2026-09-11 | âœ… Ejecutado y validado 2026-09-12 â€” ONNX fp16, 165,6 MB, 100% predicciones idénticas a PyTorch. Discrepancia de alcance 28 vs. 41 especies pendiente de confirmar |
| 16 | Dispositivo de prueba: Redmi Note 13 Pro+ (C-12) | | 2026-09-12 | ðŸŸ¡ Fijado, medición en emulación de hilos completada; falta medir en el dispositivo físico |
| ~~17~~ | ~~¿Qué segmentador falló el 11 sep â€” binario o semántico?~~ (C-13) | | 2026-09-12 | âœ… Fue el binario (individuo vs. fondo); la semántica (16 etiquetas) sigue en desarrollo aparte |
| 18 | Inicio real de desarrollo Android (C-13) | | 2026-09-12 | ðŸŸ¡ Confirmado para el lunes 14 sep â€” 3 días después de lo previsto en el cronograma; falta ajustar el resto de fechas de la Semana 2-3 |

## Registro de decisiones tomadas

| Fecha | Decisión | Motivo | Documentos actualizados |
| --- | --- | --- | --- |
| 2026-09-04 | ObjectBox como motor vectorial embebido en el móvil | Qdrant no puede correr embebido en Android; ObjectBox tiene soporte Kotlin nativo de primera clase | [[Base Vectorial (SQLite-vec)]], [[Stack Tecnológico]], [[Riesgos del Proyecto]], [[Anura â€” àndice General]] |
| 2026-09-04 | BioCLIP como àºnico backbone del proyecto (visión y audio) | Instrucción directa del autor; elimina la contradicción con EfficientNet y reduce el presupuesto de almacenamiento móvil | [[Modelo de Visión â€” BioCLIP]], [[Arquitectura Multimodal]], [[Métricas Offline]], [[Optimización para Inferencia en Móvil]], [[App Móvil]], [[Stack Tecnológico]], [[Experimentos y Resultados]], [[Anura â€” àndice General]] |
| 2026-09-04 | El ~99 % de la Etapa I se confirma como resultado legítimo | Aclaración del autor: segmentación binaria previa + `GroupSplit` por individuo, no fuga de información | [[Modelo de Visión â€” BioCLIP]], [[Métricas Offline]], [[Experimentos y Resultados]], [[Riesgos del Proyecto]], [[Anura â€” àndice General]] |
| 2026-09-05 | Fecha límite del prototipo: 27 de septiembre de 2026 | Instrucción directa del autor â€” 22 días desde hoy para un prototipo funcional desplegado, no el trabajo de grado completo | [[Cronograma y Plan de Trabajo]] (nueva §0), [[Roadmap y Fases]], [[Anura â€” àndice General]] |
| 2026-09-05 | Catálogo oficial de 28 especies para el prototipo (C-3) | Coincide con las 28 carpetas de recolección de campo y con `anuro_labels.json`; RNF-04 ("50 especies") pasa a meta de largo plazo | [[Inconsistencias y Decisiones Pendientes]] (C-3), [[Estrategia de Construcción del Dataset]], [[Anura â€” àndice General]] |
| 2026-09-05 | BioCLIP **v1** (ViT-B/16) como àºnica versión, en dispositivo y en servidor, para este sprint | Instrucción directa del autor ("asegurar esta previsión"); evita el problema de espacios de embedding incompatibles entre v1 y v2 dentro del plazo de 22 días â€” v2 en servidor queda como mejora post-sprint | [[Modelo de Visión â€” BioCLIP]], [[Stack Tecnológico]], [[Inconsistencias y Decisiones Pendientes]] |
| 2026-09-05 | Alcance mínimo del prototipo (27 sep) fijado explícitamente | Riesgo P-1 exigía esta conversación antes de que la fecha límite la decidiera por defecto | [[Cronograma y Plan de Trabajo]] §0, [[Roadmap y Fases]] |
| 2026-09-05 | Cifras reales confirmadas para el prototipo: **70 individuos/especie** (identificación, requisito original cumplido) y **25â€“30 por especie** (subconjunto anotado de segmentación, dentro del rango 20â€“40 de I-5) | Instrucción directa del autor â€” corrige una transcripción previa de esta misma bóveda que decía 20/especie para identificación | [[Estrategia de Construcción del Dataset]], [[Riesgos del Proyecto]] (D-3), I-5 |
| 2026-09-05 | Formato de audio óptimo confirmado: WAV/PCM 16-bit 44,1 kHz mono; MP3 solo en carga de usuario (I-4) | Cierra la contradicción entre RF-01.2 y la metodología de dataset | [[Objetivos y Alcance]], [[Estrategia de Construcción del Dataset]] |
| 2026-09-05 | Notion deprecado como fuente; Obsidian es la àºnica fuente de verdad (I-6) | Instrucción directa del autor â€” el proyecto de Notion es historia vieja ya migrada | Esta bóveda en su conjunto |
| 2026-09-05 | Numeración de historias de usuario corregida: no existe HU-06, es HU-05 (I-7) | El diagrama y la tabla resumen de [[Historias de Usuario]] ya coincidían salvo en el diagrama | [[Historias de Usuario]] |
| 2026-09-08 | BioCLIP-INT8 descartado como backbone on-device; EdgeNeXt-Tiny destilado (Multi-Head Loss) confirmado en su lugar (C-5) | INT8 sobre el ViT de BioCLIP fracasó en pruebas reales (~0,2 % exactitud, outliers de atención) | [[Modelo de Visión â€” BioCLIP]], [[Arquitectura Multimodal]], [[Optimización para Inferencia en Móvil]], [[Anura â€” àndice General]] |
| 2026-09-08 | Pesos de BioCLIP v1 revisados, características óptimas definidas para su rol de teacher (ViT-B/16, ~86M params, fine-tuned) | Cierra la tarea pendiente del 06 sep del sprint | [[Cronograma y Plan de Trabajo]] |
| 2026-09-08 | Dispositivo de referencia mínimo confirmado: Samsung Galaxy A30 (4GB RAM) (parte de C-5) | Instrucción directa del autor â€” es donde se emula y se miden latencia/RAM/batería | [[Optimización para Inferencia en Móvil]] |
| 2026-09-08 | SQLite (sqlite-vec) reemplaza a ObjectBox como motor vectorial local (C-6) | Instrucción directa del autor: "lo más óptimo para la nueva arquitectura" | [[Base Vectorial (SQLite-vec)]], [[Stack Tecnológico]] |
| 2026-09-08 | Rama de audio: modelo propio y dedicado, no reutilización del backbone EdgeNeXt-Tiny (C-7) | Instrucción directa del autor, por facilidad de implementación; el ahorro de MB de reutilizar ya no es crítico a esta escala | [[Modelo de Visión â€” BioCLIP]], [[Arquitectura Multimodal]] |
| 2026-09-11 | MobileNetV3-Small reemplaza a EdgeNeXt-Tiny como alumno destilado; embedding fijado en 512-d (C-8) | Soporte maduro en LiteRT frente a terreno no probado, tras el coste ya pagado por el fallo de INT8 | [[Modelo de Visión â€” BioCLIP]], [[Optimización para Inferencia en Móvil]] |
| 2026-09-11 | El entrenamiento de identificación espera al recorte segmentado; no se hace línea base sobre imagen completa (C-9) | La variante C es la que sostiene el ~99 % de la Etapa I; una cifra sobre imagen completa no sería comparable y habría que repetirla | [[Cronograma y Plan de Trabajo]], [[Riesgos del Proyecto]] |
| 2026-09-11 | `GroupSplit` por `obs_id` real de iNaturalist, con tope de 70 observaciones por especie | El identificador de individuo ya viene en el nombre de archivo del scraper; agrupar por bloques fijos habría partido individuos entre particiones | `training/prepare_dataset.py`, `training/manifiesto.json` |
| 2026-09-11 | **Destilación de BioCLIP v1 â†’ MobileNetV3-Small es INVIABLE** (C-10) | Corrida diagnóstica: Top-1 teacher 57,7% â†’ student 24,3% (degradación 33,39 puntos vs. objetivo <10). Causa: sin segmentación (variante A), la imagen completa no proporciona señal clara suficiente para que el alumno pequeño cierre el gap. La coherencia taxonómica (79,7 vs 83,4) se transfiere bien, pero la discriminación fina de especie no. La prueba de que el problema es la entrada, no el algoritmo: esperar a H4 y re-evaluar con variante C segmentada. | [[Cronograma y Plan de Trabajo]], [[Modelo de Visión â€” BioCLIP]], [[Optimización para Inferencia en Móvil]], [[Riesgos del Proyecto]] (nueva incertidumbre: arquitectura on-device aàºn por decidir) |
| 2026-09-11 | **Nueva arquitectura on-device: BioCLIP v1 oficial â†’ Transfer Learning â†’ Image Encoder â†’ ONNX FP16 â†’ Android local** (C-11) | C-5 a C-10 (destilación) descartados. El encoder visual se extrae del BioCLIP v1 entrenado en Anura, no se crea desde cero ni se usa encoder de terceros. El modelo (~173 MB) se instala localmente en el dispositivo; los paquetes regionales (embeddings + metadata por departamento) se descargan por separado, sin necesidad de re-entrenar el modelo para agregar nuevas especies. | [[Cronograma y Plan de Trabajo]], [[Modelo de Visión â€” BioCLIP]], [[Arquitectura Multimodal]], [[Optimización para Inferencia en Móvil]] |
| 2026-09-12 | C-11 ejecutado: clasificador completo exportado a ONNX fp16 (165,6 MB), validado con 100% de predicciones idénticas a PyTorch. Se probaron y descartaron int8 dinámico y estático (3 configuraciones) â€” confirman de forma independiente el fracaso de INT8 ya visto en C-5 | Necesidad de reducir tamaño de despliegue sin perder precisión; int8 resultó inviable en todas las variantes probadas para un ViT sin *quantization-aware training* | [[Optimización para Inferencia en Móvil]], [[Experimentos y Resultados]] |
| 2026-09-12 | Prior geográfico (GPS) añadido como componente del sistema: +15 a +25 pp de Top-1 segàºn distancia a datos de entrenamiento conocidos | Descubierto durante la validación de C-11; no estaba contemplado en el diseño original, pero es la mejora individual más grande medida en todo el proyecto | [[Optimización para Inferencia en Móvil]] §6, [[Experimentos y Resultados]] |
| 2026-09-12 | Dispositivo de prueba actualizado a Redmi Note 13 Pro+, reemplazando al Galaxy A30 para la arquitectura C-11 (C-12) | El Galaxy A30 (4GB) fue fijado para la arquitectura destilada (<15MB), descartada por C-10; la arquitectura vigente pesa 165,6MB y usa ~405MB de RAM, requiriendo un dispositivo con más margen | [[Optimización para Inferencia en Móvil]] §5, §7 |
| 2026-09-12 | Aclarado: el segmentador que falló el 11 sep (variante C peor que A) fue el **binario** (individuo vs. fondo); la segmentación **semántica** (16 etiquetas) sigue en desarrollo, se retoma cuando sea posible. Desarrollo Android confirmado para el **lunes 14 sep** (C-13) | Instrucción directa del autor, resuelve la ambigüedad señalada en el diagnóstico de sprint del mismo día | [[Experimentos y Resultados]], [[Cronograma y Plan de Trabajo]] |



