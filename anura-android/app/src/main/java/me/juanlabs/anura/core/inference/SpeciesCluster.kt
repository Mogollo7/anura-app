package me.juanlabs.anura.core.inference

/**
 * Clúster de especies que el modelo confunde entre sí, aceptado por una persona en el Admin y
 * horneado en la tabla `clusters` del paquete. Solo informa: nunca cambia la especie oficial.
 */
data class SpeciesCluster(
    val id: Int,
    val name: String,
    val members: List<ClusterMember>,
) {
    fun contains(taxonId: String): Boolean = members.any { it.taxonId == taxonId }
}

data class ClusterMember(val taxonId: String, val scientificName: String)
