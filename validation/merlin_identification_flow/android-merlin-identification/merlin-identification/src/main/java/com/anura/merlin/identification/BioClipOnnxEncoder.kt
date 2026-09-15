package com.anura.merlin.identification

import ai.onnxruntime.OnnxTensor
import ai.onnxruntime.OrtEnvironment
import ai.onnxruntime.OrtSession
import android.content.ContentResolver
import android.content.Context
import android.net.Uri
import java.io.File
import java.nio.FloatBuffer
import java.security.MessageDigest
import kotlin.math.abs
import kotlin.math.sqrt

/**
 * Offline adapter for the frozen Fase-9 BioCLIP encoder. It owns only image -> embedding.
 * Ranking, GEO and Open Set must be supplied by an IdentificationEngine using matching releases.
 */
class BioClipOnnxEncoder(
    context: Context,
    assetName: String = DEFAULT_ASSET_NAME,
) : AutoCloseable {
    private val environment = OrtEnvironment.getEnvironment()
    private val session: OrtSession

    init {
        val model = materializeAndVerifyAsset(context, assetName)
        session = environment.createSession(model.absolutePath, OrtSession.SessionOptions())
        val inputInfo = session.inputInfo
        require(inputInfo.size == 1) { "Expected exactly one ONNX input" }
    }

    fun embed(resolver: ContentResolver, imageUri: String): FloatArray =
        resolver.openInputStream(Uri.parse(imageUri))?.use { embed(BioClipPreprocessor.decodeAndPrepare(it)) }
            ?: throw IllegalArgumentException("Cannot open image URI")

    fun embed(nchw: FloatArray): FloatArray {
        require(nchw.size == INPUT_ELEMENTS) { "Expected Float32 NCHW [1,3,224,224]" }
        OnnxTensor.createTensor(environment, FloatBuffer.wrap(nchw), INPUT_SHAPE).use { input ->
            session.run(mapOf(session.inputNames.single() to input)).use { output ->
                val vector = (output[0].value as Array<FloatArray>).single()
                require(vector.size == EMBEDDING_DIMENSION) { "Expected 512-dimensional embedding" }
                require(vector.all { it.isFinite() }) { "Encoder produced non-finite values" }
                val norm = sqrt(vector.sumOf { (it * it).toDouble() })
                require(abs(norm - 1.0) <= L2_TOLERANCE) { "Encoder output is not L2 normalized: $norm" }
                return vector.copyOf()
            }
        }
    }

    override fun close() = session.close()

    private fun materializeAndVerifyAsset(context: Context, assetName: String): File {
        val destination = File(context.noBackupFilesDir, assetName)
        if (!destination.exists() || destination.length() == 0L) {
            context.assets.open(assetName).use { input ->
                destination.outputStream().use { output -> input.copyTo(output) }
            }
        }
        val actual = destination.inputStream().use(::sha256)
        require(actual.equals(ENCODER_SHA256, ignoreCase = true)) {
            "Frozen ONNX SHA-256 mismatch; refusing to load $assetName"
        }
        return destination
    }

    private fun sha256(input: java.io.InputStream): String {
        val digest = MessageDigest.getInstance("SHA-256")
        val buffer = ByteArray(1024 * 1024)
        while (true) {
            val count = input.read(buffer)
            if (count < 0) break
            digest.update(buffer, 0, count)
        }
        return digest.digest().joinToString("") { "%02x".format(it) }
    }

    companion object {
        const val DEFAULT_ASSET_NAME = "models/encoder_anura_fp16.onnx"
        const val ENCODER_SHA256 = "219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad"
        const val EMBEDDING_DIMENSION = 512
        const val INPUT_ELEMENTS = 3 * 224 * 224
        private const val L2_TOLERANCE = 1e-3
        private val INPUT_SHAPE = longArrayOf(1, 3, 224, 224)
    }
}
