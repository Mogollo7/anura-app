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
import androidx.compose.runtime.mutableStateOf
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
import me.juanlabs.anura.core.data.AnuraPackageManifest
import me.juanlabs.anura.core.data.LocalPackageCatalog
import me.juanlabs.anura.core.data.RegionalPackageStatus
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
    if (bytes <= 0L) return "0 MB"
    val megabytes = bytes / (1024.0 * 1024.0)
    return if (megabytes >= 1024.0) {
        "%.1f GB".format(megabytes / 1024.0)
    } else {
        "%.0f MB".format(megabytes)
    }
}

/**
 * `Zonas descargadas` (Penpot Mockup Final). Descargar/eliminar son pop-ups locales (§4.2).
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RegionalPackagesScreen(
    onBackClick: () -> Unit,
    onOpenObservationDetail: (String) -> Unit = {},
) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val context = LocalContext.current
    var pendingDownloadId by rememberSaveable { mutableStateOf<String?>(null) }
    var pendingDeleteId by rememberSaveable { mutableStateOf<String?>(null) }
    var pendingCancelId by rememberSaveable { mutableStateOf<String?>(null) }
    var openedZoneId by rememberSaveable { mutableStateOf<String?>(null) }
    fun statusOf(id: String): PackageUiStatus {
        val record = snapshot.packages.find { it.id == id }
        return when (record?.status) {
            RegionalPackageStatus.Installed -> PackageUiStatus.Installed
            RegionalPackageStatus.Downloading -> PackageUiStatus.Downloading
            RegionalPackageStatus.Error -> PackageUiStatus.Error
            else -> PackageUiStatus.Available
        }
    }
    val openedZone = LocalPackageCatalog.manifests.firstOrNull { pack ->
        pack.id == openedZoneId && statusOf(pack.id) == PackageUiStatus.Installed
    }
    if (openedZone != null) {
        ObservationCatalogScreen(
            title = openedZone.name,
            onBackClick = { openedZoneId = null },
            onOpenObservationDetail = onOpenObservationDetail,
        )
        return
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
        if (LocalPackageCatalog.manifests.isEmpty()) {
            AnuraEmptyState(
                title = stringResource(R.string.packages_empty_title),
                description = stringResource(R.string.packages_empty_body),
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding),
            )
        } else {
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
                item(key = "space-used") {
                    val storage by produceState<Pair<Long, Long>?>(null, snapshot.packages) {
                        value = withContext(Dispatchers.IO) {
                            val appBytes = context.filesDir.walkTopDown().filter { it.isFile }.sumOf { it.length() }
                            appBytes to context.filesDir.usableSpace
                        }
                    }
                    SpaceUsedCard(usedBytes = storage?.first, freeBytes = storage?.second)
                }
                items(LocalPackageCatalog.manifests, key = { it.id }) { pack ->
                    val record = snapshot.packages.find { it.id == pack.id }
                    val status = statusOf(pack.id)
                    PackageRow(
                        name = pack.name,
                        meta = stringResource(R.string.packages_meta_format, pack.speciesCount, formatPackageSize(pack.sizeBytes)),
                        status = status,
                        progress = record?.progress ?: 0f,
                        active = record?.active == true,
                        onOpenClick = { openedZoneId = pack.id },
                        onDownloadClick = { pendingDownloadId = pack.id },
                        onDeleteClick = {
                            if (status == PackageUiStatus.Downloading) {
                                pendingCancelId = pack.id
                            } else {
                                pendingDeleteId = pack.id
                            }
                        },
                        onRetryClick = {
                            if (isNetworkAvailable(context)) {
                                repository.setPackageDownloading(pack.id)
                            } else {
                                repository.failPackage(pack.id)
                            }
                        },
                        onActiveChange = { shouldBeActive ->
                            if (shouldBeActive) {
                                repository.activatePackage(pack.id)
                            } else {
                                repository.deactivatePackage(pack.id)
                            }
                        },
                    )
                }
                item(key = "coverage-note") {
                    CoverageNoteCard()
                }
            }
        }
    }

    pendingDownloadId?.let { id ->
        val name = LocalPackageCatalog.find(id)?.name.orEmpty()
        AnuraConfirmSheet(
            title = stringResource(R.string.packages_download_title),
            body = stringResource(R.string.packages_download_body, name),
            confirmLabel = stringResource(R.string.packages_download),
            onConfirm = {
                if (isNetworkAvailable(context)) {
                    repository.setPackageDownloading(id)
                } else {
                    repository.failPackage(id)
                }
                pendingDownloadId = null
            },
            onDismiss = { pendingDownloadId = null },
        )
    }
    pendingDeleteId?.let { id ->
        val name = LocalPackageCatalog.find(id)?.name.orEmpty()
        AnuraConfirmSheet(
            title = stringResource(R.string.packages_delete_title),
            body = stringResource(R.string.packages_delete_body, name),
            confirmLabel = stringResource(R.string.packages_delete),
            onConfirm = {
                repository.uninstallPackage(id)
                pendingDeleteId = null
            },
            onDismiss = { pendingDeleteId = null },
        )
    }
    pendingCancelId?.let { id ->
        val name = LocalPackageCatalog.find(id)?.name.orEmpty()
        AnuraConfirmSheet(
            title = stringResource(R.string.packages_cancel_title),
            body = stringResource(R.string.packages_cancel_body, name),
            confirmLabel = stringResource(R.string.packages_cancel),
            onConfirm = {
                repository.cancelPackage(id)
                pendingCancelId = null
            },
            onDismiss = { pendingCancelId = null },
        )
    }
}

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
    onOpenClick: () -> Unit,
    onDownloadClick: () -> Unit,
    onDeleteClick: () -> Unit,
    onRetryClick: () -> Unit,
    onActiveChange: (Boolean) -> Unit,
) {
    val pinActive = status != PackageUiStatus.Available && status != PackageUiStatus.Error
    AnuraCard(
        modifier = Modifier.fillMaxWidth(),
        bordered = true,
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .then(
                    if (status == PackageUiStatus.Installed) {
                        Modifier.clickable(role = Role.Button, onClick = onOpenClick)
                    } else {
                        Modifier
                    },
                )
                .padding(
                    horizontal = AnuraDimens.spaceCardInsetHorizontal,
                    vertical = AnuraDimens.spaceCardInsetVertical,
                ),
            verticalAlignment = Alignment.Top,
            horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
        ) {
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
                if (status == PackageUiStatus.Installed) {
                    OfflineReadyChip()
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
