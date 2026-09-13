# Plan del Modelo de Visión (y Audio) — Anura
### Versión corregida 2026-09-10 — basada en la bóveda de Obsidian (fuente única de verdad)

> [!danger] Por qué esta versión reemplaza por completo a la anterior
> La versión previa de este documento se escribió a partir de 8 Google Docs sueltos (ahora en `docs_vision_model_plan/`), documentos **anteriores y menos autoritativos** que una bóveda de Obsidian ya existente en `D:\Anura\Second Brain\Brain\` (45+ notas interconectadas). La propia bóveda lo dice explícitamente en `07 Notas de Trabajo/Inconsistencias y Decisiones Pendientes.md` (decisión I-6, 2026-09-05): **"esta bóveda de Obsidian es la única fuente de verdad; no se vuelve a consultar Notion para decisiones nuevas"** — y por extensión, tampoco los Google Docs, que son historia previa a esta consolidación. Esta versión transcribe las decisiones **ya tomadas** en la bóveda, no las reabre.

---

## 0. Qué estaba mal en el plan anterior

| # | Error del plan anterior | Corrección, con respaldo en la bóveda |
| --- | --- | --- |
| 1 | Asumía **MobileNetV3-Small** como red *alumno* de la destilación, y trataba "EdgeNeXt-Tiny / MobileNetV3-Small / fine-tuning directo" como una decisión todavía abierta | La decisión **ya está cerrada** (C-5, 2026-09-08): el *student* on-device es **EdgeNeXt-Tiny** (~2-4M parámetros, <4 MB). MobileNetV3-Small no aparece en ningún documento de la bóveda como candidato vigente — es un residuo de un Google Doc desactualizado. Ver [[Modelo de Visión — BioCLIP]] §6 (aviso) y [[Inconsistencias y Decisiones Pendientes]] C-5. |
| 2 | Presentaba el proyecto como si no existiera ningún modelo entrenado, partiendo de cero | La **Etapa I ya se ejecutó** y obtuvo **~99 % de exactitud real** (no 95,69 %, cifra con error de transcripción) sobre 10 especies × 70 individuos, con segmentación binaria individuo-vs-fondo antes de BioCLIP + `GroupSplit` por individuo — verificado sin fuga de información (C-4, [[Modelo de Visión — BioCLIP]] §7). El trabajo pendiente es **escalar el protocolo ya probado**, no inventarlo. |
| 3 | No mencionaba el modelo de segmentación como pieza separada con decisión propia | Existe una **decisión cerrada** (tabla "Decisiones a cerrar" #7): el segmentador anatómico universal usa **Ultralytics YOLO-seg** como base de trabajo, con pipeline de entrenamiento automatizado ya diseñado en [[Automatización del Entrenamiento de Segmentación]]. Es un modelo aparte del de identificación, con su propio dataset (25-30 img/especie, universal, no por especie). |
| 4 | Reducía el sistema a "solo clasificación" | El pipeline real, documentado en [[Pipeline del Sistema]], tiene **cuatro fuentes de evidencia en paralelo** tras la extracción de características: clasificación jerárquica, búsqueda vectorial, atributos morfológicos vs. plantilla, y contexto geográfico — que luego se funden (late fusion) y pasan por verificación open-set antes de la salida explicable al usuario. |
| 5 | Inventaba fechas de fases (Fase 0 a Fase 4, "17 días") sin conocer el cronograma real | Existe un cronograma día a día ya fijado en [[Cronograma y Plan de Trabajo]] §0, con hitos H1-H11 hasta el 27 sep y un punto explícito de Go/No-Go de audio el **18 de septiembre**. Este documento usa esas fechas, no fechas nuevas. |
| 6 | (Consecuencia de 1) Calculaba presupuesto de almacenamiento ~150 MB asumiendo BioCLIP completo on-device | El presupuesto revisado (C-5) es **~15-30 MB total** para los tres modelos (segmentación + EdgeNeXt-Tiny + audio dedicado), porque BioCLIP ya no viaja al dispositivo. |
| 7 | Usaba ObjectBox como motor vectorial local, dado por hecho en algunos de los 8 docs | Esa decisión (C-1, 2026-09-04) fue **revertida** el 2026-09-08 (C-6): el motor vectorial local vigente es **SQLite + sqlite-vec**, patrón "estilo Merlin Bird ID". |

---

## 1. Arquitectura vigente (decisiones ya cerradas, no abiertas)

### 1.1 Panorama en una imagen

```
                        📷 CAPTURA
              imagen(es) + audio? + GPS/altitud/fecha
                             │
                             ▼
  1. PREPROCESADO — persistir ANTES de inferir (RNF-11)
                             │
                             ▼
  2. SEGMENTACIÓN ANATÓMICA — Ultralytics YOLO-seg (modelo universal, 16 etiquetas)
     Decisión #7 en "Decisiones a cerrar" → Automatización del Entrenamiento de Segmentación
                             │  ¿hay anuro?
                    ┌────────┴────────┐
                   no                 sí
        "No se detectó un anuro"       ▼
                        3. EXTRACCIÓN DE CARACTERÍSTICAS
                        recorte segmentado → EdgeNeXt-Tiny (on-device)
                        [en servidor: BioCLIP v1 ViT-B/16, teacher/fine-tuned]
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        ▼                     ▼                      ▼                  ▼
 4a. CLASIFICACIÓN     4b. BÚSQUEDA         4c. ATRIBUTOS       4d. CONTEXTO
   jerárquica            VECTORIAL           morfológicos        geográfico
 Familia→Género→        sqlite-vec local    por región vs.      GPS, altitud,
   Especie              (paquete regional,  plantilla especie   fecha, hábitat
   (Multi-Head Loss)     estilo Merlin)
        └───────────────────────────────┬───────────────────────────────┘
                                        ▼
                       5. FUSIÓN MULTIMODAL (late fusion, ponderada)
                                        ▼
                       6. VERIFICACIÓN OPEN-SET (Mahalanobis + energy + temp. scaling)
                                        ▼
                       7. SALIDA EXPLICABLE (Top-3 + evidencia + vecinos + distribución)
```

Fuente primaria de este diagrama: [[Pipeline del Sistema]] §1-2 (ya validado por el autor en sesión previa) y [[Modelo de Visión — BioCLIP]].

### 1.2 Modelo 1 — Segmentación anatómica (YOLO-seg, universal)

- **Qué separa:** `anuro_completo` + 15 regiones anatómicas = 16 etiquetas (esquema CVAT vigente, I-2 resuelta — no 8 de Roboflow, ese esquema es histórico).
- **Distinto del segmentador binario de la Etapa I** (individuo vs. fondo), que ya está entrenado y funcionando — es el antecedente directo, con menos clases. Documentarlo formalmente sigue pendiente ([[Modelo de Visión — BioCLIP]] §10).
- **Arquitectura base:** `yolov8n-seg.pt` (Ultralytics), con `yolov8s-seg` como escalón superior solo si `n` no alcanza precisión mínima y sobra presupuesto de tamaño.
- **Dataset:** 25-30 imágenes/especie (I-5), universal — no requiere 70 individuos porque el segmentador no distingue especies, solo regiones anatómicas. Las 28 especies superan este mínimo.
- **Pipeline de entrenamiento automatizado** (no manual, no iterativo a mano): export CVAT (Datumaro/CVAT 1.1) → `convertir_cvat_a_yolo.py` (aplica el mismo split congelado que identificación, excluye clases con <5 instancias, valida geometría) → `modelo.train()` con config fija (epochs=150, imgsz=640, patience=20, seed=42) → evaluación automática (mAP50/50-95 por clase, cuadrícula de muestras, alerta si mAP50<umbral) → revisión humana de "¿esto sirve?", no de "¿cómo se entrena?". Detalle completo en [[Automatización del Entrenamiento de Segmentación]].
- **Exportación:** ONNX/TFLite nativo de Ultralytics, cuantización INT8 con dataset de calibración → 10-25 MB.

### 1.3 Modelo 2 — Identificación de especie (BioCLIP teacher servidor + EdgeNeXt-Tiny student on-device)

> [!important] Esta es la corrección central del documento
> BioCLIP-INT8 on-device **fracasó en pruebas reales** (~0,2 % de exactitud — los outliers de atención del ViT se destruyen bajo cuantización INT8). Decisión del autor, 2026-09-08 (C-5): se usa **destilación de conocimiento**.

**Teacher (solo servidor):**
- BioCLIP v1, ViT-B/16, ~86M parámetros, fine-tuned. Pesos ya revisados y características óptimas definidas (tarea del 06 sep cerrada).
- Único extractor visual del servidor; genera soft labels con temperatura T=4.
- BioCLIP 2 (ViT-L/14) queda como candidato de mejora post-sprint, no para este prototipo — evita el problema de espacios de embedding v1/v2 incompatibles dentro del plazo.

**Student (on-device):**
- **EdgeNeXt-Tiny**, ~2-4M parámetros, <4 MB.
- Entrenado con **Multi-Head Loss** (término oficial de la bóveda): cross-entropy paralela para tres cabezas (Familia + Género + Especie) **más** divergencia KL contra el teacher (T=4).
- Dispositivo de referencia confirmado: **Samsung Galaxy A30, 4 GB RAM** — es donde se emula y mide latencia/RAM/batería, no en el equipo de desarrollo.
- Verificación del tamaño real cuantizado en el A30 sigue pendiente de medir.

**Presupuesto de almacenamiento total revisado:** ~15-30 MB (segmentación + EdgeNeXt-Tiny + audio), frente a los ~150 MB calculados originalmente cuando se asumía BioCLIP completo on-device.

**Variante de entrada validada empíricamente (Etapa I):** recorte del individuo + máscara binaria (fondo a negro/neutro) — variante "C" de [[Modelo de Visión — BioCLIP]] §5, la que explica buena parte del ~99% de la Etapa I al eliminar *shortcut learning* sobre el sustrato.

**Métrica métrica adicional posible — Triplet Loss ([[Implementación de Triplet Loss]]):** no sustituye al Multi-Head Loss, lo complementaría en una fase posterior de fine-tuning parcial para dar forma al espacio de embeddings (mejor Recall@K, mejor AUROC open-set). Orden de trabajo recomendado por la propia nota: medir primero con embeddings congelados, añadir triplet/ArcFace solo si Recall@5 es insuficiente. No es parte del alcance mínimo del prototipo del 27 sep — es una nota de referencia, no una tarea de la ruta crítica.

### 1.4 Base vectorial: sqlite-vec local (patrón Merlin) + Qdrant servidor

- **Servidor (Fase 1):** Qdrant, HNSW completo, fuente de verdad, colecciones `anura_visual` (512-d BioCLIP teacher) y `anura_acustico` separadas.
- **Dispositivo (Fase 2, offline):** **SQLite + sqlite-vec** (decisión C-6, 2026-09-08 — reemplaza a ObjectBox, decisión anterior ya revertida). Motivo de ingeniería: portabilidad absoluta de archivo (`.sqlite` autocontenido, descargar = copiar un archivo, borrar = `file.delete()`), consultas híbridas metadatos+vector en una sola llamada, footprint ~30 MB en el Galaxy A30.
- **Patrón operativo "estilo Merlin" (Cornell Lab), la referencia de diseño explícita del proyecto:** el backbone (EdgeNeXt-Tiny) queda **congelado** en el APK — no cambia con la región. Lo que varía por zona son los **embeddings**, descargados/actualizados como paquetes `.sqlite` independientes por región biogeográfica (p. ej. Antioquia, Guaviare). Añadir una especie a una zona es actualizar datos, no la app.
- Validación empírica pendiente: latencia y footprint de sqlite-vec en el Galaxy A30 con paquete simulado de 10-50k vectores.
- Dimensión del embedding on-device: **ya no es 512-d de BioCLIP** — depende de la capa de salida de EdgeNeXt-Tiny, por definir durante el entrenamiento de destilación.

Detalle completo: [[Base Vectorial (Qdrant)]].

### 1.5 Rama de audio: modelo propio dedicado (condicionado a Go/No-Go 18 sep)

- Decisión C-7 (2026-09-08): **NO** reutiliza el backbone EdgeNeXt-Tiny destilado (a diferencia de BioCLIP, que era un modelo fundacional de propósito general, EdgeNeXt-Tiny fue destilado con objetivo estrecho — morfología de rana en fotos — y transferir mal a espectrogramas es un riesgo real).
- Arquitectura candidata (aún no comparada experimentalmente): CNN pequeña custom (<1 MB) / MobileNetV1-V2 adaptada 1 canal (1-3 MB) / estilo BirdNET-lite (2-6 MB).
- Entrada: WAV mono 44,1 kHz 16-bit, ventana 3-5s, SNR≥15dB → mel-espectrograma ~128×256 → augmentación SpecAugment (`TimeShift`, `FrequencyMasking`, `TimeMasking`, nunca flips geométricos).
- **Bloqueante explícito:** confirmar cobertura de dataset de audio (AnuraSet/Xeno-canto/grabación propia) para las 28 especies. **Punto Go/No-Go fijado para el 18 de septiembre** en el cronograma real — si no hay cobertura suficiente, la rama de audio se declara trabajo futuro dentro del sprint.

### 1.6 Las cuatro fuentes de evidencia en paralelo (lo que el plan anterior omitía)

Tras la extracción de características, el pipeline real ([[Pipeline del Sistema]] §2, etapa 4) no es "solo clasificación": son cuatro fuentes que se computan en paralelo y ninguna decide sola:

| Fuente | Qué aporta | Falla cuando… |
| --- | --- | --- |
| 4a Clasificación jerárquica | Probabilidad Familia/Género/Especie (Multi-Head Loss + enmascarado jerárquico para evitar predicciones taxonómicamente imposibles) | La especie no está en el catálogo |
| 4b Búsqueda vectorial | "Se parece a estas observaciones confirmadas" (sqlite-vec local) | Pocos ejemplares de esa especie en el catálogo |
| 4c Atributos vs. plantilla | Evidencia explicable carácter a carácter, con tres estados: ✅ compatible / ❌ contradictorio / ❓ no observable (nunca booleano — "no observable" ≠ "ausente") | La región no es visible en la foto |
| 4d Contexto geográfico | Compatibilidad con distribución conocida, como *prior* acotado (multiplicador 0,5-1,5), nunca como filtro duro | Mapas de distribución incompletos |

Después: **fusión multimodal** (late fusion ponderada, pesos calibrados en validación, nunca sumando porcentajes crudos — [[Arquitectura Multimodal]] §3) → **verificación open-set** (temperature scaling + distancia Mahalanobis a centroide + energy score, umbral fijado en validación con TPR≥95% — [[Open-Set Recognition]] §2) → **salida explicable** con Top-3, evidencia por región, vecinos similares y contexto de distribución mostrados al usuario, incluida la evidencia contradictoria.

---

## 2. Estado real: qué ya está hecho vs. qué falta

### 2.1 Ya hecho / decidido (no reabrir)

- ✅ **Etapa I ejecutada con ~99% de exactitud real** sobre 10 especies × 70 individuos, con segmentación binaria + `GroupSplit` por individuo + diversidad de individuos (sin fuga verificada). Ya existe un pipeline funcionando, no se parte de cero.
- ✅ C-1→C-7 cerradas en [[Inconsistencias y Decisiones Pendientes]]: BioCLIP único en servidor (C-2), Etapa I legítima (C-4), EdgeNeXt-Tiny destilado con Multi-Head Loss (C-5), sqlite-vec reemplaza ObjectBox (C-6), audio propio dedicado (C-7).
- ✅ Catálogo de 28 especies confirmado (C-3), coincide con `anuro_labels.json` y las carpetas de campo.
- ✅ Pesos BioCLIP v1 revisados y características óptimas definidas para su rol de teacher (tarea del 06 sep, ya cerrada en el cronograma).
- ✅ Dispositivo de referencia confirmado: Samsung Galaxy A30, 4 GB RAM.
- ✅ Esquema de anotación de 16 etiquetas (CVAT) vigente para segmentación anatómica.
- ✅ 24 de 28 especies con ≥70 fotos (cumplen requisito de identificación); las 28 superan el mínimo de 25-30 para segmentación. Fuentes públicas (iNaturalist, Xeno-canto) ya agotadas para las 4 especies deficitarias — verificado hoy (2026-09-10).

### 2.2 Falta por hacer (con fecha real del cronograma)

| Falta | Hito | Fecha |
| --- | --- | --- |
| Repetir el protocolo riguroso de la Etapa I (segmentación binaria + `GroupSplit`) escalando de 10 a 28 especies | H3/D-1 | Semana 1, dataset congelado 07 sep (ya en curso) |
| Entrenar formalmente el segmentador YOLO-seg de 16 clases | H5 | 2026-09-13 (automatizado, tras llegada de datos CVAT del 09-11 sep) |
| Entrenar EdgeNeXt-Tiny por destilación (Multi-Head Loss) desde BioCLIP teacher | H6 | 2026-09-15 |
| Open-set mínimo viable (Mahalanobis + temperature scaling, umbral fijado) | H7 | 2026-09-17 |
| Cuantización y verificación de presupuesto en el Galaxy A30 | H10 | 2026-09-18 |
| Poblar sqlite-vec con paquetes regionales (Antioquia, Guaviare) | — | 16 sep (generación) |
| **Go/No-Go de la rama de audio** | — | **2026-09-18** |
| Integrar pipeline completo en el APK (captura→segmentación→identificación→sqlite-vec→contexto→open-set→resultado) | H11 | 2026-09-27 |

---

## 3. Plan de fases con fechas reales (alineado a [[Cronograma y Plan de Trabajo]] §0)

No se inventan fechas nuevas: son las ya fijadas por el autor el 2026-09-05 para el sprint del prototipo (05-27 sep).

### Semana 1 (05-11 sep) — Cimientos
- 05-06 sep: decisiones bloqueantes cerradas (ya ejecutado), pesos BioCLIP v1 verificados (ya ejecutado).
- 07 sep: `GroupSplit` por individuo congelado sobre las 28 especies (70 individuos/especie).
- 08 sep: línea base zero-shot de BioCLIP medida; script `convertir_cvat_a_yolo.py` probado con datos parciales. (Mismo día: pivote de arquitectura on-device cerrado — C-5/C-6/C-7, ya ejecutado.)
- 09-11 sep: **llegada de datos de segmentación anatómica** (comprometida por el equipo) → dispara el pipeline automatizado de [[Automatización del Entrenamiento de Segmentación]]; cierre de semana con segmentador v1 promovido.

### Semana 2 (12-18 sep) — Núcleo de identificación y optimización móvil
- 12 sep: cabezas jerárquicas (Multi-Head Loss) sobre embeddings cacheados del recorte segmentado.
- 13 sep: cuantización — **aquí es donde correspondía medir la cuantización directa de BioCLIP y donde se detectó el fracaso de INT8 que motivó C-5** (ya resuelto antes del sprint, documentado como antecedente).
- 14 sep: conversión a LiteRT/ONNX Runtime Mobile del modelo destilado; mockup de pantalla de resultado.
- 15-16 sep: sqlite-vec embebido con paquete simulado; generación de paquetes regionales reales (Antioquia, Guaviare).
- 17 sep: open-set mínimo viable (Mahalanobis + temperature scaling), umbral fijado en validación.
- **18 sep: UI de resultado con datos reales del modelo + punto Go/No-Go de audio** (decidir cobertura AnuraSet/Xeno-canto para las 28 especies).

### Semana 3 (19-27 sep) — Integración, medición y despliegue
- 19 sep: pipeline completo end-to-end en el dispositivo.
- 20 sep: multi-foto real (agregación de vistas, sin promediar embeddings); decisión de multi-individuo.
- 21 sep: medición real de latencia p95, memoria pico y batería en el Galaxy A30.
- 22 sep: demo web de respaldo (FastAPI + Qdrant).
- 23-26 sep: pulido de UI, pruebas, empaquetado, ensayo general (días colchón).
- **27 sep: entrega del prototipo — APK + demo web, sobre las 28 especies.**

Fuera de este sprint (quedan documentados como continuación, no se pierden): piloto de campo con ≥150 observaciones validadas por experto, documento final, sustentación, exportación Darwin Core completa, módulo comunitario a escala, iOS.

---

## 4. Riesgos aplicables (ya documentados — no reinventar)

De [[Riesgos del Proyecto]], los que aplican directamente a esta fase de modelo de visión:

- **D-1** (Alta/impacto Alto): fuga de información en el split. Mitigado en la Etapa I; el riesgo real ahora es **no repetir la misma disciplina de `GroupSplit` + segmentación binaria al escalar de 10 a 28 especies**.
- **D-3** (cumplido para identificación, 70/especie en 24 de 28 especies): vigilar las 4 especies deficitarias (*Dendropsophus norandinus*, *Hyloxalus picachos*, *Pristimantis vilarsi*, *Sachatamia electrops*) — fuentes públicas ya agotadas, decidir si se completan con recolección de campo adicional, se reduce el catálogo para esas 4, o se documentan como limitación conocida del prototipo.
- **D-5** (Alta/Media): datos de audio insuficientes — es exactamente el bloqueante del Go/No-Go del 18 sep.
- **T-1/T-5** (histórico, ya materializado): BioCLIP no cabe cuantizado sin perder precisión aceptable — se materializó como el fracaso de INT8 documentado en C-5; la mitigación ya aplicada es la destilación a EdgeNeXt-Tiny.
- **T-4** (Alta/Media): segmentación de 16 clases poco fiable con pocas anotaciones — mitigación ya prevista: empezar con clases agrupadas, preanotar y corregir.
- **T-7** (Media/Alta): deriva entre embeddings de móvil y servidor si difieren de versión — mitigado por el diseño ya fijado: mismo modelo (EdgeNeXt-Tiny) genera embeddings en ambos lados vía el manifest versionado de los paquetes sqlite-vec.
- **P-1** (Alta/Alta, "el riesgo más probable de todos"): alcance excesivo — el núcleo mínimo defendible del prototipo ya está fijado en [[Cronograma y Plan de Trabajo]] §0; no expandirlo sin decidirlo explícitamente.

---

## 5. Próximos pasos accionables (próximas 48 h, coherentes con el cronograma real)

Dado que hoy es 2026-09-10 (día 6 del sprint, dentro de la ventana de llegada de datos de segmentación del 09-11 sep):

1. **Confirmar el estado de la entrega de datos de segmentación anatómica CVAT** (comprometida para 09-11 sep) — si ya llegó, disparar de inmediato el pipeline `convertir_cvat_a_yolo.py` → entrenamiento YOLO-seg automatizado ([[Automatización del Entrenamiento de Segmentación]] §3).
2. **Congelar formalmente el `GroupSplit` por individuo sobre las 28 especies** (tarea del 07 sep) si aún no quedó versionado, incorporando las 4 especies deficitarias con la decisión explícita de cómo se tratan (completar, reducir o documentar como limitación).
3. **Iniciar la implementación del script de destilación Multi-Head Loss** (BioCLIP teacher congelado → EdgeNeXt-Tiny student), para llegar a tiempo al hito H6 del 15 de septiembre — es la pieza de mayor riesgo de cronograma dado que el plan anterior perdió días asumiendo la arquitectura equivocada (MobileNetV3-Small).
4. **Registrar en esta bóveda** (no en Notion ni en los Google Docs) cualquier avance o desviación de estas tareas, siguiendo el patrón ya establecido en [[Cronograma y Plan de Trabajo]] §5 (seguimiento semanal).
5. **No reabrir C-1 a C-7** — son decisiones cerradas por el autor; cualquier documento nuevo (incluido este) debe transcribirlas, no volver a evaluarlas.

---

## 6. Especies con pocos individuos: ponderación agresiva + discriminación fina intra-género

Sección conservada de la versión anterior, corregida a la arquitectura vigente (EdgeNeXt-Tiny, no
MobileNetV3-Small; "Multi-Head Loss" en vez de "L_jerarquica" inventado). Responde a lo que pidió el
usuario: cómo ponderar pérdida/aumentación para especies con pocos individuos, y cómo forzar al
modelo a distinguir especies del mismo género.

### 6.1 Los 4 clústeres de género que concentran el riesgo de confusión

Verificado contra `data dirty\arbol_taxonomico.json` — **17 de las 28 especies (61%)** comparten género
con al menos otra especie del proyecto:

| Género | Especies (n) | Familia |
|---|---|---|
| *Boana* | cinerascens, lanciformis, punctata, xerophylla (4) | Hylidae |
| *Dendropsophus* | bogerti, microcephalus, norandinus, reticulatus, triangulum (5) | Hylidae |
| *Pristimantis* | achatinus, paisa, penelopus, taeniatus, vilarsi (5) | Craugastoridae |
| *Rhinella* | margaritifera, alata, horribilis (3) | Bufonidae |

Las otras 11 especies son género-único dentro del proyecto — para esas, distinguir género ya casi
resuelve la especie; el problema real está concentrado en los 4 clústeres de arriba.

### 6.2 Ponderación de la pérdida por especie (class weighting)

Se aplica **Class-Balanced Loss** (Cui et al.) en vez de frecuencia inversa simple, porque con conteos
desiguales (26 a 1925 fotos, ver §2.1) la frecuencia inversa pura sobre-pondera brutalmente a las
especies más raras y desestabiliza el entrenamiento:

```
E_n = (1 - β^n) / (1 - β)        # "número efectivo de muestras" de la especie con n imágenes
peso_especie = 1 / E_n            # normalizado para que la media de pesos sea 1
```

- β recomendado: **0.999** (desbalance real del proyecto ≈ 1:74, dentro del rango donde este β es estándar).
- **Dónde se aplica:** únicamente al término de entropía cruzada de las tres cabezas del **Multi-Head
  Loss** (Familia/Género/Especie, §1.3) contra la etiqueta dura. **No se aplica al término de
  divergencia KL contra el teacher (BioCLIP)** — esa señal es información real sobre el espacio
  biológico aprendido por BioCLIP y ponderarla por frecuencia de muestreo la distorsionaría sin razón.
- **Además, `WeightedRandomSampler`** en el DataLoader con la misma familia de pesos, para que cada
  especie aparezca con frecuencia similar dentro de un batch.

### 6.3 Aumentación escalada por Tier

Alineado con las transformaciones ya definidas en [[Estrategia de Construcción del Dataset]]
("Transformaciones Permitidas" — `HorizontalFlip`, `ShiftScaleRotate`, `RandomBrightnessContrast`,
`CLAHE`, etc.) y sus **prohibiciones explícitas** (no `HueShift > 15`, no deformaciones geométricas
extremas — invalidan el carácter taxonómico de color/morfometría):

| Tier | Definición | Aumentación adicional |
|---|---|---|
| A (≥70 fotos limpias, 24/28 especies) | Augmentación base del vault únicamente | — |
| B (<70 fotos, las 4 especies deficitarias) | Base + oversampling explícito (política ya definida en el vault: "las especies raras o endémicas reciben oversampling mediante la tubería de augmentación sintética controlada") | Repetir cada imagen con 3-5 variantes distintas por época |

- El vault ya prohíbe explícitamente lo que en la versión anterior de este documento yo excluía por
  intuición (MixUp/CutMix): confirma que alterar el color más allá de `Hue ±10` o deformar la
  morfometría invalida el carácter taxonómico — coherente con no mezclar imágenes de especies
  distintas del mismo género.

### 6.4 Extracción agresiva de características distintivas intra-género

1. **Hard-negative mining dirigido por género:** al construir los batches, muestrear negativos
   preferentemente **dentro del mismo género** en vez de aleatoriamente de las 28 especies — un
   negativo aleatorio ya está bien separado por la cabeza de género del Multi-Head Loss y no aporta
   señal nueva; uno del mismo género fuerza al modelo a encontrar el rasgo fino real.
2. **Anclaje a las zonas anatómicas diagnósticas** ya identificadas en `PLAN_ETIQUETADO_DATOS.md`
   (`bicolor_reticulado` del iris para *Pristimantis*, `reticulado` del dorso para *Dendropsophus
   reticulatus*, `pliegue_tarsal` para el clúster de Hylidae) — son exactamente las regiones que el
   Modelo 1 (YOLO-seg, §1.2) segmenta, y las que alimentan la fuente de evidencia 4c (atributos vs.
   plantilla, §1.6). No es un mecanismo nuevo: es la razón práctica por la que la fuente 4c del
   pipeline real ya está diseñada para pesar más en la confusión intra-género que la clasificación
   4a sola.
3. **Métrica de evaluación específica por clúster:** además del accuracy top-1/top-3 global de la
   Etapa II (escalado a 28 especies), reportar una matriz de confusión restringida a cada uno de los 4
   clústeres de género — la Etapa I ya mostró exactamente este patrón (*Pristimantis paisa* F1=0.86,
   *Pristimantis penelopus* F1=0.86, frente a F1=1.00 en especies de género único como *Dendrobates
   truncatus*), así que es una métrica con precedente real, no hipotético, en este proyecto.

---

## Referencias

Todas las citas de esta versión provienen de `D:\Anura\Second Brain\Brain\`:
- [[Inconsistencias y Decisiones Pendientes]] (07 Notas de Trabajo)
- [[Modelo de Visión — BioCLIP]], [[Automatización del Entrenamiento de Segmentación]], [[Implementación de Triplet Loss]], [[Optimización para Inferencia en Móvil]], [[Base Vectorial (Qdrant)]] (04 Desarrollo Técnico)
- [[Arquitectura Multimodal]], [[Open-Set Recognition]], [[Pipeline del Sistema]], [[Listado de Individuos y Arreglo Taxonómico]], [[Estrategia de Construcción del Dataset]] (02 Metodología)
- [[Cronograma y Plan de Trabajo]], [[Riesgos del Proyecto]] (01 Proyecto)
- `D:\Anura\data dirty\arbol_taxonomico.json`, `D:\Anura\PLAN_ETIQUETADO_DATOS.md` (verificación local de datos, 2026-09-10)

Los 8 documentos de `D:\Anura\docs_vision_model_plan\*.md` quedan marcados como **fuente histórica
desactualizada**, no como referencia vigente para este plan.
