package me.juanlabs.anura.feature.capture

import android.net.Uri
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
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraFormButtonStyle
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

/** `Añadir audio`. Misma interfaz que el paso 5 del wizard. */
@Composable
fun AudioCaptureScreen(
    onBackClick: () -> Unit,
    onAnalyze: () -> Unit = onBackClick,
    onCloseClick: () -> Unit = onBackClick,
) {
    var localUri by rememberSaveable { mutableStateOf<String?>(null) }
    var dirty by rememberSaveable { mutableStateOf(false) }
    if (localUri != null) {
        CaptureLocalAudioScreen(
            uri = Uri.parse(localUri),
            onBackClick = { localUri = null },
            useLabel = stringResource(R.string.audio_capture_analyze),
            onUseAudio = {
                localUri = null
                onAnalyze()
            },
            onCloseClick = onCloseClick,
        )
        return
    }
    var hasRecording by rememberSaveable { mutableStateOf(false) }
    CaptureWizardScaffold(
        appBarTitle = stringResource(R.string.audio_capture_title),
        step = 5,
        onBackClick = onBackClick,
        showProgress = false,
        onCloseClick = onCloseClick,
        unsavedChanges = dirty,
    ) {
        CaptureWizardHeading(
            title = stringResource(R.string.capture_step5_title),
            subtitle = stringResource(R.string.audio_capture_subtitle),
        )
        CaptureLiveSpectrogramSession(
            onOpenStorage = { localUri = it.toString() },
            onRecordedChange = { hasRecording = it },
            onDirtyChange = { dirty = it },
        )
        Spacer(modifier = Modifier.height(CaptureContentToFooterGap))
        AnuraFormButton(
            text = stringResource(R.string.audio_capture_analyze),
            onClick = onAnalyze,
            style = AnuraFormButtonStyle.Primary,
            enabled = hasRecording,
        )
    }
}

@AnuraPreviews
@Composable
private fun AudioCapturePreview() {
    AnuraTheme { AudioCaptureScreen(onBackClick = {}) }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun AudioCapturePreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) { AudioCaptureScreen(onBackClick = {}) }
}
