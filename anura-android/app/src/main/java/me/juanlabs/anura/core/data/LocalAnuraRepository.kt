package me.juanlabs.anura.core.data

import androidx.compose.runtime.Composable
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.platform.LocalContext
import me.juanlabs.anura.AnuraApplication

val LocalAnuraRepository = staticCompositionLocalOf<AnuraRepository?> { null }

@Composable
fun rememberAnuraRepository(): AnuraRepository {
    LocalAnuraRepository.current?.let { return it }
    val context = LocalContext.current
    val app = context.applicationContext
    return if (app is AnuraApplication) {
        app.repository
    } else {
        AnuraRepository.preview()
    }
}
