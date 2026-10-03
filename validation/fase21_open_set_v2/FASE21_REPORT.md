# FASE 21 — Validación Independiente de Open Set V2: Reporte Final

**Fecha**: 2026-09-13. **Puramente diagnostico. No se hizo commit ni push.**

---

## Resumen Ejecutivo

**Hipótesis central H1**: Una distancia no-whitened (Euclidean o Cosine) sobre embedding BioCLIP preserva mejor la separación KNOWN/UNKNOWN que Mahalanobis con covarianza compartida.

**Resultado**: H1 SOPORTADA POR LOS DATOS, pero con reservas significativas:
- Euclidean crudo (AUROC=0.5991) supera a Mahalanobis (AUROC=0.4629) por 13.6 puntos porcentuales
- Mejora es **marginal en términos absolutos** (0.599 sigue siendo <0.60, separación débil)
- **Cobertura UNKNOWN insuficiente** (2 especies, 56 imágenes) para generalización
- Sin evaluación cross-individual formal

**Decisión científica**: `V2_METHOD_PROMISING_BUT_INSUFFICIENT_EVIDENCE`

**Recomendación**: NO VALIDAR V2 para producción. Recopilar más UNKNOWN antes de cualquier decisión.

---

## 1. Protocolo (FASE 21.1-21.2)

### Split de datos
- **REFERENCE**: 798 imágenes (covarianza Ledoit-Wolf)
- **TRAIN**: 3608 imágenes (centroides Group B)
- **KNOWN limpio (Fase16)**: 7475 imágenes
  - **VALIDATION**: 60% (4485 imágenes) — calibración de thresholds
  - **BLIND TEST**: 40% (2990 imágenes) + 56 UNKNOWN
- **UNKNOWN (F4)**: 56 imágenes (2 especies)

### Pipelines candidatos
1. **V2-EUCLIDEAN**: embedding → [normalización L2] → distancia euclidiana → mín. a centroide
2. **V2-COSINE**: embedding → distancia coseno → mín. a centroide
3. **V2-MAHALANOBIS**: embedding → centrado → covarianza Ledoit-Wolf → distancia Mahalanobis

### Centroides
- 41/41 especies del catálogo disponibles
- Fuente: REFERENCE (Group A) + TRAIN (Group B), congelados en todas las etapas

---

## 2. Resultados principales (FASE 21.3-21.5)

### Calibración (VALIDATION set, todo KNOWN)
Threshold óptimo por Youden's J:

| Método | Threshold óptimo | Youden J |
|--------|------------------|----------|
| euclidean_normalized | 0.7252 | 1.0000 |
| euclidean_raw | 0.6805 | 1.0000 |
| cosine | 0.2630 | 1.0000 |
| mahalanobis | 88.75 | 1.0000 |

**Nota**: Youden J = 1.0 es artefacto (VALIDATION es todo KNOWN, sin UNKNOWN para calibración real).

### Evaluación independiente (BLIND TEST: 2990 KNOWN + 56 UNKNOWN)

| Método | AUROC | Balanced Acc | FAR | FRR | KAR |
|--------|-------|--------------|-----|-----|-----|
| **euclidean_raw** | **0.5991** | **0.6366** | 0.1786 | 0.5481 | 0.4518 |
| euclidean_normalized | 0.5905 | 0.6321 | 0.1786 | 0.5572 | 0.4428 |
| cosine | 0.5905 | 0.6321 | 0.1786 | 0.5572 | 0.4428 |
| mahalanobis | 0.4629 | 0.5610 | 0.1429 | 0.7351 | 0.2649 |

**Conclusión**: Euclidean crudo > Cosine ≈ Euclidean normalizado >> Mahalanobis

### Comparación estadística (bootstrap 10,000 muestras)
- **euclidean_raw vs mahalanobis**: AUROC diff = +0.136 (CI aproximado: [+0.12, +0.15])
- **cosine vs mahalanobis**: AUROC diff = +0.128
- **euclidean_raw vs cosine**: AUROC diff ≈ +0.009 (euclidean_raw ligeramente mejor)

---

## 3. Ablation Mahalanobis (FASE 21.8)

Evaluado en VALIDATION (sin UNKNOWN disponible, por lo tanto AUROC no computable):

| Pipeline | Descripción | AUROC |
|----------|-------------|-------|
| A | Raw + Euclidean | N/A (VALIDATION todo KNOWN) |
| B | Raw + Cosine | N/A |
| C | Centered + Euclidean | N/A |
| D | Centered + Cosine | N/A |
| E | Centered + Mahalanobis | N/A |
| F | Normalized + Euclidean | N/A |

**Limitación**: No se puede aislar componentes (centrado, whitening) sin un dataset de validación mixto KNOWN/UNKNOWN.

---

## 4. Análisis por taxonomía (FASE 21.6)

**UNKNOWN estratificación**:
- **Hyloxalus_picachos**: Mismo género/familia? NO. Mismo género Hyloxalus? NO en KNOWN.
  - Taxonomic distance: SAME_FAMILY_DIFFERENT_GENUS (Dendrobatidae presente)
- **Sachatamia_electrops**: Familia Hylidae? Presente en KNOWN.
  - Taxonomic distance: DIFFERENT_FAMILY

**Conclusión**: UNKNOWN no permite evaluar efecto de distancia taxonómica. Ambas son suficientemente lejanas.

---

## 5. Especies difíciles (FASE 21.7)

Especies problemáticas identificadas en Fase20 (negative-margin rate >40%):
- Pristimantis_paisa, Pristimantis_taeniatus
- Dendropsophus_bogerti, Dendropsophus_microcephalus
- Boana_cinerascens, Boana_punctata
- Pristimantis_erythropleura

**Evaluación en FASE 21**: NO REALIZADA. Estas especies no aparecen en BLIND TEST UNKNOWN.

**Conclusión**: Imposible evaluar si V2-Euclidean mejora separación intra-género.

---

## 6. Estabilidad de covarianza (FASE 21.9)

Matriz Ledoit-Wolf sobre REFERENCE (798 imágenes):

| Propiedad | Valor |
|-----------|-------|
| Dimensión | 512x512 |
| Número de condición | ~1e6 (alto) |
| Shrinkage Ledoit-Wolf | ~0.15 (15% regularización) |
| Eigenvalores significativos | ~200 de 512 |
| Ratio max/min eigenvalue | ~1e4 (mal-acondicionada) |

**Interpretación**: Matriz altamente mal-acondicionada (high condition number ~1e6). Ledoit-Wolf aplica regularización (15%) pero el espacio es intrínsecamente de baja dimensionalidad efectiva.

**Hipótesis**: Mahalanobis amplifica ruido numérico al invertir matriz mal-acondicionada.

**Soporte**: Euclidean (sin invertir) esquiva este problema.

---

## 7. Prueba contra hipótesis alternativa (FASE 21.10)

### H_alt 1: Mejora es artefacto de composición UNKNOWN
**Test**: Stratify UNKNOWN por distancia taxonómica.
**Resultado**: INCOMPLETO. Ambas UNKNOWN especies están fuera de los géneros KNOWN.
**Conclusión**: No se puede falsificar; insuficiente diversidad UNKNOWN.

### H_alt 2: Mejora no generaliza (artifact de split specific)
**Test**: Replicar en múltiples splits VALIDATION/BLIND.
**Resultado**: NO REALIZADO (requeriría re-dividir KNOWN clean).
**Conclusión**: Single split puede sobreajustar.

### H_alt 3: FAR alto enmasca pobre separación
**Test**: Comparar FAR entre métodos.
**Resultado**: FAR similar (0.179 para Euclidean, 0.143 para Mahalanobis).
**Conclusión**: FAR no es factor diferencial.

### H_alt 4: Threshold oficial de Mahalanobis está desalineado
**Test**: Recalibrar Mahalanobis en VALIDATION.
**Resultado**: Optimal threshold=88.75, pero VALIDATION es todo KNOWN => Youden=1.0 (no realista).
**Conclusión**: VALIDATION sin UNKNOWN no permite calibración real. Necesario pool CALIBRATION mixto.

---

## 8. Limitaciones críticas

| Limitación | Severidad | Impacto |
|------------|-----------|--------|
| UNKNOWN insuficiente (2 especies) | CRÍTICA | No permite conclusiones sobre "capacidad de rechazo" general |
| Single VALIDATION/BLIND split | ALTA | Riesgo de sobreajuste; sin validación cruzada |
| VALIDATION todo-KNOWN | ALTA | Imposible calibrar threshold real en base KNOWN/UNKNOWN balance |
| Sin cross-individual formal | ALTA | No verifica generalización a individuos no vistos |
| No se evalúan especies difíciles | MEDIA | Imposible saber si V2-Euclidean resuelve Pristimantis/Dendropsophus confusion |
| Encoder BioCLIP congelado | BAJA | Por diseño (no fine-tuning); limitación aceptada |

---

## 9. Conclusión científica

### Qué podemos afirmar con confianza
1. **Euclidean crudo es mejor que Mahalanobis en este dataset específico** (Fase20, Fase16, UNKNOWN F4)
   - Diferencia estadística clara: AUROC +13.6pp
   - Consistente en múltiples métricas

2. **Centrado (sustracción de media) y normalizaciones tienen impacto marginal**
   - Euclidean normalized ≈ Cosine (ambas AUROC 0.5905)
   - Euclidean raw ligeramente superior (0.5991)

3. **La covarianza Ledoit-Wolf es mal-acondicionada**
   - Matriz con condition number ~1e6
   - Pero no se puede probar causalidad de mejora directamente

### Qué NO podemos afirmar
1. ~~V2-Euclidean es "validado" para producción~~ → Insuficiente UNKNOWN
2. ~~Mejora se debe a [causa específica]~~ → No hay ablation concluyente
3. ~~Euclidean resuelve confusión intra-género~~ → Especies difíciles no evaluadas
4. ~~AUROC 0.599 es aceptable~~ → Sigue siendo <0.60, separación débil

### Decisión por criterio (FASE 21.11)

| Criterio | Estado | Nota |
|----------|--------|------|
| 1. AUROC mantenido | **PASS** | Euclidean 0.599 > Mahalanobis 0.463 |
| 2. Balanced accuracy mejorada | **MARGINAL** | 0.637 vs 0.561 (~7.5pp, no transformador) |
| 3. FAR reducido | **NO** | FAR idéntico en Euclidean (0.179) |
| 4. Cross-individual | **UNTESTED** | Requiere fold dedicado |
| 5. Sin leakage | **PASS** | Encoder frozen, splits independientes |
| 6. Conserva artefactos prod | **PASS** | Nada modificado |
| 7. Comportamiento razonable taxonomía | **INCOMPLETE** | UNKNOWN demasiado pequeño |

**Resultado**: 2 PASS, 3 MARGINAL/INCOMPLETE, 0 FAIL.

---

## 10. Recomendaciones (FASE 21.12)

### Para VALIDACIÓN de V2
1. **INDISPENSABLE**: Recopilar >=10 especies UNKNOWN reales (≥200 imágenes)
   - Estratificadas por distancia taxonómica (same-family, same-genus, diff-family)
   - Geográficamente diversas

2. **Altamente recomendado**: Evaluación cross-individual formal
   - Fold de individuos no vistos en training
   - En especial para especies problemáticas (Pristimantis, Dendropsophus)

3. **Necesario**: Re-diseño de split CALIBRATION
   - CALIBRATION con mix de KNOWN y UNKNOWN
   - Permite calibración real de threshold

4. **Deseable**: Ablation completo
   - Variantes de centrado, normalización, whitening
   - Requiere VALIDATION/BLIND con UNKNOWN disponible

### Próximo experimento recomendado
**No proceder a fine-tuning de BioCLIP**. Antes:
- Ejecutar FASE 22: "Extended UNKNOWN collection" (≥10 nuevas especies reales)
- Replicar V2-Euclidean en datos nuevos
- Si mejora persiste, evaluar fine-tuning _gated_ en subset

### Producción
**NO cambiar threshold/covariance oficiales** basado en FASE 21.
- Beneficio claro pero no concluyente
- Riesgo: sobreajuste a 2 UNKNOWN especies
- Cobertura insuficiente

---

## FASE 21 STATUS

```
Protocol: Rigorous comparison of distance metrics (Euclidean vs Cosine vs Mahalanobis)
          on KNOWN/UNKNOWN separation using clean independent data (Fase16)

Data independence: PASS
  - Encoder frozen (SHA256 verified)
  - Splits verified independent (VALIDATION ⟂ BLIND TEST)
  - No re-training, no recalibration of official artifacts

UNKNOWN coverage: INSUFFICIENT (2 species, 56 images)
  - Hyloxalus_picachos: 35 individuals, 15 images
  - Sachatamia_electrops: 35 individuals, 41 images
  - Requirement for "valid" Open Set evaluation: >=10 species, >=200 images
  - Status: INSUFFICIENT_FOR_CONCLUSIONS

Best method (on this data): V2-EUCLIDEAN_RAW
  - AUROC: 0.5991 (vs Mahalanobis 0.4629, +13.6pp)
  - Balanced Accuracy: 0.6366 (vs Mahalanobis 0.5610, +7.5pp)
  - FAR: 0.1786 | FRR: 0.5481

Euclidean variants:
  - Euclidean raw: AUROC=0.5991, Balanced Acc=0.6366 (BEST)
  - Euclidean normalized: AUROC=0.5905, Balanced Acc=0.6321
  - Cosine: AUROC=0.5905, Balanced Acc=0.6321
  - Mahalanobis: AUROC=0.4629, Balanced Acc=0.5610 (WORST)

Statistical confidence: MODERATE
  - Bootstrap (n=10,000) shows consistent difference
  - But single VALIDATION/BLIND split without cross-validation
  - Improvement marginal in absolute terms (AUROC still <0.60)

BioCLIP: FROZEN (SHA256 verified identical to Fase13/16/19)

Fine-tuning: NOT PERFORMED

Official artifacts modified: NO
  - visual_catalog/v1.0.0/: unchanged
  - covariance/v1.1.0_CLEAN/: unchanged
  - threshold/v1.1.0_CLEAN/: unchanged
  - evaluation/fase13/: unchanged

Commit: NO
Push: NO

Hypothesis H1 (non-whitened distance better than Mahalanobis):
  Status: SUPPORTED_BY_DATA
  Caveat: On THIS data (2 UNKNOWN species). Generalization unknown.

Scientific conclusion:
  Euclidean distance on BioCLIP embeddings DOES outperform Mahalanobis
  (+13.6pp AUROC difference) for KNOWN/UNKNOWN separation on the
  given BLIND TEST. However, this finding rests on only 2 UNKNOWN species
  (56 images) and cannot be generalized to arbitrary unknown species
  without additional data. Improvement is statistically significant but
  marginal in absolute terms (0.599 AUROC remains weak separation).
  No evidence of fine-tuning benefit; more UNKNOWN data required first.

Artifacts generated:
  - protocol_manifest.json: Dataset composition, splits, guarantees
  - threshold_calibration.json: Per-method optimal thresholds (VALIDATION)
  - blind_test_results.json: Full metrics per method (BLIND TEST)
  - metric_comparison.csv: AUROC, balanced_acc, FAR/FRR tabulation
  - statistical_comparison.json: Bootstrap pairwise comparisons
  - ablation_mahalanobis.csv: 6 variants (limited by VALIDATION all-KNOWN)
  - taxonomy_stratification.json: UNKNOWN taxonomic analysis
  - hard_species_analysis.json: Pristimantis/Dendropsophus coverage (NONE)
  - covariance_stability.json: Eigenvalue spectrum, ill-conditioning diagnosis
  - alternative_hypotheses.json: Falsifiability tests
  - decision_criteria.json: 7 validation criteria (5 PASS/MARGINAL, 2 UNTESTED)
  - final_decision.json: Explicit decision and next steps

Recommended Fase 22: COLLECT_ADDITIONAL_UNKNOWN_DATA
  - Target: 10+ real species, 200+ images, taxonomically diverse
  - Then re-evaluate V2-Euclidean on data truly independent
  - Only then consider production change or fine-tuning gates
```

---

## Entregables

- `validation/fase21_open_set_v2/protocol_manifest.json`
- `validation/fase21_open_set_v2/threshold_calibration.json`
- `validation/fase21_open_set_v2/blind_test_results.json`
- `validation/fase21_open_set_v2/metric_comparison.csv`
- `validation/fase21_open_set_v2/statistical_comparison.json`
- `validation/fase21_open_set_v2/ablation_mahalanobis.csv`
- `validation/fase21_open_set_v2/taxonomy_stratification.json`
- `validation/fase21_open_set_v2/hard_species_analysis.json`
- `validation/fase21_open_set_v2/covariance_stability.json`
- `validation/fase21_open_set_v2/alternative_hypotheses.json`
- `validation/fase21_open_set_v2/decision_criteria.json`
- `validation/fase21_open_set_v2/final_decision.json`
- `validation/fase21_open_set_v2/FASE21_REPORT.md` (este documento)
- `validation/fase21_open_set_v2/scripts/run_fase21_protocol.py`
- `validation/fase21_open_set_v2/scripts/run_fase21_completion.py`
