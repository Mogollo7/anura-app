package me.juanlabs.anura.core.data

import java.time.Instant
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString

/**
 * Comentarios reales de `observation-service` (fase 14) — antes vivían solo como
 * `AnuraSnapshot.comments` local, sin backend en ningún lado (ni la app ni la web). Mismo
 * contrato que ya usa la web (`store/commentsStore.js`, migrado a esto en el mismo cambio).
 */
object CommentsRemote {
    suspend fun list(observationId: String): List<CommentDto> =
        AnuraApi.get<List<CommentDto>>("/api/observations/$observationId/comments").orEmpty()

    suspend fun post(
        observationId: String,
        body: String,
        stance: String,
        parentId: String?,
        taxonProposalScientificName: String?,
        taxonProposalCommonName: String?,
        bearer: String,
    ): CommentDto? {
        val payload = NewCommentBody(
            body = body,
            stance = stance,
            parentId = parentId,
            taxonProposal = taxonProposalScientificName?.let {
                TaxonProposalBody(scientificName = it, commonName = taxonProposalCommonName)
            },
        )
        val json = AnuraApi.json.encodeToString(NewCommentBody.serializer(), payload)
        return AnuraApi.post<CommentDto>("/api/observations/$observationId/comments", json, bearer)
    }
}

@Serializable
data class TaxonProposalBody(val scientificName: String, val commonName: String? = null)

@Serializable
data class NewCommentBody(
    val body: String,
    val stance: String = "neutral",
    val parentId: String? = null,
    val taxonProposal: TaxonProposalBody? = null,
)

/** `GET/POST /api/observations/:id/comments`. */
@Serializable
data class CommentDto(
    val id: String,
    val observation_id: String,
    val parent_id: String? = null,
    val body: String,
    val stance: String = "neutral",
    val taxon_proposal_scientific_name: String? = null,
    val taxon_proposal_common_name: String? = null,
    val created_at: String? = null,
    val author_id: String,
    val author_username: String,
    val author_profile_image: String? = null,
) {
    fun toCommentRecord(observationId: String): CommentRecord {
        val epochMs = created_at?.let { runCatching { Instant.parse(it).toEpochMilli() }.getOrNull() } ?: 0L
        return CommentRecord(
            id = id,
            observationId = observationId,
            authorUserId = author_id,
            authorName = author_username,
            body = body,
            createdAtEpochMs = epochMs,
            parentId = parent_id,
            stance = stance,
            taxonProposalScientificName = taxon_proposal_scientific_name,
            taxonProposalCommonName = taxon_proposal_common_name,
        )
    }
}
