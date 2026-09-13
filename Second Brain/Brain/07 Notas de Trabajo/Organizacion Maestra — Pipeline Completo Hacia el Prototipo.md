# OrganizaciÃ³n Maestra â€” Pipeline Completo Hacia el Prototipo

**Fecha:** 2026-09-11 | **Deadline:** 2026-09-27 (16 dÃ­as restantes)

Mapa completo de dÃ³nde estamos y quÃ© falta, en orden de ejecuciÃ³n. Cada etapa indica su estado, dependencias, y el archivo/script responsable.

---

## Estado general

```
âœ… COMPLETADO   ðŸ”„ EN PROGRESO   â³ PENDIENTE   ðŸš« BLOQUEADO
```

| # | Etapa | Estado | Bloqueada por |
|---|---|---|---|
| 0-1 | Entorno + validar BioCLIP v1 | âœ… | â€” |
| 2-3 | Embeddings de muestra + Baseline zero-shot (70,4% Top-1) | âœ… | â€” |
| â€” | Limpieza de dataset (duplicados, fusiÃ³n de individuos, taxonomÃ­a) | âœ… | â€” |
| â€” | Crecimiento de catÃ¡logo 28â†’41 especies (mismo gÃ©nero) | âœ… | â€” |
| 4 (variante A) | Transfer Learning sin segmentar | âœ… (inconcluso: 69,2%, empate con baseline) | â€” |
| **SegmentaciÃ³n (H4)** | Entrenar segmentador rana/fondo | âœ… **IoU test 83,3%, Gate 1 OK (gap +2,4%)** | â€” |
| **Gate 2** | Aplicar segmentador a 41 especies + validar foreground | âœ… **40/41 especies OK** (Dendrobates_truncatus 23,1% degeneradas, se procede igual) | â€” |
| 4 (variante C) | Transfer Learning CON segmentaciÃ³n | âš ï¸ **Top-1 esp 58,6% (41 especies)** | â€” |
| **Experimento control** | k-NN zero-shot, recorte vs completa, mismas 41 especies | âŒ **El recorte DAÃ‘A: âˆ’9,1pp Top-1** (51,5% completa vs 42,5% recortada) | â€” |
| **4 (variante A, 41 especies)** | Transfer Learning sin recorte, catÃ¡logo completo | â³ **SIGUIENTE PASO** â€” es la config que combina TL efectivo + datos sin degradar | â€” |
| 5 | EvaluaciÃ³n completa (matriz confusiÃ³n, F1 por especie) | â³ | Fase 4 variante C |
| 6 | Extraer encoder (`model.visual`) | â³ | Fase 5 |
| 7-8 | Exportar ONNX + verificar + cuantizar FP16 | â³ | Fase 6 |
| 9 | Generar paquetes de embeddings regionales | â³ (script ya listo) | Fase 6-8 |
| 10 | IntegraciÃ³n Android + SQLite-vec | â³ | Fase 9 |
| 11 | Pruebas en dispositivo real | â³ | Fase 10 |
| 12 | IteraciÃ³n / pulido final | â³ | Fase 11 |

---

## Detalle de cada etapa pendiente

### ðŸ”„ SegmentaciÃ³n (H4) â€” EN PROGRESO AHORA

**QuÃ©:** Entrenar un segmentador rana/fondo usando 827 pares reales (`D:\Anura\Mascara\Original` + `Mask`, mÃ¡scara real vÃ­a canal alfa, sin necesitar CVAT).

**Script:** `segmentacion/entrenar_segmentador.py` â€” DeepLabV3+ResNet50 (potente, sin restricciÃ³n mÃ³vil porque solo corre en PC una vez).

**Output esperado:** `segmentacion/checkpoints/segmentador_mejor.pt`, con IoU de validaciÃ³n reportado.

**Siguiente paso automÃ¡tico:** aplicar este segmentador a las **41 especies completas** del dataset principal (`data dirty/`) para generar los recortes de variante C.

---

### â³ Fase 4 variante C â€” Transfer Learning con segmentaciÃ³n

**QuÃ©:** Repetir `bioclip/scripts/fase_4_transfer_learning.py` pero con `--masks-dir` apuntando a las mÃ¡scaras generadas automÃ¡ticamente por el segmentador sobre las 41 especies.

**ConfiguraciÃ³n ya validada (usar tal cual):**
- Dropout 0.4 en cabezas
- Weight decay 0.05 (cabezas) / 0.02 (backbone)
- Paciencia 2 (early stopping agresivo)
- GradScaler FP16, persistent_workers, logging de VRAM

**Cabeza de especie:** 41 salidas (no 28, no 43 â€” huÃ©rfanas excluidas).

**MÃ©trica de Ã©xito:** Top-1 especie DEBE superar claramente el baseline zero-shot (70,4%) â€” si no lo hace, seÃ±al de que algo mÃ¡s necesita ajuste antes de seguir a Fase 6.

---

### â³ Fase 5 â€” EvaluaciÃ³n completa

Matriz de confusiÃ³n, F1 por especie, identificar pares confundibles (ya sabemos que `Pristimantis_achatinus`/`paisa` lo eran en variante A â€” verificar si segmentaciÃ³n lo resuelve).

---

### â³ Fase 6 â€” Extraer encoder

Tomar `model.visual` del mejor checkpoint de Fase 4 variante C. Descartar las 3 cabezas de clasificaciÃ³n (ya cumplieron su funciÃ³n).

---

### â³ Fase 7-8 â€” ONNX + FP16

Exportar `model.visual` a ONNX, verificar equivalencia PyTorchâ†”ONNX (cosine similarity >0.99), cuantizar a FP16 (~173 MB objetivo).

---

### â³ Fase 9 â€” Paquetes regionales

**Script ya construido:** `paquetes_regionales/generar_embeddings.py` â€” soporta crecimiento incremental, taxonomÃ­a dinÃ¡mica, encoder desacoplado. Solo falta apuntarlo al encoder final de Fase 6-8 y correrlo sobre las 41 especies (+ las que se agreguen despuÃ©s vÃ­a el gate de validaciÃ³n documentado).

---

### â³ Fase 10-11 â€” Android + pruebas reales

IntegraciÃ³n ONNX Runtime + SQLite-vec en la app, pruebas en Samsung Galaxy A30 / Redmi Note 13 Pro+.

---

### â³ Fase 12 â€” Pulido

Ajustes finales, posible extensiÃ³n a especies adicionales vÃ­a el pipeline de crecimiento ya documentado.

---

## Decisiones ya tomadas que NO hay que reabrir

1. **41 especies** (no 28, no 43) â€” Hyloxalus_picachos y Sachatamia_electrops excluidas por ser huÃ©rfanas + tener problemas de integridad de datos
2. **GroupSplit con fusiÃ³n de individuos duplicados** â€” 118 clusters de obs_id fusionados, ya aplicado en `prepare_dataset.py`
3. **Especies de crecimiento (15 nuevas) van directo a la cabeza de especie**, no como auxiliares descartables â€” son alcance real del catÃ¡logo
4. ~~**SegmentaciÃ³n con modelo potente (DeepLabV3) para preparar datos**~~ â†’ **REVISADA 2026-09-11 noche.** El segmentador se entrenÃ³ bien (IoU 83,3%) pero el experimento controlado demostrÃ³ que el **recorte ajustado daÃ±a los embeddings (âˆ’9,1pp Top-1)**. La premisa de C-9 era falsa. El segmentador NO se descarta como herramienta, pero el recorte al bounding box no es el uso correcto. Si hay tiempo, explorar recorte con margen amplio (padding 50-100%) que conserve contexto
5. **Gate de validaciÃ³n obligatorio** antes de desplegar cualquier especie nueva post-lanzamiento (Top-1/Top-3 sobre fotos reservadas)

## âœ… SelecciÃ³n manual sobre `data cleaned` â€” HECHA (2026-09-12)

Pasada manual completada: se borraron 5,096 fotos (29% del dataset, borrosas/mal encuadradas/mal identificadas) y se eliminÃ³ `_cuarentena` completa (216 fotos sin taxÃ³n). `training/sincronizar_dataset.py` (nuevo) sincroniza `dataset_limpio.json` con lo que queda en disco tras una limpieza manual, sin reprocesar desde `data dirty` (eso revertirÃ­a la selecciÃ³n).

**Resultado:** 12,256 imÃ¡genes limpias. 4 especies quedaron con muy pocos individuos reales: `Dendropsophus_norandinus` (11), `Pristimantis_vilarsi` (32/56 segÃºn corte). Compensado con oversampling (ver abajo).

## âœ… Oversampling fijo a 70 individuos/especie en train â€” HECHO (2026-09-12)

`training/prepare_dataset.py` ahora rellena el split de TRAIN de cada especie hasta **70 individuos exactos** (`oversamplear_train`): si hay â‰¥70, corta (como antes); si hay menos, repite individuos con reemplazo hasta llegar a 70. Val/test nunca se tocan â€” deben reflejar la escasez real. El mismo nÃºmero (70) es techo y piso para todas las 41 especies del catÃ¡logo.

Cada entrada repetida se marca `"aumentada": true` en `manifiesto.json`. `bioclip/scripts/fase_4_transfer_learning.py` lee esa marca y aplica una transform **mÃ¡s agresiva** (crop hasta 40%, rotaciÃ³n Â±30Â°, color jitter +40%, oclusiÃ³n mayor) solo a esas repeticiones â€” asÃ­ una especie con 11 individuos reales (`Dendropsophus_norandinus`, +62 repeticiones) no ve 62 copias con augmentation idÃ©ntica a las de una especie abundante.

Manifiesto regenerado sobre `data cleaned` (post-limpieza manual): **train 5,215 imgs / 1,806 individuos** (70 por especie garantizado), val 697/376, test 766/401. 0 fugas entre particiones.

18 de 41 especies necesitaron oversampling (de +24 a +62 repeticiones); las 23 restantes ya tenÃ­an â‰¥70 individuos reales.

**Campo `sexo` retirado:** el campo `sexo` del registro de `dataset_limpio.json` se eliminÃ³ â€” no se usÃ³ en ninguna etapa del pipeline de entrenamiento (`prepare_dataset.py` no lo consume) y su cobertura real era nula (0 de 17 352 registros tenÃ­an valor). El esquema de `limpiar_dataset.py` ahora reutiliza `taxonomia.py` (mismo gÃ©nero/familia/especie canÃ³nicos que `prepare_dataset.py`) en vez de leer `taxon_info.json` por carpeta, para que el inventario limpio y el manifiesto de entrenamiento no diverjan.

---

## Pregunta abierta pendiente de resolver antes de Fase 10

Â¿La segmentaciÃ³n se aplica SOLO para preparar el dataset de entrenamiento (Fase 4), o tambiÃ©n hace falta en producciÃ³n (cuando el usuario toma una foto real en la app)? Si el encoder final se entrena con fotos recortadas (variante C), la app en producciÃ³n tambiÃ©n necesitarÃ­a recortar la foto del usuario ANTES de pasarla al encoder â€” eso implica desplegar tambiÃ©n un segmentador en el mÃ³vil (el YOLOv8n-seg original planeado), no solo el de preparaciÃ³n de datos. Pendiente de decidir en Fase 9-10.

**Nota (2026-09-11 noche):** dado que el recorte demostrÃ³ daÃ±ar los embeddings (ver secciÃ³n "Experimento control" arriba), esta pregunta pierde urgencia â€” si variante A (sin recorte) es la ruta ganadora, no hace falta segmentar en producciÃ³n en absoluto.

---

## âœ… Filtro `quality_grade=research` de iNaturalist â€” YA APLICADO

**Estado (2026-09-11 noche):** implementado y activo por defecto en `scraper_inaturalist.py` (`--quality-grade research`, `research` es el valor por defecto). El contenido de `D:\Anura\data cleaned` ya proviene de observaciones filtradas con este criterio. Se retira de la lista de pendientes.

**Origen:** el usuario preguntÃ³ si filtrar por `quality_grade=research` (ej. `https://www.inaturalist.org/observations?quality_grade=research&taxon_id=<id>`) mejorarÃ­a la calidad de las fotos scrapeadas.

**QuÃ© es realmente este filtro:** NO es un filtro de nitidez/calidad de imagen. Una observaciÃ³n llega a "research grade" cuando tiene foto/sonido verificable Y al menos 2 identificadores coinciden (â‰¥2/3 de consenso). Es un filtro de **confianza de identificaciÃ³n taxonÃ³mica**, no de calidad fotogrÃ¡fica.

**Por quÃ© es relevante para nosotros de todas formas:**
- Existe correlaciÃ³n indirecta con calidad de imagen: fotos borrosas/mal encuadradas tienden a quedarse en 
eeds_id` porque nadie puede confirmar la especie con confianza
- **HabrÃ­a prevenido directamente el caso `Cochranella_albomaculata.jpg` mal etiquetado dentro de `Sachatamia_electrops`** (ver hallazgo de integridad de datos, secciÃ³n "Segundo hallazgo" en `Proceso de Crecimiento del CatÃ¡logo Post-Despliegue.md`) â€” research grade exige consenso de identificaciÃ³n
- NO habrÃ­a prevenido los duplicados exactos ni la fuga de datos por obs_id distintos con la misma foto (eso es un problema de gestiÃ³n de datos, no de identificaciÃ³n)

**Trade-off:** reduce el pool de fotos disponibles. Varias especies ya luchan por llegar a 70 individuos (`Dendropsophus_norandinus`: 11, `Hyloxalus_picachos`: ~14 tras limpieza) â€” aplicar este filtro agravarÃ­a la escasez en las especies mÃ¡s dÃ©biles.

**RecomendaciÃ³n (no implementada aÃºn):** agregar `--quality-grade research` como parÃ¡metro opcional en `scraper_inaturalist.py` (actualmente usa `has[]=photos` sin filtro de calidad). Usar el filtro para especies con abundancia de datos donde sobra margen; mantener el fallback sin filtro para las especies escasas donde no se puede sacrificar volumen. Pendiente de implementar si se hace una ronda futura de scraping.



