"""Taxonomía del catálogo de especies del prototipo (C-3, bóveda Obsidian).

Ampliado el 2026-09-11 de 28 a 43 especies: se agregaron 15 especies del mismo
género que las 8 especies con <70 individuos (Boana, Dendropsophus, Phyllomedusa,
Pristimantis), descubiertas vía iNaturalist Projects regionales. NO son auxiliares
descartables — son crecimiento real de alcance del modelo: quedan identificables
en la app igual que las 28 originales (ver anura_cola_larga_taxonomica.md)."""

GENERO_A_FAMILIA = {
    "Boana": "Hylidae",
    "Dendropsophus": "Hylidae",
    "Hyloscirtus": "Hylidae",
    "Scinax": "Hylidae",
    "Craugastor": "Craugastoridae",
    "Pristimantis": "Craugastoridae",  # corregido 2026-09-11: taxon_info.json de iNaturalist confirma Craugastoridae, no Strabomantidae
    "Dendrobates": "Dendrobatidae",
    "Hyloxalus": "Dendrobatidae",
    "Engystomops": "Leptodactylidae",
    "Leptodactylus": "Leptodactylidae",
    "Phyllomedusa": "Phyllomedusidae",
    "Pithecopus": "Phyllomedusidae",
    "Rheobates": "Aromobatidae",
    "Rhinella": "Bufonidae",
    "Sachatamia": "Centrolenidae",
}

ESPECIES = [
    "Boana_cinerascens",
    "Boana_lanciformis",
    "Boana_punctata",
    "Boana_xerophylla",
    "Craugastor_raniformis",
    "Dendrobates_truncatus",
    "Dendropsophus_bogerti",
    "Dendropsophus_microcephalus",
    "Dendropsophus_norandinus",
    "Dendropsophus_reticulatus",
    "Dendropsophus_triangulum",
    "Engystomops_pustulosus",
    "Hyloscirtus_palmeri",
    # "Hyloxalus_picachos" excluida 2026-09-11: especie huérfana (sin género
    # de respaldo, sin candidatos con >=70 fotos en Colombia) + problemas de
    # integridad de datos confirmados (7 de 14 fotos eran duplicados exactos
    # de otras). Queda pendiente de H4 + más datos; se agrega vía paquete
    # regional cuando el gate de validación lo apruebe (ver
    # anura_proceso_crecimiento_catalogo.md).
    "Leptodactylus_colombiensis",
    "Phyllomedusa_tarsius",
    "Pithecopus_hypochondrialis",
    "Pristimantis_achatinus",
    "Pristimantis_paisa",
    "Pristimantis_penelopus",
    "Pristimantis_taeniatus",
    "Pristimantis_vilarsi",
    "Rheobates_palmatus",
    "Rhinella_alata",
    "Rhinella_horribilis",
    "Rhinella_margaritifera",
    # "Sachatamia_electrops" excluida 2026-09-11: especie huérfana (única
    # Centrolenidae del catálogo, sin candidatos con >=70 fotos en Colombia)
    # + problemas de integridad de datos confirmados (foto mal etiquetada
    # como Cochranella_albomaculata, 10 de 46 fotos eran duplicados exactos).
    # Mismo tratamiento que Hyloxalus_picachos, ver nota arriba.
    "Scinax_ruber",
    # --- Crecimiento de alcance 2026-09-11 (mismo género que especies débiles) ---
    "Boana_platanera",
    "Boana_pugnax",
    "Boana_boans",
    "Boana_rosenbergi",
    "Dendropsophus_molitor",
    "Dendropsophus_columbianus",
    "Dendropsophus_ebraccatus",
    "Dendropsophus_mathiassoni",
    "Phyllomedusa_venusta",
    "Pristimantis_palmeri",
    "Pristimantis_gaigei",
    "Pristimantis_bogotensis",
    "Pristimantis_thectopternus",
    "Pristimantis_erythropleura",
    "Pristimantis_permixtus",
]

# Nombres alternativos vistos en las carpetas raíz de D:\Anura, mapeados al canónico.
ALIAS = {
    "Boana cinereansis": "Boana_cinerascens",
    "Boana xeraphyla": "Boana_xerophylla",
    "Dendrosophus reticulatus": "Dendropsophus_reticulatus",
    "Pristimantis acanthinus": "Pristimantis_achatinus",
    "Rhinella SF margatiferas": "Rhinella_margaritifera",
}


def genero_de(especie: str) -> str:
    return especie.split("_")[0]


def familia_de(especie: str) -> str:
    genero = genero_de(especie)
    if genero not in GENERO_A_FAMILIA:
        raise KeyError(f"Género sin familia asignada: {genero} (especie {especie})")
    return GENERO_A_FAMILIA[genero]


def canonico(nombre: str) -> str:
    if nombre in ALIAS:
        return ALIAS[nombre]
    return nombre.replace(" ", "_")


def vocabularios():
    """Devuelve (familias, generos, especies) ordenados, para indexar las cabezas."""
    especies = sorted(ESPECIES)
    generos = sorted({genero_de(e) for e in especies})
    familias = sorted({familia_de(e) for e in especies})
    return familias, generos, especies
