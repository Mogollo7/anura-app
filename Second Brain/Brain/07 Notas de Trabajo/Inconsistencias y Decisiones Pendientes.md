---
title: "Inconsistencias y Decisiones Pendientes"
proyecto: Anura
tipo: nota-de-trabajo
estado: activo
tags: [anura, decisiones, inconsistencias, auditorÃ­a]
---

# Inconsistencias y Decisiones Pendientes

[[Anura â€” Ãndice General]] Â· [[Riesgos del Proyecto]] Â· [[Stack TecnolÃ³gico]] Â· [[Cronograma y Plan de Trabajo]]

> [!abstract] QuÃ© es esto
> Resultado de cruzar todas las fuentes del proyecto â€”el export de Notion, la guÃ­a CVAT en Word y las notas de trabajo originalesâ€” buscando contradicciones entre documentos. Ninguna de estas contradicciones es fatal, pero varias afectan a decisiones que hay que tomar **antes** de escribir cÃ³digo o citar cifras en el documento de grado.
>
> Marcar cada punto como resuelto cuando se decida, y actualizar los documentos afectados.

---

## âœ… Resueltas por el autor

Estas tres eran las de mayor impacto en la lista original. Ya tienen decisiÃ³n firme; se conservan aquÃ­ como registro de por quÃ© se decidiÃ³ asÃ­.

### C-1 (resuelto) Â· Motor vectorial embebido para el mÃ³vil â†’ **ObjectBox**

| | |
| --- | --- |
| **Problema original** | Qdrant es un servidor; no existe librerÃ­a embebible pÃºblica para Android (*Qdrant Edge* sigue en beta privada) |
| **DecisiÃ³n** | **ObjectBox** en el dispositivo (soporte Kotlin/Android de primera clase, HNSW nativo, un solo almacÃ©n para objetos y vectores); Qdrant se mantiene en el servidor |
| **Detalle tÃ©cnico** | ComparaciÃ³n completa contra sqlite-vec y USearch en [[Base Vectorial (SQLite-vec)]] Â§2 |
| **Pendiente** | Validar empÃ­ricamente latencia y memoria en el dispositivo de referencia â€” es una verificaciÃ³n, no una decisiÃ³n abierta |
| **Documentos actualizados** | [[Base Vectorial (SQLite-vec)]], [[Stack TecnolÃ³gico]], [[Riesgos del Proyecto]] (T-2), [[Anura â€” Ãndice General]] |

### C-2 (resuelto) Â· BioCLIP es el Ãºnico backbone del proyecto

| | |
| --- | --- |
| **Problema original** | [[Plan de AcciÃ³n y Arquitectura Conceptual]] proponÃ­a EfficientNet-B0 + Triplet Loss; otros documentos ya asumÃ­an BioCLIP; convivÃ­an sin resolver |
| **DecisiÃ³n del autor** | **BioCLIP siempre** â€” para visiÃ³n y, reutilizando el mismo codificador, tambiÃ©n para audio (el espectrograma se trata como imagen). Se eliminÃ³ la nota "Modelo EfficientNet" de la bÃ³veda |
| **Por quÃ© BioCLIP y no EfficientNet** | Volumen de datos disponible. EfficientNet-B0 se entrena desde cero (o con transfer learning genÃ©rico de ImageNet) y necesita mucho mÃ¡s dato propio por especie para generalizar; BioCLIP ya viene preentrenado sobre TreeOfLife-10M con la jerarquÃ­a taxonÃ³mica incorporada, por lo que rinde bien con los volÃºmenes reales de este proyecto (70 individuos/especie en el prototipo, ver [[Estrategia de ConstrucciÃ³n del Dataset]]) â€” es precisamente el escenario de "pocos datos por clase" para el que BioCLIP fue diseÃ±ado ([[Modelo de VisiÃ³n â€” BioCLIP]] Â§1) |
| **Consecuencia positiva no anticipada** | Al no necesitar un backbone de audio separado, se libera presupuesto de almacenamiento mÃ³vil (RNF-05) y se simplifica la cuantizaciÃ³n a una sola ruta |
| **Detalle tÃ©cnico** | [[Modelo de VisiÃ³n â€” BioCLIP]] Â§8â€“9 (rol en audio + experimento de validaciÃ³n pendiente) |
| **Nota** | "BlockClip", mencionado en [[Notas Originales â€” AÃ±adir Nueva InformaciÃ³n]], no existe como modelo â€” era casi con certeza un error de transcripciÃ³n de BioCLIP; queda confirmado por esta misma decisiÃ³n |
| **Documentos actualizados** | [[Modelo de VisiÃ³n â€” BioCLIP]], [[Arquitectura Multimodal]], [[MÃ©tricas Offline]], [[OptimizaciÃ³n para Inferencia en MÃ³vil]], [[App MÃ³vil]], [[Stack TecnolÃ³gico]], [[Experimentos y Resultados]], [[Anura â€” Ãndice General]] |

### C-4 (resuelto/aclarado) Â· El ~99 % de la Etapa I es legÃ­timo, no fuga de informaciÃ³n

| | |
| --- | --- |
| **Problema original** | Se sospechaba fuga de informaciÃ³n en el resultado alto de la Etapa I (documentado como 95,69 % en el export de Notion) |
| **AclaraciÃ³n del autor** | El resultado real fue **~99 %**, y se sostiene en tres decisiones metodolÃ³gicas ya aplicadas: (1) segmentaciÃ³n binaria individuo-vs-fondo antes de BioCLIP, (2) `GroupSplit` por individuo con 70 individuos Ã— 10 especies, (3) diversidad de individuos en vez de tomas repetidas del mismo ejemplar |
| **Detalle completo** | [[Modelo de VisiÃ³n â€” BioCLIP]] Â§7 |
| **Pendiente real** | No es "verificar si hubo fuga" â€” es **repetir el mismo protocolo riguroso al escalar el catÃ¡logo** y documentar formalmente el modelo de segmentaciÃ³n binaria usado |
| **Documentos actualizados** | [[Modelo de VisiÃ³n â€” BioCLIP]], [[MÃ©tricas Offline]], [[Experimentos y Resultados]], [[Riesgos del Proyecto]] (D-1), [[Anura â€” Ãndice General]] |

### C-5 (resuelto) Â· Backbone on-device: BioCLIP-INT8 descartado, EdgeNeXt-Tiny confirmado

| | |
| --- | --- |
| **Problema encontrado** | La cuantizaciÃ³n INT8 sobre BioCLIP (ViT-B/16) que C-2 y [[Modelo de VisiÃ³n â€” BioCLIP]] Â§6 daban por buena (pesos INT8 + activaciones FP16) fracasÃ³ en pruebas reales: los outliers de atenciÃ³n del ViT destruyen la geometrÃ­a bajo INT8, resultando en ~0,2 % de exactitud â€” inutilizable |
| **DecisiÃ³n del autor (2026-09-08)** | BioCLIP v1 deja de ser el backbone on-device. Se usa **destilaciÃ³n de conocimiento**: BioCLIP v1 como *teacher* (solo en servidor, fine-tuned, soft labels T=4) â†’ **EdgeNeXt-Tiny** como *student* on-device (~2-4M parÃ¡metros, <4 MB), entrenado con **Multi-Head Loss** (cross-entropy paralela Familia+GÃ©nero+Especie + divergencia KL contra el teacher) |
| **Pesos de BioCLIP** | Revisados y con caracterÃ­sticas Ã³ptimas ya definidas para su rol de *teacher* (ViT-B/16, ~86M parÃ¡metros, fine-tuned) â€” cierra la tarea del 06 sep en [[Cronograma y Plan de Trabajo]] |
| **Consecuencia sobre C-2** | La decisiÃ³n "BioCLIP Ãºnico, incl. audio" queda **parcialmente revertida**: BioCLIP sigue siendo el Ãºnico extractor en el *servidor*, pero ya no viaja al dispositivo. La rama de audio pierde su justificaciÃ³n original de "reutilizar el mismo codificador" â€” ver C-7 |
| **BioCLIP full como opciÃ³n de gama alta** | Solo se mantiene como candidato *si* demuestra caber en el presupuesto (latencia/RAM) de un dispositivo de 8 GB RAM, medido con el mismo protocolo que el dispositivo de referencia. Si no cumple, se descarta por completo â€” no solo para gama baja |
| **Dispositivo de referencia confirmado** | **Samsung Galaxy A30 (4 GB RAM)** â€” mÃ­nimo viable, es donde se emula y se miden latencia/RAM/baterÃ­a (cerraba como pendiente en [[OptimizaciÃ³n para Inferencia en MÃ³vil]] Â§5) |
| **Consecuencia en presupuesto** | El presupuesto de 150 MB (RNF-05), calculado para BioCLIP (~85-90 MB) + segmentaciÃ³n, baja a **~15-30 MB** con EdgeNeXt-Tiny (~4 MB) + segmentaciÃ³n â€” libera margen considerable |
| **Documentos afectados** | [[Modelo de VisiÃ³n â€” BioCLIP]], [[Arquitectura Multimodal]], [[OptimizaciÃ³n para Inferencia en MÃ³vil]], [[Anura â€” Ãndice General]] |

### C-6 (resuelto) Â· Motor vectorial local: SQLite (sqlite-vec) reemplaza a ObjectBox

| | |
| --- | --- |
| **DecisiÃ³n anterior (C-1, 2026-09-04)** | ObjectBox como motor vectorial embebido en el mÃ³vil |
| **DecisiÃ³n del autor (2026-09-08)** | **SQLite con extensiÃ³n sqlite-vec** es el motor Ã³ptimo para la nueva arquitectura |
| **JustificaciÃ³n de ingenierÃ­a** | (1) Portabilidad absoluta: un `.sqlite` es un archivo autocontenido â€” descargar un paquete regional es bajar un solo archivo, abrirlo bajo demanda y borrarlo con `file.delete()`; ObjectBox gestiona un almacÃ©n Ãºnico vÃ­a mmap, no estÃ¡ pensado para montar/desmontar bases aisladas en caliente. (2) Consultas hÃ­bridas: metadatos relacionales (taxonomÃ­a) y vectores conviven en la misma base, permitiendo filtrar por regiÃ³n antes de calcular distancia en una sola consulta. (3) Footprint mÃ­nimo (~30 MB) sobre el motor C de SQLite, crÃ­tico para el Galaxy A30 |
| **Modelo operativo confirmado (estilo Merlin)** | El backbone (EdgeNeXt-Tiny) queda **congelado** en el APK; lo que varÃ­a por zona son los **embeddings**, descargados/editados/aplicados como paquetes `.sqlite` independientes por regiÃ³n â€” el mismo patrÃ³n que los paquetes regionales de especies de Merlin Bird ID (Cornell Lab), la referencia de diseÃ±o explÃ­cita del proyecto |
| **Detalle completo** | [[Base Vectorial (SQLite-vec)]] Â§1.1 y Â§2 (revisadas 2026-09-08) |
| **Documentos afectados** | [[Base Vectorial (SQLite-vec)]], [[Stack TecnolÃ³gico]], [[Riesgos del Proyecto]] (T-2), [[Anura â€” Ãndice General]] |

### C-7 (resuelto) Â· Rama de audio: modelo propio dedicado, no reutilizaciÃ³n de backbone

| | |
| --- | --- |
| **OpciÃ³n evaluada** | Reutilizar el backbone EdgeNeXt-Tiny (ya destilado con objetivo estrecho: morfologÃ­a de rana en fotos) sobre mel-espectrogramas, anÃ¡logo a como C-2 proponÃ­a reutilizar BioCLIP |
| **DecisiÃ³n del autor (2026-09-08)** | **Modelo de audio propio y dedicado**, por facilidad de implementaciÃ³n â€” no se reutiliza el backbone visual. Se descarta la ruta de evaluaciÃ³n de transferencia (fine-tuning del backbone congelado sobre espectrogramas) antes de ejecutarla |
| **Por quÃ© es razonable no forzar la reutilizaciÃ³n** | A diferencia de BioCLIP (modelo fundacional con features generales de 10M imÃ¡genes), EdgeNeXt-Tiny fue destilado con un objetivo estrecho â€” el riesgo de mala transferencia a espectrogramas es alto. AdemÃ¡s, el ahorro de MB de reutilizar ya no es crÃ­tico: un modelo de audio dedicado a esta escala (1-3 MB) es tan chico que no compromete el presupuesto total (~15-30 MB del RNF-05 revisado, ver C-5) |
| **Sigue condicionado a** | Confirmar cobertura de dataset de audio (grabaciÃ³n propia o AnuraSet/Xeno-canto) para las 28 especies â€” punto Go/No-Go ya fijado en [[Cronograma y Plan de Trabajo]] para el 18 sep |
| **PatrÃ³n de carga en dispositivo** | Sin cambios: carga perezosa on-demand (solo al grabar), liberaciÃ³n inmediata despuÃ©s â€” ver [[OptimizaciÃ³n para Inferencia en MÃ³vil]] Â§4 |
| **Documentos afectados** | [[Modelo de VisiÃ³n â€” BioCLIP]] Â§8-9, [[Arquitectura Multimodal]] Â§1.2, [[Anura â€” Ãndice General]] |

### C-8 (resuelto) Â· Student on-device: MobileNetV3-Small reemplaza a EdgeNeXt-Tiny

| | |
| --- | --- |
| **DecisiÃ³n anterior (C-5, 2026-09-08)** | EdgeNeXt-Tiny (~2-4M parÃ¡metros) como alumno destilado on-device |
| **DecisiÃ³n del autor (2026-09-11)** | **MobileNetV3-Small** como alumno. El teacher no cambia: sigue siendo BioCLIP v1 (ViT-B/16) en servidor |
| **JustificaciÃ³n** | Soporte maduro en LiteRT/TFLite: MobileNetV3 es una arquitectura de primera clase en el conversor, mientras que EdgeNeXt (con sus bloques de atenciÃ³n por split-channel) es terreno menos probado. Con el pivote de INT8 ya costado una vez (C-5), reducir riesgo de conversiÃ³n pesa mÃ¡s que los ~1-2 MB de diferencia |
| **Confirmado en esta corrida** | `docs_vision_model_plan/` ya especificaba MobileNetV3-Small â€” la contradicciÃ³n con la bÃ³veda queda resuelta a favor de ese documento en este punto concreto |
| **CorrecciÃ³n adicional** | Ese mismo documento cita "BioCLIP v2.5" como teacher: **ese modelo no existe** (solo hay BioCLIP v1 y BioCLIP 2). El teacher es v1, conforme a la decisiÃ³n del 2026-09-05 |
| **DimensiÃ³n del embedding** | Fijada en **512-d**, igual que BioCLIP v1, para que los paquetes regionales `.sqlite` sigan siendo comparables entre servidor y dispositivo (cierra el "por definir" de [[Plan de AcciÃ³n y Arquitectura Conceptual]]) |
| **ImplementaciÃ³n** | `training/train_student.py` (Multi-Head Loss, Î±=0.3, T=4.0, warm-up 5 Ã©pocas AdamW 1e-3 â†’ destilaciÃ³n AdamW 1e-4 con parada temprana) |
| **Documentos afectados** | [[Modelo de VisiÃ³n â€” BioCLIP]], [[OptimizaciÃ³n para Inferencia en MÃ³vil]], [[Cronograma y Plan de Trabajo]] |

### C-9 (resuelto) Â· El entrenamiento de identificaciÃ³n espera al recorte segmentado

| | |
| --- | --- |
| **Problema** | H4 (anotaciÃ³n CVAT) no llegÃ³ el 09 sep, asÃ­ que no hay modelo de segmentaciÃ³n y por tanto no hay recortes con mÃ¡scara (variante C del Â§5 de [[Modelo de VisiÃ³n â€” BioCLIP]]) |
| **OpciÃ³n descartada** | Entrenar ya una lÃ­nea base sobre la imagen completa (variante A) para desbloquear la semana 2 |
| **DecisiÃ³n del autor (2026-09-11)** | **Esperar a segmentaciÃ³n.** No se entrena identificaciÃ³n hasta tener los recortes enmascarados |
| **Por quÃ© es defendible** | La variante C es la que sostiene el ~99 % de la Etapa I (C-4). Una cifra obtenida sobre imagen completa no serÃ­a comparable con ese antecedente y habrÃ­a que repetir el entrenamiento entero al llegar las mÃ¡scaras â€” ademÃ¡s de arriesgar *shortcut learning* sobre el sustrato |
| **Consecuencia sobre el cronograma** | Las tareas del 12â€“13 sep (cabezas jerÃ¡rquicas, destilaciÃ³n) quedan **bloqueadas por H4**, no por falta de cÃ³digo. `training/train_student.py` exige `--masks-dir` y se niega a correr sin Ã©l salvo override explÃ­cito |
| **Lo que sÃ­ avanza sin H4** | El manifiesto de `GroupSplit` ya estÃ¡ construido y verificado (`training/manifiesto.json`): 3.258 imÃ¡genes, 1.706 individuos, 0 grupos repartidos entre particiones. Entorno de entrenamiento verificado end-to-end el 2026-09-11: Python 3.13 + PyTorch 2.11+cu128 en `D:\Anura\.venv-train`, CUDA operativa sobre RTX 4050. 30 comprobaciones de humo pasan (`test_cascada.py` 17/17, `test_modelo.py` 13/13 incl. descarga real de BioCLIP v1): alumno MobileNetV3-Small = 2,07M parÃ¡metros (7,89 MB FP32 / 3,95 MB FP16, dentro del presupuesto), embedding 512-d confirmado igual en teacher y student, gradiente de la Multi-Head Loss llega a las 148 capas del alumno, cascada jerÃ¡rquica nunca predice taxonÃ³micamente imposible y respeta el techo de resoluciÃ³n tambiÃ©n a nivel de gÃ©nero |
| **Documentos afectados** | [[Cronograma y Plan de Trabajo]], [[Riesgos del Proyecto]] |

### C-11 (ejecutado y validado, 2026-09-12) Â· Arquitectura definitiva on-device: Transfer Learning + Image Encoder local

| | |
| --- | --- |
| **Decisiones revertidas** | C-5 (INT8 fracasÃ³), C-8 (MobileNetV3 destilado), C-10 (destilaciÃ³n inviable) |
| **DecisiÃ³n del autor (2026-09-11)** | **BioCLIP v1 oficial â†’ Transfer Learning â†’ extraer Image Encoder â†’ ONNX FP16 â†’ instalar en Android localmente** |
| **SeparaciÃ³n modelo/datos** | El encoder (fp16, instalado una vez) y los paquetes regionales (embeddings + metadata por departamento, descargables/actualizables) son componentes separados. Agregar nuevas especies = actualizar paquetes, no re-entrenar el encoder |
| **Flujo on-device (revisado)** | No es solo el encoder: se exportÃ³ el **clasificador completo** (encoder + 3 cabezas familia/gÃ©nero/especie) â€” foto â†’ preprocesamiento 224Ã—224 â†’ ONNX fp16 â†’ probabilidades por especie â†’ combinar con prior GPS (opcional, Â§C-11 mÃ¡s abajo) â†’ resultado. La ruta "embedding + SQLite-vec + Top-K" queda como alternativa para bÃºsqueda por similitud, no como ruta Ãºnica |
| **Cifra proyectada vs. medida** | La proyecciÃ³n original era "~173 MB FP16" â€” **medido: 165,6 MB**, cercano y confirmado empÃ­ricamente, no solo estimado |
| **VerificaciÃ³n obligatoria â€” cumplida y superada** | El criterio pedÃ­a cosine similarity > 0,99 PyTorch vs. ONNX; el resultado real fue **100 % de predicciones Top-1 idÃ©nticas** en 64 imÃ¡genes de validaciÃ³n, diferencia mÃ¡xima de probabilidad de 1,16Ã—10â»Â³ (fp16) |
| **âš ï¸ Discrepancia de alcance a verificar** | Esta entrada original cita "28 especies" (coherente con C-3, el catÃ¡logo oficial del prototipo). **El entrenamiento ejecutado y todo lo documentado en [[Experimentos y Resultados]] y [[OptimizaciÃ³n para Inferencia en MÃ³vil]] usa 41 especies** (incluye especies fuera de las 28 originales, ej. `Sachatamia_electrops` con soporte parcial). Verificar con el autor si el catÃ¡logo de 28 quedÃ³ ampliado a 41, o si el checkpoint actual excede el alcance del prototipo y debe recortarse antes de integrar en la app |
| **BioCLIP v1 estado** | âœ… Descargado en cachÃ©: `C:\Users\user\.cache\huggingface\hub\models--imageomics--bioclip` (570.87 MB, commit `ce901ab3`) |
| **Cuando re-entrenar** | Solo si la discriminaciÃ³n entre especies similares es insuficiente; agregar especies o coordenadas no exige re-entrenamiento |
| **ExtensiÃ³n no contemplada en la decisiÃ³n original: prior geogrÃ¡fico** | Se aÃ±adiÃ³ y validÃ³ un prior bayesiano simple usando GPS (+15 a +25 pp de Top-1, segÃºn distancia a datos conocidos) â€” no estaba en el diseÃ±o de C-11, se descubriÃ³ como oportunidad durante la validaciÃ³n. Detalle en [[OptimizaciÃ³n para Inferencia en MÃ³vil]] Â§6 |
| **Documentos afectados** | [[Cronograma y Plan de Trabajo]], [[Modelo de VisiÃ³n â€” BioCLIP]], [[Arquitectura Multimodal]], [[OptimizaciÃ³n para Inferencia en MÃ³vil]], [[Experimentos y Resultados]] |

### C-12 (parcial, 2026-09-12) Â· Dispositivo de prueba actualizado: Redmi Note 13 Pro+

| | |
| --- | --- |
| **DecisiÃ³n anterior (parte de C-5, 2026-09-08)** | Samsung Galaxy A30 (4 GB RAM) como dispositivo de referencia mÃ­nimo |
| **Contexto del cambio** | C-5 fijÃ³ el Galaxy A30 pensando en la arquitectura destilada (EdgeNeXt-Tiny / MobileNetV3-Small, <15 MB de modelo). Esa arquitectura fue descartada por C-10; la vigente (C-11) pesa 165,6 MB en disco y usa ~405 MB de RAM en ejecuciÃ³n â€” mucho mÃ¡s que el presupuesto original de esa nota |
| **DecisiÃ³n del autor (2026-09-12)** | **Redmi Note 13 Pro+** como dispositivo de prueba para la arquitectura C-11 |
| **Estado de la validaciÃ³n** | ðŸŸ¡ **Parcial** â€” se emulÃ³ la gama de chip variando `intra_op_num_threads` (1/2/4 hilos) sobre hardware de desarrollo (PC), no sobre el Redmi fÃ­sico. RAM medida (~405 MB) y latencia (150-400 ms) son representativas del comportamiento del modelo, pero **no sustituyen una mediciÃ³n en el dispositivo real** (ARM real, throttling tÃ©rmico, RAM compartida con el resto del sistema Android/HyperOS) |
| **Pendiente real** | Repetir la mediciÃ³n de Â§5 de [[OptimizaciÃ³n para Inferencia en MÃ³vil]] directamente en el Redmi Note 13 Pro+ una vez exista un build de Android que cargue el ONNX; confirmar variante de RAM exacta del dispositivo fÃ­sico disponible (existen versiones de 8 GB y 12 GB) |
| **Â¿El Galaxy A30 queda descartado?** | No necesariamente â€” si la arquitectura on-device vuelve a cambiar (por ejemplo, si se retoma la destilaciÃ³n con la variante C segmentada, segÃºn deja abierto C-10), el Galaxy A30 podrÃ­a volver a ser el piso de referencia. Por ahora, para C-11, el dispositivo de prueba es el Redmi Note 13 Pro+ |
| **Documentos afectados** | [[OptimizaciÃ³n para Inferencia en MÃ³vil]] Â§5, Â§7 |

### C-15 (FIRMADA, 2026-09-13) Â· Ruta de producciÃ³n FINAL para 27 sep: k-NN + SQLite-vec (Ruta B, Merlin style) â€” NO clasificaciÃ³n directa

| | |
| --- | --- |
| **DecisiÃ³n del autor (2026-09-13)** | **Ruta B (k-NN + paquetes regionales SQLite-vec)** es el flujo de producciÃ³n para cumplir requerimientos â€” imita explÃ­citamente el patrÃ³n de Merlin Bird ID (Cornell Lab). El clasificador completo ONNX (encoder+3 cabezas, Ruta A) queda como alternativa tÃ©cnica, no como ruta primaria |
| **âœ… ComparaciÃ³n empÃ­rica DEFINITIVA (EXP-015, paquete regional real de Antioquia)** | Con el paquete filtrado a las 25 especies con presencia real en Antioquia (no las 41 completas): **Ruta B (k-NN k=5): 66,2 % Top-1 / 83,7 % Top-3. Ruta A (clasificador, mismo subconjunto de 467 imÃ¡genes de test): 54,4 % Top-1 / 79,9 % Top-3. Î” = +11,8 pp a favor de Ruta B.** La mediciÃ³n previa (EXP-014, paquete con las 41 especies completas) daba âˆ’0,7 pp â€” el resultado se **invierte** al filtrar por regiÃ³n: el clasificador de 41 clases desperdicia probabilidad en 16 especies que no viven en Antioquia; el k-NN sobre el paquete regional nunca compite contra ellas. Detalle en [[Experimentos y Resultados]] EXP-014/EXP-015 |
| **Artefactos de producciÃ³n (firmados, 27 sep) â€” TODOS generados y validados** | 1. **`encoder_anura_fp16.onnx`** (165,4 MB, exportado 2026-09-13, similitud coseno 0,999999 vs. PyTorch en 64 imÃ¡genes reales) 2. **`antioquia_v1.sqlite`** (6,39 MB, 2.073 vectores, 25 especies reales â€” ver fila siguiente) 3. `vocabulario.json` 4. `prior_geografico_movil.json` |
| **Flujo FINAL de inferencia on-device (k-NN)** | Foto â†’ resize 224Ã—224 â†’ encoder ONNX fp16 â†’ embedding 512-d â†’ k-NN (k=5) en paquete `.sqlite` activo â†’ voto ponderado por similitud â†’ devolver especie + N ejemplares similares como evidencia |
| **Paquete SQLite-vec de Antioquia REAL, generado y medido (2026-09-13)** | `bioclip/paquetes_regionales/antioquia_v1.sqlite` â€” 6,39 MB, 2.073 vectores, **25/41 especies** filtradas por presencia geogrÃ¡fica real (â‰¥3 observaciones de train dentro del bbox del departamento, usando coordenadas ya auditadas de `prior_geografico_movil.json`). Reemplaza al paquete de prueba anterior (`antioquia_prueba_v1.sqlite`, simulado con las 41 especies completas) |
| **Modelo operativo** | Backbone congelado en APK; paquetes regionales descargables/reemplazables por zona (patrÃ³n Merlin Bird ID) |
| **SQLite-vec integraciÃ³n** | âœ… Confirmado funcional en Python (`sqlite_vec` cargable como extensiÃ³n, tabla `vec0` operativa) â€” falta la integraciÃ³n Android nativa (`.so` de sqlite-vec para ARM) |
| **CatÃ¡logo** | Definido por paquete regional activo, NO por modelo (crece sin reentrenar) |
| **âœ… Pendiente de C-15 anterior â€” RESUELTO (2026-09-13)** | El encoder solo existÃ­a Ãºnicamente en `.pt` (PyTorch); ya se exportÃ³ a ONNX fp16 (165,4 MB) siguiendo el mismo patrÃ³n validado en Fase 7 (opset 18, batch fijo=1, consolidaciÃ³n de external data) |
| **ðŸ”´ Pendiente real para Android (14 sep)** | Integrar `sqlite-vec` nativo para Android (librerÃ­a `.so` ARM) y `onnxruntime-android` â€” ambos existen como paquetes publicados, falta la integraciÃ³n Kotlin |
| **Presupuesto APK** | Encoder fp16 165,4 MB + cÃ³digo + runtime sqlite-vec â€” dentro de RNF-05 |
| **ValidaciÃ³n de integridad del encoder ONNX** | âœ… Similitud coseno 0,999999 fp16 vs. PyTorch (64 imÃ¡genes reales de test), 1,000000 en fp32 |
| **Documentos afectados** | [[Base Vectorial (SQLite-vec)]], [[OptimizaciÃ³n para Inferencia en MÃ³vil]], [[Proceso de Crecimiento del CatÃ¡logo Post-Despliegue]], [[Arquitectura Multimodal]], [[Experimentos y Resultados]] |

### C-14 (DESCARTADA, 2026-09-13) Â· Variante C (segmentaciÃ³n binaria previa) no se utilizarÃ¡ en el prototipo del 27 sep

| | |
| --- | --- |
| **Estado** | âŒ **DESCARTADA â€” sin reentrenamiento** |
| **DecisiÃ³n del autor (2026-09-12)** | La variante C (imagen recortada + mÃ¡scara binaria antes de BioCLIP) **no es ruta de producciÃ³n para este sprint**. Se mantiene como trabajo futuro post-27 sep |
| **Por quÃ© se descarta** | DiagnÃ³stico completo en [[Experimentos y Resultados]] (EXP-011/012/013): el segmentador binario entrenado en 9 especies empeora el resultado al escalar a 41 especies (+34 % de ruido en mÃ¡scaras, âˆ’10 pp de Top-1 incluso tras fijar dos bugs). El Ãºnico experimento que podrÃ­a revertir esta decisiÃ³n es **reentrenar Fase 4 desde cero** sobre el recorte con mÃ¡scara (variante C real, con ambos fixes aplicados) â€” pero **cronolÃ³gicamente no cabe en 15 dÃ­as** antes del 27 sep sin parar el desarrollo de Android |
| **Ruta adoptada** | Imagen completa (variante A, sin recorte ni mÃ¡scara) â€” **Top-1 56,8 % fp32 / 56,7 % fp16 + prior GPS +15-25 pp = 81,4 % en sitios conocidos** |
| **QuÃ© abre despuÃ©s del 27 sep** | (1) Reentrenar Fase 4 en variante C real con segmentador binario corregido, para cerrar la pregunta "Â¿mejora si se reentrena?". (2) SegmentaciÃ³n **semÃ¡ntica** (16 etiquetas anatÃ³micas de CVAT) â€” trabajo en curso aparte, distinto del binario, para la evidencia "por quÃ©" del resultado |
| **En tÃ©rminos de riesgo** | Cerrar esta rama ahora **simplifica el MVP**: un modelo, un preprocesamiento, un pipeline. Variante C volverÃ¡ si la evidencia de campo sugiere que hay ganancia de 5-10 pp que justifique ese reentrenamiento |
| **Documentos afectados** | [[Cronograma y Plan de Trabajo]], [[Modelo de VisiÃ³n â€” BioCLIP]], [[Experimentos y Resultados]], [[OptimizaciÃ³n para Inferencia en MÃ³vil]] |

### C-13 (aclaraciÃ³n del autor, 2026-09-12) Â· El fracaso de "variante C" del 11 sep fue con segmentaciÃ³n BINARIA, no semÃ¡ntica â€” y Android arranca el lunes

| | |
| --- | --- |
| **AmbigÃ¼edad que esto resuelve** | El diagnÃ³stico de sprint del 2026-09-12 (ver [[Experimentos y Resultados]]) encontrÃ³ que la corrida de variante C (segmentada) del 11 sep dio peor Top-1 que sin segmentar, sin poder explicar la causa exacta |
| **AclaraciÃ³n del autor** | El modelo usado para producir las mÃ¡scaras de esa corrida era el de **segmentaciÃ³n BINARIA** (individuo vs. fondo â€” el mismo tipo que sostiene el ~99 % de la Etapa I, ver arriba Â§"El ~99% de la Etapa I..."), y **ese fue el que fracasÃ³** al escalar a 41 especies con datos de campo mÃ¡s heterogÃ©neos. No fue un problema de la variante C como concepto, sino especÃ­ficamente de ese segmentador binario en este dataset mÃ¡s amplio |
| **SegmentaciÃ³n SEMÃNTICA (16 etiquetas anatÃ³micas, CVAT)** | Sigue como trabajo en curso, **se retoma cuando sea posible** â€” no es bloqueante para el sprint actual. Es un modelo distinto del binario: divide la imagen en estructuras anatÃ³micas (para la evidencia "por quÃ©" del resultado), no solo separa individuo de fondo |
| **ImplicaciÃ³n para C-9 / el pipeline de identificaciÃ³n** | La decisiÃ³n de "esperar al recorte segmentado antes de entrenar identificaciÃ³n" (C-9) queda en tensiÃ³n: el recorte binario disponible **empeora** el resultado en vez de mejorarlo. La variante A (imagen completa, sin segmentar) sigue siendo la que sostiene todo el trabajo de Fases 4-7 de esta sesiÃ³n â€” no hay, por ahora, evidencia de que valga la pena bloquear el desarrollo esperando un segmentador binario mejor |
| **DiagnÃ³stico completo (2026-09-12, mismo dÃ­a)** | Causa raÃ­z encontrada y confirmada: bug de diseÃ±o en el recorte (bbox de todos los pÃ­xeles marcados, no del componente conexo de la rana) + segmentador entrenado en 9 especies aplicado a 41. Fix aplicado en `fase_4_transfer_learning.py`. **Tras arreglarlo, sigue siendo peor que imagen completa** (60,7 %â†’50,7 % Top-1 en inferencia pareada, 150 imÃ¡genes) â€” porque el modelo de producciÃ³n nunca vio recortes en entrenamiento. Pendiente real: probar si **reentrenar** sobre el recorte arreglado sÃ­ ayuda â€” no descartado, solo sin probar. Detalle en EXP-011/EXP-012, [[Experimentos y Resultados]] Hallazgo 4 |
| **Desarrollo Android** | Arranca el **lunes 14 de septiembre de 2026** â€” 3 dÃ­as despuÃ©s de lo que el cronograma daba por hecho para el cierre de la Semana 1 (Room + Listado funcionando el 11 sep). El desfase es real y debe reflejarse en el resto del cronograma, no absorberse en silencio |
| **Documentos afectados** | [[Experimentos y Resultados]], [[Cronograma y Plan de Trabajo]], [[AutomatizaciÃ³n del Entrenamiento de SegmentaciÃ³n]] |

### ~~C-10 (INVIABLE)~~ Â· DestilaciÃ³n de conocimiento: BioCLIP v1 â†’ MobileNetV3-Small

| | |
| --- | --- |
| **DecisiÃ³n anterior (C-5/C-8)** | Multi-Head Loss (CE + KL con T=4.0, Î±=0.3) para destilar el conocimiento de BioCLIP v1 (teacher, 86M params, ViT-B/16) en MobileNetV3-Small (student, 2,07M params) |
| **Prueba realizada** | Corrida diagnÃ³stica completa: 2.230 imÃ¡genes de entrenamiento, GroupSplit por obs_id, variante A (imagen completa, sin mÃ¡scara). Fases: (1) extracciÃ³n de embeddings BioCLIP, (2) linear probe del teacher (300 Ã©pocas), (3) warm-up del alumno (5 Ã©pocas CE), (4) destilaciÃ³n conjunta (20 Ã©pocas Multi-Head Loss) |
| **Resultado cuantitativo** | **DegradaciÃ³n Top-1: 33,39 puntos** (teacher 57,7% â†’ student 24,3%). Objetivo estÃ¡ndar para destilaciÃ³n: <10 puntos. Esto es **inviable**. |
| **AnÃ¡lisis** | (1) Coherencia taxonÃ³mica: 79,7% vs 83,4% (apenas 3,6 puntos) â€” el alumno aprendiÃ³ la estructura jerÃ¡rquica. (2) Cascada: 43,6% affirmed at especie, 29,9% gÃ©nero, 26,5% familia â€” el alumno estÃ¡ degradando con gracia, no mintiendo. (3) Problema real: el alumno **no aprendiÃ³ a discriminar especies dentro de gÃ©nero** â€” dicho de otro modo, no puede hacer la distinciÃ³n fina que BioCLIP hace. |
| **Causa probable** | (1) AsimetrÃ­a fundamental: el teacher se entrenÃ³ sobre millones de imÃ¡genes biolÃ³gicas ya viendo ranas; el alumno entrena su backbone completo desde ImageNet en 2.230 imÃ¡genes donde la rana ocupa ~10% del encuadre. (2) Variante A (imagen completa) es intrÃ­nsecamente mÃ¡s dura â€” la rana es un objeto pequeÃ±o en un fondo ruidoso, y el alumno tiene que aprender "esto es una rana" Y "cuÃ¡l rana" al mismo tiempo desde hojarasca. BioCLIP ya resolviÃ³ (1), solo necesita resolver (2). (3) DestilaciÃ³n se diseÃ±Ã³ para pasos incremÃ©ntales (5-10 puntos), no para cerrar un gap de esta magnitud. |
| **DecisiÃ³n del autor (2026-09-11)** | **DestilaciÃ³n es inviable.** No se continuarÃ¡n entrenamientos por esta ruta. |
| **Consecuencia** | Se descarta C-5 y C-8 completamente. El backbone on-device ya no es MobileNetV3-Small destilado; la arquitectura on-device queda **por decidir**. Opciones: (A) BioCLIP v1 cuantizado mÃ¡s agresivo (INT4, trade-off latencia vs. precisiÃ³n), (B) backbone de propÃ³sito especÃ­fico entrenado desde cero sin destilaciÃ³n (tiempo de GPU, riesgo de falta de convergencia antes del 27 sep), (C) aceptar que la variante A diagnÃ³stica aquÃ­ requerÃ­a segmentaciÃ³n para cerrar el gap â€” lo que C-9 ya asumÃ­a |
| **Lo que SÃ se mantiene** | Multi-Head Loss y cascada jerÃ¡rquica son vÃ¡lidos **cuando se tienen datos de entrada de calidad** (variante C con segmentaciÃ³n); el problema no es la pÃ©rdida ni la cascada, es que la imagen completa no da seÃ±al clara suficiente. La prueba de esto es que la coherencia taxonÃ³mica se transfiere bien (79,7 vs 83,4). |
| **Blocker real** | No es "destilaciÃ³n no funciona" â€” es "sin segmentaciÃ³n, ni el teacher LLegÃ³ a 57,7%, el punto de partida es mucho mÃ¡s bajo". La variante A diagnÃ³stica aquÃ­ mide ambos modelos en condiciones desfavorables pero medibles. **La decisiÃ³n correcta es esperar H4 y re-evaluar con variante C segmentada.** |
| **Documentos afectados** | [[Cronograma y Plan de Trabajo]] (destilaciÃ³n bloqueada hasta H4), [[Modelo de VisiÃ³n â€” BioCLIP]], [[OptimizaciÃ³n para Inferencia en MÃ³vil]], [[Riesgos del Proyecto]] (nuevo riesgo: arquitectura on-device aÃºn indefinida sin destilaciÃ³n) |

---

## ðŸ”´ CrÃ­ticas â€” bloquean implementaciÃ³n

### C-3 (resuelto) Â· NÃºmero de especies: seis cifras distintas â†’ **28 especies** para el catÃ¡logo del prototipo

| Fuente | Cifra |
| --- | --- |
| [[IntroducciÃ³n y JustificaciÃ³n]] | 15 especies, ~70 fotografÃ­as por especie |
| [[Estrategia de ConstrucciÃ³n del Dataset]] â€” Etapa I | 14 especies en el texto (**la cifra confirmada por el autor y por la tabla de resultados es 10**) |
| [[Notas Originales â€” SegmentaciÃ³n SemÃ¡ntica y MetodologÃ­a Anura]] | 23 especies |
| [[Listado de Individuos y Arreglo TaxonÃ³mico]] | ~30 filas |
| [[GuÃ­a CVAT â€” Ãndice\|GuÃ­a CVAT]] | atributo `especie` con 30 opciones; Anexo C con 28 fichas |
| RNF-04 ([[Objetivos y Alcance]]) | "las 50 especies seleccionadas" |

| | |
| --- | --- |
| **DecisiÃ³n (2026-09-05)** | El catÃ¡logo oficial del prototipo es de **28 especies**. Coincide exactamente con las 28 carpetas de recolecciÃ³n de campo ya organizadas por `equipo 1/2/3` y con las 28 opciones reales del atributo `especie` en `anuro_labels.json` (30 valores del selector menos los dos placeholders `otra_no_listada` y 
o_determinable`) |
| **RNF-04 ("50 especies")** | Queda como **meta de largo plazo** (Etapa III de [[Escalabilidad]] Â§4), no como el catÃ¡logo de este prototipo â€” corregir la redacciÃ³n del RNF-04 en el documento de grado para no prometer 50 en la evaluaciÃ³n del 27 de septiembre |
| **RecolecciÃ³n de las 70 muestras/especie** | MÃ©todo ya en marcha: recolecciÃ³n de campo distribuida en tres equipos (`equipo 1`, `equipo 2`, `equipo 3`) por especie/regiÃ³n, unificada a JPG con `unificar_para_cvat.py` (RAW y otros formatos â†’ JPG homogÃ©neo para CVAT). Las especies que no lleguen a 70 individuos propios se completan con iNaturalist/GBIF filtrado por calidad y coordenadas verificables ([[Estrategia de ConstrucciÃ³n del Dataset]]) |
| **Pendiente real** | Confirmar, especie por especie, cuÃ¡les de las 28 ya tienen â‰¥ 70 individuos y cuÃ¡les necesitan complemento de fuente secundaria â€” tarea de la semana 1 del sprint ([[Cronograma y Plan de Trabajo]] Â§0) |
| **Documentos afectados** | [[Estrategia de ConstrucciÃ³n del Dataset]], [[Objetivos y Alcance]] (RNF-04), [[Cronograma y Plan de Trabajo]], [[Anura â€” Ãndice General]] |

---

## ðŸŸ¡ Importantes â€” afectan a coherencia del documento

### I-1 Â· Roboflow vs. CVAT

Las [[Notas Originales â€” MÃ©todo de AnotaciÃ³n y Plantillas TaxonÃ³micas|notas originales]] y la [[GuÃ­a de AnotaciÃ³n Roboflow (histÃ³rico)|guÃ­a de anotaciÃ³n de Notion]] describen el flujo en **Roboflow**; la [[GuÃ­a CVAT â€” Ãndice|guÃ­a CVAT v1.0]] describe el flujo definitivo en **CVAT**. La propia nota del autor lo dice: *"todo quedÃ³ para CVAT, en la guÃ­a CVAT quedÃ³ todo lo final"*.

**Resuelto en esta bÃ³veda:** la guÃ­a CVAT es la fuente vigente; el material de Roboflow queda marcado como histÃ³rico. Falta actualizar las menciones a Roboflow en los documentos que irÃ¡n al trabajo escrito.

### I-2 Â· NÃºmero de clases anatÃ³micas: 8 / 13 / 16 / 18

| Fuente | Clases |
| --- | --- |
| [[GuÃ­a de AnotaciÃ³n Roboflow (histÃ³rico)]] | 8 (IDs 0â€“7) |
| [[Notas Originales â€” MÃ©todo de AnotaciÃ³n y Plantillas TaxonÃ³micas]] | 13 regiones principales |
| [[GuÃ­a CVAT â€” Ãndice\|GuÃ­a CVAT v1.0]] | **16 etiquetas** âœ… vigente |
| [[Notas Originales â€” SegmentaciÃ³n SemÃ¡ntica y MetodologÃ­a Anura]] | 18 regiones anatÃ³micas |

**Propuesta:** 16 etiquetas de la guÃ­a CVAT es el esquema vigente. Documentar la evoluciÃ³n 18 â†’ 13 â†’ 16 como decisiÃ³n metodolÃ³gica (la reducciÃ³n tiene sentido: no todas las regiones son anotables de forma fiable).

### I-3 Â· SegmentaciÃ³n semÃ¡ntica vs. instancia, y quÃ© modelo

Los [[Objetivos y Alcance|objetivos]] dicen "segmentaciÃ³n semÃ¡ntica basada en **YOLO**", pero YOLO-seg hace segmentaciÃ³n **de instancias**. AdemÃ¡s el RF-03 exige distinguir varios individuos en una imagen, lo cual **requiere** instancias, no segmentaciÃ³n semÃ¡ntica.

**Propuesta:** el tÃ©rmino correcto para lo que necesita Anura es *segmentaciÃ³n de instancias con partes anatÃ³micas*. Ajustar la redacciÃ³n en el documento; es un detalle terminolÃ³gico que un jurado tÃ©cnico notarÃ¡.

### I-4 (resuelto) Â· MP3 permitido en requisitos, prohibido en la metodologÃ­a

- **RF-01.2**: "carga/grabaciÃ³n de archivos de audio (WAV, **MP3**)"
- **[[Estrategia de ConstrucciÃ³n del Dataset]]**: "Evita MP3 o AAC, ya que la compresiÃ³n psicoacÃºstica descarta armÃ³nicos finos"

**DecisiÃ³n (2026-09-05):** formato Ã³ptimo = **WAV / PCM 16-bit, 44,1 kHz, mono** â€” es el Ãºnico exigido para la grabaciÃ³n propia de la app y para todo el material de entrenamiento/calibraciÃ³n. MP3 se acepta **Ãºnicamente** en la carga de archivos ya existentes del usuario, con una advertencia visible de que puede degradar la precisiÃ³n del anÃ¡lisis bioacÃºstico.

### I-5 (resuelto) Â· Individuos por especie: 70 vs. 20/30/40

La estrategia de dataset exige **mÃ­nimo 70 individuos por especie**; las notas originales hablan de 20 (mÃ­nimo) / 30 (recomendado) / 40+ (excelente) para el segmentador. AdemÃ¡s, 550 imÃ¡genes originales de train no son compatibles con 70 individuos Ã— 30 especies.

**Confirmado por el autor (2026-09-05):** son, en efecto, requisitos de **dos modelos distintos**, tal como proponÃ­a la aclaraciÃ³n probable â€” **70 individuos/especie** para el modelo de identificaciÃ³n (28 especies, cumplido), y **25â€“30 imÃ¡genes/especie** para el modelo de segmentaciÃ³n anatÃ³mica, dentro del rango 20â€“40 previsto aquÃ­ para el segmentador universal. Las 550 imÃ¡genes son las anotadas para segmentaciÃ³n, no el total del dataset. No era una contradicciÃ³n â€” eran dos datasets con dos requisitos de volumen distintos, ya reflejado en [[Estrategia de ConstrucciÃ³n del Dataset]] y [[Riesgos del Proyecto]] (D-3).

### I-6 (resuelto) Â· "Anura" vs. "Anuro", y Notion como fuente

El proyecto se llama **Anura** en Notion y en el documento; la guÃ­a CVAT usa **Anuro** (proyecto, equipo, workspace). *Anura* es taxonÃ³micamente el nombre del orden y el que aparece en los objetivos.

**DecisiÃ³n (2026-09-05):** el nombre del producto es **Anura**, sin excepciÃ³n en documentaciÃ³n nueva. "Anuro" queda **solo** donde ya existe creado dentro de CVAT (nombre de proyecto/equipo/workspace de la herramienta) â€” no se renombra ahÃ­, no vale la pena el costo de migraciÃ³n. AdemÃ¡s, el **proyecto de Notion queda deprecado como fuente**: es historia vieja, ya migrada a esta bÃ³veda. De aquÃ­ en adelante, **esta bÃ³veda de Obsidian es la Ãºnica fuente de verdad**; no se vuelve a consultar Notion para decisiones nuevas. Las notas que citan "fuente: Notion" (p. ej. [[Plan de AcciÃ³n y Arquitectura Conceptual]], [[Estrategia de ConstrucciÃ³n del Dataset]]) se conservan como registro histÃ³rico de dÃ³nde vino el contenido, no como indicaciÃ³n de que Notion siga activo.

### I-7 (resuelto) Â· NumeraciÃ³n de historias de usuario

En [[Historias de Usuario]], el diagrama mencionaba **HU-06 (ExportaciÃ³n DwC)** mientras la tabla resumen asignaba esa funciÃ³n a **HU-05**, y la fila de HU-05 se referenciaba a sÃ­ misma como entrada.

**Corregido (2026-09-05):** no existe HU-06 â€” el diagrama de [[Historias de Usuario]] ya quedÃ³ actualizado a **HU-05: ExportaciÃ³n DwC**, coherente con la tabla resumen y con la secciÃ³n HU-05 completa del documento.

---

## ðŸŸ¢ Menores â€” precisiÃ³n terminolÃ³gica

| #   | Punto                                                                                              | CorrecciÃ³n                                                                                                                                                                                                                                                                                   |
| --- | -------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| M-1 | "TensorFlow Lite" (RF-12)                                                                          | Desde 2024 se llama **LiteRT**; dependencia `com.google.ai.edge.litert`                                                                                                                                                                                                                      |
| M-2 | "Core ML/TFLite" en las notas                                                                      | Core ML es exclusivo de iOS; el alcance es Android â†’ LiteRT/ONNX                                                                                                                                                                                                                             |
| M-3 | Cifra de especies de Colombia                                                                      | Se cita 911; conviene verificar contra la fuente vigente de *Amphibian Species of the World* / SiB Colombia y fechar el dato                                                                                                                                                                 |
| M-4 | "EfficientNet... escalamiento equilibrado" atribuido a BioCLIP en [[IntroducciÃ³n y JustificaciÃ³n]] | El escalado compuesto es de EfficientNet, no de BioCLIP. Corregir esa frase: describe una arquitectura y cita otra                                                                                                                                                                           |
| M-5 | Bases de datos vacÃ­as en Notion                                                                    | Cuatro CSV referenciados no tienen contenido: *Estrategia de organizaciÃ³n del Dataset*, *Estrategia de Manejo de ImÃ¡genes*, *Estrategia de Manejo de Audio*, *Manejo de clases desconocidas*. El contenido estÃ¡ en el cuerpo del documento; los enlaces vacÃ­os se eliminaron en la migraciÃ³n |

> [!note] M-4 conviene revisarlo con calma
> La frase de la justificaciÃ³n describe el escalado compuesto de profundidad/anchura/resoluciÃ³n â€”que es la aportaciÃ³n de EfficientNetâ€” y lo atribuye a BioCLIP citando a Stevens et al. Es el tipo de error que un jurado detecta y que resta credibilidad al marco teÃ³rico, aunque el resto estÃ© bien construido. Con EfficientNet ya fuera de la arquitectura (C-2), esta frase queda todavÃ­a mÃ¡s fuera de lugar: describe una arquitectura que el proyecto ni siquiera usa.

---

## Decisiones a cerrar

| # | DecisiÃ³n | Responsable | Fecha lÃ­mite | Estado |
| --- | --- | --- | --- | --- |
| ~~1~~ | ~~Motor vectorial en el dispositivo~~ (C-1) | | | âœ… ObjectBox |
| ~~2~~ | ~~Backbone principal~~ (C-2) | | | ðŸŸ¡ Revisado por C-5: BioCLIP Ãºnico **en servidor** (teacher); on-device es EdgeNeXt-Tiny destilado |
| 3 | NÃºmero oficial de especies por etapa (C-3) | | | ðŸ”´ |
| ~~4~~ | ~~Reevaluar Etapa I~~ (C-4) | | | âœ… Confirmado ~99 %, sin fuga |
| ~~5~~ | ~~VersiÃ³n de BioCLIP (v1 vs. v2) y coherencia mÃ³vil/servidor~~ | | 2026-09-05 | âœ… **v1 en ambos lados** para el sprint del prototipo (matiz: "ambos lados" ahora significa servidor + teacher de destilaciÃ³n, no el mÃ³vil directamente â€” ver C-5) |
| 6 | Qdrant vs. pgvector en el servidor | | | ðŸ”´ |
| 7 | Modelo de segmentaciÃ³n concreto | | | ðŸŸ¡ Ultralytics YOLO-seg como base de trabajo â†’ [[AutomatizaciÃ³n del Entrenamiento de SegmentaciÃ³n]]; tamaÃ±o exacto (n/s) por confirmar con datos reales |
| ~~8~~ | ~~Alcance mÃ­nimo defendible (riesgo P-1)~~ | | 2026-09-05 | âœ… Alcance mÃ­nimo **del prototipo al 27 sep** fijado â†’ [[Cronograma y Plan de Trabajo]] Â§0; el alcance mÃ­nimo defendible del trabajo de grado completo (con piloto de campo y documento) sigue abierto y se decide por separado |
| ~~9~~ | ~~Backbone on-device tras fracaso de INT8~~ (C-5) | | 2026-09-08 | âœ… EdgeNeXt-Tiny destilado, Multi-Head Loss |
| ~~10~~ | ~~Motor vectorial local~~ â€” revisiÃ³n de C-1 (C-6) | | 2026-09-08 | âœ… SQLite (sqlite-vec), reemplaza ObjectBox |
| ~~11~~ | ~~Rama de audio: reutilizar backbone o modelo propio~~ (C-7) | | 2026-09-08 | âœ… Modelo de audio propio y dedicado |
| ~~12~~ | ~~Student on-device~~ â€” revisiÃ³n de C-5 (C-8) | | 2026-09-11 | âœ… MobileNetV3-Small, embedding 512-d |
| ~~13~~ | ~~Â¿Entrenar lÃ­nea base sin segmentaciÃ³n?~~ (C-9) | | 2026-09-11 | âœ… No: se espera a H4 y a la variante C |
| ~~14~~ | ~~DestilaciÃ³n de BioCLIP â†’ MobileNetV3 como backbone on-device~~ (C-10) | | 2026-09-11 | ðŸ”´ **INVIABLE** â€” degradaciÃ³n Top-1 de 33 puntos (objetivo <10); sin segmentaciÃ³n no hay seÃ±al suficiente; re-evaluar con H4 |
| ~~15~~ | ~~Arquitectura on-device definitiva: Transfer Learning + encoder local~~ (C-11) | | 2026-09-11 | âœ… Ejecutado y validado 2026-09-12 â€” ONNX fp16, 165,6 MB, 100% predicciones idÃ©nticas a PyTorch. Discrepancia de alcance 28 vs. 41 especies pendiente de confirmar |
| 16 | Dispositivo de prueba: Redmi Note 13 Pro+ (C-12) | | 2026-09-12 | ðŸŸ¡ Fijado, mediciÃ³n en emulaciÃ³n de hilos completada; falta medir en el dispositivo fÃ­sico |
| ~~17~~ | ~~Â¿QuÃ© segmentador fallÃ³ el 11 sep â€” binario o semÃ¡ntico?~~ (C-13) | | 2026-09-12 | âœ… Fue el binario (individuo vs. fondo); la semÃ¡ntica (16 etiquetas) sigue en desarrollo aparte |
| 18 | Inicio real de desarrollo Android (C-13) | | 2026-09-12 | ðŸŸ¡ Confirmado para el lunes 14 sep â€” 3 dÃ­as despuÃ©s de lo previsto en el cronograma; falta ajustar el resto de fechas de la Semana 2-3 |

## Registro de decisiones tomadas

| Fecha | DecisiÃ³n | Motivo | Documentos actualizados |
| --- | --- | --- | --- |
| 2026-09-04 | ObjectBox como motor vectorial embebido en el mÃ³vil | Qdrant no puede correr embebido en Android; ObjectBox tiene soporte Kotlin nativo de primera clase | [[Base Vectorial (SQLite-vec)]], [[Stack TecnolÃ³gico]], [[Riesgos del Proyecto]], [[Anura â€” Ãndice General]] |
| 2026-09-04 | BioCLIP como Ãºnico backbone del proyecto (visiÃ³n y audio) | InstrucciÃ³n directa del autor; elimina la contradicciÃ³n con EfficientNet y reduce el presupuesto de almacenamiento mÃ³vil | [[Modelo de VisiÃ³n â€” BioCLIP]], [[Arquitectura Multimodal]], [[MÃ©tricas Offline]], [[OptimizaciÃ³n para Inferencia en MÃ³vil]], [[App MÃ³vil]], [[Stack TecnolÃ³gico]], [[Experimentos y Resultados]], [[Anura â€” Ãndice General]] |
| 2026-09-04 | El ~99 % de la Etapa I se confirma como resultado legÃ­timo | AclaraciÃ³n del autor: segmentaciÃ³n binaria previa + `GroupSplit` por individuo, no fuga de informaciÃ³n | [[Modelo de VisiÃ³n â€” BioCLIP]], [[MÃ©tricas Offline]], [[Experimentos y Resultados]], [[Riesgos del Proyecto]], [[Anura â€” Ãndice General]] |
| 2026-09-05 | Fecha lÃ­mite del prototipo: 27 de septiembre de 2026 | InstrucciÃ³n directa del autor â€” 22 dÃ­as desde hoy para un prototipo funcional desplegado, no el trabajo de grado completo | [[Cronograma y Plan de Trabajo]] (nueva Â§0), [[Roadmap y Fases]], [[Anura â€” Ãndice General]] |
| 2026-09-05 | CatÃ¡logo oficial de 28 especies para el prototipo (C-3) | Coincide con las 28 carpetas de recolecciÃ³n de campo y con `anuro_labels.json`; RNF-04 ("50 especies") pasa a meta de largo plazo | [[Inconsistencias y Decisiones Pendientes]] (C-3), [[Estrategia de ConstrucciÃ³n del Dataset]], [[Anura â€” Ãndice General]] |
| 2026-09-05 | BioCLIP **v1** (ViT-B/16) como Ãºnica versiÃ³n, en dispositivo y en servidor, para este sprint | InstrucciÃ³n directa del autor ("asegurar esta previsiÃ³n"); evita el problema de espacios de embedding incompatibles entre v1 y v2 dentro del plazo de 22 dÃ­as â€” v2 en servidor queda como mejora post-sprint | [[Modelo de VisiÃ³n â€” BioCLIP]], [[Stack TecnolÃ³gico]], [[Inconsistencias y Decisiones Pendientes]] |
| 2026-09-05 | Alcance mÃ­nimo del prototipo (27 sep) fijado explÃ­citamente | Riesgo P-1 exigÃ­a esta conversaciÃ³n antes de que la fecha lÃ­mite la decidiera por defecto | [[Cronograma y Plan de Trabajo]] Â§0, [[Roadmap y Fases]] |
| 2026-09-05 | Cifras reales confirmadas para el prototipo: **70 individuos/especie** (identificaciÃ³n, requisito original cumplido) y **25â€“30 por especie** (subconjunto anotado de segmentaciÃ³n, dentro del rango 20â€“40 de I-5) | InstrucciÃ³n directa del autor â€” corrige una transcripciÃ³n previa de esta misma bÃ³veda que decÃ­a 20/especie para identificaciÃ³n | [[Estrategia de ConstrucciÃ³n del Dataset]], [[Riesgos del Proyecto]] (D-3), I-5 |
| 2026-09-05 | Formato de audio Ã³ptimo confirmado: WAV/PCM 16-bit 44,1 kHz mono; MP3 solo en carga de usuario (I-4) | Cierra la contradicciÃ³n entre RF-01.2 y la metodologÃ­a de dataset | [[Objetivos y Alcance]], [[Estrategia de ConstrucciÃ³n del Dataset]] |
| 2026-09-05 | Notion deprecado como fuente; Obsidian es la Ãºnica fuente de verdad (I-6) | InstrucciÃ³n directa del autor â€” el proyecto de Notion es historia vieja ya migrada | Esta bÃ³veda en su conjunto |
| 2026-09-05 | NumeraciÃ³n de historias de usuario corregida: no existe HU-06, es HU-05 (I-7) | El diagrama y la tabla resumen de [[Historias de Usuario]] ya coincidÃ­an salvo en el diagrama | [[Historias de Usuario]] |
| 2026-09-08 | BioCLIP-INT8 descartado como backbone on-device; EdgeNeXt-Tiny destilado (Multi-Head Loss) confirmado en su lugar (C-5) | INT8 sobre el ViT de BioCLIP fracasÃ³ en pruebas reales (~0,2 % exactitud, outliers de atenciÃ³n) | [[Modelo de VisiÃ³n â€” BioCLIP]], [[Arquitectura Multimodal]], [[OptimizaciÃ³n para Inferencia en MÃ³vil]], [[Anura â€” Ãndice General]] |
| 2026-09-08 | Pesos de BioCLIP v1 revisados, caracterÃ­sticas Ã³ptimas definidas para su rol de teacher (ViT-B/16, ~86M params, fine-tuned) | Cierra la tarea pendiente del 06 sep del sprint | [[Cronograma y Plan de Trabajo]] |
| 2026-09-08 | Dispositivo de referencia mÃ­nimo confirmado: Samsung Galaxy A30 (4GB RAM) (parte de C-5) | InstrucciÃ³n directa del autor â€” es donde se emula y se miden latencia/RAM/baterÃ­a | [[OptimizaciÃ³n para Inferencia en MÃ³vil]] |
| 2026-09-08 | SQLite (sqlite-vec) reemplaza a ObjectBox como motor vectorial local (C-6) | InstrucciÃ³n directa del autor: "lo mÃ¡s Ã³ptimo para la nueva arquitectura" | [[Base Vectorial (SQLite-vec)]], [[Stack TecnolÃ³gico]] |
| 2026-09-08 | Rama de audio: modelo propio y dedicado, no reutilizaciÃ³n del backbone EdgeNeXt-Tiny (C-7) | InstrucciÃ³n directa del autor, por facilidad de implementaciÃ³n; el ahorro de MB de reutilizar ya no es crÃ­tico a esta escala | [[Modelo de VisiÃ³n â€” BioCLIP]], [[Arquitectura Multimodal]] |
| 2026-09-11 | MobileNetV3-Small reemplaza a EdgeNeXt-Tiny como alumno destilado; embedding fijado en 512-d (C-8) | Soporte maduro en LiteRT frente a terreno no probado, tras el coste ya pagado por el fallo de INT8 | [[Modelo de VisiÃ³n â€” BioCLIP]], [[OptimizaciÃ³n para Inferencia en MÃ³vil]] |
| 2026-09-11 | El entrenamiento de identificaciÃ³n espera al recorte segmentado; no se hace lÃ­nea base sobre imagen completa (C-9) | La variante C es la que sostiene el ~99 % de la Etapa I; una cifra sobre imagen completa no serÃ­a comparable y habrÃ­a que repetirla | [[Cronograma y Plan de Trabajo]], [[Riesgos del Proyecto]] |
| 2026-09-11 | `GroupSplit` por `obs_id` real de iNaturalist, con tope de 70 observaciones por especie | El identificador de individuo ya viene en el nombre de archivo del scraper; agrupar por bloques fijos habrÃ­a partido individuos entre particiones | `training/prepare_dataset.py`, `training/manifiesto.json` |
| 2026-09-11 | **DestilaciÃ³n de BioCLIP v1 â†’ MobileNetV3-Small es INVIABLE** (C-10) | Corrida diagnÃ³stica: Top-1 teacher 57,7% â†’ student 24,3% (degradaciÃ³n 33,39 puntos vs. objetivo <10). Causa: sin segmentaciÃ³n (variante A), la imagen completa no proporciona seÃ±al clara suficiente para que el alumno pequeÃ±o cierre el gap. La coherencia taxonÃ³mica (79,7 vs 83,4) se transfiere bien, pero la discriminaciÃ³n fina de especie no. La prueba de que el problema es la entrada, no el algoritmo: esperar a H4 y re-evaluar con variante C segmentada. | [[Cronograma y Plan de Trabajo]], [[Modelo de VisiÃ³n â€” BioCLIP]], [[OptimizaciÃ³n para Inferencia en MÃ³vil]], [[Riesgos del Proyecto]] (nueva incertidumbre: arquitectura on-device aÃºn por decidir) |
| 2026-09-11 | **Nueva arquitectura on-device: BioCLIP v1 oficial â†’ Transfer Learning â†’ Image Encoder â†’ ONNX FP16 â†’ Android local** (C-11) | C-5 a C-10 (destilaciÃ³n) descartados. El encoder visual se extrae del BioCLIP v1 entrenado en Anura, no se crea desde cero ni se usa encoder de terceros. El modelo (~173 MB) se instala localmente en el dispositivo; los paquetes regionales (embeddings + metadata por departamento) se descargan por separado, sin necesidad de re-entrenar el modelo para agregar nuevas especies. | [[Cronograma y Plan de Trabajo]], [[Modelo de VisiÃ³n â€” BioCLIP]], [[Arquitectura Multimodal]], [[OptimizaciÃ³n para Inferencia en MÃ³vil]] |
| 2026-09-12 | C-11 ejecutado: clasificador completo exportado a ONNX fp16 (165,6 MB), validado con 100% de predicciones idÃ©nticas a PyTorch. Se probaron y descartaron int8 dinÃ¡mico y estÃ¡tico (3 configuraciones) â€” confirman de forma independiente el fracaso de INT8 ya visto en C-5 | Necesidad de reducir tamaÃ±o de despliegue sin perder precisiÃ³n; int8 resultÃ³ inviable en todas las variantes probadas para un ViT sin *quantization-aware training* | [[OptimizaciÃ³n para Inferencia en MÃ³vil]], [[Experimentos y Resultados]] |
| 2026-09-12 | Prior geogrÃ¡fico (GPS) aÃ±adido como componente del sistema: +15 a +25 pp de Top-1 segÃºn distancia a datos de entrenamiento conocidos | Descubierto durante la validaciÃ³n de C-11; no estaba contemplado en el diseÃ±o original, pero es la mejora individual mÃ¡s grande medida en todo el proyecto | [[OptimizaciÃ³n para Inferencia en MÃ³vil]] Â§6, [[Experimentos y Resultados]] |
| 2026-09-12 | Dispositivo de prueba actualizado a Redmi Note 13 Pro+, reemplazando al Galaxy A30 para la arquitectura C-11 (C-12) | El Galaxy A30 (4GB) fue fijado para la arquitectura destilada (<15MB), descartada por C-10; la arquitectura vigente pesa 165,6MB y usa ~405MB de RAM, requiriendo un dispositivo con mÃ¡s margen | [[OptimizaciÃ³n para Inferencia en MÃ³vil]] Â§5, Â§7 |
| 2026-09-12 | Aclarado: el segmentador que fallÃ³ el 11 sep (variante C peor que A) fue el **binario** (individuo vs. fondo); la segmentaciÃ³n **semÃ¡ntica** (16 etiquetas) sigue en desarrollo, se retoma cuando sea posible. Desarrollo Android confirmado para el **lunes 14 sep** (C-13) | InstrucciÃ³n directa del autor, resuelve la ambigÃ¼edad seÃ±alada en el diagnÃ³stico de sprint del mismo dÃ­a | [[Experimentos y Resultados]], [[Cronograma y Plan de Trabajo]] |



