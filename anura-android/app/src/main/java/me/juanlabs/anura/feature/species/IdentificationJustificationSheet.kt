package me.juanlabs.anura.feature.species

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraBottomSheet
import me.juanlabs.anura.designsystem.component.AnuraCard
import me.juanlabs.anura.designsystem.component.AnuraFormButton
import me.juanlabs.anura.designsystem.component.AnuraFormButtonStyle
import me.juanlabs.anura.designsystem.theme.AnuraDimens

/**
 * `DESPLEGABLE1 (justificación de identificación)` — bottom sheet local, no ruta (§4.2).
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun IdentificationJustificationSheet(
    onDismiss: () -> Unit,
    onRefuteAll: () -> Unit = onDismiss,
) {
    AnuraBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = AnuraDimens.spaceGutter)
                .padding(bottom = AnuraDimens.spaceSection),
        ) {
            Text(
                text = stringResource(R.string.justification_title),
                style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            Text(
                text = stringResource(R.string.justification_heading),
                style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
            )
            Text(
                text = stringResource(R.string.justification_intro),
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            Text(
                text = stringResource(R.string.justification_hint),
                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Medium),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            Text(
                text = stringResource(R.string.justification_contribution),
                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
            )
            RegionContribution(
                name = stringResource(R.string.justification_region_tympanum),
                percent = stringResource(R.string.justification_region_tympanum_pct),
                note = stringResource(R.string.justification_region_tympanum_note),
            )
            RegionContribution(
                name = stringResource(R.string.justification_region_disc),
                percent = stringResource(R.string.justification_region_disc_pct),
                note = stringResource(R.string.justification_region_disc_note),
            )
            RegionContribution(
                name = stringResource(R.string.justification_region_fold),
                percent = stringResource(R.string.justification_region_fold_pct),
                note = stringResource(R.string.justification_region_fold_note),
            )
            RegionContribution(
                name = stringResource(R.string.justification_region_dorsal),
                percent = stringResource(R.string.justification_region_dorsal_pct),
                note = stringResource(R.string.justification_region_dorsal_note),
            )
            Spacer(modifier = Modifier.height(AnuraDimens.spaceGap))
            AnuraCard(modifier = Modifier.fillMaxWidth()) {
                Text(
                    text = stringResource(R.string.justification_footer),
                    style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.Medium),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(
                        horizontal = AnuraDimens.spaceCardInsetHorizontal,
                        vertical = AnuraDimens.spaceCardInsetVertical,
                    ),
                )
            }
            Spacer(modifier = Modifier.height(AnuraDimens.spaceSection))
            AnuraFormButton(
                text = stringResource(R.string.justification_refute_all),
                onClick = onRefuteAll,
                style = AnuraFormButtonStyle.Primary,
            )
        }
    }
}

@Composable
private fun RegionContribution(
    name: String,
    percent: String,
    note: String,
) {
    Column(modifier = Modifier.padding(vertical = AnuraDimens.spaceGap)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = name,
                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
                modifier = Modifier.weight(1f),
            )
            Text(
                text = percent,
                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.SemiBold),
            )
        }
        Text(
            text = note,
            style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.Medium),
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}
