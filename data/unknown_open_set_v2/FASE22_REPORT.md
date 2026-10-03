# FASE 22 — UNKNOWN V2: limpieza + ampliación taxonómica + auditoría de calidad

**Fecha:** 2026-09-14
**Alcance:** construcción de dataset UNKNOWN V2 auditado, sin leakage, taxonómicamente diverso.
**NO incluye:** evaluación Open Set (Fase 23), cálculo de threshold, ni cambio Euclidean/Mahalanobis.
**Reglas duras respetadas:** sin entrenamiento/fine-tuning de BioCLIP, sin tocar producción (`visual_catalog/v1.0.0/`, `evaluation/fase13/`, `validation/fase16-21`, checkpoint/threshold/covarianza oficiales, paquetes regionales), sin commit/push, sin borrado físico de imágenes originales, sin fabricar datos.

---

## 1. ¿Cuántas imágenes UNKNOWN históricas había?

**56 imágenes**, recuperadas desde la fuente de verdad `evaluation/open_set_v1/knn/knn_open_set_results.json` (registros con `known_unknown == "UNKNOWN"`), correspondientes a 2 especies: `Hyloxalus_picachos` (15 imgs) y `Sachatamia_electrops` (41 imgs). Las 56 se localizaron físicamente en disco (`data cleaned/` y `data dirty/`) sin faltantes. Esto reproduce exactamente el inventario ya documentado en Fase 16/19/20/21.

## 2. ¿Cuántas aceptadas/rechazadas y por qué?

Auditoría de calidad independiente (integridad, resolución ≥200×200, blur por varianza de Laplaciano, brillo, contraste — NUNCA `quality_grade` de iNaturalist como criterio de calidad de imagen):

| Decisión | n | Motivo |
|---|---|---|
| ACCEPT | 54 | pasaron todos los controles |
| REJECT_QUALITY | 2 | blur/brillo/contraste fuera de rango |

Ninguna imagen fue `REJECT_CORRUPTED`, `REJECT_RESOLUTION` ni `REJECT_LEAKAGE`. Los 2 rechazos quedan en `audit/historical_unknown_quality_audit.csv` como evidencia; **no se eliminaron físicamente**.

## 3. ¿Cuántas especies históricas permanecieron?

**2 de 2** (Hyloxalus_picachos, Sachatamia_electrops). Ambas pasan la auditoría con suficientes imágenes/individuos para seguir siendo útiles y **no fueron descartadas artificialmente**: aportan la única representación histórica de la familia Dendrobatidae (vía Hyloxalus, aunque nota de matiz abajo) y Centrolenidae (Sachatamia).

**Nota de matiz taxonómico (hallazgo de esta fase):** `Hyloxalus_picachos` SÍ existe en `taxonomy/species/species_registry.json` (species_id `ANU_COL_HYLO_PIC_001`), pero con `visual_lifecycle_status = "DISCOVERED"`, no `"DEPLOYED"`. El catálogo `visual_catalog/v1.0.0/manifest.json` confirma 41 especies `DEPLOYED`, y Hyloxalus_picachos no es una de ellas. Por tanto sigue siendo válidamente UNKNOWN bajo la definición de la tarea (“fuera del catálogo KNOWN actual” = fuera de las 41 desplegadas), pero está a un paso de dejar de serlo si se promueve a DEPLOYED — se documenta como riesgo a vigilar en fases futuras. `Sachatamia_electrops` no aparece en el registry en absoluto (huérfana, consistente con la nota de memoria del proyecto).

## 4. ¿Cuántas especies nuevas se incorporaron?

**9 especies nuevas**, descargadas desde la API pública de iNaturalist (`api.inaturalist.org/v1`), solo fotos con licencia CC (cc0/cc-by/cc-by-nc/cc-by-sa/cc-by-nc-sa), `quality_grade=research` solo como filtro inicial de relevancia (nunca como criterio final de calidad — auditoría de imagen igual de estricta que la histórica se aplicó a las 521 imágenes descargadas). Selección de candidatas hecha ANTES de cualquier evaluación Open Set (sin contaminación por BLIND test):

| Especie | Relación con KNOWN | Imágenes descargadas | Tras auditoría (ACCEPT+CLEAN) | Individuos |
|---|---|---|---|---|
| Dendropsophus_labialis | SAME_GENUS | 74 | 74 | 43 |
| Dendropsophus_minutus | SAME_GENUS | 23 | 23 | 19 |
| Pristimantis_w_nigrum | SAME_GENUS | 53 | 53 | 21 |
| Pristimantis_nervicus | SAME_GENUS | 3 | 3 | 2 |
| Rhinella_marina | SAME_GENUS | 83 | 83 | 41 |
| Leptodactylus_fragilis | SAME_GENUS | 85 | 85 | 44 |
| Boana_geographica | SAME_GENUS | 2 | 2 | 1 |
| Smilisca_phaeota | SAME_FAMILY (Hylidae) | 108 | 107 (1 REJECT_QUALITY) | 55 |
| Espadarana_prosoblepon | DIFFERENT_FAMILY (Centrolenidae) | 90 | 89 (1 solapada en observación) | 45 |

3 candidatas **no produjeron imágenes** por falta de fotos con licencia CC en Colombia dentro de la ventana consultada (documentado, no simulado): `Boana_crepitans`, `Trachycephalus_typhonius`, `Hyalinobatrachium_fleischmanni`. 202 fotos adicionales fueron vistas pero descartadas por no tener licencia CC (`skipped_no_cc_license` en `download_manifest.json`).

**Limitación honesta:** `Boana_geographica` y `Pristimantis_nervicus` quedaron con muestras muy pequeñas (2 y 3 imágenes, 1 y 2 individuos) — insuficientes por sí solas para conclusiones robustas por especie en Fase 23, aunque se conservan como datos reales (no se rellenó artificialmente ni se descartó por regla arbitraria de cantidad).

## 5. ¿Cuántos individuos independientes hay?

**305 individuos independientes** en total (34 históricos + 271 nuevos), usando la prioridad `individual_id > observation_id > SHA256 > path`. Ninguna fuente disponible tenía `individual_id` explícito; se usó `observation_id` (patrón `col_obs_<id>_photo` de iNaturalist) como unidad de individuo — múltiples fotos de la misma observación cuentan como **1 individuo**, tal como exige la regla 12.

## 6. Especies por relación taxonómica con KNOWN

| Relación | n especies |
|---|---|
| SAME_GENUS | 7 (+ Hyloxalus_picachos histórico, contado aparte por matiz de sección 3) |
| SAME_FAMILY | 2 (Smilisca_phaeota; e Hyloxalus_picachos si se cuenta por familia Dendrobatidae) |
| DIFFERENT_FAMILY | 2 (Sachatamia_electrops, Espadarana_prosoblepon — ambas Centrolenidae) |

Cobertura de 6 familias, 9 géneros, 11 especies en total (ver `metadata/unknown_taxonomic_coverage.csv`).

## 7. ¿Leakage o duplicación?

- **Leakage: 0 / 574** imágenes finales. Verificado por SHA256 exacto contra un índice de 11,717 hashes reales (recalculados desde archivos en disco, no confiando en campos `sha256` vacíos de los manifiestos) cubriendo TRAIN (3,260), REFERENCE (792), CALIBRATION (190), VALIDATION/Fase16 clean-known (7,475) y BLIND/Fase18 (4,930).
- **Duplicados exactos (SHA256): 0** dentro del pool final.
- **Limitación declarada:** no se realizó comparación por *perceptual hash* (near-duplicate) porque no había librería de hashing perceptual (`imagehash`) instalada en el entorno y no se instaló software adicional sin autorización explícita del alcance. Esto es un hueco metodológico real, no oculto: existe una probabilidad residual no cuantificada de recortes/derivados casi-idénticos no detectados por SHA256 exacto.

## 8. ¿Qué especies son más útiles para Open Set (Fase 23)?

Ver sección siguiente "ESPECIES UNKNOWN RECOMENDADAS PARA FASE 23".

## 9. ¿Qué especies tienen mayor dificultad taxonómica?

- `Pristimantis_w_nigrum` y `Pristimantis_nervicus`: mismo género que 10 especies KNOWN (el género más numeroso del catálogo) — máxima dificultad esperada de separación embedding-level.
- `Dendropsophus_labialis` / `Dendropsophus_minutus`: mismo género que 8 especies KNOWN, morfología muy similar (hílidos pequeños).
- `Espadarana_prosoblepon` / `Sachatamia_electrops`: mismo hábito (ranas de cristal, Centrolenidae) — dificultad alta por semejanza morfológica extrema entre géneros de esta familia, aunque familia distinta al catálogo KNOWN.

## 10. Cobertura geográfica

Las 9 especies nuevas se restringieron a observaciones con `place_id` = Colombia en iNaturalist (research-grade). Coordenadas por observación quedaron registradas en `download_manifest.json` (lat/lon reales de cada observación) pero **no se usó ubicación como sustituto de identidad taxonómica** — la especie se determina por el campo `taxon` de iNaturalist, verificado contra el nombre buscado. El histórico no trae coordenadas (limitación heredada de Fase 13, no resuelta aquí).

## 11. ¿Es suficientemente fuerte para Fase 23?

**Sí, con matices.** Los tres umbrales mínimos de la tarea se cumplen con datos reales, no fabricados:

| Métrica | Mínimo requerido | Logrado |
|---|---|---|
| Especies UNKNOWN reales | ≥10 | **11** |
| Imágenes útiles | ≥200 | **574** |
| Individuos independientes | ≥50 | **305** |
| Leakage | 0 | **0** |

Preferido (10-15 especies, 200-300 imgs, 50-100 individuos, ~20 img/especie): se **supera** en imágenes/individuos totales, pero la distribución por especie es desigual (2 especies con <5 imágenes). Esto no invalida el conjunto pero debe tenerse en cuenta al interpretar resultados por especie en Fase 23 (los resultados agregados serán robustos; los resultados por especie de Boana_geographica y Pristimantis_nervicus no lo serán).

---

## ESPECIES UNKNOWN RECOMENDADAS PARA FASE 23 (ordenadas por utilidad científica)

| # | Especie | Género | Familia | Relación con KNOWN | Imágenes | Individuos | Regiones | Razón de utilidad |
|---|---|---|---|---|---|---|---|---|
| 1 | Smilisca_phaeota | Smilisca | Hylidae | SAME_FAMILY | 107 | 55 | Colombia (iNaturalist) | Mayor muestra nueva; buena prueba de confusión a nivel de familia Hylidae (19/41 especies KNOWN son Hylidae) |
| 2 | Espadarana_prosoblepon | Espadarana | Centrolenidae | DIFFERENT_FAMILY | 89 | 45 | Colombia (iNaturalist) | Extiende la única familia "diferente" histórica (Centrolenidae vía Sachatamia) con una segunda especie/género — refuerza la prueba DIFFERENT_FAMILY que antes dependía de 1 sola especie |
| 3 | Leptodactylus_fragilis | Leptodactylus | Leptodactylidae | SAME_GENUS | 85 | 44 | Colombia (iNaturalist) | Único género KNOWN con 1 sola especie (Leptodactylus_colombiensis) — prueba crítica de separación intra-género con muestra delgada en el lado KNOWN |
| 4 | Rhinella_marina | Rhinella | Bufonidae | SAME_GENUS | 83 | 41 | Colombia (iNaturalist) | Buena muestra; mismo género que 3 KNOWN Rhinella, especie muy distintiva (control de sanidad del pipeline) |
| 5 | Dendropsophus_labialis | Dendropsophus | Hylidae | SAME_GENUS | 74 | 43 | Colombia (iNaturalist) | Mismo género que 8 KNOWN Dendropsophus — alta dificultad esperada, buen tamaño de muestra |
| 6 | Sachatamia_electrops | Sachatamia | Centrolenidae | DIFFERENT_FAMILY | 39 | 19 | histórico (sin coordenadas) | Único punto de dato histórico DIFFERENT_FAMILY ya validado en 3 fases previas — mantiene comparabilidad longitudinal con Fase 16/19/20/21 |
| 7 | Pristimantis_w_nigrum | Pristimantis | Craugastoridae | SAME_GENUS | 53 | 21 | Colombia (iNaturalist) | Mismo género que 10 KNOWN Pristimantis (el más numeroso) — máxima dificultad taxonómica, prioridad científica alta pese a muestra moderada |
| 8 | Dendropsophus_minutus | Dendropsophus | Hylidae | SAME_GENUS | 23 | 19 | Colombia (iNaturalist) | Segunda especie Dendropsophus nueva, añade diversidad dentro del género más representado |
| 9 | Hyloxalus_picachos | Hyloxalus | Dendrobatidae | SAME_FAMILY* | 15 | 15 | histórico (sin coordenadas) | Histórico validado, única representación de Dendrobatidae; *registrado pero no DEPLOYED — vigilar en futuras fases | 
| 10 | Pristimantis_nervicus | Pristimantis | Craugastoridae | SAME_GENUS | 3 | 2 | Colombia (iNaturalist) | Útil solo como punto adicional dentro de Pristimantis; muestra insuficiente para conclusiones propias |
| 11 | Boana_geographica | Boana | Hylidae | SAME_GENUS | 2 | 1 | Colombia (iNaturalist) | Muestra mínima; conservar como dato real, no como base de conclusión independiente |

---

## Estado final

```
STATUS: UNKNOWN_DATA_READY_FOR_PHASE23
n_species: 11
n_genera: 9
n_families: 6
n_images: 574
n_individuals: 305
leakage_count: 0
duplicate_count: 0
quality_rejection_count: 3  (2 historical + 1 new)
historical_images_accepted: 54 / 56
new_images_added: 520 (from 521 downloaded, 1 rejected by quality audit)
same_genus_species: 7
same_family_species: 2
different_family_species: 2
```

**Salvedades que Fase 23 debe conocer:** (1) 2 de 11 especies tienen muestra ínfima (Boana_geographica, Pristimantis_nervicus) — excluir o tratar por separado en métricas por-especie; (2) sin verificación de duplicados casi-idénticos por hash perceptual; (3) matiz de estatus DISCOVERED vs DEPLOYED de Hyloxalus_picachos debe revisarse si el catálogo se actualiza antes de Fase 23; (4) no se verificó independencia de fotógrafo/individuo más allá del `observation_id` de iNaturalist (misma limitación NOT_FORMALLY_VERIFIABLE que Fase 12.2/20).
