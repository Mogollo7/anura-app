# ANURA — contexto de traspaso para continuar en Cursor

> Generado el 2026-09-29 al pasar el trabajo de Claude Code a Cursor. Léelo entero antes de tocar nada.
> Lo que aquí dice "verificado" lo comprobó una prueba que corrió; lo que dice "sin verificar" no se ha corrido.

## 0. Prompt para pegar en Cursor (primer mensaje)

```
Lee D:\Anura\CONTEXTO_CURSOR.md completo y D:\server\Anura\_pruebas\reglas_agentes.md.
Continúa el trabajo desde la sección 7 («Estado exacto al parar») y sigue la sección 8 («Lo que falta»),
en ese orden. Respeta la sección 1 (decisiones del usuario) y la sección 2 (reglas duras): no despliegues,
no borres datos y no hagas push sin que el usuario lo confirme. Antes de escribir código, revisa el
estado real con git (sección 7) porque tres agentes se cortaron a medias.
```

## 1. La intención (qué quiere el usuario y qué ya decidió)

**Meta global.** Auditar todo el sistema ANURA y eliminar TODO dato simulado o inconsistente, salvo C3, para poder
quitar del panel admin el aviso «mock banner» (`admin/src/components/layout/mock-banner.tsx`). Lo pidió con estas
palabras: «lo único que no tocamos es C3».

- **C3** = sincronización de observaciones y rechazos basada en BioCLIP en el servidor. No se toca.
- En el admin: flujos consistentes, sin lógica repetida; aplicar criterios de `/ux-writing` y `/design`
  (español neutro, frases cortas, verbo primero en botones, errores que dicen qué pasó y qué hacer,
  estados vacíos que guían).
- **Solo si todo queda no simulado (excepto C3):** vaciar el servidor y el móvil (observaciones, especies,
  paquetes, etc.), dejando únicamente al super usuario. Después el usuario reconstruirá él mismo
  **especie → paquete → observaciones**. El usuario ejecuta ese vaciado; nunca lo hagas tú sin confirmación
  explícita (sección 9).

**Decisiones ya tomadas (no las reabras):**

| Tema | Decisión |
|---|---|
| Consolas del pipeline ML que corrían en el navegador (Worker, DB vectorial, Centroides, Clústeres, OSR, Validación, Release, Simulador, Métricas) | **Servidor real** |
| «Paso a paso» (Android) | **Construir la clave dicotómica real**, a partir de datos reales |
| Audio ID / Sonidos nocturnos (Android) | **Excepción**: se queda como demo, claramente marcada como demo |
| Despliegue (Docker) | **Al final de todo**, no antes |
| Vaciado de datos | Solo al final, con copia de seguridad y confirmación explícita |
| Web pública | Solo navegación: sin identificar especies, sin luz roja. Comentarios y refutar sí. Invitado lee pero no comenta |

## 2. Reglas duras (para ti, Cursor)

1. **No despliegues ni reconstruyas contenedores** hasta que el usuario lo autorice. Producción (`anura_*`) está apagada
   desde el 2026-09-28; déjala así. Nunca pruebes contra `anura_postgres`.
2. **No hagas `git push`.** Commits locales por bloque sí, con mensaje en español y un solo tema.
3. **No borres datos** de ninguna base real ni de MinIO. El vaciado es la sección 9 y requiere confirmación.
4. **No inventes datos**: ni especies, ni umbrales, ni valores «de relleno». Una tabla vacía se muestra como estado vacío
   honesto («Aún no hay …. Para empezar, …»).
5. **No leas ni copies secretos.** Las claves reales viven en `.env` (ignorado por git). Las pruebas usan claves de
   prueba sin valor.
6. Todo lo que hagas en Android compílalo (`./gradlew :app:compileDebugKotlin`); en el admin `npx tsc --noEmit`.

## 3. Mapa del proyecto

| Pieza | Ruta | Stack |
|---|---|---|
| App Android | `D:\Anura\anura-android` | Kotlin, Jetpack Compose, Room, WorkManager, ONNX + sqlite-vec |
| Admin (panel) | `D:\server\Anura\admin` | Next.js 16 (Turbopack), TypeScript, Tailwind |
| Web pública | `D:\server\Anura\frontend` | React + Vite |
| Servicios | `D:\server\Anura\services\*` | Node/Express: auth, observation, explorer, dataset, geo, notification, thumbnail, validation; ai-service en Python |
| Base y migraciones | `D:\server\Anura\infrastructure\postgres` | Postgres 16 + PostGIS + pgvector; `init.sql` + `phase2..phase22.sql` idempotentes; `03-roles.sh` las aplica |
| Compose de producción | `D:\server\Anura\docker-compose.server.yml` | servicio `db-migrate` monta cada `phaseN.sql` |
| Bóveda de conocimiento | `D:\Anura\Second Brain\Brain\` | Obsidian; fuente de verdad del proyecto |

**Repos git.** Dos: `D:\server\Anura` (servidor, admin, web) y `D:\Anura` (Android + documentos + bóveda).
El repo de Android tiene mucho trabajo sin commitear de sesiones anteriores (74 archivos en `anura-android`).

**Dominio público:** `https://anura.juanlabs.me` (web) — hoy caído porque los contenedores están parados.

### Arquitectura del panel (admin)
- `usePanelSession` (`lib/session/panel-session.ts`): estados `"cargando" | "sin-sesion" | "real"`. No hay modo demo.
- `SessionGate` redirige a `/login`. El token llega como `#token=` (se limpia con `history.replaceState`).
- Rutas proxy del admin: `/api/{dataset,panel,auth,observations,notifications,thumbnail}`; variables
  `AUTH_SERVICE_URL`, `DATASET_SERVICE_URL`, `OBSERVATION_SERVICE_URL`, `NOTIFICATION_SERVICE_URL`, `THUMBNAIL_SERVICE_URL`.
- Clientes: `lib/dataset/dataset-client.ts` (+ `etiquetas.ts`, `ficha.ts`, `osr.ts`), `lib/release/release-client.ts`,
  `lib/vectores/vectores-client.ts`, `lib/app-data/app-client.ts` (app móvil: usuarios, teléfonos, observaciones, avisos).
- Permisos del panel: `lib/auth/panel-accounts.ts` (`session.can('definirMorfo')`, etc.).
- Reglas del dataset (una sola definición): `admin/src/lib/dataset/reglas.ts` y `services/dataset-service/src/reglas.js`
  (`MIN_FOTOS_ENTRENABLE=10`, `MIN_INDIVIDUOS=3`, `GRUPO_A_MIN_INDIVIDUOS=200`). Deben coincidir.

### Arquitectura del dataset-service (Express, CommonJS, nombres en español)
- Rutas en `src/index.js` con `requirePanelAction('<permiso>')` (deja `req.panelAccount` y `req.userId`).
- Errores con `falla(msg, status)`; auditoría con `src/audit.js` → `registrar(db, userId, action, targetType, targetId, metadata)`.
- Cada tema en su módulo: `etiquetas.js`, `ficha.js`, `altitud.js`, `especies.js`, `vectores.js`, `centroides_morfo.js`,
  `clusteres.js`, `osr.js`, `mahalanobis.js`, `evaluacion.js`, `simulador.js`, `validacionTecnica.js`, `release.js`,
  `paqueteSqlite.js`, `clave.js` (en curso). `roles.sql` da al rol `dataset_service` el esquema `dataset`.
- Rutas públicas sin auth: `/api/dataset/publico/{paquetes,catalogo,manifiesto,fotos}`.

## 4. Entorno de pruebas desechable (todo en `D:\server\Anura\_pruebas\`)

Esta carpeta la creé al traspasar; contiene los scripts que usé. Está sin commitear (decide tú si versionarla).

- **Postgres de prueba** (imagen de producción PostGIS + pgvector `anura-postgres:16-3.4-pgvector`, puerto
  `127.0.0.1:55432`, usuario `postgres`, clave `prueba`). Crear una base con todas las migraciones:
  ```bash
  sh D:/server/Anura/_pruebas/bd_prueba.sh <nombre_bd>
  ```
  Crea el contenedor `anura_test_pg` si falta, crea la base y aplica `init.sql` + `03-roles.sh`. Es idempotente:
  vuelve a correrlo tras añadir una migración. Para empezar limpio: `docker exec anura_test_pg dropdb -U postgres --force <bd>`.
- **Pruebas por bloque** (`prueba_*.js`, cada una contra su base): `etiquetas` (bloque 1), `ficha` (2), `especies` (3),
  `vectores` (5), `osr` (6), `release` (4), `salidas` (7), `explorer`. Se corren desde el servicio correspondiente, p. ej.
  `cd D:/server/Anura/services/dataset-service && node D:/server/Anura/_pruebas/prueba_ficha.js`.
  - `prueba_release.js` necesita un MinIO de prueba:
    `docker run -d --rm --name anura_test_minio_release -e MINIO_ROOT_USER=prueba -e MINIO_ROOT_PASSWORD=prueba-prueba -p 127.0.0.1:39139:9000 minio/minio:latest server /data`
  - `prueba_salidas.js` y `prueba_explorer.js` usan express/pg/jsonwebtoken: `cd D:/server/Anura/_pruebas && npm i`
    y corre con `NODE_PATH=D:/server/Anura/_pruebas/node_modules`.
- **Entornos de UI aislados** (`entorno_*.js`): levantan un auth de mentira (súper usuario), un dataset-service local
  contra la base de prueba y `next dev` del admin en un puerto propio con `NEXT_DIST_DIR=.next-<nombre>`. Cada uno usa
  puertos distintos (ver el archivo). JWT falso para entrar: en `localStorage['anura-admin:panel-jwt:v1']` poner
  `<b64url({alg:'HS256',typ:'JWT'})>.<b64url({id:'d81f2281-6086-435e-9de6-603f766fdf5e'})>.firma`
  (e insertar ese usuario en `auth.users` de la base de prueba con `username` y `email`).
- **Trampas conocidas:**
  - `next dev` reescribe `admin/tsconfig.json` (añade las carpetas `.next-*`): hazle `git checkout -- admin/tsconfig.json` antes de commitear.
  - Los `.sh` y las `phaseN.sql` deben ir con **LF** (`.gitattributes` ya lo fuerza); con CRLF fallan dentro del contenedor.
  - `roles.sql` corre antes que `phase4.sql`: por eso crea el esquema `dataset` él mismo (ya arreglado).
  - `geo-service` no está en el entorno de prueba: el dataset-service responde 502 claro cuando falta.

## 5. Lo que ya está hecho y verificado (commits en `D:\server\Anura`)

| Bloque | Qué quedó real | Commit |
|---|---|---|
| Fase 1 | Panel sin modo demo; login real; dashboard, operación, auditoría, sistema, modelo desde el servidor; auth sin autoasignarse rol admin | base `7e66264` + fases previas |
| 1 | Morfos por subregión y estadio/sustrato/morfo por individuo (`phase15`, `etiquetas.js`, tarjeta Morfos) | `1ce2ce9`, `cb0f26a`, `68a0ae5` |
| 2 | Altitud por observación y Ficha técnica calculada (`phase16`, `ficha.js`, `altitud.js`) | `c0b95c6` |
| 3 | «Añadir especie» y Especies contra el servidor (`phase17`, `especies.js`, `taxon_id` COL_ANURA_NNNN) | `429a008` |
| 5 | Worker, DB vectorial, centroides por morfo, Clústeres (`phase19`) | `4ce900a` |
| 6 | OSR (Mahalanobis + Ledoit-Wolf, igual que el teléfono), Métricas, Simulador (`phase20`); borrados los mocks | `a551d40` |
| — | Explorador y búsqueda leen `dataset.especie_publica` (`phase22`) | `48208b6` |
| 4 | Validación técnica, Release con dos aprobaciones distintas, Actualizaciones (`phase18`); el APK ya no trae paquete | `d1c2e9f` |
| 7 | Salidas de campo app → servidor → web (`phase21`) | `fe1b9aa`, `547dbbf` |

Pruebas que pasaron en su momento: etiquetas, ficha, osr, release, salidas, explorer (21), especies (14 bloques),
vectores. `npx tsc --noEmit` del admin estaba limpio salvo el residuo conocido de `.next/types/validator.ts` sobre
`paquetes/[id]` (ignorable).

**Cómo funciona el ciclo real ahora:** una especie se crea en `dataset.especie` (una sola escritura) → se publica su
ficha en Contenido (`dataset.species_content`) → aparece en el catálogo público y en el Explorador → se cargan fotos y
vectores → se calculan centroides → se calibra y valida el umbral OSR → se compila el paquete de una subregión
(`packages.regional_packages`, borrador → aprobado con dos cuentas distintas → publicado) → el teléfono lo descarga.

## 6. Limitaciones reales (no son simulación; están dichas en la UI o aquí)

- El paquete lleva vacías las tablas de prior de zona y de clima: la app no ajusta por zona ni clima.
- Android sigue usando el modelo Open Set que viene en el APK: el umbral validado viaja en el paquete pero la app aún
  no lo lee, y `allowed_by_package.json` usa la clave `ANTIOQUIA`.
- El manifiesto del paquete lleva sha256 pero no firma Ed25519.
- El simulador del admin no puede embeber fotos nuevas (el encoder solo corre en el worker del PC): trabaja con fotos ya embebidas.
- Entrenar el micro-adaptador (matriz W 512×64) en el worker y meterlo al paquete no existe; la UI no ofrece «Entrenar».
- Clústeres decididos en `dataset.cluster`: el paquete ya los incluye; falta que el rechazo del teléfono los use.
- La app no registra la ruta GPS de las salidas de campo, ni notas de sesión/clima en el servidor.
- `explorer-service` cuenta también observaciones privadas en `/species`, `/search`, `/observers` (ya existía).
- `species.taxonomy` y `species.distribution` quedan sin lectores (no se borraron); `observations.lookup_iucn` es código muerto.
- `infrastructure/postgres/init.sql` tiene un cambio sin commitear que **no es mío** y quita columnas de `auth.users`
  (`profile_image_blob`, `biography`, `preferences_completed`): revísalo antes de commitear o de reconstruir la base.
- Web: `mocks/`, `demoMode.js`, `DemoData.jsx` y `taxonFallbackData.js` se estaban borrando (ver sección 7).

## 7. Estado exacto al parar (3 agentes se cortaron por límite de uso)

Comprueba con `git status` en ambos repos. Al parar había, **sin commitear y sin verificar**:

### 7.1 Agente «clave» — Paso a paso real (Opus) — **cortado**
- Creó `services/dataset-service/src/clave.js` (sin commitear) y 12 líneas nuevas en `services/dataset-service/src/index.js`.
- Modificó pasos del asistente de Android: `feature/capture/CaptureStep1Screen.kt`, `CaptureStep3Screen.kt`, `CaptureStep4Screen.kt`.
- Estaba ajustando `resolver` (semántica de «pendientes»). No se sabe si compila ni si tiene pruebas.
- Su encargo completo está en la sección 8.1.

### 7.2 Agente «catalogo-android» (Opus) — **cortado**
- Creó `core/data/ContentCatalog.kt` y `core/data/PackageCatalog.kt`; modificó `SpeciesCatalog.kt` y
  `feature/home/HomeCarouselCatalog.kt`. Sin verificar.
- Encargo completo en 8.2.

### 7.3 Agente «barrido» (Sonnet) — **cortado**
- Web: borró el modo demo (`DemoModeBadge.*`, `demoMode.js`, `mocks/demoApi.js`, `mocks/demoData.js`, `DemoData.*`,
  `species/taxonFallbackData.js`) y editó `App.jsx`, `AuthenticatedLayout.jsx`, `format.js`, `TaxonDetail.*`, `services/api.js`.
  Falta correr `npm run build` para confirmar que no quedan imports rotos.
- Su última acción fue reemplazar un bloque de «bioacústica inventada» por un estado vacío honesto.
- **El aviso `mock-banner.tsx` NO se ha tocado todavía.** Encargo completo en 8.3.

### 7.4 Otros pendientes de commit
- Android (`D:\Anura\anura-android`): 74 archivos sin commitear = trabajo de sesiones anteriores + bloque 4 (paquete
  descargado, sin `LocalPackageCatalog.kt` ni asset) + bloque 7 (`FieldTripsRemote.kt`, sesiones de campo) + lo de 7.1 y 7.2.
  Compila hasta el bloque 7 (`:app:compileDebugKotlin` pasó); lo de 7.1/7.2 no se ha compilado.
- `admin/tsconfig.json` modificado por `next dev`: revertir (`git checkout -- admin/tsconfig.json`).

## 8. Lo que falta, en este orden

### 8.1 Terminar «Paso a paso» = clave dicotómica real (Android + un módulo de servidor)
Hoy «Paso a paso» es el asistente de 6 pasos (`CaptureStep1..6Screen.kt`, `CaptureSvlScale.kt`, `CaptureWizardChrome.kt`)
donde la persona describe el animal a mano y termina en un resultado sin especie real. Debe volverse una clave real:
1. La clave se construye **a partir de datos reales**, nunca de conocimiento taxonómico inventado: especies del paquete
   instalado, `dataset.morfo`, `dataset.observacion_etiqueta` (estadio/sustrato/morfo), altitud p5–p95 por especie
   (`ficha.deEspecie`), `dataset.species_content`, subregión.
2. Preguntas **adaptativas**: cada respuesta filtra las especies compatibles y la siguiente pregunta es la que más separa
   las restantes (ganancia de información). «No sé» permitido en cada paso y no filtra.
3. Debe evaluarse **offline** en el teléfono. Endpoint público mínimo `GET /api/dataset/publico/clave?subregion=` (ya
   empezado en `clave.js`) o incluirla dentro del paquete (`paqueteSqlite.js`): decide y documenta el formato.
4. Resultado: 1 especie → ficha; varias → candidatas ordenadas con lo que las separa; ninguna → «desconocido» con mensaje honesto;
   sin paquete → estado claro que lleva a descargarlo.
5. Elimina todo lo simulado del asistente. Pruebas en node contra una base propia (6–8 especies con morfos, altitudes y
   sustratos conocidos: la primera pregunta es la de mayor ganancia, «no sé» no filtra, indistinguibles quedan juntas).

### 8.2 Android: catálogo y contenido reales
El usuario borrará todo; después la app no puede mostrar ninguna especie que no venga del servidor. Hoy hay ~30 especies
hardcodeadas en `core/data/SpeciesCatalog.kt`, carrusel con `HomeCarouselCatalog.legacyItems()` (especies de ejemplo) y
fotos/JSON empaquetados en `assets`/`res`. Debe pasar a datos del servidor (`/api/dataset/publico/catalogo`, fichas
publicadas, `dataset.destacado` para el carrusel) con caché en Room/archivos (offline tras la primera descarga),
fotos por URL con caché (Coil), sincronización con el WorkManager existente (`AvisosPollWorker`) y estados vacíos
honestos («Aún no hay especies publicadas…», «Conéctate para cargar las especies.»). Si faltan endpoints públicos,
módulo nuevo `services/dataset-service/src/publicoApp.js`. No tocar `feature/capture/**` mientras se hace 8.1. No tocar el
audio demo. Borrar los assets de especies que queden sin uso.

### 8.3 Barrido final (admin, web, servicios)
- Admin: buscar lo que quede simulado (`lib/mock/*` sobreviviente, `lib/data/real.ts` con `REAL_COMPARISON` sin uso,
  `localStorage` para datos de dominio, `Math.random`, arrays literales mostrados como reales, textos «mock/demo/simulado/
  ensaya/prototipo», etiquetas internas `phase:` visibles en `config/nav.ts`, enlaces rotos). **Recorrer TODAS las rutas
  de `config/nav.ts` con una base recién creada** y confirmar que cargan sin errores de consola/red y con estados vacíos
  que guían. Coherencia: una sola regla «entrenable», un solo componente de estado vacío/error/carga (`DataState`),
  botones con verbo primero, confirmación en acciones destructivas, sin dos formularios para la misma acción.
- Cuando no quede nada simulado (verificado pantalla por pantalla): **borrar `mock-banner.tsx` y su uso en el layout**.
  Si queda algo, el banner lista con precisión solo eso.
- Web: terminar de quitar el modo demo (sección 7.3), `npm run build`, grep de imports rotos.
- Servicios: buscar datos sembrados/hardcodeados que parezcan reales y fallbacks silenciosos que devuelvan datos falsos.
  Los SQL de seed con especies/observaciones de ejemplo se reportan, no se borran a escondidas
  (`seed_regiones_antioquia.sql` es geografía real y se queda).

### 8.4 Después de 8.1–8.3
1. Compilar Android y correr todas las pruebas de `_pruebas`. `npx tsc --noEmit` limpio. `vite build` de la web.
2. Commitear por bloques en los dos repos (nada de push).
3. Reunir el reporte final para el usuario: qué queda real, qué queda como limitación (sección 6), qué se probó y qué no
   (no se ha probado en un teléfono real de punta a punta).
4. **Solo entonces** pedir permiso para el despliegue (sección 9) y, después, para el vaciado.

## 9. Despliegue y vaciado (NO ejecutar sin confirmación del usuario)

### 9.1 Despliegue (el usuario dijo «al final de todo»)
1. Reconstruir las imágenes de: `auth`, `observation`, `explorer`, `dataset` (cambió a `node:22-bookworm-slim` por
   sqlite-vec), `frontend` y `admin`; volver a correr `db-migrate` para aplicar hasta `phase22.sql` (más `phase23`/`24`
   si se crean). Servicios del compose: `auth-service`, `observation-service`, `explorer-service`, `dataset-service`, `frontend`, `admin-web`, `db-migrate`.
   Comando de referencia (desde `D:\server\Anura`): `docker compose -f docker-compose.server.yml up -d --build db-migrate auth-service observation-service explorer-service dataset-service frontend admin-web`.
   Antes, verifica que `.env` tenga las variables (`DATASET_DB_PASSWORD`, etc.).
2. Tras aplicar `phase16` en producción hay que ejecutar «Calcular altitudes faltantes» por especie.
3. Comprobar `https://anura.juanlabs.me`, el login del admin y `GET /api/dataset/publico/paquetes`.

### 9.2 Vaciado (irreversible)
Solo si el barrido confirma que nada está simulado (salvo C3 y el demo de audio) **y el usuario lo confirma en el chat**:
1. **Copia de seguridad primero**: `pg_dump` de la base `anura` y copia del bucket de MinIO. Enseña al usuario dónde quedó.
2. Identifica al **super usuario** (`auth.panel_accounts` con `is_super = TRUE`; su `user_id` apunta a `auth.users`) y conserva
   solo eso. Revisa qué tablas cuelgan de `auth.users` antes de truncar.
3. Vacía: `dataset.*` (especies, fotos, observaciones del dataset, embeddings, centroides, morfos, clústeres, OSR,
   evaluaciones, paquetes, contenido, destacados, trabajos), `observations.*` (observaciones, comentarios, favoritos,
   salidas de campo), `packages.*`, `notifications.*`, `audit.log` (decide con el usuario), y los objetos de MinIO
   correspondientes. **Conserva** la geografía (`dataset.region/subregion/subregion_municipio`) y los encoders registrados
   si el usuario así lo quiere; pregúntalo.
4. Móvil: la app guarda un snapshot en Room; para vaciarlo hay que limpiar los datos de la app o desinstalar (el usuario lo hace).
5. Al terminar, comprobar que el admin abre con todo vacío y que el super usuario entra.

## 10. Convenciones y preferencias (importante para mantener el estilo)

- Idioma de la interfaz y del código de dominio: **español** (identificadores en español en dataset-service).
- Estilo de commits: `tipo(ámbito): resumen en español` + cuerpo con el porqué. Una sola idea por commit.
- UI del admin: reutiliza `components/ui/*` (Card, Badge, Button, Field/Input/Select, DataState) y los tokens existentes.
- Android: Compose, paquete `me.juanlabs.anura`; textos en `res/values/strings.xml` (español); accesibilidad con
  `semantics`/`liveRegion` y objetivos táctiles amplios. El proyecto se llama **ANURA** (no «anura-android»).
- Cuando algo se rompe por permisos de Postgres: cada servicio tiene su rol (`auth_service`, `observation_service`,
  `explorer_service`, `dataset_service`, …) con permisos por esquema/columna en `roles.sql` y en las `phaseN.sql`.
  «Corregido» no es «aplicado»: hay que correr la migración en la base real (`db-migrate`).
- Si añades una migración: nuevo número (`phase23.sql`), idempotente, registrada en `03-roles.sh` **y** montada en
  `docker-compose.server.yml`, con GRANTs en la propia phase.

## 11. Rutas de referencia rápida

- Reglas para agentes (las mismas que usé): `D:\server\Anura\_pruebas\reglas_agentes.md`
- Plan y documentos previos del proyecto: `D:\Anura\PLAN_DESARROLLO.md`, `ESTADO_PROYECTO_2026-09-13.md`,
  `SPECIES_LIFECYCLE.md`, `VALIDATION_GATE.md`, `EMBEDDING_CONTRACT.md`, `OPEN_SET_MOBILE_ARCHITECTURE.md`
- Copia de seguridad del admin antes de la fase 1: `D:\server\Anura\_respaldos\admin-src-2026-09-28-antes-fase1.tar.gz`
- Transcripción completa de esta sesión (si necesitas un detalle exacto):
  `C:\Users\user\.claude\projects\D--Anura\311511b4-f5bd-44fd-b541-5e93b3bfa860.jsonl`
- Reglas de Cursor ya existentes: `D:\Anura\.cursor\rules\anura-compose-spacing.mdc`

## 12. ACTUALIZACIÓN 2026-09-29 (posterior a Cursor) — estado final

Esta sección **reemplaza** a las secciones 7 y 8 (ya cumplidas) y a lo que diga 9.1 (ya ejecutado).

- **Hecho y commiteado** (server: `b7498c1`, `44d1d78`, `f57b5a3`; Android: `b99184a`, `ea0a600`):
  Paso a paso con clave real; catálogo del teléfono solo desde lo publicado (sin las 30 especies del APK ni sus fotos);
  el paquete lleva el modelo Open Set validado (`open_set_model`, formato ANOS v1) y el teléfono lo carga del paquete
  (sin modelo no acepta identificaciones); `versiones.js` crea la versión del dataset desde el admin (una base vacía
  antes no podía calcular centroides/OSR/release); recorrido de las 32 rutas del admin con base vacía y con datos;
  auditoría de seguridad con 6 vulnerabilidades corregidas (entre ellas la toma de la cuenta super por mayúsculas y la
  lectura de archivos por `..` en miniaturas).
- **Verificado:** `_pruebas/correr_todo.sh` (14 suites, todas pasan con bases nuevas), `tsc` limpio, `next build` del
  admin, `vite build` de la web, `:app:compileDebugKotlin` + `:app:testDebugUnitTest` de Android.
- **Desplegado el 2026-09-29** con `docker compose -f docker-compose.server.yml up -d --build` tras aplicar
  `db-migrate` («phase 2 a 22 listas»). Copias previas en `D:\server\Anura\_respaldos\`:
  `anura-pre-despliegue-20260929.dump` (pg_dump -Fc), `minio-pre-despliegue-20260929.tgz` (8,7 GB) y `uploads-thumbnails`.
  Producción tras el despliegue: 43 especies, 12.209 fotos, 100 observaciones de la app, 1 super, **0 fichas publicadas,
  0 paquetes** (el catálogo público está vacío hasta que se publique desde el admin).
- **NO se hizo el vaciado** (sección 9.2): el usuario lo rechazó por ahora. No lo hagas sin que lo pida.
- **Sigue sin verificar:** prueba de punta a punta en un teléfono real; `OnDeviceInferenceTest` (instrumentada).
- **Pendientes conocidos** (no son simulación): falta `MINIO_PUBLIC_ENDPOINT` en el `.env` real (las fotos del panel solo
  cargan en este PC); mover `ADD COLUMN profile_image_blob` de `migrate_profile_image_blob.sql` a una phase; cuenta de
  panel reclamable por la primera persona que se registre con ese correo (no hay verificación de correo); sin límite de
  intentos de login; `/api/geo` y `/api/predict` abiertos en nginx; puertos de MinIO/pgAdmin/NPM en `0.0.0.0`;
  `VITE_ADMIN_URL` no se pasa al construir la web (el botón «ir al Admin» apunta a localhost:3010).
- Limitaciones reales (sección 6): el paquete no ajusta por zona ni clima; el manifiesto del paquete sin firma Ed25519;
  el simulador solo usa fotos ya embebidas; sin entrenamiento de micro-adaptador.
