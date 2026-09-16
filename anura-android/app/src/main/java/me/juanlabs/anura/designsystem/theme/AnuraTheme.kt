package me.juanlabs.anura.designsystem.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.ColorScheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Shapes
import androidx.compose.material3.Typography
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider

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
            AnuraThemeMode.Sistema -> AnuraLightTokens // inalcanzable, resuelto arriba
        }
        val isDark = resolvedMode == AnuraThemeMode.Oscuro || resolvedMode == AnuraThemeMode.LuzRoja

        CompositionLocalProvider(LocalAnuraExtendedColors provides tokens.toExtendedColors()) {
            MaterialTheme(
                colorScheme = tokens.toColorScheme(isDark),
                typography = AnuraTypography,
                shapes = AnuraShapes,
                content = content,
            )
        }
    }
}
