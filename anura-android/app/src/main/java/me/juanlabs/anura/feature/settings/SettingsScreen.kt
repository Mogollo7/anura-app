package me.juanlabs.anura.feature.settings

import androidx.compose.runtime.Composable
import me.juanlabs.anura.navigation.MockNavAction
import me.juanlabs.anura.navigation.MockScreenScaffold

/** `ajustes` (§4.1) — top-level, tab 4. */
@Composable
fun SettingsScreen(
    onOpenRegionalPackages: () -> Unit,
    onOpenProfile: () -> Unit,
) {
    MockScreenScaffold(
        title = "Ajustes",
        actions = listOf(
            MockNavAction("Zonas descargadas", onOpenRegionalPackages),
            MockNavAction("Mi perfil", onOpenProfile),
        ),
    )
}
