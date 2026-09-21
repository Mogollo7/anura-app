package me.juanlabs.anura.feature.capture

import androidx.annotation.DrawableRes
import androidx.annotation.StringRes
import me.juanlabs.anura.R

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
    val taxonId: String,
    @param:DrawableRes val photoRes: Int,
    @param:StringRes val subtitleRes: Int,
    @param:StringRes val bodyRes: Int,
    val bodyName: String,
    @param:StringRes val sheetActionRes: Int,
    val order: OpenSetRankLine,
    val family: OpenSetRankLine,
    val genus: OpenSetRankLine,
    val species: OpenSetRankLine,
)

object MockOpenSetUnknownResults {

    private val Unconfirmed = OpenSetRankLine(
        value = "",
        percent = "",
        confirmed = false,
    )

    val Genus = OpenSetUnknownResult(
        reached = OpenSetReachedRank.Genus,
        headline = "Pristimantis sp.",
        taxonId = "ANU_COL_PRIS_PAI_001",
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
        taxonId = "ANU_COL_PRIS_PAI_001",
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
        taxonId = "ANU_COL_PRIS_PAI_001",
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
