package me.juanlabs.anura.feature.capture

import android.content.Context
import androidx.compose.runtime.Composable
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.platform.LocalContext
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.launch
import me.juanlabs.anura.core.image.BlurDetectorHelper

/**
 * Orquesta detección de borrosidad + alerta reutilizable.
 *
 * Lo usa el flujo de Foto ID ([PhotoCaptureScreen] → [CaptureAddPhotoFlow]).
 */
class CapturePhotoBlurController internal constructor(
    private val context: Context,
    private val scope: CoroutineScope,
    private val tokenState: MutableState<String?>,
) {
    var blurryToken: String?
        get() = tokenState.value
        set(value) {
            tokenState.value = value
        }

    fun inspect(tokens: List<String>) {
        if (tokens.isEmpty()) return
        scope.launch {
            val blurry = tokens.firstOrNull { token ->
                BlurDetectorHelper.isBlurryToken(context, token)
            }
            if (blurry != null) blurryToken = blurry
        }
    }

    fun dismiss() {
        blurryToken = null
    }
}

@Composable
internal fun rememberCapturePhotoBlurController(): CapturePhotoBlurController {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val tokenState = rememberSaveable { mutableStateOf<String?>(null) }
    return remember(context, scope, tokenState) {
        CapturePhotoBlurController(context, scope, tokenState)
    }
}

@Composable
internal fun CapturePhotoBlurAlert(
    controller: CapturePhotoBlurController,
    onRetakeToken: (String) -> Unit,
) {
    val token = controller.blurryToken ?: return
    CaptureBlurryPhotoSheet(
        imageToken = token,
        onRetake = {
            controller.dismiss()
            onRetakeToken(token)
        },
        onAccept = { controller.dismiss() },
        onDismiss = { controller.dismiss() },
    )
}
