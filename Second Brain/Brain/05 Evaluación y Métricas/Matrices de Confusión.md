---
title: "Matrices de Confusión"
proyecto: Anura
tipo: evaluación
estado: plantilla-lista-para-resultados
tags: [anura, evaluación, matriz-confusión, análisis-error]
---

# Matrices de Confusión

[[Anura â€” àndice General]] · [[Evaluación y Métricas â€” àndice]] · [[Métricas Offline]] · [[Listado de Individuos y Arreglo Taxonómico]]

> [!abstract] Para qué sirven aquí
> Una métrica agregada dice *cuánto* falla el modelo; la matriz de confusión dice *con qué lo confunde*. En un problema taxonómico eso es mucho más àºtil, porque los errores tienen significado biológico: confundir dos *Pristimantis* del mismo grupo es esperable; confundir un *Dendrobates* con una *Rhinella* indica un problema serio.

## 1. Las tres matrices

| Nivel | Tamaño | Utilidad |
| --- | --- | --- |
| **Familia** | 8 à— 8 | Legible de un vistazo. Errores aquí son graves. |
| **Género** | ~15 à— 15 | Nivel más informativo para diagnóstico |
| **Especie** | ~30 à— 30 | Difícil de leer entera; usar la lista de pares confundidos (§3) |

Normalizar **por fila** (recall por clase): cada fila suma 100 % y se lee como "de todas las imágenes reales de X, qué porcentaje fue a cada predicción". Con clases desbalanceadas es la àºnica lectura honesta.

## 2. Matriz por familia

Familias presentes en el dataset ([[Listado de Individuos y Arreglo Taxonómico]]): Aromobatidae, Bufonidae, Centrolenidae, Craugastoridae, Dendrobatidae, Hylidae, Leptodactylidae, Strabomantidae.

```
                  Predicho â†’
Real â†“        Arom  Bufo  Cent  Craug Dendr Hylid Lepto Strab
Aromobatidae
Bufonidae
Centrolenidae
Craugastoridae
Dendrobatidae
Hylidae
Leptodactylidae
Strabomantidae
```

*(Pegar aquí la figura generada: `![[matriz-familia-vX.png]]`)*

## 3. Pares confundidos (más àºtil que la matriz de especie completa)

Ordenar por frecuencia descendente. Esta tabla es la agenda de trabajo del proyecto.

| Real | Predicho | Frecuencia | Mismo género | Hipótesis de causa | Acción |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

Hipótesis de causa habituales, y qué implica cada una:

| Causa | Cómo se reconoce | Acción |
| --- | --- | --- |
| **Similitud morfológica real** | Especies del mismo género, crípticas | Aumentar peso de audio/contexto; caracteres finos |
| **Pocos datos de una clase** | La clase minoritaria absorbe errores | Más imágenes u *oversampling* |
| **Error de etiquetado** | Confusión asimétrica y sistemática | **Revisar el dataset antes de tocar el modelo** |
| **Sesgo de fondo/localidad** | Se confunden especies que comparten sustrato | Diversificar fondos; verificar el split |
| **Calidad de imagen** | Errores concentrados en fotos malas | Reforzar el control de calidad de entrada |
| **Polimorfismo** | Falla solo un morfo de color | Cubrir morfos en el dataset |

> [!warning] El caso *Pristimantis*
> La Etapa I ya mostró el patrón: *P. paisa* (F1 0,86) y *P. penelopus* (F1 0,86) por debajo del resto. Es el género con más especies del dataset, con cripticismo y polimorfismo bien documentados. Es esperable que sea el foco de errores â€” pero antes de asumir que es "dificultad intrínseca", hay que **descartar error de etiquetado**, que produce exactamente el mismo síntoma y se arregla mucho más barato.

## 4. Análisis por tipo de error

No todos los errores cuestan igual. Clasificarlos guía las decisiones:

| Tipo | Descripción | Gravedad |
| --- | --- | --- |
| **Intragenérico** | Especie equivocada, género correcto | Baja â€” el usuario recibe información casi correcta |
| **Intrafamiliar** | Género equivocado, familia correcta | Media |
| **Interfamiliar** | Familia equivocada | **Alta** â€” indica que el modelo no captó la morfología básica |
| **Falso conocido** | Especie desconocida clasificada como conocida | **Crítica** â€” contamina la base de datos ([[Open-Set Recognition]]) |
| **Falso desconocido** | Especie conocida rechazada | Baja â€” molesta pero es recuperable |

| Tipo de error | % del total |
| --- | --- |
| Intragenérico | |
| Intrafamiliar | |
| Interfamiliar | |

Un buen modelo taxonómico concentra sus errores en la primera fila. Si hay errores interfamiliares significativos, el problema es de representación visual, no de granularidad fina.

## 5. Errores con coste asimétrico

Dos casos donde equivocarse tiene consecuencias más allá de la métrica:

- **Especies venenosas o tóxicas** (Dendrobatidae): la HU-01 promete al usuario comàºn saber si el animal es peligroso. Un falso negativo aquí â€” decir "inofensiva" a una especie tóxica â€” es un error de seguridad, no estadístico. Debe reportarse por separado y tratarse con umbral conservador: ante duda, advertir.
- **Especies amenazadas UICN**: un registro mal identificado de una especie amenazada distorsiona datos de conservación y puede activar la ofuscación geográfica del RNF-13 sobre la especie equivocada.

## 6. Registro de análisis

| Fecha | Versión modelo | Hallazgo principal | Acción tomada | Efecto observado |
| --- | --- | --- | --- | --- |
| | | | | |

Ver también: [[Experimentos y Resultados]] · [[Estrategia de Construcción del Dataset]]



