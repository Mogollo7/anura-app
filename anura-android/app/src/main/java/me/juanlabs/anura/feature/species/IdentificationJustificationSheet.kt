package me.juanlabs.anura.feature.species

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraBottomSheet
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

/**
 * `DESPLEGABLE1 (justificación de identificación)` — bottom sheet local, no ruta (§4.2).
 *
 * El motor de identificación no guarda qué zona del animal pesó en el resultado, así que no hay
 * regiones ni porcentajes que mostrar: la hoja lo dice en vez de pintar una máscara de ejemplo.
 * (Antes tenía una máscara de segmentación y pesos por región inventados; se borraron.)
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun IdentificationJustificationSheet(
    onDismiss: () -> Unit,
) {
    AnuraBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = false),
        containerColor = AnuraTheme.extendedColors.boardBackground,
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = AnuraDimens.spaceGutter)
                .padding(bottom = AnuraDimens.spaceSection),
        ) {
            Text(
                text = stringResource(R.string.justification_title),
                style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            Text(
                text = stringResource(R.string.justification_unavailable),
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@AnuraPreviews
@Composable
private fun IdentificationJustificationPreview() {
    AnuraTheme {
        IdentificationJustificationSheet(onDismiss = {})
    }
}

@androidx.compose.ui.tooling.preview.Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun IdentificationJustificationPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) {
        IdentificationJustificationSheet(onDismiss = {})
    }
}
