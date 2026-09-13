---
title: "Base Vectorial (SQLite-vec)"
proyecto: Anura
tipo: desarrollo-tÃ©cnico
estado: motor-mÃ³vil-firmado-sqlite-vec-c15
tags: [anura, desarrollo, sqlite-vec, qdrant, base-vectorial, hnsw, offline, merlin, knn]
---

# Base Vectorial (SQLite-vec)

[[Anura â€” Ãndice General]] Â· [[Modelo de VisiÃ³n â€” BioCLIP]] Â· [[App MÃ³vil]] Â· [[Open-Set Recognition]] Â· [[Escalabilidad]]

> [!success] Motor de producciÃ³n on-device: SQLite-vec (Ruta B firmada en C-15, 2026-09-13)
> El mÃ³vil (offline) usa **SQLite + extensiÃ³n sqlite-vec** como motor vectorial embebido â€” es la Ruta B: k-NN sobre embeddings del encoder BioCLIP, con paquetes regionales `.sqlite` descargables por zona (patrÃ³n Merlin Bird ID, Cornell Lab). Qdrant sigue siendo el motor del **servidor** (Fase 1, comunidad completa), nunca corre en el dispositivo â€” ver por quÃ© en el aviso original de abajo. La comparaciÃ³n empÃ­rica k-NN vs. clasificador softmax (Ruta A) estÃ¡ en [[Experimentos y Resultados]] (EXP-014, 2026-09-13): la ganancia de Ruta B no es solo de precisiÃ³n, es la evidencia visual "por quÃ©" y el crecimiento sin reentrenar.

> [!danger] Hallazgo crÃ­tico (histÃ³rico): Qdrant **no puede correr embebido en el mÃ³vil**
> Toda la documentaciÃ³n del proyecto asume una "base vectorial local" en el dispositivo usando Qdrant (RNF-10, [[Notas Originales â€” SegmentaciÃ³n SemÃ¡ntica y MetodologÃ­a Anura|notas originales]], [[Estrategia de ConstrucciÃ³n del Dataset]]). **Eso no es posible tal como estÃ¡ planteado.** Qdrant es un servidor: se distribuye como binario/contenedor de cientos de MB y se accede por red. No existe una librerÃ­a embebible para Android de uso pÃºblico â€” *Qdrant Edge*, la variante en proceso, se anunciÃ³ en julio de 2025 en beta privada y no estÃ¡ disponible de forma general.
>
> **Esto no rompe la arquitectura, obliga a partirla en dos, y ya hay una alternativa concreta para el mÃ³vil.** Ver Â§2 â€” no es un hueco sin resolver, es una decisiÃ³n con recomendaciÃ³n firme.

## 1. QuÃ© aporta una base vectorial a Anura

La idea de fondo (bien capturada en las notas originales) es que el sistema tenga **memoria de ejemplares**, no solo un clasificador. Cada observaciÃ³n validada se almacena como vector + metadatos:

```
Vector (embedding BioCLIP 512-d)
 â”œâ”€â”€ Familia / GÃ©nero / Especie
 â”œâ”€â”€ Imagen (referencia)
 â”œâ”€â”€ Coordenadas, altitud, fecha
 â”œâ”€â”€ Embedding acÃºstico (si existe)
 â””â”€â”€ Contexto ambiental
```

De ahÃ­ salen tres capacidades que un clasificador cerrado no da:

1. **Evidencia por ejemplos.** "Se parece a estas 5 observaciones confirmadas de *Boana cinerea*" es una justificaciÃ³n mucho mÃ¡s convincente para un herpetÃ³logo que "87 % de probabilidad".
2. **Crecimiento sin reentrenar.** AÃ±adir una especie nueva = aÃ±adir sus vectores. El modelo no se toca. Es la base de [[Escalabilidad]].
3. **DetecciÃ³n de desconocidos.** Si el vecino mÃ¡s cercano estÃ¡ lejos, probablemente no es ninguna especie del catÃ¡logo â†’ [[Open-Set Recognition]].

## 2. Arquitectura resultante: dos motores, un mismo espacio vectorial

| | **Servidor (Fase 1)** | **Dispositivo (Fase 2, offline)** |
| --- | --- | --- |
| Motor | **Qdrant** | **SQLite + sqlite-vec** âœ… (revisado 2026-09-08) |
| Contenido | Todas las observaciones de la comunidad | Paquete regional descargado + observaciones locales |
| Ãndice | HNSW completo | K-NN sobre BLOBs vÃ­a `sqlite-vec`, escala de milesâ€“decenas de miles de vectores |
| Escritura | Continua, multiusuario | Local, sincroniza despuÃ©s |
| Rol | Fuente de verdad, reindexado, analÃ­tica | Inferencia y recuperaciÃ³n en campo sin red |

> [!important] DecisiÃ³n revisada (2026-09-08, C-6): SQLite + sqlite-vec reemplaza a ObjectBox
> La recomendaciÃ³n anterior de esta nota (ObjectBox) queda **revertida por decisiÃ³n directa del autor**. El argumento de fondo no es solo "una base menos que sincronizar" â€” es que el modelo de **paquetes regionales modulares al estilo Merlin** (Cornell Lab, la app de identificaciÃ³n de aves que sirve de inspiraciÃ³n directa para Anura) encaja mejor con el modelo de archivo de SQLite que con el de ObjectBox. Tres razones de ingenierÃ­a, en orden de peso:
>
> 1. **Portabilidad absoluta de archivos independientes.** Un `.sqlite` es un contenedor autocontenido y estandarizado: descargar el paquete de Antioquia o Caldas es bajar **un Ãºnico archivo** que la app abre al instante bajo demanda (llamada nativa) y borra por completo con `file.delete()` al cambiar de regiÃ³n. ObjectBox, al ser una base orientada a objetos con esquema compilado y gestiÃ³n interna de directorios vÃ­a memory-mapped files, no ofrece ese "plug-and-play" de mÃºltiples bases aisladas descargadas en caliente desde la red â€” es un solo almacÃ©n persistente, no pensado para montar/desmontar paquetes intercambiables como unidades atÃ³micas.
> 2. **Consultas hÃ­bridas de metadatos y vectores en una sola llamada local.** SQLite conserva su estructura relacional tradicional; `sqlite-vec` aÃ±ade la bÃºsqueda vectorial sobre esa misma base. Esto permite vincular la ruta taxonÃ³mica (Familiaâ†’GÃ©neroâ†’Especie) con los embeddings de EdgeNeXt-Tiny y **filtrar por regiÃ³n/subregiÃ³n antes de calcular distancia vectorial**, en una Ãºnica consulta optimizada â€” exactamente el patrÃ³n que exige el diseÃ±o de paquetes biogeogrÃ¡ficos de Â§4.
> 3. **Control estricto de recursos en gama baja.** `sqlite-vec` opera directamente sobre el motor C de SQLite con huella de memoria muy reducida (~30 MB por defecto), lo que garantiza que el **Samsung Galaxy A30** (dispositivo de referencia, ver [[OptimizaciÃ³n para Inferencia en MÃ³vil]]) ejecute las consultas K-NN en milisegundos sin disparar el consumo de RAM ni congelar el hilo de UI.
>
> USearch queda descartado por el mismo argumento de integraciÃ³n manual en Android que antes se usaba contra sqlite-vec (Â§ tabla histÃ³rica mÃ¡s abajo, conservada como referencia).

### Tabla comparativa histÃ³rica (previa a la revisiÃ³n del 08 sep â€” conservada como referencia)

| | ObjectBox (recomendaciÃ³n anterior) | **sqlite-vec** âœ… decisiÃ³n vigente | USearch |
| --- | --- | --- | --- |
| QuÃ© es | Base de datos embebida orientada a objetos, con motor HNSW **nativo** integrado | ExtensiÃ³n de SQLite en C, cargable como librerÃ­a | LibrerÃ­a de bÃºsqueda vectorial de un solo header en C++, con bindings a ~10 lenguajes |
| Soporte Android/Kotlin | Oficial y de primera clase â€” `objectbox-android`, API Kotlin idiomÃ¡tica | LibrerÃ­as precompiladas publicadas para Android e iOS desde v0.1.2; se integran como `.so`/loadable extension | Compila para Android (JNI); no trae wrapper Kotlin propio |
| Portabilidad de paquetes regionales como archivos independientes | DÃ©bil â€” almacÃ©n Ãºnico gestionado internamente, no pensado para montar/desmontar bases aisladas en caliente | **Fuerte â€” es exactamente el patrÃ³n `.sqlite` portÃ¡til que exige el diseÃ±o estilo Merlin** | DÃ©bil â€” solo el Ã­ndice, sin modelo de archivo autocontenido |
| Persistencia de metadatos junto al vector | Integrada (objetos + vector) | Integrada â€” vector y fila conviven en la misma base SQLite | No integrada â€” metadatos aparte, enlazados por ID |
| Footprint en gama baja | Compite con motores de servidor, pero como almacÃ©n Ãºnico, no por paquete | Muy ligero (~30 MB de huella por defecto), directo sobre el motor C de SQLite | HNSW en C++ puro, eficiente pero exige capa JNI propia |
| Licencia | Apache-2.0 (nÃºcleo) | MIT | Apache-2.0 |

Sigue pendiente la validaciÃ³n empÃ­rica: cargar un paquete regional simulado (10â€“50 k vectores) con `sqlite-vec` y medir latencia de bÃºsqueda y footprint de memoria **en el Galaxy A30**, antes de comprometerse en cÃ³digo de producciÃ³n.

CondiciÃ³n imprescindible en cualquier caso: **el mismo modelo debe generar los embeddings en ambos lados** â€” ahora **EdgeNeXt-Tiny**, no BioCLIP directo (ver el pivote registrado en [[Modelo de VisiÃ³n â€” BioCLIP]] y en [[Inconsistencias y Decisiones Pendientes]] C-5). Vectores de modelos distintos no se pueden comparar.

## 1.1 Modelo operativo: backbone congelado + embeddings descargables por zona (estilo Merlin)

Esta es la pieza que amarra todo el diseÃ±o y conviene dejarla explÃ­cita, porque es la que justifica por quÃ© sqlite-vec es la opciÃ³n correcta y no solo una preferencia de formato:

```
1. El modelo (EdgeNeXt-Tiny) estÃ¡ CONGELADO en el APK â€” no cambia con la regiÃ³n.
2. Lo que varÃ­a por zona son los EMBEDDINGS: se descargan, se editan/actualizan
   y se aplican como paquetes .sqlite independientes, filtrados geogrÃ¡ficamente.
3. InspiraciÃ³n directa: Merlin Bird ID (Cornell Lab) â€” el modelo de identificaciÃ³n
   viaja fijo en la app; los "paquetes regionales" de especies por zona son los
   que se descargan, activan o eliminan segÃºn dÃ³nde estÃ© el usuario.
```

Consecuencias directas de este modelo para el diseÃ±o:

- **El backbone nunca se reentrena ni se redistribuye por regiÃ³n.** Solo el Ã­ndice vectorial (los embeddings de referencia + metadatos) cambia. Esto es lo que permite que "aÃ±adir una especie nueva a una zona" sea una actualizaciÃ³n de datos, no una actualizaciÃ³n de app â€” ya lo capturaba Â§1 de esta nota ("crecimiento sin reentrenar"), pero ahora queda explÃ­cito que es exactamente el mecanismo de Merlin.
- **Cada paquete `.sqlite` es una unidad atÃ³mica de datos**, coherente con la portabilidad de archivo del punto 1 arriba: descargar = copiar un archivo; activar = abrirlo; desactivar/eliminar = borrarlo. No hay estado a medias ni migraciones de esquema entre regiones.
- **La app puede tener cero, uno o varios paquetes activos** segÃºn las regiones que el usuario haya descargado â€” igual que Merlin permite tener varios "packs" regionales de aves instalados a la vez.

## 3. DiseÃ±o de las colecciones en Qdrant

```
ColecciÃ³n: anura_visual
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

ColecciÃ³n: anura_acustico
  vector: dimensiÃ³n del modelo acÃºstico, distancia = Cosine
  payload: mismos campos + tipo_canto, snr_db, duracion_s
```

Decisiones de diseÃ±o que importan:

- **Distancia coseno** con vectores L2-normalizados, coherente con [[ImplementaciÃ³n de Triplet Loss]].
- **Colecciones separadas para visual y acÃºstico.** Vectores de distinta dimensiÃ³n y semÃ¡ntica no se mezclan en un Ã­ndice; la fusiÃ³n se hace despuÃ©s, a nivel de puntuaciÃ³n ([[Arquitectura Multimodal]]).
- **`split` en el payload** para poder filtrar el conjunto de test durante la evaluaciÃ³n. Sin esto es trivialmente fÃ¡cil evaluar contra vectores que el modelo ya vio â€” la versiÃ³n vectorial de la fuga de informaciÃ³n.
- **Ãndices de payload** en los campos por los que se filtra (regiÃ³n, familia, validado). Qdrant permite filtrado con prefiltrado eficiente, y filtrar por regiÃ³n antes de buscar es exactamente lo que pide el diseÃ±o de paquetes biogeogrÃ¡ficos.

## 4. Los paquetes regionales

La [[Estrategia de ConstrucciÃ³n del Dataset|estrategia de dataset]] ya define el concepto: el usuario no descarga imÃ¡genes, descarga **vectores** empaquetados por regiÃ³n. ConcretÃ¡ndolo:

```
paquete_antioquia_v1.anura
 â”œâ”€â”€ manifest.json        (versiÃ³n modelo, dimensiÃ³n, nÂº vectores, hash)
 â”œâ”€â”€ vectors.bin          (float16 o int8 cuantizado)
 â”œâ”€â”€ payload.db           (ObjectBox / SQLite: taxonomÃ­a, fichas, metadatos)
 â””â”€â”€ fichas/              (fichas tÃ©cnicas de especie para consulta offline, RF-10)
```

CÃ¡lculo de tamaÃ±o (el dato que decide si esto es viable):

| Vectores | float32 | float16 | int8 (escalar) |
| --- | --- | --- | --- |
| 1 000 | 2,0 MB | 1,0 MB | 0,5 MB |
| 10 000 | 20 MB | 10 MB | 5 MB |
| 100 000 | 200 MB | 100 MB | 50 MB |

Con embeddings de 512 dimensiones, **decenas de miles de vectores caben sin problema en el mÃ³vil**. La restricciÃ³n de 150 MB del RNF-05 aplica a los *modelos*; el paquete vectorial es un coste aparte y hay que sumarlo al presupuesto total de almacenamiento de la app. La cuantizaciÃ³n escalar a int8 reduce 4Ã— con pÃ©rdida de precisiÃ³n tÃ­picamente despreciable para recuperaciÃ³n Top-K.

## 5. SincronizaciÃ³n

```
        MÃ“VIL (offline)                         SERVIDOR
   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
   â”‚ SQLite/Room          â”‚              â”‚ PostgreSQL         â”‚
   â”‚  observaciones       â”‚â”€â”€â”€â”€ push â”€â”€â”€â–¶â”‚  (Supabase)        â”‚
   â”‚  + vectores locales  â”‚   diferido   â”‚        â†“           â”‚
   â”‚                      â”‚              â”‚  Qdrant (Ã­ndice)   â”‚
   â”‚ paquete regional     â”‚â—€â”€â”€â”€ pull â”€â”€â”€â”€â”‚  paquetes v2, v3â€¦  â”‚
   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   versionado â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

Reglas que evitan los problemas clÃ¡sicos:

- **El vector se recalcula en el servidor**, no se confÃ­a en el del mÃ³vil, si la versiÃ³n del modelo embarcado no coincide con la del servidor. El `manifest.json` lleva la versiÃ³n precisamente para detectarlo.
- **Los paquetes son inmutables y versionados.** No se parchean en el dispositivo; se descarga el siguiente y se sustituye. Simplifica la depuraciÃ³n enormemente.
- **Solo entran al Ã­ndice global las observaciones validadas.** Una observaciÃ³n sin validar es un dato pendiente, no memoria del sistema. Ver el flujo de curadurÃ­a en [[Historias de Usuario]] (HU-03).

## 6. Riesgo de sesgo que hay que vigilar

Si la base vectorial crece solo con lo que los usuarios fotografÃ­an, acaba dominada por las especies comunes y fotogÃ©nicas, y la recuperaciÃ³n por similitud empeora justo para las especies raras â€” que son las que mÃ¡s importan en conservaciÃ³n. MitigaciÃ³n: mantener un **subconjunto curado y balanceado** como Ã­ndice de referencia, separado del Ã­ndice comunitario completo, y reportar las mÃ©tricas de recuperaciÃ³n sobre el curado.

## 7. QuÃ© falta por decidir o medir

- [x] **Elegir motor embebido para el mÃ³vil** â†’ decidido 2026-09-04: ObjectBox â†’ **revisado 2026-09-08 (C-6): SQLite + sqlite-vec** (Â§2). Pendiente corregir el RNF-10 y el resto de documentos que aÃºn dicen "Qdrant local" u "ObjectBox" para que digan "base vectorial embebida (sqlite-vec)".
- [ ] Validar empÃ­ricamente sqlite-vec en el Galaxy A30 (latencia, memoria) con un paquete simulado de 10â€“50 k vectores.
- [ ] Confirmar la dimensiÃ³n definitiva del embedding de EdgeNeXt-Tiny (ya no es 512-d de BioCLIP â€” depende de la capa de salida del student, por definir en el entrenamiento de destilaciÃ³n).
- [ ] Medir Recall@K real del Ã­ndice frente al clasificador puro.
- [ ] Definir el formato y la polÃ­tica de versionado de los paquetes regionales `.sqlite` (estilo Merlin, Â§1.1).
- [ ] Medir latencia de bÃºsqueda en el Galaxy A30 con el tamaÃ±o de paquete previsto.

## Referencias

- Qdrant â€” documentaciÃ³n y conceptos de colecciones, payload y cuantizaciÃ³n. [qdrant.tech](https://qdrant.tech/documentation/)
- ObjectBox â€” base de datos vectorial embebida para Android/Java, con motor HNSW nativo. [objectbox.io/vector-database-for-ondevice-ai](https://objectbox.io/vector-database-for-ondevice-ai/) Â· [docs.objectbox.io/on-device-vector-search](https://docs.objectbox.io/on-device-vector-search)
- SQLite-Vector â€” bÃºsqueda vectorial embebida multiplataforma, con librerÃ­as precompiladas para Android/iOS. [sqlite.ai/sqlite-vector](https://www.sqlite.ai/sqlite-vector) Â· [alexgarcia.xyz/sqlite-vec/android-ios.html](https://alexgarcia.xyz/sqlite-vec/android-ios.html)
- USearch â€” motor HNSW de un solo header en C++, con bindings a Java/Android entre otros lenguajes. [github.com/unum-cloud/usearch](https://github.com/unum-cloud/usearch)
- Malkov & Yashunin (2018). *Efficient and robust approximate nearest neighbor search using HNSW graphs*. [arXiv:1603.09320](https://arxiv.org/abs/1603.09320)



