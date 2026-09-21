package me.juanlabs.anura.feature.capture

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraCard
import me.juanlabs.anura.designsystem.component.AnuraMeasureSlider
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

private const val CaptureSvlMin = 10f
private const val CaptureSvlMax = 160f
private const val CaptureSvlMock = 48f

/** `Paso 3: qué tamaño tenía` (§4.1). Estados: medición inicial y modificada (SVL mock). */
@Composable
fun CaptureStep3Screen(
    onBackClick: () -> Unit,
    onNext: () -> Unit,
    onSkip: () -> Unit = onNext,
    fromReview: Boolean = false,
    onSave: () -> Unit = onNext,
    onCancel: () -> Unit = onBackClick,
    onCloseClick: () -> Unit = onBackClick,
) {
    var svl by rememberSaveable { mutableFloatStateOf(CaptureSvlMock) }
    val svlMm = svl.toInt()

    CaptureWizardScaffold(
        appBarTitle = stringResource(R.string.capture_step3_appbar),
        step = 3,
        onBackClick = onBackClick,
        onCloseClick = onCloseClick,
        unsavedChanges = fromReview,
    ) {
        CaptureWizardHeading(
            title = stringResource(R.string.capture_step3_title),
            subtitle = stringResource(R.string.capture_step3_subtitle),
        )

        AnuraCard(modifier = Modifier.fillMaxWidth(), bordered = true) {
            Column(
                modifier = Modifier.padding(
                    horizontal = AnuraDimens.spaceCardInsetHorizontal,
                    vertical = AnuraDimens.spaceCardInsetVertical,
                ),
            ) {
                CaptureSvlComparison(
                    svlMm = svl,
                    modifier = Modifier.fillMaxWidth(),
                )
                Spacer(modifier = Modifier.height(8.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = AnuraIcons.Straighten,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.size(20.dp),
                    )
                    Spacer(modifier = Modifier.size(8.dp))
                    Text(
                        text = stringResource(R.string.capture_step3_candidates, svlMm),
                        style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                AnuraMeasureSlider(
                    value = svl,
                    onValueChange = { svl = it },
                    valueRange = CaptureSvlMin..CaptureSvlMax,
                )
                Row(modifier = Modifier.fillMaxWidth()) {
                    Text(
                        text = stringResource(R.string.capture_step3_min),
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.weight(1f),
                    )
                    Text(
                        text = stringResource(R.string.capture_step3_max),
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        textAlign = TextAlign.End,
                        modifier = Modifier.weight(1f),
                    )
                }
                Text(
                    text = stringResource(R.string.capture_step3_value, svlMm),
                    style = MaterialTheme.typography.headlineSmall.copy(
                        fontWeight = FontWeight.Bold,
                        fontSize = 28.sp,
                    ),
                    color = AnuraTheme.extendedColors.accentInk,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.fillMaxWidth(),
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = stringResource(R.string.capture_step3_ranges),
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }

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

@AnuraPreviews
@Composable
private fun CaptureStep3Preview() {
    AnuraTheme { CaptureStep3Screen(onBackClick = {}, onNext = {}) }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun CaptureStep3PreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) { CaptureStep3Screen(onBackClick = {}, onNext = {}) }
}
