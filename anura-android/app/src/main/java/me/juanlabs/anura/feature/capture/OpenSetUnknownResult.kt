package me.juanlabs.anura.feature.capture

import androidx.annotation.DrawableRes
import androidx.annotation.StringRes
import kotlin.math.roundToInt
import me.juanlabs.anura.R
import me.juanlabs.anura.core.data.IdentificationCandidate

/**
 * Hasta dónde llegó la evidencia cuando el open-set no confirma especie.
 * [Species] no aplica: si hay especie, el resultado es identificado, no open-set.
 */
enum class OpenSetReachedRank {
    Order,
    Family,
    Genus,
}

data class OpenSetRankLine(
    val value: String,
    val percent: String,
    val confirmed: Boolean,
)

/**
 * Resultado open-set: especie no registrada. Misma pantalla Penpot; el copy y
 * la ficha CTA dependen del rango confirmado (orden, familia o género).
 */
data class OpenSetUnknownResult(
    val reached: OpenSetReachedRank,
    val headline: String,
    /** Ficha a abrir; null cuando no hay ficha real para el rango alcanzado. */
    val taxonId: String?,
    @param:DrawableRes val photoRes: Int,
    /** Foto del usuario; cuando existe tiene prioridad sobre [photoRes]. */
    val photoToken: String? = null,
    @param:StringRes val subtitleRes: Int,
    @param:StringRes val bodyRes: Int,
    val bodyName: String,
    @param:StringRes val sheetActionRes: Int,
    val order: OpenSetRankLine,
    val family: OpenSetRankLine,
    val genus: OpenSetRankLine,
    val species: OpenSetRankLine,
)

/**
 * Resultado real a partir de las candidatas del k-NN: se agregan los votos por familia y por género
 * (el paquete trae ambos por especie) y un rango se confirma si su ganador reúne la mayoría del voto.
 * El orden es siempre Anura: todas las referencias del paquete lo son.
 */
object OpenSetUnknownResults {
    private const val RankMajority = 0.5f

    fun reachedRank(candidates: List<IdentificationCandidate>): OpenSetReachedRank {
        val family = leader(candidates) { it.family }
        val genus = leader(candidates) { it.genus }
        return when {
            family == null || family.second < RankMajority -> OpenSetReachedRank.Order
            genus == null || genus.second < RankMajority -> OpenSetReachedRank.Family
            else -> OpenSetReachedRank.Genus
        }
    }

    fun fromCandidates(candidates: List<IdentificationCandidate>, photoToken: String?): OpenSetUnknownResult {
        val reached = reachedRank(candidates)
        val family = leader(candidates) { it.family }
        val genus = leader(candidates) { it.genus }
        fun line(leader: Pair<String, Float>?, confirmed: Boolean) =
            if (leader != null && confirmed) OpenSetRankLine(leader.first, percent(leader.second), true) else Unconfirmed
        val (headline, subtitle, body, bodyName, sheet) = when (reached) {
            OpenSetReachedRank.Genus -> Headline(
                "${genus!!.first} sp.", R.string.unknown_result_subtitle_genus,
                R.string.unknown_result_body_real_genus, genus.first, R.string.unknown_result_genus_sheet,
            )
            OpenSetReachedRank.Family -> Headline(
                "${family!!.first} sp.", R.string.unknown_result_subtitle_family,
                R.string.unknown_result_body_real_family, family.first, R.string.unknown_result_family_sheet,
            )
            OpenSetReachedRank.Order -> Headline(
                "Anura sp.", R.string.unknown_result_subtitle_order,
                R.string.unknown_result_body_real_order, "Anura", R.string.unknown_result_order_sheet,
            )
        }
        return OpenSetUnknownResult(
            reached = reached,
            headline = headline,
            taxonId = null,
            photoRes = R.drawable.carousel_pristimantis_paisa,
            photoToken = photoToken,
            subtitleRes = subtitle,
            bodyRes = body,
            bodyName = bodyName,
            sheetActionRes = sheet,
            order = OpenSetRankLine("Anura", percent(1f), confirmed = true),
            family = line(family, reached != OpenSetReachedRank.Order),
            genus = line(genus, reached == OpenSetReachedRank.Genus),
            species = Unconfirmed,
        )
    }

    private data class Headline(
        val headline: String,
        @param:StringRes val subtitle: Int,
        @param:StringRes val body: Int,
        val bodyName: String,
        @param:StringRes val sheet: Int,
    )

    private val Unconfirmed = OpenSetRankLine(value = "", percent = "", confirmed = false)

    private fun percent(share: Float) = "${(share * 100).roundToInt()} %"

    private fun leader(
        candidates: List<IdentificationCandidate>,
        key: (IdentificationCandidate) -> String,
    ): Pair<String, Float>? = candidates
        .filter { key(it).isNotBlank() }
        .groupBy(key)
        .mapValues { (_, group) -> group.sumOf { it.share.toDouble() }.toFloat() }
        .maxByOrNull { it.value }
        ?.toPair()
}

object MockOpenSetUnknownResults {

    private val Unconfirmed = OpenSetRankLine(
        value = "",
        percent = "",
        confirmed = false,
    )

    val Genus = OpenSetUnknownResult(
        reached = OpenSetReachedRank.Genus,
        headline = "Pristimantis sp.",
        taxonId = "COL_ANURA_0011",
        photoRes = R.drawable.carousel_pristimantis_paisa,
        subtitleRes = R.string.unknown_result_subtitle_genus,
        bodyRes = R.string.unknown_result_body_genus,
        bodyName = "Pristimantis",
        sheetActionRes = R.string.unknown_result_genus_sheet,
        order = OpenSetRankLine("Anura", "99 %", confirmed = true),
        family = OpenSetRankLine("Strabomantidae", "96 %", confirmed = true),
        genus = OpenSetRankLine("Pristimantis", "88 %", confirmed = true),
        species = Unconfirmed,
    )

    val Family = OpenSetUnknownResult(
        reached = OpenSetReachedRank.Family,
        headline = "Strabomantidae sp.",
        taxonId = "COL_ANURA_0011",
        photoRes = R.drawable.carousel_pristimantis_paisa,
        subtitleRes = R.string.unknown_result_subtitle_family,
        bodyRes = R.string.unknown_result_body_family,
        bodyName = "Strabomantidae",
        sheetActionRes = R.string.unknown_result_family_sheet,
        order = OpenSetRankLine("Anura", "99 %", confirmed = true),
        family = OpenSetRankLine("Strabomantidae", "91 %", confirmed = true),
        genus = Unconfirmed,
        species = Unconfirmed,
    )

    val Order = OpenSetUnknownResult(
        reached = OpenSetReachedRank.Order,
        headline = "Anura sp.",
        taxonId = "COL_ANURA_0011",
        photoRes = R.drawable.carousel_pristimantis_paisa,
        subtitleRes = R.string.unknown_result_subtitle_order,
        bodyRes = R.string.unknown_result_body_order,
        bodyName = "Anura",
        sheetActionRes = R.string.unknown_result_order_sheet,
        order = OpenSetRankLine("Anura", "97 %", confirmed = true),
        family = Unconfirmed,
        genus = Unconfirmed,
        species = Unconfirmed,
    )

    fun forReached(raw: String): OpenSetUnknownResult = when (raw.lowercase()) {
        "order", "orden" -> Order
        "family", "familia" -> Family
        else -> Genus
    }
}
