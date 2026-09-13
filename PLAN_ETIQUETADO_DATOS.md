# PLAN_ETIQUETADO_DATOS.md
# Plan de Etiquetado, Valores de Atributos y Organización de Datos — Proyecto Anura
Fecha: 2026-09-10 | Deadline modelo: 2026-09-27 | Deadline dataset etiquetado (según `organiza_plan_completo.md`): 2026-09-13

Este documento es complementario a `PLAN_MODELO_VISION.md` (arquitectura de modelo: destilación
BioCLIP→MobileNetV3-Small, export FP16, sin INT8). Aquí NO se repite esa arquitectura; el alcance es
exclusivamente: (1) valores de atributos en CVAT, (2) métodos de etiquetado, (3) organización de datos
de anotación/entrenamiento.

`anuro_labels.json` **ya es un esquema casi completo** (16 items, 15 partes anatómicas + `anuro_completo`).
Este plan lo audita y corrige, no lo reemplaza.

---

## 1. Tabla de corrección de nombres de especie (`especie` en `anuro_completo`)

Verificado contra `D:\Anura\data dirty\arbol_taxonomico.json` (28 especies reales del proyecto) y
`reporte_especies_problematicas.md`.

| # | Label actual en `anuro_labels.json` | Label correcto | Justificación |
|---|---|---|---|
| 1 | `pristimantis_acanthinus` | `pristimantis_achatinus` | `arbol_taxonomico.json` y la carpeta real `data dirty\Pristimantis_achatinus` (1925 fotos) confirman *Pristimantis achatinus*. "acanthinus" no existe en el árbol taxonómico del proyecto — es un typo, no una especie distinta. |
| 2 | `hyloxalus_picachus` | `hyloxalus_picachos` | Ortografía científica correcta es *Hyloxalus picachos* (con "o"), confirmada por el usuario y por `reporte_especies_problematicas.md` ("Hyloxalus picachos: está en el árbol taxonómico pero no tiene carpeta de datos" — la carpeta real ya existe como `Hyloxalus picachos` en `D:\Anura`, top-level). Ajustar antes de que se propague al training. |
| 3 | `rhinella_sp_margaritifera` | `rhinella_margaritifera` | `arbol_taxonomico.json` la lista como *Rhinella margaritifera* sin calificador `sp`; la carpeta real es `data dirty\Rhinella_margaritifera` (241 fotos). El prefijo `sp_` sugería identificación incierta a nivel de especie, pero el árbol la trata como determinada — quitar el calificador. |
| 4 | `boana_cinereascens` | `boana_cinerascens` | Carpeta real y árbol taxonómico usan *Boana cinerascens* (sin la "e" extra tras "cinera-"). Nota: en `D:\Anura` (nivel raíz, fuera de `data dirty`) existen además variantes mal escritas `Boana cinereansis` / carpetas `equipo 1` con el mismo error — normalizar todo a `boana_cinerascens` en el pipeline de labels, no solo en `data dirty`. |
| 5 | `pristimantis_norandinus` | `dendropsophus_norandinus` (cambio de **género**, no solo de escritura) | No existe *Pristimantis norandinus* en `arbol_taxonomico.json` ni carpeta `Pristimantis_norandinus`. Sí existe *Dendropsophus norandinus* (carpeta `data dirty\Dendropsophus_norandinus`, 26 fotos) como una de las 28 especies del árbol, y **no tenía ninguna entrada propia en la lista de labels** — esto no es una especie faltante nueva, es la misma especie mal etiquetada con el género equivocado. Renombrar resuelve simultáneamente el "faltante" y el "sobrante". |
| 6 | `leucostethus_fraterdanieli` | **Eliminar del esquema** | El género *Leucostethus* no aparece en `arbol_taxonomico.json` (28 especies). No es parte del alcance del proyecto ("28 especies de Caldas"); 0 carpetas de datos. Mantenerla en la lista de valores es un riesgo real: un anotador podría usarla por error, contaminando el manifest con una clase sin ningún dato de entrenamiento posible. |
| 7 | `dendrobates_sp_guaviare` | **Eliminar del esquema** | Igual que el anterior: no está en el árbol taxonómico de las 28 especies (es una entrada geográfica/hipotética de Guaviare, fuera del alcance de Caldas), 0 carpetas de datos. Eliminar. |
| — | (resto: 21 especies) | Sin cambios | `rheobates_palmatus`, `rhinella_alata`, `rhinella_horribilis`, `sachatamia_electrops`, `craugastor_raniformis`, `dendrobates_truncatus`, `boana_lanciformis`, `boana_punctata`, `boana_xerophylla`, `dendropsophus_bogerti`, `dendropsophus_microcephalus`, `dendropsophus_reticulatus`, `dendropsophus_triangulum`, `hyloscirtus_palmeri`, `phyllomedusa_tarsius`, `pithecopus_hypochondrialis`, `scinax_ruber`, `engystomops_pustulosus`, `leptodactylus_colombiensis`, `pristimantis_paisa`, `pristimantis_penelopus`, `pristimantis_taeniatus`, `pristimantis_vilarsi` coinciden exactamente entre label, `arbol_taxonomico.json` y carpeta de `data dirty`. |
| — | `otra_no_listada` | Mantener | Catch-all para anuros fuera de las 28 especies fotografiados por error (útil para no forzar una especie falsa). |
| — | `no_determinable` | Mantener | Catch-all para cuando no se puede identificar ni siquiera aproximadamente. |

**Resultado tras la corrección:** exactamente 28 valores de especie + 2 catch-all = 30 valores en el
`select`, y el conteo cuadra 1:1 con `arbol_taxonomico.json`. Antes había 30 "especies" nominales pero
con 2 fantasmas (`leucostethus_fraterdanieli`, `dendrobates_sp_guaviare`) y 1 real faltante
(`dendropsophus_norandinus`, escondida bajo el género equivocado) — la corrección de la fila 5 resuelve
ambos problemas a la vez sin necesidad de "añadir" una especie nueva.

**Nota adicional de higiene de nombres de carpeta (no bloqueante para CVAT, pero sí para el manifest):**
en `D:\Anura` (raíz, fuera de `data dirty`) existen carpetas con errores tipográficos que **no** deben
usarse como fuente de verdad de nombres (`Boana cinereansis`, `Boana xeraphyla`, `Dendrosophus
reticulatus`, `Rhinella SF margatiferas`) — probablemente resultado de renombrado manual por los
equipos. El manifest de anotación (sección 4) debe mapear estas carpetas a los labels corregidos de la
tabla anterior vía un diccionario explícito, no vía coincidencia de texto.

---

## 2. Auditoría de valores por cada uno de los 16 items

Leyenda: se mantiene = valor correcto ya presente; se añade = falta y se justifica; se marca = sobra/ambiguo.

### 2.1 `anuro_completo`

- **`especie`** (select, mutable=false): corregir según tabla de la sección 1. `mutable=false` es
  correcto (la especie no cambia entre fotos del mismo individuo/track).
- **`vista`**: `dorsal, ventral, lateral, frontal, detalle_macro` — completos para las 28 especies.
  Sin cambios. `mutable=true` correcto (varía por foto).
- **`calidad_enfoque`**: `alta, media, borrosa_parcial` — **se añade** `borrosa_total` /
  `inutilizable`, para poder marcar explícitamente fotos que no deben usarse ni para clasificación ni
  para partes anatómicas, en vez de forzar "borrosa_parcial" que implica que aún es aprovechable
  parcialmente. Esto evita que el filtro de calidad tenga que inferirse indirectamente. `mutable=true`
  correcto.
- **`postura`**: `extendida, recogida, salto, parcialmente_oculta` — **se añade** `amplexus` (par en
  cópula), biológicamente relevante y frecuente en las fotos de campo/iNaturalist de *Engystomops
  pustulosus* y varios Hylidae (es la especie Tier A con más fotos, alta probabilidad de encontrarlo).
  Sin amplexus, esas fotos fuerzan un valor engañoso ("extendida" con dos individuos superpuestos).
  `mutable=true` correcto.
- **`sexo_aparente`**: `macho, hembra, indeterminado` — suficiente; en anfibios rara vez hay dimorfismo
  visual fuerte salvo tamaño/saco vocal, ya cubierto por otro item. Sin cambios. `mutable=false`
  correcto (rasgo del individuo, no de la foto).
- **`estadio`**: `adulto, juvenil, metamorfo` — suficiente para el objetivo del proyecto (identificar
  individuos post-metamórficos en campo); no se añade "renacuajo" porque el dataset no está compuesto
  de fotos acuáticas de larvas y agregar la clase sin datos reales sería ruido. `mutable=false` correcto.

### 2.2 `cabeza`
`forma_general`: `ancha, estrecha, triangular, ovalada` — cubre el rango morfológico de las 7 familias
del proyecto (Bufonidae ancha, Pristimantis/Craugastoridae variable, Hylidae ovalada/triangular).
Sin cambios.

### 2.3 `hocico`
`forma`: `redondeado, puntiagudo, truncado, acuminado` — terminología herpetológica estándar, cubre
Craugastoridae (hocico acuminado en varios *Pristimantis*) y Bufonidae (redondeado). Sin cambios.
`canto_rostral`: `definido, indefinido, no_evaluable` — correcto, es carácter diagnóstico clásico en
claves de *Pristimantis*/Craugastoridae. Sin cambios.

### 2.4 `ojo`
- `lado`, `orientacion`, `tamano_relativo`: correctos sin cambios.
- `forma_pupila`: `redonda, elipsoidal, romboidal, no_visible` — suficiente para las familias del
  proyecto (Bufonidae/Rhinella pupila horizontal elíptica, Centrolenidae/Dendrobatidae redonda).
- **`color_iris`**: `marron_pardo, amarillo_dorado, rojo_naranja, verde, azul_turquesa, gris_claro,
  otro, no_determinable` — **se añade** `negro` (frecuente en *Dendrobates truncatus*, Dendrobatidae en
  general tiene iris muy oscuro) y **se añade** `bicolor_reticulado` (patrón diagnóstico muy usado en
  claves de *Pristimantis*: iris con mitad superior bronce/cobre y mitad inferior oscura, o
  reticulación negra sobre fondo claro — relevante para diferenciar el clúster de 5 *Pristimantis* del
  proyecto, que es el grupo con mayor riesgo de confusión intra-género según el propio
  `PLAN_MODELO_VISION.md` sección 5).
  - **Ajuste de `mutable`**: se recomienda **mantener `mutable=false`** (es un rasgo del individuo, no
    de la foto) pero con una regla operativa explícita en el criterio de anotación (sección 3): si el
    flash nocturno o la sobreexposición distorsionan visiblemente el color percibido, el anotador debe
    usar `no_determinable`, no cambiar de valor entre fotos del mismo individuo. Convertirlo en
    `mutable=true` sería incorrecto porque el color real del iris no cambia con la luz — lo que cambia
    es la certeza de la lectura, y para eso ya existe `no_determinable`.

### 2.5 `timpano`
`lado`, `tamano_relativo_ojo`: sin cambios, correctos y diagnósticos (tamaño relativo al ojo es
carácter clásico, p. ej. tímpano grande en *Craugastor raniformis*).
`visibilidad`: `visible, oculto_pliegue, no_evaluable` — suficiente. `mutable=true` correcto (depende
del ángulo de la foto).

### 2.6 `dorso_flancos`
- `color_base`: `verde, marron_pardo, gris, amarillo_naranja, azul_turquesa, negro, otro,
  no_determinable` — suficiente para las 7 familias.
- **`patron`**: `liso, manchado, rayado, granular, verrugoso, mixto` — **se añade** `reticulado`
  (**crítico**: una de las 28 especies del proyecto se llama literalmente *Dendropsophus reticulatus*
  por su patrón dorsal reticulado; sin este valor no hay forma de anotar correctamente su rasgo más
  diagnóstico) y **se añade** `lineas_dorsolaterales` (patrón de franjas longitudinales, frecuente en
  *Engystomops*, *Craugastor*, algunos *Pristimantis*). **Se marca como ambiguo/redundante**:
  `granular` y `verrugoso` dentro de `patron` se solapan conceptualmente con `textura` (`granulosa`,
  `verrugosa`) — recomendación: restringir `patron` a **patrón cromático** (liso, manchado, rayado,
  reticulado, lineas_dorsolaterales, mixto) y dejar exclusivamente en `textura` los valores de relieve
  de la piel (granulosa, verrugosa, lisa, plegada), evitando que dos anotadores etiqueten el mismo
  rasgo físico en dos atributos distintos con valores distintos.
- `textura`: `lisa, granulosa, verrugosa, plegada` — sin cambios (ver nota anterior).
- `linea_vertebral`: `ausente, presente_delgada, presente_ancha` — sin cambios, correcto.

### 2.7 `vientre`
- `color_base`: `blanco_crema, amarillo, translucido, manchado_oscuro, azul_turquesa, otro,
  no_determinable` — el valor `translucido` ya cubre el rasgo diagnóstico clave de Centrolenidae
  (*Sachatamia electrops*, vísceras visibles a través de la piel ventral) — **sin cambios en valores**,
  pero se añade una **nota de guía de anotación** (no un valor nuevo): para *Sachatamia electrops*
  específicamente, priorizar fotografiar/anotar el vientre siempre que sea posible porque es el
  carácter más diagnóstico de la única especie de rana de cristal del proyecto.
- `patron`: `liso, moteado, reticulado, manchas_grandes` — ya incluye `reticulado` (útil para el
  patrón de venas visible en Centrolenidae). Sin cambios.

### 2.8 `ingle_muslo`
`color_patron`: `liso, manchado, marmoreado, reticulado, barreado, no_evaluable` — suficiente.
`color_flash`: `ausente, rojo, naranja, amarillo, azul, otro` — cubre los "flash colors" ocultos en la
ingle, carácter diagnóstico clásico en Craugastoridae/Leptodactylidae. Sin cambios.

### 2.9 `glandulas_pliegues`
- **`tipo`**: `parotoide, dorsolateral, cresta_dorsolateral, pliegue_supratimpanico, inguinal, femoral,
  otra` — **se añade** `pliegue_tarsal` (muy usado en claves de Hylidae — género *Boana*,
  *Dendropsophus*, *Scinax*, *Hyloscirtus* — que son 11 de las 28 especies del proyecto; su ausencia
  deja sin poder anotar uno de los caracteres más citados en literatura para diferenciar estos géneros).
- `prominencia`: `ausente, leve, moderada, marcada` — suficiente, pero es uno de los atributos más
  subjetivos del esquema → ver guía de calibración en sección 3.

### 2.10 `saco_vocal`
`presencia`: `ausente, presente_no_inflado, presente_inflado` — correcto. `posicion`:
`subgular_medial, subgular_bilateral, lateral, no_aplica` — cubre exactamente los 3 patrones presentes
en las familias del proyecto (medial en *Engystomops*, bilateral en varios Hylidae, subgular simple en
*Rhinella*). Sin cambios. `mutable=true` en `presencia` correcto (el saco se infla/desinfla entre
fotos); `posicion` con `mutable=false` correcto (es anatómico fijo).

### 2.11 `extremidad_anterior` / 2.12 `extremidad_posterior`
Solo `lado` — correcto, son items "contenedores" para anidar `dedos`/`palmeadura`/
`tuberculo_metatarsal` por extremidad. Sin cambios.

### 2.13 `tuberculo_metatarsal`
`presencia`: `ausente, presente`. `forma`: `comprimido, redondeado, no_evaluable` — carácter clásico
de Craugastoridae/Leptodactylidae, suficiente. Sin cambios.

### 2.14 `dedos`
`extremidad`: `anterior, posterior`. `presencia_discos`: `ausente, presente_pequeno, presente_grande`
— cubre el rasgo diagnóstico de discos digitales expandidos (Hylidae, Centrolenidae). Suficiente para
el nivel de esfuerzo disponible; no se añade "discos_truncados_vs_redondeados" (distinción más fina de
Centrolenidae) porque solo hay 1 especie de esa familia en el proyecto y el tiempo no lo justifica.

### 2.15 `palmeadura`
`extremidad`: `anterior, posterior`. `grado`: `ausente, basal, parcial, completa` — carácter muy
relevante (*Rheobates palmatus* lleva el nombre por su palmeadura). Sin cambios.

### 2.16 `region_cloacal`
`visibilidad`: `visible, no_observable` — mínimo pero suficiente dado el tiempo disponible; no se
recomienda añadir sub-atributos de ornamentación cloacal (presentes en algunos *Pristimantis*) porque
es un rasgo de bajo retorno frente al esfuerzo de anotación con el deadline del 27 de septiembre — se
deja como mejora explícita para v2, igual que la segmentación fina completa.

---

## 3. Métodos de etiquetado

### 3.1 Orden recomendado de anotación

**Paso 1 — Siempre primero, en todas las imágenes:** `anuro_completo` (especie, vista, calidad_enfoque,
postura, sexo_aparente, estadio). Esto es lo único estrictamente necesario para el clasificador MVP
(ver `PLAN_MODELO_VISION.md` sección 1.4/4: la segmentación de 17+ partes se pospone a v2). Anotar esto
en el máximo número de imágenes posible es la prioridad #1 del equipo de etiquetado antes del 13 de
septiembre.

**Paso 2 — Filtro de calidad antes de continuar:** si `calidad_enfoque = borrosa_total/inutilizable`
o la vista no permite ver casi ninguna parte anatómica, **no continuar** con partes anatómicas en esa
imagen — pasar a la siguiente. Evita invertir tiempo en anotación fina de fotos que no aportarán señal.

**Paso 3 — Solo para el subconjunto de referencia (ver sección 4), orden de partes anatómicas:**
`cabeza → hocico → ojo → timpano → dorso_flancos → vientre → ingle_muslo → glandulas_pliegues →
saco_vocal → extremidad_anterior → extremidad_posterior → tuberculo_metatarsal → dedos → palmeadura →
region_cloacal`.

Justificación del orden: sigue el barrido visual natural cabeza→tronco→extremidades→cloaca que también
usan las claves taxonómicas herpetológicas clásicas, minimiza saltos de atención del anotador entre
zonas de la imagen, y agrupa primero las partes casi siempre visibles (cabeza/ojo/dorso) antes de las
que dependen de ángulos específicos (palmeadura, región cloacal, que requieren vista ventral/posterior).
**No forzar polígonos en partes no visibles** — cada imagen solo debe llevar las partes que realmente
se distinguen en ella.

### 3.2 Criterios para resolver ambigüedad entre anotadores

- **Calibración previa obligatoria:** antes de que `equipo 1/2/3` empiecen a anotar en paralelo, anotar
  en conjunto (una sola sesión, las mismas 15-20 imágenes) y comparar resultados para los atributos más
  subjetivos: `calidad_enfoque`, `postura`, `prominencia` (glándulas/pliegues), `color_patron`/`color_flash`
  (ingle_muslo). Documentar 2-3 fotos de anclaje por cada valor posible de estos atributos — reutilizar
  el formato que ya existe en `D:\Anura\fotos` / `fotos_opt` (ya contiene ejemplos de referencia tipo
  `3.3a_postura_extendida.png`, `3.3b_postura_recogida.jpg`, `3.4a_estadio_adulto.png`, etc. — extender
  ese mismo patrón de guía visual a `calidad_enfoque` y `prominencia`, que hoy no lo tienen).
- **Doble anotación de control:** de las primeras 20 imágenes que anote cada equipo, que un segundo
  anotador (de otro equipo) las revise sin ver las etiquetas originales; medir desacuerdo por atributo;
  si el desacuerdo en algún atributo subjetivo supera ~20%, revisar la guía de anclaje de ese atributo
  antes de seguir, no después.
- **Regla de desempate:** ante desacuerdo entre dos valores adyacentes de una escala ordinal (p. ej.
  `leve` vs `moderada` en `prominencia`), preferir el valor más conservador (el más bajo de la escala)
  salvo evidencia inequívoca — evita sobre-declarar rasgos marcados que luego contaminan el motor de
  reglas biológicas de `archivo_md_amplio_como_hacer_modelo.md`/`etiquetado_por_familia.md`.

### 3.3 Cuándo marcar `no_determinable` / `otra_no_listada` / `no_evaluable`

- **`especie = no_determinable`:** usar cuando el individuo es claramente un anuro pero no hay
  suficiente evidencia visual para decidir entre 2+ de las 28 especies (p. ej. foto lejana, ángulo
  frontal sin dorso visible). **No adivinar** — es preferible una etiqueta "no determinable" limpia
  a una etiqueta de especie incorrecta silenciosa, que es mucho más costosa de detectar después.
- **`especie = otra_no_listada`:** usar únicamente cuando el anotador está **razonablemente seguro**
  de que el individuo fotografiado NO es ninguna de las 28 especies del proyecto (p. ej. una especie de
  ave o insecto capturada por error en la carpeta, u otro anuro claramente distinto). No usar como
  sinónimo de "no estoy seguro cuál de las 28 es" — para eso está `no_determinable`.
- **Atributos de parte anatómica (`no_evaluable`, `no_visible`, `no_aplica`):** usar siempre que la
  parte no sea visible en el ángulo/recorte de esa foto específica, en vez de forzar un valor por
  defecto solo para "completar" el formulario de CVAT — un valor por defecto sin verificación real es
  peor que un vacío marcado explícitamente como no evaluable, porque contamina el entrenamiento del
  motor de reglas biológicas sin que se note.
- **Regla general del equipo:** ante la duda entre "marcar algo" y "marcar no_determinable/no_evaluable",
  siempre gana el segundo. El coste de una etiqueta faltante es bajo (el registro simplemente no se usa
  para ese atributo); el coste de una etiqueta incorrecta con apariencia de certeza es alto (entrena mal
  al modelo o al motor de reglas sin que nadie lo detecte hasta la fase de evaluación).

---

## 4. Organización de datos para anotación y entrenamiento

### 4.1 Estructura de tareas en CVAT

- Un único **Proyecto CVAT** (`Anura_Caldas_28sp`) con el esquema de labels corregido (sección 1+2)
  aplicado a nivel de proyecto, no de tarea individual, para que los 16 items/atributos sean idénticos
  en todas las tareas.
- **Una tarea por especie** (no una tarea única con las 816 imágenes mezcladas), nombrada
  `{especie_label_corregido}_{lote}` (ej. `engystomops_pustulosus_lote1`). Motivo: permite asignar,
  medir progreso y hacer control de calidad por especie de forma independiente, y es coherente con que
  las fotos ya están organizadas por especie tanto en `data dirty\<Especie>\fotos` como en el propio
  `dataset_cvat_jpg` (los nombres de archivo llevan el prefijo de especie).
- Dentro de cada tarea, si el volumen de imágenes de esa especie es grande (p. ej. *Pristimantis
  achatinus* con 1925 fotos en bruto), dividir en **lotes de ~100-150 imágenes** para que un anotador
  pueda completar un lote en una sesión razonable y el trabajo sea repartible entre `equipo 1/2/3`.
- **Asignación por equipo:** aprovechar la división que ya existe físicamente en `D:\Anura\equipo 1`,
  `equipo 2`, `equipo 3` (que ya contienen subconjuntos de fotos por especie) como base para decidir
  qué equipo anota qué tarea CVAT — evita reorganizar desde cero y usa el trabajo de curación ya hecho.

### 4.2 Manifest versionado (train/val/test)

Crear `D:\Anura\manifest_anotacion.csv` (o `.json`) como **fuente de verdad única**, con al menos estas
columnas:

| Columna | Descripción |
|---|---|
| `image_id` | Identificador único (nombre de archivo o hash, ya usado en `dataset_cvat_jpg`) |
| `especie_label` | Valor corregido de la tabla de sección 1 (nunca el nombre de carpeta crudo) |
| `familia`, `genero` | Derivados por *lookup* desde `arbol_taxonomico.json`, no como atributos manuales de CVAT (ver sección 4.4) |
| `tier` | A/B/C según conteo real de fotos limpias (definición de tiering ya está en `PLAN_MODELO_VISION.md` Fase 0 — este manifest reutiliza esa clasificación, no crea una nueva) |
| `cvat_task_id`, `cvat_job_id` | Trazabilidad a la tarea/job de origen |
| `equipo_anotador` | equipo 1 / 2 / 3 |
| `nivel_anotacion` | `solo_anuro_completo` vs `completo_15_partes` (ver 4.3) |
| `split` | `train` / `val` / `test` |
| `fecha_anotacion` | Para auditar avance contra el deadline |

- El split estratificado train/val/test (por especie y por tier) es responsabilidad de la fase de
  modelado (`PLAN_MODELO_VISION.md` Fase 0, punto 4) — este manifest de etiquetado debe **alimentar**
  esa fase con las columnas `especie_label` y `nivel_anotacion` ya limpias, no duplicar la lógica de
  splitting.
- Versionar el manifest (aunque sea sin git, con sufijo de fecha `manifest_anotacion_2026-09-1X.csv`
  y un `CHANGELOG.md` corto) para poder auditar qué versión del manifest se usó en cada experimento de
  entrenamiento.

### 4.3 Dos niveles de anotación (clave dado el deadline)

Alineado explícitamente con `PLAN_MODELO_VISION.md` sección 1.4/4 (la segmentación de 17+ partes se
recorta del MVP v1):

1. **Nivel 1 — `solo_anuro_completo` (prioridad máxima, meta: todas las imágenes viables antes del 13
   de septiembre):** solo el item `anuro_completo` con sus 6 atributos. Esto es lo único que bloquea el
   entrenamiento del clasificador de especie.
2. **Nivel 2 — `completo_15_partes` (prioridad secundaria, no bloqueante):** anotación anatómica fina
   completa, reservada a un **subconjunto de referencia curado** de ~5-10 imágenes de alta calidad por
   especie (más para Tier A, menos o ninguna para Tier C si no hay tiempo). Este subconjunto es para
   alimentar en el futuro (post-13 sept, en paralelo con las Fases 1-4 del modelo) los embeddings por
   zona anatómica descritos en `archivo_md_amplio_como_hacer_modelo.md`, pero **no debe competir por
   tiempo de anotación con el Nivel 1** mientras el deadline del 13 esté vigente.

### 4.4 Familia/género: no como atributos de CVAT, sino por *lookup*

Respondiendo directamente al punto planteado en `bien_etiquetas_de_imagen.md` (menciona "etiquetado
jerárquico por familia, género y especie"): **no** se recomienda añadir `familia`/`genero` como
atributos adicionales de `select` en `anuro_completo`. Razón: son 100% derivables de `especie` vía
`arbol_taxonomico.json` (ya existe como fuente de verdad limpia y sin ambigüedad), así que pedirle al
anotador que también los seleccione manualmente solo añade trabajo redundante y una nueva fuente de
error humano (typos de género/familia) sin ganar información nueva. La forma correcta de "etiquetado
jerárquico" es: anotar únicamente `especie` en CVAT, y hacer el join especie→género→familia en el script
que construye el manifest/la tabla `anfibios_vectores` de SQLite (sección 1.5/1.6 de
`PLAN_MODELO_VISION.md`), tal como ya lo hace `arbol_taxonomico.json`.

### 4.5 Priorización realista dado el desbalance (0 a ~1900 fotos/especie) y el deadline

Dato clave: **con el criterio de Nivel 1 (solo `anuro_completo`), el cuello de botella no es
disponibilidad de fotos** (la mayoría de las 28 especies ya tiene bastantes fotos en `data dirty`, ver
`reporte_especies_problematicas.md`) **sino tiempo humano de anotación** antes del 13 de septiembre.
Orden de prioridad recomendado para los 3 equipos:

1. **Primero, especies Tier A con volumen ya trabajado por los equipos** (siguiendo la asignación ya
   existente en `equipo 1/2/3`): continuar lo ya empezado en vez de reorganizar.
2. **Segundo, las 2 especies con datos más abundantes** (*Engystomops pustulosus* 1772 fotos,
   *Rhinella horribilis* 1556 fotos): no es necesario anotar las ~1500-1800 fotos completas — con
   Nivel 1 (clasificación), **150-250 imágenes representativas por especie ya son más que suficientes**
   para el entrenamiento por destilación (el "profesor" BioCLIP ya aporta conocimiento previo, el
   alumno no necesita miles de ejemplos por clase). Anotar todo el volumen bruto sería un desperdicio
   de tiempo frente al deadline — mejor seleccionar un subconjunto diverso (variedad de ángulos,
   iluminación, fondo) que anotar exhaustivamente.
3. **Tercero, especies con pocas fotos (Tier B/C):** *Dendropsophus norandinus* (26), *Sachatamia
   electrops* (29), *Pristimantis vilarsi* (45), *Boana xerophylla* (70 justo al límite) — anotar el
   100% de las fotos disponibles porque cada imagen cuenta; no hay margen para ser selectivo.
4. **No invertir tiempo de anotación en especies sin ninguna carpeta de datos** (ex-`leucostethus_
   fraterdanieli`, ex-`dendrobates_sp_guaviare`, ya eliminadas del esquema en la sección 1) — con la
   corrección de la sección 1 esto ya no es un riesgo porque no aparecen como opciones seleccionables.
5. Nivel 2 (15 partes) solo se aborda si sobra tiempo de equipo después de que el Nivel 1 esté
   completo para Tier A/B — y solo sobre el subconjunto de referencia de la sección 4.3.

---

## 5. Próximos pasos accionables inmediatos (48h, 10-12 sept) — fase de etiquetado

Estos pasos son específicos de anotación/CVAT y están coordinados para **no duplicar** los pasos ya
definidos en `PLAN_MODELO_VISION.md` sección 6 (que cubre entorno de entrenamiento, dedupe de fotos y
manifest de train/val/test del lado de modelado).

1. **Hoy (10 sept):** aplicar las 7 correcciones de la tabla de sección 1 a `anuro_labels.json`
   (renombrar 4 valores, cambiar el género de 1, eliminar 2) y las adiciones de valores de la sección 2
   (`amplexus`, `borrosa_total`, `negro`/`bicolor_reticulado` en iris, `reticulado`/
   `lineas_dorsolaterales` en patrón dorsal, `pliegue_tarsal`) — esto debe quedar cerrado antes de que
   cualquier equipo empiece a anotar en CVAT, para no tener que re-anotar después por un esquema movido
   bajo los pies de los anotadores.
2. **Hoy (10 sept):** crear el Proyecto CVAT `Anura_Caldas_28sp` con el esquema corregido, e importar
   las 816 imágenes de `dataset_cvat_jpg` organizadas en tareas por especie (sección 4.1), usando el
   diccionario de mapeo carpeta-real→label-corregido de la sección 1 (nota de higiene de nombres) para
   evitar arrastrar los typos de `Boana cinereansis`/`Boana xeraphyla`/etc. a las tareas de CVAT.
3. **Hoy/mañana (10-11 sept):** sesión de calibración entre los 3 equipos (sección 3.2) sobre 15-20
   imágenes compartidas, y construir la guía visual de anclaje para `calidad_enfoque` y `prominencia`
   reutilizando el formato ya existente en `D:\Anura\fotos`/`fotos_opt`.
4. **10-12 sept, en paralelo por equipo:** ejecutar anotación **Nivel 1 (`solo_anuro_completo`)** sobre
   las especies priorizadas en la sección 4.5, comenzando por lo que cada equipo ya tenía asignado.
   Meta explícita: cobertura Nivel 1 de todas las especies Tier A/B antes del 13 de septiembre, para
   cumplir con la fecha de "dataset completamente etiquetado" que asume `organiza_plan_completo.md`.
5. **12 sept:** exportar de CVAT el primer lote anotado (aunque sea parcial) y generar la primera
   versión de `manifest_anotacion.csv` (sección 4.2), entregándolo como insumo a la Fase 0 del lado de
   modelado (`PLAN_MODELO_VISION.md`, que ya tiene programado el split train/val/test para el 11 de
   septiembre — coordinar para que ese script consuma este manifest en cuanto exista, en vez de que
   ambos equipos generen manifests paralelos e inconsistentes).

---

## Fuentes consultadas

- `D:\Anura\anuro_labels.json`
- `D:\Anura\PLAN_MODELO_VISION.md`
- `D:\Anura\docs_vision_model_plan\archivo_md_amplio_como_hacer_modelo.md`
- `D:\Anura\docs_vision_model_plan\etiquetado_por_familia.md`
- `D:\Anura\docs_vision_model_plan\organiza_plan_completo.md`
- `D:\Anura\docs_vision_model_plan\bien_etiquetas_de_imagen.md`
- `D:\Anura\data dirty\reporte_especies_problematicas.md`
- `D:\Anura\data dirty\arbol_taxonomico.json`
- `D:\Anura\dataset_cvat_jpg\` (816 JPG sin anotar, inspección directa de estructura)
- `D:\Anura\equipo 1\`, `D:\Anura\equipo 2\`, `D:\Anura\equipo 3\` (inspección directa de estructura)
- `D:\Anura\fotos\`, `D:\Anura\fotos_opt\` (guías visuales existentes de postura/estadio)
