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
            sizeBytes = 9_154_560L,
            // Incluye zone_prior/zone_prior_meta (prior geográfico) y weather_prior/weather_prior_meta
            // (prior de clima) horneadas en el paquete esta sesión — ver Arquitectura Multimodal §5.1.
            // Bug real que este valor causó: quedó desactualizado tras hornear las tablas nuevas, así
            // que un teléfono con el paquete ya "instalado" (estado persistido) nunca detectaba que el
            // asset había cambiado y seguía usando una copia vieja sin esas tablas — crash real en
            // campo ("no such table: zone_prior_meta") en vez de simplemente actualizar el paquete.
            sha256 = "ef32050262ca37dc7b08892ec93c418153a264befc0060ec20afacea44ecae9e",
            assetPath = "packages/antioquia/package.sqlite",
        ),
    )

    fun find(id: String): AnuraPackageManifest? = manifests.firstOrNull { it.id == id }
}
