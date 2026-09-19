package me.juanlabs.anura.feature.species

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraFormButtonStyle
import me.juanlabs.anura.designsystem.component.AnuraSectionLabel
import me.juanlabs.anura.designsystem.component.AnuraTopBar
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

private enum class SpeciesSheetTab {
    Taxonomy,
    Morphology,
    Bioacoustics,
    Ecology,
    Conservation,
}

/**
 * `ESPECIE, FAMILIA, GENERO` (ficha técnica, §4.1).
 * Secciones y `DESPLEGABLE1` son estado local, no rutas.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SpeciesSheetScreen(
    speciesId: String,
    onBackClick: () -> Unit,
    onExploreGenus: () -> Unit = {},
) {
    var tab by rememberSaveable(speciesId) { mutableStateOf(SpeciesSheetTab.Morphology) }
    var showJustification by rememberSaveable(speciesId) { mutableStateOf(false) }

    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        topBar = {
            AnuraTopBar(
                title = stringResource(R.string.species_sheet_title),
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
                .padding(horizontal = AnuraDimens.spaceGutter)
                .padding(bottom = 16.dp),
        ) {
            Image(
                painter = painterResource(R.drawable.carousel_dendrobates_truncatus),
                contentDescription = stringResource(R.string.species_sheet_photo_cd),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(180.dp)
                    .clip(RoundedCornerShape(AnuraDimens.radiusCard)),
                contentScale = ContentScale.Crop,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            Text(
                text = stringResource(R.string.species_sheet_common_name),
                style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
            )
            Text(
                text = stringResource(R.string.species_sheet_scientific_name),
                style = MaterialTheme.typography.titleMedium.copy(fontStyle = FontStyle.Italic),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            Row(horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap)) {
                SheetPill(stringResource(R.string.species_sheet_toxic), warning = true)
                SheetPill(stringResource(R.string.species_sheet_iucn), warning = false)
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            Text(
                text = stringResource(R.string.species_sheet_taxonomy_line),
                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            Row(modifier = Modifier.fillMaxWidth()) {
                SpeciesStat(
                    value = stringResource(R.string.species_sheet_stat_observations),
                    label = stringResource(R.string.species_sheet_stat_observations_label),
                    modifier = Modifier.weight(1f),
                )
                SpeciesStat(
                    value = stringResource(R.string.species_sheet_stat_altitude),
                    label = stringResource(R.string.species_sheet_stat_altitude_label),
                    modifier = Modifier.weight(1f),
                )
                SpeciesStat(
                    value = stringResource(R.string.species_sheet_stat_size),
                    label = stringResource(R.string.species_sheet_stat_size_label),
                    modifier = Modifier.weight(1f),
                )
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            Row(
                modifier = Modifier.horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceActionGap),
            ) {
                SpeciesTabChip(
                    label = stringResource(R.string.species_sheet_tab_taxonomy),
                    selected = tab == SpeciesSheetTab.Taxonomy,
                    onClick = { tab = SpeciesSheetTab.Taxonomy },
                )
                SpeciesTabChip(
                    label = stringResource(R.string.species_sheet_tab_morphology),
                    selected = tab == SpeciesSheetTab.Morphology,
                    onClick = { tab = SpeciesSheetTab.Morphology },
                )
                SpeciesTabChip(
                    label = stringResource(R.string.species_sheet_tab_bioacoustics),
                    selected = tab == SpeciesSheetTab.Bioacoustics,
                    onClick = { tab = SpeciesSheetTab.Bioacoustics },
                )
                SpeciesTabChip(
                    label = stringResource(R.string.species_sheet_tab_ecology),
                    selected = tab == SpeciesSheetTab.Ecology,
                    onClick = { tab = SpeciesSheetTab.Ecology },
                )
                SpeciesTabChip(
                    label = stringResource(R.string.species_sheet_tab_conservation),
                    selected = tab == SpeciesSheetTab.Conservation,
                    onClick = { tab = SpeciesSheetTab.Conservation },
                )
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            when (tab) {
                SpeciesSheetTab.Taxonomy -> {
                    Text(
                        text = stringResource(R.string.species_sheet_taxonomy_line),
                        style = MaterialTheme.typography.titleMedium,
                    )
                }
                SpeciesSheetTab.Morphology -> MorphologySection()
                SpeciesSheetTab.Bioacoustics -> {
                    RecordLine(
                        label = stringResource(R.string.observation_detail_audio),
                        value = stringResource(R.string.observation_detail_audio_value),
                    )
                }
                SpeciesSheetTab.Ecology -> {
                    RecordLine(
                        label = stringResource(R.string.species_sheet_stat_altitude_label),
                        value = stringResource(R.string.species_sheet_stat_altitude),
                    )
                }
                SpeciesSheetTab.Conservation -> {
                    RecordLine(
                        label = stringResource(R.string.species_sheet_tab_conservation),
                        value = stringResource(R.string.species_sheet_iucn),
                    )
                }
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            GeographicLocationSection()
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            AnuraFormButton(
                text = stringResource(R.string.observation_detail_justification),
                onClick = { showJustification = true },
                style = AnuraFormButtonStyle.Outline,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceActionGap))
            AnuraFormButton(
                text = stringResource(R.string.species_sheet_export),
                onClick = { },
                style = AnuraFormButtonStyle.Outline,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceActionGap))
            AnuraFormButton(
                text = stringResource(R.string.species_sheet_explore_genus),
                onClick = onExploreGenus,
                style = AnuraFormButtonStyle.Outline,
            )
        }
    }
    if (showJustification) {
        IdentificationJustificationSheet(onDismiss = { showJustification = false })
    }
}

@Composable
private fun MorphologySection() {
    Text(
        text = stringResource(R.string.species_sheet_morphology_title),
        style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
    )
    RecordLine(
        label = stringResource(R.string.species_sheet_tympanum),
        value = stringResource(R.string.species_sheet_tympanum_value),
    )
    RecordLine(
        label = stringResource(R.string.species_sheet_disc),
        value = stringResource(R.string.species_sheet_disc_value),
    )
    RecordLine(
        label = stringResource(R.string.species_sheet_fold),
        value = stringResource(R.string.species_sheet_fold_value),
    )
    RecordLine(
        label = stringResource(R.string.species_sheet_dorsal),
        value = stringResource(R.string.species_sheet_dorsal_value),
    )
    RecordLine(
        label = stringResource(R.string.species_sheet_ventral),
        value = stringResource(R.string.species_sheet_ventral_value),
    )
    RecordLine(
        label = stringResource(R.string.species_sheet_webbing),
        value = stringResource(R.string.species_sheet_webbing_value),
    )
    RecordLine(
        label = stringResource(R.string.species_sheet_svl),
        value = stringResource(R.string.species_sheet_svl_value),
    )
}

@Composable
private fun RecordLine(label: String, value: String) {
    Column(modifier = Modifier.padding(vertical = AnuraDimens.spaceLabelToContent)) {
        AnuraSectionLabel(text = label)
        Text(text = value, style = MaterialTheme.typography.titleMedium)
    }
}

@Composable
private fun SpeciesStat(value: String, label: String, modifier: Modifier = Modifier) {
    Column(modifier = modifier) {
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Medium),
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun SpeciesTabChip(
    label: String,
    selected: Boolean,
    onClick: () -> Unit,
) {
    FilterChip(
        selected = selected,
        onClick = onClick,
        label = { Text(text = label) },
        colors = FilterChipDefaults.filterChipColors(
            selectedContainerColor = AnuraTheme.extendedColors.accentInk,
            selectedLabelColor = MaterialTheme.colorScheme.onPrimary,
        ),
    )
}

@Composable
private fun SheetPill(text: String, warning: Boolean) {
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

@AnuraPreviews
@Composable
private fun SpeciesSheetPreview() {
    AnuraTheme { SpeciesSheetScreen(speciesId = "ANU_COL_PRIS_PAI_001", onBackClick = {}) }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun SpeciesSheetPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) {
        SpeciesSheetScreen(speciesId = "ANU_COL_PRIS_PAI_001", onBackClick = {})
    }
}
