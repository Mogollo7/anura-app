package me.juanlabs.anura.feature.profile

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Intent
import androidx.annotation.DrawableRes
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.GridItemSpan
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.R
import me.juanlabs.anura.core.data.AuthRemote
import me.juanlabs.anura.core.data.ExplorerRemote
import me.juanlabs.anura.core.data.GuestUserId
import me.juanlabs.anura.core.data.ObservationRecord
import me.juanlabs.anura.core.data.PublicPerson
import me.juanlabs.anura.core.data.PublicProfileResponse
import me.juanlabs.anura.core.data.SpeciesCatalog
import me.juanlabs.anura.core.data.rememberAnuraRepository
import me.juanlabs.anura.core.platform.rememberNetworkAvailable
import me.juanlabs.anura.designsystem.component.AnuraBottomSheet
import me.juanlabs.anura.designsystem.component.AnuraCard
import me.juanlabs.anura.designsystem.component.AnuraEmptyState
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraFormButtonStyle
import me.juanlabs.anura.designsystem.component.AnuraTopBar
import me.juanlabs.anura.designsystem.component.AnuraToxicityChip
import me.juanlabs.anura.designsystem.component.AnuraToxicityChipVariant
import me.juanlabs.anura.designsystem.component.ObservationCard
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode
import me.juanlabs.anura.feature.explore.ObservationCatalogScreen
import me.juanlabs.anura.feature.observations.ObservationPhoto
import me.juanlabs.anura.feature.observations.StoredObservationCard

private val ProfileAvatarSize = 80.dp
private val ProfileEditBadgeSize = 28.dp
private val ProfileStatCardHeight = 68.dp

private enum class ProfileOwnTab {
    Public,
    Private,
    Favorites,
}

private data class ProfileObservation(
    val id: String,
    @param:DrawableRes val photoRes: Int,
    val commonRes: Int,
    val scientificRes: Int,
    val isPublic: Boolean,
    val isDraft: Boolean = false,
    val isToxic: Boolean = false,
)

private val OwnPublicObservations = listOf(
    ProfileObservation("obs-001", R.drawable.carousel_dendrobates_truncatus, R.string.observations_item_1_common, R.string.observations_item_1_sci, true, isToxic = true),
    ProfileObservation("obs-003", R.drawable.carousel_sachatamia_electrops, R.string.observations_item_3_common, R.string.observations_item_3_sci, true),
    ProfileObservation("obs-005", R.drawable.carousel_dendropsophus_bogerti, R.string.observations_item_5_common, R.string.observations_item_5_sci, true),
    ProfileObservation("obs-007", R.drawable.carousel_pristimantis_paisa, R.string.observations_item_7_common, R.string.observations_item_7_sci, true),
)

private val OwnPrivateObservations = listOf(
    ProfileObservation("obs-002", R.drawable.carousel_dendropsophus_bogerti, R.string.observations_item_2_common, R.string.observations_item_2_sci, false),
    ProfileObservation("obs-004", R.drawable.carousel_pristimantis_paisa, R.string.observations_item_4_common, R.string.observations_item_4_sci, false),
)

private val OwnDraftObservations = listOf(
    ProfileObservation("obs-006", R.drawable.carousel_dendrobates_truncatus, R.string.observations_item_6_common, R.string.observations_item_6_sci, false, isDraft = true),
    ProfileObservation("obs-008", R.drawable.carousel_sachatamia_electrops, R.string.observations_item_8_common, R.string.observations_item_8_sci, false, isDraft = true),
)

private val OtherPublicObservations = listOf(
    ProfileObservation("near-001", R.drawable.carousel_dendrobates_truncatus, R.string.observations_item_1_common, R.string.observations_item_1_sci, true, isToxic = true),
    ProfileObservation("near-002", R.drawable.carousel_pristimantis_paisa, R.string.observations_item_4_common, R.string.observations_item_4_sci, true),
    ProfileObservation("near-003", R.drawable.carousel_dendropsophus_bogerti, R.string.observations_item_5_common, R.string.observations_item_5_sci, true),
    ProfileObservation("near-004", R.drawable.carousel_dendrobates_truncatus, R.string.observations_item_6_common, R.string.observations_item_6_sci, true),
)

/**
 * `profile` (propia/ajena, §4.1, argumento `userId?`). `userId == null` = propio.
 *
 * Mockup Final: kebab «Acción: puntos» en ambas; propia sin botones de cabecera
 * (acciones en sheet); ajena con «Seguir» y «Reportar o bloquear»; rejilla 167×196
 * y sección favoritos 320×250 + «Ver más favoritos».
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    userId: String?,
    onBackClick: () -> Unit,
    onOpenEditProfile: () -> Unit,
    onOpenConnections: (String, String) -> Unit,
    onOpenOtherProfile: (String) -> Unit,
    onOpenObservationDetail: (String) -> Unit,
) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val online = rememberNetworkAvailable()
    val session = snapshot.session
    // `userId` es en realidad el username real (auth.users.username) para perfiles ajenos —
    // es la clave natural de /api/auth/public/:username, no hay CommunityCatalog de respaldo.
    val isOwn = userId.isNullOrBlank() || userId == "me" || userId == session.userId || userId == session.username
    val otherUsername = userId?.takeIf { !isOwn }
    val otherProfile by produceState<PublicProfileResponse?>(initialValue = null, otherUsername) {
        value = otherUsername?.let { AuthRemote.publicProfile(it) }
    }
    val context = LocalContext.current
    val guestName = stringResource(R.string.profile_guest_name)
    val missing = stringResource(R.string.profile_value_missing)
    val displayName = if (isOwn) {
        session.displayName.ifBlank { guestName }
    } else {
        otherProfile?.user?.username ?: stringResource(R.string.profile_display_name_other)
    }
    val username = if (isOwn) {
        session.username
    } else {
        otherProfile?.user?.username?.let { "@$it" }.orEmpty()
    }
    val location = if (isOwn) session.location.ifBlank { missing } else missing
    val bio = if (isOwn) {
        session.bio.ifBlank { missing }
    } else {
        otherProfile?.user?.biography?.ifBlank { missing } ?: missing
    }
    val connectionsId = if (isOwn) session.username.ifBlank { session.userId.ifBlank { GuestUserId } } else otherUsername.orEmpty()
    val shareText = stringResource(R.string.profile_share_text, displayName, username.ifBlank { guestName })
    val shareChooser = stringResource(R.string.profile_share_chooser)
    val profileLink = stringResource(
        R.string.profile_link_mock,
        username.removePrefix("@").ifBlank { "invitado" },
    )
    val copyLinkLabel = stringResource(R.string.profile_copy_link)
    val following = !isOwn && otherUsername != null && repository.isFollowing(otherUsername)
    val followLabel = stringResource(
        if (following) R.string.observation_author_following else R.string.observation_author_follow,
    )

    var showActions by rememberSaveable { mutableStateOf(false) }
    var showReport by rememberSaveable { mutableStateOf(false) }
    var showObservationsCatalog by rememberSaveable { mutableStateOf(false) }
    var ownTab by rememberSaveable { mutableStateOf(ProfileOwnTab.Public) }
    val ownObservations = repository.ownObservations()
    val otherObservations by produceState(initialValue = emptyList<ObservationRecord>(), otherUsername, online) {
        value = if (otherUsername != null && online) {
            ExplorerRemote.feed(username = otherUsername).map { it.toObservationRecord() }
        } else {
            emptyList()
        }
    }
    val otherObservationsVisible = otherObservations.filter {
        it.visibilityPublic && !snapshot.blockedUserIds.contains(it.ownerUserId)
    }
    val gridItems = if (isOwn) {
        when (ownTab) {
            ProfileOwnTab.Public -> ownObservations.filter { it.visibilityPublic && !it.isDraft }
            ProfileOwnTab.Private -> ownObservations.filter { !it.visibilityPublic && !it.isDraft }
            ProfileOwnTab.Favorites -> snapshot.favorites.mapNotNull { id -> repository.observationById(id) }
                .filter { online || repository.isOwnObservation(it.id) }
        }
    } else {
        otherObservationsVisible
    }
    val observationsCount = if (isOwn) {
        ownObservations.size
    } else {
        otherProfile?.stats?.observations ?: otherObservationsVisible.size
    }
    val speciesCount = if (isOwn) {
        ownObservations.mapNotNull { it.speciesId }.distinct().size
    } else {
        otherProfile?.stats?.species ?: 0
    }
    val followersCount = if (isOwn) 0 else (otherProfile?.stats?.followers ?: 0)

    if (showObservationsCatalog) {
        ObservationCatalogScreen(
            title = stringResource(R.string.profile_stat_observations),
            onBackClick = { showObservationsCatalog = false },
            onOpenObservationDetail = onOpenObservationDetail,
            showQuickFilters = true,
        )
        return
    }

    fun shareProfile() {
        runCatching {
            context.startActivity(
                Intent.createChooser(
                    Intent(Intent.ACTION_SEND).apply {
                        type = "text/plain"
                        putExtra(Intent.EXTRA_TEXT, shareText)
                        putExtra(Intent.EXTRA_SUBJECT, displayName)
                    },
                    shareChooser,
                ),
            )
        }
    }

    fun copyProfileLink() {
        context.getSystemService(ClipboardManager::class.java)
            ?.setPrimaryClip(ClipData.newPlainText(copyLinkLabel, profileLink))
    }

    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        topBar = {
            AnuraTopBar(
                title = stringResource(
                    if (isOwn) R.string.profile_title_own else R.string.profile_title,
                ),
                onBackClick = onBackClick,
                centerTitle = true,
                actions = {
                    IconButton(
                        onClick = { showActions = true },
                        modifier = Modifier.size(AnuraDimens.sizeTouch),
                    ) {
                        Icon(
                            imageVector = AnuraIcons.More,
                            contentDescription = stringResource(R.string.profile_more_cd),
                            tint = AnuraTheme.extendedColors.accentInk,
                        )
                    }
                },
            )
        },
    ) { innerPadding ->
        LazyVerticalGrid(
            columns = GridCells.Fixed(2),
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding),
            contentPadding = PaddingValues(
                start = AnuraDimens.spaceGutter,
                end = AnuraDimens.spaceGutter,
                bottom = AnuraDimens.spaceSection,
            ),
            horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
            verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
        ) {
            item(
                key = "header",
                span = { GridItemSpan(maxLineSpan) },
            ) {
                ProfileHeader(
                    displayName = displayName,
                    username = username,
                    subtitle = location,
                    bio = bio,
                    isOwn = isOwn,
                    following = following,
                    followLabel = followLabel,
                    observationsValue = observationsCount.toString(),
                    speciesValue = speciesCount.toString(),
                    followersValue = followersCount.toString(),
                    onFollowClick = { otherUsername?.let(repository::toggleFollow) },
                    onReportClick = { showReport = true },
                    onOpenFollowers = { onOpenConnections(connectionsId, "followers") },
                    onOpenSecondStat = {},
                    onOpenObservations = { showObservationsCatalog = true },
                    onEditAvatar = onOpenEditProfile,
                )
            }
            if (isOwn) {
                item(
                    key = "own-tabs",
                    span = { GridItemSpan(maxLineSpan) },
                ) {
                    ProfileOwnTabs(
                        selected = ownTab,
                        onSelect = { ownTab = it },
                    )
                }
            } else {
                item(
                    key = "public-tab",
                    span = { GridItemSpan(maxLineSpan) },
                ) {
                    ProfileOtherPublicTab()
                }
                item(
                    key = "privacy-note",
                    span = { GridItemSpan(maxLineSpan) },
                ) {
                    Text(
                        text = stringResource(R.string.profile_other_privacy_note),
                        style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Medium),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
            if (gridItems.isEmpty()) {
                item(
                    key = "grid-empty",
                    span = { GridItemSpan(maxLineSpan) },
                ) {
                    val emptyOwnFavorites = isOwn && ownTab == ProfileOwnTab.Favorites
                    AnuraEmptyState(
                        title = stringResource(
                            if (emptyOwnFavorites) {
                                R.string.profile_favorites_empty
                            } else {
                                R.string.observations_empty_title
                            },
                        ),
                        description = stringResource(R.string.observations_empty_body),
                    )
                }
            } else {
                items(gridItems, key = { it.id }) { observation ->
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
    if (showActions) {
        ProfileActionsSheet(
            isOwn = isOwn,
            onEditProfile = {
                showActions = false
                onOpenEditProfile()
            },
            onShareProfile = {
                showActions = false
                shareProfile()
            },
            onCopyLink = {
                showActions = false
                copyProfileLink()
            },
            onDismiss = { showActions = false },
        )
    }
    if (showReport) {
        ProfileReportSheet(
            onDismiss = { showReport = false },
            onReport = {
                otherProfile?.user?.id?.let {
                    repository.reportUser(it)
                    repository.notify(context.getString(R.string.profile_report_sent))
                }
                showReport = false
            },
            onBlock = {
                otherProfile?.user?.id?.let {
                    repository.blockUser(it)
                    repository.notify(context.getString(R.string.profile_blocked))
                }
                showReport = false
                onBackClick()
            },
        )
    }
}

@Composable
private fun ProfileHeader(
    displayName: String,
    username: String,
    subtitle: String,
    bio: String,
    isOwn: Boolean,
    following: Boolean,
    followLabel: String,
    observationsValue: String,
    speciesValue: String,
    followersValue: String,
    onFollowClick: () -> Unit,
    onReportClick: () -> Unit,
    onOpenFollowers: () -> Unit,
    onOpenSecondStat: () -> Unit,
    onOpenObservations: () -> Unit,
    onEditAvatar: () -> Unit,
) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
    ) {
        Box(contentAlignment = Alignment.BottomEnd) {
            ProfileAvatar(size = ProfileAvatarSize)
            if (isOwn) {
                IconButton(
                    onClick = onEditAvatar,
                    modifier = Modifier
                        .offset(x = 4.dp, y = 4.dp)
                        .size(AnuraDimens.sizeTouch),
                ) {
                    Box(
                        modifier = Modifier
                            .size(ProfileEditBadgeSize)
                            .clip(CircleShape)
                            .background(AnuraTheme.extendedColors.accentInk),
                        contentAlignment = Alignment.Center,
                    ) {
                        Icon(
                            imageVector = AnuraIcons.Edit,
                            contentDescription = stringResource(R.string.profile_edit_avatar_cd),
                            tint = MaterialTheme.colorScheme.onPrimary,
                            modifier = Modifier.size(16.dp),
                        )
                    }
                }
            }
        }
        if (!isOwn) {
            Text(
                text = username,
                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Normal),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
            )
        }
        Text(
            text = displayName,
            style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
            color = MaterialTheme.colorScheme.onSurface,
            textAlign = TextAlign.Center,
        )
        Text(
            text = if (isOwn) subtitle else bio,
            style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Normal),
            color = MaterialTheme.colorScheme.onSurface,
            textAlign = TextAlign.Center,
        )
        if (!isOwn) {
            ProfileIdentifierChip()
        }
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
        ) {
            ProfileStatCard(
                value = observationsValue,
                label = stringResource(R.string.profile_stat_observations),
                onClick = onOpenObservations,
                modifier = Modifier.weight(1f),
            )
            ProfileStatCard(
                value = speciesValue,
                label = stringResource(R.string.profile_stat_species),
                onClick = onOpenSecondStat,
                modifier = Modifier.weight(1f),
            )
            ProfileStatCard(
                value = followersValue,
                label = stringResource(R.string.profile_stat_followers),
                onClick = onOpenFollowers,
                modifier = Modifier.weight(1f),
            )
        }
        if (!isOwn) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
            ) {
                AnuraFormButton(
                    text = followLabel,
                    onClick = onFollowClick,
                    modifier = Modifier.weight(1f),
                    style = if (following) {
                        AnuraFormButtonStyle.Secondary
                    } else {
                        AnuraFormButtonStyle.Primary
                    },
                )
                AnuraFormButton(
                    text = stringResource(R.string.profile_report_block),
                    onClick = onReportClick,
                    modifier = Modifier.weight(1f),
                    style = AnuraFormButtonStyle.Outline,
                )
            }
        }
    }
}

@Composable
private fun ProfileIdentifierChip() {
    val label = stringResource(R.string.profile_identifier_chip)
    Row(
        modifier = Modifier
            .clip(RoundedCornerShape(13.dp))
            .background(MaterialTheme.colorScheme.inverseSurface)
            .padding(horizontal = 10.dp, vertical = 6.dp)
            .semantics { contentDescription = label },
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        Icon(
            imageVector = AnuraIcons.Success,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.inverseOnSurface,
            modifier = Modifier.size(14.dp),
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.SemiBold),
            color = MaterialTheme.colorScheme.inverseOnSurface,
        )
    }
}

@Composable
private fun ProfileOtherPublicTab() {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(AnuraDimens.sizeTouch)
            .clip(RoundedCornerShape(20.dp))
            .background(AnuraTheme.extendedColors.accentInk),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = stringResource(R.string.profile_tab_public),
            style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.SemiBold),
            color = MaterialTheme.colorScheme.onPrimary,
        )
    }
}

@Composable
private fun ProfileAvatar(size: Dp) {
    Box(
        modifier = Modifier
            .size(size)
            .clip(CircleShape)
            .background(MaterialTheme.colorScheme.surfaceVariant),
        contentAlignment = Alignment.Center,
    ) {
        Icon(
            imageVector = AnuraIcons.Person,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.size(size / 2),
        )
    }
}

@Composable
private fun ProfileOwnTabs(
    selected: ProfileOwnTab,
    onSelect: (ProfileOwnTab) -> Unit,
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
    ) {
        ProfileOwnTab.entries.forEach { tab ->
            val label = stringResource(
                when (tab) {
                    ProfileOwnTab.Public -> R.string.profile_tab_public
                    ProfileOwnTab.Private -> R.string.profile_tab_private
                    ProfileOwnTab.Favorites -> R.string.profile_tab_favorites
                },
            )
            val isSelected = tab == selected
            Box(
                modifier = Modifier
                    .weight(1f)
                    .height(AnuraDimens.sizeTouch)
                    .clip(RoundedCornerShape(20.dp))
                    .background(
                        if (isSelected) {
                            AnuraTheme.extendedColors.accentInk
                        } else {
                            MaterialTheme.colorScheme.surface
                        },
                    )
                    .clickable(role = Role.Tab, onClick = { onSelect(tab) }),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = label,
                    style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.SemiBold),
                    color = if (isSelected) {
                        MaterialTheme.colorScheme.onPrimary
                    } else {
                        MaterialTheme.colorScheme.onSurfaceVariant
                    },
                )
            }
        }
    }
}

@Composable
private fun ProfileStatCard(
    value: String,
    label: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    AnuraCard(
        modifier = modifier
            .clickable(role = Role.Button, onClick = onClick),
        bordered = true,
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .height(ProfileStatCardHeight)
                .padding(
                    horizontal = AnuraDimens.spaceLabelToContent,
                    vertical = AnuraDimens.spaceGap,
                ),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
        ) {
            Text(
                text = value,
                style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.SemiBold),
                textAlign = TextAlign.Center,
            )
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Medium),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
                maxLines = 2,
            )
        }
    }
}

@Composable
private fun ProfileObservationCard(
    item: ProfileObservation,
    showVisibility: Boolean,
    favorite: Boolean,
    onFavoriteClick: () -> Unit,
    onClick: () -> Unit,
) {
    val commonName = stringResource(item.commonRes)
    val scientificName = stringResource(item.scientificRes)
    ObservationCard(
        commonName = commonName,
        scientificName = scientificName,
        isFavorite = favorite,
        onFavoriteClick = onFavoriteClick,
        modifier = Modifier.fillMaxWidth(),
        statusChip = when {
            item.isToxic -> {
                { AnuraToxicityChip(AnuraToxicityChipVariant.Toxic) }
            }
            showVisibility -> {
                { ProfileVisibilityChip(isPublic = item.isPublic) }
            }
            else -> null
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
private fun ProfileVisibilityChip(isPublic: Boolean) {
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

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun ProfileActionsSheet(
    isOwn: Boolean,
    onEditProfile: () -> Unit,
    onShareProfile: () -> Unit,
    onCopyLink: () -> Unit,
    onDismiss: () -> Unit,
) {
    AnuraBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = AnuraDimens.spacePopupInset),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            if (isOwn) {
                AnuraFormButton(
                    text = stringResource(R.string.edit_profile_title),
                    onClick = onEditProfile,
                    style = AnuraFormButtonStyle.Primary,
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceActionGap))
                AnuraFormButton(
                    text = stringResource(R.string.profile_share),
                    onClick = onShareProfile,
                    style = AnuraFormButtonStyle.Outline,
                )
            } else {
                AnuraFormButton(
                    text = stringResource(R.string.profile_share),
                    onClick = onShareProfile,
                    style = AnuraFormButtonStyle.Primary,
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceActionGap))
                AnuraFormButton(
                    text = stringResource(R.string.profile_copy_link),
                    onClick = onCopyLink,
                    style = AnuraFormButtonStyle.Outline,
                )
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceActionGap))
            AnuraFormButton(
                text = stringResource(R.string.anura_cancel),
                onClick = onDismiss,
                style = AnuraFormButtonStyle.Outline,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun ProfileReportSheet(
    onDismiss: () -> Unit,
    onReport: () -> Unit,
    onBlock: () -> Unit,
) {
    AnuraBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = AnuraDimens.spacePopupInset),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                text = stringResource(R.string.profile_report_block),
                style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
                color = MaterialTheme.colorScheme.onSurface,
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(vertical = AnuraDimens.spaceGap),
            )
            AnuraFormButton(
                text = stringResource(R.string.profile_report_action),
                onClick = onReport,
                style = AnuraFormButtonStyle.Primary,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceActionGap))
            AnuraFormButton(
                text = stringResource(R.string.profile_block_action),
                onClick = onBlock,
                style = AnuraFormButtonStyle.Outline,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceActionGap))
            AnuraFormButton(
                text = stringResource(R.string.anura_cancel),
                onClick = onDismiss,
                style = AnuraFormButtonStyle.Outline,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
        }
    }
}

@AnuraPreviews
@Composable
private fun ProfileOwnPreview() {
    AnuraTheme {
        ProfileScreen(
            userId = null,
            onBackClick = {},
            onOpenEditProfile = {},
            onOpenConnections = { _, _ -> },
            onOpenOtherProfile = {},
            onOpenObservationDetail = {},
        )
    }
}

@AnuraPreviews
@Composable
private fun ProfileOtherPreview() {
    AnuraTheme {
        ProfileScreen(
            userId = "user-002",
            onBackClick = {},
            onOpenEditProfile = {},
            onOpenConnections = { _, _ -> },
            onOpenOtherProfile = {},
            onOpenObservationDetail = {},
        )
    }
}

@Preview(name = "Luz roja propia", group = "modo", showBackground = true)
@Composable
private fun ProfileOwnPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) {
        ProfileScreen(
            userId = null,
            onBackClick = {},
            onOpenEditProfile = {},
            onOpenConnections = { _, _ -> },
            onOpenOtherProfile = {},
            onOpenObservationDetail = {},
        )
    }
}

@Preview(name = "Luz roja ajena", group = "modo", showBackground = true)
@Composable
private fun ProfileOtherPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) {
        ProfileScreen(
            userId = "user-002",
            onBackClick = {},
            onOpenEditProfile = {},
            onOpenConnections = { _, _ -> },
            onOpenOtherProfile = {},
            onOpenObservationDetail = {},
        )
    }
}

private enum class ConnectionsTab {
    Followers,
    Following,
    Favorites,
}

private data class ConnectionPerson(
    val id: String,
    val nameRes: Int,
    val handleRes: Int,
)

private val ConnectionPeople = listOf(
    ConnectionPerson("user-camila", R.string.connections_person_1_name, R.string.connections_person_1_handle),
    ConnectionPerson("user-julian", R.string.connections_person_2_name, R.string.connections_person_2_handle),
    ConnectionPerson("user-vale", R.string.connections_person_3_name, R.string.connections_person_3_handle),
    ConnectionPerson("user-andres", R.string.connections_person_4_name, R.string.connections_person_4_handle),
    ConnectionPerson("user-laura", R.string.connections_person_5_name, R.string.connections_person_5_handle),
)

private const val ConnectionsFollowersCount = 128
private const val ConnectionsFollowingCount = 86
private const val ConnectionsFavoritesCount = 19
private val ConnectionsFollowButtonWidth = 96.dp
private val ConnectionsAvatarSize = 48.dp

/** `Seguidos, seguidores y favoritos` (§4.1, argumento `userId`). */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ConnectionsScreen(
    userId: String,
    initialTab: String = "followers",
    onBackClick: () -> Unit,
    onOpenProfile: (String) -> Unit,
    onOpenObservationDetail: (String) -> Unit,
) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val session = snapshot.session
    val isOwn = userId == "me" || userId == session.userId || userId == session.username ||
        userId == GuestUserId || userId.isBlank()
    // `userId` es el username real para cuentas ajenas (igual que en ProfileScreen) — no hay
    // CommunityCatalog de respaldo, las listas salen de auth-service de verdad.
    val targetUsername = if (isOwn) session.username.ifBlank { null } else userId
    val otherProfile by produceState<PublicProfileResponse?>(initialValue = null, targetUsername, isOwn) {
        value = if (!isOwn) targetUsername?.let { AuthRemote.publicProfile(it) } else null
    }
    val title = if (isOwn) {
        session.displayName.ifBlank { stringResource(R.string.profile_guest_name) }
    } else {
        otherProfile?.user?.username ?: stringResource(R.string.profile_title)
    }
    var tab by rememberSaveable(initialTab) {
        mutableStateOf(
            when (initialTab) {
                "following" -> ConnectionsTab.Following
                "favorites" -> ConnectionsTab.Favorites
                else -> ConnectionsTab.Followers
            },
        )
    }
    var query by rememberSaveable { mutableStateOf("") }
    val followingQuery = query.trim()
    val followersList by produceState(initialValue = emptyList<PublicPerson>(), targetUsername) {
        value = targetUsername?.let { AuthRemote.followers(it) }.orEmpty()
    }
    val followingList by produceState(initialValue = emptyList<PublicPerson>(), targetUsername) {
        value = targetUsername?.let { AuthRemote.following(it) }.orEmpty()
    }
    val sourcePeople = when (tab) {
        ConnectionsTab.Followers -> followersList
        ConnectionsTab.Following -> followingList
        ConnectionsTab.Favorites -> emptyList()
    }
    val people = sourcePeople.filter { person ->
        followingQuery.isEmpty() || person.username.contains(followingQuery, ignoreCase = true)
    }
    val favoriteQuery = query.trim()
    val favorites = snapshot.favorites.mapNotNull { id -> repository.observationById(id) }.filter { observation ->
        if (favoriteQuery.isEmpty()) {
            true
        } else {
            val species = SpeciesCatalog.find(observation.speciesId)
            val common = observation.commonName ?: species?.commonName.orEmpty()
            val scientific = observation.scientificName ?: species?.scientificName.orEmpty()
            common.contains(favoriteQuery, ignoreCase = true) ||
                scientific.contains(favoriteQuery, ignoreCase = true)
        }
    }
    val followersCount = followersList.size
    val followingCount = followingList.size
    val favoritesCount = snapshot.favorites.size
    val searchHint = stringResource(
        when (tab) {
            ConnectionsTab.Followers -> R.string.connections_search_followers
            ConnectionsTab.Following -> R.string.connections_search_following
            ConnectionsTab.Favorites -> R.string.connections_search_favorites
        },
    )
    Scaffold(
        containerColor = MaterialTheme.colorScheme.background,
        topBar = {
            AnuraTopBar(
                title = title,
                onBackClick = onBackClick,
            )
        },
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(horizontal = AnuraDimens.spaceGutter),
        ) {
            ConnectionsTabRow(
                selected = tab,
                followersCount = followersCount,
                followingCount = followingCount,
                favoritesCount = favoritesCount,
                onSelect = { tab = it },
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(MaterialTheme.colorScheme.surface),
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .heightIn(min = AnuraDimens.sizeTouch)
                        .padding(horizontal = AnuraDimens.spaceGap),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                ) {
                    Icon(
                        imageVector = AnuraIcons.Empty,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.size(20.dp),
                    )
                    BasicTextField(
                        value = query,
                        onValueChange = { query = it },
                        modifier = Modifier
                            .weight(1f)
                            .semantics { contentDescription = searchHint },
                        textStyle = MaterialTheme.typography.bodyMedium.copy(
                            color = MaterialTheme.colorScheme.onSurface,
                        ),
                        singleLine = true,
                        cursorBrush = SolidColor(MaterialTheme.colorScheme.primary),
                        decorationBox = { inner ->
                            if (query.isEmpty()) {
                                Text(
                                    text = searchHint,
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                )
                            }
                            inner()
                        },
                    )
                }
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            when (tab) {
                ConnectionsTab.Favorites -> {
                    if (favorites.isEmpty()) {
                        AnuraEmptyState(
                            title = stringResource(R.string.connections_empty_favorites),
                            description = stringResource(R.string.observations_empty_body),
                            modifier = Modifier.fillMaxSize(),
                        )
                    } else {
                    LazyVerticalGrid(
                        columns = GridCells.Fixed(2),
                        modifier = Modifier.fillMaxSize(),
                        contentPadding = PaddingValues(bottom = AnuraDimens.spaceSection),
                        horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                        verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                    ) {
                        items(favorites, key = { it.id }) { observation ->
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
                ConnectionsTab.Followers,
                ConnectionsTab.Following -> {
                    if (people.isEmpty()) {
                        AnuraEmptyState(
                            title = stringResource(
                                if (tab == ConnectionsTab.Followers) {
                                    R.string.connections_empty_followers
                                } else {
                                    R.string.connections_empty_following
                                },
                            ),
                            modifier = Modifier.fillMaxSize(),
                        )
                    } else {
                    LazyColumn(
                        modifier = Modifier.fillMaxSize(),
                        contentPadding = PaddingValues(bottom = AnuraDimens.spaceSection),
                        verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                    ) {
                        items(people, key = { it.username }) { person ->
                            ConnectionPersonRow(
                                name = person.username,
                                handle = "@${person.username}",
                                following = repository.isFollowing(person.username),
                                onFollowClick = { repository.toggleFollow(person.username) },
                                onOpenProfile = { onOpenProfile(person.username) },
                            )
                        }
                    }
                    }
                }
            }
        }
    }
}

@Composable
private fun ConnectionsTabRow(
    selected: ConnectionsTab,
    followersCount: Int,
    followingCount: Int,
    favoritesCount: Int,
    onSelect: (ConnectionsTab) -> Unit,
) {
    Row(modifier = Modifier.fillMaxWidth()) {
        ConnectionsTab.entries.forEach { tab ->
            val label = stringResource(
                when (tab) {
                    ConnectionsTab.Followers -> R.string.connections_tab_followers
                    ConnectionsTab.Following -> R.string.connections_tab_following
                    ConnectionsTab.Favorites -> R.string.connections_tab_favorites
                },
                when (tab) {
                    ConnectionsTab.Followers -> followersCount
                    ConnectionsTab.Following -> followingCount
                    ConnectionsTab.Favorites -> favoritesCount
                },
            )
            val isSelected = tab == selected
            Column(
                modifier = Modifier
                    .weight(1f)
                    .heightIn(min = AnuraDimens.sizeTouch)
                    .clickable(role = Role.Tab, onClick = { onSelect(tab) }),
                horizontalAlignment = Alignment.Start,
                verticalArrangement = Arrangement.Center,
            ) {
                Text(
                    text = label,
                    style = MaterialTheme.typography.labelMedium.copy(
                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                    ),
                    color = if (isSelected) {
                        AnuraTheme.extendedColors.accentInk
                    } else {
                        MaterialTheme.colorScheme.onSurface
                    },
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
                Spacer(modifier = Modifier.height(6.dp))
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(3.dp)
                        .clip(RoundedCornerShape(2.dp))
                        .background(
                            if (isSelected) {
                                AnuraTheme.extendedColors.accentInk
                            } else {
                                MaterialTheme.colorScheme.background
                            },
                        ),
                )
            }
        }
    }
}

@Composable
private fun ConnectionPersonRow(
    name: String,
    handle: String,
    following: Boolean,
    onFollowClick: () -> Unit,
    onOpenProfile: () -> Unit,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(role = Role.Button, onClick = onOpenProfile),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
    ) {
        ProfileAvatar(size = ConnectionsAvatarSize)
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = name,
                style = MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.Bold),
                color = MaterialTheme.colorScheme.onSurface,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
            Text(
                text = handle,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
        }
        Button(
            onClick = onFollowClick,
            modifier = Modifier
                .width(ConnectionsFollowButtonWidth)
                .heightIn(min = AnuraDimens.sizeTouch),
            shape = RoundedCornerShape(18.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = AnuraTheme.extendedColors.accentInk,
                contentColor = MaterialTheme.colorScheme.onPrimary,
            ),
            contentPadding = PaddingValues(horizontal = 8.dp, vertical = 8.dp),
        ) {
            Text(
                text = if (following) {
                    stringResource(R.string.connections_following)
                } else {
                    stringResource(R.string.observation_author_follow)
                },
                style = MaterialTheme.typography.labelLarge.copy(fontWeight = FontWeight.SemiBold),
                maxLines = 1,
            )
        }
    }
}
