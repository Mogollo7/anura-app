package me.juanlabs.anura.core.data

import android.app.Application
import android.net.Uri
import androidx.room.Room
import java.io.File
import java.util.UUID
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlin.coroutines.coroutineContext
import kotlinx.serialization.json.Json
import me.juanlabs.anura.core.auth.AnuraServerConfig
import me.juanlabs.anura.core.inference.AnuraIdentifier
import me.juanlabs.anura.core.inference.IdentificationEnsemble
import me.juanlabs.anura.core.inference.IdentificationFailure
import me.juanlabs.anura.core.inference.IdentificationOutcome
import me.juanlabs.anura.core.key.ClaveDocumento

class AnuraRepository(
    private val dao: SnapshotDao?,
    val media: MediaPersistence?,
    private val persistEnabled: Boolean,
    private val installer: PackageInstaller? = null,
    private val identifier: AnuraIdentifier? = null,
) {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val packageInstallJobs = mutableMapOf<String, Job>()
    private val _packageTree = MutableStateFlow<List<PackageNode>>(emptyList())
    val packageTree: StateFlow<List<PackageNode>> = _packageTree.asStateFlow()
    private val _packageCatalogState = MutableStateFlow<PackageCatalogState>(PackageCatalogState.Loading)
    val packageCatalogState: StateFlow<PackageCatalogState> = _packageCatalogState.asStateFlow()
    private val uploadsInFlight = java.util.Collections.synchronizedSet(mutableSetOf<String>())
    private val json = Json {
        ignoreUnknownKeys = true
        encodeDefaults = true
    }
    private val _state = MutableStateFlow(AnuraSnapshot())
    val state: StateFlow<AnuraSnapshot> = _state.asStateFlow()
    val snapshot: AnuraSnapshot get() = _state.value

    /**
     * true en cuanto se intentó restaurar la sesión guardada en Room (haya o no datos). El
     * NavHost espera este flag antes de decidir si saltarse el login — sin él, el arranque
     * siempre caía en AuthGraph porque `_state` parte en `AnuraSnapshot()` (sesión vacía) y
     * la carga real de Room es asíncrona (ver `create()`).
     */
    private val _hydrated = MutableStateFlow(!persistEnabled)
    val hydrated: StateFlow<Boolean> = _hydrated.asStateFlow()

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

    /**
     * Login real (Google por Custom Tabs, ver core/auth/ServerAuth.kt): `claims` viene del JWT
     * que ya validó auth-service, no de un formulario local. Reemplaza el userId de invitado
     * por el id real del servidor, para que las observaciones de antes de iniciar sesión
     * puedan migrarse igual que en [signUp].
     */
    fun signInWithToken(token: String, claims: me.juanlabs.anura.core.auth.JwtClaims) {
        update { current ->
            val oldId = current.session.userId
            val newId = claims.id ?: oldId
            val migrated = if (newId != oldId) {
                current.observations.map { observation ->
                    if (observation.ownerUserId == oldId) observation.copy(ownerUserId = newId) else observation
                }
            } else {
                current.observations
            }
            current.copy(
                session = current.session.copy(
                    kind = AccountKind.Authenticated,
                    userId = newId,
                    email = claims.email ?: current.session.email,
                    username = claims.username ?: current.session.username,
                    displayName = current.session.displayName.ifBlank { claims.username ?: claims.email ?: "" },
                    enteredApp = true,
                    authToken = token,
                ),
                observations = migrated,
            )
        }
        scope.launch { hydrateFavorites() }
    }

    /**
     * Correo y contraseña contra auth-service. Devuelve null si inició sesión o el texto que
     * hay que mostrarle a la persona si no.
     */
    suspend fun signInWithPassword(email: String, password: String, offlineMessage: String): String? =
        finishPasswordAuth(me.juanlabs.anura.core.auth.AuthRemote.login(email.trim(), password), offlineMessage)

    /** Crea la cuenta en auth-service e inicia sesión con ella. Mismo contrato que [signInWithPassword]. */
    suspend fun signUpWithPassword(
        name: String,
        email: String,
        password: String,
        usage: String?,
        offlineMessage: String,
    ): String? {
        val result = me.juanlabs.anura.core.auth.AuthRemote.register(usernameFrom(name), email.trim(), password)
        val error = finishPasswordAuth(result, offlineMessage)
        if (error == null) {
            update { it.copy(session = it.session.copy(displayName = name.trim(), usageProfile = usage)) }
        }
        return error
    }

    private fun finishPasswordAuth(result: me.juanlabs.anura.core.auth.AuthRemote.Result, offlineMessage: String): String? =
        when (result) {
            is me.juanlabs.anura.core.auth.AuthRemote.Result.Ok -> {
                val claims = me.juanlabs.anura.core.auth.decodeJwtClaims(result.token)
                if (claims == null) {
                    offlineMessage
                } else {
                    signInWithToken(result.token, claims)
                    null
                }
            }
            is me.juanlabs.anura.core.auth.AuthRemote.Result.Rejected -> result.message
            me.juanlabs.anura.core.auth.AuthRemote.Result.Offline -> offlineMessage
        }

    /** "María José Pérez" → "maria_jose_perez"; el servidor agrega un número si ya existe. */
    private fun usernameFrom(name: String): String? =
        java.text.Normalizer.normalize(name.trim().lowercase(), java.text.Normalizer.Form.NFD)
            .replace(Regex("\\p{M}+"), "")
            .replace(Regex("[^a-z0-9]+"), "_")
            .trim('_')
            .take(30)
            .ifBlank { null }

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

    /**
     * Identifica las fotos del borrador con el paquete activo. Varias tomas del mismo
     * individuo se fusionan a posteriori; el motor por foto no cambia.
     */
    suspend fun identifyDraftPhoto(): IdentificationOutcome {
        return try {
            val engine = identifier
                ?: return IdentificationOutcome.Failed(IdentificationFailure.EngineError, "Sin motor de identificación")
            val photos = snapshot.draft.photoTokens.mapNotNull(MediaPersistence::fileFromToken)
            if (photos.isEmpty()) {
                return IdentificationOutcome.Failed(IdentificationFailure.NoPhoto, "El borrador no tiene foto")
            }
            val pack = snapshot.packages.firstOrNull {
                it.active && it.status == RegionalPackageStatus.Installed && it.localPath != null
            } ?: return IdentificationOutcome.Failed(IdentificationFailure.NoActivePackage, "Ningún paquete activo")
            val path = pack.localPath
                ?: return IdentificationOutcome.Failed(IdentificationFailure.NoActivePackage, "Ningún paquete activo")
            val outcomes = photos.take(MaxPhotosForIdentification).map { photo ->
                engine.identify(
                    photo,
                    path,
                    latitude = snapshot.draft.latitude,
                    longitude = snapshot.draft.longitude,
                )
            }
            IdentificationEnsemble.combine(outcomes)
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (error: Exception) {
            IdentificationOutcome.Failed(
                IdentificationFailure.EngineError,
                error.message ?: error.javaClass.simpleName,
            )
        }
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
            // Solo las candidatas que calculó el motor: sin identificación real no hay porcentajes.
            candidates = identified?.candidates.orEmpty().map {
                SpeciesCatalog.asCandidate(it.scientificName, it.share.toFloat(), it.genus, it.family)
            },
        )
        update { current -> current.copy(observations = listOf(record) + current.observations) }
        uploadObservationIfPossible(record)
        resetDraft()
        return id
    }

    /** Sube la observación recién creada a `observation-service` (C3, alcance mínimo). Solo si
     * hay sesión real y tiene al menos una foto: sin sesión (invitado) o sin foto (Audio ID,
     * paso a paso sin cámara) se queda solo local — el servidor exige ambas cosas.
     * Si ya hay una subida de este id en curso, no lanza otra.
     * Tras POST confirmado con `serverId`, libera la foto local pesada y deja `photoUrl` remota. */
    private fun uploadObservationIfPossible(record: ObservationRecord) {
        val token = snapshot.session.authToken ?: return
        if (snapshot.deviceBlocked) return
        if (record.serverId != null) return
        val photoToken = record.photoTokens.firstOrNull() ?: return
        val photo = MediaPersistence.fileFromToken(photoToken) ?: return
        if (!uploadsInFlight.add(record.id)) return
        val topCandidate = record.candidates.firstOrNull()
        scope.launch {
            try {
                val latest = snapshot.observations.find { it.id == record.id } ?: record
                val uploaded = ObservationsRemote.upload(
                    photo = photo,
                    latitude = latest.latitude,
                    longitude = latest.longitude,
                    notes = observationNotes(latest),
                    isPrivate = !latest.visibilityPublic,
                    aiTopClass = latest.scientificName.takeIf { latest.identificationStatus == IdentificationKnown },
                    aiTopProb = topCandidate?.share?.toDouble(),
                    bearer = token,
                ) ?: return@launch
                val remotePhoto = uploaded.thumbnailUrl ?: uploaded.imageUrl
                val localPhotos = latest.photoTokens
                // Persistir serverId + URL remota y vaciar tokens locales ANTES de borrar archivos,
                // para que la ficha nunca quede sin imagen si el delete falla a medias.
                update { current ->
                    current.copy(
                        observations = current.observations.map {
                            if (it.id == record.id) {
                                it.copy(
                                    serverId = uploaded.observationId,
                                    photoUrl = remotePhoto ?: it.photoUrl,
                                    photoTokens = emptyList(),
                                )
                            } else {
                                it
                            }
                        },
                    )
                }
                localPhotos.forEach { MediaPersistence.deleteLocalFile(it) }
                val published = snapshot.observations.find { it.id == record.id }
                if (published != null && published.visibilityPublic != latest.visibilityPublic) {
                    ObservationsRemote.updateVisibility(
                        uploaded.observationId,
                        isPrivate = !published.visibilityPublic,
                        bearer = token,
                    )
                }
                if (record.fieldSessionId != null) syncFieldTrips()
            } finally {
                uploadsInFlight.remove(record.id)
            }
        }
    }

    /** Reintenta las observaciones propias que se quedaron solo en el teléfono (sin red, o la
     * subida anterior falló). También libera fotos locales de las que ya tienen `serverId`
     * (subidas en una sesión anterior) sustituyéndolas por la miniatura del servidor. */
    fun syncPendingObservations() {
        if (snapshot.session.authToken == null || snapshot.deviceBlocked) return
        snapshot.observations
            .filter {
                it.serverId == null &&
                    it.photoTokens.isNotEmpty() &&
                    it.ownerUserId == snapshot.session.userId &&
                    !it.isDraft
            }
            .forEach { uploadObservationIfPossible(it) }
        snapshot.observations
            .filter {
                it.serverId != null &&
                    it.photoTokens.isNotEmpty() &&
                    it.ownerUserId == snapshot.session.userId
            }
            .forEach { releaseLocalMediaIfSynced(it) }
        syncFieldTrips()
    }

    /**
     * Sube al servidor las salidas de campo ya cerradas (`POST /api/observations/field-trips`)
     * con las observaciones propias que ya están allá. Sin sesión, sin red o sin observaciones
     * subidas todavía, la salida queda pendiente y se reintenta desde [syncPendingObservations]
     * y cuando termina de subir una observación de la salida. Idempotente: solo reenvía si cambió
     * el cierre o el conjunto de observaciones ([FieldSessionRecord.syncedSignature]).
     */
    fun syncFieldTrips() {
        val token = snapshot.session.authToken ?: return
        if (snapshot.deviceBlocked) return
        val userId = snapshot.session.userId
        snapshot.fieldSessions.filter { it.closedAtEpochMs != null }.forEach { session ->
            val serverIds = snapshot.observations
                .filter { it.fieldSessionId == session.id && it.ownerUserId == userId && !it.isDraft }
                .mapNotNull { it.serverId }
                .distinct()
                .sorted()
            if (serverIds.isEmpty()) return@forEach
            val signature = "${session.closedAtEpochMs}:${serverIds.joinToString(",")}"
            if (session.syncedSignature == signature) return@forEach
            val key = "trip-${session.id}"
            if (!uploadsInFlight.add(key)) return@forEach
            scope.launch {
                try {
                    val tripId = FieldTripsRemote.upsert(
                        clientId = session.id,
                        startedAtEpochMs = session.startedAtEpochMs,
                        endedAtEpochMs = session.closedAtEpochMs,
                        placeLabel = session.placeLabel,
                        latitude = session.latitude,
                        longitude = session.longitude,
                        observationServerIds = serverIds,
                        bearer = token,
                    ) ?: return@launch
                    update { current ->
                        current.copy(
                            fieldSessions = current.fieldSessions.map {
                                if (it.id == session.id) it.copy(serverId = tripId, syncedSignature = signature) else it
                            },
                        )
                    }
                } finally {
                    uploadsInFlight.remove(key)
                }
            }
        }
    }

    /**
     * Observación ya en el servidor pero con archivos locales todavía: borra la foto pesada
     * y deja `photoUrl` (miniatura remota). No borra la fila ni el `serverId`. Si no hay URL
     * remota aún, la pide a explorer-service; si falla, no borra nada.
     * El audio no se sube en el POST actual — se conserva en el teléfono.
     */
    private fun releaseLocalMediaIfSynced(record: ObservationRecord) {
        val serverId = record.serverId ?: return
        if (record.photoTokens.isEmpty()) return
        if (!uploadsInFlight.add("reclaim-${record.id}")) return
        scope.launch {
            try {
                var remotePhoto = record.photoUrl
                if (remotePhoto.isNullOrBlank()) {
                    remotePhoto = ExplorerRemote.observation(serverId)?.let {
                        ExplorerRemote.thumbUrl(it.thumbnail_key ?: it.image_key, size = "large")
                    }
                }
                if (remotePhoto.isNullOrBlank()) return@launch
                val localPhotos = record.photoTokens
                update { current ->
                    current.copy(
                        observations = current.observations.map {
                            if (it.id == record.id) {
                                it.copy(photoUrl = remotePhoto, photoTokens = emptyList())
                            } else {
                                it
                            }
                        },
                    )
                }
                localPhotos.forEach { MediaPersistence.deleteLocalFile(it) }
            } finally {
                uploadsInFlight.remove("reclaim-${record.id}")
            }
        }
    }

    suspend fun awaitHydrated() {
        hydrated.first { it }
    }

    private fun observationNotes(record: ObservationRecord): String? {
        val parts = buildList {
            habitatLabel(record.habitat)?.let { add("Hábitat: $it") }
            record.svlMm?.let { add("LHC: $it mm") }
            record.altitudeLabel?.takeIf { it.isNotBlank() }?.let { add("Altitud: $it") }
        }
        return parts.joinToString(". ").ifBlank { null }
    }

    fun observationById(id: String): ObservationRecord? = snapshot.observations.find { it.id == id }

    /** Cuando no es una observación propia/local: se pide de verdad al servidor
     * (`GET /api/explorer/observation/:id`) — ya no hay `CommunityCatalog` de respaldo. */
    suspend fun fetchRemoteObservation(id: String): ObservationRecord? =
        ExplorerRemote.observation(id)?.toObservationRecord()

    fun ownObservations(): List<ObservationRecord> =
        snapshot.observations.filter { it.ownerUserId == snapshot.session.userId }

    /** Favoritos propios reales, para hidratar `snapshot.favorites` al iniciar sesión. */
    suspend fun hydrateFavorites() {
        val token = snapshot.session.authToken ?: return
        val remoteIds = AnuraApi.get<List<String>>("/api/explorer/favorites", token) ?: return
        update { current -> current.copy(favorites = remoteIds) }
    }

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
                    subregion = findPackage(_packageTree.value, pack.id)?.nombre ?: pack.id,
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

    /**
     * Avisos propios (C5), para hidratar `snapshot.notifications` al iniciar sesión y al abrir
     * la pantalla de avisos. Con [context] (Activity en primer plano o `applicationContext`
     * desde `AvisosPollWorker` en segundo plano) también materializa como notificación real del
     * sistema cada aviso sin leer que no estuviera ya en el snapshot — así no se repite en cada
     * hidratación, solo la primera vez que el teléfono se entera de que existe.
     */
    suspend fun hydrateNotifications(context: android.content.Context? = null) {
        val token = snapshot.session.authToken ?: return
        val response = NotificationsRemote.fetch(token) ?: return
        val previouslySeenIds = snapshot.notifications.mapTo(mutableSetOf()) { it.id }
        update { it.copy(notifications = response.avisos, unreadNotifications = response.sin_leer) }
        if (context != null) {
            response.avisos
                .filter { !it.is_read && it.id !in previouslySeenIds }
                .forEach { me.juanlabs.anura.core.notifications.AnuraNotifications.show(context, it) }
        }
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

    /** Elimina un aviso propio: optimista en el snapshot, confirmado contra el servidor. */
    fun deleteNotification(id: String) {
        val removed = snapshot.notifications.find { it.id == id } ?: return
        update { snap ->
            snap.copy(
                notifications = snap.notifications.filterNot { it.id == id },
                unreadNotifications = if (!removed.is_read) {
                    (snap.unreadNotifications - 1).coerceAtLeast(0)
                } else {
                    snap.unreadNotifications
                },
            )
        }
        val token = snapshot.session.authToken ?: return
        scope.launch { NotificationsRemote.delete(id, token) }
    }

    fun toggleFavorite(id: String) {
        val wasFavorite = snapshot.favorites.contains(id)
        update { current ->
            val next = if (wasFavorite) current.favorites - id else current.favorites + id
            current.copy(favorites = next)
        }
        val token = snapshot.session.authToken ?: return
        scope.launch {
            val liked = AnuraApi.post<FavoriteToggleResponse>("/api/explorer/favorites/$id", bearer = token)?.liked
            // El servidor manda: si no coincide con lo optimista (falló, u otra sesión cambió el
            // estado mientras tanto), se corrige sin volver a pedir confirmación al usuario.
            if (liked != null && liked != !wasFavorite) {
                update { current ->
                    val corrected = if (liked) current.favorites + id else current.favorites - id
                    current.copy(favorites = corrected)
                }
            }
        }
    }

    fun isFavorite(id: String): Boolean = snapshot.favorites.contains(id)

    /** [username] real (`auth.users.username`), no un id inventado de `CommunityCatalog`. */
    fun toggleFollow(username: String) {
        val wasFollowing = snapshot.followingIds.contains(username)
        update { current ->
            val next = if (wasFollowing) current.followingIds - username else current.followingIds + username
            current.copy(followingIds = next)
        }
        val token = snapshot.session.authToken ?: return
        scope.launch {
            val following = AuthRemote.toggleFollow(username, token)
            if (following != null && following != !wasFollowing) {
                update { current ->
                    val corrected = if (following) current.followingIds + username else current.followingIds - username
                    current.copy(followingIds = corrected)
                }
            }
        }
    }

    fun isFollowing(username: String): Boolean = snapshot.followingIds.contains(username)

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
        val serverId = snapshot.observations.find { it.id == id }?.serverId
        update { current ->
            current.copy(
                observations = current.observations.map { observation ->
                    if (observation.id == id) observation.copy(visibilityPublic = public) else observation
                },
            )
        }
        val token = snapshot.session.authToken ?: return
        val remoteId = serverId ?: return
        scope.launch { ObservationsRemote.updateVisibility(remoteId, isPrivate = !public, bearer = token) }
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
        syncFieldTrips()
    }

/**
     * [stance]: solo "disagree" cuando trae [taxonProposalScientificName] (refutar con otra
     * especie), "neutral" en cualquier otro caso — la app nunca deja elegir postura a mano,
     * mismo criterio que ya vale para la web (`commentsStore.js`).
     */
    fun addComment(
        observationId: String,
        body: String,
        parentId: String? = null,
        taxonProposalScientificName: String? = null,
        taxonProposalCommonName: String? = null,
    ) {
        val trimmed = body.trim()
        if (trimmed.isEmpty() && taxonProposalScientificName == null) return
        val session = snapshot.session
        val stance = if (taxonProposalScientificName != null) "disagree" else "neutral"
        val localId = "local-${UUID.randomUUID()}"
        val optimistic = CommentRecord(
            id = localId,
            observationId = observationId,
            authorUserId = session.userId,
            authorName = session.displayName.ifBlank { session.username.ifBlank { if (session.isGuest) "Invitado" else "Tú" } },
            body = trimmed,
            createdAtEpochMs = System.currentTimeMillis(),
            parentId = parentId,
            stance = stance,
            taxonProposalScientificName = taxonProposalScientificName,
            taxonProposalCommonName = taxonProposalCommonName,
        )
        update { current -> current.copy(comments = current.comments + optimistic) }
        val token = session.authToken ?: return
        scope.launch {
            val posted = CommentsRemote.post(
                observationId = observationId,
                body = trimmed,
                stance = stance,
                parentId = parentId,
                taxonProposalScientificName = taxonProposalScientificName,
                taxonProposalCommonName = taxonProposalCommonName,
                bearer = token,
            )
            if (posted != null) {
                val real = posted.toCommentRecord(observationId)
                update { current ->
                    current.copy(comments = current.comments.map { if (it.id == localId) real else it })
                }
            }
        }
    }

    fun commentsFor(observationId: String): List<CommentRecord> =
        snapshot.comments.filter { it.observationId == observationId }

    /** Trae los comentarios reales del servidor y reemplaza el caché local de esta observación
     * (conserva cualquier envío optimista `local-*` que todavía no haya vuelto del servidor). */
    suspend fun refreshComments(observationId: String) {
        val remote = CommentsRemote.list(observationId).map { it.toCommentRecord(observationId) }
        update { current ->
            val pendingLocal = current.comments.filter {
                it.observationId == observationId && it.id.startsWith("local-")
            }
            val others = current.comments.filterNot { it.observationId == observationId }
            current.copy(comments = others + remote + pendingLocal)
        }
    }

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
            val existing = current.packages.find { it.id == id }
            val next = if (existing == null) {
                current.packages + transform(RegionalPackageRecord(id, RegionalPackageStatus.Available))
            } else {
                current.packages.map { pack -> if (pack.id == id) transform(pack) else pack }
            }
            current.copy(packages = next)
        }
    }

    /** Lee el árbol país → departamento → subregión. Sin catálogo no se inventa una lista. */
    suspend fun refreshPackageCatalog() {
        if (!persistEnabled) {
            _packageCatalogState.value = PackageCatalogState.Ready
            return
        }
        _packageCatalogState.value = PackageCatalogState.Loading
        val response = AnuraApi.get<PackageCatalogResponse>("/api/dataset/publico/paquetes")
        if (response == null) {
            _packageCatalogState.value = PackageCatalogState.Failed("No se pudo leer el catálogo de paquetes")
            return
        }
        _packageTree.value = response.paises
        val ids = response.paises.flatMap(::flattenPackages).map { it.id }
        if (ids.isNotEmpty()) {
            update { it.copy(packages = reconcilePackages(it.packages, ids)) }
        }
        _packageCatalogState.value = PackageCatalogState.Ready
    }

    /**
     * Baja el nodo y, si es país o departamento, también los archivos de sus hijos.
     * Cada archivo sale del servidor y se comprueba el sha256.
     */
    fun downloadPackage(id: String) {
        val root = findPackage(_packageTree.value, id)
        val engine = installer
        if (root == null || engine == null) {
            failPackage(id)
            return
        }
        val files = flattenPackages(root).filter { !it.archivoUrl.isNullOrBlank() && !it.sha256.isNullOrBlank() }
        if (files.isEmpty()) {
            notify("Ese nivel no tiene un archivo para descargar")
            return
        }
        packageInstallJobs[id]?.cancel()
        packageInstallJobs[id] = scope.launch {
            try {
                for (file in files) {
                    ensureActive()
                    val current = snapshot.packages.find { it.id == file.id }
                    if (current?.status == RegionalPackageStatus.Installed &&
                        current.sha256 == file.sha256 &&
                        !current.localPath.isNullOrBlank()
                    ) {
                        continue
                    }
                    updatePackage(file.id) { it.copy(status = RegionalPackageStatus.Downloading, progress = 0f) }
                    val url = file.archivoUrl.orEmpty().let { path ->
                        if (path.startsWith("http")) path else AnuraServerConfig.AUTH_BASE_URL + path
                    }
                    val fileName = if (file.formato == "sqlite") "package.sqlite" else "catalogo.json"
                    val result = engine.installFromUrl(
                        id = file.id,
                        version = file.version ?: "1",
                        url = url,
                        expectedSha256 = file.sha256.orEmpty(),
                        expectedBytes = file.sizeArchivo.takeIf { it > 0 } ?: file.sizeBytes,
                        fileName = fileName,
                    ) { fraction ->
                        updatePackage(file.id) { pack ->
                            if (pack.status == RegionalPackageStatus.Downloading) pack.copy(progress = fraction) else pack
                        }
                    }
                    when (result) {
                        is PackageInstallResult.Success -> {
                            if (file.formato == "sqlite") {
                                runCatching { engine.refreshClave(file.id, file.version ?: "1") }
                            }
                            updatePackage(file.id) { pack ->
                                // El primer paquete de identificación que se instala queda activo: sin
                                // eso la identificación seguiría diciendo que falta un paquete.
                                val noneActive = snapshot.packages.none {
                                    it.id != file.id && it.active && it.status == RegionalPackageStatus.Installed
                                }
                                pack.copy(
                                    status = RegionalPackageStatus.Installed,
                                    progress = 1f,
                                    version = file.version,
                                    sha256 = result.sha256,
                                    sizeBytes = result.sizeBytes,
                                    speciesCount = file.especies ?: pack.speciesCount,
                                    installedAtEpochMs = result.installedAtEpochMs,
                                    localPath = result.localPath,
                                    active = file.formato == "sqlite" && (pack.active || noneActive),
                                )
                            }
                        }
                        is PackageInstallResult.Failure -> {
                            notify(result.reason)
                            failPackage(file.id)
                        }
                    }
                }
            } catch (cancelled: CancellationException) {
                flattenPackages(root).forEach { file ->
                    updatePackage(file.id) { pack ->
                        if (pack.status == RegionalPackageStatus.Downloading) {
                            pack.copy(status = RegionalPackageStatus.Available, progress = 0f)
                        } else {
                            pack
                        }
                    }
                }
                throw cancelled
            } finally {
                val self = coroutineContext[Job]
                if (packageInstallJobs[id] === self) packageInstallJobs.remove(id)
            }
        }
    }

    fun cachedClave(packageId: String, version: String): ClaveDocumento? =
        installer?.readClave(packageId, version)

    suspend fun refreshClave(packageId: String, version: String): ClaveDocumento? =
        installer?.refreshClave(packageId, version)

    fun setPackageDownloading(id: String) = downloadPackage(id)

    fun failPackage(id: String) {
        updatePackage(id) { it.copy(status = RegionalPackageStatus.Error, progress = 0f) }
    }

    fun cancelPackage(id: String) {
        val keys = packageInstallJobs.keys.filter { jobId ->
            val root = findPackage(_packageTree.value, jobId)
            jobId == id || (root != null && flattenPackages(root).any { it.id == id })
        }
        val jobs = (if (keys.isEmpty()) listOf(id) else keys).mapNotNull { key ->
            packageInstallJobs.remove(key)
        }
        if (jobs.isEmpty()) {
            updatePackage(id) { it.copy(status = RegionalPackageStatus.Available, progress = 0f) }
        } else {
            jobs.forEach { it.cancel() }
        }
    }

    fun uninstallPackage(id: String) {
        cancelPackage(id)
        val node = findPackage(_packageTree.value, id)
        val ids = if (node != null) flattenPackages(node).map { it.id } else listOf(id)
        ids.forEach { childId ->
            installer?.uninstall(childId)
            updatePackage(childId) {
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
    }

    /** Activa el sqlite de identificación y desactiva cualquier otro. Un catálogo JSON no identifica. */
    fun activatePackage(id: String) {
        val node = findPackage(_packageTree.value, id)
        if (node?.formato == "json") return
        val path = snapshot.packages.find { it.id == id }?.localPath
        if (path != null && !path.endsWith("package.sqlite")) return
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
        private const val MaxPhotosForIdentification = 8
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
                            // Los ids salen del árbol del servidor; aquí solo se liberan descargas
                            // que quedaron a medias. Se alinean al pedir el árbol.
                            packages = reconcilePackages(parsed.packages, parsed.packages.map { it.id }),
                        )
                    }
                }
                repo._hydrated.value = true
            }
            return repo
        }

        fun preview(): AnuraRepository {
            return AnuraRepository(dao = null, media = null, persistEnabled = false)
        }
    }
}
