package me.juanlabs.anura.feature.capture

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import kotlin.math.sqrt

/**
 * Cola circular FIFO de columnas temporales.
 * El índice 0 es la izquierda (muestra más reciente); al empujar, cada columna
 * se desplaza hacia la derecha conservando su amplitud.
 */
internal class ScrollingWaveformBuffer(val capacity: Int = WaveformBarCount) {
    private val columns = FloatArray(capacity)

    fun push(amplitude: Float) {
        for (i in capacity - 1 downTo 1) {
            columns[i] = columns[i - 1]
        }
        columns[0] = amplitude.coerceIn(0f, 1f)
    }

    fun snapshot(): List<Float> = columns.toList()

    fun clear() {
        columns.fill(0f)
    }
}

internal fun pcmRms(samples: ShortArray, count: Int): Float {
    val n = count.coerceAtMost(samples.size).coerceAtLeast(1)
    var acc = 0.0
    for (i in 0 until n) {
        val v = samples[i] / 32768.0
        acc += v * v
    }
    return sqrt(acc / n).toFloat().coerceIn(0f, 1f)
}

internal fun waveformBytesRms(waveform: ByteArray): Float {
    val samples = ShortArray(waveform.size) { index ->
        ((waveform[index].toInt() and 0xFF) - 128).toShort()
    }
    return pcmRms(samples, samples.size)
}

/**
 * Lienzo de espectrograma/waveform con desplazamiento horizontal.
 * Cada valor de [amplitudes] es una columna temporal, no una banda de ecualizador.
 */
@Composable
internal fun SpectrogramView(
    amplitudes: List<Float>,
    modifier: Modifier = Modifier,
    barCount: Int = WaveformBarCount,
    barColor: Color = AnuraTheme.extendedColors.accentInk,
    barWidth: Dp = 3.dp,
    height: Dp = 120.dp,
) {
    val bars = if (amplitudes.size == barCount) {
        amplitudes
    } else {
        List(barCount) { index -> amplitudes.getOrElse(index) { 0f } }
    }
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
        val corner = CornerRadius(stroke / 2f, stroke / 2f)
        repeat(count) { index ->
            val x = step * index + step / 2f
            val energy = bars.getOrElse(index) { 0f }.coerceIn(0f, 1f)
            val half = if (energy < 0.02f) {
                stroke
            } else {
                (maxBar * energy).coerceAtLeast(stroke)
            }
            drawRoundRect(
                color = barColor,
                topLeft = Offset(x - stroke / 2f, centerY - half),
                size = Size(stroke, half * 2f),
                cornerRadius = corner,
            )
        }
    }
}
