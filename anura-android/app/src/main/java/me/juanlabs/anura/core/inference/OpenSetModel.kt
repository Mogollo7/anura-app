package me.juanlabs.anura.core.inference

import java.io.InputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.math.max
import kotlin.math.pow
import kotlin.math.sqrt

data class OpenSetScore(val mahalanobis: Double, val nearestCentroidId: String, val accepted: Boolean)

/**
 * Rechazo Open Set congelado (M5_LedoitWolf_Shared, threshold_1.1.0_CLEAN): distancia de Mahalanobis
 * mínima a los centroides con precisión compartida; se acepta si ≤ tau. Mismo cálculo que
 * `min_mahalanobis` de tools/catalog/run_open_set_evaluation.py, en doble precisión.
 * Formato del archivo: ver tools/mobile/export_mobile_inference.py.
 */
class OpenSetModel(
    val dim: Int,
    val tau: Double,
    private val precision: DoubleArray,
    private val centroids: DoubleArray,
    val centroidIds: List<String>,
) {
    /**
     * @param allowedIds si no es null, restringe la comparación a esos taxon_id (p. ej. solo las
     * especies que realmente trae el paquete regional activo). Con todo el catálogo nacional (41
     * especies) se acepta erróneamente una especie que Antioquia ni siquiera ofrece.
     */
    fun score(embedding: FloatArray, allowedIds: Set<String>? = null): OpenSetScore {
        require(embedding.size == dim) { "embedding.size=${embedding.size} != $dim" }
        val diff = DoubleArray(dim)
        var best = Double.MAX_VALUE
        var bestIndex = 0
        for (k in centroidIds.indices) {
            if (allowedIds != null && centroidIds[k] !in allowedIds) continue
            val base = k * dim
            for (d in 0 until dim) diff[d] = embedding[d].toDouble() - centroids[base + d]
            var d2 = 0.0
            for (i in 0 until dim) {
                val row = i * dim
                var acc = 0.0
                for (j in 0 until dim) acc += precision[row + j] * diff[j]
                d2 += diff[i] * acc
            }
            if (d2 < best) {
                best = d2
                bestIndex = k
            }
        }
        val distance = sqrt(max(0.0, best))
        return OpenSetScore(distance, centroidIds[bestIndex], distance <= tau)
    }

    companion object {
        private const val Magic = "ANOS"

        fun read(input: InputStream): OpenSetModel {
            val buffer = ByteBuffer.wrap(input.readBytes()).order(ByteOrder.LITTLE_ENDIAN)
            val magic = ByteArray(4).also { buffer.get(it) }.toString(Charsets.US_ASCII)
            require(magic == Magic) { "Archivo Open Set inválido: magic=$magic" }
            val version = buffer.int
            require(version == 1) { "Versión de Open Set no soportada: $version" }
            val dim = buffer.int
            val k = buffer.int
            val tau = buffer.double
            val precision = DoubleArray(dim * dim).also { buffer.asDoubleBuffer().get(it) }
            buffer.position(buffer.position() + dim * dim * 8)
            val centroids = DoubleArray(k * dim).also { buffer.asDoubleBuffer().get(it) }
            buffer.position(buffer.position() + k * dim * 8)
            val ids = List(k) {
                val bytes = ByteArray(buffer.int).also { buffer.get(it) }
                bytes.toString(Charsets.UTF_8)
            }
            return OpenSetModel(dim, tau, precision, centroids, ids)
        }
    }
}

data class Neighbor(
    val taxonId: String,
    val scientificName: String,
    val distance: Double,
    val genus: String = "",
    val family: String = "",
)

/** Especie candidata con su fracción del voto ponderado de los k vecinos (suma 1 entre candidatas). */
data class Candidate(
    val taxonId: String,
    val scientificName: String,
    val share: Double,
    val genus: String = "",
    val family: String = "",
)

/** Voto por especie entre los k vecinos, ponderado por similitud coseno (1 - distancia), como en Fase 8. */
object KnnVote {
    fun winner(neighbors: List<Neighbor>): Pair<String, Double>? {
        val votes = votes(neighbors)
        var best: Pair<String, Double>? = null
        for ((taxon, vote) in votes) {
            if (best == null || vote > best.second) best = taxon to vote
        }
        return best
    }

    /**
     * Candidatas ordenadas por voto; la primera es siempre [winner] (mismo desempate por orden de
     * llegada) — salvo que [geoPrior]/[weatherMultiplier] reordenen el voto ponderado (ver más
     * abajo), en cuyo caso el ganador es quien gane la votación ya ajustada por contexto.
     *
     * Con [geoPrior] no nulo, cada voto se multiplica por `P(especie|zona)^peso` antes de
     * normalizar — la misma combinación `score(s) = voto_knn(s) · P(s|z)^w` validada en PC
     * (`pipeline_dataset/paquetes_zonales.py`, Top-1 62.9%→72.5% con control de fuga). Sin
     * [geoPrior] (sin ubicación o sin zona en el paquete) el resultado es idéntico al voto
     * puramente visual de siempre.
     *
     * [weatherMultiplier] es un factor adicional por especie ya elevado a su peso (el llamador lo
     * arma, `KnnVote` no conoce clima) — mismo principio de "nunca eliminar, solo reponderar":
     * especies sin fila en el mapa quedan con multiplicador 1 (neutro).
     */
    fun candidates(
        neighbors: List<Neighbor>,
        geoPrior: GeoZonePrior? = null,
        weatherMultiplier: Map<String, Double>? = null,
    ): List<Candidate> {
        val votes = votes(neighbors)
        val weighted = votes.mapValuesTo(LinkedHashMap()) { (taxonId, vote) ->
            val geo = geoPrior?.let { it.priorFor(taxonId).pow(it.weight) } ?: 1.0
            val clima = weatherMultiplier?.get(taxonId) ?: 1.0
            vote * geo * clima
        }
        val total = weighted.values.sum()
        if (total <= 0.0) return emptyList()
        val byTaxon = neighbors.associateBy { it.taxonId }
        return weighted.entries
            .withIndex()
            .sortedWith(compareByDescending<IndexedValue<Map.Entry<String, Double>>> { it.value.value }.thenBy { it.index })
            .map { (_, entry) ->
                val n = byTaxon.getValue(entry.key)
                Candidate(entry.key, n.scientificName, entry.value / total, n.genus, n.family)
            }
    }

    private fun votes(neighbors: List<Neighbor>): LinkedHashMap<String, Double> {
        val votes = LinkedHashMap<String, Double>()
        for (n in neighbors) votes[n.taxonId] = (votes[n.taxonId] ?: 0.0) + (1.0 - n.distance)
        return votes
    }

    /**
     * Candidatas para mostrar en la UI: [winner] siempre primero (es la decisión oficial), seguido de
     * hasta [count]-1 alternativas distintas tomadas de [broader] (un k-NN con más vecinos que el
     * oficial, solo para tener más candidatas donde elegir — no participa en la decisión).
     *
     * El % mostrado de TODAS las candidatas (incluido el ganador) sale de [broader]: son la misma
     * distribución normalizada, así la suma de los % mostrados nunca pasa de 100%. Usar el share
     * oficial (k=5) para el ganador y el de [broader] (k=15) para el resto —como se hacía antes—
     * mezcla dos normalizaciones distintas y puede sumar más de 100% (el ganador domina más en un
     * vecindario pequeño que en uno amplio, así que su share oficial > su share en broader).
     */
    fun displayCandidates(winner: Candidate, broader: List<Candidate>, count: Int = 4): List<Candidate> {
        val winnerForDisplay = broader.firstOrNull { it.taxonId == winner.taxonId } ?: winner
        val rest = broader.filter { it.taxonId != winner.taxonId }.take(count - 1)
        return listOf(winnerForDisplay) + rest
    }
}
