# Auditoria de Solapamiento Visual — Falsos Aceptados (Fase 23A / open_set_topography_v1)

Generado a partir de `fase23a_false_accepts_context_frozen.json` (228 registros). Solo lectura — ningun archivo de datos fue modificado.

## Tabla resumen: pares de especies mas confundidos

| # | Especie UNKNOWN (real) | Especie KNOWN (predicha) | Frecuencia | visual_d1 promedio | margin promedio |
|---|---|---|---|---|---|
| 1 | Rhinella marina | Rhinella horribilis | 60 | 0.4596 | 0.2713 |
| 2 | Dendropsophus labialis | Dendropsophus molitor | 47 | 0.6352 | 0.1807 |
| 3 | Craugastor metriosistus | Craugastor raniformis | 23 | 0.4809 | 0.1455 |
| 4 | Espadarana prosoblepon | Hyloscirtus palmeri | 22 | 0.5393 | 0.1413 |
| 5 | Smilisca phaeota | Boana lanciformis | 21 | 0.6807 | 0.1387 |
| 6 | Leptodactylus fragilis | Leptodactylus colombiensis | 17 | 0.6260 | 0.2047 |
| 7 | Leptodactylus fragilis | Engystomops pustulosus | 6 | 0.7168 | 0.1849 |
| 8 | Smilisca phaeota | Dendropsophus molitor | 5 | 0.7356 | 0.1208 |
| 9 | Leptodactylus fragilis | Craugastor raniformis | 5 | 0.7282 | 0.1388 |
| 10 | Rhinella marina | Engystomops pustulosus | 4 | 0.6378 | 0.2562 |
| 11 | Smilisca phaeota | Pithecopus hypochondrialis | 3 | 0.7652 | 0.1070 |
| 12 | Craugastor metriosistus | Pristimantis thectopternus | 3 | 0.5505 | 0.1499 |
| 13 | Leptodactylus fragilis | Scinax ruber | 2 | 0.7795 | 0.1244 |
| 14 | Espadarana prosoblepon | Boana cinerascens | 1 | 0.6265 | 0.0998 |
| 15 | Leptodactylus fragilis | Rheobates palmatus | 1 | 0.6348 | 0.1590 |
| 16 | Leptodactylus fragilis | Pristimantis vilarsi | 1 | 0.7166 | 0.1505 |
| 17 | Rhinella marina | Rhinella margaritifera | 1 | 0.6748 | 0.1094 |
| 18 | Rhinella marina | Craugastor raniformis | 1 | 0.7585 | 0.1007 |
| 19 | Scinax rostratus | Pristimantis thectopternus | 1 | 0.7760 | 0.0974 |
| 20 | Scinax rostratus | Pristimantis bogotensis | 1 | 0.7835 | 0.0987 |
| 21 | Scinax rostratus | Craugastor raniformis | 1 | 0.8041 | 0.1267 |
| 22 | Scinax rostratus | Rhinella margaritifera | 1 | 0.6374 | 0.1461 |
| 23 | Scinax rostratus | Engystomops pustulosus | 1 | 0.8072 | 0.1141 |

Total de pares distintos: 23. Total de casos: 228.

Nota de lectura: `visual_d1` es la distancia visual (embedding) al centroide de la especie predicha — mas bajo significa mas parecido visualmente. `margin` es el margen entre el primer y segundo prototipo mas cercano en el protocolo de dos prototipos — mas bajo significa una decision mas ambigua/fronteriza.

## Detalle por par (top 15) — rutas de imagen para revision manual

### 1. Rhinella marina (UNKNOWN real) confundida con Rhinella horribilis (KNOWN predicha) — 60 casos

- visual_d1 promedio: 0.4596  |  margin promedio: 0.2713

**Imagenes de referencia de `Rhinella horribilis` (KNOWN, `data cleaned/`):**
- `data cleaned\Rhinella_horribilis\col_obs_332619216_photo_603683613.jpg`
- `data cleaned\Rhinella_horribilis\col_obs_332818028_photo_604089420.jpg`
- `data cleaned\Rhinella_horribilis\col_obs_333019187_photo_604501508.jpg`

**Casos UNKNOWN (`Rhinella marina`) confundidos con esta especie — hasta 10 ejemplos (de 60 totales, ver CSV para todos):**

| observation_id | visual_d1 | margin | ruta imagen UNKNOWN |
|---|---|---|---|
| 339825067 | 0.3033 | 0.3375 | `data\unknown_open_set_v2\images\primary\Rhinella_marina\col_obs_339825067_photo_618272395.jpg` |
| 348052086 | 0.3137 | 0.4093 | `data\unknown_open_set_v2\images\primary\Rhinella_marina\col_obs_348052086_photo_634711368.jpg` |
| 339454979 | 0.3160 | 0.3032 | `data\unknown_open_set_v2\images\primary\Rhinella_marina\col_obs_339454979_photo_617520543.jpg` |
| 337121627 | 0.3249 | 0.2922 | `data\unknown_open_set_v2\images\primary\Rhinella_marina\col_obs_337121627_photo_612771743.jpg` |
| 340210143 | 0.3279 | 0.3115 | `data\unknown_open_set_v2\images\primary\Rhinella_marina\col_obs_340210143_photo_619064515.jpg` |
| 347969150 | 0.3324 | 0.4066 | `data\unknown_open_set_v2\images\primary\Rhinella_marina\col_obs_347969150_photo_634544310.jpg` |
| 337121627 | 0.3368 | 0.2879 | `data\unknown_open_set_v2\images\primary\Rhinella_marina\col_obs_337121627_photo_612771743.jpg` |
| 347969150 | 0.3384 | 0.4216 | `data\unknown_open_set_v2\images\primary\Rhinella_marina\col_obs_347969150_photo_634544310.jpg` |
| 348052086 | 0.3462 | 0.3888 | `data\unknown_open_set_v2\images\primary\Rhinella_marina\col_obs_348052086_photo_634711368.jpg` |
| 338449073 | 0.3504 | 0.3113 | `data\unknown_open_set_v2\images\primary\Rhinella_marina\col_obs_338449073_photo_615499839.jpg` |

_... y 50 casos adicionales — ver `VISUAL_OVERLAP_PAIRS.csv` filtrando por true_species_evaluation_only='Rhinella marina' y predicted_species='Rhinella horribilis'._

### 2. Dendropsophus labialis (UNKNOWN real) confundida con Dendropsophus molitor (KNOWN predicha) — 47 casos

- visual_d1 promedio: 0.6352  |  margin promedio: 0.1807

**Imagenes de referencia de `Dendropsophus molitor` (KNOWN, `data cleaned/`):**
- `data cleaned\Dendropsophus_molitor\col_obs_356781671_photo_650664705.jpg`
- `data cleaned\Dendropsophus_molitor\col_obs_356781671_photo_650664838.jpg`
- `data cleaned\Dendropsophus_molitor\col_obs_357032600_photo_651143186.jpg`

**Casos UNKNOWN (`Dendropsophus labialis`) confundidos con esta especie — hasta 10 ejemplos (de 47 totales, ver CSV para todos):**

| observation_id | visual_d1 | margin | ruta imagen UNKNOWN |
|---|---|---|---|
| 398756459 | 0.4786 | 0.1880 | `data\unknown_open_set_v2\images\primary\Dendropsophus_labialis\col_obs_398756459_photo_731523344.jpg` |
| 372634674 | 0.4809 | 0.1328 | `data\unknown_open_set_v2\images\primary\Dendropsophus_labialis\col_obs_372634674_photo_680943033.jpg` |
| 398344076 | 0.4870 | 0.2578 | `data\unknown_open_set_v2\images\primary\Dendropsophus_labialis\col_obs_398344076_photo_730727185.jpg` |
| 386619505 | 0.5134 | 0.1838 | `data\unknown_open_set_v2\images\primary\Dendropsophus_labialis\col_obs_386619505_photo_707895722.jpg` |
| 378585244 | 0.5254 | 0.1456 | `data\unknown_open_set_v2\images\primary\Dendropsophus_labialis\col_obs_378585244_photo_705829359.jpg` |
| 380176757 | 0.5366 | 0.2183 | `data\unknown_open_set_v2\images\primary\Dendropsophus_labialis\col_obs_380176757_photo_695506372.jpg` |
| 395384588 | 0.5465 | 0.2854 | `data\unknown_open_set_v2\images\primary\Dendropsophus_labialis\col_obs_395384588_photo_724975242.jpg` |
| 396010056 | 0.5493 | 0.2255 | `data\unknown_open_set_v2\images\primary\Dendropsophus_labialis\col_obs_396010056_photo_726189256.jpg` |
| 389794299 | 0.5557 | 0.1691 | `data\unknown_open_set_v2\images\primary\Dendropsophus_labialis\col_obs_389794299_photo_714034734.jpg` |
| 385803911 | 0.5588 | 0.3005 | `data\unknown_open_set_v2\images\primary\Dendropsophus_labialis\col_obs_385803911_photo_706327013.jpg` |

_... y 37 casos adicionales — ver `VISUAL_OVERLAP_PAIRS.csv` filtrando por true_species_evaluation_only='Dendropsophus labialis' y predicted_species='Dendropsophus molitor'._

### 3. Craugastor metriosistus (UNKNOWN real) confundida con Craugastor raniformis (KNOWN predicha) — 23 casos

- visual_d1 promedio: 0.4809  |  margin promedio: 0.1455

**Imagenes de referencia de `Craugastor raniformis` (KNOWN, `data cleaned/`):**
- `data cleaned\Craugastor_raniformis\col_obs_1039482_photo_1303596.jpg`
- `data cleaned\Craugastor_raniformis\col_obs_1039482_photo_1303597.jpg`
- `data cleaned\Craugastor_raniformis\col_obs_105160157_photo_176379597.jpg`

**Casos UNKNOWN (`Craugastor metriosistus`) confundidos con esta especie — hasta 10 ejemplos (de 23 totales, ver CSV para todos):**

| observation_id | visual_d1 | margin | ruta imagen UNKNOWN |
|---|---|---|---|
| 271820747 | 0.3711 | 0.1017 | `data\unknown_open_set_v2\images\primary\Craugastor_metriosistus\271820747_488972452.jpg` |
| 339182754 | 0.3722 | 0.1413 | `data\unknown_open_set_v2\images\primary\Craugastor_metriosistus\339182754_616959884.jpg` |
| 338006893 | 0.3945 | 0.1308 | `data\unknown_open_set_v2\images\primary\Craugastor_metriosistus\338006893_614586134.jpg` |
| 347611201 | 0.4003 | 0.1194 | `data\unknown_open_set_v2\images\primary\Craugastor_metriosistus\347611201_633832745.jpg` |
| 271820743 | 0.4060 | 0.2036 | `data\unknown_open_set_v2\images\primary\Craugastor_metriosistus\271820743_488972411.jpg` |
| 318466281 | 0.4069 | 0.1288 | `data\unknown_open_set_v2\images\primary\Craugastor_metriosistus\318466281_575573402.jpg` |
| 274604596 | 0.4170 | 0.2056 | `data\unknown_open_set_v2\images\primary\Craugastor_metriosistus\274604596_493634137.jpg` |
| 317407555 | 0.4485 | 0.1152 | `data\unknown_open_set_v2\images\primary\Craugastor_metriosistus\317407555_573547556.jpg` |
| 335327894 | 0.4576 | 0.1065 | `data\unknown_open_set_v2\images\primary\Craugastor_metriosistus\335327894_609147470.jpg` |
| 271820742 | 0.4599 | 0.1544 | `data\unknown_open_set_v2\images\primary\Craugastor_metriosistus\271820742_488972396.jpg` |

_... y 13 casos adicionales — ver `VISUAL_OVERLAP_PAIRS.csv` filtrando por true_species_evaluation_only='Craugastor metriosistus' y predicted_species='Craugastor raniformis'._

### 4. Espadarana prosoblepon (UNKNOWN real) confundida con Hyloscirtus palmeri (KNOWN predicha) — 22 casos

- visual_d1 promedio: 0.5393  |  margin promedio: 0.1413

**Imagenes de referencia de `Hyloscirtus palmeri` (KNOWN, `data cleaned/`):**
- `data cleaned\Hyloscirtus_palmeri\col_obs_100622063_photo_167965706.jpg`
- `data cleaned\Hyloscirtus_palmeri\col_obs_103474082_photo_173188027.jpg`
- `data cleaned\Hyloscirtus_palmeri\col_obs_109757940_photo_185046308.jpg`

**Casos UNKNOWN (`Espadarana prosoblepon`) confundidos con esta especie — hasta 10 ejemplos (de 22 totales, ver CSV para todos):**

| observation_id | visual_d1 | margin | ruta imagen UNKNOWN |
|---|---|---|---|
| 325443502 | 0.4645 | 0.1827 | `data\unknown_open_set_v2\images\primary\Espadarana_prosoblepon\col_obs_325443502_photo_589239418.jpg` |
| 325443439 | 0.4661 | 0.1579 | `data\unknown_open_set_v2\images\primary\Espadarana_prosoblepon\col_obs_325443439_photo_589239322.jpg` |
| 339905927 | 0.4675 | 0.1107 | `data\unknown_open_set_v2\images\primary\Espadarana_prosoblepon\col_obs_339905927_photo_618438261.jpg` |
| 325443502 | 0.4872 | 0.1461 | `data\unknown_open_set_v2\images\primary\Espadarana_prosoblepon\col_obs_325443502_photo_589239418.jpg` |
| 341392040 | 0.4883 | 0.1779 | `data\unknown_open_set_v2\images\primary\Espadarana_prosoblepon\col_obs_341392040_photo_631005699.jpg` |
| 337215651 | 0.4892 | 0.1334 | `data\unknown_open_set_v2\images\primary\Espadarana_prosoblepon\col_obs_337215651_photo_612964150.jpg` |
| 325443502 | 0.5018 | 0.1627 | `data\unknown_open_set_v2\images\primary\Espadarana_prosoblepon\col_obs_325443502_photo_589239418.jpg` |
| 341392040 | 0.5021 | 0.2014 | `data\unknown_open_set_v2\images\primary\Espadarana_prosoblepon\col_obs_341392040_photo_631005699.jpg` |
| 374818721 | 0.5043 | 0.1131 | `data\unknown_open_set_v2\images\primary\Espadarana_prosoblepon\col_obs_374818721_photo_685142834.jpg` |
| 325443502 | 0.5084 | 0.1447 | `data\unknown_open_set_v2\images\primary\Espadarana_prosoblepon\col_obs_325443502_photo_589239418.jpg` |

_... y 12 casos adicionales — ver `VISUAL_OVERLAP_PAIRS.csv` filtrando por true_species_evaluation_only='Espadarana prosoblepon' y predicted_species='Hyloscirtus palmeri'._

### 5. Smilisca phaeota (UNKNOWN real) confundida con Boana lanciformis (KNOWN predicha) — 21 casos

- visual_d1 promedio: 0.6807  |  margin promedio: 0.1387

**Imagenes de referencia de `Boana lanciformis` (KNOWN, `data cleaned/`):**
- `data cleaned\Boana_lanciformis\col_obs_101166914_photo_168915885.jpg`
- `data cleaned\Boana_lanciformis\col_obs_107343534_photo_180518535.jpg`
- `data cleaned\Boana_lanciformis\col_obs_107343534_photo_180518539.jpg`

**Casos UNKNOWN (`Smilisca phaeota`) confundidos con esta especie — hasta 10 ejemplos (de 21 totales, ver CSV para todos):**

| observation_id | visual_d1 | margin | ruta imagen UNKNOWN |
|---|---|---|---|
| 361228692 | 0.5320 | 0.2471 | `data\unknown_open_set_v2\images\primary\Smilisca_phaeota\col_obs_361228692_photo_659221130.jpg` |
| 361067011 | 0.5325 | 0.1193 | `data\unknown_open_set_v2\images\primary\Smilisca_phaeota\col_obs_361067011_photo_658919825.jpg` |
| 399441134 | 0.5368 | 0.1874 | `data\unknown_open_set_v2\images\primary\Smilisca_phaeota\col_obs_399441134_photo_732845605.jpg` |
| 394549119 | 0.5428 | 0.1818 | `data\unknown_open_set_v2\images\primary\Smilisca_phaeota\col_obs_394549119_photo_723326388.jpg` |
| 361228692 | 0.5884 | 0.2265 | `data\unknown_open_set_v2\images\primary\Smilisca_phaeota\col_obs_361228692_photo_659221130.jpg` |
| 361334401 | 0.5952 | 0.1419 | `data\unknown_open_set_v2\images\primary\Smilisca_phaeota\col_obs_361334401_photo_659429641.jpg` |
| 362702619 | 0.6411 | 0.1226 | `data\unknown_open_set_v2\images\primary\Smilisca_phaeota\col_obs_362702619_photo_662007135.jpg` |
| 367480200 | 0.6603 | 0.1043 | `data\unknown_open_set_v2\images\primary\Smilisca_phaeota\col_obs_367480200_photo_671097781.jpg` |
| 367480200 | 0.6654 | 0.1434 | `data\unknown_open_set_v2\images\primary\Smilisca_phaeota\col_obs_367480200_photo_671097781.jpg` |
| 366302669 | 0.7081 | 0.1050 | `data\unknown_open_set_v2\images\primary\Smilisca_phaeota\col_obs_366302669_photo_668855108.jpg` |

_... y 11 casos adicionales — ver `VISUAL_OVERLAP_PAIRS.csv` filtrando por true_species_evaluation_only='Smilisca phaeota' y predicted_species='Boana lanciformis'._

### 6. Leptodactylus fragilis (UNKNOWN real) confundida con Leptodactylus colombiensis (KNOWN predicha) — 17 casos

- visual_d1 promedio: 0.6260  |  margin promedio: 0.2047

**Imagenes de referencia de `Leptodactylus colombiensis` (KNOWN, `data cleaned/`):**
- `data cleaned\Leptodactylus_colombiensis\col_obs_105634128_photo_177277406.jpg`
- `data cleaned\Leptodactylus_colombiensis\col_obs_106637284_photo_179176844.jpg`
- `data cleaned\Leptodactylus_colombiensis\col_obs_110253571_photo_185958530.jpg`

**Casos UNKNOWN (`Leptodactylus fragilis`) confundidos con esta especie — hasta 10 ejemplos (de 17 totales, ver CSV para todos):**

| observation_id | visual_d1 | margin | ruta imagen UNKNOWN |
|---|---|---|---|
| 265845259 | 0.4998 | 0.3144 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_265845259_photo_477579269.jpg` |
| 317536161 | 0.5461 | 0.2142 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_317536161_photo_573791662.jpg` |
| 399441122 | 0.5508 | 0.2386 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_399441122_photo_732845074.jpg` |
| 356722390 | 0.5521 | 0.3424 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_356722390_photo_650551162.jpg` |
| 294595331 | 0.5645 | 0.2550 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_294595331_photo_530265083.jpg` |
| 341392055 | 0.5708 | 0.2741 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_341392055_photo_631003757.jpg` |
| 331268057 | 0.5765 | 0.2285 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_331268057_photo_600909821.jpg` |
| 341158244 | 0.5988 | 0.2314 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_341158244_photo_620989893.jpg` |
| 356722390 | 0.5992 | 0.3280 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_356722390_photo_650551162.jpg` |
| 336277256 | 0.6541 | 0.1331 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_336277256_photo_611052790.jpg` |

_... y 7 casos adicionales — ver `VISUAL_OVERLAP_PAIRS.csv` filtrando por true_species_evaluation_only='Leptodactylus fragilis' y predicted_species='Leptodactylus colombiensis'._

### 7. Leptodactylus fragilis (UNKNOWN real) confundida con Engystomops pustulosus (KNOWN predicha) — 6 casos

- visual_d1 promedio: 0.7168  |  margin promedio: 0.1849

**Imagenes de referencia de `Engystomops pustulosus` (KNOWN, `data cleaned/`):**
- `data cleaned\Engystomops_pustulosus\col_obs_100166991_photo_167142158.jpg`
- `data cleaned\Engystomops_pustulosus\col_obs_100166991_photo_167142177.jpg`
- `data cleaned\Engystomops_pustulosus\col_obs_100166991_photo_167142198.jpg`

**Casos UNKNOWN (`Leptodactylus fragilis`) confundidos con esta especie — hasta 10 ejemplos (de 6 totales, ver CSV para todos):**

| observation_id | visual_d1 | margin | ruta imagen UNKNOWN |
|---|---|---|---|
| 338966350 | 0.6599 | 0.2039 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_338966350_photo_616544366.jpg` |
| 288843271 | 0.6678 | 0.2148 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_288843271_photo_519472876.jpg` |
| 386900741 | 0.6717 | 0.3156 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_386900741_photo_708411257.jpg` |
| 338966350 | 0.7020 | 0.1289 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_338966350_photo_616544366.jpg` |
| 288843271 | 0.7273 | 0.1255 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_288843271_photo_519472876.jpg` |
| 335299924 | 0.8722 | 0.1205 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_335299924_photo_609091855.jpg` |

### 8. Smilisca phaeota (UNKNOWN real) confundida con Dendropsophus molitor (KNOWN predicha) — 5 casos

- visual_d1 promedio: 0.7356  |  margin promedio: 0.1208

**Imagenes de referencia de `Dendropsophus molitor` (KNOWN, `data cleaned/`):**
- `data cleaned\Dendropsophus_molitor\col_obs_356781671_photo_650664705.jpg`
- `data cleaned\Dendropsophus_molitor\col_obs_356781671_photo_650664838.jpg`
- `data cleaned\Dendropsophus_molitor\col_obs_357032600_photo_651143186.jpg`

**Casos UNKNOWN (`Smilisca phaeota`) confundidos con esta especie — hasta 10 ejemplos (de 5 totales, ver CSV para todos):**

| observation_id | visual_d1 | margin | ruta imagen UNKNOWN |
|---|---|---|---|
| 351858887 | 0.7187 | 0.0994 | `data\unknown_open_set_v2\images\primary\Smilisca_phaeota\col_obs_351858887_photo_642152050.jpg` |
| 350409538 | 0.7209 | 0.1815 | `data\unknown_open_set_v2\images\primary\Smilisca_phaeota\col_obs_350409538_photo_639344078.jpg` |
| 350409538 | 0.7331 | 0.1071 | `data\unknown_open_set_v2\images\primary\Smilisca_phaeota\col_obs_350409538_photo_639344078.jpg` |
| 364663506 | 0.7475 | 0.1177 | `data\unknown_open_set_v2\images\primary\Smilisca_phaeota\col_obs_364663506_photo_665727724.jpg` |
| 368076117 | 0.7577 | 0.0984 | `data\unknown_open_set_v2\images\primary\Smilisca_phaeota\col_obs_368076117_photo_672237574.jpg` |

### 9. Leptodactylus fragilis (UNKNOWN real) confundida con Craugastor raniformis (KNOWN predicha) — 5 casos

- visual_d1 promedio: 0.7282  |  margin promedio: 0.1388

**Imagenes de referencia de `Craugastor raniformis` (KNOWN, `data cleaned/`):**
- `data cleaned\Craugastor_raniformis\col_obs_1039482_photo_1303596.jpg`
- `data cleaned\Craugastor_raniformis\col_obs_1039482_photo_1303597.jpg`
- `data cleaned\Craugastor_raniformis\col_obs_105160157_photo_176379597.jpg`

**Casos UNKNOWN (`Leptodactylus fragilis`) confundidos con esta especie — hasta 10 ejemplos (de 5 totales, ver CSV para todos):**

| observation_id | visual_d1 | margin | ruta imagen UNKNOWN |
|---|---|---|---|
| 352434104 | 0.6768 | 0.1424 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_352434104_photo_643257625.jpg` |
| 343232113 | 0.7040 | 0.1183 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_343232113_photo_625185169.jpg` |
| 380903606 | 0.7135 | 0.1291 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_380903606_photo_696906277.jpg` |
| 334403866 | 0.7227 | 0.1598 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_334403866_photo_607268791.jpg` |
| 320271106 | 0.8238 | 0.1440 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_320271106_photo_579033727.jpg` |

### 10. Rhinella marina (UNKNOWN real) confundida con Engystomops pustulosus (KNOWN predicha) — 4 casos

- visual_d1 promedio: 0.6378  |  margin promedio: 0.2562

**Imagenes de referencia de `Engystomops pustulosus` (KNOWN, `data cleaned/`):**
- `data cleaned\Engystomops_pustulosus\col_obs_100166991_photo_167142158.jpg`
- `data cleaned\Engystomops_pustulosus\col_obs_100166991_photo_167142177.jpg`
- `data cleaned\Engystomops_pustulosus\col_obs_100166991_photo_167142198.jpg`

**Casos UNKNOWN (`Rhinella marina`) confundidos con esta especie — hasta 10 ejemplos (de 4 totales, ver CSV para todos):**

| observation_id | visual_d1 | margin | ruta imagen UNKNOWN |
|---|---|---|---|
| 385119922 | 0.5706 | 0.3397 | `data\unknown_open_set_v2\images\primary\Rhinella_marina\col_obs_385119922_photo_705037604.jpg` |
| 385119922 | 0.5715 | 0.3251 | `data\unknown_open_set_v2\images\primary\Rhinella_marina\col_obs_385119922_photo_705037604.jpg` |
| 385119922 | 0.6470 | 0.2284 | `data\unknown_open_set_v2\images\primary\Rhinella_marina\col_obs_385119922_photo_705037604.jpg` |
| 353627520 | 0.7622 | 0.1316 | `data\unknown_open_set_v2\images\primary\Rhinella_marina\col_obs_353627520_photo_645191700.jpg` |

### 11. Smilisca phaeota (UNKNOWN real) confundida con Pithecopus hypochondrialis (KNOWN predicha) — 3 casos

- visual_d1 promedio: 0.7652  |  margin promedio: 0.1070

**Imagenes de referencia de `Pithecopus hypochondrialis` (KNOWN, `data cleaned/`):**
- `data cleaned\Pithecopus_hypochondrialis\col_obs_100613692_photo_167950532.jpg`
- `data cleaned\Pithecopus_hypochondrialis\col_obs_109686002_photo_184908405.jpg`
- `data cleaned\Pithecopus_hypochondrialis\col_obs_109686002_photo_184908475.jpg`

**Casos UNKNOWN (`Smilisca phaeota`) confundidos con esta especie — hasta 10 ejemplos (de 3 totales, ver CSV para todos):**

| observation_id | visual_d1 | margin | ruta imagen UNKNOWN |
|---|---|---|---|
| 362964998 | 0.7517 | 0.1214 | `data\unknown_open_set_v2\images\primary\Smilisca_phaeota\col_obs_362964998_photo_662520381.jpg` |
| 357372696 | 0.7537 | 0.0961 | `data\unknown_open_set_v2\images\primary\Smilisca_phaeota\col_obs_357372696_photo_651811012.jpg` |
| 357372696 | 0.7903 | 0.1033 | `data\unknown_open_set_v2\images\primary\Smilisca_phaeota\col_obs_357372696_photo_651811012.jpg` |

### 12. Craugastor metriosistus (UNKNOWN real) confundida con Pristimantis thectopternus (KNOWN predicha) — 3 casos

- visual_d1 promedio: 0.5505  |  margin promedio: 0.1499

**Imagenes de referencia de `Pristimantis thectopternus` (KNOWN, `data cleaned/`):**
- `data cleaned\Pristimantis_thectopternus\col_obs_182685181_photo_318539801.jpg`
- `data cleaned\Pristimantis_thectopternus\col_obs_189484831_photo_331954220.jpg`
- `data cleaned\Pristimantis_thectopternus\col_obs_189484831_photo_331954290.jpg`

**Casos UNKNOWN (`Craugastor metriosistus`) confundidos con esta especie — hasta 10 ejemplos (de 3 totales, ver CSV para todos):**

| observation_id | visual_d1 | margin | ruta imagen UNKNOWN |
|---|---|---|---|
| 333787226 | 0.4622 | 0.1548 | `data\unknown_open_set_v2\images\primary\Craugastor_metriosistus\333787226_606011094.jpg` |
| 293893104 | 0.5778 | 0.1933 | `data\unknown_open_set_v2\images\primary\Craugastor_metriosistus\293893104_528945355.jpg` |
| 348596771 | 0.6116 | 0.1016 | `data\unknown_open_set_v2\images\primary\Craugastor_metriosistus\348596771_635301898.jpg` |

### 13. Leptodactylus fragilis (UNKNOWN real) confundida con Scinax ruber (KNOWN predicha) — 2 casos

- visual_d1 promedio: 0.7795  |  margin promedio: 0.1244

**Imagenes de referencia de `Scinax ruber` (KNOWN, `data cleaned/`):**
- `data cleaned\Scinax_ruber\col_obs_100616333_photo_167955273.jpg`
- `data cleaned\Scinax_ruber\col_obs_101744595_photo_169952566.jpg`
- `data cleaned\Scinax_ruber\col_obs_10396065_photo_14432671.jpg`

**Casos UNKNOWN (`Leptodactylus fragilis`) confundidos con esta especie — hasta 10 ejemplos (de 2 totales, ver CSV para todos):**

| observation_id | visual_d1 | margin | ruta imagen UNKNOWN |
|---|---|---|---|
| 265941053 | 0.7721 | 0.1026 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_265941053_photo_477773364.jpg` |
| 345778928 | 0.7870 | 0.1461 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_345778928_photo_630203280.jpg` |

### 14. Espadarana prosoblepon (UNKNOWN real) confundida con Boana cinerascens (KNOWN predicha) — 1 casos

- visual_d1 promedio: 0.6265  |  margin promedio: 0.0998

**Imagenes de referencia de `Boana cinerascens` (KNOWN, `data cleaned/`):**
- `data cleaned\Boana_cinerascens\col_obs_103034322_photo_172357955.jpg`
- `data cleaned\Boana_cinerascens\col_obs_115160934_photo_194392587.jpg`
- `data cleaned\Boana_cinerascens\col_obs_115160934_photo_194392638.jpg`

**Casos UNKNOWN (`Espadarana prosoblepon`) confundidos con esta especie — hasta 10 ejemplos (de 1 totales, ver CSV para todos):**

| observation_id | visual_d1 | margin | ruta imagen UNKNOWN |
|---|---|---|---|
| 392282553 | 0.6265 | 0.0998 | `data\unknown_open_set_v2\images\primary\Espadarana_prosoblepon\col_obs_392282553_photo_718889529.jpg` |

### 15. Leptodactylus fragilis (UNKNOWN real) confundida con Rheobates palmatus (KNOWN predicha) — 1 casos

- visual_d1 promedio: 0.6348  |  margin promedio: 0.1590

**Imagenes de referencia de `Rheobates palmatus` (KNOWN, `data cleaned/`):**
- `data cleaned\Rheobates_palmatus\col_obs_10023223_photo_13784273.jpg`
- `data cleaned\Rheobates_palmatus\col_obs_10023223_photo_13784374.jpg`
- `data cleaned\Rheobates_palmatus\col_obs_100613535_photo_167950161.jpg`

**Casos UNKNOWN (`Leptodactylus fragilis`) confundidos con esta especie — hasta 10 ejemplos (de 1 totales, ver CSV para todos):**

| observation_id | visual_d1 | margin | ruta imagen UNKNOWN |
|---|---|---|---|
| 333015085 | 0.6348 | 0.1590 | `data\unknown_open_set_v2\images\primary\Leptodactylus_fragilis\col_obs_333015085_photo_604495826.jpg` |

## Metodologia

1. Se agruparon los 228 registros de `fase23a_false_accepts_context_frozen.json` por par (true_species_evaluation_only, predicted_species) y se conto frecuencia, promedio de visual_d1 y promedio de margin.
2. Para cada registro, se resolvio la ruta de la imagen UNKNOWN buscando el `observation_id` en los nombres de archivo dentro de `data/unknown_open_set_v2/images/primary/<especie_true_con_guion_bajo>/`. Se soportaron dos patrones de nombre observados: `col_obs_<obsid>_photo_<photoid>.jpg` y `<obsid>_<photoid>.jpg` (usado por ejemplo en `Craugastor_metriosistus/` y `Scinax_rostratus/`).
3. Para cada especie predicha (KNOWN), se tomaron hasta 3 imagenes de ejemplo (orden alfabetico de archivo) de `data cleaned/<especie_predicha_con_guion_bajo>/` como referencia visual.
4. Resultado: 228/228 imagenes UNKNOWN resueltas correctamente (100%), 228/228 especies KNOWN con al menos 1 imagen de referencia resuelta.

Ver `VISUAL_OVERLAP_PAIRS.csv` para las 228 filas completas enriquecidas con `unknown_image_path` y `known_reference_examples`.
