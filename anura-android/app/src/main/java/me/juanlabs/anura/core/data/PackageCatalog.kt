package me.juanlabs.anura.core.data

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * Árbol que publica dataset-service en `GET /api/dataset/publico/paquetes`.
 * País y departamento pueden no traer archivo propio: bajarlos dispara a los hijos.
 */
@Serializable
data class PackageCatalogResponse(
    val paises: List<PackageNode> = emptyList(),
)

@Serializable
data class PackageNode(
    val id: String,
    val nivel: String,
    val nombre: String,
    val version: String? = null,
    val especies: Int? = null,
    @SerialName("size_bytes") val sizeBytes: Long = 0,
    @SerialName("size_archivo") val sizeArchivo: Long = 0,
    val sha256: String? = null,
    val formato: String? = null,
    val nota: String? = null,
    @SerialName("archivo_url") val archivoUrl: String? = null,
    val hijos: List<PackageNode> = emptyList(),
)

sealed interface PackageCatalogState {
    data object Loading : PackageCatalogState
    data object Ready : PackageCatalogState
    data class Failed(val message: String) : PackageCatalogState
}

fun flattenPackages(node: PackageNode): List<PackageNode> =
    listOf(node) + node.hijos.flatMap(::flattenPackages)

fun findPackage(nodes: List<PackageNode>, id: String): PackageNode? {
    for (node in nodes) {
        if (node.id == id) return node
        findPackage(node.hijos, id)?.let { return it }
    }
    return null
}
