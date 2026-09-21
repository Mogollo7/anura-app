package me.juanlabs.anura.designsystem.component

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.size
import androidx.compose.material3.CenterAlignedTopAppBar
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarScrollBehavior
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

/**
 * Barra superior de ANURA (presente en casi todas las pantallas de detalle, §3.9):
 * flecha volver + título. Envuelve `TopAppBar` / `CenterAlignedTopAppBar` de Material 3.
 *
 * [centerTitle]: centra el título en el ancho de pantalla (auth Iniciar sesión / Crear cuenta).
 * Debajo deja [AnuraDimens.spaceTopBarToContent] para separar el título del contenido.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AnuraTopBar(
    title: String,
    modifier: Modifier = Modifier,
    onBackClick: (() -> Unit)? = null,
    centerTitle: Boolean = false,
    actions: @Composable RowScope.() -> Unit = {},
    scrollBehavior: TopAppBarScrollBehavior? = null,
) {
    val titleContent: @Composable () -> Unit = {
        Text(
            text = title,
            style = MaterialTheme.typography.titleLarge.copy(
                fontWeight = if (centerTitle) FontWeight.Bold else FontWeight.Normal,
            ),
        )
    }
    val navigationIcon: @Composable () -> Unit = {
        if (onBackClick != null) {
            IconButton(
                onClick = onBackClick,
                modifier = Modifier.size(AnuraDimens.sizeTouch),
            ) {
                Icon(imageVector = AnuraIcons.Back, contentDescription = "Volver")
            }
        }
    }

    Column(modifier = modifier) {
        if (centerTitle) {
            CenterAlignedTopAppBar(
                title = titleContent,
                navigationIcon = navigationIcon,
                actions = actions,
                scrollBehavior = scrollBehavior,
            )
        } else {
            TopAppBar(
                title = titleContent,
                navigationIcon = navigationIcon,
                actions = actions,
                scrollBehavior = scrollBehavior,
            )
        }
        Spacer(modifier = Modifier.height(AnuraDimens.spaceTopBarToContent))
    }
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
