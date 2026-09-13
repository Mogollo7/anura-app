# FASE 12.2 — CORRECCIÓN DE DUPLICADOS CROSS-SPLIT

**Fecha:** 2026-09-13  
**Estado:** COMPLETE

---

## RESUMEN EJECUTIVO

```
STATUS:                        READY_FOR_PHASE_13

DUPLICATES_DETECTED:           3
DUPLICATES_RESOLVED:           3
DUPLICATES_REMAINING:          0
AMBIGUOUS_CASES:               0

REFERENCE_SIZE:                798
CALIBRATION_SIZE:              192

REFERENCE_SPECIES:             10
CALIBRATION_SPECIES:           10

SHA256_CROSS_SPLIT_DUPLICATES: 0
CONTAMINATED_IN_REFERENCE:     0
CONTAMINATED_IN_CALIBRATION:   0

INDIVIDUAL_ID_AVAILABLE:       NO
OBS_ID_AVAILABLE:              NO
SEPARATION_STRATEGY:           SALTO_DE_5
INDIVIDUAL_INDEPENDENCE:       CONTROLLED_NOT_FORMALLY_VERIFIABLE
OBSERVATION_INDEPENDENCE:      NOT_FORMALLY_VERIFIABLE

F3_PROTECTED:                  YES
F4_PROTECTED:                  YES
MODEL_MODIFIED:                NO
DATASET_MODIFIED:              NO
PRODUCTION_MODIFIED:           NO
SOURCE_DATA_MODIFIED:          NO
MANIFESTS_UPDATED:             YES
```

---

## 1. ESTRATEGIA DE PARTICIÓN RECONSTRUIDA

La estrategia de split utilizada en Fase 12 fue **secuencial por índice numérico por especie**:

- **REFERENCE** recibe los archivos de índice numérico bajo (~primeros 80%)
- **CALIBRATION** recibe los archivos de índice numérico alto (~últimos 20%)

Evidencia empírica reconstruida desde los manifiestos:

| Especie | REFERENCE (rango) | CALIBRATION (rango) | Total |
|---------|-------------------|---------------------|-------|
| Pristimantis penelopus | _001 – _080 (80 archivos = 80.8%) | _081 – _099 (19 archivos = 19.2%) | 99 |
| Rhinella horribilis | _001 – _068 (68 archivos = 81.0%) | _069 – _084 (16 archivos = 19.0%) | 84 |

---

## 2. DUPLICADOS IDENTIFICADOS Y DECISIÓN

### Duplicate #1 — Pristimantis penelopus

```
SHA-256: f7a8ed86daf051e8e17c5ea7f2d3c1ae0d5f3dabd243395514a5d74864782697

REFERENCE (conservado):  Pristimantis_penelopus_076.jpg  [índice 76 → bloque REF 001-080]
CALIBRATION (eliminado): Pristimantis_penelopus_094.jpg  [índice 94 → bloque CAL 081-099]

Decisión: RESOLVED
Justificación: Integridad de la partición. _076 pertenece al bloque REFERENCE según la
estrategia secuencial. _094 pertenece al bloque CALIBRATION pero tiene SHA-256 idéntico
a _076. La duplicación cross-split se resuelve eliminando la copia de CALIBRATION.
```

### Duplicate #2 — Rhinella horribilis

```
SHA-256: f775bb3b95ef0951cb82b0912c9fa59b21f568aec796d351c5fd4266273b6af5

REFERENCE (conservado):  Rhinella_horribilis_003.jpg  [índice 3 → bloque REF 001-068]
CALIBRATION (eliminado): Rhinella_horribilis_084.jpg  [índice 84 → bloque CAL 069-084]

Decisión: RESOLVED
Justificación: Integridad de la partición. _003 pertenece al bloque REFERENCE. _084
pertenece al bloque CALIBRATION pero tiene SHA-256 idéntico a _003. La duplicación
cross-split se resuelve eliminando la copia de CALIBRATION.
```

### Duplicate #3 — Pristimantis penelopus

```
SHA-256: 0bffa53b8208ce86aa524e6da717f503f587f721da218d48f7c663eecac67fd5

REFERENCE (conservado):  Pristimantis_penelopus_030.jpg  [índice 30 → bloque REF 001-080]
CALIBRATION (eliminado): Pristimantis_penelopus_085.jpg  [índice 85 → bloque CAL 081-099]

Decisión: RESOLVED
Justificación: Integridad de la partición. _030 pertenece al bloque REFERENCE. _085
pertenece al bloque CALIBRATION pero tiene SHA-256 idéntico a _030. La duplicación
cross-split se resuelve eliminando la copia de CALIBRATION.
```

> **Nota metodológica:** La justificación se expresa como integridad de la partición, no
> como prueba de cuál archivo fue creado primero. La evidencia disponible establece qué
> bloque le corresponde a cada índice según la estrategia reconstruida; no establece
> cuál copia es el "original" físico.

---

## 3. ACCIONES REALIZADAS

| Acción | Archivo | Directorio | Resultado |
|--------|---------|------------|-----------|
| DELETE | Pristimantis_penelopus_094.jpg | CALIBRATION/…/Pristimantis penelopus/ | OK |
| DELETE | Pristimantis_penelopus_085.jpg | CALIBRATION/…/Pristimantis penelopus/ | OK |
| DELETE | Rhinella_horribilis_084.jpg | CALIBRATION/…/Rhinella horribilis/ | OK |
| NO ACTION | Pristimantis_penelopus_094.jpg | Fuente (data calibration/…) | INTACTO |
| NO ACTION | Pristimantis_penelopus_085.jpg | Fuente (data calibration/…) | INTACTO |
| NO ACTION | Rhinella_horribilis_084.jpg | Fuente (data calibration/…) | INTACTO |

> La colección fuente `D:\Anura\data calibration\*` permanece intacta para trazabilidad y auditoría.

---

## 4. VALIDACIONES

### 4.1 SHA-256 Cross-Split

| Métrica | Antes | Después |
|---------|-------|---------|
| SHA256_CROSS_SPLIT_DUPLICATES | 3 (FAIL) | **0 (PASS)** |
| REFERENCE unique hashes | 792 | 792 |
| CALIBRATION unique hashes | 193 | **190** |

> Los 6 duplicados internos de REFERENCE y 2 de CALIBRATION son heredados de la
> colección fuente. No son cross-split y no se modifican en esta fase.

### 4.2 Taxonomía

| Conjunto | Especies | Estado |
|----------|----------|--------|
| REFERENCE | 10 | ✓ PASS |
| CALIBRATION | 10 | ✓ PASS |

Distribución post-corrección por especie en CALIBRATION:

| Especie | Count |
|---------|-------|
| Dendrobates truncatus | 18 |
| Dendropsophus bogerti | 20 |
| Dendropsophus microcephalus | 20 |
| Hyloscirtus palmeri | 20 |
| Leucostethus fraterdanieli | 21 |
| Pristimantis acanthinus | 20 |
| Pristimantis paisa | 20 |
| Pristimantis penelopus | **17** (era 19) |
| Rhinella alata | 21 |
| Rhinella horribilis | **15** (era 16) |
| **TOTAL** | **192** |

### 4.3 Contaminación

| Métrica | Valor | Estado |
|---------|-------|--------|
| Imágenes contaminadas excluidas | 28 | ✓ PASS |
| CONTAMINATED_IN_REFERENCE | 0 | ✓ PASS |
| CONTAMINATED_IN_CALIBRATION | 0 | ✓ PASS |

### 4.4 Integridad SHA-256 (archivos conservados vs fuente)

| Archivo | Conjunto | SHA-256 coincide con fuente |
|---------|----------|---------------------------|
| Pristimantis_penelopus_076.jpg | REFERENCE | ✓ MATCH |
| Rhinella_horribilis_003.jpg | REFERENCE | ✓ MATCH |
| Pristimantis_penelopus_030.jpg | REFERENCE | ✓ MATCH |

---

## 5. MANIFIESTOS ACTUALIZADOS

| Archivo | Registros | Estado |
|---------|-----------|--------|
| CALIBRATION_manifest.json | 192 | ✓ Regenerado |
| CALIBRATION_manifest.csv | 192 | ✓ Regenerado |
| REFERENCE_manifest.json | 798 | ✓ Sin modificación |
| REFERENCE_manifest.csv | 798 | ✓ Sin modificación |

---

## 6. ARTEFACTOS PROTEGIDOS

| Artefacto | Estado |
|-----------|--------|
| D:\Anura\data cleaned | UNCHANGED ✓ |
| Embeddings F3 | UNCHANGED ✓ |
| Embeddings F4 | UNCHANGED ✓ |
| TRAIN | UNCHANGED ✓ |
| VAL | UNCHANGED ✓ |
| Modelo BioCLIP | UNCHANGED ✓ |
| Encoder ONNX | UNCHANGED ✓ |
| Índice kNN | UNCHANGED ✓ |
| Prior geográfico | UNCHANGED ✓ |
| REFERENCE (798 archivos) | UNCHANGED ✓ |
| Fuente D:\Anura\data calibration\ | UNCHANGED ✓ |

---

## 7. NOTAS METODOLÓGICAS

### Sobre independencia individual y de observaciones

La eliminación de los 3 duplicados SHA-256 elimina la duplicación cross-split confirmada.
**No implica independencia formal de individuos ni de observaciones.**

La colección no dispone de `individual_id` ni `obs_id`. La estrategia de separación
secuencial reduce el riesgo de dependencia, pero no constituye prueba formal de
independencia:

```
INDIVIDUAL_ID_AVAILABLE:    NO
OBS_ID_AVAILABLE:           NO
INDIVIDUAL_INDEPENDENCE:    CONTROLLED_NOT_FORMALLY_VERIFIABLE
OBSERVATION_INDEPENDENCE:   NOT_FORMALLY_VERIFIABLE
```

### Sobre duplicados internos remanentes

Se reportaron en Fase 12.1: 6 duplicados internos en REFERENCE y 2 en CALIBRATION,
todos heredados de la colección fuente. Estos duplicados son intra-set y no constituyen
contaminación cross-split. No se modifican en esta fase.

### Distinción cross-split vs contaminación de proyecto

- **Cross-split duplicate:** misma imagen presente en REFERENCE y CALIBRATION.
  → Resuelto: SHA256_CROSS_SPLIT_DUPLICATES = 0
- **Contaminación del proyecto:** imágenes del dataset/proyecto previamente excluidas.
  → Permanece: CONTAMINATED_IN_REFERENCE = 0, CONTAMINATED_IN_CALIBRATION = 0

---

## 8. NOTAS PARA FASE 13

1. **Alcance taxonómico:** REFERENCE/CALIBRATION contienen 10 de las 41 especies
   visuales del sistema. Fase 13 debe analizar explícitamente cómo tratar las 31
   especies no representadas antes de seleccionar el método final de rechazo.

2. **Ceguera de F3/F4:** Los conjuntos F3 KNOWN y F4 UNKNOWN deben permanecer ciegos.
   No deben usarse para seleccionar regularización, método de covarianza, umbral,
   pesos, hiperparámetros ni modelo de rechazo. Deben reservarse para evaluación final.

3. **Resultado in-sample de Fase 9:** El resultado Mahalanobis AUROC = 1.000000 de
   Fase 9 fue obtenido in-sample y no debe usarse como evidencia de rendimiento
   generalizable. Fase 13 debe producir una estimación out-of-sample.

4. **Congelamiento:** REFERENCE y CALIBRATION quedan congelados al cierre de Fase 12.2.
   No deben modificarse durante Fase 13 salvo auditoría de integridad con error
   objetivo documentado y explícito.

---

## 9. CRITERIOS DE FINALIZACIÓN — EVALUACIÓN

| Criterio | Valor requerido | Valor obtenido | Estado |
|----------|----------------|----------------|--------|
| SHA256_CROSS_SPLIT_DUPLICATES | 0 | 0 | ✓ PASS |
| REFERENCE_SPECIES | 10 | 10 | ✓ PASS |
| CALIBRATION_SPECIES | 10 | 10 | ✓ PASS |
| CONTAMINATED_IN_REFERENCE | 0 | 0 | ✓ PASS |
| CONTAMINATED_IN_CALIBRATION | 0 | 0 | ✓ PASS |
| REFERENCE_SIZE | 798 | 798 | ✓ PASS |
| CALIBRATION_SIZE | 192 | 192 | ✓ PASS |
| MANIFESTS_UPDATED | YES | YES | ✓ PASS |
| SOURCE_DATA_MODIFIED | NO | NO | ✓ PASS |
| F3_PROTECTED | YES | YES | ✓ PASS |
| F4_PROTECTED | YES | YES | ✓ PASS |
| MODEL_MODIFIED | NO | NO | ✓ PASS |
| DATASET_MODIFIED | NO | NO | ✓ PASS |
| PRODUCTION_MODIFIED | NO | NO | ✓ PASS |

**Todos los criterios satisfechos.**

```
STATUS: READY_FOR_PHASE_13
```

---

## ARCHIVOS GENERADOS

- `FASE12_2_DUPLICATE_CORRECTION.md` (este archivo)
- `FASE12_2_DUPLICATE_CORRECTION.json` (reporte máquina-legible)
- `CALIBRATION_manifest.json` (regenerado — 192 registros)
- `CALIBRATION_manifest.csv` (regenerado — 192 registros)
