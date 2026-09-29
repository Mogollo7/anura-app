package me.juanlabs.anura.core.key

import me.juanlabs.anura.core.data.HabitatWaterBody
import me.juanlabs.anura.core.data.PeriodDawn
import me.juanlabs.anura.core.data.PeriodNight
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class ClavePrefillTest {
    private val altitud = ClaveCaracter(
        id = "altitud",
        tipo = "rango",
        opciones = listOf(
            ClaveOpcion("altitud_0", "Menos de 1.000 m", hasta = 1000.0),
            ClaveOpcion("altitud_1", "De 1.000 a 2.000 m", desde = 1000.0, hasta = 2000.0),
            ClaveOpcion("altitud_2", "2.000 m o más", desde = 2000.0),
        ),
    )
    private val tamano = ClaveCaracter(
        id = "tamano",
        tipo = "rango",
        opciones = listOf(
            ClaveOpcion("tamano_0", "Menos de 40 mm", hasta = 40.0),
            ClaveOpcion("tamano_1", "40 mm o más", desde = 40.0),
        ),
    )
    private val sustrato = ClaveCaracter(
        id = "sustrato",
        tipo = "categoria",
        opciones = listOf(ClaveOpcion("hojarasca", "Hojarasca"), ClaveOpcion("quebrada", "Quebrada / agua")),
    )
    private val actividad = ClaveCaracter(
        id = "actividad",
        tipo = "categoria",
        opciones = listOf(ClaveOpcion("dia", "De día"), ClaveOpcion("noche", "De noche")),
    )
    private val clave = ClaveDocumento(
        caracteres = listOf(altitud, tamano, sustrato, actividad),
        especies = listOf(
            ClaveEspecie("A", estados = mapOf("tamano" to listOf("tamano_0"), "altitud" to listOf("altitud_0"))),
            ClaveEspecie("B", estados = mapOf("tamano" to listOf("tamano_1"), "altitud" to listOf("altitud_1"))),
            ClaveEspecie("C", estados = mapOf("tamano" to listOf("tamano_0", "tamano_1"))),
            ClaveEspecie("D"),
        ),
    )

    @Test
    fun bandaDe_incluyeDesde_yExcluyeHasta() {
        assertEquals("altitud_0", bandaDe(altitud, 999.0))
        assertEquals("altitud_1", bandaDe(altitud, 1000.0))
        assertEquals("altitud_1", bandaDe(altitud, 1999.0))
        assertEquals("altitud_2", bandaDe(altitud, 2000.0))
    }

    @Test
    fun bandaDe_categoriaNoTieneBanda() {
        assertNull(bandaDe(sustrato, 10.0))
    }

    @Test
    fun respuestasPrevias_soloConLoQueSeCapturo() {
        assertEquals(emptyList<ClaveRespuesta>(), respuestasPrevias(clave, ClaveDatos()))
        val previas = respuestasPrevias(
            clave,
            ClaveDatos(altitudM = 1500, tamanoMm = 48, habitat = HabitatWaterBody, periodo = PeriodNight),
        )
        assertEquals(
            listOf(
                ClaveRespuesta("altitud", "altitud_1"),
                ClaveRespuesta("tamano", "tamano_1"),
                ClaveRespuesta("sustrato", "quebrada"),
                ClaveRespuesta("actividad", "noche"),
            ),
            previas,
        )
    }

    @Test
    fun respuestasPrevias_amanecerNoDecideActividad_yCaracteresAusentesSeIgnoran() {
        val sinTamano = clave.copy(caracteres = listOf(altitud, actividad))
        val previas = respuestasPrevias(sinTamano, ClaveDatos(altitudM = 500, tamanoMm = 30, periodo = PeriodDawn))
        assertEquals(listOf(ClaveRespuesta("altitud", "altitud_0")), previas)
    }

    @Test
    fun especiesCompatiblesConValor_cuentaSoloLasQueTienenDato() {
        // A y C entran en la banda de menos de 40 mm; D no tiene dato y no se cuenta
        assertEquals(2, especiesCompatiblesConValor(clave, "tamano", 30.0))
        assertEquals(2, especiesCompatiblesConValor(clave, "tamano", 48.0))
        assertEquals(3, especiesConDato(clave, "tamano"))
    }

    @Test
    fun especiesCompatiblesConValor_sinDatosNoHayCifra() {
        assertNull(especiesCompatiblesConValor(clave, "sustrato", 1.0))
        val sinTamanos = clave.copy(especies = clave.especies.map { it.copy(estados = emptyMap()) })
        assertNull(especiesCompatiblesConValor(sinTamanos, "tamano", 30.0))
        assertNull(especiesCompatiblesConValor(clave.copy(caracteres = listOf(altitud)), "tamano", 30.0))
    }

    @Test
    fun especiesQueQuedan_cuentaLaResolucion() {
        assertEquals(4, especiesQueQuedan(clave, emptyList()))
        assertEquals(3, especiesQueQuedan(clave, listOf(ClaveRespuesta("tamano", "tamano_0"))))
        assertNull(especiesQueQuedan(clave, listOf(ClaveRespuesta("no_existe", "x"))))
    }

    @Test
    fun codificar_esReversible() {
        val respuestas = listOf(ClaveRespuesta("altitud", "altitud_1"), ClaveRespuesta("tamano", null))
        assertEquals(respuestas, decodificarRespuestas(codificarRespuestas(respuestas)))
        assertEquals(emptyList<ClaveRespuesta>(), decodificarRespuestas(null))
    }
}
