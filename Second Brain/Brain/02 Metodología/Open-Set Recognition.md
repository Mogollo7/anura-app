---
title: "Open-Set Recognition"
proyecto: Anura
tipo: metodología
estado: redactado
tags: [anura, metodología, open-set, ood, incertidumbre]
---

# Open-Set Recognition

[[Anura â€” àndice General]] · [[Pipeline del Sistema]] · [[Base Vectorial (SQLite-vec)]] · [[Métricas Offline]] · [[Modelo de Visión â€” BioCLIP]]

> [!abstract] El problema
> Colombia tiene más de 900 especies de anuros; Anura conocerá unas decenas. La probabilidad de que un usuario fotografíe una especie que el modelo **no conoce** no es un caso extremo: es el caso más frecuente. Un clasificador convencional siempre devuelve una de sus clases, con confianza alta, aunque le muestres un insecto. Open-set recognition es la capacidad de responder **"no lo sé / no está en mi catálogo"**.

Está recogido como objetivo específico y en la [[Estrategia de Construcción del Dataset]]; esta nota concreta cómo implementarlo y evaluarlo.

## 1. Definir "desconocido"

Cuatro casos distintos que el sistema debe manejar y que no son el mismo problema:

| Caso | Ejemplo | Respuesta esperada |
| --- | --- | --- |
| **Especie de anuro fuera del catálogo** | *Pristimantis* no incluido | âš ï¸ "Anuro no registrado" â€” idealmente con familia/género si hay confianza |
| **Otro anfibio** | Salamandra, cecilia | "No es un anuro" |
| **Otro organismo u objeto** | Insecto, hoja, mano | "No se detectó un anuro" (lo resuelve la segmentación) |
| **Imagen inservible** | Desenfocada, oscura | "Repetir la toma" (control de calidad previo) |

Distinguirlos importa porque cada uno se resuelve en una etapa distinta del pipeline: los dos àºltimos, en la segmentación y el control de calidad; los dos primeros, aquí.

> [!tip] El rechazo jerárquico es más àºtil que el binario
> Es mucho más valioso decir *"Familia Hylidae con alta confianza, género probable Boana, especie no determinable"* que un simple "desconocido". La estructura jerárquica del modelo permite rechazar **en el nivel donde la evidencia se agota**, y eso es exactamente lo que hace un herpetólogo cuando anota `Pristimantis sp.`

## 2. Métodos, y cuál usar aquí

### 2.1 MSP â€” máxima probabilidad softmax (línea base)

Umbral sobre la probabilidad máxima. Sencillo y es la línea base obligatoria de la literatura, pero **las redes profundas son notoriamente sobreconfiadas**: pueden dar 0,95 a una especie que nunca vieron. No es suficiente por sí solo.

### 2.2 Temperature scaling (calibración)

No detecta desconocidos: **hace fiables las probabilidades**. Se ajusta un àºnico parámetro *T* en el conjunto de validación dividiendo los logits antes del softmax. Barato, no cambia el ranking, y mejora todo lo que dependa de umbrales â€” incluida la fusión multimodal. Debe hacerse siempre. Ya está previsto en la estrategia de dataset.

### 2.3 Distancia en el espacio de embeddings âœ…

El enfoque natural para Anura, porque ya existe la [[Base Vectorial (SQLite-vec)|base vectorial]]:

```
embedding de la observación
        â†“
distancia al centroide de cada clase conocida
   (o al k-ésimo vecino más cercano)
        â†“
si  d_min > umbral  â†’  desconocido
```

Dos variantes:

- **Distancia coseno al centroide** â€” simple, rápida, funciona bien si [[Implementación de Triplet Loss|triplet loss]] ha compactado las clases.
- **Distancia de Mahalanobis** â€” tiene en cuenta la covarianza de cada clase, no solo la media: modela que unas especies son visualmente más dispersas que otras (*Pristimantis*, con su polimorfismo, frente a *Dendrobates truncatus*). Suele superar claramente a la distancia euclídea y es de las opciones más sólidas en los estudios comparativos de OOD.

### 2.4 Energy score

Puntuación derivada del `logsumexp` de los logits escalados por temperatura. Mejora consistentemente sobre MSP y no requiere reentrenar: se calcula sobre un modelo ya entrenado. Buen complemento barato.

### 2.5 Exposición a datos externos (outlier exposure)

Entrenar explícitamente con el conjunto open-set descrito en la estrategia de dataset (otras familias de anuros, otros anfibios, insectos, hojarasca) para que el modelo aprenda a producir baja confianza en ellos. Es lo que más mejora la detección, y el proyecto **ya tiene planificada la recolección de ese conjunto** â€” conviene no desperdiciarlo.

> [!important] Combinación recomendada
> 1. **Temperature scaling** siempre (calibración de base).
> 2. **Mahalanobis sobre embeddings** como detector principal.
> 3. **Energy score** como señal secundaria.
> 4. **Coherencia con la evidencia morfológica**: si la comparación contra plantillas produce varias contradicciones âŒ, es una señal fuerte de que el candidato no es correcto, independientemente de la probabilidad.
> 5. **Outlier exposure** cuando el conjunto open-set esté recolectado.
>
> Ninguna de las cuatro primeras exige reentrenar el modelo principal, lo cual las hace realistas dentro del alcance de un TFG.

## 3. Umbrales: cómo elegirlos sin engañarse

El umbral define el intercambio entre dos errores con costes muy distintos:

| Error | Consecuencia |
| --- | --- |
| **Falso conocido** (dice "es X" y no lo es) | Registro erróneo en la base de biodiversidad. Grave: contamina datos científicos y erosiona la confianza del experto. |
| **Falso desconocido** (rechaza una especie que sí conoce) | El usuario no obtiene identificación. Molesto, pero recuperable. |

Para un sistema de apoyo a la identificación biológica, **el primero es peor**. El umbral debe elegirse conservador.

Procedimiento correcto:
1. Fijar un objetivo operativo (por ejemplo, TPR â‰¥ 95 % sobre especies conocidas).
2. Elegir el umbral **en validación** que lo cumpla.
3. Reportar el rendimiento resultante **en test**, sin volver a tocarlo.

Ajustar el umbral mirando el test es la forma más comàºn de publicar un resultado que no se reproduce en campo.

## 4. Métricas de evaluación

Accuracy no aplica: es un problema de detección, no de clasificación.

| Métrica | Qué mide | Por qué importa aquí |
| --- | --- | --- |
| **AUROC** | Separación conocido/desconocido a todos los umbrales | Métrica principal, independiente del umbral |
| **FPR@95TPR** | Desconocidos aceptados cuando se acierta el 95 % de conocidos | La más honesta operativamente |
| **AUPR** | àrea precisión-recall | Robusta cuando las clases están desbalanceadas |
| **Accuracy en conocidos** | Que el rechazo no degrade el caso normal | Control de que no se rompió lo que funcionaba |
| **Coherencia jerárquica del rechazo** | ¿Acierta la familia aunque rechace la especie? | Específica de Anura y muy valiosa |

### Protocolo de evaluación

```
Conjunto conocido:      test estándar (especies del catálogo)
Conjunto desconocido:   â”Œ Near-OOD: anuros de otras especies/géneros próximos
                        â”” Far-OOD:  otros anfibios, insectos, hojarasca, objetos
```

Separar **near-OOD** de **far-OOD** es imprescindible: detectar que una hoja no es una rana es fácil y da nàºmeros excelentes que no significan nada. Lo difícil â€” y lo que realmente pasa en campo â€” es detectar que ese *Pristimantis* no es ninguno de los del catálogo. Reportar ambos por separado; si solo se reporta el promedio, el resultado es engañoso.

## 5. Cómo se presenta al usuario

```
âš ï¸  Especie no registrada

Coincide con: Familia Hylidae (confianza alta)
              Género Boana (confianza media)

No hay ninguna especie del catálogo con evidencia suficiente.

Observaciones más parecidas (referencia, no identificación):
   Boana lanciformis    0,71
   Boana punctata       0,68

â†’ Guardar como "pendiente de verificación experta"
```

Tres decisiones de diseño en esa pantalla:

1. **No es un error, es un resultado.** El tono debe reflejarlo: el sistema está haciendo su trabajo.
2. **Se ofrece lo que sí se sabe** (familia, género), no un vacío.
3. **Se abre la vía de curaduría**: una observación rechazada es potencialmente un registro valioso â€” una especie nueva para el catálogo o incluso para la zona. Enlaza con el flujo de validación experta de [[Historias de Usuario]] (HU-03) y con [[Escalabilidad]].

## 6. Qué falta por decidir o medir

- [ ] Recolectar y versionar el conjunto open-set (near-OOD y far-OOD por separado).
- [ ] Implementar temperature scaling y reportar el error de calibración antes/después.
- [ ] Comparar MSP vs. Energy vs. Mahalanobis sobre los mismos conjuntos.
- [ ] Fijar el umbral operativo en validación y congelarlo.
- [ ] Definir el criterio de rechazo jerárquico (a qué nivel se corta).

## Referencias

- Hendrycks & Gimpel (2017). *A Baseline for Detecting Misclassified and OOD Examples* (MSP). [arXiv:1610.02136](https://arxiv.org/abs/1610.02136)
- Liu et al. (2020). *Energy-based Out-of-distribution Detection*. [arXiv:2010.03759](https://arxiv.org/abs/2010.03759)
- Lee et al. (2018). *A Simple Unified Framework for Detecting OOD Samples* (Mahalanobis). [arXiv:1807.03888](https://arxiv.org/abs/1807.03888)
- Guo et al. (2017). *On Calibration of Modern Neural Networks* (temperature scaling). [arXiv:1706.04599](https://arxiv.org/abs/1706.04599)
- Zhang et al. *OpenOOD* â€” benchmark comparativo de métodos OOD. [github.com/Jingkang50/OpenOOD](https://github.com/Jingkang50/OpenOOD)



