package me.juanlabs.anura.core.data

import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import java.util.UUID
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import me.juanlabs.anura.core.auth.AnuraServerConfig

/**
 * `POST /api/observations` (C3, alcance mínimo — solo lo que ya acepta el endpoint real de
 * `observation-service`: foto, coordenadas, notas, privacidad y la especie que ya identificó
 * el teléfono). El vector de 512 y la cola de auditoría de rechazos con BioCLIP 2.5 del
 * servidor quedan para después (necesitan esquema de base de datos nuevo).
 *
 * Multipart/form-data porque lleva un archivo — [AnuraApi] solo maneja JSON. Sin sesión
 * (invitado) no se llama: la ruta exige `Authorization` en el servidor.
 */
object ObservationsRemote {
    private val json = Json { ignoreUnknownKeys = true }
    private const val ConnectTimeoutMs = 8_000
    private const val ReadTimeoutMs = 30_000
    private const val BoundaryPrefix = "AnuraBoundary"

    suspend fun upload(
        photo: File,
        latitude: Double?,
        longitude: Double?,
        notes: String?,
        isPrivate: Boolean,
        aiTopClass: String?,
        aiTopProb: Double?,
        bearer: String,
    ): ObservationUpload = withContext(Dispatchers.IO) {
        if (!photo.exists()) return@withContext ObservationUpload.Failed
        runCatching {
            val boundary = "$BoundaryPrefix${UUID.randomUUID()}"
            val conn = (URL(AnuraServerConfig.AUTH_BASE_URL + "/api/observations").openConnection() as HttpURLConnection).apply {
                requestMethod = "POST"
                connectTimeout = ConnectTimeoutMs
                readTimeout = ReadTimeoutMs
                doOutput = true
                setRequestProperty("Authorization", "Bearer $bearer")
                setRequestProperty("Content-Type", "multipart/form-data; boundary=$boundary")
            }
            try {
                conn.outputStream.use { out ->
                    fun field(name: String, value: String) {
                        out.write("--$boundary\r\n".toByteArray())
                        out.write("Content-Disposition: form-data; name=\"$name\"\r\n\r\n".toByteArray())
                        out.write("$value\r\n".toByteArray())
                    }
                    latitude?.let { field("lat", it.toString()) }
                    longitude?.let { field("lon", it.toString()) }
                    notes?.takeIf { it.isNotBlank() }?.let { field("notes", it) }
                    field("is_private", isPrivate.toString())
                    aiTopClass?.let { field("ai_top_class", it) }
                    aiTopProb?.let { field("ai_top_prob", it.toString()) }
                    field("ai_location_used", (latitude != null && longitude != null).toString())
                    out.write("--$boundary\r\n".toByteArray())
                    out.write(
                        "Content-Disposition: form-data; name=\"image\"; filename=\"${photo.name}\"\r\n".toByteArray(),
                    )
                    out.write("Content-Type: image/jpeg\r\n\r\n".toByteArray())
                    photo.inputStream().use { it.copyTo(out) }
                    out.write("\r\n--$boundary--\r\n".toByteArray())
                }
                val code = conn.responseCode
                if (code == 401) return@runCatching ObservationUpload.Unauthorized
                if (code !in 200..299) return@runCatching ObservationUpload.Failed
                val text = conn.inputStream.bufferedReader().use { it.readText() }
                val body = json.decodeFromString(UploadResponse.serializer(), text)
                val observationId = body.observation_id ?: return@runCatching ObservationUpload.Failed
                ObservationUpload.Saved(
                    UploadResult(
                        observationId = observationId,
                        thumbnailUrl = absoluteMediaUrl(body.thumbnail_url),
                        imageUrl = absoluteMediaUrl(body.image_url),
                    ),
                )
            } finally {
                conn.disconnect()
            }
        }.getOrDefault(ObservationUpload.Failed)
    }

    private fun absoluteMediaUrl(path: String?): String? {
        if (path.isNullOrBlank()) return null
        return if (path.startsWith("http")) path else AnuraServerConfig.AUTH_BASE_URL + path
    }

    /** Publicar o volver a ocultar una observación que ya está en el servidor. */
    suspend fun updateVisibility(serverId: String, isPrivate: Boolean, bearer: String): Boolean {
        val body = """{"is_private":$isPrivate}"""
        return AnuraApi.putOk("/api/observations/$serverId", body, bearer)
    }

    /** Borra la observación del servidor (fila, predicción y fotos). Solo la dueña puede. */
    suspend fun delete(serverId: String, bearer: String): Boolean =
        AnuraApi.deleteOk("/api/observations/$serverId", bearer)
}

sealed interface ObservationUpload {
    data class Saved(val result: UploadResult) : ObservationUpload
    /** El JWT no vale (venció o el servidor lo rechazó). Hay que volver a entrar. */
    data object Unauthorized : ObservationUpload
    data object Failed : ObservationUpload
}

/** Respuesta de `POST /api/observations` ya normalizada (URLs absolutas). */
data class UploadResult(
    val observationId: String,
    val thumbnailUrl: String?,
    val imageUrl: String?,
)

@Serializable
private data class UploadResponse(
    val observation_id: String? = null,
    val image_url: String? = null,
    val thumbnail_url: String? = null,
)
