package me.juanlabs.anura.core.auth

import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.put
import me.juanlabs.anura.core.data.AnuraApi

/**
 * Correo y contraseña contra auth-service — el mismo que usa la web. Antes este formulario
 * creaba una sesión local sin preguntarle a nadie.
 */
object AuthRemote {
    private val json = Json { ignoreUnknownKeys = true }

    sealed interface Result {
        data class Ok(val token: String) : Result
        /** Mensaje del servidor, ya escrito para mostrarse tal cual. */
        data class Rejected(val message: String) : Result
        data object Offline : Result
    }

    @Serializable
    private data class LoginBody(val token: String? = null)

    @Serializable
    private data class ErrorBody(val message: String? = null)

    suspend fun login(email: String, password: String): Result {
        val body = buildJsonObject {
            put("email", email)
            put("password", password)
            put("rememberMe", true)
        }.toString()
        val (code, text) = AnuraApi.postWithStatus("/api/auth/login", body)
        return when {
            code == -1 -> Result.Offline
            code in 200..299 -> parse<LoginBody>(text)?.token?.let(Result::Ok) ?: Result.Offline
            else -> Result.Rejected(parse<ErrorBody>(text)?.message ?: "No se pudo iniciar sesión.")
        }
    }

    /** Crea la cuenta y, si sale bien, inicia sesión con ella. */
    suspend fun register(username: String?, email: String, password: String): Result {
        val body = buildJsonObject {
            username?.let { put("username", it) }
            put("email", email)
            put("password", password)
        }.toString()
        val (code, text) = AnuraApi.postWithStatus("/api/auth/register", body)
        return when {
            code == -1 -> Result.Offline
            code in 200..299 -> login(email, password)
            code == 409 -> Result.Rejected("Ese correo ya tiene cuenta. Inicia sesión con él.")
            else -> Result.Rejected(parse<ErrorBody>(text)?.message ?: "No se pudo crear la cuenta.")
        }
    }

    private inline fun <reified T> parse(text: String?): T? =
        text?.let { runCatching { json.decodeFromString<T>(it) }.getOrNull() }
}
