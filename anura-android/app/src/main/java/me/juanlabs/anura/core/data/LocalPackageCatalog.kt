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
            version = "1.0.0",
            speciesCount = 30,
            sizeBytes = 9_117_696L,
            sha256 = "618372700d27c8d951651d21c9607daf3ddd50c50e127f16c222d0c164fbda83",
            assetPath = "packages/antioquia/package.sqlite",
        ),
    )

    fun find(id: String): AnuraPackageManifest? = manifests.firstOrNull { it.id == id }
}
