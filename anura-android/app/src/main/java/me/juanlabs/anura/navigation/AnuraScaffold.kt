package me.juanlabs.anura.navigation

import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.navigation.NavDestination
import androidx.navigation.NavDestination.Companion.hasRoute
import androidx.navigation.NavHostController
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import me.juanlabs.anura.designsystem.component.AnuraNavBar
import me.juanlabs.anura.designsystem.component.AnuraNavBarItem
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.theme.AnuraTheme

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
fun AnuraScaffold(navController: NavHostController = rememberNavController()) {
    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = backStackEntry?.destination
    val previousDestination = navController.previousBackStackEntry?.destination

    val selectedTabIndex = tabIndexFor(currentDestination)
        ?: tabIndexFor(previousDestination)?.takeIf {
            currentDestination?.hasRoute<AnuraRoute.WhatToRegister>() == true
        }

    val showTabChrome = selectedTabIndex != null

    Scaffold(
        containerColor = if (showTabChrome) {
            Color.Transparent
        } else {
            AnuraTheme.extendedColors.boardBackground
        },
        contentWindowInsets = WindowInsets(0, 0, 0, 0),
        bottomBar = {
            selectedTabIndex?.let { tabIndex ->
                AnuraNavBar(
                    items = TopLevelItems,
                    selectedIndex = tabIndex,
                    onItemSelected = { index ->
                        navController.navigateToTab(TOP_LEVEL_ROUTES[index])
                    },
                    onFabClick = { navController.navigate(AnuraRoute.WhatToRegister) },
                )
            }
        },
    ) { innerPadding ->
        // Padding inferior estable mientras haya chrome: no bajar a 0.dp en el frame
        // en que el destino deja de ser un tab (provoca salto en Home).
        AnuraNavHost(
            navController = navController,
            modifier = Modifier.padding(
                bottom = if (showTabChrome) {
                    innerPadding.calculateBottomPadding()
                } else {
                    0.dp
                },
            ),
        )
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
