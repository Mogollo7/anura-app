package me.juanlabs.anura.core.data

import androidx.annotation.DrawableRes
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraConservationChipVariant
import me.juanlabs.anura.designsystem.component.AnuraToxicityChipVariant

/**
 * Catálogo de producto (no es dato de usuario). Fuente única por `speciesId`
 * para fichas, carrusel y explorar. No inventa resultados: las candidatas de una identificación
 * salen del motor y del paquete instalado, nunca de aquí.
 *
 * Las 30 especies con id `COL_ANURA_XXXX` son las reales del paquete visual de Antioquia
 * (mismo taxon_id que `package.sqlite`/`taxonomy_guide.json` — no un id de demo inventado).
 * IUCN, altitud y SVL salen de la ficha de campo del paquete (especie). En fichas de
 * género/familia/orden, altitud y tamaño se mezclan como unión de rangos de las
 * especies miembro. `catalogObservationCount` es el número real
 * de fotos de entrenamiento disponibles en `data cleaned/<especie>/` (no un contador de
 * comunidad, que no existe en este prototipo). `similarIds` = hasta 2 especies del mismo
 * género (o familia si el género solo tiene una especie en el catálogo).
 */
data class SpeciesRecord(
    val id: String,
    val commonName: String,
    val scientificName: String,
    val genus: String,
    val family: String,
    val order: String = "Anura",
    val iucn: AnuraConservationChipVariant,
    val toxicity: AnuraToxicityChipVariant,
    val altitudeRange: String,
    val sizeRange: String,
    val catalogObservationCount: String,
    val catalogObserverCount: String,
    val curiousFact: String,
    @param:DrawableRes val photoRes: Int,
    val similarIds: List<String> = emptyList(),
    /** Foto principal publicada en Admin → Contenido (licencia CC); si es null, se usa [photoRes]. */
    val photoSha256: String? = null,
    val photoCredit: String? = null,
    /** Morfología revisada; null = no hay (la pestaña lo dice, no muestra texto de ejemplo). */
    val morphology: PublishedMorphology? = null,
    val habitat: String? = null,
    /** true si la ficha viene del catálogo publicado (revisado por un herpetólogo). */
    val isPublished: Boolean = false,
    /** false cuando la ficha publicada no trae toxicidad: no se muestra «inofensiva» por defecto. */
    val toxicityDeclared: Boolean = true,
)

object SpeciesCatalog {
    /**
     * La lista es el catálogo descargado ([ContentCatalog]), también sin red.
     * Una especie nueva publicada entra aunque no estuviera en el APK.
     * Antes de la primera descarga la lista está vacía: no se muestran las fotos
     * empaquetadas como si ya fueran fichas.
     */
    val all: List<SpeciesRecord>
        get() {
            val published = ContentCatalog.catalog?.especies ?: return emptyList()
            val overlaid = published.map { withPublished(publishedStub(it)) }
            return overlaid.map { it.copy(similarIds = similarsAmong(it, overlaid)) }
        }

    private fun publishedStub(published: PublishedSpecies): SpeciesRecord {
        val known = local.firstOrNull {
            it.id == published.taxon_id || it.scientificName.equals(published.nombre_cientifico, ignoreCase = true)
        }
        if (known != null) return known
        return SpeciesRecord(
            id = published.taxon_id,
            commonName = published.nombre_comun ?: published.nombre_cientifico,
            scientificName = published.nombre_cientifico,
            genus = published.genero.orEmpty(),
            family = published.familia.orEmpty(),
            iucn = AnuraConservationChipVariant.NE,
            toxicity = AnuraToxicityChipVariant.Harmless,
            toxicityDeclared = false,
            altitudeRange = "",
            sizeRange = "",
            catalogObservationCount = "",
            catalogObserverCount = "",
            curiousFact = "",
            photoRes = R.drawable.splash_empty,
        )
    }

    /** Especies cuya ficha (local o publicada) incluye este largo hocico–cloaca. Sin rango, no cuentan. */
    fun countForSvl(svlMm: Int): Int = all.count { record ->
        val range = TaxonTraitRanges.parse(record.sizeRange) ?: return@count false
        svlMm >= range.min && (svlMm <= range.max || range.maxOpen)
    }

    private val local: List<SpeciesRecord> = listOf(
        SpeciesRecord(
            id = "COL_ANURA_0001",
            commonName = "Palm Rocket Frog",
            scientificName = "Rheobates palmatus",
            genus = "Rheobates",
            family = "Aromobatidae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "1.500–2.500 m",
            sizeRange = "45–60 mm",
            catalogObservationCount = "70",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_rheobates_palmatus,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0002",
            commonName = "Sapo del Obispo",
            scientificName = "Rhinella alata",
            genus = "Rhinella",
            family = "Bufonidae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "0–1.500 m",
            sizeRange = "35–55 mm",
            catalogObservationCount = "90",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_rhinella_alata,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0003",
            commonName = "Sapo gigante",
            scientificName = "Rhinella horribilis",
            genus = "Rhinella",
            family = "Bufonidae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "0–1.600 m",
            sizeRange = "90–150+ mm",
            catalogObservationCount = "94",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_rhinella_horribilis,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0004",
            commonName = "Sapo Crestado",
            scientificName = "Rhinella margaritifera",
            genus = "Rhinella",
            family = "Bufonidae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "0–1.200 m",
            sizeRange = "45–75 mm",
            catalogObservationCount = "159",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_rhinella_margaritifera,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0006",
            commonName = "Rana chivita",
            scientificName = "Craugastor raniformis",
            genus = "Craugastor",
            family = "Craugastoridae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "0–1.500 m",
            sizeRange = "40–70 mm",
            catalogObservationCount = "298",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_craugastor_raniformis,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0007",
            commonName = "Cutín común de occidente",
            scientificName = "Pristimantis achatinus",
            genus = "Pristimantis",
            family = "Craugastoridae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "0–2.200 m",
            sizeRange = "25–45 mm",
            catalogObservationCount = "1902",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_pristimantis_achatinus,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0009",
            commonName = "Rana De Ingle Roja",
            scientificName = "Pristimantis erythropleura",
            genus = "Pristimantis",
            family = "Craugastoridae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "1.000–2.600 m",
            sizeRange = "20–35 mm",
            catalogObservationCount = "136",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_pristimantis_erythropleura,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0010",
            commonName = "Gaige's Rain Frog",
            scientificName = "Pristimantis gaigei",
            genus = "Pristimantis",
            family = "Craugastoridae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "0–1.200 m",
            sizeRange = "30–45 mm",
            catalogObservationCount = "89",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_pristimantis_gaigei,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0011",
            commonName = "Cutín paisa",
            scientificName = "Pristimantis paisa",
            genus = "Pristimantis",
            family = "Craugastoridae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "1.800–3.000 m",
            sizeRange = "25–35 mm",
            catalogObservationCount = "170",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_pristimantis_paisa,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0012",
            commonName = "Palmer's Robber Frog",
            scientificName = "Pristimantis palmeri",
            genus = "Pristimantis",
            family = "Craugastoridae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "1.000–2.600 m",
            sizeRange = "20–30 mm",
            catalogObservationCount = "100",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_pristimantis_palmeri,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0013",
            commonName = "Rana De Ingles Negras Y Amarillas",
            scientificName = "Pristimantis penelopus",
            genus = "Pristimantis",
            family = "Craugastoridae",
            iucn = AnuraConservationChipVariant.VU,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "1.000–2.200 m",
            sizeRange = "25–35 mm",
            catalogObservationCount = "156",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_pristimantis_penelopus,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0014",
            commonName = "Rana De Muslos Naranja",
            scientificName = "Pristimantis permixtus",
            genus = "Pristimantis",
            family = "Craugastoridae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "1.800–3.200 m",
            sizeRange = "25–35 mm",
            catalogObservationCount = "111",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_pristimantis_permixtus,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0015",
            commonName = "Banded Rain Frog",
            scientificName = "Pristimantis taeniatus",
            genus = "Pristimantis",
            family = "Craugastoridae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "0–1.500 m",
            sizeRange = "25–35 mm",
            catalogObservationCount = "160",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_pristimantis_taeniatus,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0016",
            commonName = "Rana De Espolon",
            scientificName = "Pristimantis thectopternus",
            genus = "Pristimantis",
            family = "Craugastoridae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "1.500–2.800 m",
            sizeRange = "25–40 mm",
            catalogObservationCount = "80",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_pristimantis_thectopternus,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0018",
            commonName = "Rana venenosa de rayas amarillas",
            scientificName = "Dendrobates truncatus",
            genus = "Dendrobates",
            family = "Dendrobatidae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Toxic,
            altitudeRange = "0–1.200 m",
            sizeRange = "20–25 mm",
            catalogObservationCount = "1809",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_dendrobates_truncatus,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0020",
            commonName = "Rana gladiadora",
            scientificName = "Boana boans",
            genus = "Boana",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "0–1.000 m",
            sizeRange = "90–128 mm",
            catalogObservationCount = "145",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_boana_boans,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0023",
            commonName = "Rana Platanera de Ojos Pálidos",
            scientificName = "Boana platanera",
            genus = "Boana",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.NE,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "0–2.450 m",
            sizeRange = "42–64 mm",
            catalogObservationCount = "150",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_boana_platanera,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0024",
            commonName = "Rana Platanera de ojos tornasol",
            scientificName = "Boana pugnax",
            genus = "Boana",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "0–605 m",
            sizeRange = "50–80 mm",
            catalogObservationCount = "148",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_boana_pugnax,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0026",
            commonName = "rana arbórea de gladiadora",
            scientificName = "Boana rosenbergi",
            genus = "Boana",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "0–1.000 m",
            sizeRange = "70–100 mm",
            catalogObservationCount = "148",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_boana_rosenbergi,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0027",
            commonName = "Rana platanera del escudo guayanés",
            scientificName = "Boana xerophylla",
            genus = "Boana",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "0–2.450 m",
            sizeRange = "42–64 mm",
            catalogObservationCount = "100",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_boana_xerophylla,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0028",
            commonName = "Ranita de pantano",
            scientificName = "Dendropsophus bogerti",
            genus = "Dendropsophus",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "2.400–3.000 m",
            sizeRange = "30–35 mm",
            catalogObservationCount = "948",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_dendropsophus_bogerti,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0029",
            commonName = "Ranita de pantano Colombiana",
            scientificName = "Dendropsophus columbianus",
            genus = "Dendropsophus",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "1.200–2.200 m",
            sizeRange = "25–33 mm",
            catalogObservationCount = "146",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_dendropsophus_columbianus,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0030",
            commonName = "Rana arbórea amarillenta",
            scientificName = "Dendropsophus ebraccatus",
            genus = "Dendropsophus",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "0–1.500 m",
            sizeRange = "23–35 mm",
            catalogObservationCount = "148",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_dendropsophus_ebraccatus,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0032",
            commonName = "Rana de árbol amarilla",
            scientificName = "Dendropsophus microcephalus",
            genus = "Dendropsophus",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "0–1.200 m",
            sizeRange = "20–30 mm",
            catalogObservationCount = "713",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_dendropsophus_microcephalus,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0034",
            commonName = "El Roble Tree Frog",
            scientificName = "Dendropsophus norandinus",
            genus = "Dendropsophus",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "1.400–2.000 m",
            sizeRange = "25–33 mm",
            catalogObservationCount = "26",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_dendropsophus_norandinus,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0037",
            commonName = "Rana de torrente de Palmer",
            scientificName = "Hyloscirtus palmeri",
            genus = "Hyloscirtus",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "100–1.600 m",
            sizeRange = "40–50 mm",
            catalogObservationCount = "178",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_hyloscirtus_palmeri,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0038",
            commonName = "Ranita Listada",
            scientificName = "Scinax ruber",
            genus = "Scinax",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "0–1.500 m",
            sizeRange = "30–45 mm",
            catalogObservationCount = "125",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_scinax_ruber,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0039",
            commonName = "Ranita túngara",
            scientificName = "Engystomops pustulosus",
            genus = "Engystomops",
            family = "Leptodactylidae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "0–1.000 m",
            sizeRange = "25–35 mm",
            catalogObservationCount = "1718",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_engystomops_pustulosus,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0040",
            commonName = "Colombian Thin-toed Frog",
            scientificName = "Leptodactylus colombiensis",
            genus = "Leptodactylus",
            family = "Leptodactylidae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "200–2.000 m",
            sizeRange = "35–50 mm",
            catalogObservationCount = "206",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_leptodactylus_colombiensis,
        ),
        SpeciesRecord(
            id = "COL_ANURA_0042",
            commonName = "Lovely Leaf Frog",
            scientificName = "Phyllomedusa venusta",
            genus = "Phyllomedusa",
            family = "Phyllomedusidae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "0–1.200 m",
            sizeRange = "70–100 mm",
            catalogObservationCount = "150",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_phyllomedusa_venusta,
        ),
        // No forma parte del catálogo visual de Antioquia (fuera de la muestra de 30 real) —
        // se conserva con su id anterior por compatibilidad: CommunityCatalog/HomeCarouselCatalog
        // ya la referencian como especie de demo y no vale la pena romper esos datos de prueba.
        SpeciesRecord(
            id = "ANU_COL_SACH_ELE_001",
            commonName = "Rana de cristal",
            scientificName = "Sachatamia electrops",
            genus = "Sachatamia",
            family = "Centrolenidae",
            iucn = AnuraConservationChipVariant.VU,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "400–1.800 m",
            sizeRange = "22–32 mm",
            catalogObservationCount = "198",
            catalogObserverCount = "9",
            curiousFact = "Su piel transparente permite ver sus órganos internos.",
            photoRes = R.drawable.carousel_sachatamia_electrops,
        ),
    )

    /**
     * Ficha publicada encima del registro local. Regla de la ficha pública: si hay ficha
     * publicada, se muestra SOLO lo publicado — lo escrito a mano aquí no tiene fuente y no se
     * mezcla (un campo sin dato queda vacío y la pantalla no lo pinta). La foto local queda
     * solo como respaldo mientras baja la publicada.
     */
    private fun withPublished(record: SpeciesRecord): SpeciesRecord {
        val p = ContentCatalog.byTaxonId(record.id) ?: ContentCatalog.byScientificName(record.scientificName)
        if (p == null) return record.copy(similarIds = computedSimilar(record))
        val curated = p.especies_confusion.mapNotNull { taxon -> local.firstOrNull { it.id == taxon }?.id }
        return record.copy(
            commonName = p.nombre_comun ?: p.nombre_cientifico,
            genus = p.genero ?: record.genus,
            family = p.familia ?: record.family,
            iucn = p.uicn?.categoria?.let { cat -> AnuraConservationChipVariant.entries.firstOrNull { it.name == cat } } ?: record.iucn,
            toxicity = when (p.toxicidad?.nivel) {
                "toxica_tacto", "toxica_ingestion" -> AnuraToxicityChipVariant.Toxic
                "inofensiva" -> AnuraToxicityChipVariant.Harmless
                else -> record.toxicity
            },
            toxicityDeclared = p.toxicidad?.nivel != null,
            altitudeRange = p.altitud_literatura?.let { TaxonTraitRanges.formatPublished(it.min, it.max, "m") }.orEmpty(),
            sizeRange = p.lhc?.let { TaxonTraitRanges.formatPublished(it.min, it.max, "mm") }.orEmpty(),
            catalogObservationCount = p.fotos_referencia?.toString() ?: record.catalogObservationCount,
            catalogObserverCount = "",
            curiousFact = p.dato_curioso?.valor.orEmpty(),
            // `especies_confusion` la cura un herpetólogo al publicar la ficha; sin eso, se
            // calcula de verdad (mismo género, si no misma familia) en vez de una pareja fija
            // escrita a mano por especie.
            similarIds = curated.ifEmpty { computedSimilar(record) },
            photoSha256 = p.foto_principal?.sha256,
            // La atribución de iNaturalist ya trae la licencia ("… (CC BY)"); la licencia sola solo si no hay autor.
            photoCredit = p.foto_principal?.let { it.atribucion ?: it.licencia?.uppercase() },
            morphology = p.morfologia,
            habitat = p.habitat,
            isPublished = true,
        )
    }

    /** Mismo género primero; si no hay otra especie del género, misma familia. Nunca la propia. */
    private fun computedSimilar(record: SpeciesRecord): List<String> = similarsAmong(record, local)

    private fun similarsAmong(record: SpeciesRecord, pool: List<SpeciesRecord>): List<String> {
        val curated = record.similarIds.filter { id -> pool.any { it.id == id } }
        if (curated.isNotEmpty()) return curated.take(2)
        val sameGenus = pool.filter { it.id != record.id && it.genus.isNotBlank() && it.genus == record.genus }
        if (sameGenus.isNotEmpty()) return sameGenus.take(2).map { it.id }
        return pool.filter { it.id != record.id && it.family.isNotBlank() && it.family == record.family }
            .take(2)
            .map { it.id }
    }

    /** Especie exacta por id o nombre científico — nunca especies "hermanas" por género/familia
     * (eso es [findGroup], usado solo para fichas de género/familia). */
    fun find(speciesId: String?): SpeciesRecord? {
        if (speciesId.isNullOrBlank()) return null
        return all.find {
            it.id == speciesId || it.scientificName.equals(speciesId, ignoreCase = true)
        }
    }

    /**
     * Ficha sintética de género/familia/orden: no es ninguna especie real, es un resumen de
     * [byTaxon] (conteo agregado, primera foto como miniatura — el carrusel real de la ficha
     * usa todas las fotos de los miembros, ver `speciesPhotoItems` en SpeciesScreens.kt).
     * Null si `taxonId` no tiene ningún miembro en el catálogo.
     */
    fun findGroup(taxonId: String): SpeciesRecord? {
        val members = byTaxon(taxonId)
        if (members.isEmpty()) return null
        val first = members.first()
        val rankLabel = when {
            members.all { it.genus.equals(taxonId, ignoreCase = true) } -> "Género"
            members.all { it.family.equals(taxonId, ignoreCase = true) } -> "Familia"
            else -> "Orden"
        }
        val altitude = TaxonTraitRanges.merge(members.mapNotNull { TaxonTraitRanges.parse(it.altitudeRange) })
        val size = TaxonTraitRanges.merge(members.mapNotNull { TaxonTraitRanges.parse(it.sizeRange) })
        return SpeciesRecord(
            id = taxonId,
            commonName = taxonId,
            scientificName = rankLabel,
            genus = first.genus,
            family = first.family,
            iucn = TaxonTraitRanges.worstIucn(members.map { it.iucn }),
            toxicity = if (members.any { it.toxicity == AnuraToxicityChipVariant.Toxic }) {
                AnuraToxicityChipVariant.Toxic
            } else {
                AnuraToxicityChipVariant.Harmless
            },
            altitudeRange = altitude?.let(TaxonTraitRanges::formatAltitude) ?: "Ver especies",
            sizeRange = size?.let(TaxonTraitRanges::formatSize) ?: "Ver especies",
            catalogObservationCount = members.sumOf { it.catalogObservationCount.toIntOrNull() ?: 0 }.toString(),
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = first.photoRes,
            similarIds = emptyList(),
        )
    }

    fun asCandidate(scientificName: String, share: Float, genus: String, family: String): IdentificationCandidate {
        val catalog = all.firstOrNull { it.scientificName.equals(scientificName, ignoreCase = true) }
        val parsedGenus = scientificName.substringBefore(' ')
        return IdentificationCandidate(
            scientificName = scientificName,
            share = share,
            genus = genus.ifBlank { catalog?.genus.orEmpty() }.ifBlank { parsedGenus },
            family = family.ifBlank { catalog?.family.orEmpty() },
        )
    }

    fun byTaxon(taxonId: String): List<SpeciesRecord> {
        val needle = taxonId.trim()
        if (needle.isEmpty()) return all
        return all.filter { record ->
            record.genus.equals(needle, ignoreCase = true) ||
                record.family.equals(needle, ignoreCase = true) ||
                record.order.equals(needle, ignoreCase = true) ||
                record.id == needle
        }.ifEmpty { listOfNotNull(find(needle)) }
    }
}
