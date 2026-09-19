package me.juanlabs.anura.feature.species

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraSectionLabel
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.feature.capture.CaptureOsmMap

/**
 * `Ubicación geográfica` — sección embebida, no ruta (§4.1). El mapa abre un Intent
 * `geo:` hacia la app de mapas del sistema.
 */
@Composable
fun GeographicLocationSection(
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val geoUri = stringResource(R.string.geo_location_geo_uri)
    val mapCd = stringResource(R.string.geo_location_map_cd)
    fun openMap() {
        runCatching {
            context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(geoUri)))
        }
    }
    AnuraSectionLabel(
        text = stringResource(R.string.geo_location_title),
        modifier = modifier.padding(bottom = AnuraDimens.spaceLabelToContent),
    )
    CaptureOsmMap(
        locationEnabled = false,
        onLocationChanged = {},
        modifier = Modifier
            .fillMaxWidth()
            .height(180.dp)
            .clip(RoundedCornerShape(AnuraDimens.radiusCard))
            .clickable(onClick = { openMap() })
            .semantics {
                contentDescription = mapCd
            },
    )
}
