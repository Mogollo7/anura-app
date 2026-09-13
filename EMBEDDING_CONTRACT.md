# EMBEDDING_CONTRACT.md

Especificación del contrato que todo embedding debe declarar, para que un centroide construido
hoy sea comparable con uno construido mañana solo si comparten el mismo contrato.

## Valores reales del encoder congelado (verificados, no inventados)

```json
{
  "encoder_id": "bioclip_anura_v1",
  "encoder_family": "BioCLIP",
  "encoder_variant": "ViT-B-16",
  "encoder_source": "hf-hub:imageomics/bioclip",
  "checkpoint_file": "bioclip_anura_mejor.pt",
  "checkpoint_format": "PyTorch state_dict (visual_state_dict)",
  "onnx_export": "encoder_anura_fp16.onnx",
  "encoder_sha256": "219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad",
  "embedding_dimension": 512,
  "preprocessing_version": "open_clip.create_model_and_transforms native preprocess",
  "normalization_version": "L2 (embedding / ||embedding||)"
}
```

**Fuente de estos valores**: `evaluation/fase13/fase13_compute_embeddings.py` (líneas de
construcción del modelo) + `evaluation/fase13/fase13_pre_audit.py` (verificación de hash) +
verificación directa de `reference_embeddings.npz['embeddings'].shape[1] == 512` en esta sesión.

## Por qué existe este contrato (motivo real, no hipotético)

Durante Fase 13 se detectó que un script de extracción construía el encoder con
`open_clip.create_model('ViT-B-16', pretrained=False)` + preprocessing manual, en vez de
`open_clip.create_model_and_transforms("hf-hub:imageomics/bioclip")` (usado por F3/F4). Los
embeddings resultantes eran numéricamente incompatibles aunque la dimensión (512) coincidía —
el bug no era detectable solo mirando la forma del array. **Este contrato existe para que ese
tipo de incompatibilidad silenciosa sea detectable mediante un hash de encoder registrado, no
solo mediante inspección de forma/dimensión.**

## Regla de compatibilidad

Dos conjuntos de embeddings son comparables (pueden alimentar el mismo cálculo de centroide o
covarianza) **si y solo si**:
```
encoder_sha256 idéntico
AND embedding_dimension idéntico
AND preprocessing_version idéntico
AND normalization_version idéntico
```
Si cualquiera difiere, deben tratarse como **incompatibles** aunque la dimensión coincida.

## Estado actual real de los artefactos existentes

| Artefacto | ¿Declara el contrato hoy? |
|---|---|
| `reference_embeddings.npz`, `calibration_embeddings.npz`, `train_embeddings.npz` | NO — solo guardan `embeddings, species, paths, sha256(imagen)`. El contrato se verifica aparte, manualmente, en `fase13_pre_audit.py`. |
| `knn_embeddings.npz` (F3/F4) | NO verificado en esta auditoría (fuera del alcance — no se abrió el script que lo generó). |

**No se modifican estos `.npz` existentes** (violaría la regla de no tocar Fase 13). El contrato
se aplica hacia adelante: todo `.npz` nuevo generado para especies/regiones futuras debe incluir
estos campos como metadata adjunta (ver `schemas/embedding.schema.json` y
`tools/catalog/validate_embedding_contract.py`).
