package me.juanlabs.anura.feature.capture

import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.height
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.tooling.preview.Preview
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

/**
 * `Paso 5: añadir audio` del asistente. Espectrograma en vivo y transporte circular de
 * [CaptureLiveSpectrogramSession] (la misma sesión de Audio ID). El audio es opcional y todavía
 * no hay modelo de audio: la pantalla lo dice con [AudioDemoNotice].
 */
@Composable
fun CaptureStep5Screen(
    onBackClick: () -> Unit,
    onNext: () -> Unit,
    onSkip: () -> Unit = onNext,
    fromReview: Boolean = false,
    onSave: () -> Unit = onNext,
    onCancel: () -> Unit = onBackClick,
    onCloseClick: () -> Unit = onBackClick,
) {
    var dirty by rememberSaveable { mutableStateOf(false) }
    CaptureWizardScaffold(
        appBarTitle = stringResource(R.string.capture_step5_appbar),
        step = 5,
        onBackClick = onBackClick,
        onCloseClick = onCloseClick,
        unsavedChanges = dirty || fromReview,
    ) {
        CaptureWizardHeading(
            title = stringResource(R.string.capture_step5_title),
            subtitle = stringResource(R.string.capture_step5_subtitle),
        )
        AudioDemoNotice()
        Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
        CaptureLiveSpectrogramSession(
            onAnalyzeAudio = onNext,
            showAnalyzeActions = false,
            onDirtyChange = { dirty = it },
        )
        Spacer(modifier = Modifier.height(CaptureContentToFooterGap))
        CaptureWizardStepFooter(
            fromReview = fromReview,
            onSkip = onSkip,
            onNext = onNext,
            onSave = onSave,
            onCancel = onCancel,
        )
    }
}

@AnuraPreviews
@Composable
private fun CaptureStep5Preview() {
    AnuraTheme { CaptureStep5Screen(onBackClick = {}, onNext = {}) }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun CaptureStep5PreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) { CaptureStep5Screen(onBackClick = {}, onNext = {}) }
}
