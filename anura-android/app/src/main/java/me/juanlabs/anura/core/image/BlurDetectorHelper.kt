package me.juanlabs.anura.core.image

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import kotlin.coroutines.cancellation.CancellationException
import kotlin.math.max
import kotlin.math.min
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Detector liviano de borrosidad por varianza del operador Laplaciano en escala de grises.
 *
 * No usa OpenCV ni otras dependencias nativas: opera sobre un [Bitmap] reducido
 * (por defecto 300×300) en [Dispatchers.Default] para no bloquear el hilo de UI.
 */
object BlurDetectorHelper {

    const val DEFAULT_THRESHOLD = 100.0
    const val DEFAULT_ANALYSIS_SIZE = 300

    /**
     * @return `true` si la varianza del Laplaciano es menor que [threshold].
     * Si no se puede decodificar el token, se considera nítida (fail-open).
     */
    suspend fun isBlurryToken(
        context: Context,
        token: String,
        threshold: Double = DEFAULT_THRESHOLD,
        analysisSize: Int = DEFAULT_ANALYSIS_SIZE,
        dispatcher: CoroutineDispatcher = Dispatchers.Default,
    ): Boolean = withContext(dispatcher) {
        if (token.isBlank() || token.startsWith("res:")) return@withContext false
        val bitmap = decodeToken(context, token, analysisSize * 2) ?: return@withContext false
        try {
            val variance = laplacianVariance(bitmap, analysisSize)
            variance < threshold
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (_: Exception) {
            false
        } finally {
            if (!bitmap.isRecycled) bitmap.recycle()
        }
    }

    suspend fun laplacianVariance(
        bitmap: Bitmap,
        analysisSize: Int = DEFAULT_ANALYSIS_SIZE,
        dispatcher: CoroutineDispatcher = Dispatchers.Default,
    ): Double = withContext(dispatcher) {
        val scaled = scaleForAnalysis(bitmap, analysisSize)
        try {
            val width = scaled.width
            val height = scaled.height
            val pixels = IntArray(width * height)
            scaled.getPixels(pixels, 0, width, 0, 0, width, height)
            laplacianVariance(toLuminance(pixels), width, height)
        } finally {
            if (scaled !== bitmap && !scaled.isRecycled) scaled.recycle()
        }
    }

    internal fun laplacianVariance(gray: IntArray, width: Int, height: Int): Double {
        if (width < 3 || height < 3) return 0.0
        var sum = 0.0
        var sumSq = 0.0
        var count = 0
        for (y in 1 until height - 1) {
            val row = y * width
            for (x in 1 until width - 1) {
                val index = row + x
                val laplacian = gray[index - width] +
                    gray[index + width] +
                    gray[index - 1] +
                    gray[index + 1] -
                    4 * gray[index]
                val value = laplacian.toDouble()
                sum += value
                sumSq += value * value
                count++
            }
        }
        if (count == 0) return 0.0
        val mean = sum / count
        return (sumSq / count) - mean * mean
    }

    private fun toLuminance(pixels: IntArray): IntArray {
        val gray = IntArray(pixels.size)
        for (i in pixels.indices) {
            val color = pixels[i]
            val r = (color shr 16) and 0xFF
            val g = (color shr 8) and 0xFF
            val b = color and 0xFF
            gray[i] = (r * 299 + g * 587 + b * 114) / 1000
        }
        return gray
    }

    private fun scaleForAnalysis(source: Bitmap, analysisSize: Int): Bitmap {
        val longest = max(source.width, source.height)
        if (longest <= analysisSize) return source
        val scale = analysisSize.toFloat() / longest.toFloat()
        val width = max(1, (source.width * scale).toInt())
        val height = max(1, (source.height * scale).toInt())
        return Bitmap.createScaledBitmap(source, width, height, true)
    }

    private fun decodeToken(context: Context, token: String, maxSize: Int): Bitmap? = when {
        token.startsWith("file:") -> decodeFile(token.removePrefix("file:"), maxSize)
        token.startsWith("uri:") -> decodeUri(context, Uri.parse(token.removePrefix("uri:")), maxSize)
        else -> decodeFile(token, maxSize)
    }

    private fun decodeFile(path: String, maxSize: Int): Bitmap? {
        val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        BitmapFactory.decodeFile(path, bounds)
        val options = BitmapFactory.Options().apply {
            inSampleSize = sampleSize(bounds.outWidth, bounds.outHeight, maxSize)
        }
        return BitmapFactory.decodeFile(path, options)
    }

    private fun decodeUri(context: Context, uri: Uri, maxSize: Int): Bitmap? {
        val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        context.contentResolver.openInputStream(uri)?.use { BitmapFactory.decodeStream(it, null, bounds) }
        val options = BitmapFactory.Options().apply {
            inSampleSize = sampleSize(bounds.outWidth, bounds.outHeight, maxSize)
        }
        return context.contentResolver.openInputStream(uri)?.use {
            BitmapFactory.decodeStream(it, null, options)
        }
    }

    private fun sampleSize(width: Int, height: Int, maxSize: Int): Int {
        if (width <= 0 || height <= 0) return 1
        var sample = 1
        var longest = max(width, height)
        while (longest / 2 >= maxSize) {
            sample *= 2
            longest /= 2
        }
        return min(sample, 16)
    }
}
