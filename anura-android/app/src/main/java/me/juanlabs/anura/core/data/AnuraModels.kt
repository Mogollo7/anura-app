package me.juanlabs.anura.core.data

import kotlinx.serialization.Serializable

@Serializable
enum class AccountKind {
    Guest,
    Authenticated,
}

@Serializable
data class UserSession(
    val kind: AccountKind = AccountKind.Guest,
    val userId: String = GuestUserId,
    val displayName: String = "",
    val username: String = "",
    val email: String = "",
    val bio: String = "",
    val location: String = "",
    val photoToken: String? = null,
    val usageProfile: String? = null,
    val enteredApp: Boolean = false,
    /** JWT real de auth-service (login con Google por Custom Tabs). Null: sesión local sin cuenta. */
    val authToken: String? = null,
) {
    val isGuest: Boolean get() = kind == AccountKind.Guest
    val isOwnProfile: Boolean get() = true

    fun greetingName(): String = displayName.trim()
}

@Serializable
data class CaptureDraft(
    val habitat: String? = null,
    val latitude: Double? = null,
    val longitude: Double? = null,
    val precisionMeters: Int? = null,
    val altitudeLabel: String? = null,
    /** Altitud del GPS en metros (null si el GPS no la dio o el punto se marcó a mano). */
    val altitudeMeters: Int? = null,
    val ecosystemLabel: String? = null,
    val observedAtEpochMs: Long? = null,
    val period: String? = null,
    val svlMm: Int? = null,
    val photoTokens: List<String> = emptyList(),
    val audioPath: String? = null,
    val audioDurationMs: Long? = null,
    val fieldSessionId: String? = null,
    /** Respuestas manuales a la clave del asistente (una por línea, `carácter<TAB>opción`). Null: no se usó la ayuda. */
    val claveAnswers: String? = null,
)

@Serializable
data class ObservationRecord(
    val id: String,
    val ownerUserId: String,
    val ownerDisplayName: String,
    /** Handle real (`auth.users.username`) — lo que en verdad piden los endpoints de seguir y
     * de perfil público; null para el respaldo local antiguo sin cuenta real detrás. */
    val ownerUsername: String? = null,
    val speciesId: String? = null,
    val commonName: String? = null,
    val scientificName: String? = null,
    val photoTokens: List<String> = emptyList(),
    /** Miniatura real del servidor para una observación ajena sin archivo local (`ExplorerRemote.thumbUrl`). */
    val photoUrl: String? = null,
    val audioPath: String? = null,
    val audioDurationMs: Long? = null,
    val latitude: Double? = null,
    val longitude: Double? = null,
    val placeLabel: String? = null,
    val observedAtEpochMs: Long? = null,
    val svlMm: Int? = null,
    val habitat: String? = null,
    val altitudeLabel: String? = null,
    val visibilityPublic: Boolean = true,
    val isDraft: Boolean = false,
    val expertReviewRequested: Boolean = false,
    val fieldSessionId: String? = null,
    val identificationStatus: String = IdentificationKnown,
    val createdAtEpochMs: Long = 0L,
    /** Resultado real del k-NN (vacío en observaciones sin identificación en el teléfono). */
    val candidates: List<IdentificationCandidate> = emptyList(),
    /** `observations.id` real una vez subida a `observation-service` (C3, alcance mínimo: solo
     * lo que ya acepta `POST /api/observations`). Null = todavía solo local (invitado, sin
     * foto, o la subida falló). */
    val serverId: String? = null,
) {
    val isCommunity: Boolean get() = ownerUserId.startsWith("user-")
}

/** Especie candidata y su fracción del voto ponderado de las 5 referencias más parecidas del paquete. */
@Serializable
data class IdentificationCandidate(
    val scientificName: String,
    val share: Float,
    val genus: String = "",
    val family: String = "",
)

@Serializable
data class FieldSessionRecord(
    val id: String,
    val startedAtEpochMs: Long,
    val closedAtEpochMs: Long? = null,
    val placeLabel: String? = null,
    val latitude: Double? = null,
    val longitude: Double? = null,
    val altitudeLabel: String? = null,
    /** `observations.field_trips.id` una vez subida (solo salidas cerradas y con al menos una
     * observación propia ya en el servidor). Null = todavía solo en el teléfono. */
    val serverId: String? = null,
    /** Lo último que confirmó el servidor (cierre + observaciones vinculadas); si difiere de lo
     * actual, [AnuraRepository.syncFieldTrips] la vuelve a enviar. */
    val syncedSignature: String? = null,
)

@Serializable
data class CommentRecord(
    val id: String,
    val observationId: String,
    val authorUserId: String,
    val authorName: String,
    val body: String,
    val createdAtEpochMs: Long,
    /** null = comentario de primer nivel. */
    val parentId: String? = null,
    /** "agree" | "neutral" | "disagree" — postura real del servidor, ya no una constante fija. */
    val stance: String = "neutral",
    val taxonProposalScientificName: String? = null,
    val taxonProposalCommonName: String? = null,
)

@Serializable
data class SessionNoteRecord(
    val id: String,
    val sessionId: String,
    val observationId: String? = null,
    val body: String,
    val createdAtEpochMs: Long,
)

@Serializable
enum class RegionalPackageStatus {
    Installed,
    Downloading,
    Available,
    Error,
}

@Serializable
data class RegionalPackageRecord(
    val id: String,
    val status: RegionalPackageStatus,
    val progress: Float = 0f,
    val version: String? = null,
    val sha256: String? = null,
    val sizeBytes: Long = 0L,
    val speciesCount: Int = 0,
    val active: Boolean = false,
    val installedAtEpochMs: Long? = null,
    val localPath: String? = null,
)

@Serializable
data class AnuraSnapshot(
    val session: UserSession = UserSession(),
    val observations: List<ObservationRecord> = emptyList(),
    val draft: CaptureDraft = CaptureDraft(),
    val fieldSessions: List<FieldSessionRecord> = emptyList(),
    val activeSessionId: String? = null,
    val favorites: List<String> = emptyList(),
    val comments: List<CommentRecord> = emptyList(),
    val followingIds: List<String> = emptyList(),
    /** Paquetes que conoce este teléfono. El APK no trae ninguno: salen del árbol que publica
     * el servidor (`GET /api/dataset/publico/paquetes`) y se bajan desde Paquetes. */
    val packages: List<RegionalPackageRecord> = emptyList(),
    val blockedUserIds: List<String> = emptyList(),
    val reportedUserIds: List<String> = emptyList(),
    val sessionNotes: List<SessionNoteRecord> = emptyList(),
    /** UUID generado una sola vez por instalación para `POST /api/auth/dispositivos` — no
     * depende de la cuenta: sobrevive a cerrar sesión, igual que `device_key` en el Admin. */
    val deviceKey: String? = null,
    /** Lo que respondió el servidor al último reporte de este dispositivo (C4); false/null
     * hasta el primer reporte. */
    val deviceBlocked: Boolean = false,
    val deviceBlockReason: String? = null,
    /** Avisos de `GET /api/notifications`, más recientes primero — se refrescan al iniciar
     * sesión y al abrir la pantalla de avisos, no en cada recomposición. */
    val notifications: List<AppNotification> = emptyList(),
    val unreadNotifications: Int = 0,
)

/**
 * Alinea los registros persistidos con el catálogo vigente: agrega los paquetes nuevos, descarta los
 * que ya no existen (p. ej. las zonas ficticias de versiones anteriores) y libera descargas que
 * quedaron a medias cuando el proceso murió.
 */
fun reconcilePackages(stored: List<RegionalPackageRecord>, catalogIds: List<String>): List<RegionalPackageRecord> =
    catalogIds.map { id ->
        val record = stored.firstOrNull { it.id == id } ?: RegionalPackageRecord(id, RegionalPackageStatus.Available)
        if (record.status == RegionalPackageStatus.Downloading) {
            record.copy(status = RegionalPackageStatus.Available, progress = 0f)
        } else {
            record
        }
    }

const val GuestUserId = "guest"
const val IdentificationKnown = "known"
const val IdentificationUnknownGenus = "unknown_genus"
const val IdentificationUnknownFamily = "unknown_family"
const val IdentificationUnknownOrder = "unknown_order"
const val PeriodDawn = "dawn"
const val PeriodDay = "day"
const val PeriodDusk = "dusk"
const val PeriodNight = "night"
const val HabitatLeafLitter = "leaf_litter"
const val HabitatLowVegetation = "low_vegetation"
const val HabitatWaterBody = "water_body"
const val HabitatRock = "rock"
const val UsageCuriosity = "curiosity"
const val UsageStudy = "study"
