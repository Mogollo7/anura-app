package me.juanlabs.anura.core.data

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.res.stringResource
import java.net.HttpURLConnection
import java.net.URL
import kotlin.math.roundToInt
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import me.juanlabs.anura.R

data class AmbientReading(
    val celsius: Int?,
    val humidityPercent: Int?,
    val precipitationMm: Double?,
)

/**
 * Clima actual en el punto (Open-Meteo, sin clave). Si no hay coordenadas
 * o la red no responde, la pantalla muestra N/A.
 */
object AmbientTemperature {
    private val json = Json { ignoreUnknownKeys = true }

    suspend fun read(latitude: Double, longitude: Double): AmbientReading? = withContext(Dispatchers.IO) {
        runCatching {
            val url = URL(
                "https://api.open-meteo.com/v1/forecast?latitude=$latitude&longitude=$longitude" +
                    "&current=temperature_2m,relative_humidity_2m,precipitation",
            )
            val conn = url.openConnection() as HttpURLConnection
            conn.connectTimeout = 4_000
            conn.readTimeout = 8_000
            conn.instanceFollowRedirects = true
            try {
                if (conn.responseCode !in 200..299) return@runCatching null
                parse(conn.inputStream.bufferedReader().use { it.readText() })
            } finally {
                conn.disconnect()
            }
        }.getOrNull()
    }

    internal fun parse(body: String): AmbientReading? {
        val current = json.decodeFromString<OpenMeteoForecast>(body).current ?: return null
        return AmbientReading(
            celsius = current.temperature_2m?.roundToInt(),
            humidityPercent = current.relative_humidity_2m?.roundToInt(),
            precipitationMm = current.precipitation,
        )
    }
}

@Serializable
private data class OpenMeteoForecast(val current: OpenMeteoCurrent? = null)

@Serializable
private data class OpenMeteoCurrent(
    val temperature_2m: Double? = null,
    val relative_humidity_2m: Double? = null,
    val precipitation: Double? = null,
)

data class AmbientLabels(
    val temperature: String,
    val humidity: String,
    val precipitation: String,
)

@Composable
fun rememberAmbientConditions(latitude: Double?, longitude: Double?): AmbientLabels {
    val unavailable = stringResource(R.string.weather_unavailable)
    val empty = AmbientLabels(unavailable, unavailable, unavailable)
    var labels by remember(latitude, longitude) { mutableStateOf(empty) }
    LaunchedEffect(latitude, longitude, unavailable) {
        val reading = if (latitude == null || longitude == null) {
            null
        } else {
            AmbientTemperature.read(latitude, longitude)
        }
        labels = AmbientLabels(
            temperature = reading?.celsius?.let { "$it °C" } ?: unavailable,
            humidity = reading?.humidityPercent?.let { "$it %" } ?: unavailable,
            precipitation = reading?.precipitationMm?.let(::formatPrecipitation) ?: unavailable,
        )
    }
    return labels
}

@Composable
fun rememberAmbientTemperatureLabel(latitude: Double?, longitude: Double?): String =
    rememberAmbientConditions(latitude, longitude).temperature

internal fun formatPrecipitation(mm: Double): String {
    val rounded = kotlin.math.round(mm * 10.0) / 10.0
    val text = if (rounded % 1.0 == 0.0) rounded.toInt().toString() else rounded.toString().replace('.', ',')
    return "$text mm"
}
