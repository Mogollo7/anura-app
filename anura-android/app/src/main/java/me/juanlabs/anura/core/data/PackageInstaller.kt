package me.juanlabs.anura.core.data

import android.content.Context
import java.io.File
import java.security.DigestInputStream
import java.security.MessageDigest
import kotlinx.coroutines.Dispatchers
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
 * Copia un paquete regional desde `assets/` (fuente simulada de "descarga" mientras no
 * exista servidor) hacia almacenamiento privado de la app, verificando su integridad con
 * SHA-256 contra el manifest mientras copia. El día que la fuente sea HTTP, solo cambia
 * de dónde viene el InputStream — el resto (progreso, hash incremental, verificación,
 * limpieza en error) es el mismo.
 */
class PackageInstaller(private val context: Context) {

    suspend fun install(
        manifest: AnuraPackageManifest,
        onProgress: (Float) -> Unit,
    ): PackageInstallResult = withContext(Dispatchers.IO) {
        val destDir = packageDir(manifest.id, manifest.version)
        val destFile = File(destDir, PackageFileName)
        val tempFile = File(destDir, "$PackageFileName.part")
        destDir.mkdirs()

        val digest = MessageDigest.getInstance("SHA-256")
        var bytesCopied = 0L
        val totalBytes = manifest.sizeBytes.coerceAtLeast(1L)

        try {
            context.assets.open(manifest.assetPath).use { input ->
                DigestInputStream(input, digest).use { digestStream ->
                    tempFile.outputStream().use { output ->
                        val buffer = ByteArray(ChunkSizeBytes)
                        while (true) {
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
            if (actualSha256 != manifest.sha256) {
                tempFile.delete()
                return@withContext PackageInstallResult.Failure(
                    "SHA-256 no coincide: esperado ${manifest.sha256}, obtenido $actualSha256",
                )
            }

            if (destFile.exists()) destFile.delete()
            tempFile.renameTo(destFile)
            onProgress(1f)

            PackageInstallResult.Success(
                localPath = destFile.absolutePath,
                sha256 = actualSha256,
                sizeBytes = bytesCopied,
                installedAtEpochMs = System.currentTimeMillis(),
            )
        } catch (t: Throwable) {
            tempFile.delete()
            PackageInstallResult.Failure(t.message ?: "Error desconocido al instalar el paquete")
        }
    }

    /** Borra todas las versiones instaladas de un paquete. */
    fun uninstall(id: String): Boolean {
        val dir = File(packagesRoot(), id)
        return !dir.exists() || dir.deleteRecursively()
    }

    fun localFile(id: String, version: String): File = File(packageDir(id, version), PackageFileName)

    private fun packagesRoot(): File = File(context.filesDir, "packages")

    private fun packageDir(id: String, version: String): File = File(packagesRoot(), "$id/$version")

    companion object {
        private const val ChunkSizeBytes = 64 * 1024
        private const val PackageFileName = "package.sqlite"
    }
}
