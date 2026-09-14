---
title: "Implementación de Triplet Loss"
proyecto: Anura
tipo: desarrollo-técnico
estado: redactado-por-completar-con-experimentos
tags: [anura, desarrollo, metric-learning, triplet-loss, embeddings]
---

# Implementación de Triplet Loss

[[Anura â€” àndice General]] · [[Modelo de Visión â€” BioCLIP]] · [[Base Vectorial (SQLite-vec)]] · [[Open-Set Recognition]]

> [!abstract] Para qué sirve aquí
> El *triplet loss* no clasifica: **da forma al espacio de embeddings**. Su objetivo es que dos fotos de la misma especie queden cerca y dos de especies distintas queden lejos, de modo que la bàºsqueda por similitud de la [[Base Vectorial (SQLite-vec)|base vectorial]] y el rechazo de especies desconocidas ([[Open-Set Recognition]]) funcionen sobre una geometría con sentido biológico. Es la pieza que permite **añadir especies nuevas sin reentrenar el clasificador**.

## 1. La formulación

Se toman tres muestras: un **ancla** (A), un **positivo** (P, misma clase que el ancla) y un **negativo** (N, clase distinta). La pérdida exige que el ancla esté más cerca del positivo que del negativo, por al menos un **margen** *m*:

$$\mathcal{L} = \max\big(0,\; d(A,P) - d(A,N) + m\big)$$

Donde *d* es la distancia en el espacio de embeddings (coseno o euclídea sobre vectores L2-normalizados; ambas son equivalentes hasta una transformación monótona si se normaliza).

Leído en palabras: si el negativo ya está suficientemente lejos, la pérdida es cero y ese triplete no aporta gradiente. Solo se aprende de los tripletes que **todavía violan** la condición. De ahí que la elección de tripletes sea el 80 % del problema.

## 2. El problema real: minería de tripletes

Con *N* imágenes hay del orden de *N³* tripletes posibles. La inmensa mayoría son triviales (*Rhinella horribilis* vs. *Dendrobates truncatus*: el modelo ya los separa y la pérdida vale 0). Entrenar con tripletes aleatorios hace que el gradiente se apague casi de inmediato y el modelo no mejore.

Las estrategias, de más ingenua a más usada:

| Estrategia | Qué elige | Comportamiento |
| --- | --- | --- |
| **Aleatoria** | Tripletes al azar | Converge lentísimo, la mayoría no aporta gradiente |
| **Hard negative** | El negativo *más cercano* al ancla | Señal muy fuerte, pero **inestable**: colapsa el espacio si hay ruido de etiquetas |
| **Semi-hard** | Negativo más lejos que el positivo, pero dentro del margen | Estrategia clásica de FaceNet; buen equilibrio |
| **Batch-hard** âœ… | Dentro de cada lote: el positivo más lejano y el negativo más cercano | **Recomendada.** Estable, eficiente, es el estándar actual |

**Batch-hard** requiere construir los lotes de forma específica: *P* clases à— *K* imágenes por clase (por ejemplo 8 especies à— 4 imágenes = lote de 32). No sirve un lote aleatorio, porque puede no contener ningàºn par positivo.

> [!danger] Riesgo específico de este dataset
> El *hard negative mining* busca el negativo más difícil. En este proyecto, los negativos más difíciles serán sistemáticamente *Pristimantis paisa* vs. *Pristimantis penelopus* â€” que es exactamente donde la Etapa I ya mostró peor F1 (0,86). Eso es bueno (el modelo se enfoca donde duele) **siempre que las etiquetas sean correctas**. Si hay una sola imagen mal identificada dentro de *Pristimantis*, el *hard mining* la elegirá una y otra vez como el negativo más difícil y arrastrará el espacio hacia el error. Antes de activar *hard mining*, la verificación taxonómica de ese género tiene que estar cerrada.

## 3. Dónde encaja en la arquitectura de Anura

El triplet loss **no sustituye** a la clasificación jerárquica; la complementa. Configuración recomendada, entrenamiento multi-tarea:

```
                  Imagen (recorte segmentado)
                            â†“
              BioCLIP ViT-B/16  (àºltimos bloques descongelados)
                            â†“
                   Embedding 512-d  (L2-normalizado)
                    â†™               â†˜
       Triplet loss                Cabezas jerárquicas
   (forma del espacio)          Familia · Género · Especie
                                (cross-entropy)

        Pérdida total = Î» · L_triplet + (1-Î») · L_clasificación
```

`Î»` es un hiperparámetro a barrer (valores típicos 0,3â€“0,5). La razón de combinar ambas: el triplet loss por sí solo produce un espacio bien organizado pero sin calibración de probabilidad, y las cabezas jerárquicas por sí solas producen probabilidades pero un espacio con peor estructura para bàºsqueda por similitud. Anura necesita las dos cosas.

### Variante jerárquica (opcional, más ambiciosa)

Se puede modular el margen segàºn la distancia taxonómica: penalizar más confundir familias que confundir especies del mismo género.

| Relación entre ancla y negativo | Margen sugerido |
| --- | --- |
| Misma especie | â€” (es positivo) |
| Mismo género, distinta especie | m = 0,1 (pequeño: son legítimamente parecidas) |
| Misma familia, distinto género | m = 0,3 |
| Distinta familia | m = 0,5 (grande: no deberían confundirse nunca) |

Esto codifica la taxonomía **en la geometría** del espacio, y es un aporte metodológico defendible en el documento de grado.

## 4. Configuración de referencia

| Hiperparámetro | Valor inicial | Nota |
| --- | --- | --- |
| Margen *m* | 0,2 (embeddings normalizados) | Barrer 0,1 â€“ 0,5 |
| Distancia | Coseno sobre vectores L2-normalizados | Coherente con la métrica de la base vectorial |
| Composición del lote | P=8 clases à— K=4 imágenes | Kâ‰¥4 es necesario para batch-hard |
| Minería | Batch-hard | Empezar en semi-hard si hay inestabilidad |
| Bloques descongelados | àšltimos 2â€“4 del ViT | Nunca el modelo completo con este tamaño de dataset |
| Tasa de aprendizaje | 1e-5 (backbone) / 1e-4 (cabezas) | Muy baja en el backbone: es un modelo preentrenado valioso |

**Agrupación obligatoria por individuo.** El positivo no puede ser otra foto del **mismo individuo** en la misma sesión, o el modelo aprende a reconocer ese ejemplar concreto (color exacto, cicatriz, sustrato) en vez de la especie. El positivo ideal es otro individuo de la misma especie. Esto conecta directamente con las reglas anti-fuga de [[Estrategia de Construcción del Dataset]].

## 5. Cómo se evalàºa que funcionó

El triplet loss no se evalàºa con accuracy. Las métricas correctas son de recuperación y de estructura del espacio:

- **Recall@K / Precision@K** sobre la base vectorial (¿las K observaciones más similares son de la especie correcta?).
- **Distancia intra-clase media vs. inter-clase media** â€” debe aumentar la separación relativa.
- **Silhouette score** sobre los embeddings de test.
- **AUROC de open-set** ([[Open-Set Recognition]]): un espacio mejor formado mejora directamente la detección de especies desconocidas. Esta es, probablemente, la justificación más fuerte para usar triplet loss en Anura.

Registrar en [[Métricas Offline]] y [[Experimentos y Resultados]].

## 6. Alternativas que conviene considerar antes de comprometerse

El triplet loss es de 2015 y tiene sucesores más estables y con menos hiperparámetros:

| Método | Ventaja sobre triplet |
| --- | --- |
| **ArcFace / CosFace** | Margen angular sobre la clasificación; no necesita minería de tripletes. Muy usado hoy en reconocimiento fino. |
| **SupCon** (contrastivo supervisado) | Usa todos los positivos del lote a la vez, no uno; converge mejor con lotes pequeños. |
| **Sin metric learning** | Con 550 imágenes originales, los embeddings congelados de BioCLIP pueden ser suficientes. **Medirlo antes de añadir complejidad.** |

> [!tip] Orden de trabajo recomendado
> 1. Medir la recuperación con embeddings BioCLIP **congelados** (sin entrenar nada).
> 2. Solo si Recall@5 es insuficiente, añadir triplet loss o ArcFace.
> 3. Comparar y quedarse con lo que mejore de verdad, no con lo que suene mejor.

## 7. Qué falta por decidir o medir

- [ ] Medir la línea base sin metric learning (paso 1 de arriba).
- [ ] Cerrar la verificación taxonómica de *Pristimantis* antes de activar hard mining.
- [ ] Barrer margen y Î».
- [ ] Comparar triplet vs. ArcFace vs. SupCon si hay tiempo.

## Referencias

- Schroff, Kalenichenko & Philbin (2015). *FaceNet: A Unified Embedding for Face Recognition and Clustering*. [arXiv:1503.03832](https://arxiv.org/abs/1503.03832)
- Hermans, Beyer & Leibe (2017). *In Defense of the Triplet Loss for Person Re-Identification* â€” origen del *batch-hard*. [arXiv:1703.07737](https://arxiv.org/abs/1703.07737)
- Deng et al. (2019). *ArcFace: Additive Angular Margin Loss*. [arXiv:1801.07698](https://arxiv.org/abs/1801.07698)
- Khosla et al. (2020). *Supervised Contrastive Learning*. [arXiv:2004.11362](https://arxiv.org/abs/2004.11362)

Ver también: [[Bibliografía]]



