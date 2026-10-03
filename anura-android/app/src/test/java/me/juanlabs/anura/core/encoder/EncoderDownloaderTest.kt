package me.juanlabs.anura.core.encoder

import java.io.ByteArrayInputStream
import java.io.File
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder

class EncoderDownloaderTest {
    @get:Rule val tmp = TemporaryFolder()

    private val contenido = ByteArray(300_000) { (it * 31).toByte() }
    private val sha = EncoderStore.sha256(ByteArrayInputStream(contenido))
    private val info = EncoderInfo(sha, "t", "t.onnx", 512, "", "", contenido.size.toLong(), "/api/dataset/publico/encoder/$sha/archivo")

    private fun downloader(store: EncoderStore, transport: EncoderTransport, libre: Long = Long.MAX_VALUE) =
        EncoderDownloader(store, transport, { libre }, reintentos = 3, esperaMs = { 0 })

    /** Servidor falso: honra Range; puede cortar la primera conexión a mitad. */
    private class Fake(val datos: ByteArray, var cortarPrimera: Boolean = false, val ignoraRange: Boolean = false) : EncoderTransport {
        val pedidos = mutableListOf<Long>()
        override fun abrir(path: String, desde: Long): TransportResponse {
            pedidos += desde
            val inicio = if (ignoraRange) 0 else desde.toInt()
            var trozo = datos.copyOfRange(inicio, datos.size)
            if (cortarPrimera) { cortarPrimera = false; trozo = trozo.copyOf(trozo.size / 2) }
            val code = if (desde > 0 && !ignoraRange) 206 else 200
            return TransportResponse(code, ByteArrayInputStream(trozo))
        }
    }

    @Test fun descargaVerificaYMueve() = runBlocking {
        val store = EncoderStore(tmp.newFolder())
        val r = downloader(store, Fake(contenido)).descargar(info)
        assertTrue(r is EncoderDownloadResult.Instalado)
        assertTrue(store.tiene(sha))
        assertFalse(store.temporal(sha).exists())
        assertEquals(sha, EncoderStore.sha256(store.archivo(sha)))
    }

    @Test fun reanudaConRangeTrasUnCorte() = runBlocking {
        val store = EncoderStore(tmp.newFolder())
        val fake = Fake(contenido, cortarPrimera = true)
        val r = downloader(store, fake).descargar(info)
        assertTrue(r is EncoderDownloadResult.Instalado)
        assertEquals(2, fake.pedidos.size)
        assertTrue("el segundo pedido debe continuar con Range", fake.pedidos[1] > 0)
    }

    @Test fun servidorQueIgnoraRangeReiniciaDesdeCero() = runBlocking {
        val store = EncoderStore(tmp.newFolder())
        store.carpeta(sha).mkdirs()
        store.temporal(sha).writeBytes(contenido.copyOf(1000))
        val r = downloader(store, Fake(contenido, ignoraRange = true)).descargar(info)
        assertTrue(r is EncoderDownloadResult.Instalado)
        assertEquals(sha, EncoderStore.sha256(store.archivo(sha)))
    }

    @Test fun shaMalo_borraTemporal_yNoInstala() = runBlocking {
        val store = EncoderStore(tmp.newFolder())
        val corrupto = contenido.copyOf().also { it[10] = (it[10] + 1).toByte() }
        val r = downloader(store, Fake(corrupto)).descargar(info)
        assertEquals(EncoderDownloadResult.ShaNoCoincide, r)
        assertFalse(store.tiene(sha))
        assertFalse(store.temporal(sha).exists())
    }

    @Test fun sinEspacio_noDescarga() = runBlocking {
        val store = EncoderStore(tmp.newFolder())
        val fake = Fake(contenido)
        val r = downloader(store, fake, libre = contenido.size.toLong()).descargar(info)
        assertTrue(r is EncoderDownloadResult.SinEspacio)
        assertTrue(fake.pedidos.isEmpty())
    }

    @Test fun http404_esNoDisponible() = runBlocking {
        val store = EncoderStore(tmp.newFolder())
        val r = downloader(store, { _, _ -> TransportResponse(404, null) }).descargar(info)
        assertEquals(EncoderDownloadResult.NoDisponible, r)
    }

    @Test fun yaInstalado_noVuelveAPedir() = runBlocking {
        val store = EncoderStore(tmp.newFolder())
        downloader(store, Fake(contenido)).descargar(info)
        val fake = Fake(contenido)
        assertEquals(EncoderDownloadResult.YaEstaba, downloader(store, fake).descargar(info))
        assertTrue(fake.pedidos.isEmpty())
    }
}
