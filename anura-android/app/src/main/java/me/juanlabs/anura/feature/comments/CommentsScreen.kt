package me.juanlabs.anura.feature.comments

import androidx.compose.runtime.Composable
import me.juanlabs.anura.navigation.MockScreenScaffold

/** `COMENTARIOS` (§4.1, argumento `observationId`). Hoja del árbol: solo vuelve atrás. */
@Composable
fun CommentsScreen(
    observationId: String,
    onBackClick: () -> Unit,
) {
    MockScreenScaffold(
        title = "Comentarios",
        onBackClick = onBackClick,
        description = "Comentarios de la observación $observationId — contenido temporal.",
    )
}
