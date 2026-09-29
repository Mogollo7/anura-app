package me.juanlabs.anura.core.data

import android.content.Context
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder
import kotlinx.serialization.json.Json
import me.juanlabs.anura.core.key.ClaveDocumento
import me.juanlabs.anura.core.key.ClaveFormato
import java.security.DigestInputStream
import java.security.MessageDigest
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.withContext

sealed class PackageInstallResult {
    data class Success(
        val localPath: String,
        val sha256: String,
        val sizeBytes: Long,
        val installedAtEpochMs: Long,
    ) : PackageInstallResult()

    data class Failure(val reason: String) : PackageInstallResult()
}

/**
 * Instala un paquete regional en el almacenamiento privado de la app y comprueba el SHA-256
 * mientras lo baja. El APK no trae paquetes: [installFromUrl] baja el que publica el servidor
 * (Admin → Release, `GET /api/dataset/publico/paquetes`).
 */
class PackageInstaller(private val context: Context) {

    /**
     * Descarga [url] (el sqlite de identificación o el JSON de una subregión), verifica el
     * sha256 publicado y deja el archivo en el directorio del paquete.
     */
    suspend fun installFromUrl(
        id: String,
        version: String,
        url: String,
        expectedSha256: String,
        expectedBytes: Long,
        fileName: String,
        onProgress: (Float) -> Unit,
    ): PackageInstallResult = withContext(Dispatchers.IO) {
        val destDir = packageDir(id, version)
        val destFile = File(destDir, fileName)
        val tempFile = File(destDir, "$fileName.part")
        destDir.mkdirs()
        val digest = MessageDigest.getInstance("SHA-256")
        var bytesCopied = 0L
        val conn = (URL(url).openConnection() as HttpURLConnection).apply {
            connectTimeout = 15_000
            readTimeout = 120_000
            instanceFollowRedirects = true
        }
        try {
            val code = conn.responseCode
            if (code !in 200..299) {
                tempFile.delete()
                return@withContext PackageInstallResult.Failure("El servidor respondió $code al descargar el paquete")
            }
            val totalBytes = conn.contentLengthLong.takeIf { it > 0 } ?: expectedBytes.coerceAtLeast(1L)
            conn.inputStream.use { input ->
                DigestInputStream(input, digest).use { digestStream ->
                    tempFile.outputStream().use { output ->
                        val buffer = ByteArray(ChunkSizeBytes)
                        while (true) {
                            ensureActive()
                            val read = digestStream.read(buffer)
                            if (read == -1) break
                            output.write(buffer, 0, read)
                            bytesCopied += read
                            onProgress((bytesCopied.toFloat() / totalBytes).coerceIn(0f, 0.99f))
                        }
                    }
                }
            }
            val actualSha256 = digest.digest().joinToString("") { "%02x".format(it) }
            if (actualSha256 != expectedSha256) {
                tempFile.delete()
                return@withContext PackageInstallResult.Failure(
                    "SHA-256 no coincide: esperado $expectedSha256, obtenido $actualSha256",
                )
            }
            if (destFile.exists()) destFile.delete()
            if (!tempFile.renameTo(destFile)) {
                tempFile.copyTo(destFile, overwrite = true)
                tempFile.delete()
            }
            onProgress(1f)
            PackageInstallResult.Success(
                localPath = destFile.absolutePath,
                sha256 = actualSha256,
                sizeBytes = bytesCopied,
                installedAtEpochMs = System.currentTimeMillis(),
            )
        } catch (cancelled: CancellationException) {
            tempFile.delete()
            throw cancelled
        } catch (t: Throwable) {
            tempFile.delete()
            PackageInstallResult.Failure(t.message ?: "Error desconocido al descargar el paquete")
        } finally {
            conn.disconnect()
        }
    }

    /** Borra todas las versiones instaladas de un paquete. */
    fun uninstall(id: String): Boolean {
        val dir = File(packagesRoot(), id)
        return !dir.exists() || dir.deleteRecursively()
    }

    fun localFile(id: String, version: String): File = File(packageDir(id, version), PackageFileName)

    /**
     * JSON de la clave (formato 1) junto al paquete. La pantalla lo lee sin red.
     * Si el servidor no responde, se queda el archivo anterior.
     */
    fun readClave(id: String, version: String): ClaveDocumento? {
        val file = claveFile(id, version)
        if (!file.exists()) return null
        return runCatching { claveJson.decodeFromString<ClaveDocumento>(file.readText()) }
            .getOrNull()
            ?.takeIf { it.formato == ClaveFormato }
    }

    suspend fun refreshClave(id: String, version: String): ClaveDocumento? {
        val path = "/api/dataset/publico/clave?subregion=" +
            URLEncoder.encode(id, "UTF-8") +
            "&version=" + URLEncoder.encode(version, "UTF-8")
        val text = AnuraApi.getText(path) ?: return readClave(id, version)
        val documento = runCatching { claveJson.decodeFromString<ClaveDocumento>(text) }.getOrNull()
            ?: return readClave(id, version)
        if (documento.formato != ClaveFormato) return readClave(id, version)
        val file = claveFile(id, version)
        file.parentFile?.mkdirs()
        file.writeText(text)
        return documento
    }

    private fun claveFile(id: String, version: String): File = File(packageDir(id, version), "clave.json")

    private fun packagesRoot(): File = File(context.filesDir, "packages")

    private fun packageDir(id: String, version: String): File = File(packagesRoot(), "$id/$version")

    companion object {
        private const val ChunkSizeBytes = 64 * 1024
        private const val PackageFileName = "package.sqlite"
        private val claveJson = Json { ignoreUnknownKeys = true; coerceInputValues = true }
    }
}
