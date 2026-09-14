# Proceso de Crecimiento del Catálogo Post-Despliegue

**Fecha de diseño:** 2026-09-11
**Contexto:** Definido durante la expansión de 28â†’43 especies en el dataset de entrenamiento. Responde a la pregunta: "una vez la app esté lista, ¿qué pasa si quiero añadir 500 especies nuevas?"

Ver [[Fases de Implementación â€” BioCLIP v1 a On-Device (C-11)]] para el pipeline de entrenamiento base, y `anura_cola_larga_taxonomica.md` (memoria) para el precedente de las 15 especies de crecimiento inicial.

---

## Principio arquitectónico (patrón Merlin, Cornell Lab)

El sistema separa dos componentes con ciclos de vida distintos:

| Componente | Qué es | Cuándo cambia |
|---|---|---|
| **Image Encoder** (`bioclip_anura_encoder_fp16.onnx`, ~173 MB) | Red neuronal que convierte foto â†’ embedding 512-d | Rara vez â€” solo si se decide una nueva ronda de Transfer Learning |
| **Paquetes regionales** (`.sqlite` con sqlite-vec) | Embeddings de referencia + metadata (especie/género/familia/ubicación) por cada foto conocida | Frecuente â€” cada vez que se agregan especies o fotos nuevas |

En producción, la identificación **no usa las cabezas de clasificación softmax** (esas existen solo durante entrenamiento y se descartan al extraer `model.visual` en Fase 6). Usa **k-NN**: la foto del usuario se codifica con el encoder congelado, y se busca el embedding de referencia más cercano en el paquete regional. Esto significa que **el catálogo de especies identificables lo define el paquete de datos, no el modelo**.

---

## Cómo agregar especies nuevas (mecánica)

1. Scrapear fotos de la especie (reusar `scraper_inaturalist.py`, criterio: presencia en Colombia + mínimo de fotos, `--skip-audio` si no aplica)
2. El scraper regenera `arbol_taxonomico.json` automáticamente con la especie nueva
3. Correr `paquetes_regionales/generar_embeddings.py --encoder <checkpoint>` â€” el script:
   - Lee la taxonomía dinámicamente (no requiere tocar código)
   - Identifica fotos nuevas por clave àºnica (`especie::archivo`) â€” solo procesa lo que no está ya en el paquete
   - Genera embeddings con el encoder **ya entrenado y congelado**
   - Inserta en el `.sqlite` regional correspondiente

**Cero reentrenamiento necesario para este paso.** Es la razón de ser de la separación modelo/datos.

---

## Los riesgos reales de escalar así (500 especies o cualquier lote grande)

"Se puede sin reentrenar" **no implica** "funcionará con buena precisión". Los riesgos identificados:

### 1. Distancia taxonómica/visual del dominio de entrenamiento
El encoder fue afinado específicamente para discriminar bien las 43 especies actuales (9 familias, 15 géneros). Cuanto más se afina hacia un dominio estrecho, menos generalista queda para taxones muy distintos â€” es el mismo trade-off que causó el overfitting en Fase 4 (ver `resultados_fase4_esquematizado.md`).
- **Riesgo bajo-medio:** especies nuevas del mismo género/familia que ya conocemos (más Hylidae, Strabomantidae/Craugastoridae colombianas)
- **Riesgo alto/incierto:** especies de otros continentes, otros órdenes, o morfológicamente muy distintas â€” el k-NN puede rendir peor que el BioCLIP zero-shot original sin fine-tuning

### 2. Confusión cruzada aumenta con el tamaño del catálogo
Más especies en la base de referencia = más candidatos "vecino más cercano" que pueden ganarle al correcto por poco margen. Ya observamos esto con el par `Pristimantis_achatinus`/`Pristimantis_paisa` (46% F1, confundibles en Fase 3). Agregar cientos de especies del mismo género multiplica estos pares problemáticos.

### 3. Calidad de datos por especie se repite a escala
El problema de "8 especies con <70 individuos" (ver `anura_cola_larga_taxonomica.md`) se repite con cada especie nueva que tenga pocas fotos de referencia confiables. Sin control, un lote de 500 puede terminar con 100 bien resueltas y 400 pobremente representadas.

### 4. Sin señal automática de degradación
El k-NN no emite una alerta de "esta especie quedó mal representada". Cada embedding de referencia es un voto literal â€” una foto de referencia mal identificada corrompe silenciosamente ese resultado, sin que nada en el sistema lo detecte hasta que un usuario reporta un error.

---

## Regla obligatoria: gate de validación antes de desplegar cualquier lote

**No desplegar un lote de especies nuevas a usuarios sin antes verificarlo.** El volumen (43, 100, 500) no es el criterio de riesgo â€” la proximidad taxonómica y la precisión medida sí lo son.

**Proceso de validación (replica la metodología de Fase 3):**

1. Reservar un subconjunto de fotos del lote nuevo como "test" (no metidas al paquete regional)
2. Correr una evaluación k-NN igual a `fase_3_baseline.py`: para cada foto de test, verificar si el vecino más cercano en el paquete (incluyendo el lote nuevo) es la especie correcta
3. Medir Top-1 y Top-3 específicamente para las especies del lote nuevo
4. **Umbral de decisión:**
   - Top-1 aceptable (a definir contra el baseline conocido, ej. >60-65%) â†’ desplegar el lote tal cual, sin tocar el encoder
   - Top-1 pobre â†’ **no desplegar**; es la señal de que toca una nueva ronda de Transfer Learning incluyendo esas especies como clases reales de entrenamiento (el mismo proceso que se siguió al pasar de 28â†’43 especies el 2026-09-11)

### Cuándo Sà toca reentrenar (no solo agregar embeddings)

- La validación del lote nuevo da Top-1/Top-3 inaceptable
- El lote introduce familias/géneros completamente nuevos sin representación previa en el encoder
- Se acumulan suficientes lotes con datos reales como para justificar una ronda de refinamiento (igual lógica que "más datos reales combate overfitting" aplicada del lado de producción)

---

## Resumen para decisiones futuras

| Pregunta | Respuesta corta |
|---|---|
| ¿Puedo agregar 500 especies sin reentrenar? | Sí, mecánicamente â€” el pipeline ya lo soporta |
| ¿Va a funcionar bien automáticamente? | No garantizado â€” depende de proximidad taxonómica y calidad de datos por especie |
| ¿Cómo sé si funcionó? | Gate de validación obligatorio (Top-1/Top-3 sobre fotos reservadas) antes de desplegar a usuarios |
| ¿Cuándo reentrenar en vez de solo agregar? | Cuando la validación del lote falla, o cuando se introducen familias/géneros sin representación previa |

Ver también: [[anura_architecture_vision_model]] (memoria), `paquetes_regionales/generar_embeddings.py` (implementación).

---

## Nota lateral: bug de taxonomía detectado y corregido durante esta expansión

Al verificar la taxonomía de las especies nuevas contra `arbol_taxonomico.json` (generado por el scraper desde iNaturalist), se detectó que `training/taxonomia.py` tenía **Pristimantis mapeado a Strabomantidae**, cuando el propio `taxon_info.json` de `Pristimantis_achatinus` (parte del dataset original, no de las especies nuevas) ya decía **Craugastoridae**. Era un error preexistente, no introducido por la expansión.

**Corrección aplicada:** `GENERO_A_FAMILIA["Pristimantis"] = "Craugastoridae"`. Esto redujo el vocabulario de familias de 9 a 8 (Strabomantidae no era usada por ningàºn otro género). Se verificó cruzando TODOS los `taxon_info.json` disponibles contra `taxonomia.py` â€” sin discrepancias adicionales.

**Lección:** la taxonomía manual en código puede desincronizarse de la fuente real (iNaturalist). El flujo correcto es que `taxonomia.py` derive de `arbol_taxonomico.json`, no al revés â€” pendiente de refactor si se sigue creciendo el catálogo.

---

## Segundo hallazgo (misma sesión): fuga de datos sistémica por duplicados perceptuales, y exclusión de 2 especies huérfanas

Al pedir explícitamente cuidar el tope de 70 individuos por especie, se ejecutó una verificación de duplicados perceptuales (`imagehash.phash`, distancia de Hamming) sobre las 43 especies completas. Resultado: **37 de 43 especies tenían pares de fotos sospechosas** (458 pares totales), de los cuales **249 eran duplicados exactos** (distancia=0).

**Dos tipos de duplicado exacto encontrados:**
1. Archivo manual (sin patrón `obs_id`, ej. `large (1).jpg`, fotos de WhatsApp, museo) que resultó ser copia exacta de una foto ya descargada por el scraper con `obs_id` â€” se resolvió quedándose con la versión de iNaturalist (metadata verificable) y moviendo la manual a `data dirty/_cuarentena/<especie>/`.
2. **Más grave:** dos observaciones de iNaturalist con `obs_id` DISTINTO que comparten una foto idéntica â€” evidencia de que son el mismo evento/individuo reportado dos veces. Se detectaron **118 clusters** (247 obs_id) de este tipo. Sin corregir esto, el GroupSplit los trataba como individuos diferentes â€” el chequeo "0 grupos repartidos entre particiones" NO detectaba este problema porque cada obs_id, individualmente, sí quedaba en una sola partición; el problema era que dos obs_id distintos eran, en realidad, el mismo individuo.

**Corrección aplicada:** `training/prepare_dataset.py` ahora acepta `training/individuos_fusionar.json` (generado por el análisis de duplicados) y fusiona esos obs_id en un solo grupo antes del split train/val/test â€” usando el menor obs_id de cada cluster como representante.

**Decisión de alcance (confirmada con el usuario):** se excluyeron `Hyloxalus_picachos` y `Sachatamia_electrops` del catálogo de entrenamiento â€” son las 2 àºnicas especies sin género de respaldo (huérfanas, ver `anura_cola_larga_taxonomica.md`) Y coincidieron con ser las que tenían más problemas de integridad de datos (7/14 y 10/46 fotos respectivamente eran duplicados exactos, más una foto mal etiquetada como `Cochranella_albomaculata` en Sachatamia). Quedan pendientes de H4 (segmentación) + más datos, a agregarse después vía el pipeline de crecimiento de este mismo documento, pasando por el gate de validación.

**Resultado final del dataset limpio:** 41 especies, 7 familias, 13 géneros. 5.227 imágenes totales (3.629 train / 750 val / 848 test), 1.875+387+418 individuos reales tras la fusión. Ninguna especie excede el tope de 70 individuos. Cero fuga de datos confirmada (ahora correctamente, incluyendo el caso de obs_id duplicados).



