package me.juanlabs.anura.navigation

import androidx.compose.animation.EnterTransition
import androidx.compose.animation.ExitTransition
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.window.DialogProperties
import androidx.navigation.NavDestination.Companion.hasRoute
import androidx.navigation.NavGraphBuilder
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.dialog
import androidx.navigation.compose.navigation
import androidx.navigation.toRoute
import me.juanlabs.anura.core.data.AnuraRepository
import me.juanlabs.anura.core.data.IdentificationKnown
import me.juanlabs.anura.core.data.IdentificationUnknownFamily
import me.juanlabs.anura.core.data.IdentificationUnknownGenus
import me.juanlabs.anura.core.data.IdentificationUnknownOrder
import me.juanlabs.anura.core.data.IdentificationCandidate
import me.juanlabs.anura.feature.capture.OpenSetReachedRank
import me.juanlabs.anura.feature.capture.OpenSetUnknownResults
import me.juanlabs.anura.core.data.rememberAnuraRepository
import me.juanlabs.anura.designsystem.theme.AnuraMotion
import me.juanlabs.anura.designsystem.theme.AnuraAccentRole
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode
import me.juanlabs.anura.designsystem.theme.rememberReduceMotion
import me.juanlabs.anura.feature.auth.SignInScreen
import me.juanlabs.anura.feature.auth.SignUpScreen
import me.juanlabs.anura.feature.auth.WelcomeScreen
import me.juanlabs.anura.feature.capture.AnalyzingScreen
import me.juanlabs.anura.feature.capture.AudioCaptureScreen
import me.juanlabs.anura.feature.capture.CapturePhotoDraft
import me.juanlabs.anura.feature.capture.CaptureStep1Screen
import me.juanlabs.anura.feature.capture.CaptureStep2Screen
import me.juanlabs.anura.feature.capture.CaptureStep3Screen
import me.juanlabs.anura.feature.capture.CaptureStep4Screen
import me.juanlabs.anura.feature.capture.CaptureStep5Screen
import me.juanlabs.anura.feature.capture.CaptureStep6Screen
import me.juanlabs.anura.feature.capture.PhotoCaptureScreen
import me.juanlabs.anura.core.inference.IdentificationFailure
import me.juanlabs.anura.feature.capture.MockOpenSetUnknownResults
import me.juanlabs.anura.feature.capture.UnknownResultScreen
import me.juanlabs.anura.feature.capture.WhatToRegisterContent
import me.juanlabs.anura.feature.comments.CommentsScreen
import me.juanlabs.anura.feature.explore.ExploreMoreScreen
import me.juanlabs.anura.feature.explore.ExploreScreen
import me.juanlabs.anura.feature.explore.SpeciesByTaxonScreen
import me.juanlabs.anura.feature.fieldsession.FieldSessionNotesScreen
import me.juanlabs.anura.feature.fieldsession.FieldSessionScreen
import me.juanlabs.anura.feature.fieldsession.NightSoundsScreen
import me.juanlabs.anura.feature.home.HomeCarouselCatalog
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
    themeMode: AnuraThemeMode = AnuraThemeMode.Sistema,
    onThemeModeChange: (AnuraThemeMode) -> Unit = {},
    accentRole: AnuraAccentRole = AnuraAccentRole.Ink,
    onAccentRoleChange: (AnuraAccentRole) -> Unit = {},
    preferReduceMotion: Boolean = false,
    onPreferReduceMotionChange: (Boolean) -> Unit = {},
    preferLargeText: Boolean = false,
    onPreferLargeTextChange: (Boolean) -> Unit = {},
    activeSessionId: String? = null,
    onFieldSessionActivated: (String) -> Unit = {},
    onFieldSessionClosed: () -> Unit = {},
) {
    val reduceMotion = rememberReduceMotion()
    val enter = {
        if (reduceMotion) EnterTransition.None else fadeIn(tween(AnuraMotion.DurationMedium))
    }
    val exit = {
        if (reduceMotion) ExitTransition.None else fadeOut(tween(AnuraMotion.DurationMedium))
    }
    NavHost(
        navController = navController,
        startDestination = AnuraRoute.AuthGraph,
        modifier = modifier,
        enterTransition = { enter() },
        exitTransition = { exit() },
        popEnterTransition = { enter() },
        popExitTransition = { exit() },
    ) {
        authGraph(navController)
        topLevelDestinations(
            navController,
            themeMode,
            onThemeModeChange,
            accentRole,
            onAccentRoleChange,
            preferReduceMotion,
            onPreferReduceMotionChange,
            preferLargeText,
            onPreferLargeTextChange,
            activeSessionId,
        )
        detailDestinations(
            navController,
            onFieldSessionActivated,
            onFieldSessionClosed,
        )
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
            val repository = rememberAnuraRepository()
            val needEmail = stringResource(me.juanlabs.anura.R.string.auth_forgot_password_need_email)
            val sent = stringResource(me.juanlabs.anura.R.string.auth_forgot_password_sent)
            SignInScreen(
                onBackClick = { navController.popBackStack() },
                onSignedIn = { email ->
                    repository.signIn(email)
                    navController.navigate(AnuraRoute.Home) {
                        popUpTo(AnuraRoute.AuthGraph) { inclusive = true }
                    }
                },
                onGoToSignUp = { navController.navigate(AnuraRoute.SignUp) },
                onContinueWithoutAccount = {
                    repository.enterGuest()
                    navController.navigate(AnuraRoute.Home) {
                        popUpTo(AnuraRoute.AuthGraph) { inclusive = true }
                    }
                },
                onForgotPassword = { email ->
                    repository.notify(if (email.isBlank()) needEmail else sent)
                },
            )
        }
        composable<AnuraRoute.SignUp> {
            val repository = rememberAnuraRepository()
            SignUpScreen(
                onBackClick = { navController.popBackStack() },
                onSignedUp = { name, email, usage ->
                    repository.signUp(name, email, usage)
                    navController.navigate(AnuraRoute.Home) {
                        popUpTo(AnuraRoute.AuthGraph) { inclusive = true }
                    }
                },
                onGoToSignIn = { navController.navigate(AnuraRoute.SignIn) },
                onContinueWithoutAccount = {
                    repository.enterGuest()
                    navController.navigate(AnuraRoute.Home) {
                        popUpTo(AnuraRoute.AuthGraph) { inclusive = true }
                    }
                },
            )
        }
    }
}

private fun NavGraphBuilder.topLevelDestinations(
    navController: NavHostController,
    themeMode: AnuraThemeMode,
    onThemeModeChange: (AnuraThemeMode) -> Unit,
    accentRole: AnuraAccentRole,
    onAccentRoleChange: (AnuraAccentRole) -> Unit,
    preferReduceMotion: Boolean,
    onPreferReduceMotionChange: (Boolean) -> Unit,
    preferLargeText: Boolean,
    onPreferLargeTextChange: (Boolean) -> Unit,
    activeSessionId: String?,
) {
    composable<AnuraRoute.Home> {
        val repository = rememberAnuraRepository()
        HomeScreen(
            onOpenProfile = { navController.navigate(AnuraRoute.Profile(userId = null)) },
            onOpenSpeciesSheet = { speciesId -> navController.navigate(AnuraRoute.SpeciesSheet(speciesId)) },
            onOpenFieldSession = { sessionId -> navController.navigate(AnuraRoute.FieldSession(sessionId)) },
            onPhotoId = {
                repository.beginWizard()
                navController.navigate(AnuraRoute.PhotoCapture)
            },
            onAudioId = {
                repository.beginWizard()
                navController.navigate(AnuraRoute.AudioCapture)
            },
            onStepByStep = {
                repository.beginWizard()
                navController.navigate(AnuraRoute.CaptureGraph)
            },
            activeFieldSession = activeSessionId?.let { id ->
                val session = repository.snapshot.fieldSessions.find { it.id == id }
                val registers = repository.ownObservations().count { it.fieldSessionId == id }
                me.juanlabs.anura.feature.home.HomeActiveFieldSession(
                    sessionId = id,
                    placeName = session?.placeLabel
                        ?: session?.let { me.juanlabs.anura.core.data.formatCoordinates(it.latitude, it.longitude) }
                        ?: "",
                    elapsedLabel = session?.let {
                        me.juanlabs.anura.core.data.formatElapsedShort(it.startedAtEpochMs)
                    } ?: "",
                    registerCount = registers,
                ).takeUnless { it.placeName.isEmpty() && it.elapsedLabel.isEmpty() }
                    ?: me.juanlabs.anura.feature.home.HomeActiveFieldSession(
                        sessionId = id,
                        placeName = "",
                        elapsedLabel = session?.let {
                            me.juanlabs.anura.core.data.formatElapsedShort(it.startedAtEpochMs)
                        } ?: "",
                        registerCount = registers,
                    )
            },
        )
    }
    composable<AnuraRoute.Explore> {
        ExploreScreen(
            onOpenObservationDetail = { id -> navController.navigate(AnuraRoute.ObservationDetail(id)) },
            onOpenExploreMore = { navController.navigate(AnuraRoute.ExploreMore) },
        )
    }
    composable<AnuraRoute.Observations> {
        ObservationsScreen(
            onOpenObservationDetail = { id -> navController.navigate(AnuraRoute.ObservationDetail(id)) },
            onOpenFavorites = { navController.navigate(AnuraRoute.Favorites) },
        )
    }
    composable<AnuraRoute.Settings> {
        val repository = rememberAnuraRepository()
        SettingsScreen(
            themeMode = themeMode,
            onThemeModeChange = onThemeModeChange,
            accentRole = accentRole,
            onAccentRoleChange = onAccentRoleChange,
            preferReduceMotion = preferReduceMotion,
            onPreferReduceMotionChange = onPreferReduceMotionChange,
            preferLargeText = preferLargeText,
            onPreferLargeTextChange = onPreferLargeTextChange,
            onOpenRegionalPackages = { navController.navigate(AnuraRoute.RegionalPackages) },
            onOpenProfile = { navController.navigate(AnuraRoute.Profile(userId = null)) },
            onOpenEditProfile = { navController.navigate(AnuraRoute.EditProfile) },
            onSignOut = {
                repository.signOut()
                navController.navigate(AnuraRoute.AuthGraph) {
                    popUpTo(AnuraRoute.Home) { inclusive = true }
                }
            },
        )
    }
}

private fun NavGraphBuilder.detailDestinations(
    navController: NavHostController,
    onFieldSessionActivated: (String) -> Unit,
    onFieldSessionClosed: () -> Unit,
) {
    composable<AnuraRoute.ObservationDetail> { backStackEntry ->
        val route = backStackEntry.toRoute<AnuraRoute.ObservationDetail>()
        ObservationDetailScreen(
            id = route.id,
            onBackClick = { navController.popBackStack() },
            onOpenSpeciesSheet = { speciesId -> navController.navigate(AnuraRoute.SpeciesSheet(speciesId)) },
            onOpenProfile = { userId -> navController.navigate(AnuraRoute.Profile(userId = userId)) },
        )
    }
        composable<AnuraRoute.SpeciesSheet> { backStackEntry ->
            val route = backStackEntry.toRoute<AnuraRoute.SpeciesSheet>()
            SpeciesSheetScreen(
                speciesId = route.speciesId,
                onBackClick = { navController.popBackStack() },
                onOpenTaxon = { taxonId -> navController.navigate(AnuraRoute.SpeciesSheet(taxonId)) },
                onOpenSpeciesSheet = { id -> navController.navigate(AnuraRoute.SpeciesSheet(id)) },
                onOpenSpeciesByTaxon = { taxonId ->
                    navController.navigate(AnuraRoute.SpeciesByTaxon(taxonId))
                },
                onOpenProfile = { userId -> navController.navigate(AnuraRoute.Profile(userId)) },
            )
        }
    composable<AnuraRoute.Profile> { backStackEntry ->
        val route = backStackEntry.toRoute<AnuraRoute.Profile>()
        ProfileScreen(
            userId = route.userId,
            onBackClick = { navController.popBackStack() },
            onOpenEditProfile = { navController.navigate(AnuraRoute.EditProfile) },
            onOpenConnections = { userId, tab ->
                navController.navigate(AnuraRoute.Connections(userId = userId, tab = tab))
            },
            onOpenOtherProfile = { userId -> navController.navigate(AnuraRoute.Profile(userId)) },
            onOpenObservationDetail = { id -> navController.navigate(AnuraRoute.ObservationDetail(id)) },
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
            initialTab = route.tab,
            onBackClick = { navController.popBackStack() },
            onOpenProfile = { userId -> navController.navigate(AnuraRoute.Profile(userId)) },
            onOpenObservationDetail = { id -> navController.navigate(AnuraRoute.ObservationDetail(id)) },
        )
    }
    composable<AnuraRoute.ExploreMore> {
        ExploreMoreScreen(
            onBackClick = { navController.popBackStack() },
            onOpenObservationDetail = { id -> navController.navigate(AnuraRoute.ObservationDetail(id)) },
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
        val repository = rememberAnuraRepository()
        FieldSessionScreen(
            sessionId = route.sessionId,
            onBackClick = { navController.popBackStack() },
            onOpenNightSounds = { sessionId -> navController.navigate(AnuraRoute.NightSounds(sessionId)) },
            onOpenNotes = { sessionId -> navController.navigate(AnuraRoute.FieldSessionNotes(sessionId)) },
            onPhotoId = {
                repository.beginWizard()
                navController.navigate(AnuraRoute.PhotoCapture)
            },
            onAudioId = {
                repository.beginWizard()
                navController.navigate(AnuraRoute.AudioCapture)
            },
            onStepByStep = {
                repository.beginWizard()
                navController.navigate(AnuraRoute.CaptureGraph)
            },
            onOpenRegister = { observationId ->
                navController.navigate(AnuraRoute.ObservationDetail(observationId))
            },
            onCloseSession = {
                onFieldSessionClosed()
                navController.popBackStack()
            },
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
        RegionalPackagesScreen(
            onBackClick = { navController.popBackStack() },
            onOpenObservationDetail = { id ->
                navController.navigate(AnuraRoute.ObservationDetail(id))
            },
        )
    }

    // "Pop-up del botón +": alcanzable desde varias pantallas -> destino de
    // navegación propio (§4.2), presentado como diálogo para que la pantalla de
    // origen quede visible detrás, igual que un bottom sheet real.
    dialog<AnuraRoute.WhatToRegister>(
        dialogProperties = DialogProperties(
            usePlatformDefaultWidth = false,
            decorFitsSystemWindows = false,
        ),
    ) {
        val repository = rememberAnuraRepository()
        val snapshot by repository.state.collectAsState()
        WhatToRegisterContent(
            hasActiveSession = snapshot.activeSessionId != null,
            onStartFieldSession = {
                val id = repository.startFieldSession()
                navController.navigate(AnuraRoute.FieldSession(sessionId = id)) {
                    popUpTo(AnuraRoute.WhatToRegister) { inclusive = true }
                }
            },
            onContinueFieldSession = {
                val id = repository.snapshot.activeSessionId ?: return@WhatToRegisterContent
                navController.navigate(AnuraRoute.FieldSession(sessionId = id)) {
                    popUpTo(AnuraRoute.WhatToRegister) { inclusive = true }
                }
            },
            onTakeQuickSample = {
                repository.beginWizard()
                navController.navigate(AnuraRoute.PhotoCapture) {
                    popUpTo(AnuraRoute.WhatToRegister) { inclusive = true }
                }
            },
            onRecordSound = {
                repository.beginWizard()
                navController.navigate(AnuraRoute.AudioCapture) {
                    popUpTo(AnuraRoute.WhatToRegister) { inclusive = true }
                }
            },
            onDismiss = { navController.popBackStack() },
        )
    }
}

private fun NavGraphBuilder.captureGraph(navController: NavHostController) {
    navigation<AnuraRoute.CaptureGraph>(startDestination = AnuraRoute.CaptureStep1) {
        composable<AnuraRoute.CaptureStep1> {
            val fromReview = navController.isEditingCaptureReview()
            CaptureStep1Screen(
                onBackClick = { navController.leaveCaptureStep(fromReview) },
                onNext = { navController.navigate(AnuraRoute.CaptureStep2) },
                onSkip = { navController.navigate(AnuraRoute.CaptureStep2) },
                fromReview = fromReview,
                onSave = { navController.returnToCaptureReview() },
                onCancel = { navController.returnToCaptureReview() },
                onCloseClick = { navController.closeCaptureWizard() },
            )
        }
        composable<AnuraRoute.CaptureStep2> {
            val fromReview = navController.isEditingCaptureReview()
            CaptureStep2Screen(
                onBackClick = { navController.leaveCaptureStep(fromReview) },
                onNext = { navController.navigate(AnuraRoute.CaptureStep3) },
                onSkip = { navController.navigate(AnuraRoute.CaptureStep3) },
                fromReview = fromReview,
                onSave = { navController.returnToCaptureReview() },
                onCancel = { navController.returnToCaptureReview() },
                onCloseClick = { navController.closeCaptureWizard() },
            )
        }
        composable<AnuraRoute.CaptureStep3> {
            val fromReview = navController.isEditingCaptureReview()
            CaptureStep3Screen(
                onBackClick = { navController.leaveCaptureStep(fromReview) },
                onNext = { navController.navigate(AnuraRoute.CaptureStep4) },
                onSkip = { navController.navigate(AnuraRoute.CaptureStep4) },
                fromReview = fromReview,
                onSave = { navController.returnToCaptureReview() },
                onCancel = { navController.returnToCaptureReview() },
                onCloseClick = { navController.closeCaptureWizard() },
            )
        }
        composable<AnuraRoute.CaptureStep4> {
            val fromReview = navController.isEditingCaptureReview()
            CaptureStep4Screen(
                onBackClick = { navController.leaveCaptureStep(fromReview) },
                onNext = { navController.navigate(AnuraRoute.CaptureStep5) },
                fromReview = fromReview,
                onSave = { navController.returnToCaptureReview() },
                onCloseClick = { navController.closeCaptureWizard() },
            )
        }
        composable<AnuraRoute.CaptureStep5> {
            val fromReview = navController.isEditingCaptureReview()
            CaptureStep5Screen(
                onBackClick = { navController.leaveCaptureStep(fromReview) },
                onNext = { navController.navigate(AnuraRoute.CaptureStep6) },
                onSkip = { navController.navigate(AnuraRoute.CaptureStep6) },
                fromReview = fromReview,
                onSave = { navController.returnToCaptureReview() },
                onCancel = { navController.returnToCaptureReview() },
                onCloseClick = { navController.closeCaptureWizard() },
            )
        }
        composable<AnuraRoute.CaptureStep6> {
            CaptureStep6Screen(
                onBackClick = { navController.popBackStack() },
                onAnalyze = { navController.navigate(AnuraRoute.Analyzing()) },
                onEditWhere = { navController.navigate(AnuraRoute.CaptureStep1) },
                onEditWhen = { navController.navigate(AnuraRoute.CaptureStep2) },
                onEditSize = { navController.navigate(AnuraRoute.CaptureStep3) },
                onEditPhotos = { navController.navigate(AnuraRoute.CaptureStep4) },
                onEditAudio = { navController.navigate(AnuraRoute.CaptureStep5) },
                onCloseClick = { navController.closeCaptureWizard() },
            )
        }
        composable<AnuraRoute.PhotoCapture> {
            val repository = rememberAnuraRepository()
            val requestLocation = me.juanlabs.anura.designsystem.component.rememberRequestLocationOnce()
            var showLocationPrompt by remember { mutableStateOf(false) }
            fun goToAnalyzing() {
                navController.navigate(AnuraRoute.Analyzing(AnuraRoute.Analyzing.Image)) {
                    popUpTo(AnuraRoute.PhotoCapture) { inclusive = true }
                }
            }
            PhotoCaptureScreen(
                onBackClick = { navController.popBackStack() },
                onPhotoAccepted = { showLocationPrompt = true },
                onCloseClick = { navController.closeCaptureWizard() },
            )
            if (showLocationPrompt) {
                me.juanlabs.anura.feature.capture.CaptureConfirmSheet(
                    title = stringResource(me.juanlabs.anura.R.string.photo_id_location_prompt_title),
                    body = stringResource(me.juanlabs.anura.R.string.photo_id_location_prompt_body),
                    confirmLabel = stringResource(me.juanlabs.anura.R.string.photo_id_location_prompt_confirm),
                    dismissLabel = stringResource(me.juanlabs.anura.R.string.photo_id_location_prompt_dismiss),
                    onConfirm = {
                        showLocationPrompt = false
                        requestLocation { location ->
                            if (location != null) {
                                repository.updateDraft { it.copy(latitude = location.latitude, longitude = location.longitude) }
                            }
                            goToAnalyzing()
                        }
                    },
                    onDismiss = {
                        showLocationPrompt = false
                        goToAnalyzing()
                    },
                )
            }
        }
        composable<AnuraRoute.AudioCapture> {
            AudioCaptureScreen(
                onBackClick = { navController.popBackStack() },
                onAnalyze = {
                    navController.navigate(AnuraRoute.Analyzing(AnuraRoute.Analyzing.Audio)) {
                        popUpTo(AnuraRoute.AudioCapture) { inclusive = true }
                    }
                },
                onCloseClick = { navController.closeCaptureWizard() },
            )
        }
        composable<AnuraRoute.Analyzing> { backStackEntry ->
            val route = backStackEntry.toRoute<AnuraRoute.Analyzing>()
            val repository = rememberAnuraRepository()
            val context = androidx.compose.ui.platform.LocalContext.current
            AnalyzingScreen(
                source = route.source,
                identifyPhoto = if (route.source != AnuraRoute.Analyzing.Audio) {
                    { repository.identifyDraftPhoto() }
                } else {
                    null
                },
                onIdentified = { outcome ->
                    if (outcome.accepted) {
                        val id = repository.commitObservation(IdentificationKnown, outcome)
                        navController.navigate(AnuraRoute.ObservationDetail(id = id)) {
                            popUpTo(AnuraRoute.CaptureGraph) { inclusive = true }
                        }
                    } else {
                        val candidates = outcome.candidates.map {
                            IdentificationCandidate(it.scientificName, it.share.toFloat(), it.genus, it.family)
                        }
                        val reached = OpenSetUnknownResults.reachedRank(candidates)
                        val status = when (reached) {
                            OpenSetReachedRank.Genus -> IdentificationUnknownGenus
                            OpenSetReachedRank.Family -> IdentificationUnknownFamily
                            OpenSetReachedRank.Order -> IdentificationUnknownOrder
                        }
                        val id = repository.commitObservation(status, outcome)
                        navController.navigate(AnuraRoute.UnknownResult(reached.name.lowercase(), observationId = id)) {
                            popUpTo(AnuraRoute.CaptureGraph) { inclusive = true }
                        }
                    }
                },
                onNotAnuro = { navController.popBackStack() },
                onIdentificationFailed = { reason ->
                    repository.notify(
                        context.getString(
                            when (reason) {
                                IdentificationFailure.NoPhoto -> me.juanlabs.anura.R.string.identification_error_no_photo
                                IdentificationFailure.NoActivePackage -> me.juanlabs.anura.R.string.identification_error_no_package
                                IdentificationFailure.EngineError -> me.juanlabs.anura.R.string.identification_error_engine
                            },
                        ),
                    )
                    navController.popBackStack()
                },
                onKnownResult = {
                    val id = repository.commitObservation(IdentificationKnown)
                    navController.navigate(AnuraRoute.ObservationDetail(id = id)) {
                        popUpTo(AnuraRoute.CaptureGraph) { inclusive = true }
                    }
                },
                onUnknownResult = { reached ->
                    val status = if (reached == "family") {
                        IdentificationUnknownFamily
                    } else {
                        IdentificationUnknownGenus
                    }
                    repository.commitObservation(status)
                    navController.navigate(AnuraRoute.UnknownResult(reached)) {
                        popUpTo(AnuraRoute.CaptureGraph) { inclusive = true }
                    }
                },
            )
        }
        composable<AnuraRoute.UnknownResult> { backStackEntry ->
            val resultRoute = backStackEntry.toRoute<AnuraRoute.UnknownResult>()
            val repository = rememberAnuraRepository()
            val reviewSent = stringResource(me.juanlabs.anura.R.string.expert_review_sent)
            val observation = resultRoute.observationId?.let(repository::observationById)
            val result = observation?.takeIf { it.candidates.isNotEmpty() }
                ?.let { OpenSetUnknownResults.fromCandidates(it.candidates, it.photoTokens.firstOrNull()) }
                ?: MockOpenSetUnknownResults.forReached(resultRoute.reached)
            UnknownResultScreen(
                result = result,
                onBackClick = { navController.popBackStack() },
                onOpenTaxonSheet = { taxonId ->
                    navController.navigate(AnuraRoute.SpeciesSheet(taxonId))
                },
                onRequestExpertReview = {
                    repository.requestExpertReview(resultRoute.observationId)
                    repository.notify(reviewSent)
                },
            )
        }
    }
}

private fun NavHostController.isEditingCaptureReview(): Boolean =
    previousBackStackEntry?.destination?.hasRoute<AnuraRoute.CaptureStep6>() == true

private fun NavHostController.returnToCaptureReview() {
    if (!popBackStack(AnuraRoute.CaptureStep6, inclusive = false)) {
        popBackStack()
    }
}

private fun NavHostController.leaveCaptureStep(fromReview: Boolean) {
    if (fromReview) returnToCaptureReview() else popBackStack()
}

private fun NavHostController.closeCaptureWizard() {
    // Cancelar (botón "X" en cualquier paso/foto/audio) también debe limpiar el
    // borrador de fotos, no solo terminar con éxito (P0 #4).
    CapturePhotoDraft.reset()
    navigate(AnuraRoute.Home) {
        popUpTo(AnuraRoute.CaptureGraph) { inclusive = true }
        launchSingleTop = true
    }
}
