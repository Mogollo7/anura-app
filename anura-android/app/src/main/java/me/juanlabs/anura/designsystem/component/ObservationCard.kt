package me.juanlabs.anura.designsystem.component

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.preview.SampleData
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

/**
 * Tarjeta de observación (`COMP · Tarjeta de observación`, 167×196, §3.9). Se conserva
 * la PROPORCIÓN (167:196) y la composición relativa (chip arriba-izq, corazón
 * arriba-der, panel con nombre común+científico abajo con atenuado negro 35%), no las
 * coordenadas absolutas del board — así el layout escala en distintos anchos de grilla
 * sin romperse (regla P6, §3.7).
 *
 * Puramente presentacional: no conoce `Observation` ni ningún repositorio. Quien la usa
 * decide de dónde vienen los datos (fake, Room, etc. — fases posteriores). Tampoco
 * decide su disposición en grilla (`LazyVerticalGrid` de 2 columnas, §3.9): esa es una
 * decisión de la pantalla que la use, no del componente.
 *
 * A11y: la tarjeta entera es un solo nodo de TalkBack (`mergeDescendants`) con nombre
 * común + científico; el corazón de favorito se mantiene como acción separada y
 * focalizable propia (§14 — "un solo foco por tarjeta... no seis").
 */
@Composable
fun ObservationCard(
    commonName: String,
    scientificName: String,
    isFavorite: Boolean,
    onFavoriteClick: () -> Unit,
    modifier: Modifier = Modifier,
    statusChip: @Composable (() -> Unit)? = null,
    thumbnail: @Composable () -> Unit = {},
    onClick: (() -> Unit)? = null,
) {
    val extended = AnuraTheme.extendedColors
    var cardModifier = modifier
        .aspectRatio(167f / 196f)
        .clip(RoundedCornerShape(AnuraDimens.radiusCard))
        .semantics(mergeDescendants = true) {}
    if (onClick != null) {
        cardModifier = cardModifier.clickable(onClick = onClick)
    }

    Box(modifier = cardModifier) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(extended.placeholderThumb),
        ) {
            thumbnail()
        }

        // Atenuado negro 35% en degradado, para que el texto del panel sea legible
        // sobre cualquier foto (§3.9).
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .fillMaxHeight(0.5f)
                .align(Alignment.BottomCenter)
                .background(
                    Brush.verticalGradient(
                        colors = listOf(Color.Transparent, Color.Black.copy(alpha = 0.35f)),
                    ),
                ),
        )

        if (statusChip != null) {
            Box(
                modifier = Modifier
                    .align(Alignment.TopStart)
                    .padding(start = 10.dp, top = 10.dp),
            ) {
                statusChip()
            }
        }

        IconButton(
            onClick = onFavoriteClick,
            modifier = Modifier
                .align(Alignment.TopEnd)
                .size(AnuraDimens.sizeTouch), // 48dp táctil mínimo (§3.7-P1), aunque el
            // dibujo de Penpot mida 30dp visualmente
        ) {
            Icon(
                imageVector = if (isFavorite) AnuraIcons.Favorite else AnuraIcons.FavoriteBorder,
                contentDescription = if (isFavorite) "Quitar de favoritos" else "Añadir a favoritos",
                tint = Color.White,
            )
        }

        Column(
            modifier = Modifier
                .align(Alignment.BottomStart)
                .fillMaxWidth()
                .padding(horizontal = 10.dp, vertical = 8.dp),
        ) {
            Text(
                text = commonName,
                color = Color.White,
                style = MaterialTheme.typography.titleMedium,
                maxLines = 1,
            )
            Text(
                // Los nombres científicos siempre van en cursiva: convención taxonómica,
                // no opcional (§3.5).
                text = scientificName,
                color = Color.White.copy(alpha = 0.85f),
                style = MaterialTheme.typography.bodySmall.copy(fontStyle = FontStyle.Italic),
                maxLines = 1,
            )
        }
    }
}

@Composable
private fun ObservationCardPreviewContent() {
    var favoriteShort by remember { mutableStateOf(false) }
    var favoriteLong by remember { mutableStateOf(true) }
    Row(horizontalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap)) {
        ObservationCard(
            commonName = SampleData.CommonNameShort,
            scientificName = SampleData.ScientificNameShort,
            isFavorite = favoriteShort,
            onFavoriteClick = { favoriteShort = !favoriteShort },
            modifier = Modifier.width(167.dp),
            statusChip = { AnuraToxicityChip(AnuraToxicityChipVariant.Toxic) },
        )
        // Nombres largos de verdad: revela si el layout trunca en vez de romperse.
        ObservationCard(
            commonName = SampleData.CommonNameLong,
            scientificName = SampleData.ScientificNameLong,
            isFavorite = favoriteLong,
            onFavoriteClick = { favoriteLong = !favoriteLong },
            modifier = Modifier.width(167.dp),
            statusChip = { AnuraConservationChip(AnuraConservationChipVariant.CR) },
        )
    }
}

@AnuraPreviews
@Composable
private fun ObservationCardPreview() {
    AnuraTheme { ObservationCardPreviewContent() }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun ObservationCardPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) { ObservationCardPreviewContent() }
}
