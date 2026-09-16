package me.juanlabs.anura.designsystem.preview

/**
 * Datos de muestra para previews del Design System (§15): nombres reales, no "Lorem
 * ipsum", para que los previews revelen desbordes con textos largos de verdad (p.ej.
 * en `ObservationCard` a 200% de escala de texto).
 *
 * Sin tipos de dominio: este paquete no conoce `domain` (regla de frontera §2) — son
 * literales de texto, no instancias de `Species`/`SpeciesId`.
 */
object SampleData {
    const val CommonNameShort: String = "Rana venenosa"
    const val ScientificNameShort: String = "Pristimantis paisa"

    const val CommonNameLong: String = "Rana de cristal amazónica de vientre transparente"
    const val ScientificNameLong: String = "Hyalinobatrachium ibama"
}
