package me.juanlabs.anura.navigation

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavGraphBuilder
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.dialog
import androidx.navigation.compose.navigation
import androidx.navigation.toRoute
import me.juanlabs.anura.feature.auth.SignInScreen
import me.juanlabs.anura.feature.auth.SignUpScreen
import me.juanlabs.anura.feature.auth.WelcomeScreen
import me.juanlabs.anura.feature.capture.AnalyzingScreen
import me.juanlabs.anura.feature.capture.AudioCaptureScreen
import me.juanlabs.anura.feature.capture.CaptureStep1Screen
import me.juanlabs.anura.feature.capture.CaptureStep2Screen
import me.juanlabs.anura.feature.capture.CaptureStep3Screen
import me.juanlabs.anura.feature.capture.CaptureStep4Screen
import me.juanlabs.anura.feature.capture.CaptureStep5Screen
import me.juanlabs.anura.feature.capture.PhotoCaptureScreen
import me.juanlabs.anura.feature.capture.UnknownResultScreen
import me.juanlabs.anura.feature.capture.WhatToRegisterContent
import me.juanlabs.anura.feature.comments.CommentsScreen
import me.juanlabs.anura.feature.explore.ExploreScreen
import me.juanlabs.anura.feature.explore.SpeciesByTaxonScreen
import me.juanlabs.anura.feature.fieldsession.FieldSessionNotesScreen
import me.juanlabs.anura.feature.fieldsession.FieldSessionScreen
import me.juanlabs.anura.feature.fieldsession.NightSoundsScreen
import me.juanlabs.anura.feature.home.HomeScreen
import me.juanlabs.anura.feature.observations.FavoritesScreen
import me.juanlabs.anura.feature.observations.ObservationDetailScreen
import me.juanlabs.anura.feature.observations.ObservationsScreen
import me.juanlabs.anura.feature.packages.RegionalPackagesScreen
import me.juanlabs.anura.feature.profile.ConnectionsScreen
import me.juanlabs.anura.feature.profile.EditProfileScreen
import me.juanlabs.anura.feature.profile.ProfileScreen
import me.juanlabs.anura.feature.settings.SettingsScreen
import me.juanlabs.anura.feature.species.SpeciesSheetScreen

/**
 * Grafo de navegación completo de ANURA (§4). Cada `composable<Ruta>`/`navigation<Ruta>`
 * corresponde 1:1 a una fila de la tabla §4.1 — cerrado contra esa lista, no se agregan
 * destinos fuera de [AnuraRoute].
 *
 * El grafo arranca en `AuthGraph` (Bienvenida): Penpot dibuja ese flujo primero, y
 * `Welcome` es quien ofrece "continuar sin cuenta" (decisión 6/7) — la app no se salta
 * la pantalla, solo garantiza que de ahí en adelante funciona sin cuenta.
 */
@Composable
fun AnuraNavHost(
    navController: NavHostController,
    modifier: Modifier = Modifier,
) {
    NavHost(
        navController = navController,
        startDestination = AnuraRoute.AuthGraph,
        modifier = modifier,
    ) {
        authGraph(navController)
        topLevelDestinations(navController)
        detailDestinations(navController)
        captureGraph(navController)
    }
}

private fun NavGraphBuilder.authGraph(navController: NavHostController) {
    navigation<AnuraRoute.AuthGraph>(startDestination = AnuraRoute.Welcome) {
        composable<AnuraRoute.Welcome> {
            WelcomeScreen(
                onGoToSignIn = { navController.navigate(AnuraRoute.SignIn) },
                onGoToSignUp = { navController.navigate(AnuraRoute.SignUp) },
            )
        }
        composable<AnuraRoute.SignIn> {
            SignInScreen(
                onBackClick = { navController.popBackStack() },
                onSignedIn = {
                    navController.navigate(AnuraRoute.Home) {
                        popUpTo(AnuraRoute.AuthGraph) { inclusive = true }
                    }
                },
                onGoToSignUp = { navController.navigate(AnuraRoute.SignUp) },
                onContinueWithoutAccount = {
                    navController.navigate(AnuraRoute.Home) {
                        popUpTo(AnuraRoute.AuthGraph) { inclusive = true }
                    }
                },
            )
        }
        composable<AnuraRoute.SignUp> {
            SignUpScreen(
                onBackClick = { navController.popBackStack() },
                onSignedUp = {
                    navController.navigate(AnuraRoute.Home) {
                        popUpTo(AnuraRoute.AuthGraph) { inclusive = true }
                    }
                },
                onGoToSignIn = { navController.navigate(AnuraRoute.SignIn) },
                onContinueWithoutAccount = {
                    navController.navigate(AnuraRoute.Home) {
                        popUpTo(AnuraRoute.AuthGraph) { inclusive = true }
                    }
                },
            )
        }
    }
}

private fun NavGraphBuilder.topLevelDestinations(navController: NavHostController) {
    composable<AnuraRoute.Home> {
        HomeScreen(
            onOpenProfile = { navController.navigate(AnuraRoute.Profile(userId = null)) },
            onOpenSpeciesSheet = { speciesId -> navController.navigate(AnuraRoute.SpeciesSheet(speciesId)) },
            onOpenFieldSession = { sessionId -> navController.navigate(AnuraRoute.FieldSession(sessionId)) },
            onPhotoId = { navController.navigate(AnuraRoute.PhotoCapture) },
            onAudioId = { navController.navigate(AnuraRoute.AudioCapture) },
            onStepByStep = { navController.navigate(AnuraRoute.CaptureGraph) },
        )
    }
    composable<AnuraRoute.Explore> {
        ExploreScreen(
            onOpenSpeciesByTaxon = { taxonId -> navController.navigate(AnuraRoute.SpeciesByTaxon(taxonId)) },
            onOpenSpeciesSheet = { speciesId -> navController.navigate(AnuraRoute.SpeciesSheet(speciesId)) },
        )
    }
    composable<AnuraRoute.Observations> {
        ObservationsScreen(
            onOpenObservationDetail = { id -> navController.navigate(AnuraRoute.ObservationDetail(id)) },
            onOpenFavorites = { navController.navigate(AnuraRoute.Favorites) },
        )
    }
    composable<AnuraRoute.Settings> {
        SettingsScreen(
            onOpenRegionalPackages = { navController.navigate(AnuraRoute.RegionalPackages) },
            onOpenProfile = { navController.navigate(AnuraRoute.Profile(userId = null)) },
        )
    }
}

private fun NavGraphBuilder.detailDestinations(navController: NavHostController) {
    composable<AnuraRoute.ObservationDetail> { backStackEntry ->
        val route = backStackEntry.toRoute<AnuraRoute.ObservationDetail>()
        ObservationDetailScreen(
            id = route.id,
            onBackClick = { navController.popBackStack() },
            onOpenComments = { observationId -> navController.navigate(AnuraRoute.Comments(observationId)) },
            onOpenSpeciesSheet = { speciesId -> navController.navigate(AnuraRoute.SpeciesSheet(speciesId)) },
        )
    }
    composable<AnuraRoute.SpeciesSheet> { backStackEntry ->
        val route = backStackEntry.toRoute<AnuraRoute.SpeciesSheet>()
        SpeciesSheetScreen(speciesId = route.speciesId, onBackClick = { navController.popBackStack() })
    }
    composable<AnuraRoute.Profile> { backStackEntry ->
        val route = backStackEntry.toRoute<AnuraRoute.Profile>()
        ProfileScreen(
            userId = route.userId,
            onBackClick = { navController.popBackStack() },
            onOpenEditProfile = { navController.navigate(AnuraRoute.EditProfile) },
            onOpenConnections = { userId -> navController.navigate(AnuraRoute.Connections(userId)) },
            onOpenOtherProfile = { userId -> navController.navigate(AnuraRoute.Profile(userId)) },
        )
    }
    composable<AnuraRoute.Comments> { backStackEntry ->
        val route = backStackEntry.toRoute<AnuraRoute.Comments>()
        CommentsScreen(observationId = route.observationId, onBackClick = { navController.popBackStack() })
    }
    composable<AnuraRoute.Connections> { backStackEntry ->
        val route = backStackEntry.toRoute<AnuraRoute.Connections>()
        ConnectionsScreen(
            userId = route.userId,
            onBackClick = { navController.popBackStack() },
            onOpenProfile = { userId -> navController.navigate(AnuraRoute.Profile(userId)) },
        )
    }
    composable<AnuraRoute.SpeciesByTaxon> { backStackEntry ->
        val route = backStackEntry.toRoute<AnuraRoute.SpeciesByTaxon>()
        SpeciesByTaxonScreen(
            taxonId = route.taxonId,
            onBackClick = { navController.popBackStack() },
            onOpenSpeciesSheet = { speciesId -> navController.navigate(AnuraRoute.SpeciesSheet(speciesId)) },
        )
    }
    composable<AnuraRoute.FieldSession> { backStackEntry ->
        val route = backStackEntry.toRoute<AnuraRoute.FieldSession>()
        FieldSessionScreen(
            sessionId = route.sessionId,
            onBackClick = { navController.popBackStack() },
            onOpenNightSounds = { sessionId -> navController.navigate(AnuraRoute.NightSounds(sessionId)) },
            onOpenNotes = { sessionId -> navController.navigate(AnuraRoute.FieldSessionNotes(sessionId)) },
        )
    }
    composable<AnuraRoute.NightSounds> { backStackEntry ->
        val route = backStackEntry.toRoute<AnuraRoute.NightSounds>()
        NightSoundsScreen(sessionId = route.sessionId, onBackClick = { navController.popBackStack() })
    }
    composable<AnuraRoute.FieldSessionNotes> { backStackEntry ->
        val route = backStackEntry.toRoute<AnuraRoute.FieldSessionNotes>()
        FieldSessionNotesScreen(sessionId = route.sessionId, onBackClick = { navController.popBackStack() })
    }
    composable<AnuraRoute.Favorites> {
        FavoritesScreen(
            onBackClick = { navController.popBackStack() },
            onOpenObservationDetail = { id -> navController.navigate(AnuraRoute.ObservationDetail(id)) },
        )
    }
    composable<AnuraRoute.EditProfile> {
        EditProfileScreen(onBackClick = { navController.popBackStack() })
    }
    composable<AnuraRoute.RegionalPackages> {
        RegionalPackagesScreen(onBackClick = { navController.popBackStack() })
    }

    // "Pop-up del botón +": alcanzable desde varias pantallas -> destino de
    // navegación propio (§4.2), presentado como diálogo para que la pantalla de
    // origen quede visible detrás, igual que un bottom sheet real.
    dialog<AnuraRoute.WhatToRegister> {
        WhatToRegisterContent(
            onRegisterSighting = {
                navController.navigate(AnuraRoute.CaptureGraph) {
                    popUpTo(AnuraRoute.WhatToRegister) { inclusive = true }
                }
            },
            onRecordNightSound = {
                navController.navigate(AnuraRoute.AudioCapture) {
                    popUpTo(AnuraRoute.WhatToRegister) { inclusive = true }
                }
            },
            onStartFieldSession = {
                navController.navigate(AnuraRoute.FieldSession(sessionId = "session-new")) {
                    popUpTo(AnuraRoute.WhatToRegister) { inclusive = true }
                }
            },
        )
    }
}

private fun NavGraphBuilder.captureGraph(navController: NavHostController) {
    navigation<AnuraRoute.CaptureGraph>(startDestination = AnuraRoute.CaptureStep1) {
        composable<AnuraRoute.CaptureStep1> {
            CaptureStep1Screen(
                onBackClick = { navController.popBackStack() },
                onNext = { navController.navigate(AnuraRoute.CaptureStep2) },
            )
        }
        composable<AnuraRoute.CaptureStep2> {
            CaptureStep2Screen(
                onBackClick = { navController.popBackStack() },
                onNext = { navController.navigate(AnuraRoute.CaptureStep3) },
            )
        }
        composable<AnuraRoute.CaptureStep3> {
            CaptureStep3Screen(
                onBackClick = { navController.popBackStack() },
                onNext = { navController.navigate(AnuraRoute.CaptureStep4) },
            )
        }
        composable<AnuraRoute.CaptureStep4> {
            CaptureStep4Screen(
                onBackClick = { navController.popBackStack() },
                onNext = { navController.navigate(AnuraRoute.CaptureStep5) },
                onOpenPhotoCapture = { navController.navigate(AnuraRoute.PhotoCapture) },
                onOpenAudioCapture = { navController.navigate(AnuraRoute.AudioCapture) },
            )
        }
        composable<AnuraRoute.CaptureStep5> {
            CaptureStep5Screen(
                onBackClick = { navController.popBackStack() },
                onAnalyze = { navController.navigate(AnuraRoute.Analyzing) },
            )
        }
        composable<AnuraRoute.PhotoCapture> {
            PhotoCaptureScreen(onBackClick = { navController.popBackStack() })
        }
        composable<AnuraRoute.AudioCapture> {
            AudioCaptureScreen(onBackClick = { navController.popBackStack() })
        }
        composable<AnuraRoute.Analyzing> {
            AnalyzingScreen(
                onKnownResult = {
                    navController.navigate(AnuraRoute.ObservationDetail(id = "obs-nuevo")) {
                        popUpTo(AnuraRoute.CaptureGraph) { inclusive = true }
                    }
                },
                onUnknownResult = {
                    navController.navigate(AnuraRoute.UnknownResult) {
                        popUpTo(AnuraRoute.CaptureGraph) { inclusive = true }
                    }
                },
            )
        }
        composable<AnuraRoute.UnknownResult> {
            UnknownResultScreen(onBackClick = { navController.popBackStack() })
        }
    }
}
