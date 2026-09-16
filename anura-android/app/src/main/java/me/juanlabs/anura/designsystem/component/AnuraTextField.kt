package me.juanlabs.anura.designsystem.component

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
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
 * Focus: borde, etiqueta, texto e iconos se mantienen en colores neutros (sin acento
 * primario). El trailing solo es interactivo (`IconButton`, ≥48dp) cuando se provee
 * [onTrailingIconClick].
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
    val scheme = MaterialTheme.colorScheme
    val neutralBorder = scheme.outline
    val neutralLabel = scheme.onSurfaceVariant
    val neutralText = scheme.onSurface
    val neutralIcon = scheme.onSurfaceVariant
    val errorColor = scheme.error

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
        colors = OutlinedTextFieldDefaults.colors(
            focusedBorderColor = if (isError) errorColor else neutralBorder,
            unfocusedBorderColor = if (isError) errorColor else neutralBorder,
            disabledBorderColor = neutralBorder.copy(alpha = 0.38f),
            errorBorderColor = errorColor,
            focusedLabelColor = if (isError) errorColor else neutralLabel,
            unfocusedLabelColor = if (isError) errorColor else neutralLabel,
            disabledLabelColor = neutralLabel.copy(alpha = 0.38f),
            errorLabelColor = errorColor,
            focusedTextColor = neutralText,
            unfocusedTextColor = neutralText,
            disabledTextColor = neutralText.copy(alpha = 0.38f),
            errorTextColor = neutralText,
            cursorColor = neutralText,
            errorCursorColor = errorColor,
            focusedPlaceholderColor = neutralLabel,
            unfocusedPlaceholderColor = neutralLabel,
            disabledPlaceholderColor = neutralLabel.copy(alpha = 0.38f),
            focusedLeadingIconColor = if (isError) errorColor else neutralIcon,
            unfocusedLeadingIconColor = if (isError) errorColor else neutralIcon,
            disabledLeadingIconColor = neutralIcon.copy(alpha = 0.38f),
            errorLeadingIconColor = errorColor,
            focusedTrailingIconColor = if (isError) errorColor else neutralIcon,
            unfocusedTrailingIconColor = if (isError) errorColor else neutralIcon,
            disabledTrailingIconColor = neutralIcon.copy(alpha = 0.38f),
            errorTrailingIconColor = errorColor,
        ),
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
