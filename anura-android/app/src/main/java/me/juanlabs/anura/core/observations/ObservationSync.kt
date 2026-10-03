package me.juanlabs.anura.core.observations

import java.io.File

data class SyncResumen(
    val borradasLocal: Int = 0,
    val descargadas: Int = 0,
    val pendientesSubida: Int = 0,
    val visibilidadEnviada: Int = 0,
    val fallos: Int = 0,
)

/**
 * Reconcilia teléfono y servidor aplicando [ObservationVisibilityPolicy]. Idempotente: se puede
 * volver a correr tras un corte de red o de proceso sin perder ni duplicar fotos.
 *
 * La subida de bytes (`POST /api/observaciones`, ya implementada en `ObservationsRemote`) la hace
 * quien llama con las que salgan en [SyncResumen.pendientesSubida]; aquí solo se decide y se
 * ejecuta lo que no necesita subir archivos.
 */
class ObservationSync(
    private val local: ObservationLocalStore,
    private val api: ObservationVisibilityApi,
    private val carpetaFotos: (id: String) -> File,
) {
    suspend fun reconciliar(bearer: String, privadasDesde: Long = 0): SyncResumen {
        var r = SyncResumen()
        val locales = local.todas().associateBy { it.id }

        // 1) Lo que hay en el teléfono: confirmar contra el servidor.
        for (obs in locales.values) {
            val servidor = api.obtener(obs.id, bearer)
            r = aplicar(obs, servidor, bearer, r)
        }
        // 2) Privadas que el servidor tiene y el teléfono no.
        for (srv in api.misPrivadas(privadasDesde, bearer)) {
            if (srv.id in locales) continue
            r = aplicar(null, srv, bearer, r)
        }
        return r
    }

    private suspend fun aplicar(
        obs: ObservacionLocal?,
        servidor: ObservacionServidor?,
        bearer: String,
        r: SyncResumen,
    ): SyncResumen = when (val accion = ObservationVisibilityPolicy.decidir(obs, servidor)) {
        AccionSync.Nada -> {
            if (obs != null && obs.sync != EstadoSync.Sincronizada && servidor != null) {
                local.guardar(obs.copy(sync = EstadoSync.Sincronizada))
            }
            r
        }
        AccionSync.Subir -> {
            if (obs != null && obs.sync != EstadoSync.PendienteSubida) local.guardar(obs.copy(sync = EstadoSync.PendienteSubida))
            r.copy(pendientesSubida = r.pendientesSubida + 1)
        }
        AccionSync.BorrarCopiaLocal -> {
            // Primero queda marcada como sincronizada; si el proceso muere, la próxima corrida repite el borrado.
            local.guardar(obs!!.copy(sync = EstadoSync.Sincronizada))
            local.borrarConArchivos(obs.id)
            r.copy(borradasLocal = r.borradasLocal + 1)
        }
        is AccionSync.EnviarVisibilidad ->
            if (api.cambiarVisibilidad(obs!!.id, accion.visibilidad, bearer)) r.copy(visibilidadEnviada = r.visibilidadEnviada + 1)
            else r.copy(fallos = r.fallos + 1)
        AccionSync.Descargar -> descargar(obs, servidor!!, bearer, r)
    }

    private suspend fun descargar(
        obs: ObservacionLocal?,
        servidor: ObservacionServidor,
        bearer: String,
        r: SyncResumen,
    ): SyncResumen {
        val carpeta = carpetaFotos(servidor.id)
        val fotos = mutableListOf<FotoLocal>()
        for (foto in servidor.fotos) {
            val destino = File(carpeta, "${foto.n}.jpg")
            val sha = api.descargarFoto(servidor.id, foto.n, destino, bearer)
            if (sha == null || sha != foto.sha256) {
                destino.delete() // nunca se guarda una foto que no coincide con el sha del servidor
                return r.copy(fallos = r.fallos + 1)
            }
            fotos += FotoLocal(foto.n, destino.path, sha)
        }
        local.guardar(
            ObservacionLocal(
                id = servidor.id,
                visibilidad = Visibilidad.Privada,
                sync = EstadoSync.Sincronizada,
                fotos = fotos,
                visibilidadCambiadaEn = maxOf(servidor.visibilidadCambiadaEn, obs?.visibilidadCambiadaEn ?: 0),
            ),
        )
        return r.copy(descargadas = r.descargadas + 1)
    }
}
