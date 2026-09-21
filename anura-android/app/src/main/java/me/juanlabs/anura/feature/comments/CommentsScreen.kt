package me.juanlabs.anura.feature.comments

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import me.juanlabs.anura.core.data.rememberAnuraRepository
import me.juanlabs.anura.feature.observations.ObservationMediaCarousel
import me.juanlabs.anura.feature.observations.mediaForObservation

/** Hoja `COMENTARIOS`. El flujo principal abre el sheet desde detalles de observación. */
@Composable
fun CommentsScreen(
    observationId: String,
    onBackClick: () -> Unit,
) {
    val repository = rememberAnuraRepository()
    val observation = repository.observationById(observationId)
    ObservationCommentsOverlay(
        observationId = observationId,
        onDismiss = onBackClick,
    ) {
        ObservationMediaCarousel(
            items = observation?.let { mediaForObservation(it) } ?: emptyList(),
            modifier = Modifier.fillMaxSize(),
        )
    }
}
