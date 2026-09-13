---
title: "App MÃ³vil"
proyecto: Anura
tipo: desarrollo-tÃ©cnico
estado: propuesta-de-diseÃ±o
tags: [anura, desarrollo, android, kotlin, offline, litert]
---

# App MÃ³vil

[[Anura â€” Ãndice General]] Â· [[API Backend]] Â· [[OptimizaciÃ³n para Inferencia en MÃ³vil]] Â· [[Arquitectura de la AplicaciÃ³n]] Â· [[Base Vectorial (SQLite-vec)]]

> [!note] Estado
> PÃ¡gina vacÃ­a en Notion. Propuesta de diseÃ±o construida sobre los requisitos ya definidos: RF-12 a RF-14, RNF-02 (â‰¤ 4 s), RNF-05 (â‰¤ 150 MB), RNF-07 a RNF-11 ([[Objetivos y Alcance]]).

## 1. Plataforma y stack

Los [[Objetivos y Alcance|objetivos]] fijan **Android** para la Fase 2. Con esa restricciÃ³n, la elecciÃ³n natural:

| Capa | ElecciÃ³n | Nota |
| --- | --- | --- |
| Lenguaje | **Kotlin** | Ya contemplado en las notas originales |
| UI | **Jetpack Compose** | Necesario para el modo oscuro y alto contraste del RNF-07 sin duplicar layouts |
| Inferencia | **ONNX Runtime Mobile** | LiteRT fue la ruta contemplada originalmente; C-11 confirmÃ³ ONNX como la Ãºnica que traza el ViT completo sin reescribir la arquitectura. Ver [[OptimizaciÃ³n para Inferencia en MÃ³vil]] |
| Persistencia | **Room** sobre SQLite | RNF-11 exige persistencia local tolerante a fallos |
| Vectores | **SQLite + sqlite-vec** | Qdrant **no** corre embebido â€” firmado en [[Base Vectorial (SQLite-vec)]] Â§2 (C-15: Ruta B, k-NN + paquetes regionales estilo Merlin; reemplaza a ObjectBox, decisiÃ³n C-6) |
| SincronizaciÃ³n | **WorkManager** | Reintentos, restricciones de red y baterÃ­a gestionados por el sistema |
| CÃ¡mara | **CameraX** | |
| Audio | **AudioRecord** (PCM crudo) | `MediaRecorder` comprime; el anÃ¡lisis bioacÃºstico necesita WAV sin pÃ©rdidas |
| Red | **Retrofit + OkHttp** | |

> [!note] iOS â€” decidido: no se considera en esta etapa
> InstrucciÃ³n directa del autor (2026-09-05): iOS queda fuera de alcance, sin fecha, y no se evalÃºa Kotlin Multiplatform/Flutter mientras dure el sprint del prototipo ni el resto del trabajo de grado. Si en el futuro se retoma, la migraciÃ³n de una app Android nativa con modelos LiteRT es costosa â€” pero esa conversaciÃ³n se tiene si y cuando iOS vuelva a la mesa, no ahora.

## 2. Arquitectura de la app

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ UI (Compose) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Captura Â· Resultado Â· Ficha Â· Salida de campo Â· Mapa      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                             â”‚  StateFlow
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                      ViewModels                            â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                             â”‚
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                     Casos de uso                           â”‚
â”‚  IdentificarEspecie Â· GuardarObservacion Â· SincronizarDatosâ”‚
â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
       â”‚                  â”‚                      â”‚
â”Œâ”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  ML Engine  â”‚  â”‚  Repositorios   â”‚  â”‚   Sync (WorkManager)â”‚
â”‚  LiteRT     â”‚  â”‚  Room + Vectoresâ”‚  â”‚   Retrofit          â”‚
â”‚  segment.   â”‚  â”‚  paquete regiÃ³n â”‚  â”‚                     â”‚
â”‚  bioclip    â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â”‚  acÃºstico   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

Clean architecture por capas, con una regla que importa especialmente aquÃ­: **el motor de ML no conoce la UI y la UI no conoce LiteRT**. Permite sustituir el runtime (LiteRT â†’ ONNX Runtime) o el modelo sin tocar pantallas, algo que va a pasar varias veces durante el proyecto.

## 3. El flujo de identificaciÃ³n offline

```
 Usuario pulsa capturar
        â†“
 CameraX â†’ Bitmap
        â†“
 [1] Preproceso: recorte, escala 224Ã—224, normalizaciÃ³n     ~50 ms
        â†“
 [2] SegmentaciÃ³n (YOLO-seg cuantizado)                    ~300-600 ms
        â†“  mÃ¡scaras + caja de anuro_completo
 [3] Recorte del individuo
        â†“
 [4] BioCLIP â†’ embedding 512-d                             ~400-900 ms
        â†“
 [5] Cabezas jerÃ¡rquicas â†’ Familia/GÃ©nero/Especie          ~5 ms
        â†“
 [6] BÃºsqueda vectorial local (Top-K vecinos)              ~10-50 ms
        â†“
 [7] Open-set check (distancia + umbral)                   ~1 ms
        â†“
 [8] FusiÃ³n con GPS/altitud/fecha                          ~5 ms
        â†“
 Resultado + evidencia anatÃ³mica + Top-3
```

Presupuesto total objetivo: **â‰¤ 4 s** (RNF-02), con margen suficiente en gama media. Los pasos 2 y 4 son el 90 % del coste; ahÃ­ es donde aplica todo lo de [[OptimizaciÃ³n para Inferencia en MÃ³vil]].

Detalles de implementaciÃ³n que evitan problemas reales en campo:

- **Toda la inferencia fuera del hilo principal** (corrutinas + `Dispatchers.Default`), con la UI mostrando progreso por etapas. Un bloqueo de 4 s en el hilo de UI produce un ANR.
- **Los intÃ©rpretes se crean una vez** y se reutilizan; instanciar un intÃ©rprete LiteRT por foto multiplica el tiempo y fragmenta memoria.
- **Liberar el modelo de segmentaciÃ³n cuando no se usa** si la memoria aprieta: en gama baja, tener varios modelos residentes simultÃ¡neamente puede provocar que el sistema mate el proceso. Con BioCLIP como Ãºnico backbone tambiÃ©n para audio ([[Modelo de VisiÃ³n â€” BioCLIP]] Â§8), solo hay dos modelos que gestionar, no tres.
- **Guardar primero, procesar despuÃ©s.** La foto y sus metadatos se persisten *antes* de inferir. Si la app muere a mitad de la inferencia, el dato de campo â€” que es irrepetible â€” no se pierde. Esto es lo que exige de verdad el RNF-11.

## 4. Modo campo: lo que realmente decide si la app se usa

Los requisitos RNF-07 a RNF-09 no son adornos de usabilidad; describen las condiciones de un muestreo nocturno de anfibios, que es cuando se trabaja:

- **Una sola mano.** Capturar, grabar audio y guardar deben caer en el tercio inferior de la pantalla. La otra mano sostiene la linterna o el animal.
- **Modo oscuro real y modo luz roja.** La linterna blanca altera el comportamiento nocturno de los animales y destruye la adaptaciÃ³n a la oscuridad del observador. Una pantalla que emite blanco a 100 % de brillo hace lo mismo. Un tema de luz roja es una mejora funcional para trabajo nocturno, no estÃ©tica.
- **Feedback hÃ¡ptico y sonoro** para confirmar que se guardÃ³, porque en campo no siempre se puede mirar la pantalla.
- **BaterÃ­a:** RNF-09 fija â‰¤ 5 %/hora. El GPS continuo es el mayor consumidor, por encima de la inferencia. Estrategia: fijar la posiciÃ³n al inicio de la observaciÃ³n y no mantener el GPS activo entre capturas.
- **Resistencia a interrupciones**: llamadas, baterÃ­a crÃ­tica, guantes mojados, pantalla con lluvia. Autoguardado agresivo.

## 5. Presupuesto de almacenamiento

| Componente | TamaÃ±o estimado |
| --- | --- |
| Modelo de segmentaciÃ³n (INT8) | 10â€“25 MB |
| BioCLIP ViT-B/16 (INT8) â€” **usado para visiÃ³n y audio, un solo modelo** | 85â€“90 MB |
| Cabezas + tabla de prompts de texto | < 1 MB |
| **Subtotal modelos (lÃ­mite RNF-05: 150 MB)** | **~95â€“115 MB** |
| Paquete regional de vectores (10 k, int8) | ~5 MB |
| Fichas tÃ©cnicas + imÃ¡genes de referencia | 20â€“50 MB |
| Observaciones del usuario (~80 KB c/u) | crece con el uso |

El margen mejorÃ³ notablemente frente a un diseÃ±o con backbone de audio separado: al reutilizar BioCLIP para el espectrograma ([[Modelo de VisiÃ³n â€” BioCLIP]] Â§8), se libera del orden de 5â€“8 MB y, mÃ¡s importante, una ruta de cuantizaciÃ³n entera que ya no hay que mantener. El riesgo que queda es el mismo de siempre: si la cuantizaciÃ³n INT8 de BioCLIP degrada demasiado la precisiÃ³n y hay que subir a FP16 (~170 MB), **se rompe el RNF-05** y habrÃ­a que replantear (destilaciÃ³n, o inferencia en servidor con cachÃ© offline). EstÃ¡ registrado en [[Riesgos del Proyecto]].

## 6. GestiÃ³n de imÃ¡genes: compresiÃ³n y miniaturas (reduce la carga de procesamiento)

Cada observaciÃ³n puede tener varias fotos (RF-02, multi-foto) mÃ¡s las del historial acumulado â€” cargar cada una a resoluciÃ³n completa solo para dibujar una fila de una lista es el error de rendimiento mÃ¡s comÃºn y mÃ¡s evitable en una app con cÃ¡mara.

Tres resoluciones distintas, cada una con su propÃ³sito; ninguna sustituye a las otras:

| Copia | ResoluciÃ³n | Formato | Peso aprox. | Uso | Â¿Se guarda? |
| --- | --- | --- | --- | --- | --- |
| Inferencia | 224Ã—224 | Bitmap en memoria | â€” | Entrada al modelo (segmentaciÃ³n + BioCLIP) | No, nunca se persiste |
| Almacenamiento | 1024Ã—768 | WebP 80 % | ~70â€“100 KB | Detalle de la observaciÃ³n, sincronizaciÃ³n | SÃ­ â€” ver [[Estrategia de ConstrucciÃ³n del Dataset]] |
| **Miniatura** | ~200Ã—200 | WebP 70 % | ~8â€“15 KB | Listado, galerÃ­a de multi-foto, avatar de la Ãºltima observaciÃ³n | SÃ­, generada una sola vez al guardar |

La miniatura se genera **una sola vez, al guardar** (en el mismo paso y el mismo hilo en segundo plano que la copia de almacenamiento) y se cachea junto a la observaciÃ³n â€” nunca se recalcula al desplazarse por la lista.

Reglas de implementaciÃ³n:

- **Decodificar ya reducido, no decodificar y luego reducir.** `BitmapFactory.Options.inSampleSize` (o dejar que la librerÃ­a de carga de imÃ¡genes lo haga con `size(200, 200)`) evita materializar el bitmap completo en memoria solo para escalarlo despuÃ©s â€” la diferencia entre decodificar ~10 KB y varios MB por cada fila visible.
- **CachÃ© de memoria y disco activas**, pidiendo explÃ­citamente el tamaÃ±o de destino en cada pantalla: la miniatura en el Listado, la copia de almacenamiento en ConfirmaciÃ³n/Resultado â€” nunca la misma imagen a dos tamaÃ±os sin decÃ­rselo al cargador.
- **El Listado nunca lee la copia de 1024Ã—768.** Solo la miniatura. La copia de almacenamiento se carga Ãºnicamente al entrar al detalle de una observaciÃ³n.
- **Multi-foto (RF-02):** cada vista genera su propia miniatura; el carrusel/galerÃ­a se arma con miniaturas, no con las copias de almacenamiento.

Por quÃ© importa para el sprint: es directamente medible en el presupuesto de baterÃ­a y memoria del RNF-09 (Â§4 de esta misma nota) â€” un Listado que decodifica imÃ¡genes completas por fila es una causa comÃºn de que una app de cÃ¡mara se sienta lenta y gaste baterÃ­a sin que el modelo tenga nada que ver.

## 7. Permisos y privacidad

RNF-14 exige permisos mÃ­nimos y en el momento de uso:

| Permiso | CuÃ¡ndo se pide | Si se deniega |
| --- | --- | --- |
| `CAMERA` | Al pulsar capturar por primera vez | La app no puede identificar; permitir cargar desde galerÃ­a |
| `RECORD_AUDIO` | Al iniciar grabaciÃ³n | Se identifica solo con imagen (RNF-06 lo contempla) |
| `ACCESS_FINE_LOCATION` | Al crear la primera observaciÃ³n | Se guarda sin coordenadas; el contexto geogrÃ¡fico no se aplica |

Ninguno de los tres debe pedirse en el arranque. Y el fallo elegante importa: el RNF-06 exige que el sistema prediga aunque falten datos secundarios, asÃ­ que denegar ubicaciÃ³n o micrÃ³fono **degrada** la identificaciÃ³n, no la bloquea.

## 8. QuÃ© falta por decidir o medir

- [ ] Definir el dispositivo de referencia de gama baja para las pruebas (define el presupuesto real de latencia y memoria).
- [ ] Elegir motor vectorial embebido.
- [ ] Medir consumo de baterÃ­a en una jornada real de campo (RNF-09).
- [ ] Decidir versiÃ³n mÃ­nima de Android soportada.
- [ ] Probar el flujo completo sin red durante â‰¥ 8 h con decenas de registros acumulados (RNF-10).

Ver tambiÃ©n: [[Arquitectura de la AplicaciÃ³n]] Â· [[Flujo de Datos y SincronizaciÃ³n]] Â· [[Roadmap y Fases]]



