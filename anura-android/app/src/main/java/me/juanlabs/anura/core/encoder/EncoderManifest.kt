package me.juanlabs.anura.core.encoder

import kotlinx.serialization.Serializable

/**
 * Manifiesto público `GET /api/dataset/publico/encoder` (esquema 1). No va firmado: la garantía
 * es el sha256 del archivo, que [EncoderDownloader] verifica siempre.
 */
@Serializable
data class EncoderManifest(
    val esquema: Int = 0,
    val activo: EncoderInfo? = null,
    val modelos: List<EncoderInfo> = emptyList(),
) {
    /** Modelos descargables y compatibles con este contrato, con el activo primero. */
    fun usables(): List<EncoderInfo> {
        if (esquema != EncoderContract.Esquema) return emptyList()
        return (listOfNotNull(activo) + modelos).filter { it.esCompatible() }.distinctBy { it.sha256 }
    }

    fun buscar(sha256: String): EncoderInfo? = usables().firstOrNull { it.sha256 == sha256.lowercase() }

    /** El activo, solo si es compatible (regla 6: si no, se conserva el modelo actual). */
    fun activoUsable(): EncoderInfo? = activo?.takeIf { esquema == EncoderContract.Esquema && it.esCompatible() }
}

@Serializable
data class EncoderInfo(
    val sha256: String,
    val nombre: String = "",
    val archivo: String = "",
    val dimension: Int = 0,
    val preprocesado: String = "",
    val normalizacion: String = "",
    val bytes: Long = 0,
    val url: String = "",
) {
    fun esCompatible(): Boolean =
        EncoderContract.esSha256(sha256) && dimension == EncoderContract.Dimension && bytes > 0 && url.startsWith("/")
}

object EncoderContract {
    const val Esquema = 1
    const val Dimension = 512
    const val ManifestPath = "/api/dataset/publico/encoder"

    /** sha256 del encoder que viene empaquetado en el APK (respaldo inicial). */
    const val ShaEmpaquetado = "219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad"

    private val Sha = Regex("^[0-9a-f]{64}$")

    /** Solo minúsculas: el sha se usa como nombre de carpeta, así que no admite nada más. */
    fun esSha256(valor: String?): Boolean = valor != null && Sha.matches(valor)
}
