package me.juanlabs.anura.feature.capture

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.gestures.drag
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.FilledIconButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedIconButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import kotlin.math.roundToInt
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraFormButtonStyle
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme

private val SeekTrackHeight = 4.dp
private val SeekThumbSize = 12.dp

/**
 * Transporte + analizar/rechazar sobre un clip ya grabado o elegido.
 * No sustituye el encabezado ni la tarjeta del espectrograma.
 */
@Composable
internal fun CaptureAudioPlaybackControls(
    player: CaptureAudioPlayerState,
    onAnalyze: () -> Unit,
    onReject: () -> Unit,
    analyzeLabel: String = stringResource(R.string.audio_capture_analyze),
    showAnalyzeActions: Boolean = true,
) {
    var scrubMs by remember { mutableStateOf<Int?>(null) }
    val displayMs = scrubMs ?: player.positionMs
    val elapsed = formatAudioClock(displayMs)
    val total = formatAudioClock(player.durationMs)
    val progressCd = stringResource(R.string.capture_step5_progress_cd, elapsed, total)
    Text(
        text = stringResource(R.string.capture_step5_time_remaining, elapsed, total),
        style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
        color = MaterialTheme.colorScheme.onSurface,
        textAlign = TextAlign.Center,
        modifier = Modifier.fillMaxWidth(),
    )
    Spacer(modifier = Modifier.height(8.dp))
    CaptureAudioSeekBar(
        positionMs = displayMs,
        durationMs = player.durationMs,
        contentDescription = progressCd,
        onScrub = { millis ->
            scrubMs = millis
            player.onSeekTo(millis)
        },
        onScrubEnd = { millis ->
            player.onSeekTo(millis)
            scrubMs = null
        },
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
    if (showAnalyzeActions) {
        Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
        AnuraFormButton(
            text = analyzeLabel,
            onClick = {
                player.onStopPlayback()
                onAnalyze()
            },
            style = AnuraFormButtonStyle.Primary,
        )
        Spacer(modifier = Modifier.height(AnuraDimens.spaceActionGap))
        AnuraFormButton(
            text = stringResource(R.string.audio_capture_reject),
            onClick = {
                player.onStopPlayback()
                onReject()
            },
            style = AnuraFormButtonStyle.Outline,
        )
    }
}

@Composable
private fun CaptureAudioSeekBar(
    positionMs: Int,
    durationMs: Int,
    contentDescription: String,
    onScrub: (Int) -> Unit,
    onScrubEnd: (Int) -> Unit,
) {
    val duration = durationMs.coerceAtLeast(1)
    val fraction = (positionMs / duration.toFloat()).coerceIn(0f, 1f)
    val density = LocalDensity.current
    BoxWithConstraints(
        modifier = Modifier
            .fillMaxWidth()
            .height(AnuraDimens.sizeTouch)
            .semantics { this.contentDescription = contentDescription }
            .pointerInput(duration) {
                awaitEachGesture {
                    val down = awaitFirstDown()
                    fun millisAt(x: Float): Int {
                        val ratio = (x / size.width.toFloat()).coerceIn(0f, 1f)
                        return (ratio * duration).roundToInt()
                    }
                    var lastX = down.position.x
                    onScrub(millisAt(lastX))
                    drag(down.id) { change ->
                        lastX = change.position.x
                        onScrub(millisAt(lastX))
                        change.consume()
                    }
                    onScrubEnd(millisAt(lastX))
                }
            },
        contentAlignment = Alignment.CenterStart,
    ) {
        val trackShape = RoundedCornerShape(AnuraDimens.radiusCapsule)
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(SeekTrackHeight)
                .clip(trackShape)
                .background(MaterialTheme.colorScheme.surfaceVariant),
        )
        Box(
            modifier = Modifier
                .fillMaxWidth(fraction.coerceAtLeast(0.001f))
                .height(SeekTrackHeight)
                .clip(trackShape)
                .background(AnuraTheme.extendedColors.accentInk),
        )
        val thumbPx = with(density) { SeekThumbSize.toPx() }
        val x = ((constraints.maxWidth * fraction) - thumbPx / 2f)
            .coerceIn(0f, (constraints.maxWidth - thumbPx).coerceAtLeast(0f))
        Box(
            modifier = Modifier
                .offset { IntOffset(x.roundToInt(), 0) }
                .size(SeekThumbSize)
                .clip(CircleShape)
                .background(AnuraTheme.extendedColors.accentInk)
                .align(Alignment.CenterStart),
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
