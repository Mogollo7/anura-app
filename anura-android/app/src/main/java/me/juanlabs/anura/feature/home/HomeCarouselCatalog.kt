package me.juanlabs.anura.feature.home

import androidx.annotation.DrawableRes
import androidx.annotation.StringRes
import me.juanlabs.anura.R
import me.juanlabs.anura.core.data.ContentCatalog
import me.juanlabs.anura.core.data.PublishedSpecies
import me.juanlabs.anura.core.data.SpeciesCatalog
import java.time.LocalDate

/**
 * Categorías del carrusel de `home` (Penpot): el título del overlay rota entre
 * estos cuatro valores; la especie y el dato curioso vienen del catálogo.
 */
enum class HomeCarouselCategory(
    @param:StringRes val titleRes: Int,
    /** Categoría en Admin → Destacados (`dataset.destacado.categoria`). */
    val serverKey: String,
) {
    WhereToLook(R.string.home_carousel_where_to_look, "donde_buscarla"),
    FeaturedPhoto(R.string.home_carousel_featured_photo, "foto_destacada"),
    Endangered(R.string.home_carousel_endangered, "especie_amenazada"),
    FrogOfTheDay(R.string.home_carousel_frog_of_day, "rana_del_dia"),
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
    /** Foto publicada (Admin → Contenido); mientras baja se ve [imageRes]. */
    val photoSha256: String? = null,
)

data class HomeActiveFieldSession(
    val sessionId: String,
    val placeName: String,
    val elapsedLabel: String,
    val registerCount: Int,
)

/**
 * Carrusel de inicio. Sale del catálogo publicado ([ContentCatalog]): lo programado para
 * hoy en Admin → Destacados y, si una categoría no tiene nada programado, una especie
 * elegible elegida por la fecha. Sin catálogo descargado, el carrusel queda vacío.
 */
object HomeCarouselCatalog {
    fun items(today: LocalDate = LocalDate.now()): List<HomeCarouselItem> {
        val catalog = ContentCatalog.catalog ?: return emptyList()
        val published = catalog.especies.filter { p ->
            SpeciesCatalog.find(p.taxon_id) != null || SpeciesCatalog.find(p.nombre_cientifico) != null
        }
        if (published.isEmpty()) return emptyList()
        val date = today.toString()
        val order = listOf(
            HomeCarouselCategory.FrogOfTheDay,
            HomeCarouselCategory.WhereToLook,
            HomeCarouselCategory.FeaturedPhoto,
            HomeCarouselCategory.Endangered,
        )
        return order.mapNotNull { category ->
            val scheduled = catalog.destacados
                .firstOrNull { it.fecha == date && it.categoria == category.serverKey }
                ?.let { d -> published.firstOrNull { it.taxon_id == d.taxon_id } }
            val eligible = published.filter { isEligible(it, category) }
            val pick = scheduled ?: eligible.takeIf { it.isNotEmpty() }?.let { it[Math.floorMod(today.toEpochDay(), it.size.toLong()).toInt()] }
            pick?.let { toItem(it, category) }
        }.ifEmpty { emptyList() }
    }

    private fun isEligible(p: PublishedSpecies, category: HomeCarouselCategory): Boolean = when (category) {
        HomeCarouselCategory.FrogOfTheDay -> p.foto_principal != null && p.dato_curioso != null
        HomeCarouselCategory.WhereToLook -> !p.habitat.isNullOrBlank()
        HomeCarouselCategory.FeaturedPhoto -> !p.foto_principal?.atribucion.isNullOrBlank()
        HomeCarouselCategory.Endangered -> p.uicn?.categoria in setOf("VU", "EN", "CR")
    }

    private fun toItem(p: PublishedSpecies, category: HomeCarouselCategory): HomeCarouselItem? {
        val record = SpeciesCatalog.find(p.taxon_id) ?: SpeciesCatalog.find(p.nombre_cientifico) ?: return null
        val text = when (category) {
            HomeCarouselCategory.WhereToLook -> p.habitat.orEmpty()
            HomeCarouselCategory.FeaturedPhoto -> p.foto_principal?.atribucion?.let { "Foto: $it" }.orEmpty()
            HomeCarouselCategory.Endangered -> p.dato_curioso?.valor ?: record.iucn.fullLabel
            HomeCarouselCategory.FrogOfTheDay -> p.dato_curioso?.valor.orEmpty()
        }
        return HomeCarouselItem(
            id = "carousel-${category.serverKey}-${p.taxon_id}",
            category = category,
            speciesName = p.nombre_comun ?: p.nombre_cientifico,
            curiousFact = text,
            imageRes = record.photoRes,
            speciesId = record.id,
            photoSha256 = p.foto_principal?.sha256,
        )
    }

    fun previewActiveFieldSession(): HomeActiveFieldSession = HomeActiveFieldSession(
        sessionId = "session-001",
        placeName = "Quebrada La Miel",
        elapsedLabel = "1 h 12 min",
        registerCount = 7,
    )
}

/**
 * Estados de `home` (§4.1): contenido del catálogo descargado, o carga.
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
