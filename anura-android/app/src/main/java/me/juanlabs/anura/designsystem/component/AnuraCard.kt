package me.juanlabs.anura.designsystem.component

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme

/** Tarjeta plana de ANURA: superficie blanca, sin elevación, borde opcional (§3.9). */
@Composable
fun AnuraCard(
    modifier: Modifier = Modifier,
    shape: Shape = RoundedCornerShape(AnuraDimens.radiusCard),
    bordered: Boolean = false,
    color: Color = MaterialTheme.colorScheme.surface,
    content: @Composable () -> Unit,
) {
    Surface(
        modifier = modifier,
        shape = shape,
        color = color,
        border = if (bordered) BorderStroke(1.dp, AnuraTheme.extendedColors.cardStroke) else null,
        shadowElevation = 0.dp,
        tonalElevation = 0.dp,
        content = content,
    )
}
