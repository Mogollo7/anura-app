# FASE 12.1 — AUDITORÍA FINAL DE INDEPENDENCIA

**Fecha:** 2026-09-13  
**Estado:** COMPLETE  

---

## RESUMEN EJECUTIVO

La auditoría de independencia de los conjuntos REFERENCE (798 imágenes) y CALIBRATION (195 imágenes) revela:

1. **SHA-256 Duplicates (Cross-Split):** 3 (CRÍTICO)
2. **Individual ID Verification:** NOT VERIFIABLE (no metadata)
3. **Observation ID Verification:** NOT VERIFIABLE (no metadata)
4. **Perceptual Hash Status:** NOT AVAILABLE (sin herramientas)
5. **Contaminated Images Excluded:** ✓ PASS (28 correctamente excluidas)
6. **Taxonomic Coherence:** ✓ PASS (10 especies en ambos conjuntos)

**CONCLUSIÓN:** Los conjuntos NO son completamente independientes debido a 3 imágenes duplicadas (SHA-256 idénticas) presentes en ambos.

---

## 1. AUDITORÍA DE METADATOS

### Campos Disponibles en Manifiestos

```
- FileName
- OriginalPath  
- Species
- Familia
- Genero
- SHA256
- Dataset
```

### Campos Buscados y NO Encontrados

```
✗ individual_id
✗ individuo  
✗ specimen_id
✗ animal_id
✗ obs_id
✗ observation_id
✗ source
✗ collection_code
✗ collector
✗ date
```

**RESULTADO:** Los manifiestos NO contienen identificadores formales de individuo ni de observación.

---

## 2. AUDITORÍA DE INDIVIDUOS

### Estrategia de Separación Utilizada

- **Método:** Separación por porcentaje (80/20) dentro de cada especie
- **Criterio secundario:** "Salto de aproximadamente 5 imágenes" (según nota del usuario)
- **Resultado esperado:** Imágenes consecutivas o del mismo individuo separadas entre REFERENCE y CALIBRATION

### Verificación de INDIVIDUAL_OVERLAP

**INDIVIDUAL_ID_AVAILABLE:** NO

**INDIVIDUAL_INDEPENDENCE_STATUS:** NOT_VERIFIABLE

**Razón:** Sin metadata de `individual_id` o identificador equivalente, la independencia de individuos no puede demostrarse formalmente. La separación fue diseñada para *reducir* el riesgo de incluir el mismo individuo en ambos conjuntos, pero no proporciona prueba.

**Hallazgo crítico:** Se encontraron 3 imágenes SHA-256 duplicadas entre REFERENCE y CALIBRATION, indicando que la misma fotografía física de un mismo individuo está presente en ambos conjuntos.

---

## 3. AUDITORÍA DE OBSERVACIONES

### Búsqueda de obs_id / observation_id

**OBS_ID_AVAILABLE:** NO

**OBSERVATION_INDEPENDENCE_STATUS:** NOT_VERIFIABLE

**Razón:** Sin metadata de `obs_id`, `observation_id` o similar, no se puede verificar si imágenes de la misma observación/evento están separadas entre REFERENCE y CALIBRATION.

---

## 4. AUDITORÍA DE DUPLICADOS SHA-256

### Análisis Cross-Split (REFERENCE vs CALIBRATION)

| Métrica | Valor |
|---------|-------|
| REFERENCE SHA-256 Hashes | 792 |
| CALIBRATION SHA-256 Hashes | 193 |
| **SHA-256 Cross-Split Duplicates** | **3** |
| **Status** | **FAIL** |

### Duplicados Identificados

#### Duplicate #1
```
SHA-256: f7a8ed86daf051e8e17c5ea7f2d3c1ae0d5f3dabd243395514a5d74864782697
REFERENCE:  Pristimantis_penelopus_076.jpg
            Craugastoridae\Pristimantis\Pristimantis penelopus\
CALIBRATION: Pristimantis_penelopus_094.jpg
             Craugastoridae\Pristimantis\Pristimantis penelopus\
Especie: Pristimantis penelopus
```

#### Duplicate #2
```
SHA-256: f775bb3b95ef0951cb82b0912c9fa59b21f568aec796d351c5fd4266273b6af5
REFERENCE:  Rhinella_horribilis_003.jpg
            Bufonidae\Rhinella\Rhinella horribilis\
CALIBRATION: Rhinella_horribilis_084.jpg
             Bufonidae\Rhinella\Rhinella horribilis\
Especie: Rhinella horribilis
```

#### Duplicate #3
```
SHA-256: 0bffa53b8208ce86aa524e6da717f503f587f721da218d48f7c663eecac67fd5
REFERENCE:  Pristimantis_penelopus_030.jpg
            Craugastoridae\Pristimantis\Pristimantis penelopus\
CALIBRATION: Pristimantis_penelopus_085.jpg
             Craugastoridae\Pristimantis\Pristimantis penelopus\
Especie: Pristimantis penelopus
```

### Análisis Interno

| Conjunto | Única Files | Duplicates | Status |
|----------|------------|-----------|--------|
| REFERENCE | 792 | 6 | ✗ DUPLICADOS INTERNOS |
| CALIBRATION | 193 | 2 | ✗ DUPLICADOS INTERNOS |

**Nota:** Los duplicados internos provienen de las imágenes originales en `D:\Anura\data calibration`. Las imágenes fueron copiadas tal como estaban, incluyendo duplicados.

---

## 5. AUDITORÍA PERCEPTUAL (PHASH, DHASH, AHASH)

### Herramientas Disponibles

```
Python3: NO
PIL/Pillow: NO
imagehash: NO
ImageMagick: NO
```

**PERCEPTUAL_HASH_STATUS: NOT_AVAILABLE**

No se ejecutó análisis perceptual porque no hay herramientas disponibles en el entorno. Se recomienda ejecutar este análisis en una fase posterior si es necesario.

---

## 6. AUDITORÍA DE IMÁGENES CONTAMINADAS

### Verificación de Exclusión

| Métrica | Valor |
|---------|-------|
| Contaminated Images in Original Set | 28 |
| Contaminated in REFERENCE | 0 |
| Contaminated in CALIBRATION | 0 |
| **Status** | **✓ PASS** |

### Distribución por Especie

| Especie | Count |
|---------|-------|
| Dendrobates truncatus | 15 |
| Dendropsophus bogerti | 4 |
| Dendropsophus microcephalus | 6 |
| Rhinella alata | 3 |
| **TOTAL** | **28** |

**Conclusión:** Las 28 imágenes contaminadas fueron correctamente identificadas y excluidas de REFERENCE y CALIBRATION.

---

## 7. VALIDACIÓN TAXONÓMICA

### Coherencia de Estructura Familia → Género → Especie

| Métrica | REFERENCE | CALIBRATION |
|---------|-----------|-------------|
| Grupos Taxonómicos | 10 | 10 |
| Especies Únicas | 10 | 10 |
| Grupos Faltantes | 0 | 0 |
| **Status** | **✓ PASS** | **✓ PASS** |

### Especies Representadas

1. ✓ Dendrobates truncatus (Dendrobatidae)
2. ✓ Dendropsophus bogerti (Hylidae)
3. ✓ Dendropsophus microcephalus (Hylidae)
4. ✓ Hyloscirtus palmeri (Hylidae)
5. ✓ Leucostethus fraterdanieli (Dendrobatidae)
6. ✓ Pristimantis acanthinus (Craugastoridae)
7. ✓ Pristimantis paisa (Craugastoridae)
8. ✓ Pristimantis penelopus (Craugastoridae)
9. ✓ Rhinella alata (Bufonidae)
10. ✓ Rhinella horribilis (Bufonidae)

**Conclusión:** Todas las 10 especies están representadas en ambos REFERENCE y CALIBRATION. La coherencia taxonómica es válida.

---

## 8. ARTEFACTOS PROTEGIDOS (VERIFICACIÓN)

| Artefacto | Status |
|-----------|--------|
| BioCLIP Model | UNCHANGED ✓ |
| encoder_anura_fp16.onnx | UNCHANGED ✓ |
| Embeddings F3 | UNCHANGED ✓ |
| Embeddings F4 | UNCHANGED ✓ |
| kNN Index | UNCHANGED ✓ |
| Geographic Prior | UNCHANGED ✓ |
| Training Dataset (TRAIN) | UNCHANGED ✓ |
| Validation Dataset (VAL) | UNCHANGED ✓ |

**Conclusión:** Ningún artefacto fue modificado durante esta auditoría.

---

## 9. HALLAZGOS PRINCIPALES

### Positivos (✓)
1. Las 28 imágenes contaminadas fueron correctamente excluidas
2. Todas las 10 especies están representadas en ambos conjuntos
3. Taxonomía coherente y válida
4. SHA-256 de copias coincide con originales (integridad verificada)
5. No hay interferencia con artefactos de producción

### Críticos (✗)
1. **3 duplicados SHA-256 entre REFERENCE y CALIBRATION** - misma imagen física en ambos conjuntos
2. **Sin metadata formal de individual_id** - imposible verificar independencia de individuos
3. **Sin metadata formal de obs_id** - imposible verificar independencia de observaciones
4. **Duplicados internos detectados** - 6 en REFERENCE, 2 en CALIBRATION (heredados de originales)

---

## 10. INTERPRETACIÓN DE RESULTADOS

### Individual Independence

```
INDIVIDUAL_ID: NOT AVAILABLE
INDIVIDUAL_OVERLAP: NOT VERIFIABLE (métrica calculada: 0, pero no demostrable)
INDIVIDUAL_INDEPENDENCE_RISK: HIGH

Razón: La separación fue hecha sin metadata de individuo. 
Los 3 duplicados SHA-256 demuestran que al menos 3 imágenes del mismo individuo 
están en ambos conjuntos.
```

### Observation Independence

```
OBS_ID: NOT AVAILABLE
OBSERVATION_OVERLAP: NOT VERIFIABLE
OBSERVATION_INDEPENDENCE_RISK: HIGH

Razón: Sin obs_id, no se puede verificar si múltiples imágenes de la misma 
observación fueron correctamente separadas.
```

### Separation Strategy Effectiveness

```
SEPARATION_STRATEGY: 80/20 percentile split per species + "salto de 5"
STRATEGY_STATUS: DESIGNED BUT NOT VERIFIED

Hallazgo: 3 imágenes SHA-256 idénticas violan el principio de independencia,
indicando que la estrategia no fue completamente efectiva.
```

---

## 11. RECOMENDACIONES

### Para Fase 13 (Mahalanobis Validation)

1. **Awarness:** Proceder con conocimiento de que existen 3 duplicados SHA-256 entre REFERENCE y CALIBRATION
2. **Impact Analysis:** Evaluar cómo afectan estos 3 duplicados a:
   - Centroides por especie
   - Covarianzas
   - Thresholds F3/F4
3. **Alternative:** Considerar remover los 3 duplicados y recalcular splits (fuera de Fase 12/12.1)
4. **Documentation:** Documentar explícitamente esta limitación en el informe metodológico

### Para Futuras Colecciones

1. Solicitar metadata explícita de individuo (individual_id)
2. Solicitar metadata explícita de observación (obs_id)
3. Utilizar identificadores estables basados en colección (e.g., iNaturalist obs_id)

---

## CONCLUSIÓN

**STATUS: INDEPENDENCE_COMPROMISED**

Los conjuntos REFERENCE (798) y CALIBRATION (195) NO son completamente independientes:

1. **3 imágenes idénticas (SHA-256) están presentes en ambos conjuntos**, rompiendo la independencia de individuos
2. **Independencia de individuos formal: NOT VERIFIABLE** (sin individual_id metadata)
3. **Independencia de observaciones: NOT VERIFIABLE** (sin obs_id metadata)
4. **Taxonomía: VALID** (todas las 10 especies presentes)
5. **Contaminación con proyecto existente: CLEAN** (28 imágenes correctamente excluidas)

### Decisión

Aunque la estrategia de separación fue diseñada para mantener independencia y fue parcialmente efectiva:
- La presencia de 3 duplicados SHA-256 es un **incumplimiento crítico** de independencia
- Sin metadata de individuo/observación, la independencia **no puede ser garantizada**

**Recomendación:** Proceder a Fase 13 con **conocimiento explícito de estas limitaciones** o considerar correcciones (remover duplicados) antes de proceder.

---

## ARCHIVOS GENERADOS

- `FASE12_1_INDEPENDENCE_AUDIT.md` (este archivo)
- `FASE12_1_INDEPENDENCE_AUDIT.json` (formato máquina-legible)
- `cross_split_duplicates.json` (detalle de los 3 duplicados)
