---
title: "Ficha Pública, Explorador y Destacados"
tags: [admin, anura, ficha, explorador, contenido, ux-writing]
created: 2026-09-27
status: draft
---

# Ficha Pública, Explorador y Destacados

Qué datos tiene una especie, quién los pone, de dónde salen y dónde se ven: la ficha técnica de la app, el Explorador (app y web) y el carrusel de inicio ("Rana del día"). Complementa [[Entradas y Ficha de Especie]], que cubre la ficha **del modelo** (altitud, sustrato, pesos, morfos). Esta es la ficha **que lee la gente**. Las etapas están en [[Plan del Backend Real]] (bloque K).

## 1. Cómo está hoy (revisado el 2026-09-27)

Hay tres fuentes de especies que no se hablan:

| Dónde | Fuente | Problema |
| --- | --- | --- |
| App Android: ficha, Explorar, carrusel | `SpeciesCatalog.kt` y `HomeCarouselCatalog.kt`, escritos a mano | Ver tabla de datos erróneos. Cambiar una ficha exige publicar otra app. |
| Admin | `antioquia-real.json` (exportado de los datos reales) | Solo ficha del modelo; no administra la ficha pública. |
| Web (`explorer-service`) | `species.taxonomy` en Postgres | Id `SERIAL`, no el `COL_ANURA_XXXX`. Solo nombre común y UICN. El recuento de especies sale de `ai.predictions`. |

### Datos que hoy están mal en la app

| Hallazgo | Dónde | Por qué importa |
| --- | --- | --- |
| La pestaña **Morfología** muestra tímpano, discos, pliegues, patrón y LHC de *Dendrobates truncatus* para **todas** las especies (texto fijo de Penpot). | `SpeciesScreens.kt`, `species_sheet_*_value` | Información falsa en 30 fichas. |
| Los tres *Rhinella* figuran como "inofensivos". | `SpeciesCatalog.kt` | Tienen glándulas parotoides con bufotoxinas: son peligrosos si se ingieren (mascotas). Es un dato de seguridad. |
| *D. truncatus* aparece como "Rana venenosa de Santa Marta" en el texto de ejemplo, y en el carrusel va bajo "En peligro de extinción". | `strings.xml`, `HomeCarouselCatalog.kt` | La especie no es de Santa Marta y en la UICN está en Preocupación menor (LC). |
| 7 nombres comunes en inglés ("Palm Rocket Frog", "Lovely Leaf Frog"…) y mayúsculas inconsistentes ("Rana De Ingle Roja", "rana arbórea de gladiadora"). | `SpeciesCatalog.kt` | Mezcla de idiomas; errores tipográficos. |
| Rangos de altitud escritos a mano que no cuadran con los registros (*D. bogerti* 2.400–3.000 m contra p5–p95 real de 1.513–2.577 m; *Rheobates palmatus* 1.500–2.500 m contra 515–1.706 m). | `SpeciesCatalog.kt` | Sin fuente. Un rango de literatura y uno de registros son datos distintos; hay que mostrar los dos con su fuente. |
| La LHC ("tamaño") está escrita a mano y no cita fuente. | `SpeciesCatalog.kt` | No se puede verificar. |
| "Observaciones" muestra el número de fotos de entrenamiento; "Identificadores" muestra "—" en todas las fichas. | Ficha | Etiqueta equivocada y un dato vacío que ocupa espacio. |
| 30 de 31 fichas sin dato curioso; los 4 datos del carrusel no citan fuente. | `SpeciesCatalog.kt`, carrusel | Contenido sin respaldo. |
| *Sachatamia electrops* usa el id `ANU_COL_SACH_ELE_001` y dice 198 observaciones (el catálogo real: 41 fotos curadas, en revisión, fuera del paquete). | Carrusel y catálogo | Dos esquemas de id; conteo inventado. |
| Explorar: filtro "Distancia cloaca–cabeza" con valor simulado (48 mm) y observaciones simuladas. | `ExploreScreens.kt` | El término correcto es longitud hocico-cloaca; el filtro no filtra datos reales. |
| El mensaje sin conexión dice que no se puede buscar, pero el catálogo vive en el teléfono. | `explore_offline_body` | Promete menos de lo que la app puede hacer. |
| Las fotos del carrusel (`res/drawable/carousel_*`) no traen licencia ni autor. | Recursos | Las fotos de iNaturalist exigen atribución según su licencia. |

## 2. Una sola ficha, administrada en el Admin

La ficha es **contenido**, no modelo. Se versiona aparte del paquete de identificación: corregir un nombre común no debe exigir recompilar centroides, y cambiar un τ no debe tocar la ficha.

```text
Admin (Postgres: species_content)
  → Catálogo de contenido vN (JSON firmado, por departamento)
      → App: incluido en el APK (hoy) y luego por sincronización (etapa K2 / C1)
      → Web: explorer-service lee la misma tabla
```

### Campos

"Auto" = sale de los datos del proyecto sin que nadie lo escriba. "Herp" = lo escribe o confirma el herpetólogo. "Pub" = obligatorio para publicar.

| Bloque | Campo | Origen | Pub | Se ve en |
| --- | --- | --- | --- | --- |
| Identidad | `taxon_id` (`COL_ANURA_XXXX`), nombre científico, autoría, familia, género | Auto (catálogo + GBIF backbone) | Sí | Ficha, Explorar, web |
| | Nombre común en español | Herp (con fuente) | Sí | Ficha, Explorar, carrusel, web |
| | Otros nombres comunes y sinónimos | Auto (iNaturalist) + Herp | No | Búsqueda |
| Estado | UICN (categoría, año y fuente) | Herp (desde la ficha UICN) | Sí | Ficha, filtro "Amenazada", carrusel |
| | Toxicidad (inofensiva, tóxica al tacto, tóxica si se ingiere), con nota y fuente | Herp | Sí | Ficha, filtro "Tóxica" |
| Dónde vive | Altitud de los registros (p5–p95 y n) | Auto (`records_v1` + DEM) | Sí | Ficha, filtro de altitud |
| | Rango de altitud de la literatura | Herp (con fuente) | No | Ficha, junto al de registros |
| | Subregiones con registros | Auto (point-in-polygon DANE) | Sí | Ficha, Explorar |
| | Mapa de distribución | Auto (registros) | No | Ficha |
| | Hábitat y microhábitat en palabras | Herp | No | Ficha, carrusel "Dónde buscarla" |
| Cómo reconocerla | LHC (mínimo, máximo, por sexo si aplica) | Herp (con fuente) | No | Ficha, filtro LHC |
| | Diagnóstico morfológico (tímpano, discos, pliegues, patrón dorsal y ventral, membranas) | Herp | No | Pestaña Morfología (oculta si está vacía) |
| | Especies con las que se confunde | Auto (confusión real del modelo) + Herp | No | Pestaña Similares |
| | Canto | Fase 2 | No | Pestaña Bioacústica (oculta hasta tener audio real) |
| Contenido | Dato curioso (≤ 120 caracteres, con fuente) | Herp | No | Ficha, carrusel |
| | Foto principal + galería (licencia, autor, enlace) | Auto (fotos curadas con licencia CC) + Herp elige | Sí | Ficha, carrusel, Explorar |
| Cifras | Fotos de referencia en el dataset | Auto | No | Ficha ("Fotos de referencia", no "Observaciones") |
| | Observaciones de la comunidad | Auto (etapa C3) | No | Ficha, cuando exista |
| Publicación | Estado (borrador → en revisión → publicada), quién la revisó y cuándo, versión del catálogo | Admin | Sí | Admin |

Reglas:
- Un campo vacío **no se muestra**. Nada de "—", nada de valores de ejemplo.
- Todo dato escrito a mano lleva **fuente**. Sin fuente, queda en borrador.
- La ficha se publica solo con aval del herpetólogo. Es la misma regla de dos personas del paquete, pero con un solo aval: el contenido no toca el modelo.
- Las especies en revisión (fuera del paquete) pueden tener ficha, pero la app dice que no se reconocen por foto.

### Pantalla en el Admin

- Nueva subsección **Contenido** dentro de Modelo → Conseguir, junto a Especies.
- Tiene una lista de especies con su estado de ficha y el editor por bloques de la tabla.
- A la derecha hay una **vista previa con el mismo aspecto que la ficha de la app** (tarjeta, chips de UICN y toxicidad, estadísticas y pestañas).
- Cada campo automático muestra de dónde sale y cuándo se actualizó. Cada campo manual pide fuente.

## 3. Explorador (app y web)

- Lee el catálogo de contenido publicado. Muestra solo especies publicadas.
- Los filtros usan campos reales: familia, género, toxicidad, UICN amenazada (VU, EN, CR), altitud de registros y LHC. **Un filtro sin datos para la mayoría de especies no se muestra** (hoy la LHC no tiene fuente: se oculta hasta que la tenga).
- Recuentos: especies, géneros y familias salen del catálogo publicado, no de `ai.predictions`.
- Las observaciones del mapa son las de la comunidad (C3). Mientras no existan, el mapa muestra los registros del catálogo (GBIF e iNaturalist) y lo dice.
- Sin conexión, la búsqueda funciona sobre el catálogo del teléfono; solo el mapa necesita red.

## 4. Carrusel de inicio y "Rana del día"

### Reglas por categoría

| Categoría | Condición para aparecer | Texto |
| --- | --- | --- |
| Rana del día | Ficha publicada con foto principal y dato curioso | Dato curioso |
| Dónde buscarla | Ficha con hábitat escrito y subregión con registros | Hábitat en una frase |
| Foto destacada | Foto con licencia que permita uso y atribución visible | Autor y licencia |
| Especie amenazada | UICN VU, EN o CR (con año y fuente) | Categoría y amenaza principal |

- El nombre "En peligro de extinción" se cambia a **"Especie amenazada"**: EN es una sola de las tres categorías.

### Cómo se administra

- Pantalla **Destacados** en el Admin: calendario por día y por categoría, con un selector de especie que solo ofrece fichas que cumplen la condición de la categoría.
- Vista previa del carrusel tal como se ve en el teléfono.
- Rotación automática si un día no tiene nada programado: la app elige por fecha entre las especies elegibles, de forma determinista y sin red.
- Se publica dentro del catálogo de contenido: los próximos 30 días viajan con él, así que funciona sin conexión.
- Prioriza especies de la subregión del usuario cuando hay ubicación.

## 5. Auditoría ux-writing

La guía de voz `content/voice-tone.md` que pide el skill no existe en el repo. Se aplicaron sus reglas y su checklist. La app se dirigía a la persona en voseo ("Buscá", "Tocá", "Podés"). Para Colombia se recomendó tuteo ("Busca", "Toca", "Puedes") y el autor lo confirmó (2026-09-28): los 32 textos en voseo de `strings.xml` (verbo de segunda persona y el pronombre "vos") pasaron a tuteo. Se cambió solo el pronombre/conjugación, no el resto del texto — las otras mejoras de esta misma tabla (nombrar el resultado, quitar jerga, etc.) son decisiones de copy aparte, no aplicadas todavía salvo que la fila lo diga.

| Texto actual | Propuesta | Motivo |
| --- | --- | --- |
| Ficha técnica | Ficha de la especie | Lenguaje llano; "técnica" no agrega nada. |
| Observaciones (valor = fotos del dataset) | Fotos de referencia | Nombra lo que cuenta. |
| Identificadores: — | (ocultar hasta tener dato) | No mostrar vacíos. |
| Tamaño | Longitud hocico-cloaca | Término correcto; "tamaño" es ambiguo. |
| Distancia cloaca–cabeza / Distancia entre la cloaca y la cabeza | Longitud hocico-cloaca (LHC) · "Del hocico a la cloaca, en milímetros" | Término correcto y la unidad en la ayuda. |
| Altura / Altura mínima / Altura máxima | Altitud / Altitud mínima / Altitud máxima | Altura es otra cosa. |
| Peligro (filtro) | Toxicidad | Nombra la propiedad; "peligro" se confunde con amenaza. |
| Estado (filtro) | Estado de conservación | Explícito. |
| En peligro de extinción | Especie amenazada | Precisión (VU, EN y CR). |
| En dónde mirar | Dónde buscarla | Más natural. |
| Cerca de vos | Cerca de ti | Tuteo. |
| Buscá una especie de este género | Busca una especie de este género | Tuteo. |
| Explorá más de este género | Ver más especies de este género | Verbo delante y el resultado nombrado. |
| Descargar distribución | Descargar mapa de distribución | Nombra el resultado. |
| Exportar resumen (PDF / offline) | Descargar ficha en PDF | Nombra el resultado; "offline" sobra. |
| Sin conexión · "El mapa y el recuento de especies no están disponibles. Podés ver el buscador, pero no se puede buscar sin internet." | Sin conexión · "El mapa necesita internet. Puedes buscar especies y abrir sus fichas sin conexión." | Qué pasa → qué sí se puede hacer; hoy promete menos de lo que la app hace. |
| Sin internet no se puede buscar | (quitar; la búsqueda local funciona) | Deja un callejón sin salida. |
| %1$s (%2$s) — %3$d especie(s) | Plurales de Android (`plurals`) | Evita "especie(s)" y es traducible. |
| Nombres comunes en inglés y en Title Case | Español, solo la primera letra en mayúscula ("Rana de ingles rojas") | Un idioma y mayúscula inicial solamente. |

Para la pantalla de Contenido del Admin:
- **Botones:** "Guardar borrador", "Enviar a revisión", "Publicar ficha", "Devolver al autor".
- **Confirmación:** "¿Publicar la ficha de *Pristimantis paisa*?" / "Publicar ficha" / "Cancelar".
- **Estado vacío:** "Esta especie todavía no tiene ficha pública. Empieza por el nombre común y la foto principal."
- **Error de fuente:** "Falta la fuente del rango de altitud. Agrega el artículo o la base de datos de donde sale."

Checklist aplicado:
- se lee natural en voz alta;
- verbo delante en los botones;
- sin jerga ("LHC" siempre con su nombre completo la primera vez);
- errores con qué pasó y cómo arreglarlo;
- estados vacíos que dicen el valor y la primera acción;
- mayúscula solo al inicio;
- cifras en números;
- sin instrucciones que dependan del color;
- plurales traducibles.

## 6. Estado de los hallazgos (2026-09-28)

Detalle técnico en [[Plan del Backend Real]] (bloque K).

| Hallazgo de la tabla 1 | Estado |
| --- | --- |
| Morfología de *D. truncatus* en todas las fichas | **Corregido.** La pestaña muestra solo la morfología publicada; sin ella lo dice. |
| *Rhinella* «inofensivos», nombres en inglés, altitudes y LHC sin fuente | Se corrige **publicando la ficha** en Admin → Contenido: una especie publicada muestra solo lo publicado (con fuente). Mientras no se publique, la app sigue con el respaldo escrito a mano. |
| *D. truncatus* como «especie amenazada» en el carrusel | **Corregido** en el carrusel de ejemplo (es LC); con fichas publicadas, «Especie amenazada» exige UICN VU, EN o CR. La categoría se llama «Especie amenazada». |
| «Observaciones» = fotos del dataset; «Identificadores: —» | **Corregido.** Dice «Fotos de referencia»; los datos vacíos no se muestran. «Tamaño» pasó a «Hocico-cloaca». |
| Fotos del carrusel sin licencia ni autor | **Corregido** para lo publicado: solo fotos CC, con el crédito visible en la ficha y en «Foto destacada». |
| La web lee `species.taxonomy` / datos escritos a mano | **Corregido** para lo publicado: la ficha web lee el catálogo; la web ahora también muestra la toxicidad. El recuento de especies, géneros y familias de `/api/explorer/stats` **ya sale del catálogo publicado** (2026-09-28), no de `ai.predictions` — ver [[Plan del Backend Real]]. |
| Campos que pide la web y el Admin no tenía | **Agregados**: autoría, sinónimos, descripción, actividad, dieta, reproducción, distribución, endemismo (con fuente), amenazas (con fuente), rasgos diagnósticos, especies con que se confunde. |
| Voseo vs. tuteo | **Decidido: tuteo** (2026-09-28). Aplicado en los 32 textos de `strings.xml` que estaban en voseo. |

**Bug encontrado al probar el cambio de arriba (2026-09-28):** al probar de punta a punta el recuento desde el catálogo publicado, `/api/explorer/stats`, `/api/explorer/feed` y `/api/explorer/favorites` devolvían `permission denied for schema observations`. `infrastructure/postgres/roles.sql` solo le daba a `explorer_service` `USAGE`+`SELECT` sobre `species` y `geo` («sin acceso a auth ni observations»), pero el propio `explorer-service` siempre leyó `observations.observations`, `observations.favorites`, `auth.users` (username/foto) y `ai.predictions` (clase del modelo junto al catálogo) — el rol nunca tuvo permiso para eso, no fue una regresión del cambio del catálogo. **Corregido** (opción A, no B: mover esas lecturas a `observation-service` habría significado rehacer 8 endpoints de solo lectura por un servicio que ya vive bien con acceso de lectura acotado): se amplió el `GRANT` de `explorer_service` a `SELECT` en `observations.observations` (más `UPDATE` solo de `altitude_m`/`place_guess`, que el propio servicio rellena), `SELECT`+`INSERT`+`DELETE` en `observations.favorites` (la única tabla en la que escribe: los likes), `SELECT` en `auth.users` y en `ai.predictions`. Sigue sin acceso de escritura a `observations.observations` ni a ninguna otra tabla de `auth`. **Aplicado y verificado en vivo el 2026-09-28** (quedó documentado pero sin aplicar en un pase anterior de la misma sesión — al retomar, `/api/explorer/stats` seguía devolviendo el error, así que se corrigió de verdad): los `GRANT` se aplicaron directo con `psql` contra `anura_postgres` (efecto inmediato) y quedaron también en `infrastructure/postgres/roles.sql` para que `db-migrate` los reaplique en cualquier reprovisión futura (son idempotentes). De paso se quitó de `explorer-service/src/index.js` un `CREATE TABLE IF NOT EXISTS observations.favorites` que sobraba (esa tabla ya la crea `phase2.sql`) y que, sin permiso de `CREATE` en el schema, dejaba un error confuso en el log en cada arranque aunque no bloqueaba nada. Verificado con `curl` contra `/api/explorer/stats` y `/api/explorer/feed` (200, datos reales) y visualmente en `http://localhost:5173/explorar` con el navegador: encabezado real "0 especies · 8 observadores" (0 especies porque el catálogo publicado sigue vacío — ver más abajo — no por el bug de permisos).

Relacionado: [[Roles del Admin]], [[Modelo de Datos del Admin]], [[Prueba Real del Creador de Paquetes]].
