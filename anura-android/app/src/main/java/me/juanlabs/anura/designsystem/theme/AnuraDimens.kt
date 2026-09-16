package me.juanlabs.anura.designsystem.theme

import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

/**
 * Tokens de forma y espaciado de `anura-primitivos` (§3.6). Referenciar siempre estos
 * valores en lugar de números sueltos en composables.
 */
object AnuraDimens {
    /** Radio de esquina de botones. */
    val radiusButton: Dp = 12.dp

    /** Radio de esquina de miniaturas. */
    val radiusThumb: Dp = 12.dp

    /** Radio de esquina de [me.juanlabs.anura.designsystem.theme.AnuraShapes] — tarjetas. */
    val radiusCard: Dp = 16.dp

    /** Radio de esquina de diálogos y radio superior de bottom sheets. */
    val radiusModal: Dp = 20.dp

    /** Radio de cápsula para chips (efectivamente circular a la altura usada). */
    val radiusCapsule: Dp = 999.dp

    /** Margen horizontal estándar de pantalla. */
    val spaceGutter: Dp = 20.dp

    /** Espaciado entre elementos relacionados dentro de un mismo grupo. */
    val spaceGap: Dp = 12.dp

    /** Espaciado entre secciones. */
    val spaceSection: Dp = 24.dp

    /** Tamaño del FAB central de la navbar (tamaño real del diseño). */
    val sizeThumb: Dp = 80.dp

    /**
     * Tamaño táctil mínimo. El token de Penpot/HIG es 44dp; Material 3 exige 48dp
     * y gana por la regla de plataforma (§3.7-P1). Nunca usar 44dp en Android.
     */
    val sizeTouch: Dp = 48.dp
}
