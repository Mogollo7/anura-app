---
title: "ImplementaciÃ³n de Triplet Loss"
proyecto: Anura
tipo: desarrollo-tÃ©cnico
estado: redactado-por-completar-con-experimentos
tags: [anura, desarrollo, metric-learning, triplet-loss, embeddings]
---

# ImplementaciÃ³n de Triplet Loss

[[Anura â€” Ãndice General]] Â· [[Modelo de VisiÃ³n â€” BioCLIP]] Â· [[Base Vectorial (SQLite-vec)]] Â· [[Open-Set Recognition]]

> [!abstract] Para quÃ© sirve aquÃ­
> El *triplet loss* no clasifica: **da forma al espacio de embeddings**. Su objetivo es que dos fotos de la misma especie queden cerca y dos de especies distintas queden lejos, de modo que la bÃºsqueda por similitud de la [[Base Vectorial (SQLite-vec)|base vectorial]] y el rechazo de especies desconocidas ([[Open-Set Recognition]]) funcionen sobre una geometrÃ­a con sentido biolÃ³gico. Es la pieza que permite **aÃ±adir especies nuevas sin reentrenar el clasificador**.

## 1. La formulaciÃ³n

Se toman tres muestras: un **ancla** (A), un **positivo** (P, misma clase que el ancla) y un **negativo** (N, clase distinta). La pÃ©rdida exige que el ancla estÃ© mÃ¡s cerca del positivo que del negativo, por al menos un **margen** *m*:

$$\mathcal{L} = \max\big(0,\; d(A,P) - d(A,N) + m\big)$$

Donde *d* es la distancia en el espacio de embeddings (coseno o euclÃ­dea sobre vectores L2-normalizados; ambas son equivalentes hasta una transformaciÃ³n monÃ³tona si se normaliza).

LeÃ­do en palabras: si el negativo ya estÃ¡ suficientemente lejos, la pÃ©rdida es cero y ese triplete no aporta gradiente. Solo se aprende de los tripletes que **todavÃ­a violan** la condiciÃ³n. De ahÃ­ que la elecciÃ³n de tripletes sea el 80 % del problema.

## 2. El problema real: minerÃ­a de tripletes

Con *N* imÃ¡genes hay del orden de *NÂ³* tripletes posibles. La inmensa mayorÃ­a son triviales (*Rhinella horribilis* vs. *Dendrobates truncatus*: el modelo ya los separa y la pÃ©rdida vale 0). Entrenar con tripletes aleatorios hace que el gradiente se apague casi de inmediato y el modelo no mejore.

Las estrategias, de mÃ¡s ingenua a mÃ¡s usada:

| Estrategia | QuÃ© elige | Comportamiento |
| --- | --- | --- |
| **Aleatoria** | Tripletes al azar | Converge lentÃ­simo, la mayorÃ­a no aporta gradiente |
| **Hard negative** | El negativo *mÃ¡s cercano* al ancla | SeÃ±al muy fuerte, pero **inestable**: colapsa el espacio si hay ruido de etiquetas |
| **Semi-hard** | Negativo mÃ¡s lejos que el positivo, pero dentro del margen | Estrategia clÃ¡sica de FaceNet; buen equilibrio |
| **Batch-hard** âœ… | Dentro de cada lote: el positivo mÃ¡s lejano y el negativo mÃ¡s cercano | **Recomendada.** Estable, eficiente, es el estÃ¡ndar actual |

**Batch-hard** requiere construir los lotes de forma especÃ­fica: *P* clases Ã— *K* imÃ¡genes por clase (por ejemplo 8 especies Ã— 4 imÃ¡genes = lote de 32). No sirve un lote aleatorio, porque puede no contener ningÃºn par positivo.

> [!danger] Riesgo especÃ­fico de este dataset
> El *hard negative mining* busca el negativo mÃ¡s difÃ­cil. En este proyecto, los negativos mÃ¡s difÃ­ciles serÃ¡n sistemÃ¡ticamente *Pristimantis paisa* vs. *Pristimantis penelopus* â€” que es exactamente donde la Etapa I ya mostrÃ³ peor F1 (0,86). Eso es bueno (el modelo se enfoca donde duele) **siempre que las etiquetas sean correctas**. Si hay una sola imagen mal identificada dentro de *Pristimantis*, el *hard mining* la elegirÃ¡ una y otra vez como el negativo mÃ¡s difÃ­cil y arrastrarÃ¡ el espacio hacia el error. Antes de activar *hard mining*, la verificaciÃ³n taxonÃ³mica de ese gÃ©nero tiene que estar cerrada.

## 3. DÃ³nde encaja en la arquitectura de Anura

El triplet loss **no sustituye** a la clasificaciÃ³n jerÃ¡rquica; la complementa. ConfiguraciÃ³n recomendada, entrenamiento multi-tarea:

```
                  Imagen (recorte segmentado)
                            â†“
              BioCLIP ViT-B/16  (Ãºltimos bloques descongelados)
                            â†“
                   Embedding 512-d  (L2-normalizado)
                    â†™               â†˜
       Triplet loss                Cabezas jerÃ¡rquicas
   (forma del espacio)          Familia Â· GÃ©nero Â· Especie
                                (cross-entropy)

        PÃ©rdida total = Î» Â· L_triplet + (1-Î») Â· L_clasificaciÃ³n
```

`Î»` es un hiperparÃ¡metro a barrer (valores tÃ­picos 0,3â€“0,5). La razÃ³n de combinar ambas: el triplet loss por sÃ­ solo produce un espacio bien organizado pero sin calibraciÃ³n de probabilidad, y las cabezas jerÃ¡rquicas por sÃ­ solas producen probabilidades pero un espacio con peor estructura para bÃºsqueda por similitud. Anura necesita las dos cosas.

### Variante jerÃ¡rquica (opcional, mÃ¡s ambiciosa)

Se puede modular el margen segÃºn la distancia taxonÃ³mica: penalizar mÃ¡s confundir familias que confundir especies del mismo gÃ©nero.

| RelaciÃ³n entre ancla y negativo | Margen sugerido |
| --- | --- |
| Misma especie | â€” (es positivo) |
| Mismo gÃ©nero, distinta especie | m = 0,1 (pequeÃ±o: son legÃ­timamente parecidas) |
| Misma familia, distinto gÃ©nero | m = 0,3 |
| Distinta familia | m = 0,5 (grande: no deberÃ­an confundirse nunca) |

Esto codifica la taxonomÃ­a **en la geometrÃ­a** del espacio, y es un aporte metodolÃ³gico defendible en el documento de grado.

## 4. ConfiguraciÃ³n de referencia

| HiperparÃ¡metro | Valor inicial | Nota |
| --- | --- | --- |
| Margen *m* | 0,2 (embeddings normalizados) | Barrer 0,1 â€“ 0,5 |
| Distancia | Coseno sobre vectores L2-normalizados | Coherente con la mÃ©trica de la base vectorial |
| ComposiciÃ³n del lote | P=8 clases Ã— K=4 imÃ¡genes | Kâ‰¥4 es necesario para batch-hard |
| MinerÃ­a | Batch-hard | Empezar en semi-hard si hay inestabilidad |
| Bloques descongelados | Ãšltimos 2â€“4 del ViT | Nunca el modelo completo con este tamaÃ±o de dataset |
| Tasa de aprendizaje | 1e-5 (backbone) / 1e-4 (cabezas) | Muy baja en el backbone: es un modelo preentrenado valioso |

**AgrupaciÃ³n obligatoria por individuo.** El positivo no puede ser otra foto del **mismo individuo** en la misma sesiÃ³n, o el modelo aprende a reconocer ese ejemplar concreto (color exacto, cicatriz, sustrato) en vez de la especie. El positivo ideal es otro individuo de la misma especie. Esto conecta directamente con las reglas anti-fuga de [[Estrategia de ConstrucciÃ³n del Dataset]].

## 5. CÃ³mo se evalÃºa que funcionÃ³

El triplet loss no se evalÃºa con accuracy. Las mÃ©tricas correctas son de recuperaciÃ³n y de estructura del espacio:

- **Recall@K / Precision@K** sobre la base vectorial (Â¿las K observaciones mÃ¡s similares son de la especie correcta?).
- **Distancia intra-clase media vs. inter-clase media** â€” debe aumentar la separaciÃ³n relativa.
- **Silhouette score** sobre los embeddings de test.
- **AUROC de open-set** ([[Open-Set Recognition]]): un espacio mejor formado mejora directamente la detecciÃ³n de especies desconocidas. Esta es, probablemente, la justificaciÃ³n mÃ¡s fuerte para usar triplet loss en Anura.

Registrar en [[MÃ©tricas Offline]] y [[Experimentos y Resultados]].

## 6. Alternativas que conviene considerar antes de comprometerse

El triplet loss es de 2015 y tiene sucesores mÃ¡s estables y con menos hiperparÃ¡metros:

| MÃ©todo | Ventaja sobre triplet |
| --- | --- |
| **ArcFace / CosFace** | Margen angular sobre la clasificaciÃ³n; no necesita minerÃ­a de tripletes. Muy usado hoy en reconocimiento fino. |
| **SupCon** (contrastivo supervisado) | Usa todos los positivos del lote a la vez, no uno; converge mejor con lotes pequeÃ±os. |
| **Sin metric learning** | Con 550 imÃ¡genes originales, los embeddings congelados de BioCLIP pueden ser suficientes. **Medirlo antes de aÃ±adir complejidad.** |

> [!tip] Orden de trabajo recomendado
> 1. Medir la recuperaciÃ³n con embeddings BioCLIP **congelados** (sin entrenar nada).
> 2. Solo si Recall@5 es insuficiente, aÃ±adir triplet loss o ArcFace.
> 3. Comparar y quedarse con lo que mejore de verdad, no con lo que suene mejor.

## 7. QuÃ© falta por decidir o medir

- [ ] Medir la lÃ­nea base sin metric learning (paso 1 de arriba).
- [ ] Cerrar la verificaciÃ³n taxonÃ³mica de *Pristimantis* antes de activar hard mining.
- [ ] Barrer margen y Î».
- [ ] Comparar triplet vs. ArcFace vs. SupCon si hay tiempo.

## Referencias

- Schroff, Kalenichenko & Philbin (2015). *FaceNet: A Unified Embedding for Face Recognition and Clustering*. [arXiv:1503.03832](https://arxiv.org/abs/1503.03832)
- Hermans, Beyer & Leibe (2017). *In Defense of the Triplet Loss for Person Re-Identification* â€” origen del *batch-hard*. [arXiv:1703.07737](https://arxiv.org/abs/1703.07737)
- Deng et al. (2019). *ArcFace: Additive Angular Margin Loss*. [arXiv:1801.07698](https://arxiv.org/abs/1801.07698)
- Khosla et al. (2020). *Supervised Contrastive Learning*. [arXiv:2004.11362](https://arxiv.org/abs/2004.11362)

Ver tambiÃ©n: [[BibliografÃ­a]]



