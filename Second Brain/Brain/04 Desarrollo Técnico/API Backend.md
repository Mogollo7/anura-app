---
title: "API Backend"
proyecto: Anura
tipo: desarrollo-técnico
estado: propuesta-de-diseño
tags: [anura, desarrollo, backend, api, supabase, fastapi]
---

# API Backend

[[Anura â€” àndice General]] · [[App Móvil]] · [[Base Vectorial (SQLite-vec)]] · [[Infraestructura]]

> [!note] Estado
> Esta página estaba vacía en Notion. Lo que sigue es una **propuesta de diseño** derivada de los requisitos ya escritos ([[Objetivos y Alcance]], RF-09 a RF-14, RNF-01, RNF-12, RNF-13) y de las decisiones de arquitectura de las [[Notas Originales â€” Añadir Nueva Información|notas originales]] (PostgreSQL + Supabase online, SQLite offline). Aàºn no es código existente.

## 1. Responsabilidades del backend

El backend **no** es solo un servidor de inferencia. Tiene cuatro trabajos distintos que conviene no mezclar:

1. **Inferencia (Fase 1, web).** Recibe imagen/audio, ejecuta segmentación + BioCLIP + fusión, devuelve Top-3 con explicación. RNF-01: â‰¤ 3 s.
2. **Repositorio de observaciones.** CRUD de observaciones, salidas de campo, validación experta, mapa comunitario (RF-09, RF-11).
3. **Distribución de paquetes.** Sirve los paquetes regionales de vectores y fichas que el móvil descarga ([[Base Vectorial (SQLite-vec)]] §4) y las actualizaciones de modelo.
4. **Ingesta de sincronización.** Recibe lo que el móvil generó offline, lo valida, lo indexa (RF-13).

## 2. Stack propuesto

| Capa | Elección | Por qué |
| --- | --- | --- |
| API | **FastAPI** (Python) | El modelo vive en Python. Meter una API en otro lenguaje obliga a un servicio extra o a reescribir la inferencia. Tipado, validación con Pydantic y OpenAPI automático. |
| Datos relacionales | **PostgreSQL** vía **Supabase** | Ya decidido en las notas. Aporta auth, storage y Row Level Security sin construirlos. |
| Vectores | **Qdrant** | Servicio aparte, no dentro de Postgres. Ver nota dedicada. |
| Ficheros | **Supabase Storage** (S3-compatible) | Imágenes y audios originales. |
| Tareas asíncronas | **Celery + Redis** o cola de Supabase | Reindexado, generación de paquetes, reprocesado por lotes. No bloquear la petición HTTP. |
| Auth | **Supabase Auth** (JWT) | Roles: anónimo, usuario, investigador, validador, admin. |

> [!tip] Alternativa a considerar: `pgvector` en vez de Qdrant
> Si el volumen se mantiene en el orden de decenas de miles de vectores, **pgvector** (extensión de Postgres, disponible en Supabase) evita operar un servicio adicional: una sola base de datos, transacciones consistentes entre metadatos y vectores, y una pieza menos que desplegar y monitorizar. Qdrant gana en filtrado avanzado y a escala mayor. Para un TFG con recursos limitados, pgvector es probablemente la decisión sensata; Qdrant, la decisión escalable. **Merece una comparación explícita antes de fijarla.**

## 3. Modelo de datos (esquema relacional mínimo)

```
usuarios â”€â”€â”¬â”€â”€ observaciones â”€â”€â”¬â”€â”€ medios (imagen | audio)
           â”‚                   â”œâ”€â”€ predicciones â”€â”€ evidencia_anatomica
           â”‚                   â”œâ”€â”€ validaciones (refutación experta, HU-03)
           â”‚                   â””â”€â”€ metadatos_ambientales
           â””â”€â”€ salidas_campo â”€â”€â”€â”€ (agrupa observaciones, HU-04)

especies â”€â”€â”¬â”€â”€ fichas_tecnicas (RF-10)
           â”œâ”€â”€ plantillas_morfologicas   â† caracteres fijos, Anexo C de la Guía CVAT
           â””â”€â”€ distribucion_geografica
```

Campos que no hay que olvidar porque están exigidos por requisitos ya escritos:

- `observaciones.geo_ofuscada` â€” RNF-13 obliga a ofuscar 1â€“5 km las coordenadas de especies amenazadas UICN **en las vistas pàºblicas**. La coordenada real se guarda; lo que cambia es qué devuelve la API segàºn el rol de quien pregunta. Es una regla de autorización, no un borrado.
- `predicciones.version_modelo` y `version_dataset` â€” sin esto es imposible interpretar resultados históricos o reproducir un experimento ([[Experimentos y Resultados]]).
- `observaciones.estado` â€” `borrador | sincronizada | en_revision_experta | validada | rechazada`. El flujo de HU-03 depende de esta máquina de estados.
- `identificationQualifier` â€” para exportación Darwin Core (HU-05): `cf.`, `aff.`, `sp.`

## 4. Endpoints principales

### Inferencia

```http
POST /v1/identify
  multipart: imagen(es) + audio? + metadatos(lat, lon, altitud, fecha)
  â†’ 200 {
      observacion_id,
      top3: [{familia, genero, especie, confianza}],
      segmentacion: { mascaras_url, regiones: [{clase, area_px, confianza}] },
      evidencia: [{region, caracter, valor_observado, valor_esperado, veredicto}],
      open_set: { es_desconocida: bool, score, umbral },
      vecinos_similares: [{observacion_id, especie, similitud}]
    }
```

El campo `evidencia` es lo que implementa el RF-06 y la HU-03: la explicación por regiones anatómicas, alimentada por las plantillas morfológicas del Anexo C de la [[Guía CVAT â€” àndice|guía CVAT]]. Es lo que distingue a Anura de un clasificador cualquiera y no debería tratarse como un extra opcional del contrato de la API.

### Observaciones y comunidad

```http
GET    /v1/observaciones            ?bbox=&especie=&desde=&hasta=&validado=
POST   /v1/observaciones
PATCH  /v1/observaciones/{id}
POST   /v1/observaciones/{id}/validacion     (rol: validador)
GET    /v1/especies/{id}/ficha               (RF-10, cacheable)
```

### Sincronización móvil

```http
POST /v1/sync/push
  { dispositivo_id, ultima_sync, observaciones: [...] }
  â†’ { aceptadas: [...], conflictos: [...], nueva_marca_sync }

GET  /v1/sync/paquetes?region=antioquia&version_actual=1
  â†’ { version: 2, url, hash, tamano_bytes, version_modelo, dimension_embedding }
```

Reglas de sincronización que evitan los fallos habituales:

- **Idempotencia obligatoria.** Cada observación lleva un UUID generado en el dispositivo. Reenviar la misma no crea duplicados. En campo, con red intermitente, los reintentos son la norma, no la excepción.
- **El servidor gana en conflicto de metadatos; el dispositivo gana en datos de campo.** Una validación experta hecha en web no debe ser sobrescrita por un móvil que llevaba tres días sin conectarse, pero la temperatura del sustrato que anotó el investigador sí es la buena.
- **Rechazo explícito y legible.** Si el paquete del móvil se generó con un modelo obsoleto, la respuesta debe decirlo con un código accionable, no fallar en silencio.

### Exportación científica

```http
POST /v1/export/dwc     { salidas_campo: [...] }
  â†’ 202 { tarea_id }        (asíncrono: genera occurrence.txt + eml.xml + meta.xml)
GET  /v1/export/{tarea_id}
```

Implementa HU-05. La validación previa de campos obligatorios de GBIF/SiB debe ocurrir **antes** de generar el archivo y devolver un reporte de qué registros están incompletos.

## 5. Requisitos no funcionales aplicados a la API

| Requisito | Implicación concreta |
| --- | --- |
| RNF-01 (â‰¤ 3 s) | Modelo cargado en memoria al arrancar, no por petición. Inferencia en proceso aparte del servidor web si hay GPU. Medir p95, no la media. |
| RNF-12 (TLS 1.3) | Terminación TLS en el proxy; HSTS; rechazar HTTP. |
| RNF-13 (ofuscación) | Middleware que aplica el buffer geográfico segàºn rol + estado UICN de la especie **en la serialización**, para que ningàºn endpoint pueda filtrarla por descuido. |
| RNF-14 (permisos mínimos) | La API no debe exigir cuenta para identificar: el uso anónimo es parte del valor de ciencia ciudadana. |

Además: **límite de tasa** en `/identify` (es el endpoint caro) y **tamaño máximo de subida** coherente con el peso de imagen definido en la estrategia de dataset (~70â€“100 KB en V2, hasta ~300 KB en V1).

## 6. Qué falta por decidir o medir

- [ ] Decidir **pgvector vs. Qdrant** (§2) â€” afecta a coste, despliegue y a [[Infraestructura]].
- [ ] Definir si la inferencia va en el mismo servicio que la API o en uno separado.
- [ ] Escribir el contrato OpenAPI antes de implementar (permite desarrollar app y backend en paralelo).
- [ ] Definir la política de retención de imágenes originales (peso y privacidad).
- [ ] Confirmar los términos Darwin Core exactos a mapear con SiB Colombia.

Ver también: [[App Móvil]] · [[Flujo de Datos y Sincronización]] · [[Riesgos del Proyecto]]



