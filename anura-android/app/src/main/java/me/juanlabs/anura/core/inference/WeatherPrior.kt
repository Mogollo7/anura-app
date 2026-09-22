package me.juanlabs.anura.core.inference

import java.net.HttpURLConnection
import java.net.URL
import kotlin.math.exp
import kotlin.math.max
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.double
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive

/** Media/desv. estándar de temperatura y humedad de una especie en el paquete (solo train,
 * control de fuga: Top-1 61.2%→65.1%, n=129, `evaluation/geo_weather_v1/`). */
data class WeatherStats(val n: Int, val tempMean: Double, val tempStd: Double, val humMean: Double, val humStd: Double)

data class WeatherObservation(val tempC: Double, val humidityPct: Double)

/** likelihood(s) = exp(-0.5·z_temp²) · exp(-0.5·z_hum²) — z-score contra las stats de la especie. */
fun WeatherStats.likelihood(obs: WeatherObservation): Double {
    fun z(x: Double, mean: Double, std: Double) = (x - mean) / max(std, 1e-6)
    val zt = z(obs.tempC, tempMean, tempStd)
    val zh = z(obs.humidityPct, humMean, humStd)
    return exp(-0.5 * zt * zt) * exp(-0.5 * zh * zh)
}

/**
 * Clima actual en (lat, lon) vía Open-Meteo (gratis, sin API key). Nunca bloquea la
 * identificación: cualquier fallo de red o timeout devuelve null y el voto queda sin ajuste de
 * clima, igual que sin ubicación — la app sigue funcionando sin conexión.
 */
object OpenMeteoClient {
    private const val Endpoint = "https://api.open-meteo.com/v1/forecast"
    private const val TimeoutMs = 4_000

    fun fetchCurrent(latitude: Double, longitude: Double): WeatherObservation? = runCatching {
        val url = URL("$Endpoint?latitude=$latitude&longitude=$longitude&current=temperature_2m,relative_humidity_2m")
        val body = (url.openConnection() as HttpURLConnection).run {
            connectTimeout = TimeoutMs
            readTimeout = TimeoutMs
            requestMethod = "GET"
            inputStream.bufferedReader().use { it.readText() }.also { disconnect() }
        }
        val current = Json.parseToJsonElement(body).jsonObject["current"]!!.jsonObject
        WeatherObservation(
            tempC = current["temperature_2m"]!!.jsonPrimitive.double,
            humidityPct = current["relative_humidity_2m"]!!.jsonPrimitive.double,
        )
    }.getOrNull()
}
