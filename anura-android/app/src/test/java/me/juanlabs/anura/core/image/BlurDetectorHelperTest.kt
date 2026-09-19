package me.juanlabs.anura.core.image

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class BlurDetectorHelperTest {

    @Test
    fun uniformGrayHasZeroVariance() {
        val width = 8
        val height = 8
        val gray = IntArray(width * height) { 128 }
        assertEquals(0.0, BlurDetectorHelper.laplacianVariance(gray, width, height), 0.0001)
    }

    @Test
    fun checkerboardExceedsDefaultThreshold() {
        val width = 16
        val height = 16
        val gray = IntArray(width * height) { index ->
            val x = index % width
            val y = index / width
            if ((x + y) % 2 == 0) 0 else 255
        }
        assertTrue(
            BlurDetectorHelper.laplacianVariance(gray, width, height) >
                BlurDetectorHelper.DEFAULT_THRESHOLD,
        )
    }

    @Test
    fun tinyImageReturnsZero() {
        assertEquals(0.0, BlurDetectorHelper.laplacianVariance(intArrayOf(1, 2, 3, 4), 2, 2), 0.0)
    }
}
