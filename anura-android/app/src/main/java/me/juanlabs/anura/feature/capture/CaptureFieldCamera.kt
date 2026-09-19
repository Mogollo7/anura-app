package me.juanlabs.anura.feature.capture

import android.content.Context
import android.util.Log
import android.view.ViewGroup
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import java.io.File
import java.util.concurrent.Executor
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.theme.AnuraDimens

private const val CaptureCameraTag = "AnuraFieldCamera"

internal class CaptureCameraShutter(
    private val context: Context,
    private val executor: Executor,
) {
    var imageCapture: ImageCapture? = null

    fun takePicture(onSaved: (String) -> Unit, onError: () -> Unit) {
        val capture = imageCapture
        if (capture == null) {
            onError()
            return
        }
        val dir = File(context.cacheDir, "anura_batch").apply { mkdirs() }
        val file = File(dir, "specimen_${System.currentTimeMillis()}.jpg")
        val options = ImageCapture.OutputFileOptions.Builder(file).build()
        capture.takePicture(
            options,
            executor,
            object : ImageCapture.OnImageSavedCallback {
                override fun onImageSaved(outputFileResults: ImageCapture.OutputFileResults) {
                    onSaved("file:${file.absolutePath}")
                }

                override fun onError(exception: ImageCaptureException) {
                    Log.w(CaptureCameraTag, "No se pudo guardar la captura", exception)
                    onError()
                }
            },
        )
    }
}

@Composable
internal fun rememberCaptureCameraShutter(): CaptureCameraShutter {
    val context = LocalContext.current
    val executor = remember(context) { ContextCompat.getMainExecutor(context) }
    return remember(context) { CaptureCameraShutter(context, executor) }
}

/**
 * Vista previa de cámara en la app (Batch Field Capture).
 * El obturador no cierra el visor: cada toma se suma a la cola de especímenes.
 */
@Composable
internal fun CaptureFieldCameraPreview(
    shutter: CaptureCameraShutter,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    var bindFailed by remember { mutableStateOf(false) }
    val previewView = remember {
        PreviewView(context).apply {
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT,
            )
            scaleType = PreviewView.ScaleType.FILL_CENTER
            implementationMode = PreviewView.ImplementationMode.COMPATIBLE
        }
    }

    DisposableEffect(lifecycleOwner, enabled) {
        if (!enabled) {
            shutter.imageCapture = null
            onDispose { }
        } else {
            val cameraProviderFuture = ProcessCameraProvider.getInstance(context)
            val executor = ContextCompat.getMainExecutor(context)
            val listener = Runnable {
                try {
                    val cameraProvider = cameraProviderFuture.get()
                    val preview = Preview.Builder().build().also { useCase ->
                        useCase.surfaceProvider = previewView.surfaceProvider
                    }
                    val imageCapture = ImageCapture.Builder()
                        .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                        .build()
                    cameraProvider.unbindAll()
                    cameraProvider.bindToLifecycle(
                        lifecycleOwner,
                        CameraSelector.DEFAULT_BACK_CAMERA,
                        preview,
                        imageCapture,
                    )
                    shutter.imageCapture = imageCapture
                    bindFailed = false
                } catch (error: Exception) {
                    Log.w(CaptureCameraTag, "No se pudo abrir la cámara", error)
                    shutter.imageCapture = null
                    bindFailed = true
                }
            }
            cameraProviderFuture.addListener(listener, executor)
            onDispose {
                shutter.imageCapture = null
                runCatching { cameraProviderFuture.get().unbindAll() }
            }
        }
    }

    if (bindFailed) {
        CapturePhotoPreview(
            token = "",
            processing = false,
            modifier = modifier,
        )
    } else {
        AndroidView(
            factory = { previewView },
            modifier = modifier
                .fillMaxSize()
                .clip(RoundedCornerShape(AnuraDimens.radiusCard))
                .semantics {
                    contentDescription = context.getString(R.string.capture_step4_camera_cd)
                },
        )
    }
}

@Composable
internal fun CaptureBatchFieldCapture(
    specimens: List<String>,
    capturing: Boolean,
    cameraGranted: Boolean,
    shutter: CaptureCameraShutter,
    onShutter: () -> Unit,
    onGallery: () -> Unit,
    onOpenCarousel: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(modifier = modifier.fillMaxSize()) {
        CaptureFieldCameraPreview(
            shutter = shutter,
            enabled = cameraGranted,
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
                .padding(horizontal = AnuraDimens.spaceGutter),
        )
        CaptureCameraTransport(
            lastToken = specimens.lastOrNull().orEmpty(),
            photoCount = specimens.size,
            capturing = capturing,
            cameraGranted = cameraGranted,
            onGallery = onGallery,
            onShutter = onShutter,
            onOpenCarousel = onOpenCarousel,
        )
    }
}

internal fun mockQueuedSpecimen(index: Int): String = mockPoseToken(index)
