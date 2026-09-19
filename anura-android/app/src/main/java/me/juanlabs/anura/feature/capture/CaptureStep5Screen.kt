package me.juanlabs.anura.feature.capture

import android.content.Intent
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.EnterTransition
import androidx.compose.animation.ExitTransition
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraCard
import me.juanlabs.anura.designsystem.component.AnuraPermissionKind
import me.juanlabs.anura.designsystem.component.rememberSystemPermissionGranted
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraMotion
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode
import me.juanlabs.anura.designsystem.theme.rememberReduceMotion

private enum class Step5AudioPhase {
    Idle,
    Recording,
    Paused,
    Recorded,
}

/** Modo de los controles de transporte, derivado de [Step5AudioPhase] para animar entre filas. */
private enum class Step5TransportMode {
    Recording,
    Paused,
    Idle,
}

/** `Paso 5: Añadir audio`. Espectrograma en vivo y transporte circular. Audio opcional. */
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
        CaptureLiveSpectrogramSession(
            onAnalyzeAudio = onNext,
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

@Composable
internal fun CaptureLiveSpectrogramSession(
    onAnalyzeAudio: () -> Unit,
    analyzeLabel: String = stringResource(R.string.audio_capture_analyze),
    onRecordedChange: (Boolean) -> Unit = {},
    onDirtyChange: (Boolean) -> Unit = {},
) {
    val context = LocalContext.current
    val micGranted = rememberSystemPermissionGranted(AnuraPermissionKind.Microphone)
    var phase by rememberSaveable { mutableStateOf(Step5AudioPhase.Idle) }
    var elapsedSeconds by rememberSaveable { mutableIntStateOf(0) }
    var playbackUri by rememberSaveable { mutableStateOf<String?>(null) }
    val capture = remember { LiveAudioCaptureHandle() }

    LaunchedEffect(phase, playbackUri) {
        onDirtyChange(phase != Step5AudioPhase.Idle || playbackUri != null)
        onRecordedChange(playbackUri != null)
        if (phase == Step5AudioPhase.Recorded) {
            delay(80)
            val file = capture.file
            if (file != null && file.exists() && file.length() > 44L) {
                playbackUri = Uri.fromFile(file).toString()
            }
            phase = Step5AudioPhase.Idle
            elapsedSeconds = 0
        }
    }
    val filePicker = rememberLauncherForActivityResult(
        ActivityResultContracts.OpenDocument(),
    ) { uri: Uri? ->
        if (uri != null) {
            runCatching {
                context.contentResolver.takePersistableUriPermission(
                    uri,
                    Intent.FLAG_GRANT_READ_URI_PERMISSION,
                )
            }
            playbackUri = uri.toString()
            phase = Step5AudioPhase.Idle
            elapsedSeconds = 0
        }
    }

    val recording = phase == Step5AudioPhase.Recording
    val paused = phase == Step5AudioPhase.Paused
    val clipUri = playbackUri?.let { Uri.parse(it) }
    val micLive = rememberMicWaveform(
        active = (recording || paused) && micGranted && clipUri == null,
        paused = paused,
        capture = capture,
    )
    val reduceMotion = rememberReduceMotion()

    if (clipUri != null) {
        CaptureReadyClipPlayback(
            uri = clipUri,
            analyzeLabel = analyzeLabel,
            onAnalyzeAudio = onAnalyzeAudio,
            onReject = {
                playbackUri = null
                phase = Step5AudioPhase.Idle
                elapsedSeconds = 0
            },
        )
    } else {
        val spectroPhase = when (phase) {
            Step5AudioPhase.Idle -> CaptureSpectrogramPhase.Idle
            Step5AudioPhase.Recording -> CaptureSpectrogramPhase.Recording
            Step5AudioPhase.Paused -> CaptureSpectrogramPhase.Recorded
            Step5AudioPhase.Recorded -> CaptureSpectrogramPhase.Recorded
        }
        val transportMode = when (phase) {
            Step5AudioPhase.Recording -> Step5TransportMode.Recording
            Step5AudioPhase.Paused -> Step5TransportMode.Paused
            Step5AudioPhase.Idle, Step5AudioPhase.Recorded -> Step5TransportMode.Idle
        }
        CaptureAudioRecorderCard(
            phase = spectroPhase,
            dominantKhz = micLive.dominantKhz,
            elapsedSeconds = elapsedSeconds,
            amplitudes = micLive.amplitudes,
            amplitude = micLive.level,
        )
        Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
        if (recording) {
            CaptureRecordingTicker(startAt = elapsedSeconds, onTick = { elapsedSeconds = it })
        }
        AnimatedContent(
            targetState = transportMode,
            transitionSpec = {
                if (reduceMotion) {
                    EnterTransition.None togetherWith ExitTransition.None
                } else {
                    fadeIn(tween(AnuraMotion.DurationShort)) togetherWith fadeOut(tween(AnuraMotion.DurationShort))
                }
            },
            label = "CaptureStep5Transport",
        ) { mode ->
            when (mode) {
                Step5TransportMode.Recording -> Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    CaptureCircleIconButton(
                        icon = AnuraIcons.Pause,
                        contentDescription = stringResource(R.string.capture_step5_pause),
                        filled = true,
                        large = true,
                        onClick = { phase = Step5AudioPhase.Paused },
                    )
                    CaptureCircleIconButton(
                        icon = AnuraIcons.Stop,
                        contentDescription = stringResource(R.string.capture_step5_use_clip_cd),
                        filled = false,
                        large = true,
                        onClick = { phase = Step5AudioPhase.Recorded },
                    )
                }
                Step5TransportMode.Paused -> Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    CaptureCircleIconButton(
                        icon = AnuraIcons.Pause,
                        contentDescription = stringResource(R.string.capture_step5_pause),
                        filled = false,
                        large = true,
                        enabled = false,
                        onClick = { },
                    )
                    CaptureCircleIconButton(
                        icon = AnuraIcons.Play,
                        contentDescription = stringResource(R.string.capture_step5_record_cd),
                        filled = true,
                        large = true,
                        enabled = micGranted,
                        onClick = { phase = Step5AudioPhase.Recording },
                    )
                    CaptureCircleIconButton(
                        icon = AnuraIcons.Stop,
                        contentDescription = stringResource(R.string.capture_step5_use_clip_cd),
                        filled = false,
                        large = true,
                        onClick = { phase = Step5AudioPhase.Recorded },
                    )
                }
                Step5TransportMode.Idle -> Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    CaptureCircleIconButton(
                        icon = AnuraIcons.FolderOpen,
                        contentDescription = stringResource(R.string.capture_step5_storage_cd),
                        filled = false,
                        onClick = { filePicker.launch(arrayOf("audio/*")) },
                    )
                    CaptureCircleIconButton(
                        icon = AnuraIcons.Play,
                        contentDescription = stringResource(R.string.capture_step5_record_cd),
                        filled = true,
                        large = true,
                        enabled = micGranted,
                        onClick = {
                            if (micGranted) {
                                if (phase != Step5AudioPhase.Recorded) elapsedSeconds = 0
                                phase = Step5AudioPhase.Recording
                            }
                        },
                    )
                }
            }
        }
    }
}

@Composable
private fun CaptureReadyClipPlayback(
    uri: Uri,
    analyzeLabel: String,
    onAnalyzeAudio: () -> Unit,
    onReject: () -> Unit,
) {
    val player = rememberCaptureAudioPlayer(uri)
    val live = rememberPlaybackWaveform(
        uri = uri,
        playing = player.playing,
        positionMs = player.positionMs,
        sessionId = player.sessionId,
    )
    CaptureAudioRecorderCard(
        phase = if (player.playing) {
            CaptureSpectrogramPhase.Playing
        } else {
            CaptureSpectrogramPhase.Recorded
        },
        dominantKhz = live.dominantKhz,
        elapsedSeconds = player.positionMs / 1000,
        amplitudes = live.amplitudes,
        amplitude = live.level,
    )
    Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
    CaptureAudioPlaybackControls(
        player = player,
        onAnalyze = onAnalyzeAudio,
        onReject = onReject,
        analyzeLabel = analyzeLabel,
    )
}

@Composable
internal fun CaptureAudioRecorderCard(
    phase: CaptureSpectrogramPhase,
    dominantKhz: Float,
    elapsedSeconds: Int,
    amplitudes: List<Float> = emptyList(),
    amplitude: Float = 0f,
) {
    val khzLabel = formatDominantKhz(dominantKhz)
    AnuraCard(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(
                horizontal = AnuraDimens.spaceCardInsetHorizontal,
                vertical = AnuraDimens.spaceCardInsetVertical,
            ),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                text = stringResource(R.string.capture_step5_dominant, khzLabel),
                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                color = MaterialTheme.colorScheme.onSurface,
                textAlign = TextAlign.Center,
                modifier = Modifier.fillMaxWidth(),
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            CaptureSpectrogram(
                phase = phase,
                amplitudes = amplitudes,
                amplitude = amplitude,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            Text(
                text = formatAudioClock(elapsedSeconds * 1000),
                style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
                color = MaterialTheme.colorScheme.onSurface,
                textAlign = TextAlign.Center,
                modifier = Modifier.fillMaxWidth(),
            )
        }
    }
}

@Composable
internal fun CaptureRecordingTicker(startAt: Int, onTick: (Int) -> Unit) {
    LaunchedEffect(Unit) {
        var value = startAt
        onTick(startAt)
        while (true) {
            delay(1_000)
            value += 1
            onTick(value)
        }
    }
}

private fun formatDominantKhz(value: Float): String {
    val rounded = (value * 10f).toInt() / 10f
    return if (rounded == rounded.toInt().toFloat()) rounded.toInt().toString() else rounded.toString()
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
