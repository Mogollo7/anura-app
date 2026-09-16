package me.juanlabs.anura.feature.home

import androidx.compose.runtime.Composable
import me.juanlabs.anura.navigation.MockNavAction
import me.juanlabs.anura.navigation.MockScreenScaffold

/** `home` (§4.1) — top-level, tab 1. Sin flecha de volver: es raíz de pestaña. */
@Composable
fun HomeScreen(
    onOpenObservationDetail: (String) -> Unit,
    onOpenSpeciesSheet: (String) -> Unit,
    onOpenFieldSession: (String) -> Unit,
) {
    MockScreenScaffold(
        title = "ANURA",
        actions = listOf(
            MockNavAction("Ver última observación") { onOpenObservationDetail("obs-001") },
            MockNavAction("Ver especie identificada") { onOpenSpeciesSheet("ANU_COL_PRIS_PAI_001") },
            MockNavAction("Continuar salida de campo") { onOpenFieldSession("session-001") },
        ),
    )
}
