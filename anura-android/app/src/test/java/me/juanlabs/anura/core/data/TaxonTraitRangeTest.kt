package me.juanlabs.anura.core.data

import me.juanlabs.anura.designsystem.component.AnuraConservationChipVariant
import org.junit.Assert.assertEquals
import org.junit.Test

class TaxonTraitRangeTest {
    @Test
    fun parse_thousandsAndOpenMax() {
        val altitude = TaxonTraitRanges.parse("0–1.000 m")
        assertEquals(0, altitude?.min)
        assertEquals(1000, altitude?.max)
        val size = TaxonTraitRanges.parse("90–150+ mm")
        assertEquals(90, size?.min)
        assertEquals(150, size?.max)
        assertEquals(true, size?.maxOpen)
    }

    @Test
    fun merge_familyAndGenusSpansUnion() {
        val merged = TaxonTraitRanges.merge(
            listOf(
                TaxonTraitRange(2400, 3000),
                TaxonTraitRange(0, 1200),
                TaxonTraitRange(1400, 2000),
            ),
        )
        assertEquals(0, merged?.min)
        assertEquals(3000, merged?.max)
        assertEquals("0–3.000 m", TaxonTraitRanges.formatAltitude(merged!!))
    }

    @Test
    fun worstIucn_prefersVulnerableOverLeastConcern() {
        assertEquals(
            AnuraConservationChipVariant.VU,
            TaxonTraitRanges.worstIucn(
                listOf(AnuraConservationChipVariant.LC, AnuraConservationChipVariant.VU),
            ),
        )
    }
}
