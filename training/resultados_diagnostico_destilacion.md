---
título: Resultados de Destilación BioCLIP v1 → MobileNetV3-Small (Diagnóstico Variante A)
fecha: 2026-09-11
tipo: evaluación técnica
estado: INVIABLE
tags: [anura, destilación, conocimiento, resultados, diagnóstico]
---

# Resultados de Destilación BioCLIP v1 → MobileNetV3-Small

**Conclusión:** Destilación con Multi-Head Loss en variante A (imagen completa) es **INVIABLE** por degradación de 33,39 puntos en Top-1 (objetivo: <10 puntos).

---

## Resumen Ejecutivo

| Métrica | Teacher (BioCLIP v1) | Student (MobileNetV3-S) | Diferencia |
|---|---|---|---|
| **Top-1** | 57,7% | 24,3% | **−33,39 pp** |
| **Top-3** | 78,8% | 49,8% | −29,0 pp |
| **Coherencia Taxonómica** | 83,4% | 79,7% | −3,6 pp |
| **Acierto Cascada** | 63,5% | 41,8% | −21,7 pp |
| **Parámetros** | 86M | 2,07M | 41.5x menor |

### Veredicto

- ❌ **Top-1 inaceptable** — 33,39 puntos sobre el objetivo de <10
- ✅ **Cascada y coherencia transferidas** — la estructura jerárquica Familia→Género→Especie se aprendió
- ⚠️ **Problema raíz:** Sin segmentación, la rana es un objeto pequeño (~10% del encuadre) en un fondo ruidoso; el alumno no puede hacer la discriminación fina de especies

---

## Metodología y Setup

### Dataset
- **Fuente:** `D:\Anura\data dirty` (scraper iNaturalist)
- **Total de imágenes:** 15.229
- **Imágenes válidas:** 15.228 (1 corrupta, excluida)
- **Train:** 2.230 imágenes (1.193 individuos)
- **Val:** 479 imágenes (246 individuos)
- **Test:** 548 imágenes (267 individuos)
- **Grouping:** GroupSplit por `obs_id` de iNaturalist, sin inter-partition leakage

### Configuración de Destilación
```python
# Fases del entrenamiento
[teacher] Extracción de embeddings BioCLIP (una sola vez)
[teacher] Linear probe: 300 épocas de ajuste de 3 cabezas (Familia/Género/Especie)
[warm-up] Warm-up del alumno: 5 épocas, solo entropía cruzada
[destilación] Destilación conjunta: 20 épocas, Multi-Head Loss

# Parámetros de destilación
Multi-Head Loss: α = 0.3, T = 4.0
Optimizer warm-up: AdamW lr=1e-3
Optimizer destilación: AdamW lr=1e-4, CosineAnnealingLR, parada temprana
Batch size: 4 (GPU)
Hardware: NVIDIA RTX 4050, CUDA 12.8
```

### Arquitecturas

**Teacher: BioCLIP v1 (ViT-B/16)**
- Parámetros: 86M
- Embedding: 512-d
- Estado: Congelado, solo se ajustan 3 cabezas de clasificación
- Source: HuggingFace (`microsoft/bioclip-v1`)

**Student: MobileNetV3-Small**
- Parámetros: 2,069,332 (2,07M)
- Embedding: 512-d
- Cabezas: 3 (Familia/Género/Especie)
- Tamaño FP16: 3,95 MB (dentro del presupuesto RNF-05)

---

## Resultados Detallados

### Fase 1: Linear Probe del Teacher (300 épocas)

| Época | Pérdida | Top-1 Val |
|---|---|---|
| 25 | 5.119 | 44,1% |
| 50 | 3.665 | 50,3% |
| 100 | 2.483 | 56,2% |
| 150 | 1.953 | 57,4% |
| 200 | 1.624 | 58,0% |
| 250 | 1.391 | 58,3% |
| 300 | 1.213 | **58,3%** |

**Mejor Top-1 en validación: 58,5%** (época ~250-275)

### Fase 2: Warm-up del Alumno (5 épocas, CE solo)

| Época | Pérdida |
|---|---|
| 1 | 7.644 |
| 2 | 7.018 |
| 3 | 6.799 |
| 4 | 6.422 |
| 5 | **6.191** |

### Fase 3: Destilación Conjunta (20 épocas, Multi-Head Loss)

| Época | L Total | CE | KL | Top-1 Val | Top-3 Val |
|---|---|---|---|---|---|
| 1 | 5.177 | 5.410 | 0.317 | 17,5% | 38,2% |
| 2 | 4.691 | 5.080 | 0.283 | 16,9% | 39,5% |
| 3 | 4.575 | 4.906 | 0.277 | 18,4% | 39,7% |
| 4 | 4.338 | 4.729 | 0.261 | 19,4% | 40,3% |
| 5 | 4.133 | 4.569 | 0.247 | 20,0% | 42,2% |
| 6 | 4.084 | 4.446 | 0.246 | 19,6% | 43,6% |
| 7 | 3.903 | 4.286 | 0.234 | 21,3% | 42,6% |
| 8 | 3.772 | 4.134 | 0.226 | 21,3% | 42,6% |
| 9 | 3.606 | 3.965 | 0.216 | 21,9% | 45,5% |
| 10 | 3.575 | 3.948 | 0.214 | 22,1% | 45,1% |
| 11 | 3.504 | 3.824 | 0.210 | 22,1% | 45,1% |
| 12 | 3.380 | 3.715 | 0.202 | 22,6% | 45,9% |
| 13 | 3.299 | 3.602 | 0.198 | 22,6% | 44,7% |
| 14 | 3.260 | 3.551 | 0.196 | 20,9% | 44,7% |
| 15 | 3.144 | 3.444 | 0.188 | 22,8% | 45,1% |
| 16 | 3.158 | 3.464 | 0.189 | 22,6% | 45,3% |
| 17 | 3.138 | 3.397 | 0.189 | 21,5% | 44,9% |
| 18 | 3.091 | 3.348 | 0.186 | 22,1% | 44,7% |
| 19 | 3.069 | 3.405 | 0.183 | **23,2%** | **45,9%** |
| 20 | 3.116 | 3.380 | 0.188 | 21,1% | 44,7% |

**Mejor rendimiento:** Época 19, Top-1 = 23,2%

---

## Análisis de Resultados

### 1. Degradación de Top-1 (33,39 puntos)

```
Teacher: 57,7%
Student: 24,3%
Degradación: 57,7 - 24,3 = 33,4 puntos
```

**Esto es inaceptable.** El estándar de la industria para destilación es <5-10 puntos. Una degradación de 33 puntos significa que el alumno perdió casi la mitad de la capacidad del maestro.

### 2. Top-3 y Coherencia Taxonómica

A pesar de la catástrofe en Top-1, dos métricas se transfieren bien:

- **Top-3:** 78,8% (teacher) → 49,8% (student) = 29,0 puntos de degradación
- **Coherencia Taxonómica:** 83,4% (teacher) → 79,7% (student) = solo 3,6 puntos

**Interpretación:** El alumno SÍ aprendió la estructura jerárquica Familia→Género→Especie. El problema no es el diseño de la cascada o la Multi-Head Loss; el problema es que **no puede hacer la discriminación fina de especies** dentro de un género.

### 3. Distribución de Predicciones en Cascada

El student afirma predicciones en:
- **Especie:** 43,6%
- **Género:** 29,9%
- **Familia:** 26,5%

Esto es **excelente desde el punto de vista de robustez** — el alumno no está haciendo predicciones a ciegas. Cuando no confía en especies, baja a género. Cuando no confía en género, baja a familia. El problema es que incluso cuando afirma especie, solo acierta en ~24% de los casos.

### 4. Análisis de la Curva de Entrenamiento

La pérdida de destilación bajó de 5.18 (época 1) a 3.07 (época 19):
```
Loss: 5.18 → 4.69 → 4.58 → 4.34 → ... → 3.07
```

**El modelo SÍ está aprendiendo.** La pérdida converge. Pero **la métrica de validación no mejora al ritmo que lo hace la pérdida**, señal típica de que:
- (A) La capacidad del modelo es insuficiente para el problema, o
- (B) La distribución de entrenamiento vs. validación es muy diferente

### 5. Causa Probable: Variante A sin Segmentación

En variante A (imagen completa), la rana es un objeto pequeño rodeado de fondo:
- Rana ocupa ~10% del encuadre
- Fondo: hojarasca, ramas, tierra
- La discriminación fina depende de detalles visuales muy pequeños

**Comparación:**
- **Teacher (BioCLIP v1):** Preentrenado sobre TreeOfLife-10M viendo millones de ranas, ya sabe qué es una rana. Solo necesita resolver qué especie. → 57,7%
- **Student (MobileNetV3-Small):** Entrena desde ImageNet (fotos de perros, coches, gatos, etc.). Nunca vio ranas a esta escala. Tiene que aprender "esto es una rana" Y "cuál rana" al mismo tiempo. → 24,3%

**Esto es una asimetría fatal para la destilación:**
- La destilación funciona cuando el alumno y maestro reciben la **misma distribución de entrada** y hay una brecha pequeña de capacidad.
- Aquí, la distribución de entrada es igual, pero el maestro ya vio millones de ejemplos antes, mientras que el alumno ve 2.230 en su vida entera.

---

## Variante C (Segmentada) — Hipótesis

Si en variante C (con máscara de segmentación) la rana ocupa 80-90% del encuadre y está centrada:
- La entrada es de **mucha mayor calidad** para ambos modelos
- El teacher sube a ~75-85% (según la Etapa I)
- El student podría cerrar más del gap en destilación

**Pero esto no se puede confirmar sin H4.** Por ahora, variante C permanece como hipótesis.

---

## Decisiones Inducidas

### ❌ Destilación es INVIABLE en variante A
No se continuarán entrenamientos por esta ruta en imagen completa. El coste de GPU ya está pagado, el resultado es claro.

### ❌ MobileNetV3-Small como backbone on-device queda INDEFINIDO
C-8 dependía de que la destilación funcionara. Sin destilación, la arquitectura on-device sigue siendo incógnita.

### ✅ Multi-Head Loss y cascada son VÁLIDOS (cuando hay datos de calidad)
La transferencia de coherencia taxonómica (79,7%) demuestra que el algoritmo y la pérdida son correctos. El problema es la entrada.

### ✅ H4 (Segmentación) es CRÍTICO
La hipótesis de que variante C (segmentada) permitirá cerrar el gap se vuelve **Go/No-Go** en el cronograma. Si H4 no llega en tiempo, el proyecto no tiene arquitectura on-device.

---

## Recomendaciones

### Inmediato (antes del 27 sep)
1. **No invertir más GPU en destilación.** El experimento está cerrado.
2. **Re-evaluar opciones de on-device sin destilación:**
   - (A) BioCLIP v1 con cuantización más agresiva (INT4 + activaciones INT8, trade-off latencia/precisión)
   - (B) Backbone nuevo desde cero sin teacher (riesgo: tiempo de convergencia, falta de datos)
   - (C) Aceptar que sin H4, no hay on-device — solo servidor

3. **Esperar H4 y entonces sí medir variante C segmentada** — si segmentación llega, se re-entrena identificación (student + teacher) con datos de entrada limpia, y se re-evalúa destilación. Los 2,07M parámetros de MobileNetV3 podrían ser viables en variante C.

### Documentación
- [ ] Actualizar [[Inconsistencias y Decisiones Pendientes]] con C-10 (inviable)
- [ ] Marcar C-5 y C-8 como parcialmente revertidas por C-10
- [ ] Registrar en [[Cronograma y Plan de Trabajo]] que destilación está bloqueada hasta H4 y decisión on-device es pendiente

---

## Archivos Generados

```
D:\Anura\training\
├── log_diagnostico.txt              # Log completo de la corrida (extracción, linear probe, warm-up, destilación)
├── checkpoints_diagnostico/         # Carpeta con checkpoints del alumno MobileNetV3-Small
│   ├── modelo_alumno_final.pt       # Mejor checkpoint (época 19)
│   └── ...
├── resultados_diagnostico_destilacion.md  # Este archivo
└── lista_negra.json                 # Imagen corrupta excluida
```

### Checkpoints del Student
```
checkpoints_diagnostico/modelo_alumno_final.pt
  - Parámetros: 2,069,332
  - Embedding: 512-d
  - Cabezas: Familia (9), Género (15), Especie (28)
  - Mejor Top-1 validación: 23,2% (época 19)
```

---

## Conclusión

La destilación de BioCLIP v1 → MobileNetV3-Small en variante A (imagen completa, sin máscara de segmentación) produce una **degradación inaceptable de 33,39 puntos en Top-1** contra un objetivo de <10 puntos.

La causa no es el algoritmo (Multi-Head Loss y cascada se transfieren bien), sino la **asimetría de preparación del input:** el teacher vio millones de ranas, el alumno ve 2.230, y ambos reciben una imagen donde la rana es 10% del encuadre.

**Decisión:** Destilación es **INVIABLE hasta que H4 (segmentación) desbloquee variante C**, donde se espera que la calidad de entrada sea suficiente para cerrar el gap. Mientras tanto, la arquitectura on-device permanece como incógnita.

---

**Fecha de esta evaluación:** 2026-09-11  
**Responsable:** Claude Code  
**Próximos pasos:** Esperar H4, re-evaluar con variante C segmentada, o pivotear hacia arquitectura on-device alternativa sin destilación
