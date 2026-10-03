# FASE 17 — Comparación Limpia de Métodos Open Set

**Fecha**: 2026-09-13. **Method comparison only** — sin recalibrar threshold, sin tocar Fase 13,
sin commit/push.

## Datos

Exactamente el blind limpio de Fase 16: 7475 KNOWN (24 especies, 4103 individuos) + 56
UNKNOWN (F4, 2 especies). Mismos embeddings, mismos centroides (REFERENCE Group A + TRAIN
Group B), misma `covariance_1.1.0_CLEAN` (cargada, no recalculada).

## Resultado — AUROC por método

| Método | AUROC | Score orientation |
|---|---|---|
| M1 Cosine | **0.6892** | alto = más parecido a KNOWN (similitud coseno) |
| M2 Euclidean | **0.6936** | alto = más parecido a KNOWN (−distancia euclidiana) |
| M3 Mahalanobis (Ledoit-Wolf) | **0.5920** | alto = más parecido a KNOWN (−distancia Mahalanobis) |

**Escenario A confirmado**: Cosine ≈ Euclidean >> Mahalanobis (diferencia ~10 puntos AUROC).

## Por especie UNKNOWN (diagnóstico, no evidencia de generalización nacional)

| Especie | n | FAR @ threshold histórico | AUROC vs todas las KNOWN |
|---|---|---|---|
| Sachatamia_electrops | 41 | 92.68% | 0.6066 |
| Hyloxalus_picachos | 15 | 86.67% | 0.5522 |

Ambas especies, con o sin pariente cercano en el catálogo, muestran AUROC individual débil.

## Falsos aceptados (Mahalanobis, threshold histórico τ=39.354)

- Total: 51/56 (91%) aceptados incorrectamente.
- Especie KNOWN más cercana **no está distribuida uniformemente**: `Boana_cinerascens` (13/51) y
  `Hyloscirtus_palmeri` (11/51) concentran el 47% de los falsos aceptados — un patrón real, no
  ruido disperso.

## Dispersión intra-especie KNOWN (top 5 por std)

| Especie | n_images | dist_mean | dist_std |
|---|---|---|---|
| Dendropsophus_microcephalus | 611 | 29.60 | 8.40 |
| Dendrobates_truncatus | 1684 | 25.69 | 8.05 |
| Leptodactylus_colombiensis | 38 | 31.90 | 8.02 |
| Dendropsophus_bogerti | 814 | 32.85 | 7.96 |
| Pristimantis_achatinus | 1761 | 32.10 | 7.66 |

## Matriz de distancias entre centroides (Euclidean)

`min=0.1944, median=1.1037, max=1.3371`

**Top 5 pares más cercanos** — todos son pares intra-género:

| Species A | Species B | Distance |
|---|---|---|
| Pristimantis_paisa | Pristimantis_taeniatus | 0.1944 |
| Phyllomedusa_tarsius | Phyllomedusa_venusta | 0.1983 |
| Dendropsophus_ebraccatus | Dendropsophus_triangulum | 0.1991 |
| Dendropsophus_bogerti | Dendropsophus_columbianus | 0.2283 |
| Boana_pugnax | Boana_rosenbergi | 0.2309 |

Esto confirma que existen clases visualmente solapadas — su distancia mutua es comparable a la
dispersión intra-clase de las especies más "anchas" (~0.11-0.15 en euclidean normalizado).

## Diagnóstico de Mahalanobis (documentación, no conclusión automática)

```
embedding_dimension = 512
covariance_parameters = 512×512
effective_parameters = 262144
calibration_species = 10
calibration_images = 798
condition_number = 623.99
```

## Fase 13 vs Fase 16/17 (referencia histórica, nunca mezclada)

Fase 13 seleccionó `M5_LedoitWolf_Shared` vía 5-fold CV **sobre REFERENCE únicamente**,
comparando estabilidad/condicionamiento de scores — **no AUROC KNOWN-vs-UNKNOWN** (no había
UNKNOWN disponible en esa etapa por diseño). Por tanto, la selección de Fase 13 y el AUROC de
Fase 17 **no son directamente comparables como el mismo criterio** — Fase 13 respondía "¿qué
método es más estable calibrando?", Fase 17 responde "¿qué método separa mejor KNOWN de
UNKNOWN real?". Ambas preguntas son legítimas pero distintas.

## Conclusión

```
MAHALANOBIS_WEAKER_THAN_ALTERNATIVES
```

Evidencia empírica clara (no especulación): con los mismos centroides, mismos datos, mismo
blind limpio, Cosine y Euclidean simples superan a Mahalanobis+Ledoit-Wolf por ~10 puntos de
AUROC. Esto es consistente con el diagnóstico de Fase 16 (`condition_number=624`, solo 10
especies/798 imágenes calibrando una covarianza de 262,144 parámetros).

**No se declara ningún método como oficial.** Para convertir Cosine/Euclidean en candidato
real se requeriría: calibración limpia → threshold congelado → nuevo blind independiente →
evaluación final — ninguno de esos pasos se ejecutó aquí.
