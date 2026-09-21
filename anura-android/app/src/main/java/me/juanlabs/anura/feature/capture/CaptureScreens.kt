package me.juanlabs.anura.feature.capture

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraCard
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraFormButtonStyle
import me.juanlabs.anura.designsystem.component.AnuraSectionLabel
import me.juanlabs.anura.designsystem.component.AnuraTopBar
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode
import me.juanlabs.anura.navigation.AnuraRoute

private val AnalyzingPhotoHeight = 220.dp
private val AnalyzingStageDelayMs = 1_100L

private data class AnalyzingStage(
    val title: Int,
    val engine: Int?,
)

private val AnalyzingStages = listOf(
    AnalyzingStage(R.string.analyzing_stage_crop, R.string.analyzing_stage_crop_engine),
    AnalyzingStage(R.string.analyzing_stage_compare, R.string.analyzing_stage_compare_engine),
    AnalyzingStage(R.string.analyzing_stage_context, R.string.analyzing_stage_context_engine),
    AnalyzingStage(R.string.analyzing_stage_rank, null),
)

/**
 * `Analizando · progreso por etapas` (§4.1). El sistema no retrocede mientras corre
 * el mock de etapas; al terminar navega al resultado conocido o al open-set.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AnalyzingScreen(
    onKnownResult: () -> Unit,
    onUnknownResult: (String) -> Unit = {},
    source: String = AnuraRoute.Analyzing.Wizard,
) {
    BackHandler(enabled = true) { }
    var currentStage by rememberSaveable { mutableIntStateOf(0) }
    LaunchedEffect(Unit) {
        AnalyzingStages.indices.forEach { index ->
            currentStage = index
            delay(AnalyzingStageDelayMs)
        }
        when (source) {
            AnuraRoute.Analyzing.Image -> onUnknownResult("genus")
            AnuraRoute.Analyzing.Audio -> onUnknownResult("family")
            else -> onKnownResult()
        }
    }
    val progress = when (currentStage) {
        0 -> 0.25f
        1 -> 0.62f
        2 -> 0.80f
        else -> 1f
    }
    val percent = (progress * 100).toInt()
    val showStages = source == AnuraRoute.Analyzing.Wizard
    val headline = stringResource(
        when (source) {
            AnuraRoute.Analyzing.Image -> R.string.analyzing_via_image
            AnuraRoute.Analyzing.Audio -> R.string.analyzing_via_audio
            else -> R.string.analyzing_label
        },
    )

    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        topBar = {
            AnuraTopBar(
                title = stringResource(R.string.analyzing_title),
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
                .padding(bottom = CaptureBottomBreathing),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(AnalyzingPhotoHeight)
                    .clip(RoundedCornerShape(AnuraDimens.radiusCard)),
                contentAlignment = Alignment.Center,
            ) {
                if (source == AnuraRoute.Analyzing.Audio) {
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .background(MaterialTheme.colorScheme.surfaceVariant),
                    )
                    Icon(
                        imageVector = AnuraIcons.AudioId,
                        contentDescription = stringResource(R.string.analyzing_audio_cd),
                        tint = AnuraTheme.extendedColors.accentInk,
                        modifier = Modifier.size(64.dp),
                    )
                } else {
                    Image(
                        painter = painterResource(R.drawable.carousel_dendrobates_truncatus),
                        contentDescription = stringResource(R.string.analyzing_photo_cd),
                        modifier = Modifier.fillMaxSize(),
                        contentScale = ContentScale.Crop,
                    )
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .background(MaterialTheme.colorScheme.scrim.copy(alpha = 0.28f)),
                    )
                }
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            Text(
                text = headline,
                style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
                color = MaterialTheme.colorScheme.onSurface,
                textAlign = TextAlign.Center,
                modifier = Modifier.fillMaxWidth(),
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            LinearProgressIndicator(
                progress = { progress },
                modifier = Modifier.fillMaxWidth(),
                color = AnuraTheme.extendedColors.accentInk,
                trackColor = MaterialTheme.colorScheme.surfaceVariant,
                drawStopIndicator = {},
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceLabelToContent))
            Text(
                text = stringResource(R.string.analyzing_progress_pct, percent),
                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.fillMaxWidth(),
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            if (showStages) {
                AnalyzingStages.forEachIndexed { index, stage ->
                    AnalyzingStageRow(
                        title = stringResource(stage.title),
                        engine = stage.engine?.let { stringResource(it) },
                        state = when {
                            index < currentStage -> AnalyzingStageState.Done
                            index == currentStage -> AnalyzingStageState.Current
                            else -> AnalyzingStageState.Pending
                        },
                    )
                    Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
                }
            }
            AnuraCard(modifier = Modifier.fillMaxWidth()) {
                Row(
                    modifier = Modifier.padding(
                        horizontal = AnuraDimens.spaceCardInsetHorizontal,
                        vertical = AnuraDimens.spaceCardInsetVertical,
                    ),
                    verticalAlignment = Alignment.Top,
                ) {
                    Icon(
                        imageVector = AnuraIcons.CloudOff,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.size(24.dp),
                    )
                    Spacer(modifier = Modifier.size(AnuraDimens.spaceGap))
                    Text(
                        text = stringResource(R.string.analyzing_offline),
                        style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.Medium),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
        }
    }
}

private enum class AnalyzingStageState { Done, Current, Pending }

@Composable
private fun AnalyzingStageRow(
    title: String,
    engine: String?,
    state: AnalyzingStageState,
) {
    val statusCd = stringResource(
        when (state) {
            AnalyzingStageState.Done -> R.string.analyzing_stage_done_cd
            AnalyzingStageState.Current -> R.string.analyzing_stage_current_cd
            AnalyzingStageState.Pending -> R.string.analyzing_stage_pending_cd
        },
    )
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .semantics { contentDescription = "$statusCd. $title" },
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            modifier = Modifier.size(AnuraDimens.sizeTouch / 2),
            contentAlignment = Alignment.Center,
        ) {
            when (state) {
                AnalyzingStageState.Done -> Icon(
                    imageVector = AnuraIcons.Check,
                    contentDescription = null,
                    tint = AnuraTheme.extendedColors.accentInk,
                    modifier = Modifier.size(20.dp),
                )
                AnalyzingStageState.Current -> Box(
                    modifier = Modifier
                        .size(12.dp)
                        .clip(CircleShape)
                        .background(AnuraTheme.extendedColors.accentInk),
                )
                AnalyzingStageState.Pending -> Box(
                    modifier = Modifier
                        .size(12.dp)
                        .clip(CircleShape)
                        .background(MaterialTheme.colorScheme.outlineVariant),
                )
            }
        }
        Spacer(modifier = Modifier.size(AnuraDimens.spaceGap))
        Text(
            text = title,
            style = MaterialTheme.typography.titleMedium.copy(
                fontWeight = if (state == AnalyzingStageState.Current) FontWeight.SemiBold else FontWeight.Normal,
            ),
            color = MaterialTheme.colorScheme.onSurface,
            modifier = Modifier.weight(1f),
        )
        if (engine != null) {
            Text(
                text = engine,
                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Medium),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

/** `Resultado open-set: especie no registrada` (§4.1). */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun UnknownResultScreen(
    onBackClick: () -> Unit,
    result: OpenSetUnknownResult = MockOpenSetUnknownResults.Genus,
    onOpenTaxonSheet: (String) -> Unit = {},
    onRequestExpertReview: () -> Unit = {},
) {
    val unconfirmed = stringResource(R.string.unknown_result_unconfirmed)
    val nonePct = stringResource(R.string.unknown_result_pct_none)
    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        topBar = {
            AnuraTopBar(
                title = stringResource(R.string.unknown_result_title),
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
                .padding(bottom = CaptureBottomBreathing),
        ) {
            Image(
                painter = painterResource(result.photoRes),
                contentDescription = stringResource(R.string.analyzing_photo_cd),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(AnalyzingPhotoHeight)
                    .clip(RoundedCornerShape(AnuraDimens.radiusCard)),
                contentScale = ContentScale.Crop,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            Text(
                text = result.headline,
                style = MaterialTheme.typography.headlineSmall.copy(
                    fontWeight = FontWeight.Bold,
                    fontStyle = FontStyle.Italic,
                ),
                color = MaterialTheme.colorScheme.onSurface,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceTitleToSubtitle))
            Text(
                text = stringResource(result.subtitleRes),
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            AnuraCard(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(
                        horizontal = AnuraDimens.spaceCardInsetHorizontal,
                        vertical = AnuraDimens.spaceCardInsetVertical,
                    ),
                ) {
                    Text(
                        text = stringResource(R.string.unknown_result_not_a_failure),
                        style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                    )
                    Spacer(modifier = Modifier.height(AnuraDimens.spaceLabelToContent))
                    Text(
                        text = stringResource(result.bodyRes, result.bodyName),
                        style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.Medium),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            Text(
                text = stringResource(R.string.unknown_result_how_far),
                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            RankRow(
                label = stringResource(R.string.unknown_result_order),
                line = result.order,
                unconfirmed = unconfirmed,
                nonePct = nonePct,
            )
            RankRow(
                label = stringResource(R.string.unknown_result_family),
                line = result.family,
                unconfirmed = unconfirmed,
                nonePct = nonePct,
            )
            RankRow(
                label = stringResource(R.string.unknown_result_genus),
                line = result.genus,
                unconfirmed = unconfirmed,
                nonePct = nonePct,
            )
            RankRow(
                label = stringResource(R.string.unknown_result_species),
                line = result.species,
                unconfirmed = unconfirmed,
                nonePct = nonePct,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            AnuraReviewChip(text = stringResource(R.string.unknown_result_needs_review))
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            AnuraFormButton(
                text = stringResource(result.sheetActionRes),
                onClick = { onOpenTaxonSheet(result.taxonId) },
                style = AnuraFormButtonStyle.Primary,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceActionGap))
            AnuraFormButton(
                text = stringResource(R.string.unknown_result_send_review),
                onClick = onRequestExpertReview,
                style = AnuraFormButtonStyle.Outline,
            )
        }
    }
}

@Composable
private fun RankRow(
    label: String,
    line: OpenSetRankLine,
    unconfirmed: String,
    nonePct: String,
) {
    val valueColor = if (line.confirmed) {
        MaterialTheme.colorScheme.onSurface
    } else {
        MaterialTheme.colorScheme.onSurfaceVariant
    }
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = AnuraDimens.spaceLabelToContent),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(modifier = Modifier.weight(1f)) {
            AnuraSectionLabel(text = label)
            Text(
                text = if (line.confirmed) line.value else unconfirmed,
                style = MaterialTheme.typography.titleMedium.copy(
                    fontWeight = FontWeight.SemiBold,
                    fontStyle = if (line.confirmed) FontStyle.Normal else FontStyle.Italic,
                ),
                color = valueColor,
            )
        }
        Text(
            text = if (line.confirmed) line.percent else nonePct,
            style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
            color = valueColor,
        )
    }
}

@Composable
internal fun AnuraReviewChip(
    text: String,
    modifier: Modifier = Modifier,
) {
    Text(
        text = text,
        style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
        color = AnuraTheme.extendedColors.onWarning,
        modifier = modifier
            .clip(RoundedCornerShape(AnuraDimens.radiusCapsule))
            .background(AnuraTheme.extendedColors.warning)
            .padding(horizontal = 10.dp, vertical = 4.dp),
    )
}

@AnuraPreviews
@Composable
private fun AnalyzingPreview() {
    AnuraTheme {
        AnalyzingScreen(onKnownResult = {})
    }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun AnalyzingPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) {
        AnalyzingScreen(onKnownResult = {})
    }
}

@AnuraPreviews
@Composable
private fun UnknownResultPreview() {
    AnuraTheme { UnknownResultScreen(onBackClick = {}) }
}

@AnuraPreviews
@Composable
private fun UnknownResultFamilyPreview() {
    AnuraTheme {
        UnknownResultScreen(
            onBackClick = {},
            result = MockOpenSetUnknownResults.Family,
        )
    }
}

@AnuraPreviews
@Composable
private fun UnknownResultOrderPreview() {
    AnuraTheme {
        UnknownResultScreen(
            onBackClick = {},
            result = MockOpenSetUnknownResults.Order,
        )
    }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun UnknownResultPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) { UnknownResultScreen(onBackClick = {}) }
}
