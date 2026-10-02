package me.juanlabs.anura.feature.explore

import kotlin.math.atan2
import kotlin.math.cos
import kotlin.math.pow
import kotlin.math.sin
import kotlin.math.sqrt
import kotlinx.coroutines.delay
import androidx.compose.foundation.Image
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.GridItemSpan
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.produceState
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.R
import me.juanlabs.anura.core.data.CatalogAvailability
import me.juanlabs.anura.core.data.ContentCatalog
import me.juanlabs.anura.core.data.catalogGapBody
import me.juanlabs.anura.core.data.catalogGapTitle
import me.juanlabs.anura.core.data.ExplorerFeedItem
import me.juanlabs.anura.core.data.ExplorerRemote
import me.juanlabs.anura.core.data.ExplorerSuggestion
import me.juanlabs.anura.core.data.NearbySpecies
import me.juanlabs.anura.core.data.ObservationRecord
import me.juanlabs.anura.core.data.RegionalPackageStatus
import me.juanlabs.anura.core.data.SpeciesCatalog
import me.juanlabs.anura.core.data.SpeciesRecord
import me.juanlabs.anura.core.data.rememberAnuraRepository
import me.juanlabs.anura.core.data.rememberSpeciesPhotoPainter
import me.juanlabs.anura.core.platform.rememberNetworkAvailable
import me.juanlabs.anura.core.platform.rememberPhotoPlaceholderPainter
import me.juanlabs.anura.core.platform.rememberRemotePhotoPainter
import me.juanlabs.anura.designsystem.component.AnuraBottomSheet
import me.juanlabs.anura.designsystem.component.AnuraCard
import me.juanlabs.anura.designsystem.component.AnuraConservationChip
import me.juanlabs.anura.designsystem.component.AnuraConservationChipVariant
import me.juanlabs.anura.designsystem.component.AnuraEmptyState
import me.juanlabs.anura.designsystem.component.AnuraErrorState
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraMeasureSlider
import me.juanlabs.anura.designsystem.component.lastKnownLocation
import me.juanlabs.anura.designsystem.component.AnuraToxicityChip
import me.juanlabs.anura.designsystem.component.AnuraToxicityChipVariant
import me.juanlabs.anura.designsystem.component.AnuraSectionLabel
import me.juanlabs.anura.designsystem.component.AnuraTextField
import me.juanlabs.anura.designsystem.component.AnuraTopBar
import me.juanlabs.anura.designsystem.component.LocalAnuraTabBarInset
import me.juanlabs.anura.designsystem.component.ObservationCard
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode
import me.juanlabs.anura.feature.capture.rememberCaptureBackdropPainter

private val ExploreMapHeight = 280.dp
private const val FilterFamily = "family:"
private const val FilterGenus = "genus:"
private const val FilterDanger = "danger:"
private const val FilterIucn = "iucn:"
private const val DangerToxic = "toxic"
private const val DangerHarmless = "harmless"
private const val ExploreSvlMin = 10f
private const val ExploreSvlMax = 160f
private const val ExploreSvlStart = 48f

private data class ExploreObservation(
    val id: String,
    /** Foto propia guardada en el teléfono (token de `MediaPersistence`); null = no hay. */
    val photoToken: String? = null,
    /** Miniatura real del servidor (`ExplorerRemote.thumbUrl`); null = no hay. */
    val photoUrl: String? = null,
    /** Foto publicada de la especie (sha256) para cuando la observación no tiene foto propia. */
    val photoSha256: String? = null,
    val latitude: Double,
    val longitude: Double,
    val family: String,
    val genus: String,
    val altitude: String,
    val size: String,
    val toxic: Boolean,
    val iucn: AnuraConservationChipVariant?,
    val traits: Set<String>,
    val unsynced: Boolean = false,
    val commonName: String? = null,
    val scientificName: String? = null,
)

/** Distancia en km entre dos coordenadas (haversine) — para ordenar "Cerca de vos" por
 * proximidad real, no por el orden arbitrario del catálogo. */
private fun haversineKm(lat1: Double, lon1: Double, lat2: Double, lon2: Double): Double {
    val earthRadiusKm = 6371.0
    val dLat = Math.toRadians(lat2 - lat1)
    val dLon = Math.toRadians(lon2 - lon1)
    val a = sin(dLat / 2).pow(2) +
        cos(Math.toRadians(lat1)) * cos(Math.toRadians(lat2)) * sin(dLon / 2).pow(2)
    return earthRadiusKm * 2 * atan2(sqrt(a), sqrt(1 - a))
}

/**
 * Ordena por distancia real a [origin] (todas quedan, solo cambia el orden); sin [origin] (sin
 * ubicación disponible) devuelve la lista tal cual — nunca bloquea ni oculta resultados.
 */
private fun <T> List<Pair<ExploreObservation, T>>.sortedByDistanceTo(
    origin: Pair<Double, Double>?,
): List<Pair<ExploreObservation, T>> {
    if (origin == null) return this
    val (originLat, originLon) = origin
    return sortedBy { (item, _) -> haversineKm(originLat, originLon, item.latitude, item.longitude) }
}

private const val ExploreNearYouPreviewCount = 6

/**
 * "Cerca de vos": hasta [ExploreNearYouPreviewCount] especies del catálogo, no observaciones —
 * son fichas técnicas. Ordenadas por P(especie|zona) real del paquete regional activo (mismo
 * prior geográfico de `Arquitectura Multimodal §5.1`, [NearbySpecies]) según la última ubicación
 * GPS conocida. Sin ubicación o sin paquete instalado, cae a las primeras del catálogo — nunca
 * bloquea ni deja la sección vacía por eso.
 */
@Composable
private fun rememberNearYouSpecies(): List<SpeciesRecord> {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val context = LocalContext.current
    // El catálogo también es clave: cuando termina de bajar, la lista se recalcula (antes quedaba vacía).
    return remember(snapshot.packages, ContentCatalog.catalog) {
        val activePackage = snapshot.packages.firstOrNull {
            it.active && it.status == RegionalPackageStatus.Installed && it.localPath != null
        }
        val location = lastKnownLocation(context)
        val ranked = if (activePackage?.localPath != null && location != null) {
            NearbySpecies.rankedTaxonIds(
                packagePath = activePackage.localPath,
                latitude = location.latitude,
                longitude = location.longitude,
                limit = ExploreNearYouPreviewCount,
            ).mapNotNull(SpeciesCatalog::find)
        } else {
            emptyList()
        }
        ranked.ifEmpty { SpeciesCatalog.all.take(ExploreNearYouPreviewCount) }
    }
}

/**
 * Catálogo de especies — pestaña Listado (tab 3). Fichas técnicas, no el feed de observaciones
 * (ese vive en Explorar / [ObservationsScreen]).
 *
 * La búsqueda es donde se usa la conexión con el servidor: escribir pide sugerencias reales a
 * `GET /api/explorer/suggest` (explorer-service, `species.taxonomy`), agrupadas en cliente por
 * especie/género/familia (el servidor devuelve filas de especie; los grupos de género y familia
 * son las distintas que aparecen entre esas filas — sigue siendo dato real, solo agrupado). Tocar
 * una especie abre su ficha; tocar un género o familia abre [SpeciesByTaxonScreen] con la lista de
 * esa familia/género. Sin conexión, la búsqueda no tiene de dónde sacar sugerencias — se avisa en
 * vez de mostrar algo inventado.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ExploreScreen(
    onOpenSpeciesSheet: (String) -> Unit,
    onOpenSpeciesByTaxon: (String) -> Unit,
    onOpenExploreMore: () -> Unit,
) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val online = rememberNetworkAvailable()
    var query by rememberSaveable { mutableStateOf("") }
    val needle = query.trim()
    val searching = needle.length >= 2
    var remoteSuggestions by remember { mutableStateOf<List<ExplorerSuggestion>>(emptyList()) }
    var suggestLoading by remember { mutableStateOf(false) }
    LaunchedEffect(needle) {
        if (needle.length < 2) {
            remoteSuggestions = emptyList()
            suggestLoading = false
            return@LaunchedEffect
        }
        suggestLoading = true
        delay(300) // debounce: no pedir sugerencias en cada tecla
        remoteSuggestions = ExplorerRemote.suggest(needle)
        suggestLoading = false
    }
    val genusLabel = stringResource(R.string.explore_suggestion_genus)
    val familyLabel = stringResource(R.string.explore_suggestion_family)
    val suggestions = remember(remoteSuggestions, genusLabel, familyLabel) {
        groupedTaxonSuggestions(remoteSuggestions, genusLabel, familyLabel)
    }
    val nearYou = rememberNearYouSpecies()
    val speciesCount = SpeciesCatalog.all.size
    val familyCount = SpeciesCatalog.all.map { it.family }.distinct().size
    val genusCount = SpeciesCatalog.all.map { it.genus }.distinct().size

    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        topBar = {
            AnuraTopBar(
                title = stringResource(R.string.explore_title),
                centerTitle = true,
            )
        },
    ) { innerPadding ->
        LazyVerticalGrid(
            columns = GridCells.Fixed(2),
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding),
            contentPadding = PaddingValues(
                start = AnuraDimens.spaceGutter,
                top = 0.dp,
                end = AnuraDimens.spaceGutter,
                bottom = AnuraDimens.spaceSection + LocalAnuraTabBarInset.current,
            ),
            horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
            verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
        ) {
            item(
                key = "explore-search",
                span = { GridItemSpan(maxLineSpan) },
            ) {
                AnuraTextField(
                    value = query,
                    onValueChange = { query = it },
                    label = stringResource(R.string.observations_search),
                    modifier = Modifier.fillMaxWidth(),
                    leadingIcon = AnuraIcons.Empty,
                    singleLine = true,
                )
            }
            if (!online) {
                item(
                    key = "explore-offline",
                    span = { GridItemSpan(maxLineSpan) },
                ) {
                    AnuraErrorState(
                        title = stringResource(R.string.explore_offline_title),
                        description = stringResource(R.string.explore_offline_body),
                    )
                }
            }
            if (speciesCount > 0) item(
                key = "explore-stats",
                span = { GridItemSpan(maxLineSpan) },
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                ) {
                    ExploreStatCard(
                        value = speciesCount.toString(),
                        label = stringResource(R.string.explore_stat_species),
                        modifier = Modifier.weight(1f),
                    )
                    ExploreStatCard(
                        value = familyCount.toString(),
                        label = stringResource(R.string.explore_stat_families),
                        modifier = Modifier.weight(1f),
                    )
                    ExploreStatCard(
                        value = genusCount.toString(),
                        label = stringResource(R.string.explore_stat_genera),
                        modifier = Modifier.weight(1f),
                    )
                }
            }
            if (!searching && nearYou.isNotEmpty()) {
                item(
                    key = "explore-near",
                    span = { GridItemSpan(maxLineSpan) },
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text(
                            text = stringResource(R.string.explore_near_you),
                            style = MaterialTheme.typography.titleMedium.copy(
                                fontWeight = FontWeight.SemiBold,
                            ),
                            modifier = Modifier.weight(1f),
                        )
                        TextButton(
                            onClick = onOpenExploreMore,
                        ) {
                            Text(
                                text = stringResource(R.string.explore_see_more),
                                color = AnuraTheme.extendedColors.accentInk,
                                fontWeight = FontWeight.SemiBold,
                            )
                        }
                    }
                }
            }
            if (searching) {
                item(
                    key = "explore-suggestions",
                    span = { GridItemSpan(maxLineSpan) },
                ) {
                    when {
                        suggestions.isNotEmpty() -> ExploreSuggestionMenu(
                            suggestions = suggestions,
                            onSelect = { suggestion ->
                                when (suggestion.kind) {
                                    ExploreSuggestionKind.Species -> onOpenSpeciesSheet(suggestion.query)
                                    ExploreSuggestionKind.Genus, ExploreSuggestionKind.Family ->
                                        onOpenSpeciesByTaxon(suggestion.query)
                                }
                            },
                        )
                        suggestLoading -> Unit // ya se ve el estado "sin conexión" arriba si aplica; nada que mostrar todavía
                        !online -> Unit // el aviso de "explore-offline" ya cubre este caso
                        else -> AnuraEmptyState(
                            title = stringResource(R.string.observations_empty_title),
                            description = stringResource(R.string.observations_empty_body),
                        )
                    }
                }
            } else if (nearYou.isEmpty()) {
                item(
                    key = "explore-empty",
                    span = { GridItemSpan(maxLineSpan) },
                ) {
                    AnuraEmptyState(
                        title = catalogGapTitle(),
                        description = catalogGapBody(),
                    )
                }
            } else {
                items(nearYou, key = { it.id }) { record ->
                    ObservationCard(
                        commonName = record.commonName,
                        scientificName = record.scientificName,
                        isFavorite = snapshot.favorites.contains(record.id),
                        onFavoriteClick = { repository.toggleFavorite(record.id) },
                        modifier = Modifier.fillMaxWidth(),
                        thumbnail = {
                            Image(
                                painter = rememberSpeciesPhotoPainter(record.photoSha256, ContentCatalog.ThumbWidth),
                                contentDescription = null,
                                modifier = Modifier.fillMaxSize(),
                                contentScale = ContentScale.Crop,
                            )
                        },
                        onClick = { onOpenSpeciesSheet(record.id) },
                    )
                }
            }
        }
    }
}

/**
 * `ver mas`: TODAS las fichas técnicas del catálogo (no solo las 6 cercanas), agrupadas por
 * familia y género — "género (familia) — N especies" como encabezado de sección, igual que la
 * lista que dio el usuario. Buscar filtra por nombre/género/familia sin romper la agrupación.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ExploreMoreScreen(
    onBackClick: () -> Unit,
    onOpenSpeciesSheet: (String) -> Unit,
) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    var query by rememberSaveable { mutableStateOf("") }
    val needle = query.trim()
    val filtered = SpeciesCatalog.all.filter { record ->
        needle.isEmpty() ||
            record.commonName.contains(needle, ignoreCase = true) ||
            record.scientificName.contains(needle, ignoreCase = true) ||
            record.genus.contains(needle, ignoreCase = true) ||
            record.family.contains(needle, ignoreCase = true)
    }
    val grouped = filtered
        .sortedWith(compareBy({ it.family }, { it.genus }, { it.scientificName }))
        .groupBy { it.genus to it.family }
        .toList()

    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        topBar = {
            AnuraTopBar(
                title = stringResource(R.string.explore_more_title),
                onBackClick = onBackClick,
                centerTitle = true,
            )
        },
    ) { innerPadding ->
        if (grouped.isEmpty()) {
            AnuraEmptyState(
                title = if (needle.isEmpty()) catalogGapTitle() else stringResource(R.string.observations_empty_title),
                description = if (needle.isEmpty()) catalogGapBody() else stringResource(R.string.observations_empty_body),
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding),
            )
            return@Scaffold
        }
        LazyVerticalGrid(
            columns = GridCells.Fixed(2),
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding),
            contentPadding = PaddingValues(AnuraDimens.spaceGutter),
            horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
            verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
        ) {
            item(
                key = "explore-more-search",
                span = { GridItemSpan(maxLineSpan) },
            ) {
                AnuraTextField(
                    value = query,
                    onValueChange = { query = it },
                    label = stringResource(R.string.observations_search),
                    modifier = Modifier.fillMaxWidth(),
                    leadingIcon = AnuraIcons.Empty,
                    singleLine = true,
                )
            }
            grouped.forEach { (genusFamily, members) ->
                val (genus, family) = genusFamily
                item(
                    key = "header-$genus-$family",
                    span = { GridItemSpan(maxLineSpan) },
                ) {
                    Text(
                        text = stringResource(R.string.explore_taxon_group_header, genus, family, members.size),
                        style = MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.SemiBold),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.padding(top = AnuraDimens.spaceGap),
                    )
                }
                items(members, key = { it.id }) { record ->
                    ObservationCard(
                        commonName = record.commonName,
                        scientificName = record.scientificName,
                        isFavorite = snapshot.favorites.contains(record.id),
                        onFavoriteClick = { repository.toggleFavorite(record.id) },
                        modifier = Modifier.fillMaxWidth(),
                        thumbnail = {
                            Image(
                                painter = rememberSpeciesPhotoPainter(record.photoSha256, ContentCatalog.ThumbWidth),
                                contentDescription = null,
                                modifier = Modifier.fillMaxSize(),
                                contentScale = ContentScale.Crop,
                            )
                        },
                        onClick = { onOpenSpeciesSheet(record.id) },
                    )
                }
            }
        }
    }
}

/**
 * Catálogo 2 columnas (Penpot `ver mas`). Lo reutilizan Explorar más y una zona
 * descargada: misma barra, búsqueda, recuento y ObservationCard 167×196.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ObservationCatalogScreen(
    title: String,
    onBackClick: () -> Unit,
    onOpenObservationDetail: (String) -> Unit,
    showQuickFilters: Boolean = false,
    showSheetFilters: Boolean = false,
    showSortAction: Boolean = true,
    searchHint: String? = null,
    taxonFilter: String? = null,
    sortByDistance: Boolean = false,
) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val online = rememberNetworkAvailable()
    val remoteFeed by produceState(initialValue = emptyList<ExplorerFeedItem>(), online) {
        value = if (online) ExplorerRemote.feed() else emptyList()
    }
    val catalog = run {
        val ownId = snapshot.session.userId
        val local = snapshot.observations
            .filter { observation -> observation.visibilityPublic && (online || observation.ownerUserId == ownId) }
            .mapNotNull { it.toExploreObservation() }
        val ownIds = snapshot.observations.flatMap { listOfNotNull(it.id, it.serverId) }.toSet()
        val mine = snapshot.session.username
        val community = remoteFeed
            .filter { item ->
                item.id !in ownIds &&
                    !(mine.isNotBlank() && item.username.equals(mine, ignoreCase = true))
            }
            .mapNotNull { it.toExploreObservation() }
        (local + community)
    }
        .distinctBy { it.id }
        .let { items ->
            if (taxonFilter.isNullOrBlank()) {
                items
            } else {
                items.filter { item ->
                    item.family.equals(taxonFilter, ignoreCase = true) ||
                        item.genus.equals(taxonFilter, ignoreCase = true)
                }
            }
        }
    var query by rememberSaveable { mutableStateOf("") }
    var sortByScientific by rememberSaveable { mutableStateOf(false) }
    var quickFilter by rememberSaveable { mutableStateOf(CatalogQuickFilter.All.name) }
    var selectedFilters by rememberSaveable { mutableStateOf(listOf<String>()) }
    var altitudeMin by rememberSaveable { mutableStateOf("") }
    var altitudeMax by rememberSaveable { mutableStateOf("") }
    var svlMm by rememberSaveable { mutableFloatStateOf(ExploreSvlStart) }
    var svlActive by rememberSaveable { mutableStateOf(false) }
    var showFilters by rememberSaveable { mutableStateOf(false) }
    val named = catalog.map { item -> item to item.displayNames() }
    val needle = query.trim()
    val taxon = taxonFilter?.trim().orEmpty()
    val searched = named.filter { (item, names) ->
        val textOk = needle.isEmpty() ||
            names.first.contains(needle, ignoreCase = true) ||
            names.second.contains(needle, ignoreCase = true) ||
            item.genus.contains(needle, ignoreCase = true) ||
            item.family.contains(needle, ignoreCase = true)
        val taxonOk = taxon.isEmpty() ||
            taxon.equals("Anura", ignoreCase = true) ||
            item.family.equals(taxon, ignoreCase = true) ||
            item.genus.equals(taxon, ignoreCase = true)
        val sheetOk = !showSheetFilters || item.matchesFilters(
            selected = selectedFilters,
            altitudeMinM = parseMetric(altitudeMin),
            altitudeMaxM = parseMetric(altitudeMax),
            svlMm = if (svlActive) svlMm.toInt() else null,
        )
        textOk && taxonOk && sheetOk
    }
    val filtered = if (!showQuickFilters) {
        searched
    } else {
        when (CatalogQuickFilter.valueOf(quickFilter)) {
            CatalogQuickFilter.All -> searched
            CatalogQuickFilter.Toxic -> searched.filter { it.first.toxic }
            CatalogQuickFilter.Threatened -> searched.filter {
                val iucn = it.first.iucn
                iucn != null &&
                    iucn != AnuraConservationChipVariant.LC &&
                    iucn != AnuraConservationChipVariant.DD &&
                    iucn != AnuraConservationChipVariant.NE
            }
            CatalogQuickFilter.Unsynced -> searched.filter { it.first.unsynced }
        }
    }
    val context = LocalContext.current
    val currentLocation = remember(sortByDistance) {
        if (sortByDistance) lastKnownLocation(context)?.let { it.latitude to it.longitude } else null
    }
    val shown = when {
        sortByScientific -> filtered.sortedBy { it.second.second }
        sortByDistance -> filtered.sortedByDistanceTo(currentLocation)
        else -> filtered
    }
    val resolvedSearchHint = searchHint ?: stringResource(R.string.observations_search)
    val sortCd = stringResource(R.string.explore_more_sort)
    val filterCd = stringResource(R.string.explore_filter_cd)

    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        topBar = {
            AnuraTopBar(
                title = title,
                onBackClick = onBackClick,
                centerTitle = true,
                actions = {
                    if (showSheetFilters) {
                        IconButton(
                            onClick = { showFilters = true },
                            modifier = Modifier.size(AnuraDimens.sizeTouch),
                        ) {
                            Icon(
                                imageVector = AnuraIcons.Filter,
                                contentDescription = filterCd,
                                tint = AnuraTheme.extendedColors.accentInk,
                            )
                        }
                    }
                    if (showSortAction) {
                        IconButton(
                            onClick = { sortByScientific = !sortByScientific },
                            modifier = Modifier.size(AnuraDimens.sizeTouch),
                        ) {
                            Icon(
                                imageVector = AnuraIcons.Sort,
                                contentDescription = sortCd,
                                tint = AnuraTheme.extendedColors.accentInk,
                            )
                        }
                    }
                },
            )
        },
    ) { innerPadding ->
        LazyVerticalGrid(
            columns = GridCells.Fixed(2),
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding),
            contentPadding = PaddingValues(
                start = AnuraDimens.spaceGutter,
                top = 0.dp,
                end = AnuraDimens.spaceGutter,
                bottom = AnuraDimens.spaceSection,
            ),
            horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
            verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
        ) {
            item(
                key = "explore-more-search",
                span = { GridItemSpan(maxLineSpan) },
            ) {
                Column(
                    verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                ) {
                    AnuraCard(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(AnuraDimens.radiusButton),
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .heightIn(min = AnuraDimens.sizeTouch)
                                .padding(horizontal = AnuraDimens.spaceLabelToContent),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                        ) {
                            Icon(
                                imageVector = AnuraIcons.Empty,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                                modifier = Modifier.size(20.dp),
                            )
                            BasicTextField(
                                value = query,
                                onValueChange = { query = it },
                                modifier = Modifier
                                    .weight(1f)
                                    .semantics { contentDescription = resolvedSearchHint },
                                textStyle = MaterialTheme.typography.bodyLarge.copy(
                                    color = MaterialTheme.colorScheme.onSurface,
                                ),
                                singleLine = true,
                                cursorBrush = SolidColor(MaterialTheme.colorScheme.primary),
                                decorationBox = { inner ->
                                    if (query.isEmpty()) {
                                        Text(
                                            text = resolvedSearchHint,
                                            style = MaterialTheme.typography.bodyLarge,
                                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                                        )
                                    }
                                    inner()
                                },
                            )
                        }
                    }
                    if (showQuickFilters) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .horizontalScroll(rememberScrollState()),
                            horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                        ) {
                            CatalogQuickFilter.entries.forEach { filter ->
                                ExploreFilterChip(
                                    label = stringResource(filter.labelRes),
                                    selected = quickFilter == filter.name,
                                    onClick = { quickFilter = filter.name },
                                )
                            }
                        }
                    }
                    Text(
                        text = stringResource(R.string.explore_more_count, shown.size),
                        style = MaterialTheme.typography.labelSmall.copy(
                            fontWeight = FontWeight.Medium,
                        ),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
            items(shown, key = { it.first.id }) { (item, names) ->
                ExploreObservationCard(
                    item = item,
                    names = names,
                    favorite = snapshot.favorites.contains(item.id),
                    onFavoriteClick = { repository.toggleFavorite(item.id) },
                    onClick = { onOpenObservationDetail(item.id) },
                )
            }
        }
    }
    if (showSheetFilters && showFilters) {
        ExploreFilterSheet(
            families = remember(catalog) { catalog.map { it.family }.filter { it.isNotBlank() }.distinct().sorted() },
            genera = remember(catalog) { catalog.map { it.genus }.filter { it.isNotBlank() }.distinct().sorted() },
            selected = selectedFilters,
            altitudeMin = altitudeMin,
            altitudeMax = altitudeMax,
            svlMm = svlMm,
            onToggle = { id ->
                selectedFilters = if (selectedFilters.contains(id)) {
                    selectedFilters - id
                } else {
                    selectedFilters + id
                }
            },
            onAltitudeMinChange = { altitudeMin = it },
            onAltitudeMaxChange = { altitudeMax = it },
            onSvlChange = {
                svlMm = it
                svlActive = true
            },
            onDismiss = { showFilters = false },
        )
    }
}

@Composable
private fun ExploreObservationCard(
    item: ExploreObservation,
    names: Pair<String, String>,
    favorite: Boolean,
    onFavoriteClick: () -> Unit,
    onClick: () -> Unit,
) {
    val chip: (@Composable () -> Unit)? = when {
        item.toxic -> {
            { AnuraToxicityChip(AnuraToxicityChipVariant.Toxic) }
        }
        item.iucn != null && item.iucn != AnuraConservationChipVariant.LC -> {
            { AnuraConservationChip(item.iucn) }
        }
        else -> null
    }
    ObservationCard(
        commonName = names.first,
        scientificName = names.second,
        isFavorite = favorite,
        onFavoriteClick = onFavoriteClick,
        modifier = Modifier.fillMaxWidth(),
        statusChip = chip,
        thumbnail = {
            Image(
                painter = when {
                    item.photoToken != null ->
                        rememberCaptureBackdropPainter(item.photoToken) ?: rememberPhotoPlaceholderPainter()
                    item.photoUrl != null ->
                        rememberRemotePhotoPainter(item.photoUrl, rememberSpeciesPhotoPainter(item.photoSha256, ContentCatalog.ThumbWidth))
                    else -> rememberSpeciesPhotoPainter(item.photoSha256, ContentCatalog.ThumbWidth)
                },
                contentDescription = null,
                modifier = Modifier.fillMaxSize(),
                contentScale = ContentScale.Crop,
            )
        },
        onClick = onClick,
    )
}

@Composable
private fun ExploreStatCard(
    value: String,
    label: String,
    modifier: Modifier = Modifier,
) {
    AnuraCard(modifier = modifier, bordered = true) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = AnuraDimens.spaceLabelToContent,
                    vertical = AnuraDimens.spaceGap,
                ),
        ) {
            Text(
                text = value,
                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
            )
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Medium),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
private fun ExploreFilterSheet(
    families: List<String>,
    genera: List<String>,
    selected: List<String>,
    altitudeMin: String,
    altitudeMax: String,
    svlMm: Float,
    onToggle: (String) -> Unit,
    onAltitudeMinChange: (String) -> Unit,
    onAltitudeMaxChange: (String) -> Unit,
    onSvlChange: (Float) -> Unit,
    onDismiss: () -> Unit,
) {
    val altitudePlaceholder = stringResource(R.string.explore_filter_altitude_placeholder)
    val svlValue = svlMm.toInt()

    AnuraBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = AnuraDimens.spaceGutter)
                .padding(bottom = AnuraDimens.spaceSection),
            verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceSection),
        ) {
            Text(
                text = stringResource(R.string.explore_filter_title),
                style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold),
            )
            FilterGroup(title = stringResource(R.string.explore_filter_taxonomy)) {
                families.distinct().forEach { family ->
                    ExploreFilterChip(
                        label = family,
                        selected = selected.contains(FilterFamily + family),
                        onClick = { onToggle(FilterFamily + family) },
                    )
                }
                genera.distinct().forEach { genus ->
                    ExploreFilterChip(
                        label = genus,
                        selected = selected.contains(FilterGenus + genus),
                        onClick = { onToggle(FilterGenus + genus) },
                    )
                }
            }
            Column(verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceLabelToContent)) {
                AnuraSectionLabel(text = stringResource(R.string.explore_filter_altitude))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                ) {
                    AnuraTextField(
                        value = altitudeMin,
                        onValueChange = onAltitudeMinChange,
                        label = stringResource(R.string.explore_filter_altitude_min),
                        modifier = Modifier.weight(1f),
                        placeholder = altitudePlaceholder,
                        keyboardType = KeyboardType.Number,
                    )
                    AnuraTextField(
                        value = altitudeMax,
                        onValueChange = onAltitudeMaxChange,
                        label = stringResource(R.string.explore_filter_altitude_max),
                        modifier = Modifier.weight(1f),
                        placeholder = altitudePlaceholder,
                        keyboardType = KeyboardType.Number,
                    )
                }
            }
            Column(verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceLabelToContent)) {
                AnuraSectionLabel(text = stringResource(R.string.explore_filter_svl))
                Text(
                    text = stringResource(R.string.explore_filter_svl_hint),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                AnuraMeasureSlider(
                    value = svlMm,
                    onValueChange = onSvlChange,
                    valueRange = ExploreSvlMin..ExploreSvlMax,
                )
                Row(modifier = Modifier.fillMaxWidth()) {
                    Text(
                        text = stringResource(R.string.capture_step3_min),
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.weight(1f),
                    )
                    Text(
                        text = stringResource(R.string.capture_step3_max),
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        textAlign = TextAlign.End,
                        modifier = Modifier.weight(1f),
                    )
                }
                Text(
                    text = stringResource(R.string.capture_step3_value, svlValue),
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                    color = AnuraTheme.extendedColors.accentInk,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.fillMaxWidth(),
                )
            }
            FilterGroup(title = stringResource(R.string.explore_filter_danger)) {
                ExploreFilterChip(
                    label = stringResource(R.string.explore_filter_toxic),
                    selected = selected.contains(FilterDanger + DangerToxic),
                    onClick = { onToggle(FilterDanger + DangerToxic) },
                )
                ExploreFilterChip(
                    label = stringResource(R.string.explore_filter_harmless),
                    selected = selected.contains(FilterDanger + DangerHarmless),
                    onClick = { onToggle(FilterDanger + DangerHarmless) },
                )
            }
            FilterGroup(title = stringResource(R.string.explore_filter_status)) {
                AnuraConservationChipVariant.entries.forEach { status ->
                    ExploreFilterChip(
                        label = status.shortLabel,
                        selected = selected.contains(FilterIucn + status.name),
                        onClick = { onToggle(FilterIucn + status.name) },
                    )
                }
            }
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun FilterGroup(
    title: String,
    content: @Composable () -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceLabelToContent)) {
        AnuraSectionLabel(text = title)
        FlowRow(
            horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
            verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceLabelToContent),
            content = { content() },
        )
    }
}

private enum class CatalogQuickFilter(val labelRes: Int) {
    All(R.string.favorites_filter_all),
    Toxic(R.string.favorites_filter_toxic),
    Threatened(R.string.favorites_filter_threatened),
    Unsynced(R.string.favorites_filter_unsynced),
}

@Composable
private fun ExploreFilterChip(
    label: String,
    selected: Boolean,
    onClick: () -> Unit,
) {
    FilterChip(
        selected = selected,
        onClick = onClick,
        label = { Text(text = label) },
        colors = FilterChipDefaults.filterChipColors(
            selectedContainerColor = AnuraTheme.extendedColors.accentInk,
            selectedLabelColor = MaterialTheme.colorScheme.onPrimary,
        ),
    )
}

private fun ExploreObservation.matchesFilters(
    selected: List<String>,
    altitudeMinM: Int?,
    altitudeMaxM: Int?,
    svlMm: Int?,
): Boolean {
    if (selected.isEmpty() && altitudeMinM == null && altitudeMaxM == null && svlMm == null) {
        return true
    }
    fun anyIn(prefix: String, match: (String) -> Boolean): Boolean {
        val group = selected.filter { it.startsWith(prefix) }
        if (group.isEmpty()) return true
        return group.any { match(it.removePrefix(prefix)) }
    }
    val altitudeRange = parseMetricRange(altitude)
    val sizeRange = parseMetricRange(size)
    val altitudeOk = rangesOverlap(altitudeRange, altitudeMinM, altitudeMaxM)
    val sizeOk = svlMm == null || (sizeRange != null && svlMm in sizeRange)
    return anyIn(FilterFamily) { it == family } &&
        anyIn(FilterGenus) { it == genus } &&
        anyIn(FilterDanger) {
            (it == DangerToxic && toxic) || (it == DangerHarmless && !toxic)
        } &&
        anyIn(FilterIucn) { it == iucn?.name } &&
        altitudeOk &&
        sizeOk
}

private fun parseMetric(raw: String): Int? {
    val digits = raw.filter { it.isDigit() }
    return digits.toIntOrNull()
}

private fun parseMetricRange(raw: String): IntRange? {
    val values = Regex("""\d[\d.]*""").findAll(raw).mapNotNull { match ->
        match.value.replace(".", "").toIntOrNull()
    }.toList()
    if (values.isEmpty()) return null
    val start = values.first()
    val end = values.getOrElse(1) { start }
    return minOf(start, end)..maxOf(start, end)
}

private fun rangesOverlap(range: IntRange?, min: Int?, max: Int?): Boolean {
    if (min == null && max == null) return true
    if (range == null) return false
    val low = min ?: Int.MIN_VALUE
    val high = max ?: Int.MAX_VALUE
    val filter = minOf(low, high)..maxOf(low, high)
    return range.first <= filter.last && filter.first <= range.last
}

@AnuraPreviews
@Composable
private fun ExplorePreview() {
    AnuraTheme {
        ExploreScreen(onOpenSpeciesSheet = {}, onOpenSpeciesByTaxon = {}, onOpenExploreMore = {})
    }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun ExplorePreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) {
        ExploreScreen(onOpenSpeciesSheet = {}, onOpenSpeciesByTaxon = {}, onOpenExploreMore = {})
    }
}

/**
 * `explorar → Especies del género o familia` (§4.1, argumento `taxonId`) — la "recopilación de
 * resultados en forma de listado" que aparece al tocar una sugerencia de género o familia en
 * [ExploreScreen]. El filtro de arriba se adapta a lo que hay: si `taxonId` es una familia con
 * más de un género real entre sus especies, aparecen chips por género (calculados de los propios
 * resultados, no una lista fija); si es un género, solo queda el buscador por nombre.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SpeciesByTaxonScreen(
    taxonId: String,
    onBackClick: () -> Unit,
    onOpenSpeciesSheet: (String) -> Unit,
) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val allInGroup = SpeciesCatalog.byTaxon(taxonId)
    val isFamily = taxonId.endsWith("idae", ignoreCase = true) || taxonId.equals("Anura", ignoreCase = true)
    var query by rememberSaveable { mutableStateOf("") }
    var genusFilter by rememberSaveable { mutableStateOf<String?>(null) }
    val genera = remember(allInGroup) { allInGroup.map { it.genus }.distinct().sorted() }
    val needle = query.trim()
    val species = allInGroup.filter { record ->
        (genusFilter == null || record.genus == genusFilter) &&
            (
                needle.isEmpty() ||
                    record.commonName.contains(needle, ignoreCase = true) ||
                    record.scientificName.contains(needle, ignoreCase = true)
                )
    }
    val searchHint = stringResource(
        if (isFamily) R.string.species_by_taxon_search_family else R.string.species_by_taxon_search_genus,
    )
    val allLabel = stringResource(R.string.favorites_filter_all)
    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        topBar = {
            AnuraTopBar(
                title = taxonId,
                onBackClick = onBackClick,
                centerTitle = true,
            )
        },
    ) { innerPadding ->
        if (allInGroup.isEmpty()) {
            // Sin catálogo (sin publicar, sin red o cargando) se dice eso; «sin resultados» solo si el catálogo está listo.
            val catalogReady = ContentCatalog.availability == CatalogAvailability.Ready
            AnuraEmptyState(
                title = if (catalogReady) stringResource(R.string.observations_empty_title) else catalogGapTitle(),
                description = if (catalogReady) searchHint else catalogGapBody(),
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding),
            )
        } else {
            LazyVerticalGrid(
                columns = GridCells.Fixed(2),
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding),
                contentPadding = PaddingValues(AnuraDimens.spaceGutter),
                horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
            ) {
                item(
                    key = "taxon-filters",
                    span = { GridItemSpan(maxLineSpan) },
                ) {
                    Column(verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap)) {
                        AnuraTextField(
                            value = query,
                            onValueChange = { query = it },
                            label = searchHint,
                            modifier = Modifier.fillMaxWidth(),
                            leadingIcon = AnuraIcons.Empty,
                            singleLine = true,
                        )
                        if (isFamily && genera.size > 1) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .horizontalScroll(rememberScrollState()),
                                horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                            ) {
                                ExploreFilterChip(
                                    label = allLabel,
                                    selected = genusFilter == null,
                                    onClick = { genusFilter = null },
                                )
                                genera.forEach { genus ->
                                    ExploreFilterChip(
                                        label = genus,
                                        selected = genusFilter == genus,
                                        onClick = { genusFilter = if (genusFilter == genus) null else genus },
                                    )
                                }
                            }
                        }
                    }
                }
                if (species.isEmpty()) {
                    item(
                        key = "taxon-empty",
                        span = { GridItemSpan(maxLineSpan) },
                    ) {
                        AnuraEmptyState(
                            title = stringResource(R.string.observations_empty_title),
                            description = stringResource(R.string.observations_empty_body),
                        )
                    }
                } else {
                    items(species, key = { it.id }) { record ->
                        ObservationCard(
                            commonName = record.commonName,
                            scientificName = record.scientificName,
                            isFavorite = snapshot.favorites.contains(record.id),
                            onFavoriteClick = { repository.toggleFavorite(record.id) },
                            modifier = Modifier.fillMaxWidth(),
                            thumbnail = {
                                Image(
                                    painter = rememberSpeciesPhotoPainter(record.photoSha256, ContentCatalog.ThumbWidth),
                                    contentDescription = null,
                                    modifier = Modifier.fillMaxSize(),
                                    contentScale = ContentScale.Crop,
                                )
                            },
                            onClick = { onOpenSpeciesSheet(record.id) },
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun ExploreObservation.displayNames(): Pair<String, String> =
    commonName.orEmpty() to scientificName.orEmpty()

private fun ObservationRecord.toExploreObservation(): ExploreObservation? {
    val lat = latitude ?: return null
    val lon = longitude ?: return null
    val species = SpeciesCatalog.find(speciesId)
    return ExploreObservation(
        id = id,
        photoToken = photoTokens.firstOrNull(),
        photoUrl = photoUrl,
        photoSha256 = species?.photoSha256,
        latitude = lat,
        longitude = lon,
        family = species?.family.orEmpty(),
        genus = species?.genus.orEmpty(),
        altitude = species?.altitudeRange.orEmpty(),
        size = svlMm?.let { "$it mm" } ?: species?.sizeRange.orEmpty(),
        toxic = species?.toxicity == AnuraToxicityChipVariant.Toxic,
        iucn = species?.iucn,
        traits = emptySet(),
        commonName = commonName ?: species?.commonName,
        scientificName = scientificName ?: species?.scientificName,
    )
}

/** `GET /api/explorer/feed` — la comunidad real, en vez de `CommunityCatalog`. */
private fun ExplorerFeedItem.toExploreObservation(): ExploreObservation? {
    val lat = lat ?: return null
    val lon = lon ?: return null
    val sci = if (!genus.isNullOrBlank() && !species.isNullOrBlank()) "$genus $species" else ai_class
    val local = sci?.let(SpeciesCatalog::find)
    return ExploreObservation(
        id = id,
        photoUrl = ExplorerRemote.thumbUrl(thumbnail_key ?: image_key),
        photoSha256 = local?.photoSha256,
        latitude = lat,
        longitude = lon,
        family = family ?: local?.family.orEmpty(),
        genus = genus ?: local?.genus.orEmpty(),
        altitude = local?.altitudeRange.orEmpty(),
        size = local?.sizeRange.orEmpty(),
        toxic = local?.toxicity == AnuraToxicityChipVariant.Toxic,
        iucn = local?.iucn,
        traits = emptySet(),
        unsynced = false,
        commonName = common_name ?: local?.commonName,
        scientificName = sci ?: local?.scientificName,
    )
}

private enum class ExploreSuggestionKind { Species, Genus, Family }

private data class ExploreSuggestion(
    val id: String,
    val title: String,
    val subtitle: String,
    val query: String,
    val kind: ExploreSuggestionKind,
)

@Composable
private fun ExploreSuggestionMenu(
    suggestions: List<ExploreSuggestion>,
    onSelect: (ExploreSuggestion) -> Unit,
) {
    AnuraCard(
        modifier = Modifier.fillMaxWidth(),
        bordered = true,
    ) {
        Column(modifier = Modifier.fillMaxWidth()) {
            suggestions.forEach { suggestion ->
                val description = "${suggestion.title}, ${suggestion.subtitle}"
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .heightIn(min = AnuraDimens.sizeTouch)
                        .clickable(role = Role.Button, onClick = { onSelect(suggestion) })
                        .padding(
                            horizontal = AnuraDimens.spaceLabelToContent,
                            vertical = AnuraDimens.spaceGap,
                        )
                        .semantics { contentDescription = description },
                    verticalArrangement = Arrangement.Center,
                ) {
                    Text(
                        text = suggestion.title,
                        style = MaterialTheme.typography.bodyLarge,
                    )
                    Text(
                        text = suggestion.subtitle,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
        }
    }
}

/**
 * El servidor (`GET /api/explorer/suggest`) siempre devuelve filas a nivel de especie — no hay
 * una sugerencia "de género" o "de familia" como tal. Se arman acá, agrupando los géneros y
 * familias DISTINTOS que aparecen entre esas filas reales — sigue siendo dato real, solo
 * reorganizado, nunca inventado. Especies primero (coincidencia más directa), después géneros,
 * después familias; sin duplicados, tope razonable para que quepa en la caja.
 */
private fun groupedTaxonSuggestions(
    remote: List<ExplorerSuggestion>,
    genusLabel: String,
    familyLabel: String,
): List<ExploreSuggestion> {
    val taxa = remote.filter { it.isTaxon }
    val species = taxa.mapNotNull { row ->
        val sci = row.scientific_name?.takeIf { it.isNotBlank() } ?: return@mapNotNull null
        ExploreSuggestion(
            id = "species-$sci",
            title = row.common_name?.takeIf { it.isNotBlank() } ?: sci,
            subtitle = sci,
            query = sci,
            kind = ExploreSuggestionKind.Species,
        )
    }
    val genera = taxa.mapNotNull { it.scientific_name?.substringBefore(' ')?.takeIf { g -> g.isNotBlank() } }
        .distinct()
        .map { genus ->
            ExploreSuggestion(
                id = "genus-$genus",
                title = genus,
                subtitle = genusLabel,
                query = genus,
                kind = ExploreSuggestionKind.Genus,
            )
        }
    val families = taxa.mapNotNull { it.family?.takeIf { f -> f.isNotBlank() } }
        .distinct()
        .map { family ->
            ExploreSuggestion(
                id = "family-$family",
                title = family,
                subtitle = familyLabel,
                query = family,
                kind = ExploreSuggestionKind.Family,
            )
        }
    return (species + genera + families).distinctBy { it.id }.take(8)
}
