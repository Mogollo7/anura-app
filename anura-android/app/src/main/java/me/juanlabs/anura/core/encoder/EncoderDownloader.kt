package me.juanlabs.anura.core.encoder

import java.io.File
import java.io.RandomAccessFile
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.withContext

sealed interface EncoderDownloadResult {
    data class Instalado(val archivo: File) : EncoderDownloadResult
    data object YaEstaba : EncoderDownloadResult

    /** Regla 7: hace falta ≥ 2 × bytes libres (temporal + final). */
    data class SinEspacio(val necesarios: Long, val libres: Long) : EncoderDownloadResult

    /** El servidor no tiene ONNX para ese sha (404) o el manifiesto no es compatible. */
    data object NoDisponible : EncoderDownloadResult

    /** Regla 3: el archivo descargado no tiene el sha del manifiesto; ya se borró el temporal. */
    data object ShaNoCoincide : EncoderDownloadResult
    data class ErrorRed(val detalle: String) : EncoderDownloadResult
}

/**
 * Descarga un encoder a un temporal, lo reanuda con `Range`, verifica el sha256 completo y solo
 * entonces lo mueve a su carpeta final (renombrado atómico).
 */
class EncoderDownloader(
    private val store: EncoderStore,
    private val transport: EncoderTransport,
    private val espacioLibre: (File) -> Long,
    private val reintentos: Int = 5,
    private val esperaMs: (intento: Int) -> Long = { 1_000L shl it.coerceAtMost(5) },
) {
    suspend fun descargar(info: EncoderInfo, onProgreso: (Float) -> Unit = {}): EncoderDownloadResult =
        withContext(Dispatchers.IO) {
            if (!info.esCompatible()) return@withContext EncoderDownloadResult.NoDisponible
            if (store.tiene(info.sha256)) return@withContext EncoderDownloadResult.YaEstaba

            val carpeta = store.carpeta(info.sha256).also { it.mkdirs() }
            val temporal = store.temporal(info.sha256)
            val yaBajado = if (temporal.isFile) temporal.length().coerceAtMost(info.bytes) else 0L
            val necesarios = 2 * info.bytes - yaBajado
            val libres = espacioLibre(carpeta)
            if (libres < necesarios) return@withContext EncoderDownloadResult.SinEspacio(necesarios, libres)

            var ultimoError = "sin respuesta"
            for (intento in 0 until reintentos) {
                ensureActive()
                if (intento > 0) delay(esperaMs(intento))
                when (val r = intentar(info, temporal, onProgreso)) {
                    is Intento.Completo -> return@withContext verificarYMover(info, temporal)
                    is Intento.Fatal -> return@withContext r.resultado
                    is Intento.Reintentar -> ultimoError = r.detalle
                }
            }
            EncoderDownloadResult.ErrorRed(ultimoError)
        }

    private sealed interface Intento {
        data object Completo : Intento
        data class Fatal(val resultado: EncoderDownloadResult) : Intento
        data class Reintentar(val detalle: String) : Intento
    }

    private suspend fun intentar(info: EncoderInfo, temporal: File, onProgreso: (Float) -> Unit): Intento {
        if (temporal.isFile && temporal.length() > info.bytes) temporal.delete()
        var desde = if (temporal.isFile) temporal.length() else 0L
        if (desde == info.bytes) return Intento.Completo

        val r = transport.abrir(info.url, desde)
        try {
            when (r.code) {
                200, 206 -> {
                    // 200 con Range pedido: el servidor ignoró el rango y manda todo desde 0.
                    if (r.code == 200 && desde > 0) { temporal.delete(); desde = 0 }
                    val cuerpo = r.body ?: return Intento.Reintentar("respuesta ${r.code} sin cuerpo")
                    RandomAccessFile(temporal, "rw").use { out ->
                        out.seek(desde)
                        val buffer = ByteArray(1 shl 16)
                        var total = desde
                        try {
                            while (true) {
                                kotlinx.coroutines.currentCoroutineContext().ensureActive()
                                val n = cuerpo.read(buffer)
                                if (n < 0) break
                                if (total + n > info.bytes) return Intento.Fatal(deshacer(temporal))
                                out.write(buffer, 0, n)
                                total += n
                                onProgreso(total.toFloat() / info.bytes)
                            }
                        } catch (c: CancellationException) {
                            throw c
                        } catch (t: Throwable) {
                            return Intento.Reintentar(t.message ?: "conexión interrumpida")
                        }
                        if (total != info.bytes) return Intento.Reintentar("incompleto: $total de ${info.bytes} bytes")
                    }
                    return Intento.Completo
                }
                404 -> return Intento.Fatal(EncoderDownloadResult.NoDisponible)
                416 -> { temporal.delete(); return Intento.Reintentar("rango no satisfacible, se reinicia") }
                else -> return Intento.Reintentar("HTTP ${r.code}")
            }
        } finally {
            r.close()
        }
    }

    private fun deshacer(temporal: File): EncoderDownloadResult {
        temporal.delete()
        return EncoderDownloadResult.ShaNoCoincide
    }

    private fun verificarYMover(info: EncoderInfo, temporal: File): EncoderDownloadResult {
        if (temporal.length() != info.bytes || EncoderStore.sha256(temporal) != info.sha256) {
            temporal.delete()
            return EncoderDownloadResult.ShaNoCoincide
        }
        val destino = store.archivo(info.sha256)
        if (!temporal.renameTo(destino)) {
            temporal.delete()
            return EncoderDownloadResult.ErrorRed("no se pudo mover el modelo a ${destino.path}")
        }
        return EncoderDownloadResult.Instalado(destino)
    }
}
