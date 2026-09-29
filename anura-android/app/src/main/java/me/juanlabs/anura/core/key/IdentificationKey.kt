package me.juanlabs.anura.core.key

import kotlin.math.log2
import kotlinx.serialization.Serializable

/**
 * Recorrido de la clave «Paso a paso». El servidor arma el JSON (formato 1, `clave.js`);
 * el teléfono solo lo evalúa, con el mismo criterio: «no sé» no filtra, y una especie sin
 * dato de ese carácter sigue siendo compatible.
 *
 * No dibuja nada. Las pantallas existentes preguntan; esto solo dice qué especies quedan.
 */
const val ClaveFormato = 1

private const val Eps = 1e-9

@Serializable
data class ClaveDocumento(
    val formato: Int = ClaveFormato,
    val caracteres: List<ClaveCaracter> = emptyList(),
    val especies: List<ClaveEspecie> = emptyList(),
)

@Serializable
data class ClaveCaracter(
    val id: String,
    val tipo: String = "",
    val pregunta: String = "",
    val ayuda: String = "",
    val opciones: List<ClaveOpcion> = emptyList(),
    val ganancia_bits: Double = 0.0,
)

@Serializable
data class ClaveOpcion(
    val id: String,
    val etiqueta: String = "",
    val desde: Double? = null,
    val hasta: Double? = null,
)

@Serializable
data class ClaveEspecie(
    val taxon_id: String,
    val nombre_cientifico: String = "",
    val genero: String = "",
    val familia: String = "",
    val nombre_comun: String? = null,
    val estados: Map<String, List<String>> = emptyMap(),
    val resumen: Map<String, String> = emptyMap(),
)

data class ClaveRespuesta(val caracter: String, val opcion: String?)

sealed class ClaveResolucion {
    data class Pregunta(
        val siguiente: String,
        val ganancia: Double,
        val especies: List<String>,
    ) : ClaveResolucion()

    data class Una(val taxonId: String) : ClaveResolucion()

    data class Varias(
        val especies: List<String>,
        val pendientes: List<String>,
        val indistinguibles: Boolean,
    ) : ClaveResolucion()

    data object Ninguna : ClaveResolucion()
}

/** Opciones compatibles; null = sin dato, compatible con cualquier respuesta. */
internal fun compatibles(especie: ClaveEspecie, caracter: ClaveCaracter): List<String>? {
    val estados = especie.estados[caracter.id]
    return estados?.takeIf { it.isNotEmpty() }
}

fun ganancia(caracter: ClaveCaracter, restantes: List<ClaveEspecie>): Double {
    val n = restantes.size
    if (n <= 1 || caracter.opciones.isEmpty()) return 0.0
    val p = HashMap<String, Double>()
    val tam = HashMap<String, Int>()
    for (especie in restantes) {
        val opciones = compatibles(especie, caracter) ?: caracter.opciones.map { it.id }
        for (opcion in opciones) {
            p[opcion] = (p[opcion] ?: 0.0) + 1.0 / (n * opciones.size)
            tam[opcion] = (tam[opcion] ?: 0) + 1
        }
    }
    var esperado = 0.0
    for (opcion in caracter.opciones) {
        val pa = p[opcion.id] ?: 0.0
        if (pa > 0.0) esperado += pa * log2((tam[opcion.id] ?: 0).toDouble())
    }
    return log2(n.toDouble()) - esperado
}

fun siguiente(
    clave: ClaveDocumento,
    restantes: List<ClaveEspecie>,
    respondidos: Set<String>,
): ClaveCaracter? {
    var mejor: ClaveCaracter? = null
    var mejorGanancia = Eps
    for (caracter in clave.caracteres) {
        if (caracter.id in respondidos) continue
        val actual = ganancia(caracter, restantes)
        if (actual > mejorGanancia + Eps) {
            mejor = caracter
            mejorGanancia = actual
        }
    }
    return mejor
}

/**
 * [respuestas] en el orden en que la persona contestó. `opcion` null es «no sé».
 * Lanza [IllegalArgumentException] si el carácter o la opción no están en la clave.
 */
fun resolver(clave: ClaveDocumento, respuestas: List<ClaveRespuesta> = emptyList()): ClaveResolucion {
    var restantes = clave.especies
    val respondidos = HashSet<String>()
    val noSe = HashSet<String>()
    val conDato = HashMap<String, Int>()
    for (especie in clave.especies) conDato[especie.taxon_id] = 0
    for (respuesta in respuestas) {
        val caracter = clave.caracteres.find { it.id == respuesta.caracter }
            ?: throw IllegalArgumentException("Carácter desconocido: ${respuesta.caracter}")
        respondidos.add(caracter.id)
        if (respuesta.opcion == null) {
            noSe.add(caracter.id)
            continue
        }
        if (caracter.opciones.none { it.id == respuesta.opcion }) {
            throw IllegalArgumentException("Opción desconocida: ${respuesta.opcion}")
        }
        restantes = restantes.filter { especie ->
            val compatibles = compatibles(especie, caracter)
            if (compatibles != null && respuesta.opcion !in compatibles) return@filter false
            if (compatibles != null) conDato[especie.taxon_id] = (conDato[especie.taxon_id] ?: 0) + 1
            true
        }
    }
    if (restantes.isEmpty()) return ClaveResolucion.Ninguna
    if (restantes.size == 1) return ClaveResolucion.Una(restantes.first().taxon_id)
    val proxima = siguiente(clave, restantes, respondidos)
    if (proxima != null) {
        return ClaveResolucion.Pregunta(
            siguiente = proxima.id,
            ganancia = ganancia(proxima, restantes),
            especies = restantes.map { it.taxon_id },
        )
    }
    val pendientes = clave.caracteres
        .filter { it.id in noSe && ganancia(it, restantes) > Eps }
        .map { it.id }
    val orden = restantes.sortedWith(
        compareByDescending<ClaveEspecie> { conDato[it.taxon_id] ?: 0 }
            .thenBy { it.nombre_cientifico },
    )
    return ClaveResolucion.Varias(
        especies = orden.map { it.taxon_id },
        pendientes = pendientes,
        indistinguibles = pendientes.isEmpty(),
    )
}
