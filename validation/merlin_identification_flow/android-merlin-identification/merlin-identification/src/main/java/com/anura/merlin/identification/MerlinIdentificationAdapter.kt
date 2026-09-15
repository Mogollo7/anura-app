package com.anura.merlin.identification

import android.content.ContentResolver

/** Connects the image-only runtime adapter to a ranking engine that returns the stable contract. */
class MerlinIdentificationAdapter(
    private val resolver: ContentResolver,
    private val encoder: BioClipOnnxEncoder,
    private val engine: IdentificationEngine,
) {
    suspend fun identify(request: IdentificationRequest): IdentificationResult {
        ContractValidator.validate(request)
        val result = engine.identify(request, encoder.embed(resolver, request.imageUri))
        ContractValidator.validate(result)
        require(result.observationId == request.observationId) { "Engine changed observationId" }
        return result
    }
}
