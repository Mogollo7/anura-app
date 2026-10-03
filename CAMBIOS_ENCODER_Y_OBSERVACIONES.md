# Registro de cambios: encoder por sha y visibilidad de observaciones

Commit en la rama `claude/eager-dijkstra-7hdqnx`. Nada de esto se compiló ni se probó: no había `kotlinc` ni SDK de Android en el entorno. Compila y corre las pruebas tú.

## 1. Archivos nuevos

### Documento
| Archivo | Qué es |
|---|---|
| `PROTOCOLO_ENCODER_Y_OBSERVACIONES.md` | Protocolo del **servidor**: cambio de encoder (A), subida fragmentada del ONNX (B), observaciones públicas/privadas (C). El servidor lo implementas tú aparte. |
| `CAMBIOS_ENCODER_Y_OBSERVACIONES.md` | Este registro. |

### Código Android: `core/encoder/`
| Archivo | Qué hace |
|---|---|
| `EncoderManifest.kt` | Modelos del manifiesto `GET /api/dataset/publico/encoder`; ignora esquema ≠ 1 o dimensión ≠ 512; constante `ShaEmpaquetado` (`219e860e…`). |
| `EncoderStore.kt` | Guarda cada modelo en `<raíz>/<sha256>/encoder.onnx`; calcula sha256; limpia los modelos que ningún paquete usa. |
| `EncoderTransport.kt` | Capa HTTP (con `Range`) separada para poder probar sin servidor. |
| `EncoderDownloader.kt` | Descarga a `.part`, reanuda con `Range`, exige espacio ≥ 2×, verifica sha256 completo y mueve con renombrado atómico. |
| `EncoderSync.kt` | `sincronizar()` (baja el activo y limpia), `asegurarModelo(sha)` (antes de instalar un paquete) y `EncoderResolver` (modelo por paquete). |

### Código Android: `core/observations/`
| Archivo | Qué hace |
|---|---|
| `ObservationVisibility.kt` | Estados y política: pública confirmada → borrar copia local; privada que falta → descargar; el servidor manda salvo cambio local más reciente. |
| `ObservationLocalStore.kt` | Tabla Room `observacion_local`, su DAO y un almacén abstracto para pruebas. |
| `ObservationVisibilityRemote.kt` | Llamadas al servidor: cambiar visibilidad (`PUT …/visibilidad`), consultar una observación, listar mis privadas, bajar foto. |
| `ObservationSync.kt` | Reconcilia teléfono y servidor aplicando la política; no borra nada sin confirmación del servidor. |

### Pruebas unitarias (`src/test/…/core/`)
- `encoder/EncoderDownloaderTest.kt`
- `encoder/EncoderManifestAndStoreTest.kt`
- `observations/ObservationVisibilityPolicyTest.kt`

## 2. Archivos existentes que modifiqué

| Archivo | Cambio |
|---|---|
| `core/inference/AnuraIdentifier.kt` | Lee el sha del encoder del paquete y carga ese modelo (recarga si cambia de paquete). Si no está disponible, devuelve el fallo nuevo `EncoderUnavailable`. |
| `core/inference/ImageEncoder.kt` | Nuevo `loadFile(archivo)` para cargar un modelo descargado. `load()` usa lo mismo internamente; su comportamiento no cambia. |
| `core/inference/PackageVectorIndex.kt` | Nuevo `encoderSha256()`: lee `package_info.encoder_onnx_sha256`. Devuelve `null` si no existe (se asume el modelo empaquetado). |
| `core/data/AnuraDatabase.kt` | Versión 1 → 2: entidad `ObservacionLocalEntity`, `observacionLocalDao()` y `Migration1To2`. |
| `core/data/AnuraRepository.kt` | El builder de Room añade `addMigrations(Migration1To2)`. Sin esto, la migración destructiva existente habría borrado el snapshot. |
| `navigation/AnuraNavHost.kt` | Rama nueva para `EncoderUnavailable` en el `when` de errores de identificación. |
| `res/values/strings.xml` | Texto nuevo: «Este paquete necesita un modelo más nuevo. Actualiza la app y vuelve a intentar.» |

## 3. Decisiones que tomé y debes confirmar

1. **`PUT` en vez de `PATCH`** para cambiar la visibilidad (`PUT /api/observaciones/{id}/visibilidad`): el `HttpURLConnection` de Android no soporta PATCH. El servidor debe exponer esa ruta.
2. **`package_info` como clave-valor** (`key`, `value`): lo supuse porque no vi el esquema del paquete en este repo. Si es otro, ajusta `PackageVectorIndex.encoderSha256()`.
3. **Privadas fuera del entrenamiento y fuera de la vista del admin** (salvo moderación auditada): es solo una propuesta en el protocolo.
4. **Carpeta de modelos descargados:** `files/models/by-sha/`.

## 4. Falta por cablear

- Llamar a `EncoderSync.sincronizar()` al abrir la app y antes de instalar un paquete (con Wi‑Fi).
- Lanzar `ObservationSync.reconciliar()` desde un worker o desde las pantallas de captura y perfil.
- La subida de las fotos pendientes sigue usando tu `ObservationsRemote.upload`.
- Todo el lado servidor (migración de `visibilidad`, endpoints, URLs firmadas, subida fragmentada).

## 5. Qué NO toqué

- El contrato del ONNX, la dimensión 512 y el preprocesado.
- Los paquetes, el catálogo y la verificación Ed25519.
- No hay código de servidor en este repo.
