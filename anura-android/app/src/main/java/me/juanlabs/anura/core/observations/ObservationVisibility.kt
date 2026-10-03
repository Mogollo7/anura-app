package me.juanlabs.anura.core.observations

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * Regla de producto (ver `PROTOCOLO_ENCODER_Y_OBSERVACIONES.md`, Parte C): lo público vive solo en
 * el servidor y se borra del teléfono; lo privado vive en el servidor y en el teléfono de su dueño.
 */
@Serializable
enum class Visibilidad(val wire: String) {
    @SerialName("publica") Publica("publica"),
    @SerialName("privada") Privada("privada"),
}

enum class EstadoSync {
    /** Creada en el teléfono, aún sin intento de subida. */
    SoloLocal,

    /** En cola para subir. Nunca se borra la copia local en este estado. */
    PendienteSubida,
    Subiendo,

    /** El servidor confirmó los bytes (mismo sha256 por foto). */
    Sincronizada,

    /** Privada que el servidor tiene y este teléfono todavía no. */
    PendienteDescarga,
}

@Serializable
data class FotoLocal(val n: Int, val ruta: String, val sha256: String)

data class ObservacionLocal(
    val id: String,
    val visibilidad: Visibilidad,
    val sync: EstadoSync,
    val fotos: List<FotoLocal>,
    /** Epoch ms del último cambio de visibilidad hecho en este teléfono. */
    val visibilidadCambiadaEn: Long,
)

@Serializable
data class FotoServidor(val n: Int, val sha256: String, val bytes: Long = 0)

/** Lo que el servidor dice de una observación (autoridad en visibilidad y bytes recibidos). */
@Serializable
data class ObservacionServidor(
    val id: String,
    val visibilidad: Visibilidad,
    @SerialName("visibilidad_cambiada_en") val visibilidadCambiadaEn: Long = 0,
    val fotos: List<FotoServidor> = emptyList(),
)

sealed interface AccionSync {
    /** Nada que hacer. */
    data object Nada : AccionSync

    /** El servidor no la tiene completa: subir (o reintentar). La copia local se conserva. */
    data object Subir : AccionSync

    /** Pública y confirmada: borrar fotos y fila locales. */
    data object BorrarCopiaLocal : AccionSync

    /** Privada que falta (o difiere) en el teléfono: bajar y verificar sha256. */
    data object Descargar : AccionSync

    /** El usuario cambió la visibilidad aquí más recientemente que el servidor: enviar el cambio. */
    data class EnviarVisibilidad(val visibilidad: Visibilidad) : AccionSync
}

object ObservationVisibilityPolicy {

    /** Todas las fotos locales están en el servidor con el mismo sha256. */
    fun servidorTieneTodo(local: ObservacionLocal, servidor: ObservacionServidor): Boolean {
        if (local.fotos.isEmpty()) return false
        val porN = servidor.fotos.associate { it.n to it.sha256 }
        return local.fotos.all { porN[it.n] == it.sha256 }
    }

    /** Todas las fotos del servidor están en el teléfono con el mismo sha256. */
    fun localTieneTodo(local: ObservacionLocal, servidor: ObservacionServidor): Boolean {
        if (servidor.fotos.isEmpty()) return false
        val porN = local.fotos.associate { it.n to it.sha256 }
        return servidor.fotos.all { porN[it.n] == it.sha256 }
    }

    /**
     * Decide qué hacer con una observación comparando teléfono y servidor.
     * El servidor manda en la visibilidad, salvo que el cambio local sea más reciente.
     */
    fun decidir(local: ObservacionLocal?, servidor: ObservacionServidor?): AccionSync {
        if (local == null) {
            return when (servidor?.visibilidad) {
                Visibilidad.Privada -> AccionSync.Descargar
                else -> AccionSync.Nada // pública (se ve desde el servidor) o inexistente
            }
        }
        if (servidor == null) return AccionSync.Subir // nunca borrar lo que el servidor no confirmó

        if (local.visibilidad != servidor.visibilidad && local.visibilidadCambiadaEn > servidor.visibilidadCambiadaEn) {
            return AccionSync.EnviarVisibilidad(local.visibilidad)
        }
        return when (servidor.visibilidad) {
            Visibilidad.Publica ->
                if (servidorTieneTodo(local, servidor)) AccionSync.BorrarCopiaLocal else AccionSync.Subir
            Visibilidad.Privada ->
                if (localTieneTodo(local, servidor)) AccionSync.Nada
                else if (local.sync == EstadoSync.PendienteSubida || local.sync == EstadoSync.SoloLocal) AccionSync.Subir
                else AccionSync.Descargar
        }
    }
}
