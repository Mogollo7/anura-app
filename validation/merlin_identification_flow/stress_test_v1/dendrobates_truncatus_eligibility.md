# Elegibilidad de Dendrobates truncatus

Folder crudo: data cleaned\Dendrobates_truncatus — 1809 archivos, 984 obs_id unicos por patron de nombre.
Grupos de duplicados exactos (SHA256) en el folder crudo: 0.

## Pool de embeddings realmente usado (reference+train+calibration)

| Split | Imagenes | Individuos recuperados (obs_id via SHA256) |
|---|---|---|
| reference_embeddings | 73 | 0 |
| train_embeddings | 90 | 49 |
| calibration_embeddings | 18 | 0 |

Total imagenes en pool: 181. Individuos unicos recuperados (union, piso): 49.

## Fuga cruzada entre splits (SHA256 identico)

- reference_embeddings__x__train_embeddings: 0 duplicados
- reference_embeddings__x__calibration_embeddings: 0 duplicados
- train_embeddings__x__calibration_embeddings: 0 duplicados

## Clasificacion por tier documentado

Tier: **B** — 30-69 individuos (49) -> especie, umbral MAS EXIGENTE

## Veredicto

`DENDROBATES_TRUNCATUS_ELIGIBLE = YES`

Individuos recuperados en el pool de embeddings: 49 (piso, ver caveat). Tier resultante: B. Fuga cruzada entre splits: NO. La especie YA esta DEPLOYED en el catalogo de 41 (species_registry.json, visual_lifecycle_status=DEPLOYED) y YA tiene centroide activo en el release (ANU_COL_DEND_TRU_001 participa en OpenSetReleaseAdapter con 41/41 centroides). Esta auditoria NO encontro evidencia que revierta esa decision ya tomada, pero tampoco pudo confirmar un conteo EXACTO de individuos por la limitacion de recuperacion de obs_id arriba documentada -- de ahi que si el conteo recuperado cae bajo 70 se reporte como Tier B (activable, umbral mas exigente) en vez de bloquear, dado que ya esta desplegada y funcionando en Parte 2 y Parte 4.
