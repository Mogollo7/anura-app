package me.juanlabs.anura.core.data

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class AmbientTemperatureTest {
    @Test
    fun parse_readsTemperatureHumidityAndRain() {
        val body = """{"current":{"temperature_2m":18.6,"relative_humidity_2m":86.2,"precipitation":0.4}}"""
        val reading = AmbientTemperature.parse(body)
        assertEquals(19, reading?.celsius)
        assertEquals(86, reading?.humidityPercent)
        assertEquals(0.4, reading?.precipitationMm ?: Double.NaN, 0.001)
    }

    @Test
    fun parse_withoutCurrent_isNull() {
        assertNull(AmbientTemperature.parse("{}"))
    }
}
