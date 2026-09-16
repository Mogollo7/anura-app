package me.juanlabs.anura.feature.auth

import androidx.compose.runtime.Composable
import me.juanlabs.anura.navigation.MockNavAction
import me.juanlabs.anura.navigation.MockScreenScaffold

/**
 * `LOGIN OR SINGUO` (§4.1, grafo `AuthGraph`). Debe ofrecer "continuar sin cuenta"
 * (decisión 6/7) aunque Penpot no lo dibuje explícitamente — es el único botón que no
 * viene de un board concreto, el resto sí.
 */
@Composable
fun WelcomeScreen(
    onContinueWithoutAccount: () -> Unit,
    onGoToSignIn: () -> Unit,
    onGoToSignUp: () -> Unit,
) {
    MockScreenScaffold(
        title = "Bienvenida",
        actions = listOf(
            MockNavAction("Continuar sin cuenta", onContinueWithoutAccount),
            MockNavAction("Iniciar sesión", onGoToSignIn),
            MockNavAction("Crear cuenta", onGoToSignUp),
        ),
    )
}

/** `INICIAR SECCION` (§4.1). */
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

/** `crear cuenta` (§4.1). */
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
