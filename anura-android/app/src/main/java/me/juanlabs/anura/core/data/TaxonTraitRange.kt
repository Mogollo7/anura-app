package me.juanlabs.anura.core.data

import me.juanlabs.anura.designsystem.component.AnuraConservationChipVariant

data class TaxonTraitRange(
    val min: Int,
    val max: Int,
    val maxOpen: Boolean = false,
)

object TaxonTraitRanges {
    private val Severity = listOf(
        AnuraConservationChipVariant.CR,
        AnuraConservationChipVariant.EN,
        AnuraConservationChipVariant.VU,
        AnuraConservationChipVariant.NT,
        AnuraConservationChipVariant.LC,
        AnuraConservationChipVariant.NE,
        AnuraConservationChipVariant.DD,
    )

    fun parse(raw: String): TaxonTraitRange? {
        val plus = raw.contains('+')
        val match = Regex("""(\d+(?:\.\d{3})*)\s*[–\-—]\s*(\d+(?:\.\d{3})*)""").find(raw) ?: return null
        val min = parseThousands(match.groupValues[1]) ?: return null
        val max = parseThousands(match.groupValues[2]) ?: return null
        return TaxonTraitRange(min = min, max = max, maxOpen = plus)
    }

    fun merge(ranges: List<TaxonTraitRange>): TaxonTraitRange? {
        if (ranges.isEmpty()) return null
        return TaxonTraitRange(
            min = ranges.minOf { it.min },
            max = ranges.maxOf { it.max },
            maxOpen = ranges.any { it.maxOpen },
        )
    }

    fun formatAltitude(range: TaxonTraitRange): String =
        "${formatThousands(range.min)}–${formatThousands(range.max)} m"

    fun formatSize(range: TaxonTraitRange): String {
        val max = formatThousands(range.max) + if (range.maxOpen) "+" else ""
        return "${formatThousands(range.min)}–$max mm"
    }

    /** Rango de la ficha publicada (min o max pueden faltar). Mismo formato que el resto: "1.500–2.500 m". */
    fun formatPublished(min: Double?, max: Double?, unit: String): String? {
        val lo = min?.let { formatNumber(it) }
        val hi = max?.let { formatNumber(it) }
        return when {
            lo != null && hi != null -> "$lo–$hi $unit"
            lo != null -> "desde $lo $unit"
            hi != null -> "hasta $hi $unit"
            else -> null
        }
    }

    private fun formatNumber(value: Double): String =
        if (value % 1.0 == 0.0) formatThousands(value.toInt()) else value.toString().replace('.', ',')

    fun worstIucn(statuses: List<AnuraConservationChipVariant>): AnuraConservationChipVariant =
        statuses.minByOrNull { Severity.indexOf(it).takeIf { index -> index >= 0 } ?: Severity.lastIndex }
            ?: AnuraConservationChipVariant.DD

    private fun parseThousands(raw: String): Int? = raw.replace(".", "").toIntOrNull()

    private fun formatThousands(value: Int): String {
        val digits = value.toString()
        val grouped = StringBuilder()
        digits.reversed().forEachIndexed { index, char ->
            if (index > 0 && index % 3 == 0) grouped.append('.')
            grouped.append(char)
        }
        return grouped.reverse().toString()
    }
}
