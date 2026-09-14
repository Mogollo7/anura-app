---
title: "Estado del Mockup Final â€” Pendientes y Agentes"
proyecto: Anura
tipo: proceso-desarrollo
estado: cerrado-fidelidad-pendiente-fotos
tags: [anura, proceso, penpot, mockup, agentes, pendientes]
---

# Estado del Mockup Final â€” Pendientes y Agentes

[[Anura â€” àndice General]] · [[Proceso de Desarrollo â€” àndice]] · [[Diseño de Interfaz (Penpot)]] · [[Entorno de Trabajo y MCP]]

> [!abstract] Qué documenta esta nota
> Snapshot del pase de correcciones sobre `Mockup Final` en Penpot (2026-09-07): qué pedí, qué quedó resuelto, qué sigue pendiente, y por qué los intentos automatizados se cortaron. El plan operativo detallado con coordenadas exactas vive en el scratchpad de la sesión (`anura-correcciones-v2.md`) â€” esta nota es el resumen persistente para retomar sin perder contexto.

> [!success] Cierre del pase de fidelidad (2026-09-07)
> Los 42 boards de `Page 1` tienen ya equivalente construido en `Mockup Final` (0 faltantes, verificado por diff de inventario) y las correcciones de distribución/fidelidad listadas en la §2 quedaron aplicadas y verificadas visualmente (`export_shape`) contra el original. `Page 1` permanece intacta (42 boards, sin shapes modificados â€” verificado directamente, no solo por reporte de agente). **Lo àºnico que sigue abierto es contenido, no estructura:** las fotos reales que el usuario sube manualmente, la validación de dos decisiones de diseño tomadas por los agentes (ver §3), y una posible revisión estética de los 11 boards nuevos ya que fueron construidos con inferencia razonada del contenido a partir del nombre y patrones existentes, no con estructura 1:1 tan detallada como el resto (ver nota en §2).

## 1. Contexto

El wireframe original (`Page 1`, 42 boards, **nunca se modifica**) se está
convirtiendo en un mockup final de alta fidelidad (`Mockup Final`, 48 boards)
aplicando lenguaje visual estilo Apple HIG (glass/blur, iconos vectoriales,
texto real) sobre la paleta derivada del logo (naranja/dorado de la rana),
NO la paleta gris de placeholder del wireframe original (esa es
deliberadamente de baja fidelidad, segàºn el propio contrato de diseño).

Reglas que gobiernan todo el pase: **fidelidad total a la distribución y
función de cada elemento del wireframe original primero â€” aporte propio
después, y solo si es pertinente.** Ante duda, verificar contra `Page 1` con
el MCP de Penpot antes de asumir.

## 2. Correcciones solicitadas por mí â€” RESUELTAS

- [x] `LOGIN OR SINGUO (bienvenida)`: copy exacto verbatim ("Identificá los
  anuros de Colombia desde el campo, con o sin señal."), solo logo + título +
  párrafo + 2 botones + mensaje de entrar sin conexión. Sin hero image ni
  lista de features inventada.
- [x] `profile (variante ajena)`: kebab renombrado a "Acción: puntos",
  botones "Seguir"/"Reportar o bloquear" en vez de "Editar perfil"/"Compartir".
- [x] `ajustes` â†’ sección "Apariencia": 3 modos (Claro/Oscuro/Luz roja) + 6
  muestras de acento con nombre, construida.
- [x] **(2026-09-07, pase Opus)** Variación de fondo por pantalla: 14 pop-ups
  a superficie oscura de marca (`N-900`) con recoloreado de contenido para
  contraste; 10 boards con header de foto de fondo real + atenuado negro 35%
  (receta `Atenuado sobre foto · negro 35% (HIG Clear)`) desvanecido al
  neutro base; planos claro/medio diferenciados en `LOGIN OR SINGUO`, ambos
  `profile`, `favoritos (listado)`. `Detalles de observación` y `ESPECIE,
  FAMILIA, GENERO` ya tenían el patrón correcto, no se tocaron.
- [x] **(2026-09-07, pase Opus)** `home`: eliminados 11 elementos duplicados
  (3 botones x2, carrusel, textos, 4 círculos). Orden final correcto: `top`
  (con rectángulo de fondo restaurado) â†’ carrusel 337à—300 â†’ 4 círculos de
  paginación â†’ 3 botones circulares (Foto ID/Audio ID/Paso a paso, etiquetas
  renombradas) â†’ chip "Salida de campo en curso" â†’ navbar. Geometría
  verificada contra el original. Nota: el grupo de 3 botones mide 326à—117 en
  vez de 306à—95 porque incluye las etiquetas de texto debajo (no shapes en
  el original).
- [x] **(2026-09-07, pase Opus)** `COMENTARIOS`: board construido â€” título +
  4 comentarios + hilo anidado con tarjeta de identificación propuesta
  (Dendrobates auratus, en revisión experta) + campo de entrada al pie.
  Texto real de discusión de identificación, no lorem ipsum.
- [x] **(2026-09-07, pase Opus)** `ajustes`: restauradas Cabecera de perfil
  (y=100), Zonas descargadas (y=210), Cerrar sesión (y=640) en sus
  posiciones exactas. Apariencia reconstruida con espaciado correcto (6
  muestras 48px, gap 13, margen 19). **Decisión de diseño del agente a
  validar:** Apariencia absorbió el slot de "Modo claro/oscuro" (y=286) en
  vez de convivir con él, para no duplicar el control de tema â€” desviación
  del orden literal pedido pero consistente con la intención de §6 del plan.
- [x] **(2026-09-07, pase Sonnet, 3er intento â€” los dos primeros fallaron
  por caída de conexión sin tocar nada)** `profile (variante propia)` y
  `(ajena)`: botones "Editar perfil"/"Compartir" eliminados en la propia,
  kebab renombrado a "Acción: puntos" en ambas, con nombre de capa
  documentando la relación al sheet correspondiente. Construidos dos boards
  nuevos de action-sheet (`Sheet: Acciones de perfil (propia)` con "Editar
  perfil"/"Compartir perfil"/"Cancelar"; `Sheet: Acciones de perfil (ajena)`
  con "Compartir perfil"/"Copiar enlace del perfil"/"Cancelar"), mismo
  patrón visual que los demás pop-ups (superficie oscura, radio 30).
  Verificado visualmente con `export_shape` y con inspección directa de
  `shapeStructure` â€” sin corrupción pese a un incidente técnico reportado
  por el agente (mal uso de `setParentXY` corregido en el momento).
- [x] **(2026-09-07, pase Sonnet)** Sección `favoritos` insertada en ambas
  variantes de `profile` (contenedor 320à—250 + botón "Ver más favoritos"
  245à—50), reutilizando la foto real de `Dendrobates truncatus` ya subida.
  Boards extendidos en altura (propia 1120, ajena 1018) para dar cabida sin
  romper navbar/FAB.
- [x] **(2026-09-07, pase Sonnet)** `PANTALLA DE CARGA INICIO`: logo
  realineado a relY 321, loader de dos puntos reposicionado a relY 520
  (antes quedaba invisible, superpuesto sobre el propio logo). Sigue
  pendiente de la imagen real del logo (usuario la sube manualmente).
- [x] **(2026-09-07, pase Sonnet)** `LOGIN OR SINGUO`: rectángulo de fondo
  394à—393 en (1,459) restaurado, radio 30, enviado al fondo del z-order.
- [x] **(2026-09-07, pase Sonnet)** `Resultado open-set: especie no
  registrada`: imagen corregida de 393à—280 a 335à—350 en (29,98), igual que
  `IMAGEN DE OBSERVACION`. Contenido posterior desplazado en cascada para
  mantener espaciados relativos.
- [x] **(2026-09-07, pase final)** `Detalles de observación (resultado)`:
  los 3 elementos que faltaban ya están â€” instancia real del componente
  `Desplegable de detalles para análisis semántico`, grupo `COMENTARIOS DEL
  OBSERVADOR` (título + 5 filas placeholder), etiqueta de revisión experta.
  Se agregaron al final del board (alto 1239â†’1552) sin reflowir los ~60
  elementos ya construidos entre `aciones` y "Ver ficha técnica" â€” el orden
  semántico se respeta pero no es exactamente la posición intercalada del
  original; revisar si esto importa visualmente. Verificado con
  `export_shape`.
- [x] **(2026-09-07, pase final)** Los 11 boards que faltaban del wireframe
  ya están construidos en `Mockup Final`: `ajustes modo oscuro` (clon de
  `ajustes` con remapeo de color a paleta oscura), `EDIT` (formulario de
  edición de perfil), `Fotos` (grilla 2à—2), `Ubicación geográfica` (clon del
  cluster de mapa de `explorar`), `Identificadores destacados` (buscador +
  6 filas de usuario), `Sonidos nocturnos de la salida` (clon de `Añadir
  audio` + cantos identificados), `Notas de la salida de campo` (campo de
  texto + notas guardadas), `Especies del género o familia` (buscador +
  grilla 3à—2), `Seguidos, seguidores y favoritos.` (3 pestañas + lista),
  `Fotos y observaciones` (grilla 4à—2 + navbar), `Explora más.` (2à—2 +
  botón "Ver más"). **Verificado directamente por mí (no solo por reporte
  del agente):** los 11 boards existen con tipo `board` y dimensiones
  razonables; `Page 1` sigue en 42 boards intactos. Diff de inventario final
  del agente: 42/42 boards del original con equivalente construido.
  **Nota importante:** a diferencia de las correcciones anteriores (que
  partían de estructura ya verificada contra `Page 1` con `shapeStructure`
  para cada elemento), estos 11 boards se construyeron leyendo la
  estructura real de cada uno en `Page 1` pero razonando el contenido
  final con más libertad de criterio propio (reutilizando patrones ya
  existentes en `Mockup Final` como plantilla) â€” más cerca del criterio
  "aporte propio" que "replica tal cual" que rige el resto del pase. Vale
  la pena una revisión visual manual de estos 11 antes de darlos por
  definitivos.

## 3. Correcciones solicitadas por mí â€” PENDIENTES (confirmadas contra `Page 1`)

**Estructura y fidelidad: ya no queda nada pendiente en esta categoría** â€”
lo que sigue abajo es contenido (fotos) y dos puntos de validación de
criterio, no distribución/estructura sin resolver.

- [ ] **Revisar decisión de diseño del pase Opus:** dejó `Añadir foto`,
  `Añadir audio` y `Salida de campo en curso` con superficie oscura (el
  original los tenía plano medio/degradado) porque su contenido ya estaba
  diseñado en oscuro y recolorear los 3 boards completos quedaba fuera de
  alcance del pase â€” validar si esto se acepta tal cual o se corrige en un
  próximo pase.
- [ ] **Contenedores de imagen sin foto montada** (esperando que subas la
  foto tàº): 10 `Hero · foto de fondo hábitat` (headers de `INICIAR
  SECCION`, `crear cuenta`, `home`, `ajustes`, `explorar`, `Zonas
  descargadas`, `Paso 1-5`), 6 `foto de perfil` + `Avatar del autor` +
  `Miniatura de la observación propuesta` en `COMENTARIOS`, `Avatar del
  perfil` en la cabecera de `ajustes` (todos del pase Opus); más, del pase
  Sonnet: `Contenedor de imagen 167à—196` en las rejillas de ambas variantes
  de `profile`, y `Fotografía de la observación` (335à—350, tamaño ya
  corregido) en `Resultado open-set`. La sección `favoritos` de ambas
  variantes de `profile` Sà quedó con foto real (reutilizó `Dendrobates
  truncatus`, ya subida) â€” no necesita nada.
- [ ] `PANTALLA DE CARGA INICIO`: sigue pendiente la imagen real de
  `logo.png` (el contenedor vectorial ya quedó realineado por el pase
  Sonnet, solo falta que subas el archivo).
- [ ] **Revisión visual manual recomendada de los 11 boards nuevos**
  (`ajustes modo oscuro`, `EDIT`, `Fotos`, `Ubicación geográfica`,
  `Identificadores destacados`, `Sonidos nocturnos de la salida`, `Notas de
  la salida de campo`, `Especies del género o familia`, `Seguidos,
  seguidores y favoritos.`, `Fotos y observaciones`, `Explora más.`) â€” se
  construyeron con más libertad de criterio propio que el resto del pase
  (ver nota en §2), así que conviene mirarlos en Penpot antes de darlos por
  definitivos, aunque estructuralmente ya están completos y verificados.

## 4. Estado de los intentos automatizados

| # | Resultado | Causa |
|---|---|---|
| 1 | Detenido manualmente (~4 min) | Instrucciones iniciales incorrectas (paleta gris en vez de la del logo) â€” corregido antes de causar daño real |
| 2 | Detenido manualmente (~4 min) | Sobre-corrección: usé paleta gris cuando el usuario pidió la del logo |
| 3 | Completado (~42 min) | Construyó 48 boards pero con desviaciones de fidelidad â€” origen de todas las correcciones de este documento |
| 4 | Falló de inmediato | Conexión del plugin de Penpot caída (`ConnectionRefused`) |
| 5 | Falló de inmediato | Conexión caída otra vez al arrancar |
| 6 | Detenido manualmente por error mío | Duplicé el agente en vez de continuarlo â€” no había forma de enviar mensaje a un subagente ya corriendo en este entorno, así que terminó lanzando uno nuevo en paralelo; se detuvo antes de tocar nada |
| 7 | Detenido manualmente por el usuario (~14 min) | El usuario pidió parar para consolidar todo en este documento antes de seguir â€” corrigió 3 de ~15 ítems, dejó 2 boards en estado de reconstrucción a medias (`home` con duplicados) |
| 8 | Completado (~20 min, Opus) | Pase de piezas de alta dificultad: fondo por pantalla (14 pop-ups + 10 headers con foto), `home` deduplicado, `COMENTARIOS` construido, `ajustes` restaurado. `Page 1` verificada intacta (42 boards). Pendiente: icono de chat en `Detalles de observación` no existe todavía, no se pudo cablear a `COMENTARIOS`. |
| 9 | Falló de inmediato, 0 cambios | Conexión caída al arrancar (Sonnet, dificultad media) |
| 10 | Falló de inmediato, 0 cambios | Conexión caída otra vez al arrancar (mismo pase, relanzado tras confirmar conexión propia â€” se cayó de nuevo en la ventana entre verificación y arranque del agente) |
| 11 | Completado (~21 min, Sonnet) | 3er intento del pase de dificultad media: `profile` propia/ajena (action-sheets + favoritos), logo de carga realineado, rectángulo de fondo de `LOGIN OR SINGUO`, tamaño de imagen de `Resultado open-set` â€” todos resueltos y verificados. `Detalles de observación` quedó parcial (iconos sociales sí, 3 elementos adicionales no). Incidente menor autocorregido (mal uso de `setParentXY`), verificado sin corrupción tras el hecho por mí directamente vía `shapeStructure`. |
| 12 | Falló de inmediato, 0 cambios | Conexión caída al arrancar (pase final: 3 elementos de `Detalles de observación` + 11 boards nuevos) |
| 13 | Completado (~21 min, Sonnet) | Pase final relanzado tras confirmar conexión propia: los 3 elementos restantes de `Detalles de observación` construidos, y los 11 boards faltantes del inventario construidos desde cero (leyendo estructura real de cada uno en `Page 1`). `Mockup Final` pasó de 57 a 68 boards raíz. Diff final del agente: 42/42 boards del original con equivalente. Verificado por mí directamente (no solo reporte del agente): `Page 1` intacta, los 11 boards existen con tipo `board` y dimensiones razonables, los 3 elementos de `Detalles de observación` presentes. Con esto se cierra el pase de fidelidad estructural â€” solo queda contenido (fotos) y revisión visual opcional. |

**Lección operativa:** la conexión del plugin de Penpot (bridge WebSocket
navegadorâ†”MCP) es el punto más frágil de todo el flujo â€” se cae con
frecuencia, incluso a mitad de sesión del usuario principal, no solo al
arrancar agentes. Cualquier agente nuevo debe: (a) verificar conexión con una
llamada trivial antes de empezar, (b) permitirse como máximo un reintento
ante el primer fallo, (c) detenerse y reportar de inmediato ante cualquier
fallo posterior â€” nunca reintentar en bucle ni dejar el archivo a medias sin
decirlo explícitamente. Además: **nunca lanzar un agente nuevo para
"continuar" uno que ya está corriendo** â€” verificar primero con `ListAgents`
si sigue vivo; si no hay forma de enviarle un mensaje, esperar a que termine
o detenerlo explícitamente antes de relanzar, para no correr dos agentes en
paralelo sobre el mismo archivo.

## 5. Clasificación de tareas pendientes por dificultad â€” para elegir modelo del próximo agente

**Alta dificultad (Opus recomendado):** requiere juicio de diseño, decisiones
no triviales, o coordinar muchos elementos con estado visual (glass/blur,
degradados, jerarquía) sin instrucciones 1:1 ya resueltas.
- Aplicar la variación de fondo por pantalla (flat/oscuro/degradado) con la
  paleta de marca â€” implica criterio visual, no solo copiar coordenadas.
  ([[Diseño de Interfaz (Penpot)]])
- Reconstruir `home` completo (carrusel + paginación + 3 botones sin
  duplicar + top) â€” màºltiples piezas interdependientes con estado dinámico
  documentado (categorías rotativas, círculo activo).
- Construir el board `COMENTARIOS` con el campo de entrada tipo teclado y
  cablear la interacción desde `Detalles de observación`.
- Decidir e implementar la reconstrucción de `ajustes` sin volver a perder
  Cabecera de perfil / Zonas descargadas / Cerrar sesión al integrar
  Apariencia en el hueco disponible.

**Dificultad media (Sonnet recomendado):** instrucciones ya concretas con
coordenadas/nombres exactos verificados contra `Page 1`, pero con varios
pasos y necesidad de verificación visual (`export_shape`) al final.
- Corregir `profile (variante propia)`: eliminar botones, renombrar icono,
  construir action-sheet, restaurar `favoritos` en ambas variantes.
- Restaurar los 3 iconos sociales en `Detalles de observación` + los
  elementos adicionales confirmados (Desplegable de análisis semántico,
  COMENTARIOS DEL OBSERVADOR, etiqueta de revisión experta).
- Reemplazar el logo vectorial por la imagen real en `PANTALLA DE CARGA
  INICIO` (patrón de `uploadMediaData` ya documentado paso a paso).
- Restaurar el rectángulo de fondo en `LOGIN OR SINGUO`.
- Corregir el tamaño de imagen en `Resultado open-set`.

**Baja dificultad (Haiku podría bastar, con supervisión):** construir boards
nuevos siguiendo un patrón ya establecido en el propio `Mockup Final`, con
estructura del original ya documentada o fácil de leer con
`shapeStructure`, sin decisiones de diseño nuevas.
- Los 12 boards faltantes que son principalmente listas/paneles simples
  siguiendo componentes ya construidos (p. ej. `EDIT`, `Fotos`, `Ubicación
  geográfica`, `Explora más.`, `Notas de la salida de campo`) â€” reutilizan
  patrones (tarjeta de observación, filas de ajustes, botones) que ya
  existen como componentes (`COMP · ...`) en `Mockup Final`.
- `ajustes modo oscuro`: copiar `ajustes` y aplicarle la superficie oscura
  del sistema de diseño â€” mismo patrón que `ajustes · modo LUZ ROJA`.

**Recomendación de despliegue:** dado el patrón de conexión inestable, el
tamaño del catálogo de pendientes, y que ya hubo un intento (#3) que generó
buena parte de la base pero con fidelidad floja, conviene un solo pase con
Opus para las piezas de alta dificultad (fondo por pantalla + `home` +
`COMENTARIOS` + `ajustes`) seguido de un pase con Sonnet para el resto de
correcciones puntuales y los boards de baja dificultad â€” en vez de repartir
entre muchos agentes pequeños que compiten por la misma conexión frágil del
plugin.

## 6. Fuente de verdad operativa

El plan con coordenadas exactas, estructura real verificada de cada board, y
el patrón de montaje de fotos (`uploadMediaData`) vive en:

```
C:\Users\user\AppData\Local\Temp\claude\D--Anura\fb73d0e6-145d-4fcf-8f74-89e7807d8ea8\scratchpad\anura-correcciones-v2.md
```

y el sistema de diseño completo (paleta, contraste, materiales, specs de
navbar/loading/Apariencia) en:

```
C:\Users\user\AppData\Local\Temp\claude\D--Anura\fb73d0e6-145d-4fcf-8f74-89e7807d8ea8\scratchpad\anura-design-system.md
```

Ambos son archivos de sesión (no del vault) â€” si se pierden, este documento
tiene el resumen suficiente para reconstruir el plan desde cero comparando
de nuevo `Mockup Final` contra `Page 1`.



