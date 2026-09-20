package me.juanlabs.anura.feature.comments

import androidx.annotation.DrawableRes
import me.juanlabs.anura.R

internal enum class CommentStance {
    Agree,
    Disagree,
    Neutral,
}

internal enum class TaxonRank {
    Species,
    Genus,
    Family,
}

internal data class TaxonSuggestion(
    val id: String,
    val scientificName: String,
    val commonName: String,
    val rank: TaxonRank,
    @param:DrawableRes val photoRes: Int,
)

internal data class TaxonProposal(
    val taxon: TaxonSuggestion,
    val statusRes: Int = R.string.comments_proposal_status,
)

internal data class ObservationComment(
    val id: String,
    val username: String,
    val body: String,
    val stance: CommentStance,
    val own: Boolean = false,
    val proposal: TaxonProposal? = null,
    val replies: List<ObservationComment> = emptyList(),
)

internal val CommentTaxonCatalog: List<TaxonSuggestion> = listOf(
    TaxonSuggestion(
        id = "sp-auratus",
        scientificName = "Dendrobates auratus",
        commonName = "Rana flecha verde y negra",
        rank = TaxonRank.Species,
        photoRes = R.drawable.carousel_dendrobates_truncatus,
    ),
    TaxonSuggestion(
        id = "sp-truncatus",
        scientificName = "Dendrobates truncatus",
        commonName = "Rana venenosa de bandas",
        rank = TaxonRank.Species,
        photoRes = R.drawable.carousel_dendrobates_truncatus,
    ),
    TaxonSuggestion(
        id = "sp-paisa",
        scientificName = "Pristimantis paisa",
        commonName = "Rana paisa",
        rank = TaxonRank.Species,
        photoRes = R.drawable.carousel_pristimantis_paisa,
    ),
    TaxonSuggestion(
        id = "sp-bogerti",
        scientificName = "Dendropsophus bogerti",
        commonName = "Ranita de Bogert",
        rank = TaxonRank.Species,
        photoRes = R.drawable.carousel_dendropsophus_bogerti,
    ),
    TaxonSuggestion(
        id = "gn-dendrobates",
        scientificName = "Dendrobates",
        commonName = "Ranas flecha",
        rank = TaxonRank.Genus,
        photoRes = R.drawable.carousel_dendrobates_truncatus,
    ),
    TaxonSuggestion(
        id = "gn-pristimantis",
        scientificName = "Pristimantis",
        commonName = "Pristimantis",
        rank = TaxonRank.Genus,
        photoRes = R.drawable.carousel_pristimantis_paisa,
    ),
    TaxonSuggestion(
        id = "fm-dendrobatidae",
        scientificName = "Dendrobatidae",
        commonName = "Ranas venenosas",
        rank = TaxonRank.Family,
        photoRes = R.drawable.carousel_dendrobates_truncatus,
    ),
    TaxonSuggestion(
        id = "fm-hylidae",
        scientificName = "Hylidae",
        commonName = "Ranas arborícolas",
        rank = TaxonRank.Family,
        photoRes = R.drawable.carousel_dendropsophus_bogerti,
    ),
)

internal fun mockObservationComments(): List<ObservationComment> = listOf(
    ObservationComment(
        id = "c1",
        username = "@juanma.herpeto",
        body = "Bandas dorsales amarillo-verdosas: encaja con truncatus. De acuerdo.",
        stance = CommentStance.Agree,
        replies = listOf(
            ObservationComment(
                id = "c1r1",
                username = "@laura.anura",
                body = "Sí, y el patrón inguinal también cierra.",
                stance = CommentStance.Agree,
            ),
        ),
    ),
    ObservationComment(
        id = "c2",
        username = "@laura.anura",
        body = "A 2.100 m truncatus es muy raro. ¿Confirmás la elevación del registro?",
        stance = CommentStance.Neutral,
    ),
    ObservationComment(
        id = "c3",
        username = "@c.villamil.bio",
        body = "Vientre más reticulado de lo normal, pero puede ser un juvenil.",
        stance = CommentStance.Agree,
    ),
    ObservationComment(
        id = "c4",
        username = "@santiago.rn",
        body = "La foto no deja ver la mancha inguinal, que es el carácter clave.",
        stance = CommentStance.Neutral,
    ),
    ObservationComment(
        id = "c5",
        username = "@m.restrepo",
        body = "Anillo dorsal continuo y verde metálico: yo veo auratus, no truncatus.",
        stance = CommentStance.Disagree,
        proposal = TaxonProposal(
            taxon = CommentTaxonCatalog.first { it.id == "sp-auratus" },
        ),
        replies = listOf(
            ObservationComment(
                id = "c5r1",
                username = "@juanma.herpeto",
                body = "El anillo se ve continuo por el ángulo de la foto, no por el patrón.",
                stance = CommentStance.Agree,
            ),
            ObservationComment(
                id = "c5r2",
                username = "@vale.anuros",
                body = "Si hay otra foto del dorso cerrado, se sale la duda.",
                stance = CommentStance.Neutral,
            ),
        ),
    ),
)

internal fun mentionQuery(text: String): String? {
    val at = text.lastIndexOf('@')
    if (at < 0) return null
    if (at > 0 && !text[at - 1].isWhitespace()) return null
    val raw = text.substring(at + 1)
    if (raw.contains('\n')) return null
    return raw
}

internal fun filterTaxa(query: String): List<TaxonSuggestion> {
    val q = query.trim().lowercase()
    if (q.isEmpty()) return CommentTaxonCatalog.take(5)
    return CommentTaxonCatalog.filter { taxon ->
        taxon.scientificName.lowercase().contains(q) ||
            taxon.commonName.lowercase().contains(q) ||
            taxon.rank.name.lowercase().contains(q)
    }
}

internal fun insertTaxonMention(text: String, taxon: TaxonSuggestion): String {
    val at = text.lastIndexOf('@')
    val prefix = if (at >= 0) text.substring(0, at) else text
    return prefix + "@${taxon.scientificName} "
}
