package me.juanlabs.anura.feature.observations

import android.content.Intent
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraFormButtonStyle
import me.juanlabs.anura.designsystem.component.AnuraSectionLabel
import me.juanlabs.anura.designsystem.component.AnuraTopBar
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode
import me.juanlabs.anura.feature.capture.AnuraReviewChip
import me.juanlabs.anura.feature.comments.ObservationCommentsOverlay
import me.juanlabs.anura.feature.species.IdentificationJustificationSheet
import me.juanlabs.anura.navigation.MockNavAction
import me.juanlabs.anura.navigation.MockScreenScaffold

private val ObservationHeroHeight = 280.dp

/** `Fotos y observaciones` (§4.1) — top-level, tab 3. */
@Composable
fun ObservationsScreen(
    onOpenObservationDetail: (String) -> Unit,
    onOpenFavorites: () -> Unit,
) {
    MockScreenScaffold(
        title = "Observaciones",
        actions = listOf(
            MockNavAction("Observación foto + audio") { onOpenObservationDetail("obs-001") },
            MockNavAction("Observación solo audio") { onOpenObservationDetail("obs-002") },
            MockNavAction("Ver favoritos", onOpenFavorites),
        ),
    )
}

/** `favoritos (listado)` (§4.1). */
@Composable
fun FavoritesScreen(
    onBackClick: () -> Unit,
    onOpenObservationDetail: (String) -> Unit,
) {
    MockScreenScaffold(
        title = "Favoritos",
        onBackClick = onBackClick,
        actions = listOf(
            MockNavAction("Abrir observación favorita") { onOpenObservationDetail("obs-002") },
        ),
    )
}

/** `Detalles de observación (resultado)` (§4.1, argumento `id`). */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ObservationDetailScreen(
    id: String,
    onBackClick: () -> Unit,
    onOpenSpeciesSheet: (String) -> Unit,
) {
    var showJustification by rememberSaveable { mutableStateOf(false) }
    var showComments by rememberSaveable { mutableStateOf(false) }
    Box(modifier = Modifier.fillMaxSize()) {
    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        topBar = {
            AnuraTopBar(
                title = stringResource(R.string.observation_detail_title),
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
            ObservationMediaCarousel(
                items = mockObservationMedia(id),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(ObservationHeroHeight),
            )
            ObservationTempoActions(
                onOpenComments = { showComments = true },
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            Text(
                text = stringResource(R.string.observation_detail_common_name),
                style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
            )
            Text(
                text = stringResource(R.string.observation_detail_scientific_name),
                style = MaterialTheme.typography.titleMedium.copy(fontStyle = FontStyle.Italic),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            Row(horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap)) {
                StatusPill(
                    text = stringResource(R.string.observation_detail_toxic_chip),
                    warning = true,
                )
                StatusPill(
                    text = stringResource(R.string.observation_detail_iucn_chip),
                    warning = false,
                )
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            AnuraSectionLabel(text = stringResource(R.string.observation_detail_confidence_label))
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
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            Text(
                text = stringResource(R.string.observation_detail_other_candidates),
                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
            )
            CandidateRow(
                name = stringResource(R.string.observation_detail_candidate_1),
                note = stringResource(R.string.observation_detail_candidate_1_note),
                percent = stringResource(R.string.observation_detail_candidate_1_pct),
            )
            CandidateRow(
                name = stringResource(R.string.observation_detail_candidate_2),
                note = stringResource(R.string.observation_detail_candidate_2_note),
                percent = stringResource(R.string.observation_detail_candidate_2_pct),
            )
            CandidateRow(
                name = stringResource(R.string.observation_detail_candidate_3),
                note = stringResource(R.string.observation_detail_candidate_3_note),
                percent = stringResource(R.string.observation_detail_candidate_3_pct),
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            AnuraFormButton(
                text = stringResource(R.string.observation_detail_justification),
                onClick = { showJustification = true },
                style = AnuraFormButtonStyle.Outline,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceActionGap))
            AnuraFormButton(
                text = stringResource(R.string.observation_detail_refute),
                onClick = { showJustification = true },
                style = AnuraFormButtonStyle.Primary,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            Text(
                text = stringResource(R.string.observation_detail_record_data),
                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
            )
            RecordFact(
                label = stringResource(R.string.observation_detail_where),
                value = stringResource(R.string.observation_detail_where_value),
            )
            RecordFact(
                label = stringResource(R.string.observation_detail_when),
                value = stringResource(R.string.observation_detail_when_value),
            )
            RecordFact(
                label = stringResource(R.string.observation_detail_size),
                value = stringResource(R.string.observation_detail_size_value),
            )
            RecordFact(
                label = stringResource(R.string.observation_detail_audio),
                value = stringResource(R.string.observation_detail_audio_value),
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            StatusPill(
                text = stringResource(R.string.observation_detail_synced),
                warning = false,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            AnuraFormButton(
                text = stringResource(R.string.observation_detail_species_sheet),
                onClick = { onOpenSpeciesSheet("ANU_COL_PRIS_PAI_001") },
                style = AnuraFormButtonStyle.Primary,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            AnuraReviewChip(text = stringResource(R.string.observation_detail_expert_review))
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(AnuraDimens.radiusButton))
                    .clickable { showComments = true }
                    .padding(vertical = AnuraDimens.spaceGap)
                    .semantics {
                        role = Role.Button
                    },
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Icon(
                    imageVector = AnuraIcons.Chat,
                    contentDescription = null,
                    tint = AnuraTheme.extendedColors.accentInk,
                )
                Spacer(modifier = Modifier.size(AnuraDimens.spaceGap))
                Text(
                    text = stringResource(R.string.observation_detail_comments),
                    style = MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.SemiBold),
                    modifier = Modifier.weight(1f),
                )
                Icon(
                    imageVector = AnuraIcons.ChevronRight,
                    contentDescription = stringResource(R.string.observation_detail_comments_cd),
                )
            }
        }
    }
    if (showJustification) {
        IdentificationJustificationSheet(onDismiss = { showJustification = false })
    }
    if (showComments) {
        ObservationCommentsOverlay(
            observationId = id,
            onDismiss = { showComments = false },
        ) {
            ObservationMediaCarousel(
                items = mockObservationMedia(id),
                modifier = Modifier.fillMaxSize(),
            )
        }
    }
    }
}

@Composable
private fun ObservationTempoActions(
    onOpenComments: () -> Unit,
) {
    val context = LocalContext.current
    var liked by rememberSaveable { mutableStateOf(false) }
    val commonName = stringResource(R.string.observation_detail_common_name)
    val scientificName = stringResource(R.string.observation_detail_scientific_name)
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
            onClick = { liked = !liked },
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
            onClick = { },
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
private fun CandidateRow(name: String, note: String, percent: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = AnuraDimens.spaceLabelToContent),
        verticalAlignment = Alignment.CenterVertically,
    ) {
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
            text = percent,
            style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
        )
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
        )
    }
}
