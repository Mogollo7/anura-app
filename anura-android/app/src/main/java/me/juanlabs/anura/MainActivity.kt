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
import me.juanlabs.anura.feature.startup.StartupLoadingScreen
import me.juanlabs.anura.navigation.AnuraScaffold

/**
 * Punto de entrada único de la app (§4).
 *
 * Orden de arranque fiel a Penpot:
 * 1. Splash nativo (`Theme.ANURA.Splash`) → `Estado · Cargando (PANTALLA DE CARGA INICIO)`.
 * 2. `AnuraScaffold` / `AnuraNavHost` — empieza en `AuthGraph` → `Welcome`.
 *
 * El splash no es ruta de [me.juanlabs.anura.navigation.AnuraRoute] (§4.1); es la
 * puerta previa al grafo. Runtime real (modelo/paquete) aún no conectado.
 */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen()
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            AnuraTheme {
                var startupReady by rememberSaveable { mutableStateOf(false) }
                if (!startupReady) {
                    StartupLoadingScreen(onReady = { startupReady = true })
                } else {
                    AnuraScaffold()
                }
            }
        }
    }
}
