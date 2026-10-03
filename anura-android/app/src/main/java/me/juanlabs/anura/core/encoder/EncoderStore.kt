package me.juanlabs.anura.core.encoder

import java.io.File
import java.io.InputStream
import java.security.MessageDigest

/**
 * Almacenamiento de modelos por sha256: `<raiz>/<sha256>/encoder.onnx`. Nunca se sobrescribe un
 * archivo: un sha nuevo es una carpeta nueva.
 */
class EncoderStore(private val raiz: File) {

    fun carpeta(sha256: String): File {
        require(EncoderContract.esSha256(sha256)) { "sha256 inválido" }
        return File(raiz, sha256)
    }

    fun archivo(sha256: String): File = File(carpeta(sha256), NombreArchivo)

    fun temporal(sha256: String): File = File(carpeta(sha256), "$NombreArchivo.part")

    fun tiene(sha256: String): Boolean = EncoderContract.esSha256(sha256) && archivo(sha256).isFile

    fun instalados(): Set<String> =
        raiz.listFiles()?.filter { it.isDirectory && EncoderContract.esSha256(it.name) && tiene(it.name) }
            ?.map { it.name }?.toSet().orEmpty()

    /**
     * Regla 5: borra los modelos que ningún paquete instalado usa. [protegidos] (p. ej. el activo
     * recién descargado) se conservan aunque todavía no los use ningún paquete.
     * Devuelve los sha borrados.
     */
    fun limpiar(enUso: Set<String>, protegidos: Set<String> = emptySet()): Set<String> {
        val conservar = enUso + protegidos
        val borrados = mutableSetOf<String>()
        raiz.listFiles()?.filter { it.isDirectory && EncoderContract.esSha256(it.name) }?.forEach { dir ->
            if (dir.name !in conservar && dir.deleteRecursively()) borrados += dir.name
        }
        return borrados
    }

    companion object {
        const val NombreArchivo = "encoder.onnx"

        fun sha256(archivo: File): String = archivo.inputStream().use(::sha256)

        fun sha256(input: InputStream): String {
            val digest = MessageDigest.getInstance("SHA-256")
            val buffer = ByteArray(1 shl 20)
            while (true) {
                val n = input.read(buffer)
                if (n < 0) break
                digest.update(buffer, 0, n)
            }
            return digest.digest().joinToString("") { "%02x".format(it) }
        }
    }
}
