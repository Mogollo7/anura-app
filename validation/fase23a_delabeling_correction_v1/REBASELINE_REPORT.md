# Rebaseline Fase 23A — corrección de contaminación de etiquetado Dendropsophus_labialis/molitor

Fecha: 2026-09-14
Ver contexto completo del bug en `data/unknown_open_set_v2/audit/LEAKAGE_AUDIT_CORRECTION_v2.md` y reconciliación de deleciones manuales en `data/unknown_open_set_v2/audit/USER_MANUAL_DELETIONS_RECONCILIATION.md`.

## Método

Reutilizado exactamente `validation/fase23a_geographic_context/scripts/phase_reproduce_23a.py` (min-distancia euclidiana a 41 centroides de especie; KNOWN pool = `fase16_clean_open_set/clean_known_embeddings.npz`, 7475 imágenes, sin cambios; centroides desde `reference_embeddings.npz` + `train_embeddings.npz`, sin leave-one-out). Implementado en `rebaseline_delabeling_fixed.py`.

UNKNOWN pool "v2_delabeling_fixed" = 620 imágenes originales de `unknown_embeddings.npz` **menos** las 56 imágenes de *Dendropsophus_labialis* cuyo `observation_id` coincide con una observación ya presente en el pool KNOWN *Dendropsophus_molitor* (34 `observation_id` contaminados de 43 totales de labialis — ver Parte 1). Todas las demás especies, incluida *Rhinella_marina* completa (83 imágenes), quedan sin cambios.

## Resultado — AUROC

| | Oficial (620 img UNKNOWN) | Corregido v2_delabeling_fixed (564 img UNKNOWN) |
|---|---|---|
| AUROC | **0.573292** | **0.571277** |
| Bootstrap media (1000 iter, seed=42, estratificado por individuo) | 0.573633 | 0.571246 |
| IC95% | [0.546279, 0.604829] | [0.537749, 0.600815] |
| FAR (umbral Youden-J oficial) | 51.61% | 51.42% |
| FRR (mismo umbral) | 37.26% | 37.26% |
| Balanced Accuracy | 55.56% | 55.66% |

**Diferencia de AUROC: -0.00201** (el AUROC corregido es ligeramente *menor*, no mayor). Los intervalos de confianza al 95% se solapan casi por completo — **la diferencia NO es estadísticamente significativa**.

## Interpretación honesta

Purgar los 34 `observation_id` contaminados de *Dendropsophus_labialis* (56 imágenes de 620, 9.0% del pool UNKNOWN) **no mejora el AUROC visual puro de forma perceptible**, y de hecho lo reduce ligeramente. Esto tiene sentido: las imágenes contaminadas eran, precisamente, observaciones que SON *Dendropsophus molitor* en la realidad — su embedding está cerca del centroide de *D. molitor* casi por definición, lo cual las hacía *fáciles* de aceptar falsamente como KNOWN (contribuían a FAR alto, sí, pero eran una fracción relativamente pequeña de las 620 imágenes UNKNOWN totales, y removerlas no cambia sustancialmente la distribución agregada de distancias porque los demás pares de confusión —sobre todo Rhinella— dominan el volumen de falsos aceptados).

El par de confusión **Rhinella_marina/Rhinella_horribilis (60/228 = 26.3% de los falsos aceptados en `TOPOGRAPHIC_CONTEXT_REPORT.md`) sigue intacto y sin cambios** en este rebaseline — es el mayor contribuyente individual al FAR, y es una confusión visual genuina entre dos especies reales y distintas (0 coincidencias de `observation_id` con el pool KNOWN), no arreglable con limpieza de etiquetas ni con más datos de la misma naturaleza.

**Conclusión: el bug de etiquetado labialis/molitor era real, estaba bien documentado por el trabajo previo de esta sesión, y se corrigió correctamente aquí — pero NO es la causa dominante del AUROC bajo (0.57) ni del FAR alto (~51-52%) reportado en Fase 23A/GEO-1→6.** Esos números reflejan mayormente separabilidad visual genuinamente pobre entre el espacio de embeddings de las 41 especies KNOWN y las especies UNKNOWN evaluadas (liderado por Rhinella), no un artefacto de datos corregible. No se debe presentar la corrección de este bug como una mejora sustancial del pipeline de open-set.

## Dendropsophus_labialis: ¿quedan datos suficientes como especie UNKNOWN individual?

Después de excluir la contaminación, quedan **18 imágenes / 9 observation_id únicos** limpios de *Dendropsophus_labialis* (ver `dendropsophus_labialis_clean_count.json`). Esto está por debajo del umbral práctico mínimo razonable (~10 observaciones / ~15 imágenes) para tratar la especie como un caso UNKNOWN individual estadísticamente útil — 9 observaciones es una muestra demasiado pequeña para estimar FAR/FRR específico de esta especie con márgenes de error razonables.

**Limitación documentada explícitamente**: cualquier métrica futura reportada específicamente para *Dendropsophus_labialis* como especie UNKNOWN individual (no agregada con las demás 8 especies del pool) debe tratarse como no concluyente por tamaño de muestra insuficiente.

## Parte 4 — Scraping de reemplazo: NO realizado

Se investigó si existía infraestructura de scraping reutilizable: **sí existe**, `scraper_inaturalist.py` en la raíz del repositorio (clase `INaturalistScraper`, soporta `--species`, `--output`, `--delay`, `--quality-grade`, respeta rate limiting configurable). Se verificó acceso de red a la API de iNaturalist (funcional).

Sin embargo, **no se ejecutó ningún scraping**, porque se descubrió durante la verificación previa que **"Dendropsophus labialis" ya no existe como taxón activo separado en la taxonomía actual de iNaturalist**:

- `GET /v1/taxa?q=Dendropsophus+labialis&rank=species` devuelve un único resultado: `taxon_id=1595931`, cuyo nombre actual es **"Dendropsophus molitor"** (activo).
- `GET /v1/taxa?q=Dendropsophus+labialis&is_active=any` revela dos `taxon_id` históricos para "labialis" (65363 y 555168), **ambos inactivos**, con `current_synonymous_taxon_ids: [1595931]` — es decir, iNaturalist los redirige formalmente al taxón "Dendropsophus molitor".
- `GET /v1/observations?taxon_id=65363` y `taxon_id=555168` (Colombia) devuelven **0 resultados** — todas las observaciones históricamente etiquetadas como "labialis" fueron migradas por iNaturalist al taxón activo "molitor". No queda ninguna observación accesible bajo el taxón original.

En otras palabras: **la fuente de datos original (iNaturalist) sinonimizó por completo "Dendropsophus labialis" con "Dendropsophus molitor"** — la misma especie que ya está en el catálogo KNOWN. Esto no es solo "pocos datos disponibles"; es que **no existe ya una población de datos "Dendropsophus labialis" genuinamente distinta de la que se pueda scrapear** — cualquier búsqueda actual por ese nombre devuelve observaciones de *D. molitor*. Ver el detalle completo en `scraping_decision_no_supplement.json`.

Esto además **refuerza la causa raíz documentada en la Parte 1**: el bug de contaminación no fue un accidente de pipeline, sino síntoma de un proceso de sinonimización taxonómica que ya estaba en curso en iNaturalist en el momento de las descargas originales del dataset, y que hoy está completo.

**Decisión**: no se hizo scraping, siguiendo la instrucción explícita del usuario de no scrapear innecesariamente cuando no aporta valor. Forzar una descarga adicional bajo el nombre "Dendropsophus labialis" no habría producido datos nuevos y distintos — solo más observaciones de *D. molitor* re-etiquetadas, repitiendo el mismo problema.

## Recomendación para el equipo (fuera de alcance de esta tarea, no ejecutada)

Dado que la taxonomía fuente ya no reconoce "Dendropsophus labialis" como especie separada de "Dendropsophus molitor" (KNOWN), el equipo debería evaluar si esta categoría UNKNOWN debe seguir existiendo en el pipeline de open-set, o si debe retirarse/fusionarse — mantenerla invita a repetir este mismo tipo de contaminación en cualquier scraping o actualización futura del dataset.

## Artefactos de esta corrección

- `rebaseline_delabeling_fixed.py` — script de recálculo (reutiliza la lógica de `phase_reproduce_23a.py`).
- `rebaseline_metrics.json` — AUROC oficial vs corregido, FAR/FRR/Balanced Accuracy, bootstrap 1000 iter seed=42.
- `dendropsophus_labialis_clean_count.json` — conteo de observaciones/imágenes limpias restantes y evaluación de suficiencia.
- `scraping_decision_no_supplement.json` — evidencia y justificación de por qué no se hizo scraping de reemplazo.
- Este reporte (`REBASELINE_REPORT.md`).

No se modificó ningún artefacto de Fase 23A/GEO-1→6/`open_set_topography_v1`/`merlin_identification_flow`/`fase23a_geographic_context`, ni `unknown_embeddings.npz`, ni ninguna imagen. No hubo reentrenamiento ni cambios al encoder. No se hizo commit/push.
