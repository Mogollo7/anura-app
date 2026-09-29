package me.juanlabs.anura.feature.species

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraEmptyState
import me.juanlabs.anura.core.data.SpeciesCatalog
import me.juanlabs.anura.core.data.SpeciesRecord
import me.juanlabs.anura.core.data.rememberAnuraRepository
import me.juanlabs.anura.core.data.rememberSpeciesPhotoPainter
import me.juanlabs.anura.designsystem.component.AnuraCard
import me.juanlabs.anura.designsystem.component.AnuraConservationChip
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraFormButtonStyle
import me.juanlabs.anura.designsystem.component.AnuraSectionLabel
import me.juanlabs.anura.designsystem.component.AnuraTopBar
import me.juanlabs.anura.designsystem.component.AnuraToxicityChip
import me.juanlabs.anura.designsystem.component.ObservationCard
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode
import me.juanlabs.anura.feature.observations.ObservationMediaCarousel
import me.juanlabs.anura.feature.observations.ObservationMediaItem

private enum class SpeciesSheetTab {
    Distribution,
    Morphology,
    Bioacoustics,
    Taxonomy,
    Similars,
}

private enum class SpeciesTaxonRank {
    Species,
    Genus,
    Family,
    Order,
}

private fun speciesTaxonRank(speciesId: String): SpeciesTaxonRank = when {
    speciesId.startsWith("COL_ANURA_") || speciesId.startsWith("ANU_") -> SpeciesTaxonRank.Species
    speciesId.equals("Anura", ignoreCase = true) -> SpeciesTaxonRank.Order
    speciesId.endsWith("idae", ignoreCase = true) -> SpeciesTaxonRank.Family
    else -> SpeciesTaxonRank.Genus
}

private data class IdentifierPerson(
    val id: String,
    val nameRes: Int,
    val handleRes: Int,
    val identifications: Int,
)

private val IdentifierPeople = listOf(
    IdentifierPerson("user-camila", R.string.connections_person_1_name, R.string.connections_person_1_handle, 214),
    IdentifierPerson("user-julian", R.string.connections_person_2_name, R.string.connections_person_2_handle, 187),
    IdentifierPerson("user-vale", R.string.connections_person_3_name, R.string.connections_person_3_handle, 156),
    IdentifierPerson("user-andres", R.string.connections_person_4_name, R.string.connections_person_4_handle, 132),
    IdentifierPerson("user-laura", R.string.connections_person_5_name, R.string.connections_person_5_handle, 98),
    IdentifierPerson("user-mateo", R.string.identifiers_person_6_name, R.string.identifiers_person_6_handle, 74),
)

private val IdentifierFollowButtonWidth = 96.dp
private val IdentifierAvatarSize = 48.dp

/**
 * `ESPECIE, FAMILIA, GENERO` (ficha técnica, §4.1).
 * Secciones son estado local, no rutas.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SpeciesSheetScreen(
    speciesId: String,
    onBackClick: () -> Unit,
    onOpenTaxon: (String) -> Unit = {},
    onOpenSpeciesSheet: (String) -> Unit = {},
    onOpenSpeciesByTaxon: (String) -> Unit = {},
    onOpenProfile: (String) -> Unit = {},
    onGoHome: () -> Unit = onBackClick,
) {
    var tab by rememberSaveable(speciesId) { mutableStateOf(SpeciesSheetTab.Distribution) }
    var showIdentifiers by rememberSaveable { mutableStateOf(false) }
    val rank = speciesTaxonRank(speciesId)
    val species = SpeciesCatalog.find(speciesId)
        ?: SpeciesCatalog.findGroup(speciesId).takeIf { rank != SpeciesTaxonRank.Species }
    if (species == null) {
        // Sin ficha para ese id: se dice, no se muestra otra especie en su lugar.
        Scaffold(
            containerColor = AnuraTheme.extendedColors.boardBackground,
            topBar = {
                AnuraTopBar(
                    title = stringResource(R.string.species_sheet_title),
                    onBackClick = onBackClick,
                    centerTitle = true,
                )
            },
        ) { innerPadding ->
            AnuraEmptyState(
                title = stringResource(R.string.species_not_found_title),
                description = stringResource(R.string.species_not_found_body),
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding),
            )
        }
        return
    }
    val groupMembers = when (rank) {
        SpeciesTaxonRank.Species -> emptyList()
        SpeciesTaxonRank.Genus,
        SpeciesTaxonRank.Family,
        SpeciesTaxonRank.Order -> SpeciesCatalog.byTaxon(speciesId)
    }
    val speciesCount = groupMembers.size
    val generaCount = groupMembers.map { it.genus }.distinct().size
    val familyCount = groupMembers.map { it.family }.distinct().size
    val distributionTaxonIds = when (rank) {
        SpeciesTaxonRank.Species -> listOf(species.id)
        SpeciesTaxonRank.Genus,
        SpeciesTaxonRank.Family,
        SpeciesTaxonRank.Order -> SpeciesCatalog.byTaxon(speciesId).map { it.id }
    }

    if (showIdentifiers) {
        IdentifiersHighlightedScreen(
            onBackClick = { showIdentifiers = false },
            onOpenProfile = onOpenProfile,
        )
        return
    }

    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        topBar = {
            AnuraTopBar(
                title = stringResource(R.string.species_sheet_title),
                onBackClick = onBackClick,
                centerTitle = true,
                actions = {
                    IconButton(
                        onClick = onGoHome,
                        modifier = Modifier.size(AnuraDimens.sizeTouch),
                    ) {
                        Icon(
                            imageVector = AnuraIcons.Close,
                            contentDescription = stringResource(R.string.species_sheet_close_home_cd),
                        )
                    }
                },
            )
        },
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(horizontal = AnuraDimens.spaceGutter)
                .padding(bottom = 16.dp),
        ) {
            ObservationMediaCarousel(
                items = speciesPhotoItems(species, rank, speciesId),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(220.dp),
            )
            // Crédito de la foto publicada: las licencias CC exigen atribución visible.
            if (rank == SpeciesTaxonRank.Species && species.photoSha256 != null && !species.photoCredit.isNullOrBlank()) {
                Text(
                    text = stringResource(R.string.species_sheet_photo_credit, species.photoCredit),
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(top = 4.dp),
                )
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            Text(
                text = species.commonName,
                style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
            )
            Text(
                text = species.scientificName,
                style = MaterialTheme.typography.titleMedium.copy(fontStyle = FontStyle.Italic),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            TaxonomyBreadcrumb(
                rank = rank,
                order = species.order,
                family = species.family,
                genus = species.genus,
                onOpenTaxon = onOpenTaxon,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            Row(horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap)) {
                if (species.toxicityDeclared) {
                    AnuraToxicityChip(variant = species.toxicity)
                }
                AnuraConservationChip(variant = species.iucn)
            }
            if (rank == SpeciesTaxonRank.Species && species.isPublished && species.curiousFact.isNotBlank()) {
                Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
                Text(
                    text = species.curiousFact,
                    style = MaterialTheme.typography.bodyMedium.copy(fontStyle = FontStyle.Italic),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            // Un dato vacío no se muestra (ficha publicada sin altitud o sin LHC): nada de "—".
            val hasValue = { v: String -> v.isNotBlank() && v != "—" }
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceActionGap),
            ) {
                if (hasValue(species.catalogObservationCount)) {
                    SpeciesStatCard(
                        value = species.catalogObservationCount,
                        label = stringResource(R.string.species_sheet_stat_observations_label),
                        modifier = Modifier.weight(1f),
                    )
                }
                if (hasValue(species.altitudeRange)) {
                    SpeciesStatCard(
                        value = species.altitudeRange,
                        label = stringResource(R.string.species_sheet_stat_altitude_label),
                        modifier = Modifier.weight(1f),
                    )
                }
                if (hasValue(species.sizeRange)) {
                    SpeciesStatCard(
                        value = species.sizeRange,
                        label = stringResource(R.string.species_sheet_stat_size_label),
                        modifier = Modifier.weight(1f),
                    )
                }
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceActionGap),
            ) {
                if (hasValue(species.catalogObserverCount)) {
                    SpeciesStatCard(
                        value = species.catalogObserverCount,
                        label = stringResource(R.string.species_sheet_stat_observers_label),
                        onClick = { showIdentifiers = true },
                        modifier = Modifier.weight(1f),
                    )
                }
                if (rank == SpeciesTaxonRank.Family || rank == SpeciesTaxonRank.Order) {
                    SpeciesStatCard(
                        value = generaCount.toString(),
                        label = stringResource(R.string.species_sheet_stat_genera_label),
                        onClick = { onOpenSpeciesByTaxon(speciesId) },
                        modifier = Modifier.weight(1f),
                    )
                }
                if (rank == SpeciesTaxonRank.Genus ||
                    rank == SpeciesTaxonRank.Family ||
                    rank == SpeciesTaxonRank.Order
                ) {
                    SpeciesStatCard(
                        value = speciesCount.toString(),
                        label = stringResource(R.string.species_sheet_stat_species_label),
                        onClick = { onOpenSpeciesByTaxon(speciesId) },
                        modifier = Modifier.weight(1f),
                    )
                }
            }
            if (rank == SpeciesTaxonRank.Order) {
                Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
                SpeciesStatCard(
                    value = familyCount.toString(),
                    label = stringResource(R.string.species_sheet_stat_families_label),
                    onClick = { onOpenSpeciesByTaxon(speciesId) },
                    modifier = Modifier.fillMaxWidth(),
                )
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            Row(
                modifier = Modifier.horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceActionGap),
            ) {
                SpeciesTabChip(
                    label = stringResource(R.string.species_sheet_tab_distribution),
                    selected = tab == SpeciesSheetTab.Distribution,
                    onClick = { tab = SpeciesSheetTab.Distribution },
                )
                SpeciesTabChip(
                    label = stringResource(R.string.species_sheet_tab_morphology),
                    selected = tab == SpeciesSheetTab.Morphology,
                    onClick = { tab = SpeciesSheetTab.Morphology },
                )
                SpeciesTabChip(
                    label = stringResource(R.string.species_sheet_tab_bioacoustics),
                    selected = tab == SpeciesSheetTab.Bioacoustics,
                    onClick = { tab = SpeciesSheetTab.Bioacoustics },
                )
                if (rank != SpeciesTaxonRank.Species) {
                    SpeciesTabChip(
                        label = stringResource(R.string.species_sheet_tab_taxonomy),
                        selected = tab == SpeciesSheetTab.Taxonomy,
                        onClick = { tab = SpeciesSheetTab.Taxonomy },
                    )
                }
                SpeciesTabChip(
                    label = stringResource(R.string.species_sheet_tab_similars),
                    selected = tab == SpeciesSheetTab.Similars,
                    onClick = { tab = SpeciesSheetTab.Similars },
                )
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            when (tab) {
                SpeciesSheetTab.Distribution -> DistributionSection(taxonIds = distributionTaxonIds)
                SpeciesSheetTab.Morphology -> MorphologySection(species)
                SpeciesSheetTab.Bioacoustics -> BioacousticsSection()
                SpeciesSheetTab.Taxonomy -> if (rank != SpeciesTaxonRank.Species) {
                    TaxonomyTreeSection(
                        rank = rank,
                        taxonId = speciesId,
                        family = species.family,
                        onOpenTaxon = onOpenTaxon,
                        onOpenSpeciesSheet = onOpenSpeciesSheet,
                    )
                }
                SpeciesSheetTab.Similars -> SimilarsSection(
                    species = species,
                    onOpenSpeciesSheet = onOpenSpeciesSheet,
                )
            }
        }
    }
}

/**
 * Ficha de especie: solo su propia foto (las especies similares se comparan en la pestaña
 * "Similares", no acá). Ficha de género/familia/orden: una foto de cada especie miembro —
 * "el carrusel tiene las fotos de ejemplares de esa familia o género, 1 de cada uno".
 */
private fun speciesPhotoItems(species: SpeciesRecord, rank: SpeciesTaxonRank, taxonId: String): List<ObservationMediaItem> {
    if (rank != SpeciesTaxonRank.Species) {
        return SpeciesCatalog.byTaxon(taxonId).mapIndexed { index, record ->
            ObservationMediaItem.Photo("member-$index", record.photoRes, record.photoSha256)
        }
    }
    return listOf(ObservationMediaItem.Photo("hero", species.photoRes, species.photoSha256))
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun TaxonomyBreadcrumb(
    rank: SpeciesTaxonRank,
    order: String,
    family: String,
    genus: String,
    onOpenTaxon: (String) -> Unit,
) {
    val sep = stringResource(R.string.species_sheet_taxon_sep)
    val showFamily = rank != SpeciesTaxonRank.Order
    val showGenus = rank == SpeciesTaxonRank.Species
    FlowRow(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(4.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        if (rank == SpeciesTaxonRank.Order) {
            Text(
                text = order,
                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        } else {
            TaxonLink(label = order, onClick = { onOpenTaxon(order) })
        }
        if (showFamily) {
            Text(
                text = sep,
                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            if (rank == SpeciesTaxonRank.Family) {
                Text(
                    text = family,
                    style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            } else {
                TaxonLink(label = family, onClick = { onOpenTaxon(family) })
            }
        }
        if (showGenus) {
            Text(
                text = sep,
                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            TaxonLink(label = genus, onClick = { onOpenTaxon(genus) })
        }
    }
}

@Composable
private fun TaxonLink(label: String, onClick: () -> Unit) {
    Text(
        text = label,
        style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
        color = AnuraTheme.extendedColors.accentInk,
        modifier = Modifier
            .clip(RoundedCornerShape(AnuraDimens.radiusButton))
            .clickable(onClick = onClick)
            .semantics { role = Role.Button },
    )
}

@Composable
private fun DistributionSection(taxonIds: List<String>) {
    val repository = rememberAnuraRepository()
    val queued = stringResource(R.string.species_range_queued)
    GeographicLocationSection(taxonIds = taxonIds)
    Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
    AnuraFormButton(
        text = stringResource(R.string.species_sheet_download_range),
        onClick = { repository.notify(queued) },
        style = AnuraFormButtonStyle.Outline,
        icon = AnuraIcons.Download,
    )
}

/**
 * Morfología de la ficha publicada (Admin → Contenido). Antes esta pestaña mostraba el texto de
 * ejemplo de Penpot (el de *D. truncatus*) en TODAS las especies; ahora, sin ficha revisada,
 * lo dice y no muestra nada inventado.
 */
@Composable
private fun MorphologySection(species: SpeciesRecord) {
    val repository = rememberAnuraRepository()
    val exported = stringResource(R.string.species_export_ready)
    Text(
        text = stringResource(R.string.species_sheet_morphology_title),
        style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
    )
    val m = species.morphology
    val lines = listOfNotNull(
        m?.timpano?.let { R.string.species_sheet_tympanum to it },
        m?.discos?.let { R.string.species_sheet_disc to it },
        m?.pliegues?.let { R.string.species_sheet_fold to it },
        m?.patron_dorsal?.let { R.string.species_sheet_dorsal to it },
        m?.patron_ventral?.let { R.string.species_sheet_ventral to it },
        m?.membranas?.let { R.string.species_sheet_webbing to it },
        species.sizeRange.takeIf { species.isPublished && it.isNotBlank() }?.let { R.string.species_sheet_svl to it },
    )
    if (lines.isEmpty() && m?.diagnosticos.isNullOrEmpty()) {
        Text(
            text = stringResource(R.string.species_sheet_morphology_empty),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(top = AnuraDimens.spaceGap),
        )
        return
    }
    lines.forEach { (label, value) -> RecordLine(label = stringResource(label), value = value) }
    m?.diagnosticos?.takeIf { it.isNotEmpty() }?.let { rasgos ->
        RecordLine(
            label = stringResource(R.string.species_sheet_diagnostics),
            value = rasgos.joinToString("\n") { "• $it" },
        )
    }
    Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
    AnuraFormButton(
        text = stringResource(R.string.species_sheet_export),
        onClick = { repository.notify(exported) },
        style = AnuraFormButtonStyle.Outline,
    )
}

@Composable
private fun BioacousticsSection() {
    SpeciesAudioRow(
        title = stringResource(R.string.species_sheet_audio_1),
        meta = stringResource(R.string.species_sheet_audio_1_meta),
        durationMs = 14_000,
    )
    Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
    SpeciesAudioRow(
        title = stringResource(R.string.species_sheet_audio_2),
        meta = stringResource(R.string.species_sheet_audio_2_meta),
        durationMs = 9_000,
    )
}

@Composable
private fun SpeciesAudioRow(
    title: String,
    meta: String,
    durationMs: Int,
) {
    var playing by rememberSaveable(title) { mutableStateOf(false) }
    var positionMs by rememberSaveable(title) { mutableIntStateOf(0) }
    LaunchedEffect(playing) {
        if (!playing) return@LaunchedEffect
        while (playing) {
            delay(50)
            val next = positionMs + 50
            if (next >= durationMs) {
                positionMs = durationMs
                playing = false
            } else {
                positionMs = next
            }
        }
    }
    AnuraCard(modifier = Modifier.fillMaxWidth(), bordered = true) {
        Row(
            modifier = Modifier.padding(
                horizontal = AnuraDimens.spaceGap,
                vertical = AnuraDimens.spaceGap,
            ),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                )
                Text(
                    text = meta,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            Spacer(modifier = Modifier.width(AnuraDimens.spaceGap))
            AudioRingButton(
                playing = playing,
                progress = positionMs / durationMs.toFloat(),
                contentDescription = stringResource(
                    if (playing) R.string.species_sheet_stop_cd else R.string.species_sheet_play_cd,
                    title,
                ),
                onClick = {
                    if (positionMs >= durationMs) positionMs = 0
                    playing = !playing
                },
            )
        }
    }
}

@Composable
private fun AudioRingButton(
    playing: Boolean,
    progress: Float,
    contentDescription: String,
    onClick: () -> Unit,
) {
    val track = MaterialTheme.colorScheme.outlineVariant
    val played = AnuraTheme.extendedColors.accentInk
    Box(
        modifier = Modifier.size(AnuraDimens.sizeTouch),
        contentAlignment = Alignment.Center,
    ) {
        Canvas(modifier = Modifier.size(AnuraDimens.sizeTouch)) {
            val stroke = 4.dp.toPx()
            val inset = stroke / 2f
            val arcSize = Size(size.width - stroke, size.height - stroke)
            val topLeft = Offset(inset, inset)
            drawArc(
                color = track,
                startAngle = -90f,
                sweepAngle = 360f,
                useCenter = false,
                topLeft = topLeft,
                size = arcSize,
                style = Stroke(width = stroke, cap = StrokeCap.Round),
            )
            drawArc(
                color = played,
                startAngle = -90f,
                sweepAngle = 360f * progress.coerceIn(0f, 1f),
                useCenter = false,
                topLeft = topLeft,
                size = arcSize,
                style = Stroke(width = stroke, cap = StrokeCap.Round),
            )
        }
        IconButton(
            onClick = onClick,
            modifier = Modifier
                .size(AnuraDimens.sizeTouch)
                .clip(CircleShape),
        ) {
            Icon(
                imageVector = if (playing) AnuraIcons.Stop else AnuraIcons.Play,
                contentDescription = contentDescription,
                tint = AnuraTheme.extendedColors.accentInk,
            )
        }
    }
}

/**
 * No existe para fichas de especie (esas van directo a "Similares"). En ficha de género:
 * solo las especies de ese género. En ficha de familia: sus géneros y, dentro de cada uno,
 * las especies de ese género — nunca especies de otra familia.
 */
@Composable
private fun TaxonomyTreeSection(
    rank: SpeciesTaxonRank,
    taxonId: String,
    family: String,
    onOpenTaxon: (String) -> Unit,
    onOpenSpeciesSheet: (String) -> Unit,
) {
    Text(
        text = stringResource(R.string.species_sheet_taxonomy_title),
        style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
    )
    Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
    if (rank == SpeciesTaxonRank.Genus) {
        val members = remember(taxonId) { SpeciesCatalog.byTaxon(taxonId).sortedBy { it.scientificName } }
        TaxonNode(label = taxonId, emphasized = true, onClick = { onOpenTaxon(taxonId) })
        Column(modifier = Modifier.padding(start = 16.dp)) {
            members.forEach { record ->
                TaxonNode(label = record.scientificName, onClick = { onOpenSpeciesSheet(record.id) })
            }
        }
        return
    }
    val byGenus = remember(family) {
        SpeciesCatalog.byTaxon(family).groupBy { it.genus }.toSortedMap()
    }
    TaxonNode(label = family, emphasized = true, onClick = { onOpenTaxon(family) })
    Column(modifier = Modifier.padding(start = 16.dp)) {
        byGenus.forEach { (genus, members) ->
            Spacer(modifier = Modifier.height(AnuraDimens.spaceLabelToContent))
            TaxonNode(label = genus, onClick = { onOpenTaxon(genus) })
            Column(modifier = Modifier.padding(start = 16.dp)) {
                members.sortedBy { it.scientificName }.forEach { record ->
                    TaxonNode(label = record.scientificName, onClick = { onOpenSpeciesSheet(record.id) })
                }
            }
        }
    }
}

@Composable
private fun TaxonNode(
    label: String,
    emphasized: Boolean = false,
    highlighted: Boolean = false,
    onClick: () -> Unit,
) {
    Text(
        text = label,
        style = if (emphasized) {
            MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.Bold)
        } else {
            MaterialTheme.typography.bodyMedium.copy(
                fontStyle = FontStyle.Italic,
                fontWeight = if (highlighted) FontWeight.Bold else FontWeight.Normal,
            )
        },
        color = if (highlighted) AnuraTheme.extendedColors.accentInk else MaterialTheme.colorScheme.onSurface,
        modifier = Modifier
            .clip(RoundedCornerShape(AnuraDimens.radiusButton))
            .clickable(onClick = onClick)
            .semantics { role = Role.Button }
            .padding(vertical = 4.dp),
    )
}

@Composable
private fun SimilarsSection(
    species: SpeciesRecord,
    onOpenSpeciesSheet: (String) -> Unit,
) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val similars = species.similarIds.mapNotNull { SpeciesCatalog.find(it) }
    if (similars.isEmpty()) {
        Text(
            text = stringResource(R.string.anura_value_missing),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        return
    }
    similars.chunked(2).forEach { row ->
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
        ) {
            row.forEach { record ->
                SimilarCard(
                    common = record.commonName,
                    scientific = record.scientificName,
                    imageRes = record.photoRes,
                    photoSha256 = record.photoSha256,
                    favorite = snapshot.favorites.contains(record.id),
                    onFavorite = { repository.toggleFavorite(record.id) },
                    onClick = { onOpenSpeciesSheet(record.id) },
                    modifier = Modifier.weight(1f),
                )
            }
            if (row.size == 1) {
                Spacer(modifier = Modifier.weight(1f))
            }
        }
        Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
    }
}

@Composable
private fun SimilarCard(
    common: String,
    scientific: String,
    imageRes: Int,
    photoSha256: String?,
    favorite: Boolean,
    onFavorite: () -> Unit,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    ObservationCard(
        commonName = common,
        scientificName = scientific,
        isFavorite = favorite,
        onFavoriteClick = onFavorite,
        modifier = modifier,
        thumbnail = {
            // Respaldo local visible al instante; la foto publicada real entra sola cuando
            // termina de bajar, sin bloquear la lista (K2, mismo patrón de ContentCatalog).
            Image(
                painter = rememberSpeciesPhotoPainter(photoSha256, imageRes),
                contentDescription = null,
                modifier = Modifier.fillMaxSize(),
                contentScale = ContentScale.Crop,
            )
        },
        onClick = onClick,
    )
}

@Composable
private fun RecordLine(label: String, value: String) {
    Column(modifier = Modifier.padding(vertical = AnuraDimens.spaceLabelToContent)) {
        AnuraSectionLabel(text = label)
        Text(text = value, style = MaterialTheme.typography.titleMedium)
    }
}

@Composable
private fun SpeciesStatCard(
    value: String,
    label: String,
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
) {
    AnuraCard(
        modifier = if (onClick != null) {
            modifier.clickable(role = Role.Button, onClick = onClick)
        } else {
            modifier
        },
        bordered = true,
    ) {
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

@Composable
private fun SpeciesTabChip(
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

@Composable
private fun SheetPill(text: String, warning: Boolean) {
    val bg = if (warning) AnuraTheme.extendedColors.warning else AnuraTheme.extendedColors.success
    val fg = if (warning) AnuraTheme.extendedColors.onWarning else AnuraTheme.extendedColors.onSuccess
    Text(
        text = text,
        style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
        color = fg,
        modifier = Modifier
            .clip(RoundedCornerShape(AnuraDimens.radiusCapsule))
            .background(bg)
            .padding(horizontal = 10.dp, vertical = 4.dp),
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun IdentifiersHighlightedScreen(
    onBackClick: () -> Unit,
    onOpenProfile: (String) -> Unit,
) {
    var query by rememberSaveable { mutableStateOf("") }
    val followingById = remember {
        mutableStateMapOf<String, Boolean>().apply {
            IdentifierPeople.forEach { put(it.id, false) }
        }
    }
    val needle = query.trim()
    val people = IdentifierPeople.filter { person ->
        if (needle.isEmpty()) {
            true
        } else {
            val name = stringResource(person.nameRes)
            val handle = stringResource(person.handleRes)
            name.contains(needle, ignoreCase = true) || handle.contains(needle, ignoreCase = true)
        }
    }
    val searchHint = stringResource(R.string.identifiers_search)
    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        topBar = {
            AnuraTopBar(
                title = stringResource(R.string.identifiers_title),
                onBackClick = onBackClick,
            )
        },
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(horizontal = AnuraDimens.spaceGutter),
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(MaterialTheme.colorScheme.surface),
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .heightIn(min = AnuraDimens.sizeTouch)
                        .padding(horizontal = AnuraDimens.spaceGap),
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
                            .semantics { contentDescription = searchHint },
                        textStyle = MaterialTheme.typography.bodyMedium.copy(
                            color = MaterialTheme.colorScheme.onSurface,
                        ),
                        singleLine = true,
                        cursorBrush = SolidColor(MaterialTheme.colorScheme.primary),
                        decorationBox = { inner ->
                            if (query.isEmpty()) {
                                Text(
                                    text = searchHint,
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                )
                            }
                            inner()
                        },
                    )
                }
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(bottom = AnuraDimens.spaceSection),
                verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
            ) {
                items(people, key = { it.id }) { person ->
                    IdentifierPersonRow(
                        person = person,
                        following = followingById[person.id] == true,
                        onFollowClick = {
                            followingById[person.id] = followingById[person.id] != true
                        },
                        onOpenProfile = { onOpenProfile(person.id) },
                    )
                }
            }
        }
    }
}

@Composable
private fun IdentifierPersonRow(
    person: IdentifierPerson,
    following: Boolean,
    onFollowClick: () -> Unit,
    onOpenProfile: () -> Unit,
) {
    val handle = stringResource(person.handleRes)
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(role = Role.Button, onClick = onOpenProfile),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
    ) {
        Box(
            modifier = Modifier
                .size(IdentifierAvatarSize)
                .clip(CircleShape)
                .background(MaterialTheme.colorScheme.surfaceVariant),
            contentAlignment = Alignment.Center,
        ) {
            Icon(
                imageVector = AnuraIcons.Person,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.size(IdentifierAvatarSize / 2),
            )
        }
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = stringResource(person.nameRes),
                style = MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.Bold),
                color = MaterialTheme.colorScheme.onSurface,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
            Text(
                text = stringResource(R.string.identifiers_meta, handle, person.identifications),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis,
            )
        }
        Button(
            onClick = onFollowClick,
            modifier = Modifier
                .width(IdentifierFollowButtonWidth)
                .heightIn(min = AnuraDimens.sizeTouch),
            shape = RoundedCornerShape(18.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = AnuraTheme.extendedColors.accentInk,
                contentColor = MaterialTheme.colorScheme.onPrimary,
            ),
            contentPadding = PaddingValues(horizontal = 8.dp, vertical = 8.dp),
        ) {
            Text(
                text = if (following) {
                    stringResource(R.string.connections_following)
                } else {
                    stringResource(R.string.observation_author_follow)
                },
                style = MaterialTheme.typography.labelLarge.copy(fontWeight = FontWeight.SemiBold),
                maxLines = 1,
            )
        }
    }
}

@AnuraPreviews
@Composable
private fun SpeciesSheetPreview() {
    AnuraTheme { SpeciesSheetScreen(speciesId = "ANU_COL_PRIS_PAI_001", onBackClick = {}) }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun SpeciesSheetPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) {
        SpeciesSheetScreen(speciesId = "ANU_COL_PRIS_PAI_001", onBackClick = {})
    }
}
