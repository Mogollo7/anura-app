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
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraBottomSheet
import me.juanlabs.anura.designsystem.component.AnuraCard
import me.juanlabs.anura.designsystem.component.AnuraEmptyState
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraFormButtonStyle
import me.juanlabs.anura.designsystem.component.AnuraSectionLabel
import me.juanlabs.anura.designsystem.component.AnuraTopBar
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode
import me.juanlabs.anura.feature.explore.ObservationCatalogScreen

private const val EjePackageId = "EJE"
private const val ChocoPackageId = "CHOCO"
private val StorageUsedFraction = 0.15f
private val DownloadProgressFraction = 0.64f
private val ProgressTrackHeight = 8.dp
private val ProgressTrackRadius = 4.dp
private val ZonePinSize = 24.dp

private enum class PackageUiStatus {
    Installed,
    Downloading,
    Available,
}

private data class RegionalPackage(
    val id: String,
    val nameRes: Int,
    val metaRes: Int,
)

private val CatalogPackages = listOf(
    RegionalPackage(EjePackageId, R.string.packages_eje_cafetero, R.string.packages_eje_meta),
    RegionalPackage(ChocoPackageId, R.string.packages_choco, R.string.packages_choco_meta),
    RegionalPackage("AMAZONIA", R.string.packages_amazonia, R.string.packages_amazonia_meta),
    RegionalPackage("SIERRA", R.string.packages_sierra, R.string.packages_sierra_meta),
)

/**
 * `Zonas descargadas` (Penpot Mockup Final). Descargar/eliminar son pop-ups locales (§4.2).
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RegionalPackagesScreen(
    onBackClick: () -> Unit,
    onOpenObservationDetail: (String) -> Unit = {},
) {
    var installedIds by rememberSaveable { mutableStateOf(listOf(EjePackageId)) }
    var downloadingIds by rememberSaveable { mutableStateOf(listOf(ChocoPackageId)) }
    var pendingDownloadId by rememberSaveable { mutableStateOf<String?>(null) }
    var pendingDeleteId by rememberSaveable { mutableStateOf<String?>(null) }
    var openedZoneId by rememberSaveable { mutableStateOf<String?>(null) }
    val openedZone = CatalogPackages.firstOrNull { pack ->
        pack.id == openedZoneId && statusOf(pack.id, installedIds, downloadingIds) == PackageUiStatus.Installed
    }
    if (openedZone != null) {
        ObservationCatalogScreen(
            title = stringResource(openedZone.nameRes),
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
        if (CatalogPackages.isEmpty()) {
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
                    SpaceUsedCard()
                }
                items(CatalogPackages, key = { it.id }) { pack ->
                    val status = statusOf(pack.id, installedIds, downloadingIds)
                    PackageRow(
                        name = stringResource(pack.nameRes),
                        meta = stringResource(pack.metaRes),
                        status = status,
                        onOpenClick = { openedZoneId = pack.id },
                        onDownloadClick = { pendingDownloadId = pack.id },
                        onDeleteClick = { pendingDeleteId = pack.id },
                    )
                }
                item(key = "coverage-note") {
                    CoverageNoteCard()
                }
            }
        }
    }

    pendingDownloadId?.let { id ->
        val name = CatalogPackages.first { it.id == id }.nameRes
        PackageConfirmSheet(
            title = stringResource(R.string.packages_download_title),
            body = stringResource(R.string.packages_download_body, stringResource(name)),
            confirmLabel = stringResource(R.string.packages_download),
            onConfirm = {
                installedIds = (installedIds + id).distinct()
                downloadingIds = downloadingIds - id
                pendingDownloadId = null
            },
            onDismiss = { pendingDownloadId = null },
        )
    }
    pendingDeleteId?.let { id ->
        val name = CatalogPackages.first { it.id == id }.nameRes
        PackageConfirmSheet(
            title = stringResource(R.string.packages_delete_title),
            body = stringResource(R.string.packages_delete_body, stringResource(name)),
            confirmLabel = stringResource(R.string.packages_delete),
            onConfirm = {
                installedIds = installedIds - id
                downloadingIds = downloadingIds - id
                pendingDeleteId = null
            },
            onDismiss = { pendingDeleteId = null },
        )
    }
}

private fun statusOf(
    id: String,
    installedIds: List<String>,
    downloadingIds: List<String>,
): PackageUiStatus = when {
    downloadingIds.contains(id) -> PackageUiStatus.Downloading
    installedIds.contains(id) -> PackageUiStatus.Installed
    else -> PackageUiStatus.Available
}

@Composable
private fun SpaceUsedCard() {
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
            Text(
                text = stringResource(R.string.packages_space_summary),
                style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.SemiBold),
                color = MaterialTheme.colorScheme.onSurface,
            )
            ZoneProgressBar(progress = StorageUsedFraction)
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
    onOpenClick: () -> Unit,
    onDownloadClick: () -> Unit,
    onDeleteClick: () -> Unit,
) {
    val pinActive = status != PackageUiStatus.Available
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
                }
                if (status == PackageUiStatus.Downloading) {
                    ZoneProgressBar(progress = DownloadProgressFraction)
                    Text(
                        text = stringResource(R.string.packages_download_progress),
                        style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Medium),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
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
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun PackageConfirmSheet(
    title: String,
    body: String,
    confirmLabel: String,
    onConfirm: () -> Unit,
    onDismiss: () -> Unit,
) {
    AnuraBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = AnuraDimens.spacePopupInset),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
                color = MaterialTheme.colorScheme.onSurface,
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(vertical = AnuraDimens.spaceGap),
            )
            Text(
                text = body,
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            AnuraFormButton(
                text = confirmLabel,
                onClick = onConfirm,
                style = AnuraFormButtonStyle.Primary,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceActionGap))
            AnuraFormButton(
                text = stringResource(R.string.anura_cancel),
                onClick = onDismiss,
                style = AnuraFormButtonStyle.Outline,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
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
