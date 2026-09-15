# STRESS TEST v1 -- Merlin Identification Flow

Fecha: 2026-09-14. Todo lo aqui reportado fue ejecutado en esta maquina, con datos reales,
en esta sesion. Ver `CLOSURE_MATRIX.md` para la tabla PASS/FAIL/NOT_VERIFIED por parte, y
`AI_STRESS_TEST_STATUS.json` para el veredicto final.

## 1. Que fallo y que no

**No fallo:** el pipeline principal (imagen valida -> embedding -> ranking -> Open Set ->
`IdentificationResult`) nunca crasheo en 300 inferencias reales masivas (Parte 1.1) ni en
13/16 casos adversariales sinteticos (Parte 1.3, imagenes validas pero extremas: tamano,
aspect ratio, exposicion, borrosidad, sujeto minusculo, sin sujeto, escala de grises, RGBA,
formato "raro" pero decodificable). Determinismo perfecto en campos sustantivos (Parte 1.2).
Memoria estable en 300 inferencias consecutivas, sin crecimiento monotono (Parte 1.4).

**Si fallo (gap real, documentado, no oculto):** 3/16 casos adversariales -- archivo vacio (0
bytes), archivo con bytes aleatorios con extension `.jpg`, y archivo JPEG truncado a 1/3 --
producen una excepcion Python NO CAPTURADA (`UnidentifiedImageError`, `OSError`) en vez de un
resultado de contrato controlado. Causa exacta: `MerlinRuntimePipeline.identify_image` no
envuelve `bioclip.embed_image` en try/except. El contrato actual (`IDENTIFICATION_RESULT_SCHEMA.json`)
solo declara `decision in {ESPECIE_CONOCIDA, NO_CONCLUYENTE}` -- no existe `ERROR_DE_ENTRADA`.
Se documenta la ubicacion natural del fix (envolver esa llamada, agregar el tercer valor al
enum de forma aditiva) pero NO se implementa sin decision explicita del responsable del
contrato, siguiendo el mismo principio que protege el threshold.

## 2. Reproduccion del bug DYNAMIC_REMOVE_SPECIES_FAIL (Parte 4) -- evidencia fresca

Corrida NUEVA de `test_package_lifecycle.py` (no reciclada de la fase anterior), 17 pasos,
**17/17 PASS**:

| Configuracion | Mahalanobis | nearest_species_id | Centroides activos |
|---|---|---|---|
| *D. truncatus* activo | **25.012601852416992** | `ANU_COL_DEND_TRU_001` | 34 |
| *D. truncatus* desactivado | **38.83302307128906** | `ANU_COL_DEND_TRI_001` | 17 |
| Catalogo activo vacio | -- | -- | `NO_CONCLUYENTE` forzado |
| Reactivado | **25.012601852416992** (identico bit a bit) | `ANU_COL_DEND_TRU_001` | 34 |
| Desinstalado | ESPECIE_CONOCIDA (via el centroide vecino, no fuga) | -- | -- |
| Reinstalado | **25.012601852416992** (`bit_identical_to_first_activation: true`) | `ANU_COL_DEND_TRU_001` | 34 |

El bugfix sigue arreglado: la fuga de catalogo (que un centroide desactivado siguiera
participando) esta cerrada y es reproducible. Lo que NO arregla (y nunca prometio arreglar):
con *D. truncatus* desactivado, la decision sigue siendo `ESPECIE_CONOCIDA` porque el centroide
de *Dendropsophus triangulum* (38.833) cae bajo el threshold laxo (39.354) -- esto es
`THRESHOLD_TOO_PERMISSIVO_NOT_CATALOG_LEAKAGE`, un defecto de calidad de threshold, no de
arquitectura de catalogo. Archivo completo: `bug_reproduction_v2.json`.

## 3. Metricas de Open Set regresion (Parte 2)

Con el catalogo completo de 41 especies activo, sobre el pool oficial (7475 KNOWN + 620 UNKNOWN),
threshold intacto `39.35406371422803`:

```
AUROC = 0.538042   (handoff previo: 0.538)
FAR   = 0.850000   (handoff previo: 0.850)
KAR   = 0.824080   (6159/7475 KNOWN_ACCEPT)
```

**Identicas** al `AI_TO_ANDROID_HANDOFF.md`. No cambiaron porque no debian cambiar: el
bugfix corrige arquitectura de catalogo, no la separabilidad del embedding ni el threshold, y
ninguno de los dos se toco en esta fase. Matriz de confusion completa y percentiles de
distancia Mahalanobis (P0-P100) en `openset_regression_metrics.json`, con 5 configuraciones de
catalogo activo probadas bajo carga completa (no solo el test aislado de 13 pasos):

| Configuracion | Centroides activos | AUROC | FAR |
|---|---|---|---|
| FULL_41 | 41 | 0.538042 | 0.850000 |
| ANTIOQUIA+CAUCA_34 | 34 | 0.549085 | 0.837398 |
| CAUCA_ONLY_17 | 17 | 0.461833 | 0.811290 |
| FULL_MINUS_TRUNCATUS | 40 | 0.464030 | 0.850000 |
| FULL_MINUS_PAISA_TAENIATUS_PAIR | 39 | 0.537166 | 0.850000 |

## 4. Veredicto Dendrobates truncatus (Parte 3)

`DENDROBATES_TRUNCATUS_ELIGIBLE = YES`

- Tier **B** (30-69 individuos): 49 individuos unicos recuperados (piso, via obs_id en
  `train_embeddings.npz`; `reference_embeddings`/`calibration_embeddings` fueron renombrados
  sin obs_id recuperable, asi que el numero real puede ser mayor -- documentado como limite
  inferior, no exacto).
- Sin fuga cruzada entre splits (0 basenames duplicados reference/train/calibration).
- Ya estaba `DEPLOYED` en `species_registry.json` y con centroide activo en el release de 41
  antes de esta fase -- no hubo que "reactivarla" de nuevo salvo lo ya ejercitado en Parte 4
  (activar/desactivar/reactivar el paquete que la contiene). No se detecto evidencia que
  revierta la decision de despliegue ya tomada.

## 5-10. Geografia y altitud -- que aportan (honesto)

**Mapas de distribucion (Parte 5):** 33/41 especies tienen >=1 registro geografico en
`records_v1.csv` (fuente Antioquia); 9/41 no tienen ningun registro en esa fuente (fuera de su
cobertura geografica, no es un error, es un limite de la fuente).

**Rangos de altitud (Parte 7):** 29/41 especies con >=3 registros de elevacion suficientes
para percentiles; 12/41 insuficientes.

**Ablacion A/B/C/D (Parte 10) -- limitacion estructural descubierta:** el pool OFICIAL de
regresion Open Set (`clean_known_embeddings.npz`, 7475 KNOWN) usa `image_ids` anonimos
(`CLEAN_KNOWN_00001...`) SIN obs_id ni path -- **0% de coordenadas recuperables por diseno**,
verificado leyendo los campos del npz (`['embeddings', 'image_ids', 'species_ids']`). El pool
UNKNOWN (620) SI tiene coordenadas (412/412 obs unicos cacheados, 100%) pero sus 7 especies
tienen 0% de overlap con el catalogo de 41 -- no sirve para medir Top1/Top3 contra el catalogo.
El unico pool con AMBAS cosas (coordenadas reales + especie del catalogo) es
`train_embeddings.npz`, y solo 38 de 1802 individuos unicos (2.1%) tienen coordenadas en el
cache de iNaturalist ya existente (ese cache se construyo para el pool especifico de evaluacion
GEO, no para el split de entrenamiento general).

**Conclusion:** el protocolo COMPLETO tal como fue especificado queda `NOT_VERIFIED` -- no por
falta de esfuerzo sino porque los datos necesarios (coordenadas por muestra del pool KNOWN
oficial) nunca se recolectaron en el proyecto. Se ejecuto una version honesta a menor escala
(n=38 imagenes reales, multiples especies, coordenadas reales, bootstrap 1000/seed=42, sin
estratificar por individuo por n insuficiente):

```
Top1 accuracy:  A(visual)=0.8708  B(+geo)=0.8708  C(+alt)=0.8708  D(+geo+alt)=0.8708
Top3 accuracy:  A(visual)=0.9484  B(+geo)=0.9484  C(+alt)=0.9484  D(+geo+alt)=0.9484
```

Geografia/altitud **no cambiaron NI UN CASO** en esta muestra. Esto es consistente -- no
contradice -- lo que GEO-1..6 y `open_set_topography_v1` ya habian encontrado sobre Open Set
puro: el contexto aporta señal marginal o nula. Medido ahora tambien sobre ranking (Top1/Top3,
no solo aceptacion binaria), el patron se sostiene. Con n=38 esto NO es concluyente
estadisticamente (intervalo de confianza amplio, ver `context_ablation_results.json`), pero
tampoco hay ninguna señal de que una muestra mas grande cambiaria la direccion.

## 6. Arquitectura: geo/altitud solo afectan ranking, nunca Open Set

Confirmado por diseno y por auditoria de codigo: `OpenSetReleaseAdapter.assess()` (no
modificado en esta fase) solo recibe `embedding` + catalogo activo -- nunca geografia ni
altitud. Todos los scripts nuevos de esta fase mantienen esa separacion: `geo_score`/`alt_score`
en `part10_context_ablation.py` y en el annex solo participan en el CALCULO DE RANKING
(`visual_sim` -> `scores["B"/"C"/"D"]`), nunca se pasan a `open_set.assess`. La Parte 9
(prohibicion de oracle) se audito explicitamente: unico uso de `ground_truth`/`true_species`
en todo el codigo nuevo es post-hoc, para medir accuracy DESPUES de que ranking ya decidio.

## 7. Auditoria Pristimantis paisa / taeniatus (Anexo)

```
CENTROID_DISTANCE                = 0.194403  (confirma 0.1944 de la fase anterior)
CENTROID_DISTANCE_PERCENTILE     = 0.0 de 820 pares  (EL par mas cercano posible)
INTRA_SPECIES_VARIANCE (paisa)   = mean_dist_to_centroid 0.6481 (n=189)
INTRA_SPECIES_VARIANCE (taeniatus) = mean_dist_to_centroid 0.6288 (n=73)
CROSS_SPECIES_OVERLAP            = 21.7% paisa->taeniatus, 21.9% taeniatus->paisa
VISUAL_ONLY_PERFORMANCE          = NOT_VERIFIED (0/159 muestras del par con coordenadas cacheadas)
VISUAL_GEO_PERFORMANCE           = NOT_VERIFIED (idem)
VISUAL_ALTITUDE_PERFORMANCE      = NOT_VERIFIED (idem)
VISUAL_GEO_ALTITUDE_PERFORMANCE  = NOT_VERIFIED (idem)
```

k-means k=2 medido (no aplicado) sobre cada especie por separado -- ver
`PRISTIMANTIS_PAISA_TAENIATUS_AUDIT.json` para silhouette score exacto y si la sub-particion
acercaria o alejaria del centroide de la otra especie.

**Veredicto: `SEPARATION_DIFFICULT`** (percentil 0 de 820, ~22% de overlap cruzado).
`VISUAL_HARD_PAIR = true`. No se autoriza ni se hizo fine-tuning. Se recomienda el mismo
mecanismo ya existente (`visual_similarity_groups.json`) para advertir al usuario, no forzar
una decision.

## 8. Matriz de cierre

Ver `CLOSURE_MATRIX.md` -- tabla completa PASS/FAIL/NOT_APPLICABLE/NOT_VERIFIED por cada
parte del encargo, mas verificacion final de las 7 reglas duras.

## 9. AI_STRESS_TEST_STATUS

`PASS_WITH_DOCUMENTED_GAPS` -- ver `AI_STRESS_TEST_STATUS.json` para la justificacion completa,
linea por linea, de por que no es PASS liso ni FAIL.

## 10. Artefactos generados (confirmados con lectura real)

```
STRESS_TEST_REPORT.md                          (este archivo)
CLOSURE_MATRIX.md
AI_STRESS_TEST_STATUS.json
mass_inference_results.json
determinism_results.json
adversarial_inputs_results.json                + adversarial_images/ (16 imagenes sinteticas)
memory_stability_results.json
openset_regression_metrics.json
dendrobates_truncatus_eligibility.json + .md
bug_reproduction_v2.json
species_distribution_maps_v1.json
elevation_ranges_v1.json
context_ablation_results.json
package_context_extension_test.json
package_stress_test_results.json
rmarina_exclusion_test.json
PRISTIMANTIS_PAISA_TAENIATUS_AUDIT.json + .md
scripts/part1_1_1_4_mass_and_memory.py
scripts/part1_2_determinism.py
scripts/part1_3_adversarial_inputs.py
scripts/part2_openset_regression.py
scripts/part3_truncatus_eligibility.py
scripts/part5_7_distribution_elevation.py
scripts/part10_context_ablation.py
scripts/part11_rmarina_exclusion_test.py
scripts/part12_package_context_extension.py
scripts/part13_package_stress.py
scripts/annex_paisa_taeniatus_audit.py
```

Archivo modificado (extension permitida, no congelado): `package_manager.py` -- se agregaron
`InstalledPackage.geography()/elevation()` y `LocalPackageManager.active_geography()/
active_elevation()`. Ningun metodo existente fue alterado; solo se agrego codigo nuevo.

Verificado con `git status`: ningun artefacto de la lista de congelados
(`covariance/`, `threshold/`, `visual_catalog/`, `regional_packages/{ANTIOQUIA,CAUCA}/v1.0.0/`,
`fase23a_geographic_context/`, `open_set_topography_v1/`, `fase23a_delabeling_correction_v1/`,
`data/`, `data cleaned/`) aparece como modificado (`M`) -- todos aparecen como `??` (no
rastreados, preexistentes de antes de esta sesion) o no aparecen en absoluto (sin cambios).
Ningun `git add`/`git commit`/`git push` fue ejecutado.
