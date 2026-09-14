---
title: "Base Vectorial (SQLite-vec)"
proyecto: Anura
tipo: desarrollo-técnico
estado: motor-móvil-firmado-sqlite-vec-c15
tags: [anura, desarrollo, sqlite-vec, qdrant, base-vectorial, hnsw, offline, merlin, knn]
---

# Base Vectorial (SQLite-vec)

[[Anura â€” àndice General]] · [[Modelo de Visión â€” BioCLIP]] · [[App Móvil]] · [[Open-Set Recognition]] · [[Escalabilidad]]

> [!success] Motor de producción on-device: SQLite-vec (Ruta B firmada en C-15, 2026-09-13)
> El móvil (offline) usa **SQLite + extensión sqlite-vec** como motor vectorial embebido â€” es la Ruta B: k-NN sobre embeddings del encoder BioCLIP, con paquetes regionales `.sqlite` descargables por zona (patrón Merlin Bird ID, Cornell Lab). Qdrant sigue siendo el motor del **servidor** (Fase 1, comunidad completa), nunca corre en el dispositivo â€” ver por qué en el aviso original de abajo. La comparación empírica k-NN vs. clasificador softmax (Ruta A) está en [[Experimentos y Resultados]] (EXP-014, 2026-09-13): la ganancia de Ruta B no es solo de precisión, es la evidencia visual "por qué" y el crecimiento sin reentrenar.

> [!danger] Hallazgo crítico (histórico): Qdrant **no puede correr embebido en el móvil**
> Toda la documentación del proyecto asume una "base vectorial local" en el dispositivo usando Qdrant (RNF-10, [[Notas Originales â€” Segmentación Semántica y Metodología Anura|notas originales]], [[Estrategia de Construcción del Dataset]]). **Eso no es posible tal como está planteado.** Qdrant es un servidor: se distribuye como binario/contenedor de cientos de MB y se accede por red. No existe una librería embebible para Android de uso pàºblico â€” *Qdrant Edge*, la variante en proceso, se anunció en julio de 2025 en beta privada y no está disponible de forma general.
>
> **Esto no rompe la arquitectura, obliga a partirla en dos, y ya hay una alternativa concreta para el móvil.** Ver §2 â€” no es un hueco sin resolver, es una decisión con recomendación firme.

## 1. Qué aporta una base vectorial a Anura

La idea de fondo (bien capturada en las notas originales) es que el sistema tenga **memoria de ejemplares**, no solo un clasificador. Cada observación validada se almacena como vector + metadatos:

```
Vector (embedding BioCLIP 512-d)
 â”œâ”€â”€ Familia / Género / Especie
 â”œâ”€â”€ Imagen (referencia)
 â”œâ”€â”€ Coordenadas, altitud, fecha
 â”œâ”€â”€ Embedding acàºstico (si existe)
 â””â”€â”€ Contexto ambiental
```

De ahí salen tres capacidades que un clasificador cerrado no da:

1. **Evidencia por ejemplos.** "Se parece a estas 5 observaciones confirmadas de *Boana cinerea*" es una justificación mucho más convincente para un herpetólogo que "87 % de probabilidad".
2. **Crecimiento sin reentrenar.** Añadir una especie nueva = añadir sus vectores. El modelo no se toca. Es la base de [[Escalabilidad]].
3. **Detección de desconocidos.** Si el vecino más cercano está lejos, probablemente no es ninguna especie del catálogo â†’ [[Open-Set Recognition]].

## 2. Arquitectura resultante: dos motores, un mismo espacio vectorial

| | **Servidor (Fase 1)** | **Dispositivo (Fase 2, offline)** |
| --- | --- | --- |
| Motor | **Qdrant** | **SQLite + sqlite-vec** âœ… (revisado 2026-09-08) |
| Contenido | Todas las observaciones de la comunidad | Paquete regional descargado + observaciones locales |
| àndice | HNSW completo | K-NN sobre BLOBs vía `sqlite-vec`, escala de milesâ€“decenas de miles de vectores |
| Escritura | Continua, multiusuario | Local, sincroniza después |
| Rol | Fuente de verdad, reindexado, analítica | Inferencia y recuperación en campo sin red |

> [!important] Decisión revisada (2026-09-08, C-6): SQLite + sqlite-vec reemplaza a ObjectBox
> La recomendación anterior de esta nota (ObjectBox) queda **revertida por decisión directa del autor**. El argumento de fondo no es solo "una base menos que sincronizar" â€” es que el modelo de **paquetes regionales modulares al estilo Merlin** (Cornell Lab, la app de identificación de aves que sirve de inspiración directa para Anura) encaja mejor con el modelo de archivo de SQLite que con el de ObjectBox. Tres razones de ingeniería, en orden de peso:
>
> 1. **Portabilidad absoluta de archivos independientes.** Un `.sqlite` es un contenedor autocontenido y estandarizado: descargar el paquete de Antioquia o Caldas es bajar **un àºnico archivo** que la app abre al instante bajo demanda (llamada nativa) y borra por completo con `file.delete()` al cambiar de región. ObjectBox, al ser una base orientada a objetos con esquema compilado y gestión interna de directorios vía memory-mapped files, no ofrece ese "plug-and-play" de màºltiples bases aisladas descargadas en caliente desde la red â€” es un solo almacén persistente, no pensado para montar/desmontar paquetes intercambiables como unidades atómicas.
> 2. **Consultas híbridas de metadatos y vectores en una sola llamada local.** SQLite conserva su estructura relacional tradicional; `sqlite-vec` añade la bàºsqueda vectorial sobre esa misma base. Esto permite vincular la ruta taxonómica (Familiaâ†’Géneroâ†’Especie) con los embeddings de EdgeNeXt-Tiny y **filtrar por región/subregión antes de calcular distancia vectorial**, en una àºnica consulta optimizada â€” exactamente el patrón que exige el diseño de paquetes biogeográficos de §4.
> 3. **Control estricto de recursos en gama baja.** `sqlite-vec` opera directamente sobre el motor C de SQLite con huella de memoria muy reducida (~30 MB por defecto), lo que garantiza que el **Samsung Galaxy A30** (dispositivo de referencia, ver [[Optimización para Inferencia en Móvil]]) ejecute las consultas K-NN en milisegundos sin disparar el consumo de RAM ni congelar el hilo de UI.
>
> USearch queda descartado por el mismo argumento de integración manual en Android que antes se usaba contra sqlite-vec (§ tabla histórica más abajo, conservada como referencia).

### Tabla comparativa histórica (previa a la revisión del 08 sep â€” conservada como referencia)

| | ObjectBox (recomendación anterior) | **sqlite-vec** âœ… decisión vigente | USearch |
| --- | --- | --- | --- |
| Qué es | Base de datos embebida orientada a objetos, con motor HNSW **nativo** integrado | Extensión de SQLite en C, cargable como librería | Librería de bàºsqueda vectorial de un solo header en C++, con bindings a ~10 lenguajes |
| Soporte Android/Kotlin | Oficial y de primera clase â€” `objectbox-android`, API Kotlin idiomática | Librerías precompiladas publicadas para Android e iOS desde v0.1.2; se integran como `.so`/loadable extension | Compila para Android (JNI); no trae wrapper Kotlin propio |
| Portabilidad de paquetes regionales como archivos independientes | Débil â€” almacén àºnico gestionado internamente, no pensado para montar/desmontar bases aisladas en caliente | **Fuerte â€” es exactamente el patrón `.sqlite` portátil que exige el diseño estilo Merlin** | Débil â€” solo el índice, sin modelo de archivo autocontenido |
| Persistencia de metadatos junto al vector | Integrada (objetos + vector) | Integrada â€” vector y fila conviven en la misma base SQLite | No integrada â€” metadatos aparte, enlazados por ID |
| Footprint en gama baja | Compite con motores de servidor, pero como almacén àºnico, no por paquete | Muy ligero (~30 MB de huella por defecto), directo sobre el motor C de SQLite | HNSW en C++ puro, eficiente pero exige capa JNI propia |
| Licencia | Apache-2.0 (nàºcleo) | MIT | Apache-2.0 |

Sigue pendiente la validación empírica: cargar un paquete regional simulado (10â€“50 k vectores) con `sqlite-vec` y medir latencia de bàºsqueda y footprint de memoria **en el Galaxy A30**, antes de comprometerse en código de producción.

Condición imprescindible en cualquier caso: **el mismo modelo debe generar los embeddings en ambos lados** â€” ahora **EdgeNeXt-Tiny**, no BioCLIP directo (ver el pivote registrado en [[Modelo de Visión â€” BioCLIP]] y en [[Inconsistencias y Decisiones Pendientes]] C-5). Vectores de modelos distintos no se pueden comparar.

## 1.1 Modelo operativo: backbone congelado + embeddings descargables por zona (estilo Merlin)

Esta es la pieza que amarra todo el diseño y conviene dejarla explícita, porque es la que justifica por qué sqlite-vec es la opción correcta y no solo una preferencia de formato:

```
1. El modelo (EdgeNeXt-Tiny) está CONGELADO en el APK â€” no cambia con la región.
2. Lo que varía por zona son los EMBEDDINGS: se descargan, se editan/actualizan
   y se aplican como paquetes .sqlite independientes, filtrados geográficamente.
3. Inspiración directa: Merlin Bird ID (Cornell Lab) â€” el modelo de identificación
   viaja fijo en la app; los "paquetes regionales" de especies por zona son los
   que se descargan, activan o eliminan segàºn dónde esté el usuario.
```

Consecuencias directas de este modelo para el diseño:

- **El backbone nunca se reentrena ni se redistribuye por región.** Solo el índice vectorial (los embeddings de referencia + metadatos) cambia. Esto es lo que permite que "añadir una especie nueva a una zona" sea una actualización de datos, no una actualización de app â€” ya lo capturaba §1 de esta nota ("crecimiento sin reentrenar"), pero ahora queda explícito que es exactamente el mecanismo de Merlin.
- **Cada paquete `.sqlite` es una unidad atómica de datos**, coherente con la portabilidad de archivo del punto 1 arriba: descargar = copiar un archivo; activar = abrirlo; desactivar/eliminar = borrarlo. No hay estado a medias ni migraciones de esquema entre regiones.
- **La app puede tener cero, uno o varios paquetes activos** segàºn las regiones que el usuario haya descargado â€” igual que Merlin permite tener varios "packs" regionales de aves instalados a la vez.

## 3. Diseño de las colecciones en Qdrant

```
Colección: anura_visual
  vector: 512-d, distancia = Cosine
  payload:
    familia, genero, especie          (keyword, indexado)
    individuo_id, observacion_id      (keyword)
    region_biogeografica              (keyword, indexado)  â† Antioquia / Guaviare
    lat, lon, altitud_msnm            (geo + float)
    fecha_hora                        (datetime)
    validado_por_experto              (bool, indexado)
    origen                            (keyword: campo | iNaturalist | GBIF)
    split                             (keyword: train | val | test)   â† evita fuga

Colección: anura_acustico
  vector: dimensión del modelo acàºstico, distancia = Cosine
  payload: mismos campos + tipo_canto, snr_db, duracion_s
```

Decisiones de diseño que importan:

- **Distancia coseno** con vectores L2-normalizados, coherente con [[Implementación de Triplet Loss]].
- **Colecciones separadas para visual y acàºstico.** Vectores de distinta dimensión y semántica no se mezclan en un índice; la fusión se hace después, a nivel de puntuación ([[Arquitectura Multimodal]]).
- **`split` en el payload** para poder filtrar el conjunto de test durante la evaluación. Sin esto es trivialmente fácil evaluar contra vectores que el modelo ya vio â€” la versión vectorial de la fuga de información.
- **àndices de payload** en los campos por los que se filtra (región, familia, validado). Qdrant permite filtrado con prefiltrado eficiente, y filtrar por región antes de buscar es exactamente lo que pide el diseño de paquetes biogeográficos.

## 4. Los paquetes regionales

La [[Estrategia de Construcción del Dataset|estrategia de dataset]] ya define el concepto: el usuario no descarga imágenes, descarga **vectores** empaquetados por región. Concretándolo:

```
paquete_antioquia_v1.anura
 â”œâ”€â”€ manifest.json        (versión modelo, dimensión, nº vectores, hash)
 â”œâ”€â”€ vectors.bin          (float16 o int8 cuantizado)
 â”œâ”€â”€ payload.db           (ObjectBox / SQLite: taxonomía, fichas, metadatos)
 â””â”€â”€ fichas/              (fichas técnicas de especie para consulta offline, RF-10)
```

Cálculo de tamaño (el dato que decide si esto es viable):

| Vectores | float32 | float16 | int8 (escalar) |
| --- | --- | --- | --- |
| 1 000 | 2,0 MB | 1,0 MB | 0,5 MB |
| 10 000 | 20 MB | 10 MB | 5 MB |
| 100 000 | 200 MB | 100 MB | 50 MB |

Con embeddings de 512 dimensiones, **decenas de miles de vectores caben sin problema en el móvil**. La restricción de 150 MB del RNF-05 aplica a los *modelos*; el paquete vectorial es un coste aparte y hay que sumarlo al presupuesto total de almacenamiento de la app. La cuantización escalar a int8 reduce 4à— con pérdida de precisión típicamente despreciable para recuperación Top-K.

## 5. Sincronización

```
        Mà“VIL (offline)                         SERVIDOR
   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
   â”‚ SQLite/Room          â”‚              â”‚ PostgreSQL         â”‚
   â”‚  observaciones       â”‚â”€â”€â”€â”€ push â”€â”€â”€â–¶â”‚  (Supabase)        â”‚
   â”‚  + vectores locales  â”‚   diferido   â”‚        â†“           â”‚
   â”‚                      â”‚              â”‚  Qdrant (índice)   â”‚
   â”‚ paquete regional     â”‚â—€â”€â”€â”€ pull â”€â”€â”€â”€â”‚  paquetes v2, v3â€¦  â”‚
   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   versionado â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

Reglas que evitan los problemas clásicos:

- **El vector se recalcula en el servidor**, no se confía en el del móvil, si la versión del modelo embarcado no coincide con la del servidor. El `manifest.json` lleva la versión precisamente para detectarlo.
- **Los paquetes son inmutables y versionados.** No se parchean en el dispositivo; se descarga el siguiente y se sustituye. Simplifica la depuración enormemente.
- **Solo entran al índice global las observaciones validadas.** Una observación sin validar es un dato pendiente, no memoria del sistema. Ver el flujo de curaduría en [[Historias de Usuario]] (HU-03).

## 6. Riesgo de sesgo que hay que vigilar

Si la base vectorial crece solo con lo que los usuarios fotografían, acaba dominada por las especies comunes y fotogénicas, y la recuperación por similitud empeora justo para las especies raras â€” que son las que más importan en conservación. Mitigación: mantener un **subconjunto curado y balanceado** como índice de referencia, separado del índice comunitario completo, y reportar las métricas de recuperación sobre el curado.

## 7. Qué falta por decidir o medir

- [x] **Elegir motor embebido para el móvil** â†’ decidido 2026-09-04: ObjectBox â†’ **revisado 2026-09-08 (C-6): SQLite + sqlite-vec** (§2). Pendiente corregir el RNF-10 y el resto de documentos que aàºn dicen "Qdrant local" u "ObjectBox" para que digan "base vectorial embebida (sqlite-vec)".
- [ ] Validar empíricamente sqlite-vec en el Galaxy A30 (latencia, memoria) con un paquete simulado de 10â€“50 k vectores.
- [ ] Confirmar la dimensión definitiva del embedding de EdgeNeXt-Tiny (ya no es 512-d de BioCLIP â€” depende de la capa de salida del student, por definir en el entrenamiento de destilación).
- [ ] Medir Recall@K real del índice frente al clasificador puro.
- [ ] Definir el formato y la política de versionado de los paquetes regionales `.sqlite` (estilo Merlin, §1.1).
- [ ] Medir latencia de bàºsqueda en el Galaxy A30 con el tamaño de paquete previsto.

## Referencias

- Qdrant â€” documentación y conceptos de colecciones, payload y cuantización. [qdrant.tech](https://qdrant.tech/documentation/)
- ObjectBox â€” base de datos vectorial embebida para Android/Java, con motor HNSW nativo. [objectbox.io/vector-database-for-ondevice-ai](https://objectbox.io/vector-database-for-ondevice-ai/) · [docs.objectbox.io/on-device-vector-search](https://docs.objectbox.io/on-device-vector-search)
- SQLite-Vector â€” bàºsqueda vectorial embebida multiplataforma, con librerías precompiladas para Android/iOS. [sqlite.ai/sqlite-vector](https://www.sqlite.ai/sqlite-vector) · [alexgarcia.xyz/sqlite-vec/android-ios.html](https://alexgarcia.xyz/sqlite-vec/android-ios.html)
- USearch â€” motor HNSW de un solo header en C++, con bindings a Java/Android entre otros lenguajes. [github.com/unum-cloud/usearch](https://github.com/unum-cloud/usearch)
- Malkov & Yashunin (2018). *Efficient and robust approximate nearest neighbor search using HNSW graphs*. [arXiv:1603.09320](https://arxiv.org/abs/1603.09320)



