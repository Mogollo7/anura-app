package me.juanlabs.anura.feature.capture

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.pluralStringResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.R
import me.juanlabs.anura.core.data.CaptureDraft
import me.juanlabs.anura.core.data.RegionalPackageRecord
import me.juanlabs.anura.core.data.RegionalPackageStatus
import me.juanlabs.anura.core.data.formatAudioDuration
import me.juanlabs.anura.core.data.formatCoordinates
import me.juanlabs.anura.core.data.formatObservationWhen
import me.juanlabs.anura.core.data.habitatLabel
import me.juanlabs.anura.core.data.periodLabel
import me.juanlabs.anura.core.data.rememberAnuraRepository
import me.juanlabs.anura.core.key.ClaveDatos
import me.juanlabs.anura.core.key.decodificarRespuestas
import me.juanlabs.anura.core.key.especiesQueQuedan
import me.juanlabs.anura.core.key.manualesSinPrevias
import me.juanlabs.anura.core.key.respuestasPrevias
import me.juanlabs.anura.designsystem.component.AnuraCard
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraFormButtonStyle
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

/** Relleno interno de la tarjeta info, igual que las filas de resumen para alinear la columna de iconos. */
private val CaptureSummaryRowInsetH = 16.dp
private val CaptureSummaryRowInsetV = 14.dp
private val CaptureSummaryRowGap = 10.dp

/**
 * `Paso 6: resumen y analizar` (§4.1). Muestra solo lo que la persona capturó (lo que falta dice
 * «Sin …») y cada fila lleva de vuelta al paso que la capturó. Sin al menos una foto no se puede
 * analizar: la identificación sale de las fotos.
 */
@Composable
fun CaptureStep6Screen(
    onBackClick: () -> Unit,
    onAnalyze: () -> Unit,
    onEditWhere: () -> Unit = {},
    onEditWhen: () -> Unit = {},
    onEditSize: () -> Unit = {},
    onEditPhotos: () -> Unit = {},
    onEditAudio: () -> Unit = {},
    onEditClave: () -> Unit = {},
    onCloseClick: () -> Unit = onBackClick,
) {
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val draft = snapshot.draft
    val whereParts = listOfNotNull(
        formatCoordinates(draft.latitude, draft.longitude),
        draft.altitudeLabel,
        habitatLabel(draft.habitat),
    )
    val whereValue = whereParts.joinToString(" · ").ifBlank {
        stringResource(R.string.capture_step6_where_empty)
    }
    val whenParts = listOfNotNull(
        formatObservationWhen(draft.observedAtEpochMs),
        periodLabel(draft.period),
    )
    val whenValue = whenParts.joinToString(" · ").ifBlank {
        stringResource(R.string.capture_step6_when_empty)
    }
    val sizeValue = draft.svlMm?.let { stringResource(R.string.capture_step6_size_mm, it) }
        ?: stringResource(R.string.capture_step6_size_empty)
    val photoCount = draft.photoTokens.size
    val photosValue = if (photoCount == 0) {
        stringResource(R.string.capture_step6_photos_empty)
    } else {
        pluralStringResource(R.plurals.capture_step6_photos_count, photoCount, photoCount)
    }
    val audioValue = formatAudioDuration(draft.audioDurationMs)
        ?: stringResource(R.string.capture_step6_audio_empty)
    val remaining = remainingSpecies(draft, snapshot.packages.activeInstalledPackage())
    val claveValue = when {
        draft.claveAnswers == null || remaining == null -> stringResource(R.string.capture_step6_clave_empty)
        remaining == 0 -> stringResource(R.string.capture_step6_clave_none)
        else -> pluralStringResource(R.plurals.capture_step6_clave_remaining, remaining, remaining)
    }

    CaptureWizardScaffold(
        appBarTitle = stringResource(R.string.capture_step6_appbar),
        step = 6,
        onBackClick = onBackClick,
        onCloseClick = onCloseClick,
    ) {
        CaptureWizardHeading(
            title = stringResource(R.string.capture_step6_title),
            subtitle = stringResource(R.string.capture_step6_subtitle),
        )

        CaptureSummaryRow(
            icon = AnuraIcons.FieldSession,
            label = stringResource(R.string.capture_step6_where),
            value = whereValue,
            onEdit = onEditWhere,
        )
        Spacer(modifier = Modifier.height(CaptureSummaryRowGap))
        CaptureSummaryRow(
            icon = AnuraIcons.Schedule,
            label = stringResource(R.string.capture_step6_when),
            value = whenValue,
            onEdit = onEditWhen,
        )
        Spacer(modifier = Modifier.height(CaptureSummaryRowGap))
        CaptureSummaryRow(
            icon = AnuraIcons.Straighten,
            label = stringResource(R.string.capture_step6_size),
            value = sizeValue,
            onEdit = onEditSize,
        )
        Spacer(modifier = Modifier.height(CaptureSummaryRowGap))
        CaptureSummaryRow(
            icon = AnuraIcons.PhotoId,
            label = stringResource(R.string.capture_step6_photos),
            value = photosValue,
            onEdit = onEditPhotos,
        )
        Spacer(modifier = Modifier.height(CaptureSummaryRowGap))
        CaptureSummaryRow(
            icon = AnuraIcons.AudioId,
            label = stringResource(R.string.capture_step6_audio),
            value = audioValue,
            onEdit = onEditAudio,
        )
        Spacer(modifier = Modifier.height(CaptureSummaryRowGap))
        CaptureSummaryRow(
            icon = AnuraIcons.Info,
            label = stringResource(R.string.capture_step6_clave),
            value = claveValue,
            onEdit = onEditClave,
        )

        Spacer(modifier = Modifier.height(CaptureSummaryRowGap))

        AnuraCard(modifier = Modifier.fillMaxWidth()) {
            Row(
                modifier = Modifier.padding(
                    horizontal = CaptureSummaryRowInsetH,
                    vertical = CaptureSummaryRowInsetV,
                ),
                verticalAlignment = Alignment.Top,
            ) {
                Icon(
                    imageVector = AnuraIcons.Info,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.size(24.dp),
                )
                Spacer(modifier = Modifier.size(12.dp))
                Text(
                    text = stringResource(R.string.capture_step6_info),
                    style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.Medium),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = stringResource(R.string.capture_step6_offline),
            style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.Medium),
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center,
            modifier = Modifier.fillMaxWidth(),
        )

        Spacer(modifier = Modifier.height(12.dp))

        if (photoCount == 0) {
            Text(
                text = stringResource(R.string.capture_step6_photos_required),
                style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.Medium),
                color = MaterialTheme.colorScheme.error,
                textAlign = TextAlign.Center,
                modifier = Modifier
                    .fillMaxWidth()
                    .semantics { liveRegion = LiveRegionMode.Polite },
            )
            Spacer(modifier = Modifier.height(12.dp))
        }
        AnuraFormButton(
            text = stringResource(R.string.capture_step6_analyze),
            onClick = onAnalyze,
            style = AnuraFormButtonStyle.Primary,
            enabled = photoCount > 0,
        )
    }
}

private fun List<RegionalPackageRecord>.activeInstalledPackage() =
    firstOrNull { it.active && it.status == RegionalPackageStatus.Installed && !it.localPath.isNullOrBlank() }

/**
 * Cuántas especies del paquete activo quedan con lo capturado en los pasos y las respuestas de la
 * clave. Null si no se usó la ayuda o la clave ya no está en el teléfono (no hay cifra que dar).
 */
@Composable
private fun remainingSpecies(draft: CaptureDraft, pack: RegionalPackageRecord?): Int? {
    val repository = rememberAnuraRepository()
    // se lee del disco una vez por paquete, no en cada recomposición
    val clave = remember(pack?.id, pack?.version) {
        pack?.let { repository.cachedClave(it.id, it.version ?: "1") }
    }
    if (draft.claveAnswers == null || clave == null) return null
    val previas = respuestasPrevias(
        clave,
        ClaveDatos(
            altitudM = draft.altitudeMeters,
            tamanoMm = draft.svlMm,
            habitat = draft.habitat,
            periodo = draft.period,
        ),
    )
    val manuales = manualesSinPrevias(previas, decodificarRespuestas(draft.claveAnswers))
    return especiesQueQuedan(clave, previas + manuales)
}

@Composable
private fun CaptureSummaryRow(
    icon: ImageVector,
    label: String,
    value: String,
    onEdit: () -> Unit,
) {
    AnuraCard(modifier = Modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier.padding(
                horizontal = CaptureSummaryRowInsetH,
                vertical = CaptureSummaryRowInsetV,
            ),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = AnuraTheme.extendedColors.accentInk,
                modifier = Modifier.size(24.dp),
            )
            Spacer(modifier = Modifier.size(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = label,
                    style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                Text(
                    text = value,
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Normal),
                    color = MaterialTheme.colorScheme.onSurface,
                    maxLines = 3,
                    overflow = TextOverflow.Ellipsis,
                )
            }
            IconButton(
                onClick = onEdit,
                modifier = Modifier.size(AnuraDimens.sizeTouch),
            ) {
                Icon(
                    imageVector = AnuraIcons.Edit,
                    contentDescription = stringResource(R.string.capture_step6_edit_cd, label),
                    tint = AnuraTheme.extendedColors.accentInk,
                )
            }
        }
    }
}

@AnuraPreviews
@Composable
private fun CaptureStep6Preview() {
    AnuraTheme { CaptureStep6Screen(onBackClick = {}, onAnalyze = {}) }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun CaptureStep6PreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) { CaptureStep6Screen(onBackClick = {}, onAnalyze = {}) }
}
