package me.juanlabs.anura.designsystem.component

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

/**
 * Variante visual del chip de toxicidad (`COMP · Peligro e IUCN`, §3.9). Esto NO es el
 * modelo de dominio `ToxicityStatus` (§7, fase posterior) — es solo la selección de
 * apariencia; ningún dato ni regla de negocio vive aquí.
 */
enum class AnuraToxicityChipVariant { Toxic, Harmless }

/**
 * Variante visual del chip de conservación IUCN. Igual que [AnuraToxicityChipVariant]:
 * solo apariencia, no el modelo de dominio `ConservationStatus`. Solo existen las 6
 * categorías que Penpot dibuja (CR/EN/VU/NT/LC/DD) — no se inventan EX/EW/NE (§7).
 */
enum class AnuraConservationChipVariant(val shortLabel: String, val fullLabel: String) {
    CR("CR", "En peligro crítico"),
    EN("EN", "En peligro"),
    VU("VU", "Vulnerable"),
    NT("NT", "Casi amenazada"),
    LC("LC", "Preocupación menor"),
    DD("DD", "Datos insuficientes"),
}

/**
 * Relleno del chip "Tóxica": valor literal tomado de `COMP · Peligro e IUCN` (§3.9),
 * distinto de `status.danger` (§3.2/§3.3) — es un token propio de este componente, no
 * el rol `error` de M3. No hay variante oscura/luz-roja documentada para este valor
 * específico; se mantiene fijo en los 3 temas, igual criterio que `bg.base = #000000`.
 */
private val ToxicChipFill = Color(0xFF9F1E18)

/**
 * Chip de toxicidad. La señal nunca depende solo del color (§6 de Penpot): el icono y
 * el texto completo ("Tóxica"/"Inofensiva") siempre están presentes.
 */
@Composable
fun AnuraToxicityChip(
    variant: AnuraToxicityChipVariant,
    modifier: Modifier = Modifier,
) {
    val extended = AnuraTheme.extendedColors
    val (containerColor, contentColor, icon, label) = when (variant) {
        AnuraToxicityChipVariant.Toxic ->
            ChipLook(ToxicChipFill, Color.White, AnuraIcons.Warning, "Tóxica")

        AnuraToxicityChipVariant.Harmless ->
            ChipLook(extended.success, extended.onSuccess, AnuraIcons.Success, "Inofensiva")
    }
    AnuraChipShell(
        containerColor = containerColor,
        contentColor = contentColor,
        icon = icon,
        label = label,
        contentDescription = "Toxicidad: $label",
        modifier = modifier,
    )
}

/**
 * Chip de estado de conservación IUCN. Se agrupan las 6 categorías en 3 niveles
 * semánticos de urgencia (crítico/atención/estable) porque Penpot no fija un color
 * distinto por cada una de las 6 — pero la etiqueta de texto siempre muestra la
 * categoría completa en el `contentDescription`, nunca solo el color, cumpliendo §6.
 */
@Composable
fun AnuraConservationChip(
    variant: AnuraConservationChipVariant,
    modifier: Modifier = Modifier,
) {
    val extended = AnuraTheme.extendedColors
    val colors = MaterialTheme.colorScheme
    val (containerColor, contentColor, icon) = when (variant) {
        AnuraConservationChipVariant.CR,
        AnuraConservationChipVariant.EN,
        -> Triple(colors.error, colors.onError, AnuraIcons.Warning)

        AnuraConservationChipVariant.VU,
        AnuraConservationChipVariant.NT,
        -> Triple(extended.warning, extended.onWarning, AnuraIcons.Info)

        AnuraConservationChipVariant.LC ->
            Triple(extended.success, extended.onSuccess, AnuraIcons.Success)

        AnuraConservationChipVariant.DD ->
            Triple(colors.surfaceVariant, colors.onSurfaceVariant, AnuraIcons.Info)
    }
    AnuraChipShell(
        containerColor = containerColor,
        contentColor = contentColor,
        icon = icon,
        label = variant.shortLabel,
        contentDescription = "Estado de conservación: ${variant.fullLabel}",
        modifier = modifier,
    )
}

private data class ChipLook(
    val containerColor: Color,
    val contentColor: Color,
    val icon: ImageVector,
    val label: String,
)

@Composable
private fun AnuraChipShell(
    containerColor: Color,
    contentColor: Color,
    icon: ImageVector,
    label: String,
    contentDescription: String,
    modifier: Modifier = Modifier,
) {
    Row(
        modifier = modifier
            .clip(RoundedCornerShape(AnuraDimens.radiusCapsule))
            .background(containerColor)
            .padding(horizontal = 10.dp, vertical = 4.dp)
            .semantics { this.contentDescription = contentDescription },
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null, // el contentDescription completo va en el Row
            tint = contentColor,
            modifier = Modifier.size(14.dp),
        )
        Text(
            text = label,
            color = contentColor,
            style = MaterialTheme.typography.labelSmall,
        )
    }
}

@Composable
private fun AnuraStatusChipPreviewContent() {
    Column(
        modifier = Modifier.padding(AnuraDimens.spaceGap),
        verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
    ) {
        Row(horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap)) {
            AnuraToxicityChip(AnuraToxicityChipVariant.Toxic)
            AnuraToxicityChip(AnuraToxicityChipVariant.Harmless)
        }
        Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
            AnuraConservationChipVariant.entries.forEach { variant ->
                AnuraConservationChip(variant)
            }
        }
    }
}

@AnuraPreviews
@Composable
private fun AnuraStatusChipPreview() {
    AnuraTheme { AnuraStatusChipPreviewContent() }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun AnuraStatusChipPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) { AnuraStatusChipPreviewContent() }
}
