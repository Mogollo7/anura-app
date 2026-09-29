package me.juanlabs.anura.feature.capture

import android.location.Location
import android.os.Build
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import java.text.NumberFormat
import java.util.Locale
import me.juanlabs.anura.R
import me.juanlabs.anura.core.data.AltitudeRemote
import me.juanlabs.anura.core.data.AltitudeSourceGps
import me.juanlabs.anura.core.data.AltitudeSourceOpenTopo
import me.juanlabs.anura.core.data.CaptureDraft
import me.juanlabs.anura.core.data.HabitatLeafLitter
import me.juanlabs.anura.core.data.HabitatLowVegetation
import me.juanlabs.anura.core.data.HabitatRock
import me.juanlabs.anura.core.data.HabitatWaterBody
import me.juanlabs.anura.core.data.rememberAnuraRepository
import me.juanlabs.anura.designsystem.component.AnuraCard
import me.juanlabs.anura.designsystem.component.AnuraPermissionKind
import me.juanlabs.anura.designsystem.component.AnuraSectionLabel
import me.juanlabs.anura.designsystem.component.rememberSystemPermissionGranted
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraMotion
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

private val CaptureMapHeight = 218.dp
private val CaptureMapToFieldsGap = 14.dp
private val CaptureFieldHeight = 48.dp
private val CaptureFieldsToHabitatGap = 14.dp
private val CaptureChipHeight = AnuraDimens.sizeTouch
private val CaptureChipGap = 10.dp
private val CaptureChipRowGap = 8.dp
private val CapturePrecisionChipHeight = 30.dp
private val CaptureAltitudeLocale = Locale("es", "CO")

/**
 * `Paso 1: dónde la viste` (§4.1, grafo `CaptureGraph`).
 *
 * Todo sale del GPS o de lo que la persona marca en el mapa (toque o arrastre): sin ubicación no se
 * inventa ninguna. La altitud se consulta en OpenTopoData con ese punto (también si se marcó a mano);
 * si no hay red, se usa la del GPS como respaldo y, si tampoco, se dice y se sigue. El microhábitat
 * empieza sin elegir. Omitir no cambia lo que ya haya en el borrador.
 */
@Composable
fun CaptureStep1Screen(
    onBackClick: () -> Unit,
    onNext: () -> Unit,
    onSkip: () -> Unit = onNext,
    fromReview: Boolean = false,
    onSave: () -> Unit = onNext,
    onCancel: () -> Unit = onBackClick,
    onCloseClick: () -> Unit = onBackClick,
) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val draft = snapshot.draft
    // lo que había al entrar: «Cancelar» al editar desde el resumen lo restaura
    val entry = remember { snapshot.draft }
    val locationGranted = rememberSystemPermissionGranted(AnuraPermissionKind.Location)
    val hasPoint = draft.latitude != null && draft.longitude != null
    var lookup by remember { mutableStateOf(AltitudeLookup.Idle) }
    // La altitud sale de OpenTopoData (vía el servicio geo de ANURA) con el punto del mapa, marcado a mano
    // o del GPS. La del GPS queda solo de respaldo si la consulta falla; sin ninguna, se dice y se sigue.
    LaunchedEffect(pointKey(draft.latitude), pointKey(draft.longitude)) {
        val lat = draft.latitude
        val lon = draft.longitude
        if (lat == null || lon == null) {
            lookup = AltitudeLookup.Idle
            return@LaunchedEffect
        }
        if (repository.state.value.draft.altitudeSource == AltitudeSourceOpenTopo) {
            lookup = AltitudeLookup.Done
            return@LaunchedEffect
        }
        lookup = AltitudeLookup.Loading
        val found = AltitudeRemote.fetch(lat, lon)
        if (found == null) {
            lookup = AltitudeLookup.Failed
            return@LaunchedEffect
        }
        repository.updateDraft {
            // solo si el punto sigue siendo el consultado: si la persona lo movió, esa respuesta ya no aplica
            if (pointKey(it.latitude) == pointKey(lat) && pointKey(it.longitude) == pointKey(lon)) {
                it.copy(
                    altitudeMeters = found.meters,
                    altitudeSource = found.source,
                    altitudeLabel = formatAltitude(found.meters) + " msnm",
                )
            } else {
                it
            }
        }
        lookup = AltitudeLookup.Done
    }
    val altitudeText = when {
        draft.altitudeMeters != null ->
            stringResource(R.string.capture_step1_altitude_value, formatAltitude(draft.altitudeMeters))
        !hasPoint -> stringResource(R.string.capture_step1_altitude_waiting)
        lookup == AltitudeLookup.Failed -> stringResource(R.string.capture_step1_altitude_none)
        else -> stringResource(R.string.capture_step1_altitude_loading)
    }
    val altitudeNote = when {
        draft.altitudeMeters != null && draft.altitudeSource == AltitudeSourceGps ->
            stringResource(R.string.capture_step1_altitude_source_gps)
        draft.altitudeMeters != null -> stringResource(R.string.capture_step1_altitude_source_opentopo)
        hasPoint && lookup == AltitudeLookup.Failed -> stringResource(R.string.capture_step1_altitude_failed_hint)
        else -> null
    }

    CaptureWizardScaffold(
        appBarTitle = stringResource(R.string.capture_step1_appbar),
        step = 1,
        onBackClick = onBackClick,
        onCloseClick = onCloseClick,
        unsavedChanges = fromReview,
    ) {
        CaptureWizardHeading(
            title = stringResource(R.string.capture_step1_title),
            subtitle = stringResource(R.string.capture_step1_subtitle),
        )

        CaptureLocationMap(
            locationEnabled = locationGranted,
            precisionMeters = draft.precisionMeters,
            coordinates = if (hasPoint) draft.latitude!! to draft.longitude!! else null,
            onLocationChanged = { location -> repository.updateDraft { it.withLocation(location) } },
        )

        if (!hasPoint) {
            Spacer(modifier = Modifier.height(AnuraDimens.spaceLabelToContent))
            Text(
                text = stringResource(
                    if (locationGranted) R.string.capture_step1_searching else R.string.capture_step1_no_location,
                ),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.semantics { liveRegion = LiveRegionMode.Polite },
            )
        }

        Spacer(modifier = Modifier.height(CaptureMapToFieldsGap))

        CaptureReadOnlyField(
            label = stringResource(R.string.capture_step1_altitude_label),
            value = altitudeText,
            valueStyleLarge = draft.altitudeMeters != null,
            modifier = Modifier.fillMaxWidth(),
        )
        altitudeNote?.let { note ->
            Spacer(modifier = Modifier.height(AnuraDimens.spaceLabelToContent))
            Text(
                text = note,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.semantics { liveRegion = LiveRegionMode.Polite },
            )
        }

        Spacer(modifier = Modifier.height(CaptureFieldsToHabitatGap))

        AnuraSectionLabel(stringResource(R.string.capture_step1_microhabitat_label))

        Spacer(modifier = Modifier.height(AnuraDimens.spaceLabelToContent))

        CaptureMicrohabitatGrid(
            selected = draft.habitat,
            // tocar de nuevo la opción elegida la quita: nunca queda un hábitat que la persona no marcó
            onSelect = { habitat ->
                repository.updateDraft { it.copy(habitat = habitat.takeUnless { h -> h == it.habitat }) }
            },
        )

        Spacer(modifier = Modifier.height(CaptureContentToFooterGap))

        CaptureWizardStepFooter(
            fromReview = fromReview,
            onSkip = onSkip,
            onNext = onNext,
            onSave = onSave,
            onCancel = {
                repository.updateDraft {
                    it.copy(
                        latitude = entry.latitude,
                        longitude = entry.longitude,
                        precisionMeters = entry.precisionMeters,
                        altitudeMeters = entry.altitudeMeters,
                        altitudeSource = entry.altitudeSource,
                        altitudeLabel = entry.altitudeLabel,
                        habitat = entry.habitat,
                    )
                }
                onCancel()
            },
        )
    }
}

private enum class AltitudeLookup { Idle, Loading, Done, Failed }

/** Coordenada a ~11 m: dos fijos del GPS casi iguales son el mismo punto y no repiten la consulta. */
private fun pointKey(value: Double?): Long? = value?.let { Math.round(it * 10_000) }

/**
 * Aplica al borrador un punto del GPS o marcado a mano. La altitud de un punto ya consultado en
 * OpenTopoData se conserva si el punto no cambió; si cambió, queda la del GPS (solo respaldo) o ninguna,
 * hasta que llegue la consulta del punto nuevo.
 */
private fun CaptureDraft.withLocation(location: Location): CaptureDraft {
    val manual = location.provider?.startsWith("manual") == true
    val precision = if (!manual && location.hasAccuracy()) location.accuracy.toInt().coerceAtLeast(0) else null
    val samePoint = pointKey(latitude) == pointKey(location.latitude) && pointKey(longitude) == pointKey(location.longitude)
    if (samePoint && altitudeSource == AltitudeSourceOpenTopo) {
        return copy(latitude = location.latitude, longitude = location.longitude, precisionMeters = precision)
    }
    val gps = if (manual) null else gpsAltitudeMeters(location)
    return copy(
        latitude = location.latitude,
        longitude = location.longitude,
        precisionMeters = precision,
        altitudeMeters = gps,
        altitudeSource = gps?.let { AltitudeSourceGps },
        altitudeLabel = gps?.let { formatAltitude(it) + " msnm" },
    )
}

/** Altitud sobre el nivel del mar si el teléfono la da (Android 14+); si no, la que reporta el GPS. Respaldo de OpenTopoData. */
private fun gpsAltitudeMeters(location: Location): Int? = when {
    Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE && location.hasMslAltitude() ->
        location.mslAltitudeMeters.toInt()
    location.hasAltitude() -> location.altitude.toInt()
    else -> null
}

private fun formatAltitude(meters: Int): String =
    NumberFormat.getIntegerInstance(CaptureAltitudeLocale).format(meters)

@Composable
private fun CaptureLocationMap(
    locationEnabled: Boolean,
    precisionMeters: Int?,
    coordinates: Pair<Double, Double>?,
    onLocationChanged: (Location) -> Unit,
) {
    val mapCd = stringResource(R.string.capture_step1_map_cd)
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(CaptureMapHeight)
            .clip(RoundedCornerShape(AnuraDimens.radiusCard))
            .border(
                width = 1.dp,
                color = MaterialTheme.colorScheme.surfaceVariant,
                shape = RoundedCornerShape(AnuraDimens.radiusCard),
            )
            .semantics { contentDescription = mapCd },
    ) {
        CaptureOsmMap(
            locationEnabled = locationEnabled,
            onLocationChanged = onLocationChanged,
            initialPoint = coordinates,
            modifier = Modifier.fillMaxSize(),
        )
        if (precisionMeters != null) {
            CaptureMapChip(
                text = stringResource(R.string.capture_step1_precision, precisionMeters),
                modifier = Modifier
                    .align(Alignment.BottomStart)
                    .padding(start = 14.dp, bottom = 14.dp),
            )
        }
        if (coordinates != null) {
            val (lat, lon) = coordinates
            CaptureMapChip(
                text = stringResource(
                    R.string.capture_step1_coordinates,
                    String.format(CaptureAltitudeLocale, "%.4f", lat),
                    String.format(CaptureAltitudeLocale, "%.4f", lon),
                ),
                modifier = Modifier
                    .align(Alignment.BottomEnd)
                    .padding(end = 14.dp, bottom = 14.dp),
            )
        }
    }
}

@Composable
private fun CaptureMapChip(text: String, modifier: Modifier = Modifier) {
    Surface(
        modifier = modifier.height(CapturePrecisionChipHeight),
        shape = RoundedCornerShape(AnuraDimens.radiusCapsule),
        color = MaterialTheme.colorScheme.surface.copy(alpha = 0.92f),
        border = BorderStroke(1.dp, AnuraTheme.extendedColors.cardStroke),
        shadowElevation = 0.dp,
        tonalElevation = 0.dp,
    ) {
        Box(
            modifier = Modifier.padding(horizontal = 16.dp),
            contentAlignment = Alignment.Center,
        ) {
            Text(
                text = text,
                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
                color = MaterialTheme.colorScheme.onSurface,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
        }
    }
}

@Composable
private fun CaptureReadOnlyField(
    label: String,
    value: String,
    valueStyleLarge: Boolean,
    modifier: Modifier = Modifier,
) {
    Column(modifier = modifier) {
        AnuraSectionLabel(label)
        Spacer(modifier = Modifier.height(AnuraDimens.spaceLabelToContent))
        AnuraCard(
            modifier = Modifier
                .fillMaxWidth()
                .heightIn(min = CaptureFieldHeight),
            shape = RoundedCornerShape(AnuraDimens.radiusButton),
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(min = CaptureFieldHeight)
                    .padding(horizontal = 20.dp, vertical = 8.dp),
                contentAlignment = Alignment.CenterStart,
            ) {
                Text(
                    text = value,
                    style = if (valueStyleLarge) {
                        MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Normal)
                    } else {
                        MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Normal)
                    },
                    color = if (valueStyleLarge) {
                        MaterialTheme.colorScheme.onSurface
                    } else {
                        MaterialTheme.colorScheme.onSurfaceVariant
                    },
                )
            }
        }
    }
}

@Composable
private fun CaptureMicrohabitatGrid(
    selected: String?,
    onSelect: (String) -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(CaptureChipRowGap)) {
        Row(horizontalArrangement = Arrangement.spacedBy(CaptureChipGap)) {
            CaptureHabitatChip(
                label = stringResource(R.string.capture_step1_habitat_leaf_litter),
                selected = selected == HabitatLeafLitter,
                onClick = { onSelect(HabitatLeafLitter) },
                modifier = Modifier.weight(1f),
            )
            CaptureHabitatChip(
                label = stringResource(R.string.capture_step1_habitat_low_vegetation),
                selected = selected == HabitatLowVegetation,
                onClick = { onSelect(HabitatLowVegetation) },
                modifier = Modifier.weight(1f),
            )
        }
        Row(horizontalArrangement = Arrangement.spacedBy(CaptureChipGap)) {
            CaptureHabitatChip(
                label = stringResource(R.string.capture_step1_habitat_water),
                selected = selected == HabitatWaterBody,
                onClick = { onSelect(HabitatWaterBody) },
                modifier = Modifier.weight(1f),
            )
            CaptureHabitatChip(
                label = stringResource(R.string.capture_step1_habitat_rock),
                selected = selected == HabitatRock,
                onClick = { onSelect(HabitatRock) },
                modifier = Modifier.weight(1f),
            )
        }
    }
}

@Composable
private fun CaptureHabitatChip(
    label: String,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val container by animateColorAsState(
        targetValue = if (selected) {
            AnuraTheme.extendedColors.accentInk
        } else {
            MaterialTheme.colorScheme.surface
        },
        animationSpec = tween(AnuraMotion.DurationShort),
        label = "CaptureHabitatChipContainer",
    )
    val content by animateColorAsState(
        targetValue = if (selected) {
            MaterialTheme.colorScheme.onPrimary
        } else {
            MaterialTheme.colorScheme.onSurface
        },
        animationSpec = tween(AnuraMotion.DurationShort),
        label = "CaptureHabitatChipContent",
    )
    Surface(
        selected = selected,
        onClick = onClick,
        modifier = modifier
            .heightIn(min = CaptureChipHeight)
            .semantics { role = Role.RadioButton },
        shape = RoundedCornerShape(AnuraDimens.radiusCard),
        color = container,
        shadowElevation = 0.dp,
        tonalElevation = 0.dp,
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .heightIn(min = CaptureChipHeight)
                .padding(horizontal = 8.dp, vertical = 6.dp),
            contentAlignment = Alignment.Center,
        ) {
            Text(
                text = label,
                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                color = content,
                textAlign = TextAlign.Center,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis,
            )
        }
    }
}

@AnuraPreviews
@Composable
private fun CaptureStep1Preview() {
    AnuraTheme {
        CaptureStep1Screen(onBackClick = {}, onNext = {})
    }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun CaptureStep1PreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) {
        CaptureStep1Screen(onBackClick = {}, onNext = {})
    }
}
