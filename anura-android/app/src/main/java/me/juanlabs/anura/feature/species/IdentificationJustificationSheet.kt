package me.juanlabs.anura.feature.species

import androidx.annotation.StringRes
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraBottomSheet
import me.juanlabs.anura.designsystem.component.AnuraCard
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraFormButtonStyle
import me.juanlabs.anura.designsystem.component.AnuraSectionLabel
import me.juanlabs.anura.designsystem.component.AnuraTextField
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

private val MaskPhotoHeight = 240.dp
private val RefuteThumbSize = 130.dp

private enum class RegionTint {
    Tertiary,
    Secondary,
    Success,
    Info,
}

private data class JustificationRegion(
    val id: String,
    @param:StringRes val nameRes: Int,
    @param:StringRes val percentRes: Int,
    val progress: Float,
    @param:StringRes val noteRes: Int,
    @param:StringRes val modelRes: Int,
    val tint: RegionTint,
    val xFraction: Float,
    val yFraction: Float,
    val wFraction: Float,
    val hFraction: Float,
)

private val JustificationRegions = listOf(
    JustificationRegion(
        id = "tympanum",
        nameRes = R.string.justification_region_tympanum,
        percentRes = R.string.justification_region_tympanum_pct,
        progress = 0.24f,
        noteRes = R.string.justification_region_tympanum_note,
        modelRes = R.string.justification_region_tympanum_model,
        tint = RegionTint.Tertiary,
        xFraction = 0.22f,
        yFraction = 0.15f,
        wFraction = 0.20f,
        hFraction = 0.22f,
    ),
    JustificationRegion(
        id = "dorsal",
        nameRes = R.string.justification_region_dorsal,
        percentRes = R.string.justification_region_dorsal_pct,
        progress = 0.27f,
        noteRes = R.string.justification_region_dorsal_note,
        modelRes = R.string.justification_region_dorsal_model,
        tint = RegionTint.Info,
        xFraction = 0.45f,
        yFraction = 0.11f,
        wFraction = 0.37f,
        hFraction = 0.31f,
    ),
    JustificationRegion(
        id = "fold",
        nameRes = R.string.justification_region_fold,
        percentRes = R.string.justification_region_fold_pct,
        progress = 0.18f,
        noteRes = R.string.justification_region_fold_note,
        modelRes = R.string.justification_region_fold_model,
        tint = RegionTint.Success,
        xFraction = 0.12f,
        yFraction = 0.48f,
        wFraction = 0.31f,
        hFraction = 0.18f,
    ),
    JustificationRegion(
        id = "disc",
        nameRes = R.string.justification_region_disc,
        percentRes = R.string.justification_region_disc_pct,
        progress = 0.31f,
        noteRes = R.string.justification_region_disc_note,
        modelRes = R.string.justification_region_disc_model,
        tint = RegionTint.Secondary,
        xFraction = 0.48f,
        yFraction = 0.48f,
        wFraction = 0.24f,
        hFraction = 0.25f,
    ),
)

/**
 * `DESPLEGABLE1 (justificación de identificación)` — bottom sheet local, no ruta (§4.2).
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun IdentificationJustificationSheet(
    onDismiss: () -> Unit,
    onRefuteAll: () -> Unit = onDismiss,
) {
    var refuteRegionId by rememberSaveable { mutableStateOf<String?>(null) }
    val refuteRegion = JustificationRegions.firstOrNull { it.id == refuteRegionId }
    AnuraBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = false),
        containerColor = AnuraTheme.extendedColors.boardBackground,
    ) {
        IdentificationJustificationBody(
            onSelectRegion = { refuteRegionId = it.id },
            onRefuteAll = onRefuteAll,
        )
    }
    if (refuteRegion != null) {
        RefuteRegionSheet(
            region = refuteRegion,
            onDismiss = { refuteRegionId = null },
            onSend = { refuteRegionId = null },
        )
    }
}

@Composable
private fun IdentificationJustificationBody(
    onSelectRegion: (JustificationRegion) -> Unit,
    onRefuteAll: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = AnuraDimens.spaceGutter)
            .padding(bottom = AnuraDimens.spaceSection),
    ) {
        Text(
            text = stringResource(R.string.justification_title),
            style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
        )
        Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
        Text(
            text = stringResource(R.string.justification_heading),
            style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
        )
        Text(
            text = stringResource(R.string.justification_intro),
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
        SegmentationMask(
            onSelectRegion = onSelectRegion,
        )
        Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
        Text(
            text = stringResource(R.string.justification_hint),
            style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Medium),
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
        Text(
            text = stringResource(R.string.justification_contribution),
            style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
        )
        Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
        JustificationRegions.forEach { region ->
            RegionContributionCard(
                region = region,
                onRefute = { onSelectRegion(region) },
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
        }
        AnuraCard(modifier = Modifier.fillMaxWidth(), bordered = true) {
            Row(
                modifier = Modifier.padding(
                    horizontal = AnuraDimens.spaceCardInsetHorizontal,
                    vertical = AnuraDimens.spaceCardInsetVertical,
                ),
                verticalAlignment = Alignment.Top,
            ) {
                Icon(
                    imageVector = AnuraIcons.Info,
                    contentDescription = null,
                    tint = AnuraTheme.extendedColors.info,
                    modifier = Modifier.size(20.dp),
                )
                Spacer(modifier = Modifier.size(AnuraDimens.spaceGap))
                Text(
                    text = stringResource(R.string.justification_footer),
                    style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.Medium),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.weight(1f),
                )
            }
        }
        Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
        AnuraFormButton(
            text = stringResource(R.string.justification_refute_all),
            onClick = onRefuteAll,
            style = AnuraFormButtonStyle.Primary,
        )
    }
}

@Composable
private fun SegmentationMask(onSelectRegion: (JustificationRegion) -> Unit) {
    BoxWithConstraints(
        modifier = Modifier
            .fillMaxWidth()
            .height(MaskPhotoHeight)
            .clip(RoundedCornerShape(AnuraDimens.radiusCard)),
    ) {
        Image(
            painter = painterResource(R.drawable.carousel_dendrobates_truncatus),
            contentDescription = stringResource(R.string.justification_photo_cd),
            modifier = Modifier.fillMaxSize(),
            contentScale = ContentScale.Crop,
            colorFilter = AnuraTheme.mediaColorFilter,
        )
        JustificationRegions.forEach { region ->
            val name = stringResource(region.nameRes)
            val regionCd = stringResource(R.string.justification_region_cd, name)
            val tint = regionTint(region.tint)
            Box(
                modifier = Modifier
                    .offset(
                        x = maxWidth * region.xFraction,
                        y = maxHeight * region.yFraction,
                    )
                    .size(
                        width = maxWidth * region.wFraction,
                        height = maxHeight * region.hFraction,
                    )
                    .clip(RoundedCornerShape(AnuraDimens.radiusButton))
                    .background(tint.copy(alpha = 0.32f))
                    .clickable { onSelectRegion(region) }
                    .semantics {
                        role = Role.Button
                        contentDescription = regionCd
                    },
            )
        }
    }
}

@Composable
private fun RegionContributionCard(
    region: JustificationRegion,
    onRefute: () -> Unit,
) {
    val name = stringResource(region.nameRes)
    val refuteCd = stringResource(R.string.justification_refute_region_cd, name)
    val tint = regionTint(region.tint)
    AnuraCard(modifier = Modifier.fillMaxWidth(), bordered = true) {
        Column(
            modifier = Modifier.padding(
                horizontal = AnuraDimens.spaceCardInsetHorizontal,
                vertical = AnuraDimens.spaceGap,
            ),
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier
                        .size(14.dp)
                        .clip(CircleShape)
                        .background(tint),
                )
                Spacer(modifier = Modifier.size(AnuraDimens.spaceGap))
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = name,
                        style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                    )
                    Text(
                        text = stringResource(region.noteRes),
                        style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.Medium),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                Text(
                    text = stringResource(region.percentRes),
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                )
                IconButton(
                    onClick = onRefute,
                    modifier = Modifier.size(AnuraDimens.sizeTouch),
                ) {
                    Icon(
                        imageVector = AnuraIcons.Refute,
                        contentDescription = refuteCd,
                        tint = MaterialTheme.colorScheme.error,
                    )
                }
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceLabelToContent))
            ContributionBar(progress = region.progress, fill = tint)
        }
    }
}

@Composable
private fun ContributionBar(progress: Float, fill: Color) {
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
                    .background(fill),
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun RefuteRegionSheet(
    region: JustificationRegion,
    onDismiss: () -> Unit,
    onSend: () -> Unit,
) {
    var observed by rememberSaveable(region.id) { mutableStateOf("") }
    var species by rememberSaveable(region.id) { mutableStateOf("") }
    var selectedId by rememberSaveable(region.id) { mutableStateOf(region.id) }
    val selected = JustificationRegions.firstOrNull { it.id == selectedId } ?: region
    var regionMenu by rememberSaveable { mutableStateOf(false) }
    var speciesMenu by rememberSaveable { mutableStateOf(false) }
    val speciesOptions = listOf(
        stringResource(R.string.justification_refute_species_mock),
        stringResource(R.string.species_sheet_scientific_name),
        stringResource(R.string.observations_item_2_sci),
        stringResource(R.string.species_sheet_similar_3_sci),
    )
    AnuraBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true),
        containerColor = MaterialTheme.colorScheme.surface,
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = AnuraDimens.spaceGutter)
                .padding(bottom = AnuraDimens.spaceSection),
        ) {
            Text(
                text = stringResource(R.string.justification_refute_title),
                style = MaterialTheme.typography.headlineMedium.copy(fontWeight = FontWeight.Bold),
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            Text(
                text = stringResource(R.string.justification_refute_intro),
                style = MaterialTheme.typography.titleMedium,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            Row(modifier = Modifier.fillMaxWidth()) {
                RefuteRegionThumb(region = selected)
                Spacer(modifier = Modifier.size(AnuraDimens.spaceGap))
                Column(modifier = Modifier.weight(1f)) {
                    AnuraSectionLabel(text = stringResource(R.string.justification_refute_region_label))
                    Box {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(AnuraDimens.sizeTouch)
                                .clip(RoundedCornerShape(AnuraDimens.radiusButton))
                                .background(MaterialTheme.colorScheme.surfaceVariant)
                                .clickable(
                                    role = Role.Button,
                                    onClick = { regionMenu = true },
                                )
                                .padding(horizontal = AnuraDimens.spaceGap),
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Text(
                                text = stringResource(selected.nameRes),
                                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                                modifier = Modifier.weight(1f),
                            )
                            Icon(
                                imageVector = AnuraIcons.ChevronRight,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.outlineVariant,
                                modifier = Modifier
                                    .size(20.dp)
                                    .rotate(90f),
                            )
                        }
                        DropdownMenu(
                            expanded = regionMenu,
                            onDismissRequest = { regionMenu = false },
                        ) {
                            JustificationRegions.forEach { option ->
                                DropdownMenuItem(
                                    text = { Text(stringResource(option.nameRes)) },
                                    onClick = {
                                        selectedId = option.id
                                        regionMenu = false
                                    },
                                )
                            }
                        }
                    }
                    Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
                    AnuraSectionLabel(text = stringResource(R.string.justification_refute_model_label))
                    Text(
                        text = stringResource(selected.modelRes),
                        style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.Medium),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            AnuraTextField(
                value = observed,
                onValueChange = { observed = it },
                label = stringResource(R.string.justification_refute_observed),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(96.dp),
                singleLine = false,
                placeholder = stringResource(R.string.justification_refute_observed_mock),
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            AnuraSectionLabel(text = stringResource(R.string.justification_refute_species))
            Box {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(AnuraDimens.sizeTouch)
                        .clip(RoundedCornerShape(AnuraDimens.radiusButton))
                        .background(MaterialTheme.colorScheme.surfaceVariant)
                        .clickable(
                            role = Role.Button,
                            onClick = { speciesMenu = true },
                        )
                        .padding(horizontal = AnuraDimens.spaceGap),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(
                        text = species.ifBlank { stringResource(R.string.justification_refute_species_mock) },
                        style = MaterialTheme.typography.titleMedium.copy(fontStyle = FontStyle.Italic),
                        modifier = Modifier.weight(1f),
                    )
                }
                DropdownMenu(
                    expanded = speciesMenu,
                    onDismissRequest = { speciesMenu = false },
                ) {
                    speciesOptions.forEach { option ->
                        DropdownMenuItem(
                            text = {
                                Text(text = option, fontStyle = FontStyle.Italic)
                            },
                            onClick = {
                                species = option
                                speciesMenu = false
                            },
                        )
                    }
                }
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            AnuraFormButton(
                text = stringResource(R.string.justification_refute_send),
                onClick = onSend,
                style = AnuraFormButtonStyle.Primary,
                icon = AnuraIcons.Send,
            )
        }
    }
}

@Composable
private fun RefuteRegionThumb(region: JustificationRegion) {
    val mask = AnuraTheme.extendedColors.success
    BoxWithConstraints(
        modifier = Modifier
            .size(RefuteThumbSize)
            .clip(RoundedCornerShape(AnuraDimens.radiusCard)),
    ) {
        Image(
            painter = painterResource(R.drawable.carousel_dendrobates_truncatus),
            contentDescription = stringResource(R.string.justification_photo_cd),
            modifier = Modifier.fillMaxSize(),
            contentScale = ContentScale.Crop,
            colorFilter = AnuraTheme.mediaColorFilter,
        )
        Box(
            modifier = Modifier
                .offset(
                    x = maxWidth * region.xFraction,
                    y = maxHeight * region.yFraction,
                )
                .size(
                    width = maxWidth * region.wFraction,
                    height = maxHeight * region.hFraction,
                )
                .clip(RoundedCornerShape(AnuraDimens.radiusButton))
                .background(mask.copy(alpha = 0.30f))
                .border(
                    width = 2.dp,
                    color = mask,
                    shape = RoundedCornerShape(AnuraDimens.radiusButton),
                ),
        )
    }
}

@Composable
private fun regionTint(tint: RegionTint): Color = when (tint) {
    RegionTint.Tertiary -> MaterialTheme.colorScheme.tertiary
    RegionTint.Secondary -> MaterialTheme.colorScheme.secondary
    RegionTint.Success -> AnuraTheme.extendedColors.success
    RegionTint.Info -> AnuraTheme.extendedColors.info
}

@AnuraPreviews
@Composable
private fun IdentificationJustificationPreview() {
    AnuraTheme {
        IdentificationJustificationBody(onSelectRegion = {}, onRefuteAll = {})
    }
}

@androidx.compose.ui.tooling.preview.Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun IdentificationJustificationPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) {
        IdentificationJustificationBody(onSelectRegion = {}, onRefuteAll = {})
    }
}
