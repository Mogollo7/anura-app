package me.juanlabs.anura.core.inference

import android.graphics.BitmapFactory
import android.os.SystemClock
import android.util.Log
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import java.io.File
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.float
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Compara variantes del encoder en el teléfono (tiempo y coseno contra PC). Los modelos se suben a
 * /sdcard/Android/data/me.juanlabs.anura/files/models/ y el set de referencia a .../files/golden/.
 */
@RunWith(AndroidJUnit4::class)
class EncoderBenchmarkTest {
    private val context = InstrumentationRegistry.getInstrumentation().targetContext

    @Test
    fun benchmarkEncoderVariants() {
        val goldenDir = requireNotNull(context.getExternalFilesDir("golden"))
        val models = requireNotNull(context.getExternalFilesDir("models")).listFiles { f -> f.extension == "onnx" }.orEmpty()
        assumeTrue("No hay modelos en files/models", models.isNotEmpty())
        val image = Json.parseToJsonElement(File(goldenDir, "golden_v1.json").readText())
            .jsonObject["images"]!!.jsonArray.first().jsonObject
        val reference = image["embedding"]!!.jsonArray.map { it.jsonPrimitive.float }.toFloatArray()
        val bitmap = BitmapFactory.decodeFile(File(goldenDir, image["file"]!!.jsonPrimitive.content).path)
        val pixels = IntArray(bitmap.width * bitmap.height).also {
            bitmap.getPixels(it, 0, bitmap.width, 0, 0, bitmap.width, bitmap.height)
        }
        val chw = ClipPreprocessor.preprocess(pixels, bitmap.width, bitmap.height)

        for (model in models.sortedBy { it.name }) {
            for (xnnpack in listOf(false, true)) {
                val label = "${model.name} ${if (xnnpack) "xnnpack" else "cpu"}"
                val loadStart = SystemClock.elapsedRealtime()
                val encoder = runCatching { ImageEncoder.fromFile(model.path, xnnpack) }.getOrElse {
                    Log.w(AnuraIdentifier.Tag, "bench $label no carga: ${it.message}")
                    null
                } ?: continue
                val loadMs = SystemClock.elapsedRealtime() - loadStart
                encoder.use {
                    var embedding = it.encode(chw)
                    val times = List(3) { _ ->
                        val t = SystemClock.elapsedRealtime()
                        embedding = it.encode(chw)
                        SystemClock.elapsedRealtime() - t
                    }
                    val cosine = embedding.indices.sumOf { i -> embedding[i].toDouble() * reference[i] }
                    Log.i(
                        AnuraIdentifier.Tag,
                        "bench $label load=${loadMs}ms encode=${times.sorted()[1]}ms (runs=$times) cos=${"%.6f".format(cosine)}",
                    )
                }
            }
        }
    }
}
