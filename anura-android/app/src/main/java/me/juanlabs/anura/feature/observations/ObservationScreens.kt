package me.juanlabs.anura.feature.observations

import android.content.Intent
import kotlin.math.roundToInt
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.exclude
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.ime
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.GridItemSpan
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.produceState
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.R
import me.juanlabs.anura.core.data.ContentCatalog
import me.juanlabs.anura.core.data.ExplorerRemote
import me.juanlabs.anura.core.data.IdentificationKnown
import me.juanlabs.anura.core.data.ObservationRecord
import me.juanlabs.anura.core.data.SpeciesCatalog
import me.juanlabs.anura.core.data.formatCoordinates
import me.juanlabs.anura.core.data.formatObservationDate
import me.juanlabs.anura.core.data.formatObservationWhen
import me.juanlabs.anura.core.auth.AnuraServerConfig
import me.juanlabs.anura.core.data.rememberAnuraRepository
import me.juanlabs.anura.core.data.rememberSpeciesPhotoPainter
import me.juanlabs.anura.core.platform.rememberNetworkAvailable
import me.juanlabs.anura.designsystem.component.AnuraCard
import me.juanlabs.anura.designsystem.component.AnuraConfirmSheet
import me.juanlabs.anura.designsystem.component.AnuraConservationChip
import me.juanlabs.anura.designsystem.component.AnuraEmptyState
import me.juanlabs.anura.designsystem.component.AnuraToxicityChip
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraFormButtonStyle
import me.juanlabs.anura.designsystem.component.AnuraSectionLabel
import me.juanlabs.anura.designsystem.component.AnuraTextField
import me.juanlabs.anura.designsystem.component.AnuraTopBar
import me.juanlabs.anura.designsystem.component.LocalAnuraTabBarInset
import me.juanlabs.anura.designsystem.component.ObservationCard
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode
import me.juanlabs.anura.feature.capture.AnuraReviewChip
import me.juanlabs.anura.feature.comments.ObservationCommentsOverlay
import me.juanlabs.anura.feature.fieldsession.FieldSessionRecordNotes
import me.juanlabs.anura.feature.explore.ObservationCatalogScreen
import me.juanlabs.anura.feature.species.IdentificationJustificationSheet

private val ObservationHeroHeight = 280.dp

/** Feed de observaciones — pestaña Explorar (tab 2). Las especies van en Listado. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ObservationsScreen(
    onOpenObservationDetail: (String) -> Unit,
) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val online = rememberNetworkAvailable()
    var query by rememberSaveable { mutableStateOf("") }
    fun matches(observation: ObservationRecord): Boolean {
        val needle = query.trim()
        if (needle.isEmpty()) return true
        val species = SpeciesCatalog.find(observation.speciesId)
        val common = observation.commonName ?: species?.commonName.orEmpty()
        val scientific = observation.scientificName ?: species?.scientificName.orEmpty()
        return common.contains(needle, ignoreCase = true) ||
            scientific.contains(needle, ignoreCase = true)
    }
    val communityFeed by produceState(initialValue = emptyList<ObservationRecord>(), online) {
        value = if (online) ExplorerRemote.feed().map { it.toObservationRecord() } else emptyList()
    }
    var fieldSessionFilter by rememberSaveable { mutableStateOf<String?>(null) }
    // Salidas de campo como categoría: cada una ya vive en Room (real, no inventada) pero antes
    // no había forma de volver a verla una vez cerrada — este filtro la deja alcanzable.
    val fieldSessions = snapshot.fieldSessions.sortedByDescending { it.startedAtEpochMs }
    // Feed único de todos los usuarios (propias + comunidad), no propias-o-comunidad como antes —
    // orden de pila: la más reciente primero, por fecha de creación del registro.
    val own = repository.ownObservations().filter { !it.isDraft }
    val ownIds = own.flatMap { listOfNotNull(it.id, it.serverId) }.toSet()
    val myUsername = snapshot.session.username
    // De otras personas: sin las mías (ya salen arriba, con su copia local) ni las de usuarios bloqueados.
    val others = communityFeed.filter {
        it.id !in ownIds &&
            it.ownerUserId !in snapshot.blockedUserIds &&
            !(myUsername.isNotBlank() && it.ownerUsername.equals(myUsername, ignoreCase = true))
    }
    val feed = (own + others)
        .distinctBy { it.id }
        .filter(::matches)
        .filter { fieldSessionFilter == null || it.fieldSessionId == fieldSessionFilter }
        .sortedByDescending { it.createdAtEpochMs }

    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        topBar = {
            AnuraTopBar(
                title = stringResource(R.string.observations_title),
                centerTitle = true,
            )
        },
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding),
        ) {
            AnuraTextField(
                value = query,
                onValueChange = { query = it },
                label = stringResource(R.string.observations_search),
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = AnuraDimens.spaceGutter)
                    .padding(bottom = AnuraDimens.spaceGap),
                leadingIcon = AnuraIcons.Empty,
                singleLine = true,
            )
            if (fieldSessions.isNotEmpty()) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .horizontalScroll(rememberScrollState())
                        .padding(horizontal = AnuraDimens.spaceGutter)
                        .padding(bottom = AnuraDimens.spaceGap),
                    horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                ) {
                    FilterChip(
                        selected = fieldSessionFilter == null,
                        onClick = { fieldSessionFilter = null },
                        label = { Text(stringResource(R.string.favorites_filter_all)) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = AnuraTheme.extendedColors.accentInk,
                            selectedLabelColor = MaterialTheme.colorScheme.onPrimary,
                        ),
                    )
                    fieldSessions.forEach { session ->
                        val label = stringResource(
                            if (session.closedAtEpochMs == null) {
                                R.string.observations_field_session_chip_active
                            } else {
                                R.string.observations_field_session_chip_closed
                            },
                            session.placeLabel ?: formatObservationDate(session.startedAtEpochMs).orEmpty(),
                        )
                        FilterChip(
                            selected = fieldSessionFilter == session.id,
                            onClick = {
                                fieldSessionFilter = if (fieldSessionFilter == session.id) null else session.id
                            },
                            label = { Text(label) },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = AnuraTheme.extendedColors.accentInk,
                                selectedLabelColor = MaterialTheme.colorScheme.onPrimary,
                            ),
                        )
                    }
                }
            }
            if (feed.isEmpty()) {
                AnuraEmptyState(
                    title = stringResource(R.string.observations_empty_title),
                    description = stringResource(R.string.observations_empty_body),
                    modifier = Modifier.fillMaxSize(),
                )
            } else {
                LazyVerticalGrid(
                    columns = GridCells.Fixed(2),
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(
                        start = AnuraDimens.spaceGutter,
                        end = AnuraDimens.spaceGutter,
                        bottom = AnuraDimens.spaceSection + LocalAnuraTabBarInset.current,
                    ),
                    horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                    verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                ) {
                    items(feed, key = { it.id }) { observation ->
                        StoredObservationCard(
                            observation = observation,
                            favorite = snapshot.favorites.contains(observation.id),
                            onFavoriteClick = { repository.toggleFavorite(observation.id) },
                            onClick = { onOpenObservationDetail(observation.id) },
                        )
                    }
                }
            }
        }
    }
}

@AnuraPreviews
@Composable
private fun ObservationsPreview() {
    AnuraTheme {
        ObservationsScreen(onOpenObservationDetail = {})
    }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun ObservationsPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) {
        ObservationsScreen(onOpenObservationDetail = {})
    }
}

@Composable
internal fun StoredObservationCard(
    observation: ObservationRecord,
    favorite: Boolean,
    onFavoriteClick: () -> Unit,
    onClick: () -> Unit,
) {
    val species = SpeciesCatalog.find(observation.speciesId)
    val unidentifiedCommon = stringResource(R.string.observation_unidentified_common)
    val unidentifiedScientific = stringResource(R.string.observation_unidentified_scientific)
    val common = observation.commonName ?: species?.commonName ?: unidentifiedCommon
    val scientific = observation.scientificName ?: species?.scientificName ?: unidentifiedScientific
    val isOwn = rememberAnuraRepository().isOwnObservation(observation.id)
    ObservationCard(
        commonName = common,
        scientificName = scientific,
        isFavorite = favorite,
        onFavoriteClick = onFavoriteClick,
        modifier = Modifier.fillMaxWidth(),
        statusChip = if (isOwn) {
            { VisibilityChip(isPublic = observation.visibilityPublic) }
        } else {
            null
        },
        thumbnail = { ObservationPhoto(observation) },
        onClick = onClick,
    )
}

@Composable
private fun VisibilityChip(isPublic: Boolean) {
    val label = stringResource(
        if (isPublic) {
            R.string.observation_detail_visibility_public
        } else {
            R.string.observation_detail_visibility_private
        },
    )
    val bg = if (isPublic) {
        AnuraTheme.extendedColors.success
    } else {
        MaterialTheme.colorScheme.surfaceVariant
    }
    val fg = if (isPublic) {
        AnuraTheme.extendedColors.onSuccess
    } else {
        MaterialTheme.colorScheme.onSurfaceVariant
    }
    Row(
        modifier = Modifier
            .clip(RoundedCornerShape(AnuraDimens.radiusCapsule))
            .background(bg)
            .padding(horizontal = 10.dp, vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Icon(
            imageVector = if (isPublic) AnuraIcons.Visibility else AnuraIcons.Lock,
            contentDescription = null,
            tint = fg,
            modifier = Modifier.size(14.dp),
        )
        Text(
            text = label,
            color = fg,
            style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
        )
    }
}

/** `favoritos (listado)` (§4.1). */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FavoritesScreen(
    onBackClick: () -> Unit,
    onOpenObservationDetail: (String) -> Unit,
) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val online = rememberNetworkAvailable()
    val items = snapshot.favorites.mapNotNull { id -> repository.observationById(id) }
        .filter { online || repository.isOwnObservation(it.id) }
    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        topBar = {
            AnuraTopBar(
                title = stringResource(R.string.favorites_title),
                onBackClick = onBackClick,
                centerTitle = true,
            )
        },
    ) { innerPadding ->
        if (items.isEmpty()) {
            AnuraEmptyState(
                title = stringResource(R.string.observations_empty_title),
                description = stringResource(R.string.observations_empty_body),
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding),
            )
        } else {
            LazyVerticalGrid(
                columns = GridCells.Fixed(2),
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding),
                contentPadding = PaddingValues(AnuraDimens.spaceGutter),
                horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
            ) {
                items(items, key = { it.id }) { observation ->
                    StoredObservationCard(
                        observation = observation,
                        favorite = true,
                        onFavoriteClick = { repository.toggleFavorite(observation.id) },
                        onClick = { onOpenObservationDetail(observation.id) },
                    )
                }
            }
        }
    }
}

/** `Detalles de observación (resultado)` (§4.1, argumento `id`). */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ObservationDetailScreen(
    id: String,
    onBackClick: () -> Unit,
    onOpenSpeciesSheet: (String) -> Unit,
    onOpenProfile: (String?) -> Unit,
) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    var showJustification by rememberSaveable { mutableStateOf(false) }
    var showComments by rememberSaveable { mutableStateOf(false) }
    var moreMenu by rememberSaveable { mutableStateOf(false) }
    var confirmDelete by rememberSaveable { mutableStateOf(false) }
    val localObservation = repository.observationById(id)
    // Ajena y no cacheada localmente todavía: se pide de verdad al servidor (ya no hay
    // CommunityCatalog de respaldo — ver ExplorerRemote.observation).
    val remoteObservation by produceState<ObservationRecord?>(initialValue = null, id, localObservation) {
        value = if (localObservation == null) repository.fetchRemoteObservation(id) else null
    }
    val observation = localObservation ?: remoteObservation
    val species = SpeciesCatalog.find(observation?.speciesId)
    val isOwn = observation?.let { repository.isOwnObservation(it.id) } == true
    val missing = stringResource(R.string.anura_value_missing)
    val unidentifiedCommon = stringResource(R.string.observation_unidentified_common)
    val unidentifiedScientific = stringResource(R.string.observation_unidentified_scientific)
    val visibilityUpdated = stringResource(R.string.observation_visibility_updated)
    val deletedMessage = stringResource(R.string.observation_deleted)
    val scientificName = observation?.scientificName ?: species?.scientificName ?: unidentifiedScientific
    val commonName = observation?.commonName ?: species?.commonName ?: unidentifiedCommon
    val speciesId = observation?.speciesId ?: species?.id
    val visibilityPublic = observation?.visibilityPublic == true
    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        contentWindowInsets = WindowInsets.safeDrawing.exclude(WindowInsets.ime),
        topBar = {
            AnuraTopBar(
                title = stringResource(R.string.observation_detail_title),
                onBackClick = onBackClick,
                centerTitle = true,
                actions = {
                    if (isOwn) {
                    Box {
                        IconButton(
                            onClick = { moreMenu = true },
                            modifier = Modifier.size(AnuraDimens.sizeTouch),
                        ) {
                            Icon(
                                imageVector = AnuraIcons.More,
                                contentDescription = stringResource(R.string.observation_detail_more_cd),
                            )
                        }
                        DropdownMenu(
                            expanded = moreMenu,
                            onDismissRequest = { moreMenu = false },
                        ) {
                            DropdownMenuItem(
                                text = { Text(stringResource(R.string.observation_detail_delete)) },
                                onClick = {
                                    moreMenu = false
                                    confirmDelete = true
                                },
                                leadingIcon = {
                                    Icon(AnuraIcons.Delete, contentDescription = null)
                                },
                            )
                            DropdownMenuItem(
                                text = {
                                    Text(
                                        text = stringResource(
                                            if (visibilityPublic) {
                                                R.string.observation_detail_visibility_public
                                            } else {
                                                R.string.observation_detail_visibility_private
                                            },
                                        ),
                                    )
                                },
                                onClick = {
                                    repository.setObservationVisibility(id, !visibilityPublic)
                                    repository.notify(visibilityUpdated)
                                    moreMenu = false
                                },
                                leadingIcon = {
                                    Icon(
                                        imageVector = if (visibilityPublic) {
                                            AnuraIcons.Visibility
                                        } else {
                                            AnuraIcons.VisibilityOff
                                        },
                                        contentDescription = null,
                                    )
                                },
                            )
                        }
                    }
                    }
                },
            )
        },
    ) { innerPadding ->
        Box(
            modifier = Modifier.fillMaxSize(),
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding)
                    .verticalScroll(rememberScrollState())
                    .padding(horizontal = AnuraDimens.spaceGutter)
                    .padding(bottom = 16.dp),
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(ObservationHeroHeight),
                ) {
                    ObservationMediaCarousel(
                        items = observation?.let { mediaForObservation(it) } ?: emptyList(),
                        modifier = Modifier.fillMaxSize(),
                    )
                    if (observation?.expertReviewRequested == true) {
                    AnuraReviewChip(
                        text = stringResource(R.string.observation_detail_expert_review),
                        modifier = Modifier
                            .align(Alignment.TopEnd)
                            .padding(AnuraDimens.spaceGap)
                            .fillMaxWidth(0.58f),
                    )
                    }
                }
                Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
                Text(
                    text = commonName,
                    style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
                    modifier = Modifier
                        .clip(RoundedCornerShape(AnuraDimens.radiusButton))
                        .clickable(enabled = speciesId != null) {
                            speciesId?.let(onOpenSpeciesSheet)
                        }
                        .semantics { role = Role.Button },
                )
                Text(
                    text = scientificName,
                    style = MaterialTheme.typography.titleMedium.copy(fontStyle = FontStyle.Italic),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier
                        .clip(RoundedCornerShape(AnuraDimens.radiusButton))
                        .clickable(enabled = speciesId != null) {
                            speciesId?.let(onOpenSpeciesSheet)
                        }
                        .semantics {
                            role = Role.Button
                        },
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
                ObservationAuthorRow(
                    observationId = id,
                    ownerUsername = observation?.ownerUsername,
                    ownerDisplayName = observation?.ownerDisplayName.orEmpty(),
                    isOwn = isOwn,
                    onOpenProfile = onOpenProfile,
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
                Row(horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap)) {
                    species?.let {
                        if (it.toxicityDeclared) AnuraToxicityChip(variant = it.toxicity)
                        it.iucn?.let { iucn -> AnuraConservationChip(variant = iucn) }
                    }
                }
                ObservationTempoActions(
                    observationId = id,
                    commonName = commonName,
                    scientificName = scientificName,
                    photoToken = observation?.photoTokens?.firstOrNull(),
                    onOpenComments = { showComments = true },
                )
                // en un rechazo del Open Set las candidatas no son una identificación: no se muestran como tal
                val candidates = if (observation?.identificationStatus == IdentificationKnown) {
                    observation.candidates
                } else {
                    emptyList()
                }
                candidates.firstOrNull()?.let { top ->
                    Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
                    ConfidenceCard(
                        share = top.share,
                        photoCount = observation?.photoTokens?.size ?: 0,
                    )
                }
                val known = observation?.identificationStatus == IdentificationKnown
                val morphLine = if (known) observation?.morphName?.let { stringResource(R.string.observation_detail_morph, it) } else null
                val rankLine = if (!known && observation != null) {
                    listOfNotNull(
                        observation.nearestGenus?.let { stringResource(R.string.observation_detail_nearest_genus, it) },
                        observation.nearestFamily?.let { stringResource(R.string.observation_detail_nearest_family, it) },
                    ).joinToString(" · ").takeIf { it.isNotBlank() }
                } else null
                (morphLine ?: rankLine)?.let { line ->
                    Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
                    Text(
                        text = line,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                val confusable = if (observation?.identificationStatus == IdentificationKnown) {
                    observation.confusableWith
                } else {
                    emptyList()
                }
                if (confusable.isNotEmpty()) {
                    Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
                    Text(
                        text = stringResource(R.string.observation_detail_confusable_title),
                        style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                    )
                    Text(
                        text = stringResource(R.string.observation_detail_confusable_body),
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.padding(top = 2.dp),
                    )
                    Text(
                        text = confusable.joinToString(", "),
                        style = MaterialTheme.typography.bodyMedium.copy(fontStyle = androidx.compose.ui.text.font.FontStyle.Italic),
                        color = MaterialTheme.colorScheme.onSurface,
                        modifier = Modifier.padding(top = 4.dp),
                    )
                }
                val others = candidates.drop(1)
                if (others.isNotEmpty()) {
                    Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
                    Text(
                        text = stringResource(R.string.observation_detail_other_candidates),
                        style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                    )
                    others.forEach { candidate ->
                        val catalogSpecies = SpeciesCatalog.all.firstOrNull { it.scientificName == candidate.scientificName }
                        Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
                        CandidateCard(
                            name = candidate.scientificName,
                            percent = candidate.share,
                            speciesInCatalog = catalogSpecies != null,
                            photoSha256 = catalogSpecies?.photoSha256,
                            onClick = catalogSpecies?.let { match -> { onOpenSpeciesSheet(match.id) } },
                        )
                    }
                }
                Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
                AnuraFormButton(
                    text = stringResource(R.string.observation_detail_justification),
                    onClick = { showJustification = true },
                    style = AnuraFormButtonStyle.Outline,
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
                Text(
                    text = stringResource(R.string.observation_detail_record_data),
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                )
                RecordFact(
                    label = stringResource(R.string.observation_detail_where),
                    value = observation?.placeLabel
                        ?: formatCoordinates(observation?.latitude, observation?.longitude)
                        ?: missing,
                )
                RecordFact(
                    label = stringResource(R.string.observation_detail_when),
                    value = formatObservationWhen(observation?.observedAtEpochMs) ?: missing,
                )
                RecordFact(
                    label = stringResource(R.string.observation_detail_size),
                    value = observation?.svlMm?.let { "$it mm" } ?: missing,
                )
                RecordFact(
                    label = stringResource(R.string.observation_detail_audio),
                    value = observation?.audioPath?.let {
                        me.juanlabs.anura.core.data.formatAudioDuration(observation.audioDurationMs) ?: "Audio"
                    } ?: missing,
                )
                // Mismo criterio que `candidates` arriba (línea ~550): un rechazo del Open Set
                // (género/familia/orden desconocido) no debe mostrar "Modelo local" sin
                // candidatas visibles — `commitObservation` llena `candidates` igual aunque el
                // resultado no sea una identificación.
                if (observation?.identificationStatus == IdentificationKnown && observation.candidates.isNotEmpty()) {
                    Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
                    StatusPill(text = stringResource(R.string.observation_detail_model_local), warning = false)
                }
                if (observation?.fieldSessionId != null) {
                    Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
                    FieldSessionRecordNotes(observationId = id)
                }
            }
            if (showComments) {
                ObservationCommentsOverlay(
                    observationId = id,
                    onDismiss = { showComments = false },
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(top = innerPadding.calculateTopPadding()),
                ) {
                    ObservationMediaCarousel(
                        items = observation?.let { mediaForObservation(it) } ?: emptyList(),
                        modifier = Modifier.fillMaxSize(),
                    )
                }
            }
        }
    }
    if (confirmDelete) {
        AnuraConfirmSheet(
            title = stringResource(R.string.observation_delete_confirm_title),
            body = stringResource(R.string.observation_delete_confirm_body),
            confirmLabel = stringResource(R.string.observation_delete_confirm_action),
            onConfirm = {
                repository.deleteObservation(id)
                repository.notify(deletedMessage)
                confirmDelete = false
                onBackClick()
            },
            onDismiss = { confirmDelete = false },
        )
    }
    if (showJustification) {
        IdentificationJustificationSheet(onDismiss = { showJustification = false })
    }
}

@Composable
private fun ObservationAuthorRow(
    observationId: String,
    ownerUsername: String?,
    ownerDisplayName: String,
    isOwn: Boolean,
    onOpenProfile: (String?) -> Unit,
) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val session = snapshot.session
    val displayName = when {
        isOwn && session.displayName.isNotBlank() -> session.displayName
        isOwn -> stringResource(R.string.profile_guest_name)
        ownerDisplayName.isNotBlank() -> ownerDisplayName
        else -> ownerUsername.orEmpty()
    }
    val profileUsername = if (isOwn) null else ownerUsername
    val following = ownerUsername != null && repository.isFollowing(ownerUsername)
    val openProfile = { onOpenProfile(profileUsername) }
    val profileCd = stringResource(R.string.observation_author_cd, displayName)

    AnuraCard(modifier = Modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = AnuraDimens.spaceCardInsetHorizontal,
                    vertical = AnuraDimens.spaceCardInsetVertical,
                ),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
        ) {
            Box(
                modifier = Modifier
                    .size(AnuraDimens.sizeTouch)
                    .clip(CircleShape)
                    .background(MaterialTheme.colorScheme.surfaceVariant)
                    .clickable(role = Role.Button, onClick = openProfile)
                    .semantics { contentDescription = profileCd },
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    imageVector = AnuraIcons.Person,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.size(24.dp),
                )
            }
            Text(
                text = displayName,
                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                color = MaterialTheme.colorScheme.onSurface,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
                modifier = Modifier
                    .weight(1f)
                    .clickable(role = Role.Button, onClick = openProfile)
                    .semantics { contentDescription = profileCd },
            )
            if (!isOwn && ownerUsername != null) {
                FilterChip(
                    selected = following,
                    onClick = { repository.toggleFollow(ownerUsername) },
                    label = {
                        Text(
                            stringResource(
                                if (following) {
                                    R.string.observation_author_following
                                } else {
                                    R.string.observation_author_follow
                                },
                            ),
                        )
                    },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = AnuraTheme.extendedColors.accentInk,
                        selectedLabelColor = MaterialTheme.colorScheme.onPrimary,
                    ),
                )
            }
        }
    }
}

@Composable
private fun ObservationTempoActions(
    observationId: String,
    commonName: String,
    scientificName: String,
    photoToken: String?,
    onOpenComments: () -> Unit,
) {
    val context = LocalContext.current
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val liked = snapshot.favorites.contains(observationId)
    val downloadedMessage = stringResource(R.string.observation_downloaded)
    val downloadFailed = stringResource(R.string.observation_download_failed)
    val shareText = stringResource(
        R.string.observation_detail_share_text,
        commonName,
        scientificName,
        "${AnuraServerConfig.AUTH_BASE_URL}/explorer/$observationId",
    )
    val chooserTitle = stringResource(R.string.observation_detail_share_chooser)
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        IconButton(
            onClick = { repository.toggleFavorite(observationId) },
            modifier = Modifier.size(AnuraDimens.sizeTouch),
        ) {
            Icon(
                imageVector = if (liked) AnuraIcons.Favorite else AnuraIcons.FavoriteBorder,
                contentDescription = stringResource(
                    if (liked) {
                        R.string.observation_detail_unlike_cd
                    } else {
                        R.string.observation_detail_like_cd
                    },
                ),
                tint = AnuraTheme.extendedColors.accentInk,
            )
        }
        IconButton(
            onClick = onOpenComments,
            modifier = Modifier.size(AnuraDimens.sizeTouch),
        ) {
            Icon(
                imageVector = AnuraIcons.Chat,
                contentDescription = stringResource(R.string.observation_detail_comments_cd),
                tint = AnuraTheme.extendedColors.accentInk,
            )
        }
        IconButton(
            onClick = {
                val token = photoToken
                val ok = token != null && repository.media?.exportPhotoToGallery(token) == true
                repository.notify(if (ok) downloadedMessage else downloadFailed)
            },
            modifier = Modifier.size(AnuraDimens.sizeTouch),
        ) {
            Icon(
                imageVector = AnuraIcons.Download,
                contentDescription = stringResource(R.string.observation_detail_download_cd),
                tint = AnuraTheme.extendedColors.accentInk,
            )
        }
        Spacer(modifier = Modifier.weight(1f))
        IconButton(
            onClick = {
                runCatching {
                    context.startActivity(
                        Intent.createChooser(
                            Intent(Intent.ACTION_SEND).apply {
                                type = "text/plain"
                                putExtra(Intent.EXTRA_TEXT, shareText)
                                putExtra(Intent.EXTRA_SUBJECT, commonName)
                            },
                            chooserTitle,
                        ),
                    )
                }
            },
            modifier = Modifier.size(AnuraDimens.sizeTouch),
        ) {
            Icon(
                imageVector = AnuraIcons.Share,
                contentDescription = stringResource(R.string.observation_detail_share_cd),
                tint = AnuraTheme.extendedColors.accentInk,
            )
        }
    }
}

@Composable
private fun StatusPill(text: String, warning: Boolean) {
    val bg = if (warning) AnuraTheme.extendedColors.warning else AnuraTheme.extendedColors.success
    val fg = if (warning) AnuraTheme.extendedColors.onWarning else AnuraTheme.extendedColors.onSuccess
    Text(
        text = text,
        style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
        color = fg,
        modifier = Modifier
            .clip(RoundedCornerShape(AnuraDimens.radiusCapsule))
            .background(bg)
            .padding(horizontal = 10.dp, vertical = 4.dp),
    )
}

private fun sharePercent(share: Float): Int = (share * 100).roundToInt()

@Composable
private fun ConfidenceCard(share: Float, photoCount: Int) {
    AnuraCard(modifier = Modifier.fillMaxWidth(), bordered = true) {
        Column(
            modifier = Modifier.padding(
                horizontal = AnuraDimens.spaceCardInsetHorizontal,
                vertical = AnuraDimens.spaceCardInsetVertical,
            ),
        ) {
            AnuraSectionLabel(text = stringResource(R.string.observation_detail_confidence_label))
            Spacer(modifier = Modifier.height(AnuraDimens.spaceLabelToContent))
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = stringResource(R.string.observation_detail_share_pct, sharePercent(share)),
                    style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
                    modifier = Modifier.weight(1f),
                )
            }
            if (photoCount > 1) {
                Spacer(modifier = Modifier.height(AnuraDimens.spaceLabelToContent))
                Text(
                    text = stringResource(R.string.observation_detail_multi_photo_hint, photoCount),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            ConfidenceBar(progress = share)
        }
    }
}

@Composable
private fun ConfidenceBar(progress: Float) {
    val fraction = progress.coerceIn(0f, 1f)
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(8.dp)
            .clip(RoundedCornerShape(AnuraDimens.radiusCapsule))
            .background(MaterialTheme.colorScheme.surfaceVariant),
    ) {
        if (fraction > 0f) {
            Box(
                modifier = Modifier
                    .fillMaxWidth(fraction)
                    .fillMaxHeight()
                    .background(AnuraTheme.extendedColors.accentInk),
            )
        }
    }
}

@Composable
private fun CandidateCard(
    name: String,
    percent: Float,
    speciesInCatalog: Boolean,
    photoSha256: String?,
    onClick: (() -> Unit)?,
) {
    val thumbCd = stringResource(R.string.observation_detail_candidate_thumb_cd, name)
    val sheetCd = stringResource(R.string.observation_detail_species_cd, name)
    AnuraCard(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(AnuraDimens.radiusCard))
            .then(
                if (onClick != null) {
                    Modifier
                        .clickable(onClick = onClick)
                        .semantics {
                            role = Role.Button
                            contentDescription = sheetCd
                        }
                } else {
                    Modifier
                },
            ),
        bordered = true,
    ) {
        Column(
            modifier = Modifier.padding(
                horizontal = AnuraDimens.spaceGap,
                vertical = AnuraDimens.spaceGap,
            ),
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                if (speciesInCatalog) {
                    Image(
                        painter = rememberSpeciesPhotoPainter(photoSha256, ContentCatalog.ThumbWidth),
                        contentDescription = thumbCd,
                        modifier = Modifier
                            .size(56.dp)
                            .clip(RoundedCornerShape(AnuraDimens.radiusThumb)),
                        contentScale = ContentScale.Crop,
                        colorFilter = AnuraTheme.mediaColorFilter,
                    )
                    Spacer(modifier = Modifier.width(AnuraDimens.spaceGap))
                }
                Text(
                    text = name,
                    style = MaterialTheme.typography.titleMedium.copy(fontStyle = FontStyle.Italic),
                    modifier = Modifier.weight(1f),
                )
                Text(
                    text = stringResource(R.string.observation_detail_share_pct, sharePercent(percent)),
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                )
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceLabelToContent))
            ConfidenceBar(progress = percent)
        }
    }
}

@Composable
private fun RecordFact(label: String, value: String) {
    Column(modifier = Modifier.padding(vertical = AnuraDimens.spaceLabelToContent)) {
        AnuraSectionLabel(text = label)
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
        )
    }
}

@AnuraPreviews
@Composable
private fun ObservationDetailPreview() {
    AnuraTheme {
        ObservationDetailScreen(
            id = "obs-nuevo",
            onBackClick = {},
            onOpenSpeciesSheet = {},
            onOpenProfile = {},
        )
    }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun ObservationDetailPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) {
        ObservationDetailScreen(
            id = "obs-nuevo",
            onBackClick = {},
            onOpenSpeciesSheet = {},
            onOpenProfile = {},
        )
    }
}
