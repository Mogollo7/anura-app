package me.juanlabs.anura.feature.packages

import androidx.compose.runtime.Composable
import me.juanlabs.anura.navigation.MockScreenScaffold

/**
 * `Zonas descargadas` (§4.1). Descargar/eliminar son pop-ups locales (§4.2), no
 * rutas propias — no se agregan aquí.
 */
@Composable
fun RegionalPackagesScreen(
    onBackClick: () -> Unit,
) {
    MockScreenScaffold(
        title = "Zonas descargadas",
        onBackClick = onBackClick,
        description = "Paquetes regionales (ANTIOQUIA, CAUCA) — contenido temporal, sin conectar aún.",
    )
}
