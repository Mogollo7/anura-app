package me.juanlabs.anura.core.data

import android.content.ContentValues
import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.ImageDecoder
import android.graphics.Matrix
import android.media.ExifInterface
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.util.UUID
import kotlin.math.max

/**
 * Convierte fotos/audio a un formato móvil y los guarda en almacenamiento
 * privado persistente (`filesDir`), no en caché.
 */
class MediaPersistence(private val context: Context) {
    private val photosDir: File
        get() = File(context.filesDir, "anura_media/photos").apply { mkdirs() }
    private val audioDir: File
        get() = File(context.filesDir, "anura_media/audio").apply { mkdirs() }

    fun createPhotoFile(): File = File(photosDir, "specimen_${UUID.randomUUID()}.jpg")

    fun createAudioFile(): File = File(audioDir, "clip_${UUID.randomUUID()}.wav")

    fun persistPhotoToken(token: String): String {
        if (token.startsWith("res:")) return token
        val already = token.removePrefix("file:")
        // CameraX guarda la captura directo en photosDir con la rotación solo en EXIF, y BitmapFactory
        // (visor, detector de borrosidad, identificación) la ignora: esa foto se reescribe ya rotada.
        val capturedInPlace = token.startsWith("file:") && already.startsWith(photosDir.absolutePath)
        if (capturedInPlace && exifOrientation(already) == ExifInterface.ORIENTATION_NORMAL) {
            return token
        }
        val bitmap = decodeBitmap(token) ?: return token
        val scaled = scaleToMax(bitmap, MaxPhotoEdgePx)
        // la pantalla de captura conserva el token original: la foto de cámara se reescribe en su misma ruta
        val out = if (capturedInPlace) File(already) else createPhotoFile()
        val tmp = File(out.path + ".tmp")
        FileOutputStream(tmp).use { stream ->
            scaled.compress(Bitmap.CompressFormat.JPEG, JpegQuality, stream)
        }
        if (scaled !== bitmap) scaled.recycle()
        if (!bitmap.isRecycled) bitmap.recycle()
        if (!tmp.renameTo(out)) {
            tmp.delete()
            return token
        }
        return "file:${out.absolutePath}"
    }

    fun persistAudioFile(source: File): String {
        if (!source.exists()) return "file:${source.absolutePath}"
        if (source.absolutePath.startsWith(audioDir.absolutePath)) {
            return "file:${source.absolutePath}"
        }
        val out = createAudioFile()
        source.copyTo(out, overwrite = true)
        return "file:${out.absolutePath}"
    }

    fun persistAudioUri(uri: Uri): String {
        val out = createAudioFile()
        context.contentResolver.openInputStream(uri)?.use { input ->
            FileOutputStream(out).use { output -> input.copyTo(output) }
        } ?: return uri.toString()
        return "file:${out.absolutePath}"
    }

    fun exportPhotoToGallery(token: String): Boolean {
        val bitmap = decodeBitmap(token) ?: return false
        val filename = "anura_${System.currentTimeMillis()}.jpg"
        val values = ContentValues().apply {
            put(MediaStore.Images.Media.DISPLAY_NAME, filename)
            put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                put(MediaStore.Images.Media.RELATIVE_PATH, Environment.DIRECTORY_PICTURES + "/ANURA")
                put(MediaStore.Images.Media.IS_PENDING, 1)
            }
        }
        val resolver = context.contentResolver
        val collection = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            MediaStore.Images.Media.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY)
        } else {
            MediaStore.Images.Media.EXTERNAL_CONTENT_URI
        }
        val item = resolver.insert(collection, values) ?: return false
        resolver.openOutputStream(item)?.use { stream ->
            bitmap.compress(Bitmap.CompressFormat.JPEG, JpegQuality, stream)
        } ?: return false
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            values.clear()
            values.put(MediaStore.Images.Media.IS_PENDING, 0)
            resolver.update(item, values, null, null)
        }
        return true
    }

    private fun decodeBitmap(token: String): Bitmap? = runCatching {
        when {
            token.startsWith("file:") -> decodeFileUpright(token.removePrefix("file:"))
            token.startsWith("uri:") -> decodeUri(Uri.parse(token.removePrefix("uri:")))
            token.startsWith("content:") -> decodeUri(Uri.parse(token))
            else -> decodeFileUpright(token)
        }
    }.getOrNull()

    private fun decodeFileUpright(path: String): Bitmap? =
        BitmapFactory.decodeFile(path)?.let { applyOrientation(it, exifOrientation(path)) }

    private fun decodeUri(uri: Uri): Bitmap? {
        return if (Build.VERSION.SDK_INT >= 28) {
            val source = ImageDecoder.createSource(context.contentResolver, uri)
            ImageDecoder.decodeBitmap(source)
        } else {
            context.contentResolver.openInputStream(uri)?.use { BitmapFactory.decodeStream(it) }
        }
    }

    companion object {
        private const val MaxPhotoEdgePx = 1920

        fun exifOrientation(path: String): Int = runCatching {
            ExifInterface(path).getAttributeInt(ExifInterface.TAG_ORIENTATION, ExifInterface.ORIENTATION_NORMAL)
        }.getOrDefault(ExifInterface.ORIENTATION_NORMAL).let {
            if (it == ExifInterface.ORIENTATION_UNDEFINED) ExifInterface.ORIENTATION_NORMAL else it
        }

        fun applyOrientation(source: Bitmap, orientation: Int): Bitmap {
            val matrix = Matrix()
            when (orientation) {
                ExifInterface.ORIENTATION_ROTATE_90 -> matrix.setRotate(90f)
                ExifInterface.ORIENTATION_ROTATE_180 -> matrix.setRotate(180f)
                ExifInterface.ORIENTATION_ROTATE_270 -> matrix.setRotate(270f)
                ExifInterface.ORIENTATION_FLIP_HORIZONTAL -> matrix.setScale(-1f, 1f)
                ExifInterface.ORIENTATION_FLIP_VERTICAL -> matrix.setScale(1f, -1f)
                ExifInterface.ORIENTATION_TRANSPOSE -> matrix.apply { setRotate(90f); postScale(-1f, 1f) }
                ExifInterface.ORIENTATION_TRANSVERSE -> matrix.apply { setRotate(270f); postScale(-1f, 1f) }
                else -> return source
            }
            val rotated = Bitmap.createBitmap(source, 0, 0, source.width, source.height, matrix, true)
            if (rotated !== source) source.recycle()
            return rotated
        }
        private const val JpegQuality = 82

        fun scaleToMax(source: Bitmap, maxEdge: Int): Bitmap {
            val longest = max(source.width, source.height)
            if (longest <= maxEdge) return source
            val scale = maxEdge.toFloat() / longest.toFloat()
            val width = (source.width * scale).toInt().coerceAtLeast(1)
            val height = (source.height * scale).toInt().coerceAtLeast(1)
            return Bitmap.createScaledBitmap(source, width, height, true)
        }

        fun fileFromToken(token: String): File? {
            val path = when {
                token.startsWith("file:") -> token.removePrefix("file:")
                token.startsWith("/") -> token
                else -> null
            } ?: return null
            val file = File(path)
            return file.takeIf { it.exists() }
        }

        /**
         * Borra un archivo local nuestro (`anura_media/...`) tras una subida confirmada.
         * No toca `res:`, `uri:` ni rutas fuera de esos directorios.
         */
        fun deleteLocalFile(token: String?): Boolean {
            if (token.isNullOrBlank()) return false
            val file = fileFromToken(token) ?: return false
            val path = file.absolutePath
            val underMedia = path.contains("${File.separator}anura_media${File.separator}")
            if (!underMedia) return false
            return runCatching { file.delete() }.getOrDefault(false)
        }
    }
}
