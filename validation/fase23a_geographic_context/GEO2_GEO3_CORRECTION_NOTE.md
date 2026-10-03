# Correccion metodologica de GEO-2 y GEO-3

**Estado:** `CORRECTION_COMPLETE — correccion documental vigente`  
**Fecha:** 2026-09-14  
**Alcance:** trazabilidad metodologica de GEO-2/GEO-3 y su interpretacion
posterior en GEO-6

## Resumen ejecutivo

GEO-2 demostro que existe senal geografica util para complementar la senal
visual. Sin embargo, el AUROC historico de aproximadamente **0.701** no es una
estimacion honesta de rendimiento en inferencia real: para las observaciones
KNOWN, el calculo del prior geografico utilizo en parte la especie verdadera
(`ground_truth_species`) como insumo.

La especie verdadera no esta disponible cuando el sistema recibe una
fotografia nueva. Por tanto, ese uso constituye **oracle information** y
sobreestima la magnitud de la mejora.

La reproduccion metodologicamente honesta, usando la especie predicha
visualmente y no `ground_truth_species`, produce aproximadamente
**AUROC = 0.617**.

En adelante:

- **0.701** debe citarse solo como resultado historico/diagnostico afectado por
  oracle information.
- **0.617** es la referencia honesta reproducible para el esquema GEO-2/GEO-3
  sin ese oraculo.
- El numero recomendado para el prototipo actual es el resultado de GEO-6
  two-stage, que separa ranking y open set: `w_geo=0.3` para ranking,
  **Top-1 ~= 0.662** y **Open Set AUROC ~= 0.603**.

Estos valores corresponden a experimentos con objetivos distintos y no deben
compararse como si fueran exactamente la misma tarea.

## 1. Que se hizo originalmente

GEO-2 extendio el barrido de pesos del score combinado visual-geografico y
observo una mejora creciente del AUROC al aumentar `w_geo`. El punto
historico que se reporto como optimo operativo fue aproximadamente:

- score visual + prior geografico de especie;
- `w_geo ~= 0.9`;
- Open Set AUROC ~= **0.701**.

GEO-3 heredo `w_geo=0.9` y estudio cobertura geografica y curvas de umbral.
Su reporte reconfirmo aproximadamente **AUROC = 0.701476** para esa
configuracion.

Los resultados y artefactos originales se conservan intactos. Esta nota no
los reescribe ni los sustituye; corrige unicamente la interpretacion de lo
que pueden afirmar sobre produccion.

## 2. Que informacion privilegiada utilizaba el calculo

La reproduccion fiel del scoring de GEO-2 encontro que, para las filas KNOWN,
el componente geografico se construia usando la especie real de la
observacion, equivalente a:

```text
known_top1 = known_sci_name
```

En otras palabras, el prior `P(especie | zona)` se consultaba con
`ground_truth_species` en lugar de consultar el prior con la especie que el
modelo visual habia predicho.

La implementacion historica describia correctamente el procedimiento que
ejecutaba, pero no explicitaba que esa variable era informacion privilegiada
respecto de la inferencia real.

## 3. Por que es oracle information

La especie verdadera es precisamente la variable que el sistema intenta
identificar. Usarla para seleccionar el prior geografico equivale a entregar
al scoring una parte de la respuesta correcta antes de decidir:

1. el sistema recibe la fotografia;
2. BioCLIP produce una prediccion visual;
3. el sistema combina la prediccion con el contexto geografico.

Durante ese proceso no existe una etiqueta de verdad terreno para la imagen
nueva. La etiqueta puede existir posteriormente para evaluar el resultado,
pero no para calcular el score que decide la salida del sistema.

Por ello, el resultado con `ground_truth_species` es valido como diagnostico
de una cota o de una configuracion idealizada, pero no como medicion de
rendimiento de produccion.

## 4. Por que el oraculo no existe en inferencia real

En inferencia real:

- la fotografia puede ser de una especie conocida o desconocida;
- la especie real no se conoce de antemano;
- solo estan disponibles la imagen, el contexto geografico disponible y los
  artefactos persistidos del modelo;
- el prior debe condicionarse a una especie candidata generada por la senal
  visual, no a la etiqueta de verdad terreno.

La evaluacion puede usar `ground_truth_species` despues de producir la
prediccion para medir precision, AUROC u otras metricas. No puede usarla para
construir el score de la misma prediccion sin introducir leakage metodologico.

## 5. Efecto sobre AUROC

La reproduccion documentada en GEO-6 separo las dos condiciones:

| Condicion | Interpretacion | Open Set AUROC |
|---|---|---:|
| GEO-2/GEO-3 historico, `w_geo ~= 0.9` | Usa oracle information en KNOWN | **~= 0.701** |
| Reproduccion sin oraculo | Usa la especie predicha visualmente | **~= 0.617** |

La diferencia es de aproximadamente **0.085 AUROC** y se atribuye al uso de
la especie verdadera como insumo del prior geografico. Esto no demuestra que
la geografia carezca de valor; demuestra que la magnitud historica no era
replicable bajo las restricciones de inferencia real.

## 6. Que conclusiones de GEO-2 siguen siendo validas

Siguen siendo validas, con el alcance correcto:

1. **Existe senal geografica:** el contexto geografico puede aportar
   informacion adicional a la imagen.
2. El prior de especie es mas informativo que los priors taxonomicos mas
   gruesos ensayados posteriormente.
3. El peso geografico cambia el comportamiento del detector Open Set y puede
   mejorar la separacion en determinados subgrupos.
4. El barrido de pesos fue util para descubrir una hipotesis y orientar
   experimentos posteriores.
5. GEO-2 no debe describirse como un experimento que "nunca funciono".
   Demostro una senal real; lo que debe corregirse es la magnitud atribuida a
   esa senal.

La evidencia operacional posterior indica que la senal real es mas modesta
cuando el prior se consulta con la especie predicha y cuando se separan las
tareas de ranking y Open Set.

## 7. Que conclusiones deben corregirse

Deben corregirse las siguientes afirmaciones si se presentan como rendimiento
de produccion:

- No debe afirmarse que GEO-2 obtuvo **AUROC=0.701** sin calificarlo como
  resultado historico con oracle information.
- No debe presentarse `w_geo=0.9` como una configuracion directamente validada
  para inferencia real por el solo hecho de maximizar el barrido historico.
- No debe interpretarse la mejora completa de +0.128 frente al baseline
  visual como una ganancia disponible sin conocer la especie verdadera.
- No debe usarse GEO-2/GEO-3 como evidencia de que un unico score con peso
  geografico alto resuelve simultaneamente el ranking de candidatos y el
  rechazo Open Set.

## 8. Impacto sobre GEO-3 y GEO-5

### GEO-3

GEO-3 heredo el `w_geo=0.9` de GEO-2 y por ello hereda la limitacion del
oraculo en la interpretacion del AUROC. Sus analisis de cobertura y umbral
siguen siendo trazabilidad historica del comportamiento de ese procedimiento,
pero no deben presentarse como calibracion de produccion sin una reproduccion
sin oracle.

### GEO-5

GEO-5 confirmo la cobertura y el comportamiento del prior de especie sobre el
catalogo ampliado, pero su comparacion con el punto historico de GEO-2 debe
leerse con la misma salvedad: el numero ~=0.701 es diagnostico/oracular, no
una referencia de produccion.

La conclusion de GEO-4 permanece vigente: introducir genero y familia
nuevamente en el score produjo un efecto **HARMFUL**. Familia y genero deben
quedar como metadata, contexto y explicacion, no como componentes adicionales
del score de especie.

## 9. Relacion con GEO-6

GEO-6 hizo explicita la limitacion y separo dos objetivos:

1. **Ranking:** ordenar candidatos de especie con una mezcla moderada de
   visual y geografia.
2. **Open Set:** aplicar un gate separado para decidir si la observacion es
   conocida, no concluyente o no registrada.

La comparacion de GEO-6 registro, de forma aproximada:

- baseline visual: **AUROC ~= 0.573**;
- reproduccion GEO-2/GEO-3 sin oracle: **AUROC ~= 0.617**;
- GEO-6 two-stage, `w_geo=0.3` para ranking: **Top-1 ~= 0.662**;
- GEO-6 two-stage: **Open Set AUROC ~= 0.603**.

El resultado de dos etapas no pretende ser el mismo experimento que el
AUROC historico de GEO-2. La mejora de ranking y la mejora del gate son
objetivos diferentes, con scores diferentes, por lo que sus metricas no son
intercambiables.

## 10. Referencia metodologica vigente

La referencia que debe dejarse en documentacion nueva es:

| Referencia | Metrica |
|---|---:|
| Visual baseline | **AUROC ~= 0.573** |
| Geographic Open Set sin oracle | **AUROC ~= 0.617** |
| GEO-6 two-stage, ranking (`w_geo=0.3`) | **Top-1 ~= 0.662** |
| GEO-6 two-stage, Open Set | **AUROC ~= 0.603** |

Estos numeros pertenecen a experimentos con distintos objetivos y no deben
compararse como si fueran exactamente la misma tarea.

El numero que debe citarse en adelante para la contribucion geografica
reproducible sin informacion privilegiada es:

> **Geographic Open Set sin oracle: AUROC ~= 0.617.**

El **0.701** solo debe aparecer con la etiqueta:

> **Resultado historico/diagnostico GEO-2/GEO-3 afectado por oracle
> information; no es rendimiento de produccion.**

## 11. Arquitectura recomendada para el prototipo

La arquitectura vigente es:

```text
FOTO
  |
  v
BioCLIP
  |
  v
VISUAL SCORE + GEO_ESPECIE moderado
  |
  v
TOP-K CANDIDATOS
  |
  v
OPEN SET GATE
  |
  +--> CONOCIDA
  +--> NO CONCLUYENTE
  +--> NO REGISTRADA
```

Familia y genero se conservan como metadata, contexto y explicacion. No deben
reintroducirse en el score, porque GEO-4 mostro un efecto **HARMFUL**.

## 12. Artefactos consultados y preservacion

Esta nota se basa en la trazabilidad ya existente en:

- `validation/fase23a_geographic_context/GEO2_REPORT.md`
- `validation/fase23a_geographic_context/GEO3_REPORT.md`
- `validation/fase23a_geographic_context/GEO4_REPORT.md`
- `validation/fase23a_geographic_context/GEO5_REPORT.md`
- `validation/fase23a_geographic_context/GEO6_REPORT.md`
- `validation/fase23a_geographic_context/GEO6_OPENSET_RESULTS.json`

No se modificaron esos archivos ni ningun resultado, embedding, encoder,
dataset, script de Fase 23A, artefacto de GEO-2/GEO-3/GEO-4/GEO-5/GEO-6 o
componente de produccion.

## 13. Disposicion final y politica de cita

Esta correccion queda cerrada. Para evitar que la cifra oracular vuelva a
filtrarse a reportes, tableros o decisiones de producto, se adopta la siguiente
politica:

| Cifra | Estado de cita | Fuente de trazabilidad |
|---|---|---|
| `0.7014761031` | **Prohibida como metrica de produccion.** Solo puede citarse como `GEO2_GEO3_ORACLE_HISTORICAL`. | `GEO6_COMPARISON_SUMMARY.json`, configuracion `D_geo2_original_single_score_w0.9` |
| `~0.6167` | Referencia reproducible sin oracle para el score GEO-2/GEO-3 de alto peso. | Caveat de configuracion D en `GEO6_COMPARISON_SUMMARY.json` |
| `0.6031543856` | Resultado GEO-6 two-stage Open Set; no equivale al experimento GEO-2/GEO-3 de score unico. | `GEO6_COMPARISON_SUMMARY.json`, configuracion C |
| `0.6624749164` | Top-1 de ranking GEO-6 con `w_geo_rank=0.3`; no es AUROC Open Set. | `GEO6_COMPARISON_SUMMARY.json`, configuracion B/C |

Todo resultado nuevo que incorpore ubicacion, elevacion, genero o familia debe
llevar su propio manifiesto de entrenamiento/calibracion/blind. No puede
reutilizar `0.701` como baseline, ni tratar la especie, genero o familia real
de una imagen como entrada de inferencia.

La conclusion de GEO-4 se mantiene para su experimento concreto: agregar
priors taxonomicos al score de especie no demostro mejora. No impide evaluar
de forma separada la taxonomia como evidencia contextual agregada a partir de
los candidatos visuales, siempre que se calibre sin etiquetas reales y se
pruebe contra un blind independiente.

### Criterio de verificacion

Un lector puede auditar la correccion comprobando que la configuracion D de
GEO-6 declara `ORACLE_KNOWN_TOP1`, reporta AUROC `0.7014761031`, y contiene
su caveat explicito; la misma trazabilidad registra `~0.6167` al sustituir la
especie verdadera por la predicha. Por tanto, el primero no es reproducible
para una fotografia nueva y el segundo es la comparacion metodologicamente
valida.

