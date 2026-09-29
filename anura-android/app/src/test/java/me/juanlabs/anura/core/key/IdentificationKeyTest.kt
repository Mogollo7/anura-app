package me.juanlabs.anura.core.key

import org.junit.Assert.assertEquals
import org.junit.Assert.assertThrows
import org.junit.Assert.assertTrue
import org.junit.Test

class IdentificationKeyTest {
    private val altitud = ClaveCaracter(
        id = "altitud",
        tipo = "rango",
        pregunta = "¿A qué altitud la viste?",
        opciones = listOf(
            ClaveOpcion("altitud_0", "Menos de 1.000 m", hasta = 1000.0),
            ClaveOpcion("altitud_1", "1.000 m o más", desde = 1000.0),
        ),
    )
    private val actividad = ClaveCaracter(
        id = "actividad",
        tipo = "categoria",
        pregunta = "¿La viste de día o de noche?",
        opciones = listOf(
            ClaveOpcion("dia", "De día"),
            ClaveOpcion("noche", "De noche"),
        ),
    )
    private val clave = ClaveDocumento(
        caracteres = listOf(altitud, actividad),
        especies = listOf(
            ClaveEspecie(
                taxon_id = "X1",
                nombre_cientifico = "X uno",
                estados = mapOf("altitud" to listOf("altitud_0"), "actividad" to listOf("dia")),
            ),
            ClaveEspecie(
                taxon_id = "X2",
                nombre_cientifico = "X dos",
                estados = mapOf("altitud" to listOf("altitud_1"), "actividad" to listOf("noche")),
            ),
            ClaveEspecie(taxon_id = "X3", nombre_cientifico = "X tres"),
        ),
    )

    @Test
    fun primeraPregunta_esLaDeMayorGanancia_yElEmpateRespetaElOrden() {
        val resolucion = resolver(clave)
        assertTrue(resolucion is ClaveResolucion.Pregunta)
        assertEquals("altitud", (resolucion as ClaveResolucion.Pregunta).siguiente)
        assertEquals(listOf("X1", "X2", "X3"), resolucion.especies)
    }

    @Test
    fun noSe_noDescartaEspecies() {
        val resolucion = resolver(clave, listOf(ClaveRespuesta("altitud", null)))
        assertTrue(resolucion is ClaveResolucion.Pregunta)
        val pregunta = resolucion as ClaveResolucion.Pregunta
        assertEquals("actividad", pregunta.siguiente)
        assertEquals(listOf("X1", "X2", "X3"), pregunta.especies)
    }

    @Test
    fun sinDato_sigueCompatible_yQuedaDespuesDeLaQueCoincidio() {
        val resolucion = resolver(
            clave,
            listOf(
                ClaveRespuesta("altitud", "altitud_1"),
                ClaveRespuesta("actividad", "noche"),
            ),
        )
        assertTrue(resolucion is ClaveResolucion.Varias)
        val varias = resolucion as ClaveResolucion.Varias
        assertEquals(listOf("X2", "X3"), varias.especies)
        assertEquals(true, varias.indistinguibles)
        assertEquals(emptyList<String>(), varias.pendientes)
    }

    @Test
    fun ninguna_cuandoTodasLasQueTienenDatoQuedanFuera() {
        val solo = clave.copy(especies = clave.especies.take(1))
        val resolucion = resolver(solo, listOf(ClaveRespuesta("actividad", "noche")))
        assertEquals(ClaveResolucion.Ninguna, resolucion)
    }

    @Test
    fun una_cuandoSoloQuedaUnaEspecie() {
        val resolucion = resolver(
            clave.copy(especies = clave.especies.take(2)),
            listOf(ClaveRespuesta("altitud", "altitud_0")),
        )
        assertEquals(ClaveResolucion.Una("X1"), resolucion)
    }

    @Test
    fun caracterDesconocido_falla() {
        assertThrows(IllegalArgumentException::class.java) {
            resolver(clave, listOf(ClaveRespuesta("color_ojos", "x")))
        }
    }
}
