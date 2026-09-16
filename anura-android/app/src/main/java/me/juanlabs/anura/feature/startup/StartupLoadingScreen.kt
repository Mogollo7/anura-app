package me.juanlabs.anura.feature.startup

import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraLoader
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

/**
 * Fondo exacto del board Penpot `Estado · Cargando (PANTALLA DE CARGA INICIO)` —
 * `#EFF4F0`. No es un token de tema (`bg.base` es `#F2F2F7`); es color de board.
 */
private val StartupSplashBackground = Color(0xFFEFF4F0)

/** Tamaño del `logoApp` en Penpot (178×181 dp sobre lienzo 393×852). */
private val LogoWidth = 178.dp
private val LogoHeight = 181.dp

/** Hueco logo → título "Anura" (Penpot: 20 dp). */
private val GapLogoToTitle = 20.dp

/** Hueco subtítulo → puntos del loader (Penpot: 20 dp). */
private val GapSubtitleToLoader = 20.dp

/**
 * Espera mock de la nota de diseño §5 en Penpot: "Espera corta (1–3 s)".
 * El runtime real (modelo ONNX / paquete) se conecta en una fase posterior;
 * hoy solo simula la preparación local.
 */
private const val StartupMockDelayMillis = 2_000L

/**
 * `Estado · Cargando (PANTALLA DE CARGA INICIO)` — pantalla de arranque de ANURA.
 *
 * Bloque de marca (logo + título + subtítulo + [AnuraLoader]) centrado en el área
 * superior; el label de estado va anclado al **bottom** con gutter inferior
 * ([AnuraDimens.spaceGutter]) + `navigationBarsPadding`, sin la nota de diseño §5.
 */
@Composable
fun StartupLoadingScreen(
    onReady: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val statusLabel = stringResource(R.string.startup_preparing_model)

    LaunchedEffect(Unit) {
        delay(StartupMockDelayMillis)
        onReady()
    }

    Surface(
        modifier = modifier.fillMaxSize(),
        color = StartupSplashBackground,
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .statusBarsPadding()
                .navigationBarsPadding()
                .padding(horizontal = AnuraDimens.spaceGutter),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Column(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth(),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center,
            ) {
                Image(
                    painter = painterResource(R.drawable.logo_app),
                    contentDescription = stringResource(R.string.startup_logo_cd),
                    modifier = Modifier.size(width = LogoWidth, height = LogoHeight),
                    contentScale = ContentScale.Fit,
                )

                Spacer(modifier = Modifier.height(GapLogoToTitle))

                Text(
                    text = stringResource(R.string.startup_brand_name),
                    style = MaterialTheme.typography.headlineSmall.copy(
                        fontWeight = FontWeight.Bold,
                    ),
                    color = MaterialTheme.colorScheme.onSurface,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.fillMaxWidth(),
                )

                Text(
                    text = stringResource(R.string.startup_tagline),
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = FontWeight.Normal,
                    ),
                    color = MaterialTheme.colorScheme.onSurface,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.fillMaxWidth(),
                )

                Spacer(modifier = Modifier.height(GapSubtitleToLoader))

                AnuraLoader(
                    label = statusLabel,
                    color = AnuraTheme.extendedColors.accentInk,
                )
            }

            Text(
                text = statusLabel,
                style = MaterialTheme.typography.titleMedium.copy(
                    fontWeight = FontWeight.SemiBold,
                ),
                color = MaterialTheme.colorScheme.onSurface,
                textAlign = TextAlign.Center,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = AnuraDimens.spaceSection)
                    .clearAndSetSemantics {},
            )
        }
    }
}

@AnuraPreviews
@Composable
private fun StartupLoadingScreenPreview() {
    AnuraTheme {
        StartupLoadingScreen(onReady = {})
    }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun StartupLoadingScreenPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) {
        StartupLoadingScreen(onReady = {})
    }
}
