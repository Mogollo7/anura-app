package me.juanlabs.anura.core.platform

import android.content.Context
import android.graphics.BitmapFactory
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.painter.BitmapPainter
import androidx.compose.ui.graphics.painter.ColorPainter
import androidx.compose.ui.graphics.painter.Painter
import androidx.compose.ui.platform.LocalContext
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Cargador de fotos de red genérico para miniaturas reales del servidor (feed de observaciones,
 * perfiles ajenos) que no vienen embebidas en el APK. El proyecto no trae ninguna librería de
 * imágenes (ni Coil ni Glide): mismo patrón manual que ya usa
 * [me.juanlabs.anura.core.data.ContentCatalog] para las fotos publicadas de especie (`loadPhoto`/
 * `rememberSpeciesPhotoPainter`) — cachea en disco por el hash de la URL; mientras la foto real
 * baja se ve un fondo neutro ([rememberPhotoPlaceholderPainter]), nunca una foto de ejemplo.
 */
private suspend fun downloadPhoto(context: Context, url: String): ImageBitmap? = withContext(Dispatchers.IO) {
    val hash = MessageDigest.getInstance("SHA-256").digest(url.toByteArray()).joinToString("") { "%02x".format(it) }
    val file = File(context.cacheDir, "remote_photos/$hash.jpg")
    if (!file.exists()) {
        val ok = runCatching {
            val conn = (URL(url).openConnection() as HttpURLConnection).apply {
                connectTimeout = 10_000
                readTimeout = 25_000
            }
            try {
                if (conn.responseCode != HttpURLConnection.HTTP_OK) {
                    android.util.Log.w("RemotePhoto", "HTTP ${conn.responseCode} downloading photo: $url")
                    return@runCatching false
                }
                file.parentFile?.mkdirs()
                val tmp = File(file.parentFile, file.name + ".part")
                conn.inputStream.use { input -> tmp.outputStream().use { input.copyTo(it) } }
                tmp.renameTo(file)
            } finally {
                conn.disconnect()
            }
        }.onFailure { android.util.Log.w("RemotePhoto", "Error downloading photo $url: ${it.message}") }
        .getOrDefault(false)
        if (!ok) return@withContext null
    }
    runCatching { BitmapFactory.decodeFile(file.path)?.asImageBitmap() }.getOrNull()
}

/**
 * Hueco neutro para una foto que no hay (o que todavía baja). El APK no trae fotos de especies:
 * mostrar una de ejemplo haría pasar una especie por otra.
 */
@Composable
fun rememberPhotoPlaceholderPainter(): Painter {
    val color = MaterialTheme.colorScheme.surfaceVariant
    return remember(color) { ColorPainter(color) }
}

/**
 * Foto real del servidor en cuanto termina de bajar (sin bloquear el scroll ni el primer
 * dibujo); antes, [fallback] o el hueco neutro.
 */
@Composable
fun rememberRemotePhotoPainter(url: String?, fallback: Painter? = null): Painter {
    val context = LocalContext.current
    val local = fallback ?: rememberPhotoPlaceholderPainter()
    if (url.isNullOrBlank()) return local
    val bitmap by produceState<ImageBitmap?>(initialValue = null, url) {
        value = downloadPhoto(context, url)
    }
    return bitmap?.let { BitmapPainter(it) } ?: local
}
