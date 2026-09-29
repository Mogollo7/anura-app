package me.juanlabs.anura.core.key

/** Id del carácter de tamaño que arma `clave.js` en el servidor. */
const val ClaveTamano = "tamano"

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
