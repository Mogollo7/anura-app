package me.juanlabs.anura.core.data

import android.util.Base64
import net.i2p.crypto.eddsa.EdDSAEngine
import net.i2p.crypto.eddsa.EdDSAPublicKey
import net.i2p.crypto.eddsa.spec.EdDSANamedCurveTable
import net.i2p.crypto.eddsa.spec.EdDSAPublicKeySpec
import java.security.MessageDigest

/**
 * Verifica la firma Ed25519 del manifiesto del catálogo de contenido (K2: manifest + sha256 +
 * firma, mismo mecanismo que usará C1 para los paquetes). Solo verifica — la app nunca firma
 * nada, solo el servidor puede.
 *
 * La clave pública está embebida aquí a propósito, no se pide al servidor: si viajara por el
 * mismo canal que firma el contenido, quien controlara ese canal podría cambiar el catálogo y
 * la clave a la vez, y la firma dejaría de proteger nada (mismo principio que el sha256 del
 * encoder en `CONTRATO`, services/ai-service/app/worker/embeddings.py). Es la mitad pública de
 * la clave que solo vive en `CONTENT_MANIFEST_PRIVATE_KEY_B64` en el .env del servidor — ver
 * services/dataset-service/src/manifiesto.js. Rotarla exige publicar una versión nueva de la
 * app (y de la web, que tiene su copia en `frontend/src/species/publishedCatalog.js`).
 */
private const val CONTENT_PUBLIC_KEY_B64 = "IVPJ+qhfUUcbwK8T7Z0V+L5uZCwjjeg9PU/QIuL1NNY="

object ContentManifestVerifier {
    private val curva by lazy { EdDSANamedCurveTable.getByName("Ed25519") }
    private val clavePublica: EdDSAPublicKey by lazy {
        val bytes = Base64.decode(CONTENT_PUBLIC_KEY_B64, Base64.DEFAULT)
        EdDSAPublicKey(EdDSAPublicKeySpec(bytes, curva))
    }

    /** true solo si `firmaB64` es una firma Ed25519 válida de `mensaje` con la clave del canal. */
    fun verificar(mensaje: ByteArray, firmaB64: String?): Boolean {
        if (firmaB64.isNullOrBlank()) return false
        return runCatching {
            val firma = Base64.decode(firmaB64, Base64.DEFAULT)
            val motor = EdDSAEngine(MessageDigest.getInstance(curva.hashAlgorithm))
            motor.initVerify(clavePublica)
            motor.update(mensaje)
            motor.verify(firma)
        }.getOrDefault(false)
    }
}
