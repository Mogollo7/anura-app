package me.juanlabs.anura.feature.auth

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.sizeIn
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.BiasAlignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.layout.layout
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraTextField
import me.juanlabs.anura.designsystem.component.AnuraTopBar
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

/**
 * Medidas del board Penpot `LOGIN OR SINGUO (bienvenida)` — distintas de
 * `COMP · Botones` (60 / radio 30). Aquí priman las del mockup de pantalla.
 *
 * Regla de layout: gaps entre elementos del sheet son fijos; si no cabe, el
 * contenedor (`Surface` / sheet) cede altura (Spacer del hero) — nunca se
 * comprimen esos gaps. «Entrar sin cuenta» se ancla al bottom como el status
 * del splash (`spaceSection` + `navigationBarsPadding`). Contenedor blanco:
 * radio superior 30 dp.
 */
private val WelcomeSheetTopRadius = 30.dp
private val WelcomeButtonHeight = 50.dp
private val WelcomeButtonRadius = 12.dp
private val WelcomeButtonHorizontalInset = 56.dp
private val WelcomeSheetTopPadding = 47.dp
private val WelcomePrimaryToOutlineGap = 10.dp
private val WelcomeOutlineToGuestGap = 12.dp
/** Margen entre «Entrar sin cuenta» y el borde inferior. */
private val WelcomeGuestBottomMargin = AnuraDimens.spaceSection
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
 * CTA abajo con margen al borde inferior.
 *
 * Altura de la imagen: desde el top hasta donde empieza «Conoce sobre anuros».
 * El sheet se solapa 30 dp sobre la rana (radio superior) sin franja extra entre
 * botones y «Entrar sin cuenta».
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
        Column(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth(),
        ) {
            // Zona hero: la rana termina donde empieza el sheet / título.
            Box(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .heightIn(min = WelcomeHeroMinHeight),
            ) {
                Image(
                    painter = painterResource(R.drawable.welcome_hero),
                    contentDescription = stringResource(R.string.welcome_hero_cd),
                    modifier = Modifier.fillMaxSize(),
                    contentScale = ContentScale.Crop,
                    alignment = WelcomeHeroAlignment,
                )
            }

            // Un solo contenedor blanco: solapa 30 dp la imagen (radio) y reduce
            // su altura de layout para no dejar hueco ni franja lateral.
            Surface(
                modifier = Modifier
                    .fillMaxWidth()
                    .layout { measurable, constraints ->
                        val placeable = measurable.measure(constraints)
                        val overlap = WelcomeSheetTopRadius.roundToPx()
                        layout(placeable.width, placeable.height - overlap) {
                            placeable.placeRelative(0, -overlap)
                        }
                    },
                shape = RoundedCornerShape(
                    topStart = WelcomeSheetTopRadius,
                    topEnd = WelcomeSheetTopRadius,
                ),
                color = surfaceColor,
            ) {
                Column(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalAlignment = Alignment.CenterHorizontally,
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

                    TextButton(
                        onClick = onContinueWithoutAccount,
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = WelcomeButtonHorizontalInset)
                            .sizeIn(minHeight = AnuraDimens.sizeTouch)
                            .padding(bottom = WelcomeGuestBottomMargin),
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
    }
}

/**
 * Fondo de board Penpot `INICIAR SECCION` / `crear cuenta` (`#EFF4F0`), igual que el splash.
 * No es `bg.base` del tema.
 */
private val AuthFormBackground = Color(0xFFEFF4F0)

/** Medidas de botones en los boards de auth (radio 12, no el pill 30 de COMP · Botones). */
private val AuthPrimaryButtonHeight = 60.dp
private val AuthSecondaryButtonHeight = 56.dp
private val AuthFieldRadius = 12.dp
private val AuthContentInset = 19.dp
private val AuthProfileCardHeight = 72.dp

private enum class SignUpUsageProfile {
    Curiosity,
    Study,
}

/**
 * `INICIAR SECCION` (§4.1).
 *
 * Estados locales mock: texto de correo/contraseña, visibilidad de contraseña.
 * Sin loading/error de red (auth real aún no conectada). Acciones:
 * Entrar / Google / sin conexión → Home; Crear una → SignUp; olvidé contraseña → no-op mock.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SignInScreen(
    onBackClick: () -> Unit,
    onSignedIn: () -> Unit,
    onGoToSignUp: () -> Unit,
    onContinueOffline: () -> Unit,
    onForgotPassword: () -> Unit = {},
) {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var passwordVisible by remember { mutableStateOf(false) }

    Surface(
        modifier = Modifier.fillMaxSize(),
        color = AuthFormBackground,
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .navigationBarsPadding(),
        ) {
            AnuraTopBar(
                title = stringResource(R.string.sign_in_title),
                onBackClick = onBackClick,
            )

            Column(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .verticalScroll(rememberScrollState())
                    .padding(horizontal = AuthContentInset)
                    .padding(top = AnuraDimens.spaceGap),
            ) {
                Text(
                    text = stringResource(R.string.sign_in_heading),
                    style = MaterialTheme.typography.titleLarge.copy(
                        fontWeight = FontWeight.Bold,
                        fontSize = 22.sp,
                    ),
                    color = MaterialTheme.colorScheme.onSurface,
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = stringResource(R.string.sign_in_subtitle),
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = FontWeight.Normal,
                        fontSize = 15.sp,
                    ),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )

                Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))

                AnuraTextField(
                    value = email,
                    onValueChange = { email = it },
                    label = stringResource(R.string.sign_in_email_label),
                    placeholder = stringResource(R.string.sign_in_email_placeholder),
                    leadingIcon = AnuraIcons.Email,
                    keyboardType = KeyboardType.Email,
                    modifier = Modifier.fillMaxWidth(),
                )

                Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))

                AnuraTextField(
                    value = password,
                    onValueChange = { password = it },
                    label = stringResource(R.string.sign_in_password_label),
                    leadingIcon = AnuraIcons.Lock,
                    trailingIcon = if (passwordVisible) AnuraIcons.VisibilityOff else AnuraIcons.Visibility,
                    trailingIconContentDescription = stringResource(
                        if (passwordVisible) {
                            R.string.sign_in_hide_password_cd
                        } else {
                            R.string.sign_in_show_password_cd
                        },
                    ),
                    onTrailingIconClick = { passwordVisible = !passwordVisible },
                    keyboardType = KeyboardType.Password,
                    visualTransformation = if (passwordVisible) {
                        VisualTransformation.None
                    } else {
                        PasswordVisualTransformation()
                    },
                    modifier = Modifier.fillMaxWidth(),
                )

                TextButton(
                    onClick = onForgotPassword,
                    modifier = Modifier.align(Alignment.End),
                ) {
                    Text(
                        text = stringResource(R.string.sign_in_forgot_password),
                        style = MaterialTheme.typography.labelLarge.copy(
                            fontWeight = FontWeight.SemiBold,
                            fontSize = 11.sp,
                        ),
                        color = AnuraTheme.extendedColors.accentInk,
                    )
                }

                Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))

                AuthPrimaryButton(
                    text = stringResource(R.string.sign_in_enter),
                    onClick = onSignedIn,
                )

                Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))

                AuthOrDivider()

                Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))

                AuthOutlineButton(
                    text = stringResource(R.string.sign_in_google),
                    onClick = onSignedIn,
                )

                Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))

                AuthSecondaryIconButton(
                    text = stringResource(R.string.sign_in_offline),
                    icon = AnuraIcons.CloudOff,
                    onClick = onContinueOffline,
                )
            }

            val noAccount = stringResource(R.string.sign_in_no_account)
            val createOne = stringResource(R.string.sign_in_create_one)
            Text(
                text = buildAnnotatedString {
                    append(noAccount)
                    withStyle(SpanStyle(fontWeight = FontWeight.Bold)) {
                        append(createOne)
                    }
                },
                style = MaterialTheme.typography.titleMedium.copy(
                    fontWeight = FontWeight.SemiBold,
                    fontSize = 15.sp,
                ),
                color = AnuraTheme.extendedColors.accentInk,
                textAlign = TextAlign.Center,
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable(role = Role.Button, onClick = onGoToSignUp)
                    .padding(AnuraDimens.spaceSection)
                    .sizeIn(minHeight = AnuraDimens.sizeTouch),
            )
        }
    }
}

/**
 * `crear cuenta` (§4.1).
 *
 * Estados locales mock: nombre/correo/contraseña, visibilidad, perfil de uso,
 * aceptación de términos. Sin loading/error de red. Crear cuenta → Home.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SignUpScreen(
    onBackClick: () -> Unit,
    onSignedUp: () -> Unit,
    @Suppress("UNUSED_PARAMETER") onGoToSignIn: () -> Unit,
) {
    var name by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var passwordVisible by remember { mutableStateOf(false) }
    var usageProfile by remember { mutableStateOf(SignUpUsageProfile.Curiosity) }
    var termsAccepted by remember { mutableStateOf(true) }

    Surface(
        modifier = Modifier.fillMaxSize(),
        color = AuthFormBackground,
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .navigationBarsPadding(),
        ) {
            AnuraTopBar(
                title = stringResource(R.string.sign_up_title),
                onBackClick = onBackClick,
            )

            Column(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .verticalScroll(rememberScrollState())
                    .padding(horizontal = AuthContentInset)
                    .padding(top = AnuraDimens.spaceGap),
            ) {
                Text(
                    text = stringResource(R.string.sign_up_heading),
                    style = MaterialTheme.typography.titleLarge.copy(
                        fontWeight = FontWeight.Bold,
                        fontSize = 22.sp,
                    ),
                    color = MaterialTheme.colorScheme.onSurface,
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = stringResource(R.string.sign_up_subtitle),
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = FontWeight.Normal,
                        fontSize = 15.sp,
                    ),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )

                Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))

                AnuraTextField(
                    value = name,
                    onValueChange = { name = it },
                    label = stringResource(R.string.sign_up_name_label),
                    placeholder = stringResource(R.string.sign_up_name_placeholder),
                    leadingIcon = AnuraIcons.Person,
                    modifier = Modifier.fillMaxWidth(),
                )

                Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))

                AnuraTextField(
                    value = email,
                    onValueChange = { email = it },
                    label = stringResource(R.string.sign_up_email_label),
                    placeholder = stringResource(R.string.sign_up_email_placeholder),
                    leadingIcon = AnuraIcons.Email,
                    keyboardType = KeyboardType.Email,
                    modifier = Modifier.fillMaxWidth(),
                )

                Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))

                AnuraTextField(
                    value = password,
                    onValueChange = { password = it },
                    label = stringResource(R.string.sign_up_password_label),
                    placeholder = stringResource(R.string.sign_up_password_placeholder),
                    leadingIcon = AnuraIcons.Lock,
                    trailingIcon = if (passwordVisible) AnuraIcons.VisibilityOff else AnuraIcons.Visibility,
                    trailingIconContentDescription = stringResource(
                        if (passwordVisible) {
                            R.string.sign_in_hide_password_cd
                        } else {
                            R.string.sign_in_show_password_cd
                        },
                    ),
                    onTrailingIconClick = { passwordVisible = !passwordVisible },
                    keyboardType = KeyboardType.Password,
                    visualTransformation = if (passwordVisible) {
                        VisualTransformation.None
                    } else {
                        PasswordVisualTransformation()
                    },
                    modifier = Modifier.fillMaxWidth(),
                )

                Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))

                Text(
                    text = stringResource(R.string.sign_up_usage_label),
                    style = MaterialTheme.typography.labelLarge.copy(
                        fontWeight = FontWeight.SemiBold,
                        fontSize = 11.sp,
                    ),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )

                Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                ) {
                    SignUpProfileCard(
                        label = stringResource(R.string.sign_up_profile_curiosity),
                        icon = AnuraIcons.Curiosity,
                        selected = usageProfile == SignUpUsageProfile.Curiosity,
                        onClick = { usageProfile = SignUpUsageProfile.Curiosity },
                        modifier = Modifier.weight(1f),
                    )
                    SignUpProfileCard(
                        label = stringResource(R.string.sign_up_profile_study),
                        icon = AnuraIcons.Study,
                        selected = usageProfile == SignUpUsageProfile.Study,
                        onClick = { usageProfile = SignUpUsageProfile.Study },
                        modifier = Modifier.weight(1f),
                    )
                }

                Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { termsAccepted = !termsAccepted }
                        .sizeIn(minHeight = AnuraDimens.sizeTouch),
                    verticalAlignment = Alignment.Top,
                ) {
                    Surface(
                        modifier = Modifier.size(24.dp),
                        shape = RoundedCornerShape(AnuraDimens.radiusButton),
                        color = if (termsAccepted) {
                            AnuraTheme.extendedColors.accentInk
                        } else {
                            MaterialTheme.colorScheme.surface
                        },
                        border = if (termsAccepted) {
                            null
                        } else {
                            BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
                        },
                    ) {
                        if (termsAccepted) {
                            Box(
                                modifier = Modifier.fillMaxSize(),
                                contentAlignment = Alignment.Center,
                            ) {
                                Icon(
                                    imageVector = AnuraIcons.Check,
                                    contentDescription = null,
                                    tint = MaterialTheme.colorScheme.onPrimary,
                                    modifier = Modifier.size(18.dp),
                                )
                            }
                        }
                    }
                    Spacer(modifier = Modifier.width(AnuraDimens.spaceGap))
                    Text(
                        text = stringResource(R.string.sign_up_terms),
                        style = MaterialTheme.typography.bodyMedium.copy(
                            fontWeight = FontWeight.Medium,
                            fontSize = 13.sp,
                        ),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.weight(1f),
                    )
                }

                Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))

                AuthPrimaryButton(
                    text = stringResource(R.string.sign_up_create),
                    onClick = onSignedUp,
                    enabled = termsAccepted,
                )
            }

            Text(
                text = stringResource(R.string.sign_up_guest_note),
                style = MaterialTheme.typography.labelLarge.copy(
                    fontWeight = FontWeight.Medium,
                    fontSize = 11.sp,
                ),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = AuthContentInset)
                    .padding(bottom = AnuraDimens.spaceSection),
            )
        }
    }
}

@Composable
private fun AuthPrimaryButton(
    text: String,
    onClick: () -> Unit,
    enabled: Boolean = true,
) {
    Button(
        onClick = onClick,
        enabled = enabled,
        modifier = Modifier
            .fillMaxWidth()
            .height(AuthPrimaryButtonHeight),
        shape = RoundedCornerShape(AuthFieldRadius),
        colors = ButtonDefaults.buttonColors(
            containerColor = AnuraTheme.extendedColors.accentInk,
            contentColor = MaterialTheme.colorScheme.onPrimary,
        ),
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.titleLarge.copy(
                fontWeight = FontWeight.SemiBold,
                fontSize = 20.sp,
            ),
        )
    }
}

@Composable
private fun AuthOutlineButton(
    text: String,
    onClick: () -> Unit,
) {
    OutlinedButton(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth()
            .height(AuthSecondaryButtonHeight),
        shape = RoundedCornerShape(AuthFieldRadius),
        border = BorderStroke(2.dp, AnuraTheme.extendedColors.accentInk),
        colors = ButtonDefaults.outlinedButtonColors(
            contentColor = AnuraTheme.extendedColors.accentInk,
        ),
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.titleMedium.copy(
                fontWeight = FontWeight.SemiBold,
                fontSize = 15.sp,
            ),
        )
    }
}

@Composable
private fun AuthSecondaryIconButton(
    text: String,
    icon: ImageVector,
    onClick: () -> Unit,
) {
    OutlinedButton(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth()
            .height(AuthSecondaryButtonHeight),
        shape = RoundedCornerShape(AuthFieldRadius),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
        colors = ButtonDefaults.outlinedButtonColors(
            containerColor = MaterialTheme.colorScheme.surface,
            contentColor = AnuraTheme.extendedColors.accentInk,
        ),
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            modifier = Modifier.size(24.dp),
        )
        Spacer(modifier = Modifier.width(AnuraDimens.spaceGap))
        Text(
            text = text,
            style = MaterialTheme.typography.titleMedium.copy(
                fontWeight = FontWeight.SemiBold,
                fontSize = 15.sp,
            ),
        )
    }
}

@Composable
private fun AuthOrDivider() {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        HorizontalDivider(
            modifier = Modifier.weight(1f),
            color = MaterialTheme.colorScheme.outlineVariant,
        )
        Text(
            text = stringResource(R.string.sign_in_or),
            style = MaterialTheme.typography.labelLarge.copy(
                fontWeight = FontWeight.Medium,
                fontSize = 11.sp,
            ),
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(horizontal = AnuraDimens.spaceGap),
        )
        HorizontalDivider(
            modifier = Modifier.weight(1f),
            color = MaterialTheme.colorScheme.outlineVariant,
        )
    }
}

@Composable
private fun SignUpProfileCard(
    label: String,
    icon: ImageVector,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val border = if (selected) {
        BorderStroke(2.dp, AnuraTheme.extendedColors.accentInk)
    } else {
        BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    }
    Surface(
        onClick = onClick,
        modifier = modifier.height(AuthProfileCardHeight),
        shape = RoundedCornerShape(AuthFieldRadius),
        color = MaterialTheme.colorScheme.surface,
        border = border,
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 8.dp, vertical = AnuraDimens.spaceGap),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.size(24.dp),
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = label,
                style = MaterialTheme.typography.labelLarge.copy(
                    fontWeight = FontWeight.SemiBold,
                    fontSize = 13.sp,
                ),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
            )
        }
    }
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

@AnuraPreviews
@Composable
private fun SignInScreenPreview() {
    AnuraTheme {
        SignInScreen(
            onBackClick = {},
            onSignedIn = {},
            onGoToSignUp = {},
            onContinueOffline = {},
        )
    }
}

@AnuraPreviews
@Composable
private fun SignUpScreenPreview() {
    AnuraTheme {
        SignUpScreen(
            onBackClick = {},
            onSignedUp = {},
            onGoToSignIn = {},
        )
    }
}
