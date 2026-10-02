package me.juanlabs.anura.core.inference

/**
 * Fusión tardía de varias fotos del **mismo individuo**.
 *
 * No toca BioCLIP, Open Set, umbrales ni el k-NN: cada foto ya salió por
 * [AnuraIdentifier.identify]. Aquí se promedian votos de candidatas y se decide
 * con esas salidas, porque se sabe que son la misma rana.
 */
object IdentificationEnsemble {
    fun combine(outcomes: List<IdentificationOutcome>): IdentificationOutcome {
        if (outcomes.isEmpty()) {
            return IdentificationOutcome.Failed(IdentificationFailure.NoPhoto, "Sin fotos para identificar")
        }
        if (outcomes.size == 1) return outcomes.first()

        val identified = outcomes.filterIsInstance<IdentificationOutcome.Identified>()
        val notAnuro = outcomes.filterIsInstance<IdentificationOutcome.NotAnuro>()
        val failed = outcomes.filterIsInstance<IdentificationOutcome.Failed>()

        // Un ángulo malo no descarta al individuo si otra vista sí es un anuro.
        if (identified.isEmpty()) {
            return notAnuro.minByOrNull { it.openSet.mahalanobis }
                ?: failed.firstOrNull()
                ?: IdentificationOutcome.Failed(IdentificationFailure.EngineError, "Sin resultado de identificación")
        }

        val fusedCandidates = averageCandidates(identified)
        val top = fusedCandidates.firstOrNull()
            ?: return IdentificationOutcome.Failed(IdentificationFailure.EngineError, "Sin candidatas para fusionar")
        val acceptedViews = identified.count { it.openSet.accepted }
        val accepted = acceptedViews * 2 >= identified.size ||
            identified.any { it.openSet.accepted && it.scientificName == top.scientificName }
        val mahalanobis = identified.map { it.openSet.mahalanobis }.average()
        val nearest = identified.minBy { it.openSet.mahalanobis }.openSet.nearestCentroidId
        val neighbors = identified.flatMap { it.neighbors }
            .groupBy { it.taxonId }
            .map { (_, group) ->
                val sample = group.first()
                sample.copy(distance = group.map { it.distance }.average())
            }
            .sortedBy { it.distance }

        return IdentificationOutcome.Identified(
            taxonId = top.taxonId,
            scientificName = top.scientificName,
            accepted = accepted,
            openSet = OpenSetScore(mahalanobis, nearest, accepted),
            neighbors = neighbors,
            candidates = fusedCandidates,
            clusters = identified.flatMap { it.clusters }.distinctBy { it.id }.filter { it.contains(top.taxonId) },
            morph = identified.filter { it.taxonId == top.taxonId }.mapNotNull { it.morph }.maxByOrNull { it.cosine },
            nearestGenus = identified.mapNotNull { it.nearestGenus }.maxByOrNull { it.cosine },
            nearestFamily = identified.mapNotNull { it.nearestFamily }.maxByOrNull { it.cosine },
        )
    }

    private fun averageCandidates(identified: List<IdentificationOutcome.Identified>): List<Candidate> {
        data class Acc(var share: Double, val taxonId: String, val genus: String, val family: String)
        val byName = linkedMapOf<String, Acc>()
        identified.forEach { outcome ->
            outcome.candidates.forEach { candidate ->
                val acc = byName.getOrPut(candidate.scientificName) {
                    Acc(0.0, candidate.taxonId, candidate.genus, candidate.family)
                }
                acc.share += candidate.share
            }
        }
        val n = identified.size.toDouble()
        val averaged = byName.map { (name, acc) ->
            Candidate(acc.taxonId, name, acc.share / n, acc.genus, acc.family)
        }
        val total = averaged.sumOf { it.share }.takeIf { it > 0.0 } ?: 1.0
        return averaged
            .map { it.copy(share = it.share / total) }
            .sortedByDescending { it.share }
    }
}
