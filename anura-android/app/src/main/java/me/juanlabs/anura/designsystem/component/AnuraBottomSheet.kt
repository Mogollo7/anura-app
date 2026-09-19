package me.juanlabs.anura.designsystem.component

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Surface
import androidx.compose.material3.SheetState
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import me.juanlabs.anura.designsystem.preview.AnuraPreviews
import me.juanlabs.anura.designsystem.theme.AnuraDimens
import me.juanlabs.anura.designsystem.theme.AnuraTheme
import me.juanlabs.anura.designsystem.theme.AnuraThemeMode

/**
 * Shell de bottom sheet de ANURA (`COMP · Pop-up (shell)`, §3.9): ancho a sangre, radio
 * superior 20dp ([AnuraDimens.radiusModal]), tirador 48×5dp. Expande de una vez
 * (`skipPartiallyExpanded`) para que título, cuerpo y acciones queden visibles sin
 * scroll interno.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AnuraBottomSheet(
    onDismissRequest: () -> Unit,
    modifier: Modifier = Modifier,
    sheetState: SheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true),
    containerColor: Color = MaterialTheme.colorScheme.surface,
    content: @Composable ColumnScope.() -> Unit,
) {
    ModalBottomSheet(
        onDismissRequest = onDismissRequest,
        modifier = modifier,
        sheetState = sheetState,
        containerColor = containerColor,
        shape = RoundedCornerShape(
            topStart = AnuraDimens.radiusModal,
            topEnd = AnuraDimens.radiusModal,
        ),
        dragHandle = { AnuraSheetHandle() },
        content = content,
    )
}

@Composable
fun AnuraSheetHandle() {
    Box(
        modifier = Modifier
            .padding(vertical = 12.dp)
            .size(width = 48.dp, height = 5.dp)
            .background(
                color = MaterialTheme.colorScheme.outlineVariant,
                shape = RoundedCornerShape(AnuraDimens.radiusCapsule),
            )
            // Puramente decorativo: no aporta información propia a TalkBack.
            .clearAndSetSemantics {},
    )
}

/**
 * `ModalBottomSheet` usa un `Popup`/diálogo de ventana que no se renderiza en un
 * `@Preview` estático — por eso el preview reconstruye solo la apariencia visual del
 * shell (forma + tirador) sin abrir el diálogo real.
 */
@Composable
private fun AnuraBottomSheetPreviewContent() {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        color = MaterialTheme.colorScheme.surface,
        shape = RoundedCornerShape(topStart = AnuraDimens.radiusModal, topEnd = AnuraDimens.radiusModal),
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            AnuraSheetHandle()
            Text(
                text = "Contenido del pop-up",
                modifier = Modifier.padding(bottom = AnuraDimens.spaceSection),
            )
        }
    }
}

@AnuraPreviews
@Composable
private fun AnuraBottomSheetPreview() {
    AnuraTheme { AnuraBottomSheetPreviewContent() }
}

@Preview(name = "Luz roja", group = "modo", showBackground = true)
@Composable
private fun AnuraBottomSheetPreviewRedLight() {
    AnuraTheme(AnuraThemeMode.LuzRoja) { AnuraBottomSheetPreviewContent() }
}
