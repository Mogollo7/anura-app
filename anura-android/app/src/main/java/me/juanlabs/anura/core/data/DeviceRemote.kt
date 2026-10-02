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
                    .map {
                        DeviceReportResult.Ok(
                            bloqueado = it.bloqueado,
                            motivo = it.motivo,
                            sincronizar = it.sincronizar,
                        )
                    }
                    .getOrDefault(DeviceReportResult.Failed)
            code == 401 -> DeviceReportResult.Unauthorized
            code == 403 && text != null && isSuspended(text) -> DeviceReportResult.Suspended
            else -> DeviceReportResult.Failed
        }
    }

    /** Quita la petición de sincronización que dejó el admin en este teléfono. */
    suspend fun acknowledge(bearer: String, deviceKey: String): Boolean {
        val body = json.encodeToString(SyncAckRequest.serializer(), SyncAckRequest(device_key = deviceKey))
        return AnuraApi.postOk("/api/auth/dispositivos/sincronizada", body, bearer)
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
    val sincronizar: Boolean = false,
)

@Serializable
private data class SyncAckRequest(val device_key: String)

sealed interface DeviceReportResult {
    data class Ok(val bloqueado: Boolean, val motivo: String?, val sincronizar: Boolean = false) : DeviceReportResult
    data object Unauthorized : DeviceReportResult
    data object Suspended : DeviceReportResult
    data object Failed : DeviceReportResult
}

/**
 * `GET /api/notifications` / `POST /api/notifications/:id/leido` (C5) — avisos de la cuenta que
 * inició sesión (Admin → Operación → Notificaciones los origina). Sin FCM: la app los pide al
 * abrir y, en segundo plano, `AvisosPollWorker` (como máximo cada 15 min).
 */
object NotificationsRemote {
    suspend fun fetch(bearer: String): NotificationsResponse? =
        AnuraApi.get<NotificationsResponse>("/api/notifications", bearer)

    suspend fun markRead(id: String, bearer: String): Boolean =
        AnuraApi.postOk("/api/notifications/${encode(id)}/leido", bearer = bearer)

    suspend fun delete(id: String, bearer: String): Boolean =
        AnuraApi.deleteOk("/api/notifications/${encode(id)}", bearer = bearer)

    suspend fun fetchCompleto(token: String): AvisoCompleto? =
        AnuraApi.get("/api/notifications/public/${encode(token)}")

    private fun encode(value: String): String = URLEncoder.encode(value, "UTF-8")
}

@Serializable
data class AvisoEnlaceDto(val texto: String = "", val url: String = "")

@Serializable
data class AvisoCompleto(
    val titulo: String = "",
    val cuerpo: String = "",
    val enlaces: List<AvisoEnlaceDto> = emptyList(),
    val autor: String? = null,
    val enviado: String? = null,
    val imagen: String? = null,
)

@Serializable
data class AppNotification(
    val id: String,
    val type: String? = null,
    val title: String,
    /** El panel permite enviar un aviso solo con título; el cuerpo llega `null`. */
    val body: String? = null,
    val is_read: Boolean = false,
    val created_at: String? = null,
    /** Página pública /a/<token> cuando el aviso trae texto largo, enlaces o imagen. */
    val enlace: String? = null,
)

private val PieVerCompleto = Regex("""\n*Ver completo\b[\s\S]*$""")
private val UrlEnPie = Regex("""https://\S+""")

/** El body que ve la persona, sin el pie «Ver completo: url» que el servidor mete para el resumen. */
fun AppNotification.cuerpoVisible(): String =
    body?.trim().orEmpty().replace(PieVerCompleto, "").trim()

/** Enlace de la página completa: el campo `enlace` del servidor, o el que ya venía escrito en el body. */
fun AppNotification.enlacePublico(): String? {
    enlace?.trim()?.takeIf { it.startsWith("https://") }?.let { return it }
    val pie = body?.let { PieVerCompleto.find(it) }?.value ?: return null
    return UrlEnPie.find(pie)?.value?.trimEnd('.', ',', ';')
}

/** Token de `/a/<token>` para pedir el aviso completo y dibujarlo dentro de la app. */
fun AppNotification.tokenPublico(): String? = enlacePublico()?.let(::tokenDeEnlace)

fun tokenDeEnlace(url: String): String? {
    val partes = url.substringAfter("://").substringAfter("/").trim('/').split('/')
    if (partes.size < 2 || partes[0] != "a") return null
    return partes[1].takeIf { it.isNotBlank() }
}

@Serializable
data class NotificationsResponse(
    val avisos: List<AppNotification> = emptyList(),
    val sin_leer: Int = 0,
)
