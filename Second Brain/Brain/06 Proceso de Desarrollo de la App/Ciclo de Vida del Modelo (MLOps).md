---
title: "Ciclo de Vida del Modelo (MLOps)"
proyecto: Anura
tipo: proceso-desarrollo
estado: propuesta
tags: [anura, proceso, mlops, versionado, reproducibilidad]
---

# Ciclo de Vida del Modelo (MLOps)

[[Anura â€” Ãndice General]] Â· [[Proceso de Desarrollo â€” Ãndice]] Â· [[Escalabilidad]] Â· [[Experimentos y Resultados]] Â· [[Infraestructura]]

> [!abstract] Por quÃ© esta nota existe
> En un proyecto de ML, el cÃ³digo no es el artefacto principal: lo son **el dataset, los pesos y los resultados**. Sin un proceso explÃ­cito, a los tres meses nadie sabe quÃ© versiÃ³n produjo el 87 % que aparece en el documento, ni cÃ³mo reproducirlo. Esto no es sofisticaciÃ³n de empresa; es lo que hace que un trabajo de grado sea defendible.

## 1. El ciclo completo

```
   DATOS â”€â”€â–¶ ANOTACIÃ“N â”€â”€â–¶ ENTRENAMIENTO â”€â”€â–¶ EVALUACIÃ“N â”€â”€â–¶ EMPAQUETADO â”€â”€â–¶ DESPLIEGUE
     â–²                                             â”‚                             â”‚
     â”‚                                             â–¼                             â–¼
     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ CURADURÃA â—€â”€â”€ VALIDACIÃ“N EXPERTA â—€â”€â”€ OBSERVACIONES DE CAMPO â—€â”€â”€â”€â”˜
```

El bucle inferior es lo que hace a Anura un sistema vivo: las observaciones de campo validadas por expertos alimentan el dataset siguiente. Sin ese circuito, la app se congela en el dÃ­a que se publicÃ³.

## 2. QuÃ© se versiona (y cÃ³mo)

| Artefacto | Herramienta | Formato de versiÃ³n |
| --- | --- | --- |
| CÃ³digo | Git | `commit` / etiqueta |
| Dataset | DVC o manifiesto versionado | `dataset_v3` |
| **Splits** | Listas de UUID en el repositorio | Congelados con el dataset |
| Anotaciones CVAT | ExportaciÃ³n periÃ³dica + Git LFS | `anotaciones_v2` |
| Pesos | Almacenamiento de artefactos | `modelo_vision_v1.2` |
| ConfiguraciÃ³n de entrenamiento | YAML en el repositorio | Junto al commit |
| Paquete regional | Almacenamiento + manifiesto | `antioquia_v5` |
| Resultados | [[Experimentos y Resultados]] + MLflow | `EXP-000` |

> [!important] Los splits son parte del dataset, no del cÃ³digo
> Guardar las listas de train/val/test como **identificadores versionados** es lo que permite comparar dos experimentos y afirmar que la diferencia viene del modelo y no de un reparto distinto. Es tambiÃ©n la Ãºnica defensa real contra la fuga de informaciÃ³n (riesgo D-1 en [[Riesgos del Proyecto]]).

## 3. Trazabilidad de una predicciÃ³n

Toda predicciÃ³n almacenada debe permitir responder, meses despuÃ©s: *Â¿con quÃ© se generÃ³ esto?*

```json
{
  "observacion_id": "uuid",
  "prediccion": { "familia": "...", "genero": "...", "especie": "...", "confianza": 0.87 },
  "version_modelo_vision": "1.2.0",
  "version_modelo_segmentacion": "1.0.3",
  "version_dataset": "3",
  "version_paquete": "antioquia_v5",
  "origen_inferencia": "dispositivo",
  "cuantizacion": "int8",
  "timestamp": "..."
}
```

Sin estos campos es imposible distinguir "el modelo fallÃ³" de "esa observaciÃ³n se hizo con una versiÃ³n antigua", y ambas cosas exigen respuestas opuestas.

## 4. Reproducibilidad

Requisitos mÃ­nimos para que un experimento sea reproducible:

- [ ] Semilla aleatoria fijada y registrada (y anotar que en GPU la reproducibilidad exacta no siempre es alcanzable â€” declararlo).
- [ ] Dependencias con versiones fijadas (`requirements.txt` con versiones exactas o entorno bloqueado).
- [ ] ConfiguraciÃ³n en fichero, no en argumentos escritos a mano en la terminal.
- [ ] Splits referenciados por versiÃ³n.
- [ ] Comando de ejecuciÃ³n registrado junto al resultado.
- [ ] Idealmente, 3 ejecuciones con semillas distintas â†’ media Â± desviaciÃ³n.

Una sola ejecuciÃ³n con una sola semilla no distingue una mejora real de la variabilidad del entrenamiento. Con datasets pequeÃ±os como este, esa variabilidad puede ser de varios puntos.

## 5. Del entrenamiento al dispositivo

```
1. Entrenar               PyTorch, GPU
2. Evaluar (FP32)         mÃ©tricas de referencia â†’ [[MÃ©tricas Offline]]
3. Exportar               torch.export / ONNX
4. Cuantizar              INT8 con dataset de calibraciÃ³n (del train)
5. Reevaluar              MISMO test â†’ medir la degradaciÃ³n
6. Convertir              .tflite (LiteRT)
7. Probar en dispositivo  latencia, memoria, baterÃ­a
8. Empaquetar             modelo + metadatos + versiÃ³n
9. Publicar               APK o descarga de activos
```

El paso 5 no es opcional. Un modelo cuantizado que no se reevalÃºa es un modelo cuyo rendimiento real se desconoce. Criterio de aceptaciÃ³n: Î” F1 â‰¤ 2 % ([[OptimizaciÃ³n para Inferencia en MÃ³vil]]).

## 6. Ritmo de reentrenamiento

| Disparador | AcciÃ³n | Coste |
| --- | --- | --- |
| Especie nueva con datos validados | Alta en base vectorial | Horas |
| AcumulaciÃ³n de varias especies nuevas | Reentrenar cabezas | Horas |
| Muchas observaciones validadas nuevas | Reentrenar cabezas + reevaluar | 1 dÃ­a |
| Deriva detectada en monitorizaciÃ³n | Investigar antes de reentrenar | â€” |
| Cambio de backbone | Reentrenamiento completo + reindexado | DÃ­as |

> [!warning] No reentrenar por reflejo
> Cuando la precisiÃ³n baja, la causa mÃ¡s frecuente **no** es que el modelo se haya quedado obsoleto, sino que ha cambiado el tipo de dato que le llega (localidad nueva, cÃ¡mara distinta, otra estaciÃ³n del aÃ±o). Reentrenar sin diagnosticar puede empeorar el modelo y consume el recurso mÃ¡s escaso del proyecto: el tiempo. Diagnosticar primero, con [[Matrices de ConfusiÃ³n]].

## 7. Aprendizaje continuo con datos de la comunidad

El circuito virtuoso tiene una trampa conocida que conviene anticipar:

```
PredicciÃ³n del modelo â†’ el usuario la acepta â†’ entra al dataset â†’ reentrena
        â–²                                                             â”‚
        â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ el modelo confirma su propio sesgo â—€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

Si se reentrena con las predicciones que el propio modelo hizo y nadie corrigiÃ³, se refuerzan sus errores. Mitigaciones:

1. **Solo entran al dataset observaciones validadas por un experto**, no simplemente aceptadas por el usuario.
2. **Priorizar en la cola de revisiÃ³n** las observaciones donde el modelo dudÃ³ o fallÃ³: son las que mÃ¡s informaciÃ³n aportan.
3. **Mantener un conjunto de test fijo e independiente** que no se alimente nunca del circuito comunitario. Es la Ãºnica referencia estable a lo largo del tiempo.

## 8. Lista de comprobaciÃ³n antes de publicar una versiÃ³n

- [ ] MÃ©tricas en test registradas y comparadas con la versiÃ³n anterior
- [ ] DegradaciÃ³n por cuantizaciÃ³n medida y dentro del umbral
- [ ] Latencia y memoria verificadas en el dispositivo de referencia
- [ ] Compatibilidad de dimensiÃ³n de embedding con los paquetes vigentes
- [ ] Retrocompatibilidad de sincronizaciÃ³n comprobada
- [ ] Versiones registradas en la trazabilidad
- [ ] Pesos y configuraciÃ³n respaldados
- [ ] [[Experimentos y Resultados]] actualizado



