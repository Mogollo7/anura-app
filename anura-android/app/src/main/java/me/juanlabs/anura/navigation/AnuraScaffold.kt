package me.juanlabs.anura.navigation

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.input.nestedscroll.NestedScrollConnection
import androidx.compose.ui.input.nestedscroll.NestedScrollSource
import androidx.compose.ui.input.nestedscroll.nestedScroll
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.Velocity
import androidx.navigation.NavDestination
import androidx.navigation.NavDestination.Companion.hasRoute
import androidx.navigation.NavHostController
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import android.app.Application
import me.juanlabs.anura.AnuraApplication
import me.juanlabs.anura.core.data.DeviceReportResult
import me.juanlabs.anura.R
import me.juanlabs.anura.core.data.LocalAnuraRepository
import me.juanlabs.anura.core.platform.ServerConnectionStatus
import me.juanlabs.anura.designsystem.component.AnuraNavBar
import me.juanlabs.anura.designsystem.component.AnuraNavBarItem
import me.juanlabs.anura.designsystem.component.AnuraNavBarStackHeight
import me.juanlabs.anura.designsystem.component.LocalAnuraTabBarInset
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.theme.AnuraAccentRole
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraMotion
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode
import me.juanlabs.anura.designsystem.theme.rememberReduceMotion

// Mismo orden que la web (frontend/src/components/Navbar.jsx): Inicio · Explorar · Listado · Ajustes.
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
    // Reporte del dispositivo (C4) y avisos (C5): al abrir la app con sesión iniciada y tras
    // cada login (authToken cambia). Si el servidor dice que la cuenta está suspendida, cierra
    // la sesión aquí mismo — es la única pantalla que ve cada navegación de la app.
    val deviceSuspendedMessage = stringResource(R.string.device_suspended_message)
    val deviceBlockedFallback = stringResource(R.string.device_blocked_message)
    LaunchedEffect(snapshot.session.authToken, snapshot.session.enteredApp) {
        val token = snapshot.session.authToken
        if (token != null && me.juanlabs.anura.core.auth.isJwtExpired(token)) {
            repository.noteSessionRejected()
            return@LaunchedEffect
        }
        if (token == null || !snapshot.session.enteredApp) return@LaunchedEffect
        when (val report = repository.reportDevice(context.applicationContext as Application)) {
            is DeviceReportResult.Suspended -> {
                repository.signOut()
                repository.notify(deviceSuspendedMessage)
                navController.navigate(AnuraRoute.AuthGraph) {
                    popUpTo(0) { inclusive = true }
                }
                return@LaunchedEffect
            }
            is DeviceReportResult.Ok -> {
                val blockedNow = repository.snapshot.deviceBlocked
                if (blockedNow) {
                    repository.notify(repository.snapshot.deviceBlockReason?.takeIf { it.isNotBlank() } ?: deviceBlockedFallback)
                }
                repository.hydrateNotifications(context)
                if (!blockedNow) {
                    repository.syncPendingObservations()
                    repository.hydrateOwnObservations()
                    if (report.sincronizar) repository.ackDeviceSync()
                }
            }
            DeviceReportResult.Unauthorized -> Unit
            DeviceReportResult.Failed -> {
                repository.hydrateNotifications(context)
                if (!repository.snapshot.deviceBlocked) {
                    repository.syncPendingObservations()
                    repository.hydrateOwnObservations()
                }
            }
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
    val reduceMotion = rememberReduceMotion()
    var navBarVisible by remember { mutableStateOf(true) }
    LaunchedEffect(selectedTabIndex, showTabChrome) {
        navBarVisible = true
    }
    val nestedScrollConnection = remember {
        object : NestedScrollConnection {
            override fun onPreScroll(available: Offset, source: NestedScrollSource): Offset {
                when {
                    available.y < -8f -> navBarVisible = false
                    available.y > 8f -> navBarVisible = true
                }
                return Offset.Zero
            }

            override suspend fun onPreFling(available: Velocity): Velocity {
                when {
                    available.y < -400f -> navBarVisible = false
                    available.y > 400f -> navBarVisible = true
                }
                return Velocity.Zero
            }
        }
    }

    CompositionLocalProvider(LocalAnuraRepository provides repository) {
        Scaffold(
            containerColor = AnuraTheme.extendedColors.boardBackground,
            contentWindowInsets = WindowInsets(0, 0, 0, 0),
            snackbarHost = { SnackbarHost(hostState = snackbarHostState) },
        ) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .nestedScroll(nestedScrollConnection),
            ) {
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
                    AnimatedVisibility(
                        visible = navBarVisible,
                        modifier = Modifier.align(Alignment.BottomCenter),
                        enter = if (reduceMotion) {
                            androidx.compose.animation.EnterTransition.None
                        } else {
                            slideInVertically(
                                animationSpec = tween(AnuraMotion.DurationShort),
                                initialOffsetY = { it },
                            )
                        },
                        exit = if (reduceMotion) {
                            androidx.compose.animation.ExitTransition.None
                        } else {
                            slideOutVertically(
                                animationSpec = tween(AnuraMotion.DurationShort),
                                targetOffsetY = { it },
                            )
                        },
                    ) {
                        AnuraNavBar(
                            items = TopLevelItems,
                            selectedIndex = tabIndex,
                            onItemSelected = { index ->
                                navBarVisible = true
                                navController.navigateToTab(TOP_LEVEL_ROUTES[index])
                            },
                            onFabClick = { navController.navigate(AnuraRoute.WhatToRegister) },
                        )
                    }
                }
                ConnectionIndicator(
                    modifier = Modifier
                        .align(Alignment.BottomEnd)
                        .navigationBarsPadding()
                        .padding(
                            end = AnuraDimens.spaceGutter,
                            bottom = (if (showTabChrome) AnuraNavBarStackHeight else 0.dp) + AnuraDimens.spaceGap,
                        ),
                )
                if (showTabChrome) {
                    NotificationBell(
                        unreadCount = snapshot.unreadNotifications,
                        onClick = { navController.navigate(AnuraRoute.Notifications) },
                        modifier = Modifier
                            .align(Alignment.TopEnd)
                            .statusBarsPadding()
                            .padding(end = AnuraDimens.spaceGutter - 4.dp),
                    )
                }
            }
        }
    }
}

/**
 * Campana con los avisos propios (C5) — arriba de toda pantalla top-level, sutil como
 * [ConnectionIndicator] pero con badge: no forma parte del `Mockup Final` de Penpot (igual que
 * [me.juanlabs.anura.feature.notifications.NotificationsScreen], ya fuera del inventario cerrado
 * de rutas), así que vive flotando en el scaffold en vez de forzarla dentro de cada header ya
 * diagramado (`home`, `explorar`, `Fotos y observaciones`).
 */
@Composable
private fun NotificationBell(unreadCount: Int, onClick: () -> Unit, modifier: Modifier = Modifier) {
    Box(modifier = modifier) {
        IconButton(onClick = onClick, modifier = Modifier.size(AnuraDimens.sizeTouch)) {
            Icon(
                imageVector = AnuraIcons.Notifications,
                contentDescription = stringResource(R.string.notifications_title),
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        if (unreadCount > 0) {
            Box(
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .padding(top = 6.dp, end = 6.dp)
                    .clip(CircleShape)
                    .background(MaterialTheme.colorScheme.error)
                    .padding(horizontal = 5.dp, vertical = 1.dp),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = if (unreadCount > 9) "9+" else unreadCount.toString(),
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onError,
                )
            }
        }
    }
}

/**
 * Nubecita sutil (16dp, esquina inferior, encima de la píldora de navegación) con si el
 * servidor de ANURA respondió o no a la última llamada real ([ServerConnectionStatus],
 * actualizado por [me.juanlabs.anura.core.data.AnuraApi]). Distinto de "el teléfono tiene
 * internet" — es "el servidor de ANURA responde", lo que de verdad le importa al usuario.
 * No aparece hasta que se intenta la primera llamada (evita un parpadeo falso al abrir la app).
 */
@Composable
private fun ConnectionIndicator(modifier: Modifier = Modifier) {
    val connected by ServerConnectionStatus.connected.collectAsState()
    val isConnected = connected ?: return
    Icon(
        imageVector = if (isConnected) AnuraIcons.Cloud else AnuraIcons.CloudOff,
        contentDescription = stringResource(
            if (isConnected) R.string.connection_status_online_cd else R.string.connection_status_offline_cd,
        ),
        tint = if (isConnected) {
            MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.45f)
        } else {
            AnuraTheme.extendedColors.warning
        },
        modifier = modifier.size(16.dp),
    )
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
