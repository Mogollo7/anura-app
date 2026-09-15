package com.anura.merlin.identification

object ContractValidator {
    fun validate(request: IdentificationRequest) {
        require(request.observationId.isNotBlank()) { "observationId is required" }
        require(request.imageUri.isNotBlank()) { "imageUri is required" }
        request.latitude?.let { require(it in -90.0..90.0) { "latitude out of range" } }
        request.longitude?.let { require(it in -180.0..180.0) { "longitude out of range" } }
    }

    fun validate(result: IdentificationResult) {
        require(result.observationId.isNotBlank()) { "observationId is required" }
        require(result.candidates.zipWithNext().all { (a, b) -> a.rank < b.rank }) { "candidate ranks must be ordered" }
        require(result.candidates.all { it.rank >= 1 }) { "candidate rank must be positive" }
        require(result.decision != IdentificationDecision.NO_REGISTRADA ||
            result.openSetEvidence["explicit_no_registrada_basis"] == true) {
            "NO_REGISTRADA requires explicit evidence; Open Set rejection is NO_CONCLUYENTE"
        }
    }
}
