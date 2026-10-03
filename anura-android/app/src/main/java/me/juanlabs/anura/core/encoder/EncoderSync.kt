package me.juanlabs.anura.core.encoder

import java.io.File
import me.juanlabs.anura.core.data.AnuraApi

/**
 * Orquesta el protocolo del encoder en la app (reglas 2, 4 y 5). Consultar solo al abrir la app y
 * antes de bajar o actualizar un paquete, con Wi-Fi: lo decide quien llama; aquí, si la red falla,
 * simplemente no cambia nada.
 */
class EncoderSync(
    private val store: EncoderStore,
    private val downloader: EncoderDownloader,
    private val manifiesto: suspend () -> EncoderManifest? = { AnuraApi.get<EncoderManifest>(EncoderContract.ManifestPath) },
) {
    /**
     * Baja el encoder activo en segundo plano si falta y, cuando todos los paquetes instalados ya
     * son del sha activo, borra los modelos que ningún paquete usa. [shasPaquetes] = sha de
     * encoder de cada paquete instalado.
     */
    suspend fun sincronizar(shasPaquetes: Set<String>, onProgreso: (Float) -> Unit = {}): EncoderDownloadResult? {
        val activo = manifiesto()?.activoUsable() ?: return null // sin red o contrato distinto: se conserva lo actual
        val resultado = downloader.descargar(activo, onProgreso)
        val todosNuevos = shasPaquetes.isNotEmpty() && shasPaquetes.all { it == activo.sha256 }
        if (todosNuevos && store.tiene(activo.sha256)) {
            store.limpiar(enUso = shasPaquetes, protegidos = setOf(activo.sha256))
        }
        return resultado
    }

    /**
     * Regla 4: antes de instalar un paquete cuyo encoder es [sha256], asegura que el modelo esté
     * disponible. `false` = no instalar el paquete y avisar «actualiza la app».
     */
    suspend fun asegurarModelo(sha256: String, onProgreso: (Float) -> Unit = {}): Boolean {
        if (sha256 == EncoderContract.ShaEmpaquetado || store.tiene(sha256)) return true
        val info = manifiesto()?.buscar(sha256) ?: return false
        return when (downloader.descargar(info, onProgreso)) {
            is EncoderDownloadResult.Instalado, EncoderDownloadResult.YaEstaba -> true
            else -> false
        }
    }
}

/** Qué modelo usar para un paquete (regla 4). Nunca mezcla encoders. */
sealed interface EncoderResolucion {
    /** El que viene en el APK. */
    data object Empaquetado : EncoderResolucion
    data class Descargado(val archivo: File) : EncoderResolucion

    /** Ni empaquetado ni descargado: no usar el paquete hasta bajarlo. */
    data class NoDisponible(val sha256: String) : EncoderResolucion
}

class EncoderResolver(private val store: EncoderStore) {
    /** [sha256] null = paquete antiguo sin dato: se asume el empaquetado. */
    fun resolver(sha256: String?): EncoderResolucion = when {
        sha256 == null || sha256 == EncoderContract.ShaEmpaquetado -> EncoderResolucion.Empaquetado
        !EncoderContract.esSha256(sha256) -> EncoderResolucion.NoDisponible(sha256)
        store.tiene(sha256) -> EncoderResolucion.Descargado(store.archivo(sha256))
        else -> EncoderResolucion.NoDisponible(sha256)
    }
}
