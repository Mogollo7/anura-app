---
title: "OptimizaciÃ³n para Inferencia en MÃ³vil"
proyecto: Anura
tipo: desarrollo-tÃ©cnico
estado: validado-empÃ­ricamente
tags: [anura, desarrollo, onnx, cuantizaciÃ³n, edge, optimizaciÃ³n]
---

# OptimizaciÃ³n para Inferencia en MÃ³vil

[[Anura â€” Ãndice General]] Â· [[App MÃ³vil]] Â· [[Modelo de VisiÃ³n â€” BioCLIP]] Â· [[Inconsistencias y Decisiones Pendientes]] (C-11)

> [!abstract] El problema en una frase
> Meter el clasificador BioCLIP v1 fine-tuned (Transfer Learning, Fase 4) en un dispositivo Android, corriendo **100 % local, sin servidor**, con latencia y RAM medidas â€” no estimadas â€” en un dispositivo real de referencia: **Redmi Note 13 Pro+**.

> [!success] Vigente desde C-11 (2026-09-11) â€” reemplaza la ruta de destilaciÃ³n
> Las rutas anteriores (EdgeNeXt-Tiny en C-5, MobileNetV3-Small en C-8) quedaron descartadas: **C-10 demostrÃ³ que destilar BioCLIP a un alumno pequeÃ±o es inviable** con la entrada actual (degradaciÃ³n de 33 puntos de Top-1, sin segmentaciÃ³n previa). La arquitectura vigente (**C-11**) es mÃ¡s simple y evita el paso de destilaciÃ³n por completo: **el propio encoder de BioCLIP fine-tuned viaja al dispositivo**, exportado a ONNX. Esta nota documenta la implementaciÃ³n completa de esa arquitectura, con every nÃºmero medido â€” no proyectado â€” sobre el pipeline real (Fases 4 a 7c de la sesiÃ³n de entrenamiento).

## 0. Resumen ejecutivo

| Pregunta | Respuesta |
| --- | --- |
| Â¿QuÃ© modelo viaja al dispositivo? | BioCLIP v1 (ViT-B/16) fine-tuned completo â€” encoder + 3 cabezas (familia/gÃ©nero/especie) |
| Â¿En quÃ© formato? | ONNX, **fp16** (165,6 MB) |
| Â¿Corre con red? | No â€” 100 % local, sin llamadas a servidor |
| Â¿Usa GPS? | SÃ­, opcional â€” prior geogrÃ¡fico embebido (Â§6), **+15 a +25 pp de Top-1** |
| Â¿CuÃ¡nta RAM real usa? | ~405 MB de pico (medido, no estimado â€” Â§5) |
| Â¿CuÃ¡nto tarda por foto? | 150 ms (gama alta, 4 hilos) a 400 ms (gama baja, 1 hilo) |
| Dispositivo de prueba fijado | **Redmi Note 13 Pro+** |

---

## 1. Ruta de exportaciÃ³n: por quÃ© ONNX y no LiteRT

La documentaciÃ³n previa de este proyecto contemplaba LiteRT (ex-TensorFlow Lite) como ruta principal. En la prÃ¡ctica, **`torch.onnx.export` fue la Ãºnica ruta que logrÃ³ trazar el ViT completo sin reescribir la arquitectura**, y el camino no fue directo â€” quedan documentados los tres fallos intermedios porque son la parte que un futuro mantenedor necesita para no repetirlos:

```mermaid
flowchart TD
    A[BioCLIP v1 fine-tuned<br/>checkpoint PyTorch] --> B{torch.jit.trace}
    B -->|âŒ falla| B1["'Graphs differed across invocations'<br/>el ViT tiene ramas condicionales internas"]
    A --> C{torch.onnx.export<br/>exportador dynamo}
    C -->|opset 17 forzado| C1["âŒ archivo de 1.2 MB<br/>conversiÃ³n de versiÃ³n corrompe el grafo en silencio"]
    C -->|opset 18 + dynamic_axes| C2["âŒ Reshape roto en atenciÃ³n multi-cabeza<br/>'input shape 197,8,768 â†’ requested 197,768'"]
    C -->|opset 18 + batch fijo=1| D["âœ… ONNX vÃ¡lido<br/>100% predicciones idÃ©nticas a PyTorch"]
    D --> E[Consolidar pesos externos<br/>.onnx + .onnx.data â†’ un solo archivo]
    E --> F["anura_clasificador.onnx<br/>330 MB, fp32"]
```

**LecciÃ³n de ingenierÃ­a que vale la pena preservar:** el batch dinÃ¡mico (`dynamic_axes`) rompe el reshape interno de atenciÃ³n multi-cabeza con el exportador dynamo de PyTorch. Como en el celular se procesa **una imagen a la vez**, fijar `batch=1` no cuesta nada y elimina el problema de raÃ­z.

---

## 2. ComparaciÃ³n de todos los formatos probados

Cuatro formatos, con Ã©xito y fracaso documentados con la misma vara: Top-1 real sobre el test set completo (766 imÃ¡genes), no una muestra ni una proxy de similitud de embeddings.

```mermaid
xychart-beta
    title "Top-1 (%) por formato â€” 766 imÃ¡genes de test"
    x-axis ["fp32 (referencia)", "fp16", "int8 dinÃ¡mico\n(PyTorch)", "int8 estÃ¡tico\n(ONNX, per-channel)", "int8 estÃ¡tico\n(ONNX, per-tensor)"]
    y-axis "Top-1 (%)" 0 --> 60
    bar [56.8, 56.7, 51.4, 3.5, 8.2]
```

| Formato | TamaÃ±o | Top-1 | Î” vs fp32 | RAM en dispositivo | Veredicto |
| --- | --- | --- | --- | --- | --- |
| **fp32** | 330,1 MB | 56,8 % | â€” | 391-392 MB | Referencia; demasiado pesado para el bundle |
| **fp16** âœ… | **165,6 MB** | **56,7 %** | **âˆ’0,1 pp** | 404-405 MB | **Formato de producciÃ³n** |
| int8 dinÃ¡mico (PyTorch) | 166,9 MB | 51,4 % | âˆ’5,4 pp | â€” | Descartado: pierde precisiÃ³n sin ganar tamaÃ±o sobre fp16 |
| int8 estÃ¡tico QDQ, per-channel | 84,2 MB | 3,5 % | **âˆ’53,3 pp** | â€” | **Corrupto** â€” bug de ejes en LayerNorm (rank 1) |
| int8 estÃ¡tico QDQ, per-tensor + MinMax | 83,7 MB | 8,2 % | âˆ’48,6 pp | â€” | Colapso â€” rango dinÃ¡mico de Softmax/LayerNorm mal capturado |
| int8 estÃ¡tico QDQ, per-tensor + Percentile | â€” | â€” | â€” | â€” | **Crash** (`bad allocation`) â€” histogramas de calibraciÃ³n exceden memoria disponible |

> [!warning] Por quÃ© int8 estÃ¡tico fracasa en un ViT â€” no es un error de configuraciÃ³n corregible
> Se intentaron tres configuraciones distintas (per-channel, per-tensor+MinMax, per-tensor+Percentile) con `onnxruntime.quantization.quantize_static`, incluyendo el paso de *shape inference* previo que la propia herramienta recomienda. Las tres fallan por la misma razÃ³n de fondo, documentada en la literatura de cuantizaciÃ³n de Transformers: el `Softmax` de las 12 capas de atenciÃ³n y los `LayerNorm` tienen rangos dinÃ¡micos que una escala entera simple no representa sin perder la seÃ±al â€” el error se acumula capa a capa. **Esto confirma, con metodologÃ­a independiente, el mismo hallazgo que ya estÃ¡ registrado en C-5** (BioCLIP-INT8 fracasÃ³ en pruebas reales, ~0,2 % exactitud) â€” dos intentos separados, meses de diferencia, mismo resultado. La vÃ­a real para int8 en un ViT serÃ­a *quantization-aware training* (reentrenar con la cuantizaciÃ³n simulada desde el principio), no una conversiÃ³n post-hoc.

---

## 3. Bugs de exportaciÃ³n encontrados y resueltos (registro tÃ©cnico)

| # | SÃ­ntoma | Causa raÃ­z | Fix |
| --- | --- | --- | --- |
| 1 | `torch.jit.trace`: "Graphs differed across invocations" | El ViT tiene ramas condicionales internas en `open_clip.transformer` | Usar `torch.onnx.export` (exportador dynamo), no `jit.trace` |
| 2 | Archivo ONNX de 1,2 MB en vez de ~330 MB, sin error visible | `opset_version=17` forzaba una conversiÃ³n de versiÃ³n (17â†’18) que corrompÃ­a el grafo en silencio | Exportar directo en `opset_version=18`, sin downgrade |
| 3 | `ReshapeHelper`: `input shape {197,8,768}` vs `requested {197,768}` | `dynamic_axes` con batch dinÃ¡mico rompe el reshape de atenciÃ³n multi-cabeza en el exportador dynamo | Fijar `batch=1` (coherente con el uso real: una imagen a la vez en el celular) |
| 4 | Pesos en un `.onnx.data` externo de 329 MB, separado del `.onnx` de 1,2 MB | El exportador dynamo usa formato "external data" por defecto en modelos grandes | Consolidar con `onnx.load(..., load_external_data=True)` + `onnx.save(..., save_as_external_data=False)` |
| 5 | ConversiÃ³n a fp16: ONNX Runtime nuevo requiere `onnxscript`, no instalado | Dependencia no declarada en el entorno | `pip install onnxscript onnxconverter-common` |
| 6 | int8 estÃ¡tico per-channel: "Axis 1 is out-of-range for weight ... with rank 1" en 24 nodos LayerNorm | `per_channel=True` intenta cuantizar por el eje 1 pesos de LayerNorm que son vectores de un solo eje (rank 1) | Cambiar a `per_channel=False` â€” no resuelve la precisiÃ³n pero sÃ­ la corrupciÃ³n |
| 7 | `quant_pre_process` con `skip_symbolic_shape=False`: `TypeError: object of type 'NoneType' has no len()` en un nodo `Expand` | Bug conocido de `symbolic_shape_infer.py` con grafos del exportador dynamo | Usar `skip_symbolic_shape=True` (shape inference bÃ¡sica, no symbolic) |

---

## 4. CuantizaciÃ³n fp16: por quÃ© se adopta pese a no ganar RAM ni velocidad

Hallazgo contraintuitivo medido directamente, no supuesto:

| | fp16 | fp32 | Diferencia |
| --- | --- | --- | --- |
| TamaÃ±o en disco | 165,6 MB | 330,1 MB | **fp16 gana: mitad de peso** |
| RAM en ejecuciÃ³n (1 hilo) | 404 MB | 391 MB | fp32 gana (marginal) |
| Latencia (1 hilo) | 403 ms | 363 ms | fp32 gana (~10 % mÃ¡s rÃ¡pido) |
| Latencia (4 hilos) | 154 ms | 127 ms | fp32 gana (~18 % mÃ¡s rÃ¡pido) |

**RazÃ³n tÃ©cnica:** las CPU de celular no tienen aceleraciÃ³n nativa fp16 para cÃ³mputo (solo GPU la tiene, tÃ­picamente). ONNX Runtime decodifica cada peso fp16â†’fp32 al vuelo antes de multiplicar, lo que aÃ±ade overhead sin ahorrar memoria de trabajo (los buffers de activaciones intermedias son fp32 en ambos casos).

**Por quÃ© se adopta igual:** la Ãºnica variable que sÃ­ mejora â€” y es la que mÃ¡s importa para una app instalable â€” es el **tamaÃ±o de descarga/almacenamiento**: la mitad de espacio en el dispositivo y la mitad de datos a transferir en la instalaciÃ³n. La pÃ©rdida de precisiÃ³n es indistinguible de ruido (**100 % de predicciones idÃ©nticas** en 64 imÃ¡genes de validaciÃ³n, diferencia mÃ¡xima de probabilidad de 1,16 Ã— 10â»Â³).

---

## 5. RAM y latencia medidas â€” emulaciÃ³n de gama de celular

MediciÃ³n real (no estimada) usando un worker de proceso aislado (solo `onnxruntime` + 
umpy`, sin PyTorch â€” para no inflar la RAM medida con dependencias que no existen en el APK), con un hilo de muestreo de memoria residente (RSS) cada 20 ms. El nÃºmero de hilos de `intra_op_num_threads` emula gama de chip:

| Config. (hilos) | Gama equivalente | RAM pico app | Latencia media | Latencia p95 | Carga inicial |
| --- | --- | --- | --- | --- | --- |
| 1 hilo | Baja (Cortex-A53, Helio G bajo) | 404 MB | 403 ms | 416 ms | 0,6 s |
| 2 hilos | Media (Snapdragon 6xx/7xx) | 405 MB | 229 ms | 260 ms | 0,6 s |
| 4 hilos | Alta (Snapdragon 8-series, Dimensity 7000+) | 405 MB | 154 ms | 192 ms | 0,6 s |

```mermaid
xychart-beta
    title "Latencia por foto segÃºn hilos de CPU disponibles (fp16)"
    x-axis ["1 hilo (gama baja)", "2 hilos (gama media)", "4 hilos (gama alta)"]
    y-axis "Latencia media (ms)" 0 --> 450
    bar [403, 229, 154]
```

**El grueso de la RAM no son los pesos del modelo** (165,6 MB en disco): son los buffers de activaciones intermedias del ViT â€” 197 tokens Ã— 768 dimensiones Ã— 12 capas de atenciÃ³n, que en el *forward pass* pesan mÃ¡s que los propios pesos. Es un comportamiento normal de cualquier ViT-B/16, no un problema especÃ­fico de este export.

---

## 6. Prior geogrÃ¡fico â€” la mejora mÃ¡s grande y mÃ¡s barata del sistema

Hallazgo de esta sesiÃ³n, validado con rigor metodolÃ³gico especÃ­fico para no confundir seÃ±al biogeogrÃ¡fica real con memorizaciÃ³n de coordenadas exactas:

$$P(\text{especie} \mid \text{foto}, \text{lugar}) \propto P(\text{especie} \mid \text{foto}) \cdot P(\text{especie} \mid \text{lugar})^{w}$$

- $P(\text{especie}\mid\text{lugar})$: conteo de observaciones de **train** dentro de 50 km, suavizado (ninguna especie recibe probabilidad cero).
- $w = 0{,}75$: peso Ã³ptimo encontrado por barrido.
- Coordenadas auditadas antes de usarlas: se descartaron 300 observaciones con `positional_accuracy` de hasta 7.270 km (basura de geolocalizaciÃ³n de iNaturalist), sin encontrar coordenadas en (0,0) ni fuera de Colombia.

| Distancia mÃ­nima a una obs. de train de la misma especie | N | Solo imagen | Con ubicaciÃ³n | Mejora |
| --- | --- | --- | --- | --- |
| Todas | 607 | 57,2 % | 81,4 % | **+24,2 pp** |
| > 5 km | 151 | 58,3 % | 79,5 % | +21,2 pp |
| **> 10 km** (estimaciÃ³n honesta para "sitio nuevo") | **72** | 55,6 % | 70,8 % | **+15,3 pp** |

```mermaid
xychart-beta
    title "Top-1 (%): imagen sola vs. imagen + ubicaciÃ³n, segÃºn distancia a datos conocidos"
    x-axis ["Todas (n=607)", "> 5 km (n=151)", "> 10 km (n=72)"]
    y-axis "Top-1 (%)" 0 --> 90
    line [57.2, 58.3, 55.6]
    line [81.4, 79.5, 70.8]
```

**InterpretaciÃ³n:** la mejora decae de forma gradual con la distancia (24 â†’ 21 â†’ 15 pp), no de golpe â€” es la firma de seÃ±al biogeogrÃ¡fica real ("esta especie vive en esta regiÃ³n"), no memorizaciÃ³n de coordenadas puntuales. El nÃºmero conservador para un usuario en un sitio genuinamente nuevo es **+15 pp**, muy por encima de cualquier ganancia obtenida ajustando el modelo visual.

**ImplementaciÃ³n on-device:** los puntos de train (1.678, 41/41 especies con soporte) se empaquetan en `prior_geografico_movil.json` (34 KB) â€” la app calcula haversine + conteo + suavizado localmente, sin llamar a ningÃºn servidor. Requiere permiso de GPS del dispositivo.

---

## 7. Dispositivo de prueba y requisitos â€” estilo "specs de videojuego"

> [!important] Dispositivo de prueba fijado: **Redmi Note 13 Pro+**
> Reemplaza como referencia de validaciÃ³n empÃ­rica al Samsung Galaxy A30 fijado en C-5 â€” aquel dispositivo (4 GB RAM) era el piso mÃ­nimo pensado para la arquitectura destilada (EdgeNeXt-Tiny / MobileNetV3-Small, <15 MB), descartada por C-10. La arquitectura vigente (C-11, BioCLIP fp16, 165,6 MB, ~405 MB de RAM en ejecuciÃ³n) necesita mÃ¡s margen de memoria; el Redmi Note 13 Pro+ (variantes de 8/12 GB RAM, Dimensity 7200-Ultra) es el dispositivo real donde se valida esta versiÃ³n. **Pendiente:** confirmar la ficha tÃ©cnica exacta de la unidad fÃ­sica disponible (variante de RAM, versiÃ³n Android/HyperOS) y repetir esta mediciÃ³n directamente en el hardware, no solo en emulaciÃ³n de hilos â€” ver C-12 en [[Inconsistencias y Decisiones Pendientes]].

| | **MÃNIMOS** | **RECOMENDADOS** |
| --- | --- | --- |
| RAM total del dispositivo | 3 GB | 6 GB+ |
| NÃºcleos de CPU disponibles para la app | 1 | 4 |
| RAM libre necesaria (con margen) | ~525 MB | ~450 MB |
| Latencia por foto | ~400 ms (usable, notorio) | ~150 ms (instantÃ¡neo) |
| Chip de referencia | Cortex-A53 / Helio G bajo | Snapdragon 8-series / Dimensity 7000+ |
| Ejemplo de dispositivo real | â€” | Redmi Note 13 Pro+ |

---

## 8. Archivos de producciÃ³n (generados, validados)

| Archivo | TamaÃ±o | Contenido | ValidaciÃ³n |
| --- | --- | --- | --- |
| `anura_clasificador_fp16.onnx` | 165,6 MB | Encoder + 3 cabezas, fp16 | 100 % predicciones idÃ©nticas a PyTorch (64 img.) |
| `vocabulario.json` | â€” | Ãndice â†’ nombre especie/gÃ©nero/familia | â€” |
| `prior_geografico_movil.json` | 34 KB | 1.678 puntos, 41/41 especies | â€” |

**Preprocesamiento que la app debe replicar exactamente** (si no coincide, las predicciones no sirven): resize a 224Ã—224 RGB, normalizar con mean/std de OpenAI CLIP `(0,4815, 0,4578, 0,4082)` / `(0,2686, 0,2613, 0,2758)`.

---

## 9. Pendientes reales (no resueltos por esta sesiÃ³n)

1. **Medir en el Redmi Note 13 Pro+ fÃ­sico**, no solo en emulaciÃ³n de hilos de CPU en PC â€” la emulaciÃ³n por `intra_op_num_threads` es una aproximaciÃ³n razonable, pero el chip real (ARM, no x86) puede rendir distinto.
2. Implementar el runtime `ONNX Runtime Mobile` en el proyecto Android (`onnxruntime-android`).
3. Implementar el preprocesamiento de imagen (resize + normalize) en Kotlin nativo.
4. Implementar la lÃ³gica del prior geogrÃ¡fico (haversine + conteo + suavizado) en Kotlin, usando `prior_geografico_movil.json`.
5. Medir baterÃ­a real en sesiÃ³n de campo (RNF-09: â‰¤5 %/hora) â€” no medido en esta sesiÃ³n.
6. *Quantization-aware training* como vÃ­a futura si el tamaÃ±o de 165,6 MB vuelve a ser un problema crÃ­tico â€” no intentado, requiere reentrenar.

## Referencias

- ONNX Runtime Mobile. [onnxruntime.ai](https://onnxruntime.ai/)
- ONNX Runtime Quantization. [onnxruntime.ai/docs/performance/quantization](https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html)
- PyTorch ONNX export (exportador dynamo). [pytorch.org/docs/stable/onnx.html](https://pytorch.org/docs/stable/onnx.html)



