---
title: "Experimentos y Resultados"
proyecto: Anura
tipo: evaluaciÃ³n
estado: bitÃ¡cora-activa
tags: [anura, evaluaciÃ³n, experimentos, bitÃ¡cora]
---

# Experimentos y Resultados

[[Anura â€” Ãndice General]] Â· [[EvaluaciÃ³n y MÃ©tricas â€” Ãndice]] Â· [[MÃ©tricas Offline]] Â· [[Ciclo de Vida del Modelo (MLOps)]]

> [!abstract] CÃ³mo usar esta nota
> BitÃ¡cora cronolÃ³gica de experimentos. Un experimento = una pregunta con una respuesta medida. Se registra **antes** de ejecutarlo (objetivo e hipÃ³tesis) y se completa despuÃ©s (resultados y decisiÃ³n). Registrar la hipÃ³tesis antes evita el sesgo de reinterpretar el resultado a conveniencia.

## Registro de experimentos

| ID | Fecha | Pregunta | Resultado | DecisiÃ³n |
| --- | --- | --- | --- | --- |
| EXP-001 | 2026-09-11 | Â¿CuÃ¡nto gana el Transfer Learning sobre BioCLIP zero-shot, con oversampling proporcional y class weights, sobre las 41 especies? | Top-1 test: 35,3 %â†’44,2 % (Fase A, solo cabezas) â†’54,4 %â†’**57,0 %** (Fase B, fine-tune) | âœ… Se adopta como checkpoint base (`bioclip_anura_mejor.pt`) |
| EXP-002 | 2026-09-11 | Â¿El 57 % Top-1 estÃ¡ parejo entre especies o lo arrastran unas pocas escasas? | Escasas (<45 ind. reales): 53,1 % Â· Abundantes (â‰¥45): 56,7 % â€” **hipÃ³tesis de daÃ±o por escasez rechazada**; el problema es concentrado en Dendropsophus (similitud morfolÃ³gica real, no datos) | âœ… No relanzar con mÃ¡s oversampling; el techo es taxonÃ³mico |
| EXP-003 | 2026-09-11 | Las fotos mal clasificadas en Dendropsophus, Â¿son mal etiquetado o confusiÃ³n genuina? | RevisiÃ³n visual de 97 fallos: mismo patrÃ³n de "mÃ¡scara" oscura/dorada en `ebraccatus` y `triangulum` (par mÃ¡s confundido, 15 casos) â€” confusiÃ³n real, no error de datos. Se encontraron y limpiaron 2 casos reales de ruido: 1 foto de amplexo (2 individuos) y 1 individuo con protocolo de manejo en mano | âœ… Eliminadas 2 fotos; el resto del daÃ±o se acepta como lÃ­mite biolÃ³gico del gÃ©nero |
| EXP-004 | 2026-09-12 | Â¿CuÃ¡ntas fotos de manejo (mano) o amplexo (mÃºltiples individuos) contaminan las 41 especies? | Detector CLIP zero-shot texto-imagen: 2.091/12.256 candidatas (umbral bajo, ruidoso) â†’ 50 candidatas de alta confianza (margen > 0,10). CalibraciÃ³n manual: ~65-70 % precisiÃ³n (2/3 verdaderos en muestra) | ðŸŸ¡ Lista generada, pendiente de revisiÃ³n manual completa por el autor |
| EXP-005 | 2026-09-12 | Â¿El vientre translÃºcido de Sachatamia (rana de cristal) debe descartarse como el resto de fotos de mano? | No â€” es el rasgo diagnÃ³stico que da nombre al grupo. Encontrada 1 foto con el corazÃ³n visible a travÃ©s de la piel ventral, en mano. Clasificador automÃ¡tico dorsal/ventral con prompts de texto no fue confiable (falso positivo en foto de amplexo dorsal) | âœ… RevisiÃ³n manual 1x1 de 41 fotos; eliminada 1 de amplexo, conservado el resto con categorÃ­a especial |
| EXP-006 | 2026-09-12 | Â¿CuÃ¡nto degrada fp16 y cuÃ¡nto degrada int8 el clasificador completo, en CPU real? | fp16: âˆ’0,1 pp (56,8â†’56,7 %). int8 dinÃ¡mico (PyTorch): âˆ’5,4 pp, y solo 1,17Ã— mÃ¡s rÃ¡pido en CPU (no el 2-3Ã— esperado) | âœ… fp16 adoptado; int8 dinÃ¡mico descartado |
| EXP-007 | 2026-09-12 | Â¿CuÃ¡nto mejora el reconocimiento si se usa la ubicaciÃ³n GPS como prior? | +24,9 pp en el test completo; **+15,3 pp** en el subconjunto geogrÃ¡ficamente aislado (>10 km de train, n=72) â€” la mejora decae con la distancia de forma gradual, seÃ±al de biogeografÃ­a real, no memorizaciÃ³n de coordenadas | âœ… Se adopta (`w=0,75`), pendiente de implementaciÃ³n en Kotlin |
| EXP-008 | 2026-09-12 | Â¿Se puede exportar el clasificador completo (no solo el encoder) a ONNX para producciÃ³n mÃ³vil? | SÃ­, tras resolver 4 bugs de exportaciÃ³n distintos (ver [[OptimizaciÃ³n para Inferencia en MÃ³vil]] Â§3). 100 % de predicciones idÃ©nticas a PyTorch en validaciÃ³n | âœ… `anura_clasificador_fp16.onnx` (165,6 MB) es el artefacto de producciÃ³n |
| EXP-009 | 2026-09-12 | Â¿CuÃ¡nta RAM y latencia real usa el modelo en emulaciÃ³n de gama de celular (1/2/4 hilos)? | RAM: ~405 MB de pico (constante entre 1-4 hilos). Latencia: 403 ms (1 hilo) â†’ 154 ms (4 hilos) | âœ… Requisitos mÃ­nimos/recomendados fijados en [[OptimizaciÃ³n para Inferencia en MÃ³vil]] Â§7 |
| EXP-010 | 2026-09-12 | Â¿Puede la cuantizaciÃ³n estÃ¡tica int8 de ONNX Runtime (distinta de la dinÃ¡mica de PyTorch) reducir RAM sin destruir la precisiÃ³n? | **No, en tres configuraciones distintas**: per-channel corrompe (3,5 % Top-1, bug de ejes en LayerNorm), per-tensor+MinMax colapsa (8,2 %), per-tensor+Percentile revienta por memoria. Confirma de forma independiente el hallazgo de C-5 (BioCLIP-INT8: ~0,2 % en esa corrida) | âŒ Descartado sin remedio simple â€” la vÃ­a real serÃ­a *quantization-aware training* |
| EXP-011 | 2026-09-11 | Â¿La variante C (recorte + mÃ¡scara de segmentaciÃ³n binaria) sigue mejorando el Top-1 al escalar de 10 a 41 especies? | **No** â€” peor que sin segmentar en el mismo tramo de entrenamiento (Top-1 especie 26,5â†’32,8 % en 5 Ã©pocas de cabezas, vs. 35,3â†’41,9 % en variante A). MÃ¡scaras confirmadas disponibles y usables (99,1-99,3 % del dataset) â€” no fue un problema de cobertura de datos | ðŸŸ¡ Corrida abandonada esa noche; se retomÃ³ variante A (imagen completa) para el checkpoint de producciÃ³n. Aclarado por el autor (2026-09-12, C-13): el segmentador usado es el **binario**, no el semÃ¡ntico (16 etiquetas), que sigue en desarrollo aparte |
| EXP-012 | 2026-09-12 | DiagnÃ³stico de EXP-011: Â¿por quÃ© empeora el recorte binario, y arreglarlo lo revierte? | **Causa encontrada y confirmada con evidencia visual y cuantitativa**: el segmentador se entrenÃ³ con 9 especies y se aplicÃ³ a 41 (domain shift real); `fg_medio` de solo 6-18 % en todo el dataset; y un **bug de diseÃ±o** â€” el recorte tomaba el bbox de *todos* los pÃ­xeles marcados, sin filtrar componentes conexos (34,2 % de las mÃ¡scaras de `Dendrobates_truncatus` tienen â‰¥2 islas separadas de ruido, inflando el bbox al doble del Ã¡rea real de la rana). **Tras aplicar el fix** (componente conexo mÃ¡s grande) y repetir en inferencia pareada sobre 150 imÃ¡genes de test (38 especies aleatorias, mismo modelo, mismas imÃ¡genes): **el recorte arreglado sigue siendo peor que la imagen completa (60,7 %â†’50,7 % Top-1, âˆ’10 pp)** | ðŸŸ¡ El fix por sÃ­ solo, aplicado solo en *inferencia* a un modelo que nunca vio recortes en entrenamiento, no resuelve el problema por sÃ­ mismo â€” ver EXP-013, que encontrÃ³ un segundo problema |
| EXP-013 | 2026-09-12 | El cÃ³digo de variante C Â¿aplica la mÃ¡scara pixel a pixel (fondo a negro) como documenta [[Modelo de VisiÃ³n â€” BioCLIP]] Â§5, o solo recorta? | **Solo recortaba** â€” nunca ponÃ­a el fondo a negro, dejando todo el fondo original visible dentro del bbox. Corregido, y repetido el experimento pareado con 3 vÃ­as (completa / zoom sin mÃ¡scara / zoom con fondo a negro): **el fondo a negro es AÃšN PEOR que solo el zoom** (44,7 % vs. 50,7 % vs. 60,7 % Top-1). Contradice la hipÃ³tesis de que faltaba aplicar bien la mÃ¡scara â€” aplicarla correctamente empeora mÃ¡s, porque un fondo negro artificial es una distribuciÃ³n mÃ¡s lejana de lo que BioCLIP (preentrenado en fotos naturales) conoce que un simple cambio de encuadre | âŒ Ninguna de las dos correcciones, aplicadas solo en inferencia, arregla el problema â€” ambas son evidencia de mismatch de dominio, no de que la variante C sea mala per se. **Pendiente real, sin probar todavÃ­a: reentrenar Fase 4 desde cero sobre el recorte con fondo a negro (variante C real, con ambos fixes)** |
| EXP-014 | 2026-09-13 | Â¿CuÃ¡nta precisiÃ³n se pierde (o gana) al pasar del clasificador softmax (Ruta A) a k-NN sobre embeddings + SQLite-vec (Ruta B, firmada en C-15 para cumplir el patrÃ³n Merlin)? | Mismo encoder (checkpoint de Fase 4), mismo test set de 766 imÃ¡genes que Fase 5, 3.260 embeddings de train como base de referencia (1 imagen del manifiesto ya no existe en disco, omitida). **1-NN puro: 53,9 % Top-1 / 77,9 % Top-3 (âˆ’3,1 pp vs. clasificador). k-NN (k=5, voto ponderado por similitud): 56,4 % Top-1 / 77,9 % Top-3 (âˆ’0,7 pp vs. clasificador)**, con las **41 especies completas** en el paquete de referencia. El Top-3 pierde mÃ¡s (âˆ’4,5 pp) porque el voto por k=5 vecinos satura antes que las probabilidades softmax de 41 clases | ðŸŸ¡ VÃ¡lido solo como techo pesimista â€” ver EXP-015, que mide con un paquete regional real (menos especies candidatas) y encuentra el resultado opuesto |
| EXP-015 | 2026-09-13 | Repetir EXP-014 pero con un paquete regional **real** (Antioquia, filtrado geogrÃ¡ficamente, no las 41 especies completas) â€” Â¿sigue perdiendo precisiÃ³n la Ruta B frente al clasificador? | Se exportÃ³ primero el **encoder solo a ONNX** (pendiente detectado en C-15 â€” Fase 6 solo dejÃ³ `.pt`, nunca se habÃ­a exportado a ONNX): `encoder_anura_fp16.onnx` (165,4 MB), validado con similitud coseno 0,999999 vs. PyTorch en 64 imÃ¡genes reales. Luego se filtraron las especies con presencia real en Antioquia usando las coordenadas ya auditadas de `prior_geografico_movil.json` (bbox del departamento, â‰¥3 observaciones de train dentro): **25 de 41 especies** califican. Sobre las 467 imÃ¡genes de test (de 766) cuya especie real es una de esas 25: **Ruta B (k-NN k=5, paquete de 25 especies): 66,2 % Top-1 / 83,7 % Top-3. Ruta A (clasificador de 41 clases, mismo subconjunto de test): 54,4 % Top-1 / 79,9 % Top-3.** **Î” Top-1 = +11,8 pp a favor de Ruta B** â€” se invierte por completo el resultado de EXP-014 | âœ… **Ruta B con paquete regional filtrado es MEJOR que el clasificador, no solo "aceptablemente peor"**. La causa es mecÃ¡nica, no casualidad: el clasificador de 41 clases siempre reparte probabilidad entre las 16 especies que NO son de Antioquia (puro desperdicio de masa de probabilidad para un usuario en Antioquia); el k-NN sobre el paquete regional nunca compara contra esas 16, asÃ­ que cada vecino "cuenta" solo entre candidatos plausibles. Esto es evidencia directa de que segmentar por regiÃ³n (el corazÃ³n del patrÃ³n Merlin) no es solo una conveniencia de descarga â€” es una mejora de precisiÃ³n real. Se generÃ³ `antioquia_v1.sqlite` (6,39 MB, 2.073 vectores, 25 especies) como el primer paquete regional filtrado geogrÃ¡ficamente de verdad â€” ver [[Base Vectorial (SQLite-vec)]] |

---

## Plantilla

```markdown
### EXP-000 â€” [TÃ­tulo corto]

**Fecha:** 
**Responsable:** 

**Objetivo**
QuÃ© se quiere averiguar, en una frase.

**HipÃ³tesis** (antes de ejecutar)
QuÃ© se espera que ocurra y por quÃ©.

**ConfiguraciÃ³n**
| Elemento | Valor |
| --- | --- |
| Modelo / backbone | |
| VersiÃ³n de dataset | |
| Split | |
| HiperparÃ¡metros | |
| AugmentaciÃ³n | |
| Semilla | |
| Hardware | |
| DuraciÃ³n | |

**Resultados**
| MÃ©trica | Base | Este experimento | Î” |
| --- | --- | --- | --- |

**AnÃ¡lisis**
QuÃ© pasÃ³ y por quÃ©. Incluir lo que no encaja con la hipÃ³tesis.

**DecisiÃ³n**
- [ ] Se adopta
- [ ] Se descarta
- [ ] Requiere mÃ¡s experimentos

**Siguiente paso**
```

---

## Cola de experimentos planificados

Priorizados. Los cuatro primeros son los que sostienen el capÃ­tulo de resultados.

| Prioridad | Experimento | Pregunta | Nota de referencia |
| --- | --- | --- | --- |
| **1** | LÃ­nea base BioCLIP zero-shot | Â¿CuÃ¡nto sabe el modelo sin ver una sola foto del dataset? | [[Modelo de VisiÃ³n â€” BioCLIP]] |
| **1** | Documentar formalmente el protocolo de la Etapa I | El ~99 % ya estÃ¡ explicado (segmentaciÃ³n binaria + `GroupSplit` por individuo) â€” falta dejar el desglose completo y la arquitectura del segmentador binario por escrito | [[Modelo de VisiÃ³n â€” BioCLIP]] Â§7 |
| **1** | Entrada A/B/C (completa / recorte / recorte+mÃ¡scara) | Â¿Se sostiene la ventaja de la mÃ¡scara binaria (variante C) al escalar el catÃ¡logo? | [[Modelo de VisiÃ³n â€” BioCLIP]] Â§5 |
| **1** | AblaciÃ³n multimodal | Â¿CuÃ¡nto aporta cada modalidad? | [[Arquitectura Multimodal]] Â§4 |
| 2 | BioCLIP compartido vs. modelo acÃºstico dedicado | Â¿Reutilizar BioCLIP para audio rinde cerca de un modelo especializado (BirdNET/PANNs/AnuraSet)? | [[Modelo de VisiÃ³n â€” BioCLIP]] Â§9 |
| 2 | Open-set: MSP vs. Energy vs. Mahalanobis | Â¿QuÃ© detector de desconocidos usar? | [[Open-Set Recognition]] |
| 2 | Impacto de la cuantizaciÃ³n | Â¿Cabe en mÃ³vil sin perder mÃ¡s del 2 % de F1? | [[OptimizaciÃ³n para Inferencia en MÃ³vil]] |
| 2 | ValidaciÃ³n de sqlite-vec en dispositivo | Â¿Latencia y memoria dentro de presupuesto con 10â€“50 k vectores? | [[Base Vectorial (SQLite-vec)]] Â§2 |
| 3 | Triplet loss vs. embeddings congelados | Â¿Compensa el metric learning con este dataset? | [[ImplementaciÃ³n de Triplet Loss]] |
| 3 | RecuperaciÃ³n vectorial | Â¿Los vecinos mÃ¡s cercanos son de la especie correcta? | âœ… Resuelto â€” ver EXP-014 abajo |
| 3 | ClasificaciÃ³n jerÃ¡rquica con y sin enmascarado | Â¿CuÃ¡ntas predicciones incoherentes se evitan? | [[Modelo de VisiÃ³n â€” BioCLIP]] Â§4 |

## Resultados consolidados

Se rellena a medida que se cierran experimentos. Es el material directo del capÃ­tulo de resultados.

### Hallazgo 1 â€” La segmentaciÃ³n binaria explicÃ³ el ~99 % de la Etapa I, pero **no se sostuvo al escalar a 41 especies**

Con 10 especies, 70 individuos por especie, segmentaciÃ³n binaria (individuo vs. fondo) aplicada antes de pasar el recorte a BioCLIP, y `GroupSplit` por individuo, la Etapa I alcanzÃ³ **~99 % de exactitud**. No es un artefacto de fuga de informaciÃ³n: las tres condiciones que normalmente inflan un resultado (fondo como atajo, mismo individuo en train y test, pocas variantes por clase) estÃ¡n controladas por diseÃ±o. Detalle completo en [[Modelo de VisiÃ³n â€” BioCLIP]] Â§7.

> [!warning] ActualizaciÃ³n 2026-09-12 â€” la implicaciÃ³n original de este hallazgo queda revisada
> Se probÃ³ la misma variante C (segmentada) sobre las 41 especies el 2026-09-11 (ver EXP-011) y dio **peor** resultado que sin segmentar en el mismo tramo de entrenamiento (Top-1 especie 26,5â†’32,8 % vs. 35,3â†’41,9 % sin segmentar). Aclarado por el autor: el segmentador usado en esa corrida es el **binario** (el mismo tipo que sostiene el 99 % de arriba) â€” no el de segmentaciÃ³n **semÃ¡ntica** (16 etiquetas anatÃ³micas), que sigue en desarrollo aparte y no se ha probado todavÃ­a en el pipeline de identificaciÃ³n. La implicaciÃ³n ya no es "segmentar antes de clasificar no es opcional" sin matiz: es opcional **hasta que se entienda por quÃ© el segmentador binario empeora el resultado al escalar** (Â¿calidad de mÃ¡scara en datos de campo mÃ¡s heterogÃ©neos? Â¿el corte binario elimina contexto Ãºtil que el ViT sÃ­ aprovechaba?). Por ahora, el pipeline de producciÃ³n (Fases 4-7, checkpoint vigente) usa **variante A (imagen completa, sin segmentar)**.

### Hallazgo 2 â€” La ubicaciÃ³n GPS aporta mÃ¡s que cualquier ajuste al modelo visual

Un prior geogrÃ¡fico simple (conteo de observaciones de train en 50 km, suavizado, combinado con peso 0,75) mejora el Top-1 de **57 % a 81 %** sobre el test completo, y de forma conservadora (>10 km de cualquier punto conocido) sigue aportando **+15 pp**. Para comparaciÃ³n: todo el fine-tuning de Fase 4 (oversampling + class weights + augmentaciÃ³n agresiva) ganÃ³ +8,9 pp sobre el zero-shot. La ubicaciÃ³n, con una implementaciÃ³n mucho mÃ¡s simple, gana casi el triple. Detalle y validaciÃ³n anti-fuga en [[OptimizaciÃ³n para Inferencia en MÃ³vil]] Â§6.

### Hallazgo 3 â€” Un ViT no se puede cuantizar a int8 "de fÃ¡brica", con ninguna herramienta estÃ¡ndar probada

Se intentÃ³ int8 por dos caminos (cuantizaciÃ³n dinÃ¡mica de PyTorch, cuantizaciÃ³n estÃ¡tica de ONNX Runtime en tres configuraciones) y los cinco intentos degradan el modelo a niveles inutilizables o peores que fp16 en tamaÃ±o real. Esto **confirma de forma independiente**, meses despuÃ©s y con herramientas distintas, el mismo hallazgo de C-5 (BioCLIP-INT8 fracasÃ³ en pruebas reales, ~0,2 % exactitud). La causa de fondo (documentada en la literatura de cuantizaciÃ³n de Transformers) es que el `Softmax` de atenciÃ³n y los `LayerNorm` tienen rangos dinÃ¡micos que una escala entera simple no representa sin perder la seÃ±al. **fp16 es el techo prÃ¡ctico de compresiÃ³n sin reentrenar.**

### Hallazgo 4 â€” El recorte binario, incluso arreglado (y aplicado como se documentÃ³ originalmente), no sirve sin reentrenar (EXP-011/EXP-012/EXP-013)

DiagnÃ³stico completo del fracaso de variante C en el escalado a 41 especies, con evidencia visual y cuantitativa. Dos problemas distintos encontrados y aislados por separado:

**Problema 1 â€” bug de diseÃ±o en el bbox.** `_recortar_por_mascara` tomaba el bounding-box de **todos** los pÃ­xeles marcados como foreground por el segmentador, sin distinguir la rana del ruido disperso. Con el segmentador entrenado en solo 9 especies y aplicado a 41, ese ruido es frecuente (34,2 % de las mÃ¡scaras de `Dendrobates_truncatus` tienen â‰¥2 componentes separados) y un solo falso positivo lejano estira el recorte hasta casi la imagen completa. Fix: quedarse con el componente conexo mÃ¡s grande.

**Problema 2 â€” el cÃ³digo nunca aplicaba la mÃ¡scara sobre los pÃ­xeles.** La definiciÃ³n documentada de variante C ([[Modelo de VisiÃ³n â€” BioCLIP]] Â§5, la que sostuvo el ~99 % de la Etapa I) es *"recorte **con fondo puesto a negro/neutro** usando la mÃ¡scara binaria"* â€” no solo un zoom rectangular. El cÃ³digo de Fase 4 solo hacÃ­a el recorte, dejando el fondo original completamente visible dentro de la caja. Fix: enmascarar pixel a pixel (fondo a negro) antes de recortar.

**Diez ejemplos reales, 3 paneles cada uno** (original | zoom sin mÃ¡scara | zoom con fondo a negro â€” la variante C real):

![[00_Dendrobates_truncatus_fg2%_bbox3%.jpg]]
![[03_Phyllomedusa_venusta_fg3%_bbox4%.jpg]]
![[05_Boana_xerophylla_fg39%_bbox69%.jpg]]

*(el resto de las 10 imÃ¡genes estÃ¡n en `99 Recursos/Attachments/exp_ab_recorte/`)*

**Experimento pareado de 3 vÃ­as:** mismo checkpoint (Fase 4, entrenado en variante A), mismas 150 imÃ¡genes de test (38 especies aleatorias, semilla fija):

![[exp_ab_grafico.png]]

| | Top-1 | Top-3 |
| --- | --- | --- |
| Imagen completa | **60,7 %** | **83,3 %** |
| Recorte zoom (sin mÃ¡scara) | 50,7 % | 80,7 % |
| **Recorte + fondo a negro (variante C real)** | **44,7 %** | **75,3 %** |

**Resultado que contradice la hipÃ³tesis inicial de "falta aplicar bien la mÃ¡scara":** aplicar la mÃ¡scara real (fondo a negro, como en la Etapa I) **no arregla el problema â€” lo empeora todavÃ­a mÃ¡s** que solo el zoom (de 32 casos daÃ±ados, contra 23 del zoom solo). InterpretaciÃ³n: BioCLIP fue preentrenado sobre millones de fotos naturales (TreeOfLife-10M) y el fine-tuning de Fase 4 vio siempre fondo natural â€” un fondo negro artificial es una distribuciÃ³n de imagen mÃ¡s lejana de lo que el modelo conoce que un simple cambio de encuadre. Cuanto mÃ¡s se aleja la entrada de lo visto en entrenamiento, peor rinde (ver el panel de dispersiÃ³n: los puntos de "fondo a negro" caen sistemÃ¡ticamente mÃ¡s bajo que los de "solo zoom").

**Lo que esto NO demuestra:** que la variante C sea inherentemente mala. Los tres formatos se evaluaron con un modelo que solo vio imagen completa en entrenamiento â€” es exactamente el mismatch de dominio esperado en cualquiera de las dos transformaciones. La pregunta que sigue abierta y sin responder: **Â¿mejora el Top-1 si Fase 4 se reentrena desde cero sobre el recorte con fondo a negro (la variante C real, con ambos fixes ya aplicados)?** Es el Ãºnico experimento que puede decidir si variante C vuelve a ser viable â€” nada de lo hecho hoy lo prueba ni lo descarta.

## GrÃ¡fico consolidado â€” rendimiento de todos los modelos probados (Ã©xito y fracaso)

Todo lo que se intentÃ³ para el backbone de identificaciÃ³n, en una sola vista. Eje Y = Top-1 sobre test; el color/orden separa quÃ© arquitectura y quÃ© formato de despliegue.

```mermaid
xychart-beta
    title "Todos los modelos probados â€” Top-1 (%) en test"
    x-axis ["BioCLIP\nzero-shot", "BioCLIP FT\nvariante A\n(sin crop)", "BioCLIP FT\nvariante C\n(con mÃ¡scara,\nEtapa I 10 esp.)", "MobileNetV3\ndestilado\n(C-10)", "BioCLIP FT\nfp32 (41 esp.)", "BioCLIP FT\nfp16 (41 esp.)", "BioCLIP FT\nint8 dinÃ¡mico", "BioCLIP FT\nint8 estÃ¡tico\n(mejor intento)", "BioCLIP FT fp16\n+ prior GPS"]
    y-axis "Top-1 (%)" 0 --> 100
    bar [35.3, 44.2, 99, 24.3, 56.8, 56.7, 51.4, 8.2, 81.4]
```

**Lectura del grÃ¡fico:**
- La barra de **99 %** (Etapa I, 10 especies, con segmentaciÃ³n **binaria**) y la de **57 %** (41 especies, sin segmentaciÃ³n) no son comparables directamente â€” distinto nÃºmero de especies, y la segmentaciÃ³n binaria **ya se probÃ³** en las 41 especies (EXP-011, 11 sep) y dio peor resultado, no mejor. No es un experimento pendiente: es un experimento hecho con resultado negativo, sin diagnosticar todavÃ­a. La segmentaciÃ³n **semÃ¡ntica** (16 etiquetas anatÃ³micas) sigue sin probarse en este pipeline.
- La barra de **destilaciÃ³n MobileNetV3 (C-10, 24,3 %)** es la que motivÃ³ abandonar esa ruta â€” comparada con las variantes de BioCLIP fp32/fp16 (56,7-56,8 %), la brecha de 32 puntos es la evidencia directa de por quÃ© C-11 evita destilar.
- La barra final, **fp16 + prior GPS (81,4 %)**, es el mejor nÃºmero de todo el proyecto hasta ahora para el catÃ¡logo de 41 especies â€” y es el que se debe reportar como resultado principal del capÃ­tulo de resultados, con la salvedad honesta del +15 pp en el subconjunto aislado (Hallazgo 2).

## Experimentos descartados

Igual de importantes: documentan quÃ© no funcionÃ³ y evitan repetirlo.

| ID | QuÃ© se probÃ³ | Por quÃ© se descartÃ³ |
| --- | --- | --- |
| C-5 | BioCLIP-INT8 (pesos INT8 + activaciones FP16) como backbone on-device | ~0,2 % exactitud â€” outliers de atenciÃ³n del ViT destruidos por la cuantizaciÃ³n |
| C-10 | DestilaciÃ³n BioCLIP v1 â†’ MobileNetV3-Small (Multi-Head Loss) | Top-1 teacher 57,7 % â†’ student 24,3 % (degradaciÃ³n de 33 puntos, objetivo <10). Sin segmentaciÃ³n previa, la imagen completa no da seÃ±al suficiente al alumno pequeÃ±o |
| EXP-006/EXP-010 | int8 dinÃ¡mico (PyTorch) e int8 estÃ¡tico (ONNX, 3 configuraciones) sobre el clasificador completo fp32 | DinÃ¡mico: âˆ’5,4 pp sin ganancia real de tamaÃ±o ni velocidad sobre fp16. EstÃ¡tico: corrupciÃ³n total o colapso (3,5-8,2 % Top-1) en las tres configuraciones probadas |
| â€” | `opset_version=17` forzado en la exportaciÃ³n ONNX | CorrompÃ­a el grafo en silencio (archivo de 1,2 MB en vez de ~330 MB) â€” ver [[OptimizaciÃ³n para Inferencia en MÃ³vil]] Â§3 |
| â€” | `dynamic_axes` (batch dinÃ¡mico) en la exportaciÃ³n ONNX | RompÃ­a el reshape de atenciÃ³n multi-cabeza del exportador dynamo |

> [!tip] Herramienta de seguimiento
> Esta nota funciona como bitÃ¡cora legible y para el documento escrito. Para el detalle numÃ©rico (curvas, hiperparÃ¡metros, artefactos) conviene MLflow o Weights & Biases, y enlazar aquÃ­ la ejecuciÃ³n correspondiente. Ver [[Ciclo de Vida del Modelo (MLOps)]].



