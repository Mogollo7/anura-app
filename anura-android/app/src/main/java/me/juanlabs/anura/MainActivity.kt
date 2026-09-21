package me.juanlabs.anura

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraAccentRole
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode
import me.juanlabs.anura.feature.startup.StartupLoadingScreen
import me.juanlabs.anura.navigation.AnuraScaffold

/**
 * Punto de entrada único de la app (§4).
 *
 * Orden de arranque fiel a Penpot:
 * 1. `StartupLoadingScreen` (`Estado · Cargando`) — primera vista de la app.
 *    El splash nativo solo pinta el fondo del board y se retira al primer frame.
 * 2. `AnuraScaffold` / `AnuraNavHost` — empieza en `AuthGraph` → `Welcome`.
 *
 * El splash no es ruta de [me.juanlabs.anura.navigation.AnuraRoute] (§4.1); es la
 * puerta previa al grafo. Runtime real (modelo/paquete) aún no conectado.
 */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        val splashScreen = installSplashScreen()
        super.onCreate(savedInstanceState)
        // Sin zoom/fade del icono nativo: el primer frame visible es StartupLoadingScreen.
        splashScreen.setOnExitAnimationListener { splashView -> splashView.remove() }
        enableEdgeToEdge()
        setContent {
            var themeMode by rememberSaveable { mutableStateOf(AnuraThemeMode.Sistema) }
            var accentRole by rememberSaveable { mutableStateOf(AnuraAccentRole.Ink) }
            var preferReduceMotion by rememberSaveable { mutableStateOf(false) }
            var preferLargeText by rememberSaveable { mutableStateOf(false) }
            AnuraTheme(
                themeMode = themeMode,
                accentRole = accentRole,
                preferReduceMotion = preferReduceMotion,
                preferLargeText = preferLargeText,
            ) {
                // Cold start siempre muestra el splash. Rotación/proceso restaurado
                // no lo repite (rememberSaveable).
                var startupReady by rememberSaveable { mutableStateOf(false) }
                if (!startupReady) {
                    StartupLoadingScreen(onReady = { startupReady = true })
                } else {
                    AnuraScaffold(
                        themeMode = themeMode,
                        onThemeModeChange = { themeMode = it },
                        accentRole = accentRole,
                        onAccentRoleChange = { accentRole = it },
                        preferReduceMotion = preferReduceMotion,
                        onPreferReduceMotionChange = { preferReduceMotion = it },
                        preferLargeText = preferLargeText,
                        onPreferLargeTextChange = { preferLargeText = it },
                    )
                }
            }
        }
    }
}
