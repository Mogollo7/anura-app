---
title: "Diseño de Interfaz (Penpot)"
proyecto: Anura
tipo: proceso-desarrollo
estado: mockup-en-construcción
tags: [anura, proceso, diseño, ui, penpot, wireframe]
---

# Diseño de Interfaz (Penpot)

[[Anura â€” àndice General]] · [[Proceso de Desarrollo â€” àndice]] · [[Entorno de Trabajo y MCP]] · [[App Móvil]] · [[Objetivos y Alcance]]

> [!abstract] Para qué existe esta nota
> El [[Cronograma y Plan de Trabajo|cronograma]] §0 fija que **cada pantalla se diseña como mockup y se aprueba antes de escribirse en Kotlin**, para no escribir la UI dos veces. Esta nota es el contrato de ese mockup: el sistema de componentes, el inventario de pantallas, el grafo de navegación y la trazabilidad contra [[Objetivos y Alcance|RF/RNF]]. Quien implemente en Compose debería poder trabajar desde aquí sin abrir Penpot.

> [!note] Estado
> **Mockup especificado completamente (2026-09-07).** Los conteos son del 2026-09-06. El diseño es una tarea **paralelizable** ([[Cronograma y Plan de Trabajo]] §4): no está en la ruta crítica y no compite con H3/H4.
>
> **Documentos de referencia para implementación:**
> - [[Componentes de UI â€” Especificación Detallada]] (Niveles 1â€“5, completo)
> - [[CHEAT SHEET â€” Componentes de UI (Referencia Rápida)]] (Imprimible, para desarrolladores)

## 1. Convenciones de wireframe

El mockup es de **baja fidelidad deliberada**: rectángulos grises en lugar de texto e imágenes reales. Dos reglas hacen que eso siga siendo especificación y no un boceto vago:

- **El nombre de capa ES la especificación.** Penpot muestra el nombre en el panel de capas, así que un rectángulo llamado `Botón para cerrar sesión.` ya dice qué es y qué texto lleva. No se añaden elementos de texto que repitan el nombre.
- **Un botón es un solo rectángulo.** No lleva un recuadro de texto dentro: su nombre indica la etiqueta. Un botón compuesto (rectángulo + texto interno) es un error de patrón, no una variante.

Los rectángulos grises se dimensionan segàºn la escala tipográfica: un texto de título se representa con un rectángulo de 25 de alto, uno normal con 20, y así. El alto del rectángulo *es* el tamaño de fuente previsto.

## 2. Sistema de componentes

### Paleta

| Token | Hex | Uso |
| --- | --- | --- |
| Medio | `#626264` | Barra superior, botones sobre fondo claro, texto sobre superficies claras |
| Claro | `#B1B2B5` | Superficies, botones sobre fondo oscuro, texto sobre fondo oscuro |
| Oscuro | `#373738` | Fondo de pop-ups, estado activo, modo oscuro |
| Imagen | `#eeeeee` | Marcador de posición de fotografía dentro de tarjetas |

Regla que se rompió una vez y no debe repetirse: **cada rectángulo tiene que resaltar contra el fondo sobre el que se apoya**. Un botón `#373738` sobre un pop-up `#373738` desaparece. Sobre el pop-up oscuro los botones van en `#626264`.

Los fondos varían segàºn la pantalla: degradado lineal de `#626264` (opacidad 1) a transparente de arriba abajo para las pantallas de navegación y de flujo; oscuro sólido para las de captura de foto y audio; `#373738` para pop-ups.

### Medidas fijas

| Propiedad | Valor |
| --- | --- |
| Radio de borde | **30** en todo |
| Alto de botón | **60** |
| Tamaño de pantalla | 393 à— 852 |
| Escala de texto | 25 (título) · 20 (normal) · 15 (descriptivo) · 10 (mínimo) |

### Componentes recurrentes

```
Barra superior      393à—77 · flecha 40à—40 en (19,19) · título 200à—25 en (97,26)
Barra buscadora     355à—35 en x=19
Navbar              píldora 350à—75 en (22,750)
                    4 iconos de 48 (58 el activo, elevado a y=735)
                    centros en x = 59 · 120 · [FAB] · 274 · 335
                    FAB central 80à—80 en (157,712) con signo de más
Tarjeta observación 167à—196 · rejilla de 2 columnas en x=19/203, filas cada 206
Pop-up              390 de ancho · contenedor a sangre completa
                    radio superior 30, radio inferior 0
                    título 286à—39 en (52,33) · descripción 216à—25 en (52,89)
                    botones 318à—60 en x=36, separados 20
```

La **tarjeta de observación** es el componente más reutilizado y viene del diseño original de `favoritos`. Se replicó sin cambios en los listados de fotos, explorar, especies del género y el listado completo:

```
Contenedor de imagen        167à—196   #eeeeee
Etiqueta de peligro          30à—30    (+20, +13)   â†’ abre iucnredlist.org/es
Icono de corazón             30à—30    (+121, +12)
Contenedor cristal/blur     145à—49    (+11, +139)
Nombre comàºn                107à—15    (+25, +149)
Nombre científico            97à—10    (+25, +166)
```

> [!tip] Por qué importa reutilizar
> Cada distribución que se repite es una pantalla menos que diseñar, un componente Compose menos que escribir y una inconsistencia menos que corregir. Antes de inventar una disposición nueva, buscar si ya existe una equivalente en el archivo.

## 3. Inventario de pantallas

Snapshot del 2026-09-06: **â‰ˆ42 boards** en la raíz.

### Diseñadas originalmente por el autor

`PANTALLA DE CARGA INICIO` · `LOGIN OR SINGUO` · `INICIAR SECCION` · `crear cuenta` · `home` · `profile` · `Seguidos, seguidores y favoritos.` · `favoritos` · `pop de ordenar por` · `Pop-up de eliminar de favoritos` · `Detalles de observación` · `Desplegable de detalles para análisis semántico` · `DESPLEGABLE1` · `COMENTARIOS` · `ESPECIE, FAMILIA, GENERO`

### Añadidas durante el sprint

| Grupo | Pantallas |
| --- | --- |
| Perfil y ajustes | `EDIT` · `ajustes` · `ajustes modo oscuro` · `Zonas descargadas` |
| Captura | `Añadir foto` · `Añadir audio` |
| Identificación paso a paso | `Paso 1: dónde la viste` · `Paso 2: cuándo la viste` · `Paso 3: qué tamaño tenía` · `Paso 4: adjuntar foto y audio` · `Paso 5: resumen y analizar` |
| Exploración | `explorar` · `Especies del género o familia` · `Identificadores destacados` · `Fotos y observaciones` |
| Paneles de la ficha | `Ubicación geográfica` · `Fotos` · `Explora más.` |
| Salidas de campo | `Salida de campo en curso` · `Sonidos nocturnos de la salida` · `Notas de la salida de campo` |
| Pop-ups | descargar zona · eliminar zona · cambiar fecha · foto (tomar o cargar) · audio (grabar o cargar) · botón "+" |

## 4. Navegación

### Navbar de cuatro pestañas más botón central

```
  [ home ]  [ explorar ]   ( + )   [ listado ]  [ ajustes ]
                             â”‚
                             â–¼
              Pop-up: ¿qué querés registrar?
                â”œâ”€â”€ Iniciar salida de campo
                â”œâ”€â”€ Tomar muestra rápida
                â””â”€â”€ Grabar sonido
```

El navbar está cableado de forma cruzada en las seis pantallas que lo llevan, de modo que cualquier pestaña alcanza a cualquier otra. El botón central `+` es el punto de entrada a las salidas de campo (HU-04).

### Identificación paso a paso

```
home â”€â”€â”¬â”€â”€ botón izquierdo â”€â”€â–¶ Paso 1 â”€â–¶ 2 â”€â–¶ 3 â”€â–¶ 4 â”€â–¶ 5 â”€â”€â–¶ Detalles de observación
       â”œâ”€â”€ botón central  â”€â”€â–¶ pop-up foto  â”€â”€â–¶ Añadir foto  â”€â”€â–¶ analizar â”€â”€â–¶ ídem
       â””â”€â”€ botón derecho  â”€â”€â–¶ pop-up audio â”€â”€â–¶ Añadir audio â”€â”€â–¶ analizar â”€â”€â–¶ ídem
```

Dos atajos cierran el bucle sin callejones sin salida: en el paso 4, "adjuntar foto" y "grabar audio" reutilizan las pantallas de captura completas; y en el paso 5, **cada dato del resumen tiene un botón de editar que devuelve al paso que lo capturó**.

### Pestañas de la ficha de especie

Las secciones de `ESPECIE, FAMILIA, GENERO` **no navegan a otra pantalla**: se superponen en el mismo lugar donde vive el bloque de información, dejando fija la cabecera, el carrusel, el árbol taxonómico y las estadísticas. Cada pestaña cierra las hermanas y abre la suya (`close-overlay` à— n + `open-overlay` en posición manual sobre el hueco de contenido, con fundido).

### Tipos de interacción usados

| Acción | Cuándo |
| --- | --- |
| 
avigate-to` | Cambio de pantalla completo |
| `open-overlay` | Pop-ups (desde abajo, con fondo atenuado y cierre al tocar fuera) y paneles de sección |
| `close-overlay` | Botones internos del pop-up y conmutación entre paneles |
| `previous-screen` | Todas las flechas de volver |
| `open-url` | Etiqueta de peligro de extinción â†’ `iucnredlist.org/es` |

## 5. Variantes propio vs. ajeno

Decisión de diseño: **toda pantalla que muestre contenido de una persona necesita dos variantes**, porque las acciones disponibles cambian por completo. No es un detalle cosmético: define permisos, y omitirlo produce interfaces que ofrecen acciones imposibles.

| Elemento | Variante propia | Variante ajena |
| --- | --- | --- |
| Perfil | Lápiz de editar, ve publicaciones privadas, acceso a ajustes | Botón de seguir, sin privadas, reportar o bloquear |
| Observación | Editar, eliminar, cambiar visibilidad, añadir anotaciones | Comentar, favorito, sugerir identificación, reportar |
| Comentario | Editar y borrar | Responder y reportar |
| Salida de campo | Añadir registros, cerrar, exportar | Solo ver el resumen |
| Identificación sugerida | Retirarla | Apoyarla o refutarla |
| Publicación | Pàºblica o privada, con su distintivo | Solo visibles las pàºblicas |
| Lista de favoritos | Quitar de favoritos | Puede estar oculta |

## 6. Trazabilidad contra requisitos

Estado del mockup frente a [[Objetivos y Alcance]] y [[Historias de Usuario]], al 2026-09-06.

| Req | Estado | Dónde / qué falta |
| --- | --- | --- |
| RF-01 captura imagen y audio | âœ… | `Añadir foto` · `Añadir audio` con pop-up previo de tomar/cargar y grabar/cargar |
| RF-02 multi-foto | ðŸŸ¡ | Hay miniaturas; falta etiquetar vista dorsal/ventral/lateral |
| RF-03 multi-individuo | ðŸ”´ | Sin pantalla de selección de individuo |
| RF-04 metadatos | ðŸŸ¡ | GPS y fecha/hora sí; faltan altitud y ecosistema/microhábitat |
| RF-05 Top-3 | âœ… | `DESPLEGABLE1` |
| RF-06 segmentación paso a paso | âœ… | `DESPLEGABLE1` con % por región anatómica |
| RF-07 bioacàºstica | ðŸŸ¡ | `Sonidos nocturnos` identifica cantos; falta espectrograma y frecuencia dominante |
| RF-08 fusión visión+audio+metadatos | ðŸŸ¡ | Implícita en el paso 5; sin vista que muestre la fusión |
| RF-09 repositorio de observaciones | ðŸŸ¡ | Se ve y se lista; falta editar y publicar |
| RF-10 ficha técnica completa | ðŸŸ¡ | Faltan pestañas de Morfología, Bioacàºstica, Ecología y Conservación |
| RF-11 exploración y mapa comunitario | ðŸŸ¡ | Listado y buscador sí; falta mapa con filtros |
| RF-12 modo offline | âœ… | `Zonas descargadas` (paquetes regionales) |
| RF-13 sincronización diferida | ðŸ”´ | Sin estados `LOCAL â†’ EN COLA â†’ SINCRONIZADA â†’ VALIDADA` |
| RF-14 captura bioacàºstica | âœ… | Control central de grabación con reintentar y confirmar |
| RNF-06 tolerancia a datos faltantes | ðŸ”´ | El paso a paso obliga a completar todo; falta "omitir" |
| RNF-07 modo oscuro | âœ… | `ajustes` â‡„ `ajustes modo oscuro`; falta el modo luz roja de [[App Móvil]] §4 |
| RNF-08 una sola mano | âœ… | Captura, grabación y guardar en el tercio inferior |
| RNF-13 ofuscación de amenazadas | ðŸ”´ | El mapa muestra punto exacto; falta el buffer de 1â€“5 km |
| RNF-14 permisos en el momento de uso | ðŸ”´ | Sin pop-ups de cámara, micrófono y ubicación |
| HU-03 refutación experta | ðŸ”´ | Prioridad **Alta** en el documento; sin diseñar |
| HU-04 salidas de campo | ðŸŸ¡ | Sesión, sonidos y notas hechos; falta resumen de cierre |
| HU-05 exportación Darwin Core | ðŸ”´ | Fuera del sprint segàºn [[Cronograma y Plan de Trabajo]] |

> [!warning] Alcance del sprint vs. alcance del mockup
> El cronograma deja **explícitamente fuera del 27 de septiembre** el piloto de campo, Darwin Core (HU-05) y el módulo comunitario a escala; multi-individuo (RF-03) es un Go/No-Go del 20 de septiembre. El mockup los cubre igual porque diseñar no consume ruta crítica, pero **implementarlos sí**. Lo que debe entrar a Kotlin para el prototipo es: captura â†’ paso a paso â†’ resultado â†’ ficha â†’ listado â†’ ajustes.

## 7. Qué falta por hacer o decidir

### 7.1 DECIDIDAS (2026-09-07)

#### Modo luz roja
- [x] **Decisión:** Queda como **trabajo futuro**, no entra al prototipo del 27 sep
- **Razón:** RNF-07 (modo oscuro) ya está completo; luz roja es un refinamiento avanzado para trabajo de campo nocturno, pero no es crítico para el MVP
- **Documentación:** Quedará mencionado en [[App Móvil]] §4 como mejora post-sprint

#### Campos ambientales (RF-04)
- [x] **Nuevos campos en Paso 2 (metadatos):**
  - `Altitud (msnm)` â€” campo numérico opcional, rango 0â€“5000
  - `Ecosistema/Microhábitat` â€” selector de opciones: *Bosque*, *Agua*, *Zona abierta*, *àrea urbana*, *Otro*
  - Ambos van en el mismo formulario de Paso 2 (dónde/cuándo/cuál tamaño) bajo los existentes
  - Label gris de 15pt, campo de 60pt alto igual a los otros
- **Ubicación en UI:** Paso 2 ("Cuándo la viste") â†’ expandir sección con estos dos campos

#### Botón "omitir" en pasos 1, 2, 4
- [x] **Patrón para RNF-06 (datos faltantes):**
  - Botón "Omitir este paso" (60pt alto, `#626264` sobre gradiente, mismo estilo que otros botones)
  - Ubicación: esquina inferior derecha de cada paso, junto al botón "Continuar"
  - Pasos afectados:
    - Paso 1: "Omitir ubicación"
    - Paso 2: "Omitir detalles" (cubre ecosistema/altitud si no se conocen)
    - Paso 4: "Omitir foto" (si el usuario solo quiere capturar audio o metadatos)
  - Estado guardado: se marca internamente como 
ull`, no como `""` (string vacío)

### 7.2 POR HACER (Hoy, niveles 2â€“5)

- [ ] **NIVEL 2:** Pop-ups de permisos de cámara, micrófono y ubicación, con su caso denegado (RNF-14)
- [ ] **NIVEL 2:** Pop-up de foto borrosa (HU-01 caso 2) y estado "analizando" con progreso por etapas
- [ ] **NIVEL 3:** Variantes ajenas de perfil, observación y comentario (§5)
- [ ] **NIVEL 3:** Estados de sincronización como distintivo en el listado (RF-13)
- [ ] **NIVEL 4:** Resultado open-set: especie no registrada, a nivel de género o familia (objetivo específico + HU-02 caso 3)
- [ ] **NIVEL 5:** Cuatro pestañas técnicas de la ficha para cerrar RF-10, con barra de secciones desplazable
- [ ] **NIVEL 5:** Sección "Mis publicaciones" con pestañas pàºblica y privada, y pop-up de visibilidad al guardar
- [ ] **NIVEL 5:** Resumen de salida de campo cerrada y pop-up de confirmación



