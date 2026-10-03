# ANURA — guía de escenas para Claude

Lista para pegar. Una sesión de Claude = el bloque GLOBAL + una sola escena (S01, S02, …). Claude no lee las otras escenas. No renderices el video completo.

Si la sesión inserta una subsección entre dos escenas, esa sesión es una de tres: la salida de la izquierda, la subsección, o la entrada de la derecha. Las dos de al lado se vuelven a renderizar. El resto del video no.

Documento de orquestación. No es el video. Cada escena se ejecuta sola, se revisa y se guarda. El montaje final no se hace aquí.

- Duración total: **167 s** (2 min 47 s), 60 fps, **1920×1080**. S07a suma 3 s. S10a suma 8 s. S12a suma 5 s. S12b suma 3 s. La música dura 164 s y se corta ahí. De 164.00 a 167.00 el montaje queda en silencio.
- Tempo: **120 BPM**. Beat = 0.5 s. Corchea = 0.25 s. Los cortes grandes caen en beat.
- Motor: **HyperFrames** (HTML + JS, un cuadro = función de `t`). No abras un proyecto Remotion. El diamond wipe se dibuja en canvas.
- Tono /brag: `polished`, dirección libre «pieza de ciencia, clara, con peso». No es un chiste ni un anuncio de tienda.
- Esta pieza pasa de 15–25 s a propósito: es un recorrido del producto, no un sting.

## Quién hace qué

| Rol | Qué hace | Qué no hace |
|---|---|---|
| Esta guía | Tiempos, texto, posición, efecto, archivos | No renderiza |
| Opus o Sonnet (Claude) | Una escena por sesión, o la corrección de una escena ya hecha | No adelanta la siguiente ni une el MP4 |
| Orquestador (al final, con permiso) | Une las escenas ya aprobadas | No redibuja |

Las correcciones de error de una escena ya renderizada se hacen en Claude: bloque GLOBAL + solo esa escena. No se rehacen las vecinas si la frontera (último y primer cuadro, fondo, qué queda en pantalla) no cambia.

## Subsección entre dos escenas

Una subsección es una escena nueva metida entre dos que ya existen. El id lleva la letra de la de la izquierda: entre S06 y S07 queda `S06a`, carpeta `escenas\s06a\`.

Al insertarla se vuelven a renderizar las dos de al lado. Si no, el corte no encaja: la de la izquierda entrega un final que la nueva no toma, y la de la derecha arranca de un estado que la nueva no deja.

Orden, una sesión de Claude por pieza:

1. Escribe aquí el bloque de la subsección (tiempos locales, texto, frontera de entrada y de salida) y corre los tiempos absolutos de todo lo que queda a la derecha: duración total, tabla de SFX, música y `montaje.py`.
2. Sesión de la escena izquierda: solo su salida. El último cuadro debe ser el primer estado de la subsección (fondo, qué está en pantalla, posición). Vuelve a renderizar `sNN.mp4`.
3. Sesión de la subsección: se construye y se renderiza sola.
4. Sesión de la escena derecha: solo su entrada. El primer cuadro toma el último estado de la subsección. Vuelve a renderizar ese `sNN.mp4`.

No re-renderices el resto del video. No unas el MP4 en esas sesiones.

Salida de cada escena: `D:\Anura\video\escenas\sNN\` con `index.html`, capturas de los tiempos marcados y `sNN.mp4` solo de esa ventana. Para y espera revisión.

## Modelo por escena (ahorro de tokens)

Usa **Sonnet** en tipo, números, barras, mapas dibujados y el cierre. Usa **Opus** solo si la escena dice `GRABAR` o `EMULAR-UI`.

| Sonnet | Opus |
|---|---|
| S01–S19, S07a, S10a, S12a, S12b, S25–S27, S36 | S20–S24, S28–S35 |

Si una escena Sonnet sale mal de layout dos veces, súbela a Opus solo esa.

## Estilo cerrado

Fuente: `C:\Users\user\.claude\estudio-motion\estilo.md`. No lo reentrevistes.

Confirmado: horizontal 1920×1080, música más efectos a 120 BPM, HUD apagado, intensidad equilibrada. Las pantallas reales se graban. El zoom entra solo en las escenas `GRABAR`.

Contraste medido (WCAG). Prohibido poner texto en estos pares:

| Par | Ratio | Uso |
|---|---|---|
| `#FFFFFF` sobre `#EEF5EE` | 1.11:1 | prohibido |
| `#1F7A33` sobre `#C6A15B` | 2.22:1 | prohibido |
| `#1B1C1E` sobre `#A97142` | 4.16:1 | solo el número de la medalla, 36 px |
| `#FEFEFE` sobre `#1F7A33` | 5.35:1 | texto del gancho y del cierre |
| `#1F7A33` sobre `#EEF5EE` | 4.87:1 | el 9009 y la línea del gráfico |
| `#1B1C1E` sobre `#EEF5EE` | 15.37:1 | cuerpo sobre fondo claro |

El texto se queda quieto hasta que se pueda leer (palabra corta ≥ 0.8 s; frase ≈ 0.3 s por palabra). Esa quietud gana a la regla de Estudio Motion de mover todo cada medio segundo. En este horizontal el texto vive en su columna, no ocupa el cuadro entero.

Todo tiempo de entrada cae en múltiplo de 0.25 s (corchea). Si al ejecutar ves uno que no, muévelo al 0.25 s más cercano sin cambiar el orden de los elementos.

## Skills que Claude abre

Abre solo estas. No abras Remotion, Prompt Master, `general-video` ni `product-launch-video`.

| Skill | Ruta | Para qué |
|---|---|---|
| hyperframes-core | `C:\Users\user\.claude\skills\hyperframes-core` | Contrato HTML, `t`, sin estado entre cuadros |
| hyperframes-animation | `C:\Users\user\.claude\skills\hyperframes-animation` | Easings, blur, springs |
| hyperframes-cli | `C:\Users\user\.claude\skills\hyperframes-cli` | `npx hyperframes check` y el render de ESA escena |
| hyperframes | `C:\Users\user\.claude\skills\hyperframes` | Solo si core no alcanza. No hagas su entrevista |
| brag | `D:\server\Anura\.claude\skills\brag` | Solo la música y los SFX de `assets/`. No replanées el video |
| estudio-motion | `C:\Users\user\.claude\skills\estudio-motion` | Reglas de cuadro y de fuentes. El plano ya está en esta guía |

## Audio

Desde S06 en adelante, cada `sNN.mp4` sale mudo. La música y los efectos se colocan al unir el video, no dentro de la escena.

Música, en ese montaje: `D:\server\Anura\.claude\skills\brag\assets\music\happy-beats-business-moves-vol-1-by-ende-dot-app.mp3` (164 s, 120.19 BPM), de 0.00 a 164.00, volumen 0.35. En S20–S24, 0.22. De 164.00 a 167.00 no hay música.

La tabla siguiente es la lista del montaje. No la metas en el mp4 de la escena.

| Escena | Absoluto | Archivo |
|---|---|---|
| S01 carta A | 0.50 | `assets\sfx\casino\card-place-1.ogg` |
| S01 carta B | 1.50 | `assets\sfx\casino\card-slide-1.ogg` |
| S01 carta C | 2.00 | `assets\sfx\casino\card-slide-1.ogg` |
| S02 despliegue | 4.00 | `assets\sfx\casino\card-fan-1.ogg` |
| S03 wipe | 7.00 | `assets\sfx\impact\impactSoft_medium_001.ogg` |
| S04 texto | 8.50 | `assets\sfx\ui\rollover2.ogg` |
| S05 número asentado | 14.00 | `assets\sfx\impact\impactSoft_medium_000.ogg` |
| S06 sin audio en el mp4 | — | el golpe de las barras se sonoriza al unir |
| S07 mapa | 22.00 | `assets\sfx\ui\rollover2.ogg` |
| S07a frase | 29.40 | `assets\sfx\ui\rollover2.ogg` |
| S09 tres checks | 38.00, 38.25, 38.50 | `assets\sfx\ui\rollover2.ogg` y en el tercero `assets\sfx\interface\switch_007.ogg` |
| S10a abanico | 53.75 | `assets\sfx\casino\card-fan-1.ogg` |
| S12a frase | 68.50 | `assets\sfx\ui\rollover2.ogg` |
| S12b frase | 74.00 | `assets\sfx\ui\rollover2.ogg` |
| S14 folder | 79.00 | `assets\sfx\interface\drop_001.ogg` |
| S16 y S17 cada teléfono | al aterrizar | `assets\sfx\ui\rollover2.ogg` |
| S20 y S22 clic | en el clic | `assets\sfx\interface\click_003.ogg` |
| S28 cada línea de la terminal | 131.98, 132.46, 133.98 | `assets\sfx\keyboard\keypress-001.wav` |
| S35 descarga | al aterrizar | `assets\sfx\interface\drop_002.ogg` |
| S36 wordmark | 163.50 | `assets\sfx\impact\impactBell_heavy_000.ogg` |

Ruta raíz de los SFX: `D:\server\Anura\.claude\skills\brag\assets\sfx\`. Si el archivo no está, para. No inventes otro sonido.

Fuentes ya descargadas, subset latino:

- `D:\Anura\video\assets\fonts\Archivo.woff2`
- `D:\Anura\video\assets\fonts\InstrumentSerif-Italic.woff2`
- `D:\Anura\video\assets\fonts\JetBrainsMono.woff2`

- Marca en pantalla: **ANURA**
- Fondo oscuro de gancho: `#1F7A33`. Texto sobre ese verde: `#FEFEFE`.
- Fondo claro: `#EEF5EE`. Texto sobre claro: `#1B1C1E`. Acento: `#1F7A33`.
- Papel de cards y checklist: `#FFFFFF`.
- Oro `#C6A15B`, plata `#C5C7C4`, bronce `#A97142`.
- Prohibido para texto: blanco sobre `#EEF5EE`, verde `#1F7A33` sobre `#EEF5EE` en cuerpo pequeño, verde sobre oro. El número grande verde sobre claro sí se lee; el cuerpo va en `#1B1C1E`.
- Display: **Archivo** variable, wdth 62–125, peso 700–900.
- Frase secundaria: **Instrument Serif** itálica.
- Datos, BPM, etiquetas de gráfico: **JetBrains Mono**.
- Fuentes locales en `D:\Anura\video\assets\fonts\`. No cargues Google Fonts en el render.
- Márgenes: **80 px** en los cuatro lados. Nada de texto pegado al borde.
- Entre un texto y un elemento vecino (carta, teléfono, gráfico, mapa, logo, tarjeta) hay **64 px** de aire. No se superponen. El texto no crece para llenar ese aire.
- Una idea por escena. Poco texto. Sin relleno.
- Entrada de texto genérica, solo desde S11: 0.35 s, `outExpo`, desde y+24 o x−40, con motion blur solo mientras se mueve.
- S01–S10: cada texto trae tamaño, peso, color, sitio y efecto. Úsalos tal cual.
- Una palabra corta permanece estable al menos 0.8 s. Una frase, unos 0.3 s por palabra además de la entrada.
- Nada lineal, salvo el conteo que debe leerse como conteo (el conteo usa `outExpo`, no un lerp seco).
- Transición entre escenas del mismo fondo: el elemento que sigue (número, chip, teléfono) se mueve a su nuevo sitio en 0.4 s. No hay corte a negro ni diapositiva.
- El único wipe de bloque es el diamond de S03.

## Skills y rutas que Opus debe leer

- HyperFrames: `C:\Users\user\.claude\skills\hyperframes`, `hyperframes-core`, `hyperframes-animation`, `hyperframes-cli`.
- No entres en la entrevista de `/hyperframes`. Esta guía ya decidió el plano.
- Brag (criterio, no para replanear): `D:\server\Anura\.claude\skills\brag`.
- Estudio: `C:\Users\user\.claude\skills\estudio-motion`.
- Admin real, solo como referencia de nombres: `D:\server\Anura\admin\src\config\nav.ts`.
- Geo de Colombia: `D:\Anura\geo\colombia_municipios.geojson`.
- Geo de Antioquia: `D:\Anura\geo\antioquia_municipios.geojson`.
- No hay geojson de las 9 subregiones. No inventes fronteras. La lista tipográfica es el mapa de regiones.
- No despliegues, no toques Postgres ni MinIO. Si una URL no carga, para y dilo. No rellenes con datos falsos.

## Regla de grabación

- `DIBUJAR`: HTML/canvas. No abras el navegador del producto.
- En toda escena `GRABAR` o `EMULAR-UI`, el navegador ya está autenticado como `sebastianmartinez06.js@gmail.com`, tanto en `https://anura.juanlabs.me` como en `http://localhost:3010`. No escribas ni guardes contraseñas. Si la pantalla pide login, para y avisa.
- `GRABAR`: pantalla real, cursor de **64 px** (anillo blanco, punto verde `#1F7A33`), movimiento lento, un clic visible. Sin barra del sistema.
  - El video va dentro de un marco: radio **24 px**, clip estricto, borde 1 px `rgba(254,254,254,0.35)`, sombra `0 24px 48px rgba(0,0,0,0.28)`. En fondo verde el marco no toca los 80 px de margen.
  - Zoom con drama, no con vértigo: escala 1.00 al entrar y **1.12** en el clic o en el dato que importa, 0.45 s, `inOutExpo`, con el ancla en ese punto. Al soltar, vuelve a 1.00 en 0.35 s si aún queda tiempo de lectura. El zoom ocurre dentro del marco; no se sale del clip.
  - Graba solo la escena que dice `GRABAR`. En `EMULAR-UI` no abras el sitio.
- `EMULAR-UI`: reconstruye solo el contenedor citado, con los textos reales de la interfaz. No navegues al sitio. Cursor grande solo si el plano lo pide.
- El marco de celular es el mismo en todas: alto **760 px**, ancho según la captura, bisel 14 px `#1B1C1E`, radio 36 px, pantalla interna con la foto a cover. Sombra `0 24px 40px rgba(27,28,30,0.18)`.
- Desde S10, todo teléfono que sale del cuadro lo hace hacia la derecha: centro x hasta 2500, `inExpo`, blur horizontal. No sale a la izquierda ni hacia abajo. El siguiente, si lo hay, entra desde la derecha.

## Cómo grabar (probado en S20–S24)

Así se grabaron S20, S21, S22 y S24. Repite el método; no lo reinventes.

### Herramientas

- Motor de grabación: `puppeteer-core` que ya trae la caché de `npx hyperframes` (`%LOCALAPPDATA%\npm-cache\_npx\<hash>\node_modules\puppeteer-core`). No instales nada.
- Navegador: **Edge** con el perfil **«Estudio»** (`User Data\Profile 1`), que es el que tiene la sesión de `sebastianmartinez06.js@gmail.com` en `anura.juanlabs.me`. El perfil «Sebas» (`Default`) no se usó.
- Scripts de referencia: `escenas\s20\rec\rec.cjs` (clic + aviso), `escenas\s22\rec\rec4.cjs` (clic con capturas cronometradas y login previo), `escenas\s22\rec\rec.cjs` (paso al admin), `escenas\s21\rec\rec.cjs` (sin clic).

### Sesión: cómo tenerla sin escribir contraseñas

1. Quien graba **no escribe contraseñas**. La persona inicia sesión en Edge, perfil «Estudio», en `https://anura.juanlabs.me` (vale con la cuenta de ANURA).
2. Edge debe estar **cerrado del todo** (también el inicio rápido de la bandeja). Si no, las cookies están bloqueadas y la copia sale sin sesión.
3. Edge no deja controlar el perfil en su carpeta real (`User Data`): da «The browser is already running» aunque no haya procesos. Por eso se **copia** el perfil a una carpeta temporal y se lanza desde ahí:
   - Copiar `User Data\Local State` y, dentro de `Profile 1`: `Network`, `Local Storage`, `IndexedDB`, `Session Storage`, `Preferences`, `Secure Preferences`, `Web Data`, a `%TEMP%\edge_estudio_copy\` (conservando el nombre `Profile 1`).
   - Lanzar con `executablePath: "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"`, `userDataDir` = la copia, `args: ["--profile-directory=Profile 1"]`, `headless: "new"`.
   - **Borra la copia al terminar**: contiene cookies y datos del perfil.
4. Admin local (`http://localhost:3010`): no hace falta loguearse. En la web pública, estando dentro, el botón **«Modo administrativo»** abre `localhost:3010/login#token=…`; el recuadro de `/login` aparece un momento y desaparece solo (termina en `/dashboard`). Espera ~6 s en esa pestaña y luego navega a la ruta que pida la escena. Abrir `localhost:3010` directo, sin ese paso, lleva a `/login`.
5. Comprobación rápida de sesión: en la web no debe verse la etiqueta **INVITADO** y sí «Modo administrativo»; en el admin, arriba a la derecha, «Sebastián Martínez · super usuario».

### Captura

- Viewport = proporción del marco. Marco de 960×840 → viewport **1142×1000**. Marco de 1760×830 → viewport **1467×700** (al pasar a mp4, `pad=1468:700`, libx264 no acepta ancho impar).
- `page.screencast({ path })` graba webm a 30 fps; convertir con `ffmpeg -vf fps=60 -c:v libx264 -crf 12 -pix_fmt yuv420p -an`.
- **Trampa**: si la página muestra un icono que gira (`.icon-spin`, p. ej. el corazón mientras guarda), el screencast se congela y ya no registra el estado final. En ese caso graba con **capturas cronometradas**: `page.screenshot()` en bucle guardando la hora de cada una, y monta con el demuxer `concat` de ffmpeg (`duration` = diferencia entre capturas) → mp4 a 60 fps. Sale a unos 8 cps, suficiente para una página quieta.
- El ratón real se mueve con `page.mouse.move` en pasos (curva `inOut` cúbica, ~1 s) para que los hover sean reales. El cursor de 64 px **no** sale en la grabación (headless): se dibuja en la composición siguiendo el mismo recorrido.
- Para sincronizar el clic, mide en el mp4 el primer cuadro en que cambia el botón (leer píxeles de un recorte con ffmpeg `crop,scale=1:1` a `rawvideo`) y usa ese tiempo como `CLICK` en la composición y en el `data-start` del SFX.
- El portapapeles necesita permiso: `browserContext.overridePermissions(origen, ["clipboard-read","clipboard-write","clipboard-sanitized-write"])`.

### Composición

- `<video>` mudo dentro de `#zoom`, y `#zoom` dentro del marco (`overflow: hidden`). El zoom se hace con `transform-origin` en el punto de interés (coordenadas de página × factor de escala del marco). Marca `#zoom` con `data-layout-allow-overflow` y el marco con `data-layout-allow-occlusion`.
- El cursor va fuera de `#zoom` pero dentro del marco. Si el zoom está activo cuando el cursor llega, su posición es `ancla + (punto − ancla) × escala`.
- Tras el clic, aparta el cursor 70–90 px para que se vea el cambio de estado.
- Si un aviso aparece lejos del ancla (p. ej. «Enlace copiado» abajo), vuelve a 1.00 **antes** de que salga; si no, queda fuera del marco.
- `click_003.ogg` dura 0.01 s: `data-duration="0.01"`.

### Lo que hace de verdad cada pantalla (para no pedir lo que no existe)

- **Compartir** (`explorer/<id>`, botón «Compartir observación»): no abre panel; copia el enlace y muestra el aviso «Enlace copiado» ~0.8 s después del clic. El icono queda en rojo.
- **Corazón** («Guardar en favoritos»): como invitado abre el modal «Guarda tus favoritos»; con sesión muestra `MdRefresh` girando ~0.25 s y luego el corazón lleno («Quitar de favoritos», clase `liked`). **Es un cambio real en producción**: si repites la toma, quita el favorito fuera de cámara antes de volver a darlo.
- **Observadores** (`/observaciones?view=observers`): pública, sin hover en las filas; la grabación queda quieta y solo se mueven cursor y zoom.
- **Comentarios** (`CommentsSection.jsx`): vacío real «Todavía no hay comentarios. Aportá a la identificación.»; placeholder «Aportá a la identificación… (mencioná un taxón con @)»; el botón es un icono de enviar («Publicar comentario»), no «Proponer».
- **Admin → Observaciones**: pestañas «Por revisar / Aprobadas / Rechazadas / Todas»; la tabla `overflow-x-auto rounded-lg border border-border bg-surface` tiene filas reales.
- El perfil «Estudio» muestra la web en **tema claro**; el perfil limpio de invitado, en oscuro (S20 y S21 salieron en oscuro).

## Copys en pantalla

En pantalla no hay punto ni coma al final de una frase, ni coma colgando entre escenas. Las comas internas de una lista, en la misma tarjeta, sí se quedan. Las preguntas conservan ¿ y ?.

Énfasis, sin subrayado (el subrayado parece un enlace):

- Golpe de una o dos palabras: Archivo 800 o 900.
- Frase que acompaña: Instrument Serif itálica.
- Cuerpo: Archivo 500.
- La palabra que manda en la frase: Archivo 700, el resto en 500.
- Números y códigos: JetBrains Mono 500.

Usa estas frases.

| Id | Texto |
|---|---|
| T1 | hola |
| T2 | ¿sabes quién es este pequeño? |
| T3 | o estos |
| T4 | Ellos son los anuros |
| T5 | los anfibios sin cola |
| T6 | En el mundo hay cerca de |
| T6b | 9009 especies |
| T7 | Colombia tiene cerca del 10% de especies unas 911 |
| T7c | siendo Colombia el segundo a nivel mundial |
| T7b | Para reconocerlos nació ANURA |
| T8 | ANURA es una iniciativa de 3 semilleros de la Corporación Universitaria Lasallista |
| T9 | Juntos creamos ANURA una app móvil para identificar anuros |
| T10 | Identificación por imagen |
| T11 | Modelo basado en contexto |
| T12 | IA local |
| T13 | No importa dónde estés ANURA se ejecuta en tu celular sin necesidad de internet |
| T13b | ¿Recuerdas que dijimos antes que ANURA es un modelo basado en contexto? |
| T13c | Para ello ANURA utiliza paquetes |
| T14 | Los paquetes descargables llevan solo la zona donde estás |
| T15 | Esas zonas se dividen en regiones |
| T15b | Los paquetes son un grupo de embeddings que tienen toda la información de varias especies |
| T15c | y el contexto, que es |
| T16 | ANURA usa datos geográficos para afinar el modelo |
| T17 | Un cuestionario paso a paso afina el modelo |
| T18 | Con más contexto el resultado de tu observación mejora |
| T19 | Cuando tengas internet puedes sincronizar con nuestro servidor |
| T20 | compartir tus observaciones |
| T21 | Conoce a nuevas personas con gustos similares |
| T22 | y puedes guardar tus observaciones favoritas |
| T23 | y si alguien cree que es otra especie puede proponerlo en los comentarios |
| T23b | Nosotros veremos la propuesta y un experto la validará |
| T24 | ¿Pero cómo hace todo esto ANURA? |
| T25 | ANURA ha pasado por distintas actualizaciones |
| T26 | Pasamos de 10 especies a 28 y luego a 41 |
| T28 | Antes todo era manual |
| T29 | Poco estandarizado y un solo desarrollador tenía el control |
| T30 | Ahora con el modo admin puedes tener control total del sistema |
| T27 | Gracias al panel de administración |
| T31 | y así obtienes un nuevo paquete listo para usar |

## Números (los del guion; no los cambies)

Mundo: **9009**. Colombia en el mapa: cerca del **10%**, unas **911**. El 911 es el mismo de la barra CO. No lo cambies. No escribas un porcentaje más fino.

Barras, de mayor a menor: BR 1208, CO 911, CN 716, EC 704, PE 694.
Ranking: BR oro, CO plata, CN bronce. El bronce es el tercero.

Especies por departamento: Antioquia 220, Chocó 195, Valle del Cauca 170, Cauca 160, Nariño 150, Meta 123, Amazonas 120, Putumayo 120, Caquetá 110, Cundinamarca 105, Santander 100, Boyacá 95, Risaralda 93, Tolima 90, Caldas 88, Huila 78, Norte de Santander 78, Magdalena 68, Quindío 68, Cesar 58, Vaupés 58, Guainía 50, Córdoba 50, Casanare 40, Vichada 40, Bolívar 40, Arauca 35, La Guajira 30, Sucre 30, Bogotá D.C. 13, San Andrés y Providencia 2.

Subregiones de Antioquia, solo especies: Valle de Aburrá 13, Oriente 24, Suroeste 17, Occidente 12, Norte 19, Nordeste 19, Magdalena Medio 15, Bajo Cauca 6, Urabá 15.

Línea del modelo: 10, luego 28, luego 41.

## Archivos que sí existen

- `D:\Anura\Boana cinereansis\large (1).jpg`
- `D:\Anura\data cleaned\Dendropsophus_bogerti\col_obs_39423_photo_65566.jpg`
- `D:\Anura\data cleaned\Sachatamia_electrops\IMG-20251013-WA0388.jpg`
- `D:\Anura\semillerso\SIVET.png` (la carpeta se llama `semillerso`)
- `D:\Anura\semillerso\DEDALOS.png`
- `D:\Anura\semillerso\ECOSOMOS.png`
- `D:\Anura\capturas movil\1.jpeg`
- `D:\Anura\capturas movil\pq.jpeg`
- `D:\Anura\capturas movil\paso a paso\1.jpeg`
- `D:\Anura\capturas movil\paso a paso\2.jpeg`
- `D:\Anura\capturas movil\paso a paso\3.jpeg`
- `D:\Anura\capturas movil\paso a paso\4.jpeg`
- `D:\Anura\capturas movil\paso a paso\6.jpeg`
- `D:\Anura\capturas movil\paso a paso\analisando.jpeg`
- `D:\Anura\capturas movil\paso a paso\result.jpeg`

---

## Cómo pegar una escena

Una sesión = una escena. Pega el bloque GLOBAL de abajo y solo el bloque de esa escena. Hecho cuando el MP4 de esa escena existe y las capturas de sus tiempos clave se ven bien.

### GLOBAL (péguelo siempre)

```
Eres el ejecutor de UNA escena de ANURA. El plano de esa escena viene pegado debajo. No abras el resto de D:\Anura\video\GUIA-OPUS.md.
Lee solo estas skills: C:\Users\user\.claude\skills\hyperframes-core, hyperframes-animation, hyperframes-cli. El estilo está en C:\Users\user\.claude\estudio-motion\estilo.md.
Motor: HyperFrames. Cada cuadro es función de t. Sin CSS transitions, sin setTimeout, sin requestAnimationFrame, sin Date.now(), sin Math.random() suelto. config.js aparte. Fuentes locales en D:\Anura\video\assets\fonts\. HUD apagado.
Formato: 1920x1080, 60 fps, márgenes 80 px. Fondo #1F7A33 o #EEF5EE o #1B1C1E, como diga la escena. Texto #FEFEFE sobre verde o sobre #1B1C1E. Texto #1B1C1E sobre claro. Prohibido #FFFFFF sobre #EEF5EE y #1F7A33 sobre #C6A15B.
Haz solo esa escena, en D:\Anura\video\escenas\sNN\. El mp4 sale mudo. No pongas música ni efectos.
Si esta sesión es una subsección nueva entre dos escenas, o es la re-render de una vecina para que esa subsección encaje: cambia solo la frontera que toca (salida de la izquierda, o entrada de la derecha). No reescribas el resto de la escena.
No unas el video. No abras la escena siguiente. No despliegues. No toques Postgres ni MinIO.
Para antes de borrar archivos o instalar dependencias.
Hecho cuando existen sNN.mp4 y npx hyperframes check no marca errores en esa carpeta. Si una URL de grabación no carga, para y dilo.
```

---

## S01 — Gancho, abanico · 0.00–3.50 · Sonnet · DIBUJAR

Fondo `#1F7A33`. Texto a la izquierda y cartas a la derecha, con 100 px de aire entre ambos.

- **hola** — x=80, top=320, Archivo wdth 70→115, peso 900, 120 px, `#FEFEFE`, alto de línea 0.9. 0.00–0.50: entra desde x−40, `outExpo`, blur horizontal de 14 px a 0.
- **¿sabes quién es este pequeño?** — x=80, top=470, ancho 900, Archivo 500, 40 px, alto de línea 1.2, `#FEFEFE`. 0.50–1.00: entra desde y+16, `outExpo`, sin blur. El bloque termina en x=980. Las cartas empiezan en x=1080: quedan 100 px de aire.

Cartas 300×720, radio 22, foto a cover. Sombra `18px 22px 36px rgba(0,0,0,0.35)`.
0° de CSS = carta vertical. 100° del plano = `rotate(10deg)`. 80° = `rotate(-10deg)`.

- Carta A, z=3, `large (1).jpg`. 0.50–1.50, `outExpo` y blur. Reposo: left 1080, top=160, `rotate(10deg)`.
- Carta B, z=2, Dendropsophus. 1.50–2.00. Reposo: left 1240, top=180, `rotate(0deg)`.
- Carta C, z=1, Sachatamia. 2.00–2.50. Reposo: left 1400, top=200, `rotate(-10deg)`. La carta C no pasa de x=1840.
- 2.50–3.50: quieto. El texto sigue.

Frontera: fondo verde, tres cartas en abanico, texto visible. La salida del texto es S02.

## S02 — Despliegue · 3.50–7.00 · Sonnet · DIBUJAR

Mismo fondo. Las cartas salen del reposo de S01.

- 3.50–4.00: **hola** y la pregunta suben 24 px y llegan a opacidad 0. Mismo tamaño con el que entraron.
- 3.75–4.75: las tres cartas se abren y se enderezan a `rotate(0deg)`, `outExpo`. Tamaño 400×600. Top 100. Centros x = 420, 960, 1500. El borde inferior queda en y=700. Margen lateral ≥ 80.
- 4.75–5.25: **o estos**. Centrado, top=764, Archivo 800, 80 px, `#FEFEFE`, alto de línea 1. Entra desde y+20, `outExpo`, blur vertical de 8 px a 0. Hay 64 px entre las cartas y esta frase. El texto termina cerca de y=844, a más de 80 px del borde inferior.
- 5.25–7.00: quieto.

Frontera: tres cartas en fila, **o estos** debajo, fondo verde.

## S03 — Diamond wipe · 7.00–8.50 · Sonnet · DIBUJAR

Sin texto. 1.5 s. Rombos de 56 px, de arriba abajo, cada fila escala 0→1 con `inOutExpo` y 0.04 s de retardo. Debajo, fondo `#EEF5EE` vacío. Las cartas no se deslizan: las tapa la rejilla.

Frontera: pantalla lisa `#EEF5EE`.

## S04 — Definición · 8.50–12.00 · Sonnet · DIBUJAR

Fondo `#EEF5EE`. Las dos líneas forman un bloque centrado en x y en y. No las subas al tercio alto.

- **Ellos son los anuros** — top=400, centrado, Archivo 800, 88 px, tracking −0.03 em, alto de línea 0.95, `#1B1C1E`. Sin coma al final. 8.75–9.25: desde y+28, `outExpo`, blur vertical 10 px a 0. Ancho máximo 1680.
- **los anfibios sin cola** — top=510, centrado, Instrument Serif itálica, 64 px, alto de línea 1, `#1B1C1E`. Sin punto. 9.00–9.50: igual, desde y+20. Gap de 24 px entre las dos líneas. No añadas una tercera.
- 11.25–12.00: las dos líneas bajan a opacidad 0 sin moverse de sitio.

## S05 — 9009 · 12.00–16.00 · Sonnet · DIBUJAR

Mismo fondo. Bloque centrado. La frase y el número quedan juntos: gap 12.

- **En el mundo hay cerca de** — top=340, centrado, ancho 1400, Archivo 500, 48 px, alto de línea 1.1, `#1B1C1E`. 12.00–12.50: desde y+16, `outExpo`.
- **9009** — top=420, centrado, Archivo wdth 125→100 en los últimos 0.25 s del conteo, peso 800, 200 px, alto de línea 0.9, `#1F7A33`, tabular. 12.50–14.00: cuenta de 0 a 9009, `outExpo`. Gap de 24 px bajo la frase. No pongas subtítulo debajo. El bloque queda en el centro del cuadro.
- 14.00–16.00: el número ya está en 9009. No hay barras.

## S06 — Barras · 16.00–22.00 · Sonnet · DIBUJAR

Mp4 mudo.

16.00–16.50: la frase y el 9009 viajan del centro de S05 a la izquierda, `inOutExpo`, sin cambiar palabras ni tamaños de golpe. Reposo:

- **En el mundo hay cerca de** — x=80, top=360, ancho 760, Archivo 500, 44 px, alto de línea 1.15, `#1B1C1E`. El texto acaba en x=840.
- **9009** — x=80, top=440, Archivo wdth 100, peso 800, 140 px, alto de línea 0.9, `#1F7A33`. No vuelve a contar. Gap de 20 px bajo la frase.

Gráfico a la derecha, área x=960–1840, y=180–960. Hay 120 px entre el texto (acaba en x=840) y el gráfico. Origen (1040, 860).

- 16.50–17.00: eje Y, flecha hacia arriba hasta y=240, grosor 3, punta 16, `#1B1C1E`, `outExpo`.
- 16.75–17.25: eje X, flecha hacia la derecha hasta x=1800, igual.
- Barras desde 17.50, una cada 0.25 s, de menor a mayor, izquierda a derecha. Ancho 108, gap 28. La de BR llega a y=280. `outExpo`.

| Orden | Código | Valor | Color |
|---|---|---|---|
| 1 | PE | 694 | `#7EB8DA` |
| 2 | EC | 704 | `#5B8FA8` |
| 3 | CN | 716 | `#E07A5F` |
| 4 | CO | 911 | `#1F7A33` |
| 5 | BR | 1208 | `#C6A15B` |

Código y valor: JetBrains Mono 500, 22 px, `#1B1C1E`. Código bajo la barra, valor encima. Medalla 36 px al terminar CN (bronce), CO (plata) y BR (oro). Puesto en `#1B1C1E`. PE y EC sin medalla.

20.75–22.00: texto, ejes y barras suben 24 px y llegan a opacidad 0.

## S07 — Mapa de Colombia · 22.00–29.00 · Sonnet · DIBUJAR

Corrección de contenido entre S06 y S08. Sigue siendo S07: no hay `S06a` y no se corren los tiempos de atrás. La frase vieja («Colombia es el segundo país más rico en anuros en el mundo») sale. Entran T7 a la izquierda del mapa y T7c debajo del mapa.

Fondo `#EEF5EE`. Agrega `colombia_municipios.geojson` por departamento. Escala `#D5E6D6` (2) a `#1F7A33` (220). Sin cifra sobre cada departamento. Antioquia es la mancha más oscura.

- Mapa: x=784, top=160, ancho 1056, alto 600. Borde derecho en x=1840. 22.00–23.00: opacidad 0→1 y escala 0.96→1, `outExpo`. El mapa termina en y=760.
- Izquierda, x=80, ancho 640, top=300. El bloque acaba en x=720: quedan 64 px hasta el mapa. No se monta encima.
  - **Colombia tiene cerca del** — Archivo 500, 36 px, alto de línea 1.2, `#1B1C1E`.
  - **10%** — gap 8, JetBrains Mono 500, 88 px, alto de línea 0.9, `#1F7A33`. Es número grande: el verde sobre claro aquí sí se lee.
  - **de especies** — gap 8, Archivo 500, 36 px, alto de línea 1.2, `#1B1C1E`.
  - **unas** — gap 20, Archivo 500, 32 px, `#1B1C1E`.
  - **911** — gap 8, JetBrains Mono 500, 140 px, alto de línea 0.9, `#1F7A33`. No lo cuentes: ya viene de la barra de S06.
  - 23.00–23.50: el bloque entra desde x−40, `outExpo`, blur horizontal de 12 px a 0 solo mientras se mueve.
- **siendo Colombia el segundo a nivel mundial** — x=784, ancho 1056, top=824, centrado en esa columna, Instrument Serif itálica, 36 px, alto de línea 1.15, `#1B1C1E`. Máximo dos líneas. Sin punto. Hay 64 px entre el mapa (acaba en y=760) y esta frase. La frase termina antes de y=1000. 23.50–24.00: desde y+16, `outExpo`, blur vertical de 8 px a 0.
- 24.00–27.75: quieto. La izquierda se lee (entra a las 23.50 y se queda 4.25 s). La frase de abajo se queda 3.75 s.
- 27.75–28.50: los dos textos suben 16 px, blur 8 px, opacidad 0. El mapa no se mueve.
- 28.50–29.00: el mapa viaja al centro, `inOutExpo`. Reposo: x=633, top=234, ancho 654, alto 372, opacidad 1, sin blur. Es el primer cuadro de S07a.

Frontera de entrada: pantalla lisa `#EEF5EE` (S06 no cambia). Frontera de salida: solo ese mapa centrado, sin texto. Hay que volver a renderizar S07 por esta salida.

No añadas un “2” extra. No pongas el 10% ni el 911 en verde si bajan de este tamaño. El cuerpo no va en verde.

## S07a — Para reconocerlos · 29.00–32.00 · Sonnet · DIBUJAR

Puente entre el mapa y los semilleros. 3 s. Fondo `#EEF5EE`. Carpeta `D:\Anura\video\escenas\s07a\`.

Primer cuadro, igual que el último de S07: mapa x=633, top=234, ancho 654, alto 372, opacidad 1, sin texto.

- 29.00–29.50: el mapa se encoge a escala 0.85 desde su centro, sube 20 px, blur a 14 px y opacidad 0, `inExpo`.
- **Para reconocerlos nació ANURA** — x=80, ancho 1760, top=440, centrado, Archivo 500, 96 px, alto de línea 1.15, `#1B1C1E`. **ANURA** en Archivo 800, mismo tamaño. Sin punto. 29.40–29.90: desde y+24, `outExpo`, blur 14 px a 0. El bloque termina cerca de y=550, a más de 80 px del borde.
- 29.90–32.00: quieto. Cuatro palabras, 2.1 s de lectura.

Último cuadro, el que toma S08: esa frase en top=440, opacidad 1, escala 1, sin blur. El mapa ya no está.

Capturas: 29.20, 30.20, 31.80.

## S08 — Semilleros · 32.00–37.00 · Sonnet · DIBUJAR

La frase de S07a ya está en pantalla. No la hagas entrar otra vez.

- 32.00–32.40: **Para reconocerlos nació ANURA** quieta, mismo sitio (x=80, ancho 1760, top=440, Archivo 500, 96 px, **ANURA** en 800).
- 32.40–32.90: esa frase sube, escala 0.55, blur 12 px y opacidad 0, `inOutExpo`.
- 32.65–33.15: **ANURA es una iniciativa de 3 semilleros de la Corporación Universitaria Lasallista** — top=80, centrado, ancho 1680, Archivo 500, 36 px, alto de línea 1.2, `#1B1C1E`. **ANURA** en Archivo 800. Sin punto. Desde y+16, `outExpo`. Dos líneas; el bloque termina cerca de y=166.
- 33.25, 33.50 y 33.75: SIVET, DÉDALOS, ECOSOMOS. Fila centrada, gap 80. Cada logo alto 480 px, top=230. Hay 64 px entre el título y los logos. Nombre 24 px bajo el logo: Archivo 700, 28 px, tracking 0.08 em, `#1B1C1E`. Entran con `outExpo` y escala 0.92→1. Los nombres quedan cerca de y=760, a más de 80 px del borde inferior.
- 36.25–37.00: título, logos y nombres bajan a opacidad 0.

Archivos: `D:\Anura\semillerso\SIVET.png`, `DEDALOS.png`, `ECOSOMOS.png`.

Frontera de entrada: la frase de S07a, ya visible. El resto de S08 (logos y salida) no cambia de idea. Hay que volver a renderizar S08 por esta entrada.

## S09 — La app y tres checks · 37.00–43.00 · Sonnet · DIBUJAR

- **Juntos creamos ANURA una app móvil para identificar anuros** — x=80, top=400, ancho 800, Archivo 500, 44 px, alto de línea 1.2, `#1B1C1E`. **ANURA** en Archivo 800. Sin coma ni punto. 37.00–37.50: desde x−24, `outExpo`. Tres líneas. El bloque acaba en x=880.
- Tarjetas x=980, ancho 840, alto 140, radio 20, blancas, gap 28, primera top=320. Hay 100 px entre el texto y las tarjetas. Check 28 px `#1F7A33`. Texto Archivo 600, 32 px, `#1B1C1E`, centrado en vertical dentro de la tarjeta. Las tres tarjetas terminan cerca de y=796.
  - 38.00: Identificación por imagen. `outExpo`.
  - 38.25: Modelo basado en contexto. `outExpo`.
  - 38.50: **IA local** en pastilla `#1F7A33` / letras `#FEFEFE`, Archivo 700, 32 px, radio 10, padding 8 px 14 px. Entra con `spring` 0.55. Sin borde sustituto.
- 42.50–43.00: la frase y las dos primeras tarjetas llegan a opacidad 0. La pastilla **IA local** vuela a x=80, y=140 y se queda. Ese es el título de S10.

## S10 — Siempre en el celular · 43.00–48.00 · Sonnet · DIBUJAR

Corrección de texto. La frase vieja («En monte desierto o llano ANURA funciona en tu celular») sale. Entra T13. Debajo, un wifi dibujado que pasa de encendido a apagado. Misma ventana de 5 s. S09 y S11 no se renderizan: la pastilla sigue entrando donde ya estaba y el teléfono sigue saliendo por la derecha.

La pastilla ya está en x=80, y=120: fondo `#1F7A33`, letras `#FEFEFE`, Archivo 800, 32 px, radio 12, padding 10 px 16 px.

- **No importa dónde estés ANURA se ejecuta en tu celular** — x=80, top=220, ancho 900, Archivo 500, 40 px, alto de línea 1.25, `#1B1C1E`. **ANURA** en Archivo 800. Sin comas ni punto. 43.00–43.40: desde y+16, `outExpo`.
- **sin necesidad de internet** — mismo x y ancho, gap 12 bajo la frase, Instrument Serif itálica, 36 px, alto de línea 1.15, `#1B1C1E`. Sin punto. Entra en el mismo tramo. El bloque acaba en x=980 y cerca de y=390. Catorce palabras: quieto desde 43.40 hasta 47.60.
- Wifi debajo del texto, no debajo del teléfono. Caja 112×112, x=80, top=454. Hay 64 px entre el texto (acaba cerca de y=390) y esta caja. Trazo dibujado, no un emoji ni una fuente de iconos. Tres arcos y un punto, grosor 6, puntas redondas, `#1F7A33`.
  - 44.00–44.50: los arcos se dibujan de dentro hacia fuera, uno cada 0.15 s, `outExpo`. El punto ya está. Wifi encendido.
  - 45.00–45.40: una diagonal `#1B1C1E`, grosor 6, se traza de esquina a esquina, `outExpo`. Arcos y punto bajan a opacidad 0.30. Wifi apagado. Se queda así.
- Teléfono: alto 780, top=150, centro x=1460. Su borde izquierdo queda en x=1280, a 300 px del texto y del wifi. Foto `D:\Anura\capturas movil\1.jpeg`. 43.25–43.75: entra desde la derecha, `outExpo`. El wifi no lo toca.
- 47.25–48.00: el teléfono sale solo hacia la derecha, centro x de 1460 a 2500, `inExpo`, blur horizontal de 0 a 18 px. No sale hacia la izquierda ni hacia arriba. 47.60–48.00: la pastilla, las dos líneas y el wifi se quedan en su x y bajan a opacidad 0.

Frontera: pantalla lisa `#EEF5EE`, sin teléfono, sin wifi y sin texto. Ese cuadro es el primero de S10a. El texto y el wifi de S10 no cambian.

## S10a — Del contexto a los paquetes · 48.00–56.00 · Sonnet · DIBUJAR

Puente entre el celular sin internet y los paquetes de zona. 8 s. Fondo `#EEF5EE`. Carpeta `D:\Anura\video\escenas\s10a\`. DIBUJAR. Sin fotos.

Primer cuadro: pantalla lisa `#EEF5EE`, igual que el último de S10.

- **¿Recuerdas que dijimos antes que ANURA es un modelo basado en contexto?** — centrado, x=80, ancho 1760, top=420, Archivo 500, 48 px, alto de línea 1.2, `#1B1C1E`. **ANURA** en Archivo 800. Conserva ¿ y ?. Dos líneas como máximo. El bloque termina cerca de y=535. 48.00–48.50: desde y+24, `outExpo`, blur vertical de 12 px a 0.
- 48.50–52.25: quieto. Doce palabras, 3.75 s de lectura.
- 52.25–52.75: la pregunta sube 40 px, blur 12 px y opacidad 0, `inExpo`.
- **Para ello ANURA utiliza paquetes** — centrado, x=80, ancho 1600, top=280, Archivo 500, 56 px, alto de línea 1.15, `#1B1C1E`. **ANURA** en Archivo 800. **paquetes** en Archivo 700. Sin punto. Una línea. El bloque termina cerca de y=344. 52.50–53.00: desde y+16, `outExpo`, blur vertical de 8 px a 0. Queda más arriba que la pregunta.
- Carpetas dibujadas, no una foto. Papel `#FFFFFF`, borde 2 px `#1F7A33`, lengüeta `#1F7A33`, radio 12, sombra `0 18px 28px rgba(27,28,30,0.16)`. Sin nombres ni cifras: no etiquetes regiones.
  - 53.25–53.75: una sola carpeta, 240×160, centro x=960, top=408. Hay 64 px bajo la frase (acaba cerca de y=344). Entra con `outBack`, escala 0.92→1.
  - 53.75–54.75: esa carpeta se abre en cinco, `outExpo`, blur horizontal solo mientras se mueven. Reposo, de izquierda a derecha: centros x = 420, 690, 960, 1230, 1500. Rotaciones −12°, −6°, 0°, 6°, 12°. Mismo tamaño. La de la izquierda no pasa de x=80. La de la derecha no pasa de x=1840. El borde inferior queda antes de y=1000.
- 54.75–55.50: quieto. La frase de arriba lleva en pantalla desde 53.00.
- 55.50–56.00: la frase y las cinco carpetas suben 24 px, blur 10 px y opacidad 0.

Último cuadro: pantalla lisa `#EEF5EE`. S11 entra como ya está, con el teléfono desde la derecha. No reescribas S10 ni S11: sus fronteras ya son esa pantalla lisa.

Capturas: 49.00, 53.20, 54.90, 55.40.

## S11 — Paquetes · 56.00–61.50 · Sonnet · DIBUJAR

- 56.10–56.70: el teléfono entra desde la derecha (centro x=2500 → 1380), alto 820, top=130, `outExpo`, blur horizontal. Foto `pq.jpeg`. Mismo marco que S10.
- 56.30–56.90: T14 en x=80, top=220, ancho 860, Archivo 500, 40 px, alto de línea 1.25, `#1B1C1E`. El bloque acaba cerca de y=420 y en x=940.
- 57.40–58.20: silueta de Antioquia en x=80, top=484, alto 420, ancho máximo 860, relleno `#1F7A33`. Hay 64 px entre el texto y el mapa. No la partas. No invade el teléfono.
- 60.70–61.50: el teléfono permanece; el texto T14 cruza a opacidad 0 mientras T15 entra en el mismo sitio. La silueta no salta de posición.

Capturas: 57.00, 58.40, 61.20.

## S12 — Nueve regiones · 61.50–68.50 · Sonnet · DIBUJAR

Continuidad del teléfono y de la silueta.

- En 61.50 el texto ya es T15, en x=80, top=80, ancho 1680, Archivo 600, 36 px, `#1B1C1E`. Una línea. Termina cerca de y=124.
- El teléfono queda arriba a la derecha: alto 360, top=160, centro x=1560. No tapa la lista.
- La silueta de Antioquia queda a la izquierda, x=80, top=188, alto 640. Su borde derecho no pasa de x=760.
- La lista ocupa x=860, top=560, ancho 960. Hay 100 px entre el mapa y la lista, y 40 px bajo el teléfono. No se superponen.
- Nueve filas, stagger 0.2 s. Número en JetBrains Mono 500, 22 px. Nombre en Archivo 500, 28 px. Solo especies. Ejemplo: `1   Valle de Aburrá    13 especies`. Alto de fila 44. Color `#1B1C1E`. La lista termina cerca de y=960.
- Orden: Valle de Aburrá 13, Oriente 24, Suroeste 17, Occidente 12, Norte 19, Nordeste 19, Magdalena Medio 15, Bajo Cauca 6, Urabá 15.
- No muestres observaciones ni municipios.
- 67.80–68.50: la lista y la silueta bajan a opacidad 0. El teléfono sale hacia la derecha, centro x hasta 2500, `inExpo`, blur horizontal. No sale a la izquierda ni hacia abajo.

Capturas: 64.40, 67.50.

Último cuadro: pantalla lisa `#EEF5EE`. El teléfono ya salió por la derecha. La lista y la silueta ya no están. Ese cuadro es el primero de S12a. No reescribas S12.

## S12a — Qué es un paquete · 68.50–73.50 · Sonnet · DIBUJAR

Puente entre las nueve regiones y los tres datos. 5 s. Fondo `#EEF5EE`. Carpeta `D:\Anura\video\escenas\s12a\`. DIBUJAR. Sin teléfono y sin mapa. Misma ventana: no corras los tiempos.

El texto queda arriba. Debajo, una red de puntos unidos, el dibujo de un embedding. No es un gráfico con cifras. Sin ejes, sin etiquetas, sin nombres de especie y sin un «512».

- **Los paquetes son un grupo de embeddings** — centrado, x=80, ancho 1760, top=160, Archivo 500, 48 px, alto de línea 1.2, `#1B1C1E`. **embeddings** en Archivo 700. Una línea. Sin punto. Termina cerca de y=218.
- **que tienen toda la información de varias especies** — mismo x y ancho, top=234, Instrument Serif itálica, 40 px, alto de línea 1.15, `#1B1C1E`. Gap de 16 px. Una línea. Sin punto. El bloque termina cerca de y=280.
- 68.50–68.75: las dos líneas entran juntas desde y+20, `outExpo`, blur vertical de 12 px a 0.
- 68.75–73.25: el texto quieto. Quince palabras, 4.5 s de lectura.

Puntos de 16 px, relleno `#1F7A33`, sin borde. Líneas de 3 px, `#1B1C1E`, opacidad 0.55 al terminar de trazarse. Posiciones fijas. Nada de `Math.random()`.

Grupo izquierdo:

| Id | x | y |
|---|---|---|
| A | 500 | 480 |
| B | 660 | 420 |
| C | 820 | 520 |
| D | 540 | 680 |
| E | 740 | 740 |
| F | 640 | 600 |

Grupo derecho:

| Id | x | y |
|---|---|---|
| G | 1140 | 460 |
| H | 1320 | 400 |
| I | 1480 | 540 |
| J | 1180 | 700 |
| K | 1400 | 780 |
| L | 1280 | 620 |

El punto más alto es H, en y=400. Hay más de 64 px bajo el texto. El más bajo es K, en y=780, antes de y=1000. El de la izquierda no pasa de x=80. El de la derecha no pasa de x=1840.

Uniones, solo estas: A–B, B–C, A–D, D–E, C–F, F–E, B–F, A–F, G–H, H–I, G–J, J–K, I–L, L–K, H–L, G–L, y un puente C–G.

- 69.25–70.50: los doce puntos entran en ese orden, uno cada 0.08 s, escala 0→1, `outBack`.
- 70.25–71.60: las líneas se trazan en el orden de la lista, una cada 0.05 s, `outExpo`. Cada trazo dura 0.45 s.
- 71.60–73.25: la red quieta, junto al texto.
- 73.25–73.50: texto, puntos y líneas suben 24 px, blur 10 px y opacidad 0.

Último cuadro: pantalla lisa `#EEF5EE`. S12b arranca ahí. No reescribas S12 ni S13.

Capturas: 69.00, 70.40, 72.00, 73.20.

## S12b — Y el contexto · 73.50–76.50 · Sonnet · DIBUJAR

Sigue la frase de S12a. 3 s. Carpeta `D:\Anura\video\escenas\s12b\`. DIBUJAR. Sin red y sin tarjetas.

- 73.50–74.00: barrido vertical de `#EEF5EE` a `#1F7A33`. No es el diamond.
- **y el contexto, que es** — centrado, x=160, ancho 1600, top=460, Archivo 500, 80 px, alto de línea 1.1, `#FEFEFE`. **contexto** en Archivo 800. Una línea. Sin punto. La coma se queda. 74.00–74.50: desde y+20, `outExpo`, blur vertical de 12 px a 0. El bloque termina cerca de y=548.
- 74.50–76.00: quieto. Cinco palabras, 1.5 s de lectura.
- 76.00–76.50: la frase baja a opacidad 0 y el fondo vuelve a `#EEF5EE` con el mismo barrido, ahora al revés.

Primer cuadro: pantalla lisa `#EEF5EE`, igual que el último de S12a. Último cuadro: otra vez lisa `#EEF5EE`, igual que el primero de S13. No reescribas esas dos.

Capturas: 74.20, 75.20, 76.40.

## S13 — Tres datos · 76.50–78.00 · Sonnet · DIBUJAR

1.5 s exactos. T16 centrado, top=80, ancho 1680, Archivo 600, 36 px, alto de línea 1.2, entra en 0.3 s. El título termina antes de y=170.

Tres cards 300×300, radio 32, blancas, fila centrada, gap 64, top=240. Hay 70 px entre el título y las cards. Las cards terminan en y=540.
- Izquierda: pin de mapa, icono simple, no una captura.
- Centro: marca de altitud (una cota y una cifra de ejemplo no; solo el símbolo de altura, sin número inventado).
- Derecha: esqueleto de imagen (rectángulo y un monte de líneas), no una foto de rana.

Entran juntas con `outBack` suave. A los 1.5 s siguen en pantalla: S14 las mueve.

Capturas: 77.20, 77.90.

## S14 — Al folder · 78.00–81.00 · Sonnet · DIBUJAR

- 78.00–78.80: las tres cards viajan al centro, se escalan a 220 px, rotaciones −8°, 0°, +8°, apiladas con 14 px de desplazamiento para que se vea el borde de cada una.
- 78.60–79.10: T16 sale.
- 79.00: aparece un folder abajo, centro x, top 760, ancho 360, alto 120, lengüeta incluida, color `#1F7A33`, radio 12.
- 79.20–80.20: la pila baja (`inOutExpo`) y se mete en el folder. Al cruzar el borde, un clip la oculta.
- 80.20–81.00: el folder se cierra un poco (la lengüeta baja 8 px) y queda solo.

Capturas: 78.80, 80.00, 80.90.

## S15 — Título del cuestionario · 81.00–84.00 · Sonnet · DIBUJAR

El folder sale en 0.3 s. Entra T17, top=420, centrado, ancho máximo 1500, Archivo 600, 48 px, alto de línea 1.2. Es un título solo: el aire alrededor es el margen, no un hueco por llenar. Hold hasta 84.00.

Capturas: 81.60, 83.80.

## S16 — Pasos 1 a 3 · 84.00–87.50 · Sonnet · DIBUJAR

T17 queda en top=80, centrado, ancho 1680, Archivo 600, 32 px. Tres teléfonos en columnas iguales, alto de marco 720, top=200. Hay 64 px entre el título y la etiqueta del teléfono. Entran desde la derecha y aterrizan en su columna.

- 84.10: columna izquierda, foto `paso a paso\1.jpeg`, etiqueta **Paso 1** Archivo 700, 28 px, 20 px sobre el marco. La etiqueta no toca el título ni el teléfono.
- 84.60: centro, `2.jpeg`, **Paso 2**. Misma etiqueta: 28 px, 20 px sobre el marco.
- 85.10: derecha, `3.jpeg`, **Paso 3**. Misma etiqueta.
- Hold hasta 87.50. No los quites: S17 los sustituye en el mismo sitio.

Capturas: 85.40, 87.30.

## S17 — Pasos 4, resumen, analizando · 87.50–91.00 · Sonnet · DIBUJAR

Los tres teléfonos de S16 salen juntos hacia la derecha en 0.35 s, centro x hasta 2500, `inExpo`, blur horizontal. No salen a la izquierda. Entran otros tres desde la derecha, con el mismo stagger de 0.5 s:

- **Paso 4** → `4.jpeg`
- **Resumen** → `6.jpeg`
- **Analizando** → `analisando.jpeg`

Mismas columnas y el mismo título T17 arriba. Hold. Al final de la escena los seis pasos ya se vieron; estos tres siguen en pantalla hasta que S18 limpia.

Capturas: 88.80, 90.80.

## S18 — Resultado · 91.00–95.50 · Sonnet · DIBUJAR

- 91.00–91.40: los tres teléfonos salen hacia la derecha, centro x hasta 2500, `inExpo`, blur horizontal. T17 baja a opacidad 0 en el sitio.
- 91.40–92.00: T18 en x=80, top=360, ancho 860, Archivo 600, 44 px, alto de línea 1.25. El bloque acaba en x=940.
- 91.50–92.10: entra desde la derecha un solo teléfono, alto 760, top=160, centro x=1460. Borde izquierdo en x=1280, a más de 64 px del texto. Foto `result.jpeg`. Etiqueta **Resultado**, Archivo 700, 28 px, 20 px sobre el marco.
- Hold hasta 95.10. 95.10–95.50: ese teléfono sale hacia la derecha, igual que los anteriores. No sale hacia arriba.

Capturas: 92.20, 94.80.

## S19 — Internet · 95.50–98.50 · Sonnet · DIBUJAR

Cambio de fondo en 0.4 s de `#EEF5EE` a `#1F7A33` (un barrido vertical corto, no diamond). Texto blanco.

T19 centrado, top=460, ancho máximo 1500, Archivo 600, 56 px, alto de línea 1.2, entra 95.90–96.30. Hold. La coma final es intencional: la frase sigue en S20. No pegues el texto al borde.

Capturas: 96.40, 98.20.

## S20 — Compartir · 98.50–103.00 · Opus · GRABAR

Sesión ya iniciada en `https://anura.juanlabs.me` como `sebastianmartinez06.js@gmail.com`. Si pide login, para.

Frase a la izquierda, x=80, top=360, ancho 700, Archivo 700, 48 px, alto de línea 1.15, `#FEFEFE`: **compartir tus observaciones**. El bloque acaba en x=780.

A la derecha, grabación de `https://anura.juanlabs.me/explorer/f3b3cc80-a011-4716-9a5f-762f9be94880`, dentro del marco redondeado (radio 24). Un clic en el control de compartir (`btn-secondary btn-icon`, el de compartir, no el corazón). Cursor 64 px. Zoom a 1.12 con ancla en ese botón justo antes del clic, 0.45 s. El panel de compartir debe verse abrirse. Marco en x=880–1840, y=140–980. Hay 100 px entre el texto y el marco.

Si la URL no carga, no simules usuarios ni fotos. Para y repórtalo.

Capturas: al abrir el share, y 102.50.

## S21 — Personas · 103.00–107.00 · Opus · GRABAR

Misma sesión pública: `sebastianmartinez06.js@gmail.com`. Si pide login, para.

El texto de S20 se sustituye en el mismo sitio, 0.3 s, por **Conoce a nuevas personas con gustos similares**. Sin punto. Mismo bloque: x=80, top=360, ancho 700, `#FEFEFE`. Dos líneas, Archivo 500, 44 px, alto de línea 1.2. **gustos similares** en Archivo 700. El bloque acaba en x=780 y cerca de y=466. Hay 100 px hasta el marco. Siete palabras: quieto desde 103.30.

Grabación de `https://anura.juanlabs.me/observaciones?view=observers`, contenedor `observers-list card`, mismo marco redondeado. Cursor 64 px. Zoom suave a 1.08 sobre la primera fila real, 0.6 s, y quédate ahí. Si la lista está vacía, no inventes filas: quédate en 1.00 y muestra el vacío.

Capturas: 104.00, 106.50.

## S22 — Me gusta · 107.00–111.00 · Opus · GRABAR

Misma sesión pública: `sebastianmartinez06.js@gmail.com`. Si pide login, para.

Texto a la izquierda. Arranca con **Conoce a nuevas personas con gustos similares** ya visible, como la dejó S21, y en 0.3 s pasa a **y puedes guardar tus observaciones favoritas**. Sin punto. La y va en minúscula: sigue la frase anterior. Mismo bloque: x=80, top=240, ancho 700, `#FEFEFE`. Dos líneas, Archivo 500, 44 px, alto de línea 1.2. **favoritas** en Archivo 700. El bloque acaba en x=780 y cerca de y=346. Hay 100 px hasta el marco. Seis palabras: quieto desde 107.30 hasta 111.00.

Debajo del texto, no dentro de la grabación. Corazón de 120 px, centro x=430, top=410. Hay 64 px bajo la frase. Trazo dibujado, no un emoji.

- 107.60–108.20: se siluetea. El contorno `#FEFEFE`, grosor 8, se traza de arriba abajo, `outExpo`. Relleno transparente.
- 108.20–108.50: el relleno pasa a `#FEFEFE`, `outExpo`.
- 108.50–109.80: salen seis corazones de 18 px, `#FEFEFE`, desde el centro. Uno cada 0.12 s. Tres suben y tres se abren a los lados. Recorrido 0.7 s, `outExpo`. La opacidad va de 1 a 0 en ese mismo tramo, así que al llegar ya no se ven. No pasan de x=780 ni tapan las palabras. Posiciones finales, en este orden: (430, 360), (360, 390), (500, 380), (300, 500), (560, 510), (250, 440).
- 110.40–111.00: el corazón grande baja a opacidad 0. Los chicos ya no están.

La grabación no cambia: `https://anura.juanlabs.me/explorer/38371927-7a28-48b3-873e-0ff1cc6cad5e`, mismo marco. Entra por `detail-card card glassmorphism`. Zoom a 1.12 con ancla en `heart-header-btn`, luego un clic. El corazón de la página debe cambiar de estado en cámara. Cursor 64 px. Vuelve a 1.00 en los últimos 0.4 s. Si repites la toma, quita el favorito fuera de cámara antes.

Último cuadro: la frase sigue, el corazón dibujado ya no está. S23 no hereda ese corazón. No reescribas S21 ni S23.

Capturas: 107.80, 108.40, 109.40, 110.80.

## S23 — Comentarios · 111.00–115.50 · Opus · EMULAR-UI

No abras el sitio para esta escena. Si necesitas mirar la interfaz real, usa la sesión de `sebastianmartinez06.js@gmail.com`. No guardes contraseñas.

No grabes esta. Emula solo `detail-card card comments-section`: cabecera, una observación ya visible (usa el texto real si lo lees del componente; si no puedes leerlo sin inventar el hilo, deja el compositor vacío y un comentario de interfaz genérico que ya exista en el código, no uno inventado de una especie).

T23 a la izquierda, x=80, top=280, ancho 700, Archivo 500, 36 px, alto de línea 1.3, `#FEFEFE`. El bloque acaba en x=780.

A la derecha, la tarjeta blanca, x=880, ancho 960, top=160, radio 20. Hay 100 px entre el texto y la tarjeta. Campo de comentario y el botón real de la UI («Proponer» o el que use el componente). Un cursor grande escribe el foco en el campo, sin enviar.

Capturas: 112.20, 114.80.

## S24 — Llega a evaluación · 115.50–119.50 · Opus · GRABAR

Sesión ya iniciada en `http://localhost:3010` como `sebastianmartinez06.js@gmail.com`. Si pide login, para.

La frase vieja («La solicitud llega a evaluación») sale. Entra T23b, arriba de la grabación. El marco se achica para dejarle sitio.

**Nosotros veremos la propuesta y un experto la validará** — centrado, x=80, ancho 1760, top=80, Archivo 500, 40 px, alto de línea 1.2, `#FEFEFE`. **validará** en Archivo 700. Una línea. Sin punto. 115.70–116.20: desde y+16, `outExpo`. El bloque termina cerca de y=128. Nueve palabras: quieto desde 116.20.

Marco más chico: x=160, y=192, ancho 1600, alto 720. Borde derecho en x=1760. Borde inferior en y=912. Hay 64 px bajo la frase. Radio 24, el mismo clip y el mismo borde. No tapa el texto.

Destino: `http://localhost:3010/observaciones`, tabla `overflow-x-auto rounded-lg border border-border bg-surface`, dentro de ese marco.

El admin está encendido: grábalo. Cursor 64 px. Zoom a 1.10 sobre la tabla al entrar, 0.5 s. Si la tabla no tiene filas, muestra ese vacío. No fabriques una rana ni un usuario.

Salida: el fondo verde se mantiene hasta S25. S23 y S25 no cambian.

Capturas: 116.40, 117.40, 119.00.

## S25 — La pregunta · 119.50–122.00 · Sonnet · DIBUJAR

2.5 s. Fondo `#1B1C1E`. T24 centrado, top=460, ancho 1600, Archivo 700, 64 px, alto de línea 1.15, `#FEFEFE`. Entra 119.70–120.10. Sale 121.60–122.00 en opacidad, y el fondo cruza a `#EEF5EE` en ese mismo final para que S26 no sea un corte.

Capturas: 120.40, 121.80.

## S26 — 10, 28, 41 · 122.00–128.00 · Sonnet · DIBUJAR

Fondo claro.

- Izquierda, x=80, top=280, ancho 760: T25, Archivo 600, 44 px, alto de línea 1.2. Entra 122.20. El bloque acaba en x=840.
- Derecha, x=960, top=180, ancho 880, alto 640: gráfica de línea. Hay 120 px entre el texto y la gráfica. Tres puntos: 10, 28, 41. La línea se dibuja de izquierda a derecha en 2.2 s (`inOutExpo`). Cada número, JetBrains Mono 500, 28 px, 16 px encima del punto. Trazo `#1F7A33`, grosor 4, punto 12 px.
- 125.20: T26 entra bajo T25, gap 24, Archivo 500, 32 px, ancho 760. No invade la gráfica.
- 127.40–128.00: la gráfica se queda; el bloque de texto se prepara para correr a la izquierda en S27. No lo borres del todo.

Capturas: 123.00, 125.40, 127.60.

## S27 — Administración · 128.00–131.00 · Sonnet · DIBUJAR

T25 y T26 se van. T27 entra al centro, top=470, ancho 1500, Archivo 700, 52 px, alto de línea 1.2. La línea de la gráfica se encoge hacia la derecha y desaparece en 0.5 s. Hold limpio.

Capturas: 128.60, 130.60.

## S28 — Antes, la terminal · 131.00–136.00 · Opus · EMULAR-UI

Si miras el admin real, entra como `sebastianmartinez06.js@gmail.com`. No guardes la contraseña.

- Izquierda, x=80, top=280, ancho 760. El bloque acaba en x=840.
- 131.10: T28, Archivo 700, 48 px, alto de línea 1.15.
- 131.80: T29, Archivo 500, 32 px, alto de línea 1.3, gap 20 bajo T28.
- Derecha: ventana x=960, y=260, 800×480, radio 16, fondo `#1B1C1E`, barra de tres puntos, JetBrains Mono 500, 22 px, `#D7E8D4`. Hay 120 px entre el texto y la ventana.
- Dentro se escribe código real, copiado de `D:\server\Anura\services\dataset-service\src\reglas.js`. Estas tres líneas, en este orden, sin cambiar una letra y sin el comentario de arriba del archivo:

```
const MIN_FOTOS_ENTRENABLE = 10;
const MIN_INDIVIDUOS = 3;
const esEntrenable = (m) => m.fotos_activas >= MIN_FOTOS_ENTRENABLE && m.individuos >= MIN_INDIVIDUOS;
```

- La tercera línea no cabe en el ancho: se parte sola. No la recortes ni la reescribas. Sin prompt, sin secretos y sin comandos.
- 131.50: empieza a teclearse. 0.015 s por carácter. Pausa de 0.10 s entre líneas. Termina cerca de 133.98 y se queda quieta hasta que la ventana se cierra. Una tecla al completar cada línea: 131.98, 132.46 y 133.98.
- 134.80–136.00: la ventana se cierra (escala y hacia el centro) cuando entra T30 en la izquierda. T30 es «Ahora con el modo admin puedes tener control total del sistema», sin punto.

Capturas: 132.20, 133.20, 134.40.

## S29 — Resumen del admin · 136.00–140.00 · Opus · EMULAR-UI

No abras el login. La sesión ya está iniciada. Arriba a la derecha, la línea real del panel: «Sebastián Martínez · super usuario». No escribas ni guardes la contraseña.

T30, x=80, top=80, ancho 1680, Archivo 500, 36 px, alto de línea 1.2, `#1B1C1E`. **control total** en Archivo 700. Una línea. Sin punto: **Ahora con el modo admin puedes tener control total del sistema**. El panel empieza en y=150, sin tapar esta línea. Once palabras: quieta desde 136.40.

Emula `/dashboard` ya cargado, no el estado «Leyendo del servidor…». Sidebar oscuro con las áreas reales de `nav.ts` (Inicio, Analítica, Modelo, App, Operación, Sistema). Contenedor `flex-1 overflow-y-auto px-2 py-3` para el nav, y el main con radio 16, borde y clip.

Las cuatro tarjetas de `dashboard-live.tsx`, con sus etiquetas reales. Cifras de esta toma, no una lectura del servidor:

| Tarjeta | Valor | Hint |
|---|---|---|
| Observaciones refutadas | 0 | 0 sin decidir |
| Paquetes descargables | 9 | 9 subregiones |
| Especies en el dataset | 41 | 41 en el catálogo |
| Actividad en 7 días | 0 | eventos de la app |

El 41 es el de la línea del modelo. El 9 es el de las regiones de S12. Los ceros son la toma vacía de esas dos tarjetas, no un fallo de carga.

Debajo, los dos paneles del componente. Problemas abiertos: el texto real cuando no hay nada, «Nada pendiente por ahora.» Actividad reciente: «Todavía no hay acciones en la bitácora.» No inventes nombres ni especies en la bitácora.

Capturas: 136.80, 138.50, 139.50.

## S30 — Conseguir · 140.00–144.00 · Opus · EMULAR-UI

La sesión sigue abierta, como en S29: «Sebastián Martínez · super usuario». No hay login. No guardes la contraseña.

El nav permanece. Se resalta **Conseguir**. El main, al lado del navbar, es la pantalla real, no un título con el blurb. Las tablas pueden ir vacías. Los botones y los rótulos se copian tal cual.

Uno por beat, sin recargar la página:

- **Scraping** (`scraping-console.tsx`). Título «Scraping». Acordeones «iNaturalist» y «GBIF». Botón **Consultar muestra**. Casilla «Ensayo: taxonomía y conteo, sin bajar archivos». No lances la consulta.
- **Imágenes** (`server-photos-card.tsx`). Título «Imágenes». Botón **Subir foto**. En la fila, **Invalidar**, **Excluir** y **Revertir invalidación**. Sin fotos inventadas: la lista vacía del propio componente.
- **Especies** (`server-catalog.tsx`). Título «Especies». Botón **Añadir especie** y **Editar nombre y familia**. La tabla puede estar vacía.

Pie en x=80, top=960, ancho 1760, Archivo 500, 28 px: **Conseguir las fotos y nombrar las especies.** No tapa el panel. Hay al menos 48 px entre el panel y este pie.

Capturas: en cada uno de los tres títulos.

## S31 — Limpiar · 144.00–147.50 · Opus · EMULAR-UI

Misma cáscara y la misma sesión. Resalta **Limpiar**. El main copia la pantalla.

- **Ficha** (`species-sheet-manager.tsx`). Título «Ficha de especie». Botones **Calcular altitudes faltantes**, **Guardar como manual** y **Volver al calculado**.
- **Calidad** (`data-cleaning-console.tsx`). Título «Limpieza del dataset». Botones **Pendientes** y **Decididos**. Si el conteo es 0, el botón dice «Pendientes (0)» y «Decididos (0)». No inventes filas.

Pie en x=80, top=960, Archivo 500, 28 px: **Limpiar lo que no debe entrenar.**

Capturas: 144.80, 146.80.

## S32 — Procesar · 147.50–151.50 · Opus · EMULAR-UI

Misma cáscara. Resalta **Procesar**. No afirmes que un trabajo terminó. No toques C3.

- **Worker** (`worker-console.tsx`). Título «Worker y embeddings». Tarjetas «Workers», «Encoders registrados», «Nuevo trabajo de vectores» y «Cola e historial». Botón **Crear trabajo**. Campos «Encoder» y «Fotos». La cola puede estar vacía.
- **DB vectorial** (`index-panel.tsx`). Botón **Medir latencia**. El rótulo «Latencia de búsqueda».
- **Centroides** (`real-centroids-card.tsx`, `dataset-version-card.tsx`). Título «Centroides y morfos». Botones **Calcular centroides** y **Crear versión**.

Pie en x=80, top=960, Archivo 500, 28 px: **Procesar: vectores, centroides y lo que se confunde.**

Capturas: 148.40, 150.80.

## S33 — Validar · 151.50–155.00 · Opus · EMULAR-UI

Misma cáscara. Resalta OSR y Validación.

- **OSR** (`osr-console.tsx`). Título «OSR · rechazo de desconocidas». Tarjetas «Calcular la propuesta», «Puntos de operación» y «Validar τ». Botones **Calcular propuesta**, **Usar** y **Validar τ**. Campo «τ (distancia de Mahalanobis)» y «Nota (opcional)» con placeholder «Por qué este τ». Si no hay τ, la insignia real «Sin τ validado». No calcules uno.
- **Validación** (`technical-validation-console.tsx`). Título «Validación técnica». Tarjetas «Encoder del teléfono», «Centroides», «Umbral OSR» y «Especies de la subregión». Si no hay subregión, el texto real «Aún no hay subregiones para validar».

Pie en x=80, top=960, Archivo 500, 28 px: **Una persona valida el rechazo. Luego se mira si está listo.**

Capturas: 152.40, 154.40.

## S34 — Publicar · 155.00–159.00 · Opus · EMULAR-UI

Misma cáscara. Main de Release (`compiler-console.tsx`). Título «Release».

Botón **Compilar paquete**. Al pulsarlo en la toma, el rótulo pasa a **Compilando…**, que es el texto del propio botón. No dibujes una barra de 0 a 100: esa barra no está en la interfaz. También están **Aprobar (científica)**, **Aprobar (técnica)**, **Publicar** y **Cancelar**. Tabla con columnas Versión, Estado, Especies, Tamaño, Compilado, Aprobaciones. Si no hay filas, el texto real «Aún no hay subregiones para compilar» o «Todavía no se puede compilar». No publiques nada.

Pie en x=80, top=960, Archivo 500, 28 px: **Compilar y publicar el paquete de la región.**

Capturas: 156.00 y cuando el botón ya dice Compilando…

## S35 — Paquete listo · 159.00–163.00 · Opus · EMULAR-UI

Dos bloques con el mismo centro vertical, y=540.

A la izquierda, la pantalla de Release, con **Compilar paquete** y **Publicar** visibles. No es un panel en blanco. Se reduce y se corre a la izquierda. Al quedar quieta, su centro vertical sigue en y=540, igual que el grupo de la derecha.

A la derecha, el grupo del paquete, también centrado en y=540. El icono va arriba. El texto va debajo, bien separado. Nada de este grupo se pega al borde inferior.

- Icono de paquete, 120 px. Baja 80 px y aterriza, 0.8 s, `outBack`.
- 96 px más abajo, T31: **y así obtienes un nuevo paquete listo para usar**. Archivo 700, 44 px, `#1B1C1E`, centrado en su columna. Una línea. Sin punto.
- El centro vertical del icono más esa frase es y=540, el mismo que el de la pantalla de Release.

Hold 1.5 s después de aterrizar.

Capturas: 160.20, 162.40.

## S36 — Cierre · 163.00–167.00 · Sonnet · DIBUJAR

Fondo `#1F7A33`. Entra el wordmark **ANURA** en top=420, Archivo wdth 100, peso 900, 120 px, `#FEFEFE`, centrado. Debajo, gap 28, Instrument Serif itálica, 40 px: **Identificación de anuros.** El bloque termina antes de y=640. No lo agrandes hasta los bordes.

163.20–163.70 entrada con `outBack`. Hold. En el último medio segundo no añadas un iris ni un loop: esta pieza no se repite en bucle. Termina en el wordmark quieto, para que el corte final sea una imagen estable.

Capturas: 163.80, 166.50.

---

## Montaje (no lo hagas hasta que cada escena esté aceptada)

Orden S01→S36, y en medio cada subsección (`S06a`, …) en el hueco que esta guía le dio. Las fronteras ya coinciden en color de fondo. Al unir, recorta 0 s de negro entre medias. El diamond de S03 es el único wipe largo. El resto son continuidades de 0.3–0.4 s ya metidas dentro de cada escena. Si acabas de insertar una subsección, no unas hasta que sus dos vecinas estén re-renderizadas.

Archivo final previsto: `D:\Anura\video\anura-presentacion.mp4`.
Poster: el cuadro de S01 en 2.35 s (el abanico), no el cierre.
