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
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.mutableStateOf
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

private val ProfileAvatarSize = 80.dp
private val ProfileEditBadgeSize = 28.dp
private val ProfileStatCardHeight = 68.dp
private val FavoritesHeroHeight = 250.dp

private enum class ProfileOwnTab {
    Public,
    Private,
    Drafts,
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
    onOpenFavorites: () -> Unit,
    onOpenObservationDetail: (String) -> Unit,
) {
    val isOwn = userId == null
    val context = LocalContext.current
    val displayName = stringResource(
        if (isOwn) R.string.profile_display_name_own else R.string.profile_display_name_other,
    )
    val username = stringResource(
        if (isOwn) R.string.home_user_username_mock else R.string.observation_author_other,
    )
    val location = stringResource(R.string.profile_location_own)
    val bio = stringResource(
        if (isOwn) R.string.edit_profile_bio_mock else R.string.profile_bio_other,
    )
    val connectionsId = userId ?: "me"
    val shareText = stringResource(R.string.profile_share_text, displayName, username)
    val shareChooser = stringResource(R.string.profile_share_chooser)
    val profileLink = stringResource(R.string.profile_link_mock, username.removePrefix("@"))
    val copyLinkLabel = stringResource(R.string.profile_copy_link)

    var showActions by rememberSaveable { mutableStateOf(false) }
    var showReport by rememberSaveable { mutableStateOf(false) }
    var showObservationsCatalog by rememberSaveable { mutableStateOf(false) }
    var following by rememberSaveable { mutableStateOf(false) }
    var favoriteIds by rememberSaveable { mutableStateOf(listOf("obs-001", "near-001")) }
    var ownTab by rememberSaveable { mutableStateOf(ProfileOwnTab.Public) }

    if (showObservationsCatalog) {
        ObservationCatalogScreen(
            title = stringResource(R.string.profile_stat_observations),
            onBackClick = { showObservationsCatalog = false },
            onOpenObservationDetail = onOpenObservationDetail,
            showQuickFilters = true,
        )
        return
    }

    val gridItems = if (isOwn) {
        when (ownTab) {
            ProfileOwnTab.Public -> OwnPublicObservations
            ProfileOwnTab.Private -> OwnPrivateObservations
            ProfileOwnTab.Drafts -> OwnDraftObservations
        }
    } else {
        OtherPublicObservations
    }
    val featuredFavorite = OwnPublicObservations.first()

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
                    onFollowClick = { following = !following },
                    onReportClick = { showReport = true },
                    onOpenFollowers = { onOpenConnections(connectionsId, "followers") },
                    onOpenSecondStat = {
                        if (isOwn) {
                            onOpenConnections(connectionsId, "favorites")
                        }
                    },
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
                    val emptyOwnDrafts = isOwn && ownTab == ProfileOwnTab.Drafts
                    AnuraEmptyState(
                        title = stringResource(
                            if (emptyOwnDrafts) {
                                R.string.profile_drafts_empty_title
                            } else {
                                R.string.observations_empty_title
                            },
                        ),
                        description = stringResource(
                            if (emptyOwnDrafts) {
                                R.string.profile_drafts_empty_body
                            } else {
                                R.string.observations_empty_body
                            },
                        ),
                    )
                }
            } else {
                items(gridItems, key = { it.id }) { item ->
                    ProfileObservationCard(
                        item = item,
                        showVisibility = isOwn && ownTab != ProfileOwnTab.Public,
                        favorite = favoriteIds.contains(item.id),
                        onFavoriteClick = {
                            favoriteIds = if (favoriteIds.contains(item.id)) {
                                favoriteIds - item.id
                            } else {
                                favoriteIds + item.id
                            }
                        },
                        onClick = { onOpenObservationDetail(item.id) },
                    )
                }
            }
            item(
                key = "favorites",
                span = { GridItemSpan(maxLineSpan) },
            ) {
                ProfileFavoritesSection(
                    featured = featuredFavorite,
                    onOpenFeatured = { onOpenObservationDetail(featuredFavorite.id) },
                    onSeeMore = onOpenFavorites,
                )
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
        ProfileReportSheet(onDismiss = { showReport = false })
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
                value = stringResource(
                    if (isOwn) {
                        R.string.profile_stat_observations_own_value
                    } else {
                        R.string.profile_stat_observations_other_value
                    },
                ),
                label = stringResource(R.string.profile_stat_observations),
                onClick = onOpenObservations,
                modifier = Modifier.weight(1f),
            )
            ProfileStatCard(
                value = stringResource(
                    if (isOwn) {
                        R.string.profile_stat_species_value
                    } else {
                        R.string.profile_stat_species_other_value
                    },
                ),
                label = stringResource(R.string.profile_stat_species),
                onClick = onOpenSecondStat,
                modifier = Modifier.weight(1f),
            )
            ProfileStatCard(
                value = stringResource(
                    if (isOwn) {
                        R.string.profile_stat_followers_own_value
                    } else {
                        R.string.profile_stat_followers_other_value
                    },
                ),
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
                    text = stringResource(R.string.observation_author_follow),
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
                    ProfileOwnTab.Drafts -> R.string.profile_tab_drafts
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

@Composable
private fun ProfileFavoritesSection(
    featured: ProfileObservation,
    onOpenFeatured: () -> Unit,
    onSeeMore: () -> Unit,
) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(FavoritesHeroHeight)
            .clip(RoundedCornerShape(AnuraDimens.radiusCard))
            .clickable(role = Role.Button, onClick = onOpenFeatured),
    ) {
        Image(
            painter = painterResource(featured.photoRes),
            contentDescription = stringResource(featured.commonRes),
            modifier = Modifier.fillMaxSize(),
            contentScale = ContentScale.Crop,
        )
        AnuraFormButton(
            text = stringResource(R.string.profile_see_more_favorites),
            onClick = onSeeMore,
            style = AnuraFormButtonStyle.Secondary,
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(bottom = AnuraDimens.spaceGap)
                .fillMaxWidth(0.77f),
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
private fun ProfileReportSheet(onDismiss: () -> Unit) {
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
            onOpenFavorites = {},
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
            onOpenFavorites = {},
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
            onOpenFavorites = {},
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
            onOpenFavorites = {},
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
    val followingById = remember {
        mutableStateMapOf<String, Boolean>().apply {
            ConnectionPeople.forEach { put(it.id, true) }
        }
    }
    val followingQuery = query.trim()
    val people = ConnectionPeople.filter { person ->
        if (followingQuery.isEmpty()) {
            true
        } else {
            val name = stringResource(person.nameRes)
            val handle = stringResource(person.handleRes)
            name.contains(followingQuery, ignoreCase = true) ||
                handle.contains(followingQuery, ignoreCase = true)
        }
    }
    val favoriteQuery = query.trim()
    val favorites = OwnPublicObservations.filter { item ->
        if (favoriteQuery.isEmpty()) {
            true
        } else {
            stringResource(item.commonRes).contains(favoriteQuery, ignoreCase = true) ||
                stringResource(item.scientificRes).contains(favoriteQuery, ignoreCase = true)
        }
    }
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
                title = stringResource(R.string.profile_display_name_own),
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
                    LazyVerticalGrid(
                        columns = GridCells.Fixed(2),
                        modifier = Modifier.fillMaxSize(),
                        contentPadding = PaddingValues(bottom = AnuraDimens.spaceSection),
                        horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                        verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                    ) {
                        items(favorites, key = { it.id }) { item ->
                            ProfileObservationCard(
                                item = item,
                                showVisibility = false,
                                favorite = true,
                                onFavoriteClick = {},
                                onClick = { onOpenObservationDetail(item.id) },
                            )
                        }
                    }
                }
                ConnectionsTab.Followers,
                ConnectionsTab.Following -> {
                    LazyColumn(
                        modifier = Modifier.fillMaxSize(),
                        contentPadding = PaddingValues(bottom = AnuraDimens.spaceSection),
                        verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                    ) {
                        items(people, key = { it.id }) { person ->
                            ConnectionPersonRow(
                                person = person,
                                following = followingById[person.id] == true,
                                onFollowClick = {
                                    followingById[person.id] = followingById[person.id] != true
                                },
                                onOpenProfile = { onOpenProfile(person.id) },
                            )
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
                    ConnectionsTab.Followers -> ConnectionsFollowersCount
                    ConnectionsTab.Following -> ConnectionsFollowingCount
                    ConnectionsTab.Favorites -> ConnectionsFavoritesCount
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
    person: ConnectionPerson,
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
                text = stringResource(person.nameRes),
                style = MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.Bold),
                color = MaterialTheme.colorScheme.onSurface,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
            Text(
                text = stringResource(person.handleRes),
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
