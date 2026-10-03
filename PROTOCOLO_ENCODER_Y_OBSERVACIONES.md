# Protocolo del encoder y de las observaciones (servidor ↔ app Android)

Este documento fija tres cosas:

- **Parte A.** Cómo cambiar el encoder (el ONNX que convierte una foto en un vector de 512) sin romper a las apps que ya están en la calle.
- **Parte B.** Cómo subir el ONNX al servidor **fragmentado** y cómo el servidor lo reensambla y lo valida.
- **Parte C.** Cómo se comportan las observaciones públicas y privadas entre el servidor y el celular.

**Reparto del trabajo:**

- **Servidor (`D:\server\Anura`):** este documento es solo el protocolo. Se implementa aparte, no hay código de servidor en este repo.
- **App Android (`anura-android/`):** ya está en código (paquete `core/encoder/` y `core/data/ObservationVisibility*.kt`). Las secciones A.3, A.6, C.3 y C.4 describen lo que la app implementa; el servidor solo debe respetar los contratos de API.

El servidor ya soporta la Parte A. Las Partes B y C son diseño nuevo, todavía sin implementar en el servidor.

---

# Parte A. Protocolo del encoder

## A.1 Idea central

- Un encoder se identifica por el **sha256 de su archivo ONNX**. Dos vectores solo se comparan si salen del mismo sha.
- Cada paquete regional dice con qué encoder se calculó: `package_info.encoder_onnx_sha256` (y `paquete.json → encoder.sha256`).
- Para cada paquete, la app usa **el modelo cuyo sha coincide con el del paquete**. Nunca mezcla.
- El servidor anuncia el encoder **activo** y los demás ONNX que guarda. La app baja lo que le falta.

## A.2 API del servidor (pública, sin sesión)

### `GET /api/dataset/publico/encoder`

```json
{
  "esquema": 1,
  "activo": {
    "sha256": "b3f1…64 hex",
    "nombre": "bioclip_anura_v2",
    "archivo": "encoder_anura_v2_fp16.onnx",
    "dimension": 512,
    "preprocesado": "RGB 224x224 open_clip",
    "normalizacion": "L2 (embedding / ||embedding||)",
    "bytes": 175123456,
    "url": "/api/dataset/publico/encoder/b3f1…/archivo"
  },
  "modelos": [ { "...mismo formato; el activo va primero..." } ]
}
```

- `activo` es `null` si todavía no se activó ningún encoder con ONNX en el servidor. En ese caso la app sigue con el modelo que trae empaquetado.
- La respuesta lleva `Cache-Control: no-cache`.
- No va firmada. La garantía es el sha256 (regla A.3.3).

### `GET /api/dataset/publico/encoder/{sha256}/archivo`

- Responde `302` a una URL firmada de MinIO. Vale 10 minutos para **empezar**; una descarga ya iniciada no se corta.
- Admite `Range`, así que se puede reanudar. Si la URL expira, pide el `302` otra vez y continúa con `Range: bytes=<ya_descargado>-`.
- Responde `404` si ese sha no tiene ONNX en el servidor.

## A.3 Reglas para la app

1. **Almacenamiento por sha.** Guarda cada modelo bajo su sha, por ejemplo `files/models/<sha256>/encoder.onnx`. Nunca sobrescribas un archivo: un sha nuevo es una carpeta nueva.
2. **Cuándo consultar.** Al abrir la app y antes de descargar o actualizar un paquete, con Wi‑Fi. Si falla la red, sigue con lo que tienes.
3. **Verificar siempre.** Descarga a un archivo temporal y calcula el sha256 completo. Compáralo con el `sha256` del manifiesto.
   - Si no coincide: borra el temporal, no lo uses y reintenta luego.
   - Si coincide: mueve el archivo a su carpeta final con un renombrado atómico.
4. **Elegir modelo por paquete.** Al identificar con el paquete P, usa `models/<P.encoder_onnx_sha256>/encoder.onnx`.
   - Si no lo tienes, descárgalo antes de instalar el paquete. Está en `modelos` del manifiesto.
   - Si no está en `modelos` ni en local, **no instales ese paquete** y avisa «actualiza la app».
5. **Transición** cuando cambia el activo:
   - Baja el modelo nuevo en segundo plano.
   - Sigue identificando con el viejo mientras tengas paquetes del encoder viejo.
   - Cuando todos tus paquetes instalados sean del sha nuevo, borra los modelos que ningún paquete use.
6. **Compatibilidad de formato.** El ONNX debe cumplir el contrato de A.4. Si el manifiesto trae `esquema` distinto de 1 o `dimension` distinta de 512, ignóralo y conserva el actual.
7. **Espacio.** Comprueba que el espacio libre sea ≥ 2 × `bytes` antes de bajar (temporal + final).
8. **Retroceso.** Si el servidor reactiva un encoder anterior, el `activo` vuelve al sha viejo. La app no necesita nada especial: solo la regla 4 y conservar los modelos mientras algún paquete los use.

## A.4 Contrato del ONNX

| Tema | Valor |
|---|---|
| Entrada | tensor `imagen` float32 `[1,3,224,224]` |
| Salida | tensor `embedding` float32 `[1,512]` |
| Preprocesado | RGB, lado corto a 224 (bicúbico), recorte central 224×224, `/255`, media `0.48145466, 0.4578275, 0.40821073`, desviación `0.26862954, 0.26130258, 0.27577711` (open_clip) |
| Normalización | L2: `v / ‖v‖` |
| Distancia | coseno |
| Dimensión | 512 (el servidor guarda `vector(512)`; otra dimensión exige migrar la base y los paquetes) |

Cambiar el preprocesado o la dimensión no es un cambio de encoder, es un cambio de contrato. Toca la base, el worker y el compilador de paquetes, así que hay que avisar antes.

## A.5 Procedimiento en el servidor para cambiar de encoder

1. **Entrenar y exportar** el ONNX nuevo en el PC (`encoder_..._fp16.onnx`).
2. **Subirlo al servidor** con el método fragmentado de la Parte B (el cliente de línea de comandos del PC también se implementa aparte, siguiendo B.2 y B.4). Queda guardado en MinIO y registrado como **inactivo**. Su sha256 lo imprime el comando.
3. **Worker con el encoder nuevo.** En el `.env` del PC con GPU:
   ```
   ENCODER_PATH=/app/models/encoder/encoder_nuevo_fp16.onnx
   ENCODER_ID=bioclip_anura_v2
   ENCODER_CHECKPOINT=bioclip_anura_v2_mejor.pt
   ```
   Reinicia `model-service`. Esto declara el sha del archivo al servidor.
4. **Calcular vectores.** Admin → Worker → «Nuevo trabajo de vectores», eligiendo el encoder nuevo. Espera al 100 % en la barra «fotos con vector».
5. **Activar.** Admin → Worker → tarjeta de encoders → «Activar». El servidor lo rechaza si falta el ONNX o si hay fotos de entrenamiento sin vector. Desde ese momento:
   - los centroides, la validación y los paquetes nuevos usan el encoder activo;
   - los borradores hechos con el anterior quedan «desactualizados»;
   - los paquetes **ya publicados** siguen válidos para sus apps, porque llevan su propio sha.
6. **Recalcular** centroides y umbral OSR. Compilar el paquete de cada subregión, aprobar (científica + técnica) y publicar, como siempre.
7. **Apps.** Al abrirse ven el manifiesto, bajan el modelo nuevo (regla A.3.5) y luego los paquetes nuevos.
8. **Retiro del anterior.** Cuando ninguna app dependa de él, no hace falta nada en el servidor. El ONNX viejo se queda guardado: ocupa espacio, pero permite volver atrás.

**Volver al encoder anterior:** Admin → Worker → «Activar» en el viejo (sus vectores siguen en la base) y recompilar y publicar sus paquetes.

## A.6 Estado en `anura-android`

Implementado en `core/encoder/` (manifiesto, almacenamiento por sha, descarga con `Range` + verificación + renombrado atómico, limpieza, selección por paquete). Pendiente de cablear: llamar a `EncoderSync.sincronizar()` al abrir la app y antes de instalar un paquete, y usar `EncoderResolver.rutaPara(sha)` donde se crea el `ImageEncoder`.

## A.7 Límites actuales

- El manifiesto del encoder no va firmado (el catálogo de contenido sí, con Ed25519). Hoy la integridad depende del sha256 que viene en `package_info` de cada paquete. Si se quiere firmar el manifiesto, se añade con la misma clave del catálogo.
- La dimensión 512 está fija en la base (`vector(512)`) y en el worker.

---

# Parte B. Subida fragmentada del ONNX (PC → servidor)

Reemplaza al `scp` + `subir-encoder.sh` de una sola pieza. El objetivo es que el ONNX (> 100 MB) pase por Cloudflare en trozos, se pueda **reanudar** si se corta y el servidor lo **reensamble y valide** solo.

## B.1 Principios

- El cliente corta el archivo en fragmentos de tamaño fijo, **8 MiB** por defecto. Eso queda muy por debajo del límite de 100 MB de Cloudflare.
- Cada fragmento lleva su propio sha256, y el archivo completo tiene un sha256 declarado de antemano.
- Los fragmentos son **idempotentes**: reenviar el fragmento N no daña nada.
- Nada queda activo ni visible hasta que el reensamblado verifica el sha256 del todo y el contrato ONNX.
- El servidor es la autoridad: el cliente no decide el orden ni el estado.

## B.2 API (requiere sesión admin; ruta bajo `/api/admin/encoder/subidas`)

### 1. Abrir la subida

`POST /api/admin/encoder/subidas`

```json
{
  "nombre": "bioclip_anura_v2",
  "archivo": "encoder_anura_v2_fp16.onnx",
  "bytes": 175123456,
  "sha256": "b3f1…64 hex",
  "tam_fragmento": 8388608
}
```

Respuesta:

```json
{
  "subida_id": "u_01J…",
  "tam_fragmento": 8388608,
  "total_fragmentos": 21,
  "expira": "2026-10-04T12:00:00Z"
}
```

- Si el `sha256` ya existe como encoder registrado, responde `409` con `{"existe": true}`. No hay nada que subir.
- Si ya hay una subida abierta con el mismo `sha256`, devuelve esa misma (así se reanuda desde otro terminal).
- El servidor puede ajustar `tam_fragmento` a la baja y lo informa.

### 2. Enviar un fragmento

`PUT /api/admin/encoder/subidas/{subida_id}/fragmentos/{n}`

- `n` va de `0` a `total_fragmentos - 1`.
- Cuerpo: bytes crudos (`application/octet-stream`).
- Encabezados: `Content-Length` y `X-Fragmento-Sha256: <sha del fragmento>`.

El servidor valida:

- que el tamaño sea el esperado (`tam_fragmento`, salvo el último);
- que el sha del cuerpo coincida con el encabezado.

Luego lo guarda en MinIO en `encoders/_subidas/{subida_id}/{n:05d}.parte`.

Respuestas:

- `201` si es nuevo.
- `200` si ya existía con el mismo sha (idempotente).
- `422` si el sha o el tamaño no coinciden. El cliente reintenta ese fragmento.

### 3. Consultar el avance (reanudar)

`GET /api/admin/encoder/subidas/{subida_id}`

```json
{
  "estado": "abierta",
  "recibidos": [0,1,2,3,5],
  "faltan": [4,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
}
```

Si el proceso se corta, el cliente pide esto y sube solo lo que falta.

### 4. Completar

`POST /api/admin/encoder/subidas/{subida_id}/completar`

Funciona solo si no falta ningún fragmento (`409` con la lista de faltantes si falta alguno). El servidor, en este orden:

1. **Ensambla** los fragmentos en orden, con una operación de composición de MinIO o una lectura en streaming. No carga el archivo en memoria.
2. Calcula el **sha256 del archivo completo** y lo compara con el declarado. Si no coincide: estado `corrupta`, no registra nada, conserva los fragmentos 1 hora para diagnóstico.
3. Valida el **contrato ONNX** (A.4) con `onnxruntime`:
   - entrada `imagen` `[1,3,224,224]` float32;
   - salida `embedding` `[1,512]` float32;
   - una pasada de prueba con una imagen sintética que debe devolver 512 valores finitos.
4. Mueve el archivo a `encoders/<sha256>/encoder.onnx` y lo registra como **inactivo**.
5. Borra los fragmentos y marca la subida como `completada`.

Respuesta: `{"sha256": "…", "nombre": "…", "estado": "inactivo"}`.

### 5. Cancelar

`DELETE /api/admin/encoder/subidas/{subida_id}` borra los fragmentos y cierra la subida.

### Limpieza automática

Una tarea periódica borra las subidas `abiertas` sin actividad en 24 horas.

## B.3 Estados de una subida

```
abierta ──(todos los fragmentos)──► completando ──► completada
   │                                     │
   ├─(24 h sin actividad)──► expirada    └─(sha o ONNX inválido)──► corrupta
   └─(DELETE)──► cancelada
```

## B.4 Cliente en el PC (comportamiento esperado)

```bash
subir-encoder-fragmentado encoder_nuevo_fp16.onnx --nombre bioclip_anura_v2
```

Hace, en orden:

1. Calcula el sha256 total (lectura en streaming).
2. Abre la subida (B.2.1). Si el servidor devuelve una existente, pregunta el avance (B.2.3).
3. Sube los fragmentos que faltan, con 3 en paralelo y hasta 5 reintentos con espera exponencial por fragmento.
4. Muestra una barra de progreso y llama a `completar`.
5. Imprime el sha256 final y el estado del ONNX.

**Plan B sin script** (si no hay Python): cortar y subir a mano.

```bash
split -b 8M -d -a 5 encoder_nuevo_fp16.onnx parte_
sha256sum encoder_nuevo_fp16.onnx   # guardar este valor
# subir cada parte_NNNNN con curl -T al endpoint PUT del fragmento (cada parte con su X-Fragmento-Sha256)
```

El reensamblado siempre lo hace el servidor (B.2.4). Nunca se reconstruye a mano en producción.

## B.5 Seguridad

- Todos los endpoints exigen rol admin.
- El sha256 total declarado es inmutable una vez abierta la subida.
- Límites: máximo 2 GB por subida y 2 subidas abiertas a la vez.
- Se registra en auditoría quién subió qué sha y cuándo.

---

# Parte C. Observaciones públicas y privadas

## C.1 Regla

| | Pública | Privada |
|---|---|---|
| Dónde vive | Solo en el servidor | Servidor **y** celular |
| En el celular | Se borra tras confirmar la subida | Se conserva (o se descarga si falta) |
| Quién la ve | Los usuarios, según las reglas de la web (comentar y refutar sí; invitado solo lee) | Solo su dueño, desde su perfil |

La app solo conserva en local lo privado. Todo lo público se consulta en el servidor.

## C.2 Modelo de datos en el servidor

Tabla `observaciones` (campos relevantes):

| Campo | Tipo | Nota |
|---|---|---|
| `id` | uuid | Lo genera la app al crear la observación; sirve de clave de idempotencia |
| `propietario_id` | fk usuarios | |
| `visibilidad` | enum `publica` \| `privada` | Por defecto `privada` |
| `visibilidad_cambiada_en` | timestamptz | |
| `estado` | enum `recibida` \| `procesada` | Por ejemplo, vectorizada por BioCLIP (C3) |
| `fotos` | relación `observacion_fotos` | Cada foto con `sha256`, `bytes`, `clave_minio` |
| `creada_en`, `actualizada_en` | timestamptz | |

**Garantías en el servidor**, aplicadas siempre en la capa de datos y no solo en la interfaz:

- Cualquier consulta de otros usuarios filtra por `visibilidad = 'publica'`.
- Una observación privada solo se devuelve si `propietario_id = usuario de la sesión`.
- Las fotos privadas solo se sirven con URL firmada de **vida corta (60 s)** emitida a su dueño, con `Cache-Control: private, no-store`.
- Comentarios y refutaciones solo existen sobre observaciones públicas. Si una pública pasa a privada, sus hilos se ocultan; no se borran, por si vuelve a ser pública.
- Excepción abierta: la sincronización C3 (BioCLIP) procesa fotos en el servidor y las revisa el personal autorizado. Hay que decidir si una privada entra o no al pipeline de entrenamiento. **Propuesta:** las privadas no entran a entrenamiento ni a estadísticas públicas.

## C.3 Modelo de datos en la app (Room)

Tabla local `observacion_local`:

| Campo | Valores |
|---|---|
| `id` | el mismo uuid del servidor |
| `visibilidad` | `publica` \| `privada` |
| `sync` | `solo_local` \| `pendiente_subida` \| `subiendo` \| `sincronizada` \| `pendiente_descarga` |
| `fotos` | rutas locales y `sha256` por foto |

Estados útiles:

- `pendiente_subida`: la foto está en el celular y aún no está confirmada en el servidor. **Nunca se borra en este estado.**
- `sincronizada`: el servidor confirmó los bytes (mismo `sha256`). Solo desde aquí se puede borrar la copia local si es pública.
- `pendiente_descarga`: es privada, el servidor la tiene y el celular aún no.

## C.4 Flujos

### Crear una observación
1. Se guarda en local como `solo_local` con visibilidad elegida (por defecto `privada`) y pasa a `pendiente_subida`.
2. Sube las fotos y los datos al servidor (idempotente por `id`).
3. El servidor responde con el sha256 recibido de cada foto.

### Pública
1. El servidor confirma que los sha256 coinciden con los locales.
2. La app marca `sincronizada` y **borra las fotos locales y la fila**.
3. A partir de ahí la observación se ve desde el servidor (listas, mapa, perfil).
4. Si no hay red, se queda `pendiente_subida` y se reintenta con WorkManager. No se pierde nada.

### Privada
1. Se queda guardada en el servidor con `visibilidad = 'privada'`. Los usuarios comunes dejan de verla. Solo su dueño la ve en su perfil.
2. Si no está en el celular (otro dispositivo o instalación nueva), pasa a `pendiente_descarga`. La app la baja con URL firmada, verifica el sha256 y la guarda como `sincronizada`.
3. Lo único que el celular guarda de forma permanente es lo privado.

### Cambios de visibilidad
- **Privada → pública:** `PUT /api/observaciones/{id}/visibilidad` con `{"visibilidad":"publica"}`. Con la confirmación del servidor, la app borra su copia local, como en el flujo de pública.
- **Pública → privada:** la app envía `{"visibilidad":"privada"}`. El servidor deja de mostrarla al resto y la app la baja y la guarda (`pendiente_descarga` → `sincronizada`).
- Si hay conflicto, **gana el servidor**. La app siempre reconcilia por `visibilidad_cambiada_en`.

### Borrado local seguro
Solo se borra una copia local cuando se cumplen las dos condiciones:
1. `visibilidad = publica`.
2. El servidor confirmó el sha256 de cada foto.

Hacer esto en una transacción: primero se marca `sincronizada` en la base, después se borran los archivos. Si la app muere entre los dos pasos, al abrir se completa la limpieza.

## C.5 API

| Método | Ruta | Para qué |
|---|---|---|
| `POST` | `/api/observaciones` | Crear (idempotente por `id`) |
| `PUT` | `/api/observaciones/{id}/fotos/{n}` | Subir foto (puede usar el esquema fragmentado de B.2 si pesa mucho) |
| `PUT` | `/api/observaciones/{id}/visibilidad` | Cambiar `visibilidad` (PUT y no PATCH: `HttpURLConnection` de Android no soporta PATCH) |
| `GET` | `/api/observaciones/{id}` | Estado en el servidor: `visibilidad`, `visibilidad_cambiada_en` (epoch ms) y fotos con `n`, `sha256`, `bytes` |
| `GET` | `/api/observaciones/mias?visibilidad=privada&desde=<ts>` | Mis privadas, para sincronizar al celular |
| `GET` | `/api/observaciones/publicas` | Listado público |
| `GET` | `/api/observaciones/{id}/fotos/{n}` | `302` a URL firmada; 404 si es privada y no eres el dueño |

Para la sincronización de privadas, la app pide `mias?visibilidad=privada&desde=<último ts>` y baja las que le falten.

## C.6 Pendientes

Servidor (a implementar aparte):

- [ ] Migración: columna `visibilidad` (por defecto `privada`) y revisión de los filtros de todas las consultas existentes.
- [ ] Endpoints de C.5 y URLs firmadas de vida corta para privadas.
- [ ] Decidir si el personal admin puede ver privadas (propuesta: no, salvo moderación explícita y auditada).
- [ ] Decidir si las privadas entran al pipeline de entrenamiento (propuesta: no).

App Android (en código): `ObservationVisibility.kt`, `ObservationVisibilityRemote.kt`, tabla `observacion_local` con migración 1→2. Falta cablear el worker de sincronización a la pantalla de captura y al perfil.
