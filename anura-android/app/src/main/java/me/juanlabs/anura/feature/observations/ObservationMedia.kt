package me.juanlabs.anura.feature.observations

import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import me.juanlabs.anura.core.data.ObservationRecord
import me.juanlabs.anura.core.data.SpeciesCatalog
import me.juanlabs.anura.core.data.rememberSpeciesPhotoPainter
import me.juanlabs.anura.core.platform.rememberPhotoPlaceholderPainter
import me.juanlabs.anura.core.platform.rememberRemotePhotoPainter
import me.juanlabs.anura.feature.capture.rememberCaptureBackdropPainter

internal sealed interface ObservationMediaItem {
    val id: String

    /** Foto publicada del catálogo de contenido (por sha256); sin foto o mientras baja, un hueco neutro. */
    data class Photo(
        override val id: String,
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
        listOf(ObservationMediaItem.RemotePhoto(id = "p-remote", url = it))
    }.orEmpty()
    val photoItems = photos.ifEmpty { remote }
    val audio = observation.audioPath?.let {
        listOf(
            ObservationMediaItem.Audio(
                id = "a1",
                durationMs = (observation.audioDurationMs ?: 0L).toInt().coerceAtLeast(0),
                uri = it,
            ),
        )
    }.orEmpty()
    // Sin foto ni audio propios: la foto publicada de la especie, o un hueco neutro si no la hay.
    return (photoItems + audio).ifEmpty {
        listOf(ObservationMediaItem.Photo("empty", SpeciesCatalog.find(observation.speciesId)?.photoSha256))
    }
}

@Composable
internal fun ObservationPhoto(
    observation: ObservationRecord,
    modifier: Modifier = Modifier,
) {
    val token = observation.photoTokens.firstOrNull()
    val speciesSha = SpeciesCatalog.find(observation.speciesId)?.photoSha256
    val painter = when {
        token != null -> rememberCaptureBackdropPainter(token) ?: rememberPhotoPlaceholderPainter()
        observation.photoUrl != null -> rememberRemotePhotoPainter(observation.photoUrl, rememberSpeciesPhotoPainter(speciesSha))
        else -> rememberSpeciesPhotoPainter(speciesSha)
    }
    Image(
        painter = painter,
        contentDescription = null,
        modifier = modifier.fillMaxSize(),
        contentScale = ContentScale.Crop,
    )
}
