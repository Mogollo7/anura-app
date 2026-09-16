package me.juanlabs.anura.feature.observations

import androidx.compose.runtime.Composable
import me.juanlabs.anura.navigation.MockNavAction
import me.juanlabs.anura.navigation.MockScreenScaffold

/** `Fotos y observaciones` (§4.1) — top-level, tab 3. */
@Composable
fun ObservationsScreen(
    onOpenObservationDetail: (String) -> Unit,
    onOpenFavorites: () -> Unit,
) {
    MockScreenScaffold(
        title = "Observaciones",
        actions = listOf(
            MockNavAction("Abrir observación") { onOpenObservationDetail("obs-001") },
            MockNavAction("Ver favoritos", onOpenFavorites),
        ),
    )
}

/** `favoritos (listado)` (§4.1). */
@Composable
fun FavoritesScreen(
    onBackClick: () -> Unit,
    onOpenObservationDetail: (String) -> Unit,
) {
    MockScreenScaffold(
        title = "Favoritos",
        onBackClick = onBackClick,
        actions = listOf(
            MockNavAction("Abrir observación favorita") { onOpenObservationDetail("obs-002") },
        ),
    )
}

/** `Detalles de observación (resultado)` (§4.1, argumento `id`). */
@Composable
fun ObservationDetailScreen(
    id: String,
    onBackClick: () -> Unit,
    onOpenComments: (String) -> Unit,
    onOpenSpeciesSheet: (String) -> Unit,
) {
    MockScreenScaffold(
        title = "Observación $id",
        onBackClick = onBackClick,
        actions = listOf(
            MockNavAction("Ver comentarios") { onOpenComments(id) },
            MockNavAction("Ver especie identificada") { onOpenSpeciesSheet("ANU_COL_PRIS_PAI_001") },
        ),
    )
}
