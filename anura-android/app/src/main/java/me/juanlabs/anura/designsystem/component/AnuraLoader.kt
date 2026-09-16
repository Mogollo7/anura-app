package me.juanlabs.anura.designsystem.component

import android.provider.Settings
import androidx.compose.animation.core.EaseInOut
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.StartOffset
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.keyframes
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

private const val AnuraLoaderPeriodMillis = 1200
private const val AnuraLoaderPhaseOffsetMillis = 200
private val AnuraLoaderDotDiameter = 12.dp
private val AnuraLoaderAmplitude = 8.dp

/**
 * Indicador de progreso de dos puntos (`COMP · Cargando`, §3.9): ⌀12dp, separación de
 * centros 24dp, amplitud ±8dp, periodo 1200ms, desfase 200ms entre puntos, ease-in-out.
 *
 * [label] es **obligatorio** y describe la tarea concreta en curso ("Analizando
 * imagen…", "Buscando paquete regional…"), nunca un genérico "Cargando…" (§3.9). Se
 * anuncia a TalkBack vía región en vivo; no se dibuja texto — quien use este loader
 * dentro de una pantalla decide si además muestra [label] visualmente.
 *
 * Si el sistema tiene animaciones reducidas (ajuste de accesibilidad "Quitar
 * animaciones", `ANIMATOR_DURATION_SCALE == 0`), se usa la variante Reduce Motion de
 * Penpot: pulso de opacidad sin desplazamiento vertical.
 */
@Composable
fun AnuraLoader(
    label: String,
    modifier: Modifier = Modifier,
    /**
     * Color de los puntos. Por defecto `primary` (acento). En
     * `Estado · Cargando (PANTALLA DE CARGA INICIO)` Penpot usa `accent.ink` (#1E7A34).
     */
    color: Color = MaterialTheme.colorScheme.primary,
) {
    val context = LocalContext.current
    val reduceMotion = remember {
        Settings.Global.getFloat(context.contentResolver, Settings.Global.ANIMATOR_DURATION_SCALE, 1f) == 0f
    }

    val transition = rememberInfiniteTransition(label = "AnuraLoader")
    val dot1 by transition.animateFloat(
        initialValue = -1f,
        targetValue = -1f,
        animationSpec = infiniteRepeatable(
            animation = keyframes {
                durationMillis = AnuraLoaderPeriodMillis
                -1f at 0 using EaseInOut
                1f at AnuraLoaderPeriodMillis / 2 using EaseInOut
                -1f at AnuraLoaderPeriodMillis using EaseInOut
            },
            repeatMode = RepeatMode.Restart,
        ),
        label = "AnuraLoaderDot1",
    )
    val dot2 by transition.animateFloat(
        initialValue = -1f,
        targetValue = -1f,
        animationSpec = infiniteRepeatable(
            animation = keyframes {
                durationMillis = AnuraLoaderPeriodMillis
                -1f at 0 using EaseInOut
                1f at AnuraLoaderPeriodMillis / 2 using EaseInOut
                -1f at AnuraLoaderPeriodMillis using EaseInOut
            },
            repeatMode = RepeatMode.Restart,
            initialStartOffset = StartOffset(AnuraLoaderPhaseOffsetMillis),
        ),
        label = "AnuraLoaderDot2",
    )

    Row(
        modifier = modifier.semantics {
            contentDescription = label
            liveRegion = LiveRegionMode.Polite
        },
        // Separación de centros 24dp - diámetro 12dp = 12dp de hueco entre bordes.
        horizontalArrangement = Arrangement.spacedBy(AnuraLoaderDotDiameter),
    ) {
        AnuraLoaderDot(offsetFactor = dot1, reduceMotion = reduceMotion, color = color)
        AnuraLoaderDot(offsetFactor = dot2, reduceMotion = reduceMotion, color = color)
    }
}

@Composable
private fun AnuraLoaderDot(
    offsetFactor: Float,
    reduceMotion: Boolean,
    color: Color,
) {
    val dotModifier = if (reduceMotion) {
        Modifier.graphicsLayer(alpha = 0.4f + 0.6f * ((offsetFactor + 1f) / 2f))
    } else {
        Modifier.offset(y = AnuraLoaderAmplitude * offsetFactor)
    }
    Box(
        modifier = dotModifier
            .size(AnuraLoaderDotDiameter)
            .background(color = color, shape = CircleShape),
    )
}

@AnuraPreviews
@Composable
private fun AnuraLoaderPreview() {
    AnuraTheme { AnuraLoader(label = "Analizando imagen…") }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun AnuraLoaderPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) { AnuraLoader(label = "Analizando imagen…") }
}
