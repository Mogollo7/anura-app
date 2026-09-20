package me.juanlabs.anura.feature.observations

import androidx.annotation.DrawableRes
import me.juanlabs.anura.R

internal sealed interface ObservationMediaItem {
    val id: String

    data class Photo(
        override val id: String,
        @param:DrawableRes val imageRes: Int,
    ) : ObservationMediaItem

    data class Audio(
        override val id: String,
        val durationMs: Int = 14_000,
    ) : ObservationMediaItem
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
