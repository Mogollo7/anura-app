package me.juanlabs.anura.feature.auth

import android.app.Activity
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
import androidx.compose.foundation.selection.toggleable
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.minimumInteractiveComponentSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.BiasAlignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.layout.layout
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.view.WindowCompat
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraFormButtonStyle
import me.juanlabs.anura.designsystem.component.AnuraSectionLabel
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
 * contenedor (`Surface` / sheet) cede altura (hero con `weight`) — nunca se
 * comprimen esos gaps. Contenedor blanco: radio superior 30 dp.
 */
private val WelcomeSheetTopPadding = 47.dp
private val WelcomeSheetBottomPadding = AnuraDimens.spaceSection
/** Piso del área hero para que no desaparezca. */
private val WelcomeHeroMinHeight = 160.dp

/**
 * Encuadre Penpot: capa `image` 867×611 en (−141, −29); fill real 1024×721.
 * Bias sobre el bitmap exportado (1024×721).
 */
private val WelcomeHeroAlignment = BiasAlignment(
    horizontalBias = ((141f * 1024f / 867f + 393f * 1024f / 867f / 2f) - 1024f / 2f) / (1024f / 2f),
    verticalBias = ((29f * 721f / 611f + 520f * 721f / 611f / 2f) - 721f / 2f) / (721f / 2f),
)

/**
 * `LOGIN OR SINGUO (bienvenida)` (§4.1, grafo `AuthGraph`).
 *
 * Estados: pantalla estática de entrada — sin loading/error propios. Acciones:
 * crear cuenta → [AnuraRoute.SignUp], ya tengo cuenta → [AnuraRoute.SignIn].
 * El acceso sin cuenta vive en Iniciar sesión / Crear cuenta.
 *
 * Altura de la imagen: desde el top hasta donde empieza «Conoce sobre anuros».
 * El sheet se solapa 30 dp sobre la rana (radio superior) sin franjas extra.
 */
@Composable
fun WelcomeScreen(
    onGoToSignIn: () -> Unit,
    onGoToSignUp: () -> Unit,
) {
    val surfaceColor = MaterialTheme.colorScheme.surface

    // Bug §RNF: `themes.xml` fija iconos oscuros de barra de estado (windowLightStatusBar)
    // y aquí se pinta una foto casi negra debajo → hora/iconos invisibles. Se fuerzan
    // iconos claros mientras esta pantalla está en composición.
    val view = LocalView.current
    if (!view.isInEditMode) {
        DisposableEffect(view) {
            val window = (view.context as? Activity)?.window
            val controller = window?.let { WindowCompat.getInsetsController(it, view) }
            val previous = controller?.isAppearanceLightStatusBars
            controller?.isAppearanceLightStatusBars = false
            onDispose { if (controller != null && previous != null) controller.isAppearanceLightStatusBars = previous }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .navigationBarsPadding(),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        // Hero flexible: al quitar el CTA inferior, el sheet se encoge y la
        // imagen gana el espacio liberado sin cambiar BiasAlignment/crop.
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

        Surface(
            modifier = Modifier
                .fillMaxWidth()
                .layout { measurable, constraints ->
                    val placeable = measurable.measure(constraints)
                    val overlap = AnuraDimens.radiusSheet.roundToPx()
                    layout(placeable.width, placeable.height - overlap) {
                        placeable.placeRelative(0, -overlap)
                    }
                },
            shape = RoundedCornerShape(
                topStart = AnuraDimens.radiusSheet,
                topEnd = AnuraDimens.radiusSheet,
            ),
            color = surfaceColor,
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = AnuraDimens.spacePopupInset)
                    .padding(
                        top = WelcomeSheetTopPadding,
                        bottom = WelcomeSheetBottomPadding,
                    ),
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Text(
                    text = stringResource(R.string.welcome_title),
                    style = MaterialTheme.typography.headlineMedium,
                    color = MaterialTheme.colorScheme.onSurface,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.fillMaxWidth(),
                )

                Spacer(modifier = Modifier.height(AnuraDimens.spaceSheetTitleToBody))

                Text(
                    text = stringResource(R.string.welcome_body),
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = FontWeight.Normal,
                        lineHeight = 22.sp,
                    ),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.fillMaxWidth(),
                )

                Spacer(modifier = Modifier.height(AnuraDimens.spaceSheetBodyToActions))

                AnuraFormButton(
                    text = stringResource(R.string.welcome_create_account),
                    onClick = onGoToSignUp,
                    style = AnuraFormButtonStyle.Primary,
                )

                Spacer(modifier = Modifier.height(AnuraDimens.spaceActionGap))

                AnuraFormButton(
                    text = stringResource(R.string.welcome_have_account),
                    onClick = onGoToSignIn,
                    style = AnuraFormButtonStyle.OutlineNeutral,
                )
            }
        }
    }
}

private val AuthProfileCardHeight = 72.dp
/** Misma distancia al borde inferior en Iniciar sesión y Crear cuenta. */
private val AuthFooterBottomMargin = AnuraDimens.spaceSection

private enum class SignUpUsageProfile {
    Curiosity,
    Study,
}

/**
 * `INICIAR SECCION` (§4.1).
 *
 * Estados locales mock: texto de correo/contraseña, visibilidad de contraseña.
 * Sin loading/error de red. Entrar → Home; Entrar sin cuenta → Home (invitado);
 * Crear una → SignUp; olvidé contraseña → no-op mock.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SignInScreen(
    onBackClick: () -> Unit,
    onSignedIn: () -> Unit,
    onGoToSignUp: () -> Unit,
    onContinueWithoutAccount: () -> Unit,
    onForgotPassword: () -> Unit = {},
) {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var passwordVisible by remember { mutableStateOf(false) }

    Surface(
        modifier = Modifier.fillMaxSize(),
        color = AnuraTheme.extendedColors.boardBackground,
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .navigationBarsPadding(),
        ) {
            AnuraTopBar(
                title = stringResource(R.string.sign_in_title),
                onBackClick = onBackClick,
                centerTitle = true,
            )

            Column(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .verticalScroll(rememberScrollState())
                    .padding(horizontal = AnuraDimens.spaceGutter),
            ) {
                Text(
                    text = stringResource(R.string.sign_in_heading),
                    style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
                    color = MaterialTheme.colorScheme.onSurface,
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceTitleToSubtitle))
                Text(
                    text = stringResource(R.string.sign_in_subtitle),
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Normal),
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
                        style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
                        color = AnuraTheme.extendedColors.accentInk,
                    )
                }

                Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))

                AnuraFormButton(
                    text = stringResource(R.string.sign_in_enter),
                    onClick = onSignedIn,
                    style = AnuraFormButtonStyle.Primary,
                )

                Spacer(modifier = Modifier.height(AnuraDimens.spaceActionGap))

                AnuraFormButton(
                    text = stringResource(R.string.sign_in_without_account),
                    onClick = onContinueWithoutAccount,
                    style = AnuraFormButtonStyle.Outline,
                )
            }

            AuthFormFooter {
                AuthFooterLinkRow(
                    prefix = stringResource(R.string.sign_in_no_account),
                    action = stringResource(R.string.sign_in_create_one),
                    onActionClick = onGoToSignUp,
                )
            }
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
    onGoToSignIn: () -> Unit,
    onContinueWithoutAccount: () -> Unit,
) {
    var name by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var passwordVisible by remember { mutableStateOf(false) }
    var usageProfile by remember { mutableStateOf(SignUpUsageProfile.Curiosity) }
    var termsAccepted by remember { mutableStateOf(true) }

    Surface(
        modifier = Modifier.fillMaxSize(),
        color = AnuraTheme.extendedColors.boardBackground,
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .navigationBarsPadding(),
        ) {
            AnuraTopBar(
                title = stringResource(R.string.sign_up_title),
                onBackClick = onBackClick,
                centerTitle = true,
            )

            Column(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .verticalScroll(rememberScrollState())
                    .padding(horizontal = AnuraDimens.spaceGutter),
            ) {
                Text(
                    text = stringResource(R.string.sign_up_heading),
                    style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
                    color = MaterialTheme.colorScheme.onSurface,
                )
                Spacer(modifier = Modifier.height(AnuraDimens.spaceTitleToSubtitle))
                Text(
                    text = stringResource(R.string.sign_up_subtitle),
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Normal),
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

                AnuraSectionLabel(stringResource(R.string.sign_up_usage_label))

                Spacer(modifier = Modifier.height(AnuraDimens.spaceLabelToContent))

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
                        .toggleable(
                            value = termsAccepted,
                            role = Role.Checkbox,
                            onValueChange = { termsAccepted = it },
                        )
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
                        style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.Medium),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.weight(1f),
                    )
                }

                Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))

                AnuraFormButton(
                    text = stringResource(R.string.sign_up_create),
                    onClick = onSignedUp,
                    style = AnuraFormButtonStyle.Primary,
                    enabled = termsAccepted,
                )

                Spacer(modifier = Modifier.height(AnuraDimens.spaceActionGap))

                AnuraFormButton(
                    text = stringResource(R.string.sign_up_without_account),
                    onClick = onContinueWithoutAccount,
                    style = AnuraFormButtonStyle.Outline,
                )
            }

            AuthFormFooter {
                AuthFooterLinkRow(
                    prefix = stringResource(R.string.sign_up_footer_prefix),
                    action = stringResource(R.string.sign_up_footer_sign_in),
                    onActionClick = onGoToSignIn,
                )
            }
        }
    }
}

/** Pie de auth: misma altura y margen inferior en SignIn y SignUp. */
@Composable
private fun AuthFormFooter(
    content: @Composable () -> Unit,
) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = AnuraDimens.spaceGutter)
            .padding(bottom = AuthFooterBottomMargin)
            .sizeIn(minHeight = AnuraDimens.sizeTouch),
        contentAlignment = Alignment.Center,
    ) {
        content()
    }
}

/**
 * Prefijo en color secundario + espacio horizontal + acción en verde, misma baseline.
 */
@Composable
private fun AuthFooterLinkRow(
    prefix: String,
    action: String,
    onActionClick: () -> Unit,
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.Center,
    ) {
        Text(
            text = prefix,
            style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Normal),
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.alignByBaseline(),
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = action,
            style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
            color = AnuraTheme.extendedColors.accentInk,
            modifier = Modifier
                .alignByBaseline()
                .minimumInteractiveComponentSize()
                .clickable(role = Role.Button, onClick = onActionClick),
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
        shape = RoundedCornerShape(AnuraDimens.radiusCard),
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
                style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.SemiBold),
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
            onContinueWithoutAccount = {},
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
            onContinueWithoutAccount = {},
        )
    }
}
