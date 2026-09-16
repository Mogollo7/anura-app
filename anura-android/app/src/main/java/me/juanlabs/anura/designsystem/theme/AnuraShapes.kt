package me.juanlabs.anura.designsystem.theme

import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Shapes

/**
 * [Shapes] de Material 3 derivadas de los radios de `anura-primitivos` (§3.6).
 * No existe un token de Penpot distinto para `extraSmall`: se reutiliza el radio
 * de botón como base más pequeña disponible.
 */
val AnuraShapes: Shapes = Shapes(
    extraSmall = RoundedCornerShape(AnuraDimens.radiusButton),
    small = RoundedCornerShape(AnuraDimens.radiusThumb),
    medium = RoundedCornerShape(AnuraDimens.radiusCard),
    large = RoundedCornerShape(AnuraDimens.radiusModal),
    extraLarge = RoundedCornerShape(AnuraDimens.radiusCapsule),
)
