package me.juanlabs.anura.designsystem.preview

import android.content.res.Configuration
import androidx.compose.ui.tooling.preview.Preview

/**
 * Multipreview de verificación del Design System (§15). Cubre automáticamente los
 * modos que Compose puede resolver por `Configuration`/`fontScale`: Claro, Oscuro y
 * texto al 200% (accesibilidad).
 *
 * El modo "Luz roja" NO es un `uiMode` del sistema (§3.4: es una selección manual del
 * usuario, no ligada a `isSystemInDarkTheme()`), así que esta anotación no lo cubre.
 * Cada preview que necesite verificar Luz Roja debe añadir una función de preview
 * separada que envuelva su contenido explícitamente en
 * `AnuraTheme(AnuraThemeMode.LuzRoja) { ... }`.
 */
@Preview(name = "Claro", group = "modo", showBackground = true)
@Preview(
    name = "Oscuro",
    group = "modo",
    showBackground = true,
    uiMode = Configuration.UI_MODE_NIGHT_YES,
)
@Preview(name = "Texto 200%", group = "accesibilidad", showBackground = true, fontScale = 2.0f)
annotation class AnuraPreviews
