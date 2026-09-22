package me.juanlabs.anura.core.inference

import org.junit.Assert.assertEquals
import org.junit.Test

class KnnVoteTest {
    private fun candidate(id: String, share: Double) = Candidate(id, id, share)

    @Test
    fun displayCandidates_keepsWinnerFirstEvenIfNotTopOfBroaderSet() {
        val winner = candidate("A", 0.9)
        // en el k más amplio B superó a A en votos (vecindario distinto) — igual A debe ir primero:
        // es la decisión oficial (k=5), esta lista es solo para mostrar alternativas.
        val broader = listOf(candidate("B", 0.4), candidate("A", 0.3), candidate("C", 0.2), candidate("D", 0.1))

        val result = KnnVote.displayCandidates(winner, broader, count = 4)

        assertEquals(listOf("A", "B", "C", "D"), result.map { it.taxonId })
        // el % mostrado sale de broader para TODAS, incluido el ganador — no del share oficial (0.9) —
        // para que la suma de los % mostrados nunca pase de 100%: 0.3+0.4+0.2+0.1=1.0.
        assertEquals(0.3, result.first().share, 0.0)
        assertEquals(1.0, result.sumOf { it.share }, 1e-9)
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
