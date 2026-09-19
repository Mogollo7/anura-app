package me.juanlabs.anura.feature.capture

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier

enum class CaptureSpectrogramPhase {
    Idle,
    Recording,
    Recorded,
    Playing,
    Unavailable,
}

@Composable
internal fun CaptureSpectrogram(
    phase: CaptureSpectrogramPhase,
    modifier: Modifier = Modifier,
    amplitudes: List<Float> = emptyList(),
    amplitude: Float = 0f,
) {
    val live = phase == CaptureSpectrogramPhase.Recording ||
        phase == CaptureSpectrogramPhase.Playing
    val idle = !live && (
        phase == CaptureSpectrogramPhase.Idle ||
            phase == CaptureSpectrogramPhase.Unavailable ||
            amplitude < WaveformIdleThreshold && amplitudes.all { it < WaveformIdleThreshold }
        )
    if (idle) {
        AnuraCenteredWaveform(
            amplitudes = List(WaveformBarCount) { 0f },
            modifier = modifier,
            amplitude = 0f,
        )
    } else {
        SpectrogramView(
            amplitudes = amplitudes.ifEmpty { List(WaveformBarCount) { 0f } },
            modifier = modifier,
        )
    }
}
