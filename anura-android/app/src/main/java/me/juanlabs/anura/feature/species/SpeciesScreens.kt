package me.juanlabs.anura.feature.species

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import me.juanlabs.anura.designsystem.component.AnuraBottomSheet
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.navigation.MockNavAction
import me.juanlabs.anura.navigation.MockScreenScaffold

/**
 * `ESPECIE, FAMILIA, GENERO` (ficha técnica, §4.1, argumento `speciesId`).
 *
 * `DESPLEGABLE1` (justificación de identificación) es un **bottom sheet local de esta
 * pantalla**, no una ruta (§4.2: "abre en una sola pantalla → estado local"). Se
 * demuestra aquí con [AnuraBottomSheet], reutilizando el componente del Design System
 * en vez de inventar uno nuevo.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SpeciesSheetScreen(
    speciesId: String,
    onBackClick: () -> Unit,
) {
    var showJustification by remember { mutableStateOf(false) }

    MockScreenScaffold(
        title = speciesId,
        onBackClick = onBackClick,
        description = "Ficha técnica de $speciesId — contenido temporal.",
        actions = listOf(
            MockNavAction("Ver justificación de identificación") { showJustification = true },
        ),
    )

    if (showJustification) {
        AnuraBottomSheet(onDismissRequest = { showJustification = false }) {
            Text(
                text = "Justificación de identificación de $speciesId (contenido temporal).",
                modifier = Modifier.padding(AnuraDimens.spaceGutter),
            )
        }
    }
}
