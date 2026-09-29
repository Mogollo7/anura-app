package me.juanlabs.anura.feature.comments

import me.juanlabs.anura.R
import me.juanlabs.anura.core.data.SpeciesCatalog

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
    /** Foto publicada de la especie (sha256); null = sin foto, se ve un hueco neutro. */
    val photoSha256: String?,
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

/** Especies publicadas (catálogo del servidor). Sin catálogo, no hay a quién mencionar: la lista queda vacía. */
internal val CommentTaxonCatalog: List<TaxonSuggestion>
    get() = SpeciesCatalog.all.map { species ->
        TaxonSuggestion(
            id = species.id,
            scientificName = species.scientificName,
            commonName = species.commonName,
            rank = TaxonRank.Species,
            photoSha256 = species.photoSha256,
        )
    }

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
