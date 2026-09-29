package me.juanlabs.anura.core.data

import android.net.Uri
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * `anura://notifications` o `anura://notifications/<id>` — a dónde apunta el `PendingIntent`
 * de una notificación de aviso (`core/notifications/AnuraNotifications.kt`).
 *
 * `StateFlow` (no `SharedFlow`): el toque puede llegar en `onCreate`, antes de que el
 * `NavHost` exista. Un `SharedFlow` sin replay pierde ese evento y la app abre en Inicio.
 * El valor se queda hasta que la navegación de arranque lo lee.
 */
data class NotificationOpen(val id: String?, val token: Long)

private val _notificationOpenRequests = MutableStateFlow<NotificationOpen?>(null)
val notificationOpenRequests: StateFlow<NotificationOpen?> = _notificationOpenRequests.asStateFlow()

fun emitNotificationOpen(id: String?) {
    _notificationOpenRequests.value = NotificationOpen(id = id, token = System.nanoTime())
}

/** `true` si esta Uri es el deep link de "abrir Avisos" (MainActivity puede recibir otras). */
fun isNotificationOpenUri(uri: Uri?): Boolean {
    if (uri == null) return false
    return uri.scheme == "anura" && uri.host == "notifications"
}

/** Id del aviso concreto, si el `PendingIntent` lo traía en el path. */
fun notificationIdFromUri(uri: Uri?): String? {
    if (!isNotificationOpenUri(uri)) return null
    val segment = uri?.lastPathSegment ?: return null
    if (segment.isBlank() || segment == "notifications") return null
    return segment
}
