package me.juanlabs.anura.feature.auth

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.sizeIn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.BiasAlignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode
import me.juanlabs.anura.navigation.MockNavAction
import me.juanlabs.anura.navigation.MockScreenScaffold

/**
 * Medidas del board Penpot `LOGIN OR SINGUO (bienvenida)` — distintas de
 * `COMP · Botones` (60 / radio 30). Aquí priman las del mockup de pantalla.
 *
 * Regla de layout: gaps entre elementos del sheet son fijos; si no cabe, el
 * contenedor (`Surface` / sheet) cede altura (Spacer del hero) — nunca se
 * comprimen esos gaps. «Entrar sin cuenta» se ancla al bottom como el status
 * del splash (`spaceSection` + `navigationBarsPadding`).
 */
private val WelcomeSheetTopRadius = 20.dp
private val WelcomeButtonHeight = 50.dp
private val WelcomeButtonRadius = 12.dp
private val WelcomeButtonHorizontalInset = 56.dp
private val WelcomeSheetTopPadding = 47.dp
private val WelcomePrimaryToOutlineGap = 10.dp
private val WelcomeOutlineToGuestGap = 12.dp
/** Piso del área hero (Spacer sobre la imagen) para que no desaparezca. */
private val WelcomeHeroMinHeight = 160.dp

/** Huecos tipográficos fijos (nivel sheet). */
private val WelcomeTitleToBodyGap = 20.dp
private val WelcomeBodyToButtonsGap = 32.dp

/**
 * Encuadre Penpot: capa `image` 867×611 en (−141, −29); fill real 1024×721.
 * Bias sobre el bitmap exportado (1024×721).
 */
private val WelcomeHeroAlignment = BiasAlignment(
    horizontalBias = ((141f * 1024f / 867f + 393f * 1024f / 867f / 2f) - 1024f / 2f) / (1024f / 2f),
    verticalBias = ((29f * 721f / 611f + 520f * 721f / 611f / 2f) - 721f / 2f) / (721f / 2f),
)

/** Contorno del botón "Ya tengo cuenta" en Penpot (stop #626264 del stroke). */
private val WelcomeOutlineStroke = Color(0xFF626264)

/**
 * `LOGIN OR SINGUO (bienvenida)` (§4.1, grafo `AuthGraph`).
 *
 * Estados: pantalla estática de entrada — sin loading/error propios. Tres acciones
 * de navegación ya cableadas en [me.juanlabs.anura.navigation.AnuraNavHost]:
 * crear cuenta → [AnuraRoute.SignUp], ya tengo cuenta → [AnuraRoute.SignIn],
 * entrar sin cuenta → Home (pop AuthGraph), decisión 6/7.
 *
 * Misma estructura que [StartupLoadingScreen]: bloque superior `weight(1f)` +
 * texto anclado al bottom con `padding(bottom = spaceSection)`.
 * La foto se cropea solo en la zona hero (no a pantalla completa).
 */
@Composable
fun WelcomeScreen(
    onContinueWithoutAccount: () -> Unit,
    onGoToSignIn: () -> Unit,
    onGoToSignUp: () -> Unit,
) {
    val surfaceColor = MaterialTheme.colorScheme.surface

    Column(
        modifier = Modifier
            .fillMaxSize()
            .navigationBarsPadding(),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        // Equivalente al Column(weight(1f)) del splash.
        Column(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth(),
        ) {
            Image(
                painter = painterResource(R.drawable.welcome_hero),
                contentDescription = stringResource(R.string.welcome_hero_cd),
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
                    .heightIn(min = WelcomeHeroMinHeight),
                contentScale = ContentScale.Crop,
                alignment = WelcomeHeroAlignment,
            )

            Surface(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(
                    topStart = WelcomeSheetTopRadius,
                    topEnd = WelcomeSheetTopRadius,
                ),
                color = surfaceColor,
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = WelcomeButtonHorizontalInset)
                        .padding(
                            top = WelcomeSheetTopPadding,
                            bottom = WelcomeOutlineToGuestGap,
                        ),
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    Text(
                        text = stringResource(R.string.welcome_title),
                        style = MaterialTheme.typography.headlineMedium.copy(
                            fontWeight = FontWeight.Bold,
                            fontSize = 28.sp,
                            lineHeight = 34.sp,
                        ),
                        color = MaterialTheme.colorScheme.onSurface,
                        textAlign = TextAlign.Center,
                        modifier = Modifier.fillMaxWidth(),
                    )

                    Spacer(modifier = Modifier.height(WelcomeTitleToBodyGap))

                    Text(
                        text = stringResource(R.string.welcome_body),
                        style = MaterialTheme.typography.titleMedium.copy(
                            fontWeight = FontWeight.Normal,
                            fontSize = 15.sp,
                            lineHeight = 22.sp,
                        ),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        textAlign = TextAlign.Center,
                        modifier = Modifier.fillMaxWidth(),
                    )

                    Spacer(modifier = Modifier.height(WelcomeBodyToButtonsGap))

                    Button(
                        onClick = onGoToSignUp,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(WelcomeButtonHeight),
                        shape = RoundedCornerShape(WelcomeButtonRadius),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = AnuraTheme.extendedColors.accentInk,
                            contentColor = MaterialTheme.colorScheme.onPrimary,
                        ),
                    ) {
                        Text(
                            text = stringResource(R.string.welcome_create_account),
                            style = MaterialTheme.typography.titleLarge.copy(
                                fontWeight = FontWeight.SemiBold,
                            ),
                        )
                    }

                    Spacer(modifier = Modifier.height(WelcomePrimaryToOutlineGap))

                    OutlinedButton(
                        onClick = onGoToSignIn,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(WelcomeButtonHeight),
                        shape = RoundedCornerShape(WelcomeButtonRadius),
                        border = BorderStroke(2.dp, WelcomeOutlineStroke),
                        colors = ButtonDefaults.outlinedButtonColors(
                            contentColor = MaterialTheme.colorScheme.onSurface,
                        ),
                    ) {
                        Text(
                            text = stringResource(R.string.welcome_have_account),
                            style = MaterialTheme.typography.titleMedium.copy(
                                fontWeight = FontWeight.SemiBold,
                            ),
                        )
                    }
                }
            }
        }

        // Misma ancla que el Text «Cargando modelo» del splash.
        Surface(
            modifier = Modifier.fillMaxWidth(),
            color = surfaceColor,
        ) {
            TextButton(
                onClick = onContinueWithoutAccount,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = WelcomeButtonHorizontalInset)
                    .sizeIn(minHeight = AnuraDimens.sizeTouch)
                    .padding(bottom = AnuraDimens.spaceSection),
            ) {
                Text(
                    text = stringResource(R.string.welcome_continue_without_account),
                    style = MaterialTheme.typography.bodySmall.copy(
                        fontWeight = FontWeight.SemiBold,
                        fontSize = 13.sp,
                    ),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    textAlign = TextAlign.Center,
                )
            }
        }
    }
}

/** `INICIAR SECCION` (§4.1) — mock hasta su bloque de producto. */
@Composable
fun SignInScreen(
    onBackClick: () -> Unit,
    onSignedIn: () -> Unit,
    onGoToSignUp: () -> Unit,
) {
    MockScreenScaffold(
        title = "Iniciar sesión",
        onBackClick = onBackClick,
        actions = listOf(
            MockNavAction("Entrar", onSignedIn),
            MockNavAction("Crear cuenta", onGoToSignUp),
        ),
    )
}

/** `crear cuenta` (§4.1) — mock hasta su bloque de producto. */
@Composable
fun SignUpScreen(
    onBackClick: () -> Unit,
    onSignedUp: () -> Unit,
    onGoToSignIn: () -> Unit,
) {
    MockScreenScaffold(
        title = "Crear cuenta",
        onBackClick = onBackClick,
        actions = listOf(
            MockNavAction("Crear cuenta", onSignedUp),
            MockNavAction("Ya tengo cuenta", onGoToSignIn),
        ),
    )
}

@AnuraPreviews
@Composable
private fun WelcomeScreenPreview() {
    AnuraTheme {
        WelcomeScreen(
            onContinueWithoutAccount = {},
            onGoToSignIn = {},
            onGoToSignUp = {},
        )
    }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun WelcomeScreenPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) {
        WelcomeScreen(
            onContinueWithoutAccount = {},
            onGoToSignIn = {},
            onGoToSignUp = {},
        )
    }
}
