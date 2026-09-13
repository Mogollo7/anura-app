# Proceso de Crecimiento del CatÃ¡logo Post-Despliegue

**Fecha de diseÃ±o:** 2026-09-11
**Contexto:** Definido durante la expansiÃ³n de 28â†’43 especies en el dataset de entrenamiento. Responde a la pregunta: "una vez la app estÃ© lista, Â¿quÃ© pasa si quiero aÃ±adir 500 especies nuevas?"

Ver [[Fases de ImplementaciÃ³n â€” BioCLIP v1 a On-Device (C-11)]] para el pipeline de entrenamiento base, y `anura_cola_larga_taxonomica.md` (memoria) para el precedente de las 15 especies de crecimiento inicial.

---

## Principio arquitectÃ³nico (patrÃ³n Merlin, Cornell Lab)

El sistema separa dos componentes con ciclos de vida distintos:

| Componente | QuÃ© es | CuÃ¡ndo cambia |
|---|---|---|
| **Image Encoder** (`bioclip_anura_encoder_fp16.onnx`, ~173 MB) | Red neuronal que convierte foto â†’ embedding 512-d | Rara vez â€” solo si se decide una nueva ronda de Transfer Learning |
| **Paquetes regionales** (`.sqlite` con sqlite-vec) | Embeddings de referencia + metadata (especie/gÃ©nero/familia/ubicaciÃ³n) por cada foto conocida | Frecuente â€” cada vez que se agregan especies o fotos nuevas |

En producciÃ³n, la identificaciÃ³n **no usa las cabezas de clasificaciÃ³n softmax** (esas existen solo durante entrenamiento y se descartan al extraer `model.visual` en Fase 6). Usa **k-NN**: la foto del usuario se codifica con el encoder congelado, y se busca el embedding de referencia mÃ¡s cercano en el paquete regional. Esto significa que **el catÃ¡logo de especies identificables lo define el paquete de datos, no el modelo**.

---

## CÃ³mo agregar especies nuevas (mecÃ¡nica)

1. Scrapear fotos de la especie (reusar `scraper_inaturalist.py`, criterio: presencia en Colombia + mÃ­nimo de fotos, `--skip-audio` si no aplica)
2. El scraper regenera `arbol_taxonomico.json` automÃ¡ticamente con la especie nueva
3. Correr `paquetes_regionales/generar_embeddings.py --encoder <checkpoint>` â€” el script:
   - Lee la taxonomÃ­a dinÃ¡micamente (no requiere tocar cÃ³digo)
   - Identifica fotos nuevas por clave Ãºnica (`especie::archivo`) â€” solo procesa lo que no estÃ¡ ya en el paquete
   - Genera embeddings con el encoder **ya entrenado y congelado**
   - Inserta en el `.sqlite` regional correspondiente

**Cero reentrenamiento necesario para este paso.** Es la razÃ³n de ser de la separaciÃ³n modelo/datos.

---

## Los riesgos reales de escalar asÃ­ (500 especies o cualquier lote grande)

"Se puede sin reentrenar" **no implica** "funcionarÃ¡ con buena precisiÃ³n". Los riesgos identificados:

### 1. Distancia taxonÃ³mica/visual del dominio de entrenamiento
El encoder fue afinado especÃ­ficamente para discriminar bien las 43 especies actuales (9 familias, 15 gÃ©neros). Cuanto mÃ¡s se afina hacia un dominio estrecho, menos generalista queda para taxones muy distintos â€” es el mismo trade-off que causÃ³ el overfitting en Fase 4 (ver `resultados_fase4_esquematizado.md`).
- **Riesgo bajo-medio:** especies nuevas del mismo gÃ©nero/familia que ya conocemos (mÃ¡s Hylidae, Strabomantidae/Craugastoridae colombianas)
- **Riesgo alto/incierto:** especies de otros continentes, otros Ã³rdenes, o morfolÃ³gicamente muy distintas â€” el k-NN puede rendir peor que el BioCLIP zero-shot original sin fine-tuning

### 2. ConfusiÃ³n cruzada aumenta con el tamaÃ±o del catÃ¡logo
MÃ¡s especies en la base de referencia = mÃ¡s candidatos "vecino mÃ¡s cercano" que pueden ganarle al correcto por poco margen. Ya observamos esto con el par `Pristimantis_achatinus`/`Pristimantis_paisa` (46% F1, confundibles en Fase 3). Agregar cientos de especies del mismo gÃ©nero multiplica estos pares problemÃ¡ticos.

### 3. Calidad de datos por especie se repite a escala
El problema de "8 especies con <70 individuos" (ver `anura_cola_larga_taxonomica.md`) se repite con cada especie nueva que tenga pocas fotos de referencia confiables. Sin control, un lote de 500 puede terminar con 100 bien resueltas y 400 pobremente representadas.

### 4. Sin seÃ±al automÃ¡tica de degradaciÃ³n
El k-NN no emite una alerta de "esta especie quedÃ³ mal representada". Cada embedding de referencia es un voto literal â€” una foto de referencia mal identificada corrompe silenciosamente ese resultado, sin que nada en el sistema lo detecte hasta que un usuario reporta un error.

---

## Regla obligatoria: gate de validaciÃ³n antes de desplegar cualquier lote

**No desplegar un lote de especies nuevas a usuarios sin antes verificarlo.** El volumen (43, 100, 500) no es el criterio de riesgo â€” la proximidad taxonÃ³mica y la precisiÃ³n medida sÃ­ lo son.

**Proceso de validaciÃ³n (replica la metodologÃ­a de Fase 3):**

1. Reservar un subconjunto de fotos del lote nuevo como "test" (no metidas al paquete regional)
2. Correr una evaluaciÃ³n k-NN igual a `fase_3_baseline.py`: para cada foto de test, verificar si el vecino mÃ¡s cercano en el paquete (incluyendo el lote nuevo) es la especie correcta
3. Medir Top-1 y Top-3 especÃ­ficamente para las especies del lote nuevo
4. **Umbral de decisiÃ³n:**
   - Top-1 aceptable (a definir contra el baseline conocido, ej. >60-65%) â†’ desplegar el lote tal cual, sin tocar el encoder
   - Top-1 pobre â†’ **no desplegar**; es la seÃ±al de que toca una nueva ronda de Transfer Learning incluyendo esas especies como clases reales de entrenamiento (el mismo proceso que se siguiÃ³ al pasar de 28â†’43 especies el 2026-09-11)

### CuÃ¡ndo SÃ toca reentrenar (no solo agregar embeddings)

- La validaciÃ³n del lote nuevo da Top-1/Top-3 inaceptable
- El lote introduce familias/gÃ©neros completamente nuevos sin representaciÃ³n previa en el encoder
- Se acumulan suficientes lotes con datos reales como para justificar una ronda de refinamiento (igual lÃ³gica que "mÃ¡s datos reales combate overfitting" aplicada del lado de producciÃ³n)

---

## Resumen para decisiones futuras

| Pregunta | Respuesta corta |
|---|---|
| Â¿Puedo agregar 500 especies sin reentrenar? | SÃ­, mecÃ¡nicamente â€” el pipeline ya lo soporta |
| Â¿Va a funcionar bien automÃ¡ticamente? | No garantizado â€” depende de proximidad taxonÃ³mica y calidad de datos por especie |
| Â¿CÃ³mo sÃ© si funcionÃ³? | Gate de validaciÃ³n obligatorio (Top-1/Top-3 sobre fotos reservadas) antes de desplegar a usuarios |
| Â¿CuÃ¡ndo reentrenar en vez de solo agregar? | Cuando la validaciÃ³n del lote falla, o cuando se introducen familias/gÃ©neros sin representaciÃ³n previa |

Ver tambiÃ©n: [[anura_architecture_vision_model]] (memoria), `paquetes_regionales/generar_embeddings.py` (implementaciÃ³n).

---

## Nota lateral: bug de taxonomÃ­a detectado y corregido durante esta expansiÃ³n

Al verificar la taxonomÃ­a de las especies nuevas contra `arbol_taxonomico.json` (generado por el scraper desde iNaturalist), se detectÃ³ que `training/taxonomia.py` tenÃ­a **Pristimantis mapeado a Strabomantidae**, cuando el propio `taxon_info.json` de `Pristimantis_achatinus` (parte del dataset original, no de las especies nuevas) ya decÃ­a **Craugastoridae**. Era un error preexistente, no introducido por la expansiÃ³n.

**CorrecciÃ³n aplicada:** `GENERO_A_FAMILIA["Pristimantis"] = "Craugastoridae"`. Esto redujo el vocabulario de familias de 9 a 8 (Strabomantidae no era usada por ningÃºn otro gÃ©nero). Se verificÃ³ cruzando TODOS los `taxon_info.json` disponibles contra `taxonomia.py` â€” sin discrepancias adicionales.

**LecciÃ³n:** la taxonomÃ­a manual en cÃ³digo puede desincronizarse de la fuente real (iNaturalist). El flujo correcto es que `taxonomia.py` derive de `arbol_taxonomico.json`, no al revÃ©s â€” pendiente de refactor si se sigue creciendo el catÃ¡logo.

---

## Segundo hallazgo (misma sesiÃ³n): fuga de datos sistÃ©mica por duplicados perceptuales, y exclusiÃ³n de 2 especies huÃ©rfanas

Al pedir explÃ­citamente cuidar el tope de 70 individuos por especie, se ejecutÃ³ una verificaciÃ³n de duplicados perceptuales (`imagehash.phash`, distancia de Hamming) sobre las 43 especies completas. Resultado: **37 de 43 especies tenÃ­an pares de fotos sospechosas** (458 pares totales), de los cuales **249 eran duplicados exactos** (distancia=0).

**Dos tipos de duplicado exacto encontrados:**
1. Archivo manual (sin patrÃ³n `obs_id`, ej. `large (1).jpg`, fotos de WhatsApp, museo) que resultÃ³ ser copia exacta de una foto ya descargada por el scraper con `obs_id` â€” se resolviÃ³ quedÃ¡ndose con la versiÃ³n de iNaturalist (metadata verificable) y moviendo la manual a `data dirty/_cuarentena/<especie>/`.
2. **MÃ¡s grave:** dos observaciones de iNaturalist con `obs_id` DISTINTO que comparten una foto idÃ©ntica â€” evidencia de que son el mismo evento/individuo reportado dos veces. Se detectaron **118 clusters** (247 obs_id) de este tipo. Sin corregir esto, el GroupSplit los trataba como individuos diferentes â€” el chequeo "0 grupos repartidos entre particiones" NO detectaba este problema porque cada obs_id, individualmente, sÃ­ quedaba en una sola particiÃ³n; el problema era que dos obs_id distintos eran, en realidad, el mismo individuo.

**CorrecciÃ³n aplicada:** `training/prepare_dataset.py` ahora acepta `training/individuos_fusionar.json` (generado por el anÃ¡lisis de duplicados) y fusiona esos obs_id en un solo grupo antes del split train/val/test â€” usando el menor obs_id de cada cluster como representante.

**DecisiÃ³n de alcance (confirmada con el usuario):** se excluyeron `Hyloxalus_picachos` y `Sachatamia_electrops` del catÃ¡logo de entrenamiento â€” son las 2 Ãºnicas especies sin gÃ©nero de respaldo (huÃ©rfanas, ver `anura_cola_larga_taxonomica.md`) Y coincidieron con ser las que tenÃ­an mÃ¡s problemas de integridad de datos (7/14 y 10/46 fotos respectivamente eran duplicados exactos, mÃ¡s una foto mal etiquetada como `Cochranella_albomaculata` en Sachatamia). Quedan pendientes de H4 (segmentaciÃ³n) + mÃ¡s datos, a agregarse despuÃ©s vÃ­a el pipeline de crecimiento de este mismo documento, pasando por el gate de validaciÃ³n.

**Resultado final del dataset limpio:** 41 especies, 7 familias, 13 gÃ©neros. 5.227 imÃ¡genes totales (3.629 train / 750 val / 848 test), 1.875+387+418 individuos reales tras la fusiÃ³n. Ninguna especie excede el tope de 70 individuos. Cero fuga de datos confirmada (ahora correctamente, incluyendo el caso de obs_id duplicados).



