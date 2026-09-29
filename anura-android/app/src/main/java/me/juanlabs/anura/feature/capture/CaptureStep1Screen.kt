package me.juanlabs.anura.feature.capture

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
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
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
private val CaptureFieldGap = 15.dp
private val CaptureFieldsToHabitatGap = 14.dp
private val CaptureChipHeight = AnuraDimens.sizeTouch
private val CaptureChipGap = 10.dp
private val CaptureChipRowGap = 8.dp
private val CapturePrecisionChipHeight = 30.dp
private val CaptureAltitudeLocale = Locale("es", "CO")

private enum class CaptureMicrohabitat {
    LeafLitter,
    LowVegetation,
    WaterBody,
    Rock,
}

/**
 * Valores iniciales del Paso 1. Ubicación, precisión y altitud salen del GPS del teléfono
 * (`CaptureOsmMap`); omitir deja la observación sin ubicación (`null`, no `""`).
 */
data class CaptureStep1UiState(
    val ecosystemLabel: String = "",
)

/**
 * `Paso 1: dónde la viste` (§4.1, grafo `CaptureGraph`).
 *
 * Estados: contenido. El permiso de ubicación se pide con el diálogo del sistema.
 * Skip y Continuar avanzan al Paso 2; Skip no rellena ubicación.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CaptureStep1Screen(
    onBackClick: () -> Unit,
    onNext: () -> Unit,
    onSkip: () -> Unit = onNext,
    fromReview: Boolean = false,
    onSave: () -> Unit = onNext,
    onCancel: () -> Unit = onBackClick,
    onCloseClick: () -> Unit = onBackClick,
    uiState: CaptureStep1UiState = CaptureStep1UiState(),
) {
    val repository = rememberAnuraRepository()
    val draft = repository.snapshot.draft
    val locationGranted = rememberSystemPermissionGranted(AnuraPermissionKind.Location)
    val missing = stringResource(R.string.anura_value_missing)
    val ecosystem = uiState.ecosystemLabel.ifEmpty { draft.ecosystemLabel.orEmpty() }
    var selectedHabitat by rememberSaveable {
        mutableStateOf(
            when (draft.habitat) {
                HabitatLowVegetation -> CaptureMicrohabitat.LowVegetation
                HabitatWaterBody -> CaptureMicrohabitat.WaterBody
                HabitatRock -> CaptureMicrohabitat.Rock
                else -> CaptureMicrohabitat.LeafLitter
            },
        )
    }
    var precisionMeters by rememberSaveable { mutableIntStateOf(draft.precisionMeters ?: -1) }
    var altitudeLabel by rememberSaveable { mutableStateOf(draft.altitudeLabel.orEmpty()) }
    var latitude by rememberSaveable { mutableStateOf(draft.latitude) }
    var longitude by rememberSaveable { mutableStateOf(draft.longitude) }
    val altitude = altitudeLabel.ifEmpty { missing }

    LaunchedEffect(selectedHabitat, precisionMeters, altitudeLabel, latitude, longitude) {
        repository.updateDraft { current ->
            current.copy(
                habitat = when (selectedHabitat) {
                    CaptureMicrohabitat.LeafLitter -> HabitatLeafLitter
                    CaptureMicrohabitat.LowVegetation -> HabitatLowVegetation
                    CaptureMicrohabitat.WaterBody -> HabitatWaterBody
                    CaptureMicrohabitat.Rock -> HabitatRock
                },
                precisionMeters = precisionMeters.takeIf { it >= 0 },
                altitudeLabel = altitudeLabel.ifBlank { null },
                latitude = latitude,
                longitude = longitude,
            )
        }
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
            precisionMeters = precisionMeters.takeIf { it >= 0 },
            coordinates = latitude?.let { lat -> longitude?.let { lon -> lat to lon } },
            onLocationChanged = { location ->
                if (location.hasAccuracy()) {
                    precisionMeters = location.accuracy.toInt().coerceAtLeast(0)
                }
                if (location.hasAltitude()) {
                    val formatted = NumberFormat.getIntegerInstance(CaptureAltitudeLocale)
                        .format(location.altitude.toInt())
                    altitudeLabel = formatted + " msnm"
                }
                latitude = location.latitude
                longitude = location.longitude
            },
        )

        Spacer(modifier = Modifier.height(CaptureMapToFieldsGap))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(CaptureFieldGap),
        ) {
            CaptureReadOnlyField(
                label = stringResource(R.string.capture_step1_altitude_label),
                value = altitude,
                valueStyleLarge = true,
                modifier = Modifier.weight(1f),
            )
            CaptureReadOnlyField(
                label = stringResource(R.string.capture_step1_ecosystem_label),
                value = ecosystem,
                valueStyleLarge = false,
                modifier = Modifier.weight(1f),
            )
        }

        Spacer(modifier = Modifier.height(CaptureFieldsToHabitatGap))

        AnuraSectionLabel(stringResource(R.string.capture_step1_microhabitat_label))

        Spacer(modifier = Modifier.height(AnuraDimens.spaceLabelToContent))

        CaptureMicrohabitatGrid(
            selected = selectedHabitat,
            onSelect = { selectedHabitat = it },
        )

        Spacer(modifier = Modifier.height(CaptureContentToFooterGap))

        CaptureWizardStepFooter(
            fromReview = fromReview,
            onSkip = onSkip,
            onNext = onNext,
            onSave = onSave,
            onCancel = onCancel,
        )
    }
}

@Composable
private fun CaptureLocationMap(
    locationEnabled: Boolean,
    precisionMeters: Int?,
    coordinates: Pair<Double, Double>?,
    onLocationChanged: (android.location.Location) -> Unit,
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
            modifier = Modifier.fillMaxSize(),
        )
        if (precisionMeters != null) {
            Surface(
                modifier = Modifier
                    .align(Alignment.BottomStart)
                    .padding(start = 14.dp, bottom = 14.dp)
                    .height(CapturePrecisionChipHeight),
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
                        text = stringResource(R.string.capture_step1_precision, precisionMeters),
                        style = MaterialTheme.typography.labelSmall.copy(
                            fontWeight = FontWeight.SemiBold,
                        ),
                        color = MaterialTheme.colorScheme.onSurface,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                    )
                }
            }
        }
        if (coordinates != null) {
            val (lat, lon) = coordinates
            Surface(
                modifier = Modifier
                    .align(Alignment.BottomEnd)
                    .padding(end = 14.dp, bottom = 14.dp)
                    .height(CapturePrecisionChipHeight),
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
                        text = stringResource(
                            R.string.capture_step1_coordinates,
                            String.format(CaptureAltitudeLocale, "%.4f", lat),
                            String.format(CaptureAltitudeLocale, "%.4f", lon),
                        ),
                        style = MaterialTheme.typography.labelSmall.copy(
                            fontWeight = FontWeight.SemiBold,
                        ),
                        color = MaterialTheme.colorScheme.onSurface,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                    )
                }
            }
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
                .height(CaptureFieldHeight),
            shape = RoundedCornerShape(AnuraDimens.radiusButton),
        ) {
            Box(
                modifier = Modifier.padding(horizontal = 20.dp),
                contentAlignment = Alignment.CenterStart,
            ) {
                Text(
                    text = value,
                    style = if (valueStyleLarge) {
                        MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Normal)
                    } else {
                        MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Normal)
                    },
                    color = MaterialTheme.colorScheme.onSurface,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
            }
        }
    }
}

@Composable
private fun CaptureMicrohabitatGrid(
    selected: CaptureMicrohabitat,
    onSelect: (CaptureMicrohabitat) -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(CaptureChipRowGap)) {
        Row(horizontalArrangement = Arrangement.spacedBy(CaptureChipGap)) {
            CaptureHabitatChip(
                label = stringResource(R.string.capture_step1_habitat_leaf_litter),
                selected = selected == CaptureMicrohabitat.LeafLitter,
                onClick = { onSelect(CaptureMicrohabitat.LeafLitter) },
                modifier = Modifier.weight(1f),
            )
            CaptureHabitatChip(
                label = stringResource(R.string.capture_step1_habitat_low_vegetation),
                selected = selected == CaptureMicrohabitat.LowVegetation,
                onClick = { onSelect(CaptureMicrohabitat.LowVegetation) },
                modifier = Modifier.weight(1f),
            )
        }
        Row(horizontalArrangement = Arrangement.spacedBy(CaptureChipGap)) {
            CaptureHabitatChip(
                label = stringResource(R.string.capture_step1_habitat_water),
                selected = selected == CaptureMicrohabitat.WaterBody,
                onClick = { onSelect(CaptureMicrohabitat.WaterBody) },
                modifier = Modifier.weight(1f),
            )
            CaptureHabitatChip(
                label = stringResource(R.string.capture_step1_habitat_rock),
                selected = selected == CaptureMicrohabitat.Rock,
                onClick = { onSelect(CaptureMicrohabitat.Rock) },
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
                .padding(horizontal = 8.dp),
            contentAlignment = Alignment.Center,
        ) {
            Text(
                text = label,
                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                color = content,
                textAlign = TextAlign.Center,
                maxLines = 1,
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
