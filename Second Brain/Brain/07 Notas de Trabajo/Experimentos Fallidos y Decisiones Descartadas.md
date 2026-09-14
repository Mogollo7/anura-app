---
title: "Experimentos Fallidos y Decisiones Descartadas"
proyecto: Anura
tipo: registro-histórico
estado: activo
tags: [anura, fracasos, experimentos, decisiones-descartadas, lecciones-aprendidas]
---

# Experimentos Fallidos y Decisiones Descartadas

[[Anura â€” àndice General]] · [[Inconsistencias y Decisiones Pendientes]]

> [!warning] Propósito de este documento
> Registro de experimentos que fallaron, decisiones que fueron descartadas, e investigaciones que resultaron inviables. No es "trabajo perdido" â€” es **reducción de espacio de bàºsqueda**: evita reintentar lo mismo y documenta por qué no funcionó. Cada fracaso cierra una rama del árbol de decisiones.

---

## ðŸ”´ Fracasos Críticos (Bloqueadores)

### F-1 · Destilación de BioCLIP v1 â†’ MobileNetV3-Small (2026-09-11)

| Aspecto | Detalle |
|---|---|
| **Decisión que descartaba** | C-5 y C-8: usar destilación Multi-Head Loss con T=4.0, Î±=0.3 para entrenar alumno MobileNetV3-Small on-device |
| **Hipótesis teórica** | Un modelo pequeño (2,07M params, 3,95 MB FP16) podría aprender de BioCLIP v1 (86M params, ViT-B/16) usando Knowledge Distillation con pérdida conjunta (CE + KL) |
| **Configuración de prueba** | Variante A: imagen completa (sin máscara de segmentación). 2.230 imágenes de entrenamiento, GroupSplit por obs_id, 5 épocas warm-up + 20 épocas destilación |
| **Resultado** | **FRACASO TOTAL** |
| **Métrica fracaso** | Top-1: Teacher 57,7% â†’ Student 24,3% = **degradación 33,39 puntos** (objetivo: <10 puntos) |
| **Otras métricas** | Top-3: degradación 29,0 pp; Coherencia tax.: degradación solo 3,6 pp (esto Sà se transfirió); Cascada: válida (43,6% especie, 29,9% género, 26,5% familia) |
| **Causa raíz** | **Asimetría fundamental de preparación del input.** Teacher (BioCLIP v1) preentrenado sobre TreeOfLife-10M, ya "sabe qué es una rana"; solo aprende "cuál rana". Student (MobileNetV3 desde ImageNet 0) aprende "esto es una rana" Y "cuál rana" simultáneamente, con rana ocupando ~10% del encuadre. Destilación no puede cerrar un gap tan grande (necesita <5 puntos) con entrada de baja calidad |
| **Lo que Sà funcionó** | Multi-Head Loss (CE paralela Familia/Género/Especie + KL). La cascada jerárquica fue correcta. El problema no es el algoritmo; es la distribución de entrada |
| **Lección aprendida** | Destilación necesita (1) entrada de calidad para ambos modelos, (2) gap de capacidad pequeño, (3) teacher y student con preentrenamiento similar. Con una rana en 10% del encuadre, ninguno de estos se cumple |
| **Próximo paso** | Re-evaluar destilación con **variante C (segmentada)** si H4 llega. Si rana ocupa 80%+ del encuadre, el gap puede ser cerrable. Si H4 no llega, encontrar arquitectura on-device alternativa (INT4 de BioCLIP, backbone nuevo, o solo servidor) |
| **Archivos** | `training/resultados_diagnostico_destilacion.md` (análisis completo), `training/log_diagnostico.txt` (log de la corrida), `training/checkpoints_diagnostico/` (pesos descartados del alumno) |
| **Documentación oficial** | [[Inconsistencias y Decisiones Pendientes]] (C-10), esta sección (F-1) |

**Timeline de fracaso:**
- 2026-09-08: Decisión C-8 de usar MobileNetV3-Small con destilación
- 2026-09-11: Corrida diagnóstica completa (extracción embeddings + linear probe + warmup + 20 épocas destilación)
- 2026-09-11: Resultados: Top-1 = 24,3%, inaceptable
- 2026-09-11: Decisión de cancelar destilación, marcar como INVIABLE hasta H4

---

## ðŸŸ  Fracasos Parciales (Recuperables)

### F-2 · Cuantización INT8 de BioCLIP (2026-09-08)

| Aspecto | Detalle |
|---|---|
| **Decisión que descartaba** | C-5 original: usar BioCLIP v1 (ViT-B/16) cuantizado INT8 + activaciones FP16 como backbone on-device |
| **Hipótesis teórica** | La cuantización simétrica INT8 de pesos + FP16 de activaciones podría comprimir BioCLIP de 90 MB a ~11 MB manteniendo precisión aceptable |
| **Resultado** | **FRACASO** â€” exactitud cayó a ~0,2% (inutilizable) |
| **Causa raíz** | Los outliers de atención del ViT (características de los Transformers) no toleran INT8; la geometría del espacio de embeddings se destruye bajo cuantización simétrica tan agresiva |
| **Lección aprendida** | ViT + INT8 es una combinación conocida como problemática en la literatura. Los CNNs (como MobileNetV3) toleran INT8 mejor que los Transformers. Debería haberse consultado primero la literatura antes de intentar |
| **Próximo paso** | Si se necesita BioCLIP on-device, intentar INT4 (aàºn más drástico, pero quizá necesario) o aceptar solo servidor. Destilación fue la solución intentada (C-5 pivot a EdgeNeXt-Tiny), que a su vez falló (F-1) |
| **Documentación oficial** | [[Inconsistencias y Decisiones Pendientes]] (C-5, con mención del fracaso de INT8) |

---

## ðŸŸ¡ Decisiones Descartadas (No Fracasadas, Reemplazadas)

### D-1 · EdgeNeXt-Tiny como alumno destilado (descartado 2026-09-11)

| Aspecto | Detalle |
|---|---|
| **Decisión anterior** | C-5 (2026-09-08): Usar EdgeNeXt-Tiny (~2-4M params) como alumno en destilación |
| **Razón de cambio a C-8** | Soporte de conversión a LiteRT/TFLite más maduro en MobileNetV3-Small. EdgeNeXt es menos probado en conversores ONNX/TFLite |
| **Resultado de C-8** | MobileNetV3-Small tampoco funcionó (F-1), así que EdgeNeXt sigue siendo una opción en-congelador, pero no probada |
| **Lección** | La "madurez del conversor" no fue el problema real; el problema fue la destilación completa (F-1). Si alguna vez se reintenta destilación, EdgeNeXt podría ser comparable a MobileNetV3 |
| **Documentación oficial** | [[Inconsistencias y Decisiones Pendientes]] (C-5, C-8) |

### D-2 · EfficientNet-B0 como backbone (descartado 2026-09-04)

| Aspecto | Detalle |
|---|---|
| **Decisión descartada** | [[Plan de Acción y Arquitectura Conceptual]] proponía EfficientNet-B0 + Triplet Loss |
| **Razón de descarte** | BioCLIP v1 ya preentrenado en TreeOfLife-10M con estructura taxonómica incorporada, mejor para "pocos datos por clase" (70 individuos/especie). EfficientNet desde ImageNet necesitaría mucho más dato por especie para generalizar |
| **Evidencia** | La Etapa I (10 especies, BioCLIP) alcanzó ~99% exactitud con los mismos 70 individuos/especie que fallarían con EfficientNet |
| **Lección** | El preentrenamiento específico del dominio (BioCLIP en fauna, TreeOfLife) supera al preentrenamiento genérico (EfficientNet en ImageNet) cuando hay pocos datos por clase |
| **Documentación oficial** | [[Inconsistencias y Decisiones Pendientes]] (C-2) |

### D-3 · ObjectBox como motor vectorial embebido (descartado 2026-09-08)

| Aspecto | Detalle |
|---|---|
| **Decisión anterior** | C-1 (2026-09-04): ObjectBox en Android (HNSW nativo, Kotlin de primera clase) |
| **Razón de cambio a C-6** | Instrucción directa del autor (2026-09-08): "SQLite con sqlite-vec es lo más óptimo para la nueva arquitectura" |
| **Ventaja de sqlite-vec** | (1) Portabilidad: un `.sqlite` es un archivo autocontenido; descargar paquete regional = descargar un archivo, abrirlo bajo demanda, borrarlo con `file.delete()`. ObjectBox gestiona un almacén àºnico vía mmap, no pensado para montar/desmontar bases aisladas en caliente. (2) Consultas híbridas: metadatos (taxonomía) + vectores en la misma base. (3) Footprint mínimo sobre SQLite |
| **Lección** | La portabilidad y granularidad de paquetes regionales es crítica para modelos on-device que deben descargar/actualizar datos. ObjectBox fue prematura sin evaluar el modelo operativo (paquetes regionales estilo Merlin) |
| **Documentación oficial** | [[Inconsistencias y Decisiones Pendientes]] (C-1, C-6) |

### D-4 · Reutilización del backbone EdgeNeXt-Tiny para audio (descartado 2026-09-08)

| Aspecto | Detalle |
|---|---|
| **Decisión anterior** | C-2 consideraba reutilizar BioCLIP; C-7 evaluó reutilizar EdgeNeXt-Tiny |
| **Opción evaluada** | Fine-tuning de EdgeNeXt (destilado para visión) sobre mel-espectrogramas de audio |
| **Razón de descarte** | Instrucción del autor (2026-09-08): "Modelo de audio propio y dedicado, por facilidad de implementación" |
| **Justificación técnica** | EdgeNeXt-Tiny fue destilado con objetivo estrecho (morfología de rana); riesgo de mala transferencia a espectrogramas es alto. Además, modelo de audio dedicado (1-3 MB) no compromete presupuesto total (15-30 MB del RNF-05 revisado) |
| **Lección** | No forzar reutilización sin evaluar primero la transferencia. A veces, un modelo pequeño dedicado es más barato que optimizar la transferencia de un modelo general |
| **Documentación oficial** | [[Inconsistencias y Decisiones Pendientes]] (C-7) |

---

## ðŸ“‹ Tabla Resumen: Fracasos y Descarte

| # | Tipo | Experimento/Decisión | Fecha Fracaso | Grave | Recuperable | Documentación |
|---|---|---|---|---|---|---|
| F-1 | Fracaso Total | Destilación BioCLIPâ†’MobileNetV3 | 2026-09-11 | âœ… Sí (bloquea on-device) | âš ï¸ Solo si H4 llega | [[Inconsistencias y Decisiones Pendientes]] C-10 |
| F-2 | Fracaso Parcial | INT8 de BioCLIP | 2026-09-08 | âœ… Sí (motivó F-1) | âš ï¸ INT4 queda abierto | [[Inconsistencias y Decisiones Pendientes]] C-5 |
| D-1 | Descartado | EdgeNeXt-Tiny como alumno | 2026-09-11 | âš ï¸ No (reemplazado, no fallido) | âœ… Podría reintentarse | [[Inconsistencias y Decisiones Pendientes]] C-5, C-8 |
| D-2 | Descartado | EfficientNet-B0 | 2026-09-04 | âŒ No | âœ… Sí, pero BioCLIP es mejor | [[Inconsistencias y Decisiones Pendientes]] C-2 |
| D-3 | Descartado | ObjectBox | 2026-09-08 | âŒ No | âœ… sqlite-vec es mejor | [[Inconsistencias y Decisiones Pendientes]] C-1, C-6 |
| D-4 | Descartado | Reutilizar EdgeNeXt para audio | 2026-09-08 | âŒ No | âœ… Modelo dedicado es mejor | [[Inconsistencias y Decisiones Pendientes]] C-7 |

---

## ðŸ”¬ Lecciones Clave

### 1. **Preentrenamiento específico del dominio supera al genérico cuando hay pocos datos**
- BioCLIP (TreeOfLife-10M) >> EfficientNet (ImageNet) para 70 individuos/especie
- **Aplicar a:** cualquier tarea de visión biológica con <1000 ejemplos por clase

### 2. **Destilación requiere input de calidad para ambos modelos**
- Si el teacher ve ranas en 10% del encuadre y el alumno ve lo mismo, no hay "enseñanza" â€” ambos están confundidos
- Destilación necesita gap pequeño (<5-10 puntos) Y entrada de buena calidad
- **Aplicar a:** no intentar destilación hasta tener segmentación

### 3. **ViT + cuantización INT8 es una combinación conocida problemática**
- Los Transformers son sensibles a cuantización simétrica en los outliers de atención
- CNN (MobileNetV3) toleran INT8 mejor que ViT
- **Aplicar a:** consultar literatura ANTES de intentar optimizaciones nuevas

### 4. **Portabilidad y granularidad de datos son críticas on-device**
- SQLite (archivo autocontenido) >> ObjectBox (almacén àºnico mmap) para paquetes regionales
- El modelo operativo (descargar/actualizar/borrar paquetes por región) determina la tecnología
- **Aplicar a:** definir operaciones on-device primero, elegir motor segundo

### 5. **No forzar reutilización sin evaluar transferencia primero**
- Un modelo pequeño dedicado (1-3 MB) es a veces más eficiente que optimizar la transferencia de uno general
- El presupuesto total es lo que importa, no la elegancia arquitectónica
- **Aplicar a:** audio, segmentación, cualquier rama nueva â€” considerar modelo dedicado

---

## ðŸ“Œ Impacto en el Cronograma

### Blockers Actuales (por fracaso)

| Blocker | Causado por | Fecha Descubierto | Impacto | Solución |
|---|---|---|---|---|
| **Arquitectura on-device indefinida** | F-1 (destilación inviable) | 2026-09-11 | El alumno MobileNetV3 no puede ser entrenado sin destilación. BioCLIP full requiere INT4 o simplemente no cabe | Esperar H4 â†’ re-evaluar destilación con variante C, o elegir alternativa (INT4, backbone nuevo, solo servidor) |
| **H4 crítico para validar hipótesis** | F-1 (gap en imagen completa) | 2026-09-11 | No se puede probar si la destilación funciona con segmentación sin H4 | Establecer H4 como fecha límite de Go/No-Go |

---

## ðŸ”® Hipótesis Pendientes (No Descartadas, Aàºn Por Probar)

| # | Hipótesis | Depende de | Status |
|---|---|---|---|
| H-1 | Destilación funciona en variante C (segmentada) con rana en 80%+ encuadre | H4 (segmentación) | â³ Esperando H4 |
| H-2 | BioCLIP INT4 + activaciones INT8 puede funcionar (más agresivo que INT8 full) | Presupuesto y latencia on-device | â³ No probado |
| H-3 | Un backbone CNN pequeño nuevo (desde ImageNet + fine-tuning) converge en 2.230 imágenes | Tiempo de GPU restante | â³ No probado |

---

## Resumen Final

**Fracasos críticos:** 1 (destilación, F-1)  
**Fracasos parciales:** 1 (INT8, F-2, mitigado por F-1)  
**Decisiones descartadas (no fracasadas):** 4 (reemplazadas por opciones mejores)  

**Estado:** La arquitectura on-device está **indefinida** a falta de H4 o de una decisión de backup (INT4, backbone nuevo, o solo servidor).

**Próximos pasos:**
1. Aguardar H4 (segmentación)
2. Si H4 llega: re-evaluar destilación con variante C
3. Si H4 no llega: elegir plan B para on-device antes del 27 sep

---

**àšltima actualización:** 2026-09-11  
**Responsable:** Claude Code  
**Referencias cruzadas:** [[Inconsistencias y Decisiones Pendientes]], [[Cronograma y Plan de Trabajo]], [[Riesgos del Proyecto]]



