package me.juanlabs.anura.feature.capture

import androidx.activity.compose.BackHandler
import androidx.annotation.StringRes
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
import androidx.compose.runtime.mutableStateOf
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
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.async
import kotlinx.coroutines.delay
import kotlinx.coroutines.withTimeoutOrNull
import me.juanlabs.anura.R
import me.juanlabs.anura.core.data.IdentificationCandidate
import me.juanlabs.anura.core.inference.IdentificationFailure
import me.juanlabs.anura.core.inference.IdentificationOutcome
import me.juanlabs.anura.designsystem.component.AnuraBottomSheet
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
private val AnalyzingIdentifyTimeoutMs = 45_000L

private data class AnalyzingStage(
    val title: Int,
    val engine: Int?,
)

private val AnalyzingStages = listOf(
    AnalyzingStage(R.string.analyzing_stage_crop, null),
    AnalyzingStage(R.string.analyzing_stage_compare, R.string.analyzing_stage_compare_engine),
    AnalyzingStage(R.string.analyzing_stage_context, R.string.analyzing_stage_context_engine),
    AnalyzingStage(R.string.analyzing_stage_rank, null),
)

/**
 * `Analizando · progreso por etapas` (§4.1). El sistema no retrocede mientras corre la animación.
 * Con [identifyPhoto] la identificación real corre en paralelo y decide el resultado; si falla,
 * se avisa y no se guarda nada como identificado. Sin él (solo Audio ID) el resultado es una
 * demostración: todavía no hay modelo de audio, y la pantalla lo dice.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AnalyzingScreen(
    onUnknownResult: (String) -> Unit = {},
    source: String = AnuraRoute.Analyzing.Wizard,
    identifyPhoto: (suspend () -> IdentificationOutcome)? = null,
    onIdentified: (IdentificationOutcome.Identified) -> Unit = {},
    onNotAnuro: () -> Unit = {},
    onIdentificationFailed: (IdentificationFailure) -> Unit = {},
    /** Sin paquete de identificación instalado: lleva a Paquetes para bajar el de la región. */
    onOpenPackages: () -> Unit = {},
) {
    BackHandler(enabled = true) { }
    var currentStage by rememberSaveable { mutableIntStateOf(0) }
    var showNotAnuro by rememberSaveable { mutableStateOf(false) }
    var showNoPackage by rememberSaveable { mutableStateOf(false) }
    var showNoOpenSet by rememberSaveable { mutableStateOf(false) }
    LaunchedEffect(Unit) {
        val pending = identifyPhoto?.let { identify ->
            async {
                try {
                    identify()
                } catch (cancelled: CancellationException) {
                    throw cancelled
                } catch (error: Exception) {
                    IdentificationOutcome.Failed(
                        IdentificationFailure.EngineError,
                        error.message ?: error.javaClass.simpleName,
                    )
                }
            }
        }
        AnalyzingStages.indices.forEach { index ->
            currentStage = index
            delay(AnalyzingStageDelayMs)
        }
        if (pending != null) {
            val outcome = try {
                withTimeoutOrNull(AnalyzingIdentifyTimeoutMs) { pending.await() }
            } catch (cancelled: CancellationException) {
                throw cancelled
            } catch (error: Exception) {
                IdentificationOutcome.Failed(
                    IdentificationFailure.EngineError,
                    error.message ?: error.javaClass.simpleName,
                )
            }
            when (outcome) {
                is IdentificationOutcome.Identified -> onIdentified(outcome)
                is IdentificationOutcome.NotAnuro -> showNotAnuro = true
                is IdentificationOutcome.Failed -> when (outcome.reason) {
                    IdentificationFailure.NoActivePackage -> showNoPackage = true
                    IdentificationFailure.NoOpenSetModel -> showNoOpenSet = true
                    else -> onIdentificationFailed(outcome.reason)
                }
                null -> onIdentificationFailed(IdentificationFailure.EngineError)
            }
            return@LaunchedEffect
        }
        // Solo Audio ID llega aquí (sin identificador): demostración, sin especie ni familia.
        onUnknownResult("order")
    }
    val progress = when (currentStage) {
        0 -> 0.25f
        1 -> 0.62f
        2 -> 0.80f
        else -> 1f
    }
    val percent = (progress * 100).toInt()
    val showStages = source == AnuraRoute.Analyzing.Wizard
    val photoCount = CapturePhotoDraft.tokens.size
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
                    // Antes mostraba siempre la misma foto de archivo, sin importar la
                    // foto real capturada por el usuario (auditoría Fase 0-9, P0 #6).
                    // El fallback a la foto de archivo solo aplica si no hay ninguna foto
                    // capturada (no debería ocurrir en un flujo real, pero evita una
                    // pantalla en blanco si algún caller llega aquí sin fotos).
                    val capturedToken = CapturePhotoDraft.tokens.firstOrNull()
                    val capturedPainter = capturedToken?.let { rememberCaptureBackdropPainter(it) }
                    if (capturedPainter != null) {
                        Image(
                            painter = capturedPainter,
                            contentDescription = stringResource(R.string.analyzing_photo_cd),
                            modifier = Modifier.fillMaxSize(),
                            contentScale = ContentScale.Crop,
                            colorFilter = AnuraTheme.mediaColorFilter,
                        )
                    } else {
                        Box(modifier = Modifier.fillMaxSize().background(MaterialTheme.colorScheme.surfaceVariant))
                    }
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
            if (source == AnuraRoute.Analyzing.Audio) {
                Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
                AudioDemoNotice()
            }
            if (source != AnuraRoute.Analyzing.Audio && photoCount > 1) {
                Spacer(modifier = Modifier.height(AnuraDimens.spaceLabelToContent))
                Text(
                    text = stringResource(R.string.analyzing_multi_photos, photoCount),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.fillMaxWidth(),
                )
            }
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
                    val title = if (index == 0 && photoCount > 1) {
                        stringResource(R.string.analyzing_stage_crop_multi)
                    } else {
                        stringResource(stage.title)
                    }
                    AnalyzingStageRow(
                        title = title,
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
    if (showNotAnuro) {
        NotAnuroSheet(onDismiss = { showNotAnuro = false; onNotAnuro() })
    }
    if (showNoPackage) {
        NoPackageSheet(
            onDownload = { showNoPackage = false; onOpenPackages() },
            onDismiss = { showNoPackage = false; onIdentificationFailed(IdentificationFailure.NoActivePackage) },
        )
    }
    if (showNoOpenSet) {
        NoPackageSheet(
            title = R.string.identification_no_openset_title,
            body = R.string.identification_no_openset_body,
            action = R.string.identification_no_openset_action,
            onDownload = { showNoOpenSet = false; onOpenPackages() },
            onDismiss = { showNoOpenSet = false; onIdentificationFailed(IdentificationFailure.NoOpenSetModel) },
        )
    }
}

/**
 * El APK no trae especies: sin paquete de la región no hay con qué comparar la foto. También sirve
 * para un paquete sin modelo de rechazo (se pasa otro texto): hay que bajar uno actualizado.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun NoPackageSheet(
    onDownload: () -> Unit,
    onDismiss: () -> Unit,
    @StringRes title: Int = R.string.identification_no_package_title,
    @StringRes body: Int = R.string.identification_no_package_body,
    @StringRes action: Int = R.string.identification_no_package_action,
) {
    AnuraBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = AnuraDimens.spacePopupInset),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                text = stringResource(title),
                style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
                color = MaterialTheme.colorScheme.onSurface,
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(vertical = AnuraDimens.spaceGap),
            )
            Text(
                text = stringResource(body),
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            AnuraFormButton(
                text = stringResource(action),
                onClick = onDownload,
                style = AnuraFormButtonStyle.Primary,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            AnuraFormButton(
                text = stringResource(R.string.identification_no_package_later),
                onClick = onDismiss,
                style = AnuraFormButtonStyle.OutlineNeutral,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
        }
    }
}

/** Pop-up (`AnuraBottomSheet`, mismo shell que `CaptureConfirmSheet`) cuando el rechazo Open Set
 * supera [me.juanlabs.anura.core.inference.AnuraIdentifier.NotAnuroTau]: no es un rechazo de
 * especie desconocida, es que la foto no parece contener ningún anuro. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun NotAnuroSheet(onDismiss: () -> Unit) {
    AnuraBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = AnuraDimens.spacePopupInset),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                text = stringResource(R.string.identification_not_anuro_title),
                style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
                color = MaterialTheme.colorScheme.onSurface,
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(vertical = AnuraDimens.spaceGap),
            )
            Text(
                text = stringResource(R.string.identification_not_anuro),
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            AnuraFormButton(
                text = stringResource(R.string.identification_not_anuro_action),
                onClick = onDismiss,
                style = AnuraFormButtonStyle.Primary,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
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
    result: OpenSetUnknownResult,
    audioDemo: Boolean = false,
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
            if (audioDemo) {
                AudioDemoNotice()
                Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            }
            result.photoToken?.let { rememberCaptureBackdropPainter(it) }?.let { painter ->
                Image(
                    painter = painter,
                    contentDescription = stringResource(R.string.analyzing_photo_cd),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(AnalyzingPhotoHeight)
                        .clip(RoundedCornerShape(AnuraDimens.radiusCard)),
                    contentScale = ContentScale.Crop,
                    colorFilter = AnuraTheme.mediaColorFilter,
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            }
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
            result.taxonId?.let { taxonId ->
                AnuraFormButton(
                    text = stringResource(result.sheetActionRes),
                    onClick = { onOpenTaxonSheet(taxonId) },
                    style = AnuraFormButtonStyle.Primary,
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceActionGap))
            }
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
        AnalyzingScreen()
    }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun AnalyzingPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) {
        AnalyzingScreen()
    }
}

@AnuraPreviews
@Composable
private fun UnknownResultPreview() {
    AnuraTheme { UnknownResultScreen(onBackClick = {}, result = PreviewUnknownGenus) }
}

@AnuraPreviews
@Composable
private fun UnknownResultFamilyPreview() {
    AnuraTheme {
        UnknownResultScreen(
            onBackClick = {},
            result = PreviewUnknownFamily,
        )
    }
}

@AnuraPreviews
@Composable
private fun UnknownResultOrderPreview() {
    AnuraTheme {
        UnknownResultScreen(
            onBackClick = {},
            result = OpenSetUnknownResults.fromCandidates(emptyList(), null),
        )
    }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun UnknownResultPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) { UnknownResultScreen(onBackClick = {}, result = PreviewUnknownGenus) }
}

// Solo para las vistas previas de Android Studio: candidatas de ejemplo pasadas por el mismo cálculo real.
private val PreviewUnknownGenus = OpenSetUnknownResults.fromCandidates(
    listOf(
        IdentificationCandidate("Pristimantis paisa", 0.5f, genus = "Pristimantis", family = "Strabomantidae"),
        IdentificationCandidate("Pristimantis achatinus", 0.3f, genus = "Pristimantis", family = "Strabomantidae"),
    ),
    null,
)
private val PreviewUnknownFamily = OpenSetUnknownResults.fromCandidates(
    listOf(
        IdentificationCandidate("Pristimantis paisa", 0.4f, genus = "Pristimantis", family = "Strabomantidae"),
        IdentificationCandidate("Craugastor raniformis", 0.3f, genus = "Craugastor", family = "Strabomantidae"),
    ),
    null,
)
