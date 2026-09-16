package me.juanlabs.anura.designsystem.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

/**
 * Tipografía de ANURA mapeada sobre roles de Material 3, con los tamaños reales de
 * `anura-primitivos` (§3.5). La familia real del archivo de Penpot es **Inter Tight**
 * (889/893 textos), pero sus archivos `.ttf` todavía no existen en `res/font/` de este
 * módulo. Se usa [FontFamily.Default] como marcador temporal: cuando se añadan los
 * recursos de fuente, solo hay que cambiar [AnuraFontFamily] aquí, no cada composable.
 *
 * Los pesos (400/500/600/700) por rol son una asignación razonable a partir de los
 * nombres de estilo de la biblioteca de Penpot (`Título 25`, `Normal 20 +Semibold`,
 * `Descriptivo 15 +Semibold`, `Mínimo 10 +Semibold`) y deben confirmarse contra Penpot
 * antes de darse por definitivos.
 */
internal val AnuraFontFamily: FontFamily = FontFamily.Default

val AnuraTypography: Typography = Typography(
    // font.large-title — 34sp
    displaySmall = TextStyle(
        fontFamily = AnuraFontFamily,
        fontWeight = FontWeight.Bold,
        fontSize = 34.sp,
        lineHeight = 41.sp,
    ),
    // font.title1 — 28sp
    headlineMedium = TextStyle(
        fontFamily = AnuraFontFamily,
        fontWeight = FontWeight.Bold,
        fontSize = 28.sp,
        lineHeight = 34.sp,
    ),
    // font.title2 — 22sp
    headlineSmall = TextStyle(
        fontFamily = AnuraFontFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 22.sp,
        lineHeight = 28.sp,
    ),
    // font.title3 — 20sp
    titleLarge = TextStyle(
        fontFamily = AnuraFontFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 20.sp,
        lineHeight = 25.sp,
    ),
    // font.body — 17sp
    bodyLarge = TextStyle(
        fontFamily = AnuraFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 17.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.2.sp,
    ),
    // font.callout — 16sp
    bodyMedium = TextStyle(
        fontFamily = AnuraFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 22.sp,
        letterSpacing = 0.2.sp,
    ),
    // font.subhead — 15sp
    titleMedium = TextStyle(
        fontFamily = AnuraFontFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 15.sp,
        lineHeight = 20.sp,
    ),
    // font.footnote — 13sp
    bodySmall = TextStyle(
        fontFamily = AnuraFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 13.sp,
        lineHeight = 18.sp,
        letterSpacing = 0.3.sp,
    ),
    // font.caption — 11sp
    labelSmall = TextStyle(
        fontFamily = AnuraFontFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 11.sp,
        lineHeight = 14.sp,
        letterSpacing = 0.4.sp,
    ),
)
