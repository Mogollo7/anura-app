---
title: "Plan del Backend Real"
tags: [admin, anura, backend, despliegue, plan]
created: 2026-09-26
status: draft
---

# Plan del Backend Real

Cómo pasar el Admin de prototipo a sistema real en sus tres áreas conectadas (**Modelo, Operación y Sistema**) y cómo enlazarlo con el teléfono. Parte de lo que ya existe en `D:\server\Anura` y del resultado de [[Prueba Real del Creador de Paquetes]]. El Admin muestra este mismo plan en *Sistema → Plan de conexión* (`src/lib/system/connection-plan.ts`). Si cambia una etapa, se cambia en los dos lados.

Inicio, Analítica y App (usuarios de campo, dispositivos, observaciones) siguen simulados hasta las etapas C3–C4. Contenido (ficha pública, Explorador, destacados) es un bloque nuevo, **K**: hoy vive escrito a mano en el código de la app y no lo administra nadie. Detalle en [[Ficha Publica, Explorador y Destacados]].

## Arquitectura de dos máquinas (decisión del autor, 2026-09-27)

**No es una etapa transitoria: es la forma final.** Dos máquinas con roles distintos, permanentes:

```text
┌─────────────────────────────┐         HTTPS / túnel        ┌──────────────────────────────┐
│  SERVIDOR (Hostinger, pago)  │ ◄──────────────────────────► │  MODEL-SERVICE (este PC, GPU)  │
│  Liviano, sin GPU             │                              │  Todo lo pesado                │
│                               │                              │                                │
│  gateway, auth, observation,  │                              │  encoder_anura (worker M2)      │
│  geo, thumbnail, explorer,    │                              │  BioCLIP 2.5 (auditoría)        │
│  notification, admin-api,     │                              │  creador de paquetes (M3)       │
│  Postgres, Redis, MinIO       │                              │  Grafana/Prometheus del GPU      │
└─────────────────────────────┘                              └──────────────────────────────┘
```

**Por qué:** entrenar y probar el modelo de visión es pesado — RAM, GPU, ida y vuelta constante. Pagar esa capacidad en un servidor rentado sale más caro que usar la RTX 4050 que ya se tiene. `ai-service` (BioCLIP 2.5 + el clasificador), el worker de embeddings (M2) y el creador de paquetes (M3) son **un solo servicio, `model-service`**, y viven en este PC, no en el servidor pago.

- El servidor nunca corre torch ni carga un modelo. Le habla al `model-service` por HTTP (`POST /encode`, `POST /audit`, `POST /jobs/{id}/run`) a través de un túnel saliente (Cloudflare Tunnel o Tailscale) — el PC no necesita IP pública ni puerto abierto.
- Si el PC está apagado, el servidor sigue vivo (login, observaciones, catálogo, ficha pública): solo se cae lo que depende de calcular (nuevos embeddings, auditoría de rechazos, compilar un release).
- `docker-compose.yml` de `D:\server\Anura` **ya está separado (E0, 2026-09-27)**: `docker-compose.server.yml` (sin GPU) y `docker-compose.model.yml` (`model-service`, con la GPU). Detalle y cómo se levanta en [[#E0 · Separación hecha (2026-09-27)]].
- Esta separación **ya estaba insinuada** en [[Arquitectura Desacoplada]] ("teléfono sin red" / "PC local, cuando hay red") — lo que cambia aquí es que el PC local **no es el mismo servidor**, es una tercera máquina.

## Meta inmediata (2026-09-27): el servidor en este PC, hablando con el teléfono

Hostinger queda para después — no hace falta para probar que el sistema funciona de punta a punta. La meta de ahora es: servidor + `model-service` corriendo en este PC, y el teléfono real descargando un release y sincronizando contra ellos, en la misma red (o por túnel si se prueba fuera de casa).

Secuencia exacta para llegar ahí, sin desviarse a nada de Hostinger todavía:

```text
E0 → S1 → M1 → M2 → K → M3 → M5 → M4 → L1 → C1 → C2
```

`S2` (Grafana/Prometheus) y `S3` (mudar a Hostinger) quedan fuera de esta meta: no hacen falta para que el teléfono hable con el servidor, se retoman después. `C3`–`C6` (sincronizar observaciones, avisos, publicar en Play) también son de después: la meta es que el teléfono **reciba** un release y lo instale, no todavía que reporte de vuelta.

**L1 — nueva, la pieza que faltaba:** hacer que el teléfono llegue al servidor sin publicarlo en internet.
- Más simple: PC y teléfono en la misma red Wi-Fi; la app apunta a `http://<ip-lan-del-pc>:PUERTO`. Sirve para probar en casa, cero configuración de red.
- Para probar fuera de esa red sin esperar a Hostinger: un túnel gratis (Cloudflare Tunnel o `ngrok`) apunta a este PC con una URL pública temporal — el mismo mecanismo que se usará después con `model-service`, aplicado ahora también al servidor.
- La URL base del servidor **no va escrita en el código de la app**: es un valor de configuración (`BuildConfig` / `local.properties` o una pantalla de desarrollador), para no tener que recompilar la app cuando el servidor se mude a Hostinger.

## Qué hay hoy (verificado el 2026-09-26, corregido 2026-09-27)

| Pieza | Estado |
| --- | --- |
| `docker-compose.yml` | Túnel de Cloudflare, Nginx Proxy Manager, Postgres/PostGIS, Redis, MinIO, `db-migrate` y pgAdmin. |
| `auth-service` | JWT + Google OAuth, para la app web. |
| `observation-service` | Observaciones y fotos en MinIO. |
| `geo-service` | PostGIS. |
| `thumbnail-service` | Miniaturas. |
| `explorer-service` | Catálogo para la web. |
| `model-service` (antes `ai-service`) | BioCLIP 2.5 ViT-H/14 (1024) + clasificador sklearn, `/api/predict`. Código en `services/ai-service`; desde E0 vive en `docker-compose.model.yml`, fuera del servidor. |
| `notification-service`, `validation-service` | Esqueletos: solo `/health`. |
| `infrastructure/monitoring` | Vacío. Sin Prometheus, Loki ni Grafana. |
| `admin-web` | Contenedor en `127.0.0.1:3010`. Sin API propia: todo en el navegador. |
| App Android | versionCode 1. Paquete de Antioquia dentro del APK. No habla con el servidor; solo pide el clima a Open-Meteo. |
| Pipeline del modelo | Scripts en `D:\Anura` (scraper, `pipeline_dataset/`, `bioclip/scripts/`, `evaluation/`). El GPU del PC los corre a mano. |

## Principios

1. **19_ADMIN manda** en el método (centroides, cascada, tres capas, dos avales). Lo que el backend cambie del método entra primero como decisión en [[Decisiones de Escalabilidad del Admin]].
2. **Una API para el Admin (`admin-api`, FastAPI).** El cálculo del modelo ya es Python (numpy, onnxruntime, torch). El creador de `evaluation/admin_v2_comparison/` se vuelve una librería del servicio, no se reescribe en TypeScript.
3. **Postgres guarda el estado; MinIO guarda archivos.** El `localStorage` del Admin (morfos, clústeres, OSR, releases, curación, fichas, jobs) pasa a tablas. Cada store del front ya tiene el contrato de su tabla.
4. **El worker pesado corre en el PC con GPU**, no en el servidor. Toma jobs de Redis por el túnel.
5. **Nada se publica solo.** Dos personas distintas, y la compuerta de regresión (M5) antes del aval técnico.

## Orden de 0 a 100

Tres fases. **Local:** todo corre en este PC (servidor liviano y `model-service`, como contenedores separados en la misma máquina) y el teléfono ya lo usa por LAN o túnel — **esta es la meta de ahora**, ver arriba. **Futuro (Hostinger):** mudar el servidor liviano a un host pago; deliberadamente pospuesto, no bloquea nada de lo de ahora. **Remoto:** lo que solo tiene sentido una vez el servidor es público (avisos push, publicar en Play).

`herramienta` sugiere dónde conviene trabajar cada etapa, ya que hay Cursor Pro disponible: **Cursor** para código nuevo y aislado (un servicio, un módulo Kotlin, migraciones) donde el autocompletado dentro del archivo pesa más que el contexto de todo el repo; **Claude Code** para lo que cruza el Admin, la app y el vault a la vez, o depende de una decisión de 19_ADMIN.

| # | Etapa | Fase | Herramienta | Bloquea a |
| --- | --- | --- | --- | --- |
| 0 | **E0 Separar `docker-compose`** en servidor y `model-service`; probar que hablan entre sí en esta máquina (sin túnel todavía). **Hecho 2026-09-27.** | Local | Claude Code (toca el compose y el Admin a la vez) | todo lo demás |
| 1 | **S1** Cuentas, roles y sesión reales. **Hecho 2026-09-27** (Google para el panel y la regla de dos personas en servidor, pendientes). | Local | Claude Code (permisos ya viven en 19_ADMIN/Admin) | depende de 0 |
| 2 | **M1** Dataset en Postgres/MinIO + subida manual de foto. **Hecho 2026-09-27** (el scraper como trabajo desde el Admin queda para después). | Local | Cursor (esquema + importador, código nuevo aislado) | M2 |
| 3 | **M2** Worker real (embeddings) en `model-service`. **Hecho 2026-09-27** (corre en CPU; cola por especie y validación de vectores, pendientes). | Local | Cursor (servicio Python nuevo, cola Redis) | M3 |
| 4 | **K** Contenido: ficha pública, Explorador, destacados ([[Ficha Publica, Explorador y Destacados]]). **Hecho (2026-09-28): el Admin lo administra, la app y la web leen el catálogo, y viaja firmado (K2).** | Local | Claude Code (toca Admin + app Android + vault) | — |
| 5 | **M3** Creador real (centroides, clústeres, ArcFace, OSR, tres capas) en `model-service` | Local | Claude Code (portar `adapters.ts`/`osr.ts` tal cual, decisión de 19_ADMIN) | M5 |
| 6 | **M5** Compuerta de regresión | Local | Cursor (script de comparación, ya existe en Python) | M4 |
| 7 | **M4** Compilador real y paquete v2 | Local | Claude Code (formato compartido con la app Android) | L1 |
| 8 | **L1** Conectar el teléfono a este PC (LAN o túnel; ver "Meta inmediata"). **Hecho y probado en vivo 2026-09-28** (teléfono real, sin USB, por `anura.juanlabs.me`). | Local | Claude Code (túnel + nginx + `ContentCatalog.kt`) | C1 |
| 9 | **C1** Entrega de paquetes al teléfono | Local | Claude Code (protocolo servidor↔app) | C2 |
| 10 | **C2** Versiones y compatibilidad servidor↔app | Local | Claude Code | **Meta cumplida aquí** |
| 11 | **S2** Observabilidad (Prometheus/Loki/Grafana) | Local, después de la meta | Cursor (configuración de infraestructura) | — |
| 12 | ~~**K2** Entrega del catálogo de contenido a la app y a la web~~ — hecho (2026-09-28) | Local | Claude Code | — |
| 13 | **S3** Mudar el servidor liviano a Hostinger. `model-service` se queda en el PC, conectado por túnel. | Futuro (Hostinger) | Cursor (DevOps: imágenes, migraciones, respaldos) | C3–C6 |
| 14 | **C3** Sincronización de observaciones y rechazos (alimenta la auditoría de `model-service`) | Remoto | Claude Code | C4 |
| 15 | **C4** Telemetría de dispositivos | Remoto | Cursor | — |
| 16 | **C5** Avisos push | Remoto | Cursor | — |
| 17 | **C6** Publicación de la app (CI, Play) | Remoto | Cursor (CI/CD) | — |

Esto reemplaza el orden anterior ("S1 → S3 → M1 → …"), que mezclaba S3 (que en realidad es la bisagra hacia lo remoto) en medio de Modelo.

### Sistema

#### E0 · Separación hecha (2026-09-27)

Archivos en `D:\server\Anura`:

| Archivo | Qué levanta |
| --- | --- |
| `docker-compose.server.yml` | Todo lo liviano: Postgres, Redis, MinIO, `db-migrate`, pgAdmin, los microservicios, `frontend`, `admin-web`, Nginx Proxy Manager y el túnel. Sin GPU. |
| `docker-compose.model.yml` | `model-service` (código de `services/ai-service`) con la GPU. Red propia (`model-net`), sin base de datos. |
| `docker-compose.yml` | Solo `include:` de los dos: `docker compose up -d` sigue levantando todo en este PC. |

Cómo se hablan:
- El nginx del `frontend` es ahora una **plantilla**: la imagen oficial sustituye `${MODEL_SERVICE_URL}` y `${MODEL_SERVICE_TOKEN}` al arrancar. `/api/predict` y `/api/ai` van a `MODEL_SERVICE_URL`.
- En este PC, `MODEL_SERVICE_URL=http://host.docker.internal:8000` y `model-service` publica solo en `127.0.0.1:8000`. Con el servidor en Hostinger, la misma variable apunta a la URL del túnel; no cambia código.
- Token compartido `MODEL_SERVICE_TOKEN` (header `X-Model-Token`, comparación en tiempo constante). Sin token, todo menos `/health` responde 401.
- Nginx no reenvía `Host $host` a `model-service`: un túnel de Cloudflare enruta por el nombre del destino.
- El proyecto de Docker sigue llamándose `anura` a propósito: así los volúmenes (`anura_postgres_data`, `anura_minio_data`) son los mismos de antes. Con otro nombre, Postgres habría arrancado vacío.
- `./models/u2net` guarda el modelo de rembg (176 MB); sin ese volumen se descargaba en cada arranque y el contenedor quedaba "unhealthy".

Prueba hecha:

| Prueba | Resultado |
| --- | --- |
| Foto real de *Pristimantis paisa* por el nginx del servidor → `model-service` | 200, *P. paisa* 99,9 %, 8,5 s |
| `/api/predict` directo sin token | 401 |
| El servidor busca `model-service` por nombre de red | No lo encuentra (redes separadas, como en dos máquinas) |
| `model-service` con BioCLIP 2.5 en la RTX 4050 | Sano; arranca en ~1 min con los pesos en caché |

Se levanta así:
- Todo: `docker compose up -d`.
- Solo el modelo: `docker compose -f docker-compose.model.yml up -d`.
- Solo el servidor, sin el túnel público: `docker compose -f docker-compose.server.yml up -d postgres redis minio frontend admin-web …`.

Hallazgo que pasa a S1: `auth-service` no arranca (`Cannot find module '../models/User'`). El `.gitignore` raíz tiene `models/` (pensado para pesos de ML) y eso ignoró también `services/auth-service/src/models/`: `User.js` y `UserPreferences.js` nunca entraron a git y ya no están en disco. Ya venía caído antes de E0.

#### S1 · Cuentas, roles y sesión reales — hecho en lo esencial (2026-09-27)

No quedó como se planeó arriba: en vez de tres tablas nuevas (`panel_role`, `role_permission`) se usó **una sola** — más simple y más fiel a como ya estaba modelado en el Admin (`admin/src/lib/mock/admin-accounts.ts`): el permiso vive por acción en cada cuenta, la plantilla (administrador/herpetólogo) es solo un punto de partida al crearla, no una tabla aparte.

- `auth.panel_accounts` (migración `phase3.sql`): `email`, `name`, `is_super`, `permissions` (JSONB con las 18 acciones), `user_id` (se ata solo, la primera vez que esa persona entra de verdad — no hay paso manual de "vincular cuenta").
- Login: `/login` en el Admin llama a `POST /api/auth/login` de `auth-service` (correo y contraseña, la misma cuenta que ANURA Mobile) — no hay contraseña aparte para el panel. Google queda pendiente para el panel (sí funciona para la app).
- `auth-service` gana `/api/panel/me`, `/api/panel/accounts` (GET/POST), `/api/panel/accounts/:id/permissions` (PATCH), `/api/panel/accounts/:id` (DELETE). Las plantillas de permisos viven en el servidor (`panelService.js`), nunca se confía en lo que mande el cliente.
- El servidor bloquea degradar o borrar al super usuario (antes solo estaba deshabilitado en la interfaz). Cada alta, cambio de permiso o baja entra a `audit.log` (esa tabla ya existía desde Fase 2, sin usar).
- El Admin reenvía `/api/auth/*` y `/api/panel/*` a `auth-service` — mismo origen para el navegador, igual que hará nginx cuando el Admin esté detrás de él. Sin CORS. **No** con `rewrites()` de `next.config.ts`: ese reenvío se calcula en el build (`output: "standalone"`) y quedó apuntando a `localhost:3001` incluso dentro del contenedor, donde no existe — bug encontrado al probar el contenedor real, no solo `npm run dev`. Corregido con dos route handlers (`src/app/api/{auth,panel}/[...path]/route.ts`) que leen `AUTH_SERVICE_URL` en cada request, no en el build.
- Sin sesión (nadie inició sesión, o el servidor no responde), el panel cae a **modo demostración**: las cuentas de ejemplo de siempre, guardadas en el navegador — así se puede seguir revisando la interfaz sin depender del servidor. El selector "operar como" del topbar **solo existe ahí**; con sesión real no hay "operar como otra persona", se opera como quien entró.
- Bug encontrado de paso (bloqueaba cualquier registro nuevo, incluido Google): `preferencesRepository.create()` inserta una columna (`preferences_completed`) que nunca estuvo en una migración aplicada automáticamente — solo en un script suelto (`src/cli/migrate.js`) que nadie corría. Ya estaba corregido a mano en esta base, pero quedó agregado a `phase3.sql` para que sea automático en cualquier base nueva.

Prueba hecha (en el navegador, contra el servidor real, con `docker compose -f docker-compose.server.yml up`):

| Prueba | Resultado |
| --- | --- |
| Login con correo/contraseña real | Entra, topbar muestra el nombre real |
| Login con contraseña equivocada | "No existe el usuario", sin redirigir |
| Cuenta real sin fila en `auth.panel_accounts` | 403 "Esta cuenta no está en el panel administrativo" |
| Sin token, a `/api/panel/*` | 401 |
| Crear cuenta, cambiar un permiso, borrar cuenta desde la pantalla | Los tres llegan a Postgres y a `audit.log` (verificado por SQL directo) |
| Intentar quitarle "Administrar cuentas" o borrar al super usuario | 400 en el servidor, aunque se fuerce la llamada sin pasar por la interfaz |
| Cerrar sesión | Vuelve a `/login`; sin sesión, cae a modo demostración con las cuentas de ejemplo de antes |

Pendiente de S1 (no bloquea la meta de ahora, sí conviene resolver antes de invitar gente real): Google OAuth para el panel (hoy solo correo/contraseña); la regla de dos personas de Release ([[Prueba Real del Creador de Paquetes]] hallazgo 12-13) la sigue validando el cliente, no el servidor — se vuelve real junto con M4/M5, cuando el compilador deje de ser simulado.

**S2 · Observabilidad.**
- Prometheus con node-exporter, cAdvisor y `nvidia_gpu_exporter` en el PC del worker, más `/metrics` en cada servicio.
- Loki + Promtail para logs.
- Grafana como motor: `admin-api` consulta `/api/ds/query` o Prometheus directo y el Admin dibuja sus propias gráficas. No se usa iframe ([[Observabilidad y Simulador]]).
- Las alertas de Grafana van a `notification-service`.
- Lo científico (AUROC, confusión, ROC) sale de Postgres (`ExperimentResult`). Nunca se mezcla en el mismo panel con la GPU.

**S3 · Mudar el servidor liviano a Hostinger (pospuesto a propósito, no bloquea la meta de ahora).**
- Imágenes etiquetadas por commit (GitHub Actions → GHCR).
- Stacks de staging y producción.
- `db-migrate` con migraciones versionadas.
- Respaldo diario de Postgres y MinIO en `infrastructure/backups`.
- Portainer: ver la sección de abajo.
- `model-service` no se muda nunca: ya vive en este PC desde la etapa 0.

### Modelo

#### M1 · Dataset en el servidor — hecho (2026-09-27)

Decisiones del autor antes de empezar (2026-09-27): clave de MinIO por **sha256** (cambiar el nombre de una especie no mueve archivos); rellenar coordenadas desde la **API de iNaturalist**; subir las fotos sin licencia **marcadas**, no dejarlas fuera. Para M2: model-service **pide trabajos por HTTP** (solo conexiones salientes) y los vectores van en **pgvector**, organizados para pasar directo a sqlite-vec del teléfono (float32 × 512 + sha256 del encoder).

Lo construido:
- **MinIO:** bucket privado `anura-dataset`, clave `fotos/<sha[0:2]>/<sha256>.jpg`. **12.209 fotos** de 43 especies (8,2 GB).
- **Postgres, esquema `dataset`** (`phase4.sql`, `phase5.sql`): `especie` (34 con `taxon_id` COL_ANURA; 9 son de fuera del catálogo de Antioquia), `observacion`, `foto`, `exclusion` (5.223 descartes de la limpieza original), `version` + `version_foto` (el manifiesto de entrenamiento: 4.724 rutas con su partición), `limpieza_corrida`, `hallazgo`.
- **`dataset-service`** (nuevo, puerto 3008): dueño del esquema y del bucket. Solo cuentas del panel (verifica con `auth-service`, igual que S1). URLs de MinIO firmadas por 10 min.
- **Importador** `tools/dataset/import_to_minio.py` y **relleno** `tools/dataset/backfill_inaturalist.py`: corren en un contenedor temporal dentro de la red del servidor (Postgres no se expone). Idempotentes.
- **Curación** muestra las fotos reales de la especie con partición, licencia y coordenada; Calidad tiene la limpieza y las decisiones.

Hallazgos de la importación (no eran conocidos):
- **El sha256 de `dataset_limpio.json` no es el del archivo limpio.** `limpiar_dataset.py` guarda el hash del **original descargado** y escribe una copia recodificada (JPEG 95). No es corrupción: se guarda como `sha256_origen` para rastrear procedencia.
- **4.119 fotos (34 %) son "todos los derechos reservados"** en iNaturalist (su `license_code` viene vacío), no "sin licencia". Se guardan como `all-rights-reserved`. Otras 304 sí no tienen metadatos. Por la decisión del autor del 2026-09-13 ([[Dataset Jerárquico de Colombia — Paquetes Departamentales]] §8) sirven para vectores, nunca para mostrarse como evidencia.
- **45 fotos** listadas en `dataset_limpio.json` ya no están en disco (34 de ellas en el manifiesto).
- **Coordenadas:** `records_v1.csv` solo cubría 3.221 fotos (es de Antioquia). La API de iNaturalist devolvió 4.970 de 4.971 observaciones restantes; 250 vienen ocultas por iNaturalist (desplazadas dentro de una celda de 0,2°).

**Limpieza con mediana, decisiones en el Admin** (Admin → Calidad). La limpieza automática **solo propone**; una persona decide, queda en `audit.log`, y ninguna corrida nueva cambia lo decidido. La coordenada original nunca se sobrescribe (lo limpio va en `latitud_limpia`, `longitud_limpia`, `uso_geografico` = punto / celda / excluida).

| Hallazgo | Cuántos | Propuesta automática |
| --- | --- | --- |
| Coordenada aproximada (oculta por iNaturalist o incertidumbre > 1 km) | 1.278 | Con ≥ 3 registros precisos de la misma especie en su celda de 0,2°: **la mediana de esos registros** (669). Si no: usarla solo a nivel de celda — como la altitud del paquete, mediana por zona y no el punto. |
| Coordenada atípica (aislada) | 38 | Excluir de las capas geográficas (no del entrenamiento). Aislada = distancia al 2.º vecino preciso de la especie con z robusto (mediana + MAD) > 3,5 **y** > 200 km. |
| Sin coordenada | 1 | Excluir de las capas geográficas. |
| Todos los derechos reservados / sin licencia | 4.119 / 304 | Solo para entrenar (decisión del autor 2026-09-13). |

Nota de método: la primera versión de "atípica" medía la distancia a la mediana **nacional** de la especie y marcó 268 puntos, casi todos poblaciones reales en otra región (Pacífico contra Amazonía; solo 20 estaban fuera de Colombia). Se cambió a aislamiento local. Con piso de 50 km seguían saliendo 286, porque la distancia típica al vecino es ~1 km (los registros se agrupan donde hay observadores); con 200 km quedan 38, que sí vale la pena revisar a mano. Todos los parámetros se ajustan desde Calidad y cada corrida los guarda.

**Curación en el servidor y subida manual (2026-09-27).** Con esto M1 queda cerrado; solo el scraper como trabajo lanzado desde el Admin queda para después (hoy se corre a mano).

- **Subir foto** (Admin → Curación → "Fotos en el servidor"): el navegador lee el GPS y la fecha del EXIF (`exifr`) o se escribe la coordenada (acepta coma decimal). Si se cambia la del EXIF, se guarda como escrita a mano. Licencia y autor son obligatorios.
- **Validación con `geo-service`**: nuevo `GET /api/geo/ubicacion`, punto en polígono sobre los límites DANE de `D:\Anura\geo\colombia_departamentos.geojson`, **sin red externa** (el geocoding existente depende de Nominatim y no sirve para validar). Devuelve el departamento; fuera de Colombia dice a cuántos km queda del más cercano y pide confirmar (en la costa puede ser el borde simplificado del mapa). Los municipios no se usan todavía en la validación de coordenadas (sí en Regiones, ver más abajo).
- **Igual que el importador**: la foto se recodifica a JPEG 95 sin metadatos (el GPS queda en Postgres, no en el archivo público), clave por sha256 del JPEG, `sha256_origen` del archivo subido, rechaza duplicados (409). La observación queda `fuente = manual`, `coordenada_fuente` exif/manual, con departamento, y entra a las capas en la siguiente corrida de la limpieza como cualquier otra.
- **Excluir foto / invalidar observación** dejan de vivir en el navegador (`phase6.sql`): `exclusion.origen` (limpieza_original, curacion, observacion_invalidada, decision_licencia) y cada pantalla solo revierte lo suyo — Curación no deshace una decisión de licencia de Calidad. Invalidar excluye todas las fotos de la observación, la saca de las capas geográficas y guarda lo limpio de antes (`invalidada_previo`) para que revertir no pierda lo decidido en Calidad. La limpieza ignora observaciones invalidadas y no pide decidir la licencia de fotos ya excluidas. Todo va a `audit.log`.
- La muestra simulada de Curación queda solo para estadio y morfo; con sesión real ya no ofrece excluir ni invalidar ahí.

Bugs encontrados al probar (corregidos): una foto excluida aparte y luego invalidada se podía reincluir con la observación todavía invalidada; el Admin reenviaba el cuerpo como texto (`req.text()`) y habría dañado cualquier foto subida; la fecha del EXIF salía un día después para fotos tomadas después de las 7 p. m. en Colombia (`toISOString()` pasa a UTC).

Prueba hecha en el navegador, contra el servidor real: subir con GPS del EXIF (sale Antioquia), longitud con signo cambiado (aviso a 15.772 km, botón bloqueado hasta confirmar), subir, excluir, invalidar, reincluir bloqueado mientras está invalidada, revertir, reincluir. Las dos fotos de prueba se borraron después de MinIO y Postgres (quedan sus filas en `audit.log`), y la limpieza volvió a dar exactamente los mismos conteos.

#### M2 · Worker real, dentro de `model-service` — hecho (2026-09-27)

Plan original: cola en Redis, vectores en pgvector o `.npy`. Quedó así, por las decisiones del autor del 2026-09-27 (el worker pide trabajos por HTTP; pgvector organizado para pasar directo a sqlite-vec):

- **Sin Redis.** `model-service` **pide** trabajo a `dataset-service` (`/api/worker/*`, token `WORKER_TOKEN` en `X-Worker-Token`). Solo hace conexiones salientes, así que funciona igual en este PC (`host.docker.internal:3008`) que con el servidor en Hostinger detrás de un túnel (hará falta `location /api/worker` en nginx). Las fotos también las baja por `dataset-service`: MinIO no se expone.
- **Nada en memoria.** Lo que falta se calcula siempre como "fotos sin vector de este encoder", así que un trabajo cancelado o un worker caído sigue donde iba. Si el worker deja de latir 2 minutos, el trabajo se retoma. Las fotos dañadas quedan en `trabajo_error` y no frenan el resto.
- **Postgres con pgvector.** Nueva imagen `infrastructure/postgres/image` (PostGIS 16 + `postgresql-16-pgvector`, pgvector 0.8.6), misma versión mayor, así que el volumen se reutilizó. Antes se sacó un respaldo: `infrastructure/backups/anura_2026-09-27_antes_pgvector.dump`, ignorado por git. `phase7.sql` crea `encoder`, `embedding` (vector(512), PK foto + encoder), `trabajo`, `trabajo_error` y `worker`.
- **Admin → Worker**: tarjeta "Worker real" con el estado del worker (conectado, CPU/CUDA, ms por foto), vectores calculados del total, botón para calcular los faltantes (permiso Ejecutar entrenamiento), tabla de trabajos con avance y botón para cancelar. La consola simulada sigue debajo para lo que llega con M3.
- **Exportación a sqlite-vec**: `tools/dataset/export_sqlite_vec.py` escribe `vec_references` igual que `pipeline_dataset/paquetes_zonales.py` (vec0, FLOAT[512], coseno, sqlite-vec 0.1.9). Probado: cada blob es idéntico bit a bit al float4 de pgvector, y cada vector se encuentra a sí mismo. No arma un paquete; eso lo hace M4.

**¿fp16 o fp32?** (verificado 2026-09-27, a pregunta del autor):
- **Los vectores son float32 en todas partes**: pgvector, sqlite-vec del teléfono y la caché del paquete. "fp16" es solo el formato de los **pesos** del encoder.
- **El worker usa exactamente el archivo del teléfono**, `encoder_anura_fp16.onnx` (sha256 `219e860e…`). Si el archivo no coincide, el worker no arranca: con otro encoder los vectores no serían comparables.
- El preprocesado del worker (PIL + numpy) da el mismo tensor que `open_clip` (diferencia 0,0). Lo guardado en pgvector coincide con un cálculo independiente con coseno 0,9999999.

Comparado en 40 fotos:

| Comparación | Coseno mínimo |
| --- | --- |
| ONNX fp16 contra ONNX fp32 (`encoder_anura.onnx`) | 0,999999 |
| ONNX fp16 contra los vectores del paquete de Antioquia (`COLOMBIA_ANURA/cache/embeddings`) | 0,9992 |
| ONNX fp32 contra los mismos vectores del paquete | 0,9992 |

El paquete de Antioquia que ya viaja en el APK se calculó con el `.pt` y `torch.autocast` en GPU, no con el ONNX que corre el teléfono. La diferencia es pequeña, pero siguiendo la regla de la app (las referencias se calculan con el mismo modelo que consulta), los paquetes que compile M4 desde el servidor ya quedan hechos con el mismo ONNX fp16 que usa el teléfono.

**Pendiente de M2** (no bloquea M3):
- **Corre en CPU**: ~0,3–0,4 s por foto, así que las 12.209 fotos tardan ~1,5 h. El `onnxruntime` de la imagen de `model-service` no trae CUDA. Pasar a `onnxruntime-gpu` exige empatarlo con CUDA 12 / cuDNN 8 de la imagen y volver a medir la paridad.
- La cola por especie, el tope por observación y la validación de vectores del Admin siguen simulados.
- Métricas a S2.

**M3 · Creador real, dentro de `model-service`.** Hecho en lo que los datos permiten (2026-09-27).
- Centroide global L2, dispersión, vecino y supercentroides de género y familia, desde las fotos `train` que ya tienen vector.
- Radio Weibull: τ por especie, género y familia (cobertura 95 %). La cascada (especie → género → familia → rechazo) se mide en la partición `val`, que no entra al centroide ni al τ.
- ArcFace (margen angular) corre sobre los pares con coseno alto o confusión en validación y guarda el acierto antes y después. Es una sugerencia: no publica el clúster. El herpetólogo lo arma.
- No hay gaussiana de altitud ni centroide regional. Las observaciones no traen metros y no existe el polígono de subregión. No se rellenan con `antioquia-real.json` ni con la cabecera más cercana.
- El cálculo vive junto a pgvector, en `dataset-service`, para no reiniciar el worker de embeddings. Las fórmulas son las de `osr.ts` y `adapters.ts`.

#### K · Contenido: ficha pública, Explorador y destacados — hecho (Admin 2026-09-27; app y web 2026-09-28)

Ver [[Ficha Publica, Explorador y Destacados]] para el detalle de campos y pantallas.

- **`dataset.species_content`** (`phase8.sql`): un bloque `campos` por especie con los del punto 2 de esa nota. Los que exigen fuente (nombre común, UICN, toxicidad, altitud de literatura, LHC, dato curioso) se guardan como `{valor, fuente}`; sin fuente, el servidor no deja enviar a revisión ni publicar. Un campo vacío nunca llega al catálogo.
- **Estados borrador → en revisión → publicada**, con dos permisos separados: `editarContenido` escribe y envía a revisión; `publicarContenido` es el aval del herpetólogo (misma idea de dos personas que el paquete, con un solo aval porque el contenido no toca el modelo). Editar una ficha publicada la vuelve a borrador, pero **lo publicado es una copia fija** (`species_content.publicada`, `phase11.sql`): la app y la web siguen viendo esa versión hasta el próximo aval. Antes de esa fase, editar sacaba la especie del catálogo mientras se corregía.
- **`dataset.destacado`** (`phase8.sql`): un día y una categoría a la vez. El servidor calcula qué especies son elegibles para cada categoría (foto con licencia CC y autor, hábitat escrito, UICN VU/EN/CR…) y solo dentro de esas se puede programar.
- **Admin → Contenido**: lista de especies con su estado, editor por bloques con la foto principal y la galería elegidas entre las fotos con licencia CC de esa especie (`GET .../fotos?solo_cc=true`, para que una especie con miles de fotos no esconda la única CC fuera de la primera página), y una vista previa con el mismo aspecto de la ficha de la app.
- **Admin → Destacados**: calendario de dos semanas, con el selector de especie ya filtrado a las elegibles de esa categoría.
- **`GET /api/dataset/contenido/catalogo`**: solo especies publicadas, solo campos con valor — la previsualización del catálogo. Firmarlo y entregarlo por su propio canal es K2.

Prueba hecha en el navegador contra el servidor real: llenar una ficha, ver el checklist de "falta para publicar" bajar a cero, enviar a revisión, publicar, verla aparecer en el catálogo y en las elegibles de Destacados, programarla, editarla y revertir. Los datos de prueba se borraron después.

**Auditoría de lo que piden la app y la web (2026-09-28).** Se compararon los campos de Contenido con lo que pintan la ficha de la app (`SpeciesScreens.kt`, carrusel) y la de la web (`TaxonDetail.jsx`):
- La web pedía datos que el Admin no dejaba escribir: autoría del nombre, sinónimos, descripción («¿Qué es?»), actividad, dieta, reproducción, distribución en texto, endemismo y amenazas. Se agregaron; **endemismo y amenazas llevan fuente** (son afirmaciones de conservación, como la UICN). Morfología ganó «rasgos diagnósticos» y la UI de «especies con las que se confunde» (existía en el esquema, no en la pantalla).
- Cada bloque del editor dice dónde se ve («App: ficha, carrusel · Web: ficha»), para saber qué se está llenando.
- La app mostraba en la pestaña **Morfología el texto de ejemplo de *D. truncatus* en las 31 especies**; ahora muestra solo la morfología publicada o «todavía no tiene la morfología revisada».
- La web no mostraba la **toxicidad** (dato de seguridad que la app sí muestra): ahora sí.

**Entrega a la app y la web (sin firma todavía).**
- `GET /api/dataset/publico/catalogo` (sin sesión): solo la copia publicada, solo campos con valor, fotos de referencia, los destacados de los próximos 30 días (fecha de Colombia, no UTC) y `version` = sha256 del contenido, con `ETag`: si no cambió, responde 304.
- `GET /api/dataset/publico/fotos/:sha256?ancho=320|640|1080`: solo si la foto es la principal o de la galería de una ficha publicada **y** tiene licencia CC; cualquier otra foto del dataset sigue privada.
- **App** (`ContentCatalog.kt`): al abrir, carga la copia guardada en el teléfono (`files/content/catalogo.json`) y pide la nueva al servidor. Una especie con ficha publicada muestra **solo lo publicado** (no se mezcla con lo escrito a mano en `SpeciesCatalog.kt`); sin ficha publicada, sigue el respaldo local. El carrusel sale de Destacados (o, si un día no tiene nada, de una especie elegible elegida por la fecha, sin red). La URL del servidor es una preferencia (L1); sin ella prueba `http://127.0.0.1:3008` (teléfono por USB con `adb reverse tcp:3008 tcp:3008`) y luego el dominio público. Crédito de la foto visible (licencias CC).
- **Web** (`publishedCatalog.js` + `TaxonDetail.jsx`): igual regla; nginx y Vite reenvían solo `/api/dataset/publico/`.
- Probado en el teléfono real (Xiaomi, USB) y en la web con una ficha de prueba marcada «PRUEBA»: carrusel «Rana del día» y «Foto destacada» con la foto CC y su autor, ficha con toxicidad, UICN, altitud y LHC publicadas, morfología publicada; después se borró la ficha y el teléfono volvió solo al respaldo al sincronizar.

Pendiente de K: firmar el catálogo y entregarlo por su propio canal (K2); `explorer-service` sigue contando especies desde `ai.predictions`; el carrusel de ejemplo (sin ficha publicada) quedó sin *D. truncatus* como «especie amenazada» (es LC).

**K2 · Entrega del contenido — hecho (2026-09-28).** El catálogo de contenido se descarga con el mismo mecanismo que va a usar C1 (manifest + sha256 + firma), en su propio canal — se actualiza más seguido que el paquete de identificación y no fuerza ninguna recompilación.
- **`GET /api/dataset/publico/manifiesto`**: `{formato, canal:"contenido", version, sha256, tamano, generado, firma, url}`. `services/dataset-service/src/manifiesto.js` firma con Ed25519 (Node `crypto`, sin dependencias): la clave privada vive en `CONTENT_MANIFEST_PRIVATE_KEY_B64` (.env, nunca se imprime ni sale del servidor). El texto exacto que se firma se cachea por `version` (antes `generado` cambiaba en cada request y la firma nunca hubiera coincidido con una segunda descarga del mismo contenido — se detectó y se corrigió antes de firmar nada).
- **La clave PÚBLICA va embebida en la app y en la web**, no se sirve por este mismo canal — si viajara junto con el contenido, quien lo controlara podría cambiar los dos a la vez y la firma no protegería nada (mismo principio que el sha256 del encoder, `CONTRATO`). App: `core/data/ContentManifestVerifier.kt`, con `net.i2p.crypto:eddsa` (Java puro — el JCA de Android solo trae Ed25519 desde la API 33, y `minSdk` de la app es 26). Web: `frontend/src/species/contentManifest.js`, con `crypto.subtle` (Web Crypto ya trae Ed25519).
- Antes de aceptar un catálogo nuevo, los dos verifican la firma del manifiesto y que el sha256 de lo descargado sea el que se firmó; si algo no cuadra, se quedan con el que ya tenían.
- Probado: en el teléfono real (con una ficha de prueba publicada, `adb reverse`) y en el navegador — firma real verificada como válida, firma alterada y sha256 alterado rechazados en los dos lados. Cruzado además con Java puro fuera de Gradle usando el mismo `.jar` de `net.i2p.crypto:eddsa`, contra una firma real del servidor: coincide con lo que valida Node.js.
- Pendiente: nada de este alcance. La rotación de la clave si algún día hace falta exige publicar una versión nueva de la app y de la web (las dos tienen la pública embebida).
- **Reauditado en vivo el 2026-09-28** al retomar la sesión, pidiendo el manifiesto real a `dataset-service` (no una prueba antigua): la firma verificó válida contra la clave pública embebida usando Node `crypto.verify` directo (reconstruyendo el SPKI a partir de los mismos 32 bytes de `contentManifest.js`/`ContentManifestVerifier.kt`), el `sha256` coincidió byte a byte con el cuerpo servido, y una segunda petición devolvió exactamente el mismo `generado`/`firma`/`sha256` (el caché por versión sigue determinista). El catálogo publicado está vacío (`"especies":[]`) porque las 5 fichas de `dataset.species_content` siguen en `borrador` — nadie ha publicado contenido real todavía; no es un bug de K2, es que aún no hay nada que publicar.

#### Regiones · departamentos y subregiones en el servidor — hecho (2026-09-28)

La unidad que se versiona y se descarga es la subregión ([[Decisiones de Escalabilidad del Admin]] #8), pero las 9 de Antioquia vivían escritas en el Admin. Ahora son datos:
- **`dataset.region`, `dataset.subregion`, `dataset.subregion_municipio`** (`phase12.sql`): un departamento (código DANE), sus subregiones y a cuál pertenece cada municipio (uno por municipio).
- **Antioquia sembrada** por `tools/admin/build_antioquia_subregiones.py` desde datos reales: polígonos DANE de `geo/antioquia_municipios.geojson` (el nombre de subregion.json no siempre es el oficial del DANE, así que se cruzan por nombre normalizado o por código cuando faltan) y la lista de municipios de cada `COLOMBIA_ANURA/ANTIOQUIA/SUBREGIONS/*/subregion.json`. Cinco nombres de uso común no son el oficial del DANE (El Peñol/Peñol, El Retiro/Retiro, San Vicente/San Vicente Ferrer, Carolina del Príncipe/Carolina, Cuerquia/Cuerquía) y quedaron como equivalencias explícitas. Resultado: 125 municipios en 10, 23, 23, 19, 17, 10, 6, 6 y 11 — la división oficial.
- **geo-service** sirve los 33 departamentos (contorno liviano para el mapa) y los municipios por departamento; `POST …/ubicar` ubica miles de puntos por municipio. Sin red externa.
- **dataset-service** (`regiones.js`): agregar un departamento (queda en borrador), crear, renombrar y borrar subregiones (solo vacías), pasar municipios de una a otra, activar (solo si todos los municipios tienen subregión) y quitar un borrador. Permiso `generarPaquete`; todo con auditoría. Las cifras por subregión (observaciones y especies con fotos) salen de las observaciones del dataset ubicadas por municipio, sin las invalidadas.
- **Admin → Regiones**: mapa de Colombia (activo en verde, borrador en naranja), lista de departamentos, «Agregar un departamento»; al elegir uno, el mapa de sus municipios coloreado por subregión, la leyenda con cifras y, por subregión, sus municipios, sus especies y «Pintar municipios» (tocar un municipio lo pasa a esa subregión). Un departamento sin límites municipales se puede agregar y la pantalla dice qué falta para dividirlo.
- **Límites municipales de los 33 departamentos (2026-09-28)** — ya no falta ninguno: `geo/colombia_municipios.geojson` (1.122 municipios, MGN DANE 2018, mismo esquema que `antioquia_municipios.geojson`) sale de la conversión pública [caticoa3/colombia_mapa](https://github.com/caticoa3/colombia_mapa) del shapefile oficial del DANE; se verificó contra el archivo de Antioquia que el proyecto ya traía (125 códigos DANE y las cajas delimitadoras de la geometría coinciden exactamente, así que es la misma fuente). `tools/admin/build_municipios_geojson.py` genera `data/municipios_<DPTO>.geojson` para los otros 32 departamentos (Antioquia sigue con su propio script y sus nombres de uso común). Probado agregando Cauca de verdad: sus 42 municipios aparecen con nombre correcto, se creó una subregión y se pintó Popayán (con sus 2 observaciones reales), y se quitó — la base quedó como estaba.
  - **Nota sobre una falsa alarma de este mismo día**: se creyó que `antioquia_municipios.geojson` (y por lo tanto el nacional) tenía los nombres con la codificación dañada — visto así en varias comprobaciones con `print()` de Python durante esta sesión. Al revisar los *bytes* del archivo directamente (no lo que imprime la consola) los tres archivos están en UTF-8 correcto, sin un solo carácter de reemplazo; lo dañado era la consola de Windows al mostrar acentos de un `print()` sin `-X utf8`, no el dato. `tools/admin/nombres.py` (capitalización de título en español, sin inventar nada) reemplaza el parche que asumía corrupción.
- Probado también: agregar Cauca (antes de tener sus límites) y quitarlo; pasar Puerto Nare a Oriente pintando y devolverlo.

Pendiente: que el compilador (M4) arme un paquete por cada subregión de esta tabla.

#### Revisión de UX de Imágenes (Curación) y Especies (Catálogo) — hecha (2026-09-28)

- **Curación**: la lista de especies salía del catálogo simulado (34) y el servidor tiene 43: nueve especies (p. ej. *Boana punctata*, 395 fotos) no se podían curar. Ahora, con sesión, la lista es la del servidor, con buscador y conteos. La explicación del pipeline (rutas de archivos) ocupaba la primera pantalla: quedó plegada al final. Las fotos se agrupan por observación (fuente, fecha, lugar y «Invalidar observación» una vez por grupo) y hay filtros con conteo que aplica el servidor (excluidas, sin licencia CC, coordenada aproximada, sin coordenada, subidas a mano, partición): filtrar solo la página cargada escondía casos. Estadio y morfo (todavía simulados) quedaron aparte, plegados y rotulados. Sin sesión sigue la muestra simulada.
- **Especies**: con sesión, las cifras salen del servidor (43 especies, familias, géneros, fuera del paquete, fichas publicadas), con fotos reales, «Curar fotos» y «Ficha pública» (con su estado). Se quitaron «Sin imágenes cargadas en simulación», «1 observaciones», «Longitud rostro-cloaca: – mm» y el título engañoso «Especies que añadiste» (el formulario de alta, que es simulado, quedó plegado y lo dice).

**M5 · Compuerta de regresión.** Cada release se mide contra el vigente con las mismas fotos de prueba y desconocidas. Si empeora la especie equivocada, el FAR o el AUROC más allá de un margen, no se puede dar el aval técnico.

**M4 · Compilador real y paquete v2.**
- Propuesta: **un SQLite por subregión** con las tablas del [[Esquema JSON del Paquete]]:
  - `species` (centroides FP16 en blob, τ, altitud, pesos);
  - `genus_node` y `family_node` (con centroide);
  - `cluster` (W en blob, ε);
  - `manifest`.
- Firma: sha256 real y manifest firmado con Ed25519.
- La app ya usa SQLite (Room): reusa el driver y solo cambia el lector.
- El `.sqlite` k-NN actual se sigue publicando mientras haya apps que no lean v2 (C2).

### Operación y conexión con el teléfono

**L1 · Conectar el teléfono a este PC. Hecho y verificado en vivo (2026-09-28).**
- La URL base del catálogo de contenido ya es una preferencia, no una constante (`ContentCatalog.candidates()`, `services/.../ContentCatalog.kt`): prueba primero una preferencia guardada (`ContentCatalog.setBaseUrl`, sin UI propia todavía — pendiente si hace falta un selector manual), después `http://127.0.0.1:3008` (USB + `adb reverse`) y por último `AnuraServerConfig.AUTH_BASE_URL` = `https://anura.juanlabs.me` (dominio público, mismo que ya usaba el login de Google por exigencia de Google Cloud Console).
- El túnel de Cloudflare (`anura_tunnel`) y Nginx Proxy Manager (`anura_npm`) ya estaban configurados (ingress `anura.juanlabs.me → npm:80 → frontend:80`, que a su vez reenvía cada `/api/<servicio>` al microservicio interno) pero llevaban 2 días apagados; se levantaron de nuevo (`restart: unless-stopped`, quedan arriba solos).
- **Bug encontrado al levantar el túnel:** `/api/dataset/publico/*` (K2) respondía el `index.html` del frontend en vez del JSON de la API cuando se pedía por el dominio público. Causa: la imagen Docker de `frontend` (la de producción, detrás de `npm`) tenía el `nginx.conf` de antes de agregar esa ruta en la etapa K — el archivo fuente ya estaba bien, solo faltaba reconstruir la imagen. Corregido con `docker compose -f docker-compose.server.yml build frontend && up -d --no-deps frontend`.
- **Prueba real:** con el teléfono conectado (`D6D6MRC6YX55WCPR`), se quitó el `adb reverse tcp:3008` (`adb reverse --remove-all`, ya no había ninguno activo) para que `127.0.0.1:3008` en el teléfono fallara de verdad, y se reabrió la app. El log de acceso de `npm` mostró la petición llegando por `https://anura.juanlabs.me/api/dataset/publico/manifiesto` y luego `/catalogo` con `User-Agent: Dalvik ... 23090RA98G` (el teléfono real) — y el catálogo quedó escrito en `files/content/catalogo.json` del propio teléfono con el mismo `sha256` que firmó el servidor, o sea que además pasó la verificación de firma de K2 (si no, `refresh()` nunca escribe el archivo). Camino LAN/Wi-Fi sigue disponible igual; el dominio público es ahora el respaldo real, no solo teórico.
- Pendiente opcional, no bloqueante: una pantalla de desarrollador para fijar `ContentCatalog.setBaseUrl()` a mano (hoy la función existe pero nada la llama); el fallback automático ya cubre el caso de uso real.

**C1 · Entrega de paquetes.**
- `GET /api/packages/manifest?subregion=&app_version=&schema=&encoder_sha=` devuelve el release compatible.
- Descarga por URL firmada de MinIO, reanudable.
- La app verifica sha256 y firma, escribe en un archivo temporal y cambia de forma atómica. Guarda la versión anterior para revertir sin red.

**C2 · Versiones y compatibilidad.** Cada paquete declara `schema_version`, `encoder_sha256` y `min_app_version`.

| Qué cambia | Qué versión sube | ¿Hay que actualizar la app? |
| --- | --- | --- |
| Centroides, τ, clústeres, especies (mismo esquema y encoder) | Menor o parche del paquete | No |
| Esquema del paquete (campo nuevo, tabla nueva) | Mayor del paquete | Sí, a la versión que lo lee. El servidor publica los dos formatos mientras queden apps viejas (se ve en Dispositivos). |
| Encoder (otro ONNX) | Mayor de app y mayor de paquete | Sí, obligatorio (`min_app_version`). Los paquetes quedan atados al `encoder_sha256`. |
| Servidor (API) | Versión de la API (`/api/v1`, `/api/v2`) | No mientras v1 siga viva. Se retira cuando ninguna app activa la use. |
| Revertir | Puntero del release vigente | No. La app baja la anterior en la siguiente sincronización. |

**C3 · Sincronización de observaciones.**
- La app sube a `observation-service` la foto, el vector de 512, GPS, altitud, sustrato y el `IdentificationResult`.
- Los rechazos pasan a una cola de auditoría con el BioCLIP 2.5 del servidor y llegan al Admin para revisión.
- Nunca crean especies ni publican solos.

**C4 · Telemetría de dispositivos.** Versión de la app y de cada paquete, espacio libre y última sincronización.

**C5 · Avisos.** `notification-service` + FCM a quien tiene la subregión cuando se publica un release.

**Área App del Admin con datos reales — hecho del lado servidor y Admin (2026-09-28).** Pedido del autor: Admin → App (`/movil`, Usuarios, Dispositivos, Observaciones) y Avisos mostraban datos inventados en el código (la vista general decía 1.284 usuarios / 946 teléfonos / 5.820 observaciones mientras las páginas listaban 42 / 53 / 56). Ahora todo sale del servidor; sin sesión del panel no se muestra ningún número, se pide iniciar sesión.
- **Hallazgo de la auditoría:** `observation-service`, `notification-service` y `validation-service` llevaban ~23 h detenidos (exit 137, `restart: unless-stopped` no los levanta tras un `docker stop`) — la web no podía subir ni editar observaciones. Se levantaron con `docker start`.
- **Hallazgo:** `auth.users.is_active` existía pero nadie lo revisaba: "suspender" no impedía entrar. Ahora el login por correo y el de Google rechazan una cuenta suspendida (los JWT ya emitidos duran hasta 1 día).
- `phase13.sql`: `auth.user_devices` gana `device_key` (una fila por instalación), `app_version`, `paquetes`, `espacio_libre_mb`, `last_seen`, `bloqueado` y motivo; `auth.users.suspension_reason`; `observations.review_reason`/`reviewed_at`; `dataset.centroide_regional`.
- **auth-service:** `GET/PATCH /api/panel/usuarios` y `/api/panel/dispositivos` (permiso "Administrar cuentas": son datos personales), `POST /api/auth/dispositivos` para que el teléfono se reporte (C4) — responde si está bloqueado. `/api/panel/me` devuelve además `userId` para firmar `audit.log` desde otros servicios.
- **observation-service:** `GET /api/observations/panel` (incluye privadas) y `PATCH /api/observations/panel/:id` (aprobar, rechazar con motivo obligatorio, "en revisión"), permiso "Revisar fotografías" — el herpetólogo revisa sin ver correos. El permiso lo decide auth-service (se reenvía el mismo token a `/api/panel/me`).
- **notification-service** (era solo `/health`): el Admin envía un aviso a todas las cuentas activas o a una; queda una fila por persona. La app y la web lo leen con `GET /api/notifications` y lo marcan con `POST /api/notifications/:id/leido` (sin FCM todavía).
- **Admin:** una sola fuente para las tarjetas (`AppKpis`, usada en Inicio, App, Operación y Analítica) y las páginas. Diseño revisado con `design-critique` y `ux-writing`: se quitó "Invitar" (hacía escribir nombre, correo y departamento que la persona vuelve a escribir al registrarse, y no tenía servidor) y las acciones que no hacían nada (reenviar invitación, restablecer contraseña, cerrar sesión remota, exportar, anonimizar, cambiar rol). Observaciones abre en "Por revisar" y, al aprobar o rechazar, pasa sola a la siguiente; el detalle de un usuario muestra sus observaciones y teléfonos con enlace directo, sin volver a buscar. Botón destructivo a la izquierda, principal a la derecha; la confirmación repite la acción ("Suspender cuenta", "Rechazar observación"); el motivo se pide una vez y queda en Auditoría. El proxy del Admin ahora pasa bytes (las miniaturas se corrompían como texto).
- **Centroides regionales reales (M3):** en la misma corrida que los globales, las observaciones con coordenada exacta (las ocultas de iNaturalist no cuentan) se ubican por point-in-polygon en geo-service (`/regiones/departamentos/:dane/ubicar`) y se asignan a la subregión de su municipio (Regiones). Regional propio con ≥ 3 individuos; si no, se guarda el par como "presta el global". Corrida #4: 45 propios y 57 prestados en las 9 subregiones de Antioquia; coseno regional-global mediano 0,958 (mín 0,759). La evaluación M3 sigue midiendo solo el global.
- Verificado: los endpoints nuevos rechazan sin sesión (401), con sesión devuelven 15 usuarios, 85 observaciones (todas "por revisar"), 0 teléfonos y 0 avisos reales; bloquear/desbloquear, avisos y validaciones (motivo obligatorio, no suspenderse a sí mismo, 404) probados con filas de prueba que después se borraron. En el Admin, con sesión, las cuatro pantallas y el diálogo de revisión con foto real.
- **Hecho (Android, 2026-09-28 noche):** la app llama `POST /api/auth/dispositivos` al abrir con sesión iniciada y tras cada login (modelo, versión de Android, versión de la app, paquetes regionales instalados, espacio libre); si el servidor responde bloqueado deja de sincronizar y avisa, si responde 403 suspendida cierra la sesión. Muestra `GET /api/notifications` en Ajustes → Avisos y marca cada uno leído al tocarlo (`POST /api/notifications/:id/leido`). Probado de punta a punta con el teléfono real: fila real en `auth.user_devices` (modelo, paquete Antioquia v1.1.0, espacio libre) y aviso de prueba marcado `is_read` desde la app. Pendiente: subir observaciones (C3). Hay 3 cuentas de prueba en `auth.users` (`test_panel_s1`, `phase2tester`, `copilot_test`) — decidir si se suspenden o se borran.

**C6 · Publicación de la app.**
- Un CI de Android firma el AAB y lo sube a pruebas internas de Play; el paso a producción es manual.
- `versionCode` sube en cada build.
- `/api/app/min-version` fuerza la actualización cuando cambia el encoder o un esquema que ya no se publica.

## Portainer: ¿sí o no?

**Sí, Portainer CE, con límites.** Encaja con un servidor con docker-compose y un solo operador:
- stacks desde el repo;
- logs y reinicio de contenedores;
- vista de volúmenes;
- webhook para redeploy desde el CI.

Límites:
- Monta el socket de Docker, así que es acceso de root al servidor. Va **solo** detrás de Cloudflare Access (o red interna) y nunca con el puerto publicado.
- En CE, los permisos por equipo son limitados.
- No reemplaza al CI ni a los respaldos.
- El Admin no depende de su API. Salud y métricas vienen de Prometheus (S2), y reiniciar un servicio se hace en Portainer, no en el Admin.

Descartados por ahora:
- **Kubernetes:** sobra para un servidor.
- **Coolify y Dokploy:** sirven, pero reemplazan a Nginx Proxy Manager, que ya funciona.

## Grafana en el Admin

```text
Admin (Next.js) ──► admin-api ──► Prometheus / Loki (vía Grafana o directo)
                         └──────► Postgres (ExperimentResult, releases, auditoría)
```

- **Sistema y Worker** (técnico, solo administrador): servicios arriba o caídos, latencia, jobs por minuto, GPU/VRAM del PC, errores y logs.
- **Resúmenes** (Inicio, Modelo, Operación): gráficas propias con un titular que dice la conclusión, como la tarjeta "Prueba con los datos reales" (barras viejo contra nuevo) y el avance del plan.
- Grafana también sirve como consola interna del operador. El herpetólogo no entra ahí.

## Qué se vuelve real, pantalla por pantalla

| Pantalla | Hoy | Real en |
| --- | --- | --- |
| Especies, Regiones, Ficha (altitud, presencia) | **Datos reales exportados** | M1 (desde la base) |
| Imágenes / Curación | Conteos reales; fotos y decisiones simuladas o en el navegador | M1 |
| Worker, DB vectorial | Simulado | M2, S2 |
| Centroides, Clústeres, OSR, Validación | Mecánica real sobre vectores simulados; resultado real en la tarjeta de prueba | M3 |
| Release | Flujo real de avales en el navegador; JSON con marcadores | M4, M5, S1 |
| Simulador | Contra el release publicado, vectores simulados | M3–M4 (foto real subida) |
| Métricas | Tarjeta real + explorador simulado | M5 |
| Actualizaciones | Releases reales del navegador; sin entrega | C1, C2 |
| Usuarios, Dispositivos, Observaciones, Notificaciones | **Reales desde el servidor** (2026-09-28); Dispositivos y Avisos ya los llena el teléfono real | C3 (subir observaciones, pendiente) |
| Sincronización | Simulado | C3 |
| Sistema | Topología real; estado simulado; plan | S1, S2, S3 |
| Auditoría | Simulado | S1 |
| Ficha pública, Explorador, carrusel (app y web) | Escritos a mano en el código, sin administrar | K, K2 |

## Revisión de lo ya hecho: qué quedó mal o incompleto (2026-09-27)

Pedido explícito del autor: revisar qué etapas anteriores quedaron mal y afectan lo que sigue.

- **F16 (Regiones/subregiones), gap heredado, ya corregido en la prueba real:** el corte de especie por subregión usaba un rango de altitud simulado. La exportación de datos reales (`export_admin_seed.py`) lo reemplazó por presencia real (point-in-polygon). Sin acción pendiente.
- **F17 (Worker):** el job ya descuenta las exclusiones manuales de Curación (cerrado en la sesión anterior). Sigue sin acción real: cuando exista M2, este flujo pasa tal cual al `model-service`.
- **F19 (Clústeres), cerrado (2026-09-27):** el entrenamiento ya es ArcFace real (margen angular aditivo, descenso de gradiente desde cero, sin librería), no el LDA anterior. Bug de la propia verificación: el `lr` inicial diverge con clústeres de más de ~20-30 muestras por época (colapsa a un prototipo, precisión cae a ~50 %); corregido con decaimiento por paso. Detalle en [[Prueba Real del Creador de Paquetes]] hallazgo 6. M3 hereda el mismo algoritmo, solo cambia dónde corre (en `model-service`, no en el navegador).
- **F23 (Compilador):** el JSON compilado no lo lee ninguna app — es el hallazgo #11 de [[Prueba Real del Creador de Paquetes]]. Bloqueante real: nadie debe seguir iterando la UI de Release sin decidir M4 (formato v2) primero, o se repetirá trabajo.
- **Carrusel y ficha pública (nuevo, no era una fase numerada):** estaban totalmente fuera del alcance de las fases 0–24 — se trataban como "vistas" de la app, no como datos administrables. Es la etapa K.
- **`ai-service` en el mismo compose que el servidor pago:** no era un error de código, era una decisión de infraestructura implícita. **Corregido en E0 (2026-09-27).**
- **`auth-service` caído, encontrado en E0:** faltan `src/models/User.js` y `UserPreferences.js` porque el `.gitignore` raíz (`models/`) los ignoró. Bloquea S1: hay que rehacerlos y anclar el patrón a `/models/`.
- **Nada de la Fase 0–24 quedó "a medias" en el sentido de bugs sin cerrar** — los tres bugs reales atrapados en verificación (F22 fingerprint, F23 fingerprint, F24 excludes) ya están corregidos y documentados en la auditoría. Lo que falta en todas las fases es lo mismo: conectar a datos y servicios reales, no arreglar lógica rota.

## `auth.users` por columnas, no tabla completa (2026-09-28)

**Problema.** Para que `GET /api/observations` dejara de fallar, una sesión anterior amplió el permiso de `observation_service` a `GRANT SELECT ON auth.users` (tabla completa). Funcionaba, pero con eso el rol podía leer `email`, `password_hash`, `google_id`, `profile_image_blob`, `suspension_reason` y el resto: si `observation-service` tuviera una inyección SQL, se llevaría los hashes de todas las cuentas. `explorer_service` y `thumbnail_service` tienen el mismo `GRANT` de tabla completa (lo documentado en [[Ficha Publica, Explorador y Destacados]] decía "solo username/foto", pero el `GRANT` real no lo limitaba).

**Qué columnas usa cada servicio de verdad** (grep de `auth.users` y de los alias en `src/`, sin `SELECT *` ni `u.*` en ninguno):

| Rol | Dónde | Columnas que lee |
| --- | --- | --- |
| `observation_service` | `observation.routes.js` (feed `GET /`, comentarios `GET /:id/comments`), `panel.routes.js` (`GET /api/observations/panel`) | `id`, `username`, `profile_image` |
| `explorer_service` | `explorer-service/src/index.js` (feed, favoritos, perfil, observadores, detalle, búsqueda y sugerencias) | `id`, `username`, `profile_image`, `created_at` (búsqueda de usuarios) |
| `thumbnail_service` | `thumbnail-service/src/index.js` (avatar) | `profile_image` (en el `WHERE`), `profile_image_blob` |

Las claves foráneas hacia `auth.users` (p. ej. `observations.comments.author_id`) no necesitan `SELECT` del rol que inserta: Postgres hace esa comprobación con los permisos del dueño de la tabla.

**Hecho para `observation_service` — aplicado y verificado en vivo:**
- `infrastructure/postgres/roles.sql`: `REVOKE SELECT ON auth.users FROM observation_service;` + `GRANT SELECT (id, username, profile_image) ON auth.users TO observation_service;`. El `REVOKE` va en el archivo a propósito: un `GRANT` por columnas no quita un `GRANT` de tabla completa anterior, así que sin él re-aplicar `roles.sql` sobre esta base dejaría el permiso ancho. (`roles.sql` sigue sin versionar en git.)
- Mismo `REVOKE` + `GRANT` aplicado con `psql` dentro de `anura_postgres`, en una transacción.

| Prueba | Resultado |
| --- | --- |
| `information_schema`: permiso de tabla de `observation_service` en `auth.users` | Ninguno; por columna solo `id, profile_image, username` |
| `SET ROLE observation_service` → `SELECT email` / `password_hash` / `*` | `permission denied for table users` (los tres) |
| `curl http://localhost:3002/api/observations` | 200, 50 filas, las 50 con `username` (mismo tamaño que antes del cambio) |
| `curl .../api/observations/:id/comments` | 200 |
| Consulta de `panel.routes.js` ejecutada como `observation_service` (el endpoint pide sesión del panel) | 85 filas, sin error |
| `docker logs anura_observations` | Sin `permission denied` |

Postgres comprueba los permisos por columna al planificar la consulta, no por fila, así que comentarios queda cubierto aunque hoy la tabla esté vacía.

**Propuesto para los otros dos roles — sin aplicar todavía** (mismo patrón; verificar después `/api/explorer/feed`, `/api/explorer/search`, un avatar por `/api/explorer/thumbnail/...` y los logs de `anura_explorer` y `anura_thumbnails`):

```sql
REVOKE SELECT ON auth.users FROM explorer_service;
GRANT SELECT (id, username, profile_image, created_at) ON auth.users TO explorer_service;

REVOKE SELECT ON auth.users FROM thumbnail_service;
GRANT SELECT (profile_image, profile_image_blob) ON auth.users TO thumbnail_service;
```

Regla que queda: ningún servicio distinto de `auth-service` recibe `SELECT` de tabla completa sobre `auth.users`. Si un servicio empieza a necesitar otra columna, se agrega esa columna al `GRANT`, no la tabla.

## Login real de la app y "Modo administrativo" en la web (2026-09-27)

Decisión del autor, aparte de las 18 etapas de arriba (esas son la identificación; esto es
cuentas de usuario de ANURA Mobile y de la web, y cómo llegan al panel). Ya hecho y probado:

- **La app Android abre Google en Custom Tabs, no un SDK nativo de Google.** Evita registrar
  un segundo cliente OAuth en Google Cloud Console — reusa el mismo login que ya funciona
  para la web (`GET /api/auth/google`). `?platform=mobile` viaja como `state` de OAuth (sin
  sesión ni servidor de estado, Google lo devuelve tal cual) y `auth-service` lo usa para
  redirigir de vuelta a `anura://auth/callback?token=...` en vez de al frontend web.
  `MainActivity` (`launchMode="singleTask"`) recibe ese deep link por `onNewIntent`, no
  reabre la app. Probado: `GET /api/auth/google?platform=mobile` sí trae `state=mobile` en
  la URL real de Google; `?platform` ausente sigue dando `state=web` (compatibilidad con la
  web, sin cambios). El botón vive en Iniciar sesión (`SignInScreen`), no en Bienvenida —
  no está en el board de Penpot todavía, falta reflejarlo ahí. El correo/contraseña de esa
  pantalla sigue siendo mock; solo Google quedó real.
- **"Modo administrativo" en la web (`frontend/`, no en la app — son cosas separadas) ya
  funciona de verdad.** Existía como prop `isAdmin` sin ningún dato real detrás (miraba
  `auth.users.role === 'admin'`, un campo que nadie pone nunca en 'admin') y un botón que
  navegaba a `/admin`, una ruta que no existe. Corregido: `isAdmin` ahora es real, sale de
  preguntarle a `auth-service` (`GET /api/panel/me`, la misma verificación de S1) si esa
  sesión es también cuenta del panel — dos autorizaciones separadas (rol de moderación
  contra cuenta del panel), no una mezclada con la otra. El botón (TopBar y el tab inferior)
  abre `admin/login?token=...` en pestaña nueva: el JWT que ya tiene la web sirve tal cual
  para el Admin (mismo mecanismo de S1). Probado en el navegador: la cuenta real que sí está
  en `auth.panel_accounts` ve el botón y entra sin pedir contraseña otra vez; una cuenta real
  que no está en el panel no lo ve. Se agregó `location /api/panel` al nginx del `frontend`
  (antes solo tenía `/api/auth` y `/api/preferences`) — NPM ya reenvía todo el dominio a ese
  contenedor, así que no hace falta tocar nada en NPM.

## Evaluación de la skill externa (2026-09-27)

El autor preguntó por `github.com/Jeffallan/claude-skills` (marketplace de 67 skills genéricas: `architecture-designer`, `cloud-architect`, `devops-engineer`, etc.) para planear este backend. **Veredicto: no aporta aquí.** Son plantillas genéricas (ADR, patrones de arquitectura de libro de texto, checklists de NFR) pensadas para partir de cero sin contexto de dominio. Este plan ya nace de algo más específico y verificado: el código real del repo, las cifras medidas con datos reales y las decisiones ya tomadas en 19_ADMIN. Instalarla agregaría un proceso de documentación (ADRs formales) que no hace falta para un solo autor con un vault que ya cumple esa función. No se instaló.

## Qué no se promete

- Resolver el rechazo de desconocidas. Con vectores reales, 3 de cada 4 todavía reciben un nombre. Mejorarlo es trabajo de modelo (más desconocidas para calibrar, clústeres bien armados, contexto), no de backend.
- Mediciones de GPU del worker. No hay benchmark en el vault; se miden en M2.

Relacionado: [[Arquitectura Desacoplada]], [[Worker Releases y Sandbox]], [[Roles del Admin]], [[Modelo de Datos del Admin]].
