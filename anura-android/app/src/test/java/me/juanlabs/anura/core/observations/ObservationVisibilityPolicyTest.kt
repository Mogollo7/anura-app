package me.juanlabs.anura.core.observations

import java.io.File
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ObservationVisibilityPolicyTest {
    private fun local(vis: Visibilidad, sync: EstadoSync = EstadoSync.PendienteSubida, ts: Long = 0, shas: List<String> = emptyList()) =
        ObservacionLocal("o1", vis, sync, shas.mapIndexed { i, s -> FotoLocal(i, "/tmp/$i.jpg", s) }, ts)

    private fun srv(vis: Visibilidad, ts: Long = 0, shas: List<String> = emptyList()) =
        ObservacionServidor("o1", vis, ts, shas.mapIndexed { i, s -> FotoServidor(i, s) })

    @Test fun publicaConfirmada_borraCopiaLocal() =
        assertEquals(AccionSync.BorrarCopiaLocal, ObservationVisibilityPolicy.decidir(
            local(Visibilidad.Publica, shas = listOf("a", "b")), srv(Visibilidad.Publica, shas = listOf("a", "b"))))

    @Test fun publicaSinConfirmar_nuncaBorra() {
        assertEquals(AccionSync.Subir, ObservationVisibilityPolicy.decidir(local(Visibilidad.Publica, shas = listOf("a")), null))
        // el servidor tiene la observación pero le falta una foto, o el sha no coincide
        assertEquals(AccionSync.Subir, ObservationVisibilityPolicy.decidir(
            local(Visibilidad.Publica, shas = listOf("a", "b")), srv(Visibilidad.Publica, shas = listOf("a"))))
        assertEquals(AccionSync.Subir, ObservationVisibilityPolicy.decidir(
            local(Visibilidad.Publica, shas = listOf("a")), srv(Visibilidad.Publica, shas = listOf("otro"))))
    }

    @Test fun privadaQueFaltaEnElTelefono_seDescarga() =
        assertEquals(AccionSync.Descargar, ObservationVisibilityPolicy.decidir(null, srv(Visibilidad.Privada, shas = listOf("a"))))

    @Test fun publicaAjenaAlTelefono_nadaQueHacer() =
        assertEquals(AccionSync.Nada, ObservationVisibilityPolicy.decidir(null, srv(Visibilidad.Publica, shas = listOf("a"))))

    @Test fun privadaYaSincronizada_seConserva() =
        assertEquals(AccionSync.Nada, ObservationVisibilityPolicy.decidir(
            local(Visibilidad.Privada, EstadoSync.Sincronizada, shas = listOf("a")), srv(Visibilidad.Privada, shas = listOf("a"))))

    @Test fun servidorManda_salvoCambioLocalMasReciente() {
        // pública→privada hecho en el servidor (más nuevo): el teléfono baja la copia
        assertEquals(AccionSync.Descargar, ObservationVisibilityPolicy.decidir(
            local(Visibilidad.Publica, EstadoSync.Sincronizada, 1, listOf("a")), srv(Visibilidad.Privada, 5, listOf("a", "b"))))
        // cambio local más reciente que el del servidor: se envía
        assertEquals(AccionSync.EnviarVisibilidad(Visibilidad.Privada), ObservationVisibilityPolicy.decidir(
            local(Visibilidad.Privada, EstadoSync.Sincronizada, 9, listOf("a")), srv(Visibilidad.Publica, 5, listOf("a"))))
    }

    // --- ObservationSync con almacenes en memoria ---
    private class MemLocal(vararg o: ObservacionLocal) : ObservationLocalStore {
        val filas = o.associateBy { it.id }.toMutableMap()
        val borradas = mutableListOf<String>()
        override suspend fun todas() = filas.values.toList()
        override suspend fun obtener(id: String) = filas[id]
        override suspend fun guardar(obs: ObservacionLocal) { filas[obs.id] = obs }
        override suspend fun borrarConArchivos(id: String) { filas.remove(id); borradas += id }
    }

    private class FakeApi(val servidor: Map<String, ObservacionServidor>, val shaFoto: String? = null) : ObservationVisibilityApi {
        override suspend fun cambiarVisibilidad(id: String, visibilidad: Visibilidad, bearer: String) = true
        override suspend fun obtener(id: String, bearer: String) = servidor[id]
        override suspend fun misPrivadas(desde: Long, bearer: String) = servidor.values.filter { it.visibilidad == Visibilidad.Privada }
        override suspend fun descargarFoto(id: String, n: Int, destino: File, bearer: String): String? {
            destino.parentFile?.mkdirs(); destino.writeText("x"); return shaFoto
        }
    }

    @Test fun sync_borraPublicasConfirmadasYBajaPrivadasNuevas() = runBlocking {
        val pub = local(Visibilidad.Publica, shas = listOf("a")).copy(id = "pub")
        val store = MemLocal(pub)
        val api = FakeApi(mapOf(
            "pub" to srv(Visibilidad.Publica, shas = listOf("a")).copy(id = "pub"),
            "priv" to ObservacionServidor("priv", Visibilidad.Privada, 0, listOf(FotoServidor(0, "zz"))),
        ), shaFoto = "zz")
        val dir = java.nio.file.Files.createTempDirectory("obs").toFile()
        val r = ObservationSync(store, api) { File(dir, it) }.reconciliar("tok")
        assertEquals(1, r.borradasLocal); assertEquals(1, r.descargadas); assertEquals(0, r.fallos)
        assertEquals(listOf("pub"), store.borradas)
        assertEquals(EstadoSync.Sincronizada, store.filas["priv"]?.sync)
    }

    @Test fun sync_fotoDescargadaConShaDistinto_noSeGuarda() = runBlocking {
        val store = MemLocal()
        val api = FakeApi(mapOf("p" to ObservacionServidor("p", Visibilidad.Privada, 0, listOf(FotoServidor(0, "esperado")))), shaFoto = "otro")
        val dir = java.nio.file.Files.createTempDirectory("obs").toFile()
        val r = ObservationSync(store, api) { File(dir, it) }.reconciliar("tok")
        assertEquals(1, r.fallos)
        assertTrue(store.filas.isEmpty())
        assertTrue(!File(dir, "p/0.jpg").exists())
    }
}
