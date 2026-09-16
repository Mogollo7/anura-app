package me.juanlabs.anura.designsystem.icon

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.List
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.CloudOff
import androidx.compose.material.icons.filled.Email
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.FavoriteBorder
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.MenuBook
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.TravelExplore
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.VisibilityOff
import androidx.compose.material.icons.filled.Warning
import androidx.compose.ui.graphics.vector.ImageVector

/**
 * Punto único de acceso a la iconografía de ANURA (§3.8).
 *
 * Iconos **Material (Android)**, no SVG exportados de Penpot. Auth y chrome usan
 * `material-icons-core` + `material-icons-extended` solo para glifos ausentes en core
 * (p. ej. Visibility, CloudOff).
 *
 * Ningún icono aquí lleva `contentDescription` propio: eso lo decide cada composable
 * que lo usa (§14).
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

    // Auth — INICIAR SECCION / crear cuenta (Material, no Penpot).
    val Email: ImageVector = Icons.Filled.Email
    val Lock: ImageVector = Icons.Filled.Lock
    val Person: ImageVector = Icons.Filled.Person
    val Visibility: ImageVector = Icons.Filled.Visibility
    val VisibilityOff: ImageVector = Icons.Filled.VisibilityOff
    val CloudOff: ImageVector = Icons.Filled.CloudOff
    val Check: ImageVector = Icons.Filled.Check
    val Curiosity: ImageVector = Icons.Filled.TravelExplore
    val Study: ImageVector = Icons.Filled.MenuBook
}
