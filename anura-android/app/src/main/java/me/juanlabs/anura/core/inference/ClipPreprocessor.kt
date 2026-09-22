package me.juanlabs.anura.core.inference

import kotlin.math.ceil
import kotlin.math.round

/**
 * Réplica exacta del preprocesado de open_clip para BioCLIP (el mismo con el que se construyó el paquete):
 * Resize(224, bicubic) sobre el lado corto → CenterCrop(224) → ToTensor → Normalize(mean/std de CLIP).
 *
 * El Resize de torchvision sobre imágenes PIL delega en Pillow, que remuestrea en punto fijo de 8 bits
 * con núcleo bicúbico (a = -0.5) ensanchado al reducir. Se porta tal cual (Resample.c) porque un
 * bilineal/bicúbico distinto cambia el embedding y rompe la paridad con PC.
 */
object ClipPreprocessor {
    const val InputSize = 224
    private val Mean = floatArrayOf(0.48145466f, 0.4578275f, 0.40821073f)
    private val Std = floatArrayOf(0.26862954f, 0.26130258f, 0.27577711f)

    private const val PrecisionBits = 32 - 8 - 2
    private const val BicubicSupport = 2.0

    /** [argb] en el orden de `Bitmap.getPixels` (fila a fila). Devuelve CHW float32 de 3×224×224. */
    fun preprocess(argb: IntArray, width: Int, height: Int): FloatArray {
        require(argb.size == width * height) { "argb.size=${argb.size} != $width×$height" }
        val rgb = IntArray(width * height * 3)
        for (i in argb.indices) {
            val p = argb[i]
            rgb[i * 3] = (p shr 16) and 0xFF
            rgb[i * 3 + 1] = (p shr 8) and 0xFF
            rgb[i * 3 + 2] = p and 0xFF
        }
        return preprocessRgb(rgb, width, height)
    }

    /** [rgb] intercalado R,G,B por píxel, valores 0..255. */
    fun preprocessRgb(rgb: IntArray, width: Int, height: Int): FloatArray {
        val (newW, newH) = resizedSize(width, height)
        val resized = resizeBicubic(rgb, width, height, newW, newH)
        val top = round((newH - InputSize) / 2.0).toInt()
        val left = round((newW - InputSize) / 2.0).toInt()
        val plane = InputSize * InputSize
        val out = FloatArray(3 * plane)
        for (y in 0 until InputSize) {
            for (x in 0 until InputSize) {
                val src = ((y + top) * newW + (x + left)) * 3
                val dst = y * InputSize + x
                for (c in 0 until 3) {
                    val v = resized[src + c].toFloat() / 255f
                    out[c * plane + dst] = (v - Mean[c]) / Std[c]
                }
            }
        }
        return out
    }

    /** torchvision `_compute_resized_output_size` con size=224 y max_size=None. */
    fun resizedSize(width: Int, height: Int): Pair<Int, Int> {
        return if (width <= height) {
            InputSize to (InputSize.toLong() * height / width).toInt()
        } else {
            (InputSize.toLong() * width / height).toInt() to InputSize
        }
    }

    private fun bicubic(value: Double): Double {
        val a = -0.5
        val x = if (value < 0.0) -value else value
        return when {
            x < 1.0 -> ((a + 2.0) * x - (a + 3.0)) * x * x + 1
            x < 2.0 -> (((x - 5) * x + 8) * x - 4) * a
            else -> 0.0
        }
    }

    private class Coefficients(val ksize: Int, val bounds: IntArray, val weights: IntArray)

    private fun precompute(inSize: Int, outSize: Int): Coefficients {
        val scale = inSize.toDouble() / outSize
        val filterScale = if (scale < 1.0) 1.0 else scale
        val support = BicubicSupport * filterScale
        val ksize = ceil(support).toInt() * 2 + 1
        val bounds = IntArray(outSize * 2)
        val weights = IntArray(outSize * ksize)
        val k = DoubleArray(ksize)
        for (xx in 0 until outSize) {
            val center = (xx + 0.5) * scale
            val ss = 1.0 / filterScale
            var xmin = (center - support + 0.5).toInt()
            if (xmin < 0) xmin = 0
            var xmax = (center + support + 0.5).toInt()
            if (xmax > inSize) xmax = inSize
            xmax -= xmin
            var ww = 0.0
            for (x in 0 until xmax) {
                val w = bicubic((x + xmin - center + 0.5) * ss)
                k[x] = w
                ww += w
            }
            for (x in 0 until ksize) {
                val normalized = if (x < xmax && ww != 0.0) k[x] / ww else if (x < xmax) k[x] else 0.0
                weights[xx * ksize + x] = if (normalized < 0) {
                    (-0.5 + normalized * (1 shl PrecisionBits)).toInt()
                } else {
                    (0.5 + normalized * (1 shl PrecisionBits)).toInt()
                }
            }
            bounds[xx * 2] = xmin
            bounds[xx * 2 + 1] = xmax
        }
        return Coefficients(ksize, bounds, weights)
    }

    private fun clip8(value: Int): Int {
        val shifted = value shr PrecisionBits
        return if (shifted < 0) 0 else if (shifted > 255) 255 else shifted
    }

    private fun resizeBicubic(src: IntArray, w: Int, h: Int, outW: Int, outH: Int): IntArray {
        val horizontal = if (outW != w) {
            val c = precompute(w, outW)
            val tmp = IntArray(outW * h * 3)
            for (y in 0 until h) {
                val row = y * w * 3
                for (xx in 0 until outW) {
                    val xmin = c.bounds[xx * 2]
                    val xmax = c.bounds[xx * 2 + 1]
                    var s0 = 1 shl (PrecisionBits - 1)
                    var s1 = s0
                    var s2 = s0
                    for (x in 0 until xmax) {
                        val kw = c.weights[xx * c.ksize + x]
                        val p = row + (x + xmin) * 3
                        s0 += src[p] * kw
                        s1 += src[p + 1] * kw
                        s2 += src[p + 2] * kw
                    }
                    val o = (y * outW + xx) * 3
                    tmp[o] = clip8(s0)
                    tmp[o + 1] = clip8(s1)
                    tmp[o + 2] = clip8(s2)
                }
            }
            tmp
        } else {
            src
        }
        if (outH == h) return horizontal
        val c = precompute(h, outH)
        val out = IntArray(outW * outH * 3)
        for (yy in 0 until outH) {
            val ymin = c.bounds[yy * 2]
            val ymax = c.bounds[yy * 2 + 1]
            for (x in 0 until outW) {
                var s0 = 1 shl (PrecisionBits - 1)
                var s1 = s0
                var s2 = s0
                for (y in 0 until ymax) {
                    val kw = c.weights[yy * c.ksize + y]
                    val p = ((y + ymin) * outW + x) * 3
                    s0 += horizontal[p] * kw
                    s1 += horizontal[p + 1] * kw
                    s2 += horizontal[p + 2] * kw
                }
                val o = (yy * outW + x) * 3
                out[o] = clip8(s0)
                out[o + 1] = clip8(s1)
                out[o + 2] = clip8(s2)
            }
        }
        return out
    }
}
