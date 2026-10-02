package me.juanlabs.anura.core.inference

import kotlin.math.sqrt

/**
 * Contexto de una especie horneado por el servidor en `taxon_context` (Ficha técnica): rango de
 * altitud, pesos `wv + wg + wm = 1` (visual, geográfico, hábitat/sustrato) y largo de la cabeza al
 * cloaca. Un campo `null` = la Ficha no tiene el dato: sin ajuste, nunca un valor inventado.
 */
data class TaxonContext(
    val altitudeMin: Double?,
    val altitudeMax: Double?,
    val weightVisual: Double?,
    val weightGeo: Double?,
    val weightHabitat: Double?,
    val lrcMin: Double?,
    val lrcMax: Double?,
)

class NamedVector(val name: String, val vector: FloatArray)

/** Lo que el paquete trae además de los vecinos: contexto de Ficha, morfos y supercentroides. */
class PackageExtras(
    val context: Map<String, TaxonContext>,
    val morphs: Map<String, List<NamedVector>>,
    val genera: List<NamedVector>,
    val families: List<NamedVector>,
) {
    companion object {
        val Empty = PackageExtras(emptyMap(), emptyMap(), emptyList(), emptyList())
    }
}

/** Más cercano por coseno con su valor; `null` si no hay candidatos. */
data class NearestMatch(val name: String, val cosine: Double)

object ContextWeights {
    /**
     * Exponente con el que una especie aplica un ajuste de contexto, según el peso que su Ficha le da.
     * Pesos iguales (1/3 cada uno) dan 1,0 = el comportamiento de siempre; una especie que depende más
     * de ese contexto lo aplica con más fuerza y una generalista con menos. Acotado a [0,2 ; 2,0].
     * Sin peso en la Ficha: 1,0. Heurística de reparto, no un valor validado contra evaluación en PC.
     */
    fun exponent(weight: Double?): Double = if (weight == null) 1.0 else (weight * 3.0).coerceIn(0.2, 2.0)

    fun apply(multipliers: Map<String, Double>?, context: Map<String, TaxonContext>, pick: (TaxonContext) -> Double?): Map<String, Double>? {
        if (multipliers == null || context.isEmpty()) return multipliers
        return multipliers.mapValues { (taxon, factor) ->
            val e = exponent(context[taxon]?.let(pick))
            if (e == 1.0 || factor <= 0.0) factor else Math.pow(factor, e)
        }
    }
}

fun cosine(a: FloatArray, b: FloatArray): Double {
    if (a.size != b.size || a.isEmpty()) return 0.0
    var dot = 0.0
    var na = 0.0
    var nb = 0.0
    for (i in a.indices) {
        dot += a[i] * b[i]
        na += a[i] * a[i]
        nb += b[i] * b[i]
    }
    val d = sqrt(na) * sqrt(nb)
    return if (d == 0.0) 0.0 else dot / d
}

fun List<NamedVector>.nearest(embedding: FloatArray): NearestMatch? =
    maxByOrNull { cosine(embedding, it.vector) }?.let { NearestMatch(it.name, cosine(embedding, it.vector)) }
