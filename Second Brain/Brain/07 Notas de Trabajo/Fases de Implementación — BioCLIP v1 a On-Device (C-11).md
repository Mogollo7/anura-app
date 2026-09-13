---
title: "Fases de ImplementaciÃ³n â€” BioCLIP v1 a On-Device (C-11)"
proyecto: Anura
tipo: plan-tÃ©cnico
estado: activo
tags: [anura, fases, cronograma, transfer-learning, onnx, android]
---

# Fases de ImplementaciÃ³n: BioCLIP v1 Transfer Learning â†’ Android

[[Anura â€” Ãndice General]] Â· [[Inconsistencias y Decisiones Pendientes]] (C-11) Â· [[Experimentos Fallidos y Decisiones Descartadas]] (F-1)

> [!warning] Contexto de C-11
> Reemplaza completamente las decisiones C-5, C-8, C-10 (destilaciÃ³n). Ver [[Experimentos Fallidos y Decisiones Descartadas]] para por quÃ© fallÃ³ destilaciÃ³n (degradaciÃ³n Top-1 33pp).

---

## Cronograma General

**Deadline:** 27 sep 2026  
**Hoy:** 11 sep 2026  
**DÃ­as restantes:** 16  
**Blocker:** H4 (segmentaciÃ³n) determina si variante C (segmentada) o A (completa)

```
Semana 1 (11-15 sep)   â†’ Fases 0-3  (validaciÃ³n + baseline)
Semana 2 (16-22 sep)   â†’ Fases 4-8  (Transfer Learning + ONNX)
Semana 3 (23-27 sep)   â†’ Fases 9-12 (Android + pruebas)
```

---

## ðŸŸ¢ Fase 0 â€” Preparar Entorno âœ… COMPLETADA (2026-09-11)

**Estado:** âœ… Completada â€” se reutiliza `.venv-train` en vez de crear un venv nuevo  
**Responsable:** Claude Code  
**Deliverable:** `.venv-train` con todas las dependencias de BioCLIP + ONNX

### DecisiÃ³n

No se crea `.venv-bioclip` separado. El entorno `D:\Anura\.venv-train` (Python 3.13, PyTorch 2.11+cu128, CUDA RTX 4050) ya tenÃ­a `torch`, `open_clip_torch` 3.3.0 y `Pillow` instalados desde el trabajo de destilaciÃ³n (ahora descartado, ver C-10). Se instalaron encima los paquetes que faltaban: `scikit-learn`, `onnx`, `onnxruntime-gpu`, `onnxsim`, `tqdm`. Un solo entorno para todo el pipeline de visiÃ³n â€” sin duplicar ~6 GB de PyTorch+CUDA en un segundo venv.

### VerificaciÃ³n realizada

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

### Limpieza de cÃ³digo obsoleto

Con C-10 (destilaciÃ³n inviable) y C-11 (nueva arquitectura), se eliminaron de `training/` los archivos especÃ­ficos del pipeline de destilaciÃ³n descartado:

| Eliminado | Por quÃ© |
|---|---|
| `train_student.py` | Multi-Head Loss BioCLIPâ†’MobileNetV3, destilaciÃ³n inviable (C-10) |
| `cascada.py`, `test_cascada.py` | Cascada jerÃ¡rquica diseÃ±ada para el student pequeÃ±o; ya no hay student separado |
| `test_modelo.py` | Tests de arquitectura student/teacher descartada |
| `comparar_arquitecturas.py` | Comparaba MobileNetV3 vs EdgeNeXt, ambos descartados |
| `analizar_cobertura.py`, `politica_resolucion.json` | Generaban la polÃ­tica de resoluciÃ³n que consumÃ­a cascada.py |
| `checkpoints_diagnostico/` | Pesos del student fracasado (student_v1.pt, teacher_heads.pt) |
| `log_diagnostico.txt` | Ya documentado en `resultados_diagnostico_destilacion.md`, no hace falta el log crudo |
| `requirements-training.txt` | Reemplazado por el venv unificado |

**Se conservÃ³** (reutilizable para C-11): `prepare_dataset.py`, `taxonomia.py`, `manifiesto.json`, `lista_negra.json`, `validar_integridad.py`, `resultados_diagnostico_destilacion.md` (valor histÃ³rico del fracaso).

---

## ðŸŸ¢ Fase 1 â€” Probar BioCLIP v1 Original âœ… COMPLETADA (2026-09-11)

**Estado:** âœ… Completada  
**Resultado real:** Image Encoder = 86.192.640 params (coincide con lo documentado en C-5/C-11), Text Encoder = 63.428.097 params (no viaja al mÃ³vil, se descarta), embedding shape (1,512) con norma L2 = 1.0. Sin errores CUDA.

**Estado (referencia original):** â³ Script listo  
**Responsable:** TÃº  
**DuraciÃ³n estimada:** 10 min  
**Deliverable:** ConfirmaciÃ³n que BioCLIP carga, procesa imagen, genera embedding

### Objetivo

Comprobar que BioCLIP v1 (sin modificar) funciona correctamente antes de cualquier entrenamiento.

### EjecuciÃ³n

```bash
cd D:\Anura
.venv-train\Scripts\activate  # Windows â€” venv unificado, no hay .venv-bioclip
python bioclip/scripts/fase_1_probar_bioclip.py

# Opcional: con una imagen de prueba
python bioclip/scripts/fase_1_probar_bioclip.py --imagen "D:\Anura\data dirty\Especie1\fotos\imagen.jpg"
```

### QuÃ© esperar

```
======================================================
FASE 1: Probar BioCLIP v1 original
======================================================
CUDA disponible: True
GPU: NVIDIA RTX 4050
VRAM disponible: 6.0 GB

Cargando BioCLIP v1...
  OK (86,107,904 parÃ¡metros)

[encoder visual]
  Tipo: VisionTransformer

[imagen sintÃ©tica] tensor aleatorio 224Ã—224

Resultados:
  Forma embedding: torch.Size([1, 512])
  Norma L2: 1.000000
  Primeros 5 valores: [0.124, -0.381, 0.552, ...]

âœ… FASE 1 OK â€” BioCLIP v1 carga y genera embeddings correctamente
```

### ValidaciÃ³n

- [ ] Carga sin errores CUDA
- [ ] Embedding shape = (1, 512)
- [ ] Norma L2 = 1.0 (verificaciÃ³n de normalizaciÃ³n)

---

## ðŸŸ¢ Fase 2 â€” Obtener Embeddings âœ… COMPLETADA (2026-09-11)

**Estado:** âœ… Completada  
**Resultado real:** 419 imÃ¡genes procesadas (15 max/especie, 28 especies), 0 errores. `embeddings_muestra.npy` shape (419, 512).

**Estado (referencia original):** â³ Script listo  
**Responsable:** TÃº  
**DuraciÃ³n estimada:** 5-15 min (depende de --imagenes-por-especie)  
**Deliverable:** `embeddings_muestra.npy` + `embeddings_muestra_meta.json`

### Objetivo

Generar embeddings de una muestra del dataset (validaciÃ³n de pipeline) antes de entrenar.

### EjecuciÃ³n

```bash
# OpciÃ³n A: muestra pequeÃ±a (10 imÃ¡genes por especie)
python bioclip/scripts/fase_2_obtener_embeddings.py

# OpciÃ³n B: muestra mediana (50 imÃ¡genes por especie)
python bioclip/scripts/fase_2_obtener_embeddings.py --imagenes-por-especie 50

# OpciÃ³n C: todo el dataset
python bioclip/scripts/fase_2_obtener_embeddings.py --todas
```

### QuÃ© esperar

```
Dispositivo: cuda
Cargando BioCLIP v1...
  OK (86,107,904 parÃ¡metros)

Descubriendo imÃ¡genes (10 max/especie)...
  280 imÃ¡genes de 28 especies

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

### ValidaciÃ³n

- [ ] 0 errores de procesamiento
- [ ] Archivo `embeddings_muestra.npy` existe
- [ ] Archivo `embeddings_muestra_meta.json` existe con entries

---

## ðŸŸ¢ Fase 3 â€” Baseline (Sin Transfer Learning) âœ… COMPLETADA (2026-09-11)

**Estado:** âœ… Completada  
**Resultado real (k-NN cosine, k=5, 5-fold CV sobre 419 embeddings):**

| MÃ©trica | Valor |
|---|---|
| **Top-1** | **70,4% Â± 4,4%** |
| **Top-3** | **90,9% Â± 2,3%** |
| **F1-macro** | 68,3% Â± 4,2% |

> [!success] Contraste con destilaciÃ³n fracasada
> BioCLIP v1 **zero-shot** (sin ningÃºn entrenamiento, solo k-NN sobre sus embeddings crudos) ya alcanza 70,4% Top-1. Esto es **13 puntos mÃ¡s alto** que el 57,7% que el teacher (con linear probe de 300 Ã©pocas) alcanzÃ³ en la corrida diagnÃ³stica de destilaciÃ³n â€” probablemente porque esa corrida medÃ­a sobre variante A completa con train/val mÃ¡s ruidoso, mientras este baseline usa una muestra balanceada de 15 img/especie. En cualquier caso, confirma que BioCLIP es muy fuerte "out of the box" para el dominio y que el camino de Transfer Learning (C-11) tiene una base sÃ³lida sobre la cual mejorar.

**Especies dÃ©biles identificadas (prioridad para Transfer Learning):**

| Especie | F1 | Nota |
|---|---|---|
| `Scinax_ruber` | 28,6% | La mÃ¡s dÃ©bil â€” revisar calidad/cantidad de imÃ¡genes |
| `Rheobates_palmatus` | 42,1% | |
| `Pristimantis_achatinus` | 46,2% | Par confundible con P. paisa |
| `Pristimantis_paisa` | 46,7% | Par confundible con P. achatinus â€” **el ejemplo de especies visualmente similares que se anticipÃ³ en la discusiÃ³n de arquitectura** |

Informe completo: `D:\Anura\bioclip\evaluation\baseline_bioclip_v1.json`

**Estado (referencia original):** â³ Script listo  
**Responsable:** TÃº  
**DuraciÃ³n estimada:** 5-10 min  
**Deliverable:** `baseline_bioclip_v1.json` (referencia)

### Objetivo

Evaluar BioCLIP puro (sin modificar) usando k-NN como clasificador. Esta es la **lÃ­nea de referencia**: cualquier mejora con Transfer Learning debe superar esta cifra.

### EjecuciÃ³n

```bash
python bioclip/scripts/fase_3_baseline.py
```

### QuÃ© esperar

```
Fase 3: Baseline BioCLIP v1 (sin Transfer Learning)
Dataset: 280 embeddings, 28 especies

ValidaciÃ³n cruzada (5 folds)...
  Fold 1: Top-1 45.7%  Top-3 68.3%  F1 44.2%
  Fold 2: Top-1 46.2%  Top-3 69.1%  F1 45.1%
  ...

============================================================
BASELINE BioCLIP v1 (k-NN, 5-fold CV)
============================================================
  Top-1 Accuracy:  46.1% Â± 1.2%
  Top-3 Accuracy:  68.9% Â± 1.5%
  F1-macro:        44.8% Â± 1.1%

F1 por especie:
  Boana_cinerascens                   56.5% â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ
  Dendrobates_auratus                 52.3% â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ
  ...

âœ… FASE 3 OK â€” Informe guardado
Este es el baseline: cualquier mejora con Transfer Learning debe superar 46.1% Top-1
```

### ValidaciÃ³n

- [ ] Archivo `baseline_bioclip_v1.json` existe
- [ ] Top-1 baseline entre 40-60% (rango esperado para BioCLIP puro)

---

## ðŸŸ¡ Fase 4 â€” Transfer Learning âœ… EJECUTADA en variante A (2026-09-11) â€” resultado inconcluso

**Estado:** âœ… Corrida completa en variante A (fallback, H4 no llegÃ³). **No confirma mejora sobre baseline zero-shot.**

**Resultado real (test, mejor checkpoint = Ã©poca 10 de Fase B):**

| MÃ©trica | Zero-shot (Fase 3) | Transfer Learning (variante A) |
|---|---|---|
| Top-1 especie | 70,4% | **69,2%** (prÃ¡cticamente empatado, ligera regresiÃ³n) |
| Top-3 especie | 90,9% | 89,8% |
| Top-1 gÃ©nero | â€” | 85,6% |
| Top-1 familia | â€” | 88,9% |

> [!warning] Lectura honesta: variante A tiene techo
> La pÃ©rdida de entrenamiento cayÃ³ de 0,92 a 0,01 en 15 Ã©pocas (overfitting evidente) mientras el top-1 de validaciÃ³n se estancÃ³ en 70-72% desde la Ã©poca 5-6 y retrocediÃ³ despuÃ©s del pico (72,7% Ã©poca 10 â†’ 70,8% Ã©poca 15). El modelo memoriza train sin ganar generalizaciÃ³n nueva. **Esta es la segunda seÃ±al independiente** (despuÃ©s de F-1, destilaciÃ³n) de que en variante A (imagen completa) hay un techo real cerca del 70% que ni el fine-tuning logra romper â€” la rana ocupa ~10% del encuadre y ya se extrajo casi toda la seÃ±al disponible ahÃ­. Refuerza directamente C-9: la segmentaciÃ³n no es una mejora incremental, decide si hay techo o no.

**ConfiguraciÃ³n usada:** BioCLIP v1 + 3 cabezas (Familia/GÃ©nero/Especie), Fase A 8 Ã©pocas solo cabezas (backbone congelado), Fase B hasta 20 Ã©pocas con Ãºltimas 4 resblocks del ViT descongeladas + cabezas, GradScaler FP16, batch 16, parada temprana con paciencia 5 (activada en Ã©poca 15). VRAM pico 1,1 GB de 6,4 GB disponibles â€” sin problema de memoria, mucho margen si se quisiera batch mÃ¡s grande.

**Checkpoint guardado:** `D:\Anura\bioclip\checkpoints\bioclip_anura_mejor.pt` (best top1_especie=72,7% en val, Ã© poca 10)

**DecisiÃ³n:** No se avanza a Fase 6-8 (extracciÃ³n/ONNX) con este checkpoint todavÃ­a â€” no hay mejora clara que justifique reemplazar el baseline zero-shot como "el encoder a exportar". **Se espera H4** para repetir Fase 4 en variante C (segmentada) antes de decidir quÃ© encoder final exportar.

---

**Estado (plan original, referencia):** â³ Pendiente H4 (segmentaciÃ³n)  
**Responsable:** TÃº  
**DuraciÃ³n estimada:** 2-4 horas (RTX 4050)  
**Deliverable:** `bioclip_anura_ft.pt` (checkpoint entrenado)

### Objetivo

Fine-tuning de BioCLIP v1 sobre el dataset completo de 28 especies.

### Blocker

**H4 (segmentaciÃ³n de CVAT)** determina quÃ© variante usar:
- Si H4 llega antes del 16 sep â†’ Variante C (imagen segmentada, mejor seÃ±al)
- Si H4 no llega â†’ Variante A (imagen completa, menor Top-1 pero medible)

### Prerequisitos

```bash
# Asegurar que manifiesto.json existe y es vÃ¡lido
D:\Anura\training\manifiesto.json  # 3.258 imÃ¡genes, 28 especies, GroupSplit por obs_id
```

### EjecuciÃ³n (cuando H4 llegue)

```bash
# Variante C (con segmentaciÃ³n)
python bioclip/scripts/fase_4_transfer_learning.py \
  --masks-dir "D:\Anura\segmentacion\masks" \
  --variante C \
  --epocas 30

# Variante A (sin segmentaciÃ³n, fallback)
python bioclip/scripts/fase_4_transfer_learning.py \
  --permitir-sin-mascaras \
  --variante A \
  --epocas 30
```

### ConfiguraciÃ³n esperada

```python
# Capas descongeladas
encoder.resblocks[-3:] â†’ trainable  # Ãšltimas 3 capas ResBlock del ViT
proyection â†’ trainable              # Capa de proyecciÃ³n a 512-d
cabezas (familia, genero, especie) â†’ trainable  # 3 cabezas de clasificaciÃ³n
```

### Criterio de parada

- Epoch 30 si no converge
- Early stopping si val_loss no mejora en 3 Ã©pocas

---

## ðŸŸ¡ Fase 5 â€” EvaluaciÃ³n

**Estado:** â³ Pendiente Fase 4  
**Responsable:** TÃº  
**DuraciÃ³n estimada:** 10-15 min  
**Deliverable:** `evaluation_anura_ft.json` (mÃ©tricas completas)

### Objetivo

Medir exactitud del modelo entrenado y comparar contra baseline.

### MÃ©trica de Ã©xito

- Top-1 â‰¥ baseline + 20pp (si es realista con dados disponibles)
- Top-3 â‰¥ 75%
- F1-macro â‰¥ 0.60

---

## ðŸ”µ Fase 6-8 â€” ExportaciÃ³n a ONNX + FP16

**Estado:** â³ Pendiente Fase 4  
**Responsable:** TÃº (o Claude si scripts estÃ¡n listos)  
**DuraciÃ³n estimada:** 30-60 min  
**Deliverable:** `bioclip_anura_encoder_fp16.onnx` (~173 MB)

### Hitos

**Fase 6:** Extraer `model.visual` del checkpoint PyTorch  
**Fase 7:** Exportar a ONNX, verificar que PyTorch â‰ˆ ONNX (cosine similarity >0.99)  
**Fase 8:** Convertir a FP16, medir tamaÃ±o final

### ValidaciÃ³n crÃ­tica

```python
# Misma imagen, misma salida
imagen = ...
emb_pytorch = modelo_pytorch(imagen)       # [1, 512]
emb_onnx = modelo_onnx(imagen)             # [1, 512]
similitud = cosine_similarity(emb_pytorch, emb_onnx)
assert similitud > 0.99, f"DegradaciÃ³n en exportaciÃ³n: {similitud}"
```

---

## ðŸ”µ Fase 9-10 â€” Android + SQLite-vec

**Estado:** â³ Pendiente Fases 6-8  
**Responsable:** TÃº (desarrollador Android)  
**DuraciÃ³n estimada:** 2-3 dÃ­as  
**Deliverable:** APK prototipo + paquete regional Antioquia

### Flujo

```
APK (inmovilizado)
â”œâ”€â”€ ONNX Runtime
â”œâ”€â”€ bioclip_anura_encoder_fp16.onnx (~173 MB)
â””â”€â”€ SQLite-vec

Paquetes regionales (descargables)
â”œâ”€â”€ antioquia.sitrana (2-5 MB)
â”‚   â”œâ”€â”€ embeddings (5 especies Ã— 10 imÃ¡genes Ã— 512-d)
â”‚   â”œâ”€â”€ metadata (JSON: taxonomÃ­a, coordenadas, referencias)
â”‚   â””â”€â”€ fotos (JPEG pequeÃ±o para UI)
â”œâ”€â”€ cauca.sitrana
â””â”€â”€ ...
```

---

## ðŸŸ¢ Fase 11 â€” Pruebas en Redmi Note 13 Pro+

**Estado:** â³ Pendiente Fases 9-10  
**Responsable:** TÃº  
**DuraciÃ³n estimada:** 1-2 dÃ­as (mediciones + iteraciÃ³n)  
**Deliverable:** Reporte de latencia, RAM, Top-1, offline status

### MÃ©tricas a medir

| MÃ©trica | Objetivo |
|---|---|
| TamaÃ±o APK | <200 MB |
| Encoder load time | <2 seg |
| Embedding time (per imagen) | <500 ms |
| RAM pico | <2 GB |
| Top-1 on-device â‰ˆ Top-1 desktop | Â±2pp |
| Offline support | âœ… |
| SQLite-vec latencia | <100 ms para Top-5 |

---

## ðŸŸ¢ Fase 12 â€” IteraciÃ³n / Pulido

**Estado:** â³ Pendiente Fases 11  
**Responsable:** TÃº  
**DuraciÃ³n estimada:** 1-3 dÃ­as  
**Deliverable:** VersiÃ³n final lista para 27 sep

---

## Go/No-Go Decisiones

| Checkpoint | Criterio | Consecuencia si No |
|---|---|---|
| **Fase 0-1** (Hoy) | BioCLIP carga sin errores | Debugging entorno CUDA/PyTorch |
| **Fase 2-3** (MaÃ±ana) | Baseline >40% Top-1 | BioCLIP puede no ser compatible con dataset |
| **Fase 4** (16-17 sep) | H4 llega O declino variante A | Transfer Learning bloqueado indefinidamente |
| **Fase 5** (18 sep) | Top-1 â‰¥ baseline + 20pp | Considerar arquitectura alternativa o mejor dataset |
| **Fase 6-8** (21 sep) | PyTorch â‰ˆ ONNX >0.99 cosine | Problemas de conversiÃ³n, requiere debug |
| **Fase 9-10** (23 sep) | APK corre sin crashes | Debugging ONNX Runtime en Android |
| **Fase 11** (25 sep) | Latencia <1 seg, RAM OK | OptimizaciÃ³n FP16 mÃ¡s agresiva o backend alternativo |

---

**Ãšltima actualizaciÃ³n:** 2026-09-11  
**Responsable:** C-11 decision, usuario ejecuta Fases 0-3 ahora  
**Referencias:** [[Inconsistencias y Decisiones Pendientes]] (C-11), [[Experimentos Fallidos y Decisiones Descartadas]] (F-1)



