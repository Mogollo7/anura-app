package me.juanlabs.anura.designsystem.icon

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.List
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.FavoriteBorder
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Warning
import androidx.compose.ui.graphics.vector.ImageVector

/**
 * Punto único de acceso a la iconografía de ANURA (§3.8).
 *
 * TEMPORAL: el pipeline real de Penpot exporta cada icono como SVG vectorizado
 * (`export_shape`) para importarse como *Vector Asset* en `res/drawable/`. Esta sesión
 * no tiene acceso al archivo de Penpot (sin MCP disponible en este entorno), así que se
 * usan los iconos equivalentes de `material-icons-core` como marcador semántico 1:1
 * sustituible: cuando se importen los vectores reales, solo cambia el valor de estas
 * constantes — ningún composable que las consuma tiene que cambiar.
 *
 * `material-icons-core` solo incluye el subconjunto "clásico" de Material Icons (no
 * `Error` ni `Image`, por ejemplo). Se evita a propósito añadir
 * `material-icons-extended` (varios MB, miles de iconos no usados) solo para dos
 * glifos — [Error] reutiliza [Warning] y [Empty] usa [Search] mientras no exista el
 * vector real de Penpot.
 *
 * Ningún icono aquí lleva `contentDescription` propio: eso lo decide cada composable
 * que lo usa, según si el icono es semántico (obligatorio) o decorativo (`null`), tal
 * como exige §14.
 */
object AnuraIcons {
    val Back: ImageVector = Icons.AutoMirrored.Filled.ArrowBack
    val Close: ImageVector = Icons.Filled.Close
    val Favorite: ImageVector = Icons.Filled.Favorite
    val FavoriteBorder: ImageVector = Icons.Filled.FavoriteBorder
    val Warning: ImageVector = Icons.Filled.Warning
    val Error: ImageVector = Icons.Filled.Warning
    val Success: ImageVector = Icons.Filled.CheckCircle
    val Info: ImageVector = Icons.Filled.Info
    val Empty: ImageVector = Icons.Filled.Search

    // Navbar (§3.9 AnuraNavBar) + FAB central ("+").
    val Home: ImageVector = Icons.Filled.Home
    val Explore: ImageVector = Icons.Filled.Search
    val Observations: ImageVector = Icons.AutoMirrored.Filled.List
    val Settings: ImageVector = Icons.Filled.Settings
    val Add: ImageVector = Icons.Filled.Add
}
