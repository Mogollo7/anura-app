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
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.R
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

/** `Paso 6: resumen y analizar` (§4.1). Conserva el paso 5 anterior; solo cambia el índice. */
@Composable
fun CaptureStep6Screen(
    onBackClick: () -> Unit,
    onAnalyze: () -> Unit,
    onEditWhere: () -> Unit = {},
    onEditWhen: () -> Unit = {},
    onEditSize: () -> Unit = {},
    onEditPhotos: () -> Unit = {},
    onEditAudio: () -> Unit = {},
    onCloseClick: () -> Unit = onBackClick,
) {
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
            value = stringResource(R.string.capture_step6_where_value),
            onEdit = onEditWhere,
        )
        Spacer(modifier = Modifier.height(CaptureSummaryRowGap))
        CaptureSummaryRow(
            icon = AnuraIcons.Schedule,
            label = stringResource(R.string.capture_step6_when),
            value = stringResource(R.string.capture_step6_when_value),
            onEdit = onEditWhen,
        )
        Spacer(modifier = Modifier.height(CaptureSummaryRowGap))
        CaptureSummaryRow(
            icon = AnuraIcons.Straighten,
            label = stringResource(R.string.capture_step6_size),
            value = stringResource(R.string.capture_step6_size_value),
            onEdit = onEditSize,
        )
        Spacer(modifier = Modifier.height(CaptureSummaryRowGap))
        CaptureSummaryRow(
            icon = AnuraIcons.PhotoId,
            label = stringResource(R.string.capture_step6_photos),
            value = stringResource(R.string.capture_step6_photos_value),
            onEdit = onEditPhotos,
        )
        Spacer(modifier = Modifier.height(CaptureSummaryRowGap))
        CaptureSummaryRow(
            icon = AnuraIcons.AudioId,
            label = stringResource(R.string.capture_step6_audio),
            value = stringResource(R.string.capture_step6_audio_value),
            onEdit = onEditAudio,
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

        AnuraFormButton(
            text = stringResource(R.string.capture_step6_analyze),
            onClick = onAnalyze,
            style = AnuraFormButtonStyle.Primary,
        )
    }
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
                    maxLines = 2,
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
