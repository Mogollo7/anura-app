---
title: "EvaluaciÃ³n y MÃ©tricas â€” Ãndice"
proyecto: Anura
tipo: Ã­ndice
tags: [anura, evaluaciÃ³n, Ã­ndice]
---

# EvaluaciÃ³n y MÃ©tricas â€” Ãndice

[[Anura â€” Ãndice General]]

## Notas

| Nota | QuÃ© cubre |
| --- | --- |
| [[MÃ©tricas Offline]] | Resultados en test controlado: Top-1/Top-3, F1 macro, por nivel taxonÃ³mico, ablaciones, cuantizaciÃ³n |
| [[Matrices de ConfusiÃ³n]] | Con quÃ© se confunde el modelo y por quÃ©; tipos de error y coste asimÃ©trico |
| [[EvaluaciÃ³n en Campo Real]] | Protocolo del piloto: diseÃ±o, criterios de Ã©xito, instrumentaciÃ³n, Ã©tica |
| [[Reportes de Pruebas Piloto]] | Plantilla por salida y consolidado entre pilotos |
| [[Experimentos y Resultados]] | BitÃ¡cora de experimentos y cola priorizada |

## Los dos niveles de evaluaciÃ³n

| | Offline | Campo |
| --- | --- | --- |
| QuÃ© mide | El modelo | El sistema completo con personas |
| Condiciones | Controladas, imÃ¡genes seleccionadas | Reales, de noche, con lluvia |
| MÃ©trica principal | F1 macro | Top-3 accuracy y usabilidad |
| Resultado esperado | Mejor | Peor â€” **y esa diferencia es un resultado** |

## Objetivos comprometidos

| Meta | Valor | Fuente |
| --- | --- | --- |
| Top-3 Accuracy | â‰¥ 85 % | RNF-04 y objetivo general |
| PrecisiÃ³n a nivel Familia | 90â€“95 % | [[Estrategia de ConstrucciÃ³n del Dataset]] |
| PrecisiÃ³n a nivel GÃ©nero | 80â€“85 % | Ã­dem |
| PrecisiÃ³n a nivel Especie | â‰¥ 80 % | Ã­dem |
| Latencia web | â‰¤ 3 s | RNF-01 |
| Latencia mÃ³vil | â‰¤ 4 s | RNF-02 |
| TamaÃ±o de modelos | â‰¤ 150 MB | RNF-05 |
| BaterÃ­a | â‰¤ 5 %/hora | RNF-09 |

## Reglas de la casa

1. **F1 macro** es la mÃ©trica de selecciÃ³n, no la accuracy: el dataset estÃ¡ desbalanceado y las especies raras importan.
2. El **test se toca lo mÃ­nimo**; los umbrales se eligen en validaciÃ³n.
3. Todo resultado se acompaÃ±a de versiÃ³n de modelo y de dataset.
4. Los resultados negativos tambiÃ©n se registran.
5. Near-OOD y far-OOD se reportan por separado.

> [!tip] La Etapa I ya es el ejemplo a seguir
> Verificar que cada resultado se obtuvo con `GroupSplit` por individuo y localidad â€” es exactamente lo que hizo la Etapa I (segmentaciÃ³n binaria + split por individuo), que por eso alcanzÃ³ ~99 % de forma legÃ­tima y no por fuga de informaciÃ³n. Ver C-4 (resuelto) en [[Inconsistencias y Decisiones Pendientes]] y el detalle en [[Modelo de VisiÃ³n â€” BioCLIP]] Â§7.



