package me.juanlabs.anura.designsystem.component

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.designsystem.icon.AnuraIcons
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

/**
 * Estados comunes de pantalla (`Estado · Cargando/Error/Vacío`, §3.9), reutilizados por
 * todos los listados y, por decisión 13 del documento de arquitectura, por "sin
 * paquete regional instalado" (mismo `AnuraEmptyState`, copy propio, sin diseño nuevo).
 *
 * Ninguno de los tres conoce `UiState`/`ErrorKind` de dominio: reciben textos y
 * callbacks ya resueltos por quien los usa (regla de frontera §2 — `designsystem` no
 * conoce `domain`). El estado "Éxito" (4º board de Penpot) no tiene composable propio:
 * significa "mostrar el contenido real", no un placeholder.
 */
@Composable
fun AnuraLoadingState(
    label: String,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(AnuraDimens.spaceSection),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
    ) {
        // AnuraLoader ya anuncia `label` como región en vivo; el Text visual es un eco
        // decorativo para evitar que TalkBack lo lea dos veces.
        AnuraLoader(label = label)
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center,
            modifier = Modifier.clearAndSetSemantics {},
        )
    }
}

@Composable
fun AnuraEmptyState(
    title: String,
    modifier: Modifier = Modifier,
    description: String? = null,
    actionLabel: String? = null,
    onAction: (() -> Unit)? = null,
) {
    AnuraStateScaffold(
        icon = AnuraIcons.Empty,
        iconTint = MaterialTheme.colorScheme.onSurfaceVariant,
        title = title,
        description = description,
        actionLabel = actionLabel,
        onAction = onAction,
        modifier = modifier,
    )
}

@Composable
fun AnuraErrorState(
    title: String,
    modifier: Modifier = Modifier,
    description: String? = null,
    actionLabel: String? = "Reintentar",
    onAction: (() -> Unit)? = null,
) {
    AnuraStateScaffold(
        icon = AnuraIcons.Error,
        iconTint = MaterialTheme.colorScheme.error,
        title = title,
        description = description,
        actionLabel = actionLabel,
        onAction = onAction,
        modifier = modifier,
    )
}

@Composable
private fun AnuraStateScaffold(
    icon: ImageVector,
    iconTint: Color,
    title: String,
    description: String?,
    actionLabel: String?,
    onAction: (() -> Unit)?,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(AnuraDimens.spaceSection),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = iconTint,
            modifier = Modifier.size(48.dp),
        )
        Text(
            text = title,
            style = MaterialTheme.typography.titleMedium,
            textAlign = TextAlign.Center,
        )
        if (description != null) {
            Text(
                text = description,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
            )
        }
        if (actionLabel != null && onAction != null) {
            AnuraFormButton(
                text = actionLabel,
                onClick = onAction,
                style = AnuraFormButtonStyle.Outline,
            )
        }
    }
}

@Composable
private fun StateViewsPreviewContent() {
    Column(verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceSection)) {
        AnuraLoadingState(label = "Buscando observaciones…")
        AnuraEmptyState(
            title = "Todavía no hay observaciones",
            description = "Registra tu primera observación desde el botón +.",
        )
        AnuraErrorState(
            title = "No se pudo cargar",
            description = "Revisa tu conexión e inténtalo otra vez.",
            onAction = {},
        )
    }
}

@AnuraPreviews
@Composable
private fun StateViewsPreview() {
    AnuraTheme { StateViewsPreviewContent() }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun StateViewsPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) { StateViewsPreviewContent() }
}