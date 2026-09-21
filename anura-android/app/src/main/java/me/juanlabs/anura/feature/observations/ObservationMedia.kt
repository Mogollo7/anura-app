package me.juanlabs.anura.feature.observations

import androidx.annotation.DrawableRes
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import me.juanlabs.anura.R
import me.juanlabs.anura.core.data.ObservationRecord
import me.juanlabs.anura.core.data.SpeciesCatalog
import me.juanlabs.anura.feature.capture.rememberCaptureBackdropPainter

internal sealed interface ObservationMediaItem {
    val id: String

    data class Photo(
        override val id: String,
        @param:DrawableRes val imageRes: Int,
    ) : ObservationMediaItem

    data class FilePhoto(
        override val id: String,
        val token: String,
    ) : ObservationMediaItem

    data class Audio(
        override val id: String,
        val durationMs: Int = 14_000,
        val uri: String? = null,
    ) : ObservationMediaItem
}

internal fun mediaForObservation(observation: ObservationRecord): List<ObservationMediaItem> {
    val photos = observation.photoTokens.mapIndexed { index, token ->
        ObservationMediaItem.FilePhoto("p$index", token)
    }
    val fallback = observation.photoRes?.let {
        listOf(ObservationMediaItem.Photo("p-res", it))
    }.orEmpty()
    val photoItems = photos.ifEmpty { fallback }
    val audio = observation.audioPath?.let {
        listOf(
            ObservationMediaItem.Audio(
                id = "a1",
                durationMs = (observation.audioDurationMs ?: 0L).toInt().coerceAtLeast(0),
                uri = it,
            ),
        )
    }.orEmpty()
    return (photoItems + audio).ifEmpty {
        val speciesPhoto = SpeciesCatalog.find(observation.speciesId)?.photoRes
            ?: R.drawable.carousel_dendrobates_truncatus
        listOf(ObservationMediaItem.Photo("empty", speciesPhoto))
    }
}

@Composable
internal fun ObservationPhoto(
    observation: ObservationRecord,
    modifier: Modifier = Modifier,
) {
    val token = observation.photoTokens.firstOrNull()
    val painter = token?.let { rememberCaptureBackdropPainter(it) }
        ?: painterResource(
            observation.photoRes
                ?: SpeciesCatalog.find(observation.speciesId)?.photoRes
                ?: R.drawable.carousel_dendrobates_truncatus,
        )
    Image(
        painter = painter,
        contentDescription = null,
        modifier = modifier.fillMaxSize(),
        contentScale = ContentScale.Crop,
    )
}

internal fun mockObservationMedia(observationId: String): List<ObservationMediaItem> {
    val photos = listOf(
        ObservationMediaItem.Photo("p1", R.drawable.carousel_dendrobates_truncatus),
        ObservationMediaItem.Photo("p2", R.drawable.carousel_pristimantis_paisa),
        ObservationMediaItem.Photo("p3", R.drawable.carousel_dendropsophus_bogerti),
    )
    val audio = ObservationMediaItem.Audio("a1")
    return when {
        observationId.endsWith("002") || observationId.contains("audio-only") -> listOf(audio)
        observationId.contains("photo-only") -> photos.take(2)
        observationId.endsWith("001") -> photos.take(2) + audio
        else -> photos + audio
    }
}
