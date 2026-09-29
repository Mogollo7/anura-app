package me.juanlabs.anura.core.data

import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonNull
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive

/**
 * `POST /api/observations/field-trips` (observation-service, phase21). Sube una salida de campo
 * cerrada junto con los ids de servidor de sus observaciones. Idempotente por `clientId` (el id
 * local de la sesión): reintentar no duplica la salida. Sin sesión no se llama.
 */
object FieldTripsRemote {
    /** Devuelve `field_trips.id` o null si no hubo red / el servidor la rechazó. */
    suspend fun upsert(
        clientId: String,
        startedAtEpochMs: Long,
        endedAtEpochMs: Long?,
        placeLabel: String?,
        latitude: Double?,
        longitude: Double?,
        observationServerIds: List<String>,
        bearer: String,
    ): String? {
        val body = JsonObject(
            mapOf(
                "clientId" to JsonPrimitive(clientId),
                "startedAt" to JsonPrimitive(startedAtEpochMs),
                "endedAt" to (endedAtEpochMs?.let { JsonPrimitive(it) } ?: JsonNull),
                "placeLabel" to (placeLabel?.let { JsonPrimitive(it) } ?: JsonNull),
                "latitude" to (latitude?.let { JsonPrimitive(it) } ?: JsonNull),
                "longitude" to (longitude?.let { JsonPrimitive(it) } ?: JsonNull),
                "observationIds" to JsonArray(observationServerIds.map { JsonPrimitive(it) }),
            ),
        ).toString()
        return AnuraApi.post<FieldTripResponse>("/api/observations/field-trips", body, bearer)?.id
    }
}

@Serializable
private data class FieldTripResponse(val id: String? = null)
