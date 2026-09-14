---
title: "Flujo de Datos y Sincronización"
proyecto: Anura
tipo: proceso-desarrollo
estado: propuesta
tags: [anura, proceso, sincronización, offline-first, datos]
---

# Flujo de Datos y Sincronización

[[Anura â€” àndice General]] · [[Proceso de Desarrollo â€” àndice]] · [[App Móvil]] · [[API Backend]] · [[Base Vectorial (SQLite-vec)]]

> [!abstract] El requisito que manda
> RNF-10 exige que el **100 %** de la captura, el procesamiento y la consulta funcionen sin ninguna conectividad. Eso convierte a Anura en un sistema *offline-first*: la red es una optimización ocasional, no un supuesto. Todo el diseño de datos se deriva de ahí.

## 1. Offline-first en la práctica

La diferencia con una app "con modo offline" es de dirección:

| | App con modo offline | **Offline-first (Anura)** |
| --- | --- | --- |
| Fuente de verdad para el usuario | El servidor | **La base local** |
| Sin red | Funcionalidad degradada | Funcionalidad completa |
| La red sirve para | Todo | Compartir y actualizar |
| Escritura | Va al servidor | Va a local; se propaga después |

En campo, una salida nocturna de cuatro horas sin señal es lo normal. Si el usuario percibe la app como "está fallando" cuando no hay red, el proyecto fracasa en su caso de uso principal.

## 2. Almacenamiento local

```
SQLite / Room
â”œâ”€â”€ observaciones          (uuid, estado, taxonomía, timestamps)
â”œâ”€â”€ medios                 (rutas locales a imagen/audio, hash)
â”œâ”€â”€ predicciones           (top3, evidencia, versión de modelo)
â”œâ”€â”€ metadatos_ambientales  (GPS, altitud, clima, microhábitat)
â”œâ”€â”€ salidas_campo          (sesiones/transectos, HU-04)
â”œâ”€â”€ cola_sync              (pendientes, reintentos, àºltimo error)
â””â”€â”€ vectores               (embeddings locales + paquete regional)

Almacenamiento de archivos
â”œâ”€â”€ originales/            (WebP 1024à—768 ~80 KB)
â”œâ”€â”€ audio/                 (WAV o FLAC)
â””â”€â”€ paquetes/              (región descargada: vectores + fichas)
```

Dos reglas concretas:

- **La imagen se comprime a WebP 80 % antes de guardarla**, no después. Ver especificación en [[Estrategia de Construcción del Dataset]]: ~300 KB â†’ ~70â€“100 KB. Con decenas de registros por noche, la diferencia decide si el teléfono se llena.
- **El audio no se comprime con pérdida.** WAV o FLAC. MP3/AAC destruyen armónicos que la rama acàºstica necesita.

## 3. El ciclo de una observación

```
1. CAPTURA          foto + audio + GPS
      â†“
2. PERSISTIR        estado = LOCAL          â† antes de inferir
      â†“
3. INFERIR          modelos locales
      â†“
4. GUARDAR RESULTADO  predicción + versión de modelo
      â†“
5. ENCOLAR          estado = EN_COLA
      â†“
   ... el usuario sigue trabajando, sin red, durante horas o días ...
      â†“
6. WorkManager detecta conectividad
      â†“
7. PUSH             envío por lotes, idempotente
      â†“
8. ACK              estado = SINCRONIZADA
      â†“
9. (servidor) validación experta â†’ VALIDADA â†’ entra al índice global
```

El paso 2 antes del 3 es deliberado y es la decisión más importante de todo este flujo.

## 4. Reglas de sincronización

### Idempotencia

Cada observación lleva un **UUID generado en el dispositivo**. El servidor usa ese UUID como clave: reenviar la misma observación no crea duplicados. En campo, con red intermitente, los reintentos parciales son la norma â€” sin idempotencia, la base se llena de duplicados en la primera salida real.

### Resolución de conflictos

| Campo | Gana | Motivo |
| --- | --- | --- |
| Datos de campo (foto, GPS, hora, microhábitat) | **Dispositivo** | Solo el dispositivo estuvo allí |
| Identificación validada por experto | **Servidor** | La validación es posterior y más autorizada |
| Ficha técnica de especie | **Servidor** | Contenido curado centralmente |
| Notas del usuario | **àšltima escritura**, conservando ambas versiones | Evita pérdida silenciosa |

### Lotes y reintentos

- Enviar por lotes (10â€“20 observaciones), no de una en una.
- Reintento con retroceso exponencial, gestionado por WorkManager.
- Restricciones: preferir Wi-Fi para paquetes grandes; permitir datos móviles para observaciones pequeñas.
- **Nada se borra del dispositivo hasta recibir confirmación** del servidor.

### Versiones

Cada push incluye la versión de modelo y de paquete regional. Si el servidor detecta una versión antigua, **recalcula el embedding** en vez de rechazar el dato (ver [[Escalabilidad]] §2). Rechazar significaría perder trabajo de campo irrepetible por un motivo puramente técnico.

## 5. Bajada: paquetes regionales

```
App consulta:  GET /v1/sync/paquetes?region=antioquia&version_actual=4
Servidor:      { version: 5, url, hash, tamano, version_modelo, dimension }
App:           descarga (solo Wi-Fi) â†’ verifica hash â†’ instala â†’ activa
```

- **Descarga atómica**: el paquete nuevo no reemplaza al anterior hasta estar íntegro y verificado. Un paquete a medias durante una salida de campo dejaría la app sin catálogo.
- **Un paquete por región**, para no obligar a descargar el país entero.
- **Verificación de compatibilidad**: si el paquete se generó con un modelo distinto al embarcado, no se activa y se avisa de que hay que actualizar la app.

## 6. Presupuesto de almacenamiento

| Elemento | Tamaño |
| --- | --- |
| Modelos | 100â€“125 MB |
| Paquete regional (10 k vectores + fichas) | 25â€“55 MB |
| Observación (imagen + audio + metadatos) | ~90â€“350 KB |
| 100 observaciones acumuladas | ~10â€“35 MB |

Gestión sensata: avisar al 80 % del espacio asignado, ofrecer liberar observaciones ya sincronizadas y validadas (los originales están a salvo en el servidor), y **no borrar nunca automáticamente** nada que no esté confirmado.

## 7. Fallos previsibles y respuesta

| Fallo | Respuesta |
| --- | --- |
| Sin red durante días | Normal. La cola crece; no molestar al usuario con avisos |
| Sync interrumpida a mitad | Reintento; los ya confirmados no se reenvían |
| Servidor caído | Retroceso exponencial; no perder la cola |
| Almacenamiento lleno | Avisar y ofrecer liberar; nunca bloquear la captura |
| App cerrada durante inferencia | La observación está en `LOCAL`; se reprocesa al abrir |
| Cambio de dispositivo | Exportación/importación de la base local (deseable, no crítico) |
| Conflicto de versión | Recálculo en servidor, no rechazo |

## 8. Qué falta por decidir o medir

- [ ] Formato exacto del paquete regional y su versionado.
- [ ] Tamaño de lote óptimo para push.
- [ ] Política de retención local tras sincronización.
- [ ] Probar el flujo completo con â‰¥ 8 h sin red y decenas de registros acumulados.



