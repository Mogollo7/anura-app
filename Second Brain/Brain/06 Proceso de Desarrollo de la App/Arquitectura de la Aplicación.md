---
title: "Arquitectura de la Aplicación"
proyecto: Anura
tipo: proceso-desarrollo
estado: propuesta
tags: [anura, proceso, arquitectura, android, diseño]
---

# Arquitectura de la Aplicación

[[Anura â€” àndice General]] · [[Proceso de Desarrollo â€” àndice]] · [[App Móvil]] · [[Flujo de Datos y Sincronización]] · [[Pipeline del Sistema]]

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
â”‚  sin conexión        â”‚         â”‚  Storage                     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
         â–²                                      â–²
         â”‚                                      â”‚
    trabajo de campo                      web comunitaria
```

Regla que define la arquitectura entera: **el servidor es opcional para identificar, obligatorio para compartir.** Todo lo que sea "identificar y guardar" ocurre en el dispositivo; todo lo que sea "publicar, validar, exportar" ocurre en el servidor.

## 2. Capas de la app

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ PRESENTACIà“N         Compose · ViewModels · StateFlowâ”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ DOMINIO              Casos de uso · Modelos · Reglas â”‚   â† sin dependencias
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ DATOS                Repositorios (interfaces)       â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ INFRAESTRUCTURA      Room · LiteRT · Vectores · API  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

La capa de dominio no importa nada de Android, ni de LiteRT, ni de Retrofit. Suena a purismo, pero tiene dos consecuencias muy prácticas en este proyecto:

1. La lógica de identificación (fusión, umbrales open-set, evidencia por caracteres) es **testeable sin dispositivo ni modelo**, con JUnit puro y datos sintéticos. Sin eso, probar la regla de "no observable â‰  ausente" exige un teléfono y una rana.
2. El motor de inferencia se puede cambiar (LiteRT â†’ ONNX) sin tocar pantallas. Va a pasar.

## 3. Módulos

```
:app                 navegación, DI, tema
:feature:captura     cámara, grabación de audio
:feature:resultado   Top-3, evidencia anatómica, ficha
:feature:campo       salidas, transectos, metadatos (HU-04)
:feature:historial   observaciones locales, estado de sync
:core:ml             LiteRT, pre/postproceso, fusión, open-set
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

// Un resultado puede ser legítimamente "no lo sé"
sealed interface ResultadoIdentificacion {
    data class Identificada(
        val candidatos: List<Candidato>,      // Top-3
        val evidencia: List<EvidenciaRegion>,
        val vecinos: List<ObservacionSimilar>,
        val confianza: NivelConfianza
    ) : ResultadoIdentificacion

    data class NoRegistrada(                   // open-set
        val nivelAlcanzado: RangoTaxonomico,   // familia / género
        val referencias: List<Candidato>
    ) : ResultadoIdentificacion

    data class SinAnuroDetectado(val motivo: String) : ResultadoIdentificacion
    data class CalidadInsuficiente(val sugerencia: String) : ResultadoIdentificacion
}
```

Modelar `NoRegistrada` como un resultado de primera clase â€” y no como un error o un 
ull` â€” obliga a que la interfaz lo trate con dignidad. Es la diferencia entre una app que dice "no se pudo identificar" y una que dice "es un Hylidae, probablemente Boana, pero ninguna especie de mi catálogo encaja".

## 5. Estados de una observación

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
| **Captura** | Visor, disparo, grabación, indicador GPS/offline | RF-01, RNF-07/08 |
| **Procesando** | Progreso por etapas (segmentando â†’ identificandoâ€¦) | Evita percepción de bloqueo |
| **Resultado** | Top-3, evidencia por región, vecinos similares, acciones | RF-05, RF-06 |
| **Ficha de especie** | Taxonomía, morfología, bioacàºstica, distribución, UICN | RF-10 |
| **Refutación** | Selección de región, corrección, envío | HU-03 |
| **Salida de campo** | Sesión, transecto, variables ambientales | HU-04 |
| **Historial** | Observaciones locales y estado de sincronización | RF-13 |
| **Ajustes** | Paquetes regionales, sincronización, tema, almacenamiento | |

La pantalla de **resultado** es donde se juega el valor del proyecto: debe mostrar la evidencia contradictoria y lo no observable con el mismo peso visual que lo compatible. Ocultar la duda convertiría a Anura en el oráculo que el [[Referente Teórico]] dice explícitamente que no debe ser.

## 7. Pruebas

| Nivel | Qué se prueba | Herramienta |
| --- | --- | --- |
| Unitarias | Fusión, umbrales, coherencia taxonómica, estados de carácter | JUnit |
| Integración | Room, cola de sincronización, idempotencia | Robolectric |
| Instrumentadas | Inferencia real, latencia, memoria | Dispositivo físico |
| UI | Flujos completos | Compose UI Test |
| Campo | El sistema con personas reales | [[Evaluación en Campo Real]] |

Casos que hay que probar y que se olvidan sistemáticamente: sin permisos, sin GPS, sin red durante días, batería crítica a mitad de inferencia, almacenamiento lleno, y **cambio de versión de modelo con observaciones pendientes de sincronizar**.



