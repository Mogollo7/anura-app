package me.juanlabs.anura.core.data

import androidx.annotation.DrawableRes
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraConservationChipVariant
import me.juanlabs.anura.designsystem.component.AnuraToxicityChipVariant

/**
 * Catálogo de producto (no es dato de usuario). Fuente única por `speciesId`
 * para fichas, carrusel y resultados simulados.
 *
 * Las 30 especies con id `COL_ANURA_XXXX` son las reales del paquete visual de Antioquia
 * (mismo taxon_id que `package.sqlite`/`taxonomy_guide.json` — no un id de demo inventado).
 * `iucn = DD` en todas: no hay una fuente de estado de conservación verificada por especie
 * integrada todavía (evitar fabricar CR/EN/VU/NT/LC sin dato real). `altitudeRange`/
 * `sizeRange` = "Sin datos" por el mismo motivo. `catalogObservationCount` es el número real
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
)

object SpeciesCatalog {
    val all: List<SpeciesRecord> = listOf(
        SpeciesRecord(
            id = "COL_ANURA_0001",
            commonName = "Palm Rocket Frog",
            scientificName = "Rheobates palmatus",
            genus = "Rheobates",
            family = "Aromobatidae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "70",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_rheobates_palmatus,
            similarIds = listOf(),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0002",
            commonName = "Sapo del Obispo",
            scientificName = "Rhinella alata",
            genus = "Rhinella",
            family = "Bufonidae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "90",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_rhinella_alata,
            similarIds = listOf("COL_ANURA_0003", "COL_ANURA_0004"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0003",
            commonName = "Sapo gigante",
            scientificName = "Rhinella horribilis",
            genus = "Rhinella",
            family = "Bufonidae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "94",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_rhinella_horribilis,
            similarIds = listOf("COL_ANURA_0002", "COL_ANURA_0004"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0004",
            commonName = "Sapo Crestado",
            scientificName = "Rhinella margaritifera",
            genus = "Rhinella",
            family = "Bufonidae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "159",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_rhinella_margaritifera,
            similarIds = listOf("COL_ANURA_0002", "COL_ANURA_0003"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0006",
            commonName = "Rana chivita",
            scientificName = "Craugastor raniformis",
            genus = "Craugastor",
            family = "Craugastoridae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "298",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_craugastor_raniformis,
            similarIds = listOf("COL_ANURA_0007", "COL_ANURA_0009"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0007",
            commonName = "Cutín común de occidente",
            scientificName = "Pristimantis achatinus",
            genus = "Pristimantis",
            family = "Craugastoridae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "1902",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_pristimantis_achatinus,
            similarIds = listOf("COL_ANURA_0009", "COL_ANURA_0010"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0009",
            commonName = "Rana De Ingle Roja",
            scientificName = "Pristimantis erythropleura",
            genus = "Pristimantis",
            family = "Craugastoridae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "136",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_pristimantis_erythropleura,
            similarIds = listOf("COL_ANURA_0007", "COL_ANURA_0010"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0010",
            commonName = "Gaige's Rain Frog",
            scientificName = "Pristimantis gaigei",
            genus = "Pristimantis",
            family = "Craugastoridae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "89",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_pristimantis_gaigei,
            similarIds = listOf("COL_ANURA_0007", "COL_ANURA_0009"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0011",
            commonName = "Cutín paisa",
            scientificName = "Pristimantis paisa",
            genus = "Pristimantis",
            family = "Craugastoridae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "170",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_pristimantis_paisa,
            similarIds = listOf("COL_ANURA_0007", "COL_ANURA_0009"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0012",
            commonName = "Palmer's Robber Frog",
            scientificName = "Pristimantis palmeri",
            genus = "Pristimantis",
            family = "Craugastoridae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "100",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_pristimantis_palmeri,
            similarIds = listOf("COL_ANURA_0007", "COL_ANURA_0009"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0013",
            commonName = "Rana De Ingles Negras Y Amarillas",
            scientificName = "Pristimantis penelopus",
            genus = "Pristimantis",
            family = "Craugastoridae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "156",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_pristimantis_penelopus,
            similarIds = listOf("COL_ANURA_0007", "COL_ANURA_0009"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0014",
            commonName = "Rana De Muslos Naranja",
            scientificName = "Pristimantis permixtus",
            genus = "Pristimantis",
            family = "Craugastoridae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "111",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_pristimantis_permixtus,
            similarIds = listOf("COL_ANURA_0007", "COL_ANURA_0009"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0015",
            commonName = "Banded Rain Frog",
            scientificName = "Pristimantis taeniatus",
            genus = "Pristimantis",
            family = "Craugastoridae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "160",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_pristimantis_taeniatus,
            similarIds = listOf("COL_ANURA_0007", "COL_ANURA_0009"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0016",
            commonName = "Rana De Espolon",
            scientificName = "Pristimantis thectopternus",
            genus = "Pristimantis",
            family = "Craugastoridae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "80",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_pristimantis_thectopternus,
            similarIds = listOf("COL_ANURA_0007", "COL_ANURA_0009"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0018",
            commonName = "Rana venenosa de rayas amarillas",
            scientificName = "Dendrobates truncatus",
            genus = "Dendrobates",
            family = "Dendrobatidae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Toxic,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "1809",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_dendrobates_truncatus,
            similarIds = listOf(),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0020",
            commonName = "Rana gladiadora",
            scientificName = "Boana boans",
            genus = "Boana",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "145",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_boana_boans,
            similarIds = listOf("COL_ANURA_0023", "COL_ANURA_0024"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0023",
            commonName = "Rana Platanera de Ojos Pálidos",
            scientificName = "Boana platanera",
            genus = "Boana",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "150",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_boana_platanera,
            similarIds = listOf("COL_ANURA_0020", "COL_ANURA_0024"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0024",
            commonName = "Rana Platanera de ojos tornasol",
            scientificName = "Boana pugnax",
            genus = "Boana",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "148",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_boana_pugnax,
            similarIds = listOf("COL_ANURA_0020", "COL_ANURA_0023"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0026",
            commonName = "rana arbórea de gladiadora",
            scientificName = "Boana rosenbergi",
            genus = "Boana",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "148",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_boana_rosenbergi,
            similarIds = listOf("COL_ANURA_0020", "COL_ANURA_0023"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0027",
            commonName = "Rana platanera del escudo guayanés",
            scientificName = "Boana xerophylla",
            genus = "Boana",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "100",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_boana_xerophylla,
            similarIds = listOf("COL_ANURA_0020", "COL_ANURA_0023"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0028",
            commonName = "Ranita de pantano",
            scientificName = "Dendropsophus bogerti",
            genus = "Dendropsophus",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "948",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_dendropsophus_bogerti,
            similarIds = listOf("COL_ANURA_0029", "COL_ANURA_0030"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0029",
            commonName = "Ranita de pantano Colombiana",
            scientificName = "Dendropsophus columbianus",
            genus = "Dendropsophus",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "146",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_dendropsophus_columbianus,
            similarIds = listOf("COL_ANURA_0028", "COL_ANURA_0030"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0030",
            commonName = "Rana arbórea amarillenta",
            scientificName = "Dendropsophus ebraccatus",
            genus = "Dendropsophus",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "148",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_dendropsophus_ebraccatus,
            similarIds = listOf("COL_ANURA_0028", "COL_ANURA_0029"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0032",
            commonName = "Rana de árbol amarilla",
            scientificName = "Dendropsophus microcephalus",
            genus = "Dendropsophus",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "713",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_dendropsophus_microcephalus,
            similarIds = listOf("COL_ANURA_0028", "COL_ANURA_0029"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0034",
            commonName = "El Roble Tree Frog",
            scientificName = "Dendropsophus norandinus",
            genus = "Dendropsophus",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "26",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_dendropsophus_norandinus,
            similarIds = listOf("COL_ANURA_0028", "COL_ANURA_0029"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0037",
            commonName = "Rana de torrente de Palmer",
            scientificName = "Hyloscirtus palmeri",
            genus = "Hyloscirtus",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "178",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_hyloscirtus_palmeri,
            similarIds = listOf("COL_ANURA_0020", "COL_ANURA_0023"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0038",
            commonName = "Ranita Listada",
            scientificName = "Scinax ruber",
            genus = "Scinax",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "125",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_scinax_ruber,
            similarIds = listOf("COL_ANURA_0020", "COL_ANURA_0023"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0039",
            commonName = "Ranita túngara",
            scientificName = "Engystomops pustulosus",
            genus = "Engystomops",
            family = "Leptodactylidae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "1718",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_engystomops_pustulosus,
            similarIds = listOf("COL_ANURA_0040"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0040",
            commonName = "Colombian Thin-toed Frog",
            scientificName = "Leptodactylus colombiensis",
            genus = "Leptodactylus",
            family = "Leptodactylidae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "206",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_leptodactylus_colombiensis,
            similarIds = listOf("COL_ANURA_0039"),
        ),
        SpeciesRecord(
            id = "COL_ANURA_0042",
            commonName = "Lovely Leaf Frog",
            scientificName = "Phyllomedusa venusta",
            genus = "Phyllomedusa",
            family = "Phyllomedusidae",
            iucn = AnuraConservationChipVariant.DD,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "Sin datos",
            sizeRange = "Sin datos",
            catalogObservationCount = "150",
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = R.drawable.carousel_phyllomedusa_venusta,
            similarIds = listOf(),
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
            similarIds = listOf("COL_ANURA_0011"),
        ),
    )

    private val byId = all.associateBy { it.id }

    /** Especie exacta por id o nombre científico — nunca especies "hermanas" por género/familia
     * (eso es [findGroup], usado solo para fichas de género/familia). */
    fun find(speciesId: String?): SpeciesRecord? {
        if (speciesId.isNullOrBlank()) return null
        byId[speciesId]?.let { return it }
        return all.find { it.scientificName.equals(speciesId, ignoreCase = true) }
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
        return SpeciesRecord(
            id = taxonId,
            commonName = taxonId,
            scientificName = rankLabel,
            genus = first.genus,
            family = first.family,
            iucn = AnuraConservationChipVariant.DD,
            toxicity = if (members.any { it.toxicity == AnuraToxicityChipVariant.Toxic }) {
                AnuraToxicityChipVariant.Toxic
            } else {
                AnuraToxicityChipVariant.Harmless
            },
            altitudeRange = "Ver especies",
            sizeRange = "Ver especies",
            catalogObservationCount = members.sumOf { it.catalogObservationCount.toIntOrNull() ?: 0 }.toString(),
            catalogObserverCount = "—",
            curiousFact = "",
            photoRes = first.photoRes,
            similarIds = emptyList(),
        )
    }

    fun requireOrTruncatus(speciesId: String?): SpeciesRecord =
        find(speciesId) ?: all.first { it.id == SimulatedKnownSpeciesId }

    fun rankedCandidates(species: SpeciesRecord): List<IdentificationCandidate> {
        val ranked = listOf(species) + species.similarIds.mapNotNull(::find).take(2)
        val shares = when (ranked.size) {
            1 -> floatArrayOf(0.92f)
            2 -> floatArrayOf(0.81f, 0.19f)
            else -> floatArrayOf(0.74f, 0.16f, 0.10f)
        }
        return ranked.mapIndexed { index, record ->
            IdentificationCandidate(record.scientificName, shares[index], record.genus, record.family)
        }
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
