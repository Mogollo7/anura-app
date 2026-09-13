# Protocolo reproducible para una futura referencia independiente

## Objetivo

Construir una referencia KNOWN y un conjunto de CALIBRATION independientes del entrenamiento y de las evaluaciones F3/F4, permitiendo validar posteriormente el rechazo Open Set sin contaminación metodológica.

### 1. Congelamiento del estado actual

Antes de incorporar cualquier nueva imagen:

* Congelar y calcular SHA-256 de:

  * modelo/checkpoint;
  * encoder ONNX;
  * embeddings existentes;
  * dataset actual;
  * manifiestos;
  * splits TRAIN/VAL/TEST;
  * F3;
  * F4;
  * índice kNN;
  * prior geográfico;
  * scripts críticos de evaluación.
* Registrar versiones, fechas y hashes en un manifiesto inmutable.
* A partir de este momento, F3 y F4 quedan protegidos.

### 2. Recolección independiente

Las nuevas imágenes deben proceder de una colección nueva.

No reutilizar ni descargar nuevamente imágenes del corpus actual.

Por cada imagen registrar:

* `obs_id`
* `individual_id`
* `source`
* `date`
* `location`
* `coordinates`
* `author`
* `license`
* `URL`
* `timestamp`
* `filename`
* `SHA-256`
* `perceptual_hash`

La unidad de independencia debe ser la **observación/individuo**, no simplemente el archivo.

### 3. Procedencia y licencia

Para cada imagen:

* verificar autorización/licencia;
* conservar evidencia de procedencia;
* conservar información de descarga;
* conservar el manifiesto original;
* almacenar los datos en una estructura versionada.

Una imagen cuya procedencia no pueda demostrarse no puede considerarse independiente.

Clasificación:

```text
A = independiente verificable
B = potencialmente independiente, no verificable
C = contaminada/no utilizable
D = procedencia insuficiente
```

Solamente las imágenes A pueden entrar en la referencia independiente principal.

### 4. Separación de conjuntos

Construir conjuntos físicamente separados:

```text
REFERENCE
    ↓
estimación de distribución
centroides + covarianzas

CALIBRATION
    ↓
regularización + threshold

F3 KNOWN
    ↓
evaluación final

F4 UNKNOWN
    ↓
evaluación Open Set final
```

REFERENCE y CALIBRATION deben ser distintos.

Ninguna imagen de estos conjuntos puede pertenecer a:

* TRAIN;
* VAL;
* F3;
* F4;
* índice kNN existente;
* otra colección utilizada para seleccionar el checkpoint.

La contaminación debe comprobarse mediante:

* path;
* `obs_id`;
* `individual_id`;
* SHA-256;
* perceptual hash.

### 5. Tamaño recomendado

Como objetivo inicial:

**REFERENCE**

* 10–20 imágenes independientes por especie.

**CALIBRATION**

* 5–10 imágenes independientes por especie.

Para 41 especies:

```text
REFERENCE:   410–820 imágenes
CALIBRATION: 205–410 imágenes
```

Estos números son objetivos, no requisitos artificiales.

Para especies raras:

* no utilizar duplicados;
* no reutilizar individuos;
* no completar artificialmente el número;
* declarar explícitamente la cobertura insuficiente.

### 6. Congelamiento de Reference

Una vez completado el conjunto REFERENCE:

1. congelarlo;
2. generar SHA-256;
3. generar manifiesto;
4. ejecutar auditoría de contaminación;
5. documentar número de especies e imágenes;
6. no utilizarlo posteriormente para seleccionar thresholds.

REFERENCE se utilizará exclusivamente para estimar la distribución de las clases.

### 7. Calibración

La CALIBRATION debe utilizarse exclusivamente para seleccionar:

* método de covariance;
* regularización;
* threshold;
* cualquier otro hiperparámetro estrictamente relacionado con rechazo Open Set.

Las decisiones deben tomarse sin consultar el rendimiento final de F3/F4.

### 8. Evaluación final

Una vez congelados:

```text
REFERENCE
CALIBRATION
regularización
threshold
```

se ejecutará:

```text
F3 KNOWN → evaluación cerrada
F4 UNKNOWN → evaluación Open Set
```

F3 y F4 deben tratarse como evaluación final ciega para cualquier decisión metodológica.

No modificar parámetros después de observar sus resultados.

Si se desea realizar otra iteración, debe comenzar un nuevo experimento con un protocolo independiente y quedar documentada.

### 9. Auditoría de contaminación

Ejecutar una auditoría:

**ANTES**

* antes de aceptar imágenes en REFERENCE/CALIBRATION.

**DESPUÉS**

* después de congelar ambos conjuntos.

Comparar:

```text
path
obs_id
individual_id
SHA-256
perceptual hash
```

contra todo el material previamente utilizado.

Generar:

* listado de coincidencias;
* listado de posibles coincidencias;
* imágenes excluidas;
* imágenes aceptadas;
* razones de exclusión;
* hashes;
* manifiesto final.

### 10. Regla de procedencia

Si la procedencia no puede demostrarse:

```text
NO PROMOVER A REFERENCE
NO PROMOVER A CALIBRATION
```

La incertidumbre de procedencia debe prevalecer sobre la necesidad de completar el número de imágenes.

### 11. Inmutabilidad

Una vez congelados REFERENCE y CALIBRATION:

* no reemplazar imágenes silenciosamente;
* no modificar metadatos sin versionado;
* no eliminar registros sin dejar evidencia;
* no recalcular hashes y sobrescribir los anteriores;
* conservar los manifiestos originales.

Cualquier cambio debe producir una nueva versión documentada.

### 12. Criterio de finalización

La fase de recolección no se considera completa solamente por alcanzar un número de imágenes.

Debe cumplirse:

```text
PROCEDENCIA VERIFICABLE
        +
INDEPENDENCIA VERIFICABLE
        +
COBERTURA DOCUMENTADA
        +
CONTAMINACIÓN = 0
        +
REFERENCE CONGELADA
        +
CALIBRATION SEPARADA
```

Si alguna especie no tiene cobertura suficiente:

```text
COVERAGE_INSUFFICIENT
```

y se reporta explícitamente.

Nunca completar la cobertura mediante imágenes potencialmente contaminadas.

## Regla fundamental

> Es preferible una referencia pequeña pero demostrablemente independiente que una referencia grande cuya independencia no pueda demostrarse.

Hasta cumplir este protocolo, el resultado de Mahalanobis de Fase 9 (`AUROC = 1.0`) debe seguir considerándose **in-sample y no válido como evidencia de rendimiento productivo**.
