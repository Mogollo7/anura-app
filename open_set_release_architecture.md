# Arquitectura de Releases Open Set — ANURA/SITRana

Documento de arquitectura para la calibración Open Set versionada, trazable y compatible
con catálogos de tamaño variable. Formaliza lo que antes vivía disperso en scripts de
Fase 13 (recálculo ad-hoc, sin persistencia ni versión) como artefactos independientes.

## Diagrama

```
BIOCLIP CHECKPOINT (congelado, bioclip_anura_mejor.pt / encoder_anura_fp16.onnx)
        │  encoder_sha256 = 219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad
        ▼
EMBEDDING CONTRACT (EMBEDDING_CONTRACT.md)
        │  dim=512, preprocessing=create_model_and_transforms(hf-hub:imageomics/bioclip), L2
        ▼
CATALOG RELEASE (visual_catalog/{version}/manifest.json)
        │
        ├── species_ids[]      ← lista explicita, resuelta via taxonomia.canonico()
        ├── centroids          ← especificos de especie, recalculados por release
        │
        ▼
COVARIANCE RELEASE (covariance/{version}/manifest.json + covariance_matrix.npz)
        │  Ledoit-Wolf shared, estimado sobre REFERENCE, GLOBAL al release
        ▼
THRESHOLD RELEASE (threshold/{version}/manifest.json)
        │  calibrado sobre CALIBRATION, GLOBAL al release, ligado a covariance_release
        ▼
OPEN SET EVALUATION (run_open_set_evaluation.py)
        │  usa covariance/threshold PERSISTIDOS, no recalcula — AUROC/KAR/UDR/FAR/FRR/F1
        ▼
BLIND TEST (F3 KNOWN + F4 UNKNOWN)
        │  ⚠️ F3 tiene leakage confirmado contra TRAIN (ver limitaciones) — F4 es limpio
        ▼
DEPLOYABLE RELEASE (regional_package, previa validation_gate PASS)
```

## 1. Encoder congelado

`bioclip_anura_mejor.pt` (PyTorch) / `encoder_anura_fp16.onnx` (ONNX FP16). Nunca se
reentrena para incorporar especies nuevas. Su `encoder_sha256` se verifica en cada
artefacto nuevo (`catalog_release`, `covariance_release`, `threshold_release`) para
detectar cualquier divergencia silenciosa — el bug original de Fase 13 (embeddings
extraídos con arquitectura distinta) es precisamente lo que este contrato previene hacia
adelante.

## 2. Embeddings

Ver `EMBEDDING_CONTRACT.md`. 512D, L2-normalizados, mismo preprocessing que produjo los
embeddings históricos de Fase 13. No se persiste `encoder_sha256`/`dim` dentro de cada
`.npz` de embeddings todavía — sigue siendo una brecha documentada, no resuelta en esta
tarea (fuera de alcance: tocaría re-generar `.npz` históricos).

## 3. Centroides

Calculados con `compute_centroids()` (media de embeddings L2-normalizados por especie).
Específicos de especie, recalculados por cada `catalog_release` — no se persisten como
artefacto propio versionado independientemente (a diferencia de covarianza/threshold);
viven implícitamente en cada script de evaluación que los recalcula desde
`reference_embeddings.npz`/`train_embeddings.npz`. Esto es una simplificación aceptada:
los embeddings fuente sí están congelados y versionados (vía `species_ids[]` +
`encoder_sha256`), por lo que el centroide es reproducible incluso sin persistirse.

## 4. Covariance Release

**Antes**: `ledoit_wolf()` se recalculaba desde cero en 3 scripts distintos de Fase 13
cada vez que se necesitaba, sin persistirse.

**Ahora**: `build_covariance_release.py` la calcula UNA VEZ, la persiste en un `.npz` con
su propio SHA256, y registra procedencia completa (`catalog_release`, `encoder_contract`,
`calibration_dataset`, `species_ids`, `method`, `dimension`, `regularization`). Verificado
byte-idéntico contra el cálculo original de Fase 13 (mismo REFERENCE, mismo método) — esto
es **formalización**, no recalibración.

Es **global al release**: compartida entre Group A (calibración independiente) y Group B
(estructural), tal como Fase 13 la diseñó.

## 5. Threshold Release

**Antes**: guardado solo en `frozen_rejection_config.json`, con `timestamp_utc` pero sin
hash de contenido ni referencia explícita a qué covarianza lo calibró.

**Ahora**: `build_threshold_release.py` preserva el valor exacto (`39.354064` para
`threshold_1.0.0`, sin redondear ni truncar), y lo liga explícitamente a
`covariance_release` + `catalog_release` + `encoder_contract`, con un `sha256` del
contenido científico (excluyendo el timestamp, que es metadata naturalmente variable —
dos ejecuciones con los mismos datos de entrada producen el mismo hash).

## 6. Catalog Release

`visual_catalog/{version}/manifest.json`, con `species_ids[]` explícito (no solo un
conteo) resuelto vía `taxonomic_resolution.py` (reutiliza `taxonomia.canonico()`, el
mismo mecanismo de alias que ya prevenía `acanthinus→achatinus`, ahora conectado).
`v1.0.0` es `FROZEN` e inmutable; releases futuros (`v1.1.0`, etc.) son candidatos
independientes que nunca sobrescriben uno anterior.

## 7. Compatibilidad entre releases

`check_release_compatibility.py` valida, antes de combinar artefactos:
```
catalog_release    == covariance.catalog_release
catalog_release    == threshold.catalog_release
covariance_release == threshold.covariance_release
encoder_sha256 (catalog) == encoder_sha256 (covariance) == encoder_sha256 (threshold)
```
Falla explícitamente (`exit 1`) ante cualquier mismatch — nunca combina releases
incompatibles en silencio. Probado con casos compatible e incompatible reales.

## 8. Calibration Split

```
REFERENCE   (798 imgs, 10 especies incl. 1 huérfana) → calibra COVARIANCE
CALIBRATION (192 imgs, 10 especies)                  → calibra THRESHOLD
TRAIN       (4724 imgs, 41 especies)                 → centroides estructurales Group B
```
Cada uno tiene un rol distinto y documentado; ninguno se reutiliza para el rol de otro
dentro del mismo release.

## 9. Blind Test

**Diseño esperado**: F3 (KNOWN, 766 imgs) + F4 (UNKNOWN, 56 imgs) nunca usados para
calibrar covariance/threshold/centroides.

**Hallazgo real (ver limitaciones)**: F3 completo es un subconjunto exacto de TRAIN
(path idéntico, no solo nombre de archivo) — 197/197 imágenes Group A y 569/569 imágenes
Group B. F4 sí está limpio (0/56 overlap con TRAIN). El blind test es genuino solo para
el lado UNKNOWN de la evaluación.

## 10. Unknown / Open-Set

`run_open_set_evaluation.py` separa KNOWN (especie en `catalog_release.species_ids`) de
UNKNOWN (especie fuera de él). No implementa todavía una categoría `NO_CONCLUSIVE`
explícita (zona ambigua de score) — queda como extensión futura, no bloqueante.

## 11. Lifecycle

Ver `SPECIES_LIFECYCLE.md`. Corrección aplicada en `generate_species_id.py`: una especie
nueva inicia en `DISCOVERED`, nunca en `DEPLOYED`. El estado se hereda automáticamente
para especies ya presentes en el registry de salida, preservando el historial exacto de
las 41 especies ya desplegadas.

## 12. Regional Package

`build_regional_package.py` distingue `regional_catalog_scope` (biodiversidad) de
`visual_classifier_scope` (soporte del release específico), uniendo exclusivamente por
`species_id` — nunca por nombre científico. Verificado con Antioquia (28/29) y Cauca
(17/17) reales, y con un release candidato simulado que demuestra membership correcto
por release.

## 13. Reproducibilidad

Verificada explícitamente en: `species_id` (determinista, 2 ejecuciones idénticas),
`covariance` (2 cálculos independientes idénticos + reproducción cruzada del cálculo
original de Fase 13), `threshold` (hash de contenido científico idéntico tras excluir
timestamp), `catalog_release manifest` (regeneración byte-idéntica), evaluación Open Set
(AUROC/KAR/UDR/FAR idénticos a los oficiales de Fase 13 usando artefactos versionados).

## 14. Inmutabilidad

44 archivos de `evaluation/fase13/`, `visual_catalog/v1.0.0/`, `bioclip/checkpoints/`
verificados con SHA256 antes y después de toda esta auditoría — `diff` exit code 0.
Confirmado independientemente con `git status --short` (vacío en las tres rutas).

---

Ver `validation/new_species_test/open_set_scalability_final_report.md` para el reporte
completo de esta auditoría, incluyendo el hallazgo crítico de leakage F3↔TRAIN.
