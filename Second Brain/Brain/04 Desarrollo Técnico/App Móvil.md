---
title: "App Móvil"
proyecto: Anura
tipo: desarrollo-técnico
estado: propuesta-de-diseño
tags: [anura, desarrollo, android, kotlin, offline, litert]
---

# App Móvil

[[Anura â€” àndice General]] · [[API Backend]] · [[Optimización para Inferencia en Móvil]] · [[Arquitectura de la Aplicación]] · [[Base Vectorial (SQLite-vec)]]

> [!note] Estado
> Página vacía en Notion. Propuesta de diseño construida sobre los requisitos ya definidos: RF-12 a RF-14, RNF-02 (â‰¤ 4 s), RNF-05 (â‰¤ 150 MB), RNF-07 a RNF-11 ([[Objetivos y Alcance]]).

## 1. Plataforma y stack

Los [[Objetivos y Alcance|objetivos]] fijan **Android** para la Fase 2. Con esa restricción, la elección natural:

| Capa | Elección | Nota |
| --- | --- | --- |
| Lenguaje | **Kotlin** | Ya contemplado en las notas originales |
| UI | **Jetpack Compose** | Necesario para el modo oscuro y alto contraste del RNF-07 sin duplicar layouts |
| Inferencia | **ONNX Runtime Mobile** | LiteRT fue la ruta contemplada originalmente; C-11 confirmó ONNX como la àºnica que traza el ViT completo sin reescribir la arquitectura. Ver [[Optimización para Inferencia en Móvil]] |
| Persistencia | **Room** sobre SQLite | RNF-11 exige persistencia local tolerante a fallos |
| Vectores | **SQLite + sqlite-vec** | Qdrant **no** corre embebido â€” firmado en [[Base Vectorial (SQLite-vec)]] §2 (C-15: Ruta B, k-NN + paquetes regionales estilo Merlin; reemplaza a ObjectBox, decisión C-6) |
| Sincronización | **WorkManager** | Reintentos, restricciones de red y batería gestionados por el sistema |
| Cámara | **CameraX** | |
| Audio | **AudioRecord** (PCM crudo) | `MediaRecorder` comprime; el análisis bioacàºstico necesita WAV sin pérdidas |
| Red | **Retrofit + OkHttp** | |

> [!note] iOS â€” decidido: no se considera en esta etapa
> Instrucción directa del autor (2026-09-05): iOS queda fuera de alcance, sin fecha, y no se evalàºa Kotlin Multiplatform/Flutter mientras dure el sprint del prototipo ni el resto del trabajo de grado. Si en el futuro se retoma, la migración de una app Android nativa con modelos LiteRT es costosa â€” pero esa conversación se tiene si y cuando iOS vuelva a la mesa, no ahora.

## 2. Arquitectura de la app

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ UI (Compose) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Captura · Resultado · Ficha · Salida de campo · Mapa      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                             â”‚  StateFlow
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                      ViewModels                            â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                             â”‚
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                     Casos de uso                           â”‚
â”‚  IdentificarEspecie · GuardarObservacion · SincronizarDatosâ”‚
â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
       â”‚                  â”‚                      â”‚
â”Œâ”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  ML Engine  â”‚  â”‚  Repositorios   â”‚  â”‚   Sync (WorkManager)â”‚
â”‚  LiteRT     â”‚  â”‚  Room + Vectoresâ”‚  â”‚   Retrofit          â”‚
â”‚  segment.   â”‚  â”‚  paquete región â”‚  â”‚                     â”‚
â”‚  bioclip    â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â”‚  acàºstico   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

Clean architecture por capas, con una regla que importa especialmente aquí: **el motor de ML no conoce la UI y la UI no conoce LiteRT**. Permite sustituir el runtime (LiteRT â†’ ONNX Runtime) o el modelo sin tocar pantallas, algo que va a pasar varias veces durante el proyecto.

## 3. El flujo de identificación offline

```
 Usuario pulsa capturar
        â†“
 CameraX â†’ Bitmap
        â†“
 [1] Preproceso: recorte, escala 224à—224, normalización     ~50 ms
        â†“
 [2] Segmentación (YOLO-seg cuantizado)                    ~300-600 ms
        â†“  máscaras + caja de anuro_completo
 [3] Recorte del individuo
        â†“
 [4] BioCLIP â†’ embedding 512-d                             ~400-900 ms
        â†“
 [5] Cabezas jerárquicas â†’ Familia/Género/Especie          ~5 ms
        â†“
 [6] Bàºsqueda vectorial local (Top-K vecinos)              ~10-50 ms
        â†“
 [7] Open-set check (distancia + umbral)                   ~1 ms
        â†“
 [8] Fusión con GPS/altitud/fecha                          ~5 ms
        â†“
 Resultado + evidencia anatómica + Top-3
```

Presupuesto total objetivo: **â‰¤ 4 s** (RNF-02), con margen suficiente en gama media. Los pasos 2 y 4 son el 90 % del coste; ahí es donde aplica todo lo de [[Optimización para Inferencia en Móvil]].

Detalles de implementación que evitan problemas reales en campo:

- **Toda la inferencia fuera del hilo principal** (corrutinas + `Dispatchers.Default`), con la UI mostrando progreso por etapas. Un bloqueo de 4 s en el hilo de UI produce un ANR.
- **Los intérpretes se crean una vez** y se reutilizan; instanciar un intérprete LiteRT por foto multiplica el tiempo y fragmenta memoria.
- **Liberar el modelo de segmentación cuando no se usa** si la memoria aprieta: en gama baja, tener varios modelos residentes simultáneamente puede provocar que el sistema mate el proceso. Con BioCLIP como àºnico backbone también para audio ([[Modelo de Visión â€” BioCLIP]] §8), solo hay dos modelos que gestionar, no tres.
- **Guardar primero, procesar después.** La foto y sus metadatos se persisten *antes* de inferir. Si la app muere a mitad de la inferencia, el dato de campo â€” que es irrepetible â€” no se pierde. Esto es lo que exige de verdad el RNF-11.

## 4. Modo campo: lo que realmente decide si la app se usa

Los requisitos RNF-07 a RNF-09 no son adornos de usabilidad; describen las condiciones de un muestreo nocturno de anfibios, que es cuando se trabaja:

- **Una sola mano.** Capturar, grabar audio y guardar deben caer en el tercio inferior de la pantalla. La otra mano sostiene la linterna o el animal.
- **Modo oscuro real y modo luz roja.** La linterna blanca altera el comportamiento nocturno de los animales y destruye la adaptación a la oscuridad del observador. Una pantalla que emite blanco a 100 % de brillo hace lo mismo. Un tema de luz roja es una mejora funcional para trabajo nocturno, no estética.
- **Feedback háptico y sonoro** para confirmar que se guardó, porque en campo no siempre se puede mirar la pantalla.
- **Batería:** RNF-09 fija â‰¤ 5 %/hora. El GPS continuo es el mayor consumidor, por encima de la inferencia. Estrategia: fijar la posición al inicio de la observación y no mantener el GPS activo entre capturas.
- **Resistencia a interrupciones**: llamadas, batería crítica, guantes mojados, pantalla con lluvia. Autoguardado agresivo.

## 5. Presupuesto de almacenamiento

| Componente | Tamaño estimado |
| --- | --- |
| Modelo de segmentación (INT8) | 10â€“25 MB |
| BioCLIP ViT-B/16 (INT8) â€” **usado para visión y audio, un solo modelo** | 85â€“90 MB |
| Cabezas + tabla de prompts de texto | < 1 MB |
| **Subtotal modelos (límite RNF-05: 150 MB)** | **~95â€“115 MB** |
| Paquete regional de vectores (10 k, int8) | ~5 MB |
| Fichas técnicas + imágenes de referencia | 20â€“50 MB |
| Observaciones del usuario (~80 KB c/u) | crece con el uso |

El margen mejoró notablemente frente a un diseño con backbone de audio separado: al reutilizar BioCLIP para el espectrograma ([[Modelo de Visión â€” BioCLIP]] §8), se libera del orden de 5â€“8 MB y, más importante, una ruta de cuantización entera que ya no hay que mantener. El riesgo que queda es el mismo de siempre: si la cuantización INT8 de BioCLIP degrada demasiado la precisión y hay que subir a FP16 (~170 MB), **se rompe el RNF-05** y habría que replantear (destilación, o inferencia en servidor con caché offline). Está registrado en [[Riesgos del Proyecto]].

## 6. Gestión de imágenes: compresión y miniaturas (reduce la carga de procesamiento)

Cada observación puede tener varias fotos (RF-02, multi-foto) más las del historial acumulado â€” cargar cada una a resolución completa solo para dibujar una fila de una lista es el error de rendimiento más comàºn y más evitable en una app con cámara.

Tres resoluciones distintas, cada una con su propósito; ninguna sustituye a las otras:

| Copia | Resolución | Formato | Peso aprox. | Uso | ¿Se guarda? |
| --- | --- | --- | --- | --- | --- |
| Inferencia | 224à—224 | Bitmap en memoria | â€” | Entrada al modelo (segmentación + BioCLIP) | No, nunca se persiste |
| Almacenamiento | 1024à—768 | WebP 80 % | ~70â€“100 KB | Detalle de la observación, sincronización | Sí â€” ver [[Estrategia de Construcción del Dataset]] |
| **Miniatura** | ~200à—200 | WebP 70 % | ~8â€“15 KB | Listado, galería de multi-foto, avatar de la àºltima observación | Sí, generada una sola vez al guardar |

La miniatura se genera **una sola vez, al guardar** (en el mismo paso y el mismo hilo en segundo plano que la copia de almacenamiento) y se cachea junto a la observación â€” nunca se recalcula al desplazarse por la lista.

Reglas de implementación:

- **Decodificar ya reducido, no decodificar y luego reducir.** `BitmapFactory.Options.inSampleSize` (o dejar que la librería de carga de imágenes lo haga con `size(200, 200)`) evita materializar el bitmap completo en memoria solo para escalarlo después â€” la diferencia entre decodificar ~10 KB y varios MB por cada fila visible.
- **Caché de memoria y disco activas**, pidiendo explícitamente el tamaño de destino en cada pantalla: la miniatura en el Listado, la copia de almacenamiento en Confirmación/Resultado â€” nunca la misma imagen a dos tamaños sin decírselo al cargador.
- **El Listado nunca lee la copia de 1024à—768.** Solo la miniatura. La copia de almacenamiento se carga àºnicamente al entrar al detalle de una observación.
- **Multi-foto (RF-02):** cada vista genera su propia miniatura; el carrusel/galería se arma con miniaturas, no con las copias de almacenamiento.

Por qué importa para el sprint: es directamente medible en el presupuesto de batería y memoria del RNF-09 (§4 de esta misma nota) â€” un Listado que decodifica imágenes completas por fila es una causa comàºn de que una app de cámara se sienta lenta y gaste batería sin que el modelo tenga nada que ver.

## 7. Permisos y privacidad

RNF-14 exige permisos mínimos y en el momento de uso:

| Permiso | Cuándo se pide | Si se deniega |
| --- | --- | --- |
| `CAMERA` | Al pulsar capturar por primera vez | La app no puede identificar; permitir cargar desde galería |
| `RECORD_AUDIO` | Al iniciar grabación | Se identifica solo con imagen (RNF-06 lo contempla) |
| `ACCESS_FINE_LOCATION` | Al crear la primera observación | Se guarda sin coordenadas; el contexto geográfico no se aplica |

Ninguno de los tres debe pedirse en el arranque. Y el fallo elegante importa: el RNF-06 exige que el sistema prediga aunque falten datos secundarios, así que denegar ubicación o micrófono **degrada** la identificación, no la bloquea.

## 8. Qué falta por decidir o medir

- [ ] Definir el dispositivo de referencia de gama baja para las pruebas (define el presupuesto real de latencia y memoria).
- [ ] Elegir motor vectorial embebido.
- [ ] Medir consumo de batería en una jornada real de campo (RNF-09).
- [ ] Decidir versión mínima de Android soportada.
- [ ] Probar el flujo completo sin red durante â‰¥ 8 h con decenas de registros acumulados (RNF-10).

Ver también: [[Arquitectura de la Aplicación]] · [[Flujo de Datos y Sincronización]] · [[Roadmap y Fases]]



