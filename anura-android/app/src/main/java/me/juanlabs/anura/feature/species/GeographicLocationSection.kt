package me.juanlabs.anura.feature.species

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import me.juanlabs.anura.R
import me.juanlabs.anura.core.data.RegionalPackageStatus
import me.juanlabs.anura.core.data.SpeciesOccurrences
import me.juanlabs.anura.core.data.rememberAnuraRepository
import me.juanlabs.anura.designsystem.component.AnuraSectionLabel
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.theme.AnuraDimens

/**
 * `Ubicación geográfica` — sección embebida, no ruta (§4.1). Un pin cuadrado naranja por cada
 * coordenada real de ocurrencia de [taxonIds] (la especie sola en ficha de especie, todas las
 * especies del género/familia en esas fichas — ver `SpeciesSheetScreen`). Tocar el mapa abre un
 * Intent `geo:` hacia la app de mapas del sistema; el botón de expandir lo muestra más grande en
 * un [Dialog] a pantalla completa (estado local, no navega — no rompe el back stack).
 */
@Composable
fun GeographicLocationSection(
    taxonIds: List<String>,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val mapCd = stringResource(R.string.geo_location_map_cd)
    val expandCd = stringResource(R.string.geo_location_expand_cd)
    val collapseCd = stringResource(R.string.geo_location_collapse_cd)
    var expanded by rememberSaveable { mutableStateOf(false) }
    val points = rememberDistributionPoints(taxonIds)
    fun openMap() {
        val target = points.firstOrNull() ?: return
        val uri = Uri.parse("geo:${target.first},${target.second}?q=${target.first},${target.second}")
        runCatching { context.startActivity(Intent(Intent.ACTION_VIEW, uri)) }
    }
    AnuraSectionLabel(
        text = stringResource(R.string.geo_location_title),
        modifier = modifier.padding(bottom = AnuraDimens.spaceLabelToContent),
    )
    Box(modifier = Modifier.fillMaxWidth()) {
        SpeciesDistributionMap(
            points = points,
            modifier = Modifier
                .fillMaxWidth()
                .height(180.dp)
                .clip(RoundedCornerShape(AnuraDimens.radiusCard))
                .clickable(onClick = { openMap() })
                .semantics {
                    contentDescription = mapCd
                },
        )
        IconButton(
            onClick = { expanded = true },
            modifier = Modifier
                .padding(AnuraDimens.spaceLabelToContent)
                .align(Alignment.TopEnd)
                .size(AnuraDimens.sizeTouch)
                .clip(CircleShape)
                .background(MaterialTheme.colorScheme.surface),
        ) {
            Icon(
                imageVector = AnuraIcons.Expand,
                contentDescription = expandCd,
                tint = MaterialTheme.colorScheme.onSurface,
            )
        }
    }
    if (expanded) {
        Dialog(
            onDismissRequest = { expanded = false },
            properties = DialogProperties(usePlatformDefaultWidth = false),
        ) {
            Box(modifier = Modifier.fillMaxSize()) {
                SpeciesDistributionMap(
                    points = points,
                    modifier = Modifier
                        .fillMaxSize()
                        .semantics { contentDescription = mapCd },
                )
                IconButton(
                    onClick = { expanded = false },
                    modifier = Modifier
                        .padding(AnuraDimens.spaceGap)
                        .align(Alignment.TopEnd)
                        .size(AnuraDimens.sizeTouch)
                        .clip(CircleShape)
                        .background(MaterialTheme.colorScheme.surface),
                ) {
                    Icon(
                        imageVector = AnuraIcons.Collapse,
                        contentDescription = collapseCd,
                        tint = MaterialTheme.colorScheme.onSurface,
                    )
                }
            }
        }
    }
}

@Composable
private fun rememberDistributionPoints(taxonIds: List<String>): List<Pair<Double, Double>> {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    return remember(snapshot.packages, taxonIds) {
        val activePackage = snapshot.packages.firstOrNull {
            it.active && it.status == RegionalPackageStatus.Installed && it.localPath != null
        }
        val localPath = activePackage?.localPath ?: return@remember emptyList()
        SpeciesOccurrences.pointsFor(localPath, taxonIds)
    }
}
