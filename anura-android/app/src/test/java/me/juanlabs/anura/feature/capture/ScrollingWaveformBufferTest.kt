package me.juanlabs.anura.feature.capture

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ScrollingWaveformBufferTest {

    @Test
    fun newestSampleEntersOnTheLeftAndShiftsRight() {
        val buffer = ScrollingWaveformBuffer(capacity = 4)
        buffer.push(0.1f)
        buffer.push(0.5f)
        buffer.push(0.9f)
        val snapshot = buffer.snapshot()
        assertEquals(0.9f, snapshot[0], 0.0001f)
        assertEquals(0.5f, snapshot[1], 0.0001f)
        assertEquals(0.1f, snapshot[2], 0.0001f)
        assertEquals(0f, snapshot[3], 0.0001f)
    }

    @Test
    fun silenceHasZeroRms() {
        assertEquals(0f, pcmRms(ShortArray(64), 64), 0.0001f)
    }

    @Test
    fun fullScaleHasHighRms() {
        val samples = ShortArray(32) { Short.MAX_VALUE }
        assertTrue(pcmRms(samples, samples.size) > 0.8f)
    }

    @Test
    fun boostRaisesQuietFieldLevels() {
        assertTrue(boostWaveform(0.08f) > 0.3f)
        assertEquals(1f, boostWaveform(0.9f), 0.0001f)
    }
}
