---
title: "Sistema de Estilos HIG â€” Refactor de Paleta y ElevaciÃ³n"
proyecto: Anura
tipo: proceso-desarrollo
estado: aplicado-08-sep-2026
tags: [anura, diseÃ±o, hig, paleta, tokens, penpot, accesibilidad, luz-roja]
---

# Sistema de Estilos HIG â€” Refactor de Paleta y ElevaciÃ³n

[[Anura â€” Ãndice General]] Â· [[ÃNDICE DE DISEÃ‘O â€” Sprint 27 Sep]] Â· [[DiseÃ±o de Interfaz (Penpot)]] Â· [[Componentes de UI â€” EspecificaciÃ³n Detallada]] Â· [[Estado del Mockup Final â€” Pendientes y Agentes]]

> [!abstract] QuÃ© documenta esta nota
> El pase del 08-sep-2026 sobre `Mockup Final` (Penpot, archivo ANURA): se
> reemplazÃ³ por completo la paleta cÃ¡lida marrÃ³n/naranja por una paleta HIG
> neutra con acento verde, se introdujo elevaciÃ³n en el eje Z (no existÃ­a
> ninguna sombra en todo el mockup), se normalizaron radios y escala
> tipogrÃ¡fica, y se construyÃ³ el modo Luz roja como tema completo.
> **La estructura y la distribuciÃ³n de los 62 boards no se tocaron.**
> `Page 1` (wireframe original) sigue intacta.

> [!warning] Punto de restauraciÃ³n
> Antes del pase se guardÃ³ la versiÃ³n **"Pre-refactor HIG Â· palette+shadows
> (Claude)"** en el historial del archivo de Penpot. Todo lo de abajo es
> reversible desde ahÃ­.

---

## 1. DiagnÃ³stico de partida (medido, no opinado)

AuditorÃ­a automÃ¡tica sobre 3 410 shapes de `Mockup Final`:

| Hallazgo | Cifra | Lectura |
|---|---|---|
| Sombras en todo el mockup | **0** | No habÃ­a eje Z. Todo el contenido estaba al mismo plano visual. |
| Degradados | 60 | 40 legÃ­timos (atenuados sobre foto), 20 anÃ³malos: texto con relleno degradado, un board entero con degradado de acento, puntos con degradado de un solo color. |
| Color mÃ¡s usado | `#756661` (229) | Gris cÃ¡lido apagado â€” el "gris muerto". Junto a `#493F3C`, `#978682`, `#BFB4B0`, `#E0D9D7` formaba una rampa parda sin jerarquÃ­a en escala de grises. |
| Fondo base | `#FCFBFA` / `#F0ECEA` | Casi blanco: las tarjetas no se distinguÃ­an del fondo. |
| Acento | `#C03A16` (193) + `#F9B712` (115) | Ã“xido y dorado. |
| Radios distintos | 19 valores (1,3 â†’ 30) | Sin escala. |
| TamaÃ±os de fuente | 10 (365Ã—), 15, 20, 25 | 10 pt estÃ¡ por debajo del mÃ­nimo de iOS (11 pt, Caption 2). |

---

## 2. Paleta resultante

### Neutros

| Rol | Claro | Oscuro | Nota |
|---|---|---|---|
| Fondo de pantalla | `#F2F2F7` | `#000000` | Nunca blanco puro: las tarjetas necesitan contra quÃ© flotar. |
| Tarjeta / contenedor | `#FFFFFF` | `#1C1C1E` | |
| Superficie sutil, campos | `#E5E5EA` | `#2C2C2E` | |
| Separador | `#C6C6C8` | `#48484A` | |
| Texto primario | `#1C1C1E` | `#FFFFFF` | 15,25:1 sobre el fondo base. |
| Texto secundario | `#8E8E93` | `#8E8E93` | Ver Â§5. |
| Marcador de miniatura | `#E5E5EA` | `#2C2C2E` | |
| Marcador de foto de cabecera | `#6E6E73` | `#3A3A3C` | MÃ¡s oscuro a propÃ³sito: encima va texto blanco. |

### Verde rana â€” por quÃ© es una rampa y no un solo tono

`#34C759` es el matiz de marca, pero **como tinta sobre fondo claro mide
2,22:1 sobre blanco**. Un botÃ³n verde con etiqueta blanca a 2,22:1 es
ilegible a pleno sol, que es exactamente la condiciÃ³n de uso de esta app.
El verde se abriÃ³ en cuatro pasos, todos "verde rana", cada uno medido:

| Token | Valor | Uso | Contraste |
|---|---|---|---|
| `green-500` | `#34C759` | Matiz de marca: pista del interruptor encendido, tintes al 12 % | â€” |
| `green-600` | `#2AA84A` | Relleno con glifo blanco (FAB, botones circulares) | 3,09:1 âœ“ objeto grÃ¡fico |
| `green-700` | `#1E7A34` | **Tinta**: texto verde, iconos, CTA con etiqueta blanca | 5,40:1 âœ“ AA |
| `green-dark` | `#30D158` | Modo oscuro | 8,42:1 âœ“ AAA |

Regla: **sobre claro se usa la tinta; sobre oscuro o sobre foto, el vivo.**
En modo oscuro el relleno se invierte: verde claro con etiqueta oscura
(`#062B12`, 7,63:1), nunca blanco sobre `#30D158` (serÃ­a 2,02:1).

### Estado y IUCN

`#D70015` peligro Â· `#FF9500` alerta Â· `#007AFF` info Â· `#AF52DE` violeta Â·
`#30B0C7` turquesa. Se mantiene la regla del mockup original: **la seÃ±al va
en la forma (icono + texto), el color sÃ³lo refuerza.** Los distintivos IUCN
conservan su codificaciÃ³n y los chips neutros pasaron a `#48484A` para que
la etiqueta blanca llegue a 8,6:1.

---

## 3. ElevaciÃ³n (lo que faltaba por completo)

| Nivel | Sombra | Se aplica a |
|---|---|---|
| Tarjeta | `0 1px 2px rgba(0,0,0,.04)`, `0 4px 14px rgba(0,0,0,.06)` | Tarjetas, listas, campos, chips, contenedores de imagen (156 elementos) |
| Flotante | `0 2px 6px rgba(0,0,0,.08)`, `0 8px 24px rgba(0,0,0,.12)` | Navbar, tab bar, FAB, botones circulares (58) |
| Modal | `0 4px 10px rgba(0,0,0,.08)`, `0 16px 40px rgba(0,0,0,.18)` | 16 pop-ups y sheets |

En modo oscuro las sombras suben a 40â€“65 % de opacidad; en Luz roja **no hay
sombras**: sobre negro puro no hay nada que separar y una sombra sÃ³lo
aÃ±adirÃ­a emisiÃ³n.

---

## 4. GeometrÃ­a, tipografÃ­a y materiales

- **Radios:** 12 botÃ³n y miniatura Â· 16 tarjeta Â· 20 modal Â· cÃ¡psula (`h/2`)
  para distintivos y para la pÃ­ldora del tab bar. 597 shapes normalizados,
  16 boards de modal a 20.
- **TipografÃ­a:** escala real de iOS â€” 28 Title 1 Â· 22 Title 2 Â· 20 Title 3 Â·
  17 Body Â· 16 Callout Â· 15 Subhead Â· 13 Footnote Â· 11 Caption 2.
  447 textos ajustados. Cada texto recibiÃ³ el tamaÃ±o HIG **que cabe en su
  caja**, para no alterar la distribuciÃ³n: los 365 textos de 10 pt pasaron a
  11 pt (o 13 pt donde la caja lo permitÃ­a). Ya no queda ningÃºn tamaÃ±o fuera
  de la escala.
- **Materiales:** las barras superior e inferior son translÃºcidas (92 % en el
  mockup, porque Penpot sÃ³lo tiene desenfoque de capa y no de fondo). El
  desenfoque real vive en el cÃ³digo:
  `backdrop-filter: blur(20px) saturate(180%)`, con respaldo opaco bajo
  `prefers-reduced-transparency`.
- **Contenedores de imagen:** miniatura 80Ã—80 r12 Â· foto 4:3 r16 Â·
  cabecera 16:9 Â· todos con `object-fit: cover` y relleno neutro cuando
  estÃ¡n vacÃ­os. Los atenuados sobre foto se normalizaron a negro (antes
  algunos eran grises), lo que devuelve contraste al texto encima.

---

## 5. Decisiones que conviene validar

1. **Pop-ups oscuros â†’ claros.** Los 14 pop-ups y los 2 sheets eran
   superficie oscura de marca (`N-900`, decisiÃ³n del pase del 07-sep). Al
   pedir "tarjetas y contenedores en blanco puro" sobre fondo `#F2F2F7`, se
   convirtieron a sheet claro estÃ¡ndar de iOS: superficie blanca, tÃ­tulo
   `#1C1C1E`, subtÃ­tulo `#8E8E93`, primario verde relleno, secundario
   `#F2F2F7` con etiqueta verde. **Si se prefiere recuperar el modal oscuro
   como recurso de marca, es un cambio de un solo token.**
2. **Texto secundario a `#8E8E93`.** Es el `systemGray` de Apple y es el
   valor pedido, pero mide **3,26:1 sobre blanco y 2,92:1 sobre `#F2F2F7`**:
   no llega a AA. Se aplicÃ³ tal cual a 178 metadatos. El sistema incluye
   `--label-secondary-aa` (`#6C6C70`, 5,23:1) y lo activa automÃ¡ticamente
   bajo `prefers-contrast: more`. **Para una app que se usa a pleno sol vale
   la pena decidir si el secundario deberÃ­a ser el valor AA por defecto** â€”
   es redefinir una variable.
3. **CorazÃ³n de favorito en rojo, no verde.** El acento verde queda reservado
   a CTA, tab bar e interruptores, asÃ­ que el favorito volviÃ³ a la convenciÃ³n
   de iOS (`#FF3B30`).
4. **La barra superior de las pantallas con foto de cabecera** quedÃ³ como
   material claro salvo en las pantallas de captura (`AÃ±adir foto`,
   `AÃ±adir audio`), donde el visor pide cromo oscuro.

---

## 6. Modo Luz roja (visiÃ³n nocturna)

Estaba marcado como trabajo futuro en el [[ÃNDICE DE DISEÃ‘O â€” Sprint 27 Sep|Ã­ndice de diseÃ±o]]; ahora
existe como tema completo.

| Rol | Valor |
|---|---|
| Fondo | `#000000` |
| Superficie / elevada | `#160000` / `#210605` |
| Separador | `#5A170F` |
| Texto primario y acento | `#FF453A` (6,16:1 sobre negro) |
| Texto secundario | `#B3352C` (variante AA `#D9463C`, 4,73:1) |
| Relleno de CTA | `#3A0D0A` con etiqueta `#FF453A` (4,96:1) |
| FAB | `#6B1F19` con glifo y aro `#FF453A` (3,36:1) |

Principio: lo que rompe la adaptaciÃ³n a la oscuridad es **el brillo**, no el
matiz â€” por eso ninguna superficie grande va al 100 % de luminancia. El FAB,
que en claro es un disco verde lleno, aquÃ­ es un disco casi negro con aro
rojo. Fotos, mapas y espectrogramas pasan por un filtro rojo monocromo
(`grayscale â†’ sepia â†’ hue-rotate â†’ brightness .55`) mÃ¡s una capa de
atenuaciÃ³n: cero emisiÃ³n blanca o azul.

Boards: `ajustes Â· modo LUZ ROJA` (ya existÃ­a, corregido) y
**`home Â· modo LUZ ROJA (visiÃ³n nocturna)`** (nuevo, para validar el modo
sobre una pantalla real con foto).

---

## 7. DÃ³nde viven las variables

| Artefacto | Ruta | Para quÃ© |
|---|---|---|
| Colores de biblioteca | Penpot â€º ANURA â€º biblioteca local (28 muestras `Anura / â€¦`) | Trabajar en el lienzo |
| Sets de tokens | `anura-primitivos`, `anura-claro`, `anura-oscuro`, `anura-luz-roja` (73 tokens) | Mismos nombres, tres valores |
| Temas | Penpot â€º Temas â€º grupo **Anura**: Claro Â· Oscuro Â· Luz roja | Cambiar de modo en el lienzo |
| Hoja de estilos | `D:\Anura\design-system\anura-hig.css` | ImplementaciÃ³n: variables + clases `.a-*` |
| Banco de comprobaciÃ³n | `D:\Anura\design-system\index.html` | Ver los tres temas, con medidor de contraste incorporado |

El banco se levanta con la configuraciÃ³n `anura-design-system`
(`python -m http.server 8777 --directory design-system`) y mide en vivo cada
par tinta/fondo contra su umbral. Estado actual: **todo pasa en oscuro y en
luz roja; en claro el Ãºnico que no pasa es el `#8E8E93` del punto 5.2, que es
una decisiÃ³n consciente.**

---

## 8. TraducciÃ³n a Compose (para el sprint del 27)

Los nombres de token estÃ¡n pensados para mapear 1:1 a un `ColorScheme` de
Material 3 con tres esquemas (`claro`, `oscuro`, `luzRoja`):
`bg.base â†’ background`, `bg.elevated â†’ surface`, `label.primary â†’ onSurface`,
`label.secondary â†’ onSurfaceVariant`, `cta.bg â†’ primary`,
`cta.fg â†’ onPrimary`, `separator â†’ outlineVariant`, `danger â†’ error`.
El par `cta.bg`/`cta.fg` es el importante: es lo que evita repetir el error
de blanco sobre verde claro al portar el tema oscuro.



