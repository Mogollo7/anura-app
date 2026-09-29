package me.juanlabs.anura.feature.settings

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ExperimentalMaterial3Api
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
import me.juanlabs.anura.core.data.AccountKind
import me.juanlabs.anura.core.data.rememberAnuraRepository
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraCard
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraFormButtonStyle
import me.juanlabs.anura.designsystem.component.AnuraTopBar
import me.juanlabs.anura.designsystem.component.LocalAnuraTabBarInset
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraAccentRole
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

/** Penpot `ajustes`: margen 19. */
private val SettingsGutter = 19.dp

/**
 * `ajustes` (§4.1) — top-level, tab 4.
 *
 * Board: Cabecera de perfil · Zonas descargadas · Apariencia (sección) ·
 * Cerrar sesión. Navbar/FAB viven en [me.juanlabs.anura.navigation.AnuraScaffold].
 * El hero de hábitat no se pinta: el mockup aún no tiene esa foto.
 *
 * Estados: perfil y paquetes reales; el modo de tema es una selección local de esta sesión.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    themeMode: AnuraThemeMode,
    onThemeModeChange: (AnuraThemeMode) -> Unit,
    accentRole: AnuraAccentRole,
    onAccentRoleChange: (AnuraAccentRole) -> Unit,
    preferReduceMotion: Boolean = false,
    onPreferReduceMotionChange: (Boolean) -> Unit = {},
    preferLargeText: Boolean = false,
    onPreferLargeTextChange: (Boolean) -> Unit = {},
    onOpenRegionalPackages: () -> Unit,
    onOpenNotifications: () -> Unit,
    onOpenProfile: () -> Unit,
    onOpenEditProfile: () -> Unit,
    onSignOut: () -> Unit,
) {
    var showAppearance by rememberSaveable { mutableStateOf(false) }
    BackHandler(enabled = showAppearance) { showAppearance = false }
    if (showAppearance) {
        AppearanceScreen(
            themeMode = themeMode,
            onThemeModeChange = onThemeModeChange,
            accentRole = accentRole,
            onAccentRoleChange = onAccentRoleChange,
            preferReduceMotion = preferReduceMotion,
            onPreferReduceMotionChange = onPreferReduceMotionChange,
            preferLargeText = preferLargeText,
            onPreferLargeTextChange = onPreferLargeTextChange,
            onBackClick = { showAppearance = false },
        )
        return
    }
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val guestName = stringResource(R.string.profile_guest_name)
    val guestLabel = stringResource(R.string.settings_guest_label)
    val displayName = snapshot.session.displayName.ifBlank { guestName }
    val username = snapshot.session.username.ifBlank {
        if (snapshot.session.kind == AccountKind.Guest) guestLabel else ""
    }
    val signOutLabel = stringResource(
        if (snapshot.session.kind == AccountKind.Guest) {
            R.string.settings_sign_out_guest
        } else {
            R.string.settings_sign_out
        },
    )
    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        topBar = {
            AnuraTopBar(
                title = stringResource(R.string.settings_title),
                centerTitle = true,
            )
        },
    ) { innerPadding ->
        BoxWithConstraints(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding),
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(min = maxHeight)
                    .verticalScroll(rememberScrollState())
                    .padding(horizontal = SettingsGutter)
                    .padding(bottom = AnuraDimens.spaceSection + LocalAnuraTabBarInset.current),
                verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceSection),
            ) {
                SettingsProfileHeader(
                    displayName = displayName,
                    username = username,
                    onClick = onOpenProfile,
                    onEditClick = onOpenEditProfile,
                )
                SettingsNavRow(
                    title = stringResource(R.string.settings_packages),
                    leadingIcon = AnuraIcons.Download,
                    onClick = onOpenRegionalPackages,
                )
                SettingsNavRow(
                    title = stringResource(R.string.settings_notifications),
                    leadingIcon = AnuraIcons.Notifications,
                    badgeCount = snapshot.unreadNotifications,
                    onClick = onOpenNotifications,
                )
                SettingsNavRow(
                    title = stringResource(R.string.settings_appearance),
                    leadingIcon = AnuraIcons.Settings,
                    onClick = { showAppearance = true },
                )
                Spacer(modifier = Modifier.weight(1f))
                AnuraFormButton(
                    text = signOutLabel,
                    onClick = onSignOut,
                    style = AnuraFormButtonStyle.OutlineNeutral,
                )
            }
        }
    }
}

@Composable
private fun SettingsProfileHeader(
    displayName: String,
    username: String,
    onClick: () -> Unit,
    onEditClick: () -> Unit,
) {
    AnuraCard(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(role = Role.Button, onClick = onClick),
    ) {
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
                    .background(MaterialTheme.colorScheme.surfaceVariant),
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    imageVector = AnuraIcons.Person,
                    contentDescription = stringResource(R.string.settings_profile_cd),
                    tint = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.size(24.dp),
                )
            }
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = displayName,
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                    color = MaterialTheme.colorScheme.onSurface,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
                Text(
                    text = username,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
            }
            IconButton(
                onClick = onEditClick,
                modifier = Modifier.size(AnuraDimens.sizeTouch),
            ) {
                Icon(
                    imageVector = AnuraIcons.Edit,
                    contentDescription = stringResource(R.string.settings_edit_profile_cd),
                    tint = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
    }
}

@Composable
private fun SettingsNavRow(
    title: String,
    leadingIcon: ImageVector,
    onClick: () -> Unit,
    badgeCount: Int = 0,
) {
    AnuraCard(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(role = Role.Button, onClick = onClick),
    ) {
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
            Icon(
                imageVector = leadingIcon,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurface,
                modifier = Modifier.weight(1f),
            )
            if (badgeCount > 0) {
                Box(
                    modifier = Modifier
                        .clip(CircleShape)
                        .background(MaterialTheme.colorScheme.error)
                        .padding(horizontal = 8.dp, vertical = 2.dp),
                    contentAlignment = Alignment.Center,
                ) {
                    Text(
                        text = badgeCount.toString(),
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onError,
                    )
                }
            }
            Icon(
                imageVector = AnuraIcons.ChevronRight,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@AnuraPreviews
@Composable
private fun SettingsPreview() {
    AnuraTheme {
        SettingsScreen(
            themeMode = AnuraThemeMode.Claro,
            onThemeModeChange = {},
            accentRole = AnuraAccentRole.Ink,
            onAccentRoleChange = {},
            onOpenRegionalPackages = {},
            onOpenNotifications = {},
            onOpenProfile = {},
            onOpenEditProfile = {},
            onSignOut = {},
        )
    }
}

@Preview(name = "Oscuro", group = "modo", showBackground = true)
@Composable
private fun SettingsPreviewDark() {
    AnuraTheme(AnuraThemeMode.Oscuro) {
        SettingsScreen(
            themeMode = AnuraThemeMode.Oscuro,
            onThemeModeChange = {},
            accentRole = AnuraAccentRole.Ink,
            onAccentRoleChange = {},
            onOpenRegionalPackages = {},
            onOpenNotifications = {},
            onOpenProfile = {},
            onOpenEditProfile = {},
            onSignOut = {},
        )
    }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun SettingsPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) {
        SettingsScreen(
            themeMode = AnuraThemeMode.LuzRoja,
            onThemeModeChange = {},
            accentRole = AnuraAccentRole.Ink,
            onAccentRoleChange = {},
            onOpenRegionalPackages = {},
            onOpenNotifications = {},
            onOpenProfile = {},
            onOpenEditProfile = {},
            onSignOut = {},
        )
    }
}
