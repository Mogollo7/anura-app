package me.juanlabs.anura.core.encoder

import java.io.Closeable
import java.io.InputStream
import java.net.HttpURLConnection
import java.net.URL

/** Respuesta de una petición de descarga. [code] -1 = fallo de conexión. */
class TransportResponse(val code: Int, val body: InputStream?, private val onClose: () -> Unit = {}) : Closeable {
    override fun close() {
        runCatching { body?.close() }
        onClose()
    }
}

/** Abstracción de red para poder probar la descarga sin servidor. */
fun interface EncoderTransport {
    /** GET de [path] (relativo al servidor); [desde] > 0 envía `Range: bytes=<desde>-`. */
    fun abrir(path: String, desde: Long): TransportResponse
}

/**
 * HTTP real. `HttpURLConnection` sigue el `302` hacia la URL firmada de MinIO conservando el
 * encabezado `Range`, así que una descarga interrumpida se reanuda pidiendo el `302` otra vez.
 */
class HttpEncoderTransport(private val baseUrl: String) : EncoderTransport {
    override fun abrir(path: String, desde: Long): TransportResponse {
        val conn = (URL(baseUrl + path).openConnection() as HttpURLConnection).apply {
            connectTimeout = 15_000
            readTimeout = 60_000
            instanceFollowRedirects = true
            if (desde > 0) setRequestProperty("Range", "bytes=$desde-")
        }
        return try {
            val code = conn.responseCode
            TransportResponse(code, if (code in 200..299) conn.inputStream else null) { conn.disconnect() }
        } catch (t: Throwable) {
            conn.disconnect()
            TransportResponse(-1, null)
        }
    }
}
