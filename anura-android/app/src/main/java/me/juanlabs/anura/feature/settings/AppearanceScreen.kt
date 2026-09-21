package me.juanlabs.anura.feature.settings

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.IntrinsicSize
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.selection.selectableGroup
import androidx.compose.foundation.selection.toggleable
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraCard
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraFormButtonStyle
import me.juanlabs.anura.designsystem.component.AnuraSectionLabel
import me.juanlabs.anura.designsystem.component.AnuraTopBar
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraAccentRole
import me.juanlabs.anura.designsystem.theme.AnuraColorTokens
import me.juanlabs.anura.designsystem.theme.AnuraDarkTokens
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraLightTokens
import me.juanlabs.anura.designsystem.theme.AnuraRedLightTokens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

private val SettingsGutter = 19.dp
private val AccentSwatchSize = AnuraDimens.sizeTouch
private val ThemePreviewHeight = 64.dp

/**
 * Sección `Apariencia` dentro de `ajustes`: tema, acento, pantalla y vista previa.
 * No es ruta §4.1 — es sección del tab Ajustes.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AppearanceScreen(
    themeMode: AnuraThemeMode,
    onThemeModeChange: (AnuraThemeMode) -> Unit,
    accentRole: AnuraAccentRole,
    onAccentRoleChange: (AnuraAccentRole) -> Unit,
    preferReduceMotion: Boolean,
    onPreferReduceMotionChange: (Boolean) -> Unit,
    preferLargeText: Boolean,
    onPreferLargeTextChange: (Boolean) -> Unit,
    onBackClick: () -> Unit,
) {
    val swatches = AnuraTheme.swatchColors
    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        topBar = {
            AnuraTopBar(
                title = stringResource(R.string.settings_appearance),
                onBackClick = onBackClick,
                centerTitle = true,
            )
        },
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(horizontal = SettingsGutter)
                .padding(bottom = AnuraDimens.spaceSection),
            verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceSection),
        ) {
            AppearanceSection(
                title = stringResource(R.string.settings_appearance_theme_section),
                body = stringResource(R.string.settings_appearance_theme_body),
            ) {
                Column(
                    modifier = Modifier.selectableGroup(),
                    verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                ) {
                    ThemeModeRow {
                        ThemeModeCard(
                            title = stringResource(R.string.settings_mode_light),
                            description = stringResource(R.string.settings_appearance_theme_light_body),
                            icon = AnuraIcons.Day,
                            selected = themeMode == AnuraThemeMode.Claro,
                            onClick = { onThemeModeChange(AnuraThemeMode.Claro) },
                            modifier = Modifier.weight(1f),
                            preview = { ThemeMiniPreview(AnuraLightTokens) },
                        )
                        ThemeModeCard(
                            title = stringResource(R.string.settings_mode_dark),
                            description = stringResource(R.string.settings_appearance_theme_dark_body),
                            icon = AnuraIcons.Night,
                            selected = themeMode == AnuraThemeMode.Oscuro,
                            onClick = { onThemeModeChange(AnuraThemeMode.Oscuro) },
                            modifier = Modifier.weight(1f),
                            preview = { ThemeMiniPreview(AnuraDarkTokens) },
                        )
                    }
                    ThemeModeRow {
                        ThemeModeCard(
                            title = stringResource(R.string.settings_mode_system),
                            description = stringResource(R.string.settings_appearance_theme_system_body),
                            icon = AnuraIcons.ThemeSystem,
                            selected = themeMode == AnuraThemeMode.Sistema,
                            onClick = { onThemeModeChange(AnuraThemeMode.Sistema) },
                            modifier = Modifier.weight(1f),
                            preview = { SystemThemeMiniPreview() },
                        )
                        ThemeModeCard(
                            title = stringResource(R.string.settings_mode_red),
                            description = stringResource(R.string.settings_appearance_theme_red_body),
                            icon = AnuraIcons.Warning,
                            selected = themeMode == AnuraThemeMode.LuzRoja,
                            onClick = { onThemeModeChange(AnuraThemeMode.LuzRoja) },
                            modifier = Modifier.weight(1f),
                            preview = { ThemeMiniPreview(AnuraRedLightTokens) },
                        )
                    }
                }
            }
            AppearanceSection(
                title = stringResource(R.string.settings_appearance_accent_section),
                body = stringResource(R.string.settings_appearance_accent_body),
            ) {
                AnuraCard(modifier = Modifier.fillMaxWidth()) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .selectableGroup()
                            .padding(
                                horizontal = AnuraDimens.spaceCardInsetHorizontal,
                                vertical = AnuraDimens.spaceCardInsetVertical,
                            ),
                        verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                    ) {
                        AccentSwatchRow {
                            AccentSwatch(
                                label = stringResource(R.string.settings_swatch_tint),
                                color = swatches.tint,
                                selected = accentRole == AnuraAccentRole.Tint,
                                onClick = { onAccentRoleChange(AnuraAccentRole.Tint) },
                                modifier = Modifier.weight(1f),
                            )
                            AccentSwatch(
                                label = stringResource(R.string.settings_swatch_icon),
                                color = swatches.icon,
                                selected = accentRole == AnuraAccentRole.Icon,
                                onClick = { onAccentRoleChange(AnuraAccentRole.Icon) },
                                modifier = Modifier.weight(1f),
                            )
                            AccentSwatch(
                                label = stringResource(R.string.settings_swatch_ink),
                                color = swatches.ink,
                                selected = accentRole == AnuraAccentRole.Ink,
                                onClick = { onAccentRoleChange(AnuraAccentRole.Ink) },
                                modifier = Modifier.weight(1f),
                            )
                        }
                        AccentSwatchRow {
                            AccentSwatch(
                                label = stringResource(R.string.settings_swatch_danger),
                                color = swatches.danger,
                                selected = accentRole == AnuraAccentRole.Danger,
                                onClick = { onAccentRoleChange(AnuraAccentRole.Danger) },
                                modifier = Modifier.weight(1f),
                            )
                            AccentSwatch(
                                label = stringResource(R.string.settings_swatch_warning),
                                color = swatches.warning,
                                checkColor = AnuraTheme.extendedColors.onWarning,
                                selected = accentRole == AnuraAccentRole.Warning,
                                onClick = { onAccentRoleChange(AnuraAccentRole.Warning) },
                                modifier = Modifier.weight(1f),
                            )
                            AccentSwatch(
                                label = stringResource(R.string.settings_swatch_info),
                                color = swatches.info,
                                selected = accentRole == AnuraAccentRole.Info,
                                onClick = { onAccentRoleChange(AnuraAccentRole.Info) },
                                modifier = Modifier.weight(1f),
                            )
                        }
                    }
                }
            }
            AppearanceSection(
                title = stringResource(R.string.settings_appearance_display_section),
                body = stringResource(R.string.settings_appearance_display_body),
            ) {
                AnuraCard(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.fillMaxWidth()) {
                        AppearanceToggleRow(
                            title = stringResource(R.string.settings_appearance_reduce_motion),
                            body = stringResource(R.string.settings_appearance_reduce_motion_body),
                            icon = AnuraIcons.ReduceMotion,
                            checked = preferReduceMotion,
                            onCheckedChange = onPreferReduceMotionChange,
                        )
                        HorizontalDivider(
                            modifier = Modifier.padding(horizontal = AnuraDimens.spaceCardInsetHorizontal),
                            color = AnuraTheme.extendedColors.cardStroke,
                        )
                        AppearanceToggleRow(
                            title = stringResource(R.string.settings_appearance_large_text),
                            body = stringResource(R.string.settings_appearance_large_text_body),
                            icon = AnuraIcons.TextSize,
                            checked = preferLargeText,
                            onCheckedChange = onPreferLargeTextChange,
                        )
                    }
                }
            }
            AppearanceSection(
                title = stringResource(R.string.settings_appearance_preview_section),
                body = stringResource(R.string.settings_appearance_preview_body),
            ) {
                AnuraCard(modifier = Modifier.fillMaxWidth()) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(
                                horizontal = AnuraDimens.spaceCardInsetHorizontal,
                                vertical = AnuraDimens.spaceCardInsetVertical,
                            ),
                        verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                    ) {
                        Text(
                            text = stringResource(R.string.settings_appearance_preview_common),
                            style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                            color = MaterialTheme.colorScheme.onSurface,
                        )
                        Text(
                            text = stringResource(R.string.settings_appearance_preview_sci),
                            style = MaterialTheme.typography.bodyMedium.copy(fontStyle = FontStyle.Italic),
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        AnuraFormButton(
                            text = stringResource(R.string.settings_appearance_preview_action),
                            onClick = {},
                            style = AnuraFormButtonStyle.Primary,
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun AppearanceSection(
    title: String,
    body: String,
    content: @Composable () -> Unit,
) {
    Column(
        verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceLabelToContent),
    ) {
        AnuraSectionLabel(text = title)
        Text(
            text = body,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        content()
    }
}

@Composable
private fun ThemeModeRow(content: @Composable RowScope.() -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .height(IntrinsicSize.Max),
        horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
        content = content,
    )
}

@Composable
private fun AccentSwatchRow(content: @Composable RowScope.() -> Unit) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
        content = content,
    )
}

@Composable
private fun ThemeModeCard(
    title: String,
    description: String,
    icon: ImageVector,
    selected: Boolean,
    onClick: () -> Unit,
    preview: @Composable () -> Unit,
    modifier: Modifier = Modifier,
) {
    AnuraCard(
        bordered = selected,
        modifier = modifier
            .fillMaxHeight()
            .selectable(
                selected = selected,
                role = Role.RadioButton,
                onClick = onClick,
            ),
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = AnuraDimens.spaceLabelToContent,
                    vertical = AnuraDimens.spaceGap,
                ),
            verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceLabelToContent),
        ) {
            preview()
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceLabelToContent),
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = if (selected) {
                        AnuraTheme.extendedColors.accentInk
                    } else {
                        MaterialTheme.colorScheme.onSurfaceVariant
                    },
                    modifier = Modifier.size(20.dp),
                )
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = title,
                        style = MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.SemiBold),
                        color = MaterialTheme.colorScheme.onSurface,
                    )
                    Text(
                        text = description,
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        maxLines = 2,
                    )
                }
            }
        }
    }
}

@Composable
private fun ThemeMiniPreview(
    tokens: AnuraColorTokens,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .height(ThemePreviewHeight)
            .clip(RoundedCornerShape(AnuraDimens.radiusButton))
            .background(tokens.bgBase)
            .padding(AnuraDimens.spaceLabelToContent),
        verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceTitleToSubtitle),
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
                .clip(RoundedCornerShape(AnuraDimens.radiusThumb))
                .background(tokens.bgElevated),
        )
        Box(
            modifier = Modifier
                .fillMaxWidth(0.45f)
                .height(AnuraDimens.spaceLabelToContent)
                .clip(CircleShape)
                .background(tokens.accentInk),
        )
    }
}

@Composable
private fun SystemThemeMiniPreview() {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .height(ThemePreviewHeight)
            .clip(RoundedCornerShape(AnuraDimens.radiusButton)),
    ) {
        ThemeMiniPreview(
            tokens = AnuraLightTokens,
            modifier = Modifier.weight(1f),
        )
        ThemeMiniPreview(
            tokens = AnuraDarkTokens,
            modifier = Modifier.weight(1f),
        )
    }
}

@Composable
private fun AppearanceToggleRow(
    title: String,
    body: String,
    icon: ImageVector,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .heightIn(min = AnuraDimens.sizeTouch)
            .toggleable(
                value = checked,
                role = Role.Switch,
                onValueChange = onCheckedChange,
            )
            .padding(
                horizontal = AnuraDimens.spaceCardInsetHorizontal,
                vertical = AnuraDimens.spaceGap,
            ),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = AnuraTheme.extendedColors.accentInk,
            modifier = Modifier.size(24.dp),
        )
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.SemiBold),
                color = MaterialTheme.colorScheme.onSurface,
            )
            Text(
                text = body,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        Switch(
            checked = checked,
            onCheckedChange = null,
            modifier = Modifier.clearAndSetSemantics {},
            colors = SwitchDefaults.colors(
                checkedThumbColor = MaterialTheme.colorScheme.onPrimary,
                checkedTrackColor = AnuraTheme.extendedColors.accentInk,
            ),
        )
    }
}

@Composable
private fun AccentSwatch(
    label: String,
    color: Color,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    checkColor: Color = MaterialTheme.colorScheme.onPrimary,
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceLabelToContent),
        modifier = modifier.selectable(
            selected = selected,
            role = Role.RadioButton,
            onClick = onClick,
        ),
    ) {
        Box(
            contentAlignment = Alignment.Center,
            modifier = Modifier
                .size(AccentSwatchSize)
                .border(
                    width = 2.dp,
                    color = if (selected) {
                        MaterialTheme.colorScheme.onSurface
                    } else {
                        Color.Transparent
                    },
                    shape = CircleShape,
                )
                .padding(3.dp)
                .clip(CircleShape)
                .background(color),
        ) {
            if (selected) {
                Icon(
                    imageVector = AnuraIcons.Check,
                    contentDescription = null,
                    tint = checkColor,
                    modifier = Modifier.size(18.dp),
                )
            }
        }
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center,
            maxLines = 1,
        )
    }
}

@AnuraPreviews
@Composable
private fun AppearancePreview() {
    AnuraTheme {
        AppearanceScreen(
            themeMode = AnuraThemeMode.Claro,
            onThemeModeChange = {},
            accentRole = AnuraAccentRole.Ink,
            onAccentRoleChange = {},
            preferReduceMotion = false,
            onPreferReduceMotionChange = {},
            preferLargeText = false,
            onPreferLargeTextChange = {},
            onBackClick = {},
        )
    }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun AppearancePreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) {
        AppearanceScreen(
            themeMode = AnuraThemeMode.LuzRoja,
            onThemeModeChange = {},
            accentRole = AnuraAccentRole.Ink,
            onAccentRoleChange = {},
            preferReduceMotion = true,
            onPreferReduceMotionChange = {},
            preferLargeText = true,
            onPreferLargeTextChange = {},
            onBackClick = {},
        )
    }
}
