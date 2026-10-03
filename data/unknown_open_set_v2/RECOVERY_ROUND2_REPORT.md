# FASE 22.1 — Recuperación ROUND2: candidatas reales verificadas

Fecha: 2026-09-14
Estado final: **RECOVERY_REAL_COMPLETE**

## Lección aplicada

La ronda anterior aceptó `Boana_albifrons` y `Pristimantis_brevirostris` sin verificar
que existieran como taxones reales; ambas resultaron 0 resultados en iNaturalist y
GBIF (`matchType: NONE`). En esta ronda, **toda candidata fue verificada por
taxon_id real (iNaturalist + GBIF, PASO 0) antes de ser considerada**, y ninguna
candidata fue aceptada sin pasar ambas verificaciones.

## PASO 0-1: Candidatas evaluadas y verificación de taxón

Ver tabla completa en `data/unknown_open_set_v2/candidates/species_candidate_availability_ROUND2.csv`
(23 candidatas, todas con `verification_status = VERIFIED_REAL_TAXON`).

Resumen de la búsqueda:

- **Género Boana** (Colombia, iNaturalist, cualquier grado, con fotos): ninguna especie
  no-KNOWN alcanzó el margen de seguridad (>=85 imágenes utilizables). El mejor
  candidato de género fue `Boana picturata` con 55 fotos totales en Colombia.
  `Boana crepitans`, pese a tener 1,959 ocurrencias en GBIF (datos de museo/registros,
  no fotografías), solo tiene 4 observaciones con fotos en Colombia en iNaturalist —
  confirma que el conteo de ocurrencias GBIF no es un proxy fiable de disponibilidad
  fotográfica real.
- **Género Pristimantis** (Colombia): mejor candidato `Pristimantis elegans` con 72
  fotos totales / 42 con licencia CC — por debajo del margen de seguridad.
- Dado que ninguna candidata de género alcanzó el umbral, se escaló a **SAME_FAMILY**
  como indica el protocolo, documentando explícitamente el cambio de prioridad:
  - Familia **Hylidae** (para reemplazar el slot de Boana): se encontraron varias
    especies con alta disponibilidad real: `Scinax rostratus` (114 fotos CC en
    Colombia), `Osteocephalus taurinus` (99), `Pseudis paradoxa` (91).
  - Familia **Craugastoridae** (para reemplazar el slot de Pristimantis): se encontró
    `Craugastor metriosistus` con 200 fotos CC en Colombia — muy por encima del
    margen de seguridad.

## PASO 2: Selección final

| Slot reemplazado | Especie original objetivo | Especie seleccionada | Relación | taxon_id (iNat) | GBIF speciesKey | Verificación |
|---|---|---|---|---|---|---|
| Boana_albifrons (alucinado) | Boana geographica (2 img reales, insuficiente) | **Scinax rostratus** | SAME_FAMILY (Hylidae) | 24292 | 5217865 | iNat: rank=species, is_active=true. GBIF: matchType=EXACT, rank=SPECIES |
| Pristimantis_brevirostris (alucinado) | Pristimantis nervicus (3 img reales, insuficiente) | **Craugastor metriosistus** | SAME_FAMILY (Craugastoridae) | 517046 | 10819374 | iNat: rank=species, is_active=true. GBIF: matchType=EXACT, rank=SPECIES |

Ambas especies fueron confirmadas AUSENTES del catálogo KNOWN de 41 especies
(`taxonomy/species/species_registry.json`).

## PASO 3: Descarga real y auditoría

Descarga vía API real de iNaturalist (`/v1/observations`, `place_id=7196` Colombia,
`photo_license` restringido a licencias CC), respetando 1 req/seg.

| Especie | Observaciones CC disponibles (CO) | Descargadas | Válidas post-auditoría | Individuos independientes (proxy = observation_id distintos) |
|---|---|---|---|---|
| Scinax rostratus | 114 | 110 | **100** (tras trim determinista) | 100 |
| Craugastor metriosistus | 200 | 85 (descarga detenida deliberadamente dentro de la banda 70-100) | **85** | 85 |

Auditoría automática (heurísticas, sin revisión visual humana):

- **Integridad/resolución/blur/brillo/contraste**: `Scinax rostratus` 109/110 OK,
  1 imagen descartada por `BAD_BRIGHTNESS`. `Craugastor metriosistus` 85/85 OK.
- **Duplicados exactos (SHA256)**: 0 en ambas especies.
- **Near-duplicate perceptual hash**: no disponible en este entorno (sin librería
  de pHash instalada) — registrado como `near_duplicate_automated_check: unavailable`,
  igual que en fases previas.
- **Leakage**: comparado contra `data/unknown_open_set_v2/audit/hash_index_recovery_reference.txt`
  (12,234 hashes). **Leakage detectado: 0** en ambas especies.

Archivos de auditoría generados:
- `data/unknown_open_set_v2/audit/image_quality_audit_ROUND2.csv`
- `data/unknown_open_set_v2/audit/duplicate_audit_ROUND2.csv`
- `data/unknown_open_set_v2/audit/leakage_audit_ROUND2.csv`
- `data/unknown_open_set_v2/audit/audit_summary_ROUND2.json`

## PASO 5: Límite final (70-100)

`Scinax rostratus` quedó en 109 imágenes válidas tras la auditoría de calidad (110
descargadas − 1 descartada), superando el máximo de 100. Se aplicó selección
determinista: **ordenar por SHA256 ascendente y conservar las primeras 100**; las
10 imágenes restantes se movieron a
`images/primary/_excluded_Scinax_rostratus/` (no se eliminaron, quedan trazables).

`Craugastor metriosistus` quedó en 85 imágenes válidas, dentro del rango 70-100 sin
necesidad de recorte.

## PASO 6: Resultado

**Caso A: ambas especies alcanzaron el rango 70-100.**
Dataset UNKNOWN_V2.1 reconstruido con 7 especies:

| Especie | Imágenes válidas | Individuos |
|---|---|---|
| Smilisca phaeota | 107 (desviación de contrato documentada, no tocada) | 55 |
| Espadarana prosoblepon | 89 | 45 |
| Leptodactylus fragilis | 85 | 44 |
| Rhinella marina | 83 | 41 |
| Dendropsophus labialis | 74 | 43 |
| **Scinax rostratus** (nuevo) | **100** | 100 |
| **Craugastor metriosistus** (nuevo) | **85** | 85 |
| **TOTAL** | **623** | **413** |

Estado: **READY_FOR_FASE23A_EVALUATION**

## PASO 7: Manifests actualizados

`data/unknown_open_set_v2/manifests/PRIMARY_MANIFEST.json` actualizado con
conteos reales verificados: `n_species=7`, `n_images=623`, `n_individuals=413`,
`gate_verification="PASS_7_SPECIES_ROUND2"`, `ready_for_phase23=true`.

`data/unknown_open_set_v2/manifests/download_manifest_ROUND2.json` contiene las
185 entradas reales (100 Scinax rostratus + 85 Craugastor metriosistus) con
observation_id, photo_id, taxon_id, license, original_url, local_path, sha256,
download_timestamp, quality_grade, coordinates.

## Evidencia física verificable

- Rutas reales: `D:\Anura\data\unknown_open_set_v2\images\primary\Scinax_rostratus\`
  (100 archivos) y `D:\Anura\data\unknown_open_set_v2\images\primary\Craugastor_metriosistus\`
  (85 archivos).
- SHA256 de muestra (recalculado en disco, no solo leído del manifest):
  - `102423919_171208426.jpg` (Scinax rostratus) →
    `64763d1c5b112dce78f571de3204dd37e81a6db6df50cff6a174c3aff357ba70`
  - Ver manifest completo para las 185 entradas con SHA256 individual.
- Licencias confirmadas en el manifest: únicamente CC (`cc0`, `cc-by`, `cc-by-nc`,
  `cc-by-nc-sa`, `cc-by-nc-nd`) — ninguna imagen sin licencia CC fue descargada.

## Limitaciones documentadas (honestidad, no ocultas)

- El proxy de "individuos independientes" es el conteo de `observation_id`
  distintos, igual que en fases previas — no hay verificación formal de que dos
  observaciones distintas no correspondan al mismo individuo re-fotografiado
  (mismo patrón de limitación ya documentado en
  `anura_reference_calibration_independencia.md`).
- Perceptual-hash near-duplicate check no disponible en este entorno de ejecución.
- Los conteos de ocurrencias de GBIF (usados solo para el descubrimiento inicial
  de candidatas) incluyen registros de museo/herbario sin fotografía y **no son
  equivalentes** a disponibilidad fotográfica real en iNaturalist — esto explica
  por qué `Boana crepitans` (1,959 ocurrencias GBIF) tiene solo 4 fotos reales en
  Colombia. Todas las decisiones de selección final se basaron en conteos reales
  de iNaturalist, no en GBIF.
