---
title: "Experimentos Fallidos y Decisiones Descartadas"
proyecto: Anura
tipo: registro-histÃ³rico
estado: activo
tags: [anura, fracasos, experimentos, decisiones-descartadas, lecciones-aprendidas]
---

# Experimentos Fallidos y Decisiones Descartadas

[[Anura â€” Ãndice General]] Â· [[Inconsistencias y Decisiones Pendientes]]

> [!warning] PropÃ³sito de este documento
> Registro de experimentos que fallaron, decisiones que fueron descartadas, e investigaciones que resultaron inviables. No es "trabajo perdido" â€” es **reducciÃ³n de espacio de bÃºsqueda**: evita reintentar lo mismo y documenta por quÃ© no funcionÃ³. Cada fracaso cierra una rama del Ã¡rbol de decisiones.

---

## ðŸ”´ Fracasos CrÃ­ticos (Bloqueadores)

### F-1 Â· DestilaciÃ³n de BioCLIP v1 â†’ MobileNetV3-Small (2026-09-11)

| Aspecto | Detalle |
|---|---|
| **DecisiÃ³n que descartaba** | C-5 y C-8: usar destilaciÃ³n Multi-Head Loss con T=4.0, Î±=0.3 para entrenar alumno MobileNetV3-Small on-device |
| **HipÃ³tesis teÃ³rica** | Un modelo pequeÃ±o (2,07M params, 3,95 MB FP16) podrÃ­a aprender de BioCLIP v1 (86M params, ViT-B/16) usando Knowledge Distillation con pÃ©rdida conjunta (CE + KL) |
| **ConfiguraciÃ³n de prueba** | Variante A: imagen completa (sin mÃ¡scara de segmentaciÃ³n). 2.230 imÃ¡genes de entrenamiento, GroupSplit por obs_id, 5 Ã©pocas warm-up + 20 Ã©pocas destilaciÃ³n |
| **Resultado** | **FRACASO TOTAL** |
| **MÃ©trica fracaso** | Top-1: Teacher 57,7% â†’ Student 24,3% = **degradaciÃ³n 33,39 puntos** (objetivo: <10 puntos) |
| **Otras mÃ©tricas** | Top-3: degradaciÃ³n 29,0 pp; Coherencia tax.: degradaciÃ³n solo 3,6 pp (esto SÃ se transfiriÃ³); Cascada: vÃ¡lida (43,6% especie, 29,9% gÃ©nero, 26,5% familia) |
| **Causa raÃ­z** | **AsimetrÃ­a fundamental de preparaciÃ³n del input.** Teacher (BioCLIP v1) preentrenado sobre TreeOfLife-10M, ya "sabe quÃ© es una rana"; solo aprende "cuÃ¡l rana". Student (MobileNetV3 desde ImageNet 0) aprende "esto es una rana" Y "cuÃ¡l rana" simultÃ¡neamente, con rana ocupando ~10% del encuadre. DestilaciÃ³n no puede cerrar un gap tan grande (necesita <5 puntos) con entrada de baja calidad |
| **Lo que SÃ funcionÃ³** | Multi-Head Loss (CE paralela Familia/GÃ©nero/Especie + KL). La cascada jerÃ¡rquica fue correcta. El problema no es el algoritmo; es la distribuciÃ³n de entrada |
| **LecciÃ³n aprendida** | DestilaciÃ³n necesita (1) entrada de calidad para ambos modelos, (2) gap de capacidad pequeÃ±o, (3) teacher y student con preentrenamiento similar. Con una rana en 10% del encuadre, ninguno de estos se cumple |
| **PrÃ³ximo paso** | Re-evaluar destilaciÃ³n con **variante C (segmentada)** si H4 llega. Si rana ocupa 80%+ del encuadre, el gap puede ser cerrable. Si H4 no llega, encontrar arquitectura on-device alternativa (INT4 de BioCLIP, backbone nuevo, o solo servidor) |
| **Archivos** | `training/resultados_diagnostico_destilacion.md` (anÃ¡lisis completo), `training/log_diagnostico.txt` (log de la corrida), `training/checkpoints_diagnostico/` (pesos descartados del alumno) |
| **DocumentaciÃ³n oficial** | [[Inconsistencias y Decisiones Pendientes]] (C-10), esta secciÃ³n (F-1) |

**Timeline de fracaso:**
- 2026-09-08: DecisiÃ³n C-8 de usar MobileNetV3-Small con destilaciÃ³n
- 2026-09-11: Corrida diagnÃ³stica completa (extracciÃ³n embeddings + linear probe + warmup + 20 Ã©pocas destilaciÃ³n)
- 2026-09-11: Resultados: Top-1 = 24,3%, inaceptable
- 2026-09-11: DecisiÃ³n de cancelar destilaciÃ³n, marcar como INVIABLE hasta H4

---

## ðŸŸ  Fracasos Parciales (Recuperables)

### F-2 Â· CuantizaciÃ³n INT8 de BioCLIP (2026-09-08)

| Aspecto | Detalle |
|---|---|
| **DecisiÃ³n que descartaba** | C-5 original: usar BioCLIP v1 (ViT-B/16) cuantizado INT8 + activaciones FP16 como backbone on-device |
| **HipÃ³tesis teÃ³rica** | La cuantizaciÃ³n simÃ©trica INT8 de pesos + FP16 de activaciones podrÃ­a comprimir BioCLIP de 90 MB a ~11 MB manteniendo precisiÃ³n aceptable |
| **Resultado** | **FRACASO** â€” exactitud cayÃ³ a ~0,2% (inutilizable) |
| **Causa raÃ­z** | Los outliers de atenciÃ³n del ViT (caracterÃ­sticas de los Transformers) no toleran INT8; la geometrÃ­a del espacio de embeddings se destruye bajo cuantizaciÃ³n simÃ©trica tan agresiva |
| **LecciÃ³n aprendida** | ViT + INT8 es una combinaciÃ³n conocida como problemÃ¡tica en la literatura. Los CNNs (como MobileNetV3) toleran INT8 mejor que los Transformers. DeberÃ­a haberse consultado primero la literatura antes de intentar |
| **PrÃ³ximo paso** | Si se necesita BioCLIP on-device, intentar INT4 (aÃºn mÃ¡s drÃ¡stico, pero quizÃ¡ necesario) o aceptar solo servidor. DestilaciÃ³n fue la soluciÃ³n intentada (C-5 pivot a EdgeNeXt-Tiny), que a su vez fallÃ³ (F-1) |
| **DocumentaciÃ³n oficial** | [[Inconsistencias y Decisiones Pendientes]] (C-5, con menciÃ³n del fracaso de INT8) |

---

## ðŸŸ¡ Decisiones Descartadas (No Fracasadas, Reemplazadas)

### D-1 Â· EdgeNeXt-Tiny como alumno destilado (descartado 2026-09-11)

| Aspecto | Detalle |
|---|---|
| **DecisiÃ³n anterior** | C-5 (2026-09-08): Usar EdgeNeXt-Tiny (~2-4M params) como alumno en destilaciÃ³n |
| **RazÃ³n de cambio a C-8** | Soporte de conversiÃ³n a LiteRT/TFLite mÃ¡s maduro en MobileNetV3-Small. EdgeNeXt es menos probado en conversores ONNX/TFLite |
| **Resultado de C-8** | MobileNetV3-Small tampoco funcionÃ³ (F-1), asÃ­ que EdgeNeXt sigue siendo una opciÃ³n en-congelador, pero no probada |
| **LecciÃ³n** | La "madurez del conversor" no fue el problema real; el problema fue la destilaciÃ³n completa (F-1). Si alguna vez se reintenta destilaciÃ³n, EdgeNeXt podrÃ­a ser comparable a MobileNetV3 |
| **DocumentaciÃ³n oficial** | [[Inconsistencias y Decisiones Pendientes]] (C-5, C-8) |

### D-2 Â· EfficientNet-B0 como backbone (descartado 2026-09-04)

| Aspecto | Detalle |
|---|---|
| **DecisiÃ³n descartada** | [[Plan de AcciÃ³n y Arquitectura Conceptual]] proponÃ­a EfficientNet-B0 + Triplet Loss |
| **RazÃ³n de descarte** | BioCLIP v1 ya preentrenado en TreeOfLife-10M con estructura taxonÃ³mica incorporada, mejor para "pocos datos por clase" (70 individuos/especie). EfficientNet desde ImageNet necesitarÃ­a mucho mÃ¡s dato por especie para generalizar |
| **Evidencia** | La Etapa I (10 especies, BioCLIP) alcanzÃ³ ~99% exactitud con los mismos 70 individuos/especie que fallarÃ­an con EfficientNet |
| **LecciÃ³n** | El preentrenamiento especÃ­fico del dominio (BioCLIP en fauna, TreeOfLife) supera al preentrenamiento genÃ©rico (EfficientNet en ImageNet) cuando hay pocos datos por clase |
| **DocumentaciÃ³n oficial** | [[Inconsistencias y Decisiones Pendientes]] (C-2) |

### D-3 Â· ObjectBox como motor vectorial embebido (descartado 2026-09-08)

| Aspecto | Detalle |
|---|---|
| **DecisiÃ³n anterior** | C-1 (2026-09-04): ObjectBox en Android (HNSW nativo, Kotlin de primera clase) |
| **RazÃ³n de cambio a C-6** | InstrucciÃ³n directa del autor (2026-09-08): "SQLite con sqlite-vec es lo mÃ¡s Ã³ptimo para la nueva arquitectura" |
| **Ventaja de sqlite-vec** | (1) Portabilidad: un `.sqlite` es un archivo autocontenido; descargar paquete regional = descargar un archivo, abrirlo bajo demanda, borrarlo con `file.delete()`. ObjectBox gestiona un almacÃ©n Ãºnico vÃ­a mmap, no pensado para montar/desmontar bases aisladas en caliente. (2) Consultas hÃ­bridas: metadatos (taxonomÃ­a) + vectores en la misma base. (3) Footprint mÃ­nimo sobre SQLite |
| **LecciÃ³n** | La portabilidad y granularidad de paquetes regionales es crÃ­tica para modelos on-device que deben descargar/actualizar datos. ObjectBox fue prematura sin evaluar el modelo operativo (paquetes regionales estilo Merlin) |
| **DocumentaciÃ³n oficial** | [[Inconsistencias y Decisiones Pendientes]] (C-1, C-6) |

### D-4 Â· ReutilizaciÃ³n del backbone EdgeNeXt-Tiny para audio (descartado 2026-09-08)

| Aspecto | Detalle |
|---|---|
| **DecisiÃ³n anterior** | C-2 consideraba reutilizar BioCLIP; C-7 evaluÃ³ reutilizar EdgeNeXt-Tiny |
| **OpciÃ³n evaluada** | Fine-tuning de EdgeNeXt (destilado para visiÃ³n) sobre mel-espectrogramas de audio |
| **RazÃ³n de descarte** | InstrucciÃ³n del autor (2026-09-08): "Modelo de audio propio y dedicado, por facilidad de implementaciÃ³n" |
| **JustificaciÃ³n tÃ©cnica** | EdgeNeXt-Tiny fue destilado con objetivo estrecho (morfologÃ­a de rana); riesgo de mala transferencia a espectrogramas es alto. AdemÃ¡s, modelo de audio dedicado (1-3 MB) no compromete presupuesto total (15-30 MB del RNF-05 revisado) |
| **LecciÃ³n** | No forzar reutilizaciÃ³n sin evaluar primero la transferencia. A veces, un modelo pequeÃ±o dedicado es mÃ¡s barato que optimizar la transferencia de un modelo general |
| **DocumentaciÃ³n oficial** | [[Inconsistencias y Decisiones Pendientes]] (C-7) |

---

## ðŸ“‹ Tabla Resumen: Fracasos y Descarte

| # | Tipo | Experimento/DecisiÃ³n | Fecha Fracaso | Grave | Recuperable | DocumentaciÃ³n |
|---|---|---|---|---|---|---|
| F-1 | Fracaso Total | DestilaciÃ³n BioCLIPâ†’MobileNetV3 | 2026-09-11 | âœ… SÃ­ (bloquea on-device) | âš ï¸ Solo si H4 llega | [[Inconsistencias y Decisiones Pendientes]] C-10 |
| F-2 | Fracaso Parcial | INT8 de BioCLIP | 2026-09-08 | âœ… SÃ­ (motivÃ³ F-1) | âš ï¸ INT4 queda abierto | [[Inconsistencias y Decisiones Pendientes]] C-5 |
| D-1 | Descartado | EdgeNeXt-Tiny como alumno | 2026-09-11 | âš ï¸ No (reemplazado, no fallido) | âœ… PodrÃ­a reintentarse | [[Inconsistencias y Decisiones Pendientes]] C-5, C-8 |
| D-2 | Descartado | EfficientNet-B0 | 2026-09-04 | âŒ No | âœ… SÃ­, pero BioCLIP es mejor | [[Inconsistencias y Decisiones Pendientes]] C-2 |
| D-3 | Descartado | ObjectBox | 2026-09-08 | âŒ No | âœ… sqlite-vec es mejor | [[Inconsistencias y Decisiones Pendientes]] C-1, C-6 |
| D-4 | Descartado | Reutilizar EdgeNeXt para audio | 2026-09-08 | âŒ No | âœ… Modelo dedicado es mejor | [[Inconsistencias y Decisiones Pendientes]] C-7 |

---

## ðŸ”¬ Lecciones Clave

### 1. **Preentrenamiento especÃ­fico del dominio supera al genÃ©rico cuando hay pocos datos**
- BioCLIP (TreeOfLife-10M) >> EfficientNet (ImageNet) para 70 individuos/especie
- **Aplicar a:** cualquier tarea de visiÃ³n biolÃ³gica con <1000 ejemplos por clase

### 2. **DestilaciÃ³n requiere input de calidad para ambos modelos**
- Si el teacher ve ranas en 10% del encuadre y el alumno ve lo mismo, no hay "enseÃ±anza" â€” ambos estÃ¡n confundidos
- DestilaciÃ³n necesita gap pequeÃ±o (<5-10 puntos) Y entrada de buena calidad
- **Aplicar a:** no intentar destilaciÃ³n hasta tener segmentaciÃ³n

### 3. **ViT + cuantizaciÃ³n INT8 es una combinaciÃ³n conocida problemÃ¡tica**
- Los Transformers son sensibles a cuantizaciÃ³n simÃ©trica en los outliers de atenciÃ³n
- CNN (MobileNetV3) toleran INT8 mejor que ViT
- **Aplicar a:** consultar literatura ANTES de intentar optimizaciones nuevas

### 4. **Portabilidad y granularidad de datos son crÃ­ticas on-device**
- SQLite (archivo autocontenido) >> ObjectBox (almacÃ©n Ãºnico mmap) para paquetes regionales
- El modelo operativo (descargar/actualizar/borrar paquetes por regiÃ³n) determina la tecnologÃ­a
- **Aplicar a:** definir operaciones on-device primero, elegir motor segundo

### 5. **No forzar reutilizaciÃ³n sin evaluar transferencia primero**
- Un modelo pequeÃ±o dedicado (1-3 MB) es a veces mÃ¡s eficiente que optimizar la transferencia de uno general
- El presupuesto total es lo que importa, no la elegancia arquitectÃ³nica
- **Aplicar a:** audio, segmentaciÃ³n, cualquier rama nueva â€” considerar modelo dedicado

---

## ðŸ“Œ Impacto en el Cronograma

### Blockers Actuales (por fracaso)

| Blocker | Causado por | Fecha Descubierto | Impacto | SoluciÃ³n |
|---|---|---|---|---|
| **Arquitectura on-device indefinida** | F-1 (destilaciÃ³n inviable) | 2026-09-11 | El alumno MobileNetV3 no puede ser entrenado sin destilaciÃ³n. BioCLIP full requiere INT4 o simplemente no cabe | Esperar H4 â†’ re-evaluar destilaciÃ³n con variante C, o elegir alternativa (INT4, backbone nuevo, solo servidor) |
| **H4 crÃ­tico para validar hipÃ³tesis** | F-1 (gap en imagen completa) | 2026-09-11 | No se puede probar si la destilaciÃ³n funciona con segmentaciÃ³n sin H4 | Establecer H4 como fecha lÃ­mite de Go/No-Go |

---

## ðŸ”® HipÃ³tesis Pendientes (No Descartadas, AÃºn Por Probar)

| # | HipÃ³tesis | Depende de | Status |
|---|---|---|---|
| H-1 | DestilaciÃ³n funciona en variante C (segmentada) con rana en 80%+ encuadre | H4 (segmentaciÃ³n) | â³ Esperando H4 |
| H-2 | BioCLIP INT4 + activaciones INT8 puede funcionar (mÃ¡s agresivo que INT8 full) | Presupuesto y latencia on-device | â³ No probado |
| H-3 | Un backbone CNN pequeÃ±o nuevo (desde ImageNet + fine-tuning) converge en 2.230 imÃ¡genes | Tiempo de GPU restante | â³ No probado |

---

## Resumen Final

**Fracasos crÃ­ticos:** 1 (destilaciÃ³n, F-1)  
**Fracasos parciales:** 1 (INT8, F-2, mitigado por F-1)  
**Decisiones descartadas (no fracasadas):** 4 (reemplazadas por opciones mejores)  

**Estado:** La arquitectura on-device estÃ¡ **indefinida** a falta de H4 o de una decisiÃ³n de backup (INT4, backbone nuevo, o solo servidor).

**PrÃ³ximos pasos:**
1. Aguardar H4 (segmentaciÃ³n)
2. Si H4 llega: re-evaluar destilaciÃ³n con variante C
3. Si H4 no llega: elegir plan B para on-device antes del 27 sep

---

**Ãšltima actualizaciÃ³n:** 2026-09-11  
**Responsable:** Claude Code  
**Referencias cruzadas:** [[Inconsistencias y Decisiones Pendientes]], [[Cronograma y Plan de Trabajo]], [[Riesgos del Proyecto]]



