# Open Set Calibration v1 — reporte reproducible

**Fecha:** 2026-09-14  
**Estado:** `NO_GO — OPEN SET NO ALCANZA EL CRITERIO DE PRODUCTO`  
**Código ejecutado:** `run_protocol.py`  
**Salida principal:** `summary.json`, `calibration_experiment_results.csv`, `fase23a_false_accepts_frozen.csv`.

## 1. Estado del encoder

No se reentrenó, reemplazó ni modificó BioCLIP. La inferencia de las 130 imágenes UNKNOWN de calibración utilizó el ONNX FP16 congelado con el contrato existente. El diagnóstico anterior ya confirmó SHA-256 `219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad` y embeddings L2 de 512 dimensiones.

## 2. Estado de embeddings y separación visual

La distancia Euclidean raw conserva una señal visual, pero las distribuciones se solapan:

| Pool de calibración | n | Mediana d1 | p05–p95 d1 | Media d1 |
|---|---:|---:|---:|---:|
| KNOWN independiente | 2,545 | 0.6424 | 0.4035–0.9019 | 0.6451 |
| UNKNOWN histórico | 130 | 0.7070 | 0.5109–0.9131 | 0.7070 |

El desplazamiento de la mediana es pequeño respecto del solapamiento. Por eso un umbral de distancia que rechaza UNKNOWN también rechaza muchas observaciones KNOWN.

## 3. Baseline Euclidean

El baseline histórico Fase 21 permanece sin modificar: Euclidean raw AUROC 0.5991 frente a Mahalanobis 0.4629. La nueva calibración mixta obtiene para el método de centroide único:

| Método | AUROC d1 en calibración | FAR | UDR | KAR | FRR |
|---|---:|---:|---:|---:|---:|
| Centroide único, Euclidean | 0.6231 | 4.62% | 95.38% | 19.76% | 80.24% |
| Centroide único, Euclidean + margen | 0.6231 | 1.54% | 98.46% | 38.82% | 61.18% |
| Dos prototipos por especie + margen | 0.6189 | 4.62% | 95.38% | **44.95%** | 55.05% |

Los parámetros no fueron elegidos contra Fase 23A: se seleccionó el método con mayor KAR sujeto a FAR de calibración ≤5%.

## 4. Calibración Open Set válida y separación de Fase 23A

La calibración usa:

- 2,545 imágenes KNOWN del subset independiente Fase 18, con 1,406 individuos.
- 130 imágenes UNKNOWN históricas de cuatro especies que no aparecen en el conjunto `primary` usado por Fase 23A:
  - `Hyloxalus picachos`: misma familia, género ausente.
  - `Sachatamia electrops`: familia ausente.
  - `Dendropsophus minutus`: mismo género presente en catálogo.
  - `Pristimantis w-nigrum`: mismo género presente en catálogo.

El manifiesto `supplementary_historical` declara esas cuatro especies, pero sus directorios estaban vacíos. La auditoría localizó sus 130 archivos físicos en `images/final`; no se movió, copió ni modificó ningún archivo. El conjunto `images/primary` de Fase 23A no participó en selección de método ni parámetros.

Después de la calibración se congeló:

```text
method: two prototypes per species (K=2) + d1/d2 margin
distance threshold: 1.106687307357788
margin threshold:   0.09397119522094727
selection: maximum calibration KAR subject to FAR <= 5%
```

## 5. Diagnóstico de falsos positivos en Fase 23A blind

Al aplicar sin cambio el método congelado al blind Fase 23A (`primary`, 620 UNKNOWN, siete especies), se aceptaron erróneamente **229/620 = 36.94%**. UDR = 63.06%. Esto mejora frente al diagnóstico anterior de Euclidean raw simple (56.95% de FAR sobre el conjunto previo de 439 imágenes), pero sigue muy lejos de FAR ≤5% y UDR ≥95%.

| Especie UNKNOWN blind | n | Falsos aceptados | FAR por especie |
|---|---:|---:|---:|
| `Rhinella marina` | 83 | 66 | 79.5% |
| `Dendropsophus labialis` | 74 | 47 | 63.5% |
| `Leptodactylus fragilis` | 84 | 32 | 38.1% |
| `Craugastor metriosistus` | 85 | 26 | 30.6% |
| `Smilisca phaeota` | 107 | 30 | 28.0% |
| `Espadarana prosoblepon` | 87 | 23 | 26.4% |
| `Scinax rostratus` | 100 | 5 | 5.0% |

Las predicciones falsas se concentran contra pocos prototipos del catálogo:

| Especie predicha de catálogo | Falsos positivos |
|---|---:|
| `Rhinella horribilis` | 60 |
| `Dendropsophus molitor` | 53 |
| `Craugastor raniformis` | 30 |
| `Hyloscirtus palmeri` | 22 |
| `Boana lanciformis` | 21 |
| `Leptodactylus colombiensis` | 17 |

Esto responde a dos preguntas diagnósticas: los errores no son uniformes y sí se concentran en especies UNKNOWN y regiones/prototipos conocidos concretos. El archivo `fase23a_false_accepts_frozen.csv` conserva por cada falso positivo: especie real solo para evaluación, especie predicha, d1, d2, margen, consistencia de prototipo, brillo, contraste, desenfoque y ruta.

El margen no funciona como evidencia universal de incertidumbre: la mediana de margen de falsos aceptados fue 0.1627, mientras que la de rechazados fue 0.0307. En otras palabras, muchos UNKNOWN erróneamente aceptados tienen una preferencia clara por un candidato incorrecto; no son solo empates Top-1/Top-2.

## 6. Resultados de experimentos

| Experimento | Resultado de calibración | Lectura |
|---|---|---|
| A. Euclidean d1 | FAR 4.62%, KAR 19.76% | Cumple seguridad solo rechazando demasiados KNOWN. |
| B. Euclidean d1 + margen | FAR 1.54%, KAR 38.82% | El margen reduce FAR, pero sigue con FRR muy alto. |
| C/D. Quality | Sin efecto | La calidad no fue seleccionada: las imágenes aceptadas no fueron consistentemente peores en blur/contraste/tamaño que las rechazadas. |
| E. Consistencia de prototipo | Sin ganancia frente a B | No mejoró la regla congelada. |
| F. K=2 prototipos + margen | Mejor KAR: 44.95%, FAR 4.62% | Seleccionado para blind; generaliza mal (FAR 36.94%). |
| G. Mahalanobis diagonal | AUROC 0.6270, KAR 19.76% | No mejora la operación. |
| G. Mahalanobis shrinkage | AUROC 0.5403, KAR 16.58% | Empeora; descartado. |
| G. PCA-64 + Mahalanobis shrinkage | AUROC 0.6262, KAR 16.58% | No mejora la operación; descartado. |

No se continuó optimizando variantes que no superaron el baseline operativo. El resultado no justifica modificar el release de producción.

## 7. Calidad, vista y evidencia visible

Se calcularon señales de brillo, contraste, varianza Laplaciana, dimensión mínima y número de píxeles. La hipótesis pre-registrada para un quality gate requería que los falsos aceptados fueran consistentemente de peor calidad en los tres indicadores evaluados. No ocurrió; por ello **no se habilitó quality gate**. Un gate habría ocultado el problema rechazando indiscriminadamente sin evidencia de que explica el FAR.

No hay etiquetas fiables `DORSAL/LATERAL/FRONTAL/VENTRAL/PARTIAL` en los pools auditados. Tampoco hay un contrato de rasgos visibles estable. Se registran como evidencia ausente, no se infiere que un rasgo no visible esté ausente.

## 8. Métricas por tipo de UNKNOWN

La calibración incluye familia ausente, género ausente y especies del mismo género. El blind contiene especies del mismo género, misma familia y familia ausente. El fallo en `Rhinella marina` (79.5%) y `Dendropsophus labialis` (63.5%) muestra que los casos taxonómicamente cercanos son especialmente problemáticos, aunque esta evaluación aún no permite atribuir causalidad visual sin etiquetas de vista/morfología revisadas.

## 9. Estado de eliminación dinámica

Permanece **FAIL** del gate anterior: retirar `Dendrobates truncatus` del catálogo de ranking no retiró sus centroides del release Open Set. Su imagen fue reasignada y devolvió `ESPECIE_CONOCIDA`. Todo release futuro debe ejecutar, como una única operación versionada:

```text
remove species -> rebuild prototypes -> rebuild index -> rebuild/revalidate Open Set release -> assert catalog/index/prototype equality
```

El test debe exigir cero casos aceptados para la especie eliminada; que la especie no aparezca como Top-1 no es suficiente.

## 10. GO / NO-GO

**NO-GO.** Ningún método cumple simultáneamente FAR ≤5%, UDR ≥95%, KAR ≥80%, FRR ≤20% y AUROC ≥0.80. El mejor método calibrado logra FAR 4.62% pero KAR 44.95%; en Fase 23A blind su FAR sube a 36.94%.

## 11. Causa más probable y siguiente intervención justificada

La evidencia no indica un encoder corrupto. Indica tres límites separados:

1. El embedding BioCLIP actual tiene solapamiento Open Set relevante: d1 separa débilmente KNOWN/UNKNOWN.
2. Full-covariance Mahalanobis empeora esa señal; las variantes regularizadas no mejoran la operación.
3. La calibración de cuatro especies no cubre por completo la variación del blind, especialmente especies visualmente/taxonómicamente cercanas. El aumento de FAR de 4.62% a 36.94% lo demuestra.

La siguiente intervención técnicamente justificada no es mover el threshold ni añadir GEO/familia/género. Es ampliar la calibración independiente con UNKNOWN reales, especialmente del mismo género y condiciones de campo, con etiquetas de calidad/vista revisadas. Después debe repetirse el mismo protocolo y mantener Fase 23A como blind. Si con una calibración diversa el mejor método basado en el embedding sigue lejos de los objetivos, entonces quedará demostrada la insuficiencia del embedding para Open Set y será justificable evaluar un rejector aprendido, hard-negative mining o fine-tuning contrastivo en un protocolo nuevo.

> **Actualización de alcance (2026-09-14):** el responsable del producto autorizó evaluar ubicación, género y familia como evidencia contextual. La política, límites de cobertura y protocolo ciego se definen en `CONTEXTUAL_OPEN_SET_PROTOCOL.md`. Esta actualización no modifica ninguno de los resultados visuales de este reporte ni autoriza usar GEO o taxonomía real para aceptar una especie.
