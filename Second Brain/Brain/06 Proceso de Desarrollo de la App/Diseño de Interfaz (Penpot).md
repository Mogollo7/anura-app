---
title: "DiseÃ±o de Interfaz (Penpot)"
proyecto: Anura
tipo: proceso-desarrollo
estado: mockup-en-construcciÃ³n
tags: [anura, proceso, diseÃ±o, ui, penpot, wireframe]
---

# DiseÃ±o de Interfaz (Penpot)

[[Anura â€” Ãndice General]] Â· [[Proceso de Desarrollo â€” Ãndice]] Â· [[Entorno de Trabajo y MCP]] Â· [[App MÃ³vil]] Â· [[Objetivos y Alcance]]

> [!abstract] Para quÃ© existe esta nota
> El [[Cronograma y Plan de Trabajo|cronograma]] Â§0 fija que **cada pantalla se diseÃ±a como mockup y se aprueba antes de escribirse en Kotlin**, para no escribir la UI dos veces. Esta nota es el contrato de ese mockup: el sistema de componentes, el inventario de pantallas, el grafo de navegaciÃ³n y la trazabilidad contra [[Objetivos y Alcance|RF/RNF]]. Quien implemente en Compose deberÃ­a poder trabajar desde aquÃ­ sin abrir Penpot.

> [!note] Estado
> **Mockup especificado completamente (2026-09-07).** Los conteos son del 2026-09-06. El diseÃ±o es una tarea **paralelizable** ([[Cronograma y Plan de Trabajo]] Â§4): no estÃ¡ en la ruta crÃ­tica y no compite con H3/H4.
>
> **Documentos de referencia para implementaciÃ³n:**
> - [[Componentes de UI â€” EspecificaciÃ³n Detallada]] (Niveles 1â€“5, completo)
> - [[CHEAT SHEET â€” Componentes de UI (Referencia RÃ¡pida)]] (Imprimible, para desarrolladores)

## 1. Convenciones de wireframe

El mockup es de **baja fidelidad deliberada**: rectÃ¡ngulos grises en lugar de texto e imÃ¡genes reales. Dos reglas hacen que eso siga siendo especificaciÃ³n y no un boceto vago:

- **El nombre de capa ES la especificaciÃ³n.** Penpot muestra el nombre en el panel de capas, asÃ­ que un rectÃ¡ngulo llamado `BotÃ³n para cerrar sesiÃ³n.` ya dice quÃ© es y quÃ© texto lleva. No se aÃ±aden elementos de texto que repitan el nombre.
- **Un botÃ³n es un solo rectÃ¡ngulo.** No lleva un recuadro de texto dentro: su nombre indica la etiqueta. Un botÃ³n compuesto (rectÃ¡ngulo + texto interno) es un error de patrÃ³n, no una variante.

Los rectÃ¡ngulos grises se dimensionan segÃºn la escala tipogrÃ¡fica: un texto de tÃ­tulo se representa con un rectÃ¡ngulo de 25 de alto, uno normal con 20, y asÃ­. El alto del rectÃ¡ngulo *es* el tamaÃ±o de fuente previsto.

## 2. Sistema de componentes

### Paleta

| Token | Hex | Uso |
| --- | --- | --- |
| Medio | `#626264` | Barra superior, botones sobre fondo claro, texto sobre superficies claras |
| Claro | `#B1B2B5` | Superficies, botones sobre fondo oscuro, texto sobre fondo oscuro |
| Oscuro | `#373738` | Fondo de pop-ups, estado activo, modo oscuro |
| Imagen | `#eeeeee` | Marcador de posiciÃ³n de fotografÃ­a dentro de tarjetas |

Regla que se rompiÃ³ una vez y no debe repetirse: **cada rectÃ¡ngulo tiene que resaltar contra el fondo sobre el que se apoya**. Un botÃ³n `#373738` sobre un pop-up `#373738` desaparece. Sobre el pop-up oscuro los botones van en `#626264`.

Los fondos varÃ­an segÃºn la pantalla: degradado lineal de `#626264` (opacidad 1) a transparente de arriba abajo para las pantallas de navegaciÃ³n y de flujo; oscuro sÃ³lido para las de captura de foto y audio; `#373738` para pop-ups.

### Medidas fijas

| Propiedad | Valor |
| --- | --- |
| Radio de borde | **30** en todo |
| Alto de botÃ³n | **60** |
| TamaÃ±o de pantalla | 393 Ã— 852 |
| Escala de texto | 25 (tÃ­tulo) Â· 20 (normal) Â· 15 (descriptivo) Â· 10 (mÃ­nimo) |

### Componentes recurrentes

```
Barra superior      393Ã—77 Â· flecha 40Ã—40 en (19,19) Â· tÃ­tulo 200Ã—25 en (97,26)
Barra buscadora     355Ã—35 en x=19
Navbar              pÃ­ldora 350Ã—75 en (22,750)
                    4 iconos de 48 (58 el activo, elevado a y=735)
                    centros en x = 59 Â· 120 Â· [FAB] Â· 274 Â· 335
                    FAB central 80Ã—80 en (157,712) con signo de mÃ¡s
Tarjeta observaciÃ³n 167Ã—196 Â· rejilla de 2 columnas en x=19/203, filas cada 206
Pop-up              390 de ancho Â· contenedor a sangre completa
                    radio superior 30, radio inferior 0
                    tÃ­tulo 286Ã—39 en (52,33) Â· descripciÃ³n 216Ã—25 en (52,89)
                    botones 318Ã—60 en x=36, separados 20
```

La **tarjeta de observaciÃ³n** es el componente mÃ¡s reutilizado y viene del diseÃ±o original de `favoritos`. Se replicÃ³ sin cambios en los listados de fotos, explorar, especies del gÃ©nero y el listado completo:

```
Contenedor de imagen        167Ã—196   #eeeeee
Etiqueta de peligro          30Ã—30    (+20, +13)   â†’ abre iucnredlist.org/es
Icono de corazÃ³n             30Ã—30    (+121, +12)
Contenedor cristal/blur     145Ã—49    (+11, +139)
Nombre comÃºn                107Ã—15    (+25, +149)
Nombre cientÃ­fico            97Ã—10    (+25, +166)
```

> [!tip] Por quÃ© importa reutilizar
> Cada distribuciÃ³n que se repite es una pantalla menos que diseÃ±ar, un componente Compose menos que escribir y una inconsistencia menos que corregir. Antes de inventar una disposiciÃ³n nueva, buscar si ya existe una equivalente en el archivo.

## 3. Inventario de pantallas

Snapshot del 2026-09-06: **â‰ˆ42 boards** en la raÃ­z.

### DiseÃ±adas originalmente por el autor

`PANTALLA DE CARGA INICIO` Â· `LOGIN OR SINGUO` Â· `INICIAR SECCION` Â· `crear cuenta` Â· `home` Â· `profile` Â· `Seguidos, seguidores y favoritos.` Â· `favoritos` Â· `pop de ordenar por` Â· `Pop-up de eliminar de favoritos` Â· `Detalles de observaciÃ³n` Â· `Desplegable de detalles para anÃ¡lisis semÃ¡ntico` Â· `DESPLEGABLE1` Â· `COMENTARIOS` Â· `ESPECIE, FAMILIA, GENERO`

### AÃ±adidas durante el sprint

| Grupo | Pantallas |
| --- | --- |
| Perfil y ajustes | `EDIT` Â· `ajustes` Â· `ajustes modo oscuro` Â· `Zonas descargadas` |
| Captura | `AÃ±adir foto` Â· `AÃ±adir audio` |
| IdentificaciÃ³n paso a paso | `Paso 1: dÃ³nde la viste` Â· `Paso 2: cuÃ¡ndo la viste` Â· `Paso 3: quÃ© tamaÃ±o tenÃ­a` Â· `Paso 4: adjuntar foto y audio` Â· `Paso 5: resumen y analizar` |
| ExploraciÃ³n | `explorar` Â· `Especies del gÃ©nero o familia` Â· `Identificadores destacados` Â· `Fotos y observaciones` |
| Paneles de la ficha | `UbicaciÃ³n geogrÃ¡fica` Â· `Fotos` Â· `Explora mÃ¡s.` |
| Salidas de campo | `Salida de campo en curso` Â· `Sonidos nocturnos de la salida` Â· `Notas de la salida de campo` |
| Pop-ups | descargar zona Â· eliminar zona Â· cambiar fecha Â· foto (tomar o cargar) Â· audio (grabar o cargar) Â· botÃ³n "+" |

## 4. NavegaciÃ³n

### Navbar de cuatro pestaÃ±as mÃ¡s botÃ³n central

```
  [ home ]  [ explorar ]   ( + )   [ listado ]  [ ajustes ]
                             â”‚
                             â–¼
              Pop-up: Â¿quÃ© querÃ©s registrar?
                â”œâ”€â”€ Iniciar salida de campo
                â”œâ”€â”€ Tomar muestra rÃ¡pida
                â””â”€â”€ Grabar sonido
```

El navbar estÃ¡ cableado de forma cruzada en las seis pantallas que lo llevan, de modo que cualquier pestaÃ±a alcanza a cualquier otra. El botÃ³n central `+` es el punto de entrada a las salidas de campo (HU-04).

### IdentificaciÃ³n paso a paso

```
home â”€â”€â”¬â”€â”€ botÃ³n izquierdo â”€â”€â–¶ Paso 1 â”€â–¶ 2 â”€â–¶ 3 â”€â–¶ 4 â”€â–¶ 5 â”€â”€â–¶ Detalles de observaciÃ³n
       â”œâ”€â”€ botÃ³n central  â”€â”€â–¶ pop-up foto  â”€â”€â–¶ AÃ±adir foto  â”€â”€â–¶ analizar â”€â”€â–¶ Ã­dem
       â””â”€â”€ botÃ³n derecho  â”€â”€â–¶ pop-up audio â”€â”€â–¶ AÃ±adir audio â”€â”€â–¶ analizar â”€â”€â–¶ Ã­dem
```

Dos atajos cierran el bucle sin callejones sin salida: en el paso 4, "adjuntar foto" y "grabar audio" reutilizan las pantallas de captura completas; y en el paso 5, **cada dato del resumen tiene un botÃ³n de editar que devuelve al paso que lo capturÃ³**.

### PestaÃ±as de la ficha de especie

Las secciones de `ESPECIE, FAMILIA, GENERO` **no navegan a otra pantalla**: se superponen en el mismo lugar donde vive el bloque de informaciÃ³n, dejando fija la cabecera, el carrusel, el Ã¡rbol taxonÃ³mico y las estadÃ­sticas. Cada pestaÃ±a cierra las hermanas y abre la suya (`close-overlay` Ã— n + `open-overlay` en posiciÃ³n manual sobre el hueco de contenido, con fundido).

### Tipos de interacciÃ³n usados

| AcciÃ³n | CuÃ¡ndo |
| --- | --- |
| 
avigate-to` | Cambio de pantalla completo |
| `open-overlay` | Pop-ups (desde abajo, con fondo atenuado y cierre al tocar fuera) y paneles de secciÃ³n |
| `close-overlay` | Botones internos del pop-up y conmutaciÃ³n entre paneles |
| `previous-screen` | Todas las flechas de volver |
| `open-url` | Etiqueta de peligro de extinciÃ³n â†’ `iucnredlist.org/es` |

## 5. Variantes propio vs. ajeno

DecisiÃ³n de diseÃ±o: **toda pantalla que muestre contenido de una persona necesita dos variantes**, porque las acciones disponibles cambian por completo. No es un detalle cosmÃ©tico: define permisos, y omitirlo produce interfaces que ofrecen acciones imposibles.

| Elemento | Variante propia | Variante ajena |
| --- | --- | --- |
| Perfil | LÃ¡piz de editar, ve publicaciones privadas, acceso a ajustes | BotÃ³n de seguir, sin privadas, reportar o bloquear |
| ObservaciÃ³n | Editar, eliminar, cambiar visibilidad, aÃ±adir anotaciones | Comentar, favorito, sugerir identificaciÃ³n, reportar |
| Comentario | Editar y borrar | Responder y reportar |
| Salida de campo | AÃ±adir registros, cerrar, exportar | Solo ver el resumen |
| IdentificaciÃ³n sugerida | Retirarla | Apoyarla o refutarla |
| PublicaciÃ³n | PÃºblica o privada, con su distintivo | Solo visibles las pÃºblicas |
| Lista de favoritos | Quitar de favoritos | Puede estar oculta |

## 6. Trazabilidad contra requisitos

Estado del mockup frente a [[Objetivos y Alcance]] y [[Historias de Usuario]], al 2026-09-06.

| Req | Estado | DÃ³nde / quÃ© falta |
| --- | --- | --- |
| RF-01 captura imagen y audio | âœ… | `AÃ±adir foto` Â· `AÃ±adir audio` con pop-up previo de tomar/cargar y grabar/cargar |
| RF-02 multi-foto | ðŸŸ¡ | Hay miniaturas; falta etiquetar vista dorsal/ventral/lateral |
| RF-03 multi-individuo | ðŸ”´ | Sin pantalla de selecciÃ³n de individuo |
| RF-04 metadatos | ðŸŸ¡ | GPS y fecha/hora sÃ­; faltan altitud y ecosistema/microhÃ¡bitat |
| RF-05 Top-3 | âœ… | `DESPLEGABLE1` |
| RF-06 segmentaciÃ³n paso a paso | âœ… | `DESPLEGABLE1` con % por regiÃ³n anatÃ³mica |
| RF-07 bioacÃºstica | ðŸŸ¡ | `Sonidos nocturnos` identifica cantos; falta espectrograma y frecuencia dominante |
| RF-08 fusiÃ³n visiÃ³n+audio+metadatos | ðŸŸ¡ | ImplÃ­cita en el paso 5; sin vista que muestre la fusiÃ³n |
| RF-09 repositorio de observaciones | ðŸŸ¡ | Se ve y se lista; falta editar y publicar |
| RF-10 ficha tÃ©cnica completa | ðŸŸ¡ | Faltan pestaÃ±as de MorfologÃ­a, BioacÃºstica, EcologÃ­a y ConservaciÃ³n |
| RF-11 exploraciÃ³n y mapa comunitario | ðŸŸ¡ | Listado y buscador sÃ­; falta mapa con filtros |
| RF-12 modo offline | âœ… | `Zonas descargadas` (paquetes regionales) |
| RF-13 sincronizaciÃ³n diferida | ðŸ”´ | Sin estados `LOCAL â†’ EN COLA â†’ SINCRONIZADA â†’ VALIDADA` |
| RF-14 captura bioacÃºstica | âœ… | Control central de grabaciÃ³n con reintentar y confirmar |
| RNF-06 tolerancia a datos faltantes | ðŸ”´ | El paso a paso obliga a completar todo; falta "omitir" |
| RNF-07 modo oscuro | âœ… | `ajustes` â‡„ `ajustes modo oscuro`; falta el modo luz roja de [[App MÃ³vil]] Â§4 |
| RNF-08 una sola mano | âœ… | Captura, grabaciÃ³n y guardar en el tercio inferior |
| RNF-13 ofuscaciÃ³n de amenazadas | ðŸ”´ | El mapa muestra punto exacto; falta el buffer de 1â€“5 km |
| RNF-14 permisos en el momento de uso | ðŸ”´ | Sin pop-ups de cÃ¡mara, micrÃ³fono y ubicaciÃ³n |
| HU-03 refutaciÃ³n experta | ðŸ”´ | Prioridad **Alta** en el documento; sin diseÃ±ar |
| HU-04 salidas de campo | ðŸŸ¡ | SesiÃ³n, sonidos y notas hechos; falta resumen de cierre |
| HU-05 exportaciÃ³n Darwin Core | ðŸ”´ | Fuera del sprint segÃºn [[Cronograma y Plan de Trabajo]] |

> [!warning] Alcance del sprint vs. alcance del mockup
> El cronograma deja **explÃ­citamente fuera del 27 de septiembre** el piloto de campo, Darwin Core (HU-05) y el mÃ³dulo comunitario a escala; multi-individuo (RF-03) es un Go/No-Go del 20 de septiembre. El mockup los cubre igual porque diseÃ±ar no consume ruta crÃ­tica, pero **implementarlos sÃ­**. Lo que debe entrar a Kotlin para el prototipo es: captura â†’ paso a paso â†’ resultado â†’ ficha â†’ listado â†’ ajustes.

## 7. QuÃ© falta por hacer o decidir

### 7.1 DECIDIDAS (2026-09-07)

#### Modo luz roja
- [x] **DecisiÃ³n:** Queda como **trabajo futuro**, no entra al prototipo del 27 sep
- **RazÃ³n:** RNF-07 (modo oscuro) ya estÃ¡ completo; luz roja es un refinamiento avanzado para trabajo de campo nocturno, pero no es crÃ­tico para el MVP
- **DocumentaciÃ³n:** QuedarÃ¡ mencionado en [[App MÃ³vil]] Â§4 como mejora post-sprint

#### Campos ambientales (RF-04)
- [x] **Nuevos campos en Paso 2 (metadatos):**
  - `Altitud (msnm)` â€” campo numÃ©rico opcional, rango 0â€“5000
  - `Ecosistema/MicrohÃ¡bitat` â€” selector de opciones: *Bosque*, *Agua*, *Zona abierta*, *Ãrea urbana*, *Otro*
  - Ambos van en el mismo formulario de Paso 2 (dÃ³nde/cuÃ¡ndo/cuÃ¡l tamaÃ±o) bajo los existentes
  - Label gris de 15pt, campo de 60pt alto igual a los otros
- **UbicaciÃ³n en UI:** Paso 2 ("CuÃ¡ndo la viste") â†’ expandir secciÃ³n con estos dos campos

#### BotÃ³n "omitir" en pasos 1, 2, 4
- [x] **PatrÃ³n para RNF-06 (datos faltantes):**
  - BotÃ³n "Omitir este paso" (60pt alto, `#626264` sobre gradiente, mismo estilo que otros botones)
  - UbicaciÃ³n: esquina inferior derecha de cada paso, junto al botÃ³n "Continuar"
  - Pasos afectados:
    - Paso 1: "Omitir ubicaciÃ³n"
    - Paso 2: "Omitir detalles" (cubre ecosistema/altitud si no se conocen)
    - Paso 4: "Omitir foto" (si el usuario solo quiere capturar audio o metadatos)
  - Estado guardado: se marca internamente como 
ull`, no como `""` (string vacÃ­o)

### 7.2 POR HACER (Hoy, niveles 2â€“5)

- [ ] **NIVEL 2:** Pop-ups de permisos de cÃ¡mara, micrÃ³fono y ubicaciÃ³n, con su caso denegado (RNF-14)
- [ ] **NIVEL 2:** Pop-up de foto borrosa (HU-01 caso 2) y estado "analizando" con progreso por etapas
- [ ] **NIVEL 3:** Variantes ajenas de perfil, observaciÃ³n y comentario (Â§5)
- [ ] **NIVEL 3:** Estados de sincronizaciÃ³n como distintivo en el listado (RF-13)
- [ ] **NIVEL 4:** Resultado open-set: especie no registrada, a nivel de gÃ©nero o familia (objetivo especÃ­fico + HU-02 caso 3)
- [ ] **NIVEL 5:** Cuatro pestaÃ±as tÃ©cnicas de la ficha para cerrar RF-10, con barra de secciones desplazable
- [ ] **NIVEL 5:** SecciÃ³n "Mis publicaciones" con pestaÃ±as pÃºblica y privada, y pop-up de visibilidad al guardar
- [ ] **NIVEL 5:** Resumen de salida de campo cerrada y pop-up de confirmaciÃ³n



