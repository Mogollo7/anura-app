---
title: "Open-Set Recognition"
proyecto: Anura
tipo: metodologÃ­a
estado: redactado
tags: [anura, metodologÃ­a, open-set, ood, incertidumbre]
---

# Open-Set Recognition

[[Anura â€” Ãndice General]] Â· [[Pipeline del Sistema]] Â· [[Base Vectorial (SQLite-vec)]] Â· [[MÃ©tricas Offline]] Â· [[Modelo de VisiÃ³n â€” BioCLIP]]

> [!abstract] El problema
> Colombia tiene mÃ¡s de 900 especies de anuros; Anura conocerÃ¡ unas decenas. La probabilidad de que un usuario fotografÃ­e una especie que el modelo **no conoce** no es un caso extremo: es el caso mÃ¡s frecuente. Un clasificador convencional siempre devuelve una de sus clases, con confianza alta, aunque le muestres un insecto. Open-set recognition es la capacidad de responder **"no lo sÃ© / no estÃ¡ en mi catÃ¡logo"**.

EstÃ¡ recogido como objetivo especÃ­fico y en la [[Estrategia de ConstrucciÃ³n del Dataset]]; esta nota concreta cÃ³mo implementarlo y evaluarlo.

## 1. Definir "desconocido"

Cuatro casos distintos que el sistema debe manejar y que no son el mismo problema:

| Caso | Ejemplo | Respuesta esperada |
| --- | --- | --- |
| **Especie de anuro fuera del catÃ¡logo** | *Pristimantis* no incluido | âš ï¸ "Anuro no registrado" â€” idealmente con familia/gÃ©nero si hay confianza |
| **Otro anfibio** | Salamandra, cecilia | "No es un anuro" |
| **Otro organismo u objeto** | Insecto, hoja, mano | "No se detectÃ³ un anuro" (lo resuelve la segmentaciÃ³n) |
| **Imagen inservible** | Desenfocada, oscura | "Repetir la toma" (control de calidad previo) |

Distinguirlos importa porque cada uno se resuelve en una etapa distinta del pipeline: los dos Ãºltimos, en la segmentaciÃ³n y el control de calidad; los dos primeros, aquÃ­.

> [!tip] El rechazo jerÃ¡rquico es mÃ¡s Ãºtil que el binario
> Es mucho mÃ¡s valioso decir *"Familia Hylidae con alta confianza, gÃ©nero probable Boana, especie no determinable"* que un simple "desconocido". La estructura jerÃ¡rquica del modelo permite rechazar **en el nivel donde la evidencia se agota**, y eso es exactamente lo que hace un herpetÃ³logo cuando anota `Pristimantis sp.`

## 2. MÃ©todos, y cuÃ¡l usar aquÃ­

### 2.1 MSP â€” mÃ¡xima probabilidad softmax (lÃ­nea base)

Umbral sobre la probabilidad mÃ¡xima. Sencillo y es la lÃ­nea base obligatoria de la literatura, pero **las redes profundas son notoriamente sobreconfiadas**: pueden dar 0,95 a una especie que nunca vieron. No es suficiente por sÃ­ solo.

### 2.2 Temperature scaling (calibraciÃ³n)

No detecta desconocidos: **hace fiables las probabilidades**. Se ajusta un Ãºnico parÃ¡metro *T* en el conjunto de validaciÃ³n dividiendo los logits antes del softmax. Barato, no cambia el ranking, y mejora todo lo que dependa de umbrales â€” incluida la fusiÃ³n multimodal. Debe hacerse siempre. Ya estÃ¡ previsto en la estrategia de dataset.

### 2.3 Distancia en el espacio de embeddings âœ…

El enfoque natural para Anura, porque ya existe la [[Base Vectorial (SQLite-vec)|base vectorial]]:

```
embedding de la observaciÃ³n
        â†“
distancia al centroide de cada clase conocida
   (o al k-Ã©simo vecino mÃ¡s cercano)
        â†“
si  d_min > umbral  â†’  desconocido
```

Dos variantes:

- **Distancia coseno al centroide** â€” simple, rÃ¡pida, funciona bien si [[ImplementaciÃ³n de Triplet Loss|triplet loss]] ha compactado las clases.
- **Distancia de Mahalanobis** â€” tiene en cuenta la covarianza de cada clase, no solo la media: modela que unas especies son visualmente mÃ¡s dispersas que otras (*Pristimantis*, con su polimorfismo, frente a *Dendrobates truncatus*). Suele superar claramente a la distancia euclÃ­dea y es de las opciones mÃ¡s sÃ³lidas en los estudios comparativos de OOD.

### 2.4 Energy score

PuntuaciÃ³n derivada del `logsumexp` de los logits escalados por temperatura. Mejora consistentemente sobre MSP y no requiere reentrenar: se calcula sobre un modelo ya entrenado. Buen complemento barato.

### 2.5 ExposiciÃ³n a datos externos (outlier exposure)

Entrenar explÃ­citamente con el conjunto open-set descrito en la estrategia de dataset (otras familias de anuros, otros anfibios, insectos, hojarasca) para que el modelo aprenda a producir baja confianza en ellos. Es lo que mÃ¡s mejora la detecciÃ³n, y el proyecto **ya tiene planificada la recolecciÃ³n de ese conjunto** â€” conviene no desperdiciarlo.

> [!important] CombinaciÃ³n recomendada
> 1. **Temperature scaling** siempre (calibraciÃ³n de base).
> 2. **Mahalanobis sobre embeddings** como detector principal.
> 3. **Energy score** como seÃ±al secundaria.
> 4. **Coherencia con la evidencia morfolÃ³gica**: si la comparaciÃ³n contra plantillas produce varias contradicciones âŒ, es una seÃ±al fuerte de que el candidato no es correcto, independientemente de la probabilidad.
> 5. **Outlier exposure** cuando el conjunto open-set estÃ© recolectado.
>
> Ninguna de las cuatro primeras exige reentrenar el modelo principal, lo cual las hace realistas dentro del alcance de un TFG.

## 3. Umbrales: cÃ³mo elegirlos sin engaÃ±arse

El umbral define el intercambio entre dos errores con costes muy distintos:

| Error | Consecuencia |
| --- | --- |
| **Falso conocido** (dice "es X" y no lo es) | Registro errÃ³neo en la base de biodiversidad. Grave: contamina datos cientÃ­ficos y erosiona la confianza del experto. |
| **Falso desconocido** (rechaza una especie que sÃ­ conoce) | El usuario no obtiene identificaciÃ³n. Molesto, pero recuperable. |

Para un sistema de apoyo a la identificaciÃ³n biolÃ³gica, **el primero es peor**. El umbral debe elegirse conservador.

Procedimiento correcto:
1. Fijar un objetivo operativo (por ejemplo, TPR â‰¥ 95 % sobre especies conocidas).
2. Elegir el umbral **en validaciÃ³n** que lo cumpla.
3. Reportar el rendimiento resultante **en test**, sin volver a tocarlo.

Ajustar el umbral mirando el test es la forma mÃ¡s comÃºn de publicar un resultado que no se reproduce en campo.

## 4. MÃ©tricas de evaluaciÃ³n

Accuracy no aplica: es un problema de detecciÃ³n, no de clasificaciÃ³n.

| MÃ©trica | QuÃ© mide | Por quÃ© importa aquÃ­ |
| --- | --- | --- |
| **AUROC** | SeparaciÃ³n conocido/desconocido a todos los umbrales | MÃ©trica principal, independiente del umbral |
| **FPR@95TPR** | Desconocidos aceptados cuando se acierta el 95 % de conocidos | La mÃ¡s honesta operativamente |
| **AUPR** | Ãrea precisiÃ³n-recall | Robusta cuando las clases estÃ¡n desbalanceadas |
| **Accuracy en conocidos** | Que el rechazo no degrade el caso normal | Control de que no se rompiÃ³ lo que funcionaba |
| **Coherencia jerÃ¡rquica del rechazo** | Â¿Acierta la familia aunque rechace la especie? | EspecÃ­fica de Anura y muy valiosa |

### Protocolo de evaluaciÃ³n

```
Conjunto conocido:      test estÃ¡ndar (especies del catÃ¡logo)
Conjunto desconocido:   â”Œ Near-OOD: anuros de otras especies/gÃ©neros prÃ³ximos
                        â”” Far-OOD:  otros anfibios, insectos, hojarasca, objetos
```

Separar **near-OOD** de **far-OOD** es imprescindible: detectar que una hoja no es una rana es fÃ¡cil y da nÃºmeros excelentes que no significan nada. Lo difÃ­cil â€” y lo que realmente pasa en campo â€” es detectar que ese *Pristimantis* no es ninguno de los del catÃ¡logo. Reportar ambos por separado; si solo se reporta el promedio, el resultado es engaÃ±oso.

## 5. CÃ³mo se presenta al usuario

```
âš ï¸  Especie no registrada

Coincide con: Familia Hylidae (confianza alta)
              GÃ©nero Boana (confianza media)

No hay ninguna especie del catÃ¡logo con evidencia suficiente.

Observaciones mÃ¡s parecidas (referencia, no identificaciÃ³n):
   Boana lanciformis    0,71
   Boana punctata       0,68

â†’ Guardar como "pendiente de verificaciÃ³n experta"
```

Tres decisiones de diseÃ±o en esa pantalla:

1. **No es un error, es un resultado.** El tono debe reflejarlo: el sistema estÃ¡ haciendo su trabajo.
2. **Se ofrece lo que sÃ­ se sabe** (familia, gÃ©nero), no un vacÃ­o.
3. **Se abre la vÃ­a de curadurÃ­a**: una observaciÃ³n rechazada es potencialmente un registro valioso â€” una especie nueva para el catÃ¡logo o incluso para la zona. Enlaza con el flujo de validaciÃ³n experta de [[Historias de Usuario]] (HU-03) y con [[Escalabilidad]].

## 6. QuÃ© falta por decidir o medir

- [ ] Recolectar y versionar el conjunto open-set (near-OOD y far-OOD por separado).
- [ ] Implementar temperature scaling y reportar el error de calibraciÃ³n antes/despuÃ©s.
- [ ] Comparar MSP vs. Energy vs. Mahalanobis sobre los mismos conjuntos.
- [ ] Fijar el umbral operativo en validaciÃ³n y congelarlo.
- [ ] Definir el criterio de rechazo jerÃ¡rquico (a quÃ© nivel se corta).

## Referencias

- Hendrycks & Gimpel (2017). *A Baseline for Detecting Misclassified and OOD Examples* (MSP). [arXiv:1610.02136](https://arxiv.org/abs/1610.02136)
- Liu et al. (2020). *Energy-based Out-of-distribution Detection*. [arXiv:2010.03759](https://arxiv.org/abs/2010.03759)
- Lee et al. (2018). *A Simple Unified Framework for Detecting OOD Samples* (Mahalanobis). [arXiv:1807.03888](https://arxiv.org/abs/1807.03888)
- Guo et al. (2017). *On Calibration of Modern Neural Networks* (temperature scaling). [arXiv:1706.04599](https://arxiv.org/abs/1706.04599)
- Zhang et al. *OpenOOD* â€” benchmark comparativo de mÃ©todos OOD. [github.com/Jingkang50/OpenOOD](https://github.com/Jingkang50/OpenOOD)



