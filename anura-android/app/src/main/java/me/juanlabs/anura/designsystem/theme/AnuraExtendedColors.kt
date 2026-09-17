package me.juanlabs.anura.designsystem.theme

import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Color

/**
 * Roles de color de ANURA que no tienen equivalente directo en el [androidx.compose.material3.ColorScheme]
 * de Material 3 (§3.2/§3.3): acentos secundarios, estados semánticos (warning/info/success) y
 * placeholders de imagen. Se expone vía [AnuraTheme.extendedColors], nunca hardcodeado en un
 * composable.
 */
data class AnuraExtendedColors(
    val accentIcon: Color,
    val accentInk: Color,
    val accentPressed: Color,
    val warning: Color,
    val info: Color,
    val success: Color,
    val placeholderThumb: Color,
    val placeholderHero: Color,
    // Contrapartes "on-X" para texto/icono sobre un fondo warning/info/success (p.ej.
    // AnuraStatusChip). Material 3 no define estos roles porque warning/info/success no
    // son roles nativos de ColorScheme. Penpot tampoco los especifica explícitamente en
    // §3.2/§3.3 (solo da el color de fondo, no el de contenido) — se derivan aquí por
    // contraste (WCAG AA) y quedan documentados como derivados, no extraídos.
    val onWarning: Color,
    val onInfo: Color,
    val onSuccess: Color,
    /**
     * Vidrio claro HIG (Light Glass / Vibrancy) sobre media: tinte blanco translúcido.
     * API 31+ se combina con backdrop blur; por debajo, usar [glassLightFallback].
     */
    val glassLight: Color,
    val glassLightFallback: Color,
    val glassStroke: Color,
    /** Texto sobre vidrio claro. Siempre blanco (`Color.White`) para contraste sobre foto. */
    val onGlass: Color,
    val onGlassShadow: Color,
)

internal fun AnuraColorTokens.toExtendedColors(): AnuraExtendedColors = AnuraExtendedColors(
    accentIcon = accentIcon,
    accentInk = accentInk,
    accentPressed = accentPressed,
    warning = statusWarning,
    info = statusInfo,
    success = statusSuccess,
    placeholderThumb = placeholderThumb,
    placeholderHero = placeholderHero,
    // status.warning es un naranja de brillo medio-alto en los 3 temas: texto oscuro
    // pasa contraste AA, blanco no siempre. status.info/status.success son azul/verde
    // suficientemente saturados para texto blanco en los 3 temas.
    onWarning = Color(0xFF1C1C1E),
    onInfo = Color(0xFFFFFFFF),
    onSuccess = Color(0xFFFFFFFF),
    // Light Glass HIG: mismo overlay sobre foto en claro/oscuro/luz roja.
    glassLight = Color.White.copy(alpha = 0.32f),
    glassLightFallback = Color.White.copy(alpha = 0.55f),
    glassStroke = Color.White.copy(alpha = 0.42f),
    onGlass = Color.White,
    onGlassShadow = Color.Black.copy(alpha = 0.55f),
)

/** Valor por defecto sin usar: [AnuraTheme] siempre provee el valor real antes de `content`. */
internal val LocalAnuraExtendedColors = staticCompositionLocalOf {
    AnuraExtendedColors(
        accentIcon = Color.Unspecified,
        accentInk = Color.Unspecified,
        accentPressed = Color.Unspecified,
        warning = Color.Unspecified,
        info = Color.Unspecified,
        success = Color.Unspecified,
        placeholderThumb = Color.Unspecified,
        placeholderHero = Color.Unspecified,
        onWarning = Color.Unspecified,
        onInfo = Color.Unspecified,
        onSuccess = Color.Unspecified,
        glassLight = Color.Unspecified,
        glassLightFallback = Color.Unspecified,
        glassStroke = Color.Unspecified,
        onGlass = Color.Unspecified,
        onGlassShadow = Color.Unspecified,
    )
}
