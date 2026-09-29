package me.juanlabs.anura.core.data

import me.juanlabs.anura.designsystem.component.AnuraConservationChipVariant
import me.juanlabs.anura.designsystem.component.AnuraToxicityChipVariant
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

/** El registro de especie sale SOLO de la ficha publicada: lo que no trae queda vacío, nunca inventado. */
class SpeciesCatalogTest {
    private fun species(
        id: String,
        name: String,
        genus: String? = null,
        family: String? = null,
        confusion: List<String> = emptyList(),
    ) = PublishedSpecies(
        taxon_id = id,
        nombre_cientifico = name,
        genero = genus,
        familia = family,
        especies_confusion = confusion,
    )

    @Test
    fun sinFichas_noHayRegistros() {
        assertTrue(SpeciesCatalog.recordsFrom(emptyList()).isEmpty())
    }

    @Test
    fun fichaMinima_noInventaNingunDato() {
        val record = SpeciesCatalog.recordsFrom(listOf(species("COL_ANURA_0001", "Rhinella alata"))).single()
        assertEquals("Rhinella alata", record.commonName) // sin nombre común, el científico
        assertNull(record.iucn)
        assertEquals("", record.altitudeRange)
        assertEquals("", record.sizeRange)
        assertEquals("", record.catalogObservationCount)
        assertEquals("", record.curiousFact)
        assertNull(record.photoSha256)
        assertNull(record.morphology)
        assertEquals(false, record.toxicityDeclared)
    }

    @Test
    fun fichaCompleta_usaLosDatosPublicados() {
        val published = PublishedSpecies(
            taxon_id = "COL_ANURA_0007",
            nombre_cientifico = "Dendrobates truncatus",
            nombre_comun = "Rana venenosa",
            genero = "Dendrobates",
            familia = "Dendrobatidae",
            uicn = PublishedIucn(categoria = "VU"),
            toxicidad = PublishedToxicity(nivel = "toxica_tacto"),
            altitud_literatura = PublishedRange(min = 0.0, max = 1200.0),
            lhc = PublishedRange(min = 20.0, max = 25.0),
            fotos_referencia = 42,
            foto_principal = PublishedPhoto(sha256 = "abc", licencia = "cc-by", atribucion = "Ana (CC BY)"),
        )
        val record = SpeciesCatalog.recordsFrom(listOf(published)).single()
        assertEquals("Rana venenosa", record.commonName)
        assertEquals(AnuraConservationChipVariant.VU, record.iucn)
        assertEquals(AnuraToxicityChipVariant.Toxic, record.toxicity)
        assertEquals(true, record.toxicityDeclared)
        assertEquals("0–1.200 m", record.altitudeRange)
        assertEquals("20–25 mm", record.sizeRange)
        assertEquals("42", record.catalogObservationCount)
        assertEquals("abc", record.photoSha256)
        assertEquals("Ana (CC BY)", record.photoCredit)
    }

    @Test
    fun similares_curadasGananSobreLasCalculadas() {
        val records = SpeciesCatalog.recordsFrom(
            listOf(
                species("A", "Boana boans", "Boana", "Hylidae", confusion = listOf("C")),
                species("B", "Boana pugnax", "Boana", "Hylidae"),
                species("C", "Scinax ruber", "Scinax", "Hylidae"),
            ),
        ).associateBy { it.id }
        assertEquals(listOf("C"), records.getValue("A").similarIds)
        assertEquals(listOf("A"), records.getValue("B").similarIds) // mismo género
        assertEquals(listOf("A", "B"), records.getValue("C").similarIds) // sin congéneres: misma familia
    }

    @Test
    fun similares_ignoraCurasHaciaEspeciesQueNoEstanPublicadas() {
        val record = SpeciesCatalog.recordsFrom(
            listOf(species("A", "Boana boans", "Boana", "Hylidae", confusion = listOf("NO_EXISTE"))),
        ).single()
        assertTrue(record.similarIds.isEmpty())
    }
}
