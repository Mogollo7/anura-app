package me.juanlabs.anura.core.inference

import android.util.Log
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import java.io.File
import kotlin.math.sqrt
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import kotlinx.serialization.json.double
import kotlinx.serialization.json.float
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Paridad teléfono ↔ PC del pipeline completo (paquete instalado + sqlite-vec + ONNX + Open Set).
 * Requiere el set de referencia en el almacenamiento externo de la app:
 *   adb push golden_images/. /sdcard/Android/data/me.juanlabs.anura/files/golden/
 *   adb push golden_v1.json  /sdcard/Android/data/me.juanlabs.anura/files/golden/
 *   adb push package.sqlite  /sdcard/Android/data/me.juanlabs.anura/files/golden/
 * (package.sqlite: el paquete de Antioquia con el que PC generó el set; el APK ya no trae paquetes).
 * (lo genera tools/mobile/export_mobile_inference.py).
 */
@RunWith(AndroidJUnit4::class)
class OnDeviceInferenceTest {
    private val context = InstrumentationRegistry.getInstrumentation().targetContext

    @Test
    fun goldenImages_matchPcPipeline() = runBlocking {
        val goldenDir = requireNotNull(context.getExternalFilesDir("golden"))
        val golden = Json.parseToJsonElement(File(goldenDir, "golden_v1.json").readText()).jsonObject

        val packageFile = File(goldenDir, "package.sqlite")
        assertTrue("falta ${packageFile.path}", packageFile.exists())
        val packagePath = packageFile.path

        val identifier = AnuraIdentifier(context)
        val failures = mutableListOf<String>()
        for (image in golden["images"]!!.jsonArray.map { it.jsonObject }) {
            val file = image["file"]!!.jsonPrimitive.content
            val expectedEmbedding = image["embedding"]!!.jsonArray.map { it.jsonPrimitive.float }.toFloatArray()
            val outcome = identifier.identify(File(goldenDir, file), packagePath, GoldenPackageId)
            if (outcome !is IdentificationOutcome.Identified) {
                failures += "$file: $outcome"
                continue
            }
            val record = Json.parseToJsonElement(
                File(context.filesDir, "inference_debug/last_identification.json").readText(),
            ).jsonObject
            val embedding = record["embedding"]!!.jsonArray.map { it.jsonPrimitive.float }.toFloatArray()
            val cosine = embedding.indices.sumOf { embedding[it].toDouble() * expectedEmbedding[it] }
            val expectedTaxon = image["predicted_taxon_id"]!!.jsonPrimitive.content
            // el teléfono restringe el Open Set a las especies del paquete activo (ver AnuraIdentifier),
            // así que la decisión a comparar es la restringida, no la del catálogo nacional completo.
            val expectedAccept = image["decision_restricted"]!!.jsonPrimitive.content == "ACCEPT"
            Log.i(
                AnuraIdentifier.Tag,
                "golden $file cos=${"%.6f".format(cosine)} pred=${outcome.taxonId}/$expectedTaxon " +
                    "maha=${"%.3f".format(outcome.openSet.mahalanobis)}/${image["mahalanobis_min_restricted"]!!.jsonPrimitive.content} " +
                    "accept=${outcome.accepted}/$expectedAccept candidates=${outcome.candidates.size}",
            )
            if (cosine < MinCosine) failures += "$file: coseno $cosine < $MinCosine"
            // |d(q',r) - d(q,r)| <= ||q' - q|| = sqrt(2(1 - cos)): el margen entre dos vecinos cambia como mucho 2x eso.
            // Si el 5.º y el 6.º vecino de PC están más cerca que ese límite, el top-5 puede cambiar legítimamente.
            val boundaryGap = image["k_boundary_gap"]!!.jsonPrimitive.double
            val maxGapShift = 2 * sqrt(2 * (1 - cosine))
            if (outcome.taxonId != expectedTaxon) {
                if (boundaryGap < maxGapShift) {
                    Log.w(AnuraIdentifier.Tag, "golden $file empate en el borde k: gap=$boundaryGap < $maxGapShift, especie ${outcome.taxonId} (PC $expectedTaxon)")
                } else {
                    failures += "$file: especie ${outcome.taxonId} != $expectedTaxon (gap=$boundaryGap >= $maxGapShift)"
                }
            }
            if (outcome.accepted != expectedAccept) failures += "$file: decisión ${outcome.accepted} != $expectedAccept"
        }
        assertEquals(failures.joinToString("\n"), 0, failures.size)
    }

    private companion object {
        const val MinCosine = 0.999
    }
}

/** Clave del paquete del set de referencia en `openset/allowed_by_package.json`. */
private const val GoldenPackageId = "ANTIOQUIA"
