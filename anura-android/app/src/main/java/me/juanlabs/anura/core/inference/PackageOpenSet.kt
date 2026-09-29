package me.juanlabs.anura.core.inference

import java.security.MessageDigest

/**
 * Modelo de rechazo Open Set de un paquete instalado. Sale de la tabla `open_set_model` del sqlite
 * (lo compila dataset-service con el umbral que validó una persona). Sin modelo válido no se acepta
 * ninguna identificación: no hay modelo de respaldo empaquetado en el APK.
 */
sealed interface PackageOpenSet {
    data class Ready(val model: OpenSetModel, val sha256: String) : PackageOpenSet

    /** El paquete no trae modelo, o trae uno dañado o que no corresponde a sus especies. */
    data class Unavailable(val detail: String) : PackageOpenSet
}

object PackageOpenSets {
    const val Format = "ANOS v1"

    /**
     * Valida y decodifica la fila `open_set_model` (id = 1) de un paquete.
     *
     * @param packageTaxonIds los `taxon_id` de la tabla `taxa`: el modelo tiene que cubrir exactamente
     * esas especies (el servidor calibró τ con esas medias; con otras el umbral no significa lo mismo).
     */
    fun decode(format: String?, sha256: String?, data: ByteArray?, packageTaxonIds: Set<String>): PackageOpenSet {
        if (data == null || data.isEmpty()) return PackageOpenSet.Unavailable("El paquete no trae modelo de rechazo")
        if (format != Format) return PackageOpenSet.Unavailable("Formato de rechazo no soportado: $format")
        val actual = sha256Hex(data)
        if (!actual.equals(sha256, ignoreCase = true)) {
            return PackageOpenSet.Unavailable("El modelo de rechazo está dañado (sha256 no coincide)")
        }
        val model = runCatching { OpenSetModel.parse(data) }.getOrElse {
            return PackageOpenSet.Unavailable(it.message ?: "El modelo de rechazo no se puede leer")
        }
        if (model.centroidIds.toSet() != packageTaxonIds || model.centroidIds.size != packageTaxonIds.size) {
            return PackageOpenSet.Unavailable("El modelo de rechazo no corresponde a las especies del paquete")
        }
        return PackageOpenSet.Ready(model, actual)
    }

    private fun sha256Hex(bytes: ByteArray): String =
        MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }
}
