package me.juanlabs.anura.feature.capture

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.size
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import kotlin.math.max
import kotlin.math.roundToInt
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.theme.AnuraTheme

/** Diámetro físico de la moneda de $100 COP, en milímetros. */
internal const val Cop100DiameterMm = 20.30f

/** Relación ancho máximo/alto del huevo: no se deforma al cambiar el SVL. */
private const val IndividualAspect = 0.62f

internal fun cop100EquivalentCoins(svlMm: Float): Float = svlMm / Cop100DiameterMm

/** Solo monedas enteras: un recorte parcial no se dibuja. 40 mm ≈ 2. */
internal fun cop100CompleteCoins(svlMm: Float): Int =
    cop100EquivalentCoins(svlMm).roundToInt().coerceAtLeast(0)

private val CaptureSvlStageHeight = 220.dp
private val CaptureSvlMaxCoin = 72.dp

/**
 * Comparación a escala única: pila de monedas completas de $100 COP (20,30 mm)
 * e individuo en forma de huevo (punta arriba, base ancha) con línea vertical punteada (el SVL).
 */
@Composable
internal fun CaptureSvlComparison(
    svlMm: Float,
    modifier: Modifier = Modifier,
) {
    val coinColor = MaterialTheme.colorScheme.outline
    val individualColor = AnuraTheme.extendedColors.accentInk
    val completeCoins = cop100CompleteCoins(svlMm)
    val density = LocalDensity.current

    BoxWithConstraints(
        modifier = modifier
            .fillMaxWidth()
            .height(CaptureSvlStageHeight),
    ) {
        val availableH = (constraints.maxHeight.toFloat() - with(density) { 22.dp.toPx() })
            .coerceAtLeast(1f)
        val columnW = constraints.maxWidth / 2f
        val stackMm = completeCoins * Cop100DiameterMm
        val ovoidHeightMm = svlMm.coerceAtLeast(1f)
        val ovoidWidthMm = ovoidHeightMm * IndividualAspect
        val neededH = max(ovoidHeightMm, max(stackMm, Cop100DiameterMm))
        val neededW = max(Cop100DiameterMm, ovoidWidthMm)
        val maxCoinPx = with(density) { CaptureSvlMaxCoin.toPx() }
        val pxPerMm = minOf(
            availableH / neededH,
            columnW / neededW,
            maxCoinPx / Cop100DiameterMm,
        )

        Row(
            modifier = Modifier.fillMaxSize(),
            horizontalArrangement = Arrangement.SpaceEvenly,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                modifier = Modifier
                    .weight(1f)
                    .fillMaxHeight(),
            ) {
                Canvas(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxWidth(),
                ) {
                    drawCompleteCoinStack(
                        count = completeCoins,
                        diameter = Cop100DiameterMm * pxPerMm,
                        color = coinColor,
                    )
                }
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = AnuraIcons.Coin,
                        contentDescription = null,
                        tint = coinColor,
                        modifier = Modifier.size(16.dp),
                    )
                    Spacer(modifier = Modifier.size(4.dp))
                    Text(
                        text = stringResource(R.string.capture_step3_coin_ref),
                        style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                modifier = Modifier
                    .weight(1f)
                    .fillMaxHeight(),
            ) {
                Canvas(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxWidth(),
                ) {
                    val height = ovoidHeightMm * pxPerMm
                    drawEggIndividual(
                        height = height,
                        width = height * IndividualAspect,
                        color = individualColor,
                    )
                }
                Text(
                    text = stringResource(R.string.capture_step3_individual),
                    style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
                    color = individualColor,
                )
            }
        }
    }
}

private fun DrawScope.drawCompleteCoinStack(
    count: Int,
    diameter: Float,
    color: Color,
) {
    if (count <= 0 || diameter <= 0f) return
    val radius = diameter / 2f
    val totalHeight = count * diameter
    var y = (size.height - totalHeight) / 2f
    val cx = size.width / 2f
    val stroke = 3.dp.toPx()
    repeat(count) {
        drawCircle(
            color = color,
            radius = radius,
            center = Offset(cx, y + radius),
            style = Stroke(width = stroke, cap = StrokeCap.Round),
        )
        y += diameter
    }
}

private fun DrawScope.drawEggIndividual(
    height: Float,
    width: Float,
    color: Color,
) {
    val stroke = 3.dp.toPx()
    val left = (size.width - width) / 2f
    val top = (size.height - height) / 2f
    val right = left + width
    val bottom = top + height
    val cx = left + width / 2f
    val widestY = top + height * 0.68f
    val path = Path().apply {
        moveTo(cx, top)
        cubicTo(
            cx + width * 0.18f,
            top + height * 0.04f,
            right,
            top + height * 0.34f,
            right,
            widestY,
        )
        cubicTo(
            right,
            top + height * 0.90f,
            cx + width * 0.30f,
            bottom,
            cx,
            bottom,
        )
        cubicTo(
            cx - width * 0.30f,
            bottom,
            left,
            top + height * 0.90f,
            left,
            widestY,
        )
        cubicTo(
            left,
            top + height * 0.34f,
            cx - width * 0.18f,
            top + height * 0.04f,
            cx,
            top,
        )
        close()
    }
    drawPath(
        path = path,
        color = color,
        style = Stroke(width = stroke, cap = StrokeCap.Round, join = StrokeJoin.Round),
    )
    drawLine(
        color = color,
        start = Offset(cx, top + stroke),
        end = Offset(cx, bottom - stroke),
        strokeWidth = 2.dp.toPx(),
        cap = StrokeCap.Round,
        pathEffect = PathEffect.dashPathEffect(
            floatArrayOf(5.dp.toPx(), 4.dp.toPx()),
            0f,
        ),
    )
}
