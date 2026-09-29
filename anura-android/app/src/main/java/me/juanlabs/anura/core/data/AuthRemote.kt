package me.juanlabs.anura.core.data

import java.net.URLEncoder
import kotlinx.serialization.Serializable

/**
 * Perfil público y relaciones de seguimiento reales de `auth-service` — reemplaza
 * `CommunityCatalog.people`/`person()` como fuente de "quién es esta persona" para perfiles
 * ajenos y la pantalla Conexiones.
 */
object AuthRemote {
    suspend fun publicProfile(username: String): PublicProfileResponse? =
        AnuraApi.get<PublicProfileResponse>("/api/auth/public/${encode(username)}")

    suspend fun followers(username: String): List<PublicPerson> =
        AnuraApi.get<List<PublicPerson>>("/api/auth/followers/${encode(username)}").orEmpty()

    suspend fun following(username: String): List<PublicPerson> =
        AnuraApi.get<List<PublicPerson>>("/api/auth/following/${encode(username)}").orEmpty()

    suspend fun followStatus(username: String, bearer: String): Boolean =
        AnuraApi.get<FollowStatusResponse>("/api/auth/follow/${encode(username)}/status", bearer)?.following == true

    suspend fun toggleFollow(username: String, bearer: String): Boolean? =
        AnuraApi.post<FollowStatusResponse>("/api/auth/follow/${encode(username)}", bearer = bearer)?.following

    private fun encode(value: String): String = URLEncoder.encode(value, "UTF-8")
}

@Serializable
data class PublicPerson(
    val username: String,
    val profile_image: String? = null,
    val biography: String? = null,
)

@Serializable
data class PublicProfileUser(
    val id: String,
    val username: String,
    val email: String? = null,
    val profile_image: String? = null,
    val biography: String? = null,
)

@Serializable
data class PublicProfileStats(
    val observations: Int = 0,
    val species: Int = 0,
    val followers: Int = 0,
    val following: Int = 0,
    val joined: String? = null,
)

@Serializable
data class PublicProfileResponse(
    val user: PublicProfileUser,
    val stats: PublicProfileStats,
)

@Serializable
data class FollowStatusResponse(val following: Boolean)
