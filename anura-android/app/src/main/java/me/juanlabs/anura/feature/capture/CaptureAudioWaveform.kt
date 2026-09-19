package me.juanlabs.anura.feature.capture

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Fill
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.rememberReduceMotion

internal const val WaveformBarCount = 32
internal const val WaveformIdleThreshold = 0.035f

/**
 * Visualizador de audio centrado: puntos en reposo y barras simétricas con sonido.
 *
 * Parámetros configurables: [barCount], colores, [barWidth], [dotRadius] y [amplitude]
 * (0f..1f). Las [amplitudes] por barra también van de 0 a 1.
 *
 * Actualización en tiempo real desde AudioRecord / Visualizer:
 * ```
 * val frame = rememberMicWaveform(active = recording)
 * AnuraCenteredWaveform(
 *     amplitudes = frame.amplitudes,
 *     amplitude = frame.level,
 * )
 * ```
 */
@Composable
internal fun AnuraCenteredWaveform(
    amplitudes: List<Float>,
    modifier: Modifier = Modifier,
    barCount: Int = WaveformBarCount,
    barColor: Color = AnuraTheme.extendedColors.accentInk,
    dotColor: Color = AnuraTheme.extendedColors.accentInk,
    barWidth: Dp = 3.dp,
    dotRadius: Dp = 3.dp,
    amplitude: Float = 0f,
    height: Dp = 120.dp,
) {
    val reduceMotion = rememberReduceMotion()
    val breath = if (reduceMotion) {
        1f
    } else {
        val pulse = rememberInfiniteTransition(label = "waveform-idle")
        val animatedBreath by pulse.animateFloat(
            initialValue = 0.72f,
            targetValue = 1f,
            animationSpec = infiniteRepeatable(
                animation = tween(durationMillis = 1_100, easing = LinearEasing),
                repeatMode = RepeatMode.Reverse,
            ),
            label = "waveform-breath",
        )
        animatedBreath
    }
    val bars = if (amplitudes.size == barCount) {
        amplitudes
    } else {
        List(barCount) { index ->
            amplitudes.getOrElse(index) { 0f }
        }
    }
    val peak = bars.maxOrNull() ?: 0f
    val level = amplitude.coerceIn(0f, 1f).coerceAtLeast(peak)
    val idle = level < WaveformIdleThreshold

    Canvas(
        modifier = modifier
            .fillMaxWidth()
            .height(height),
    ) {
        val count = barCount.coerceAtLeast(1)
        val step = size.width / count
        val centerY = size.height / 2f
        val maxBar = size.height * 0.46f
        val stroke = barWidth.toPx()
        val radius = dotRadius.toPx() * if (idle) breath else 1f
        val corner = CornerRadius(stroke / 2f, stroke / 2f)
        repeat(count) { index ->
            val x = step * index + step / 2f
            val energy = bars.getOrElse(index) { 0f }.coerceIn(0f, 1f)
            if (idle) {
                drawCircle(
                    color = dotColor.copy(alpha = 0.45f + breath * 0.4f),
                    radius = radius,
                    center = Offset(x, centerY),
                    style = Fill,
                )
            } else {
                val half = (maxBar * energy.coerceAtLeast(0.08f)).coerceAtLeast(stroke)
                drawRoundRect(
                    color = barColor,
                    topLeft = Offset(x - stroke / 2f, centerY - half),
                    size = Size(stroke, half * 2f),
                    cornerRadius = corner,
                )
            }
        }
    }
}
