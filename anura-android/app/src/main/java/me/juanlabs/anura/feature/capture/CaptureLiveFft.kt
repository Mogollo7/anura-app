package me.juanlabs.anura.feature.capture

internal data class LiveWaveformFrame(
    val amplitudes: List<Float>,
    val level: Float,
    val dominantKhz: Float,
)
