"""
taxonomia_v1_1_0_candidate.py — Fixture para test lifecycle.
Contiene las 41 especies de v1.0.0 + 1 especie TEST sintetica para test.
"""

ESPECIES = [
    "Boana_boans", "Boana_cinerascens", "Boana_lanciformis", "Boana_platanera",
    "Boana_pugnax", "Boana_punctata", "Boana_rosenbergi", "Boana_xerophylla",
    "Craugastor_raniformis", "Dendrobates_truncatus", "Dendropsophus_bogerti",
    "Dendropsophus_columbianus", "Dendropsophus_ebraccatus", "Dendropsophus_mathiassoni",
    "Dendropsophus_microcephalus", "Dendropsophus_molitor", "Dendropsophus_norandinus",
    "Dendropsophus_reticulatus", "Dendropsophus_triangulum", "Engystomops_pustulosus",
    "Hyloscirtus_palmeri", "Hyloxalus_picachos", "Leptodactylus_colombiensis",
    "Phyllomedusa_tarsius", "Phyllomedusa_venusta", "Pithecopus_hypochondrialis",
    "Pristimantis_achatinus", "Pristimantis_bogotensis", "Pristimantis_erythropleura",
    "Pristimantis_gaigei", "Pristimantis_paisa", "Pristimantis_palmeri",
    "Pristimantis_penelopus", "Pristimantis_permixtus", "Pristimantis_taeniatus",
    "Pristimantis_thectopternus", "Pristimantis_vilarsi", "Rheobates_palmatus",
    "Rhinella_alata", "Rhinella_horribilis", "Rhinella_margaritifera", "Scinax_ruber",
    "Testicus_synthetica",
]

GENERO_DE_ESPECIE = {
    "Boana_boans": "Boana", "Boana_cinerascens": "Boana", "Boana_lanciformis": "Boana",
    "Boana_platanera": "Boana", "Boana_pugnax": "Boana", "Boana_punctata": "Boana",
    "Boana_rosenbergi": "Boana", "Boana_xerophylla": "Boana", "Craugastor_raniformis": "Craugastor",
    "Dendrobates_truncatus": "Dendrobates", "Dendropsophus_bogerti": "Dendropsophus",
    "Dendropsophus_columbianus": "Dendropsophus", "Dendropsophus_ebraccatus": "Dendropsophus",
    "Dendropsophus_mathiassoni": "Dendropsophus", "Dendropsophus_microcephalus": "Dendropsophus",
    "Dendropsophus_molitor": "Dendropsophus", "Dendropsophus_norandinus": "Dendropsophus",
    "Dendropsophus_reticulatus": "Dendropsophus", "Dendropsophus_triangulum": "Dendropsophus",
    "Engystomops_pustulosus": "Engystomops", "Hyloscirtus_palmeri": "Hyloscirtus",
    "Hyloxalus_picachos": "Hyloxalus", "Leptodactylus_colombiensis": "Leptodactylus",
    "Phyllomedusa_tarsius": "Phyllomedusa", "Phyllomedusa_venusta": "Phyllomedusa",
    "Pithecopus_hypochondrialis": "Pithecopus", "Pristimantis_achatinus": "Pristimantis",
    "Pristimantis_bogotensis": "Pristimantis", "Pristimantis_erythropleura": "Pristimantis",
    "Pristimantis_gaigei": "Pristimantis", "Pristimantis_paisa": "Pristimantis",
    "Pristimantis_palmeri": "Pristimantis", "Pristimantis_penelopus": "Pristimantis",
    "Pristimantis_permixtus": "Pristimantis", "Pristimantis_taeniatus": "Pristimantis",
    "Pristimantis_thectopternus": "Pristimantis", "Pristimantis_vilarsi": "Pristimantis",
    "Rheobates_palmatus": "Rheobates", "Rhinella_alata": "Rhinella",
    "Rhinella_horribilis": "Rhinella", "Rhinella_margaritifera": "Rhinella", "Scinax_ruber": "Scinax",
    "Testicus_synthetica": "Testicus",
}

FAMILIA_DE_ESPECIE = {
    "Boana_boans": "Hylidae", "Boana_cinerascens": "Hylidae", "Boana_lanciformis": "Hylidae",
    "Boana_platanera": "Hylidae", "Boana_pugnax": "Hylidae", "Boana_punctata": "Hylidae",
    "Boana_rosenbergi": "Hylidae", "Boana_xerophylla": "Hylidae", "Craugastor_raniformis": "Craugastoridae",
    "Dendrobates_truncatus": "Dendrobatidae", "Dendropsophus_bogerti": "Hylidae",
    "Dendropsophus_columbianus": "Hylidae", "Dendropsophus_ebraccatus": "Hylidae",
    "Dendropsophus_mathiassoni": "Hylidae", "Dendropsophus_microcephalus": "Hylidae",
    "Dendropsophus_molitor": "Hylidae", "Dendropsophus_norandinus": "Hylidae",
    "Dendropsophus_reticulatus": "Hylidae", "Dendropsophus_triangulum": "Hylidae",
    "Engystomops_pustulosus": "Leptodactylidae", "Hyloscirtus_palmeri": "Hylidae",
    "Hyloxalus_picachos": "Dendrobatidae", "Leptodactylus_colombiensis": "Leptodactylidae",
    "Phyllomedusa_tarsius": "Hylidae", "Phyllomedusa_venusta": "Hylidae",
    "Pithecopus_hypochondrialis": "Hylidae", "Pristimantis_achatinus": "Craugastoridae",
    "Pristimantis_bogotensis": "Craugastoridae", "Pristimantis_erythropleura": "Craugastoridae",
    "Pristimantis_gaigei": "Craugastoridae", "Pristimantis_paisa": "Craugastoridae",
    "Pristimantis_palmeri": "Craugastoridae", "Pristimantis_penelopus": "Craugastoridae",
    "Pristimantis_permixtus": "Craugastoridae", "Pristimantis_taeniatus": "Craugastoridae",
    "Pristimantis_thectopternus": "Craugastoridae", "Pristimantis_vilarsi": "Craugastoridae",
    "Rheobates_palmatus": "Aromobatidae", "Rhinella_alata": "Bufonidae",
    "Rhinella_horribilis": "Bufonidae", "Rhinella_margaritifera": "Bufonidae", "Scinax_ruber": "Hylidae",
    "Testicus_synthetica": "Hylidae",
}

ALIAS = {}

def genero_de(especie: str) -> str:
    return GENERO_DE_ESPECIE.get(especie, especie.split("_")[0])

def familia_de(especie: str) -> str:
    return FAMILIA_DE_ESPECIE.get(especie, "Unknown")
