package me.juanlabs.anura.core.data

import android.app.Application
import android.net.Uri
import androidx.room.Room
import java.io.File
import java.util.UUID
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.serialization.json.Json
import me.juanlabs.anura.core.inference.AnuraIdentifier
import me.juanlabs.anura.core.inference.IdentificationFailure
import me.juanlabs.anura.core.inference.IdentificationOutcome

class AnuraRepository(
    private val dao: SnapshotDao?,
    val media: MediaPersistence?,
    private val persistEnabled: Boolean,
    private val installer: PackageInstaller? = null,
    private val identifier: AnuraIdentifier? = null,
) {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val packageInstallJobs = mutableMapOf<String, Job>()
    private val json = Json {
        ignoreUnknownKeys = true
        encodeDefaults = true
    }
    private val _state = MutableStateFlow(AnuraSnapshot())
    val state: StateFlow<AnuraSnapshot> = _state.asStateFlow()
    val snapshot: AnuraSnapshot get() = _state.value

    private val _messages = MutableSharedFlow<String>(extraBufferCapacity = 4)
    val messages: SharedFlow<String> = _messages.asSharedFlow()

    fun notify(message: String) {
        _messages.tryEmit(message)
    }

    fun hydrate(initial: AnuraSnapshot) {
        _state.value = initial
    }

    fun update(transform: (AnuraSnapshot) -> AnuraSnapshot) {
        var next: AnuraSnapshot? = null
        _state.update { current ->
            transform(current).also { next = it }
        }
        val payload = next ?: return
        if (persistEnabled && dao != null) {
            scope.launch {
                runCatching {
                    dao.save(SnapshotEntity(payload = json.encodeToString(AnuraSnapshot.serializer(), payload)))
                }
            }
        }
    }

    fun enterGuest() {
        update { current ->
            val session = if (current.session.enteredApp && current.session.kind == AccountKind.Guest) {
                current.session
            } else {
                current.session.copy(
                    kind = AccountKind.Guest,
                    userId = current.session.userId.ifBlank { GuestUserId },
                    enteredApp = true,
                )
            }
            current.copy(session = session)
        }
    }

    fun signIn(email: String) {
        update { current ->
            val existing = current.session.takeIf {
                it.email.equals(email.trim(), ignoreCase = true) && it.email.isNotBlank()
            }
            val session = (existing ?: current.session).copy(
                kind = AccountKind.Authenticated,
                email = email.trim(),
                enteredApp = true,
                userId = existing?.userId?.takeIf { it != GuestUserId } ?: UUID.randomUUID().toString(),
            )
            current.copy(session = session)
        }
    }

    fun signUp(name: String, email: String, usage: String?) {
        update { current ->
            val oldId = current.session.userId
            val newId = UUID.randomUUID().toString()
            val migrated = current.observations.map { observation ->
                if (observation.ownerUserId == oldId) {
                    observation.copy(ownerUserId = newId, ownerDisplayName = name.trim())
                } else {
                    observation
                }
            }
            current.copy(
                session = UserSession(
                    kind = AccountKind.Authenticated,
                    userId = newId,
                    displayName = name.trim(),
                    email = email.trim(),
                    usageProfile = usage,
                    enteredApp = true,
                ),
                observations = migrated,
            )
        }
    }

    fun signOut() {
        update { current ->
            current.copy(
                session = current.session.copy(enteredApp = false),
            )
        }
    }

    fun updateProfile(
        displayName: String? = null,
        username: String? = null,
        bio: String? = null,
        location: String? = null,
        photoToken: String? = UNCHANGED,
    ) {
        update { current ->
            val persistedPhoto = if (photoToken != null && photoToken != UNCHANGED && media != null) {
                media.persistPhotoToken(photoToken)
            } else if (photoToken == UNCHANGED) {
                current.session.photoToken
            } else {
                null
            }
            current.copy(
                session = current.session.copy(
                    displayName = displayName ?: current.session.displayName,
                    username = username ?: current.session.username,
                    bio = bio ?: current.session.bio,
                    location = location ?: current.session.location,
                    photoToken = persistedPhoto,
                ),
            )
        }
    }

    fun updateDraft(transform: (CaptureDraft) -> CaptureDraft) {
        update { current -> current.copy(draft = transform(current.draft)) }
    }

    fun resetDraft() {
        val sessionId = snapshot.activeSessionId
        update { it.copy(draft = CaptureDraft(fieldSessionId = sessionId)) }
    }

    fun beginWizard() {
        resetDraft()
        val now = System.currentTimeMillis()
        val hour = java.time.LocalDateTime.now().hour
        updateDraft {
            it.copy(
                observedAtEpochMs = now,
                period = dayPeriodFromHour(hour),
            )
        }
    }

    fun setDraftPhotos(tokens: List<String>) {
        val persisted = tokens.map { token ->
            media?.persistPhotoToken(token) ?: token
        }
        updateDraft { it.copy(photoTokens = persisted) }
    }

    fun setDraftAudio(path: String?, durationMs: Long?) {
        val persisted = when {
            path == null -> null
            path.startsWith("file:") -> media?.persistAudioFile(File(path.removePrefix("file:"))) ?: path
            path.startsWith("content:") || path.startsWith("uri:") -> {
                val uri = Uri.parse(path.removePrefix("uri:"))
                media?.persistAudioUri(uri) ?: path
            }
            else -> media?.persistAudioFile(File(path)) ?: path
        }
        updateDraft { it.copy(audioPath = persisted, audioDurationMs = durationMs) }
    }

    /** Identifica la primera foto del borrador con el paquete regional activo. */
    suspend fun identifyDraftPhoto(): IdentificationOutcome {
        val engine = identifier
            ?: return IdentificationOutcome.Failed(IdentificationFailure.EngineError, "Sin motor de identificación")
        val photo = snapshot.draft.photoTokens.firstOrNull()?.let(MediaPersistence::fileFromToken)
            ?: return IdentificationOutcome.Failed(IdentificationFailure.NoPhoto, "El borrador no tiene foto")
        val pack = snapshot.packages.firstOrNull {
            it.active && it.status == RegionalPackageStatus.Installed && it.localPath != null
        } ?: return IdentificationOutcome.Failed(IdentificationFailure.NoActivePackage, "Ningún paquete activo")
        return engine.identify(
            photo,
            requireNotNull(pack.localPath),
            pack.id,
            latitude = snapshot.draft.latitude,
            longitude = snapshot.draft.longitude,
        )
    }

    fun commitObservation(
        identificationStatus: String,
        identified: IdentificationOutcome.Identified? = null,
    ): String {
        val draft = snapshot.draft
        val session = snapshot.session
        val id = "obs-${UUID.randomUUID().toString().take(8)}"
        // un rechazo del Open Set guarda las candidatas pero nunca atribuye especie
        val named = identified?.takeIf { identificationStatus == IdentificationKnown }
        val species = when {
            named != null -> SpeciesCatalog.all.firstOrNull { it.scientificName == named.scientificName }
            identified == null && identificationStatus == IdentificationKnown -> SpeciesCatalog.find(SimulatedKnownSpeciesId)
            else -> null
        }
        val photos = draft.photoTokens.map { token ->
            media?.persistPhotoToken(token) ?: token
        }
        val audio = draft.audioPath?.let { path ->
            val file = MediaPersistence.fileFromToken(path)
            if (file != null) media?.persistAudioFile(file) ?: path else path
        }
        val record = ObservationRecord(
            id = id,
            ownerUserId = session.userId,
            ownerDisplayName = session.displayName.ifBlank { "" },
            speciesId = species?.id,
            // el paquete no trae nombres comunes: sin ficha en el catálogo se titula con el nombre científico
            commonName = species?.commonName ?: named?.scientificName,
            scientificName = named?.scientificName ?: species?.scientificName,
            photoTokens = photos,
            audioPath = audio,
            audioDurationMs = draft.audioDurationMs,
            latitude = draft.latitude,
            longitude = draft.longitude,
            placeLabel = formatCoordinates(draft.latitude, draft.longitude),
            observedAtEpochMs = draft.observedAtEpochMs,
            svlMm = draft.svlMm,
            habitat = draft.habitat,
            altitudeLabel = draft.altitudeLabel,
            visibilityPublic = false,
            fieldSessionId = draft.fieldSessionId ?: snapshot.activeSessionId,
            identificationStatus = identificationStatus,
            createdAtEpochMs = System.currentTimeMillis(),
            candidates = identified?.candidates.orEmpty().map {
                IdentificationCandidate(it.scientificName, it.share.toFloat(), it.genus, it.family)
            },
        )
        update { current -> current.copy(observations = listOf(record) + current.observations) }
        uploadObservationIfPossible(record)
        resetDraft()
        return id
    }

    /** Sube la observación recién creada a `observation-service` (C3, alcance mínimo). Solo si
     * hay sesión real y tiene al menos una foto: sin sesión (invitado) o sin foto (Audio ID,
     * paso a paso sin cámara) se queda solo local — el servidor exige ambas cosas. */
    private fun uploadObservationIfPossible(record: ObservationRecord) {
        val token = snapshot.session.authToken ?: return
        val photoToken = record.photoTokens.firstOrNull() ?: return
        val photo = MediaPersistence.fileFromToken(photoToken) ?: return
        val topCandidate = record.candidates.firstOrNull()
        scope.launch {
            val serverId = ObservationsRemote.upload(
                photo = photo,
                latitude = record.latitude,
                longitude = record.longitude,
                notes = habitatLabel(record.habitat)?.let { "Hábitat: $it" },
                isPrivate = !record.visibilityPublic,
                aiTopClass = record.scientificName.takeIf { record.identificationStatus == IdentificationKnown },
                aiTopProb = topCandidate?.share?.toDouble(),
                bearer = token,
            ) ?: return@launch
            update { current ->
                current.copy(
                    observations = current.observations.map {
                        if (it.id == record.id) it.copy(serverId = serverId) else it
                    },
                )
            }
        }
    }

    fun observationById(id: String): ObservationRecord? =
        snapshot.observations.find { it.id == id } ?: CommunityCatalog.observation(id)

    fun ownObservations(): List<ObservationRecord> =
        snapshot.observations.filter { it.ownerUserId == snapshot.session.userId }

    /** UUID de este teléfono para `POST /api/auth/dispositivos` — se genera una sola vez y
     * queda en el snapshot (persistido por Room), igual que cualquier otro dato de la app. */
    private fun ensureDeviceKey(): String {
        snapshot.deviceKey?.let { return it }
        val generated = UUID.randomUUID().toString()
        update { it.copy(deviceKey = generated) }
        return generated
    }

    /**
     * Reporta este dispositivo al servidor (C4): modelo, versión de Android, versión de la
     * app, paquetes regionales instalados y espacio libre. Se llama al abrir la app con sesión
     * iniciada y tras cada login (ver `AnuraScaffold`); sin sesión no hace nada.
     */
    suspend fun reportDevice(context: Application): DeviceReportResult {
        val token = snapshot.session.authToken ?: return DeviceReportResult.Failed
        val deviceKey = ensureDeviceKey()
        val paquetes = snapshot.packages
            .filter { it.status == RegionalPackageStatus.Installed }
            .map { pack ->
                DevicePackageEntry(
                    subregion = LocalPackageCatalog.find(pack.id)?.region ?: pack.id,
                    version = pack.version.orEmpty(),
                )
            }
        val espacioLibreMb = runCatching { context.filesDir.freeSpace / (1024L * 1024L) }.getOrNull()
        val versionName = runCatching {
            context.packageManager.getPackageInfo(context.packageName, 0).versionName
        }.getOrNull().orEmpty()
        val result = DeviceRemote.report(
            bearer = token,
            deviceKey = deviceKey,
            modelo = android.os.Build.MODEL.orEmpty(),
            android = android.os.Build.VERSION.RELEASE.orEmpty(),
            appVersion = versionName,
            paquetes = paquetes,
            espacioLibreMb = espacioLibreMb,
        )
        if (result is DeviceReportResult.Ok) {
            update { it.copy(deviceBlocked = result.bloqueado, deviceBlockReason = result.motivo) }
        }
        return result
    }

    /** Avisos propios (C5), para hidratar `snapshot.notifications` al iniciar sesión y al
     * abrir la pantalla de avisos. */
    suspend fun hydrateNotifications() {
        val token = snapshot.session.authToken ?: return
        val response = NotificationsRemote.fetch(token) ?: return
        update { it.copy(notifications = response.avisos, unreadNotifications = response.sin_leer) }
    }

    /** Marca un aviso como leído: optimista en el snapshot, confirmado contra el servidor. */
    fun markNotificationRead(id: String) {
        val current = snapshot.notifications.find { it.id == id } ?: return
        if (current.is_read) return
        update { snap ->
            snap.copy(
                notifications = snap.notifications.map { if (it.id == id) it.copy(is_read = true) else it },
                unreadNotifications = (snap.unreadNotifications - 1).coerceAtLeast(0),
            )
        }
        val token = snapshot.session.authToken ?: return
        scope.launch { NotificationsRemote.markRead(id, token) }
    }

    fun toggleFavorite(id: String) {
        update { current ->
            val next = if (current.favorites.contains(id)) {
                current.favorites - id
            } else {
                current.favorites + id
            }
            current.copy(favorites = next)
        }
    }

    fun isFavorite(id: String): Boolean = snapshot.favorites.contains(id)

    fun toggleFollow(userId: String) {
        update { current ->
            val next = if (current.followingIds.contains(userId)) {
                current.followingIds - userId
            } else {
                current.followingIds + userId
            }
            current.copy(followingIds = next)
        }
    }

    fun isFollowing(userId: String): Boolean = snapshot.followingIds.contains(userId)

    fun deleteObservation(id: String) {
        if (!isOwnObservation(id)) return
        update { current ->
            current.copy(
                observations = current.observations.filterNot { it.id == id },
                favorites = current.favorites.filterNot { it == id },
                comments = current.comments.filterNot { it.observationId == id },
            )
        }
    }

    fun setObservationVisibility(id: String, public: Boolean) {
        if (!isOwnObservation(id)) return
        update { current ->
            current.copy(
                observations = current.observations.map { observation ->
                    if (observation.id == id) observation.copy(visibilityPublic = public) else observation
                },
            )
        }
    }

    fun isOwnObservation(id: String): Boolean {
        val observation = snapshot.observations.find { it.id == id } ?: return false
        return observation.ownerUserId == snapshot.session.userId
    }

    fun requestExpertReview(observationId: String?) {
        val id = observationId ?: snapshot.observations.firstOrNull {
            it.ownerUserId == snapshot.session.userId
        }?.id ?: return
        update { current ->
            current.copy(
                observations = current.observations.map { observation ->
                    if (observation.id == id) observation.copy(expertReviewRequested = true) else observation
                },
            )
        }
    }

    fun startFieldSession(): String {
        val id = "session-${UUID.randomUUID().toString().take(8)}"
        val record = FieldSessionRecord(
            id = id,
            startedAtEpochMs = System.currentTimeMillis(),
        )
        update { current ->
            current.copy(
                fieldSessions = listOf(record) + current.fieldSessions,
                activeSessionId = id,
                draft = current.draft.copy(fieldSessionId = id),
            )
        }
        return id
    }

    fun closeFieldSession() {
        val activeId = snapshot.activeSessionId ?: return
        val now = System.currentTimeMillis()
        update { current ->
            current.copy(
                activeSessionId = null,
                fieldSessions = current.fieldSessions.map { session ->
                    if (session.id == activeId) session.copy(closedAtEpochMs = now) else session
                },
                draft = current.draft.copy(fieldSessionId = null),
            )
        }
    }

    fun addComment(observationId: String, body: String) {
        val trimmed = body.trim()
        if (trimmed.isEmpty()) return
        val session = snapshot.session
        val record = CommentRecord(
            id = "c-${UUID.randomUUID().toString().take(8)}",
            observationId = observationId,
            authorUserId = session.userId,
            authorName = session.displayName.ifBlank { if (session.isGuest) "Invitado" else "Tú" },
            body = trimmed,
            createdAtEpochMs = System.currentTimeMillis(),
        )
        update { current -> current.copy(comments = current.comments + record) }
    }

    fun commentsFor(observationId: String): List<CommentRecord> =
        snapshot.comments.filter { it.observationId == observationId }

    fun addSessionNote(sessionId: String, body: String, observationId: String? = null) {
        val trimmed = body.trim()
        if (trimmed.isEmpty()) return
        val record = SessionNoteRecord(
            id = "n-${UUID.randomUUID().toString().take(8)}",
            sessionId = sessionId,
            observationId = observationId,
            body = trimmed,
            createdAtEpochMs = System.currentTimeMillis(),
        )
        update { current -> current.copy(sessionNotes = current.sessionNotes + record) }
    }

    fun reportUser(userId: String) {
        update { current ->
            current.copy(reportedUserIds = (current.reportedUserIds + userId).distinct())
        }
    }

    fun blockUser(userId: String) {
        update { current ->
            current.copy(
                blockedUserIds = (current.blockedUserIds + userId).distinct(),
                followingIds = current.followingIds.filterNot { it == userId },
            )
        }
    }

    private fun updatePackage(id: String, transform: (RegionalPackageRecord) -> RegionalPackageRecord) {
        update { current ->
            current.copy(packages = current.packages.map { pack -> if (pack.id == id) transform(pack) else pack })
        }
    }

    fun setPackageDownloading(id: String) {
        val manifest = LocalPackageCatalog.find(id)
        val engine = installer
        if (manifest == null || engine == null) {
            failPackage(id)
            return
        }
        updatePackage(id) { it.copy(status = RegionalPackageStatus.Downloading, progress = 0f) }
        packageInstallJobs[id]?.cancel()
        packageInstallJobs[id] = scope.launch {
            val result = engine.install(manifest) { fraction ->
                updatePackage(id) { pack ->
                    if (pack.status == RegionalPackageStatus.Downloading) pack.copy(progress = fraction) else pack
                }
            }
            when (result) {
                is PackageInstallResult.Success -> updatePackage(id) { pack ->
                    pack.copy(
                        status = RegionalPackageStatus.Installed,
                        progress = 1f,
                        version = manifest.version,
                        sha256 = result.sha256,
                        sizeBytes = result.sizeBytes,
                        speciesCount = manifest.speciesCount,
                        installedAtEpochMs = result.installedAtEpochMs,
                        localPath = result.localPath,
                    )
                }
                is PackageInstallResult.Failure -> {
                    notify(result.reason)
                    failPackage(id)
                }
            }
            packageInstallJobs.remove(id)
        }
    }

    fun failPackage(id: String) {
        updatePackage(id) { it.copy(status = RegionalPackageStatus.Error, progress = 0f) }
    }

    fun cancelPackage(id: String) {
        packageInstallJobs.remove(id)?.cancel()
        updatePackage(id) { it.copy(status = RegionalPackageStatus.Available, progress = 0f) }
    }

    fun uninstallPackage(id: String) {
        packageInstallJobs.remove(id)?.cancel()
        installer?.uninstall(id)
        updatePackage(id) {
            it.copy(
                status = RegionalPackageStatus.Available,
                progress = 0f,
                active = false,
                version = null,
                sha256 = null,
                sizeBytes = 0L,
                speciesCount = 0,
                installedAtEpochMs = null,
                localPath = null,
            )
        }
    }

    /** Activa este paquete para identificación y desactiva cualquier otro (uno a la vez). */
    fun activatePackage(id: String) {
        update { current ->
            current.copy(
                packages = current.packages.map { pack ->
                    when {
                        pack.id == id && pack.status == RegionalPackageStatus.Installed -> pack.copy(active = true)
                        pack.id != id -> pack.copy(active = false)
                        else -> pack
                    }
                },
            )
        }
    }

    fun deactivatePackage(id: String) {
        updatePackage(id) { it.copy(active = false) }
    }

    companion object {
        const val UNCHANGED = "__unchanged__"

        @Volatile
        lateinit var instance: AnuraRepository
            private set

        val isInitialized: Boolean get() = ::instance.isInitialized

        fun create(application: Application): AnuraRepository {
            val db = Room.databaseBuilder(
                application,
                AnuraDatabase::class.java,
                "anura.db",
            ).fallbackToDestructiveMigration(dropAllTables = true).build()
            val repo = AnuraRepository(
                dao = db.snapshotDao(),
                media = MediaPersistence(application),
                persistEnabled = true,
                installer = PackageInstaller(application),
                identifier = AnuraIdentifier(application),
            )
            instance = repo
            repo.scope.launch {
                val stored = runCatching { db.snapshotDao().load() }.getOrNull()
                if (stored != null) {
                    val parsed = runCatching {
                        repo.json.decodeFromString(AnuraSnapshot.serializer(), stored.payload)
                    }.getOrNull()
                    if (parsed != null) {
                        repo._state.value = parsed.copy(
                            packages = reconcilePackages(parsed.packages, LocalPackageCatalog.manifests.map { it.id }),
                        )
                    }
                }
            }
            return repo
        }

        fun preview(): AnuraRepository {
            return AnuraRepository(dao = null, media = null, persistEnabled = false)
        }
    }
}
