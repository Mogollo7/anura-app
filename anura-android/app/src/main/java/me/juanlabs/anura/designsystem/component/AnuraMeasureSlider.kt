package me.juanlabs.anura.designsystem.component

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Slider
import androidx.compose.material3.SliderDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import me.juanlabs.anura.designsystem.theme.AnuraTheme

/**
 * Línea de medición del paso a paso (SVL / hocico–cloaca): track de marca y thumb
 * neutro. Misma línea en captura y en filtros de explorar.
 */
@Composable
fun AnuraMeasureSlider(
    value: Float,
    onValueChange: (Float) -> Unit,
    valueRange: ClosedFloatingPointRange<Float>,
    modifier: Modifier = Modifier,
) {
    Slider(
        value = value,
        onValueChange = onValueChange,
        modifier = modifier,
        valueRange = valueRange,
        colors = SliderDefaults.colors(
            thumbColor = MaterialTheme.colorScheme.outlineVariant,
            activeTrackColor = AnuraTheme.extendedColors.accentInk,
            inactiveTrackColor = MaterialTheme.colorScheme.surfaceVariant,
        ),
    )
}
