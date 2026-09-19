package me.juanlabs.anura.designsystem.component

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.sizeIn
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

/**
 * Un destino de la barra inferior. Puramente presentacional: no conoce `AnuraRoute` ni
 * `NavController` (regla de frontera §2 — `designsystem` no depende de `navigation`).
 */
data class AnuraNavBarItem(
    val label: String,
    val icon: ImageVector,
)

/** Medidas Penpot `navbar` en `home`: grupo 350×113, píldora 350×75 @ y=38, FAB 80×80 @ y=0. */
private val AnuraNavChromeHeight = 113.dp
private val AnuraNavPillHeight = 75.dp
private val AnuraNavPillHorizontalInset = 22.dp
private val AnuraNavFabSize = AnuraDimens.sizeFab // 80 dp
private val AnuraNavFabIconSize = 32.dp
private val AnuraNavItemIconSize = 24.dp

/**
 * Barra inferior ANURA fiel a Penpot (`COMP · Navbar` / `home` · navbar):
 * píldora Liquid Glass + FAB central 80×80 tintado de marca integrado en el eje
 * (no un FAB flotante del Scaffold).
 *
 * Iconos Material; 4 destinos con etiqueta; el hueco central es el FAB.
 */
@Composable
fun AnuraNavBar(
    items: List<AnuraNavBarItem>,
    selectedIndex: Int,
    onItemSelected: (Int) -> Unit,
    onFabClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    require(items.size == 4) {
        "AnuraNavBar espera exactamente 4 destinos (Inicio · Explorar · Listado · Ajustes)."
    }

    val extended = AnuraTheme.extendedColors

    Box(
        modifier = modifier
            .fillMaxWidth()
            .navigationBarsPadding()
            .padding(horizontal = AnuraNavPillHorizontalInset)
            .height(AnuraNavChromeHeight),
    ) {
        // Píldora Liquid Glass (blanca 92%) anclada abajo; el FAB la solapa desde arriba.
        Surface(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .fillMaxWidth()
                .height(AnuraNavPillHeight),
            shape = RoundedCornerShape(AnuraDimens.radiusCapsule),
            color = MaterialTheme.colorScheme.surface.copy(alpha = 0.92f),
            border = BorderStroke(1.dp, extended.cardStroke),
            shadowElevation = 0.dp,
            tonalElevation = 0.dp,
        ) {
            Row(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(horizontal = 4.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Row(
                    modifier = Modifier.weight(1f),
                    horizontalArrangement = Arrangement.SpaceEvenly,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    AnuraNavTab(
                        item = items[0],
                        selected = selectedIndex == 0,
                        onClick = { onItemSelected(0) },
                    )
                    AnuraNavTab(
                        item = items[1],
                        selected = selectedIndex == 1,
                        onClick = { onItemSelected(1) },
                    )
                }

                Spacer(modifier = Modifier.width(AnuraNavFabSize))

                Row(
                    modifier = Modifier.weight(1f),
                    horizontalArrangement = Arrangement.SpaceEvenly,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    AnuraNavTab(
                        item = items[2],
                        selected = selectedIndex == 2,
                        onClick = { onItemSelected(2) },
                    )
                    AnuraNavTab(
                        item = items[3],
                        selected = selectedIndex == 3,
                        onClick = { onItemSelected(3) },
                    )
                }
            }
        }

        // FAB 80×80 · Liquid Glass TINTADO de marca — clickable estático (sin
        // Surface(onClick), que anima elevation y puede percibirse como salto).
        Surface(
            modifier = Modifier
                .align(Alignment.TopCenter)
                .size(AnuraNavFabSize)
                .clip(CircleShape)
                .clickable(role = Role.Button, onClick = onFabClick),
            shape = CircleShape,
            color = extended.accentInk,
            shadowElevation = 0.dp,
            tonalElevation = 0.dp,
        ) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    imageVector = AnuraIcons.Add,
                    contentDescription = "Añadir observación",
                    tint = MaterialTheme.colorScheme.onPrimary,
                    modifier = Modifier.size(AnuraNavFabIconSize),
                )
            }
        }
    }
}

@Composable
private fun AnuraNavTab(
    item: AnuraNavBarItem,
    selected: Boolean,
    onClick: () -> Unit,
) {
    val tint = if (selected) {
        AnuraTheme.extendedColors.accentInk
    } else {
        MaterialTheme.colorScheme.onSurfaceVariant
    }

    Column(
        modifier = Modifier
            .sizeIn(minWidth = AnuraDimens.sizeTouch, minHeight = AnuraDimens.sizeTouch)
            .selectable(selected = selected, role = Role.Tab, onClick = onClick),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
    ) {
        Icon(
            imageVector = item.icon,
            contentDescription = null,
            tint = tint,
            modifier = Modifier.size(AnuraNavItemIconSize),
        )
        Text(
            text = item.label,
            style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
            color = tint,
            textAlign = TextAlign.Center,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
        )
    }
}

@Composable
private fun AnuraNavBarPreviewContent() {
    val items = listOf(
        AnuraNavBarItem("Inicio", AnuraIcons.Home),
        AnuraNavBarItem("Explorar", AnuraIcons.Explore),
        AnuraNavBarItem("Listado", AnuraIcons.Observations),
        AnuraNavBarItem("Ajustes", AnuraIcons.Settings),
    )
    Box(modifier = Modifier.padding(top = 24.dp)) {
        AnuraNavBar(
            items = items,
            selectedIndex = 0,
            onItemSelected = {},
            onFabClick = {},
        )
    }
}

@AnuraPreviews
@Composable
private fun AnuraNavBarPreview() {
    AnuraTheme { AnuraNavBarPreviewContent() }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun AnuraNavBarPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) { AnuraNavBarPreviewContent() }
}
