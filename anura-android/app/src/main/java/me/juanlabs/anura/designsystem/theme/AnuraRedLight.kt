package me.juanlabs.anura.designsystem.theme

import androidx.compose.runtime.Composable
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.Modifier
import androidx.compose.ui.composed
import androidx.compose.ui.draw.drawWithCache
import androidx.compose.ui.draw.drawWithContent
import androidx.compose.ui.geometry.toRect
import androidx.compose.ui.graphics.BlendMode
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ColorFilter
import androidx.compose.ui.graphics.ColorMatrix
import androidx.compose.ui.graphics.CompositingStrategy
import androidx.compose.ui.graphics.Paint
import androidx.compose.ui.graphics.drawscope.drawIntoCanvas
import androidx.compose.ui.graphics.graphicsLayer

/**
 * Filtro de fotos en Luz Roja (RNF-07): luminancia → canal rojo, sin verde ni azul,
 * para no romper la adaptación a la oscuridad. El chrome de UI no lo usa: ya está
 * pintado con tokens rojos.
 */
internal val AnuraRedLightMediaColorFilter: ColorFilter = ColorFilter.colorMatrix(
    ColorMatrix(
        floatArrayOf(
            0.2126f, 0.7152f, 0.0722f, 0f, 0f,
            0f, 0f, 0f, 0f, 0f,
            0f, 0f, 0f, 0f, 0f,
            0f, 0f, 0f, 1f, 0f,
        ),
    ),
)

internal val LocalAnuraMediaColorFilter = staticCompositionLocalOf<ColorFilter?> { null }

/** Velo rojo sobre la UI: el blanco y las fotos se tiñen, el negro se queda negro. */
internal val AnuraRedLightOverlayColor = Color(0xFFFF453A)

fun Modifier.anuraRedLightOverlay(): Modifier =
    graphicsLayer { compositingStrategy = CompositingStrategy.Offscreen }
        .drawWithContent {
            drawContent()
            drawRect(
                color = AnuraRedLightOverlayColor,
                blendMode = BlendMode.Multiply,
            )
        }

/** Teñido de media (foto, hero, miniatura) según el tema activo. */
@Composable
fun Modifier.anuraMediaTint(): Modifier = composed {
    val filter = LocalAnuraMediaColorFilter.current
    if (filter == null) {
        this
    } else {
        drawWithCache {
            val paint = Paint().apply { colorFilter = filter }
            onDrawWithContent {
                drawIntoCanvas { canvas ->
                    canvas.saveLayer(size.toRect(), paint)
                    drawContent()
                    canvas.restore()
                }
            }
        }
    }
}
