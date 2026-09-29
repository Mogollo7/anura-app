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
import me.juanlabs.anura.core.platform.rememberRemotePhotoPainter
import me.juanlabs.anura.feature.capture.rememberCaptureBackdropPainter

internal sealed interface ObservationMediaItem {
    val id: String

    data class Photo(
        override val id: String,
        @param:DrawableRes val imageRes: Int,
        /** Foto publicada del catálogo de contenido; mientras baja (o sin red) se ve [imageRes]. */
        val remoteSha256: String? = null,
    ) : ObservationMediaItem

    data class FilePhoto(
        override val id: String,
        val token: String,
    ) : ObservationMediaItem

    /** Foto real de una observación ajena, pedida al servidor (miniatura de explorer-service),
     * no una publicada del catálogo de contenido ni un archivo local del teléfono. */
    data class RemotePhoto(
        override val id: String,
        val url: String,
        @param:DrawableRes val fallbackRes: Int,
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
    val remote = observation.photoUrl?.let {
        listOf(
            ObservationMediaItem.RemotePhoto(
                id = "p-remote",
                url = it,
                fallbackRes = observation.photoRes
                    ?: SpeciesCatalog.find(observation.speciesId)?.photoRes
                    ?: R.drawable.carousel_dendrobates_truncatus,
            ),
        )
    }.orEmpty()
    val fallback = observation.photoRes?.let {
        listOf(ObservationMediaItem.Photo("p-res", it))
    }.orEmpty()
    val photoItems = photos.ifEmpty { remote.ifEmpty { fallback } }
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
    val fallbackRes = observation.photoRes
        ?: SpeciesCatalog.find(observation.speciesId)?.photoRes
        ?: R.drawable.carousel_dendrobates_truncatus
    val painter = when {
        token != null -> rememberCaptureBackdropPainter(token) ?: painterResource(fallbackRes)
        observation.photoUrl != null -> rememberRemotePhotoPainter(observation.photoUrl, fallbackRes)
        else -> painterResource(fallbackRes)
    }
    Image(
        painter = painter,
        contentDescription = null,
        modifier = modifier.fillMaxSize(),
        contentScale = ContentScale.Crop,
    )
}
