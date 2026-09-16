package me.juanlabs.anura.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavDestination.Companion.hasRoute
import androidx.navigation.NavHostController
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import me.juanlabs.anura.designsystem.component.AnuraNavBar
import me.juanlabs.anura.designsystem.component.AnuraNavBarItem
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.theme.AnuraDimens

private val TopLevelItems = listOf(
    AnuraNavBarItem("Inicio", AnuraIcons.Home),
    AnuraNavBarItem("Explorar", AnuraIcons.Explore),
    AnuraNavBarItem("Observaciones", AnuraIcons.Observations),
    AnuraNavBarItem("Ajustes", AnuraIcons.Settings),
)

/**
 * Scaffold raíz de ANURA: `NavigationBar` M3 + FAB central (§3.9 `AnuraNavBar`,
 * §3.7-P2/decisiones 8-9) sobre el [AnuraNavHost]. La barra inferior y el FAB solo se
 * muestran cuando el destino actual es uno de los 4 tabs (§4.4) — en Auth, Captura o
 * cualquier pantalla de detalle no hay barra que mostrar.
 */
@Composable
fun AnuraScaffold(navController: NavHostController = rememberNavController()) {
    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = backStackEntry?.destination

    val selectedTabIndex = when {
        currentDestination?.hasRoute<AnuraRoute.Home>() == true -> 0
        currentDestination?.hasRoute<AnuraRoute.Explore>() == true -> 1
        currentDestination?.hasRoute<AnuraRoute.Observations>() == true -> 2
        currentDestination?.hasRoute<AnuraRoute.Settings>() == true -> 3
        else -> null
    }
    val showTabChrome = selectedTabIndex != null

    Scaffold(
        bottomBar = {
            if (showTabChrome) {
                AnuraNavBar(
                    items = TopLevelItems,
                    selectedIndex = selectedTabIndex,
                    onItemSelected = { index ->
                        navController.navigateToTab(TOP_LEVEL_ROUTES[index])
                    },
                )
            }
        },
        floatingActionButton = {
            if (showTabChrome) {
                FloatingActionButton(
                    onClick = { navController.navigate(AnuraRoute.WhatToRegister) },
                    modifier = Modifier.size(AnuraDimens.sizeThumb),
                ) {
                    Icon(imageVector = AnuraIcons.Add, contentDescription = "Registrar")
                }
            }
        },
    ) { innerPadding ->
        AnuraNavHost(
            navController = navController,
            modifier = Modifier.padding(bottom = if (showTabChrome) innerPadding.calculateBottomPadding() else 0.dp),
        )
    }
}

private val TOP_LEVEL_ROUTES: List<AnuraRoute> = listOf(
    AnuraRoute.Home,
    AnuraRoute.Explore,
    AnuraRoute.Observations,
    AnuraRoute.Settings,
)

/**
 * Cambia de pestaña con las reglas de back stack de §4.3: `launchSingleTop = true`,
 * `restoreState = true`, `popUpTo(startDestination) { saveState = true }`. `Home`
 * actúa como el destino base del área de pestañas: `AuthGraph` ya salió del stack al
 * llegar aquí (se saca con `inclusive = true` al continuar sin cuenta o iniciar
 * sesión), así que es el `startDestination` real del área navegable por tabs.
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
