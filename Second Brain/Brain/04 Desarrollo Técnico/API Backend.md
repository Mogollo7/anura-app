---
title: "API Backend"
proyecto: Anura
tipo: desarrollo-tÃ©cnico
estado: propuesta-de-diseÃ±o
tags: [anura, desarrollo, backend, api, supabase, fastapi]
---

# API Backend

[[Anura â€” Ãndice General]] Â· [[App MÃ³vil]] Â· [[Base Vectorial (SQLite-vec)]] Â· [[Infraestructura]]

> [!note] Estado
> Esta pÃ¡gina estaba vacÃ­a en Notion. Lo que sigue es una **propuesta de diseÃ±o** derivada de los requisitos ya escritos ([[Objetivos y Alcance]], RF-09 a RF-14, RNF-01, RNF-12, RNF-13) y de las decisiones de arquitectura de las [[Notas Originales â€” AÃ±adir Nueva InformaciÃ³n|notas originales]] (PostgreSQL + Supabase online, SQLite offline). AÃºn no es cÃ³digo existente.

## 1. Responsabilidades del backend

El backend **no** es solo un servidor de inferencia. Tiene cuatro trabajos distintos que conviene no mezclar:

1. **Inferencia (Fase 1, web).** Recibe imagen/audio, ejecuta segmentaciÃ³n + BioCLIP + fusiÃ³n, devuelve Top-3 con explicaciÃ³n. RNF-01: â‰¤ 3 s.
2. **Repositorio de observaciones.** CRUD de observaciones, salidas de campo, validaciÃ³n experta, mapa comunitario (RF-09, RF-11).
3. **DistribuciÃ³n de paquetes.** Sirve los paquetes regionales de vectores y fichas que el mÃ³vil descarga ([[Base Vectorial (SQLite-vec)]] Â§4) y las actualizaciones de modelo.
4. **Ingesta de sincronizaciÃ³n.** Recibe lo que el mÃ³vil generÃ³ offline, lo valida, lo indexa (RF-13).

## 2. Stack propuesto

| Capa | ElecciÃ³n | Por quÃ© |
| --- | --- | --- |
| API | **FastAPI** (Python) | El modelo vive en Python. Meter una API en otro lenguaje obliga a un servicio extra o a reescribir la inferencia. Tipado, validaciÃ³n con Pydantic y OpenAPI automÃ¡tico. |
| Datos relacionales | **PostgreSQL** vÃ­a **Supabase** | Ya decidido en las notas. Aporta auth, storage y Row Level Security sin construirlos. |
| Vectores | **Qdrant** | Servicio aparte, no dentro de Postgres. Ver nota dedicada. |
| Ficheros | **Supabase Storage** (S3-compatible) | ImÃ¡genes y audios originales. |
| Tareas asÃ­ncronas | **Celery + Redis** o cola de Supabase | Reindexado, generaciÃ³n de paquetes, reprocesado por lotes. No bloquear la peticiÃ³n HTTP. |
| Auth | **Supabase Auth** (JWT) | Roles: anÃ³nimo, usuario, investigador, validador, admin. |

> [!tip] Alternativa a considerar: `pgvector` en vez de Qdrant
> Si el volumen se mantiene en el orden de decenas de miles de vectores, **pgvector** (extensiÃ³n de Postgres, disponible en Supabase) evita operar un servicio adicional: una sola base de datos, transacciones consistentes entre metadatos y vectores, y una pieza menos que desplegar y monitorizar. Qdrant gana en filtrado avanzado y a escala mayor. Para un TFG con recursos limitados, pgvector es probablemente la decisiÃ³n sensata; Qdrant, la decisiÃ³n escalable. **Merece una comparaciÃ³n explÃ­cita antes de fijarla.**

## 3. Modelo de datos (esquema relacional mÃ­nimo)

```
usuarios â”€â”€â”¬â”€â”€ observaciones â”€â”€â”¬â”€â”€ medios (imagen | audio)
           â”‚                   â”œâ”€â”€ predicciones â”€â”€ evidencia_anatomica
           â”‚                   â”œâ”€â”€ validaciones (refutaciÃ³n experta, HU-03)
           â”‚                   â””â”€â”€ metadatos_ambientales
           â””â”€â”€ salidas_campo â”€â”€â”€â”€ (agrupa observaciones, HU-04)

especies â”€â”€â”¬â”€â”€ fichas_tecnicas (RF-10)
           â”œâ”€â”€ plantillas_morfologicas   â† caracteres fijos, Anexo C de la GuÃ­a CVAT
           â””â”€â”€ distribucion_geografica
```

Campos que no hay que olvidar porque estÃ¡n exigidos por requisitos ya escritos:

- `observaciones.geo_ofuscada` â€” RNF-13 obliga a ofuscar 1â€“5 km las coordenadas de especies amenazadas UICN **en las vistas pÃºblicas**. La coordenada real se guarda; lo que cambia es quÃ© devuelve la API segÃºn el rol de quien pregunta. Es una regla de autorizaciÃ³n, no un borrado.
- `predicciones.version_modelo` y `version_dataset` â€” sin esto es imposible interpretar resultados histÃ³ricos o reproducir un experimento ([[Experimentos y Resultados]]).
- `observaciones.estado` â€” `borrador | sincronizada | en_revision_experta | validada | rechazada`. El flujo de HU-03 depende de esta mÃ¡quina de estados.
- `identificationQualifier` â€” para exportaciÃ³n Darwin Core (HU-05): `cf.`, `aff.`, `sp.`

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

El campo `evidencia` es lo que implementa el RF-06 y la HU-03: la explicaciÃ³n por regiones anatÃ³micas, alimentada por las plantillas morfolÃ³gicas del Anexo C de la [[GuÃ­a CVAT â€” Ãndice|guÃ­a CVAT]]. Es lo que distingue a Anura de un clasificador cualquiera y no deberÃ­a tratarse como un extra opcional del contrato de la API.

### Observaciones y comunidad

```http
GET    /v1/observaciones            ?bbox=&especie=&desde=&hasta=&validado=
POST   /v1/observaciones
PATCH  /v1/observaciones/{id}
POST   /v1/observaciones/{id}/validacion     (rol: validador)
GET    /v1/especies/{id}/ficha               (RF-10, cacheable)
```

### SincronizaciÃ³n mÃ³vil

```http
POST /v1/sync/push
  { dispositivo_id, ultima_sync, observaciones: [...] }
  â†’ { aceptadas: [...], conflictos: [...], nueva_marca_sync }

GET  /v1/sync/paquetes?region=antioquia&version_actual=1
  â†’ { version: 2, url, hash, tamano_bytes, version_modelo, dimension_embedding }
```

Reglas de sincronizaciÃ³n que evitan los fallos habituales:

- **Idempotencia obligatoria.** Cada observaciÃ³n lleva un UUID generado en el dispositivo. Reenviar la misma no crea duplicados. En campo, con red intermitente, los reintentos son la norma, no la excepciÃ³n.
- **El servidor gana en conflicto de metadatos; el dispositivo gana en datos de campo.** Una validaciÃ³n experta hecha en web no debe ser sobrescrita por un mÃ³vil que llevaba tres dÃ­as sin conectarse, pero la temperatura del sustrato que anotÃ³ el investigador sÃ­ es la buena.
- **Rechazo explÃ­cito y legible.** Si el paquete del mÃ³vil se generÃ³ con un modelo obsoleto, la respuesta debe decirlo con un cÃ³digo accionable, no fallar en silencio.

### ExportaciÃ³n cientÃ­fica

```http
POST /v1/export/dwc     { salidas_campo: [...] }
  â†’ 202 { tarea_id }        (asÃ­ncrono: genera occurrence.txt + eml.xml + meta.xml)
GET  /v1/export/{tarea_id}
```

Implementa HU-05. La validaciÃ³n previa de campos obligatorios de GBIF/SiB debe ocurrir **antes** de generar el archivo y devolver un reporte de quÃ© registros estÃ¡n incompletos.

## 5. Requisitos no funcionales aplicados a la API

| Requisito | ImplicaciÃ³n concreta |
| --- | --- |
| RNF-01 (â‰¤ 3 s) | Modelo cargado en memoria al arrancar, no por peticiÃ³n. Inferencia en proceso aparte del servidor web si hay GPU. Medir p95, no la media. |
| RNF-12 (TLS 1.3) | TerminaciÃ³n TLS en el proxy; HSTS; rechazar HTTP. |
| RNF-13 (ofuscaciÃ³n) | Middleware que aplica el buffer geogrÃ¡fico segÃºn rol + estado UICN de la especie **en la serializaciÃ³n**, para que ningÃºn endpoint pueda filtrarla por descuido. |
| RNF-14 (permisos mÃ­nimos) | La API no debe exigir cuenta para identificar: el uso anÃ³nimo es parte del valor de ciencia ciudadana. |

AdemÃ¡s: **lÃ­mite de tasa** en `/identify` (es el endpoint caro) y **tamaÃ±o mÃ¡ximo de subida** coherente con el peso de imagen definido en la estrategia de dataset (~70â€“100 KB en V2, hasta ~300 KB en V1).

## 6. QuÃ© falta por decidir o medir

- [ ] Decidir **pgvector vs. Qdrant** (Â§2) â€” afecta a coste, despliegue y a [[Infraestructura]].
- [ ] Definir si la inferencia va en el mismo servicio que la API o en uno separado.
- [ ] Escribir el contrato OpenAPI antes de implementar (permite desarrollar app y backend en paralelo).
- [ ] Definir la polÃ­tica de retenciÃ³n de imÃ¡genes originales (peso y privacidad).
- [ ] Confirmar los tÃ©rminos Darwin Core exactos a mapear con SiB Colombia.

Ver tambiÃ©n: [[App MÃ³vil]] Â· [[Flujo de Datos y SincronizaciÃ³n]] Â· [[Riesgos del Proyecto]]



