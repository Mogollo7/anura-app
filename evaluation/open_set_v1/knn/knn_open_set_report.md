# Fase 6 — Embeddings, k-NN y señales Open Set

**Estado:** `FASE_6_COMPLETE`

## Pipeline reproducido

- Encoder: visual del checkpoint `bioclip_anura_mejor.pt`.
- Dimensión observada: 512; el artefacto existente no produce 768 dimensiones.
- Normalización: L2; se verificó norma media y máxima desviación en los embeddings guardados.
- Métrica: similitud coseno mediante distancia sqlite-vec; `similarity = 1 - distance`.
- k: 5.
- Paquete: `antioquia_v1.sqlite`, filtro geográfico Antioquia ya materializado.
- Vectores consultados: 2073.

## Comparación de señales

- Softmax Top-1: AUROC 0.585812.
- Softmax Margin: AUROC 0.584647.
- k-NN max_similarity: AUROC **0.678478**.
- k-NN mean_top5_similarity: AUROC **0.675308**.
- k-NN species_vote_count: AUROC **0.510083**.

Mejor señal vectorial: **max_similarity**.
FPR/FAR @ 95% TPR: **0.964286**, threshold analítico **0.010913**.
KNOWN aceptados: 752; UNKNOWN aceptados: 54.

## Consenso

El consenso es el número máximo de los cinco vecinos que pertenecen a la misma especie; no se combinó con Softmax ni con ningún prior.

## Correlación

- max_similarity vs softmax_top1: Pearson 0.408880; Spearman 0.425760.
- max_similarity vs softmax_margin: Pearson 0.253075; Spearman 0.213314.
- mean_top5_similarity vs softmax_top1: Pearson 0.411989; Spearman 0.431282.
- mean_top5_similarity vs softmax_margin: Pearson 0.247778; Spearman 0.206615.

## UNKNOWN

- El conjunto UNKNOWN contiene 56 imágenes de solo 2 especies.
- Las listas completas de vecinos y los casos de mayor similitud/consenso están en el JSON.
- Los resultados son piloto y pueden reflejar sesgo de cobertura del catálogo y similitud visual real.

### Resumen por especie

- **Hyloxalus_picachos** (15): max similarity media 0.185759; mean Top-5 media 0.153977; consenso medio 3.200; predicciones Pristimantis_achatinus=10, Craugastor_raniformis=3, Dendropsophus_bogerti=2.
- **Sachatamia_electrops** (41): max similarity media 0.253561; mean Top-5 media 0.219358; consenso medio 3.878; predicciones Hyloscirtus_palmeri=28, Scinax_ruber=5, Dendropsophus_bogerti=4, Dendropsophus_columbianus=3, Dendropsophus_microcephalus=1.

### Casos vectoriales destacados

- UNKNOWN con consenso 5/5: 26.
- UNKNOWN con consenso 4/5: 4.
- Los 10 casos con mayor similitud máxima y media Top-5 están en los artefactos JSON.

## Conclusión: `VECTORIAL_NO_MEJORA`

k-NN no constituye por sí mismo un detector Open Set. No se creó score combinado, no se aplicó threshold y no se modificó el catálogo ni SQLite-vec.
