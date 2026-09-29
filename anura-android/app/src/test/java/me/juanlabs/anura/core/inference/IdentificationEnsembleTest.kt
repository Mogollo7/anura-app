package me.juanlabs.anura.core.inference

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class IdentificationEnsembleTest {
    @Test
    fun combine_singleOutcome_returnsSame() {
        val only = identified("A", 0.8, accepted = true)
        assertEquals(only, IdentificationEnsemble.combine(listOf(only)))
    }

    @Test
    fun combine_sameIndividual_averagesVotesAndPicksConsensus() {
        val dorsal = identified("A", 0.55, runnerUp = "B" to 0.45, accepted = true)
        val lateral = identified("A", 0.70, runnerUp = "B" to 0.30, accepted = true)
        val fused = IdentificationEnsemble.combine(listOf(dorsal, lateral)) as IdentificationOutcome.Identified

        assertEquals("A", fused.scientificName)
        assertTrue(fused.accepted)
        assertEquals(0.625, fused.candidates.first().share, 1e-9)
        assertEquals(1.0, fused.candidates.sumOf { it.share }, 1e-9)
    }

    @Test
    fun combine_badAngleNotAnuro_doesNotDiscardGoodViews() {
        val good = identified("A", 0.9, accepted = true)
        val leaf = IdentificationOutcome.NotAnuro(OpenSetScore(60.0, "none", accepted = false))
        val fused = IdentificationEnsemble.combine(listOf(good, leaf)) as IdentificationOutcome.Identified

        assertEquals("A", fused.scientificName)
        assertTrue(fused.accepted)
    }

    @Test
    fun combine_allNotAnuro_staysNotAnuro() {
        val a = IdentificationOutcome.NotAnuro(OpenSetScore(55.0, "x", accepted = false))
        val b = IdentificationOutcome.NotAnuro(OpenSetScore(62.0, "y", accepted = false))
        val fused = IdentificationEnsemble.combine(listOf(a, b))

        assertTrue(fused is IdentificationOutcome.NotAnuro)
        assertEquals(55.0, (fused as IdentificationOutcome.NotAnuro).openSet.mahalanobis, 1e-9)
    }

    private fun identified(
        winner: String,
        share: Double,
        runnerUp: Pair<String, Double>? = null,
        accepted: Boolean,
    ): IdentificationOutcome.Identified {
        val candidates = buildList {
            add(Candidate(winner, winner, share, genus = "G", family = "F"))
            runnerUp?.let { add(Candidate(it.first, it.first, it.second, genus = "G", family = "F")) }
        }
        return IdentificationOutcome.Identified(
            taxonId = winner,
            scientificName = winner,
            accepted = accepted,
            openSet = OpenSetScore(20.0, winner, accepted),
            neighbors = emptyList(),
            candidates = candidates,
        )
    }
}
