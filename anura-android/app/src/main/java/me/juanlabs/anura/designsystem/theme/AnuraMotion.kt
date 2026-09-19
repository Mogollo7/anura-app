package me.juanlabs.anura.designsystem.theme

import android.provider.Settings
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.platform.LocalContext

/**
 * Duraciones de animación de ANURA (§3.9). Referenciar siempre estos valores en lugar de
 * milisegundos sueltos en composables.
 */
object AnuraMotion {
    /** Feedback de estado/selección (HIG ~150–200 ms). */
    const val DurationShort = 150

    /** Transiciones entre pantallas / cambios de contenido. */
    const val DurationMedium = 250
}

/** true si el sistema tiene "Quitar animaciones" (ANIMATOR_DURATION_SCALE == 0). */
@Composable
fun rememberReduceMotion(): Boolean {
    val context = LocalContext.current
    return remember {
        Settings.Global.getFloat(context.contentResolver, Settings.Global.ANIMATOR_DURATION_SCALE, 1f) == 0f
    }
}
