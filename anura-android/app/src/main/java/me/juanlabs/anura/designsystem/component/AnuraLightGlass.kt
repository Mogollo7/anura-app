package me.juanlabs.anura.designsystem.component

import android.os.Build
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.requiredSize
import androidx.compose.foundation.layout.wrapContentSize
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.blur
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.painter.Painter
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.layout.LayoutCoordinates
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import kotlin.math.roundToInt
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme

/** Radio de desenfoque del vidrio claro (Apple HIG Light Glass / Vibrancy). */
val AnuraGlassBlurRadius: Dp = 20.dp

/**
 * Recuadro translúcido sobre media: tinte [AnuraTheme.extendedColors.glassLight],
 * borde [glassStroke] y, en API 31+, copia desenfocada de [backdropPainter].
 */
@Composable
fun AnuraLightGlass(
    modifier: Modifier = Modifier,
    contentPadding: PaddingValues = PaddingValues(horizontal = 14.dp, vertical = 10.dp),
    backdropPainter: Painter? = null,
    hostCoordinates: LayoutCoordinates? = null,
    content: @Composable BoxScope.() -> Unit,
) {
    val density = LocalDensity.current
    val extended = AnuraTheme.extendedColors
    val blurSupported = Build.VERSION.SDK_INT >= Build.VERSION_CODES.S
    val glassTint = if (blurSupported) extended.glassLight else extended.glassLightFallback
    val overlayShape = RoundedCornerShape(AnuraDimens.radiusButton)
    var overlayCoords by remember { mutableStateOf<LayoutCoordinates?>(null) }

    Box(
        modifier = modifier
            .onGloballyPositioned { overlayCoords = it }
            .clip(overlayShape)
            .border(1.dp, extended.glassStroke, overlayShape),
        contentAlignment = Alignment.Center,
    ) {
        val cardLayout = hostCoordinates
        val overlayLayout = overlayCoords
        val cardSize = cardLayout?.size
        val overlayOrigin = if (
            backdropPainter != null &&
            cardLayout != null &&
            overlayLayout != null &&
            cardLayout.isAttached &&
            overlayLayout.isAttached
        ) {
            cardLayout.localPositionOf(overlayLayout, Offset.Zero)
        } else {
            Offset.Zero
        }

        if (
            blurSupported &&
            backdropPainter != null &&
            cardSize != null &&
            cardSize.width > 0
        ) {
            Box(
                modifier = Modifier
                    .matchParentSize()
                    .wrapContentSize(unbounded = true, align = Alignment.TopStart),
            ) {
                Image(
                    painter = backdropPainter,
                    contentDescription = null,
                    contentScale = ContentScale.Crop,
                    modifier = Modifier
                        .requiredSize(
                            width = with(density) { cardSize.width.toDp() },
                            height = with(density) { cardSize.height.toDp() },
                        )
                        .offset {
                            IntOffset(
                                x = -overlayOrigin.x.roundToInt(),
                                y = -overlayOrigin.y.roundToInt(),
                            )
                        }
                        .blur(AnuraGlassBlurRadius),
                )
            }
        }

        Box(
            modifier = Modifier
                .matchParentSize()
                .background(glassTint),
        )

        Box(
            modifier = Modifier.padding(contentPadding),
            contentAlignment = Alignment.Center,
            content = content,
        )
    }
}
