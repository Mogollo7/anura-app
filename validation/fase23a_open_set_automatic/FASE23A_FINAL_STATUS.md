# FASE 23A — FINAL STATUS REPORT (CORREGIDO)

**Date:** 2026-09-14  
**Status:** FASE23A_COMPLETE_PARTIAL_DATA_CORRECTED_ENCODER  
**Executed by:** Claude Sonnet 5  
**Puramente diagnóstico. No se hizo commit ni push.**

---

## Corrección Metodológica Aplicada

Una revisión externa detectó que la primera ejecución usó el **BioCLIP genérico pre-entrenado** (`hf-hub:imageomics/bioclip` sin fine-tuning) en lugar del **encoder congelado real** usado para generar los embeddings KNOWN de Fase 13. Esto invalidaba toda comparación de distancias (espacios de embedding distintos e incompatibles).

### Verificación de infraestructura BioCLIP (exploración exhaustiva de `bioclip/`)

✓ **Confirmado — infraestructura completa presente:**
- `bioclip/checkpoints/`: 9 checkpoints (bioclip_anura_mejor.pt, encoder_anura.pt, encoder_anura_fp16.pt/.onnx, encoder_anura_int8.pt, anura_clasificador*.onnx)
- `bioclip/scripts/`: Fases 1-9 completas (prueba, embeddings, baseline, transfer learning, evaluación, extracción de encoder, exportación móvil, k-NN vs clasificador, paquete regional)
- `bioclip/paquetes_regionales/antioquia_v1.sqlite`: presente
- `bioclip/evaluation/encoder_metadata.json`: metadata completa del encoder fine-tuned

### Encoder correcto identificado

Inspeccionando `evaluation/fase13/fase13_compute_train_embeddings.py` (script real que generó `train_embeddings.npz`, los embeddings KNOWN usados en Fase 13-21), se confirmó la receta exacta:

```python
model, _, preprocess = open_clip.create_model_and_transforms("hf-hub:imageomics/bioclip")
checkpoint = torch.load("bioclip/checkpoints/bioclip_anura_mejor.pt", ...)
model.visual.load_state_dict(checkpoint["visual_state_dict"])
visual_model = model.visual.to(device).eval()
# embedding = visual_model(img); embedding /= embedding.norm()
```

**Checkpoint verificado por SHA256:**
```
bioclip_anura_mejor.pt SHA256: 98a6c54d6edb27e2b0344b8bbbaebd2ab749b1bf5136991ff73b37f66ee2c1ac
```
Este hash coincide con el nombre del archivo cacheado en `COLOMBIA_ANURA/cache/embeddings/98a6c54d6edb27e2.npz`, confirmando que es el checkpoint consistentemente usado en el pipeline de producción (fine-tuned en Fase 4: transfer learning jerárquico sobre 12,254 fotos / 41 especies, extraído en Fase 6).

**Nota:** El hash `219e860e6fa9...` referenciado en `threshold/v1.1.0_CLEAN/manifest.json` como `encoder_sha256` no coincide con el hash de bytes crudos de ningún checkpoint local (probablemente corresponde a un hash del export ONNX o de metadata combinada, no verificable en este ciclo). Se usó como fuente de verdad el **script real de generación de embeddings KNOWN** (fase13_compute_train_embeddings.py) en lugar del hash documentado, ya que garantiza compatibilidad exacta del espacio de embeddings.

Script corregido: `validation/fase23a_open_set_automatic/fase23a_final.py` — ahora carga `bioclip_anura_mejor.pt` con verificación de hash en tiempo de ejecución (assert), replicando exactamente el pipeline de Fase 13.

---

## Resultado de la Corrección: Antes vs Después

| Métrica | Encoder INCORRECTO (BioCLIP genérico) | Encoder CORRECTO (fine-tuned) |
|---------|---------------------------------------|-------------------------------|
| Euclidean distance (media) | 0.910 | **0.623** |
| Cosine distance (media) | 0.421 | **0.219** |
| Mahalanobis distance (media) | 49.658 | **32.462** |
| Mahalanobis vs threshold (39.35) | Por encima (mayoría rechazada) | **Por debajo (mayoría ACEPTADA)** |

**Implicación crítica:** con el encoder genérico, las distancias eran artificialmente altas (embeddings en espacios distintos), sugiriendo — incorrectamente — buen rechazo de UNKNOWN. Con el encoder correcto, las distancias caen dramáticamente por debajo del threshold oficial, revelando que el sistema **acepta erróneamente la mayoría de las imágenes UNKNOWN como si fueran de especies conocidas**.

---

## Segundo Bug Corregido: Threshold Único Mal Aplicado

El threshold oficial (39.354) es válido **únicamente para Mahalanobis** (método M5_LedoitWolf_Shared, congelado en `threshold/v1.1.0_CLEAN/manifest.json`). Se detectó que se aplicó erróneamente ese mismo valor numérico a Euclidean/Cosine/Normalized (escalas ~0.2–0.9), produciendo FAR=1.0/FRR=1.0 degenerados (artefacto, no señal).

**Corrección:** se aplicó threshold específico por método:

| Método | Threshold | Tipo | Fuente |
|--------|-----------|------|--------|
| Mahalanobis | 39.354 | OFFICIAL_FROZEN | threshold/v1.1.0_CLEAN (M5_LedoitWolf_Shared, KAR 95%) |
| Euclidean_Raw | 0.6805 | DIAGNOSTIC_ONLY | FASE21 VALIDATION (Youden J, KNOWN-only, no re-optimizado aquí) |
| Cosine | 0.2630 | DIAGNOSTIC_ONLY | FASE21 VALIDATION (Youden J) |
| Normalized_Euclidean | 0.7252 | DIAGNOSTIC_ONLY | FASE21 VALIDATION (Youden J) |

---

## Resultados Finales Corregidos (439 imágenes disponibles, 5/7 especies PRIMARY)

### FAR por método (fracción de UNKNOWN aceptada erróneamente como KNOWN)

| Método | Threshold | Tipo | FAR | Bootstrap CI 95% |
|--------|-----------|------|-----|-------------------|
| **Mahalanobis** | 39.354 | OFFICIAL | **0.754** | [0.711, 0.793] |
| Cosine | 0.263 | DIAGNOSTIC | 0.629 | [0.585, 0.677] |
| Normalized Euclidean | 0.7252 | DIAGNOSTIC | 0.628 | [0.583, 0.674] |
| Euclidean Raw | 0.6805 | DIAGNOSTIC | 0.569 | [0.522, 0.615] |

**Hallazgo principal:** con el encoder y thresholds correctos, el sistema Open Set **acepta erróneamente entre 57% y 75% de las imágenes UNKNOWN automáticas como especies conocidas**, según el método. Mahalanobis (el método OFICIAL en producción) es el que peor rechaza UNKNOWN en este dataset (FAR=75.4%).

### FAR por especie (Mahalanobis oficial vs Euclidean diagnóstico)

| Especie | n | FAR Mahalanobis | FAR Euclidean |
|---------|---|------------------|-----------------|
| Espadarana_prosoblepon | 89 | **0.966** | 0.888 |
| Rhinella_marina | 83 | 0.880 | 0.819 |
| Dendropsophus_labialis | 74 | 0.743 | 0.689 |
| Smilisca_phaeota | 108 | 0.685 | 0.296 |
| Leptodactylus_fragilis | 85 | 0.506 | **0.235** |

**Interpretación:** Espadarana_prosoblepon (Centrolenidae, familia ausente del catálogo KNOWN) es la más frecuentemente mal-aceptada — contraintuitivo, ya que se esperaría que una familia completamente distinta fuera más fácil de rechazar. Leptodactylus_fragilis y Smilisca_phaeota (con Euclidean) muestran mejor rechazo relativo.

### AUROC: NaN (correcto, no es un bug)

AUROC/AUPRC requieren ambas clases (KNOWN y UNKNOWN) en `y_true` para definirse. Este dataset es **puramente UNKNOWN** (todas las etiquetas = 0), por diseño del protocolo Fase 23A. Por tanto AUROC es matemáticamente indefinido (`sklearn` lo reporta como NaN con warning explícito) — **no representa un fallo del pipeline**. Para obtener AUROC comparable a Fase 21 sería necesario mezclar este UNKNOWN con una muestra BLIND TEST de KNOWN, lo cual queda fuera del alcance de Fase 23A (que evalúa específicamente el comportamiento sobre UNKNOWN automático).

---

## Dataset: Gap de Datos Confirmado (Sin Relación con Infraestructura)

Búsqueda exhaustiva en TODO el repositorio (`find /d/Anura -iname "*Boana_albifrons*"` y equivalente para Pristimantis_brevirostris) confirma:

- **PRIMARY_MANIFEST.json declara:** 622 imágenes, 7 especies, 321 individuos
- **Imágenes físicamente presentes:** 439 imágenes, 5 especies
- **Especies con directorio vacío en TODO el repo:** Boana_albifrons (0/95), Pristimantis_brevirostris (0/89)

Estos directorios existen únicamente en `data/unknown_open_set_v2/images/primary/{especie}/` pero están **vacíos** — no hay copias en `/final/`, `/new/`, `/historical/`, ni en ninguna otra ubicación del repositorio. Esto es un **gap de datos genuino**, confirmado independientemente de la corrección de encoder — no relacionado con disponibilidad de infraestructura BioCLIP (que sí está completa y funcional).

---

## Artefactos Finales

```
validation/fase23a_open_set_automatic/
├── FASE23A_FINAL_STATUS.md              (este archivo — reporte definitivo)
├── FASE23A_COMPLETE_REPORT.md           (reporte técnico, encoder corregido)
├── fase23a_final.py                     (script corregido: encoder + hash verificado)
├── fix_per_method_thresholds.py         (script de corrección de thresholds)
├── method_comparison_corrected.csv      (4 métodos, thresholds correctos)
├── bootstrap_far_corrected.csv          (FAR + IC 95%, 1000 iteraciones)
├── metrics_by_species_corrected.csv     (FAR por especie, 2 métodos)
├── metrics_by_species.csv               (distancias medias por especie)
└── predictions/predictions_full.csv     (439 predicciones, 4 scores cada una)
```

---

## Conclusión Científica

1. **Infraestructura BioCLIP:** ✓ Completa y funcional (confirmado tras exploración exhaustiva de `bioclip/`)
2. **Encoder correcto:** ✓ Corregido y verificado por SHA256 (`bioclip_anura_mejor.pt`)
3. **Thresholds correctos por método:** ✓ Corregido (oficial para Mahalanobis, diagnóstico para el resto)
4. **Hallazgo principal:** El sistema Open Set en producción (Mahalanobis, threshold oficial) **acepta erróneamente el 75.4% de imágenes UNKNOWN automáticas** como especies conocidas — un resultado mucho más preocupante que el sugerido por la ejecución inicial con encoder incorrecto.
5. **Gap de datos:** 183 imágenes (2/7 especies PRIMARY) genuinamente ausentes del filesystem — confirmado, no relacionado con el encoder.
6. **AUROC NaN:** esperado y correcto para diseño de dataset puramente UNKNOWN (no evaluable sin mezcla KNOWN).

**Recomendación:** Estos resultados (FAR 57-75%) son señal de alarma real sobre el rendimiento del rechazo Open Set con datos automáticos sin curar, y deberían ser priorizados sobre la ejecución previa (que subestimaba el problema por usar encoder incorrecto).

**No se realizó commit ni push.**

---

**PHASE STATUS: FASE23A_COMPLETE_PARTIAL_DATA_CORRECTED_ENCODER**
