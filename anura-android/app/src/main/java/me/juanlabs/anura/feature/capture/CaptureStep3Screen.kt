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
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import me.juanlabs.anura.R
import me.juanlabs.anura.core.key.ClaveTamano
import me.juanlabs.anura.core.key.especiesCompatiblesConValor
import me.juanlabs.anura.core.key.especiesConDato
import me.juanlabs.anura.core.data.rememberAnuraRepository
import me.juanlabs.anura.designsystem.component.AnuraCard
import me.juanlabs.anura.designsystem.component.AnuraMeasureSlider
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

private const val CaptureSvlMin = 10f
private const val CaptureSvlMax = 160f

/** Dónde queda el control antes de que la persona lo mueva. No es una medida: no se guarda. */
private const val CaptureSvlRest = 40f

/**
 * `Paso 3: qué tamaño tenía` (§4.1). La medida solo se guarda cuando la persona mueve el control;
 * omitir el paso la borra. Cuántas especies del paquete coinciden sale de la clave descargada con el
 * paquete activo (rango de tamaño de cada especie); sin paquete, sin clave o sin tamaños en ella, no
 * hay cifra y la pantalla dice por qué.
 */
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
    val repository = rememberAnuraRepository()
    val snapshot by repository.state.collectAsState()
    val entrySvl = remember { snapshot.draft.svlMm }
    var svl by rememberSaveable { mutableStateOf(snapshot.draft.svlMm?.toFloat()) }
    val svlMm = svl?.toInt()
    val carga = rememberClaveCarga().carga

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
                    svlMm = svl ?: CaptureSvlRest,
                    modifier = Modifier.fillMaxWidth(),
                )
                Spacer(modifier = Modifier.height(8.dp))
                Row(verticalAlignment = Alignment.Top) {
                    Icon(
                        imageVector = AnuraIcons.Straighten,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.size(20.dp),
                    )
                    Spacer(modifier = Modifier.size(8.dp))
                    Text(
                        text = candidatesText(carga, svlMm),
                        style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.SemiBold),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier
                            .weight(1f)
                            .semantics { liveRegion = LiveRegionMode.Polite },
                    )
                }
                AnuraMeasureSlider(
                    value = svl ?: CaptureSvlRest,
                    onValueChange = { value ->
                        svl = value
                        repository.updateDraft { it.copy(svlMm = value.toInt()) }
                    },
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
                if (svlMm != null) {
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
                }
            }
        }

        Spacer(modifier = Modifier.height(CaptureContentToFooterGap))

        CaptureWizardStepFooter(
            fromReview = fromReview,
            // omitir = sin medida, aunque antes se haya movido el control
            onSkip = {
                repository.updateDraft { it.copy(svlMm = null) }
                onSkip()
            },
            onNext = onNext,
            onSave = onSave,
            onCancel = {
                repository.updateDraft { it.copy(svlMm = entrySvl) }
                onCancel()
            },
        )
    }
}

/** La línea que dice cuántas especies coinciden con la medida, o por qué no hay cifra. */
@Composable
private fun candidatesText(carga: ClaveCarga, svlMm: Int?): String = when (carga) {
    ClaveCarga.SinPaquete -> stringResource(R.string.capture_step3_no_package)
    ClaveCarga.Cargando -> stringResource(R.string.capture_step3_loading_key)
    ClaveCarga.Obsoleta -> stringResource(R.string.clave_stale_body)
    ClaveCarga.SinClave -> stringResource(R.string.capture_step3_no_key)
    ClaveCarga.SinEspecies -> stringResource(R.string.capture_step3_no_sizes)
    is ClaveCarga.Lista -> {
        val conTamano = especiesConDato(carga.documento, ClaveTamano)
        when {
            conTamano == 0 -> stringResource(R.string.capture_step3_no_sizes)
            svlMm == null -> stringResource(R.string.capture_step3_untouched)
            else -> stringResource(
                R.string.capture_step3_matches,
                svlMm,
                especiesCompatiblesConValor(carga.documento, ClaveTamano, svlMm.toDouble()) ?: 0,
                conTamano,
            )
        }
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
