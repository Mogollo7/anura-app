package me.juanlabs.anura.core.inference

import kotlin.math.exp
import kotlin.math.max

/** Rango de altitud (m) de una especie; un extremo nulo = abierto (sin ese límite). */
data class AltitudeRange(val min: Double?, val max: Double?) {
    val isEmpty: Boolean get() = min == null && max == null
}

/**
 * Rangos de altitud por especie, de datos reales: los del paquete (`clave.json` descargado con él) y,
 * si el paquete no trae la especie, los de la ficha publicada. Sin dato = no hay entrada = sin ajuste.
 * Se busca por `taxon_id` y, si el paquete usa otro id, por nombre científico.
 */
class SpeciesAltitudeRanges(
    private val byTaxon: Map<String, AltitudeRange>,
    private val byName: Map<String, AltitudeRange>,
) {
    val size: Int get() = byTaxon.size

    fun find(taxonId: String, scientificName: String): AltitudeRange? =
        byTaxon[taxonId] ?: byName[normalizeName(scientificName)]

    companion object {
        val Empty = SpeciesAltitudeRanges(emptyMap(), emptyMap())

        internal fun normalizeName(name: String): String = name.trim().lowercase().replace('_', ' ').replace(Regex("\\s+"), " ")

        /**
         * [fromPackage]: (taxon_id, nombre científico, texto del rango de `resumen["altitud"]`) de la
         * clave del paquete. [fromCatalog]: (taxon_id, nombre científico, rango de literatura publicado).
         * El paquete gana; el catálogo solo completa lo que el paquete no trae.
         */
        fun build(
            fromPackage: List<Triple<String, String, String?>>,
            fromCatalog: List<Triple<String, String, AltitudeRange?>>,
        ): SpeciesAltitudeRanges {
            val byTaxon = LinkedHashMap<String, AltitudeRange>()
            val byName = LinkedHashMap<String, AltitudeRange>()
            fun put(taxon: String, name: String, range: AltitudeRange?) {
                if (range == null || range.isEmpty) return
                byTaxon.putIfAbsent(taxon, range)
                byName.putIfAbsent(normalizeName(name), range)
            }
            fromPackage.forEach { (taxon, name, text) -> put(taxon, name, text?.let(AltitudePrior::parseRange)) }
            fromCatalog.forEach { (taxon, name, range) -> put(taxon, name, range) }
            return SpeciesAltitudeRanges(byTaxon, byName)
        }
    }
}

/**
 * Prior de altitud del ranking mostrado: mismo principio que el de clima ("nunca eliminar, solo
 * reponderar"). Una especie cuyo rango de altitud no incluye la del punto pierde peso en el voto
 * ponderado; las que sí lo incluyen, o no tienen dato, conservan el suyo. Nunca decide la especie
 * oficial (esa sale del voto visual k=5): solo mueve los porcentajes mostrados.
 *
 * Forma (heurística sin validar contra PC; ver `AltitudePriorTest`): dentro del rango o hasta
 * [ToleranceM] fuera de él el factor es 1; más allá cae como `exp(-exceso / ScaleM)` con piso [Floor].
 */
object AltitudePrior {
    /** Holgura por lo poco precisos que son los rangos de literatura y el modelo de elevación (SRTM 30 m). */
    const val ToleranceM = 100.0
    const val ScaleM = 400.0
    const val Floor = 0.15

    fun factor(altitudeM: Double, range: AltitudeRange): Double {
        val below = range.min?.let { it - altitudeM } ?: 0.0
        val above = range.max?.let { altitudeM - it } ?: 0.0
        val excess = max(0.0, max(below, above) - ToleranceM)
        if (excess == 0.0) return 1.0
        return max(Floor, exp(-excess / ScaleM))
    }

    /**
     * Multiplicador por `taxon_id` para las especies de [neighbors] que tienen rango. Null si no hay
     * altitud o no hay ningún rango aplicable: el resultado es entonces idéntico al de antes.
     */
    fun multipliers(
        altitudeM: Double?,
        neighbors: List<Neighbor>,
        ranges: SpeciesAltitudeRanges?,
    ): Map<String, Double>? {
        if (altitudeM == null || ranges == null) return null
        val result = LinkedHashMap<String, Double>()
        for (n in neighbors) {
            if (n.taxonId in result) continue
            val range = ranges.find(n.taxonId, n.scientificName) ?: continue
            result[n.taxonId] = factor(altitudeM, range)
        }
        return result.takeIf { it.isNotEmpty() }
    }

    /** Producto por especie de dos multiplicadores (clima × altitud); null solo si ambos son null. */
    fun combine(a: Map<String, Double>?, b: Map<String, Double>?): Map<String, Double>? {
        if (a == null) return b
        if (b == null) return a
        val result = LinkedHashMap(a)
        b.forEach { (taxon, factor) -> result[taxon] = (result[taxon] ?: 1.0) * factor }
        return result
    }

    /**
     * Rango escrito por `clave.js` (`resumen.altitud`): «1.500–2.500 m», «Desde 1.200 m», «Hasta 800 m»
     * (miles con punto, decimales con coma), o el de la ficha («desde 500 m»). Null si no se entiende.
     */
    fun parseRange(text: String): AltitudeRange? {
        val lower = text.trim().lowercase()
        val numbers = Regex("""\d+(?:\.\d{3})*(?:,\d+)?""").findAll(lower).mapNotNull {
            it.value.replace(".", "").replace(',', '.').toDoubleOrNull()
        }.toList()
        return when {
            lower.startsWith("desde") && numbers.size == 1 -> AltitudeRange(numbers[0], null)
            lower.startsWith("hasta") && numbers.size == 1 -> AltitudeRange(null, numbers[0])
            numbers.size == 2 -> AltitudeRange(minOf(numbers[0], numbers[1]), maxOf(numbers[0], numbers[1]))
            else -> null
        }
    }
}
