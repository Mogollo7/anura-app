package me.juanlabs.anura.core.encoder

import java.io.File
import kotlinx.serialization.json.Json
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder

class EncoderManifestAndStoreTest {
    @get:Rule val tmp = TemporaryFolder()

    private val shaA = "a".repeat(64)
    private val shaB = "b".repeat(64)
    private fun info(sha: String, dim: Int = 512) = EncoderInfo(sha, "n", "f.onnx", dim, "", "", 10, "/x/$sha/archivo")

    @Test fun parseaElManifiestoDelServidor() {
        val json = """{"esquema":1,"activo":{"sha256":"$shaA","nombre":"v2","archivo":"e.onnx","dimension":512,"bytes":5,"url":"/api/dataset/publico/encoder/$shaA/archivo","campo_nuevo":1},"modelos":[]}"""
        val m = Json { ignoreUnknownKeys = true }.decodeFromString<EncoderManifest>(json)
        assertEquals(shaA, m.activoUsable()?.sha256)
        assertEquals(shaA, m.buscar(shaA)?.sha256)
    }

    @Test fun regla6_esquemaODimensionDistintos_seIgnoran() {
        assertNull(EncoderManifest(esquema = 2, activo = info(shaA)).activoUsable())
        assertNull(EncoderManifest(esquema = 1, activo = info(shaA, dim = 768)).activoUsable())
        assertTrue(EncoderManifest(esquema = 2, activo = info(shaA)).usables().isEmpty())
    }

    @Test fun activoPrimeroYSinDuplicados() {
        val m = EncoderManifest(1, info(shaA), listOf(info(shaA), info(shaB)))
        assertEquals(listOf(shaA, shaB), m.usables().map { it.sha256 })
    }

    @Test fun shaInvalidoNoSePuedeUsarComoCarpeta() {
        assertFalse(EncoderContract.esSha256("../../etc"))
        assertFalse(EncoderContract.esSha256(shaA.uppercase()))
        assertFalse(EncoderStore(tmp.newFolder()).tiene("../x"))
    }

    @Test fun limpiarBorraSoloLoQueNingunPaqueteUsa() {
        val store = EncoderStore(tmp.newFolder())
        listOf(shaA, shaB).forEach { store.carpeta(it).mkdirs(); store.archivo(it).writeText("x") }
        val borrados = store.limpiar(enUso = emptySet(), protegidos = setOf(shaB))
        assertEquals(setOf(shaA), borrados)
        assertEquals(setOf(shaB), store.instalados())
    }

    @Test fun resolverUsaElModeloDelPaquete() {
        val store = EncoderStore(tmp.newFolder())
        val r = EncoderResolver(store)
        assertEquals(EncoderResolucion.Empaquetado, r.resolver(null))
        assertEquals(EncoderResolucion.Empaquetado, r.resolver(EncoderContract.ShaEmpaquetado))
        assertEquals(EncoderResolucion.NoDisponible(shaA), r.resolver(shaA))
        store.carpeta(shaA).mkdirs(); store.archivo(shaA).writeText("x")
        assertEquals(EncoderResolucion.Descargado(store.archivo(shaA)), r.resolver(shaA))
    }
}
