package me.juanlabs.anura.feature.observations

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.shape.RoundedCornerShape
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
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Shadow
import androidx.compose.ui.graphics.painter.Painter
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.layout.LayoutCoordinates
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlin.math.sin
import kotlinx.coroutines.delay
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraLightGlass
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.feature.capture.CaptureAudioPlaybackControls
import me.juanlabs.anura.feature.capture.CaptureAudioPlayerState
import me.juanlabs.anura.feature.capture.CaptureSpectrogram
import me.juanlabs.anura.feature.capture.CaptureSpectrogramPhase
import me.juanlabs.anura.feature.capture.WaveformBarCount

private val ObservationCarouselIndexInset = 16.dp

@Composable
internal fun ObservationMediaCarousel(
    items: List<ObservationMediaItem>,
    modifier: Modifier = Modifier,
) {
    val pages = items.ifEmpty {
        listOf(ObservationMediaItem.Photo("empty", R.drawable.carousel_dendrobates_truncatus))
    }
    val pagerState = rememberPagerState(pageCount = { pages.size })
    val carouselCd = stringResource(R.string.observation_media_carousel_cd)
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(AnuraDimens.radiusCard))
            .semantics { contentDescription = carouselCd },
    ) {
        HorizontalPager(
            state = pagerState,
            modifier = Modifier.fillMaxSize(),
            pageSpacing = AnuraDimens.spaceGap,
        ) { page ->
            ObservationMediaPage(
                item = pages[page],
                index = page + 1,
                total = pages.size,
                active = pagerState.currentPage == page,
            )
        }
    }
}

@Composable
private fun ObservationMediaPage(
    item: ObservationMediaItem,
    index: Int,
    total: Int,
    active: Boolean,
) {
    var hostCoords by remember { mutableStateOf<LayoutCoordinates?>(null) }
    val indexLabel = stringResource(R.string.capture_step4_photo_index, index, total)
    val indexCd = stringResource(R.string.observation_media_index_cd, index, total)
    val extended = AnuraTheme.extendedColors
    val onGlassShadow = remember(extended.onGlassShadow) {
        Shadow(
            color = extended.onGlassShadow,
            offset = Offset(0f, 1f),
            blurRadius = 8f,
        )
    }
    val backdrop: Painter? = when (item) {
        is ObservationMediaItem.Photo -> painterResource(item.imageRes)
        is ObservationMediaItem.Audio -> null
    }
    Box(
        modifier = Modifier
            .fillMaxSize()
            .clip(RoundedCornerShape(AnuraDimens.radiusCard))
            .onGloballyPositioned { hostCoords = it },
    ) {
        when (item) {
            is ObservationMediaItem.Photo -> {
                Image(
                    painter = painterResource(item.imageRes),
                    contentDescription = stringResource(R.string.observation_detail_photo_cd),
                    modifier = Modifier.fillMaxSize(),
                    contentScale = ContentScale.Crop,
                )
            }
            is ObservationMediaItem.Audio -> {
                ObservationAudioSlide(
                    durationMs = item.durationMs,
                    active = active,
                    modifier = Modifier.fillMaxSize(),
                )
            }
        }
        if (total > 1) {
            AnuraLightGlass(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(bottom = ObservationCarouselIndexInset)
                    .semantics { contentDescription = indexCd },
                contentPadding = PaddingValues(horizontal = 10.dp, vertical = 4.dp),
                backdropPainter = backdrop,
                hostCoordinates = hostCoords,
            ) {
                Text(
                    text = indexLabel,
                    style = MaterialTheme.typography.labelSmall.copy(
                        fontWeight = FontWeight.SemiBold,
                        fontSize = 12.sp,
                        lineHeight = 14.sp,
                        shadow = onGlassShadow,
                    ),
                    color = extended.onGlass,
                )
            }
        }
    }
}

@Composable
private fun ObservationAudioSlide(
    durationMs: Int,
    active: Boolean,
    modifier: Modifier = Modifier,
) {
    val player = rememberMockObservationAudioPlayer(durationMs = durationMs, active = active)
    var amplitudes by remember { mutableStateOf(List(WaveformBarCount) { 0.12f }) }
    LaunchedEffect(player.playing, player.positionMs, active) {
        if (!active) return@LaunchedEffect
        val t = player.positionMs / 180.0
        amplitudes = List(WaveformBarCount) { i ->
            val wave = (sin(t + i * 0.35) + 1.0) / 2.0
            val live = if (player.playing) 0.55 else 0.18
            (0.08 + live * wave).toFloat().coerceIn(0f, 1f)
        }
    }
    Column(
        modifier = modifier
            .background(MaterialTheme.colorScheme.surfaceVariant)
            .padding(AnuraDimens.spaceGap),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        CaptureSpectrogram(
            phase = if (player.playing) {
                CaptureSpectrogramPhase.Playing
            } else {
                CaptureSpectrogramPhase.Recorded
            },
            amplitudes = amplitudes,
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f),
        )
        Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
        CaptureAudioPlaybackControls(
            player = player,
            onAnalyze = {},
            onReject = {},
            showAnalyzeActions = false,
        )
    }
}

@Composable
private fun rememberMockObservationAudioPlayer(
    durationMs: Int,
    active: Boolean,
): CaptureAudioPlayerState {
    var playing by rememberSaveable { mutableStateOf(false) }
    var positionMs by remember { mutableIntStateOf(0) }
    LaunchedEffect(active) {
        if (!active) playing = false
    }
    LaunchedEffect(playing, active) {
        if (!playing || !active) return@LaunchedEffect
        while (playing && active) {
            delay(50)
            val next = positionMs + 50
            if (next >= durationMs) {
                positionMs = durationMs
                playing = false
            } else {
                positionMs = next
            }
        }
    }
    return CaptureAudioPlayerState(
        playing = playing && active,
        positionMs = positionMs,
        durationMs = durationMs.coerceAtLeast(1),
        sessionId = 0,
        onTogglePlay = {
            if (!active) return@CaptureAudioPlayerState
            if (positionMs >= durationMs) positionMs = 0
            playing = !playing
        },
        onSeekBy = { delta ->
            positionMs = (positionMs + delta).coerceIn(0, durationMs)
        },
        onSeekTo = { millis ->
            positionMs = millis.coerceIn(0, durationMs)
        },
        onStopPlayback = { playing = false },
    )
}
