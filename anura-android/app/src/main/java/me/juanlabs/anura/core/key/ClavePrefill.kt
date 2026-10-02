package me.juanlabs.anura.core.key

/** Id del carácter de tamaño que arma `clave.js` en el servidor. */
const val ClaveTamano = "tamano"

const val ClaveSustrato = "sustrato"

private const val PasoCompatible = 1.15
private const val PasoIncompatible = 0.8

private val HabitatASustrato = mapOf(
    "leaf_litter" to "hojarasca",
    "low_vegetation" to "vegetacion",
    "water_body" to "quebrada",
    "rock" to "roca",
)

/**
 * Peso por especie según lo que la persona contestó en el paso a paso. Un campo vacío no entra.
 * Una especie del paquete sin ese dato queda en 1: compatible con cualquier respuesta, no se penaliza.
 * Nunca vale 0: no saca a una especie de la lista.
 */
fun pasoAPasoMultiplicadores(clave: ClaveDocumento?, habitat: String?, svlMm: Int?): Map<String, Double>? {
    if (clave == null || (habitat == null && svlMm == null)) return null
    val sustrato = habitat?.let { HabitatASustrato[it] }
    val banda = svlMm?.let { mm ->
        clave.caracteres.firstOrNull { it.id == ClaveTamano }?.let { bandaDe(it, mm.toDouble()) }
    }
    if (sustrato == null && banda == null) return null
    val out = LinkedHashMap<String, Double>()
    for (especie in clave.especies) {
        var peso = 1.0
        if (sustrato != null) peso *= factor(especie.estados[ClaveSustrato], sustrato)
        if (banda != null) peso *= factor(especie.estados[ClaveTamano], banda)
        if (peso != 1.0) out[especie.taxon_id] = peso
    }
    return out.takeIf { it.isNotEmpty() }
}

private fun factor(estados: List<String>?, opcion: String): Double {
    if (estados.isNullOrEmpty()) return 1.0
    return if (opcion in estados) PasoCompatible else PasoIncompatible
}

/** Id de la banda de un carácter de rango que contiene [valor]; null si el carácter no es de rango o no la hay. */
fun bandaDe(caracter: ClaveCaracter, valor: Double): String? =
    caracter.opciones.firstOrNull { opcion ->
        (opcion.desde != null || opcion.hasta != null) &&
            (opcion.desde == null || valor >= opcion.desde) &&
            (opcion.hasta == null || valor < opcion.hasta)
    }?.id

/** Cuántas especies de la clave tienen dato para [caracterId] (las demás quedan compatibles con todo). */
fun especiesConDato(clave: ClaveDocumento, caracterId: String): Int =
    clave.especies.count { !it.estados[caracterId].isNullOrEmpty() }

/**
 * Especies con dato de [caracterId] compatibles con [valor]. Null si el paquete no trae ese
 * carácter o ninguna especie tiene dato: no hay cifra honesta que dar.
 */
fun especiesCompatiblesConValor(clave: ClaveDocumento, caracterId: String, valor: Double): Int? {
    val caracter = clave.caracteres.firstOrNull { it.id == caracterId } ?: return null
    if (especiesConDato(clave, caracterId) == 0) return null
    val banda = bandaDe(caracter, valor) ?: return null
    return clave.especies.count { banda in it.estados[caracterId].orEmpty() }
}
