package me.juanlabs.anura.feature.capture

import android.net.Uri
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.FilledIconButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButtonDefaults
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedIconButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraFormButtonStyle
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme

@Composable
internal fun CaptureLocalAudioScreen(
    uri: Uri,
    onBackClick: () -> Unit,
    onUseAudio: () -> Unit,
    onCloseClick: () -> Unit = onBackClick,
    useLabel: String = stringResource(R.string.capture_step5_use_audio),
) {
    val player = rememberCaptureAudioPlayer(uri)
    val live = rememberPlaybackWaveform(
        uri = uri,
        playing = player.playing,
        positionMs = player.positionMs,
        sessionId = player.sessionId,
    )
    val phase = if (player.playing) {
        CaptureSpectrogramPhase.Playing
    } else {
        CaptureSpectrogramPhase.Recorded
    }

    CaptureWizardScaffold(
        appBarTitle = stringResource(R.string.capture_step5_local_title),
        step = 5,
        onBackClick = {
            player.onStopPlayback()
            onBackClick()
        },
        showProgress = false,
        onCloseClick = onCloseClick,
        unsavedChanges = true,
        unsavedTitle = stringResource(R.string.capture_step5_leave_local_title),
        unsavedBody = stringResource(R.string.capture_step5_leave_local_body),
    ) {
        val elapsed = formatAudioClock(player.positionMs)
        val total = formatAudioClock(player.durationMs)
        val progressCd = stringResource(R.string.capture_step5_progress_cd, elapsed, total)
        CaptureAudioRecorderCard(
            phase = phase,
            dominantKhz = live.dominantKhz,
            elapsedSeconds = player.positionMs / 1000,
            amplitudes = live.amplitudes,
            amplitude = live.level,
        )
        Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
        Text(
            text = stringResource(R.string.capture_step5_time_remaining, elapsed, total),
            style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
            color = MaterialTheme.colorScheme.onSurface,
            textAlign = TextAlign.Center,
            modifier = Modifier.fillMaxWidth(),
        )
        Spacer(modifier = Modifier.height(8.dp))
        LinearProgressIndicator(
            progress = { (player.positionMs / player.durationMs.toFloat()).coerceIn(0f, 1f) },
            modifier = Modifier
                .fillMaxWidth()
                .semantics { contentDescription = progressCd },
            color = AnuraTheme.extendedColors.accentInk,
            trackColor = MaterialTheme.colorScheme.surfaceVariant,
        )
        Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceEvenly,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            CaptureCircleIconButton(
                icon = AnuraIcons.Replay10,
                contentDescription = stringResource(R.string.capture_step5_seek_back_cd),
                filled = false,
                onClick = { player.onSeekBy(-10_000) },
            )
            CaptureCircleIconButton(
                icon = if (player.playing) AnuraIcons.Pause else AnuraIcons.Play,
                contentDescription = stringResource(
                    if (player.playing) R.string.capture_step5_pause else R.string.capture_step5_play,
                ),
                filled = true,
                large = true,
                onClick = player.onTogglePlay,
            )
            CaptureCircleIconButton(
                icon = AnuraIcons.Forward10,
                contentDescription = stringResource(R.string.capture_step5_seek_forward_cd),
                filled = false,
                onClick = { player.onSeekBy(10_000) },
            )
        }
        Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
        AnuraFormButton(
            text = useLabel,
            onClick = onUseAudio,
            style = AnuraFormButtonStyle.Primary,
        )
    }
}

@Composable
internal fun CaptureCircleIconButton(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    contentDescription: String,
    onClick: () -> Unit,
    filled: Boolean,
    large: Boolean = false,
    enabled: Boolean = true,
) {
    val size = if (large) 72.dp else 56.dp
    val iconSize = if (large) 32.dp else 24.dp
    val modifier = Modifier.size(size.coerceAtLeast(AnuraDimens.sizeTouch))
    if (filled) {
        FilledIconButton(
            onClick = onClick,
            modifier = modifier,
            enabled = enabled,
            shape = CircleShape,
            colors = IconButtonDefaults.filledIconButtonColors(
                containerColor = AnuraTheme.extendedColors.accentInk,
                contentColor = MaterialTheme.colorScheme.onPrimary,
            ),
        ) {
            Icon(
                imageVector = icon,
                contentDescription = contentDescription,
                modifier = Modifier.size(iconSize),
            )
        }
    } else {
        OutlinedIconButton(
            onClick = onClick,
            modifier = modifier,
            enabled = enabled,
            shape = CircleShape,
            border = BorderStroke(2.dp, AnuraTheme.extendedColors.accentInk),
            colors = IconButtonDefaults.outlinedIconButtonColors(
                contentColor = AnuraTheme.extendedColors.accentInk,
            ),
        ) {
            Icon(
                imageVector = icon,
                contentDescription = contentDescription,
                modifier = Modifier.size(iconSize),
            )
        }
    }
}

internal fun formatAudioClock(millis: Int): String {
    val totalSeconds = (millis / 1000).coerceAtLeast(0)
    val minutes = totalSeconds / 60
    val seconds = totalSeconds % 60
    return "%02d:%02d".format(minutes, seconds)
}
