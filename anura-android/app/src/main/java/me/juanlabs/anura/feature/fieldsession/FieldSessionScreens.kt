package me.juanlabs.anura.feature.fieldsession

import androidx.compose.runtime.Composable
import me.juanlabs.anura.navigation.MockNavAction
import me.juanlabs.anura.navigation.MockScreenScaffold

/** `Salida de campo en curso` (§4.1, argumento `sessionId`). */
@Composable
fun FieldSessionScreen(
    sessionId: String,
    onBackClick: () -> Unit,
    onOpenNightSounds: (String) -> Unit,
    onOpenNotes: (String) -> Unit,
) {
    MockScreenScaffold(
        title = "Salida de campo $sessionId",
        onBackClick = onBackClick,
        actions = listOf(
            MockNavAction("Sonidos nocturnos") { onOpenNightSounds(sessionId) },
            MockNavAction("Notas de la salida") { onOpenNotes(sessionId) },
        ),
    )
}

/** `Sonidos nocturnos de la salida` (§4.1, argumento `sessionId`). Hoja del árbol. */
@Composable
fun NightSoundsScreen(
    sessionId: String,
    onBackClick: () -> Unit,
) {
    MockScreenScaffold(
        title = "Sonidos nocturnos",
        onBackClick = onBackClick,
        description = "Sonidos nocturnos de la salida $sessionId — contenido temporal.",
    )
}

/** `Notas de la salida de campo` (§4.1, argumento `sessionId`). Hoja del árbol. */
@Composable
fun FieldSessionNotesScreen(
    sessionId: String,
    onBackClick: () -> Unit,
) {
    MockScreenScaffold(
        title = "Notas de la salida",
        onBackClick = onBackClick,
        description = "Notas de la salida $sessionId — contenido temporal.",
    )
}
