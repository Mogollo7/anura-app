package me.juanlabs.anura.feature.capture

import androidx.compose.runtime.Composable
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.tooling.preview.Preview
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

/** `Añadir foto` (Identificación ID). Misma interfaz y chequeo de borrosidad que el paso 4. */
@Composable
fun PhotoCaptureScreen(
    onBackClick: () -> Unit,
    onPhotoAccepted: () -> Unit = onBackClick,
    onCloseClick: () -> Unit = onBackClick,
) {
    CaptureAddPhotoFlow(
        appBarTitle = stringResource(R.string.photo_capture_title),
        showProgress = false,
        confirmLabel = stringResource(R.string.photo_capture_analyze),
        onBackClick = onBackClick,
        onConfirm = onPhotoAccepted,
        onCloseClick = onCloseClick,
    )
}

@AnuraPreviews
@Composable
private fun PhotoCapturePreview() {
    AnuraTheme { PhotoCaptureScreen(onBackClick = {}) }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun PhotoCapturePreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) { PhotoCaptureScreen(onBackClick = {}) }
}
