package me.juanlabs.anura.designsystem.component

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme

/**
 * Botón de pantalla (átomo de auth: Iniciar sesión / Crear cuenta / Bienvenida).
 * Alto 56 dp, radio 12, label 15 sp semibold — no el de `COMP · Botones` (60 / 30).
 */
enum class AnuraFormButtonStyle {
    Primary,
    Secondary,
    Outline,
    OutlineNeutral,
}

/** Literal de Penpot (botón "Ya tengo cuenta"); sin token equivalente. */
private val NeutralOutlineStroke = Color(0xFF626264)

@Composable
fun AnuraFormButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    style: AnuraFormButtonStyle = AnuraFormButtonStyle.Primary,
    icon: ImageVector? = null,
    enabled: Boolean = true,
) {
    val shape = RoundedCornerShape(AnuraDimens.radiusButton)
    val buttonModifier = modifier
        .fillMaxWidth()
        .height(AnuraDimens.sizeActionButton)
    val contentPadding = PaddingValues(horizontal = AnuraDimens.spaceGap)

    when (style) {
        AnuraFormButtonStyle.Primary -> Button(
            onClick = onClick,
            modifier = buttonModifier,
            enabled = enabled,
            shape = shape,
            contentPadding = contentPadding,
            colors = ButtonDefaults.buttonColors(
                containerColor = AnuraTheme.extendedColors.accentInk,
                contentColor = MaterialTheme.colorScheme.onPrimary,
            ),
        ) {
            AnuraFormButtonLabel(text = text, icon = icon)
        }

        AnuraFormButtonStyle.Secondary -> Button(
            onClick = onClick,
            modifier = buttonModifier,
            enabled = enabled,
            shape = shape,
            contentPadding = contentPadding,
            colors = ButtonDefaults.buttonColors(
                containerColor = MaterialTheme.colorScheme.background,
                contentColor = AnuraTheme.extendedColors.accentInk,
            ),
            elevation = ButtonDefaults.buttonElevation(
                defaultElevation = 0.dp,
                pressedElevation = 0.dp,
            ),
        ) {
            AnuraFormButtonLabel(text = text, icon = icon)
        }

        AnuraFormButtonStyle.Outline -> OutlinedButton(
            onClick = onClick,
            modifier = buttonModifier,
            enabled = enabled,
            shape = shape,
            contentPadding = contentPadding,
            border = BorderStroke(2.dp, AnuraTheme.extendedColors.accentInk),
            colors = ButtonDefaults.outlinedButtonColors(
                contentColor = AnuraTheme.extendedColors.accentInk,
            ),
        ) {
            AnuraFormButtonLabel(text = text, icon = icon)
        }

        AnuraFormButtonStyle.OutlineNeutral -> OutlinedButton(
            onClick = onClick,
            modifier = buttonModifier,
            enabled = enabled,
            shape = shape,
            contentPadding = contentPadding,
            border = BorderStroke(2.dp, NeutralOutlineStroke),
            colors = ButtonDefaults.outlinedButtonColors(
                contentColor = MaterialTheme.colorScheme.onSurface,
            ),
        ) {
            AnuraFormButtonLabel(text = text, icon = icon)
        }
    }
}

@Composable
private fun AnuraFormButtonLabel(
    text: String,
    icon: ImageVector?,
) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.Center,
    ) {
        if (icon != null) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(24.dp),
            )
            Spacer(modifier = Modifier.width(8.dp))
        }
        Text(
            text = text,
            style = MaterialTheme.typography.titleMedium.copy(
                fontWeight = FontWeight.SemiBold,
                fontSize = 15.sp,
            ),
        )
    }
}
