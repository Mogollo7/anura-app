# Diagnóstico actual — Euclidean Raw Open Set

**Fecha:** 2026-09-14  
**Ejecutado:** `validation/fase21_open_set_v2/scripts/run_fase21_protocol.py` sobre artefactos actuales.  
**Cambios metodológicos:** ninguno. BioCLIP, embeddings, catálogo, covarianza y thresholds oficiales permanecen sin cambios. Las salidas actualizadas se escribieron solo bajo `validation/fase21_open_set_v2/`.

## Resultado reproducido

El encoder ONNX coincide con el hash congelado y todas las entradas auditadas son 512D. Sobre el blind test de Fase 21 (2,990 KNOWN + 56 UNKNOWN), la distancia Euclidean raw sigue siendo el mejor método comparado:

| Método | AUROC | Balanced accuracy | FAR | FRR | KAR | UDR |
|---|---:|---:|---:|---:|---:|---:|
| Euclidean raw | **0.5991** | **0.6366** | 0.1786 | 0.5482 | 0.4518 | 0.8214 |
| Euclidean normalizado | 0.5905 | 0.6321 | 0.1786 | 0.5572 | 0.4428 | 0.8214 |
| Cosine | 0.5905 | 0.6321 | 0.1786 | 0.5572 | 0.4428 | 0.8214 |
| Mahalanobis | 0.4629 | 0.5610 | 0.1429 | 0.7351 | 0.2649 | 0.8571 |

Euclidean raw supera a Mahalanobis por **0.1361 AUROC** y por **0.0756** de balanced accuracy. No se promueve a producción: el threshold `0.6804759` es diagnóstico y el FAR/FRR no cumple un gate de producto.

## Dónde empieza el problema

### 1. No empieza en la integridad del encoder

- El SHA-256 ONNX esperado coincide: `219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad`.
- REFERENCE, TRAIN, KNOWN limpio y UNKNOWN del protocolo son 512D y pertenecen al mismo contrato de embedding.
- No hubo reentrenamiento ni mezcla de etiquetas de verdad en la inferencia de distancias.

Esto descarta un checkpoint equivocado o una ruptura dimensional como causa inmediata.

### 2. La primera degradación cuantificada está en Mahalanobis/covarianza

La representación visual cruda tiene señal, pero débil (AUROC 0.5991). Al introducir centrado, covarianza compartida e inversión Mahalanobis, cae a AUROC 0.4629: peor que azar en este blind test.

La covarianza de REFERENCE tiene 512×512, solo 798 imágenes de 10 especies, ratio máximo/mínimo de eigenvalor ≈10,026 y eigenvalor mínimo `1.93e-05`. Ledoit-Wolf regulariza, pero esa transformación pondera direcciones inestables y empeora la separación observada. Esto identifica un problema de **postprocesamiento Open Set**, no una prueba de que BioCLIP esté corrupto.

### 3. Euclidean raw revela una limitación real de representación, no una solución completa

Aunque elimina la degradación Mahalanobis, Euclidean raw solo alcanza AUROC 0.5991. Para rechazar el 82.1% de UNKNOWN en Fase 21, rechaza también el 54.8% de KNOWN. La distribución de distancias de las clases se solapa de forma importante.

Por tanto, la causa no es exclusivamente el threshold: incluso antes de fijar un operating point, la capacidad de separación del embedding para este problema Open Set es modesta.

### 4. El protocolo de threshold es un problema independiente

La partición VALIDATION de Fase 21 contiene únicamente KNOWN. Por ello, un Youden J de 1.0 en calibración es un artefacto: no puede elegir un compromiso FAR/FRR sin UNKNOWN. El threshold de Euclidean raw no es un threshold productivo ni fue ajustado en esta auditoría.

Se requiere un pool CALIBRATION separado y mixto (KNOWN + UNKNOWN), y un BLIND TEST que no participe ni en selección de método ni de threshold.

### 5. Los datos de evaluación actuales muestran que la cobertura es parte crítica del problema

Fase 21 contiene solo 56 UNKNOWN de **dos especies**: `Hyloxalus picachos` (misma familia, género distinto) y `Sachatamia electrops` (familia distinta). No hay UNKNOWN del mismo género ni prueba dedicada sobre especies conocidas difíciles.

Al aplicar el threshold diagnóstico Fase 21 (`0.6805`) al conjunto actual Fase 23A de 439 UNKNOWN disponibles, más diverso, Euclidean raw acepta erróneamente **250/439 = 56.95%**. Por especie, el FAR observado fue: Espadarana `88.8%`, Rhinella `81.9%`, Dendropsophus `68.9%`, Smilisca `29.6%` y Leptodactylus `23.5%`.

Esto no demuestra que las imágenes sean incorrectas; demuestra que el resultado favorable limitado de Fase 21 no generaliza al UNKNOWN disponible más amplio. Además, Fase 23A documenta que 2 de 7 especies declaradas (183 imágenes) no están físicamente presentes, de modo que tampoco es una evaluación completa de su manifest.

### 6. Falta evidencia en las especies conocidas difíciles

Fase 20 ya marcó confusión intra-género/individual en `Pristimantis paisa`, `P. taeniatus`, `Dendropsophus bogerti`, `D. microcephalus`, `Boana cinerascens`, `B. punctata` y `P. erythropleura`. Esas especies no están cubiertas por el blind test específico de Fase 21, por lo que no se puede atribuir el FRR elevado a una causa taxonómica concreta todavía.

## Atribución final

| Parte | Diagnóstico | Evidencia |
|---|---|---|
| Checkpoint/preprocesamiento/forma de vector | No es el fallo inmediato | Hash y contrato 512D correctos |
| Modelo/embedding BioCLIP | Limitación parcial | Euclidean raw AUROC 0.5991: señal débil y solapamiento KNOWN/UNKNOWN |
| Mahalanobis/covarianza | Falla técnica demostrada | AUROC baja de 0.5991 a 0.4629; espectro de covarianza mal condicionado |
| Threshold | No validable con el split actual | VALIDATION solo contiene KNOWN; calibración de Youden es artefactual |
| Datos/evaluación | Bloqueo crítico de generalización | Solo 2 UNKNOWN en Fase 21; FAR 56.95% al aplicar Euclidean raw al UNKNOWN actual de Fase 23A |

## Conclusión

**Euclidean raw es preferible a Mahalanobis para investigar el Open Set actual, pero no es un release aceptable.**

La prioridad no es reentrenar BioCLIP ni mover un threshold para subir una métrica. Primero se necesita una evaluación correctamente separada: UNKNOWN taxonómicamente diverso, CALIBRATION mixta independiente y BLIND TEST independiente, incluyendo especies conocidas difíciles e individuos no vistos. Solo entonces se podrá decidir si el límite restante está principalmente en el embedding o si un nuevo Open Set sobre el mismo embedding alcanza los objetivos.
