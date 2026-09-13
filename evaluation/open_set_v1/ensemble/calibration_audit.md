# Fase 8A — Auditoría de fuente de calibración

**Estado:** `PARTIAL`

## data cleaned

- 12.254 imágenes JPG y un manifiesto auxiliar `dataset_limpio.json`.
- Contiene 41 especies/directorios, incluyendo las dos especies UNKNOWN de Fase 4.
- No se modificó ningún archivo del dataset.

## Splits y uso

- TRAIN: 3609 entradas de manifiesto.
- VAL: 697 entradas; fue usado para seleccionar checkpoint y early stopping.
- TEST: 766 entradas; es la evaluación F3 y queda excluido.
- No manifestado: 7531 imágenes; split y uso histórico no demostrables con evidencia suficiente.

## kNN

- `antioquia_v1.sqlite`: 2073 vectores, 25 especies.
- El código de Fase 8/9 lo construye desde TRAIN no aumentado.
- No se detectó solapamiento por path con F3/F4; no es una calibración independiente, sino referencia del índice.

## Candidatos

- Softmax: TRAIN solo puede usarse como referencia de escala, no como calibración independiente.
- kNN: el índice existente puede describir la escala de similitud, pero fue construido con TRAIN.
- VAL no es válido como calibración independiente porque participó en model selection.
- TEST y F4 UNKNOWN no pueden usarse para calibrar.
- No se identificó un conjunto REFERENCE/CALIBRATION independiente.

## Leakage

- Solapamiento directo F3/F4: paths=0, obs_id=0, SHA-256=0.
- Perceptual hash e individual_id completo no están disponibles para una comprobación global; obs_id fue inferido de los nombres.

## Decisión

La situación es `PARTIAL`: hay fuentes legítimas para referencia de escala (TRAIN y el índice kNN), pero no existe una fuente verdaderamente independiente de calibración. La Fase 8 no debe seleccionar pesos ni normalizadores con F3, F4 o UNKNOWN; cualquier ensemble posterior debe declararse exploratorio o esperar una fuente independiente.

No se ejecutó ensemble, no se calcularon métricas de ensemble, no se modificó modelo, dataset ni producción.
