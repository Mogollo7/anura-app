package me.juanlabs.anura.core.key

import me.juanlabs.anura.core.data.HabitatLeafLitter
import me.juanlabs.anura.core.data.HabitatLowVegetation
import me.juanlabs.anura.core.data.HabitatRock
import me.juanlabs.anura.core.data.HabitatWaterBody
import me.juanlabs.anura.core.data.PeriodDay
import me.juanlabs.anura.core.data.PeriodNight

/**
 * Lo que la persona ya dijo en los pasos del asistente y la clave puede aprovechar.
 * Cada dato es null si no se capturó: nunca se rellena con un valor supuesto.
 */
data class ClaveDatos(
    val altitudM: Int? = null,
    val tamanoMm: Int? = null,
    val habitat: String? = null,
    val periodo: String? = null,
)

/** Ids de carácter que arma `clave.js` en el servidor. */
const val ClaveAltitud = "altitud"
const val ClaveTamano = "tamano"
const val ClaveSustrato = "sustrato"
const val ClaveActividad = "actividad"

/**
 * Respuestas que la clave puede dar por contestadas con [datos]. Solo cuentan los caracteres que
 * el paquete trae y solo si el dato cae en una de sus opciones; el resto queda para preguntarse.
 *  - altitud y tamaño: la banda que contiene el valor (`desde` incluido, `hasta` excluido).
 *  - sustrato: el microhábitat del Paso 1.
 *  - actividad: día o noche según la franja del Paso 2 (amanecer y atardecer no deciden).
 */
fun respuestasPrevias(clave: ClaveDocumento, datos: ClaveDatos): List<ClaveRespuesta> = buildList {
    for (caracter in clave.caracteres) {
        val opcion = when (caracter.id) {
            ClaveAltitud -> datos.altitudM?.let { bandaDe(caracter, it.toDouble()) }
            ClaveTamano -> datos.tamanoMm?.let { bandaDe(caracter, it.toDouble()) }
            ClaveSustrato -> when (datos.habitat) {
                HabitatLeafLitter -> "hojarasca"
                HabitatLowVegetation -> "vegetacion"
                HabitatWaterBody -> "quebrada"
                HabitatRock -> "roca"
                else -> null
            }
            ClaveActividad -> when (datos.periodo) {
                PeriodDay -> "dia"
                PeriodNight -> "noche"
                else -> null
            }
            else -> null
        }
        if (opcion != null && caracter.opciones.any { it.id == opcion }) {
            add(ClaveRespuesta(caracter.id, opcion))
        }
    }
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

/** Especies que quedan con [respuestas]; null si alguna no corresponde a esta clave (paquete distinto). */
fun especiesQueQuedan(clave: ClaveDocumento, respuestas: List<ClaveRespuesta>): Int? =
    runCatching {
        when (val resolucion = resolver(clave, respuestas)) {
            is ClaveResolucion.Pregunta -> resolucion.especies.size
            is ClaveResolucion.Una -> 1
            is ClaveResolucion.Varias -> resolucion.especies.size
            ClaveResolucion.Ninguna -> 0
        }
    }.getOrNull()

/** Las respuestas manuales que no repiten un carácter que los pasos anteriores ya contestaron (esas ganan). */
fun manualesSinPrevias(previas: List<ClaveRespuesta>, manuales: List<ClaveRespuesta>): List<ClaveRespuesta> {
    val ids = previas.map { it.caracter }.toSet()
    return manuales.filter { it.caracter !in ids }
}

/** Serialización de las respuestas manuales para guardarlas en el borrador (una por línea). */
fun codificarRespuestas(respuestas: List<ClaveRespuesta>): String =
    respuestas.joinToString("\n") { "${it.caracter}\t${it.opcion.orEmpty()}" }

fun decodificarRespuestas(raw: String?): List<ClaveRespuesta> =
    raw.orEmpty().split('\n').filter { it.isNotEmpty() }.map { linea ->
        val partes = linea.split('\t', limit = 2)
        ClaveRespuesta(partes[0], partes.getOrNull(1)?.ifEmpty { null })
    }
