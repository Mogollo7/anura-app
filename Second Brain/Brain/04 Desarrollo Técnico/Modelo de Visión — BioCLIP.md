---
title: "Modelo de VisiÃ³n â€” BioCLIP"
proyecto: Anura
tipo: desarrollo-tÃ©cnico
estado: teacher-en-servidor-student-on-device
tags: [anura, desarrollo, bioclip, edgenext, destilaciÃ³n, visiÃ³n, audio, embeddings]
---

# Modelo de VisiÃ³n (y Audio) â€” BioCLIP

[[Anura â€” Ãndice General]] Â· [[Plan de AcciÃ³n y Arquitectura Conceptual]] Â· [[ImplementaciÃ³n de Triplet Loss]] Â· [[Arquitectura Multimodal]]

> [!warning] Revisado 2026-09-08: BioCLIP ya no viaja al dispositivo
> La cuantizaciÃ³n INT8 de BioCLIP (ViT-B/16) descrita en Â§6 **fracasÃ³ en pruebas reales** (~0,2 % de exactitud â€” los outliers de atenciÃ³n del ViT destruyen la geometrÃ­a bajo INT8). BioCLIP sigue siendo el Ãºnico extractor visual **del servidor** (ya no hay comparaciÃ³n abierta con EfficientNet, ese punto de C-2 se mantiene), pero el modelo on-device es ahora **EdgeNeXt-Tiny**, obtenido por destilaciÃ³n de conocimiento desde BioCLIP como *teacher* (Multi-Head Loss: Familia+GÃ©nero+Especie + KL divergence). La rama de audio **tampoco reutiliza ya un backbone compartido** â€” tiene modelo propio dedicado (Â§8 revisado). Ver decisiones C-5 y C-7 en [[Inconsistencias y Decisiones Pendientes]]. Los pesos de BioCLIP v1 ya estÃ¡n revisados y sus caracterÃ­sticas Ã³ptimas definidas para el rol de teacher (ver Â§10).

> [!abstract] Rol dentro de Anura
> BioCLIP es el **extractor de representaciÃ³n** del sistema: convierte la fotografÃ­a (o el recorte segmentado del individuo) en un vector numÃ©rico que alimenta la clasificaciÃ³n jerÃ¡rquica, la bÃºsqueda por similitud en la [[Base Vectorial (SQLite-vec)|base vectorial]] y la detecciÃ³n de especies desconocidas ([[Open-Set Recognition]]). No es el clasificador final; es la capa que produce el espacio donde todo lo demÃ¡s opera.

## 1. QuÃ© es BioCLIP y por quÃ© encaja en este proyecto

BioCLIP es un modelo fundacional de visiÃ³n entrenado con aprendizaje contrastivo imagenâ€“texto (la misma familia que CLIP), pero especializado en el Ã¡rbol de la vida: en lugar de aprender la relaciÃ³n entre fotos y descripciones genÃ©ricas de internet, aprende la relaciÃ³n entre imÃ¡genes de organismos y su **nombre taxonÃ³mico jerÃ¡rquico completo** (reino â†’ filo â†’ clase â†’ orden â†’ familia â†’ gÃ©nero â†’ especie).

Esa diferencia es la que importa aquÃ­. Un backbone genÃ©rico (ImageNet, CLIP estÃ¡ndar) aprende a separar "rana" de "coche". BioCLIP aprende un espacio donde *Boana cinereascens* y *Boana lanciformis* estÃ¡n cerca entre sÃ­ y lejos de *Rhinella horribilis*, porque el texto con el que se entrenÃ³ codificaba esa jerarquÃ­a. Para Anura, cuyo objetivo es precisamente resolver Familia â†’ GÃ©nero â†’ Especie, el espacio ya viene organizado con la estructura correcta.

Ventaja prÃ¡ctica adicional: la generalizaciÃ³n a especies con pocos ejemplos. Es el escenario exacto de este proyecto (ver [[Estrategia de ConstrucciÃ³n del Dataset]]).

## 2. QuÃ© versiÃ³n usar â€” decisiÃ³n con implicaciones de despliegue

Existen dos modelos y **no son intercambiables** para este proyecto, porque tienen tamaÃ±os muy distintos:

| | **BioCLIP** (v1) | **BioCLIP 2** |
| --- | --- | --- |
| PublicaciÃ³n | CVPR 2024 | NeurIPS 2025 (spotlight) |
| Codificador visual | ViT-B/16 (~86 M parÃ¡metros) | ViT-L/14 (~304 M parÃ¡metros) |
| Datos de entrenamiento | TreeOfLife-10M (~10 M imÃ¡genes) | TreeOfLife-200M (~214 M imÃ¡genes) |
| DimensiÃ³n del embedding | 512 | 1024 |
| PrecisiÃ³n esperada | Menor | Mayor (mejor en rasgos y hÃ¡bitat) |
| Â¿Viable embebido en mÃ³vil? | **SÃ­, con cuantizaciÃ³n** | **No de forma realista** |

> [!important] DecisiÃ³n recomendada: arquitectura de dos velocidades
> - **En el dispositivo (Fase 2, offline):** BioCLIP v1 / ViT-B/16, cuantizado. Es el Ãºnico de los dos que cabe en el presupuesto de 150 MB del RNF-05 junto al modelo de segmentaciÃ³n â€” y, gracias a Â§8, sin necesitar un modelo adicional para audio.
> - **En el servidor (Fase 1 y reprocesamiento):** BioCLIP 2 / ViT-L/14, para generar los embeddings de referencia de mayor calidad del catÃ¡logo y para reevaluar observaciones cuando llegan sincronizadas.
>
> **Consecuencia crÃ­tica que hay que tener presente:** los embeddings de v1 (512-d) y v2 (1024-d) **viven en espacios distintos y no son comparables entre sÃ­**. Si el mÃ³vil genera vectores con v1 y el servidor los compara contra un Ã­ndice construido con v2, los resultados son basura. Hay que decidir una de dos:
> 1. **Un solo espacio** (recomendado para el TFG): usar v1 en ambos lados. Simple, coherente, sin riesgo.
> 2. **Dos Ã­ndices paralelos**: cada observaciÃ³n se indexa dos veces, y cada consulta usa el Ã­ndice que corresponde a su origen. MÃ¡s preciso en el servidor, pero duplica almacenamiento y complejidad de sincronizaciÃ³n.

## 3. CÃ³mo se usa: tres estrategias posibles

Ordenadas de menor a mayor coste y riesgo.

### 3.1 Zero-shot (lÃ­nea base, sin entrenar nada)

BioCLIP puede clasificar sin entrenamiento: se construyen descripciones textuales de cada especie del catÃ¡logo ("a photo of *Dendropsophus microcephalus*, a frog"), se codifican con el codificador de texto, y se compara la imagen contra todas por similitud coseno.

Sirve como **suelo de referencia**: cualquier mÃ©todo entrenado debe superar este nÃºmero. Es barato de obtener y da una cifra defendible en el documento de grado ("el modelo ajustado mejora X puntos sobre BioCLIP zero-shot").

### 3.2 Linear probe / cabezas jerÃ¡rquicas sobre embeddings congelados

Se congela BioCLIP, se extraen los embeddings una sola vez para todo el dataset, y se entrenan **tres clasificadores lineales** (Familia, GÃ©nero, Especie) sobre esos vectores.

```
Imagen segmentada (mÃ¡scara binaria individuo/fondo)
      â†“
[BioCLIP congelado]  â† no se actualiza ni un peso
      â†“
Embedding (512-d)  â† se calcula UNA vez y se cachea en disco
      â†“
   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
   â†“          â†“          â†“
Familia    GÃ©nero     Especie     (3 capas lineales + softmax)
```

Por quÃ© funcionÃ³ tan bien en la Etapa I (Â§7): entrena en minutos, es casi imposible de sobreajustar destructivamente con pocos datos, permite iterar rÃ¡pido, y admite penalizar la coherencia jerÃ¡rquica explÃ­citamente (Â§4).

### 3.3 Fine-tuning parcial + Triplet Loss (fase posterior)

Descongelar los Ãºltimos bloques del ViT y ajustar el espacio con [[ImplementaciÃ³n de Triplet Loss|triplet loss]], para que individuos de la misma especie se agrupen mÃ¡s y especies crÃ­pticas se separen mejor. Es lo que mÃ¡s puede subir el rendimiento en gÃ©neros difÃ­ciles como *Pristimantis*, pero exige mÃ¡s datos y validaciÃ³n cuidadosa. Ver esa nota para el detalle y los riesgos.

## 4. ClasificaciÃ³n jerÃ¡rquica: cÃ³mo evitar predicciones incoherentes

Un problema real de tener tres cabezas independientes es que el modelo puede predecir *Familia = Hylidae* y *Especie = Rhinella horribilis* (que es Bufonidae). Eso es taxonÃ³micamente imposible y destruye la credibilidad del sistema ante un herpetÃ³logo.

Tres formas de resolverlo, combinables:

1. **Enmascarado jerÃ¡rquico en inferencia:** una vez elegida la familia, se ponen a cero las probabilidades de todas las especies que no pertenecen a ella y se renormaliza. Barato y garantiza coherencia total.
2. **PÃ©rdida con penalizaciÃ³n de coherencia:** aÃ±adir un tÃ©rmino que castigue la discrepancia entre lo que predice la cabeza de especie (agregada a nivel de familia) y lo que predice la cabeza de familia.
3. **BÃºsqueda adaptativa Top-K** (lo descrito en las [[Notas Originales â€” SegmentaciÃ³n SemÃ¡ntica y MetodologÃ­a Anura|notas originales]]): no colapsar a una sola familia si la distribuciÃ³n estÃ¡ repartida (52 % / 44 %), y sÃ­ hacerlo si es dominante (96 % / 2 %). Mantiene ramas vivas cuando la evidencia es ambigua.

La mÃ©trica que hay que reportar para esto es **consistencia taxonÃ³mica** (% de predicciones jerÃ¡rquicamente vÃ¡lidas), documentada en [[MÃ©tricas Offline]].

## 5. Entrada del modelo: imagen completa o recorte segmentado

AquÃ­ se conecta con el [[Pipeline del Sistema]] y con toda la anotaciÃ³n de la [[GuÃ­a CVAT â€” Ãndice|guÃ­a CVAT]]. Tres variantes posibles:

| Variante | Entrada a BioCLIP | QuÃ© se espera |
| --- | --- | --- |
| A â€” Imagen completa | Foto original redimensionada | LÃ­nea base. Riesgo de *shortcut learning*: el modelo aprende el fondo (hojarasca, musgo) en vez del animal. |
| B â€” Recorte del individuo | Caja de `anuro_completo` recortada y redimensionada | Elimina la mayor parte del fondo. |
| **C â€” Recorte + mÃ¡scara binaria** âœ… | Recorte con fondo puesto a negro/neutro usando la mÃ¡scara binaria individuo-vs-fondo | **Es la variante ya validada empÃ­ricamente en la Etapa I** (Â§7): al eliminar por completo el fondo, el modelo deja de tener la opciÃ³n de aprender sustrato en vez de morfologÃ­a, y eso explica gran parte del salto de rendimiento observado. |

> [!tip] Sigue siendo un experimento formal pendiente
> Que la variante C haya funcionado muy bien en la Etapa I no reemplaza la comparaciÃ³n controlada A/B/C con el mismo split â€” solo la hace mÃ¡s interesante: ahora hay un resultado fuerte que explicar y contrastar. Registrar en [[Experimentos y Resultados]].

## 6. Presupuesto de cÃ³mputo en mÃ³vil

Cifras de referencia para dimensionar (a confirmar empÃ­ricamente en el dispositivo objetivo, ver [[OptimizaciÃ³n para Inferencia en MÃ³vil]]):

- ViT-B/16 en FP32 â‰ˆ 330 MB â†’ **inviable** solo.
- ViT-B/16 con pesos INT8 â‰ˆ 85â€“90 MB â†’ cabe holgadamente junto al modelo de segmentaciÃ³n dentro de los 150 MB del RNF-05, **sobre todo porque no hace falta un tercer modelo para audio** (Â§8).
- PrÃ¡ctica habitual en ViT mÃ³vil: **pesos INT8, activaciones FP16** â€” las activaciones del transformer son sensibles y cuantizarlas agresivamente degrada la precisiÃ³n.
- Solo se necesita el **codificador de imagen**. El codificador de texto no viaja al dispositivo: los prompts de las especies del catÃ¡logo se codifican una vez en el servidor y se embarcan como una tabla de vectores ya calculados (unos pocos KB).

## 7. Etapa I: por quÃ© el resultado (~99 %) es legÃ­timo, no fuga de informaciÃ³n

> [!important] AclaraciÃ³n del autor sobre la Etapa I
> El resultado real de la Etapa I fue de **~99 % de exactitud**, y no un artefacto de fuga de informaciÃ³n. Se sostiene en tres decisiones metodolÃ³gicas tomadas deliberadamente:
> 1. **SegmentaciÃ³n binaria previa a la clasificaciÃ³n** â€” cada imagen se procesÃ³ primero con un modelo de segmentaciÃ³n binaria (individuo vs. fondo) y solo el recorte enmascarado se pasÃ³ a BioCLIP. Es exactamente la variante **C** de la tabla del Â§5. Al quitar el fondo, se elimina la vÃ­a mÃ¡s comÃºn de "trampa" que hace que un resultado alto sea engaÃ±oso (*shortcut learning* sobre el sustrato).
> 2. **DivisiÃ³n por individuo** â€” 70 individuos por especie, 10 especies, con las fotos de un mismo individuo confinadas a un Ãºnico conjunto (train/val/test). Es precisamente la regla `GroupSplit` que el resto de esta bÃ³veda insiste en aplicar ([[Estrategia de ConstrucciÃ³n del Dataset]]).
> 3. **Diversidad de individuos, no de tomas repetidas** â€” el conjunto se construyÃ³ variando individuos, no fotografiando el mismo ejemplar muchas veces, asÃ­ que el modelo no tuvo oportunidad de memorizar un ejemplar concreto.
>
> Estas tres decisiones son, en conjunto, exactamente lo que un split riguroso exige. **El punto 4.9.1 de las metas de la [[Estrategia de ConstrucciÃ³n del Dataset]] queda asÃ­ confirmado como alcanzado en la Etapa I**, no como sospechoso de fuga.

Esto **corrige** la advertencia que aparecÃ­a antes en esta nota (y en [[Inconsistencias y Decisiones Pendientes]], punto C-4): no hay indicio de fuga; al contrario, la Etapa I es un caso bien controlado y vale la pena documentarlo asÃ­ en el trabajo de grado, con el detalle metodolÃ³gico completo, porque es un argumento a favor de la robustez del enfoque (segmentar antes de clasificar), no solo una cifra bonita.

Lo que sigue pendiente **no es "descartar fuga"**, sino:
- Confirmar el desglose por especie completo de esa corrida (la tabla ya documentada en la estrategia de dataset cubre 10 especies).
- Repetir el protocolo exacto (segmentaciÃ³n binaria + `GroupSplit`) al escalar a mÃ¡s especies, para verificar que el resultado se sostiene y no era particular de esas 10.
- Documentar formalmente el modelo de segmentaciÃ³n binaria usado en la Etapa I (arquitectura, entrenamiento) como antecedente directo del modelo de segmentaciÃ³n anatÃ³mica de 16 regiones de la [[GuÃ­a CVAT â€” Ãndice|guÃ­a CVAT]] â€” son dos pasos de la misma idea, con distinto nivel de granularidad.

## 8. Rol en la rama de audio: modelo propio dedicado (revisado 2026-09-08)

> [!warning] DecisiÃ³n revertida: ya no se reutiliza un backbone compartido
> La versiÃ³n anterior de esta secciÃ³n proponÃ­a reutilizar el codificador de BioCLIP sobre el mel-espectrograma. Esa idea dependÃ­a de que BioCLIP viajara al dispositivo â€” dejÃ³ de ser cierto tras el fracaso de INT8 (Â§6, ver el aviso al inicio de la nota). Con EdgeNeXt-Tiny como modelo on-device, la reutilizaciÃ³n pierde su argumento fuerte: EdgeNeXt-Tiny fue destilado con un objetivo estrecho (imitar a BioCLIP especÃ­ficamente para morfologÃ­a de rana en fotos naturales), asÃ­ que no hay garantÃ­a de que transfiera bien a espectrogramas â€” a diferencia de BioCLIP, que sÃ­ es un modelo fundacional con features generales. AdemÃ¡s, el ahorro de almacenamiento de reutilizar ya no es decisivo: un modelo de audio dedicado a esta escala (1-3 MB) es tan pequeÃ±o que no compromete el presupuesto revisado (~15-30 MB total, ver C-5). **DecisiÃ³n del autor (2026-09-08, C-7):** modelo de audio propio y dedicado, por facilidad de implementaciÃ³n.

```
Audio 3-5 s (WAV mono 44,1 kHz)   [[Estrategia de ConstrucciÃ³n del Dataset]]
        â†“
Mel-espectrograma (~128 Ã— 256)
        â†“
   Modelo de audio dedicado (CNN pequeÃ±a, 1-3 MB â€” arquitectura a definir,
   referencia: BirdNET-lite / PANNs-tiny)
        â†“
Embedding o clasificaciÃ³n acÃºstica directa
        â†“
â†’ fusiÃ³n multimodal ([[Arquitectura Multimodal]])
```

Consideraciones que siguen vigentes de la versiÃ³n anterior:

- La augmentaciÃ³n para esta rama es **SpecAugment** (`TimeShift`, `FrequencyMasking`, `TimeMasking`), no la augmentaciÃ³n geomÃ©trica de fotos: voltear un espectrograma en frecuencia produce un canto fÃ­sicamente imposible.
- Carga on-demand: el modelo de audio se activa solo al grabar y se libera despuÃ©s â€” ver [[OptimizaciÃ³n para Inferencia en MÃ³vil]] Â§4. Este patrÃ³n no cambia por tener modelo propio.
- **Bloqueante previo a construir esto**: confirmar que existe dataset de audio (grabaciÃ³n propia o AnuraSet/Xeno-canto) con cobertura razonable de las 28 especies. Punto Go/No-Go ya fijado en [[Cronograma y Plan de Trabajo]] para el 18 sep â€” si no hay cobertura suficiente, la rama de audio se declara trabajo futuro y no se invierte mÃ¡s tiempo en ella dentro del sprint del prototipo.

## 9. Arquitectura del modelo de audio propio â€” por definir

Con la reutilizaciÃ³n descartada, queda pendiente elegir la arquitectura concreta del modelo dedicado. Candidatas, de menor a mayor capacidad:

| Arquitectura | TamaÃ±o aprox. | Referencia |
| --- | --- | --- |
| CNN pequeÃ±a custom (4-6 capas conv sobre mel-espectrograma) | <1 MB | Suficiente si el nÃºmero de especies con audio es reducido |
| MobileNetV1/V2 adaptada (1 canal de entrada) | 1-3 MB | Punto de partida razonable, arquitectura probada en mÃ³vil |
| Arquitectura estilo BirdNET-lite (EfficientNet-lite reducido) | 2-6 MB | Referencia validada en bioacÃºstica a escala similar (miles de especies de aves; aquÃ­ serÃ­an 28) |

**No hay comparaciÃ³n experimental corrida todavÃ­a** â€” es trabajo pendiente, condicionado al bloqueante de dataset de audio de arriba. Registrar en [[Experimentos y Resultados]] cuando se ejecute.

## 10. QuÃ© falta por decidir o medir

- [x] Fijar versiÃ³n (v1 vs v2) â†’ **resuelto 2026-09-05: BioCLIP v1** para el sprint del prototipo (evita el problema de espacios de embedding incompatibles dentro del plazo del 27 de septiembre) â†’ [[Inconsistencias y Decisiones Pendientes]]. Matiz 2026-09-08 (C-5): v1 ya no corre en el dispositivo, solo en servidor como teacher de destilaciÃ³n. v2 en servidor queda abierto como mejora posterior al prototipo.
- [x] Revisar pesos de BioCLIP v1 y definir caracterÃ­sticas Ã³ptimas â†’ **resuelto 2026-09-08**: ViT-B/16 (~86M parÃ¡metros), fine-tuned, confirmado para su rol de teacher en servidor â†’ [[Inconsistencias y Decisiones Pendientes]] (C-5).
- [x] Backbone on-device tras fracaso de INT8 â†’ **resuelto 2026-09-08**: EdgeNeXt-Tiny destilado con Multi-Head Loss â†’ C-5.
- [x] Rama de audio: Â¿reutilizar backbone o modelo propio? â†’ **resuelto 2026-09-08**: modelo propio dedicado â†’ C-7. El experimento de comparaciÃ³n (antiguo Â§9) queda descartado por decisiÃ³n directa, no por resultado medido.
- [ ] Medir zero-shot como lÃ­nea base antes de entrenar nada.
- [ ] Completar la comparaciÃ³n formal A/B/C del Â§5 (ya con C como candidato fuerte).
- [ ] Elegir y entrenar la arquitectura del modelo de audio dedicado (Â§9) â€” condicionado a confirmar cobertura de dataset de audio para las 28 especies.
- [ ] Verificar el tamaÃ±o real de EdgeNeXt-Tiny cuantizado en el Samsung Galaxy A30 (dispositivo de referencia confirmado 2026-09-08).
- [ ] Confirmar la licencia de uso de los pesos de BioCLIP para uso en servidor (ya no aplica distribuciÃ³n en el APK, al no viajar al dispositivo).
- [ ] Documentar formalmente el modelo de segmentaciÃ³n binaria de la Etapa I.

## Referencias

- Stevens et al. (2024). *BioCLIP: A Vision Foundation Model for the Tree of Life*. CVPR 2024. [arXiv:2311.18803](https://doi.org/10.48550/arXiv.2311.18803)
- Imageomics. *BioCLIP 2* â€” modelo y tarjeta del modelo. [github.com/Imageomics/bioclip-2](https://github.com/Imageomics/bioclip-2) Â· [huggingface.co/imageomics/bioclip-2](https://huggingface.co/imageomics/bioclip-2)
- Pan & Yang (2010). *A survey on transfer learning*. [doi:10.1109/TKDE.2009.191](https://doi.org/10.1109/TKDE.2009.191)
- CaÃ±as et al. (2023). *AnuraSet*. [arXiv:2307.06860](https://doi.org/10.48550/arXiv.2307.06860) â€” referencia de comparaciÃ³n para la rama acÃºstica.

Ver tambiÃ©n: [[BibliografÃ­a]]



