package me.juanlabs.anura.feature.home

import androidx.annotation.DrawableRes
import androidx.annotation.StringRes
import me.juanlabs.anura.R

/**
 * Categorías del carrusel de `home` (Penpot): el título del overlay rota entre
 * estos cuatro valores; la especie y el dato curioso vienen del catálogo.
 */
enum class HomeCarouselCategory(
    @param:StringRes val titleRes: Int,
) {
    WhereToLook(R.string.home_carousel_where_to_look),
    FeaturedPhoto(R.string.home_carousel_featured_photo),
    Endangered(R.string.home_carousel_endangered),
    FrogOfTheDay(R.string.home_carousel_frog_of_day),
}

/**
 * Ítem del carrusel de inicio. `imageRes` apunta a un drawable local; para
 * ampliar el carrusel basta con añadir un recurso en `res/drawable` y una
 * entrada aquí (o en la fuente que alimente [HomeCarouselCatalog.items]).
 */
data class HomeCarouselItem(
    val id: String,
    val category: HomeCarouselCategory,
    val speciesName: String,
    val curiousFact: String,
    @param:DrawableRes val imageRes: Int,
    /** Id de catálogo para [me.juanlabs.anura.navigation.AnuraRoute.SpeciesSheet]. */
    val speciesId: String,
)

data class HomeActiveFieldSession(
    val sessionId: String,
    val placeName: String,
    val elapsedLabel: String,
    val registerCount: Int,
)

/**
 * Catálogo mock del carrusel. Fuente única y modular: sustituible por red/Room
 * sin tocar el layout de [HomeScreen].
 */
object HomeCarouselCatalog {
    fun items(): List<HomeCarouselItem> = listOf(
        HomeCarouselItem(
            id = "carousel-pristimantis-paisa",
            category = HomeCarouselCategory.WhereToLook,
            speciesName = "Pristimantis paisa",
            curiousFact = "Nace desarrollada del huevo, sin fase de renacuajo.",
            imageRes = R.drawable.carousel_pristimantis_paisa,
            speciesId = "COL_ANURA_0011",
        ),
        HomeCarouselItem(
            id = "carousel-sachatamia-electrops",
            category = HomeCarouselCategory.FeaturedPhoto,
            speciesName = "Sachatamia electrops",
            curiousFact = "Su piel transparente permite ver sus órganos internos.",
            imageRes = R.drawable.carousel_sachatamia_electrops,
            speciesId = "ANU_COL_SACH_ELE_001",
        ),
        HomeCarouselItem(
            id = "carousel-dendrobates-truncatus",
            category = HomeCarouselCategory.Endangered,
            speciesName = "Dendrobates truncatus",
            curiousFact = "Acumula su veneno comiendo hormigas y ácaros.",
            imageRes = R.drawable.carousel_dendrobates_truncatus,
            speciesId = "COL_ANURA_0018",
        ),
        HomeCarouselItem(
            id = "carousel-dendropsophus-bogerti",
            category = HomeCarouselCategory.FrogOfTheDay,
            speciesName = "Dendropsophus bogerti",
            curiousFact = "Canta en alta frecuencia junto a ríos de montaña.",
            imageRes = R.drawable.carousel_dendropsophus_bogerti,
            speciesId = "COL_ANURA_0028",
        ),
    )

    fun mockActiveFieldSession(): HomeActiveFieldSession = HomeActiveFieldSession(
        sessionId = "session-001",
        placeName = "Quebrada La Miel",
        elapsedLabel = "1 h 12 min",
        registerCount = 7,
    )
}

/**
 * Estados de `home` (§4.1): contenido local (carrusel mock) o carga.
 * La salida de campo activa es opcional dentro de [Content].
 */
sealed interface HomeUiState {
    data object Loading : HomeUiState

    data class Content(
        val userDisplayName: String,
        val carouselItems: List<HomeCarouselItem>,
        val activeFieldSession: HomeActiveFieldSession?,
    ) : HomeUiState
}
