---
title: "Fases de Implementación â€” BioCLIP v1 a On-Device (C-11)"
proyecto: Anura
tipo: plan-técnico
estado: activo
tags: [anura, fases, cronograma, transfer-learning, onnx, android]
---

# Fases de Implementación: BioCLIP v1 Transfer Learning â†’ Android

[[Anura â€” àndice General]] · [[Inconsistencias y Decisiones Pendientes]] (C-11) · [[Experimentos Fallidos y Decisiones Descartadas]] (F-1)

> [!warning] Contexto de C-11
> Reemplaza completamente las decisiones C-5, C-8, C-10 (destilación). Ver [[Experimentos Fallidos y Decisiones Descartadas]] para por qué falló destilación (degradación Top-1 33pp).

---

## Cronograma General

**Deadline:** 27 sep 2026  
**Hoy:** 11 sep 2026  
**Días restantes:** 16  
**Blocker:** H4 (segmentación) determina si variante C (segmentada) o A (completa)

```
Semana 1 (11-15 sep)   â†’ Fases 0-3  (validación + baseline)
Semana 2 (16-22 sep)   â†’ Fases 4-8  (Transfer Learning + ONNX)
Semana 3 (23-27 sep)   â†’ Fases 9-12 (Android + pruebas)
```

---

## ðŸŸ¢ Fase 0 â€” Preparar Entorno âœ… COMPLETADA (2026-09-11)

**Estado:** âœ… Completada â€” se reutiliza `.venv-train` en vez de crear un venv nuevo  
**Responsable:** Claude Code  
**Deliverable:** `.venv-train` con todas las dependencias de BioCLIP + ONNX

### Decisión

No se crea `.venv-bioclip` separado. El entorno `D:\Anura\.venv-train` (Python 3.13, PyTorch 2.11+cu128, CUDA RTX 4050) ya tenía `torch`, `open_clip_torch` 3.3.0 y `Pillow` instalados desde el trabajo de destilación (ahora descartado, ver C-10). Se instalaron encima los paquetes que faltaban: `scikit-learn`, `onnx`, `onnxruntime-gpu`, `onnxsim`, `tqdm`. Un solo entorno para todo el pipeline de visión â€” sin duplicar ~6 GB de PyTorch+CUDA en un segundo venv.

### Verificación realizada

```
torch: OK (2.11.0+cu128)
open_clip: OK (3.3.0)
sklearn: OK (1.9.1) â€” instalado
onnx: OK (1.22.0) â€” instalado
onnxruntime: OK (1.30.0, GPU) â€” instalado
PIL: OK (12.3.0)
numpy: OK (2.5.2)
CUDA disponible: True
GPU: NVIDIA GeForce RTX 4050 Laptop GPU
```

### Limpieza de código obsoleto

Con C-10 (destilación inviable) y C-11 (nueva arquitectura), se eliminaron de `training/` los archivos específicos del pipeline de destilación descartado:

| Eliminado | Por qué |
|---|---|
| `train_student.py` | Multi-Head Loss BioCLIPâ†’MobileNetV3, destilación inviable (C-10) |
| `cascada.py`, `test_cascada.py` | Cascada jerárquica diseñada para el student pequeño; ya no hay student separado |
| `test_modelo.py` | Tests de arquitectura student/teacher descartada |
| `comparar_arquitecturas.py` | Comparaba MobileNetV3 vs EdgeNeXt, ambos descartados |
| `analizar_cobertura.py`, `politica_resolucion.json` | Generaban la política de resolución que consumía cascada.py |
| `checkpoints_diagnostico/` | Pesos del student fracasado (student_v1.pt, teacher_heads.pt) |
| `log_diagnostico.txt` | Ya documentado en `resultados_diagnostico_destilacion.md`, no hace falta el log crudo |
| `requirements-training.txt` | Reemplazado por el venv unificado |

**Se conservó** (reutilizable para C-11): `prepare_dataset.py`, `taxonomia.py`, `manifiesto.json`, `lista_negra.json`, `validar_integridad.py`, `resultados_diagnostico_destilacion.md` (valor histórico del fracaso).

---

## ðŸŸ¢ Fase 1 â€” Probar BioCLIP v1 Original âœ… COMPLETADA (2026-09-11)

**Estado:** âœ… Completada  
**Resultado real:** Image Encoder = 86.192.640 params (coincide con lo documentado en C-5/C-11), Text Encoder = 63.428.097 params (no viaja al móvil, se descarta), embedding shape (1,512) con norma L2 = 1.0. Sin errores CUDA.

**Estado (referencia original):** â³ Script listo  
**Responsable:** Tàº  
**Duración estimada:** 10 min  
**Deliverable:** Confirmación que BioCLIP carga, procesa imagen, genera embedding

### Objetivo

Comprobar que BioCLIP v1 (sin modificar) funciona correctamente antes de cualquier entrenamiento.

### Ejecución

```bash
cd D:\Anura
.venv-train\Scripts\activate  # Windows â€” venv unificado, no hay .venv-bioclip
python bioclip/scripts/fase_1_probar_bioclip.py

# Opcional: con una imagen de prueba
python bioclip/scripts/fase_1_probar_bioclip.py --imagen "D:\Anura\data dirty\Especie1\fotos\imagen.jpg"
```

### Qué esperar

```
======================================================
FASE 1: Probar BioCLIP v1 original
======================================================
CUDA disponible: True
GPU: NVIDIA RTX 4050
VRAM disponible: 6.0 GB

Cargando BioCLIP v1...
  OK (86,107,904 parámetros)

[encoder visual]
  Tipo: VisionTransformer

[imagen sintética] tensor aleatorio 224à—224

Resultados:
  Forma embedding: torch.Size([1, 512])
  Norma L2: 1.000000
  Primeros 5 valores: [0.124, -0.381, 0.552, ...]

âœ… FASE 1 OK â€” BioCLIP v1 carga y genera embeddings correctamente
```

### Validación

- [ ] Carga sin errores CUDA
- [ ] Embedding shape = (1, 512)
- [ ] Norma L2 = 1.0 (verificación de normalización)

---

## ðŸŸ¢ Fase 2 â€” Obtener Embeddings âœ… COMPLETADA (2026-09-11)

**Estado:** âœ… Completada  
**Resultado real:** 419 imágenes procesadas (15 max/especie, 28 especies), 0 errores. `embeddings_muestra.npy` shape (419, 512).

**Estado (referencia original):** â³ Script listo  
**Responsable:** Tàº  
**Duración estimada:** 5-15 min (depende de --imagenes-por-especie)  
**Deliverable:** `embeddings_muestra.npy` + `embeddings_muestra_meta.json`

### Objetivo

Generar embeddings de una muestra del dataset (validación de pipeline) antes de entrenar.

### Ejecución

```bash
# Opción A: muestra pequeña (10 imágenes por especie)
python bioclip/scripts/fase_2_obtener_embeddings.py

# Opción B: muestra mediana (50 imágenes por especie)
python bioclip/scripts/fase_2_obtener_embeddings.py --imagenes-por-especie 50

# Opción C: todo el dataset
python bioclip/scripts/fase_2_obtener_embeddings.py --todas
```

### Qué esperar

```
Dispositivo: cuda
Cargando BioCLIP v1...
  OK (86,107,904 parámetros)

Descubriendo imágenes (10 max/especie)...
  280 imágenes de 28 especies

Generando embeddings...
  50/280 procesadas, 0 errores
  100/280 procesadas, 0 errores
  150/280 procesadas, 0 errores
  200/280 procesadas, 0 errores
  250/280 procesadas, 0 errores

Resultados:
  Embeddings guardados: 280
  Forma array: (280, 512)
  Errores: 0
  Archivos: D:\Anura\bioclip\datasets\embeddings_muestra.npy, ...meta.json

âœ… FASE 2 OK â€” embeddings listos para baseline
```

### Validación

- [ ] 0 errores de procesamiento
- [ ] Archivo `embeddings_muestra.npy` existe
- [ ] Archivo `embeddings_muestra_meta.json` existe con entries

---

## ðŸŸ¢ Fase 3 â€” Baseline (Sin Transfer Learning) âœ… COMPLETADA (2026-09-11)

**Estado:** âœ… Completada  
**Resultado real (k-NN cosine, k=5, 5-fold CV sobre 419 embeddings):**

| Métrica | Valor |
|---|---|
| **Top-1** | **70,4% ± 4,4%** |
| **Top-3** | **90,9% ± 2,3%** |
| **F1-macro** | 68,3% ± 4,2% |

> [!success] Contraste con destilación fracasada
> BioCLIP v1 **zero-shot** (sin ningàºn entrenamiento, solo k-NN sobre sus embeddings crudos) ya alcanza 70,4% Top-1. Esto es **13 puntos más alto** que el 57,7% que el teacher (con linear probe de 300 épocas) alcanzó en la corrida diagnóstica de destilación â€” probablemente porque esa corrida medía sobre variante A completa con train/val más ruidoso, mientras este baseline usa una muestra balanceada de 15 img/especie. En cualquier caso, confirma que BioCLIP es muy fuerte "out of the box" para el dominio y que el camino de Transfer Learning (C-11) tiene una base sólida sobre la cual mejorar.

**Especies débiles identificadas (prioridad para Transfer Learning):**

| Especie | F1 | Nota |
|---|---|---|
| `Scinax_ruber` | 28,6% | La más débil â€” revisar calidad/cantidad de imágenes |
| `Rheobates_palmatus` | 42,1% | |
| `Pristimantis_achatinus` | 46,2% | Par confundible con P. paisa |
| `Pristimantis_paisa` | 46,7% | Par confundible con P. achatinus â€” **el ejemplo de especies visualmente similares que se anticipó en la discusión de arquitectura** |

Informe completo: `D:\Anura\bioclip\evaluation\baseline_bioclip_v1.json`

**Estado (referencia original):** â³ Script listo  
**Responsable:** Tàº  
**Duración estimada:** 5-10 min  
**Deliverable:** `baseline_bioclip_v1.json` (referencia)

### Objetivo

Evaluar BioCLIP puro (sin modificar) usando k-NN como clasificador. Esta es la **línea de referencia**: cualquier mejora con Transfer Learning debe superar esta cifra.

### Ejecución

```bash
python bioclip/scripts/fase_3_baseline.py
```

### Qué esperar

```
Fase 3: Baseline BioCLIP v1 (sin Transfer Learning)
Dataset: 280 embeddings, 28 especies

Validación cruzada (5 folds)...
  Fold 1: Top-1 45.7%  Top-3 68.3%  F1 44.2%
  Fold 2: Top-1 46.2%  Top-3 69.1%  F1 45.1%
  ...

============================================================
BASELINE BioCLIP v1 (k-NN, 5-fold CV)
============================================================
  Top-1 Accuracy:  46.1% ± 1.2%
  Top-3 Accuracy:  68.9% ± 1.5%
  F1-macro:        44.8% ± 1.1%

F1 por especie:
  Boana_cinerascens                   56.5% â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ
  Dendrobates_auratus                 52.3% â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ
  ...

âœ… FASE 3 OK â€” Informe guardado
Este es el baseline: cualquier mejora con Transfer Learning debe superar 46.1% Top-1
```

### Validación

- [ ] Archivo `baseline_bioclip_v1.json` existe
- [ ] Top-1 baseline entre 40-60% (rango esperado para BioCLIP puro)

---

## ðŸŸ¡ Fase 4 â€” Transfer Learning âœ… EJECUTADA en variante A (2026-09-11) â€” resultado inconcluso

**Estado:** âœ… Corrida completa en variante A (fallback, H4 no llegó). **No confirma mejora sobre baseline zero-shot.**

**Resultado real (test, mejor checkpoint = época 10 de Fase B):**

| Métrica | Zero-shot (Fase 3) | Transfer Learning (variante A) |
|---|---|---|
| Top-1 especie | 70,4% | **69,2%** (prácticamente empatado, ligera regresión) |
| Top-3 especie | 90,9% | 89,8% |
| Top-1 género | â€” | 85,6% |
| Top-1 familia | â€” | 88,9% |

> [!warning] Lectura honesta: variante A tiene techo
> La pérdida de entrenamiento cayó de 0,92 a 0,01 en 15 épocas (overfitting evidente) mientras el top-1 de validación se estancó en 70-72% desde la época 5-6 y retrocedió después del pico (72,7% época 10 â†’ 70,8% época 15). El modelo memoriza train sin ganar generalización nueva. **Esta es la segunda señal independiente** (después de F-1, destilación) de que en variante A (imagen completa) hay un techo real cerca del 70% que ni el fine-tuning logra romper â€” la rana ocupa ~10% del encuadre y ya se extrajo casi toda la señal disponible ahí. Refuerza directamente C-9: la segmentación no es una mejora incremental, decide si hay techo o no.

**Configuración usada:** BioCLIP v1 + 3 cabezas (Familia/Género/Especie), Fase A 8 épocas solo cabezas (backbone congelado), Fase B hasta 20 épocas con àºltimas 4 resblocks del ViT descongeladas + cabezas, GradScaler FP16, batch 16, parada temprana con paciencia 5 (activada en época 15). VRAM pico 1,1 GB de 6,4 GB disponibles â€” sin problema de memoria, mucho margen si se quisiera batch más grande.

**Checkpoint guardado:** `D:\Anura\bioclip\checkpoints\bioclip_anura_mejor.pt` (best top1_especie=72,7% en val, é poca 10)

**Decisión:** No se avanza a Fase 6-8 (extracción/ONNX) con este checkpoint todavía â€” no hay mejora clara que justifique reemplazar el baseline zero-shot como "el encoder a exportar". **Se espera H4** para repetir Fase 4 en variante C (segmentada) antes de decidir qué encoder final exportar.

---

**Estado (plan original, referencia):** â³ Pendiente H4 (segmentación)  
**Responsable:** Tàº  
**Duración estimada:** 2-4 horas (RTX 4050)  
**Deliverable:** `bioclip_anura_ft.pt` (checkpoint entrenado)

### Objetivo

Fine-tuning de BioCLIP v1 sobre el dataset completo de 28 especies.

### Blocker

**H4 (segmentación de CVAT)** determina qué variante usar:
- Si H4 llega antes del 16 sep â†’ Variante C (imagen segmentada, mejor señal)
- Si H4 no llega â†’ Variante A (imagen completa, menor Top-1 pero medible)

### Prerequisitos

```bash
# Asegurar que manifiesto.json existe y es válido
D:\Anura\training\manifiesto.json  # 3.258 imágenes, 28 especies, GroupSplit por obs_id
```

### Ejecución (cuando H4 llegue)

```bash
# Variante C (con segmentación)
python bioclip/scripts/fase_4_transfer_learning.py \
  --masks-dir "D:\Anura\segmentacion\masks" \
  --variante C \
  --epocas 30

# Variante A (sin segmentación, fallback)
python bioclip/scripts/fase_4_transfer_learning.py \
  --permitir-sin-mascaras \
  --variante A \
  --epocas 30
```

### Configuración esperada

```python
# Capas descongeladas
encoder.resblocks[-3:] â†’ trainable  # àšltimas 3 capas ResBlock del ViT
proyection â†’ trainable              # Capa de proyección a 512-d
cabezas (familia, genero, especie) â†’ trainable  # 3 cabezas de clasificación
```

### Criterio de parada

- Epoch 30 si no converge
- Early stopping si val_loss no mejora en 3 épocas

---

## ðŸŸ¡ Fase 5 â€” Evaluación

**Estado:** â³ Pendiente Fase 4  
**Responsable:** Tàº  
**Duración estimada:** 10-15 min  
**Deliverable:** `evaluation_anura_ft.json` (métricas completas)

### Objetivo

Medir exactitud del modelo entrenado y comparar contra baseline.

### Métrica de éxito

- Top-1 â‰¥ baseline + 20pp (si es realista con dados disponibles)
- Top-3 â‰¥ 75%
- F1-macro â‰¥ 0.60

---

## ðŸ”µ Fase 6-8 â€” Exportación a ONNX + FP16

**Estado:** â³ Pendiente Fase 4  
**Responsable:** Tàº (o Claude si scripts están listos)  
**Duración estimada:** 30-60 min  
**Deliverable:** `bioclip_anura_encoder_fp16.onnx` (~173 MB)

### Hitos

**Fase 6:** Extraer `model.visual` del checkpoint PyTorch  
**Fase 7:** Exportar a ONNX, verificar que PyTorch â‰ˆ ONNX (cosine similarity >0.99)  
**Fase 8:** Convertir a FP16, medir tamaño final

### Validación crítica

```python
# Misma imagen, misma salida
imagen = ...
emb_pytorch = modelo_pytorch(imagen)       # [1, 512]
emb_onnx = modelo_onnx(imagen)             # [1, 512]
similitud = cosine_similarity(emb_pytorch, emb_onnx)
assert similitud > 0.99, f"Degradación en exportación: {similitud}"
```

---

## ðŸ”µ Fase 9-10 â€” Android + SQLite-vec

**Estado:** â³ Pendiente Fases 6-8  
**Responsable:** Tàº (desarrollador Android)  
**Duración estimada:** 2-3 días  
**Deliverable:** APK prototipo + paquete regional Antioquia

### Flujo

```
APK (inmovilizado)
â”œâ”€â”€ ONNX Runtime
â”œâ”€â”€ bioclip_anura_encoder_fp16.onnx (~173 MB)
â””â”€â”€ SQLite-vec

Paquetes regionales (descargables)
â”œâ”€â”€ antioquia.sitrana (2-5 MB)
â”‚   â”œâ”€â”€ embeddings (5 especies à— 10 imágenes à— 512-d)
â”‚   â”œâ”€â”€ metadata (JSON: taxonomía, coordenadas, referencias)
â”‚   â””â”€â”€ fotos (JPEG pequeño para UI)
â”œâ”€â”€ cauca.sitrana
â””â”€â”€ ...
```

---

## ðŸŸ¢ Fase 11 â€” Pruebas en Redmi Note 13 Pro+

**Estado:** â³ Pendiente Fases 9-10  
**Responsable:** Tàº  
**Duración estimada:** 1-2 días (mediciones + iteración)  
**Deliverable:** Reporte de latencia, RAM, Top-1, offline status

### Métricas a medir

| Métrica | Objetivo |
|---|---|
| Tamaño APK | <200 MB |
| Encoder load time | <2 seg |
| Embedding time (per imagen) | <500 ms |
| RAM pico | <2 GB |
| Top-1 on-device â‰ˆ Top-1 desktop | ±2pp |
| Offline support | âœ… |
| SQLite-vec latencia | <100 ms para Top-5 |

---

## ðŸŸ¢ Fase 12 â€” Iteración / Pulido

**Estado:** â³ Pendiente Fases 11  
**Responsable:** Tàº  
**Duración estimada:** 1-3 días  
**Deliverable:** Versión final lista para 27 sep

---

## Go/No-Go Decisiones

| Checkpoint | Criterio | Consecuencia si No |
|---|---|---|
| **Fase 0-1** (Hoy) | BioCLIP carga sin errores | Debugging entorno CUDA/PyTorch |
| **Fase 2-3** (Mañana) | Baseline >40% Top-1 | BioCLIP puede no ser compatible con dataset |
| **Fase 4** (16-17 sep) | H4 llega O declino variante A | Transfer Learning bloqueado indefinidamente |
| **Fase 5** (18 sep) | Top-1 â‰¥ baseline + 20pp | Considerar arquitectura alternativa o mejor dataset |
| **Fase 6-8** (21 sep) | PyTorch â‰ˆ ONNX >0.99 cosine | Problemas de conversión, requiere debug |
| **Fase 9-10** (23 sep) | APK corre sin crashes | Debugging ONNX Runtime en Android |
| **Fase 11** (25 sep) | Latencia <1 seg, RAM OK | Optimización FP16 más agresiva o backend alternativo |

---

**àšltima actualización:** 2026-09-11  
**Responsable:** C-11 decision, usuario ejecuta Fases 0-3 ahora  
**Referencias:** [[Inconsistencias y Decisiones Pendientes]] (C-11), [[Experimentos Fallidos y Decisiones Descartadas]] (F-1)



