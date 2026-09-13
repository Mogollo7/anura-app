# Duplicados y versiones

## Método
El manifiesto [00_SOURCE_MANIFEST.json](./00_SOURCE_MANIFEST.json) registra ruta, título y SHA-256 de las fuentes inventariadas. Se conserva cada original; no se borran ni se sobrescriben para resolver duplicados. La comparación de contenido debe usar la ruta y el hash, no solo el título.

## Duplicados funcionales observados
- **Índices de dos generaciones:** `00_MASTER_INDEX.md` y `00_KNOWLEDGE_MAP.md` apuntan a las mismas 18 áreas. El primero es índice compacto; el segundo añade árbol y enlaces de lectura.
- **Índices consolidados y originales:** `03_AI_BIOCLIP/INDEX.md`, `05_OPEN_SET/INDEX.md` y `06_EVALUATION/RESULTS_INDEX.md` son síntesis nuevas; las notas detalladas permanecen en `04 Desarrollo Técnico`, `02 Metodología` y `05 Evaluación y Métricas`.
- **Propuestas históricas:** [Plan de Acción](./04 Desarrollo Técnico/Plan de Acción y Arquitectura Conceptual.md) conserva EfficientNet/Qdrant como histórico; [Modelo BioCLIP](./04 Desarrollo Técnico/Modelo de Visión — BioCLIP.md) documenta la sustitución.
- **Resultados repetidos con distinto alcance:** ~99 % corresponde a Etapa I/10 especies; 57 % a 41 especies; 81 % incluye prior GPS; 66,2 % a paquete regional Antioquia. No son duplicados ni deben mezclarse.
- **Formatos del modelo:** `bioclip_anura_mejor.pt` (checkpoint), `anura_clasificador_fp16.onnx` (clasificador completo) y `encoder_anura_fp16.onnx` (encoder para k-NN) cumplen roles distintos.

## Inconsistencias que no se resuelven por borrado
El manifiesto conserva 502 fuentes inventariadas, mientras la bóveda actual contiene 94 Markdown; son universos de inventario distintos. Los conteos 28/41 especies aparecen en documentos de alcance diferente y deben etiquetarse por fase. Una imagen ausente en disco fue omitida explícitamente en EXP-014. Estas diferencias quedan registradas en [Contradicciones](./00_CONTRADICTIONS.md) y [Resultados](./06_EVALUATION/RESULTS_INDEX.md).

## Regla de versionado
Toda cifra nueva debe indicar fecha, versión de modelo, versión de dataset, split, configuración y artefacto. Nunca reemplazar una fila histórica de [Experimentos y Resultados](./05 Evaluación y Métricas/Experimentos y Resultados.md).



