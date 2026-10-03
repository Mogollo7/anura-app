# FASE 18 — Calibración Limpia y Blind Independiente: Reporte Final

**Fecha**: 2026-09-13. **No se hizo commit ni push.**

---

## 1. Objetivo y decisión metodológica de partida

Fase 17 mostró `MAHALANOBIS_WEAKER_THAN_ALTERNATIVES` (Cosine/Euclidean ~10 puntos AUROC por
encima). Esta fase determina si Euclidean o Cosine, calibrados y evaluados correctamente
(calibración → freeze → blind independiente), pueden convertirse en candidato real.

## 2. Auditoría de datos disponibles

- **UNKNOWN real total en el repositorio**: 56 imágenes (`Hyloxalus_picachos`: 15,
  `Sachatamia_electrops`: 41) — exactamente F4. **No existe ningún UNKNOWN adicional real.**
  No se fabricó, duplicó ni reutilizó ninguna imagen como individuo distinto.
- **KNOWN limpio disponible**: 7475 imágenes (Fase 16), 24/41 especies, 4103 individuos.

## 3. Splits construidos (`build_splits.py`, semilla fija 1618)

| | KNOWN | UNKNOWN |
|---|---|---|
| CALIBRATION_18 | 2545 imgs, 24 sp, 1405 ind | 17 imgs, 2 sp, 3 ind |
| BLIND_F18 | 4930 imgs, 24 sp, 2654 ind | 39 imgs, 2 sp, 11 ind |

Partición por `individual_id` (obs_id), estratificada por especie. **0 overlap de individuo**
entre CALIBRATION_18 y BLIND_F18 (verificado programáticamente, no asumido).

## 4. Limitación crítica declarada (no oculta)

`BLIND_F18` es un **subconjunto** del mismo pool de 7475+56 imágenes que Fase 17 ya evaluó
íntegramente para comparar AUROC de métodos. **No existen más datos reales** para construir un
blind completamente virgen. Esto introduce un riesgo de **sesgo de selección de método**
(no de calibración de threshold — en Fase 17 no se ajustó ningún hiperparámetro, solo se
comparó el AUROC de 3 fórmulas matemáticas fijas). Ver `leakage_audit.json`.
**Este hallazgo por sí solo impide declarar PASS incondicional.**

`CALIBRATION_18` vs `TRAIN`/`REFERENCE`/`CALIBRATION` original de Fase 13: **0 overlap**,
heredado de la verificación ya hecha en Fase 16.

## 5. Centroides

Reutilizados sin modificar: Group A (REFERENCE, 9 especies) + Group B (TRAIN, 32 especies) =
41 centroides. **Nunca calculados con datos de BLIND_F18 ni CALIBRATION_18.** Documentado en
`centroid_documentation.json`.

## 6-8. Calibración (solo sobre CALIBRATION_18, threshold definido antes de ver blind)

Regla de selección: percentil 95 de la métrica nativa (distancia para Euclidean, similitud
para Cosine) sobre KNOWN de calibración — misma filosofía que Fase 13 (target KAR=95%).

| | Euclidean | Cosine |
|---|---|---|
| Threshold | 0.9019 | 0.4966 |
| KAR (calibración) | 94.97% | 94.97% |
| FAR (calibración) | 94.12% | 88.24% |
| Balanced accuracy (calibración) | 0.5043 | 0.5337 |
| AUROC (diagnóstico) | 0.7437 | 0.7392 |

## 9. Selección de candidato

**Cosine seleccionado** — mayor `balanced_accuracy` en calibración (0.534 vs 0.504). Elegido
**antes** de observar `BLIND_F18` (ver `method_selection.json`).

## 10. Freeze

`fase18_freeze_manifest.json`: método=`COSINE`, threshold=`0.4966`, hashes de embeddings
REFERENCE/TRAIN, manifests de calibración/blind, resultados de calibración — todos capturados
**antes** de ejecutar el blind test.

## 11-13. Blind Test (BLIND_F18, después del freeze)

```
KNOWN_ACCEPTED / KNOWN_REJECTED:       4600 / 330  (de 4930)
UNKNOWN_REJECTED / UNKNOWN_FALSE_ACCEPTED: 2 / 37   (de 39)
```

| Métrica | Valor | IC 95% |
|---|---|---|
| KAR | 93.29% | (92.55%, 93.95%) |
| FRR | 6.71% | — |
| **FAR** | **94.87%** | (83.11%, 98.58%) |
| UDR | 5.13% | — |
| AUROC | 0.6672 | — |
| **Balanced accuracy** | **0.4921** | — (por debajo de azar) |
| F1 (unknown) | 0.0108 | — |

**Comparado con Fase 16 (Mahalanobis)**: AUROC mejora (0.667 vs 0.593), pero **FAR empeora**
(94.87% vs 93.88%) y **balanced_accuracy sigue por debajo de 0.5**. Cambiar de método no
resolvió el problema — lo desplazó.

## 14. Análisis por especie UNKNOWN

| Especie | n | Falsos aceptados | FAR |
|---|---|---|---|
| Sachatamia_electrops | 29 | 28 | 96.55% |
| Hyloxalus_picachos | 10 | 9 | 90.00% |

Ambas especies fallan de forma consistente y severa, igual que en Fase 16/17 — el patrón no es
específico del método, es estructural del catálogo/threshold.

## 15. Comparación (nunca mezclada)

Ver `fase18_comparison.json`: Fase 13 (Mahalanobis, contaminado) / Fase 16 (Mahalanobis,
limpio, pool completo) / Fase 17 (diagnóstico de métodos) / Fase 18 (Cosine, calibración +
blind independientes) reportados por separado, sin promediar.

## 16. Criterio de decisión

**No se fuerza PASS.** `balanced_accuracy=0.492` (por debajo de azar) y `FAR=94.87%` con IC 95%
estrecho (83%-98.6%, consistentemente alto) son evidencia clara y reproducible — a través de
3 fases distintas y 2 métodos distintos — de que el mecanismo actual **no rechaza especies
desconocidas de forma aceptable**, independientemente de si se usa Mahalanobis, Euclidean o
Cosine.

## 17. Lenguaje correcto (regla especial respetada)

No se declara "Open Set resuelto". Correcto: *"La evidencia indica que Cosine mejora el AUROC
diagnóstico respecto a Mahalanobis, pero el blind independiente muestra que el problema de
falsa aceptación de UNKNOWN no se resuelve cambiando de métrica de distancia — persiste con
severidad similar o mayor."*

## 18. Impacto móvil

| Método | Operación por consulta | Memoria adicional | Complejidad |
|---|---|---|---|
| Cosine | 1 producto punto por centroide (embeddings ya L2-norm) | Ninguna (solo centroides normalizados, 41×512 floats ≈ 84KB) | O(41×512) multiply-add |
| Euclidean | 1 resta + norma L2 por centroide | Ninguna | O(41×512), + sqrt opcional |
| Mahalanobis | 1 resta + 2 productos matriz-vector (512×512) por centroide | Matriz de precisión 512×512 ≈ 1MB | O(41×512²) — **~500x más costoso** |

Cosine y Euclidean son prácticamente equivalentes en costo; ambos son órdenes de magnitud más
baratos que Mahalanobis para runtime offline en móvil. Si el rendimiento científico fuera
equivalente, Cosine sería preferible (no requiere `sqrt`, solo productos punto). **Pero el
resultado científico no es equivalente ni aceptable para ninguno de los tres.**

## 19. Limitaciones (separadas por tipo)

**Ingeniería**: ninguna nueva — pipeline de splits, freeze y blind ejecutado correctamente.

**Datos**: (a) BLIND_F18 KNOWN no es completamente virgen respecto a exposición diagnóstica de
Fase 17 (sin datos adicionales disponibles para evitarlo); (b) solo 39 UNKNOWN / 11 individuos
/ 2 especies en blind — insuficiente para generalizar a "cualquier especie desconocida";
(c) solo 24/41 especies KNOWN tienen datos limpios.

**Científica**: el mecanismo de rechazo Open Set (bajo cualquiera de los 3 métodos evaluados
en 3 fases distintas) muestra `balanced_accuracy` en o por debajo de azar frente a datos
genuinamente held-out. Esto no es un problema de calibración de threshold — es evidencia de
que **la representación embedding actual no separa suficientemente estas especies conocidas
de estas especies desconocidas concretas**, consistente con los pares de centroides
intra-género casi solapados encontrados en Fase 17.

---

# FASE 18 FINAL STATUS

```
Calibration:
PASS

Blind independence:
PASS  (0 overlap de individuo verificado CALIBRATION_18 vs BLIND_F18; limitación de
       exposición parcial a Fase 17 documentada explícitamente, no oculta)

Selected candidate:
COSINE

Threshold:
0.4966  (similitud coseno; aceptar si score >= threshold)

Known:
KAR = 93.29%
FRR = 6.71%

Unknown:
FAR = 94.87%  (IC 95%: 83.11% - 98.58%)

AUROC = 0.6672
Balanced accuracy = 0.4921  (por debajo de azar)
F1 = 0.0108

Known species = 24 (de 41 en el catálogo)
Unknown species = 2
Individuals = 2654 KNOWN + 11 UNKNOWN (blind)

Scientific Open Set:
FAIL

Mobile suitability:
Cosine es computacionalmente muy superior a Mahalanobis (~500x menos operaciones,
sin matriz de covarianza que transportar) — pero esto es irrelevante mientras el
resultado científico sea FAIL.

Main limitation:
FAR≈95% es consistente a través de 3 fases y 3 métodos distintos (Mahalanobis, Euclidean,
Cosine) — el problema no es el método de distancia, es que los embeddings de las 2 especies
UNKNOWN disponibles no se distinguen de las especies KNOWN vecinas (mismo patrón de
Fase 17: pares de centroides intra-género casi solapados). Cambiar de métrica desplazó el
problema, no lo resolvió.

Next recommended phase:
No iterar más sobre métricas de distancia con los datos actuales — ya se probaron 3 y todas
fallan de forma similar. Se requiere: (a) más especies/individuos UNKNOWN reales para
confirmar si el patrón se sostiene o es artefacto de solo 2 especies, y (b) investigar si el
propio encoder BioCLIP (congelado) produce embeddings con suficiente separación inter-especie
para esta tarea, antes de seguir ajustando el mecanismo de rechazo posterior.
```
