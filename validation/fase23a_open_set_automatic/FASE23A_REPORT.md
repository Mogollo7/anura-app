# FASE 23A — Open Set Evaluation, UNKNOWN Automático (Reconstruido + Deduplicado)

Fecha ejecución: 2026-09-14
Estado: **FASE23A_COMPLETE** (métricas y artefactos 100% reales — embeddings generados en esta
sesión, bootstrap ejecutado en esta sesión)

> **NOTA SOBRE ARTEFACTOS PREVIOS EN ESTE DIRECTORIO**: existían archivos de una ejecución anterior
> (`FASE23A_STATUS.txt`, `FASE23A_FINAL_STATUS.md`, `*_corrected.csv`, etc.) que afirmaban
> encoder SHA256=`219e860e...` y un dataset de 622 imágenes / 321 individuos, y que la fase estaba
> `BLOCKED` por falta de embeddings. Esta sesión verificó de forma independiente que el SHA256 real
> del checkpoint (`98a6c54d...`) SÍ coincide con el especificado, generó embeddings reales, y
> encontró el dataset real en 620 imágenes / 412 individuos (tras la deduplicación de esta sesión).
> Los archivos previos se dejaron intactos (no se borraron) pero están **superados** por los
> artefactos de este reporte.

## 1. Dataset UNKNOWN (entrada)

- Fuente: `data/unknown_open_set_v2/images/primary/` reconstruido y deduplicado en esta sesión.
- 7 especies, **620 imágenes**, **412 individuos** (por `observation_id` real).
- Leakage vs. dataset KNOWN real (`data cleaned/`, 12254 archivos): **0**.
- Duplicados exactos: **0** (post-deduplicación determinista por SHA256/observation_id).
- Manifest: `data/unknown_open_set_v2/manifests/PRIMARY_MANIFEST.json` (v1.3.0-rebuild-dedup).

## 2. Encoder

- `bioclip/checkpoints/bioclip_anura_mejor.pt`
- SHA256 verificado en esta sesión: `98a6c54d6edb27e2b0344b8bbbaebd2ab749b1bf5136991ff73b37f66ee2c1ac`
  — **coincide exactamente** con el valor especificado en la tarea.
- Cargado con el patrón exacto de `evaluation/fase13/fase13_compute_train_embeddings.py`
  (`open_clip.create_model_and_transforms("hf-hub:imageomics/bioclip")` +
  `model.visual.load_state_dict(checkpoint["visual_state_dict"])`). Sin fine-tuning, sin ONNX.
- Nota de compatibilidad: los manifests de covarianza/threshold/catálogo referencian
  `encoder_sha256=219e860e...`, que corresponde al export ONNX del mismo entrenamiento (confirmado
  cruzando `evaluation/model_size_audit.md` y
  `validation/new_species_test/fixture/embedding_contract_verified.json`, que listan ambos hashes
  como identificadores gemelos del mismo modelo congelado). No hay incompatibilidad real de pesos.

## 3. Embeddings

- UNKNOWN: 620 × 512, generados en GPU (CUDA) en esta sesión. 0 NaN, 0 Inf, norma L2 = 1.0 ±1e-6.
  Archivo: `embeddings/unknown_embeddings.npz`.
- KNOWN: `validation/fase16_clean_open_set/clean_known_embeddings.npz` — 7475 × 512, 24 especies
  (subset verificado libre de leakage TRAIN/individuo, split `CLEAN_KNOWN_FASE16`). **No** son las
  41 especies completas del catálogo — es el único pool KNOWN con independencia de individuo ya
  verificada por Fase 16; se documenta explícitamente, no se sustituye silenciosamente por otro.
- Centroides: 41 especies (9 Grupo A desde REFERENCE, 32 Grupo B desde TRAIN), replicando
  exactamente la lógica de `evaluation/fase13/fase13_final_evaluation.py::compute_centroids` /
  merge Group A/B (aserciones de conteo verificadas: 41/9/32 OK).
- Covarianza: `covariance/v1.1.0_CLEAN/covariance_matrix.npz` (Ledoit-Wolf, shrinkage=0.066659),
  cargada sin recalcular.

## 4. Métodos y thresholds

| Método | τ usado | Estado del threshold |
|---|---|---|
| Mahalanobis | 39.354064 | **HISTORICAL_FROZEN_NOT_OPTIMIZED_FOR_THIS_UNKNOWN** (congelado de Fase 13/threshold v1.1.0_CLEAN) |
| Euclidean Raw | 0.824366 | CALIBRATED_DIAGNOSTIC_KAR95_QUANTILE_KNOWN_ONLY |
| Cosine | 0.422240 | CALIBRATED_DIAGNOSTIC_KAR95_QUANTILE_KNOWN_ONLY |
| Normalized Euclidean | 0.918951 | CALIBRATED_DIAGNOSTIC_KAR95_QUANTILE_KNOWN_ONLY |

**Anomalía metodológica documentada (no corregida silenciosamente)**: la instrucción pedía calibrar
Euclidean/Cosine/Normalized-Euclidean con Youden-J sobre CALIBRATION. El split
`evaluation/fase13/embeddings/calibration_embeddings.npz` contiene **únicamente 192 imágenes
KNOWN** (0 UNKNOWN) — un verdadero índice de Youden-J requiere ambas clases en el set de
calibración, y usar BLIND/TEST (que sí tiene UNKNOWN) para calibrar está expresamente prohibido por
la tarea ("nunca mirar BLIND/TEST para calibrar"). No existe un split de calibración UNKNOWN
independiente para estos 3 métodos. Se usó en su lugar el cuantil KAR-95% de CALIBRATION
(KNOWN-only) — el mismo punto de operación convencional que el threshold histórico de Mahalanobis
— y se etiquetó explícitamente `CALIBRATED_DIAGNOSTIC_KAR95_QUANTILE_KNOWN_ONLY`, distinto de un
verdadero Youden-J. Ver `reproducibility/anomalies.json`.

## 5. Convención de matriz de confusión (verificada antes de reportar)

KNOWN = clase positiva (aceptar = correcto, label=1). UNKNOWN = clase negativa (rechazar =
correcto, label=0). TP=known aceptado correctamente, TN=unknown rechazado correctamente,
FP=unknown aceptado incorrectamente (→ FAR), FN=known rechazado incorrectamente (→ FRR).
Documentado en `confusion_matrices.json`.

## 6. Resultados globales (4 métodos, IC 95% por bootstrap estratificado por individuo, 1000 iteraciones, seed=42)

| Método | AUROC | AUROC IC95% | FAR | FAR IC95% | FRR | FRR IC95% | Balanced Acc | Bal.Acc IC95% |
|---|---|---|---|---|---|---|---|---|
| **Euclidean Raw** | **0.5733** | [0.5426, 0.6041] | 0.8113 | [0.7753, 0.8454] | 0.1390 | [0.1311, 0.1473] | 0.5249 | [0.5075, 0.5434] |
| Cosine | 0.5731 | [0.5424, 0.6026] | 0.8210 | [0.7861, 0.8517] | 0.1303 | [0.1228, 0.1381] | 0.5244 | [0.5082, 0.5418] |
| Normalized Euclidean | 0.5731 | [0.5435, 0.6023] | 0.8210 | [0.7849, 0.8513] | 0.1303 | [0.1228, 0.1374] | 0.5244 | [0.5085, 0.5431] |
| Mahalanobis | 0.5380 | [0.5084, 0.5644] | 0.8500 | [0.8193, 0.8804] | 0.1761 | [0.1675, 0.1847] | 0.4870 | [0.4716, 0.5024] |

**Mejor método por AUROC: Euclidean Raw** (0.5733), aunque las diferencias entre los 3 métodos no
Mahalanobis son marginales (solapamiento total de IC95%). Mahalanobis es el peor y el único con
AUROC IC95% que casi cruza 0.5 (azar), y con `balanced_accuracy` bajo el azar (0.487) — esperable
dado que su threshold no fue calibrado para este UNKNOWN (es el histórico congelado).

**FAR es muy alto en los 4 métodos (0.81–0.85)**: con el punto de operación KAR-95% (calibrado para
aceptar el 95% de KNOWN), la gran mayoría de las 620 imágenes UNKNOWN son aceptadas incorrectamente
como KNOWN. Esto es consistente con AUROC cercano a 0.5-0.57: el encoder BioCLIP congelado separa
muy débilmente estas 7 especies UNKNOWN del catálogo KNOWN en el espacio de embeddings.

Tabla completa: `method_comparison.csv`. Bootstrap crudo: `bootstrap_results.csv`.
Umbrales: `threshold_analysis.csv`. Matrices de confusión: `confusion_matrices.json`.

## 7. Por especie (7 UNKNOWN) y por relación taxonómica

Ver `metrics_by_species.csv` y `metrics_by_taxonomic_relation.csv` (completos). Relación
taxonómica de cada especie UNKNOWN frente al catálogo KNOWN de 41 especies:

| Especie UNKNOWN | Género | Familia | Relación con KNOWN-41 |
|---|---|---|---|
| Craugastor_metriosistus | Craugastor | Craugastoridae | SAME_GENUS |
| Dendropsophus_labialis | Dendropsophus | Hylidae | SAME_GENUS |
| Leptodactylus_fragilis | Leptodactylus | Leptodactylidae | SAME_GENUS |
| Rhinella_marina | Rhinella | Bufonidae | SAME_GENUS |
| Scinax_rostratus | Scinax | Hylidae | SAME_GENUS |
| Smilisca_phaeota | Smilisca | Hylidae | SAME_FAMILY |
| Espadarana_prosoblepon | Espadarana | Centrolenidae | DIFFERENT_FAMILY |

Nota: 5 de las 7 especies UNKNOWN comparten género con alguna de las 41 especies KNOWN
(taxonómicamente "cercanas" en el espacio biológico), lo que es consistente con la baja
separabilidad observada (AUROC ~0.53-0.57): son especies emparentadas y visualmente similares a
especies ya conocidas por el modelo, un escenario de open-set genuinamente difícil.

## 8. Por individuo

`metrics_by_individual.csv` — 412 individuos UNKNOWN + individuos KNOWN, con distancia media,
predicción y corrección por individuo (agregando sus múltiples fotos).

## 9. Comparación con Fase 20/21

| Método | Fase21 AUROC | Fase23A AUROC | Fase21 FAR | Fase23A FAR | Fase21 Bal.Acc | Fase23A Bal.Acc |
|---|---|---|---|---|---|---|
| Euclidean Raw | 0.5991 | 0.5733 | 0.1786 | 0.8113 | 0.6366 | 0.5249 |
| Cosine | 0.5905 | 0.5731 | 0.1786 | 0.8210 | 0.6321 | 0.5244 |
| Normalized Euclidean | 0.5905 | 0.5731 | 0.1786 | 0.8210 | 0.6321 | 0.5244 |
| Mahalanobis | 0.4629 | 0.5380 | 0.1429 | 0.8500 | 0.5610 | 0.4870 |

**Comparabilidad de protocolo: PARCIAL, no un re-test controlado.** Fase 21 usó UNKNOWN=2 especies
manualmente curadas (56 imágenes) con thresholds Youden-J calibrados sobre un split UNKNOWN de
calibración etiquetado; Fase 23A usa UNKNOWN=7 especies automáticas sin curación (620 imágenes),
con 3/4 thresholds calibrados solo con KNOWN (ver sección 4). El FAR mucho más alto en Fase 23A
para los 3 métodos no-Mahalanobis refleja principalmente ese cambio de protocolo de calibración
(threshold más permisivo, calibrado sin señal UNKNOWN), no necesariamente una degradación real del
modelo. La AUROC (que no depende del threshold) es la métrica más comparable entre fases, y se
mantiene en el mismo rango bajo (0.46–0.60) en ambas, confirmando el hallazgo consistente de
separabilidad débil del encoder BioCLIP congelado frente a especies genuinamente nuevas.
Detalle: `comparison_fase20_fase21_vs_fase23a.csv`.

## 10. Anomalías detectadas (no corregidas silenciosamente)

1. **Calibración Youden-J imposible con CALIBRATION KNOWN-only** — ver sección 4.
2. **KNOWN pool = 24 especies, no 41** — es el único pool con independencia de individuo verificada
   (Fase 16); usar los 41 hubiera requerido mezclar TRAIN (leakage) o inventar una fuente no
   documentada. Se usó el real y se documentó la limitación.
3. Ningún NaN/Inf en embeddings ni en distancias; ningún FAR/FRR/TPR/TNR fuera de [0,1].
   `reproducibility/anomalies.json` contiene el detalle completo (incluye los 2 puntos anteriores).

## 11. Limitaciones

- El AUROC ~0.53-0.57 indica que, con el encoder BioCLIP actual (congelado, sin fine-tuning), estas
  7 especies UNKNOWN son difíciles de separar del catálogo KNOWN — probablemente por relación
  taxonómica cercana (5/7 comparten género) y por variabilidad de pose/fondo/calidad fotográfica en
  datos automáticos de iNaturalist no curados.
- Los thresholds de Euclidean/Cosine/Normalized-Euclidean son diagnósticos (KAR95-quantile
  KNOWN-only), no Youden-J verdaderos — los valores de FAR/FRR con estos thresholds no deben
  interpretarse como el punto de operación óptimo real, solo como un punto de referencia
  consistente con la convención KAR-95% ya usada para Mahalanobis.
- El threshold Mahalanobis es histórico y explícitamente no optimizado para este UNKNOWN.
- KNOWN pool limitado a 24/41 especies (las únicas con independencia de individuo verificada).
- Comparación con Fase 20/21 es parcial por diferencias de protocolo (ver sección 9).

## 12. Rutas de artefactos

- `embeddings/unknown_embeddings.npz` — embeddings UNKNOWN reales (620×512)
- `embeddings/merged_eval_state.npz` — estado combinado KNOWN+UNKNOWN usado para bootstrap/estratificación
- `dataset_audit.json`
- `reproducibility/config.json`, `reproducibility/anomalies.json`, `reproducibility/best_method.json`
- `method_comparison.csv`, `method_comparison_raw.json`
- `threshold_analysis.csv`
- `metrics_by_species.csv`, `metrics_by_taxonomic_relation.csv`, `metrics_by_individual.csv`
- `bootstrap_results.csv`
- `confusion_matrices.json`
- `predictions/predictions_raw.json`
- `plots/roc_curves.png`, `plots/score_distributions.png`
- `comparison_fase20_fase21_vs_fase23a.csv`

## 13. Estado final

**FASE23A_COMPLETE.** Ninguna curación manual, fine-tuning, scraping, ni modificación de BioCLIP /
producción / artefactos protegidos. No commit, no push.
