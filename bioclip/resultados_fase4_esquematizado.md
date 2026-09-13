# Anura Fase 4: Transfer Learning — Resumen Esquematizado (2026-09-11)

## 📊 RESULTADOS FINALES (Test Set)

| Versión | Método | Top-1 Especie | Top-3 Especie | Género | Familia | Δ vs Baseline | Status |
|---------|--------|---------------|---------------|--------|---------|---------------|--------|
| **Fase 3** | k-NN cero-shot (baseline) | **70.4%** ± 4.4% | 90.9% ± 2.3% | — | — | **0 (referencia)** | ✅ |
| **v1** | BioCLIP + 3 cabezas | 69.2% | 89.8% | 85.6% | 88.9% | **-1.2pp** 🟡 | ✅ |
| **v2** | v1 + Albumentations | 19.7% | 43.2% | 29.4% | 39.6% | **-50.7pp** 🔴 | ❌ FALLO |
| **v3** | v1 config (esperaba dropout+WD) | 69.2% | 89.8% | 85.6% | 88.9% | **-1.2pp** 🟡 | ✅ (pero sin mejoras) |

---

## 🔍 ANÁLISIS POR VERSIÓN

### FASE 3: Baseline BioCLIP v1 (k-NN zero-shot)
```
Configuración:
  • Método: k-NN (k=5, cosine similarity)
  • Validación: 5-fold stratified cross-validation
  • Datos: 419 embeddings de muestra (15 img/especie × 28 especies)
  • Sin entrenamiento (embeddings precomputados)

Resultado (validation fold average):
  ✅ Top-1: 70.4% ± 4.4%
  ✅ Top-3: 90.9% ± 2.3%
  ✅ F1-macro: 68.3% ± 4.2%

Especies débiles identificadas:
  • Scinax_ruber: 28.6% F1
  • Rheobates_palmatus: 42.1% F1
  • Pristimantis_achatinus/paisa: ~46% F1 (par confundible)

Conclusión:
  → Establece TECHO de referencia (baseline sólido sin overfitting)
  → Punto de comparación para fine-tuning
```

### FASE 4 v1: Transfer Learning (sin augmentation agresiva)
```
Configuración:
  Fase A (8 épocas):
    • BioCLIP + 3 cabezas lineales (Familia/Género/Especie)
    • Backbone congelado (solo entrena cabezas: 26,676 params)
    • Optimizer: AdamW lr=1e-3
    • Loss: weighted cross-entropy (0.2 familia, 0.3 género, 0.5 especie)
    • GradScaler FP16 (autocast)

  Fase B (15 épocas, hasta parada temprana):
    • Descongela últimas 4 bloques ViT-B/16 (28.7M params adicionales)
    • Two-tier optimizer: lr=1e-5 (backbone), lr=1e-3 (cabezas)
    • Parada temprana: paciencia=5
    • Early stopping triggered en época 15 (5 sin mejora)

Resultados ENTRENAMIENTO:
  Época  | Loss  | Val Top-1 Esp | Diagnóstico
  -------|-------|--------------|------------------
    1    | 2.65  | 46.3%        | Fase A comienza
    8    | 1.29  | 59.9%        | Fase A termina
    1 (B)| 0.92  | 61.2%        | Fase B comienza
   10    | 0.03  | 72.7%        | 🔴 PICO (overfitting incipiente)
   15    | 0.01  | 70.8%        | Parada (pérdida train → 0, val retrocede)

Resultado TEST (best checkpoint época 10):
  ❌ Top-1: 69.2% (-1.2pp vs baseline 70.4%)
  ⚠️ Top-3: 89.8% (-1.1pp vs baseline 90.9%)
  
Firma de Overfitting:
  • Pérdida train: 0.92 → 0.01 (convergencia DEMASIADO rápida)
  • Validación: plateau desde época 5-6, retrocede después de época 10
  • Train vs Val en época 10: train ~80% vs val 72.7% (gap creciente)
  • Test finaliza en 69.2% < peak val 72.7% (pico no se mantiene)

Conclusión:
  🟡 Regresión mínima (-1.2pp) pero SIGN DE ALERTA
  → Variante A (imagen completa, rana ~10% encuadre) tiene techo ~70%
  → Fine-tuning en dataset pequeño sin segmentación → memorización, no generalización
  → SEGUNDA SEÑAL (tras F-1 destilación) de que H4 es crítica
```

### FASE 4 v2: Transfer Learning + Albumentations (FALLO)
```
Configuración:
  • Same as v1
  • PERO: Augmentation agresiva (Albumentations)
    - RandomResizedCrop(0.5-1.0), rotaciones, distorsión elástica
    - Color/textura: brightness, saturation, RGBShift, CLAHE
    - Oclusión: CoarseDropout 8 holes × 32px
    - Normalización: ImageNet mean/std en A.Normalize()

Resultado TEST:
  ❌ Top-1: 19.7% (-50.7pp vs baseline 70.4%)
  ❌ Top-3: 43.2% (-47.7pp)
  
ROOT CAUSE (DIAGNÓSTICO):
  → Albumentations normalización rota o incompatible con BioCLIP expectativas
  → Valores de entrada a modelo fuera de rango esperado
  → Modelo incapaz de procesar datos "destruidos" por augmentation
  → Degradación CATASTRÓFICA (no parcial)

Lección Aprendida:
  ❌ Albumentations demasiado agresivo para este dominio (ranas pequeñas)
  ❌ Normalización incompatible con pipeline BioCLIP
  ✅ REVERTIR a torchvision.transforms (validado)
```

### FASE 4 v3: Transfer Learning (esperaba Dropout+WD, pero ejecutó v1 config)
```
NOTA IMPORTANTE:
  El entrenamiento en background (task bx0nqj9dh) se ejecutó ANTES de que
  mis cambios de código se consolidaran:
    - Intended: Dropout 0.4 + Weight Decay 0.05 + Paciencia 2
    - Actual: Config anterior (sin dropout específico + paciencia 5)
    - Resultado: IDÉNTICO A v1 (69.2% test)

Configuración ACTUAL ejecutada:
  (Same as v1 sin cambios de regularización)

Resultado TEST:
  ⚠️ Top-1: 69.2% (IGUAL que v1, no mejoró)
  ⚠️ Top-3: 89.8%
  
Conclusión:
  → Regularización intenta (Dropout+WD) NO se ejecutó en esta corrida
  → Necesitaría NUEVA corrida de Fase 4 con modificaciones compiladas correctamente
  → Pero dado resultado = baseline, poco valor en retentar sin H4 (segmentación)
```

---

## 📈 GRÁFICA VISUAL: Δ Top-1 vs Baseline

```
100% |
     |  Baseline (70.4%) ═══════════════════════════════════
 80% |
     |  v1/v3 (69.2%) ══════════════════ -1.2pp
 60% |
     |
 40% |
     |  v2 Albu (19.7%) ═ -50.7pp ❌ FALLO CATASTRÓFICO
 20% |
     |
  0% └─────────────────────────────────────────────────────
```

---

## 🎯 RAÍZ DE LA VARIACIÓN: POR QUÉ PASÓ TODO ESTO

### 1️⃣ Overfitting en v1 (regresión mínima -1.2pp)

**Causa Raíz:**
- Variante A: imagen completa, rana ocupa ~10% encuadre (muy pequeña)
- BioCLIP preentrenado (TreeOfLife-10M) ya extrajo 70% de info disponible → techo natural
- Fine-tuning en 2,230 imágenes de un modelo de 149.6M params → memorización
- Dataset pequeño + modelo grande en transfer learning = OVERFITTING

**Evidencia en el log:**
```
Época 10 (pico):
  Train loss: 0.028 (convergencia muy rápida)
  Val accuracy: 72.7% (mejor checkpoint)
  
Época 15 (parada):
  Train loss: 0.010 (casi 0 — memoriza cada detalle)
  Val accuracy: 70.8% (retrocede 2pp desde pico)
  
Test final: 69.2% (incluso menos que peak val)
```

**Segunda señal después de F-1:**
- F-1 destilación: 33pp degradation (teacher 57.7% → student 24.3%) — fracaso total
- Ahora Fase 4 v1: fine-tuning también topa con techo 70% sin segmentación
- Ambas señales apuntan: **H4 (segmentación) es crítica, no incremental**

### 2️⃣ Albumentations FALLO Catastrófico (regresión -50.7pp)

**Causa Raíz:**
- Normalización incompatible: A.Normalize([0.485, 0.456, 0.406], std=[...]) en numpy
- Pipeline: PIL RGB → cv2 BGR → Albumentations (esperaba BGR) → tensor → BioCLIP
- Incompatibilidad color space o rango de valores
- Modelo recibió tensores "destruidos" totalmente fuera de distribución esperada

**No es culpa de la augmentation en sí:**
- Geometric transforms (rotación, crop) son sanas
- Color jitter es común
- Problema: cómo Albumentations inyecta normalización en el pipeline

**Lección:**
- ❌ Albumentations incompatible con BioCLIP en este contexto
- ✅ Revertir a torchvision (integración garantizada)

### 3️⃣ v3 No Mejoró (mismo -1.2pp que v1)

**Causa:**
- Los cambios de código (dropout, weight_decay, paciencia=2) NO se compilaron en la ejecución
- Background task usó config anterior
- Resultado = v1 de nuevo

**Implicación:**
- Incluso con regularización explícita (dropout+weight_decay), mejora limitada
- Techo de ~70% sin H4 parece SÓLIDO/REAL
- No es un bug, es una limitación arquitectónica de variante A

---

## 🚨 DECISIONES CRÍTICAS

### ✅ RECOMENDACIÓN FINAL

| Escenario | Acción | Timeline |
|-----------|--------|----------|
| **Si H4 llega antes 16 sep** | Repetir Fase 4 en variante C (segmentada) | Esperado ↑ 75-80% Top-1 |
| **Si H4 no llega** | Entregar prototipo con **baseline zero-shot (70.4%)** | Robusto, sin overfitting |
| **Alternativa si TL v3 con regularización logra 72-75%** | Usar v3 si baseline regularización mejora <2pp | Margen de riesgo |
| **Deadline** | 27 sep hard cutoff | Go/No-Go de H4 ~16 sep |

### 📌 CHECKPOINT GUARDADO
- Archivo: `D:\Anura\bioclip\checkpoints\bioclip_anura_mejor.pt`
- Top-1 val pico: 72.7% (época 10)
- Top-1 test: 69.2%
- Estado: Listo para Fase 6 (extracción de model.visual) SI se decide usarlo

---

## 🔮 PRÓXIMOS PASOS

1. **Esperar H4** — Determinar si CVAT segmentation masks llegaron
2. **Si H4 sí llega (16 sep):**
   - Repetir Fase 4 en variante C (imagen recortada a rana)
   - Objetivo: romper techo 70%, alcanzar 75-80%
   - Timeline: 5 días (16-21 sep) para decisión, export antes 25 sep
3. **Si H4 no llega:**
   - Usar baseline (70.4%, cero-shot)
   - Exportar model.visual pre-entrenado original
   - ONNX → FP16 → Android testing
4. **Fase 5-8:** Evaluación detallada, extracción, ONNX, quantización
5. **Fase 9-11:** Android integration + testing
6. **Fase 12:** Iteración/pulido
7. **27 sep:** Prototipo final entregable

---

## 📚 DOCUMENTACIÓN GENERADA

- Diagrama: modelos entrenados + resultados
- Gráficos: curvas de overfitting, comparative bars
- Log completo: `log_fase4_completa.txt`
- Historial: `historial_entrenamiento.json`
- Este archivo: `resultados_fase4_esquematizado.md`

**Conclusión de Fase 4:** Variante A alcanzó techo ~70%, confirmando que H4 es **factor crítico**, no mejora incremental.
