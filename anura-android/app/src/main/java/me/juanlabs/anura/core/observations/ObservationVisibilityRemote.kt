package me.juanlabs.anura.core.observations

import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import me.juanlabs.anura.core.auth.AnuraServerConfig
import me.juanlabs.anura.core.data.AnuraApi
import me.juanlabs.anura.core.encoder.EncoderStore

/** Operaciones de C.5 del protocolo que la app necesita para publicar/privatizar y sincronizar privadas. */
interface ObservationVisibilityApi {
    /** `PUT /api/observaciones/{id}/visibilidad` (Android no soporta PATCH en HttpURLConnection). */
    suspend fun cambiarVisibilidad(id: String, visibilidad: Visibilidad, bearer: String): Boolean

    /** `GET /api/observaciones/{id}` — null si no existe (o no es tuya). */
    suspend fun obtener(id: String, bearer: String): ObservacionServidor?

    /** `GET /api/observaciones/mias?visibilidad=privada&desde=<ts>`. */
    suspend fun misPrivadas(desde: Long, bearer: String): List<ObservacionServidor>

    /** Baja la foto `n` a [destino] (vía el `302` a la URL firmada) y devuelve su sha256, o null si falla. */
    suspend fun descargarFoto(id: String, n: Int, destino: File, bearer: String): String?
}

object ObservationVisibilityRemote : ObservationVisibilityApi {
    override suspend fun cambiarVisibilidad(id: String, visibilidad: Visibilidad, bearer: String): Boolean =
        AnuraApi.putOk(
            "/api/observaciones/$id/visibilidad",
            """{"visibilidad":"${visibilidad.wire}"}""",
            bearer,
        )

    override suspend fun obtener(id: String, bearer: String): ObservacionServidor? =
        AnuraApi.get<ObservacionServidor>("/api/observaciones/$id", bearer)

    override suspend fun misPrivadas(desde: Long, bearer: String): List<ObservacionServidor> =
        AnuraApi.get<List<ObservacionServidor>>("/api/observaciones/mias?visibilidad=privada&desde=$desde", bearer)
            .orEmpty()

    override suspend fun descargarFoto(id: String, n: Int, destino: File, bearer: String): String? =
        withContext(Dispatchers.IO) {
            val temporal = File(destino.path + ".part")
            runCatching {
                destino.parentFile?.mkdirs()
                val conn = (URL(AnuraServerConfig.AUTH_BASE_URL + "/api/observaciones/$id/fotos/$n")
                    .openConnection() as HttpURLConnection).apply {
                    connectTimeout = 8_000
                    readTimeout = 30_000
                    instanceFollowRedirects = true
                    setRequestProperty("Authorization", "Bearer $bearer")
                }
                try {
                    if (conn.responseCode !in 200..299) return@runCatching null
                    conn.inputStream.use { input -> temporal.outputStream().use { input.copyTo(it, 1 shl 16) } }
                } finally {
                    conn.disconnect()
                }
                val sha = EncoderStore.sha256(temporal)
                if (temporal.renameTo(destino)) sha else null
            }.getOrNull().also { if (it == null) temporal.delete() }
        }
}
