package me.juanlabs.anura.designsystem.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.ColorScheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Shapes
import androidx.compose.material3.Typography
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.graphics.ColorFilter
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.Density

/**
 * Modo de tema de ANURA. No es lo mismo que `light/dark` de Android: [LuzRoja] es un
 * tercer tema explícito, seleccionado manualmente por el usuario, no derivado de
 * `isSystemInDarkTheme()` (§3.4). Persistencia en DataStore llega en un bloque
 * posterior (B5); aquí solo se define el tipo y la resolución visual.
 */
enum class AnuraThemeMode {
    Claro,
    Oscuro,
    LuzRoja,
    Sistema,
}

/** Muestra de acento en Apariencia: pinta botones y `accentInk` / `primary`. */
enum class AnuraAccentRole {
    Tint,
    Icon,
    Ink,
    Danger,
    Warning,
    Info,
}

internal fun AnuraColorTokens.colorFor(role: AnuraAccentRole) = when (role) {
    AnuraAccentRole.Tint -> accentTint
    AnuraAccentRole.Icon -> accentIcon
    AnuraAccentRole.Ink -> accentInk
    AnuraAccentRole.Danger -> statusDanger
    AnuraAccentRole.Warning -> statusWarning
    AnuraAccentRole.Info -> statusInfo
}

/**
 * Design System theme de ANURA. Sigue el mismo patrón que [MaterialTheme]: un objeto
 * con `operator fun invoke` como composable de theming y propiedades de solo lectura
 * para leer el tema activo desde cualquier composable (`AnuraTheme.extendedColors`,
 * análogo a `MaterialTheme.colorScheme`).
 *
 * Dynamic color queda desactivado a propósito (§3.7-P4): el color transporta
 * semántica de seguridad (toxicidad, IUCN, luz roja) y no puede depender del
 * wallpaper del usuario.
 */
object AnuraTheme {

    val extendedColors: AnuraExtendedColors
        @Composable
        get() = LocalAnuraExtendedColors.current

    val swatchColors: AnuraSwatchColors
        @Composable
        get() = LocalAnuraSwatchColors.current

    val mediaColorFilter: ColorFilter?
        @Composable
        get() = LocalAnuraMediaColorFilter.current

    val colorScheme: ColorScheme
        @Composable
        get() = MaterialTheme.colorScheme

    val typography: Typography
        @Composable
        get() = MaterialTheme.typography

    val shapes: Shapes
        @Composable
        get() = MaterialTheme.shapes

    @Composable
    operator fun invoke(
        themeMode: AnuraThemeMode = AnuraThemeMode.Sistema,
        accentRole: AnuraAccentRole = AnuraAccentRole.Ink,
        preferReduceMotion: Boolean = false,
        preferLargeText: Boolean = false,
        content: @Composable () -> Unit,
    ) {
        val systemDark = isSystemInDarkTheme()
        val resolvedMode = if (themeMode == AnuraThemeMode.Sistema) {
            if (systemDark) AnuraThemeMode.Oscuro else AnuraThemeMode.Claro
        } else {
            themeMode
        }

        val tokens = when (resolvedMode) {
            AnuraThemeMode.Claro -> AnuraLightTokens
            AnuraThemeMode.Oscuro -> AnuraDarkTokens
            AnuraThemeMode.LuzRoja -> AnuraRedLightTokens
            AnuraThemeMode.Sistema -> AnuraLightTokens
        }
        val isDark = resolvedMode == AnuraThemeMode.Oscuro || resolvedMode == AnuraThemeMode.LuzRoja
        val accent = tokens.colorFor(accentRole)
        val extended = tokens.toExtendedColors()
        val onAccent = if (accentRole == AnuraAccentRole.Warning) {
            extended.onWarning
        } else {
            tokens.labelOnAccent
        }

        val density = LocalDensity.current
        val themedContent: @Composable () -> Unit = {
            CompositionLocalProvider(
                LocalAnuraExtendedColors provides extended.copy(
                    accentIcon = accent,
                    accentInk = accent,
                    accentPressed = accent,
                ),
                LocalAnuraSwatchColors provides tokens.toSwatchColors(),
                LocalPreferReduceMotion provides preferReduceMotion,
                LocalAnuraMediaColorFilter provides if (resolvedMode == AnuraThemeMode.LuzRoja) {
                    AnuraRedLightMediaColorFilter
                } else {
                    null
                },
            ) {
                MaterialTheme(
                    colorScheme = tokens.toColorScheme(isDark).copy(
                        primary = accent,
                        primaryContainer = accent,
                        onPrimary = onAccent,
                        onPrimaryContainer = onAccent,
                    ),
                    typography = AnuraTypography,
                    shapes = AnuraShapes,
                    content = content,
                )
            }
        }
        if (preferLargeText) {
            CompositionLocalProvider(
                LocalDensity provides Density(
                    density = density.density,
                    fontScale = density.fontScale * 1.15f,
                ),
            ) {
                themedContent()
            }
        } else {
            themedContent()
        }
    }
}
