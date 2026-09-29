package me.juanlabs.anura.core.data

import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.withTimeoutOrNull
import kotlinx.serialization.Serializable
import kotlin.math.roundToInt

/** Altitud sobre el nivel del mar de un punto y de dónde salió ([AltitudeSourceOpenTopo] o [AltitudeSourceGps]). */
data class PointAltitude(val meters: Int, val source: String)

const val AltitudeSourceOpenTopo = "opentopodata"
const val AltitudeSourceGps = "gps"

@Serializable
private data class AltitudeResponse(val altitude_m: Double? = null, val source: String? = null)

/**
 * Altitud de un punto con OpenTopoData (SRTM 30 m, ASTER de respaldo) a través del servicio geo de
 * ANURA: `GET /api/geo/altitude?lat=&lon=`. Con red lenta, sin red o sin dato devuelve null y el
 * llamador sigue sin altitud: nunca se inventa una.
 */
object AltitudeRemote {
    private const val TimeoutMs = 8_000L

    suspend fun fetch(latitude: Double, longitude: Double): PointAltitude? {
        val path = "/api/geo/altitude?lat=${"%.5f".format(java.util.Locale.US, latitude)}&lon=${"%.5f".format(java.util.Locale.US, longitude)}"
        val response = try {
            withTimeoutOrNull(TimeoutMs) { AnuraApi.get<AltitudeResponse>(path) }
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (_: Exception) {
            null
        }
        val meters = response?.altitude_m?.takeIf { it.isFinite() } ?: return null
        return PointAltitude(meters.roundToInt(), AltitudeSourceOpenTopo)
    }
}
