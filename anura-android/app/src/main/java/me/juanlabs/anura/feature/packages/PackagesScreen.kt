package me.juanlabs.anura.feature.packages

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.produceState
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.ui.platform.LocalContext
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.platform.LocalInspectionMode
import me.juanlabs.anura.core.data.PackageCatalogState
import me.juanlabs.anura.core.data.PackageNode
import me.juanlabs.anura.core.data.RegionalPackageRecord
import me.juanlabs.anura.core.data.flattenPackages
import me.juanlabs.anura.core.data.findPackage
import me.juanlabs.anura.core.data.RegionalPackageStatus
import me.juanlabs.anura.core.data.hasUsableLocalInstall
import me.juanlabs.anura.core.data.rememberAnuraRepository
import me.juanlabs.anura.designsystem.component.AnuraErrorState
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import kotlin.math.roundToInt
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraConfirmSheet
import me.juanlabs.anura.designsystem.component.AnuraCard
import me.juanlabs.anura.designsystem.component.AnuraEmptyState
import me.juanlabs.anura.designsystem.component.AnuraSectionLabel
import me.juanlabs.anura.designsystem.component.AnuraTopBar
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode
import me.juanlabs.anura.feature.explore.ObservationCatalogScreen

private val ProgressTrackHeight = 8.dp
private val ProgressTrackRadius = 4.dp
private val ZonePinSize = 24.dp

private enum class PackageUiStatus {
    Installed,
    Downloading,
    Available,
    Error,
}

private fun formatPackageSize(bytes: Long): String {
    if (bytes <= 0L) return "0 KB"
    val megabytes = bytes / (1024.0 * 1024.0)
    return when {
        megabytes >= 1024.0 -> "%.1f GB".format(megabytes / 1024.0)
        megabytes >= 10.0 -> "%.0f MB".format(megabytes)
        megabytes >= 1.0 -> "%.1f MB".format(megabytes)
        else -> "${(bytes / 1024L).coerceAtLeast(1L)} KB"
    }
}

private data class PackageRowUi(val node: PackageNode, val depth: Int)

private fun visiblePackageRows(nodes: List<PackageNode>, expanded: Set<String>, depth: Int = 0): List<PackageRowUi> =
    nodes.flatMap { node ->
        val self = listOf(PackageRowUi(node, depth))
        val children = if (node.id in expanded) visiblePackageRows(node.hijos, expanded, depth + 1) else emptyList()
        self + children
    }

private fun aggregateStatus(node: PackageNode, packages: List<RegionalPackageRecord>): Pair<PackageUiStatus, Float> {
    val files = flattenPackages(node).filter { !it.archivoUrl.isNullOrBlank() }
    if (files.isEmpty()) return PackageUiStatus.Available to 0f
    val records = files.map { file -> packages.find { it.id == file.id } }
    if (records.any { it?.status == RegionalPackageStatus.Downloading }) {
        val progress = files.map { file ->
            val record = packages.find { it.id == file.id }
            when {
                record?.status == RegionalPackageStatus.Downloading -> record.progress
                record?.status == RegionalPackageStatus.Installed && record.sha256 == file.sha256 -> 1f
                else -> 0f
            }
        }.average().toFloat()
        return PackageUiStatus.Downloading to progress
    }
    val installed = files.all { file ->
        val record = packages.find { it.id == file.id }
        record?.status == RegionalPackageStatus.Installed && record.sha256 == file.sha256
    }
    if (installed) return PackageUiStatus.Installed to 1f
    if (records.any { it?.status == RegionalPackageStatus.Error }) return PackageUiStatus.Error to 0f
    return PackageUiStatus.Available to 0f
}

/**
 * Paquetes regionales: país, departamento y subregión, con el catálogo del servidor.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RegionalPackagesScreen(
    onBackClick: () -> Unit,
    onOpenObservationDetail: (String) -> Unit = {},
) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val tree by repository.packageTree.collectAsState()
    val catalogState by repository.packageCatalogState.collectAsState()
    val context = LocalContext.current
    val inspection = LocalInspectionMode.current
    var pendingDownloadId by rememberSaveable { mutableStateOf<String?>(null) }
    var pendingDeleteId by rememberSaveable { mutableStateOf<String?>(null) }
    var pendingCancelId by rememberSaveable { mutableStateOf<String?>(null) }
    var openedZoneId by rememberSaveable { mutableStateOf<String?>(null) }
    var expandedRaw by rememberSaveable { mutableStateOf("") }
    val expanded = expandedRaw.split(',').filter { it.isNotBlank() }.toSet()
    var reload by remember { mutableIntStateOf(0) }
    LaunchedEffect(reload) {
        if (!inspection) repository.refreshPackageCatalog()
    }
    val shownTree = if (inspection) previewPackageTree() else tree
    val opened = findPackage(shownTree, openedZoneId.orEmpty())
        ?.takeIf { it.formato == "sqlite" && aggregateStatus(it, snapshot.packages).first == PackageUiStatus.Installed }
    if (opened != null) {
        ObservationCatalogScreen(
            title = opened.nombre,
            onBackClick = { openedZoneId = null },
            onOpenObservationDetail = onOpenObservationDetail,
        )
        return
    }
    fun nodeName(id: String) = findPackage(shownTree, id)?.nombre.orEmpty()
    fun toggle(id: String) {
        val next = expanded.toMutableSet()
        if (!next.add(id)) next.remove(id)
        expandedRaw = next.joinToString(",")
    }

    Scaffold(
        containerColor = AnuraTheme.extendedColors.boardBackground,
        topBar = {
            AnuraTopBar(
                title = stringResource(R.string.packages_title),
                onBackClick = onBackClick,
                centerTitle = true,
            )
        },
    ) { innerPadding ->
        when {
            !inspection && catalogState is PackageCatalogState.Loading -> {
                Text(
                    text = stringResource(R.string.packages_loading),
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(innerPadding)
                        .padding(AnuraDimens.spaceGutter),
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            !inspection && catalogState is PackageCatalogState.Failed -> {
                AnuraErrorState(
                    title = stringResource(R.string.packages_catalog_error),
                    description = (catalogState as PackageCatalogState.Failed).message,
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(innerPadding),
                    onAction = { reload += 1 },
                )
            }
            shownTree.isEmpty() -> {
                AnuraEmptyState(
                    title = stringResource(R.string.packages_empty_title),
                    description = stringResource(R.string.packages_empty_body),
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(innerPadding),
                )
            }
            else -> {
                val rows = visiblePackageRows(shownTree, expanded)
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(innerPadding),
                    contentPadding = PaddingValues(
                        start = AnuraDimens.spaceGutter,
                        end = AnuraDimens.spaceGutter,
                        bottom = AnuraDimens.spaceSection,
                    ),
                    verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
                ) {
                    item(key = "intro") {
                        Text(
                            text = stringResource(R.string.packages_intro),
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                    item(key = "space-used") {
                        val storage by produceState<Pair<Long, Long>?>(null, snapshot.packages) {
                            value = withContext(Dispatchers.IO) {
                                val appBytes = context.filesDir.walkTopDown().filter { it.isFile }.sumOf { it.length() }
                                appBytes to context.filesDir.usableSpace
                            }
                        }
                        SpaceUsedCard(usedBytes = storage?.first, freeBytes = storage?.second)
                    }
                    items(rows, key = { it.node.id }) { row ->
                        val node = row.node
                        val record = snapshot.packages.find { it.id == node.id }
                        val (status, progress) = aggregateStatus(node, snapshot.packages)
                        val kind = when (node.formato) {
                            "sqlite" -> stringResource(R.string.packages_kind_identify)
                            "json" -> stringResource(R.string.packages_kind_catalog)
                            else -> when (node.nivel) {
                                "pais" -> stringResource(R.string.packages_kind_country)
                                "departamento" -> stringResource(R.string.packages_kind_department)
                                else -> stringResource(R.string.packages_kind_catalog)
                            }
                        }
                        val bytes = if (node.formato != null) node.sizeArchivo.takeIf { it > 0 } ?: node.sizeBytes else node.sizeBytes
                        val species = if (node.especies != null) {
                            stringResource(R.string.packages_meta_format, node.especies, formatPackageSize(bytes))
                        } else {
                            null
                        }
                        val meta = listOfNotNull(
                            kind,
                            species,
                            node.version?.takeIf { node.formato != null }?.let { "v$it" },
                            if (species == null) formatPackageSize(bytes) else null,
                        ).joinToString(" · ")
                        PackageRow(
                            name = node.nombre,
                            meta = meta,
                            status = status,
                            progress = progress,
                            active = record?.active == true,
                            depth = row.depth,
                            expandable = node.hijos.isNotEmpty(),
                            expanded = node.id in expanded,
                            showActive = node.formato == "sqlite",
                            canOpen = node.formato == "sqlite" && record?.hasUsableLocalInstall() == true,
                            onToggle = { toggle(node.id) },
                            onOpenClick = { openedZoneId = node.id },
                            onDownloadClick = { pendingDownloadId = node.id },
                            onDeleteClick = {
                                if (status == PackageUiStatus.Downloading) pendingCancelId = node.id else pendingDeleteId = node.id
                            },
                            onRetryClick = {
                                if (isNetworkAvailable(context)) {
                                    repository.downloadPackage(node.id)
                                } else {
                                    flattenPackages(node).filter { it.archivoUrl != null }.forEach { repository.failPackage(it.id) }
                                }
                            },
                            onActiveChange = { shouldBeActive ->
                                if (shouldBeActive) repository.activatePackage(node.id) else repository.deactivatePackage(node.id)
                            },
                        )
                    }
                    item(key = "coverage-note") { CoverageNoteCard() }
                }
            }
        }
    }

    pendingDownloadId?.let { id ->
        val node = findPackage(shownTree, id)
        val includesChildren = node?.hijos?.isNotEmpty() == true
        val downloadBody = stringResource(R.string.packages_download_body, nodeName(id))
        val includesLabel = stringResource(R.string.packages_download_includes)
        AnuraConfirmSheet(
            title = stringResource(R.string.packages_download_title),
            body = if (includesChildren) "$downloadBody $includesLabel" else downloadBody,
            confirmLabel = stringResource(R.string.packages_download),
            onConfirm = {
                if (isNetworkAvailable(context)) {
                    repository.downloadPackage(id)
                } else {
                    val targets = node?.let { flattenPackages(it).filter { file -> file.archivoUrl != null } }.orEmpty()
                    if (targets.isEmpty()) repository.failPackage(id) else targets.forEach { repository.failPackage(it.id) }
                }
                pendingDownloadId = null
            },
            onDismiss = { pendingDownloadId = null },
        )
    }
    pendingDeleteId?.let { id ->
        AnuraConfirmSheet(
            title = stringResource(R.string.packages_delete_title),
            body = stringResource(R.string.packages_delete_body, nodeName(id)),
            confirmLabel = stringResource(R.string.packages_delete),
            onConfirm = {
                repository.uninstallPackage(id)
                pendingDeleteId = null
            },
            onDismiss = { pendingDeleteId = null },
        )
    }
    pendingCancelId?.let { id ->
        AnuraConfirmSheet(
            title = stringResource(R.string.packages_cancel_title),
            body = stringResource(R.string.packages_cancel_body, nodeName(id)),
            confirmLabel = stringResource(R.string.packages_cancel),
            onConfirm = {
                repository.cancelPackage(id)
                pendingCancelId = null
            },
            onDismiss = { pendingCancelId = null },
        )
    }
}

private fun previewPackageTree(): List<PackageNode> = listOf(
    PackageNode(
        id = "colombia",
        nivel = "pais",
        nombre = "Colombia",
        sizeBytes = 9_600_000,
        hijos = listOf(
            PackageNode(
                id = "ANTIOQUIA",
                nivel = "departamento",
                nombre = "Antioquia",
                version = "1.1.0",
                especies = 30,
                formato = "sqlite",
                sizeBytes = 9_510_912,
                sizeArchivo = 9_510_912,
                archivoUrl = "/api/dataset/publico/paquetes/ANTIOQUIA/archivo",
                sha256 = "preview",
                hijos = listOf(
                    PackageNode(
                        id = "ANTIOQUIA.VALLE_DE_ABURRA",
                        nivel = "subregion",
                        nombre = "Valle de Aburrá",
                        version = "2026-09-12",
                        especies = 33,
                        formato = "json",
                        sizeBytes = 12_000,
                        sizeArchivo = 12_000,
                        archivoUrl = "/preview",
                        sha256 = "preview",
                    ),
                ),
            ),
        ),
    ),
)

private fun isNetworkAvailable(context: Context): Boolean {
    val cm = context.getSystemService(ConnectivityManager::class.java) ?: return false
    val network = cm.activeNetwork ?: return false
    val caps = cm.getNetworkCapabilities(network) ?: return false
    return caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
}

@Composable
private fun SpaceUsedCard(usedBytes: Long?, freeBytes: Long?) {
    AnuraCard(
        modifier = Modifier.fillMaxWidth(),
        bordered = true,
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = AnuraDimens.spaceCardInsetHorizontal,
                    vertical = AnuraDimens.spaceCardInsetVertical,
                ),
            verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceLabelToContent),
        ) {
            AnuraSectionLabel(text = stringResource(R.string.packages_space_used))
            if (usedBytes != null && freeBytes != null) {
                Text(
                    text = stringResource(
                        R.string.packages_space_summary,
                        formatPackageSize(usedBytes),
                        formatPackageSize(freeBytes),
                    ),
                    style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.SemiBold),
                    color = MaterialTheme.colorScheme.onSurface,
                )
                ZoneProgressBar(progress = usedBytes.toFloat() / (usedBytes + freeBytes).coerceAtLeast(1L))
            }
        }
    }
}

@Composable
private fun CoverageNoteCard() {
    AnuraCard(modifier = Modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = AnuraDimens.spaceCardInsetHorizontal,
                    vertical = AnuraDimens.spaceCardInsetVertical,
                ),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
        ) {
            Icon(
                imageVector = AnuraIcons.CloudOff,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.size(AnuraDimens.sizeTouch / 2),
            )
            Text(
                text = stringResource(R.string.packages_coverage_note),
                style = MaterialTheme.typography.labelLarge.copy(fontWeight = FontWeight.Medium),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun ZoneProgressBar(progress: Float) {
    LinearProgressIndicator(
        progress = { progress },
        modifier = Modifier
            .fillMaxWidth()
            .height(ProgressTrackHeight)
            .clip(RoundedCornerShape(ProgressTrackRadius)),
        color = AnuraTheme.extendedColors.accentInk,
        trackColor = MaterialTheme.colorScheme.surfaceVariant,
        drawStopIndicator = {},
        gapSize = 0.dp,
    )
}

@Composable
private fun OfflineReadyChip() {
    val label = stringResource(R.string.packages_offline_chip)
    Row(
        modifier = Modifier
            .clip(RoundedCornerShape(AnuraDimens.radiusCapsule))
            .background(MaterialTheme.colorScheme.inverseSurface)
            .padding(horizontal = 10.dp, vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Icon(
            imageVector = AnuraIcons.Check,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.inverseOnSurface,
            modifier = Modifier.size(10.dp),
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
            color = MaterialTheme.colorScheme.inverseOnSurface,
        )
    }
}

@Composable
private fun PackageRow(
    name: String,
    meta: String,
    status: PackageUiStatus,
    progress: Float,
    active: Boolean,
    depth: Int,
    expandable: Boolean,
    expanded: Boolean,
    showActive: Boolean,
    canOpen: Boolean,
    onToggle: () -> Unit,
    onOpenClick: () -> Unit,
    onDownloadClick: () -> Unit,
    onDeleteClick: () -> Unit,
    onRetryClick: () -> Unit,
    onActiveChange: (Boolean) -> Unit,
) {
    val pinActive = status != PackageUiStatus.Available && status != PackageUiStatus.Error
    AnuraCard(
        modifier = Modifier
            .fillMaxWidth()
            .padding(start = (depth * 12).dp),
        bordered = true,
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .then(
                    if (canOpen) Modifier.clickable(role = Role.Button, onClick = onOpenClick) else Modifier,
                )
                .padding(
                    horizontal = AnuraDimens.spaceCardInsetHorizontal,
                    vertical = AnuraDimens.spaceCardInsetVertical,
                ),
            verticalAlignment = Alignment.Top,
            horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
        ) {
            if (expandable) {
                IconButton(onClick = onToggle, modifier = Modifier.size(AnuraDimens.sizeTouch)) {
                    Icon(
                        imageVector = AnuraIcons.ChevronRight,
                        contentDescription = if (expanded) "Cerrar $name" else "Abrir $name",
                        tint = MaterialTheme.colorScheme.onSurface,
                        modifier = Modifier.rotate(if (expanded) 90f else 0f),
                    )
                }
            } else {
                Spacer(modifier = Modifier.size(AnuraDimens.sizeTouch))
            }
            Icon(
                imageVector = AnuraIcons.FieldSession,
                contentDescription = null,
                tint = if (pinActive) {
                    AnuraTheme.extendedColors.accentInk
                } else {
                    MaterialTheme.colorScheme.onSurfaceVariant
                },
                modifier = Modifier.size(ZonePinSize),
            )
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceTitleToSubtitle),
            ) {
                Text(
                    text = name,
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                    color = MaterialTheme.colorScheme.onSurface,
                )
                Text(
                    text = meta,
                    style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Medium),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                if (status == PackageUiStatus.Installed || active) {
                    OfflineReadyChip()
                    if (showActive) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceLabelToContent),
                    ) {
                        Switch(
                            checked = active,
                            onCheckedChange = onActiveChange,
                            colors = SwitchDefaults.colors(checkedTrackColor = AnuraTheme.extendedColors.accentInk),
                        )
                        Text(
                            text = if (active) {
                                stringResource(R.string.packages_active_label)
                            } else {
                                stringResource(R.string.packages_activate)
                            },
                            style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Medium),
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                    }
                }
                if (status == PackageUiStatus.Downloading) {
                    ZoneProgressBar(progress = progress)
                    Text(
                        text = stringResource(R.string.packages_download_progress_format, (progress * 100).roundToInt()),
                        style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Medium),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                if (status == PackageUiStatus.Error) {
                    Text(
                        text = stringResource(R.string.packages_error_title),
                        style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Medium),
                        color = MaterialTheme.colorScheme.error,
                    )
                }
            }
            when (status) {
                PackageUiStatus.Installed -> {
                    IconButton(
                        onClick = onDeleteClick,
                        modifier = Modifier.size(AnuraDimens.sizeTouch),
                    ) {
                        Icon(
                            imageVector = AnuraIcons.Delete,
                            contentDescription = stringResource(R.string.packages_delete_cd, name),
                            tint = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }
                PackageUiStatus.Downloading -> {
                    IconButton(
                        onClick = onDeleteClick,
                        modifier = Modifier.size(AnuraDimens.sizeTouch),
                    ) {
                        Icon(
                            imageVector = AnuraIcons.Close,
                            contentDescription = stringResource(R.string.packages_cancel_download_cd, name),
                            tint = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }
                PackageUiStatus.Available -> {
                    IconButton(
                        onClick = onDownloadClick,
                        modifier = Modifier.size(AnuraDimens.sizeTouch),
                    ) {
                        Icon(
                            imageVector = AnuraIcons.Download,
                            contentDescription = stringResource(R.string.packages_download_cd, name),
                            tint = AnuraTheme.extendedColors.accentInk,
                        )
                    }
                }
                PackageUiStatus.Error -> {
                    IconButton(
                        onClick = onRetryClick,
                        modifier = Modifier.size(AnuraDimens.sizeTouch),
                    ) {
                        Icon(
                            imageVector = AnuraIcons.Download,
                            contentDescription = stringResource(R.string.packages_retry),
                            tint = MaterialTheme.colorScheme.error,
                        )
                    }
                }
            }
        }
    }
}

@AnuraPreviews
@Composable
private fun PackagesPreview() {
    AnuraTheme { RegionalPackagesScreen(onBackClick = {}) }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun PackagesPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) { RegionalPackagesScreen(onBackClick = {}) }
}
