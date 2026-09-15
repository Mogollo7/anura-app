package com.anura.merlin.identification

/** Stable input contract. imageUri must be a URI readable by the caller's ContentResolver. */
data class IdentificationRequest(
    val observationId: String,
    val imageUri: String,
    val latitude: Double? = null,
    val longitude: Double? = null,
    val isAnuran: Boolean? = null,
    val anuranEvidence: Map<String, String> = emptyMap(),
)

enum class IdentificationDecision { ESPECIE_CONOCIDA, NO_CONCLUYENTE, NO_REGISTRADA }

data class IdentificationCandidate(
    val rank: Int,
    val speciesId: String,
    val scientificName: String,
    val commonName: String?,
    val genus: String?,
    val family: String?,
    /** Similarity, not a probability. */ val visualScore: Double,
    /** Geographic context score, not a probability. */ val geographicScore: Double?,
    /** Experimental score, not a probability. */ val rankingScore: Double,
    val geographicContextAvailable: Boolean,
)

data class IdentificationResult(
    val observationId: String,
    val inputMetadata: Map<String, Any?>,
    val isAnuran: Boolean?,
    val anuranEvidence: Map<String, String>,
    val candidates: List<IdentificationCandidate>,
    val decision: IdentificationDecision,
    val openSetEvidence: Map<String, Any?>,
    val explanation: Map<String, Any?>,
    val limitations: List<String>,
    val modelVersion: String,
    val catalogVersion: String,
    val geographicContextUsed: Boolean,
    val geographicContextAvailable: Boolean,
    val experimentalFlags: List<String>,
    val segmentationEvidence: List<SegmentationEvidence> = emptyList(),
)

data class SegmentationEvidence(val feature: String, val state: SegmentationState)
enum class SegmentationState { PRESENTE, AUSENTE, NO_EVALUABLE }

/** Ranking/GEO/Open Set ownership remains behind this boundary. */
fun interface IdentificationEngine {
    suspend fun identify(request: IdentificationRequest, embedding: FloatArray): IdentificationResult
}
