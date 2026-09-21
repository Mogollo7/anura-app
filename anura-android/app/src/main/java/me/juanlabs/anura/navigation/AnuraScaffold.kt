package me.juanlabs.anura.navigation

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.navigation.NavDestination
import androidx.navigation.NavDestination.Companion.hasRoute
import androidx.navigation.NavHostController
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import me.juanlabs.anura.AnuraApplication
import me.juanlabs.anura.core.data.LocalAnuraRepository
import me.juanlabs.anura.designsystem.component.AnuraNavBar
import me.juanlabs.anura.designsystem.component.AnuraNavBarItem
import me.juanlabs.anura.designsystem.component.AnuraNavBarStackHeight
import me.juanlabs.anura.designsystem.component.LocalAnuraTabBarInset
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.theme.AnuraAccentRole
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

private val TopLevelItems = listOf(
    AnuraNavBarItem("Inicio", AnuraIcons.Home),
    AnuraNavBarItem("Explorar", AnuraIcons.Explore),
    AnuraNavBarItem("Listado", AnuraIcons.Observations),
    AnuraNavBarItem("Ajustes", AnuraIcons.Settings),
)

/**
 * Scaffold raíz de ANURA: navbar Penpot (píldora + FAB integrado) sobre [AnuraNavHost].
 *
 * El chrome de tabs se mantiene también bajo el diálogo `WhatToRegister` para no
 * recolapsar el padding inferior de Home en el frame previo a la transición (salto
 * vertical de los botones de acción).
 */
@Composable
fun AnuraScaffold(
    navController: NavHostController = rememberNavController(),
    themeMode: AnuraThemeMode = AnuraThemeMode.Sistema,
    onThemeModeChange: (AnuraThemeMode) -> Unit = {},
    accentRole: AnuraAccentRole = AnuraAccentRole.Ink,
    onAccentRoleChange: (AnuraAccentRole) -> Unit = {},
    preferReduceMotion: Boolean = false,
    onPreferReduceMotionChange: (Boolean) -> Unit = {},
    preferLargeText: Boolean = false,
    onPreferLargeTextChange: (Boolean) -> Unit = {},
) {
    val context = LocalContext.current
    val repository = (context.applicationContext as AnuraApplication).repository
    val snapshot by repository.state.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }
    LaunchedEffect(repository) {
        repository.messages.collect { message ->
            snackbarHostState.showSnackbar(message)
        }
    }
    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = backStackEntry?.destination
    val previousDestination = navController.previousBackStackEntry?.destination

    val selectedTabIndex = tabIndexFor(currentDestination)
        ?: tabIndexFor(previousDestination)?.takeIf {
            currentDestination?.hasRoute<AnuraRoute.WhatToRegister>() == true
        }

    val showTabChrome = selectedTabIndex != null

    CompositionLocalProvider(LocalAnuraRepository provides repository) {
        Scaffold(
            containerColor = AnuraTheme.extendedColors.boardBackground,
            contentWindowInsets = WindowInsets(0, 0, 0, 0),
            snackbarHost = { SnackbarHost(hostState = snackbarHostState) },
        ) {
            Box(modifier = Modifier.fillMaxSize()) {
                CompositionLocalProvider(
                    LocalAnuraTabBarInset provides if (showTabChrome) AnuraNavBarStackHeight else 0.dp,
                ) {
                    AnuraNavHost(
                        navController = navController,
                        themeMode = themeMode,
                        onThemeModeChange = onThemeModeChange,
                        accentRole = accentRole,
                        onAccentRoleChange = onAccentRoleChange,
                        preferReduceMotion = preferReduceMotion,
                        onPreferReduceMotionChange = onPreferReduceMotionChange,
                        preferLargeText = preferLargeText,
                        onPreferLargeTextChange = onPreferLargeTextChange,
                        activeSessionId = snapshot.activeSessionId,
                        onFieldSessionActivated = { },
                        onFieldSessionClosed = { repository.closeFieldSession() },
                        modifier = Modifier.fillMaxSize(),
                    )
                }
                selectedTabIndex?.let { tabIndex ->
                    AnuraNavBar(
                        items = TopLevelItems,
                        selectedIndex = tabIndex,
                        onItemSelected = { index ->
                            navController.navigateToTab(TOP_LEVEL_ROUTES[index])
                        },
                        onFabClick = { navController.navigate(AnuraRoute.WhatToRegister) },
                        modifier = Modifier.align(Alignment.BottomCenter),
                    )
                }
            }
        }
    }
}

private fun tabIndexFor(destination: NavDestination?): Int? = when {
    destination == null -> null
    destination.hasRoute<AnuraRoute.Home>() -> 0
    destination.hasRoute<AnuraRoute.Explore>() -> 1
    destination.hasRoute<AnuraRoute.Observations>() -> 2
    destination.hasRoute<AnuraRoute.Settings>() -> 3
    else -> null
}

private val TOP_LEVEL_ROUTES: List<AnuraRoute> = listOf(
    AnuraRoute.Home,
    AnuraRoute.Explore,
    AnuraRoute.Observations,
    AnuraRoute.Settings,
)

/**
 * Cambia de pestaña con las reglas de back stack de §4.3: `launchSingleTop = true`,
 * `restoreState = true`, `popUpTo(startDestination) { saveState = true }`.
 */
private fun NavHostController.navigateToTab(route: AnuraRoute) {
    navigate(route) {
        popUpTo(AnuraRoute.Home) {
            saveState = true
        }
        launchSingleTop = true
        restoreState = true
    }
}
