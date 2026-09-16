package me.juanlabs.anura.feature.capture

import androidx.activity.compose.BackHandler
import androidx.compose.runtime.Composable
import me.juanlabs.anura.navigation.MockNavAction
import me.juanlabs.anura.navigation.MockScreenScaffold

/** `Paso 1: dónde la viste` (§4.1, grafo `CaptureGraph`). */
@Composable
fun CaptureStep1Screen(onBackClick: () -> Unit, onNext: () -> Unit) {
    MockScreenScaffold(
        title = "Paso 1 · Dónde la viste",
        onBackClick = onBackClick,
        actions = listOf(MockNavAction("Siguiente", onNext)),
    )
}

/** `Paso 2: cuándo la viste` (§4.1, grafo `CaptureGraph`). */
@Composable
fun CaptureStep2Screen(onBackClick: () -> Unit, onNext: () -> Unit) {
    MockScreenScaffold(
        title = "Paso 2 · Cuándo la viste",
        onBackClick = onBackClick,
        actions = listOf(MockNavAction("Siguiente", onNext)),
    )
}

/** `Paso 3: qué tamaño tenía` (§4.1, grafo `CaptureGraph`). */
@Composable
fun CaptureStep3Screen(onBackClick: () -> Unit, onNext: () -> Unit) {
    MockScreenScaffold(
        title = "Paso 3 · Qué tamaño tenía",
        onBackClick = onBackClick,
        actions = listOf(MockNavAction("Siguiente", onNext)),
    )
}

/** `Paso 4: adjuntar foto y audio` (§4.1, grafo `CaptureGraph`). */
@Composable
fun CaptureStep4Screen(
    onBackClick: () -> Unit,
    onNext: () -> Unit,
    onOpenPhotoCapture: () -> Unit,
    onOpenAudioCapture: () -> Unit,
) {
    MockScreenScaffold(
        title = "Paso 4 · Adjuntar foto y audio",
        onBackClick = onBackClick,
        actions = listOf(
            MockNavAction("Añadir foto", onOpenPhotoCapture),
            MockNavAction("Añadir audio", onOpenAudioCapture),
            MockNavAction("Siguiente", onNext),
        ),
    )
}

/** `Paso 5: resumen y analizar` (§4.1, grafo `CaptureGraph`). */
@Composable
fun CaptureStep5Screen(onBackClick: () -> Unit, onAnalyze: () -> Unit) {
    MockScreenScaffold(
        title = "Paso 5 · Resumen y analizar",
        onBackClick = onBackClick,
        actions = listOf(MockNavAction("Analizar", onAnalyze)),
    )
}

/** `Añadir foto` (§4.1, grafo `CaptureGraph`). Hoja del árbol, vuelve al Paso 4. */
@Composable
fun PhotoCaptureScreen(onBackClick: () -> Unit) {
    MockScreenScaffold(title = "Añadir foto", onBackClick = onBackClick)
}

/**
 * `Añadir audio` (§4.1, grafo `CaptureGraph`). Alcanzable también desde
 * `WhatToRegister` (§4.2) como acceso rápido "grabar sonido nocturno".
 */
@Composable
fun AudioCaptureScreen(onBackClick: () -> Unit) {
    MockScreenScaffold(title = "Añadir audio", onBackClick = onBackClick)
}

/**
 * `Analizando · progreso por etapas` (§4.1, grafo `CaptureGraph`). **No navegable
 * hacia atrás con back normal** mientras dura el análisis: se consume el evento de
 * back en vez de delegarlo (`BackHandler` sin acción), en vez de esconder la flecha de
 * volver de [MockScreenScaffold] nada más — ambos gestos quedan bloqueados.
 */
@Composable
fun AnalyzingScreen(
    onKnownResult: () -> Unit,
    onUnknownResult: () -> Unit,
) {
    BackHandler(enabled = true) { /* Intencional: no se puede retroceder durante el análisis. */ }
    MockScreenScaffold(
        title = "Analizando",
        description = "Progreso por etapas — contenido temporal. Simula el veredicto del motor (fake, fase posterior):",
        actions = listOf(
            MockNavAction("Simular resultado conocido", onKnownResult),
            MockNavAction("Simular resultado open-set (desconocido)", onUnknownResult),
        ),
    )
}

/** `Resultado open-set: especie no registrada` (§4.1, grafo `CaptureGraph`). */
@Composable
fun UnknownResultScreen(onBackClick: () -> Unit) {
    MockScreenScaffold(
        title = "Especie no registrada",
        onBackClick = onBackClick,
        description = "Veredicto Open Set: la especie no está en el catálogo — contenido temporal.",
    )
}

/**
 * `Pop-up del botón "+": qué registrar` (§4.1/§4.2 — ruta real `WhatToRegister`,
 * alcanzable desde varias pantallas). Punto de entrada a cámara, audio y salida de
 * campo.
 */
@Composable
fun WhatToRegisterContent(
    onRegisterSighting: () -> Unit,
    onRecordNightSound: () -> Unit,
    onStartFieldSession: () -> Unit,
) {
    MockScreenScaffold(
        title = "¿Qué quieres registrar?",
        description = "Elige qué quieres registrar — contenido temporal.",
        actions = listOf(
            MockNavAction("Registrar avistamiento", onRegisterSighting),
            MockNavAction("Grabar sonido nocturno", onRecordNightSound),
            MockNavAction("Iniciar salida de campo", onStartFieldSession),
        ),
    )
}
