package me.juanlabs.anura.core.data

import me.juanlabs.anura.R

/**
 * Observaciones de otras personas para Explorar / cercanas.
 * No se atribuyen al usuario actual: son catálogo de comunidad del prototipo.
 */
object CommunityCatalog {
    val people: List<CommunityPerson> = listOf(
        CommunityPerson("user-laura", "Laura Restrepo", "@laura.anura", "Medellín, Antioquia"),
        CommunityPerson("user-camila", "Camila Ortiz", "@camila.herpeto", "Manizales, Caldas"),
        CommunityPerson("user-julian", "Julián Pérez", "@julian.anuros", "Pereira, Risaralda"),
        CommunityPerson("user-vale", "Valentina Ruiz", "@vale.campo", "Armenia, Quindío"),
        CommunityPerson("user-andres", "Andrés Gómez", "@andres.bio", "Cali, Valle"),
    )

    val observations: List<ObservationRecord> = listOf(
        communityObs(
            id = "near-001",
            owner = people[0],
            speciesId = "COL_ANURA_0018",
            photoRes = R.drawable.carousel_dendrobates_truncatus,
            lat = 5.0689,
            lon = -75.5174,
            place = "Cercanías de Manizales",
        ),
        communityObs(
            id = "near-002",
            owner = people[1],
            speciesId = "COL_ANURA_0011",
            photoRes = R.drawable.carousel_pristimantis_paisa,
            lat = 5.0820,
            lon = -75.4980,
            place = "Bosque cerca a Villamaría",
        ),
        communityObs(
            id = "near-003",
            owner = people[2],
            speciesId = "COL_ANURA_0028",
            photoRes = R.drawable.carousel_dendropsophus_bogerti,
            lat = 5.0510,
            lon = -75.5400,
            place = "Quebrada Olivares",
        ),
        communityObs(
            id = "near-004",
            owner = people[3],
            speciesId = "ANU_COL_SACH_ELE_001",
            photoRes = R.drawable.carousel_sachatamia_electrops,
            lat = 5.0950,
            lon = -75.5300,
            place = "Río Chinchiná",
        ),
        communityObs(
            id = "near-005",
            owner = people[4],
            speciesId = "COL_ANURA_0011",
            photoRes = R.drawable.carousel_pristimantis_paisa,
            lat = 5.0700,
            lon = -75.5100,
            place = "Sendero La Linda",
        ),
    )

    fun person(userId: String?): CommunityPerson? =
        people.find { it.userId == userId }

    fun observationsOf(userId: String): List<ObservationRecord> =
        observations.filter { it.ownerUserId == userId }

    fun observation(id: String): ObservationRecord? =
        observations.find { it.id == id }
}

data class CommunityPerson(
    val userId: String,
    val displayName: String,
    val handle: String,
    val location: String,
)

private fun communityObs(
    id: String,
    owner: CommunityPerson,
    speciesId: String,
    photoRes: Int,
    lat: Double,
    lon: Double,
    place: String,
): ObservationRecord {
    val species = SpeciesCatalog.find(speciesId)
    return ObservationRecord(
        id = id,
        ownerUserId = owner.userId,
        ownerDisplayName = owner.displayName,
        speciesId = speciesId,
        commonName = species?.commonName,
        scientificName = species?.scientificName,
        photoRes = photoRes,
        latitude = lat,
        longitude = lon,
        placeLabel = place,
        visibilityPublic = true,
        identificationStatus = IdentificationKnown,
        createdAtEpochMs = 1_725_000_000_000L,
    )
}
