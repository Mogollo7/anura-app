package me.juanlabs.anura.navigation

import kotlinx.serialization.Serializable

/**
 * Rutas type-safe de ANURA (§4, §4.1). Fuente única de verdad de la navegación:
 * ninguna ruta se referencia como string suelto en ningún composable.
 *
 * Inventario cerrado contra el `Mockup Final` de Penpot (70 boards) — no se agregan
 * rutas fuera de esta lista. Las pantallas de detalle sin ruta propia (Fotos,
 * Ubicación geográfica, Identificadores destacados, Especies del género o familia,
 * Notas de la salida) NO están aquí a propósito: reciben datos del
 * ViewModel/composable padre (`Profile`/`SpeciesSheet`/`FieldSession`), no son
 * destinos de navegación (§4.1).
 */
sealed interface AnuraRoute {

    // ---- Top-level (NavigationBar) — exactamente 4, dentro del rango 3–5 (§4) ----
    @Serializable
    data object Home : AnuraRoute

    @Serializable
    data object Explore : AnuraRoute

    @Serializable
    data object Observations : AnuraRoute

    @Serializable
    data object Settings : AnuraRoute

    // ---- Con argumento ----
    @Serializable
    data class ObservationDetail(val id: String) : AnuraRoute

    /** `speciesId` con el formato real del catálogo, p.ej. "ANU_COL_PRIS_PAI_001". */
    @Serializable
    data class SpeciesSheet(val speciesId: String) : AnuraRoute

    /** `userId = null` significa perfil propio (§4.1). */
    @Serializable
    data class Profile(val userId: String? = null) : AnuraRoute

    @Serializable
    data class Comments(val observationId: String) : AnuraRoute

    /** `tab`: followers | following | favorites — board Seguidos, seguidores y favoritos. */
    @Serializable
    data class Connections(val userId: String, val tab: String = "followers") : AnuraRoute

    @Serializable
    data class SpeciesByTaxon(val taxonId: String) : AnuraRoute

    @Serializable
    data class FieldSession(val sessionId: String) : AnuraRoute

    @Serializable
    data class NightSounds(val sessionId: String) : AnuraRoute

    @Serializable
    data class FieldSessionNotes(val sessionId: String) : AnuraRoute

    // ---- Pantallas simples adicionales ----
    @Serializable
    data object Favorites : AnuraRoute

    @Serializable
    data object EditProfile : AnuraRoute

    @Serializable
    data object RegionalPackages : AnuraRoute

    /** Avisos de `GET /api/notifications` (C5) — entrada desde Ajustes. */
    @Serializable
    data object Notifications : AnuraRoute

    /** Aviso rico dibujado dentro de la app (`GET /api/notifications/public/:token`). */
    @Serializable
    data class AvisoDetalle(val token: String) : AnuraRoute

    /** `Explora más.` — listado 2×2 del board Penpot, desde explorar. */
    @Serializable
    data object ExploreMore : AnuraRoute

    /** `reached`: genus | family | order — resultado open-set (§4.1). */
    @Serializable
    data class UnknownResult(
        val reached: String = "genus",
        val observationId: String? = null,
        /** Viene de Audio ID: no hay modelo de audio, la pantalla lo avisa como demostración. */
        val audioDemo: Boolean = false,
    ) : AnuraRoute

    /** Sheet del FAB — ruta real, alcanzable desde varias pantallas (§4.2). */
    @Serializable
    data object WhatToRegister : AnuraRoute

    // ---- Grafo anidado: autenticación ----
    @Serializable
    data object AuthGraph : AnuraRoute

    @Serializable
    data object Welcome : AnuraRoute

    @Serializable
    data object SignIn : AnuraRoute

    @Serializable
    data object SignUp : AnuraRoute

    // ---- Grafo anidado: captura/asistente de observación ----
    @Serializable
    data object CaptureGraph : AnuraRoute

    // Los seis pasos del asistente «Paso a paso» (dónde, cuándo, tamaño, fotos, audio, resumen).
    @Serializable
    data object CaptureStep1 : AnuraRoute

    @Serializable
    data object CaptureStep2 : AnuraRoute

    @Serializable
    data object CaptureStep3 : AnuraRoute

    @Serializable
    data object CaptureStep4 : AnuraRoute

    @Serializable
    data object CaptureStep5 : AnuraRoute

    @Serializable
    data object CaptureStep6 : AnuraRoute

    @Serializable
    data object PhotoCapture : AnuraRoute

    @Serializable
    data object AudioCapture : AnuraRoute

    /** No navegable hacia atrás con back normal mientras dura el análisis (§4.1). */
    @Serializable
    data class Analyzing(val source: String = Wizard) : AnuraRoute {
        companion object {
            const val Wizard = "wizard"
            const val Image = "image"
            const val Audio = "audio"
        }
    }
}
