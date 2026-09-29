package me.juanlabs.anura.core.data

import android.net.Uri
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import me.juanlabs.anura.core.auth.AnuraServerConfig

/**
 * `https://anura.juanlabs.me/explorer/<id>` — el mismo link que arma la web (`App.jsx`,
 * ruta `/explorer/:id`) y que ahora comparte la app (ver `ObservationTempoActions`,
 * `ObservationScreens.kt`). App Links (`AndroidManifest.xml`) entrega ese link a
 * `MainActivity` en vez de al navegador; mismo puente `onNewIntent`→`SharedFlow` que
 * `core/auth/ServerAuth.kt` usa para el callback de Google.
 */
private val _observationDeepLinkEvents = MutableSharedFlow<String>(extraBufferCapacity = 1)
val observationDeepLinkEvents: SharedFlow<String> = _observationDeepLinkEvents.asSharedFlow()

fun emitObservationDeepLink(id: String) {
    _observationDeepLinkEvents.tryEmit(id)
}

/** `null` si esta Uri no es un link de observación (MainActivity puede recibir otras). */
fun extractObservationId(uri: Uri?): String? {
    if (uri == null) return null
    val host = Uri.parse(AnuraServerConfig.AUTH_BASE_URL).host
    if (uri.host != host) return null
    val segments = uri.pathSegments
    if (segments.size != 2 || segments[0] != "explorer") return null
    return segments[1]
}
