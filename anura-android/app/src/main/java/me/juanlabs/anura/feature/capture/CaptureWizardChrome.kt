package me.juanlabs.anura.feature.capture

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBars
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
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import me.juanlabs.anura.R
import me.juanlabs.anura.core.data.AnuraRepository
import me.juanlabs.anura.designsystem.component.AnuraBottomSheet
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraFormButtonStyle
import me.juanlabs.anura.designsystem.component.AnuraTopBar
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme

internal const val CaptureWizardTotalSteps = 6
const val CaptureDraftPhotoCountKey = "capture_photo_count"

internal object CapturePhotoDraft {
    var tokens: List<String>
        get() = if (AnuraRepository.isInitialized) {
            AnuraRepository.instance.snapshot.draft.photoTokens
        } else {
            emptyList()
        }
        set(value) {
            if (AnuraRepository.isInitialized) {
                AnuraRepository.instance.setDraftPhotos(value)
            }
        }

    fun reset() {
        if (AnuraRepository.isInitialized) {
            AnuraRepository.instance.resetDraft()
        }
    }
}

internal val CaptureProgressHeight = 6.dp
internal val CaptureProgressGap = 12.dp
internal val CaptureProgressToTitleGap = 14.dp
internal val CaptureTitleToSubtitleGap = 4.dp
internal val CaptureSubtitleToContentGap = 16.dp
internal val CaptureNoteToSkipGap = AnuraDimens.spaceGap
internal val CaptureBottomBreathing = 16.dp

/** Contenido → pie de botones del wizard (Step1 microhábitat, Step2/3/5, AudioCapture). */
internal val CaptureContentToFooterGap = 20.dp

@OptIn(ExperimentalMaterial3Api::class)
@Composable
internal fun CaptureWizardScaffold(
    appBarTitle: String,
    step: Int,
    onBackClick: () -> Unit,
    scrollable: Boolean = true,
    showProgress: Boolean = true,
    edgeToEdge: Boolean = false,
    onCloseClick: (() -> Unit)? = null,
    unsavedChanges: Boolean = false,
    unsavedTitle: String = stringResource(R.string.capture_unsaved_title),
    unsavedBody: String = stringResource(R.string.capture_unsaved_body),
    content: @Composable ColumnScope.() -> Unit,
) {
    val closeCd = stringResource(R.string.capture_wizard_close_cd)
    var confirmLeave by rememberSaveable { mutableStateOf(false) }
    fun requestBack() {
        if (unsavedChanges) confirmLeave = true else onBackClick()
    }
    BackHandler { requestBack() }
    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        contentWindowInsets = WindowInsets.navigationBars,
        topBar = {
            AnuraTopBar(
                title = appBarTitle,
                onBackClick = { requestBack() },
                centerTitle = true,
                actions = {
                    if (onCloseClick != null) {
                        IconButton(
                            onClick = onCloseClick,
                            modifier = Modifier.size(AnuraDimens.sizeTouch),
                        ) {
                            Icon(
                                imageVector = AnuraIcons.Close,
                                contentDescription = closeCd,
                            )
                        }
                    }
                },
            )
        },
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .then(if (scrollable) Modifier.verticalScroll(rememberScrollState()) else Modifier)
                .padding(horizontal = if (edgeToEdge) 0.dp else AnuraDimens.spaceGutter)
                .padding(bottom = CaptureBottomBreathing),
        ) {
            if (showProgress) {
                CaptureWizardProgress(currentStep = step, totalSteps = CaptureWizardTotalSteps)
                Spacer(modifier = Modifier.height(CaptureProgressToTitleGap))
            }
            content()
        }
    }
    if (confirmLeave) {
        CaptureConfirmSheet(
            title = unsavedTitle,
            body = unsavedBody,
            onConfirm = {
                confirmLeave = false
                onBackClick()
            },
            onDismiss = { confirmLeave = false },
        )
    }
}

@Composable
internal fun CaptureWizardHeading(
    title: String,
    subtitle: String,
) {
    Text(
        text = title,
        style = MaterialTheme.typography.headlineSmall.copy(
            fontWeight = FontWeight.Bold,
            lineHeight = 32.sp,
        ),
        color = MaterialTheme.colorScheme.onSurface,
    )
    Spacer(modifier = Modifier.height(CaptureTitleToSubtitleGap))
    Text(
        text = subtitle,
        style = MaterialTheme.typography.titleMedium.copy(
            fontWeight = FontWeight.Normal,
            lineHeight = 22.sp,
        ),
        color = MaterialTheme.colorScheme.onSurface,
    )
    Spacer(modifier = Modifier.height(CaptureSubtitleToContentGap))
}

@Composable
internal fun CaptureWizardOptionalActions(
    onSkip: () -> Unit,
    onNext: () -> Unit,
    nextLabel: String = stringResource(R.string.capture_wizard_next),
) {
    AnuraFormButton(
        text = nextLabel,
        onClick = onNext,
        style = AnuraFormButtonStyle.Primary,
    )
    Spacer(modifier = Modifier.height(AnuraDimens.spaceActionGap))
    AnuraFormButton(
        text = stringResource(R.string.capture_wizard_skip),
        onClick = onSkip,
        style = AnuraFormButtonStyle.Outline,
    )
    Spacer(modifier = Modifier.height(CaptureNoteToSkipGap))
    CaptureWizardSkipNote()
}

@Composable
private fun CaptureWizardSkipNote() {
    Text(
        text = stringResource(R.string.capture_wizard_optional_note),
        style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.Medium),
        color = MaterialTheme.colorScheme.onSurfaceVariant,
        textAlign = TextAlign.Center,
        modifier = Modifier.fillMaxWidth(),
    )
}

@Composable
internal fun CaptureWizardPrimaryAction(
    onNext: () -> Unit,
    enabled: Boolean = true,
    nextLabel: String = stringResource(R.string.capture_wizard_next),
) {
    AnuraFormButton(
        text = nextLabel,
        onClick = onNext,
        style = AnuraFormButtonStyle.Primary,
        enabled = enabled,
    )
}

@Composable
internal fun CaptureWizardStepFooter(
    fromReview: Boolean,
    onSkip: () -> Unit,
    onNext: () -> Unit,
    onSave: () -> Unit,
    onCancel: () -> Unit,
    nextEnabled: Boolean = true,
    showSkip: Boolean = true,
    nextLabel: String = stringResource(R.string.capture_wizard_next),
) {
    if (fromReview) {
        var confirmCancel by rememberSaveable { mutableStateOf(false) }
        AnuraFormButton(
            text = stringResource(R.string.capture_wizard_save),
            onClick = onSave,
            style = AnuraFormButtonStyle.Primary,
            enabled = nextEnabled,
        )
        Spacer(modifier = Modifier.height(AnuraDimens.spaceActionGap))
        AnuraFormButton(
            text = stringResource(R.string.anura_cancel),
            onClick = { confirmCancel = true },
            style = AnuraFormButtonStyle.Outline,
        )
        if (confirmCancel) {
            CaptureConfirmSheet(
                title = stringResource(R.string.capture_wizard_cancel_edit_title),
                body = stringResource(R.string.capture_wizard_cancel_edit_body),
                onConfirm = {
                    confirmCancel = false
                    onCancel()
                },
                onDismiss = { confirmCancel = false },
            )
        }
    } else if (showSkip) {
        CaptureWizardOptionalActions(
            onSkip = onSkip,
            onNext = onNext,
            nextLabel = nextLabel,
        )
    } else {
        CaptureWizardPrimaryAction(
            onNext = onNext,
            enabled = nextEnabled,
            nextLabel = nextLabel,
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
internal fun CaptureConfirmSheet(
    title: String,
    body: String,
    onConfirm: () -> Unit,
    onDismiss: () -> Unit,
    confirmLabel: String = stringResource(R.string.anura_accept),
    dismissLabel: String = stringResource(R.string.anura_discard),
) {
    AnuraBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = AnuraDimens.spacePopupInset),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
                color = MaterialTheme.colorScheme.onSurface,
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(vertical = AnuraDimens.spaceGap),
            )
            Text(
                text = body,
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            AnuraFormButton(
                text = confirmLabel,
                onClick = onConfirm,
                style = AnuraFormButtonStyle.Primary,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceActionGap))
            AnuraFormButton(
                text = dismissLabel,
                onClick = onDismiss,
                style = AnuraFormButtonStyle.Outline,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
        }
    }
}

@Composable
internal fun CaptureWizardProgress(
    currentStep: Int,
    totalSteps: Int,
) {
    val description = stringResource(
        R.string.capture_wizard_progress_cd,
        currentStep,
        totalSteps,
    )
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .semantics { contentDescription = description },
        horizontalArrangement = Arrangement.spacedBy(CaptureProgressGap),
    ) {
        repeat(totalSteps) { index ->
            val completed = index < currentStep
            Box(
                modifier = Modifier
                    .weight(1f)
                    .height(CaptureProgressHeight)
                    .clip(RoundedCornerShape(AnuraDimens.radiusCapsule))
                    .background(
                        if (completed) {
                            AnuraTheme.extendedColors.accentInk
                        } else {
                            MaterialTheme.colorScheme.surfaceVariant
                        },
                    ),
            )
        }
    }
}
