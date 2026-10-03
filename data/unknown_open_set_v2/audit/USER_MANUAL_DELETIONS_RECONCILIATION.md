# Reconciliación de deleciones manuales del usuario — Rhinella_marina y Dendropsophus_labialis (UNKNOWN pool)

Fecha: 2026-09-14

## Contexto

Antes de conocerse el bug de etiquetado labialis/molitor (ver `LEAKAGE_AUDIT_CORRECTION_v2.md`), el usuario hizo una limpieza de calidad visual manual sobre las carpetas `data/unknown_open_set_v2/images/primary/Rhinella_marina/` y `.../Dendropsophus_labialis/`, borrando imágenes directamente del disco. Este documento reconcilia esas 35 deleciones contra el estado original congelado en `unknown_embeddings.npz` (que no se vio afectado por las deleciones, pues se extrajo antes) y contra la lista de contaminación de la Parte 1.

Esto es **solo lectura + documentación**. No se restauró ni se borró ningún archivo adicional.

## Rhinella_marina — 25 imágenes borradas (83 → 58 en disco)

Ninguna de las 25 imágenes borradas de `Rhinella_marina` corresponde a contaminación de etiquetado: la auditoría completa de `observation_id` entre `Rhinella_marina` (UNKNOWN) y `Rhinella_horribilis` (KNOWN) confirmó **0 coincidencias** de `observation_id` — el par de confusión Rhinella_marina/Rhinella_horribilis es genuinamente una confusión visual entre dos especies de sapo distintas, no un artefacto de etiquetado. Las 25 deleciones se clasifican todas como `limpieza_calidad_normal` (motivo: calidad visual, decisión del usuario, independiente del bug).

## Dendropsophus_labialis — 10 imágenes borradas (74 → 64 en disco)

De las 10 imágenes borradas:
- **6 (`contaminado_por_bug`)**: pertenecían a `observation_id` que también aparecen en el pool KNOWN `Dendropsophus_molitor` (ver lista completa de 34 `observation_id` contaminados en la Parte 1). El usuario, sin saberlo, ya había limpiado 6 de las 56 imágenes contaminadas originales al momento de esta auditoría (quedan 50 contaminadas todavía en disco).
  - `col_obs_373025436_photo_681683401.jpg`
  - `col_obs_373092737_photo_681812477.jpg`
  - `col_obs_373094275_photo_681815521.jpg`
  - `col_obs_373457992_photo_682516168.jpg`
  - `col_obs_374130656_photo_683802225.jpg`
  - `col_obs_383929385_photo_702740737.jpg`
- **4 (`limpieza_calidad_normal`)**: las 4 imágenes de la observación `380176757`, que NO está en la lista de contaminación (su `observation_id` no aparece en `data cleaned/Dendropsophus_molitor/`). Borrado por motivo de calidad visual, no relacionado con el bug.

## Nota importante sobre los embeddings congelados

**Todas las imágenes borradas (35 en total) siguen presentes en `unknown_embeddings.npz`** — los embeddings se extrajeron antes de las deleciones manuales, por lo que cualquier resultado ya reportado de Fase 23A/GEO-1→6 que use ese `.npz` tal cual sigue incluyendo estas 35 imágenes (tanto las contaminadas como las de limpieza de calidad normal). El `.npz` original no fue modificado en esta sesión.

## Recomendación

Para ambas especies y ambos motivos (`contaminado_por_bug` y `limpieza_calidad_normal`): **los 35 archivos deben permanecer excluidos definitivamente del dataset "primary"**. Las 25 de Rhinella_marina y las 4 "normales" de labialis fueron descartadas por el usuario por motivo de calidad visual — motivo válido e independiente del bug de etiquetado, no hay razón para restaurarlas. Las 6 contaminadas de labialis ya fueron correctamente removidas del pool aunque el usuario no supiera aún la razón exacta; se confirma aquí que esa remoción fue correcta también desde la óptica del bug.

## Archivo de datos

`USER_MANUAL_DELETIONS_RECONCILIATION.csv` — 35 filas: especie, archivo, `observation_id`, estado (`contaminado_por_bug` / `limpieza_calidad_normal`), confirmación de presencia en `unknown_embeddings.npz` (todas: SI), recomendación (todas: `EXCLUIR_DEFINITIVAMENTE_DE_PRIMARY`).
