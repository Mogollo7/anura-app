package me.juanlabs.anura.core.inference

import kotlin.math.pow

/**
 * P(especie|zona) de una zona geográfica del paquete regional activo, horneado en PC
 * (`pipeline_dataset/paquetes_zonales.py`) desde ocurrencias reales con suavizado de Laplace
 * (`P(s|z) = (N(s,z)+α)/(N(z)+αK)`) — nunca cero para una especie no observada en la zona,
 * usa [unobservedP] en su lugar. Validado con control de fuga: Top-1 62.9%→72.5% sobre 167
 * imágenes de prueba fuera del prior (`COLOMBIA_ANURA/ANTIOQUIA/reports/packages_v1.0.0.json`).
 */
data class GeoZonePrior(
    val zoneId: String,
    /** Exponente de la combinación `voto_visual · P(s|z)^peso` — mismo valor congelado en PC (0.75). */
    val weight: Double,
    val unobservedP: Double,
    private val byTaxon: Map<String, Double>,
) {
    fun priorFor(taxonId: String): Double = byTaxon[taxonId] ?: unobservedP
}
