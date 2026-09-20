package me.juanlabs.anura.feature.capture

import android.graphics.BitmapFactory
import android.net.Uri
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Shadow
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.painter.BitmapPainter
import androidx.compose.ui.graphics.painter.Painter
import androidx.compose.ui.layout.LayoutCoordinates
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraFormButtonStyle
import me.juanlabs.anura.designsystem.component.AnuraLightGlass
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme

private val CaptureCarouselIndexInset = 16.dp

@Composable
internal fun CapturePhotoCarousel(
    specimens: List<String>,
    selectedIndex: Int,
    onSelect: (Int) -> Unit,
    onDelete: (Int) -> Unit,
    onTakeSamples: () -> Unit,
    onSave: () -> Unit,
    confirmLabel: String,
    modifier: Modifier = Modifier,
) {
    val pageCount = specimens.size.coerceAtLeast(1)
    val pagerState = rememberPagerState(
        initialPage = selectedIndex.coerceIn(0, pageCount - 1),
        pageCount = { pageCount },
    )
    LaunchedEffect(selectedIndex, specimens.size) {
        val target = selectedIndex.coerceIn(0, pageCount - 1)
        if (pagerState.currentPage != target) {
            pagerState.scrollToPage(target)
        }
    }
    LaunchedEffect(pagerState.currentPage, specimens.size) {
        if (specimens.isNotEmpty() && pagerState.currentPage != selectedIndex) {
            onSelect(pagerState.currentPage.coerceAtMost(specimens.lastIndex))
        }
    }
    val carouselCd = stringResource(R.string.capture_step4_carousel_cd)
    Column(modifier = modifier.fillMaxSize()) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
                .semantics { contentDescription = carouselCd },
        ) {
            if (specimens.isEmpty()) {
                CapturePhotoPreview(
                    token = "",
                    processing = false,
                    modifier = Modifier.fillMaxSize(),
                )
            } else {
                HorizontalPager(
                    state = pagerState,
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(0.dp),
                    pageSpacing = AnuraDimens.spaceGap,
                ) { page ->
                    CaptureCarouselPage(
                        token = specimens[page],
                        index = page + 1,
                        total = specimens.size,
                    )
                }
                IconButton(
                    onClick = { onDelete(pagerState.currentPage) },
                    modifier = Modifier
                        .align(Alignment.TopEnd)
                        .padding(8.dp)
                        .size(AnuraDimens.sizeTouch),
                ) {
                    Box(
                        modifier = Modifier
                            .size(32.dp)
                            .clip(CircleShape)
                            .background(MaterialTheme.colorScheme.error),
                        contentAlignment = Alignment.Center,
                    ) {
                        Icon(
                            imageVector = AnuraIcons.Delete,
                            contentDescription = stringResource(
                                R.string.capture_step4_delete_specimen_cd,
                                (pagerState.currentPage + 1).toString(),
                            ),
                            tint = MaterialTheme.colorScheme.onError,
                            modifier = Modifier.size(18.dp),
                        )
                    }
                }
            }
        }
        Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = AnuraDimens.spaceGutter),
            horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceActionGap),
        ) {
            Box(modifier = Modifier.weight(1f)) {
                AnuraFormButton(
                    text = stringResource(R.string.capture_step4_take_samples),
                    onClick = onTakeSamples,
                    style = AnuraFormButtonStyle.Outline,
                )
            }
            Box(modifier = Modifier.weight(1f)) {
                AnuraFormButton(
                    text = confirmLabel,
                    onClick = onSave,
                    style = AnuraFormButtonStyle.Primary,
                    enabled = specimens.isNotEmpty(),
                )
            }
        }
    }
}

@Composable
private fun CaptureCarouselPage(
    token: String,
    index: Int,
    total: Int,
) {
    var hostCoords by remember { mutableStateOf<LayoutCoordinates?>(null) }
    val backdrop = rememberCaptureBackdropPainter(token)
    val indexLabel = stringResource(R.string.capture_step4_photo_index, index, total)
    val indexCd = stringResource(R.string.capture_step4_photo_index_cd, index, total)
    val extended = AnuraTheme.extendedColors
    val onGlassShadow = remember(extended.onGlassShadow) {
        Shadow(
            color = extended.onGlassShadow,
            offset = Offset(0f, 1f),
            blurRadius = 8f,
        )
    }
    Box(
        modifier = Modifier
            .fillMaxSize()
            .clip(RoundedCornerShape(AnuraDimens.radiusCard))
            .onGloballyPositioned { hostCoords = it },
    ) {
        CapturePhotoPreview(
            token = token,
            processing = false,
            modifier = Modifier.fillMaxSize(),
        )
        AnuraLightGlass(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(bottom = CaptureCarouselIndexInset)
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

@Composable
private fun rememberCaptureBackdropPainter(token: String): Painter? {
    return when {
        token.startsWith("res:") -> {
            val resId = token.removePrefix("res:").toIntOrNull()
                ?: R.drawable.carousel_pristimantis_paisa
            painterResource(resId)
        }
        token.startsWith("uri:") -> {
            val bitmap = rememberUriImage(Uri.parse(token.removePrefix("uri:")))
            bitmap?.let { BitmapPainter(it) }
        }
        token.startsWith("file:") -> {
            val path = token.removePrefix("file:")
            val bitmap = remember(path) {
                BitmapFactory.decodeFile(path)?.asImageBitmap()
            }
            bitmap?.let { BitmapPainter(it) }
        }
        else -> null
    }
}

@Composable
internal fun CaptureCameraTransport(
    lastToken: String,
    photoCount: Int,
    capturing: Boolean,
    cameraGranted: Boolean,
    onGallery: () -> Unit,
    onShutter: () -> Unit,
    onOpenCarousel: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val galleryCd = stringResource(R.string.capture_step4_gallery_cd)
    val shutterCd = stringResource(R.string.capture_step4_shutter_cd)
    val reviewCd = stringResource(R.string.capture_step4_review_cd, photoCount)
    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = AnuraDimens.spaceGutter, vertical = AnuraDimens.spaceGap),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceEvenly,
    ) {
        IconButton(
            onClick = onGallery,
            enabled = !capturing,
            modifier = Modifier.size(AnuraDimens.sizeTouch),
        ) {
            Icon(
                imageVector = AnuraIcons.PhotoLibrary,
                contentDescription = galleryCd,
                tint = AnuraTheme.extendedColors.accentInk,
                modifier = Modifier.size(28.dp),
            )
        }
        Box(
            modifier = Modifier
                .size(80.dp)
                .clip(CircleShape)
                .border(
                    width = 4.dp,
                    color = AnuraTheme.extendedColors.accentInk,
                    shape = CircleShape,
                )
                .clickable(
                    enabled = cameraGranted && !capturing,
                    role = Role.Button,
                    onClick = onShutter,
                )
                .semantics { contentDescription = shutterCd },
            contentAlignment = Alignment.Center,
        ) {
            Box(
                modifier = Modifier
                    .size(58.dp)
                    .clip(CircleShape)
                    .background(AnuraTheme.extendedColors.accentInk),
            )
        }
        Box(
            modifier = Modifier
                .size(64.dp)
                .clip(RoundedCornerShape(AnuraDimens.radiusThumb))
                .border(
                    width = 1.dp,
                    color = MaterialTheme.colorScheme.outlineVariant,
                    shape = RoundedCornerShape(AnuraDimens.radiusThumb),
                )
                .clickable(
                    enabled = photoCount > 0 && !capturing,
                    role = Role.Button,
                    onClick = onOpenCarousel,
                )
                .semantics { contentDescription = reviewCd },
        ) {
            CapturePhotoPreview(
                token = lastToken,
                processing = false,
                modifier = Modifier.fillMaxSize(),
            )
            Box(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(bottom = 4.dp)
                    .size(24.dp)
                    .clip(CircleShape)
                    .background(AnuraTheme.extendedColors.accentInk),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = photoCount.toString(),
                    style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold),
                    color = MaterialTheme.colorScheme.onPrimary,
                )
            }
        }
    }
}
