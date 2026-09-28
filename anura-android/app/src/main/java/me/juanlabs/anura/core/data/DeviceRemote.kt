package me.juanlabs.anura.core.data

import java.net.URLEncoder
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.booleanOrNull
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive

/**
 * `POST /api/auth/dispositivos` (C4) — la app se reporta al abrir con sesión iniciada y tras
 * cada login: modelo, versión de Android, versión de la app, paquetes regionales instalados y
 * espacio libre. El servidor contesta si el dispositivo está bloqueado (Admin → Dispositivos) o,
 * con 403, si la cuenta entera está suspendida (Admin → Usuarios) — ese caso no lo cubre
 * [AnuraApi.post] normal porque descarta el cuerpo de cualquier respuesta que no sea 2xx.
 */
object DeviceRemote {
    private val json = Json { ignoreUnknownKeys = true }

    suspend fun report(
        bearer: String,
        deviceKey: String,
        modelo: String,
        android: String,
        appVersion: String,
        paquetes: List<DevicePackageEntry>,
        espacioLibreMb: Long?,
    ): DeviceReportResult {
        val request = DeviceReportRequest(
            device_key = deviceKey,
            modelo = modelo,
            android = android,
            app_version = appVersion,
            paquetes = paquetes,
            espacio_libre_mb = espacioLibreMb,
        )
        val body = json.encodeToString(DeviceReportRequest.serializer(), request)
        val (code, text) = AnuraApi.postWithStatus("/api/auth/dispositivos", body, bearer)
        return when {
            code in 200..299 && text != null ->
                runCatching { json.decodeFromString(DeviceReportResponse.serializer(), text) }
                    .map { DeviceReportResult.Ok(bloqueado = it.bloqueado, motivo = it.motivo) }
                    .getOrDefault(DeviceReportResult.Failed)
            code == 403 && text != null && isSuspended(text) -> DeviceReportResult.Suspended
            else -> DeviceReportResult.Failed
        }
    }

    private fun isSuspended(body: String): Boolean =
        runCatching { Json.parseToJsonElement(body).jsonObject["suspendida"]?.jsonPrimitive?.booleanOrNull }
            .getOrNull() == true
}

@Serializable
private data class DeviceReportRequest(
    val device_key: String,
    val modelo: String,
    val android: String,
    val app_version: String,
    val paquetes: List<DevicePackageEntry>,
    val espacio_libre_mb: Long?,
)

@Serializable
data class DevicePackageEntry(val subregion: String, val version: String)

@Serializable
private data class DeviceReportResponse(
    val id: String? = null,
    val bloqueado: Boolean = false,
    val motivo: String? = null,
)

sealed interface DeviceReportResult {
    data class Ok(val bloqueado: Boolean, val motivo: String?) : DeviceReportResult
    data object Suspended : DeviceReportResult
    data object Failed : DeviceReportResult
}

/**
 * `GET /api/notifications` / `POST /api/notifications/:id/leido` (C5) — avisos de la cuenta que
 * inició sesión (Admin → Operación → Notificaciones los origina). Sin FCM todavía: la app los
 * lee cuando abre la pantalla de avisos, no por push.
 */
object NotificationsRemote {
    suspend fun fetch(bearer: String): NotificationsResponse? =
        AnuraApi.get<NotificationsResponse>("/api/notifications", bearer)

    suspend fun markRead(id: String, bearer: String): Boolean =
        AnuraApi.postOk("/api/notifications/${encode(id)}/leido", bearer = bearer)

    private fun encode(value: String): String = URLEncoder.encode(value, "UTF-8")
}

@Serializable
data class AppNotification(
    val id: String,
    val type: String? = null,
    val title: String,
    val body: String,
    val is_read: Boolean = false,
    val created_at: String? = null,
)

@Serializable
data class NotificationsResponse(
    val avisos: List<AppNotification> = emptyList(),
    val sin_leer: Int = 0,
)
