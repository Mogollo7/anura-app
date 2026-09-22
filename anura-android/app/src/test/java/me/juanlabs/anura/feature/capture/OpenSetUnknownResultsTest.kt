package me.juanlabs.anura.feature.capture

import me.juanlabs.anura.core.data.IdentificationCandidate
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class OpenSetUnknownResultsTest {
    private fun candidate(name: String, share: Float, family: String) =
        IdentificationCandidate(name, share, genus = name.substringBefore(' '), family = family)

    @Test
    fun genusMajority_reachesGenusWithRealShares() {
        val candidates = listOf(
            candidate("Pristimantis paisa", 0.4f, "Strabomantidae"),
            candidate("Pristimantis palmeri", 0.3f, "Strabomantidae"),
            candidate("Boana boans", 0.2f, "Hylidae"),
            candidate("Pristimantis taeniatus", 0.1f, "Strabomantidae"),
        )

        val result = OpenSetUnknownResults.fromCandidates(candidates, photoToken = "file:/x.jpg")

        assertEquals(OpenSetReachedRank.Genus, result.reached)
        assertEquals("Pristimantis sp.", result.headline)
        assertEquals("80 %", result.genus.percent)
        assertEquals("Strabomantidae", result.family.value)
        assertEquals("80 %", result.family.percent)
        assertFalse(result.species.confirmed)
        assertNull("sin ficha real no se ofrece botón de ficha", result.taxonId)
        assertEquals("file:/x.jpg", result.photoToken)
    }

    @Test
    fun familyMajorityWithoutGenusMajority_reachesFamily() {
        val candidates = listOf(
            candidate("Boana platanera", 0.4f, "Hylidae"),
            candidate("Dendropsophus norandinus", 0.3f, "Hylidae"),
            candidate("Scinax ruber", 0.3f, "Hylidae"),
        )

        val result = OpenSetUnknownResults.fromCandidates(candidates, photoToken = null)

        assertEquals(OpenSetReachedRank.Family, result.reached)
        assertEquals("Hylidae sp.", result.headline)
        assertTrue(result.family.confirmed)
        assertFalse(result.genus.confirmed)
    }

    @Test
    fun noFamilyMajority_staysAtOrder() {
        val candidates = listOf(
            candidate("Boana boans", 0.3f, "Hylidae"),
            candidate("Rhinella alata", 0.3f, "Bufonidae"),
            candidate("Pristimantis paisa", 0.2f, "Strabomantidae"),
            candidate("Rheobates palmatus", 0.2f, "Aromobatidae"),
        )

        val result = OpenSetUnknownResults.fromCandidates(candidates, photoToken = null)

        assertEquals(OpenSetReachedRank.Order, result.reached)
        assertEquals("Anura sp.", result.headline)
        assertFalse(result.family.confirmed)
        assertEquals("100 %", result.order.percent)
    }
}
