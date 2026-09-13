---
title: "Flujo de Datos y SincronizaciÃ³n"
proyecto: Anura
tipo: proceso-desarrollo
estado: propuesta
tags: [anura, proceso, sincronizaciÃ³n, offline-first, datos]
---

# Flujo de Datos y SincronizaciÃ³n

[[Anura â€” Ãndice General]] Â· [[Proceso de Desarrollo â€” Ãndice]] Â· [[App MÃ³vil]] Â· [[API Backend]] Â· [[Base Vectorial (SQLite-vec)]]

> [!abstract] El requisito que manda
> RNF-10 exige que el **100 %** de la captura, el procesamiento y la consulta funcionen sin ninguna conectividad. Eso convierte a Anura en un sistema *offline-first*: la red es una optimizaciÃ³n ocasional, no un supuesto. Todo el diseÃ±o de datos se deriva de ahÃ­.

## 1. Offline-first en la prÃ¡ctica

La diferencia con una app "con modo offline" es de direcciÃ³n:

| | App con modo offline | **Offline-first (Anura)** |
| --- | --- | --- |
| Fuente de verdad para el usuario | El servidor | **La base local** |
| Sin red | Funcionalidad degradada | Funcionalidad completa |
| La red sirve para | Todo | Compartir y actualizar |
| Escritura | Va al servidor | Va a local; se propaga despuÃ©s |

En campo, una salida nocturna de cuatro horas sin seÃ±al es lo normal. Si el usuario percibe la app como "estÃ¡ fallando" cuando no hay red, el proyecto fracasa en su caso de uso principal.

## 2. Almacenamiento local

```
SQLite / Room
â”œâ”€â”€ observaciones          (uuid, estado, taxonomÃ­a, timestamps)
â”œâ”€â”€ medios                 (rutas locales a imagen/audio, hash)
â”œâ”€â”€ predicciones           (top3, evidencia, versiÃ³n de modelo)
â”œâ”€â”€ metadatos_ambientales  (GPS, altitud, clima, microhÃ¡bitat)
â”œâ”€â”€ salidas_campo          (sesiones/transectos, HU-04)
â”œâ”€â”€ cola_sync              (pendientes, reintentos, Ãºltimo error)
â””â”€â”€ vectores               (embeddings locales + paquete regional)

Almacenamiento de archivos
â”œâ”€â”€ originales/            (WebP 1024Ã—768 ~80 KB)
â”œâ”€â”€ audio/                 (WAV o FLAC)
â””â”€â”€ paquetes/              (regiÃ³n descargada: vectores + fichas)
```

Dos reglas concretas:

- **La imagen se comprime a WebP 80 % antes de guardarla**, no despuÃ©s. Ver especificaciÃ³n en [[Estrategia de ConstrucciÃ³n del Dataset]]: ~300 KB â†’ ~70â€“100 KB. Con decenas de registros por noche, la diferencia decide si el telÃ©fono se llena.
- **El audio no se comprime con pÃ©rdida.** WAV o FLAC. MP3/AAC destruyen armÃ³nicos que la rama acÃºstica necesita.

## 3. El ciclo de una observaciÃ³n

```
1. CAPTURA          foto + audio + GPS
      â†“
2. PERSISTIR        estado = LOCAL          â† antes de inferir
      â†“
3. INFERIR          modelos locales
      â†“
4. GUARDAR RESULTADO  predicciÃ³n + versiÃ³n de modelo
      â†“
5. ENCOLAR          estado = EN_COLA
      â†“
   ... el usuario sigue trabajando, sin red, durante horas o dÃ­as ...
      â†“
6. WorkManager detecta conectividad
      â†“
7. PUSH             envÃ­o por lotes, idempotente
      â†“
8. ACK              estado = SINCRONIZADA
      â†“
9. (servidor) validaciÃ³n experta â†’ VALIDADA â†’ entra al Ã­ndice global
```

El paso 2 antes del 3 es deliberado y es la decisiÃ³n mÃ¡s importante de todo este flujo.

## 4. Reglas de sincronizaciÃ³n

### Idempotencia

Cada observaciÃ³n lleva un **UUID generado en el dispositivo**. El servidor usa ese UUID como clave: reenviar la misma observaciÃ³n no crea duplicados. En campo, con red intermitente, los reintentos parciales son la norma â€” sin idempotencia, la base se llena de duplicados en la primera salida real.

### ResoluciÃ³n de conflictos

| Campo | Gana | Motivo |
| --- | --- | --- |
| Datos de campo (foto, GPS, hora, microhÃ¡bitat) | **Dispositivo** | Solo el dispositivo estuvo allÃ­ |
| IdentificaciÃ³n validada por experto | **Servidor** | La validaciÃ³n es posterior y mÃ¡s autorizada |
| Ficha tÃ©cnica de especie | **Servidor** | Contenido curado centralmente |
| Notas del usuario | **Ãšltima escritura**, conservando ambas versiones | Evita pÃ©rdida silenciosa |

### Lotes y reintentos

- Enviar por lotes (10â€“20 observaciones), no de una en una.
- Reintento con retroceso exponencial, gestionado por WorkManager.
- Restricciones: preferir Wi-Fi para paquetes grandes; permitir datos mÃ³viles para observaciones pequeÃ±as.
- **Nada se borra del dispositivo hasta recibir confirmaciÃ³n** del servidor.

### Versiones

Cada push incluye la versiÃ³n de modelo y de paquete regional. Si el servidor detecta una versiÃ³n antigua, **recalcula el embedding** en vez de rechazar el dato (ver [[Escalabilidad]] Â§2). Rechazar significarÃ­a perder trabajo de campo irrepetible por un motivo puramente tÃ©cnico.

## 5. Bajada: paquetes regionales

```
App consulta:  GET /v1/sync/paquetes?region=antioquia&version_actual=4
Servidor:      { version: 5, url, hash, tamano, version_modelo, dimension }
App:           descarga (solo Wi-Fi) â†’ verifica hash â†’ instala â†’ activa
```

- **Descarga atÃ³mica**: el paquete nuevo no reemplaza al anterior hasta estar Ã­ntegro y verificado. Un paquete a medias durante una salida de campo dejarÃ­a la app sin catÃ¡logo.
- **Un paquete por regiÃ³n**, para no obligar a descargar el paÃ­s entero.
- **VerificaciÃ³n de compatibilidad**: si el paquete se generÃ³ con un modelo distinto al embarcado, no se activa y se avisa de que hay que actualizar la app.

## 6. Presupuesto de almacenamiento

| Elemento | TamaÃ±o |
| --- | --- |
| Modelos | 100â€“125 MB |
| Paquete regional (10 k vectores + fichas) | 25â€“55 MB |
| ObservaciÃ³n (imagen + audio + metadatos) | ~90â€“350 KB |
| 100 observaciones acumuladas | ~10â€“35 MB |

GestiÃ³n sensata: avisar al 80 % del espacio asignado, ofrecer liberar observaciones ya sincronizadas y validadas (los originales estÃ¡n a salvo en el servidor), y **no borrar nunca automÃ¡ticamente** nada que no estÃ© confirmado.

## 7. Fallos previsibles y respuesta

| Fallo | Respuesta |
| --- | --- |
| Sin red durante dÃ­as | Normal. La cola crece; no molestar al usuario con avisos |
| Sync interrumpida a mitad | Reintento; los ya confirmados no se reenvÃ­an |
| Servidor caÃ­do | Retroceso exponencial; no perder la cola |
| Almacenamiento lleno | Avisar y ofrecer liberar; nunca bloquear la captura |
| App cerrada durante inferencia | La observaciÃ³n estÃ¡ en `LOCAL`; se reprocesa al abrir |
| Cambio de dispositivo | ExportaciÃ³n/importaciÃ³n de la base local (deseable, no crÃ­tico) |
| Conflicto de versiÃ³n | RecÃ¡lculo en servidor, no rechazo |

## 8. QuÃ© falta por decidir o medir

- [ ] Formato exacto del paquete regional y su versionado.
- [ ] TamaÃ±o de lote Ã³ptimo para push.
- [ ] PolÃ­tica de retenciÃ³n local tras sincronizaciÃ³n.
- [ ] Probar el flujo completo con â‰¥ 8 h sin red y decenas de registros acumulados.



