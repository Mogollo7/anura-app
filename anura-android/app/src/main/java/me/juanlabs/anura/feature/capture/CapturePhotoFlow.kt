package me.juanlabs.anura.feature.capture

import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.tooling.preview.Preview
import me.juanlabs.anura.R
import me.juanlabs.anura.core.data.rememberAnuraRepository
import me.juanlabs.anura.designsystem.component.AnuraPermissionKind
import me.juanlabs.anura.designsystem.component.rememberSystemPermissionGranted
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

/**
 * Cámara a pantalla completa y carrusel de revisión de fotos. Lo usa Foto ID ([PhotoCaptureScreen]);
 * el paso «Añadir foto» del asistente viejo ya no existe.
 */
@Composable
internal fun CaptureAddPhotoFlow(
    appBarTitle: String,
    onBackClick: () -> Unit,
    onConfirm: () -> Unit,
    showProgress: Boolean = true,
    step: Int = 4,
    fromReview: Boolean = false,
    onSave: () -> Unit = onConfirm,
    confirmLabel: String,
    onCloseClick: () -> Unit = onBackClick,
) {
    val cameraGranted = rememberSystemPermissionGranted(AnuraPermissionKind.Camera)
    val repository = rememberAnuraRepository()
    val captureFailedMessage = stringResource(R.string.capture_photo_failed)
    var specimens by rememberSaveable {
        mutableStateOf(
            CapturePhotoDraft.tokens,
        )
    }
    var selected by rememberSaveable {
        mutableIntStateOf(specimens.lastIndex.coerceAtLeast(0))
    }
    var reviewing by rememberSaveable {
        mutableStateOf(fromReview && specimens.isNotEmpty())
    }
    var capturing by rememberSaveable { mutableStateOf(false) }
    val blurController = rememberCapturePhotoBlurController()
    val shutter = rememberCaptureCameraShutter()
    var confirmLeave by rememberSaveable { mutableStateOf(false) }

    fun persist(next: List<String>) {
        CapturePhotoDraft.tokens = next
        // se conservan los tokens ya persistidos para no re-codificar (y duplicar) las fotos en cada cambio
        val stored = CapturePhotoDraft.tokens.takeIf { it.size == next.size } ?: next
        specimens = stored
        selected = selected.coerceAtMost(stored.lastIndex.coerceAtLeast(0))
    }

    val gallery = rememberGalleryPicker { uris ->
        if (uris.isEmpty()) return@rememberGalleryPicker
        val added = uris.map { "uri:$it" }
        persist(specimens + added)
        blurController.inspect(added)
    }

    fun enqueue(token: String) {
        persist(specimens + token)
        capturing = false
        blurController.inspect(listOf(token))
    }

    fun captureStill() {
        capturing = true
        shutter.takePicture(
            onSaved = { enqueue(it) },
            // Si la cámara falla no se agrega nada: nunca una foto que la persona no tomó.
            onError = {
                capturing = false
                repository.notify(captureFailedMessage)
            },
        )
    }

    fun removeAt(index: Int) {
        if (specimens.isEmpty()) return
        val next = specimens.toMutableList().also { it.removeAt(index) }
        persist(next)
        if (next.isEmpty()) reviewing = false
    }

    fun goBack() {
        when {
            !reviewing && fromReview && specimens.isNotEmpty() -> reviewing = true
            reviewing && !fromReview -> reviewing = false
            specimens.isNotEmpty() || fromReview -> confirmLeave = true
            else -> onBackClick()
        }
    }

    CaptureWizardScaffold(
        appBarTitle = appBarTitle,
        step = step,
        onBackClick = { goBack() },
        scrollable = false,
        showProgress = showProgress,
        edgeToEdge = true,
        onCloseClick = onCloseClick,
    ) {
        if (reviewing) {
            CapturePhotoCarousel(
                specimens = specimens,
                selectedIndex = selected,
                onSelect = { selected = it },
                onDelete = { removeAt(it) },
                onTakeSamples = { reviewing = false },
                onSave = if (fromReview) onSave else onConfirm,
                confirmLabel = confirmLabel,
                modifier = Modifier.weight(1f),
            )
        } else {
            CaptureBatchFieldCapture(
                specimens = specimens,
                capturing = capturing,
                cameraGranted = cameraGranted,
                shutter = shutter,
                onShutter = { captureStill() },
                onGallery = {
                    gallery.launch(
                        PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly),
                    )
                },
                onOpenCarousel = {
                    if (specimens.isNotEmpty()) reviewing = true
                },
                modifier = Modifier.weight(1f),
            )
        }
    }

    CapturePhotoBlurAlert(controller = blurController) { blurryToken ->
        val index = specimens.indexOf(blurryToken)
        if (index >= 0) persist(specimens.toMutableList().also { it.removeAt(index) })
        reviewing = false
    }
    if (confirmLeave) {
        CaptureConfirmSheet(
            title = stringResource(R.string.capture_unsaved_title),
            body = stringResource(R.string.capture_unsaved_body),
            onConfirm = {
                confirmLeave = false
                onBackClick()
            },
            onDismiss = { confirmLeave = false },
        )
    }
}
