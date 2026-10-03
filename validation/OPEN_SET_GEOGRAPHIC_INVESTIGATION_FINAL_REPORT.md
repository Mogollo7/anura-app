# Open Set + contexto geográfico/topográfico — Reporte consolidado de cierre

**Estado final: `CLOSED — GEOGRAPHY_NOT_SUFFICIENT`**
**Fecha:** 2026-09-14
**Alcance:** Fases 23A (oficial), GEO-1→GEO-6, `open_set_topography_v1`, corrección de contaminación por etiquetado (`fase23a_delabeling_correction_v1`).

Este documento cierra la línea de investigación completa sobre si el contexto geográfico (zona biogeográfica, elevación, pendiente, relieve, frecuencia de especie) puede mejorar la detección Open Set (KNOWN vs UNKNOWN) de ANURA/SITRana en Antioquia. Consolida ~10 experimentos ejecutados en secuencia, cada uno construido sobre las correcciones del anterior.

---

## 1. Baseline oficial (Fase 23A)

- Encoder: `bioclip_anura_mejor.pt`, SHA256 `98a6c54d...` (verificado, congelado, nunca modificado).
- 620 imágenes UNKNOWN (7 especies) vs 7,475 imágenes KNOWN (24 especies), embeddings 512-D.
- **AUROC visual puro (euclidean_raw) = 0.57329** — reproducido exacto (diff=0.0) en cada fase posterior como gate obligatorio.
- FAR/FRR en el umbral Youden-J: FAR=51.6%, FRR=37.3%, Balanced Accuracy=55.6%.

Este número es la referencia inmutable contra la que se midió todo lo demás.

---

## 2. Línea GEO — contexto geográfico por zona biogeográfica

| Fase | Qué probó | Resultado |
|---|---|---|
| **GEO-1** (auditoría) | Localizó infraestructura geográfica reutilizable de Antioquia (4 zonas biogeográficas, prior P(especie\|zona) con smoothing, 15,081 registros GBIF+iNaturalist). Confirmó que ni las 620 UNKNOWN ni las 7,475 KNOWN tenían lat/lon vinculada directamente, pero sí `observation_id` recuperable vía API. | Infraestructura reutilizable confirmada; recuperación de coordenadas vía API viable. |
| **GEO-2/V2** | Prior geográfico purgado de contaminación cruzada (1,214 registros excluidos). Barrido de pesos visual+geo. | AUROC subía hasta w_geo=0.9 → **0.701** (IC95% [0.673,0.730]). **Este número resultó estar inflado por un oráculo (ver §4) — valor honesto real ≈0.617.** |
| **GEO-3** | Curva de threshold completa (sin fijar FRR=5%), puntos operativos FAR≤50/30/20/10/5%. | Ningún punto operativo tiene Precision aceptable (9-14% en todos, por desbalance de clases 620 vs 7,475). Cobertura de zona: 42% UNKNOWN, 37% KNOWN — techo estructural, no mejorable con más scraping (100% de los observation_id relevantes ya estaban en cache). |
| **GEO-4** | Añadir género y familia como señales adicionales al score (prior jerárquico). | **`HARMFUL`** — Top-1 cae de 0.634 a 0.411, AUROC Open Set cae a ~0.55-0.57 (vuelve casi al baseline). Los priors de género/familia son demasiado gruesos y arrastran las predicciones hacia la especie más común del género. **Descartado definitivamente.** |
| **GEO-5** | Escalar de 24 a las 291 especies reales del catálogo regional de Antioquia (auditoría reveló que el catálogo real es 291, no ~29 como se asumía). | Solo 33/291 especies tienen embeddings evaluables, 21/291 tienen set KNOWN curado. La mejora Open Set de GEO-2 se sostiene al escalar (el prior ya cubría las 291 especies desde su construcción), pero **el mismo peso w_geo=0.9 que ayuda al Open Set perjudica el ranking de identificación cerrada** — primera señal clara de que ranking y decisión Open Set son dos problemas distintos. |
| **GEO-6** | Arquitectura de dos etapas: ranking (w_geo_rank bajo, 0.0-0.3) separado de la decisión Open Set (w_geo_open_set=0.9). | **`HELPFUL`** como arquitectura — resuelve el conflicto de GEO-5: ranking mejora (Top-1 0.585→0.662, MRR 0.7145→0.7741) y Open Set también mejora sobre el baseline visual simultáneamente, sin sacrificar uno por el otro. Al corregir el bug de threshold degenerado se descubrió el problema del oráculo (ver §4): AUROC honesto de la arquitectura de dos etapas ≈0.603, no 0.701. |

---

## 3. Contexto topográfico real (elevación, pendiente, relieve) — línea paralela

`validation/open_set_topography_v1/` probó una hipótesis más fuerte que GEO-1→3: en vez de solo zona biogeográfica, usó **elevación, pendiente, orientación (seno/coseno), relieve local y rugosidad** por coordenada (OpenTopoData SRTM 30m), con un protocolo de calibración independiente (2,545 KNOWN + 130 UNKNOWN, separado de Fase 23A) y una regla visual congelada de dos prototipos + margen.

**Resultado: `NO_GO`.**

| | FAR | Cambio |
|---|---|---|
| Visual solo (Fase 23A completa) | 36.94% | — |
| Visual + topografía completa | 36.77% | **-0.16 puntos, 1 solo caso** |

En la calibración (donde hay clases balanceadas) el efecto es exactamente cero: FAR 4.62% antes y después. Este es el resultado más contundente de toda la investigación: incluso con la señal geográfica más rica posible (no solo zona, sino relieve y topografía real), **el contexto geográfico no corrige el solapamiento visual**.

---

## 4. Hallazgo crítico: el bug del oráculo (corrección GEO-2/GEO-3)

Al depurar GEO-6 se descubrió que el cálculo histórico de GEO-2/GEO-3 (AUROC≈0.701) usaba, para las imágenes KNOWN, la **especie real (ground truth)** como entrada para consultar el prior geográfico — información que no existe en inferencia real, donde solo se tiene la especie *predicha* visualmente.

- **0.701** = resultado histórico/diagnóstico, afectado por información privilegiada (oráculo). **No debe citarse como rendimiento de producción.**
- **≈0.617** = referencia honesta, reproducible sin ground truth (usando la especie predicha).

Documentado formalmente en `validation/fase23a_geographic_context/GEO2_GEO3_CORRECTION_NOTE.md`. No invalida que exista señal geográfica (0.617 sigue siendo mejor que el 0.573 visual puro), pero corrige la magnitud: la mejora real es aproximadamente **la mitad** de lo que se pensaba inicialmente.

---

## 5. Contaminación de datos descubierta durante la auditoría manual

Durante la revisión visual manual del usuario se encontraron dos problemas de integridad de datos, ambos investigados y cerrados:

### 5.1 Bug de etiquetado *Dendropsophus labialis* / *Dendropsophus molitor*
- **34 de 43 observation_id (79.1%)** de la especie UNKNOWN *D. labialis* son la misma observación real de iNaturalist que ya existe en el pool KNOWN como *D. molitor* — 56 de 74 imágenes afectadas.
- Causa raíz: el `leakage_audit.csv` oficial del proyecto compara solo por SHA256 exacto, ciego a la misma observación re-descargada/re-codificada en momentos distintos. Además, *D. labialis* fue sinonimizada por completo con *D. molitor* en iNaturalist después de construirse el dataset (taxón inactivo, verificado vía API) — no hay población nueva que scrapear.
- **Rebaseline tras purgar la contaminación: AUROC 0.5733 (oficial, 620 img) → 0.5713 (corregido, 564 img). Diferencia -0.002, no significativa (IC95% se solapan casi por completo).**
- **Conclusión: el bug era real y se corrigió por integridad científica, pero no era la causa del FAR alto.**

Documentado en `data/unknown_open_set_v2/audit/LEAKAGE_AUDIT_CORRECTION_v2.md` y `USER_MANUAL_DELETIONS_RECONCILIATION.md`.

### 5.2 Par *Rhinella marina* / *Rhinella horribilis*
- Confirmado como **taxonómicamente válido** (ambas especies resuelven ACCEPTED contra GBIF backbone, `taxon_id` distintos: COL_ANURA_0065 vs COL_ANURA_0003) — no es un bug de datos, es solapamiento visual genuino entre especies hermanas.
- Es el mayor contribuyente individual a los falsos aceptados: **60/228 (26.3%)** del reporte topográfico.
- Verificación de elevación: *R. marina* 25-2,500m (mediana 473m) vs *R. horribilis* 4.5-2,467m (mediana 1,060m) — **rangos casi totalmente solapados**, sin margen para separarlas geográfica o altitudinalmente.
- Al excluirla del cómputo (solo como diagnóstico, no como intervención de producción): AUROC sube de 0.5733 a **0.6156** (+0.042, IC95% ya casi no se solapan). Confirma que esta especie concentra una parte real y grande de la dificultad del problema — pero no es corregible con datos ni con geografía.

---

## 6. Solapamiento visual — mapa completo de los 228 falsos aceptados

23 pares distintos de especies causan los 228 falsos aceptados; 6 pares concentran el 84% (191/228):

| Especie UNKNOWN | Confundida con (KNOWN) | Frecuencia | Naturaleza |
|---|---|---|---|
| *Rhinella marina* | *Rhinella horribilis* | 60 | Confusión visual genuina, especies hermanas válidas |
| *Dendropsophus labialis* | *Dendropsophus molitor* | 47 | **Bug de etiquetado (§5.1), ya corregido/documentado** |
| *Craugastor metriosistus* | *Craugastor raniformis* | 23 | Confusión visual, sin auditar en detalle |
| *Espadarana prosoblepon* | *Hyloscirtus palmeri* | 22 | Confusión visual, sin auditar en detalle |
| *Smilisca phaeota* | *Boana lanciformis* | 21 | Confusión visual, sin auditar en detalle |
| *Leptodactylus fragilis* | *Leptodactylus colombiensis* | 17 | Confusión visual, sin auditar en detalle |

Rutas de imagen para revisión manual en `validation/open_set_topography_v1/VISUAL_OVERLAP_AUDIT.md` y `VISUAL_OVERLAP_PAIRS.csv`.

---

## 7. Veredicto consolidado

**Cuatro líneas de evidencia independientes, con protocolos distintos, llegan a la misma conclusión:**

1. GEO-1→3 (zona biogeográfica + prior bayesiano): señal débil/moderada, techo estructural de cobertura (42%).
2. GEO-4 (género/familia): activamente dañino.
3. GEO-5/GEO-6 (escala completa + arquitectura de dos etapas, corregida de oráculo): mejora honesta ≈+0.03 a +0.05 AUROC, no resuelve el FAR operativo.
4. `open_set_topography_v1` (elevación/pendiente/relieve real, protocolo de calibración independiente): **NO_GO**, cambio de 0.16 puntos porcentuales de FAR.
5. Verificación directa de elevación para el par que domina el problema (*Rhinella marina*/*horribilis*): rangos casi idénticos, sin separación posible.

**El cuello de botella del Open Set de ANURA es solapamiento real en el espacio de embeddings visuales de BioCLIP, concentrado en un número pequeño de pares de especies morfológicamente casi gemelas — no falta de contexto geográfico, elevación, ni volumen de datos.**

Inyectar más datos de iNaturalist estratificados por zona/altura no va a crear separación donde biológicamente no existe (especies que genuinamente coexisten en el mismo rango). **Se cierra esta línea de investigación.**

---

## 8. Siguiente paso recomendado

No geográfico. Dos caminos, en orden de costo creciente:

1. **Rejector aprendido** sobre los embeddings ya existentes — un clasificador binario KNOWN/UNKNOWN entrenado sobre los 512-D ya extraídos, sin tocar el encoder ni requerir fine-tuning. Más barato y rápido de probar.
2. **Mejora del embedding vía hard negatives / fine-tuning dirigido**, específicamente a los pares identificados en §6 (*Rhinella marina*/*horribilis* como prioridad, dado que concentra el mayor efecto). Requiere protocolo nuevo, toca el encoder — más costoso pero ataca la causa raíz.

---

## 9. Artefactos de toda la investigación (índice)

```
validation/fase23a_open_set_automatic/          — Fase 23A oficial (congelado, fuente de verdad)
validation/fase23a_geographic_context/          — GEO-1 a GEO-6
  GEO2_GEO3_CORRECTION_NOTE.md                  — corrección del bug de oráculo
  GEO6_REPORT.md, GEO6_COMPARISON.md            — arquitectura de dos etapas final
validation/open_set_topography_v1/              — contexto topográfico real (elevación/relieve), NO_GO
  VISUAL_OVERLAP_AUDIT.md, VISUAL_OVERLAP_PAIRS.csv — mapa de los 228 falsos aceptados
data/unknown_open_set_v2/audit/
  LEAKAGE_AUDIT_CORRECTION_v2.md                — bug de etiquetado Dendropsophus
  USER_MANUAL_DELETIONS_RECONCILIATION.md       — reconciliación de limpieza manual
validation/fase23a_delabeling_correction_v1/    — rebaseline post-corrección + exclusión Rhinella
  rhinella_exclusion_comparison.json            — evidencia cuantitativa del §5.2
```

**Nada de lo anterior modificó Fase 23A, el encoder, los embeddings oficiales, ni producción. Ningún artefacto fue commiteado.**
