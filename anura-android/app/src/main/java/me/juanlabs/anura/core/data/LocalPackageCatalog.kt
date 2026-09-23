package me.juanlabs.anura.core.data

/**
 * Catálogo local de paquetes regionales descargables, empaquetados en `assets/`.
 * Hoy es la única fuente (no hay servidor); el día que exista `GET /packages`,
 * este objeto se reemplaza por una llamada de red que devuelva [AnuraPackageManifest]
 * con la misma forma, sin tocar el resto del pipeline de instalación.
 */
object LocalPackageCatalog {
    val manifests: List<AnuraPackageManifest> = listOf(
        AnuraPackageManifest(
            id = AntioquiaPackageId,
            name = "Antioquia",
            region = "Antioquia",
            version = "1.1.0",
            speciesCount = 30,
            sizeBytes = 9_510_912L,
            // v1.1.0 agrega occurrence_points (coordenadas reales de ocurrencia GBIF por
            // taxon_id, hasta 300 por especie de las 30 reales) para pintar el mapa de
            // distribución de cada ficha — antes no existía ningún punto real, solo el
            // prior de zona agregado (zone_prior). El bump de versión es intencional (no
            // solo el sha256): como no hay detección de paquete desactualizado (ver
            // 00_OPEN_TASKS.md), un teléfono con "1.0.0" ya instalado seguiría usando la
            // copia vieja sin esta tabla si solo cambiara el hash con la misma versión.
            sha256 = "83b328771c261f950cefcd61138c9e37904d015ce924dc21113f713b2c3a8647",
            assetPath = "packages/antioquia/package.sqlite",
        ),
    )

    fun find(id: String): AnuraPackageManifest? = manifests.firstOrNull { it.id == id }
}
