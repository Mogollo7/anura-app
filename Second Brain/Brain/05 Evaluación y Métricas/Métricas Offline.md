---
title: "Métricas Offline"
proyecto: Anura
tipo: evaluación
estado: plantilla-lista-para-resultados
tags: [anura, evaluación, métricas, experimentos]
---

# Métricas Offline

[[Anura â€” àndice General]] · [[Evaluación y Métricas â€” àndice]] · [[Matrices de Confusión]] · [[Experimentos y Resultados]] · [[Open-Set Recognition]]

> [!abstract] Qué se mide aquí
> Rendimiento en condiciones controladas, sobre el conjunto de test congelado. Es la evaluación que sostiene las afirmaciones del documento de grado; la evaluación en condiciones reales está en [[Evaluación en Campo Real]] y suele dar nàºmeros peores â€” eso es normal y hay que reportarlo, no esconderlo.

## 1. Configuración de la evaluación

Se rellena una vez y se congela. Cambiarla invalida la comparación entre experimentos.

| Campo | Valor |
| --- | --- |
| Conjunto de test | 120 imágenes originales, sin augmentación |
| Estrategia de split | `GroupSplit` por individuo y localidad |
| Nº de clases | *(pendiente de fijar â€” ver [[Inconsistencias y Decisiones Pendientes]])* |
| Balance de clases | Desbalanceado (ver [[Listado de Individuos y Arreglo Taxonómico]]) |
| **Métrica principal** | **F1 macro** |
| Métricas secundarias | Top-1, Top-3, precisión, sensibilidad, consistencia taxonómica |
| Métrica del objetivo | **Top-3 Accuracy â‰¥ 85 %** (RNF-04) |

> [!important] Por qué F1 macro y no accuracy
> Con clases desbalanceadas, la accuracy premia acertar las especies abundantes. Un modelo que ignore por completo las especies raras â€” que son las que más importan en conservación â€” puede tener buena accuracy y ser inàºtil. **F1 macro pondera todas las especies por igual** y penaliza el abandono de las minoritarias. La accuracy se reporta igualmente, pero no se optimiza contra ella.

## 2. Resultados globales

Rellenar por cada versión evaluada. No sobrescribir filas anteriores: el histórico es lo que permite ver si se avanza.

| Fecha | Versión modelo | Versión dataset | Top-1 | Top-3 | F1 macro | Precisión macro | Recall macro | Notas |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | | |

## 3. Resultados por nivel taxonómico

La clasificación es jerárquica, así que reportar solo especie oculta información àºtil. Las metas fijadas en [[Estrategia de Construcción del Dataset]]:

| Nivel | Meta | Top-1 | Top-3 | F1 macro |
| --- | --- | --- | --- | --- |
| Familia | 90â€“95 % | | | |
| Género | 80â€“85 % | | | |
| Especie | â‰¥ 80 % | | | |

Y una métrica propia de este diseño:

| Métrica | Valor | Definición |
| --- | --- | --- |
| **Consistencia taxonómica** | | % de predicciones donde especie â†’ género â†’ familia son coherentes entre sí |

## 4. Resultados por especie

La tabla que revela dónde está el problema real. Ordenar por F1 ascendente: las primeras filas son la lista de trabajo.

| Especie | N test | Precisión | Recall | F1 | Confusión principal |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

**Referencia de la Etapa I: 10 especies, exactitud global ~99 %**, con segmentación binaria (individuo vs. fondo) antes de BioCLIP y `GroupSplit` por individuo â€” detalle metodológico completo en [[Modelo de Visión â€” BioCLIP]] §7 y en [[Estrategia de Construcción del Dataset]]. No es fuga de información: es el resultado de un pipeline correctamente diseñado. Pendiente: repetir el mismo protocolo al escalar el catálogo, para confirmar que se sostiene.

## 5. Ablación por modalidad

El experimento clave de [[Arquitectura Multimodal]] §4. Todas las filas sobre el **mismo subconjunto** con todas las modalidades disponibles.

| Configuración | N | Top-1 | Top-3 | F1 macro | Î” F1 |
| --- | --- | --- | --- | --- | --- |
| Solo imagen | | | | | â€” |
| + contexto geográfico | | | | | |
| + audio | | | | | |
| + audio + contexto | | | | | |
| + morfología (plantillas) | | | | | |

## 6. Estrategias de uso de BioCLIP (àºnico backbone del proyecto)

BioCLIP es el àºnico modelo del proyecto ([[Modelo de Visión â€” BioCLIP]]); esta tabla no compara arquitecturas distintas, compara **cuánto se le pide a BioCLIP** â€” de menor a mayor coste de entrenamiento.

| Configuración | Tamaño | Top-1 | Top-3 | F1 macro | Latencia |
| --- | --- | --- | --- | --- | --- |
| BioCLIP zero-shot (sin entrenar nada) | | | | | |
| BioCLIP congelado + cabezas jerárquicas | | | | | |
| BioCLIP + triplet loss (fine-tuning parcial) | | | | | |
| **Etapa I (segmentación binaria + BioCLIP + cabezas)** | | ~99 % | | | |

### Comparación de entrada al modelo (variantes A/B/C)

Definida en [[Modelo de Visión â€” BioCLIP]] §5. La variante C (recorte + máscara binaria) es la que ya produjo el resultado de la Etapa I.

| Variante de entrada | Top-1 | Top-3 | F1 macro |
| --- | --- | --- | --- |
| A â€” Imagen completa | | | |
| B â€” Recorte del individuo | | | |
| **C â€” Recorte + máscara binaria** âœ… | ~99 % (Etapa I) | | |

### Rama de audio: BioCLIP compartido vs. modelo acàºstico dedicado

Definida en [[Modelo de Visión â€” BioCLIP]] §9. Determina si reutilizar el mismo codificador para audio es viable o si hace falta reconsiderarlo.

| Configuración | Top-1 (audio) | Recall@5 |
| --- | --- | --- |
| BioCLIP compartido sobre espectrograma | | |
| Modelo acàºstico dedicado (BirdNET / PANNs / AnuraSet) | | |

## 7. Recuperación vectorial

Métricas de [[Base Vectorial (SQLite-vec)]] e [[Implementación de Triplet Loss]].

| Métrica | Valor |
| --- | --- |
| Recall@1 / @5 / @10 | |
| Precision@5 | |
| Distancia media intra-clase | |
| Distancia media inter-clase | |
| Silhouette score | |

## 8. Open-set

Detalle del protocolo en [[Open-Set Recognition]] §4. **Near-OOD y far-OOD separados**, nunca promediados.

| Método | AUROC near | AUROC far | FPR@95TPR near | FPR@95TPR far | Acc. en conocidos |
| --- | --- | --- | --- | --- | --- |
| MSP (línea base) | | | | | |
| + temperature scaling | | | | | |
| Energy score | | | | | |
| Mahalanobis | | | | | |

## 9. Impacto de la cuantización

Requisito de [[Optimización para Inferencia en Móvil]]: la degradación debe medirse, no suponerse.

| Modelo | Tamaño | Top-1 | Top-3 | F1 macro | Latencia p95 | Î” F1 |
| --- | --- | --- | --- | --- | --- | --- |
| FP32 (referencia) | | | | | | â€” |
| FP16 | | | | | | |
| INT8 | | | | | | |

Criterio de aceptación: Î” F1 â‰¤ 2 %.

## 10. Reglas de higiene experimental

1. El test se toca **lo mínimo posible**. Los hiperparámetros y umbrales se eligen en validación.
2. Cada fila registra versión de modelo y de dataset. Sin eso el nàºmero no significa nada.
3. Ninguna cifra se cita en el documento sin su configuración asociada.
4. Los resultados peores también se registran. Un experimento que falló es información, y omitirlo sesga las conclusiones.
5. Semilla aleatoria fijada y anotada; idealmente, media ± desviación de 3 ejecuciones.



