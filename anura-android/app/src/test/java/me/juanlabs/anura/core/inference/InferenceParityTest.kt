package me.juanlabs.anura.core.inference

import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.math.abs
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.double
import kotlinx.serialization.json.float
import kotlinx.serialization.json.int
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * Paridad con PC usando los valores que genera tools/mobile/export_mobile_inference.py
 * (open_clip + ONNX fp16 + sqlite-vec + Mahalanobis oficiales).
 */
class InferenceParityTest {
    private val golden: JsonObject by lazy {
        Json.parseToJsonElement(resource("golden/golden_v1.json").readText()).jsonObject
    }
    private val openSet: OpenSetModel by lazy {
        File("src/main/assets/openset/openset_v1.1.0_clean.bin").inputStream().use(OpenSetModel::read)
    }

    private fun resource(name: String): File =
        File(requireNotNull(javaClass.classLoader?.getResource(name)) { "Falta el recurso $name" }.toURI())

    @Test
    fun preprocess_matchesPillowBicubicResizeCenterCropNormalize() {
        val raw = ByteBuffer.wrap(resource("golden/preprocess_input_rgb.bin").readBytes()).order(ByteOrder.LITTLE_ENDIAN)
        val width = raw.int
        val height = raw.int
        val rgb = IntArray(width * height * 3) { raw.get().toInt() and 0xFF }
        val expected = ByteBuffer.wrap(resource("golden/preprocess_expected_chw.bin").readBytes())
            .order(ByteOrder.LITTLE_ENDIAN).asFloatBuffer()
            .let { buf -> FloatArray(buf.remaining()).also { buf.get(it) } }

        val actual = ClipPreprocessor.preprocessRgb(rgb, width, height)

        assertEquals(expected.size, actual.size)
        val maxDiff = expected.indices.maxOf { abs(expected[it] - actual[it]) }
        assertTrue("max |Δ| = $maxDiff (Pillow vs Kotlin)", maxDiff < 1e-6f)
    }

    @Test
    fun resizedSize_followsTorchvisionShortSideRule() {
        assertEquals(294 to 224, ClipPreprocessor.resizedSize(317, 241))
        assertEquals(224 to 298, ClipPreprocessor.resizedSize(1440, 1920))
        assertEquals(224 to 224, ClipPreprocessor.resizedSize(500, 500))
    }

    @Test
    fun openSetFile_matchesExportedContract() {
        assertEquals(512, openSet.dim)
        assertEquals(41, openSet.centroidIds.size)
        assertEquals(golden["tau"]!!.jsonPrimitive.double, openSet.tau, 0.0)
    }

    @Test
    fun mahalanobis_andDecision_matchPcForEveryGoldenImage() {
        for (image in golden["images"]!!.jsonArray.map { it.jsonObject }) {
            val file = image["file"]!!.jsonPrimitive.content
            val embedding = image["embedding"]!!.jsonArray.map { it.jsonPrimitive.float }.toFloatArray()
            val expected = image["mahalanobis_min"]!!.jsonPrimitive.double

            val score = openSet.score(embedding)

            assertEquals("$file mahalanobis", expected, score.mahalanobis, 1e-6)
            assertEquals("$file centroide", image["nearest_centroid"]!!.jsonPrimitive.content, score.nearestCentroidId)
            assertEquals("$file decisión", image["decision"]!!.jsonPrimitive.content == "ACCEPT", score.accepted)
        }
    }

    @Test
    fun restrictedOpenSet_matchesPcForEveryGoldenImage() {
        val allowedJson = Json.parseToJsonElement(
            File("src/main/assets/openset/allowed_by_package.json").readText(),
        ).jsonObject
        val allowed = allowedJson["ANTIOQUIA"]!!.jsonArray.map { it.jsonPrimitive.content }.toSet()
        assertEquals(30, allowed.size)

        for (image in golden["images"]!!.jsonArray.map { it.jsonObject }) {
            val file = image["file"]!!.jsonPrimitive.content
            val embedding = image["embedding"]!!.jsonArray.map { it.jsonPrimitive.float }.toFloatArray()
            val expected = image["mahalanobis_min_restricted"]!!.jsonPrimitive.double

            val score = openSet.score(embedding, allowed)

            assertEquals("$file mahalanobis restringido", expected, score.mahalanobis, 1e-6)
            assertTrue("$file centroide restringido debe estar en el paquete", score.nearestCentroidId in allowed)
            assertEquals(
                "$file decisión restringida",
                image["decision_restricted"]!!.jsonPrimitive.content == "ACCEPT",
                score.accepted,
            )
        }
    }

    @Test
    fun knnVote_matchesPcPredictionForEveryGoldenImage() {
        assertEquals(5, golden["k"]!!.jsonPrimitive.int)
        for (image in golden["images"]!!.jsonArray.map { it.jsonObject }) {
            val neighbors = image["neighbors"]!!.jsonArray.map { n ->
                val o = n.jsonObject
                Neighbor(
                    taxonId = o["taxon_id"]!!.jsonPrimitive.content,
                    scientificName = o["scientific_name"]!!.jsonPrimitive.content,
                    distance = o["distance"]!!.jsonPrimitive.double,
                )
            }
            assertEquals(
                image["file"]!!.jsonPrimitive.content,
                image["predicted_taxon_id"]!!.jsonPrimitive.content,
                KnnVote.winner(neighbors)?.first,
            )
            val candidates = KnnVote.candidates(neighbors)
            assertEquals(KnnVote.winner(neighbors)?.first, candidates.first().taxonId)
            assertEquals(1.0, candidates.sumOf { it.share }, 1e-9)
            assertTrue(candidates.zipWithNext().all { (a, b) -> a.share >= b.share })
        }
    }
}
