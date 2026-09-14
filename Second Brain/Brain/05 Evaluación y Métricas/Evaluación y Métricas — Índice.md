---
title: "Evaluación y Métricas â€” àndice"
proyecto: Anura
tipo: índice
tags: [anura, evaluación, índice]
---

# Evaluación y Métricas â€” àndice

[[Anura â€” àndice General]]

## Notas

| Nota | Qué cubre |
| --- | --- |
| [[Métricas Offline]] | Resultados en test controlado: Top-1/Top-3, F1 macro, por nivel taxonómico, ablaciones, cuantización |
| [[Matrices de Confusión]] | Con qué se confunde el modelo y por qué; tipos de error y coste asimétrico |
| [[Evaluación en Campo Real]] | Protocolo del piloto: diseño, criterios de éxito, instrumentación, ética |
| [[Reportes de Pruebas Piloto]] | Plantilla por salida y consolidado entre pilotos |
| [[Experimentos y Resultados]] | Bitácora de experimentos y cola priorizada |

## Los dos niveles de evaluación

| | Offline | Campo |
| --- | --- | --- |
| Qué mide | El modelo | El sistema completo con personas |
| Condiciones | Controladas, imágenes seleccionadas | Reales, de noche, con lluvia |
| Métrica principal | F1 macro | Top-3 accuracy y usabilidad |
| Resultado esperado | Mejor | Peor â€” **y esa diferencia es un resultado** |

## Objetivos comprometidos

| Meta | Valor | Fuente |
| --- | --- | --- |
| Top-3 Accuracy | â‰¥ 85 % | RNF-04 y objetivo general |
| Precisión a nivel Familia | 90â€“95 % | [[Estrategia de Construcción del Dataset]] |
| Precisión a nivel Género | 80â€“85 % | ídem |
| Precisión a nivel Especie | â‰¥ 80 % | ídem |
| Latencia web | â‰¤ 3 s | RNF-01 |
| Latencia móvil | â‰¤ 4 s | RNF-02 |
| Tamaño de modelos | â‰¤ 150 MB | RNF-05 |
| Batería | â‰¤ 5 %/hora | RNF-09 |

## Reglas de la casa

1. **F1 macro** es la métrica de selección, no la accuracy: el dataset está desbalanceado y las especies raras importan.
2. El **test se toca lo mínimo**; los umbrales se eligen en validación.
3. Todo resultado se acompaña de versión de modelo y de dataset.
4. Los resultados negativos también se registran.
5. Near-OOD y far-OOD se reportan por separado.

> [!tip] La Etapa I ya es el ejemplo a seguir
> Verificar que cada resultado se obtuvo con `GroupSplit` por individuo y localidad â€” es exactamente lo que hizo la Etapa I (segmentación binaria + split por individuo), que por eso alcanzó ~99 % de forma legítima y no por fuga de información. Ver C-4 (resuelto) en [[Inconsistencias y Decisiones Pendientes]] y el detalle en [[Modelo de Visión â€” BioCLIP]] §7.



