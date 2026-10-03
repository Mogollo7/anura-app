# PRIMARY_REBUILD_REPORT — data/unknown_open_set_v2/images/primary/

Fecha: 2026-09-14
Estado final: **BLOCKED_DUPLICATES_NOT_ZERO** (no `PRIMARY_REBUILD_COMPLETE`)

## Paso 1 — Copia mecánica

| Especie | Fuente elegida | Conteo new/ | Conteo final/ | Copiados a primary/ | Identidad SHA256 antes/después |
|---|---|---|---|---|---|
| Smilisca_phaeota | final/ | 108 | 108 | 108 | OK 108/108 |
| Espadarana_prosoblepon | final/ | 90 | 89 | 89 | OK 89/89 |
| Leptodactylus_fragilis | final/ | 85 | 85 | 85 | OK 85/85 |
| Rhinella_marina | final/ | 83 | 83 | 83 | OK 83/83 |
| Dendropsophus_labialis | final/ | 74 | 74 | 74 | OK 74/74 |

**Criterio de elección de fuente**: se usó `final/` porque es el resultado documentado de la
auditoría de calidad (`images/final/` = post quality-audit; `images/new/` = raw descargado). Esto
se confirma empíricamente para Espadarana_prosoblepon: `new/`=90, `final/`=89 — `final/` tiene
exactamente 1 archivo menos, consistente con un rechazo de calidad aplicado después de la
descarga. Las demás especies tienen conteos idénticos en `new/` y `final/`, por lo que la elección
no cambia el resultado salvo en ese caso.

No se movieron ni eliminaron los originales en `new/`/`final/`. Ningún archivo nuevo fue
descargado. No hubo curación manual (0 revisiones visuales de inclusión/exclusión).

## Paso 2 — Re-auditoría completa (7 especies, filesystem real)

### 2.1 Conteo físico real (post-copia)

| Especie | Archivos reales en primary/ |
|---|---|
| Smilisca_phaeota | 108 |
| Espadarana_prosoblepon | 89 |
| Leptodactylus_fragilis | 85 |
| Rhinella_marina | 83 |
| Dendropsophus_labialis | 74 |
| Scinax_rostratus | 100 |
| Craugastor_metriosistus | 85 |
| **TOTAL** | **624** |

(La consigna mencionaba ~623; el conteo físico real y verificado es 624.)

### 2.2 Integridad

Cada uno de los 624 archivos fue abierto y decodificado con Pillow (`Image.verify()` +
`Image.load()`). **0 fallos de integridad** — los 624 son JPEG válidos y decodificables.

### 2.3 SHA256 y unicidad

SHA256 recalculado para los 624 archivos. **Duplicados exactos dentro del set: 3 grupos / 4
archivos extra** (NO cero):

| SHA256 (prefijo) | Especie | Tipo | Archivos |
|---|---|---|---|
| `0b0f4767...` | Smilisca_phaeota | **CROSS_OBSERVATION** (observation_id distinto, imagen byte-idéntica) | `col_obs_350918262_photo_640324804.jpg`, `col_obs_366894693_photo_669971437.jpg` |
| `c8de293b...` | Espadarana_prosoblepon | SAME_OBSERVATION (obs 320644020, 3 subidas idénticas) | `..._579765862.jpg`, `..._579765880.jpg`, `..._579766366.jpg` |
| `9acecd8d...` | Leptodactylus_fragilis | SAME_OBSERVATION (obs 288843271, 2 subidas idénticas) | `..._519472876.jpg`, `..._519482732.jpg` |

El caso de Smilisca_phaeota es el más relevante: dos `observation_id` **distintos** de iNaturalist
apuntan a un archivo binario idéntico, lo cual es una anomalía de los datos de origen preexistente
en `final/` (no introducida por esta copia) que afecta la independencia de individuos.

Estos duplicados existían YA en `images/final/` antes de esta reconstrucción; la copia mecánica
los preservó tal cual, como exige la restricción de no hacer curación manual.

### 2.4 Leakage — ANOMALÍA DETECTADA (no corregida silenciosamente)

El índice pre-existente `audit/hash_index_recovery_reference.txt` (12234 hashes) marca **439/624
archivos (100% de las 5 especies recién copiadas) como leakage**, mientras que Scinax_rostratus y
Craugastor_metriosistus dan 0/185 (consistente con `leakage_audit_ROUND2.csv` ya existente).

Se investigó la causa: se buscaron los SHA256 flagueados directamente en el filesystem completo de
`D:\Anura` (roots `data`, `data cleaned`, `training`, `validation`). Las únicas coincidencias
encontradas están **dentro del propio árbol `unknown_open_set_v2/images/{new,final,primary}`** —
es decir, el índice de referencia contiene hashes de las propias imágenes "unknown" (auto-
contaminación), no hashes reales del split KNOWN (TRAIN/REFERENCE/CALIBRATION/VALIDATION/BLIND).

Para obtener un resultado confiable se reconstruyó un índice limpio en esta sesión, hasheando
en fresco los 12254 archivos JPEG/PNG bajo `D:\Anura\data cleaned` (la raíz real del dataset KNOWN
de 41 especies) y comparando contra los 624 hashes de `primary/`:

**Resultado: leakage real = 0 / 624.**

`audit/hash_index_recovery_reference.txt` **no fue sobrescrito** (se preserva como evidencia de
auditoría); el manifest regenerado documenta explícitamente esta discrepancia y usa el resultado
verificado (0) en vez del resultado contaminado (439), dejando registrado el número original.

### 2.5 Taxonomía

Se ejecutó `tools/catalog/taxonomic_resolution.py` (`SpeciesResolver`) contra
`taxonomy/species/species_registry.json` para las 7 especies. Resultado: **las 7 resuelven a
`UNRESOLVED_NOT_IN_REGISTRY`** — resultado esperado y correcto, ya que estas son especies del
open-set (no pertenecen al catálogo cerrado de 41 especies KNOWN). Género/familia se documentan
por taxonomía estándar (no derivados del proyecto):

| Especie | Género | Familia |
|---|---|---|
| Smilisca_phaeota | Smilisca | Hylidae |
| Espadarana_prosoblepon | Espadarana | Centrolenidae |
| Leptodactylus_fragilis | Leptodactylus | Leptodactylidae |
| Rhinella_marina | Rhinella | Bufonidae |
| Dendropsophus_labialis | Dendropsophus | Hylidae |
| Scinax_rostratus | Scinax | Hylidae |
| Craugastor_metriosistus | Craugastor | Craugastoridae |

### 2.6 Individuos reales (no 1 imagen = 1 individuo)

Contados por `observation_id`/`individual_id` real extraído del nombre de archivo (patrón
`col_obs_<obsid>_photo_<photoid>.jpg` para las 5 especies reconstruidas; `<obsid>_<photoid>.jpg`
para Scinax/Craugastor, ya pobladas correctamente):

| Especie | Imágenes | Individuos (obs_id únicos) |
|---|---|---|
| Smilisca_phaeota | 108 | 55 |
| Espadarana_prosoblepon | 89 | 45 |
| Leptodactylus_fragilis | 85 | 44 |
| Rhinella_marina | 83 | 41 |
| Dendropsophus_labialis | 74 | 43 |
| Scinax_rostratus | 100 | 100 |
| Craugastor_metriosistus | 85 | 85 |
| **TOTAL** | **624** | **413** |

## Paso 3 — PRIMARY_MANIFEST.json regenerado

Reescrito en `data/unknown_open_set_v2/manifests/PRIMARY_MANIFEST.json`, derivado exclusivamente
de la verificación de esta sesión (conteos, SHA256, taxonomía, individuos, leakage real). No se
copiaron números del manifest anterior ("fantasma").

`ready_for_phase23a: false` — porque el gate de "duplicados exactos = 0" especificado por el
usuario NO se cumple (4 archivos duplicados). Todos los demás criterios sí se cumplen:
- 7 especies con archivos físicos reales confirmados: ✅
- leakage = 0 (contra dataset KNOWN real): ✅ (el índice pre-generado da 439 pero está contaminado, ver 2.4)
- taxonomía resuelta para las 7: ✅ (UNRESOLVED_NOT_IN_REGISTRY es el resultado correcto esperado)
- rango 70-100 por especie (excepto Smilisca, documentado): ✅ Smilisca=108 (CONTRACT_DEVIATION_AUTOMATIC_DATA), Scinax=100 (límite superior, dentro de rango), resto en rango
- **duplicados exactos = 0: ❌ (3 grupos / 4 archivos)**

## Paso 4 — Boana_albifrons / Pristimantis_brevirostris

Confirmado: ambas carpetas permanecen vacías en el filesystem (0 archivos) y **no aparecen** como
entradas en el `PRIMARY_MANIFEST.json` regenerado. Se dejaron intactas como evidencia de auditoría,
según lo permitido.

## Conclusión y bloqueo

La reconstrucción mecánica (Paso 1) se completó con éxito total: 5 especies copiadas, 100%
identidad SHA256 verificada, 0 archivos nuevos descargados, 0 curación manual, originales
preservados.

La re-auditoría (Paso 2) reveló dos hallazgos que el proceso **no corrigió silenciosamente**:

1. El índice de leakage pre-existente está contaminado (auto-referencial); el leakage real
   verificado contra el dataset KNOWN es 0. Esto se documenta pero **no bloquea** por sí solo.
2. Existen 4 archivos duplicados exactos (3 grupos) heredados de los datos de origen en `final/`,
   uno de ellos cruzando dos `observation_id` distintos de iNaturalist. Esto **sí bloquea** el gate
   `ready_for_phase23a` tal como fue especificado por el usuario (duplicados exactos = 0).

**Por esta razón, la ejecución de FASE 23A NO se inició.** Continuar automáticamente habría
requerido decidir unilateralmente cómo tratar los 4 archivos duplicados (eliminar 1 de cada
grupo sería una forma de curación de datos, no de auditoría mecánica), lo cual excede el mandato
de "copia mecánica + auditoría automática, sin curación manual" y podría alterar silenciosamente
los conteos reportados como reales.

## Artefactos generados en esta sesión

- `data/unknown_open_set_v2/images/primary/<5 especies>/` — 439 archivos copiados
- `data/unknown_open_set_v2/manifests/PRIMARY_MANIFEST.json` — regenerado
- `data/unknown_open_set_v2/PRIMARY_REBUILD_REPORT.md` — este reporte
- Índice limpio de hashes KNOWN (12254 hashes, `data cleaned/`) generado en el scratchpad de
  sesión para la verificación de leakage real; no se persistió dentro del repo para no pisar
  `audit/hash_index_recovery_reference.txt` sin instrucción explícita del usuario.

## Recomendación (no ejecutada, requiere decisión del usuario)

Para poder completar el gate y proceder a FASE 23A, el usuario debe decidir explícitamente:
- (a) aceptar los 4 duplicados como parte legítima de la variabilidad de individuos (múltiples
  fotos idénticas de la misma observación no afectan el conteo de individuos, ya que ya se cuenta
  por `observation_id`; solo el caso cross-observation de Smilisca_phaeota necesitaría revisión), o
- (b) autorizar explícitamente la eliminación de las copias duplicadas redundantes (dejando 1 por
  grupo), lo cual SÍ constituye una decisión de curación y por tanto requiere aprobación explícita
  fuera del alcance "mecánico" de esta tarea.
- Adicionalmente, se recomienda reconstruir formalmente `audit/hash_index_recovery_reference.txt`
  para excluir la auto-contaminación detectada, de forma que futuras auditorías de leakage no
  reporten falsos positivos.
