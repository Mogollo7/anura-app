package me.juanlabs.anura.core.inference

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class AltitudePriorTest {
    private fun n(taxon: String, name: String, d: Double) = Neighbor(taxon, name, d, name.substringBefore(' '), "Familia")

    // Foto sintética de Dendropsophus bogerti (correcta): 15 vecinos, mezclada con otras especies parecidas.
    private val bogerti = "COL_ANURA_0001"
    private val columbianus = "COL_ANURA_0002"
    private val microcephalus = "COL_ANURA_0003"
    private val truncatus = "COL_ANURA_0004"
    private val neighbors = listOf(
        n(bogerti, "Dendropsophus bogerti", 0.10), n(bogerti, "Dendropsophus bogerti", 0.12),
        n(columbianus, "Dendropsophus columbianus", 0.14), n(bogerti, "Dendropsophus bogerti", 0.15),
        n(microcephalus, "Dendropsophus microcephalus", 0.16),
        // hasta aquí el k=5 oficial; el resto solo alimenta las alternativas mostradas
        n(columbianus, "Dendropsophus columbianus", 0.20), n(bogerti, "Dendropsophus bogerti", 0.22),
        n(microcephalus, "Dendropsophus microcephalus", 0.24), n(columbianus, "Dendropsophus columbianus", 0.25),
        n(truncatus, "Dendrobates truncatus", 0.26), n(columbianus, "Dendropsophus columbianus", 0.28),
        n(microcephalus, "Dendropsophus microcephalus", 0.30), n(truncatus, "Dendrobates truncatus", 0.31),
        n(bogerti, "Dendropsophus bogerti", 0.33), n(columbianus, "Dendropsophus columbianus", 0.35),
    )

    // Rangos de altitud reales de la clave del paquete (texto de `resumen.altitud`) y de la ficha publicada.
    private val ranges = SpeciesAltitudeRanges.build(
        fromPackage = listOf(
            Triple(bogerti, "Dendropsophus bogerti", "1.000–2.000 m"),
            Triple(columbianus, "Dendropsophus columbianus", "0–600 m"),
        ),
        fromCatalog = listOf(
            Triple(microcephalus, "Dendropsophus microcephalus", AltitudeRange(0.0, 900.0)),
            // truncatus: la ficha no trae altitud → sin ajuste
            Triple(truncatus, "Dendrobates truncatus", null),
        ),
    )

    /** Lo que hace `AnuraIdentifier`: ganador oficial con k=5 visual y porcentajes mostrados con k=15 + contexto. */
    private fun shown(altitudeM: Int?, ranges: SpeciesAltitudeRanges?, weather: Map<String, Double>? = null): List<Candidate> {
        val top = KnnVote.candidates(neighbors.take(5)).first()
        val context = AltitudePrior.combine(weather, AltitudePrior.multipliers(altitudeM?.toDouble(), neighbors, ranges))
        return KnnVote.displayCandidates(top, KnnVote.candidates(neighbors, null, context), 4)
    }

    @Test
    fun sinAltitud_elResultadoEsIdenticoAlDeAntes() {
        val antes = KnnVote.displayCandidates(
            KnnVote.candidates(neighbors.take(5)).first(),
            KnnVote.candidates(neighbors, null, null),
            4,
        )
        assertEquals(antes, shown(null, ranges))
        assertEquals(antes, shown(1500, null))
        assertEquals(antes, shown(1500, SpeciesAltitudeRanges.Empty))
    }

    @Test
    fun sinAltitud_yConClima_elClimaSigueIgual() {
        val clima = mapOf(bogerti to 1.2, columbianus to 0.7)
        val antes = KnnVote.displayCandidates(
            KnnVote.candidates(neighbors.take(5)).first(),
            KnnVote.candidates(neighbors, null, clima),
            4,
        )
        assertEquals(antes, shown(null, ranges, clima))
    }

    @Test
    fun conAltitud_laEspecieCorrectaRecuperaSuValor_yLasOtrasSiguenAhi() {
        val antes = shown(null, ranges)
        val ahora = shown(1500, ranges)

        val antesBogerti = antes.first { it.taxonId == bogerti }.share
        val ahoraBogerti = ahora.first { it.taxonId == bogerti }.share
        println("bogerti sin altitud=%.3f con 1500 m=%.3f".format(antesBogerti, ahoraBogerti))
        println("candidatas sin altitud: " + antes.joinToString { "%s %.3f".format(it.scientificName, it.share) })
        println("candidatas con 1500 m: " + ahora.joinToString { "%s %.3f".format(it.scientificName, it.share) })
        assertTrue("bogerti debe subir: $antesBogerti -> $ahoraBogerti", ahoraBogerti > antesBogerti + 0.05)

        // la especie de tierras bajas cae, pero sigue apareciendo entre las alternativas
        val antesCol = antes.first { it.taxonId == columbianus }.share
        val ahoraCol = ahora.first { it.taxonId == columbianus }.share
        assertTrue(ahoraCol < antesCol)

        // otras candidatas: mismas 4 especies, ganador primero, todas con porcentaje, suma <= 100 %
        assertEquals(4, ahora.size)
        assertEquals(bogerti, ahora.first().taxonId)
        assertEquals(antes.map { it.taxonId }.toSet(), ahora.map { it.taxonId }.toSet())
        assertTrue(ahora.drop(1).all { it.share > 0.0 })
        assertTrue(ahora.sumOf { it.share } <= 1.0 + 1e-9)
    }

    @Test
    fun laAltitudNoCambiaLaEspecieOficial() {
        // aunque el punto este muy lejos del rango del ganador, el ganador es el del voto visual
        val top = KnnVote.candidates(neighbors.take(5)).first()
        val ahora = shown(5, ranges)
        assertEquals(top.taxonId, ahora.first().taxonId)
        assertTrue(ahora.first().share >= ahora.drop(1).maxOf { it.share })
    }

    @Test
    fun factor_dentroDelRangoYTolerancia_esNeutro_yFueraCaeConPiso() {
        val r = AltitudeRange(1000.0, 2000.0)
        assertEquals(1.0, AltitudePrior.factor(1500.0, r), 0.0)
        assertEquals(1.0, AltitudePrior.factor(900.0, r), 0.0) // 100 m fuera = holgura
        assertTrue(AltitudePrior.factor(700.0, r) < 1.0)
        assertTrue(AltitudePrior.factor(700.0, r) > AltitudePrior.factor(300.0, r))
        assertEquals(AltitudePrior.Floor, AltitudePrior.factor(-3000.0, r), 0.0)
        assertEquals(1.0, AltitudePrior.factor(5000.0, AltitudeRange(1000.0, null)), 0.0) // rango abierto
    }

    @Test
    fun parseRange_entiendeLoQueEscribeElServidorYLaFicha() {
        assertEquals(AltitudeRange(1500.0, 2500.0), AltitudePrior.parseRange("1.500–2.500 m"))
        assertEquals(AltitudeRange(0.0, 600.0), AltitudePrior.parseRange("0–600 m"))
        assertEquals(AltitudeRange(1200.0, null), AltitudePrior.parseRange("Desde 1.200 m"))
        assertEquals(AltitudeRange(null, 800.0), AltitudePrior.parseRange("hasta 800 m"))
        assertEquals(AltitudeRange(500.5, 1200.0), AltitudePrior.parseRange("500,5–1.200 m"))
        assertNull(AltitudePrior.parseRange("Sin datos"))
        assertNull(AltitudePrior.parseRange(""))
    }

    @Test
    fun rangos_elPaqueteGana_elCatalogoCompleta_yEsSinDatoSiNoHay() {
        val r = SpeciesAltitudeRanges.build(
            fromPackage = listOf(Triple("A", "Especie a", "1.000–2.000 m"), Triple("B", "Especie b", null)),
            fromCatalog = listOf(
                Triple("A", "Especie a", AltitudeRange(0.0, 100.0)), // pierde contra el paquete
                Triple("B", "Especie b", AltitudeRange(300.0, 400.0)), // el paquete no la trae
                Triple("C", "Especie c", null),
            ),
        )
        assertEquals(AltitudeRange(1000.0, 2000.0), r.find("A", "x"))
        assertEquals(AltitudeRange(300.0, 400.0), r.find("B", "x"))
        assertNull(r.find("C", "Especie c"))
        // el paquete usa otro id: se encuentra por nombre cientifico
        assertNotNull(r.find("OTRO_ID", "Especie_A"))
        assertEquals(2, r.size)
    }

    @Test
    fun multipliers_nullSinAltitudOSinRangoAplicable() {
        assertNull(AltitudePrior.multipliers(null, neighbors, ranges))
        assertNull(AltitudePrior.multipliers(1500.0, neighbors, null))
        assertNull(AltitudePrior.multipliers(1500.0, neighbors, SpeciesAltitudeRanges.Empty))
        val m = AltitudePrior.multipliers(1500.0, neighbors, ranges)!!
        assertEquals(1.0, m.getValue(bogerti), 0.0)
        assertTrue(m.getValue(columbianus) < 1.0)
        assertTrue(truncatus !in m) // sin dato = sin ajuste
    }
}
