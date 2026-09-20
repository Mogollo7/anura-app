package me.juanlabs.anura.feature.comments

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import me.juanlabs.anura.feature.observations.ObservationMediaCarousel
import me.juanlabs.anura.feature.observations.mockObservationMedia

/** Hoja `COMENTARIOS`. El flujo principal abre el sheet desde detalles de observación. */
@Composable
fun CommentsScreen(
    observationId: String,
    onBackClick: () -> Unit,
) {
    ObservationCommentsOverlay(
        observationId = observationId,
        onDismiss = onBackClick,
    ) {
        ObservationMediaCarousel(
            items = mockObservationMedia(observationId),
            modifier = Modifier.fillMaxSize(),
        )
    }
}
