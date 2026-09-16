package me.juanlabs.anura.designsystem.component

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.tooling.preview.Preview
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

/**
 * Campo de texto base de ANURA. Envuelve `OutlinedTextField` de Material 3: Penpot no
 * define una forma o radio propios para los campos del wizard/auth (§3.9 — "Sobre
 * OutlinedTextField M3"), así que se usa la forma por defecto de Material 3
 * ([me.juanlabs.anura.designsystem.theme.AnuraShapes]), sin reinventar el componente.
 *
 * El icono trailing solo es interactivo (`IconButton`, objetivo táctil ≥48dp) cuando
 * se provee [onTrailingIconClick]; de lo contrario es puramente informativo (p.ej. un
 * ícono de error) y no roba foco de TalkBack.
 */
@Composable
fun AnuraTextField(
    value: String,
    onValueChange: (String) -> Unit,
    label: String,
    modifier: Modifier = Modifier,
    placeholder: String? = null,
    supportingText: String? = null,
    isError: Boolean = false,
    enabled: Boolean = true,
    singleLine: Boolean = true,
    leadingIcon: ImageVector? = null,
    trailingIcon: ImageVector? = null,
    trailingIconContentDescription: String? = null,
    onTrailingIconClick: (() -> Unit)? = null,
    keyboardType: KeyboardType = KeyboardType.Text,
    visualTransformation: VisualTransformation = VisualTransformation.None,
) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        modifier = modifier,
        enabled = enabled,
        label = { Text(label) },
        placeholder = placeholder?.let { text -> { Text(text) } },
        supportingText = supportingText?.let { text -> { Text(text) } },
        isError = isError,
        singleLine = singleLine,
        visualTransformation = visualTransformation,
        keyboardOptions = KeyboardOptions(keyboardType = keyboardType),
        leadingIcon = leadingIcon?.let { icon ->
            { Icon(imageVector = icon, contentDescription = null) }
        },
        trailingIcon = trailingIcon?.let { icon ->
            {
                val onClick = onTrailingIconClick
                if (onClick != null) {
                    IconButton(onClick = onClick) {
                        Icon(imageVector = icon, contentDescription = trailingIconContentDescription)
                    }
                } else {
                    Icon(imageVector = icon, contentDescription = trailingIconContentDescription)
                }
            }
        },
    )
}

@Composable
private fun AnuraTextFieldPreviewContent() {
    var normalValue by remember { mutableStateOf("") }
    var errorValue by remember { mutableStateOf("valor inválido") }
    Column(
        modifier = Modifier.padding(AnuraDimens.spaceGap),
        verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
    ) {
        AnuraTextField(
            value = normalValue,
            onValueChange = { normalValue = it },
            label = "Dónde la viste",
            placeholder = "Ej. quebrada El Roble",
        )
        AnuraTextField(
            value = errorValue,
            onValueChange = { errorValue = it },
            label = "Correo",
            isError = true,
            supportingText = "Formato de correo inválido",
            trailingIcon = AnuraIcons.Warning,
            trailingIconContentDescription = "Campo con error",
        )
    }
}

@AnuraPreviews
@Composable
private fun AnuraTextFieldPreview() {
    AnuraTheme { AnuraTextFieldPreviewContent() }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun AnuraTextFieldPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) { AnuraTextFieldPreviewContent() }
}
