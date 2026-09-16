package me.juanlabs.anura.designsystem.component

import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

/**
 * Variantes de [AnuraButton] definidas en `COMP · Botones (alto 60, radio 30)` (§3.9).
 * No hay estados hover/focus dibujados en Penpot: se usan los de Material 3 por
 * defecto (§3.7-P5, decisión 12). El estado "deshabilitado" también se resuelve con el
 * comportamiento estándar de M3 vía el parámetro `enabled`, no con una variante propia.
 */
enum class AnuraButtonStyle {
    Primary,
    Secondary,
    Outline,
    Danger,
}

private val AnuraButtonHeight = 60.dp
private val AnuraButtonShape = RoundedCornerShape(30.dp) // radio = alto/2, medida real del board

/**
 * Botón base de ANURA. Un único composable para las 6 variantes del board de Penpot
 * (los 3 estilos con relleno + contorno se resuelven con [AnuraButtonStyle]; la
 * variante oscura de cada uno la resuelve [AnuraTheme] automáticamente, no es un
 * parámetro de este componente).
 */
@Composable
fun AnuraButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    style: AnuraButtonStyle = AnuraButtonStyle.Primary,
    enabled: Boolean = true,
) {
    val interactionSource = remember { MutableInteractionSource() }
    // El único color de "pressed" explícito en Penpot es accent.pressed (§3.2/§3.3),
    // documentado solo para el acento primario. Las demás variantes usan el overlay de
    // pressed por defecto de Material 3 (no hay token equivalente para ellas en Penpot).
    val isPrimaryPressed by interactionSource.collectIsPressedAsState()

    when (style) {
        AnuraButtonStyle.Primary -> Button(
            onClick = onClick,
            modifier = modifier.height(AnuraButtonHeight),
            enabled = enabled,
            shape = AnuraButtonShape,
            interactionSource = interactionSource,
            colors = ButtonDefaults.buttonColors(
                containerColor = if (isPrimaryPressed) {
                    AnuraTheme.extendedColors.accentPressed
                } else {
                    MaterialTheme.colorScheme.primary
                },
                contentColor = MaterialTheme.colorScheme.onPrimary,
            ),
        ) {
            Text(text)
        }

        AnuraButtonStyle.Secondary -> Button(
            onClick = onClick,
            modifier = modifier.height(AnuraButtonHeight),
            enabled = enabled,
            shape = AnuraButtonShape,
            colors = ButtonDefaults.buttonColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant,
                contentColor = MaterialTheme.colorScheme.onSurfaceVariant,
            ),
        ) {
            Text(text)
        }

        AnuraButtonStyle.Outline -> OutlinedButton(
            onClick = onClick,
            modifier = modifier.height(AnuraButtonHeight),
            enabled = enabled,
            shape = AnuraButtonShape,
        ) {
            Text(text)
        }

        AnuraButtonStyle.Danger -> Button(
            onClick = onClick,
            modifier = modifier.height(AnuraButtonHeight),
            enabled = enabled,
            shape = AnuraButtonShape,
            colors = ButtonDefaults.buttonColors(
                containerColor = MaterialTheme.colorScheme.error,
                contentColor = MaterialTheme.colorScheme.onError,
            ),
        ) {
            Text(text)
        }
    }
}

@Composable
private fun AnuraButtonPreviewContent() {
    Column(
        modifier = Modifier.padding(AnuraDimens.spaceGap),
        verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
    ) {
        AnuraButton(text = "Continuar", onClick = {}, style = AnuraButtonStyle.Primary)
        AnuraButton(text = "Secundario", onClick = {}, style = AnuraButtonStyle.Secondary)
        AnuraButton(text = "Contorno", onClick = {}, style = AnuraButtonStyle.Outline)
        AnuraButton(text = "Eliminar", onClick = {}, style = AnuraButtonStyle.Danger)
        AnuraButton(text = "Deshabilitado", onClick = {}, enabled = false)
    }
}

@AnuraPreviews
@Composable
private fun AnuraButtonPreview() {
    AnuraTheme { AnuraButtonPreviewContent() }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun AnuraButtonPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) { AnuraButtonPreviewContent() }
}
