package com.anura.merlin.identification

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import java.io.InputStream

/**
 * RGB -> Float32 NCHW preprocessing for BioCLIP. Android's filtered Bitmap scaler must be
 * parity-tested against the frozen OpenCLIP transform before it can be called equivalent.
 */
object BioClipPreprocessor {
    private const val SIZE = 224
    private val mean = floatArrayOf(0.48145466f, 0.4578275f, 0.40821073f)
    private val std = floatArrayOf(0.26862954f, 0.26130258f, 0.27577711f)

    fun decodeAndPrepare(input: InputStream): FloatArray {
        val bitmap = BitmapFactory.decodeStream(input) ?: throw IllegalArgumentException("Invalid image")
        return bitmap.use { prepare(it) }
    }

    fun prepare(source: Bitmap): FloatArray {
        require(source.width > 0 && source.height > 0) { "Empty bitmap" }
        val scale = SIZE.toFloat() / minOf(source.width, source.height).toFloat()
        val resized = Bitmap.createScaledBitmap(
            source, (source.width * scale).toInt().coerceAtLeast(SIZE),
            (source.height * scale).toInt().coerceAtLeast(SIZE), true,
        )
        val left = (resized.width - SIZE) / 2
        val top = (resized.height - SIZE) / 2
        val cropped = Bitmap.createBitmap(resized, left, top, SIZE, SIZE)
        if (resized !== source) resized.recycle()
        return cropped.use { bitmap ->
            val pixels = IntArray(SIZE * SIZE)
            bitmap.getPixels(pixels, 0, SIZE, 0, 0, SIZE, SIZE)
            FloatArray(3 * SIZE * SIZE).also { output ->
                for (index in pixels.indices) {
                    val color = pixels[index]
                    output[index] = (((color shr 16) and 0xff) / 255f - mean[0]) / std[0]
                    output[SIZE * SIZE + index] = (((color shr 8) and 0xff) / 255f - mean[1]) / std[1]
                    output[2 * SIZE * SIZE + index] = ((color and 0xff) / 255f - mean[2]) / std[2]
                }
            }
        }
    }
}

private inline fun <T : Bitmap, R> T.use(block: (T) -> R): R = try {
    block(this)
} finally {
    recycle()
}
