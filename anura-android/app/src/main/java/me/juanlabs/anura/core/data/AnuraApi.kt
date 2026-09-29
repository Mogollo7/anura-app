package me.juanlabs.anura.core.data

import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.Json
import me.juanlabs.anura.core.auth.AnuraServerConfig
import me.juanlabs.anura.core.platform.ServerConnectionStatus

/**
 * Cliente HTTP compartido hacia el servidor real de ANURA — explorer-service, auth-service,
 * observation-service, todos alcanzados por `https://anura.juanlabs.me` (nginx del frontend
 * enruta cada prefijo `/api/<servicio>` al microservicio correcto, ver
 * `D:\server\Anura\frontend\nginx.conf`). Mismo dominio que ya usa el login de Google
 * ([AnuraServerConfig]) y que ya quedó probado de punta a punta con el teléfono real sin USB
 * (L1, sesión 2026-09-28).
 *
 * A propósito NO reusa el resolver de candidatos LAN de [ContentCatalog] (preferencia →
 * `127.0.0.1:3008` → dominio público): ese existe para que K2 sincronice el catálogo sin sesión
 * ni red pública, algo que estas llamadas (autenticadas, o que dependen de varios servicios a la
 * vez) no necesitan — igual que el login, van siempre por el dominio público.
 */
object AnuraApi {
    @PublishedApi
    internal val json = Json { ignoreUnknownKeys = true }
    private const val ConnectTimeoutMs = 4_000
    private const val ReadTimeoutMs = 10_000

    suspend fun getText(path: String, bearer: String? = null): String? =
        request(path, "GET", body = null, bearer = bearer)

    suspend fun postText(path: String, jsonBody: String = "{}", bearer: String? = null): String? =
        request(path, "POST", body = jsonBody, bearer = bearer)

    suspend inline fun <reified T> get(path: String, bearer: String? = null): T? =
        getText(path, bearer)?.let { text -> runCatching { json.decodeFromString<T>(text) }.getOrNull() }

    suspend inline fun <reified T> post(path: String, jsonBody: String = "{}", bearer: String? = null): T? =
        postText(path, jsonBody, bearer)?.let { text -> runCatching { json.decodeFromString<T>(text) }.getOrNull() }

    /** Para POST cuya única respuesta que importa es "no falló" (p. ej. borrar algo). */
    suspend fun postOk(path: String, jsonBody: String = "{}", bearer: String? = null): Boolean =
        request(path, "POST", body = jsonBody, bearer = bearer) != null

    suspend fun deleteOk(path: String, bearer: String? = null): Boolean =
        request(path, "DELETE", body = null, bearer = bearer) != null

    /** PUT JSON cuya única respuesta que importa es "no falló" (p. ej. publicar una observación). */
    suspend fun putOk(path: String, jsonBody: String, bearer: String? = null): Boolean =
        request(path, "PUT", body = jsonBody, bearer = bearer) != null

    /**
     * Igual que [postText], pero devuelve también el código HTTP — lo necesita [DeviceRemote]
     * para distinguir un 403 "cuenta suspendida" (trae cuerpo) de un error de red (no trae).
     * `code == -1` es fallo de conexión, no una respuesta del servidor.
     */
    suspend fun postWithStatus(path: String, jsonBody: String = "{}", bearer: String? = null): Pair<Int, String?> =
        requestWithStatus(path, "POST", body = jsonBody, bearer = bearer)

    private suspend fun request(
        path: String,
        method: String,
        body: String?,
        bearer: String?,
    ): String? = requestWithStatus(path, method, body, bearer).let { (code, text) -> text.takeIf { code in 200..299 } }

    private suspend fun requestWithStatus(
        path: String,
        method: String,
        body: String?,
        bearer: String?,
    ): Pair<Int, String?> = withContext(Dispatchers.IO) {
        runCatching {
            val conn = (URL(AnuraServerConfig.AUTH_BASE_URL + path).openConnection() as HttpURLConnection).apply {
                requestMethod = method
                connectTimeout = ConnectTimeoutMs
                readTimeout = ReadTimeoutMs
                bearer?.let { setRequestProperty("Authorization", "Bearer $it") }
                if (body != null) {
                    doOutput = true
                    setRequestProperty("Content-Type", "application/json")
                }
            }
            try {
                if (body != null) {
                    OutputStreamWriter(conn.outputStream).use { it.write(body) }
                }
                val code = conn.responseCode
                // El servidor respondió algo (aunque sea 4xx/5xx de negocio): la conexión en sí
                // funciona, que es lo que le importa al indicador de conexión.
                ServerConnectionStatus.update(true)
                val stream = if (code in 200..299) conn.inputStream else conn.errorStream
                val text = stream?.bufferedReader()?.use { it.readText() }
                code to text
            } finally {
                conn.disconnect()
            }
        }.onFailure { ServerConnectionStatus.update(false) }.getOrDefault(-1 to null)
    }
}
