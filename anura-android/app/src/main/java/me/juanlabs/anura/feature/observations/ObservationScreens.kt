package me.juanlabs.anura.feature.observations

import android.content.Intent
import androidx.annotation.DrawableRes
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.GridItemSpan
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
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
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
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
import me.juanlabs.anura.core.data.CommunityCatalog
import me.juanlabs.anura.core.data.ObservationRecord
import me.juanlabs.anura.core.data.SpeciesCatalog
import me.juanlabs.anura.core.data.formatCoordinates
import me.juanlabs.anura.core.data.formatObservationWhen
import me.juanlabs.anura.core.data.rememberAnuraRepository
import me.juanlabs.anura.designsystem.component.AnuraCard
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
import me.juanlabs.anura.feature.fieldsession.fieldSessionRegister
import me.juanlabs.anura.feature.explore.ObservationCatalogScreen
import me.juanlabs.anura.feature.species.IdentificationJustificationSheet

private val ObservationHeroHeight = 280.dp

private data class ListedObservation(
    val id: String,
    val commonRes: Int,
    val scientificRes: Int,
    @param:DrawableRes val photoRes: Int,
    val isPublic: Boolean,
    val own: Boolean,
)

private val MockOwnObservations = listOf(
    ListedObservation("obs-001", R.string.observations_item_1_common, R.string.observations_item_1_sci, R.drawable.carousel_dendrobates_truncatus, isPublic = true, own = true),
    ListedObservation("obs-002", R.string.observations_item_2_common, R.string.observations_item_2_sci, R.drawable.carousel_dendropsophus_bogerti, isPublic = false, own = true),
    ListedObservation("obs-003", R.string.observations_item_3_common, R.string.observations_item_3_sci, R.drawable.carousel_sachatamia_electrops, isPublic = true, own = true),
    ListedObservation("obs-004", R.string.observations_item_4_common, R.string.observations_item_4_sci, R.drawable.carousel_pristimantis_paisa, isPublic = false, own = true),
    ListedObservation("obs-005", R.string.observations_item_5_common, R.string.observations_item_5_sci, R.drawable.carousel_dendropsophus_bogerti, isPublic = true, own = true),
    ListedObservation("obs-006", R.string.observations_item_6_common, R.string.observations_item_6_sci, R.drawable.carousel_dendrobates_truncatus, isPublic = false, own = true),
    ListedObservation("obs-007", R.string.observations_item_7_common, R.string.observations_item_7_sci, R.drawable.carousel_pristimantis_paisa, isPublic = true, own = true),
    ListedObservation("obs-008", R.string.observations_item_8_common, R.string.observations_item_8_sci, R.drawable.carousel_sachatamia_electrops, isPublic = false, own = true),
)

private val MockNearbyObservations = listOf(
    ListedObservation("near-001", R.string.observations_item_1_common, R.string.observations_item_1_sci, R.drawable.carousel_dendrobates_truncatus, isPublic = true, own = false),
    ListedObservation("near-002", R.string.observations_item_4_common, R.string.observations_item_4_sci, R.drawable.carousel_pristimantis_paisa, isPublic = true, own = false),
    ListedObservation("near-003", R.string.observations_item_5_common, R.string.observations_item_5_sci, R.drawable.carousel_dendropsophus_bogerti, isPublic = true, own = false),
    ListedObservation("near-004", R.string.observations_item_6_common, R.string.observations_item_6_sci, R.drawable.carousel_dendrobates_truncatus, isPublic = true, own = false),
    ListedObservation("near-005", R.string.observations_nearby_paisa, R.string.observations_nearby_paisa, R.drawable.carousel_pristimantis_paisa, isPublic = true, own = false),
)

/** `Fotos y observaciones` (§4.1) — top-level, tab 3. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ObservationsScreen(
    onOpenObservationDetail: (String) -> Unit,
    onOpenFavorites: () -> Unit,
) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    var query by rememberSaveable { mutableStateOf("") }
    val own = repository.ownObservations()
    val nearby = CommunityCatalog.observations
    fun matches(observation: ObservationRecord): Boolean {
        val needle = query.trim()
        if (needle.isEmpty()) return true
        val species = SpeciesCatalog.find(observation.speciesId)
        val common = observation.commonName ?: species?.commonName.orEmpty()
        val scientific = observation.scientificName ?: species?.scientificName.orEmpty()
        return common.contains(needle, ignoreCase = true) ||
            scientific.contains(needle, ignoreCase = true)
    }
    val ownFiltered = own.filter(::matches)
    val nearbyFiltered = nearby.filter(::matches)
    val showNearby = ownFiltered.isEmpty()

    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        topBar = {
            AnuraTopBar(
                title = stringResource(R.string.observations_title),
                centerTitle = true,
                actions = {
                    IconButton(
                        onClick = onOpenFavorites,
                        modifier = Modifier.size(AnuraDimens.sizeTouch),
                    ) {
                        Icon(
                            imageVector = AnuraIcons.FavoriteBorder,
                            contentDescription = stringResource(R.string.observations_favorites_cd),
                        )
                    }
                },
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
            if (showNearby && nearbyFiltered.isEmpty()) {
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
                    if (showNearby) {
                        item(
                            key = "nearby-title",
                            span = { GridItemSpan(maxLineSpan) },
                        ) {
                            Text(
                                text = stringResource(R.string.observations_nearby_title),
                                style = MaterialTheme.typography.titleMedium.copy(
                                    fontWeight = FontWeight.SemiBold,
                                ),
                            )
                        }
                        items(nearbyFiltered, key = { it.id }) { observation ->
                            StoredObservationCard(
                                observation = observation,
                                favorite = snapshot.favorites.contains(observation.id),
                                onFavoriteClick = { repository.toggleFavorite(observation.id) },
                                onClick = { onOpenObservationDetail(observation.id) },
                            )
                        }
                    } else {
                        items(ownFiltered, key = { it.id }) { observation ->
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
}

@AnuraPreviews
@Composable
private fun ObservationsPreview() {
    AnuraTheme {
        ObservationsScreen(onOpenObservationDetail = {}, onOpenFavorites = {})
    }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun ObservationsPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) {
        ObservationsScreen(onOpenObservationDetail = {}, onOpenFavorites = {})
    }
}

@Composable
private fun ListedObservationCard(
    item: ListedObservation,
    names: Pair<String, String>,
    favorite: Boolean,
    onFavoriteClick: () -> Unit,
    onClick: () -> Unit,
) {
    ObservationCard(
        commonName = names.first,
        scientificName = names.second,
        isFavorite = favorite,
        onFavoriteClick = onFavoriteClick,
        modifier = Modifier.fillMaxWidth(),
        statusChip = if (item.own) {
            { VisibilityChip(isPublic = item.isPublic) }
        } else {
            null
        },
        thumbnail = {
            Image(
                painter = painterResource(item.photoRes),
                contentDescription = null,
                modifier = Modifier.fillMaxSize(),
                contentScale = ContentScale.Crop,
            )
        },
        onClick = onClick,
    )
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
    val items = snapshot.favorites.mapNotNull { id -> repository.observationById(id) }
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
    val observation = repository.observationById(id)
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
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding),
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
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
                    ownerUserId = observation?.ownerUserId,
                    ownerDisplayName = observation?.ownerDisplayName.orEmpty(),
                    isOwn = isOwn,
                    onOpenProfile = onOpenProfile,
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
                Row(horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap)) {
                    species?.let {
                        AnuraToxicityChip(variant = it.toxicity)
                        AnuraConservationChip(variant = it.iucn)
                    }
                }
                ObservationTempoActions(
                    observationId = id,
                    commonName = commonName,
                    scientificName = scientificName,
                    photoToken = observation?.photoTokens?.firstOrNull(),
                    onOpenComments = { showComments = true },
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
                ConfidenceCard()
                Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
                Text(
                    text = stringResource(R.string.observation_detail_other_candidates),
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
                CandidateCard(
                    name = stringResource(R.string.observation_detail_candidate_1),
                    note = stringResource(R.string.observation_detail_candidate_1_note),
                    percent = 0.94f,
                    percentLabel = stringResource(R.string.observation_detail_candidate_1_pct),
                    imageRes = R.drawable.carousel_dendrobates_truncatus,
                    onClick = { onOpenSpeciesSheet("ANU_COL_DEND_TRU_001") },
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
                CandidateCard(
                    name = stringResource(R.string.observation_detail_candidate_2),
                    note = stringResource(R.string.observation_detail_candidate_2_note),
                    percent = 0.04f,
                    percentLabel = stringResource(R.string.observation_detail_candidate_2_pct),
                    imageRes = R.drawable.carousel_dendrobates_truncatus,
                    onClick = { onOpenSpeciesSheet("ANU_COL_DEND_AUR_001") },
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
                CandidateCard(
                    name = stringResource(R.string.observation_detail_candidate_3),
                    note = stringResource(R.string.observation_detail_candidate_3_note),
                    percent = 0.02f,
                    percentLabel = stringResource(R.string.observation_detail_candidate_3_pct),
                    imageRes = R.drawable.carousel_sachatamia_electrops,
                    onClick = { onOpenSpeciesSheet("ANU_COL_PHYL_TER_001") },
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
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
                Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
                StatusPill(
                    text = stringResource(
                        if (id.endsWith("002")) {
                            R.string.observation_detail_model_cloud
                        } else {
                            R.string.observation_detail_model_local
                        },
                    ),
                    warning = false,
                )
                if (observation?.fieldSessionId != null) {
                    Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
                    FieldSessionRecordNotes(observationId = id)
                }
            }
            if (showComments) {
                ObservationCommentsOverlay(
                    observationId = id,
                    onDismiss = { showComments = false },
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
        androidx.compose.material3.AlertDialog(
            onDismissRequest = { confirmDelete = false },
            title = { Text(stringResource(R.string.observation_delete_confirm_title)) },
            text = { Text(stringResource(R.string.observation_delete_confirm_body)) },
            confirmButton = {
                androidx.compose.material3.TextButton(
                    onClick = {
                        repository.deleteObservation(id)
                        repository.notify(deletedMessage)
                        confirmDelete = false
                        onBackClick()
                    },
                ) {
                    Text(stringResource(R.string.observation_delete_confirm_action))
                }
            },
            dismissButton = {
                androidx.compose.material3.TextButton(onClick = { confirmDelete = false }) {
                    Text(stringResource(R.string.anura_cancel))
                }
            },
        )
    }
    if (showJustification) {
        IdentificationJustificationSheet(onDismiss = { showJustification = false })
    }
}

@Composable
private fun ObservationAuthorRow(
    observationId: String,
    ownerUserId: String?,
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
        else -> CommunityCatalog.person(ownerUserId)?.displayName.orEmpty()
    }
    val profileUserId = if (isOwn) null else ownerUserId
    val following = ownerUserId != null && repository.isFollowing(ownerUserId)
    val openProfile = { onOpenProfile(profileUserId) }
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
            if (!isOwn && ownerUserId != null) {
                FilterChip(
                    selected = following,
                    onClick = { repository.toggleFollow(ownerUserId) },
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

@Composable
private fun ConfidenceCard() {
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
                    text = stringResource(R.string.observation_detail_confidence_value),
                    style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
                    modifier = Modifier.weight(1f),
                )
                Text(
                    text = stringResource(R.string.observation_detail_confidence_level),
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                )
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            ConfidenceBar(progress = 0.94f)
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
    note: String,
    percent: Float,
    percentLabel: String,
    @DrawableRes imageRes: Int,
    onClick: () -> Unit,
) {
    val thumbCd = stringResource(R.string.observation_detail_candidate_thumb_cd, name)
    val sheetCd = stringResource(R.string.observation_detail_species_cd, name)
    AnuraCard(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(AnuraDimens.radiusCard))
            .clickable(onClick = onClick)
            .semantics {
                role = Role.Button
                contentDescription = sheetCd
            },
        bordered = true,
    ) {
        Column(
            modifier = Modifier.padding(
                horizontal = AnuraDimens.spaceGap,
                vertical = AnuraDimens.spaceGap,
            ),
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Image(
                    painter = painterResource(imageRes),
                    contentDescription = thumbCd,
                    modifier = Modifier
                        .size(56.dp)
                        .clip(RoundedCornerShape(AnuraDimens.radiusThumb)),
                    contentScale = ContentScale.Crop,
                    colorFilter = AnuraTheme.mediaColorFilter,
                )
                Spacer(modifier = Modifier.width(AnuraDimens.spaceGap))
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = name,
                        style = MaterialTheme.typography.titleMedium.copy(fontStyle = FontStyle.Italic),
                    )
                    Text(
                        text = note,
                        style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Medium),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                Text(
                    text = percentLabel,
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

@Preview(name = "Ajena", group = "modo", showBackground = true)
@Composable
private fun ObservationDetailPreviewOther() {
    AnuraTheme {
        ObservationDetailScreen(
            id = "near-001",
            onBackClick = {},
            onOpenSpeciesSheet = {},
            onOpenProfile = {},
        )
    }
}
