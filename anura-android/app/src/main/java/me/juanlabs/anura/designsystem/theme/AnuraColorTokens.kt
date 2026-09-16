package me.juanlabs.anura.designsystem.theme

import androidx.compose.material3.ColorScheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.ui.graphics.Color

/**
 * Tokens de color crudos extraídos de Penpot (sets `anura-claro`, `anura-oscuro`,
 * `anura-luz-roja`). Ver arquitectura §3.2-3.4. Esta es la única fuente de valores
 * hexadecimales de la app: ningún composable debe hardcodear un color propio,
 * siempre se referencia [MaterialTheme.colorScheme] o [AnuraTheme.extendedColors].
 */
internal data class AnuraColorTokens(
    val accentTint: Color,
    val accentIcon: Color,
    val accentInk: Color,
    val accentPressed: Color,
    val bgBase: Color,
    val bgElevated: Color,
    val bgSubtle: Color,
    val separator: Color,
    val labelPrimary: Color,
    val labelSecondary: Color,
    val labelTertiary: Color,
    val labelOnAccent: Color,
    val statusDanger: Color,
    val statusWarning: Color,
    val statusInfo: Color,
    val statusSuccess: Color,
    val placeholderThumb: Color,
    val placeholderHero: Color,
)

/** `anura-claro` — valores reales verificados contra Penpot (§3.2). */
internal val AnuraLightTokens = AnuraColorTokens(
    accentTint = Color(0xFF34C759),
    accentIcon = Color(0xFF2AA84A),
    accentInk = Color(0xFF1E7A34),
    accentPressed = Color(0xFF248A3D),
    bgBase = Color(0xFFF2F2F7),
    bgElevated = Color(0xFFFFFFFF),
    bgSubtle = Color(0xFFE5E5EA),
    separator = Color(0xFFC6C6C8),
    labelPrimary = Color(0xFF1C1C1E),
    labelSecondary = Color(0xFF8E8E93),
    labelTertiary = Color(0xFFC7C7CC),
    labelOnAccent = Color(0xFFFFFFFF),
    statusDanger = Color(0xFFD70015),
    statusWarning = Color(0xFFFF9500),
    statusInfo = Color(0xFF007AFF),
    statusSuccess = Color(0xFF248A3D),
    placeholderThumb = Color(0xFFE5E5EA),
    placeholderHero = Color(0xFF6E6E73),
)

/** `anura-oscuro` — valores reales verificados contra Penpot (§3.3). */
internal val AnuraDarkTokens = AnuraColorTokens(
    accentTint = Color(0xFF30D158),
    accentIcon = Color(0xFF30D158),
    accentInk = Color(0xFF30D158),
    accentPressed = Color(0xFF34C759),
    bgBase = Color(0xFF000000),
    bgElevated = Color(0xFF1C1C1E),
    bgSubtle = Color(0xFF2C2C2E),
    separator = Color(0xFF38383A),
    labelPrimary = Color(0xFFFFFFFF),
    labelSecondary = Color(0xFF8E8E93),
    labelTertiary = Color(0xFF636366),
    labelOnAccent = Color(0xFF0B2B14),
    statusDanger = Color(0xFFFF453A),
    statusWarning = Color(0xFFFF9F0A),
    statusInfo = Color(0xFF0A84FF),
    statusSuccess = Color(0xFF30D158),
    // placeholder.thumb / placeholder.hero no tienen valor explícito para "oscuro" en el
    // documento de arquitectura (§3.3 solo lista los tokens con valor distinto al claro).
    // Se derivan de bg.subtle / separator por consistencia tonal. Verificar contra Penpot
    // antes de usarlos en un componente real (ObservationCard, etc.).
    placeholderThumb = Color(0xFF2C2C2E),
    placeholderHero = Color(0xFF636366),
)

/** `anura-luz-roja` — valores reales verificados contra Penpot (§3.4). */
internal val AnuraRedLightTokens = AnuraColorTokens(
    accentTint = Color(0xFF6B1F19),
    accentIcon = Color(0xFFFF453A),
    accentInk = Color(0xFFFF453A),
    // accent.pressed no está listado explícitamente en §3.4; se reutiliza accent.tint
    // (mismo criterio monocromático del tema) — verificar contra Penpot.
    accentPressed = Color(0xFF6B1F19),
    bgBase = Color(0xFF000000),
    bgElevated = Color(0xFF160000),
    bgSubtle = Color(0xFF210605),
    separator = Color(0xFF5A170F),
    labelPrimary = Color(0xFFFF453A),
    labelSecondary = Color(0xFFB3352C),
    // label.tertiary no está listado en §3.4; se reutiliza label.secondary — verificar.
    labelTertiary = Color(0xFFB3352C),
    // label.on-accent y los status.* no están listados en §3.4 (tema monocromático rojo,
    // sin semántica de estado propia). Se fuerzan al rojo del tema para no introducir
    // otro matiz que rompa la adaptación nocturna. Verificar contra Penpot.
    labelOnAccent = Color(0xFFFF453A),
    statusDanger = Color(0xFFFF453A),
    statusWarning = Color(0xFFFF453A),
    statusInfo = Color(0xFFFF453A),
    statusSuccess = Color(0xFFFF453A),
    placeholderThumb = Color(0xFF210605),
    placeholderHero = Color(0xFF5A170F),
)

/**
 * Mapea los tokens de Penpot a un [ColorScheme] de Material 3 siguiendo la tabla de
 * roles de §3.2/§3.3. Dynamic color queda desactivado por decisión de arquitectura
 * (§3.7-P4): el color transporta semántica de seguridad y no puede depender del
 * wallpaper del usuario.
 */
internal fun AnuraColorTokens.toColorScheme(isDark: Boolean): ColorScheme {
    val base = if (isDark) darkColorScheme() else lightColorScheme()
    return base.copy(
        primary = accentTint,
        onPrimary = labelOnAccent,
        primaryContainer = accentTint,
        onPrimaryContainer = labelOnAccent,
        background = bgBase,
        onBackground = labelPrimary,
        surface = bgElevated,
        onSurface = labelPrimary,
        surfaceVariant = bgSubtle,
        onSurfaceVariant = labelSecondary,
        outline = labelTertiary,
        outlineVariant = separator,
        error = statusDanger,
        onError = labelOnAccent,
    )
}
