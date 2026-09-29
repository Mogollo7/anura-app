package me.juanlabs.anura.feature.capture

import androidx.compose.runtime.Composable
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.tooling.preview.Preview
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

/**
 * `Paso 4: añadir foto` del asistente. Es la misma cámara y el mismo carrusel de revisión de
 * Foto ID ([CaptureAddPhotoFlow]); aquí solo cambian el título y la barra de progreso.
 * Sin foto no hay identificación, por eso este paso no se puede omitir.
 */
@Composable
fun CaptureStep4Screen(
    onBackClick: () -> Unit,
    onNext: () -> Unit,
    fromReview: Boolean = false,
    onSave: () -> Unit = onNext,
    onCloseClick: () -> Unit = onBackClick,
) {
    CaptureAddPhotoFlow(
        appBarTitle = stringResource(R.string.capture_step4_appbar),
        showProgress = true,
        step = 4,
        confirmLabel = stringResource(R.string.capture_wizard_next),
        onBackClick = onBackClick,
        onConfirm = onNext,
        fromReview = fromReview,
        onSave = onSave,
        onCloseClick = onCloseClick,
    )
}

@AnuraPreviews
@Composable
private fun CaptureStep4Preview() {
    AnuraTheme { CaptureStep4Screen(onBackClick = {}, onNext = {}) }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun CaptureStep4PreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) { CaptureStep4Screen(onBackClick = {}, onNext = {}) }
}
