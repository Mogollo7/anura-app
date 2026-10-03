package me.juanlabs.anura.core.inference

import ai.onnxruntime.OnnxTensor
import ai.onnxruntime.OrtEnvironment
import ai.onnxruntime.OrtSession
import android.content.Context
import java.io.File
import java.nio.FloatBuffer
import kotlin.math.sqrt

/**
 * Encoder BioCLIP fine-tuned exportado a ONNX (fp16, entrada `imagen` float32 [1,3,224,224],
 * salida `embedding` [1,512]). El asset se copia una vez a filesDir porque ORT carga el modelo
 * desde ruta sin duplicarlo en el heap de Java.
 */
class ImageEncoder private constructor(private val session: OrtSession) : AutoCloseable {

    fun encode(chw: FloatArray): FloatArray {
        val env = OrtEnvironment.getEnvironment()
        val shape = longArrayOf(1, 3, ClipPreprocessor.InputSize.toLong(), ClipPreprocessor.InputSize.toLong())
        OnnxTensor.createTensor(env, FloatBuffer.wrap(chw), shape).use { input ->
            session.run(mapOf(InputName to input)).use { result ->
                @Suppress("UNCHECKED_CAST")
                val raw = (result.get(OutputName).get().value as Array<FloatArray>)[0]
                return l2Normalize(raw)
            }
        }
    }

    override fun close() = session.close()

    companion object {
        const val AssetPath = "models/encoder_anura_fp16.onnx"
        private const val InputName = "imagen"
        private const val OutputName = "embedding"

        fun load(context: Context): ImageEncoder {
            val modelFile = File(context.filesDir, AssetPath)
            val expectedSize = context.assets.openFd(AssetPath).use { it.length }
            if (!modelFile.exists() || modelFile.length() != expectedSize) {
                modelFile.parentFile?.mkdirs()
                val tmp = File(modelFile.path + ".part")
                context.assets.open(AssetPath).use { input -> tmp.outputStream().use { input.copyTo(it, 1 shl 20) } }
                check(tmp.renameTo(modelFile)) { "No se pudo mover el modelo a ${modelFile.path}" }
            }
            // FP16 en el EP de CPU usa kernels genéricos (~14 s/foto en ARM); XNNPACK ~0,8 s con el mismo modelo.
            return loadFile(modelFile)
        }

        /** Encoder descargado (`models/by-sha/<sha256>/encoder.onnx`), ya verificado por el descargador. */
        fun loadFile(modelFile: File): ImageEncoder =
            runCatching { fromFile(modelFile.absolutePath, xnnpack = true) }
                .getOrElse { fromFile(modelFile.absolutePath, xnnpack = false) }

        fun fromFile(modelPath: String, xnnpack: Boolean = false): ImageEncoder {
            val options = OrtSession.SessionOptions().apply {
                setOptimizationLevel(OrtSession.SessionOptions.OptLevel.ALL_OPT)
                if (xnnpack) {
                    setIntraOpNumThreads(1)
                    addConfigEntry("session.intra_op.allow_spinning", "0")
                    addXnnpack(mapOf("intra_op_num_threads" to "4"))
                } else {
                    setIntraOpNumThreads(4)
                }
            }
            return ImageEncoder(OrtEnvironment.getEnvironment().createSession(modelPath, options))
        }

        fun l2Normalize(v: FloatArray): FloatArray {
            var sum = 0.0
            for (x in v) sum += x.toDouble() * x
            val norm = sqrt(sum).toFloat()
            return FloatArray(v.size) { v[it] / norm }
        }
    }
}
