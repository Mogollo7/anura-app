---
title: "MÃ©tricas Offline"
proyecto: Anura
tipo: evaluaciÃ³n
estado: plantilla-lista-para-resultados
tags: [anura, evaluaciÃ³n, mÃ©tricas, experimentos]
---

# MÃ©tricas Offline

[[Anura â€” Ãndice General]] Â· [[EvaluaciÃ³n y MÃ©tricas â€” Ãndice]] Â· [[Matrices de ConfusiÃ³n]] Â· [[Experimentos y Resultados]] Â· [[Open-Set Recognition]]

> [!abstract] QuÃ© se mide aquÃ­
> Rendimiento en condiciones controladas, sobre el conjunto de test congelado. Es la evaluaciÃ³n que sostiene las afirmaciones del documento de grado; la evaluaciÃ³n en condiciones reales estÃ¡ en [[EvaluaciÃ³n en Campo Real]] y suele dar nÃºmeros peores â€” eso es normal y hay que reportarlo, no esconderlo.

## 1. ConfiguraciÃ³n de la evaluaciÃ³n

Se rellena una vez y se congela. Cambiarla invalida la comparaciÃ³n entre experimentos.

| Campo | Valor |
| --- | --- |
| Conjunto de test | 120 imÃ¡genes originales, sin augmentaciÃ³n |
| Estrategia de split | `GroupSplit` por individuo y localidad |
| NÂº de clases | *(pendiente de fijar â€” ver [[Inconsistencias y Decisiones Pendientes]])* |
| Balance de clases | Desbalanceado (ver [[Listado de Individuos y Arreglo TaxonÃ³mico]]) |
| **MÃ©trica principal** | **F1 macro** |
| MÃ©tricas secundarias | Top-1, Top-3, precisiÃ³n, sensibilidad, consistencia taxonÃ³mica |
| MÃ©trica del objetivo | **Top-3 Accuracy â‰¥ 85 %** (RNF-04) |

> [!important] Por quÃ© F1 macro y no accuracy
> Con clases desbalanceadas, la accuracy premia acertar las especies abundantes. Un modelo que ignore por completo las especies raras â€” que son las que mÃ¡s importan en conservaciÃ³n â€” puede tener buena accuracy y ser inÃºtil. **F1 macro pondera todas las especies por igual** y penaliza el abandono de las minoritarias. La accuracy se reporta igualmente, pero no se optimiza contra ella.

## 2. Resultados globales

Rellenar por cada versiÃ³n evaluada. No sobrescribir filas anteriores: el histÃ³rico es lo que permite ver si se avanza.

| Fecha | VersiÃ³n modelo | VersiÃ³n dataset | Top-1 | Top-3 | F1 macro | PrecisiÃ³n macro | Recall macro | Notas |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | | |

## 3. Resultados por nivel taxonÃ³mico

La clasificaciÃ³n es jerÃ¡rquica, asÃ­ que reportar solo especie oculta informaciÃ³n Ãºtil. Las metas fijadas en [[Estrategia de ConstrucciÃ³n del Dataset]]:

| Nivel | Meta | Top-1 | Top-3 | F1 macro |
| --- | --- | --- | --- | --- |
| Familia | 90â€“95 % | | | |
| GÃ©nero | 80â€“85 % | | | |
| Especie | â‰¥ 80 % | | | |

Y una mÃ©trica propia de este diseÃ±o:

| MÃ©trica | Valor | DefiniciÃ³n |
| --- | --- | --- |
| **Consistencia taxonÃ³mica** | | % de predicciones donde especie â†’ gÃ©nero â†’ familia son coherentes entre sÃ­ |

## 4. Resultados por especie

La tabla que revela dÃ³nde estÃ¡ el problema real. Ordenar por F1 ascendente: las primeras filas son la lista de trabajo.

| Especie | N test | PrecisiÃ³n | Recall | F1 | ConfusiÃ³n principal |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

**Referencia de la Etapa I: 10 especies, exactitud global ~99 %**, con segmentaciÃ³n binaria (individuo vs. fondo) antes de BioCLIP y `GroupSplit` por individuo â€” detalle metodolÃ³gico completo en [[Modelo de VisiÃ³n â€” BioCLIP]] Â§7 y en [[Estrategia de ConstrucciÃ³n del Dataset]]. No es fuga de informaciÃ³n: es el resultado de un pipeline correctamente diseÃ±ado. Pendiente: repetir el mismo protocolo al escalar el catÃ¡logo, para confirmar que se sostiene.

## 5. AblaciÃ³n por modalidad

El experimento clave de [[Arquitectura Multimodal]] Â§4. Todas las filas sobre el **mismo subconjunto** con todas las modalidades disponibles.

| ConfiguraciÃ³n | N | Top-1 | Top-3 | F1 macro | Î” F1 |
| --- | --- | --- | --- | --- | --- |
| Solo imagen | | | | | â€” |
| + contexto geogrÃ¡fico | | | | | |
| + audio | | | | | |
| + audio + contexto | | | | | |
| + morfologÃ­a (plantillas) | | | | | |

## 6. Estrategias de uso de BioCLIP (Ãºnico backbone del proyecto)

BioCLIP es el Ãºnico modelo del proyecto ([[Modelo de VisiÃ³n â€” BioCLIP]]); esta tabla no compara arquitecturas distintas, compara **cuÃ¡nto se le pide a BioCLIP** â€” de menor a mayor coste de entrenamiento.

| ConfiguraciÃ³n | TamaÃ±o | Top-1 | Top-3 | F1 macro | Latencia |
| --- | --- | --- | --- | --- | --- |
| BioCLIP zero-shot (sin entrenar nada) | | | | | |
| BioCLIP congelado + cabezas jerÃ¡rquicas | | | | | |
| BioCLIP + triplet loss (fine-tuning parcial) | | | | | |
| **Etapa I (segmentaciÃ³n binaria + BioCLIP + cabezas)** | | ~99 % | | | |

### ComparaciÃ³n de entrada al modelo (variantes A/B/C)

Definida en [[Modelo de VisiÃ³n â€” BioCLIP]] Â§5. La variante C (recorte + mÃ¡scara binaria) es la que ya produjo el resultado de la Etapa I.

| Variante de entrada | Top-1 | Top-3 | F1 macro |
| --- | --- | --- | --- |
| A â€” Imagen completa | | | |
| B â€” Recorte del individuo | | | |
| **C â€” Recorte + mÃ¡scara binaria** âœ… | ~99 % (Etapa I) | | |

### Rama de audio: BioCLIP compartido vs. modelo acÃºstico dedicado

Definida en [[Modelo de VisiÃ³n â€” BioCLIP]] Â§9. Determina si reutilizar el mismo codificador para audio es viable o si hace falta reconsiderarlo.

| ConfiguraciÃ³n | Top-1 (audio) | Recall@5 |
| --- | --- | --- |
| BioCLIP compartido sobre espectrograma | | |
| Modelo acÃºstico dedicado (BirdNET / PANNs / AnuraSet) | | |

## 7. RecuperaciÃ³n vectorial

MÃ©tricas de [[Base Vectorial (SQLite-vec)]] e [[ImplementaciÃ³n de Triplet Loss]].

| MÃ©trica | Valor |
| --- | --- |
| Recall@1 / @5 / @10 | |
| Precision@5 | |
| Distancia media intra-clase | |
| Distancia media inter-clase | |
| Silhouette score | |

## 8. Open-set

Detalle del protocolo en [[Open-Set Recognition]] Â§4. **Near-OOD y far-OOD separados**, nunca promediados.

| MÃ©todo | AUROC near | AUROC far | FPR@95TPR near | FPR@95TPR far | Acc. en conocidos |
| --- | --- | --- | --- | --- | --- |
| MSP (lÃ­nea base) | | | | | |
| + temperature scaling | | | | | |
| Energy score | | | | | |
| Mahalanobis | | | | | |

## 9. Impacto de la cuantizaciÃ³n

Requisito de [[OptimizaciÃ³n para Inferencia en MÃ³vil]]: la degradaciÃ³n debe medirse, no suponerse.

| Modelo | TamaÃ±o | Top-1 | Top-3 | F1 macro | Latencia p95 | Î” F1 |
| --- | --- | --- | --- | --- | --- | --- |
| FP32 (referencia) | | | | | | â€” |
| FP16 | | | | | | |
| INT8 | | | | | | |

Criterio de aceptaciÃ³n: Î” F1 â‰¤ 2 %.

## 10. Reglas de higiene experimental

1. El test se toca **lo mÃ­nimo posible**. Los hiperparÃ¡metros y umbrales se eligen en validaciÃ³n.
2. Cada fila registra versiÃ³n de modelo y de dataset. Sin eso el nÃºmero no significa nada.
3. Ninguna cifra se cita en el documento sin su configuraciÃ³n asociada.
4. Los resultados peores tambiÃ©n se registran. Un experimento que fallÃ³ es informaciÃ³n, y omitirlo sesga las conclusiones.
5. Semilla aleatoria fijada y anotada; idealmente, media Â± desviaciÃ³n de 3 ejecuciones.



