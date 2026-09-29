package me.juanlabs.anura.core.data

import java.net.URLEncoder
import java.time.Instant
import kotlinx.serialization.Serializable
import me.juanlabs.anura.core.auth.AnuraServerConfig

/**
 * Datos reales de `explorer-service` (D:\server\Anura\services\explorer-service) — reemplaza el
 * catálogo local (`SpeciesCatalog`, `CommunityCatalog`) como fuente de "qué hay en el servidor"
 * para Explorar y Listado. Todas estas rutas son de solo lectura y públicas (sin `Authorization`)
 * en el servidor real.
 */
object ExplorerRemote {
    /** Sugerencias de taxón/usuario mientras se escribe (`ExploreSuggestionMenu`). Vacío si `q`
     * tiene menos de 2 caracteres — el propio servidor lo exige igual, evita un viaje inútil. */
    suspend fun suggest(query: String): List<ExplorerSuggestion> =
        if (query.trim().length < 2) {
            emptyList()
        } else {
            AnuraApi.get<List<ExplorerSuggestion>>("/api/explorer/suggest?q=${encode(query.trim())}").orEmpty()
        }

    /** Feed público: propio si se pasa `username`, o el de toda la comunidad. */
    suspend fun feed(username: String? = null): List<ExplorerFeedItem> {
        val path = if (username != null) "/api/explorer/feed?username=${encode(username)}" else "/api/explorer/feed"
        return AnuraApi.get<List<ExplorerFeedItem>>(path).orEmpty()
    }

    suspend fun observation(id: String): ExplorerFeedItem? =
        AnuraApi.get<ExplorerFeedItem>("/api/explorer/observation/${encode(id)}")

    /** URL de una miniatura ya subida — mismo esquema que usa la web (`services/api.js`,
     * `getThumbUrl`): el nombre de archivo, sin la carpeta, contra el proxy de explorer-service. */
    fun thumbUrl(key: String?, size: String = "medium"): String? {
        if (key.isNullOrBlank()) return null
        val filename = key.substringAfterLast('/')
        return "${AnuraServerConfig.AUTH_BASE_URL}/api/explorer/thumbnail/$size/${encode(filename)}"
    }

    private fun encode(value: String): String = URLEncoder.encode(value, "UTF-8")
}

/** `POST /api/explorer/favorites/:id`. */
@Serializable
data class FavoriteToggleResponse(val liked: Boolean)

/** `GET /api/explorer/suggest` — filas de taxón y de usuario mezcladas, distinguidas por `type`. */
@Serializable
data class ExplorerSuggestion(
    val type: String,
    val id: Int? = null,
    val scientific_name: String? = null,
    val common_name: String? = null,
    val family: String? = null,
    val order_name: String? = null,
    val slug: String? = null,
    val username: String? = null,
    val profile_image: String? = null,
) {
    val isTaxon: Boolean get() = type == "taxon"
}

/** `GET /api/explorer/feed` y `/api/explorer/observation/:id` — misma forma base. */
@Serializable
data class ExplorerFeedItem(
    val id: String,
    val image_key: String? = null,
    val thumbnail_key: String? = null,
    val lat: Double? = null,
    val lon: Double? = null,
    val altitude_m: Double? = null,
    val place_guess: String? = null,
    val notes: String? = null,
    val is_private: Boolean? = null,
    val created_at: String? = null,
    val username: String? = null,
    val profile_image: String? = null,
    val user_id: String? = null,
    val ai_class: String? = null,
    val ai_prob: Double? = null,
    val taxon_id: Int? = null,
    val class_name: String? = null,
    val order_name: String? = null,
    val family: String? = null,
    val genus: String? = null,
    val species: String? = null,
    val common_name: String? = null,
) {
    /** `observation.ownerUserId`/`ownerUsername`/etc. — la observación de otra persona, tal como
     * la app maneja las propias, para que `ObservationDetailScreen` no necesite dos caminos. */
    fun toObservationRecord(): ObservationRecord {
        val sci = if (!genus.isNullOrBlank() && !species.isNullOrBlank()) "$genus $species" else ai_class
        val local = sci?.let(SpeciesCatalog::find)
        val epochMs = created_at?.let { runCatching { Instant.parse(it).toEpochMilli() }.getOrNull() } ?: 0L
        return ObservationRecord(
            id = id,
            ownerUserId = user_id ?: username.orEmpty(),
            ownerDisplayName = username.orEmpty(),
            ownerUsername = username,
            speciesId = local?.id,
            commonName = common_name ?: local?.commonName,
            scientificName = sci ?: local?.scientificName,
            photoTokens = emptyList(),
            photoUrl = ExplorerRemote.thumbUrl(thumbnail_key ?: image_key, size = "large"),
            latitude = lat,
            longitude = lon,
            placeLabel = place_guess,
            observedAtEpochMs = epochMs.takeIf { it > 0L },
            svlMm = null,
            habitat = null,
            altitudeLabel = altitude_m?.let { "${it.toInt()} m" },
            visibilityPublic = is_private != true,
            isDraft = false,
            expertReviewRequested = false,
            fieldSessionId = null,
            identificationStatus = IdentificationKnown,
            createdAtEpochMs = epochMs,
            candidates = buildList {
                val name = sci ?: ai_class?.replace('_', ' ')
                val prob = ai_prob
                if (!name.isNullOrBlank() && prob != null) {
                    add(
                        IdentificationCandidate(
                            scientificName = name.replace('_', ' '),
                            share = prob.toFloat().coerceIn(0f, 1f),
                            genus = genus.orEmpty(),
                            family = family.orEmpty(),
                        ),
                    )
                }
            },
        )
    }
}
