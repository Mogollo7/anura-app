# FASE 8B ? ENSEMBLE SOFTMAX + kNN

## Estado: ENSEMBLE_NO_MEJORA

## 1. Alcance
- Evaluaci?n retrospectiva del ensemble Softmax + kNN usando ?nicamente TRAIN como referencia de escala.
- No se modific? modelo, dataset ni producci?n.

## 2. Limitaci?n metodol?gica
> No existe una calibraci?n independiente. TRAIN fue usado s?lo para estimar los par?metros de escala del score.

## 3. Fuentes
- KNOWN: 766 im?genes F3.
- UNKNOWN: 56 im?genes F4, con Hyloxalus_picachos=15 y Sachatamia_electrops=41.
- Softmax: scores from F3/F4.
- kNN: from knn_open_set_results.json.
- Referencia de escala: TRAIN (non-augmented, 3260 images).

## 4. Normalizaci?n
- Cada se?al se normaliz? con min-max calculado exclusivamente sobre TRAIN.
- Se eligi? min-max por ser determinista y reproducible, sin usar UNKNOWN ni KNOWN para fijar par?metros.

## 5. Pesos evaluados
- 0.25/0.75, 0.50/0.50, 0.75/0.25 (softmax/knn)

## 6. Resultados

| M?todo | AUROC | FPR@95TPR | UDR | FAR | KAR | OSCR |
|---|---:|---:|---:|---:|---:|---:|
| Softmax Top1 | 0.585812 | 0.8928571428571429 | 0.1071428571428571 | 0.8928571428571429 | 0.9543080939947781 | NOT_COMPUTABLE |
| Softmax Margin | 0.584647 | 0.875 | 0.125 | 0.875 | 0.9503916449086162 | NOT_COMPUTABLE |
| kNN Max Similarity | 0.678478 | 0.9642857142857143 | 0.0357142857142857 | 0.9642857142857143 | 0.9817232375979112 | NOT_COMPUTABLE |
| kNN Mean Top5 | 0.675308 | 0.9642857142857143 | 0.0357142857142857 | 0.9642857142857143 | 0.9712793733681462 | NOT_COMPUTABLE |
| kNN Consensus | 0.510083 | 0.9821428571428571 | 0.017857142857142905 | 0.9821428571428571 | 0.9817232375979112 | NOT_COMPUTABLE |
| Ensemble best observed | 0.702793 | 0.9285714285714286 | 0.0714285714285714 | 0.9285714285714286 | 0.9595300261096605 | NOT_COMPUTABLE |


## 7. Comparaci?n
- Softmax best individual: AUROC 0.585812.
- kNN best individual: AUROC 0.678478.
- Ensemble best observed: AUROC 0.702793; FAR 0.9285714285714286.

## 8. False Acceptance
- Los UNKNOWN con mayor evidencia en Softmax/kNN fueron revisados en ensemble_cases.csv.
- El punto cr?tico es que la mejora de AUROC no necesariamente mejora el FAR operacional.

## 9. False Rejection
- Los KNOWN con puntuaciones bajas fueron revisados en el an?lisis anal?tico, y la tasa de aceptaci?n KNOWN fue reportada en KAR.

## 10. Resultados por UNKNOWN
- Se evaluaron por especie separadamente: Hyloxalus_picachos y Sachatamia_electrops.
- El resumen anal?tico se conserva en los artefactos JSON/CSV; no se ajust? ning?n peso sobre UNKNOWN.

## 11. Limitaciones
- TRAIN no es una calibraci?n independiente.
- UNKNOWN n=56, con solo 2 especies.
- No se dispone de un conjunto de referencia independiente para normalizar y elegir pesos.
- OSCR se marca como NOT_COMPUTABLE porque los scores ensemble no representan un clasificador completo con relaci?n de clasificaci?n correcta para cada threshold.

## 12. Conclusi?n
- Resultado: ENSEMBLE_NO_MEJORA
- Esta fase es exclusivamente evaluativa y no modifica el modelo ni el dataset.
