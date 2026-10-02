package me.juanlabs.anura.core.auth

import android.content.Context
import android.net.Uri
import androidx.browser.customtabs.CustomTabsIntent
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

/**
 * Base del backend real (D:\server\Anura). Google exige un `redirect_uri` fijo, registrado
 * en su consola — hoy es el dominio público detrás del túnel de Cloudflare, el mismo que ya
 * usa la web (frontend/). Por eso el login de Google de la app SIEMPRE pasa por ahí, aunque
 * el resto de la etapa L1 (servidor propio en LAN) todavía no exista: son cosas separadas,
 * "con quién habla la app para identificar" contra "con quién habla para iniciar sesión".
 */
object AnuraServerConfig {
    const val AUTH_BASE_URL = "https://anura.juanlabs.me"

    /** Esquema del deep link de vuelta (ver AndroidManifest.xml e intent-filter en MainActivity). */
    const val AUTH_CALLBACK_SCHEME = "anura"
    const val AUTH_CALLBACK_HOST = "auth"
}

@Serializable
data class JwtClaims(
    val id: String? = null,
    val email: String? = null,
    val username: String? = null,
    val role: String? = null,
    /** Segundos desde epoch. Lo pone auth-service (`expiresIn`). */
    val exp: Long? = null,
)

private val jwtJson = Json { ignoreUnknownKeys = true }

/**
 * Puente entre MainActivity (recibe el deep link, sin acceso directo al repositorio ni al
 * NavHost) y AnuraNavHost (los tiene, ver el LaunchedEffect ahí) — mismo patrón que
 * `AnuraRepository.messages`.
 */
private val _authTokenEvents = MutableSharedFlow<String>(extraBufferCapacity = 1)
val authTokenEvents: SharedFlow<String> = _authTokenEvents.asSharedFlow()

fun emitAuthToken(token: String) {
    _authTokenEvents.tryEmit(token)
}

/**
 * Login con Google sin SDK nativo ni un segundo cliente OAuth que registrar en Google Cloud
 * Console: abre el mismo login que ya usa la web (auth-service + Google), en Custom Tabs
 * (no un WebView — Google bloquea OAuth dentro de WebView desde 2016). `platform=mobile` es
 * lo único distinto: auth-service usa ese parámetro para redirigir de vuelta al deep link de
 * la app en vez de al frontend web.
 */
fun launchGoogleLogin(context: Context) {
    val url = "${AnuraServerConfig.AUTH_BASE_URL}/api/auth/google?platform=mobile"
    CustomTabsIntent.Builder().build().launchUrl(context, Uri.parse(url))
}

/**
 * `anura://auth/callback?token=...` — lo que auth-service arma cuando `state=mobile` volvió
 * intacto de Google. `null` si esta Uri no es ese deep link (MainActivity puede recibir otras).
 */
fun extractAuthToken(uri: Uri?): String? {
    if (uri == null) return null
    if (uri.scheme != AnuraServerConfig.AUTH_CALLBACK_SCHEME) return null
    if (uri.host != AnuraServerConfig.AUTH_CALLBACK_HOST) return null
    return uri.getQueryParameter("token")
}

/** True si el JWT ya venció (o vence en los próximos [skewSeconds]). Sin `exp`, no se considera vencido. */
fun isJwtExpired(token: String, skewSeconds: Long = 60): Boolean {
    val exp = decodeJwtClaims(token)?.exp ?: return false
    return exp <= System.currentTimeMillis() / 1000 + skewSeconds
}

/** Payload del JWT (mismo secreto de auth-service) — solo para mostrar/enrutar en la UI. */
fun decodeJwtClaims(token: String): JwtClaims? {
    return runCatching {
        val parts = token.split(".")
        if (parts.size < 2) return null
        val payload = parts[1]
            .replace('-', '+')
            .replace('_', '/')
            .let { it.padEnd(it.length + (4 - it.length % 4) % 4, '=') }
        val decoded = android.util.Base64.decode(payload, android.util.Base64.DEFAULT)
        jwtJson.decodeFromString<JwtClaims>(String(decoded, Charsets.UTF_8))
    }.getOrNull()
}
