package me.juanlabs.anura.feature.observations

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import me.juanlabs.anura.core.data.rememberSpeciesPhotoPainter
import me.juanlabs.anura.core.platform.rememberRemotePhotoPainter
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.feature.capture.rememberCaptureBackdropPainter

@Composable
internal fun MediaLightbox(
    items: List<ObservationMediaItem>,
    initialIndex: Int,
    onDismiss: () -> Unit,
) {
    val photos = items.filter {
        it is ObservationMediaItem.Photo || it is ObservationMediaItem.FilePhoto || it is ObservationMediaItem.RemotePhoto
    }
    if (photos.isEmpty()) return
    val start = initialIndex.coerceIn(0, photos.lastIndex)
    val pagerState = rememberPagerState(initialPage = start, pageCount = { photos.size })
    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(
            usePlatformDefaultWidth = false,
            dismissOnBackPress = true,
            dismissOnClickOutside = true,
        ),
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(MaterialTheme.colorScheme.scrim.copy(alpha = 0.92f)),
        ) {
            HorizontalPager(
                state = pagerState,
                modifier = Modifier.fillMaxSize(),
            ) { page ->
                LightboxPhoto(item = photos[page])
            }
            if (photos.size > 1) {
                Text(
                    text = stringResource(
                        R.string.capture_step4_photo_index,
                        pagerState.currentPage + 1,
                        photos.size,
                    ),
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.inverseOnSurface,
                    modifier = Modifier
                        .align(Alignment.BottomCenter)
                        .padding(AnuraDimens.spaceSection),
                )
            }
            IconButton(
                onClick = onDismiss,
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .windowInsetsPadding(WindowInsets.statusBars)
                    .padding(AnuraDimens.spaceGap)
                    .size(AnuraDimens.sizeTouch),
            ) {
                Icon(
                    imageVector = AnuraIcons.Close,
                    contentDescription = stringResource(R.string.media_lightbox_close_cd),
                    tint = MaterialTheme.colorScheme.inverseOnSurface,
                )
            }
        }
    }
}

@Composable
private fun LightboxPhoto(item: ObservationMediaItem) {
    val painter = when (item) {
        is ObservationMediaItem.Photo -> rememberSpeciesPhotoPainter(item.remoteSha256, item.imageRes)
        is ObservationMediaItem.FilePhoto -> rememberCaptureBackdropPainter(item.token)
            ?: painterResource(R.drawable.carousel_dendrobates_truncatus)
        is ObservationMediaItem.RemotePhoto -> rememberRemotePhotoPainter(item.url, item.fallbackRes)
        is ObservationMediaItem.Audio -> return
    }
    Image(
        painter = painter,
        contentDescription = stringResource(R.string.observation_detail_photo_cd),
        modifier = Modifier.fillMaxSize(),
        contentScale = ContentScale.Fit,
        colorFilter = AnuraTheme.mediaColorFilter,
    )
}
