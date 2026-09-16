package me.juanlabs.anura.designsystem.component

import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.size
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarScrollBehavior
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

/**
 * Barra superior de ANURA (presente en casi todas las pantallas de detalle, §3.9):
 * flecha volver + título. Envuelve `TopAppBar` de Material 3, `scrollBehavior`
 * conectable por quien la use (§3.9).
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AnuraTopBar(
    title: String,
    modifier: Modifier = Modifier,
    onBackClick: (() -> Unit)? = null,
    actions: @Composable RowScope.() -> Unit = {},
    scrollBehavior: TopAppBarScrollBehavior? = null,
) {
    TopAppBar(
        title = {
            Text(text = title, style = MaterialTheme.typography.titleLarge)
        },
        modifier = modifier,
        navigationIcon = {
            if (onBackClick != null) {
                IconButton(
                    onClick = onBackClick,
                    modifier = Modifier.size(AnuraDimens.sizeTouch),
                ) {
                    Icon(imageVector = AnuraIcons.Back, contentDescription = "Volver")
                }
            }
        },
        actions = actions,
        scrollBehavior = scrollBehavior,
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun AnuraTopBarPreviewContent() {
    AnuraTopBar(title = "Detalles de observación", onBackClick = {})
}

@AnuraPreviews
@Composable
private fun AnuraTopBarPreview() {
    AnuraTheme { AnuraTopBarPreviewContent() }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun AnuraTopBarPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) { AnuraTopBarPreviewContent() }
}
