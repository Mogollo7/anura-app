package me.juanlabs.anura.feature.home

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.indication
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.material3.ripple
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Shadow
import androidx.compose.ui.graphics.painter.Painter
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.layout.LayoutCoordinates
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.pluralStringResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import me.juanlabs.anura.R
import me.juanlabs.anura.core.data.rememberAnuraRepository
import me.juanlabs.anura.designsystem.component.AnuraLightGlass
import me.juanlabs.anura.designsystem.component.AnuraLoadingState
import me.juanlabs.anura.designsystem.component.LocalAnuraTabBarInset
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraMotion
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

private val HomeAvatarSize = 40.dp
private val HomeCarouselHorizontalInset = 28.dp
private val HomeCarouselAspect = 337f / 300f
private val HomeCarouselRadius = 20.dp
private val HomeOverlayInset = 15.dp
private val HomeDotSize = 15.dp
private val HomeDotGap = 18.dp
/** Penpot: secundarios 80, Foto ID 92×95. */
private val HomeActionSecondarySize = 80.dp
private val HomeActionPrimarySize = 92.dp
/** Grupo acciones Penpot 326×117 @ x=29. */
private val HomeActionsHorizontalInset = 29.dp
private val HomeActionsHeight = 117.dp
private val HomeHeaderToCarouselGap = 12.dp
private val HomeCarouselToDotsGap = 12.dp
private val HomeActionsToChipGap = 12.dp
/** Hueco puntos → acciones (Penpot: 495 − 429 = 66). Solo este valor baja el grupo. */
private val HomeDotsToActionsGap = 66.dp
private val HomeBottomBreathing = 8.dp

/**
 * `home` (§4.1) — top-level, tab 1. Sin flecha de volver: es raíz de pestaña.
 * Navbar / FAB viven en [me.juanlabs.anura.navigation.AnuraScaffold], no aquí.
 *
 * Estados: [HomeUiState.Loading] · [HomeUiState.Content] (con o sin salida de campo).
 */
@Composable
fun HomeScreen(
    onOpenProfile: () -> Unit,
    onOpenSpeciesSheet: (String) -> Unit,
    onOpenFieldSession: (String) -> Unit,
    onPhotoId: () -> Unit,
    onAudioId: () -> Unit,
    onStepByStep: () -> Unit,
    uiState: HomeUiState? = null,
    activeFieldSession: HomeActiveFieldSession? = null,
) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val resolvedState = uiState ?: HomeUiState.Content(
        userDisplayName = snapshot.session.greetingName(),
        carouselItems = HomeCarouselCatalog.items(),
        activeFieldSession = activeFieldSession,
    )
    when (resolvedState) {
        HomeUiState.Loading -> {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(AnuraTheme.extendedColors.boardBackground),
                contentAlignment = Alignment.Center,
            ) {
                AnuraLoadingState(label = stringResource(R.string.home_loading))
            }
        }

        is HomeUiState.Content -> {
            HomeContent(
                state = resolvedState,
                onOpenProfile = onOpenProfile,
                onOpenSpeciesSheet = onOpenSpeciesSheet,
                onOpenFieldSession = onOpenFieldSession,
                onPhotoId = onPhotoId,
                onAudioId = onAudioId,
                onStepByStep = onStepByStep,
            )
        }
    }
}

@Composable
private fun HomeContent(
    state: HomeUiState.Content,
    onOpenProfile: () -> Unit,
    onOpenSpeciesSheet: (String) -> Unit,
    onOpenFieldSession: (String) -> Unit,
    onPhotoId: () -> Unit,
    onAudioId: () -> Unit,
    onStepByStep: () -> Unit,
) {
    val pagerState = rememberPagerState(pageCount = { state.carouselItems.size })

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(AnuraTheme.extendedColors.boardBackground),
    ) {
        HomeHeader(
            userDisplayName = state.userDisplayName,
            onAvatarClick = onOpenProfile,
        )

        Spacer(modifier = Modifier.height(HomeHeaderToCarouselGap))

        if (state.carouselItems.isNotEmpty()) {
            HorizontalPager(
                state = pagerState,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = HomeCarouselHorizontalInset),
                contentPadding = PaddingValues(0.dp),
                pageSpacing = AnuraDimens.spaceGap,
            ) { page ->
                val item = state.carouselItems[page]
                HomeCarouselCard(
                    item = item,
                    onClick = { onOpenSpeciesSheet(item.speciesId) },
                )
            }

            Spacer(modifier = Modifier.height(HomeCarouselToDotsGap))

            HomeCarouselDots(
                count = state.carouselItems.size,
                selectedIndex = pagerState.currentPage,
                modifier = Modifier.align(Alignment.CenterHorizontally),
            )
        }

        // Gap fijo bajo el carrusel: el weight va DEBAJO del bloque de acciones/chip.
        // Si el weight estuviera aquí, al ocultarse la navbar (navegación) el Column
        // crece y los botones saltan hacia abajo (bug visual de press → navigate).
        Spacer(modifier = Modifier.height(HomeDotsToActionsGap))

        HomeQuickActions(
            onStepByStep = onStepByStep,
            onPhotoId = onPhotoId,
            onAudioId = onAudioId,
            modifier = Modifier
                .fillMaxWidth()
                .height(HomeActionsHeight)
                .padding(horizontal = HomeActionsHorizontalInset),
        )

        val session = state.activeFieldSession
        if (session != null) {
            Spacer(modifier = Modifier.height(HomeActionsToChipGap))
            HomeFieldSessionChip(
                session = session,
                onClick = { onOpenFieldSession(session.sessionId) },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = AnuraDimens.spaceGutter),
            )
        }

        Spacer(modifier = Modifier.height(HomeBottomBreathing + LocalAnuraTabBarInset.current))
        Spacer(modifier = Modifier.weight(1f))
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun HomeHeader(
    userDisplayName: String,
    onAvatarClick: () -> Unit,
) {
    Column(modifier = Modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .statusBarsPadding()
                .height(TopAppBarDefaults.TopAppBarExpandedHeight)
                .background(MaterialTheme.colorScheme.surface.copy(alpha = 0.92f))
                .padding(horizontal = AnuraDimens.spaceGutter - 4.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Box(
                modifier = Modifier
                    .size(AnuraDimens.sizeTouch)
                    .clip(CircleShape)
                    .clickable(role = Role.Button, onClick = onAvatarClick),
                contentAlignment = Alignment.Center,
            ) {
                Box(
                    modifier = Modifier
                        .size(HomeAvatarSize)
                        .clip(CircleShape)
                        .background(MaterialTheme.colorScheme.surfaceVariant),
                    contentAlignment = Alignment.Center,
                ) {
                    Icon(
                        imageVector = AnuraIcons.Person,
                        contentDescription = stringResource(R.string.home_avatar_cd),
                        tint = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.size(24.dp),
                    )
                }
            }

            Spacer(modifier = Modifier.size(29.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = stringResource(R.string.home_brand_welcome),
                    style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
                    color = MaterialTheme.colorScheme.onSurface,
                )
                Text(
                    text = if (userDisplayName.isBlank()) {
                        stringResource(R.string.home_greeting_guest)
                    } else {
                        stringResource(R.string.home_greeting, userDisplayName)
                    },
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Normal),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
        HorizontalDivider(
            thickness = 1.dp,
            color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f),
        )
    }
}

@Composable
private fun HomeCarouselCard(
    item: HomeCarouselItem,
    onClick: () -> Unit,
) {
    val categoryTitle = stringResource(item.category.titleRes)
    val cardCd = stringResource(
        R.string.home_carousel_card_cd,
        categoryTitle,
        item.speciesName,
        item.curiousFact,
    )

    val painter = painterResource(item.imageRes)
    var cardCoords by remember { mutableStateOf<LayoutCoordinates?>(null) }

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .aspectRatio(HomeCarouselAspect)
            .clip(RoundedCornerShape(HomeCarouselRadius))
            .onGloballyPositioned { cardCoords = it }
            .clickable(role = Role.Button, onClick = onClick)
            .semantics { contentDescription = cardCd },
    ) {
        Image(
            painter = painter,
            contentDescription = null,
            modifier = Modifier.fillMaxSize(),
            contentScale = ContentScale.Crop,
            colorFilter = AnuraTheme.mediaColorFilter,
        )

        HomeCarouselLightGlass(
            painter = painter,
            cardCoords = cardCoords,
            categoryTitle = categoryTitle,
            speciesName = item.speciesName,
            curiousFact = item.curiousFact,
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .fillMaxWidth()
                .padding(HomeOverlayInset),
        )
    }
}

/**
 * Contenedor translúcido claro estilo Apple HIG (Light Glass / Vibrancy) sobre la foto.
 */
@Composable
private fun HomeCarouselLightGlass(
    painter: Painter,
    cardCoords: LayoutCoordinates?,
    categoryTitle: String,
    speciesName: String,
    curiousFact: String,
    modifier: Modifier = Modifier,
) {
    val extended = AnuraTheme.extendedColors
    val onGlassShadow = remember(extended.onGlassShadow) {
        Shadow(
            color = extended.onGlassShadow,
            offset = Offset(0f, 1f),
            blurRadius = 8f,
        )
    }

    AnuraLightGlass(
        modifier = modifier,
        backdropPainter = painter,
        hostCoordinates = cardCoords,
    ) {
        Column(modifier = Modifier.fillMaxWidth()) {
            Text(
                text = categoryTitle,
                style = MaterialTheme.typography.titleLarge.copy(
                    fontWeight = FontWeight.SemiBold,
                    fontSize = 20.sp,
                    lineHeight = 24.sp,
                    shadow = onGlassShadow,
                ),
                color = extended.onGlass,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
            Spacer(modifier = Modifier.height(2.dp))
            Text(
                text = speciesName,
                style = MaterialTheme.typography.bodyMedium.copy(
                    fontStyle = FontStyle.Italic,
                    fontSize = 13.sp,
                    lineHeight = 16.sp,
                    shadow = onGlassShadow,
                ),
                color = extended.onGlass,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
            Spacer(modifier = Modifier.height(2.dp))
            Text(
                text = curiousFact,
                style = MaterialTheme.typography.bodySmall.copy(
                    fontWeight = FontWeight.Medium,
                    fontSize = 12.sp,
                    lineHeight = 15.sp,
                    shadow = onGlassShadow,
                ),
                color = extended.onGlass,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis,
            )
        }
    }
}

@Composable
private fun HomeCarouselDots(
    count: Int,
    selectedIndex: Int,
    modifier: Modifier = Modifier,
) {
    Row(
        modifier = modifier,
        horizontalArrangement = Arrangement.spacedBy(HomeDotGap),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        repeat(count) { index ->
            val selected = index == selectedIndex
            val dotColor by animateColorAsState(
                targetValue = if (selected) {
                    AnuraTheme.extendedColors.accentInk
                } else {
                    MaterialTheme.colorScheme.outlineVariant
                },
                animationSpec = tween(AnuraMotion.DurationShort),
                label = "HomeCarouselDot",
            )
            Box(
                modifier = Modifier
                    .size(HomeDotSize)
                    .clip(CircleShape)
                    .background(dotColor),
            )
        }
    }
}

@Composable
fun HomeQuickActions(
    onStepByStep: () -> Unit,
    onPhotoId: () -> Unit,
    onAudioId: () -> Unit,
    modifier: Modifier = Modifier,
) {
    // Orden Penpot L→R: Paso a paso · Foto ID (verde) · Audio ID.
    Row(
        modifier = modifier,
        horizontalArrangement = Arrangement.SpaceEvenly,
        verticalAlignment = Alignment.Top,
    ) {
        HomeCircularAction(
            label = stringResource(R.string.home_action_step_by_step),
            icon = AnuraIcons.StepByStep,
            primary = false,
            onClick = onStepByStep,
            modifier = Modifier.weight(1f),
        )
        HomeCircularAction(
            label = stringResource(R.string.home_action_photo_id),
            icon = AnuraIcons.PhotoId,
            primary = true,
            onClick = onPhotoId,
            modifier = Modifier.weight(1f),
        )
        HomeCircularAction(
            label = stringResource(R.string.home_action_audio_id),
            icon = AnuraIcons.AudioId,
            primary = false,
            onClick = onAudioId,
            modifier = Modifier.weight(1f),
        )
    }
}

@Composable
private fun HomeCircularAction(
    label: String,
    icon: ImageVector,
    primary: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val size = if (primary) HomeActionPrimarySize else HomeActionSecondarySize
    val container = if (primary) {
        AnuraTheme.extendedColors.accentInk
    } else {
        MaterialTheme.colorScheme.surface
    }
    val content = if (primary) {
        MaterialTheme.colorScheme.onPrimary
    } else {
        AnuraTheme.extendedColors.accentInk
    }
    val interaction = remember { MutableInteractionSource() }

    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = modifier.clickable(
            interactionSource = interaction,
            indication = null,
            role = Role.Button,
            onClick = onClick,
        ),
    ) {
        // Secundarios en Penpot empiezan 8 dp más abajo que Foto ID.
        if (!primary) {
            Spacer(modifier = Modifier.height(8.dp))
        }
        Surface(
            modifier = Modifier
                .size(size)
                .clip(CircleShape)
                .indication(interaction, ripple()),
            shape = CircleShape,
            color = container,
            shadowElevation = if (primary) 6.dp else 0.dp,
            tonalElevation = 0.dp,
        ) {
            Box(contentAlignment = Alignment.Center, modifier = Modifier.fillMaxSize()) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = content,
                    modifier = Modifier.size(if (primary) 36.dp else 32.dp),
                )
            }
        }
        Spacer(modifier = Modifier.height(6.dp))
        Text(
            text = label,
            style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
            color = MaterialTheme.colorScheme.onSurface,
            textAlign = TextAlign.Center,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 2.dp),
        )
    }
}

@Composable
private fun HomeFieldSessionChip(
    session: HomeActiveFieldSession,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val extended = AnuraTheme.extendedColors
    val chipAccent = MaterialTheme.colorScheme.primary
    val meta = stringResource(
        R.string.home_field_session_meta,
        session.placeName,
        session.elapsedLabel,
        pluralStringResource(
            R.plurals.home_field_session_registers,
            session.registerCount,
            session.registerCount,
        ),
    )

    Surface(
        onClick = onClick,
        modifier = modifier.height(84.dp),
        shape = RoundedCornerShape(AnuraDimens.radiusCard),
        color = chipAccent.copy(alpha = 0.12f),
        border = BorderStroke(1.dp, chipAccent),
    ) {
        Row(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 20.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Box(
                modifier = Modifier
                    .size(12.dp)
                    .clip(CircleShape)
                    .background(extended.accentInk),
            )
            Spacer(modifier = Modifier.size(10.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = stringResource(R.string.home_field_session_title),
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                    color = extended.accentInk,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
                Text(
                    text = meta,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
            }
            Icon(
                imageVector = AnuraIcons.ChevronRight,
                contentDescription = stringResource(R.string.home_field_session_open_cd),
                tint = extended.accentInk,
                modifier = Modifier.size(20.dp),
            )
        }
    }
}

@AnuraPreviews
@Composable
private fun HomeScreenPreview() {
    AnuraTheme {
        HomeScreen(
            onOpenProfile = {},
            onOpenSpeciesSheet = {},
            onOpenFieldSession = {},
            onPhotoId = {},
            onAudioId = {},
            onStepByStep = {},
        )
    }
}

@Preview(name = "Sin salida", group = "estado", showBackground = true)
@Composable
private fun HomeScreenPreviewNoSession() {
    AnuraTheme {
        HomeScreen(
            onOpenProfile = {},
            onOpenSpeciesSheet = {},
            onOpenFieldSession = {},
            onPhotoId = {},
            onAudioId = {},
            onStepByStep = {},
            uiState = HomeUiState.Content(
                userDisplayName = "Sebastián",
                carouselItems = HomeCarouselCatalog.items(),
                activeFieldSession = null,
            ),
        )
    }
}

@Preview(name = "Con salida", group = "estado", showBackground = true)
@Composable
private fun HomeScreenPreviewWithSession() {
    AnuraTheme {
        HomeScreen(
            onOpenProfile = {},
            onOpenSpeciesSheet = {},
            onOpenFieldSession = {},
            onPhotoId = {},
            onAudioId = {},
            onStepByStep = {},
            activeFieldSession = HomeCarouselCatalog.mockActiveFieldSession(),
        )
    }
}

@Preview(name = "Cargando", group = "estado", showBackground = true)
@Composable
private fun HomeScreenPreviewLoading() {
    AnuraTheme {
        HomeScreen(
            onOpenProfile = {},
            onOpenSpeciesSheet = {},
            onOpenFieldSession = {},
            onPhotoId = {},
            onAudioId = {},
            onStepByStep = {},
            uiState = HomeUiState.Loading,
        )
    }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun HomeScreenPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) {
        HomeScreen(
            onOpenProfile = {},
            onOpenSpeciesSheet = {},
            onOpenFieldSession = {},
            onPhotoId = {},
            onAudioId = {},
            onStepByStep = {},
        )
    }
}
