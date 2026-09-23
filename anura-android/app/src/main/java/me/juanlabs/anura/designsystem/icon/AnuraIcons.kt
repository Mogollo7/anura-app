package me.juanlabs.anura.designsystem.icon

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.Chat
import androidx.compose.material.icons.automirrored.filled.Reply
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.automirrored.filled.Sort
import androidx.compose.material.icons.filled.CloudOff
import androidx.compose.material.icons.automirrored.filled.FormatListBulleted
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material.icons.automirrored.filled.MenuBook
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Animation
import androidx.compose.material.icons.filled.BrightnessAuto
import androidx.compose.material.icons.filled.CalendarToday
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.DarkMode
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Download
import androidx.compose.material.icons.filled.Email
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.FavoriteBorder
import androidx.compose.material.icons.filled.FilterList
import androidx.compose.material.icons.filled.FolderOpen
import androidx.compose.material.icons.filled.Forward10
import androidx.compose.material.icons.filled.Fullscreen
import androidx.compose.material.icons.filled.FullscreenExit
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.automirrored.filled.Notes
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.MonetizationOn
import androidx.compose.material.icons.filled.Pause
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.PhotoCamera
import androidx.compose.material.icons.filled.PhotoLibrary
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Replay10
import androidx.compose.material.icons.filled.Schedule
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Share
import androidx.compose.material.icons.filled.ThumbDown
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material.icons.filled.TextFields
import androidx.compose.material.icons.filled.Straighten
import androidx.compose.material.icons.filled.TravelExplore
import androidx.compose.material.icons.filled.Tune
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.VisibilityOff
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material.icons.filled.WbCloudy
import androidx.compose.material.icons.filled.WbSunny
import androidx.compose.material.icons.filled.WbTwilight
import androidx.compose.ui.graphics.vector.ImageVector

/**
 * Punto único de acceso a la iconografía de ANURA (§3.8).
 *
 * Iconos **Material (Android)**, no SVG exportados de Penpot. Auth y chrome usan
 * `material-icons-core` + `material-icons-extended` solo para glifos ausentes en core
 * (p. ej. Visibility).
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
    val Filter: ImageVector = Icons.Filled.FilterList
    val Sort: ImageVector = Icons.AutoMirrored.Filled.Sort

    // Navbar (§3.9 AnuraNavBar) + FAB central ("+") — glifos Material alineados a Penpot.
    val Home: ImageVector = Icons.Filled.Home
    val Explore: ImageVector = Icons.Filled.TravelExplore
    val Observations: ImageVector = Icons.AutoMirrored.Filled.FormatListBulleted
    val Settings: ImageVector = Icons.Filled.Tune
    val Add: ImageVector = Icons.Filled.Add

    // Auth — INICIAR SECCION / crear cuenta (Material, no Penpot).
    val Email: ImageVector = Icons.Filled.Email
    val Lock: ImageVector = Icons.Filled.Lock
    val Person: ImageVector = Icons.Filled.Person
    val Visibility: ImageVector = Icons.Filled.Visibility
    val VisibilityOff: ImageVector = Icons.Filled.VisibilityOff
    val Check: ImageVector = Icons.Filled.Check
    val Curiosity: ImageVector = Icons.Filled.TravelExplore
    val Study: ImageVector = Icons.AutoMirrored.Filled.MenuBook

    // home — Foto ID / Audio ID / Paso a paso + chip de salida.
    val PhotoId: ImageVector = Icons.Filled.PhotoCamera
    val PhotoLibrary: ImageVector = Icons.Filled.PhotoLibrary
    val AudioId: ImageVector = Icons.Filled.Mic
    val FieldSession: ImageVector = Icons.Filled.LocationOn
    val Notes: ImageVector = Icons.AutoMirrored.Filled.Notes
    val StepByStep: ImageVector = Icons.AutoMirrored.Filled.FormatListBulleted
    val ChevronRight: ImageVector = Icons.AutoMirrored.Filled.KeyboardArrowRight

    val Calendar: ImageVector = Icons.Filled.CalendarToday
    val Schedule: ImageVector = Icons.Filled.Schedule
    val Edit: ImageVector = Icons.Filled.Edit
    val Play: ImageVector = Icons.Filled.PlayArrow
    val Pause: ImageVector = Icons.Filled.Pause
    val FolderOpen: ImageVector = Icons.Filled.FolderOpen
    val Replay10: ImageVector = Icons.Filled.Replay10
    val Forward10: ImageVector = Icons.Filled.Forward10
    val Delete: ImageVector = Icons.Filled.Delete
    val Dawn: ImageVector = Icons.Filled.WbTwilight
    val Day: ImageVector = Icons.Filled.WbSunny
    val Dusk: ImageVector = Icons.Filled.WbCloudy
    val Night: ImageVector = Icons.Filled.DarkMode
    val ThemeSystem: ImageVector = Icons.Filled.BrightnessAuto
    val ReduceMotion: ImageVector = Icons.Filled.Animation
    val TextSize: ImageVector = Icons.Filled.TextFields
    val Straighten: ImageVector = Icons.Filled.Straighten
    val Coin: ImageVector = Icons.Filled.MonetizationOn
    val Stop: ImageVector = Icons.Filled.Stop
    val Chat: ImageVector = Icons.AutoMirrored.Filled.Chat
    val CloudOff: ImageVector = Icons.Filled.CloudOff
    val Download: ImageVector = Icons.Filled.Download
    val Share: ImageVector = Icons.Filled.Share
    val Send: ImageVector = Icons.AutoMirrored.Filled.Send
    val Reply: ImageVector = Icons.AutoMirrored.Filled.Reply
    val More: ImageVector = Icons.Filled.MoreVert
    val Refute: ImageVector = Icons.Filled.ThumbDown
    val Expand: ImageVector = Icons.Filled.Fullscreen
    val Collapse: ImageVector = Icons.Filled.FullscreenExit
}
