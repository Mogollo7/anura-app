package me.juanlabs.anura.designsystem.component

import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.tooling.preview.Preview
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

/**
 * Un destino de la barra inferior. Puramente presentacional: no conoce `AnuraRoute` ni
 * `NavController` (regla de frontera §2 — `designsystem` no depende de `navigation`).
 * Quien la usa (`navigation/AnuraScaffold`) traduce la selección de índice a
 * navegación real.
 */
data class AnuraNavBarItem(
    val label: String,
    val icon: ImageVector,
)

/**
 * Barra de navegación inferior de ANURA (`COMP · Navbar`, §3.9). Se usa el
 * `NavigationBar` de Material 3 (decisión 8/9, §3.7-P2), no la píldora Liquid Glass
 * de Penpot: se conserva la composición (4 destinos con etiqueta) y el acento; se
 * pierde el fondo flotante.
 *
 * §3.7-P5/P9: Penpot especifica que el ítem activo "no crece, cero tween de posición o
 * escala" — se usan los valores por defecto de M3 (solo cambio de color/indicador), sin
 * añadir animación de escala o posición.
 *
 * `material-icons-core` no tiene una pareja filled/outline para estos iconos concretos
 * (sí la tiene `Favorite`/`FavoriteBorder`, pero no `Home`/`Search`/`List`/`Settings`):
 * la diferenciación seleccionado/no-seleccionado se resuelve con el color de M3 por
 * defecto, no con un cambio de glifo. Se documenta como limitación temporal del set de
 * iconos (§3.8), a corregir cuando se importen los SVG reales de Penpot.
 */
@Composable
fun AnuraNavBar(
    items: List<AnuraNavBarItem>,
    selectedIndex: Int,
    onItemSelected: (Int) -> Unit,
    modifier: Modifier = Modifier,
) {
    NavigationBar(modifier = modifier) {
        items.forEachIndexed { index, item ->
            NavigationBarItem(
                selected = index == selectedIndex,
                onClick = { onItemSelected(index) },
                icon = { Icon(imageVector = item.icon, contentDescription = null) },
                label = { Text(item.label) },
            )
        }
    }
}

@Composable
private fun AnuraNavBarPreviewContent() {
    val items = listOf(
        AnuraNavBarItem("Inicio", AnuraIcons.Home),
        AnuraNavBarItem("Explorar", AnuraIcons.Explore),
        AnuraNavBarItem("Observaciones", AnuraIcons.Observations),
        AnuraNavBarItem("Ajustes", AnuraIcons.Settings),
    )
    AnuraNavBar(items = items, selectedIndex = 0, onItemSelected = {})
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
