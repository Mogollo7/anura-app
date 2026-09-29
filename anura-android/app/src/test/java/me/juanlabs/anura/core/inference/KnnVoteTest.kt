package me.juanlabs.anura.core.inference

import org.junit.Assert.assertEquals
import org.junit.Test

class KnnVoteTest {
    private fun candidate(id: String, share: Double) = Candidate(id, id, share)
    private fun neighbor(id: String, distance: Double) = Neighbor(id, id, distance)

    @Test
    fun candidates_withoutGeoPrior_isPureVisualVote() {
        // A vota más que B (menor distancia = mayor voto): visual puro decide A.
        val neighbors = listOf(neighbor("A", 0.5), neighbor("B", 0.3))

        val result = KnnVote.candidates(neighbors)

        assertEquals("B", result.first().taxonId) // 1-0.3=0.7 > 1-0.5=0.5
        assertEquals(1.0, result.sumOf { it.share }, 1e-9)
    }

    @Test
    fun candidates_withGeoPrior_reweightsAndCanFlipWinner() {
        // Visual puro favorece a B (voto 0.7 vs 0.5), pero la zona favorece fuertemente a A.
        val neighbors = listOf(neighbor("A", 0.5), neighbor("B", 0.3))
        val geoPrior = GeoZonePrior(
            zoneId = "ZONE_TEST",
            weight = 1.0,
            unobservedP = 0.01,
            byTaxon = mapOf("A" to 0.9, "B" to 0.1),
        )

        val result = KnnVote.candidates(neighbors, geoPrior)

        // combinado: A=0.5*0.9=0.45, B=0.7*0.1=0.07 -> A gana ahora
        assertEquals("A", result.first().taxonId)
        assertEquals(1.0, result.sumOf { it.share }, 1e-9)
    }

    @Test
    fun candidates_withWeatherMultiplier_reweightsIndependentlyOfGeo() {
        val neighbors = listOf(neighbor("A", 0.5), neighbor("B", 0.3))
        val clima = mapOf("A" to 2.0, "B" to 0.5) // A favorecido por clima, B penalizado

        val result = KnnVote.candidates(neighbors, weatherMultiplier = clima)

        // combinado: A=0.5*2.0=1.0, B=0.7*0.5=0.35 -> A gana
        assertEquals("A", result.first().taxonId)
        assertEquals(1.0, result.sumOf { it.share }, 1e-9)
    }

    @Test
    fun candidates_taxonWithoutWeatherEntry_staysNeutral() {
        val neighbors = listOf(neighbor("A", 0.5), neighbor("B", 0.3))
        val clima = mapOf("B" to 0.01) // solo B tiene fila; A queda neutro (multiplicador 1)

        val result = KnnVote.candidates(neighbors, weatherMultiplier = clima)

        assertEquals("A", result.first().taxonId) // B penalizado, A sin cambios sigue ganando
    }

    @Test
    fun displayCandidates_keepsWinnerFirstEvenIfNotTopOfBroaderSet() {
        val winner = candidate("A", 0.9)
        // en el k más amplio B superó a A en votos (vecindario distinto) — igual A debe ir primero:
        // es la decisión oficial (k=5), esta lista es solo para mostrar alternativas.
        val broader = listOf(candidate("B", 0.4), candidate("A", 0.3), candidate("C", 0.2), candidate("D", 0.1))

        val result = KnnVote.displayCandidates(winner, broader, count = 4)

        assertEquals(listOf("A", "B", "C", "D"), result.map { it.taxonId })
        // el % mostrado sale de broader para TODAS, incluido el ganador — no del share oficial (0.9) —
        // y ninguna alternativa se muestra por encima del ganador: B (0.4) se limita a 0.3.
        // Suma mostrada: 0.3+0.3+0.2+0.1 = 0.9, nunca pasa de 100%.
        assertEquals(0.3, result.first().share, 0.0)
        assertEquals(0.3, result[1].share, 0.0)
        assertEquals(0.9, result.sumOf { it.share }, 1e-9)
    }

    @Test
    fun displayCandidates_capsAtRequestedCount() {
        val winner = candidate("A", 0.5)
        val broader = listOf(candidate("A", 0.5), candidate("B", 0.2), candidate("C", 0.15), candidate("D", 0.1), candidate("E", 0.05))

        val result = KnnVote.displayCandidates(winner, broader, count = 4)

        assertEquals(4, result.size)
        assertEquals(listOf("A", "B", "C", "D"), result.map { it.taxonId })
    }

    @Test
    fun displayCandidates_fewerThanCountWhenBroaderHasFewSpecies() {
        val winner = candidate("A", 1.0)
        val broader = listOf(candidate("A", 1.0))

        val result = KnnVote.displayCandidates(winner, broader, count = 4)

        assertEquals(listOf("A"), result.map { it.taxonId })
    }
}
