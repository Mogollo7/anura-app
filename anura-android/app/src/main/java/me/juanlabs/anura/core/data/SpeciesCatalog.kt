package me.juanlabs.anura.core.data

import me.juanlabs.anura.designsystem.component.AnuraConservationChipVariant
import me.juanlabs.anura.designsystem.component.AnuraToxicityChipVariant

/**
 * Ficha de una especie tal como la publicó el herpetólogo en Admin → Contenido (ver
 * [ContentCatalog]). Se arma SOLO desde [PublishedSpecies]: el APK no trae ninguna especie, nombre,
 * cifra ni foto. Todo dato que la ficha publicada no trae queda vacío/nulo y la pantalla lo dice
 * («Sin dato»); nunca se rellena con un valor inventado.
 *
 * - [altitudeRange] y [sizeRange] son la altitud y el largo hocico–cloaca **de literatura** que
 *   trae la ficha (`altitud_literatura`, `lhc`), con su fuente en el servidor. Vacío = sin dato.
 * - [catalogObservationCount] es el número de fotos de referencia vigentes de la especie en el
 *   servidor (`fotos_referencia`), no un contador de comunidad. Vacío = sin dato.
 * - [iucn] es nula cuando la ficha no declara categoría UICN: no se pinta «No evaluada» por defecto.
 * - `similarIds` = las especies de confusión que curó el herpetólogo; si no hay, hasta 2 del mismo
 *   género (o de la misma familia si el género solo tiene una especie publicada).
 */
data class SpeciesRecord(
    val id: String,
    val commonName: String,
    val scientificName: String,
    val genus: String,
    val family: String,
    val order: String = "Anura",
    val iucn: AnuraConservationChipVariant? = null,
    val toxicity: AnuraToxicityChipVariant = AnuraToxicityChipVariant.Harmless,
    val altitudeRange: String = "",
    val sizeRange: String = "",
    val catalogObservationCount: String = "",
    val curiousFact: String = "",
    val similarIds: List<String> = emptyList(),
    /** Foto principal publicada en Admin → Contenido (licencia CC), bajada por sha256; null = sin foto. */
    val photoSha256: String? = null,
    val photoCredit: String? = null,
    /** Morfología revisada; null = no hay (la pestaña lo dice, no muestra texto de ejemplo). */
    val morphology: PublishedMorphology? = null,
    val habitat: String? = null,
    /** false cuando la ficha publicada no trae toxicidad: no se muestra «inofensiva» por defecto. */
    val toxicityDeclared: Boolean = false,
)

object SpeciesCatalog {
    /**
     * La lista es el catálogo descargado ([ContentCatalog]), también sin red. Una especie nueva
     * publicada entra aunque no estuviera antes en el teléfono. Antes de la primera descarga, o si
     * el servidor no tiene especies publicadas, la lista está vacía: cada pantalla lo dice con
     * [catalogGapTitle]/[catalogGapBody].
     */
    val all: List<SpeciesRecord>
        get() {
            val published = ContentCatalog.catalog?.especies ?: return emptyList()
            return recordsFrom(published)
        }

    /** Las fichas de [published] tal cual, con las similares resueltas. Sin datos inventados (ver [SpeciesRecord]). */
    internal fun recordsFrom(published: List<PublishedSpecies>): List<SpeciesRecord> {
        val records = published.map(::fromPublished)
        return records.map { it.copy(similarIds = similarFor(it, published, records)) }
    }

    private fun fromPublished(p: PublishedSpecies): SpeciesRecord = SpeciesRecord(
        id = p.taxon_id,
        commonName = p.nombre_comun ?: p.nombre_cientifico,
        scientificName = p.nombre_cientifico,
        genus = p.genero.orEmpty(),
        family = p.familia.orEmpty(),
        iucn = p.uicn?.categoria?.let { cat -> AnuraConservationChipVariant.entries.firstOrNull { it.name == cat } },
        toxicity = when (p.toxicidad?.nivel) {
            "toxica_tacto", "toxica_ingestion" -> AnuraToxicityChipVariant.Toxic
            else -> AnuraToxicityChipVariant.Harmless
        },
        toxicityDeclared = p.toxicidad?.nivel != null,
        altitudeRange = p.altitud_literatura?.let { TaxonTraitRanges.formatPublished(it.min, it.max, "m") }.orEmpty(),
        sizeRange = p.lhc?.let { TaxonTraitRanges.formatPublished(it.min, it.max, "mm") }.orEmpty(),
        catalogObservationCount = p.fotos_referencia?.toString().orEmpty(),
        curiousFact = p.dato_curioso?.valor.orEmpty(),
        photoSha256 = p.foto_principal?.sha256,
        // La atribución de iNaturalist ya trae la licencia ("… (CC BY)"); la licencia sola solo si no hay autor.
        photoCredit = p.foto_principal?.let { it.atribucion ?: it.licencia?.uppercase() },
        morphology = p.morfologia,
        habitat = p.habitat,
    )

    /**
     * `especies_confusion` la cura un herpetólogo al publicar la ficha; sin eso, se calcula de
     * verdad (mismo género, si no misma familia) en vez de una pareja fija escrita a mano.
     */
    private fun similarFor(record: SpeciesRecord, published: List<PublishedSpecies>, pool: List<SpeciesRecord>): List<String> {
        val curated = published.firstOrNull { it.taxon_id == record.id }
            ?.especies_confusion
            .orEmpty()
            .filter { taxon -> taxon != record.id && pool.any { it.id == taxon } }
        return curated.ifEmpty { computedSimilar(record, pool) }.take(2)
    }

    /** Mismo género primero; si no hay otra especie del género, misma familia. Nunca la propia. */
    private fun computedSimilar(record: SpeciesRecord, pool: List<SpeciesRecord>): List<String> {
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
     * [byTaxon] (conteo agregado, rangos unidos de las fichas que los traen, primera foto como
     * miniatura — el carrusel real de la ficha usa todas las fotos de los miembros, ver
     * `speciesPhotoItems` en SpeciesScreens.kt).
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
        val counts = members.mapNotNull { it.catalogObservationCount.toIntOrNull() }
        return SpeciesRecord(
            id = taxonId,
            commonName = taxonId,
            scientificName = rankLabel,
            genus = first.genus,
            family = first.family,
            iucn = members.mapNotNull { it.iucn }.takeIf { it.isNotEmpty() }?.let(TaxonTraitRanges::worstIucn),
            toxicity = if (members.any { it.toxicity == AnuraToxicityChipVariant.Toxic }) {
                AnuraToxicityChipVariant.Toxic
            } else {
                AnuraToxicityChipVariant.Harmless
            },
            toxicityDeclared = members.any { it.toxicityDeclared },
            altitudeRange = altitude?.let(TaxonTraitRanges::formatAltitude).orEmpty(),
            sizeRange = size?.let(TaxonTraitRanges::formatSize).orEmpty(),
            catalogObservationCount = counts.takeIf { it.isNotEmpty() }?.sum()?.toString().orEmpty(),
            photoSha256 = first.photoSha256,
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
