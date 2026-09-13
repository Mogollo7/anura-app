---
title: "Arquitectura de la AplicaciÃ³n"
proyecto: Anura
tipo: proceso-desarrollo
estado: propuesta
tags: [anura, proceso, arquitectura, android, diseÃ±o]
---

# Arquitectura de la AplicaciÃ³n

[[Anura â€” Ãndice General]] Â· [[Proceso de Desarrollo â€” Ãndice]] Â· [[App MÃ³vil]] Â· [[Flujo de Datos y SincronizaciÃ³n]] Â· [[Pipeline del Sistema]]

## 1. Vista general del sistema

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”         â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚   APP ANDROID        â”‚         â”‚        SERVIDOR              â”‚
â”‚                      â”‚         â”‚                              â”‚
â”‚  UI (Compose)        â”‚         â”‚  API FastAPI                 â”‚
â”‚  ViewModels          â”‚  HTTPS  â”‚   â”œâ”€â”€ /identify              â”‚
â”‚  Casos de uso        â”‚â—€â”€â”€â”€â”€â”€â”€â”€â–¶â”‚   â”œâ”€â”€ /observaciones         â”‚
â”‚  â”œâ”€â”€ ML local        â”‚  sync   â”‚   â”œâ”€â”€ /sync                  â”‚
â”‚  â”œâ”€â”€ Room (SQLite)   â”‚diferida â”‚   â””â”€â”€ /export/dwc            â”‚
â”‚  â””â”€â”€ Vectores local  â”‚         â”‚                              â”‚
â”‚                      â”‚         â”‚  PostgreSQL (Supabase)       â”‚
â”‚  100 % funcional     â”‚         â”‚  Vectores (Qdrant/pgvector)  â”‚
â”‚  sin conexiÃ³n        â”‚         â”‚  Storage                     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
         â–²                                      â–²
         â”‚                                      â”‚
    trabajo de campo                      web comunitaria
```

Regla que define la arquitectura entera: **el servidor es opcional para identificar, obligatorio para compartir.** Todo lo que sea "identificar y guardar" ocurre en el dispositivo; todo lo que sea "publicar, validar, exportar" ocurre en el servidor.

## 2. Capas de la app

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ PRESENTACIÃ“N         Compose Â· ViewModels Â· StateFlowâ”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ DOMINIO              Casos de uso Â· Modelos Â· Reglas â”‚   â† sin dependencias
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ DATOS                Repositorios (interfaces)       â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ INFRAESTRUCTURA      Room Â· LiteRT Â· Vectores Â· API  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

La capa de dominio no importa nada de Android, ni de LiteRT, ni de Retrofit. Suena a purismo, pero tiene dos consecuencias muy prÃ¡cticas en este proyecto:

1. La lÃ³gica de identificaciÃ³n (fusiÃ³n, umbrales open-set, evidencia por caracteres) es **testeable sin dispositivo ni modelo**, con JUnit puro y datos sintÃ©ticos. Sin eso, probar la regla de "no observable â‰  ausente" exige un telÃ©fono y una rana.
2. El motor de inferencia se puede cambiar (LiteRT â†’ ONNX) sin tocar pantallas. Va a pasar.

## 3. MÃ³dulos

```
:app                 navegaciÃ³n, DI, tema
:feature:captura     cÃ¡mara, grabaciÃ³n de audio
:feature:resultado   Top-3, evidencia anatÃ³mica, ficha
:feature:campo       salidas, transectos, metadatos (HU-04)
:feature:historial   observaciones locales, estado de sync
:core:ml             LiteRT, pre/postproceso, fusiÃ³n, open-set
:core:datos          Room, vectores, repositorios
:core:sync           WorkManager, cliente API
:core:ui             componentes, tema oscuro/campo
:core:modelo         entidades de dominio
```

## 4. Modelo de dominio: los tipos que importan

Dos decisiones de tipado que evitan errores conceptuales del proyecto entero:

```kotlin
// "no observable" NO es lo mismo que "ausente"
enum class EstadoCaracter { PRESENTE, AUSENTE, NO_OBSERVABLE, VARIABLE }

// Un resultado puede ser legÃ­timamente "no lo sÃ©"
sealed interface ResultadoIdentificacion {
    data class Identificada(
        val candidatos: List<Candidato>,      // Top-3
        val evidencia: List<EvidenciaRegion>,
        val vecinos: List<ObservacionSimilar>,
        val confianza: NivelConfianza
    ) : ResultadoIdentificacion

    data class NoRegistrada(                   // open-set
        val nivelAlcanzado: RangoTaxonomico,   // familia / gÃ©nero
        val referencias: List<Candidato>
    ) : ResultadoIdentificacion

    data class SinAnuroDetectado(val motivo: String) : ResultadoIdentificacion
    data class CalidadInsuficiente(val sugerencia: String) : ResultadoIdentificacion
}
```

Modelar `NoRegistrada` como un resultado de primera clase â€” y no como un error o un 
ull` â€” obliga a que la interfaz lo trate con dignidad. Es la diferencia entre una app que dice "no se pudo identificar" y una que dice "es un Hylidae, probablemente Boana, pero ninguna especie de mi catÃ¡logo encaja".

## 5. Estados de una observaciÃ³n

```
   BORRADOR â”€â”€â–¶ LOCAL â”€â”€â–¶ EN_COLA â”€â”€â–¶ SINCRONIZADA â”€â”€â–¶ EN_REVISION â”€â”€â–¶ VALIDADA
                  â”‚           â”‚                                          â”‚
                  â”‚           â””â”€â”€â–¶ ERROR_SYNC â”€â”€(reintento)â”€â”€â”˜           â”‚
                  â”‚                                                       â–¼
                  â””â”€â”€â–¶ (siempre recuperable)                          RECHAZADA
```

`LOCAL` se alcanza **antes** de la inferencia: la foto y sus metadatos se persisten primero. Si la app muere durante el procesamiento, el dato de campo sobrevive.

## 6. Pantallas principales

| Pantalla | Contenido | Requisitos |
| --- | --- | --- |
| **Captura** | Visor, disparo, grabaciÃ³n, indicador GPS/offline | RF-01, RNF-07/08 |
| **Procesando** | Progreso por etapas (segmentando â†’ identificandoâ€¦) | Evita percepciÃ³n de bloqueo |
| **Resultado** | Top-3, evidencia por regiÃ³n, vecinos similares, acciones | RF-05, RF-06 |
| **Ficha de especie** | TaxonomÃ­a, morfologÃ­a, bioacÃºstica, distribuciÃ³n, UICN | RF-10 |
| **RefutaciÃ³n** | SelecciÃ³n de regiÃ³n, correcciÃ³n, envÃ­o | HU-03 |
| **Salida de campo** | SesiÃ³n, transecto, variables ambientales | HU-04 |
| **Historial** | Observaciones locales y estado de sincronizaciÃ³n | RF-13 |
| **Ajustes** | Paquetes regionales, sincronizaciÃ³n, tema, almacenamiento | |

La pantalla de **resultado** es donde se juega el valor del proyecto: debe mostrar la evidencia contradictoria y lo no observable con el mismo peso visual que lo compatible. Ocultar la duda convertirÃ­a a Anura en el orÃ¡culo que el [[Referente TeÃ³rico]] dice explÃ­citamente que no debe ser.

## 7. Pruebas

| Nivel | QuÃ© se prueba | Herramienta |
| --- | --- | --- |
| Unitarias | FusiÃ³n, umbrales, coherencia taxonÃ³mica, estados de carÃ¡cter | JUnit |
| IntegraciÃ³n | Room, cola de sincronizaciÃ³n, idempotencia | Robolectric |
| Instrumentadas | Inferencia real, latencia, memoria | Dispositivo fÃ­sico |
| UI | Flujos completos | Compose UI Test |
| Campo | El sistema con personas reales | [[EvaluaciÃ³n en Campo Real]] |

Casos que hay que probar y que se olvidan sistemÃ¡ticamente: sin permisos, sin GPS, sin red durante dÃ­as, baterÃ­a crÃ­tica a mitad de inferencia, almacenamiento lleno, y **cambio de versiÃ³n de modelo con observaciones pendientes de sincronizar**.



