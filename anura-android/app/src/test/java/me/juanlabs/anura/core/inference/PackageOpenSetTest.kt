package me.juanlabs.anura.core.inference

import java.io.File
import java.security.MessageDigest
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.boolean
import kotlinx.serialization.json.double
import kotlinx.serialization.json.float
import kotlinx.serialization.json.int
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Test

/**
 * El modelo de rechazo que compila dataset-service en `open_set_model` (osrModelo.js, ANOS v1).
 * `osr/anos_servidor_dim4.bin` lo generó el codificador del servidor y `.json` trae las distancias
 * que calcula mahalanobis.js del servidor: `node D:/server/Anura/_pruebas/generar_anos_kotlin.js`.
 */
class PackageOpenSetTest {
    private val blob: ByteArray by lazy { resource("osr/anos_servidor_dim4.bin").readBytes() }
    private val expected: JsonObject by lazy {
        Json.parseToJsonElement(resource("osr/anos_servidor_dim4.json").readText()).jsonObject
    }
    private val taxonIds: Set<String> by lazy { expected["ids"]!!.jsonArray.map { it.jsonPrimitive.content }.toSet() }
    private val sha256: String by lazy { expected["sha256"]!!.jsonPrimitive.content }

    private fun resource(name: String): File =
        File(requireNotNull(javaClass.classLoader?.getResource(name)) { "Falta el recurso $name" }.toURI())

    @Test
    fun serverBlob_decodesWithTheHeaderTheServerWrote() {
        val model = OpenSetModel.parse(blob)

        assertEquals(expected["dim"]!!.jsonPrimitive.int, model.dim)
        assertEquals(expected["k"]!!.jsonPrimitive.int, model.centroidIds.size)
        assertEquals(expected["tau"]!!.jsonPrimitive.double, model.tau, 0.0)
        assertEquals(expected["ids"]!!.jsonArray.map { it.jsonPrimitive.content }, model.centroidIds)
        assertEquals(expected["size_bytes"]!!.jsonPrimitive.int, blob.size)
        assertEquals(sha256, sha256Hex(blob))
    }

    @Test
    fun mahalanobis_andDecision_matchTheServerForEverySample() {
        val model = OpenSetModel.parse(blob)
        val samples = expected["muestras"]!!.jsonArray.map { it.jsonObject }
        assertTrue(samples.any { it["acepta"]!!.jsonPrimitive.boolean })
        assertTrue(samples.any { !it["acepta"]!!.jsonPrimitive.boolean })

        for (sample in samples) {
            val name = sample["nombre"]!!.jsonPrimitive.content
            val embedding = sample["embedding"]!!.jsonArray.map { it.jsonPrimitive.float }.toFloatArray()

            val score = model.score(embedding)

            assertEquals("$name mahalanobis", sample["distancia"]!!.jsonPrimitive.double, score.mahalanobis, 1e-6)
            assertEquals("$name centroide", sample["centroide_mas_cercano"]!!.jsonPrimitive.content, score.nearestCentroidId)
            assertEquals("$name decisión", sample["acepta"]!!.jsonPrimitive.boolean, score.accepted)
        }
    }

    @Test
    fun decode_acceptsTheBlobWhenItCoversExactlyThePackageSpecies() {
        val state = PackageOpenSets.decode(PackageOpenSets.Format, sha256, blob, taxonIds)

        assertTrue(state is PackageOpenSet.Ready)
        assertEquals(sha256, (state as PackageOpenSet.Ready).sha256)
        assertEquals(expected["tau"]!!.jsonPrimitive.double, state.model.tau, 0.0)
    }

    @Test
    fun decode_isUnavailableWithoutAModel() {
        assertUnavailable(PackageOpenSets.decode(null, null, null, taxonIds))
        assertUnavailable(PackageOpenSets.decode(PackageOpenSets.Format, sha256, ByteArray(0), taxonIds))
    }

    @Test
    fun decode_rejectsWrongFormatChecksumSpeciesOrCorruptBytes() {
        assertUnavailable(PackageOpenSets.decode("ANOS v2", sha256, blob, taxonIds))
        assertUnavailable(PackageOpenSets.decode(PackageOpenSets.Format, "0".repeat(64), blob, taxonIds))
        // El paquete tiene una especie que el modelo no cubre, o el modelo tiene una que el paquete no trae.
        assertUnavailable(PackageOpenSets.decode(PackageOpenSets.Format, sha256, blob, taxonIds + "COL_ANURA_9999"))
        assertUnavailable(PackageOpenSets.decode(PackageOpenSets.Format, sha256, blob, taxonIds - taxonIds.first()))
        // Truncado, con el sha256 del truncado (llega hasta el parser).
        val truncated = blob.copyOf(blob.size - 5)
        assertUnavailable(PackageOpenSets.decode(PackageOpenSets.Format, sha256Hex(truncated), truncated, taxonIds))
        val withExtra = blob + byteArrayOf(0)
        assertUnavailable(PackageOpenSets.decode(PackageOpenSets.Format, sha256Hex(withExtra), withExtra, taxonIds))
        val badMagic = blob.copyOf().also { it[0] = 'X'.code.toByte() }
        assertUnavailable(PackageOpenSets.decode(PackageOpenSets.Format, sha256Hex(badMagic), badMagic, taxonIds))
    }

    @Test
    fun parse_failsOnATruncatedFile() {
        try {
            OpenSetModel.parse(blob.copyOf(20))
            fail("debía fallar")
        } catch (expected: IllegalArgumentException) {
            assertFalse(expected.message.isNullOrBlank())
        }
    }

    private fun assertUnavailable(state: PackageOpenSet) {
        assertTrue("esperaba Unavailable y llegó $state", state is PackageOpenSet.Unavailable)
        assertFalse((state as PackageOpenSet.Unavailable).detail.isBlank())
    }

    private fun sha256Hex(bytes: ByteArray): String =
        MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }
}
