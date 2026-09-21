package me.juanlabs.anura.core.data

import androidx.annotation.DrawableRes
import me.juanlabs.anura.R
import me.juanlabs.anura.designsystem.component.AnuraConservationChipVariant
import me.juanlabs.anura.designsystem.component.AnuraToxicityChipVariant

/**
 * Catálogo de producto (no es dato de usuario). Fuente única por `speciesId`
 * para fichas, carrusel y resultados simulados.
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
            id = "ANU_COL_DEND_TRU_001",
            commonName = "Rana venenosa de dorso amarillo",
            scientificName = "Dendrobates truncatus",
            genus = "Dendrobates",
            family = "Dendrobatidae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Toxic,
            altitudeRange = "0–1.200 m",
            sizeRange = "20–31 mm",
            catalogObservationCount = "1.284",
            catalogObserverCount = "6",
            curiousFact = "Acumula su veneno comiendo hormigas y ácaros.",
            photoRes = R.drawable.carousel_dendrobates_truncatus,
            similarIds = listOf("ANU_COL_PHYL_TER_001", "ANU_COL_DEND_BOG_001"),
        ),
        SpeciesRecord(
            id = "ANU_COL_PRIS_PAI_001",
            commonName = "Rana paisa",
            scientificName = "Pristimantis paisa",
            genus = "Pristimantis",
            family = "Strabomantidae",
            iucn = AnuraConservationChipVariant.NT,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "1.800–2.600 m",
            sizeRange = "18–28 mm",
            catalogObservationCount = "412",
            catalogObserverCount = "14",
            curiousFact = "Nace desarrollada del huevo, sin fase de renacuajo.",
            photoRes = R.drawable.carousel_pristimantis_paisa,
            similarIds = listOf("ANU_COL_SACH_ELE_001", "ANU_COL_DEND_BOG_001"),
        ),
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
            similarIds = listOf("ANU_COL_ESPA_PRO_001", "ANU_COL_PRIS_PAI_001"),
        ),
        SpeciesRecord(
            id = "ANU_COL_DEND_BOG_001",
            commonName = "Ranita de Bogert",
            scientificName = "Dendropsophus bogerti",
            genus = "Dendropsophus",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "800–2.000 m",
            sizeRange = "22–35 mm",
            catalogObservationCount = "673",
            catalogObserverCount = "21",
            curiousFact = "Canta en alta frecuencia junto a ríos de montaña.",
            photoRes = R.drawable.carousel_dendropsophus_bogerti,
            similarIds = listOf("ANU_COL_BOAN_PUG_001", "ANU_COL_SACH_ELE_001"),
        ),
        SpeciesRecord(
            id = "ANU_COL_PHYL_TER_001",
            commonName = "Rana batea",
            scientificName = "Phyllobates terribilis",
            genus = "Phyllobates",
            family = "Dendrobatidae",
            iucn = AnuraConservationChipVariant.EN,
            toxicity = AnuraToxicityChipVariant.Toxic,
            altitudeRange = "100–200 m",
            sizeRange = "37–47 mm",
            catalogObservationCount = "86",
            catalogObserverCount = "4",
            curiousFact = "Es una de las ranas más tóxicas del planeta.",
            photoRes = R.drawable.carousel_dendrobates_truncatus,
            similarIds = listOf("ANU_COL_DEND_TRU_001"),
        ),
        SpeciesRecord(
            id = "ANU_COL_ESPA_PRO_001",
            commonName = "Rana de espolón",
            scientificName = "Espadarana prosoblepon",
            genus = "Espadarana",
            family = "Centrolenidae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "0–1.500 m",
            sizeRange = "21–31 mm",
            catalogObservationCount = "241",
            catalogObserverCount = "11",
            curiousFact = "Los machos defienden hojas sobre arroyos.",
            photoRes = R.drawable.carousel_sachatamia_electrops,
            similarIds = listOf("ANU_COL_SACH_ELE_001"),
        ),
        SpeciesRecord(
            id = "ANU_COL_BOAN_PUG_001",
            commonName = "Rana platanera",
            scientificName = "Boana pugnax",
            genus = "Boana",
            family = "Hylidae",
            iucn = AnuraConservationChipVariant.LC,
            toxicity = AnuraToxicityChipVariant.Harmless,
            altitudeRange = "0–1.600 m",
            sizeRange = "45–70 mm",
            catalogObservationCount = "531",
            catalogObserverCount = "18",
            curiousFact = "Se reproduce en charcas temporales tras lluvias fuertes.",
            photoRes = R.drawable.carousel_dendropsophus_bogerti,
            similarIds = listOf("ANU_COL_DEND_BOG_001"),
        ),
    )

    private val byId = all.associateBy { it.id }

    fun find(speciesId: String?): SpeciesRecord? {
        if (speciesId.isNullOrBlank()) return null
        byId[speciesId]?.let { return it }
        return all.find { record ->
            record.genus.equals(speciesId, ignoreCase = true) ||
                record.family.equals(speciesId, ignoreCase = true) ||
                record.order.equals(speciesId, ignoreCase = true) ||
                record.scientificName.equals(speciesId, ignoreCase = true)
        }
    }

    fun requireOrTruncatus(speciesId: String?): SpeciesRecord =
        find(speciesId) ?: all.first { it.id == SimulatedKnownSpeciesId }

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
