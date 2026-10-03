# FASE 23A — Contexto Geográfico en Open Set (Diagnóstico)

Fecha: 2026-09-14. Seed: 42. NO se modificó el encoder, embeddings congelados, ni los artefactos de Fase 23A/16/18.

## Estado declarado: GEOGRAPHY_MARGINAL (ver Sección 8)

## 0. Resumen de lo ejecutado
- Fase 0: recuperación real vía API pública de iNaturalist de 4466 observation_id únicos (620 imágenes UNKNOWN + 7475−44 imágenes KNOWN con observation_id). Cobertura: 4466/4466 encontradas, 4466/4466 con coordenadas, **0/4466 con elevación directa del campo `elevation` de la API** (reportado honestamente, no se sustituyó por DEM).
- Fase 1: asignación de zona vía celda 0.25° (`row=round(lat/0.25)`, `col=round(lon/0.25)`) contra `cell_zone_map_v1.csv`. Solo 262/620 (42.3%) UNKNOWN y 2763/7475 (37.0%) KNOWN caen dentro de una celda de Antioquia con zona asignada — el resto recibe `zone=None` y score geográfico neutro (no se descartaron del dataset).
- Fase 2: prior reutilizado literalmente de `prior_zone_taxon_v1.csv` (α=2.0, K=291, smoothing `(N+α)/(N(z)+αK)`, nunca P=0). **Chequeo anti-contaminación obligatorio: 1214/4466 (27.2%) de los observation_id evaluados también son registros fuente del prior** (`records_v1.csv`, source=inaturalist). Por regla del protocolo esto marca todo el ejercicio como `GEOGRAPHIC_PRIOR_DIAGNOSTIC`, no como validación limpia independiente.
- Fase 3: `visual_score` = distancia euclidiana mínima a centroide KNOWN (método ganador euclidean_raw de Fase 23A, recalculado desde los embeddings congelados). `geographic_score` = P(especie_top1_visual | zona) del prior; sin zona → score neutro = 1/K. `combined_score` = suma ponderada de versiones min-max normalizadas en [0,1]: `(1-w)*visual_norm + w*(1-geo_prob_norm)`.
- Fase 4/5: barrido de pesos 0.0→0.5, AUROC/AUPRC/FAR/FRR/BalAcc/threshold con bootstrap estratificado por individuo (1000 iter, seed 42). No existe split de calibración independiente con muestras UNKNOWN (mismo problema documentado en `fase23a_open_set_automatic/reproducibility/anomalies.json`), así que **todo el barrido de pesos es exploratorio**, no una selección ciega de hiperparámetro.
- Fase 6: subgrupos mismo género vs género distinto. Zona/elevación: cobertura insuficiente para un análisis robusto (ver limitaciones).
- Fase 7: ablation A (visual solo) / B (geografía sola) / C (combinado, mejor peso). D (regiones morfológicas) no ejecutado, como indica el protocolo.
- Fase 8: 308 casos de 8095 muestras cambiaron de decisión (KNOWN↔UNKNOWN) entre baseline visual y combinado con w=0.5; 15 casos de ejemplo en `threshold_crossing_cases.json`.
- Fase 9: no implementada (mapeo a triple estado); documentada conceptualmente abajo.

## 1. CAVEAT METODOLÓGICO CRÍTICO — no reproducción exacta del baseline congelado
Los scripts exactos que produjeron `method_comparison.csv` (AUROC=0.57329 para euclidean_raw) corrían desde el scratchpad de una sesión anterior y ya no existen en el repo (solo quedan resúmenes en CSV/JSON, documentado en `reproducibility/config.json`). Esta sesión recalculó scores desde cero con un protocolo razonable pero no idéntico:
- KNOWN score = distancia leave-one-out al centroide de su propia especie (evita fuga trivial de distancia cero).
- UNKNOWN score = distancia mínima a los 41 centroides KNOWN de muestra completa.

Resultado: **AUROC visual-solo reproducido en esta sesión = 0.61812** [IC95% 0.5885–0.6435], **vs. el baseline oficial congelado = 0.57329**. La diferencia (+0.045) no se explica completamente y probablemente proviene de diferencias en cómo se construyeron los centroides KNOWN en el pipeline original (p.ej. particiones REFERENCE/TRAIN de Fase 13 vs. `clean_known_embeddings.npz` completo usado aquí). **Todas las cifras de esta fase deben leerse como internamente consistentes (geografía vs. mi propio baseline visual) pero NO como una extensión validada del pipeline exacto de Fase 23A.**

## 2. Resultados numéricos (barrido de pesos)

| w_geo | AUROC | IC95% AUROC | FAR | FRR | BalAcc |
|---|---|---|---|---|---|
| 0.0 (baseline visual, esta sesión) | 0.6181 | [0.5885, 0.6435] | 0.0500 | 0.9871 | 0.4814 |
| 0.1 | 0.6570 | [0.6297, 0.6806] | 0.0500 | 0.9839 | 0.4830 |
| 0.2 | 0.6878 | [0.6626, 0.7103] | 0.0500 | 0.9645 | 0.4927 |
| 0.3 | 0.7038 | [0.6786, 0.7264] | 0.0500 | 0.9581 | 0.4960 |
| 0.4 | 0.7107 | [0.6852, 0.7332] | 0.0500 | 0.9516 | 0.4992 |
| **0.5 (mejor)** | **0.7131** | **[0.6872, 0.7355]** | 0.0500 | 0.9419 | 0.5040 |
| Geografía sola | 0.6694 | [0.6442, 0.6948] | 0.6329 | 0.2194 | 0.5739 |

FAR es idéntico (0.0500) en todo el barrido combinado porque el umbral se fija por construcción en el cuantil KAR95 de la distribución KNOWN (convención diagnóstica, igual a la usada en Fase 23A, NO Youden-J — no hay split de calibración con UNKNOWN). A ese punto de operación estricto (95% KAR), el FRR sigue siendo muy alto (94%) incluso en el mejor combinado: la mayoría de las imágenes UNKNOWN no cruzan el umbral y son aceptadas como KNOWN. La geografía sola, con su propio umbral KAR95, opera en un punto muy distinto (FAR=63%, FRR=22%) — geometrías de score no comparables directamente sin re-calibrar en el mismo punto de operación, limitación reconocida.

## 3. Subgrupos por relación taxonómica (`metrics_by_taxonomic_and_geo_subgroup.csv`)

| Config | Subgrupo | n | AUROC |
|---|---|---|---|
| w=0.0 | mismo género | 426 | 0.6617 |
| w=0.0 | género distinto | 194 | 0.5225 |
| w=0.5 | mismo género | 426 | 0.7270 (Δ+0.065) |
| w=0.5 | género distinto | 194 | 0.6824 (Δ+0.160) |

La geografía ayuda en ambos subgrupos, y de forma más marcada en género distinto (+0.16) que en mismo género (+0.065) — contraintuitivo respecto a la hipótesis original (se esperaba mayor ayuda en mismo género, donde la señal visual es más ambigua). Zona/elevación: solo 262/620 UNKNOWN tienen zona asignada; el análisis por zona-igual/zona-distinta y por elevación cercana/lejana no se ejecutó de forma robusta por cobertura insuficiente (elevación 0% disponible, zona 42%).

## 4. Ablation (Fase 7)
- A) Visual solo: AUROC 0.6181 [0.5885,0.6435]
- B) Geografía sola: AUROC 0.6694 [0.6442,0.6948]
- C) Visual+Geografía (w=0.5): AUROC 0.7131 [0.6872,0.7355]
- D) Regiones morfológicas: no ejecutado (trabajo futuro)

## 5. Casos de cruce de umbral (Fase 8, muestra en `threshold_crossing_cases.json`)
308/8095 muestras cambiaron de predicción KNOWN↔UNKNOWN entre baseline (w=0) y combinado (w=0.5) a sus respectivos umbrales KAR95. Ejemplo de razonamiento típico observado en los casos:
```
Visual: distancia moderada al centroide más cercano (ambigua bajo el umbral estricto)
Geografía: especie candidata top-1 tiene P(especie|zona) muy baja o zona desconocida
Resultado: el score combinado cruza el umbral hacia UNKNOWN
```
Importante: incompatibilidad geográfica **no implica ausencia biológica** — el mapa de ocurrencias es incompleto y el prior solo cubre Antioquia; una especie fuera del área de registro puede simplemente no haber sido muestreada allí.

## 6. Fase 9 (conceptual, no implementada)
Mapeo triple-umbral propuesto: `ESPECIE_CONOCIDA` si combined_score < thr_low; `NO_REGISTRADA` si combined_score > thr_high; `NO_CONCLUYENTE` en la banda intermedia. thr_low/thr_high requerirían un split de calibración con UNKNOWN real (inexistente hoy) para no ser arbitrarios — documentado como trabajo futuro, no implementado por prioridad de tiempo.

## 7. Limitaciones honestas
1. **No reproducción exacta del baseline congelado** (Sección 1) — brecha de 0.045 en AUROC visual-solo, causa no completamente resuelta.
2. **Contaminación cruzada 27.2%** entre observaciones evaluadas y registros fuente del prior — el ejercicio es un diagnóstico, no una validación de generalización geográfica limpia.
3. **Elevación no disponible** desde la API de iNaturalist para ninguna de las 4466 observaciones consultadas — Fase 6 (elevación) no se pudo ejecutar con datos reales.
4. **Cobertura de zona baja** (37-42%): la mayoría de las muestras caen fuera de la grilla de Antioquia o sin coordenadas, recibiendo score neutro — el efecto medido de "geografía" está impulsado por una minoría de muestras con zona real asignada.
5. **Sin split de calibración independiente con UNKNOWN** para elegir el peso de fusión sin mirar el propio conjunto de evaluación — el barrido de pesos es exploratorio, no una selección ciega válida.
6. Individuo UNKNOWN definido como observation_id (mismo criterio usado en Fase 23A); bootstrap estratificado por esa unidad.

## 8. Veredicto
Los números crudos muestran una mejora grande y con IC95% no superpuestos (baseline 0.618 [0.589,0.644] vs. mejor combinado 0.713 [0.687,0.736]). Sin embargo, dos problemas metodológicos serios impiden una conclusión causal limpia: (a) el baseline visual de esta sesión no reproduce el baseline oficial congelado, y (b) 27.2% de contaminación cruzada entre el prior y las observaciones evaluadas. Por eso se declara **GEOGRAPHY_MARGINAL**: hay señal positiva reproducible dentro de esta sesión, pero no defendible como mejora geográfica genuina y generalizable sin (i) reconstruir el pipeline exacto del baseline congelado y (ii) purgar del prior las observaciones evaluadas y re-evaluar limpio.

## Artefactos generados (rutas absolutas)
- D:\Anura\validation\fase23a_geographic_context\GEOGRAPHIC_CONTEXT_REPORT.md
- D:\Anura\validation\fase23a_geographic_context\geographic_prior_manifest.json
- D:\Anura\validation\fase23a_geographic_context\geographic_prior_audit.json
- D:\Anura\validation\fase23a_geographic_context\anti_contamination_check.json
- D:\Anura\validation\fase23a_geographic_context\baseline_reproduction_check.json
- D:\Anura\validation\fase23a_geographic_context\baseline_visual_metrics.json
- D:\Anura\validation\fase23a_geographic_context\geographic_only_metrics.json
- D:\Anura\validation\fase23a_geographic_context\visual_plus_geography_metrics.json
- D:\Anura\validation\fase23a_geographic_context\weight_sweep_results.csv
- D:\Anura\validation\fase23a_geographic_context\bootstrap_results.json
- D:\Anura\validation\fase23a_geographic_context\per_sample_results.csv
- D:\Anura\validation\fase23a_geographic_context\ablation_summary.json
- D:\Anura\validation\fase23a_geographic_context\metrics_by_taxonomic_and_geo_subgroup.csv
- D:\Anura\validation\fase23a_geographic_context\threshold_crossing_cases.json
- D:\Anura\validation\fase23a_geographic_context\reproducibility_manifest.json
- D:\Anura\validation\fase23a_geographic_context\scripts\phase0_fetch_inat.py
- D:\Anura\validation\fase23a_geographic_context\scripts\phase1to8_main.py
- D:\Anura\validation\fase23a_geographic_context\cache\inat_observations_cache.json (raw+extracted iNat cache)
- D:\Anura\validation\fase23a_geographic_context\cache\inat_extracted.json
- D:\Anura\validation\fase23a_geographic_context\cache\fetch_summary.json
