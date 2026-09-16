package me.juanlabs.anura.navigation

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import me.juanlabs.anura.designsystem.component.AnuraButton
import me.juanlabs.anura.designsystem.component.AnuraButtonStyle
import me.juanlabs.anura.designsystem.component.AnuraTopBar
import me.juanlabs.anura.designsystem.theme.AnuraDimens

/**
 * Shell temporal para pantallas de esta fase de navegación. Muestra el título real de
 * la pantalla (§4.1), una nota de que el contenido es de relleno, y botones para
 * ejercitar cada transición de navegación real definida por la arquitectura, con
 * argumentos de muestra.
 *
 * Se reemplaza pantalla por pantalla en los bloques de producto (B6+) — este archivo
 * entero deja de usarse cuando la última pantalla tenga su UI real; no es parte del
 * Design System ni del dominio.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MockScreenScaffold(
    title: String,
    modifier: Modifier = Modifier,
    onBackClick: (() -> Unit)? = null,
    description: String = "Contenido temporal — la pantalla real llega en un bloque de producto posterior.",
    actions: List<MockNavAction> = emptyList(),
) {
    Scaffold(
        modifier = modifier.fillMaxSize(),
        topBar = { AnuraTopBar(title = title, onBackClick = onBackClick) },
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(AnuraDimens.spaceGutter),
            verticalArrangement = Arrangement.spacedBy(AnuraDimens.spaceGap),
        ) {
            Text(
                text = description,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            actions.forEach { action ->
                AnuraButton(
                    text = action.label,
                    onClick = action.onClick,
                    style = AnuraButtonStyle.Outline,
                    modifier = Modifier.fillMaxWidth(),
                )
            }
        }
    }
}

/** Una transición de navegación real que el mock de una pantalla puede disparar. */
data class MockNavAction(
    val label: String,
    val onClick: () -> Unit,
)
