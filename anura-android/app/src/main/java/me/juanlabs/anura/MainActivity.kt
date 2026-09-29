package me.juanlabs.anura

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalView
import androidx.core.content.ContextCompat
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import androidx.core.view.WindowCompat
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import me.juanlabs.anura.core.auth.emitAuthToken
import me.juanlabs.anura.core.data.ContentCatalog
import me.juanlabs.anura.core.auth.extractAuthToken
import me.juanlabs.anura.core.data.emitNotificationOpen
import me.juanlabs.anura.core.data.emitObservationDeepLink
import me.juanlabs.anura.core.data.extractObservationId
import me.juanlabs.anura.core.data.isNotificationOpenUri
import me.juanlabs.anura.core.data.notificationIdFromUri
import me.juanlabs.anura.core.notifications.AnuraNotifications
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
 * puerta previa al grafo. Espera (con tope) a que se restauren la sesión y el catálogo guardados.
 */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        val splashScreen = installSplashScreen()
        super.onCreate(savedInstanceState)
        // Sin zoom/fade del icono nativo: el primer frame visible es StartupLoadingScreen.
        splashScreen.setOnExitAnimationListener { splashView -> splashView.remove() }
        enableEdgeToEdge()
        AnuraNotifications.ensureChannel(applicationContext)
        handleAuthDeepLink(intent)
        handleObservationDeepLink(intent)
        handleNotificationDeepLink(intent)
        // Catálogo de contenido publicado (fichas y carrusel): primero lo guardado en el
        // teléfono, luego el servidor si responde. Sin red, la app sigue con lo que tiene.
        lifecycleScope.launch {
            ContentCatalog.sync(applicationContext)
        }
        setContent {
            // Android 13+ exige este permiso en runtime para poder mostrar cualquier
            // notificación (avisos, `core/notifications/AnuraNotifications.kt`); antes de eso
            // el sistema las concede solas. Se pide cuando ya se fue el splash — pedirlo en
            // el primer frame lo tapa el splash y la persona no llega a ver el diálogo. Si
            // lo niega, los avisos se siguen viendo dentro de la app.
            val notificationPermission = rememberLauncherForActivityResult(
                ActivityResultContracts.RequestPermission(),
            ) { }
            var themeMode by rememberSaveable { mutableStateOf(AnuraThemeMode.Sistema) }
            var accentRole by rememberSaveable { mutableStateOf(AnuraAccentRole.Ink) }
            var preferReduceMotion by rememberSaveable { mutableStateOf(false) }
            var preferLargeText by rememberSaveable { mutableStateOf(false) }

            // Iconos de la barra de estado/navegación según el tema REAL resuelto (mismo
            // cálculo que AnuraTheme.invoke), no un valor estático de themes.xml. Antes
            // solo WelcomeScreen forzaba esto de forma temporal y local; en el resto de
            // la app (Ajustes, Perfil, wizard...) los iconos quedaban oscuros e
            // ilegibles sobre fondo oscuro/Luz Roja (auditoría Fase 0-9, P0 #13).
            val systemDark = isSystemInDarkTheme()
            val resolvedIsDark = when (themeMode) {
                AnuraThemeMode.Sistema -> systemDark
                AnuraThemeMode.Claro -> false
                AnuraThemeMode.Oscuro, AnuraThemeMode.LuzRoja -> true
            }
            val view = LocalView.current
            if (!view.isInEditMode) {
                DisposableEffect(view, resolvedIsDark) {
                    val window = this@MainActivity.window
                    val controller = WindowCompat.getInsetsController(window, view)
                    controller.isAppearanceLightStatusBars = !resolvedIsDark
                    controller.isAppearanceLightNavigationBars = !resolvedIsDark
                    onDispose {}
                }
            }

            AnuraTheme(
                themeMode = themeMode,
                accentRole = accentRole,
                preferReduceMotion = preferReduceMotion,
                preferLargeText = preferLargeText,
            ) {
                // Cold start siempre muestra el splash. Rotación/proceso restaurado
                // no lo repite (rememberSaveable).
                var startupReady by rememberSaveable { mutableStateOf(false) }
                LaunchedEffect(startupReady) {
                    if (!startupReady) return@LaunchedEffect
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
                        ContextCompat.checkSelfPermission(
                            this@MainActivity,
                            Manifest.permission.POST_NOTIFICATIONS,
                        ) != PackageManager.PERMISSION_GRANTED
                    ) {
                        notificationPermission.launch(Manifest.permission.POST_NOTIFICATIONS)
                    }
                }
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

    // singleTask (AndroidManifest.xml): la vuelta del login de Google llega aquí, no a un
    // onCreate nuevo — la Activity ya existe, solo estaba detrás de la Custom Tab.
    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        handleAuthDeepLink(intent)
        handleObservationDeepLink(intent)
        handleNotificationDeepLink(intent)
    }

    private fun handleAuthDeepLink(intent: Intent?) {
        val token = extractAuthToken(intent?.data) ?: return
        emitAuthToken(token)
    }

    // Tocar una notificación de aviso (core/notifications/AnuraNotifications.kt) llega aquí
    // — mismo puente que handleAuthDeepLink.
    private fun handleNotificationDeepLink(intent: Intent?) {
        if (!isNotificationOpenUri(intent?.data)) return
        emitNotificationOpen(notificationIdFromUri(intent?.data))
    }

    // App Links (AndroidManifest.xml): https://anura.juanlabs.me/explorer/<id> llega aquí en
    // vez de al navegador cuando la app está instalada — mismo puente que handleAuthDeepLink.
    private fun handleObservationDeepLink(intent: Intent?) {
        val id = extractObservationId(intent?.data) ?: return
        emitObservationDeepLink(id)
    }
}
