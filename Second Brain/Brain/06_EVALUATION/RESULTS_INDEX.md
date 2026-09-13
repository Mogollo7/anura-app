# Índice de resultados por fases

Corte: 2026-09-13. **NOT_EXECUTED** solo aparece cuando ninguna fuente Markdown contiene evidencia de ejecución; una fase puede tener diseño y tareas pendientes sin ser un resultado.

| Fase | Objetivo | Datos | Modelo | Configuración | Resultado | Métricas | Conclusión | Limitaciones | Artefactos |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Definir requisitos y alcance | RF/RNF e historias documentados | No aplica | Objetivos, riesgos y roadmap | **EXECUTED (documental)** | RNF-01 ≤3 s, RNF-02 ≤4 s p95, RNF-05 ≤150 MB, etc. | Alcance y criterios fijados | No es validación de producto | [Objetivos](../01 Proyecto/Objetivos y Alcance.md) |
| 2 | Construir dataset y split reproducible | 41 especies; 12.256 imágenes citadas; 3.260 embeddings train; test de 766 | No aplica | `GroupSplit` por individuo/localidad | **EXECUTED parcialmente** | 70 individuos/especie en Etapa I; una imagen faltante en EXP-014 | Base suficiente para experimentos reportados, requiere auditoría continua | Fuentes y conteos varían por alcance (28/41); no asumir equivalencia | [Estrategia](../02 Metodología/Estrategia de Construcción del Dataset.md) |
| 3 | Anotar anatomía y preparar segmentación | Guía CVAT v1.0, 16 etiquetas; 25–30 imágenes/especie para segmentador | Segmentación semántica planificada | CVAT, jerarquía y reglas de calidad | **PARTIAL** | Cobertura de máscaras binarias 99,1–99,3 % en corrida reportada | Protocolo listo; ejecución en volumen y modelo semántico no evidenciados | No hay métricas semánticas | [Guía CVAT](../03 Anotación y Segmentación/Guía CVAT/Guía CVAT — Índice.md) |
| 4 | Entrenar BioCLIP para 41 especies | 41 especies, split del test documentado | BioCLIP, cabezas y fine-tuning; variante A | oversampling, class weights, augmentación | **EXECUTED** | 35,3 % zero-shot → 57,0 % fine-tune; escasas 53,1 %, abundantes 56,7 % | Checkpoint base válido; confusiones taxonómicas persisten | No es aún evaluación de campo | [EXP-001/002](../05 Evaluación y Métricas/Experimentos y Resultados.md) |
| 5 | Evaluar exactitud y errores | 766 test; revisión de 97 fallos y muestra de 150 | BioCLIP FP32/FP16; variante C diagnóstica | comparaciones pareadas | **EXECUTED** | Etapa I ~99 %/10 especies; 60,7 % vs 50,7 % vs 44,7 % en 150 imágenes; 81 % con prior GPS | El modelo global vigente es A + prior; C necesita reentrenamiento | Cifras de alcances distintos no son comparables directamente | `bioclip_anura_mejor.pt`, gráficos y EXP-011–013 |
| 6 | Recuperación vectorial y paquetes regionales | 3.260 train; Antioquia 2.073 vectores/25 especies | k-NN coseno, encoder ONNX | k=5 ponderado; paquete regional | **EXECUTED** | Completo: 56,4/77,9 Top-1/3; Antioquia: 66,2/83,7; +11,8 pp Top-1 | Ruta regional supera al clasificador global en el subconjunto | Falta prueba de latencia/memoria on-device | `encoder_anura_fp16.onnx`, `antioquia_v1.sqlite` |
| 7 | Open-set y desconocidos | Conjuntos near/far descritos, no medidos | MSP, temperature, energy, Mahalanobis propuestos | umbral elegido en validación | **NOT_EXECUTED** | Sin AUROC/FPR@95TPR en Markdown | No se puede afirmar detección operativa | No hay corpus versionado ni umbral congelado | [Protocolo](../02 Metodología/Open-Set Recognition.md) |
| 8 | Despliegue móvil/offline | Emulación CPU y artefacto ONNX | ONNX FP16; Kotlin planificado | 1/2/4 hilos | **PARTIAL** | 165,6 MB; ~405 MB RAM; 403→154 ms | Exportación validada; integración de app no demostrada | Presupuesto RNF-05 y medición real de batería pendientes | `anura_clasificador_fp16.onnx`, EXP-008/009 |
| 9 | Piloto y validación en campo | Plantilla de reporte sin filas completadas | App/modelo final | ≥2 localidades planificadas | **NOT_EXECUTED** | Sin Top-1/Top-3/SUS de piloto | No hay evidencia de desempeño real | Sin reportes de participantes, clima o fallos | [Reportes piloto](../05 Evaluación y Métricas/Reportes de Pruebas Piloto.md) |

## Fuentes
[Bitácora completa](../05 Evaluación y Métricas/Experimentos y Resultados.md) · [Métricas offline](../05 Evaluación y Métricas/Métricas Offline.md) · [Estado](../00_PROJECT_STATE.md)



