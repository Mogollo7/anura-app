package me.juanlabs.anura.feature.capture

import org.junit.Assert.assertEquals
import org.junit.Test

class CaptureSvlScaleTest {

    @Test
    fun fortyMillimetresShowsTwoCompleteCoins() {
        assertEquals(1.97f, cop100EquivalentCoins(40f), 0.01f)
        assertEquals(2, cop100CompleteCoins(40f))
    }

    @Test
    fun oneCoinMatchesPhysicalDiameter() {
        assertEquals(1f, cop100EquivalentCoins(Cop100DiameterMm), 0.001f)
        assertEquals(1, cop100CompleteCoins(Cop100DiameterMm))
    }

    @Test
    fun tenMillimetresDoesNotShowAPartialCoin() {
        assertEquals(0, cop100CompleteCoins(10f))
    }

    @Test
    fun fiftyMillimetresShowsTwoCompleteCoins() {
        assertEquals(2, cop100CompleteCoins(50f))
    }
}
