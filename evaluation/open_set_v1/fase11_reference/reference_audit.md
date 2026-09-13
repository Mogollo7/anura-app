# Fase 11 — auditoría de referencia independiente

**Resultado:** `NO_INDEPENDENT_REFERENCE_AVAILABLE`.

Se auditaron `data cleaned`, `training/manifiesto.json`, manifiestos de open-set,
documentación de F3/F4 y artefactos previos de calibración. El corpus contiene
12254 imágenes; TRAIN=3609, VAL=697,
F3/TEST=766. Las imágenes fuera de esos splits no tienen
declaración verificable de origen, uso histórico o retención independiente, por lo
que se clasifican B y no se promocionan. F3 y F4 se mantienen protegidos.

## Clasificación

| Clase | Conteo | Uso |
|---|---:|---|
| A | 0 | independiente verificable |
| B | 7475 | potencialmente independiente, no verificable; solo candidatos |
| C | 4779 | TRAIN/VAL/F3/F4, contaminada o no utilizable |
| D | 0 | información insuficiente |

## Cobertura por especie

| Especie | Imágenes limpias | Candidatas B | A aceptadas |
|---|---:|---:|---:|
| Boana_boans | 145 | 30 | 0 |
| Boana_cinerascens | 138 | 30 | 0 |
| Boana_lanciformis | 209 | 84 | 0 |
| Boana_platanera | 150 | 18 | 0 |
| Boana_pugnax | 148 | 12 | 0 |
| Boana_punctata | 395 | 281 | 0 |
| Boana_rosenbergi | 148 | 0 | 0 |
| Boana_xerophylla | 100 | 0 | 0 |
| Craugastor_raniformis | 298 | 184 | 0 |
| Dendrobates_truncatus | 1809 | 1684 | 0 |
| Dendropsophus_bogerti | 948 | 814 | 0 |
| Dendropsophus_columbianus | 146 | 6 | 0 |
| Dendropsophus_ebraccatus | 148 | 8 | 0 |
| Dendropsophus_mathiassoni | 150 | 0 | 0 |
| Dendropsophus_microcephalus | 713 | 611 | 0 |
| Dendropsophus_molitor | 150 | 41 | 0 |
| Dendropsophus_norandinus | 26 | 0 | 0 |
| Dendropsophus_reticulatus | 100 | 0 | 0 |
| Dendropsophus_triangulum | 132 | 0 | 0 |
| Engystomops_pustulosus | 1718 | 1592 | 0 |
| Hyloscirtus_palmeri | 178 | 44 | 0 |
| Leptodactylus_colombiensis | 206 | 38 | 0 |
| Phyllomedusa_tarsius | 97 | 0 | 0 |
| Phyllomedusa_venusta | 150 | 14 | 0 |
| Pithecopus_hypochondrialis | 149 | 0 | 0 |
| Pristimantis_achatinus | 1902 | 1761 | 0 |
| Pristimantis_bogotensis | 143 | 0 | 0 |
| Pristimantis_erythropleura | 136 | 28 | 0 |
| Pristimantis_gaigei | 89 | 0 | 0 |
| Pristimantis_paisa | 170 | 48 | 0 |
| Pristimantis_palmeri | 100 | 0 | 0 |
| Pristimantis_penelopus | 156 | 14 | 0 |
| Pristimantis_permixtus | 111 | 0 | 0 |
| Pristimantis_taeniatus | 160 | 46 | 0 |
| Pristimantis_thectopternus | 80 | 0 | 0 |
| Pristimantis_vilarsi | 56 | 0 | 0 |
| Rheobates_palmatus | 70 | 0 | 0 |
| Rhinella_alata | 90 | 0 | 0 |
| Rhinella_horribilis | 100 | 0 | 0 |
| Rhinella_margaritifera | 159 | 51 | 0 |
| Scinax_ruber | 125 | 36 | 0 |

No se ejecutó Mahalanobis, tuning ni evaluación sobre F3/F4. No se modificaron
modelos, checkpoints, encoder, embeddings, dataset, splits, SQLite-vec, prior,
móvil ni producción. Los hashes de fuentes y el control SHA-256 están en
`reference_audit.json`.
