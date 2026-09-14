---
title: "Ciclo de Vida del Modelo (MLOps)"
proyecto: Anura
tipo: proceso-desarrollo
estado: propuesta
tags: [anura, proceso, mlops, versionado, reproducibilidad]
---

# Ciclo de Vida del Modelo (MLOps)

[[Anura â€” àndice General]] · [[Proceso de Desarrollo â€” àndice]] · [[Escalabilidad]] · [[Experimentos y Resultados]] · [[Infraestructura]]

> [!abstract] Por qué esta nota existe
> En un proyecto de ML, el código no es el artefacto principal: lo son **el dataset, los pesos y los resultados**. Sin un proceso explícito, a los tres meses nadie sabe qué versión produjo el 87 % que aparece en el documento, ni cómo reproducirlo. Esto no es sofisticación de empresa; es lo que hace que un trabajo de grado sea defendible.

## 1. El ciclo completo

```
   DATOS â”€â”€â–¶ ANOTACIà“N â”€â”€â–¶ ENTRENAMIENTO â”€â”€â–¶ EVALUACIà“N â”€â”€â–¶ EMPAQUETADO â”€â”€â–¶ DESPLIEGUE
     â–²                                             â”‚                             â”‚
     â”‚                                             â–¼                             â–¼
     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ CURADURàA â—€â”€â”€ VALIDACIà“N EXPERTA â—€â”€â”€ OBSERVACIONES DE CAMPO â—€â”€â”€â”€â”˜
```

El bucle inferior es lo que hace a Anura un sistema vivo: las observaciones de campo validadas por expertos alimentan el dataset siguiente. Sin ese circuito, la app se congela en el día que se publicó.

## 2. Qué se versiona (y cómo)

| Artefacto | Herramienta | Formato de versión |
| --- | --- | --- |
| Código | Git | `commit` / etiqueta |
| Dataset | DVC o manifiesto versionado | `dataset_v3` |
| **Splits** | Listas de UUID en el repositorio | Congelados con el dataset |
| Anotaciones CVAT | Exportación periódica + Git LFS | `anotaciones_v2` |
| Pesos | Almacenamiento de artefactos | `modelo_vision_v1.2` |
| Configuración de entrenamiento | YAML en el repositorio | Junto al commit |
| Paquete regional | Almacenamiento + manifiesto | `antioquia_v5` |
| Resultados | [[Experimentos y Resultados]] + MLflow | `EXP-000` |

> [!important] Los splits son parte del dataset, no del código
> Guardar las listas de train/val/test como **identificadores versionados** es lo que permite comparar dos experimentos y afirmar que la diferencia viene del modelo y no de un reparto distinto. Es también la àºnica defensa real contra la fuga de información (riesgo D-1 en [[Riesgos del Proyecto]]).

## 3. Trazabilidad de una predicción

Toda predicción almacenada debe permitir responder, meses después: *¿con qué se generó esto?*

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

Sin estos campos es imposible distinguir "el modelo falló" de "esa observación se hizo con una versión antigua", y ambas cosas exigen respuestas opuestas.

## 4. Reproducibilidad

Requisitos mínimos para que un experimento sea reproducible:

- [ ] Semilla aleatoria fijada y registrada (y anotar que en GPU la reproducibilidad exacta no siempre es alcanzable â€” declararlo).
- [ ] Dependencias con versiones fijadas (`requirements.txt` con versiones exactas o entorno bloqueado).
- [ ] Configuración en fichero, no en argumentos escritos a mano en la terminal.
- [ ] Splits referenciados por versión.
- [ ] Comando de ejecución registrado junto al resultado.
- [ ] Idealmente, 3 ejecuciones con semillas distintas â†’ media ± desviación.

Una sola ejecución con una sola semilla no distingue una mejora real de la variabilidad del entrenamiento. Con datasets pequeños como este, esa variabilidad puede ser de varios puntos.

## 5. Del entrenamiento al dispositivo

```
1. Entrenar               PyTorch, GPU
2. Evaluar (FP32)         métricas de referencia â†’ [[Métricas Offline]]
3. Exportar               torch.export / ONNX
4. Cuantizar              INT8 con dataset de calibración (del train)
5. Reevaluar              MISMO test â†’ medir la degradación
6. Convertir              .tflite (LiteRT)
7. Probar en dispositivo  latencia, memoria, batería
8. Empaquetar             modelo + metadatos + versión
9. Publicar               APK o descarga de activos
```

El paso 5 no es opcional. Un modelo cuantizado que no se reevalàºa es un modelo cuyo rendimiento real se desconoce. Criterio de aceptación: Î” F1 â‰¤ 2 % ([[Optimización para Inferencia en Móvil]]).

## 6. Ritmo de reentrenamiento

| Disparador | Acción | Coste |
| --- | --- | --- |
| Especie nueva con datos validados | Alta en base vectorial | Horas |
| Acumulación de varias especies nuevas | Reentrenar cabezas | Horas |
| Muchas observaciones validadas nuevas | Reentrenar cabezas + reevaluar | 1 día |
| Deriva detectada en monitorización | Investigar antes de reentrenar | â€” |
| Cambio de backbone | Reentrenamiento completo + reindexado | Días |

> [!warning] No reentrenar por reflejo
> Cuando la precisión baja, la causa más frecuente **no** es que el modelo se haya quedado obsoleto, sino que ha cambiado el tipo de dato que le llega (localidad nueva, cámara distinta, otra estación del año). Reentrenar sin diagnosticar puede empeorar el modelo y consume el recurso más escaso del proyecto: el tiempo. Diagnosticar primero, con [[Matrices de Confusión]].

## 7. Aprendizaje continuo con datos de la comunidad

El circuito virtuoso tiene una trampa conocida que conviene anticipar:

```
Predicción del modelo â†’ el usuario la acepta â†’ entra al dataset â†’ reentrena
        â–²                                                             â”‚
        â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ el modelo confirma su propio sesgo â—€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

Si se reentrena con las predicciones que el propio modelo hizo y nadie corrigió, se refuerzan sus errores. Mitigaciones:

1. **Solo entran al dataset observaciones validadas por un experto**, no simplemente aceptadas por el usuario.
2. **Priorizar en la cola de revisión** las observaciones donde el modelo dudó o falló: son las que más información aportan.
3. **Mantener un conjunto de test fijo e independiente** que no se alimente nunca del circuito comunitario. Es la àºnica referencia estable a lo largo del tiempo.

## 8. Lista de comprobación antes de publicar una versión

- [ ] Métricas en test registradas y comparadas con la versión anterior
- [ ] Degradación por cuantización medida y dentro del umbral
- [ ] Latencia y memoria verificadas en el dispositivo de referencia
- [ ] Compatibilidad de dimensión de embedding con los paquetes vigentes
- [ ] Retrocompatibilidad de sincronización comprobada
- [ ] Versiones registradas en la trazabilidad
- [ ] Pesos y configuración respaldados
- [ ] [[Experimentos y Resultados]] actualizado



