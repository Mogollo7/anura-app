# Fase 10 - Inventario de calibracion y referencia

## Estado

```text
STATUS = NO_INDEPENDENT_REFERENCE_AVAILABLE
INDEPENDENT_REFERENCE = false
REFERENCE_SIZE = 0
REFERENCE_SPECIES = []
```

## Conjuntos auditados

| Conjunto | Tamano | Uso metodologico |
|---|---:|---|
| TRAIN | 3,609 entradas de manifiesto; 3,260 en el split efectivo | `TRAIN_REFERENCE`; no independiente porque participo en entrenamiento y origino el indice kNN |
| VAL | 697 | `VALIDATION_REFERENCE`; participo en seleccion de checkpoint/early stopping |
| TEST/F3 | 766 | Evaluacion final KNOWN exclusivamente; no se uso para ajustar |
| F4 UNKNOWN | 56 | Evaluacion Open Set exclusivamente; no se uso para ajustar |
| Fuera de splits declarados | 7,531 imagenes | Candidatos no aceptados: pertenecen al mismo corpus limpio y no tienen declaracion de referencia independiente |

## Evidencia de independencia

Se auditaron `data cleaned`, `training/manifiesto.json`,
`evaluation/open_set_v1`, los embeddings existentes y la procedencia del
indice kNN. La evidencia detallada por imagen, incluyendo path, obs_id,
SHA-256, especie y split declarado, esta en
`calibration_inventory.json`.

No existe una particion declarada que sea simultaneamente:

- de las mismas 41 especies conocidas;
- fuera de TRAIN, VAL y TEST/F3;
- fuera de la seleccion del checkpoint;
- con procedencia independiente verificable;
- apta para estimar centroides/covarianzas de Mahalanobis.

Los 7,531 archivos fuera de los splits declarados no se pueden llamar
independientes solo por estar fuera del manifiesto. Forman parte del mismo
corpus limpio y carecen de declaracion de origen y uso que permita demostrar
independencia. El cache de embeddings existente es mixto y no contiene
metadatos de split suficientes para certificarlo.

## Uso de fuentes

```text
TRAIN: TRAIN_REFERENCE, no calibracion independiente
VAL: VALIDATION_REFERENCE, no calibracion independiente
TEST/F3: evaluacion final, prohibido para ajuste
F4: evaluacion UNKNOWN final, prohibido para ajuste
```

No se utilizaron GPS, prior, sonido, segmentacion, mascaras, imagenes
externas ni metadata artificial. No se ajusto Mahalanobis, no se eligio
regularizacion, no se selecciono threshold y no se evaluaron F3/F4 para
evitar fabricar una validacion out-of-sample.

## Referencia necesaria para repetir Fase 10

Se requiere una coleccion KNOWN retenida antes de la evaluacion, con
proveniencia documentada y separacion verificable por path, obs_id, SHA-256,
individual_id y perceptual hash cuando esten disponibles. Debe dividirse
explicitamente en:

```text
REFERENCE: estima centroides/covarianzas
CALIBRATION: fija regularizacion y threshold sin mirar F3/F4
FINAL TEST: F3 KNOWN
UNKNOWN TEST: F4 UNKNOWN
```

La Fase 10 actual queda como `NO_INDEPENDENT_REFERENCE_AVAILABLE`; AUROC,
AUPR, FAR, UDR, KAR, FNR, bootstrap y casos de evaluacion out-of-sample son
`NO_ESTIMABLES`.

## Integridad

Los hashes SHA-256 de las fuentes auditadas antes y despues estan registrados
en `calibration_inventory.json`. No se modificaron modelos, embeddings,
dataset, F3, F4, indice kNN, prior, pipeline movil ni produccion.
