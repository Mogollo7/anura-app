---
title: "Modelo de Visión â€” BioCLIP"
proyecto: Anura
tipo: desarrollo-técnico
estado: teacher-en-servidor-student-on-device
tags: [anura, desarrollo, bioclip, edgenext, destilación, visión, audio, embeddings]
---

# Modelo de Visión (y Audio) â€” BioCLIP

[[Anura â€” àndice General]] · [[Plan de Acción y Arquitectura Conceptual]] · [[Implementación de Triplet Loss]] · [[Arquitectura Multimodal]]

> [!warning] Revisado 2026-09-08: BioCLIP ya no viaja al dispositivo
> La cuantización INT8 de BioCLIP (ViT-B/16) descrita en §6 **fracasó en pruebas reales** (~0,2 % de exactitud â€” los outliers de atención del ViT destruyen la geometría bajo INT8). BioCLIP sigue siendo el àºnico extractor visual **del servidor** (ya no hay comparación abierta con EfficientNet, ese punto de C-2 se mantiene), pero el modelo on-device es ahora **EdgeNeXt-Tiny**, obtenido por destilación de conocimiento desde BioCLIP como *teacher* (Multi-Head Loss: Familia+Género+Especie + KL divergence). La rama de audio **tampoco reutiliza ya un backbone compartido** â€” tiene modelo propio dedicado (§8 revisado). Ver decisiones C-5 y C-7 en [[Inconsistencias y Decisiones Pendientes]]. Los pesos de BioCLIP v1 ya están revisados y sus características óptimas definidas para el rol de teacher (ver §10).

> [!abstract] Rol dentro de Anura
> BioCLIP es el **extractor de representación** del sistema: convierte la fotografía (o el recorte segmentado del individuo) en un vector numérico que alimenta la clasificación jerárquica, la bàºsqueda por similitud en la [[Base Vectorial (SQLite-vec)|base vectorial]] y la detección de especies desconocidas ([[Open-Set Recognition]]). No es el clasificador final; es la capa que produce el espacio donde todo lo demás opera.

## 1. Qué es BioCLIP y por qué encaja en este proyecto

BioCLIP es un modelo fundacional de visión entrenado con aprendizaje contrastivo imagenâ€“texto (la misma familia que CLIP), pero especializado en el árbol de la vida: en lugar de aprender la relación entre fotos y descripciones genéricas de internet, aprende la relación entre imágenes de organismos y su **nombre taxonómico jerárquico completo** (reino â†’ filo â†’ clase â†’ orden â†’ familia â†’ género â†’ especie).

Esa diferencia es la que importa aquí. Un backbone genérico (ImageNet, CLIP estándar) aprende a separar "rana" de "coche". BioCLIP aprende un espacio donde *Boana cinereascens* y *Boana lanciformis* están cerca entre sí y lejos de *Rhinella horribilis*, porque el texto con el que se entrenó codificaba esa jerarquía. Para Anura, cuyo objetivo es precisamente resolver Familia â†’ Género â†’ Especie, el espacio ya viene organizado con la estructura correcta.

Ventaja práctica adicional: la generalización a especies con pocos ejemplos. Es el escenario exacto de este proyecto (ver [[Estrategia de Construcción del Dataset]]).

## 2. Qué versión usar â€” decisión con implicaciones de despliegue

Existen dos modelos y **no son intercambiables** para este proyecto, porque tienen tamaños muy distintos:

| | **BioCLIP** (v1) | **BioCLIP 2** |
| --- | --- | --- |
| Publicación | CVPR 2024 | NeurIPS 2025 (spotlight) |
| Codificador visual | ViT-B/16 (~86 M parámetros) | ViT-L/14 (~304 M parámetros) |
| Datos de entrenamiento | TreeOfLife-10M (~10 M imágenes) | TreeOfLife-200M (~214 M imágenes) |
| Dimensión del embedding | 512 | 1024 |
| Precisión esperada | Menor | Mayor (mejor en rasgos y hábitat) |
| ¿Viable embebido en móvil? | **Sí, con cuantización** | **No de forma realista** |

> [!important] Decisión recomendada: arquitectura de dos velocidades
> - **En el dispositivo (Fase 2, offline):** BioCLIP v1 / ViT-B/16, cuantizado. Es el àºnico de los dos que cabe en el presupuesto de 150 MB del RNF-05 junto al modelo de segmentación â€” y, gracias a §8, sin necesitar un modelo adicional para audio.
> - **En el servidor (Fase 1 y reprocesamiento):** BioCLIP 2 / ViT-L/14, para generar los embeddings de referencia de mayor calidad del catálogo y para reevaluar observaciones cuando llegan sincronizadas.
>
> **Consecuencia crítica que hay que tener presente:** los embeddings de v1 (512-d) y v2 (1024-d) **viven en espacios distintos y no son comparables entre sí**. Si el móvil genera vectores con v1 y el servidor los compara contra un índice construido con v2, los resultados son basura. Hay que decidir una de dos:
> 1. **Un solo espacio** (recomendado para el TFG): usar v1 en ambos lados. Simple, coherente, sin riesgo.
> 2. **Dos índices paralelos**: cada observación se indexa dos veces, y cada consulta usa el índice que corresponde a su origen. Más preciso en el servidor, pero duplica almacenamiento y complejidad de sincronización.

## 3. Cómo se usa: tres estrategias posibles

Ordenadas de menor a mayor coste y riesgo.

### 3.1 Zero-shot (línea base, sin entrenar nada)

BioCLIP puede clasificar sin entrenamiento: se construyen descripciones textuales de cada especie del catálogo ("a photo of *Dendropsophus microcephalus*, a frog"), se codifican con el codificador de texto, y se compara la imagen contra todas por similitud coseno.

Sirve como **suelo de referencia**: cualquier método entrenado debe superar este nàºmero. Es barato de obtener y da una cifra defendible en el documento de grado ("el modelo ajustado mejora X puntos sobre BioCLIP zero-shot").

### 3.2 Linear probe / cabezas jerárquicas sobre embeddings congelados

Se congela BioCLIP, se extraen los embeddings una sola vez para todo el dataset, y se entrenan **tres clasificadores lineales** (Familia, Género, Especie) sobre esos vectores.

```
Imagen segmentada (máscara binaria individuo/fondo)
      â†“
[BioCLIP congelado]  â† no se actualiza ni un peso
      â†“
Embedding (512-d)  â† se calcula UNA vez y se cachea en disco
      â†“
   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
   â†“          â†“          â†“
Familia    Género     Especie     (3 capas lineales + softmax)
```

Por qué funcionó tan bien en la Etapa I (§7): entrena en minutos, es casi imposible de sobreajustar destructivamente con pocos datos, permite iterar rápido, y admite penalizar la coherencia jerárquica explícitamente (§4).

### 3.3 Fine-tuning parcial + Triplet Loss (fase posterior)

Descongelar los àºltimos bloques del ViT y ajustar el espacio con [[Implementación de Triplet Loss|triplet loss]], para que individuos de la misma especie se agrupen más y especies crípticas se separen mejor. Es lo que más puede subir el rendimiento en géneros difíciles como *Pristimantis*, pero exige más datos y validación cuidadosa. Ver esa nota para el detalle y los riesgos.

## 4. Clasificación jerárquica: cómo evitar predicciones incoherentes

Un problema real de tener tres cabezas independientes es que el modelo puede predecir *Familia = Hylidae* y *Especie = Rhinella horribilis* (que es Bufonidae). Eso es taxonómicamente imposible y destruye la credibilidad del sistema ante un herpetólogo.

Tres formas de resolverlo, combinables:

1. **Enmascarado jerárquico en inferencia:** una vez elegida la familia, se ponen a cero las probabilidades de todas las especies que no pertenecen a ella y se renormaliza. Barato y garantiza coherencia total.
2. **Pérdida con penalización de coherencia:** añadir un término que castigue la discrepancia entre lo que predice la cabeza de especie (agregada a nivel de familia) y lo que predice la cabeza de familia.
3. **Bàºsqueda adaptativa Top-K** (lo descrito en las [[Notas Originales â€” Segmentación Semántica y Metodología Anura|notas originales]]): no colapsar a una sola familia si la distribución está repartida (52 % / 44 %), y sí hacerlo si es dominante (96 % / 2 %). Mantiene ramas vivas cuando la evidencia es ambigua.

La métrica que hay que reportar para esto es **consistencia taxonómica** (% de predicciones jerárquicamente válidas), documentada en [[Métricas Offline]].

## 5. Entrada del modelo: imagen completa o recorte segmentado

Aquí se conecta con el [[Pipeline del Sistema]] y con toda la anotación de la [[Guía CVAT â€” àndice|guía CVAT]]. Tres variantes posibles:

| Variante | Entrada a BioCLIP | Qué se espera |
| --- | --- | --- |
| A â€” Imagen completa | Foto original redimensionada | Línea base. Riesgo de *shortcut learning*: el modelo aprende el fondo (hojarasca, musgo) en vez del animal. |
| B â€” Recorte del individuo | Caja de `anuro_completo` recortada y redimensionada | Elimina la mayor parte del fondo. |
| **C â€” Recorte + máscara binaria** âœ… | Recorte con fondo puesto a negro/neutro usando la máscara binaria individuo-vs-fondo | **Es la variante ya validada empíricamente en la Etapa I** (§7): al eliminar por completo el fondo, el modelo deja de tener la opción de aprender sustrato en vez de morfología, y eso explica gran parte del salto de rendimiento observado. |

> [!tip] Sigue siendo un experimento formal pendiente
> Que la variante C haya funcionado muy bien en la Etapa I no reemplaza la comparación controlada A/B/C con el mismo split â€” solo la hace más interesante: ahora hay un resultado fuerte que explicar y contrastar. Registrar en [[Experimentos y Resultados]].

## 6. Presupuesto de cómputo en móvil

Cifras de referencia para dimensionar (a confirmar empíricamente en el dispositivo objetivo, ver [[Optimización para Inferencia en Móvil]]):

- ViT-B/16 en FP32 â‰ˆ 330 MB â†’ **inviable** solo.
- ViT-B/16 con pesos INT8 â‰ˆ 85â€“90 MB â†’ cabe holgadamente junto al modelo de segmentación dentro de los 150 MB del RNF-05, **sobre todo porque no hace falta un tercer modelo para audio** (§8).
- Práctica habitual en ViT móvil: **pesos INT8, activaciones FP16** â€” las activaciones del transformer son sensibles y cuantizarlas agresivamente degrada la precisión.
- Solo se necesita el **codificador de imagen**. El codificador de texto no viaja al dispositivo: los prompts de las especies del catálogo se codifican una vez en el servidor y se embarcan como una tabla de vectores ya calculados (unos pocos KB).

## 7. Etapa I: por qué el resultado (~99 %) es legítimo, no fuga de información

> [!important] Aclaración del autor sobre la Etapa I
> El resultado real de la Etapa I fue de **~99 % de exactitud**, y no un artefacto de fuga de información. Se sostiene en tres decisiones metodológicas tomadas deliberadamente:
> 1. **Segmentación binaria previa a la clasificación** â€” cada imagen se procesó primero con un modelo de segmentación binaria (individuo vs. fondo) y solo el recorte enmascarado se pasó a BioCLIP. Es exactamente la variante **C** de la tabla del §5. Al quitar el fondo, se elimina la vía más comàºn de "trampa" que hace que un resultado alto sea engañoso (*shortcut learning* sobre el sustrato).
> 2. **División por individuo** â€” 70 individuos por especie, 10 especies, con las fotos de un mismo individuo confinadas a un àºnico conjunto (train/val/test). Es precisamente la regla `GroupSplit` que el resto de esta bóveda insiste en aplicar ([[Estrategia de Construcción del Dataset]]).
> 3. **Diversidad de individuos, no de tomas repetidas** â€” el conjunto se construyó variando individuos, no fotografiando el mismo ejemplar muchas veces, así que el modelo no tuvo oportunidad de memorizar un ejemplar concreto.
>
> Estas tres decisiones son, en conjunto, exactamente lo que un split riguroso exige. **El punto 4.9.1 de las metas de la [[Estrategia de Construcción del Dataset]] queda así confirmado como alcanzado en la Etapa I**, no como sospechoso de fuga.

Esto **corrige** la advertencia que aparecía antes en esta nota (y en [[Inconsistencias y Decisiones Pendientes]], punto C-4): no hay indicio de fuga; al contrario, la Etapa I es un caso bien controlado y vale la pena documentarlo así en el trabajo de grado, con el detalle metodológico completo, porque es un argumento a favor de la robustez del enfoque (segmentar antes de clasificar), no solo una cifra bonita.

Lo que sigue pendiente **no es "descartar fuga"**, sino:
- Confirmar el desglose por especie completo de esa corrida (la tabla ya documentada en la estrategia de dataset cubre 10 especies).
- Repetir el protocolo exacto (segmentación binaria + `GroupSplit`) al escalar a más especies, para verificar que el resultado se sostiene y no era particular de esas 10.
- Documentar formalmente el modelo de segmentación binaria usado en la Etapa I (arquitectura, entrenamiento) como antecedente directo del modelo de segmentación anatómica de 16 regiones de la [[Guía CVAT â€” àndice|guía CVAT]] â€” son dos pasos de la misma idea, con distinto nivel de granularidad.

## 8. Rol en la rama de audio: modelo propio dedicado (revisado 2026-09-08)

> [!warning] Decisión revertida: ya no se reutiliza un backbone compartido
> La versión anterior de esta sección proponía reutilizar el codificador de BioCLIP sobre el mel-espectrograma. Esa idea dependía de que BioCLIP viajara al dispositivo â€” dejó de ser cierto tras el fracaso de INT8 (§6, ver el aviso al inicio de la nota). Con EdgeNeXt-Tiny como modelo on-device, la reutilización pierde su argumento fuerte: EdgeNeXt-Tiny fue destilado con un objetivo estrecho (imitar a BioCLIP específicamente para morfología de rana en fotos naturales), así que no hay garantía de que transfiera bien a espectrogramas â€” a diferencia de BioCLIP, que sí es un modelo fundacional con features generales. Además, el ahorro de almacenamiento de reutilizar ya no es decisivo: un modelo de audio dedicado a esta escala (1-3 MB) es tan pequeño que no compromete el presupuesto revisado (~15-30 MB total, ver C-5). **Decisión del autor (2026-09-08, C-7):** modelo de audio propio y dedicado, por facilidad de implementación.

```
Audio 3-5 s (WAV mono 44,1 kHz)   [[Estrategia de Construcción del Dataset]]
        â†“
Mel-espectrograma (~128 à— 256)
        â†“
   Modelo de audio dedicado (CNN pequeña, 1-3 MB â€” arquitectura a definir,
   referencia: BirdNET-lite / PANNs-tiny)
        â†“
Embedding o clasificación acàºstica directa
        â†“
â†’ fusión multimodal ([[Arquitectura Multimodal]])
```

Consideraciones que siguen vigentes de la versión anterior:

- La augmentación para esta rama es **SpecAugment** (`TimeShift`, `FrequencyMasking`, `TimeMasking`), no la augmentación geométrica de fotos: voltear un espectrograma en frecuencia produce un canto físicamente imposible.
- Carga on-demand: el modelo de audio se activa solo al grabar y se libera después â€” ver [[Optimización para Inferencia en Móvil]] §4. Este patrón no cambia por tener modelo propio.
- **Bloqueante previo a construir esto**: confirmar que existe dataset de audio (grabación propia o AnuraSet/Xeno-canto) con cobertura razonable de las 28 especies. Punto Go/No-Go ya fijado en [[Cronograma y Plan de Trabajo]] para el 18 sep â€” si no hay cobertura suficiente, la rama de audio se declara trabajo futuro y no se invierte más tiempo en ella dentro del sprint del prototipo.

## 9. Arquitectura del modelo de audio propio â€” por definir

Con la reutilización descartada, queda pendiente elegir la arquitectura concreta del modelo dedicado. Candidatas, de menor a mayor capacidad:

| Arquitectura | Tamaño aprox. | Referencia |
| --- | --- | --- |
| CNN pequeña custom (4-6 capas conv sobre mel-espectrograma) | <1 MB | Suficiente si el nàºmero de especies con audio es reducido |
| MobileNetV1/V2 adaptada (1 canal de entrada) | 1-3 MB | Punto de partida razonable, arquitectura probada en móvil |
| Arquitectura estilo BirdNET-lite (EfficientNet-lite reducido) | 2-6 MB | Referencia validada en bioacàºstica a escala similar (miles de especies de aves; aquí serían 28) |

**No hay comparación experimental corrida todavía** â€” es trabajo pendiente, condicionado al bloqueante de dataset de audio de arriba. Registrar en [[Experimentos y Resultados]] cuando se ejecute.

## 10. Qué falta por decidir o medir

- [x] Fijar versión (v1 vs v2) â†’ **resuelto 2026-09-05: BioCLIP v1** para el sprint del prototipo (evita el problema de espacios de embedding incompatibles dentro del plazo del 27 de septiembre) â†’ [[Inconsistencias y Decisiones Pendientes]]. Matiz 2026-09-08 (C-5): v1 ya no corre en el dispositivo, solo en servidor como teacher de destilación. v2 en servidor queda abierto como mejora posterior al prototipo.
- [x] Revisar pesos de BioCLIP v1 y definir características óptimas â†’ **resuelto 2026-09-08**: ViT-B/16 (~86M parámetros), fine-tuned, confirmado para su rol de teacher en servidor â†’ [[Inconsistencias y Decisiones Pendientes]] (C-5).
- [x] Backbone on-device tras fracaso de INT8 â†’ **resuelto 2026-09-08**: EdgeNeXt-Tiny destilado con Multi-Head Loss â†’ C-5.
- [x] Rama de audio: ¿reutilizar backbone o modelo propio? â†’ **resuelto 2026-09-08**: modelo propio dedicado â†’ C-7. El experimento de comparación (antiguo §9) queda descartado por decisión directa, no por resultado medido.
- [ ] Medir zero-shot como línea base antes de entrenar nada.
- [ ] Completar la comparación formal A/B/C del §5 (ya con C como candidato fuerte).
- [ ] Elegir y entrenar la arquitectura del modelo de audio dedicado (§9) â€” condicionado a confirmar cobertura de dataset de audio para las 28 especies.
- [ ] Verificar el tamaño real de EdgeNeXt-Tiny cuantizado en el Samsung Galaxy A30 (dispositivo de referencia confirmado 2026-09-08).
- [ ] Confirmar la licencia de uso de los pesos de BioCLIP para uso en servidor (ya no aplica distribución en el APK, al no viajar al dispositivo).
- [ ] Documentar formalmente el modelo de segmentación binaria de la Etapa I.

## Referencias

- Stevens et al. (2024). *BioCLIP: A Vision Foundation Model for the Tree of Life*. CVPR 2024. [arXiv:2311.18803](https://doi.org/10.48550/arXiv.2311.18803)
- Imageomics. *BioCLIP 2* â€” modelo y tarjeta del modelo. [github.com/Imageomics/bioclip-2](https://github.com/Imageomics/bioclip-2) · [huggingface.co/imageomics/bioclip-2](https://huggingface.co/imageomics/bioclip-2)
- Pan & Yang (2010). *A survey on transfer learning*. [doi:10.1109/TKDE.2009.191](https://doi.org/10.1109/TKDE.2009.191)
- Cañas et al. (2023). *AnuraSet*. [arXiv:2307.06860](https://doi.org/10.48550/arXiv.2307.06860) â€” referencia de comparación para la rama acàºstica.

Ver también: [[Bibliografía]]



