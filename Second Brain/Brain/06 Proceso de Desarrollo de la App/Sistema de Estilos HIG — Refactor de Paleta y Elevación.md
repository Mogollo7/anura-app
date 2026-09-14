---
title: "Sistema de Estilos HIG â€” Refactor de Paleta y Elevación"
proyecto: Anura
tipo: proceso-desarrollo
estado: aplicado-08-sep-2026
tags: [anura, diseño, hig, paleta, tokens, penpot, accesibilidad, luz-roja]
---

# Sistema de Estilos HIG â€” Refactor de Paleta y Elevación

[[Anura â€” àndice General]] · [[àNDICE DE DISEà‘O â€” Sprint 27 Sep]] · [[Diseño de Interfaz (Penpot)]] · [[Componentes de UI â€” Especificación Detallada]] · [[Estado del Mockup Final â€” Pendientes y Agentes]]

> [!abstract] Qué documenta esta nota
> El pase del 08-sep-2026 sobre `Mockup Final` (Penpot, archivo ANURA): se
> reemplazó por completo la paleta cálida marrón/naranja por una paleta HIG
> neutra con acento verde, se introdujo elevación en el eje Z (no existía
> ninguna sombra en todo el mockup), se normalizaron radios y escala
> tipográfica, y se construyó el modo Luz roja como tema completo.
> **La estructura y la distribución de los 62 boards no se tocaron.**
> `Page 1` (wireframe original) sigue intacta.

> [!warning] Punto de restauración
> Antes del pase se guardó la versión **"Pre-refactor HIG · palette+shadows
> (Claude)"** en el historial del archivo de Penpot. Todo lo de abajo es
> reversible desde ahí.

---

## 1. Diagnóstico de partida (medido, no opinado)

Auditoría automática sobre 3 410 shapes de `Mockup Final`:

| Hallazgo | Cifra | Lectura |
|---|---|---|
| Sombras en todo el mockup | **0** | No había eje Z. Todo el contenido estaba al mismo plano visual. |
| Degradados | 60 | 40 legítimos (atenuados sobre foto), 20 anómalos: texto con relleno degradado, un board entero con degradado de acento, puntos con degradado de un solo color. |
| Color más usado | `#756661` (229) | Gris cálido apagado â€” el "gris muerto". Junto a `#493F3C`, `#978682`, `#BFB4B0`, `#E0D9D7` formaba una rampa parda sin jerarquía en escala de grises. |
| Fondo base | `#FCFBFA` / `#F0ECEA` | Casi blanco: las tarjetas no se distinguían del fondo. |
| Acento | `#C03A16` (193) + `#F9B712` (115) | à“xido y dorado. |
| Radios distintos | 19 valores (1,3 â†’ 30) | Sin escala. |
| Tamaños de fuente | 10 (365à—), 15, 20, 25 | 10 pt está por debajo del mínimo de iOS (11 pt, Caption 2). |

---

## 2. Paleta resultante

### Neutros

| Rol | Claro | Oscuro | Nota |
|---|---|---|---|
| Fondo de pantalla | `#F2F2F7` | `#000000` | Nunca blanco puro: las tarjetas necesitan contra qué flotar. |
| Tarjeta / contenedor | `#FFFFFF` | `#1C1C1E` | |
| Superficie sutil, campos | `#E5E5EA` | `#2C2C2E` | |
| Separador | `#C6C6C8` | `#48484A` | |
| Texto primario | `#1C1C1E` | `#FFFFFF` | 15,25:1 sobre el fondo base. |
| Texto secundario | `#8E8E93` | `#8E8E93` | Ver §5. |
| Marcador de miniatura | `#E5E5EA` | `#2C2C2E` | |
| Marcador de foto de cabecera | `#6E6E73` | `#3A3A3C` | Más oscuro a propósito: encima va texto blanco. |

### Verde rana â€” por qué es una rampa y no un solo tono

`#34C759` es el matiz de marca, pero **como tinta sobre fondo claro mide
2,22:1 sobre blanco**. Un botón verde con etiqueta blanca a 2,22:1 es
ilegible a pleno sol, que es exactamente la condición de uso de esta app.
El verde se abrió en cuatro pasos, todos "verde rana", cada uno medido:

| Token | Valor | Uso | Contraste |
|---|---|---|---|
| `green-500` | `#34C759` | Matiz de marca: pista del interruptor encendido, tintes al 12 % | â€” |
| `green-600` | `#2AA84A` | Relleno con glifo blanco (FAB, botones circulares) | 3,09:1 âœ“ objeto gráfico |
| `green-700` | `#1E7A34` | **Tinta**: texto verde, iconos, CTA con etiqueta blanca | 5,40:1 âœ“ AA |
| `green-dark` | `#30D158` | Modo oscuro | 8,42:1 âœ“ AAA |

Regla: **sobre claro se usa la tinta; sobre oscuro o sobre foto, el vivo.**
En modo oscuro el relleno se invierte: verde claro con etiqueta oscura
(`#062B12`, 7,63:1), nunca blanco sobre `#30D158` (sería 2,02:1).

### Estado y IUCN

`#D70015` peligro · `#FF9500` alerta · `#007AFF` info · `#AF52DE` violeta ·
`#30B0C7` turquesa. Se mantiene la regla del mockup original: **la señal va
en la forma (icono + texto), el color sólo refuerza.** Los distintivos IUCN
conservan su codificación y los chips neutros pasaron a `#48484A` para que
la etiqueta blanca llegue a 8,6:1.

---

## 3. Elevación (lo que faltaba por completo)

| Nivel | Sombra | Se aplica a |
|---|---|---|
| Tarjeta | `0 1px 2px rgba(0,0,0,.04)`, `0 4px 14px rgba(0,0,0,.06)` | Tarjetas, listas, campos, chips, contenedores de imagen (156 elementos) |
| Flotante | `0 2px 6px rgba(0,0,0,.08)`, `0 8px 24px rgba(0,0,0,.12)` | Navbar, tab bar, FAB, botones circulares (58) |
| Modal | `0 4px 10px rgba(0,0,0,.08)`, `0 16px 40px rgba(0,0,0,.18)` | 16 pop-ups y sheets |

En modo oscuro las sombras suben a 40â€“65 % de opacidad; en Luz roja **no hay
sombras**: sobre negro puro no hay nada que separar y una sombra sólo
añadiría emisión.

---

## 4. Geometría, tipografía y materiales

- **Radios:** 12 botón y miniatura · 16 tarjeta · 20 modal · cápsula (`h/2`)
  para distintivos y para la píldora del tab bar. 597 shapes normalizados,
  16 boards de modal a 20.
- **Tipografía:** escala real de iOS â€” 28 Title 1 · 22 Title 2 · 20 Title 3 ·
  17 Body · 16 Callout · 15 Subhead · 13 Footnote · 11 Caption 2.
  447 textos ajustados. Cada texto recibió el tamaño HIG **que cabe en su
  caja**, para no alterar la distribución: los 365 textos de 10 pt pasaron a
  11 pt (o 13 pt donde la caja lo permitía). Ya no queda ningàºn tamaño fuera
  de la escala.
- **Materiales:** las barras superior e inferior son translàºcidas (92 % en el
  mockup, porque Penpot sólo tiene desenfoque de capa y no de fondo). El
  desenfoque real vive en el código:
  `backdrop-filter: blur(20px) saturate(180%)`, con respaldo opaco bajo
  `prefers-reduced-transparency`.
- **Contenedores de imagen:** miniatura 80à—80 r12 · foto 4:3 r16 ·
  cabecera 16:9 · todos con `object-fit: cover` y relleno neutro cuando
  están vacíos. Los atenuados sobre foto se normalizaron a negro (antes
  algunos eran grises), lo que devuelve contraste al texto encima.

---

## 5. Decisiones que conviene validar

1. **Pop-ups oscuros â†’ claros.** Los 14 pop-ups y los 2 sheets eran
   superficie oscura de marca (`N-900`, decisión del pase del 07-sep). Al
   pedir "tarjetas y contenedores en blanco puro" sobre fondo `#F2F2F7`, se
   convirtieron a sheet claro estándar de iOS: superficie blanca, título
   `#1C1C1E`, subtítulo `#8E8E93`, primario verde relleno, secundario
   `#F2F2F7` con etiqueta verde. **Si se prefiere recuperar el modal oscuro
   como recurso de marca, es un cambio de un solo token.**
2. **Texto secundario a `#8E8E93`.** Es el `systemGray` de Apple y es el
   valor pedido, pero mide **3,26:1 sobre blanco y 2,92:1 sobre `#F2F2F7`**:
   no llega a AA. Se aplicó tal cual a 178 metadatos. El sistema incluye
   `--label-secondary-aa` (`#6C6C70`, 5,23:1) y lo activa automáticamente
   bajo `prefers-contrast: more`. **Para una app que se usa a pleno sol vale
   la pena decidir si el secundario debería ser el valor AA por defecto** â€”
   es redefinir una variable.
3. **Corazón de favorito en rojo, no verde.** El acento verde queda reservado
   a CTA, tab bar e interruptores, así que el favorito volvió a la convención
   de iOS (`#FF3B30`).
4. **La barra superior de las pantallas con foto de cabecera** quedó como
   material claro salvo en las pantallas de captura (`Añadir foto`,
   `Añadir audio`), donde el visor pide cromo oscuro.

---

## 6. Modo Luz roja (visión nocturna)

Estaba marcado como trabajo futuro en el [[àNDICE DE DISEà‘O â€” Sprint 27 Sep|índice de diseño]]; ahora
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

Principio: lo que rompe la adaptación a la oscuridad es **el brillo**, no el
matiz â€” por eso ninguna superficie grande va al 100 % de luminancia. El FAB,
que en claro es un disco verde lleno, aquí es un disco casi negro con aro
rojo. Fotos, mapas y espectrogramas pasan por un filtro rojo monocromo
(`grayscale â†’ sepia â†’ hue-rotate â†’ brightness .55`) más una capa de
atenuación: cero emisión blanca o azul.

Boards: `ajustes · modo LUZ ROJA` (ya existía, corregido) y
**`home · modo LUZ ROJA (visión nocturna)`** (nuevo, para validar el modo
sobre una pantalla real con foto).

---

## 7. Dónde viven las variables

| Artefacto | Ruta | Para qué |
|---|---|---|
| Colores de biblioteca | Penpot â€º ANURA â€º biblioteca local (28 muestras `Anura / â€¦`) | Trabajar en el lienzo |
| Sets de tokens | `anura-primitivos`, `anura-claro`, `anura-oscuro`, `anura-luz-roja` (73 tokens) | Mismos nombres, tres valores |
| Temas | Penpot â€º Temas â€º grupo **Anura**: Claro · Oscuro · Luz roja | Cambiar de modo en el lienzo |
| Hoja de estilos | `D:\Anura\design-system\anura-hig.css` | Implementación: variables + clases `.a-*` |
| Banco de comprobación | `D:\Anura\design-system\index.html` | Ver los tres temas, con medidor de contraste incorporado |

El banco se levanta con la configuración `anura-design-system`
(`python -m http.server 8777 --directory design-system`) y mide en vivo cada
par tinta/fondo contra su umbral. Estado actual: **todo pasa en oscuro y en
luz roja; en claro el àºnico que no pasa es el `#8E8E93` del punto 5.2, que es
una decisión consciente.**

---

## 8. Traducción a Compose (para el sprint del 27)

Los nombres de token están pensados para mapear 1:1 a un `ColorScheme` de
Material 3 con tres esquemas (`claro`, `oscuro`, `luzRoja`):
`bg.base â†’ background`, `bg.elevated â†’ surface`, `label.primary â†’ onSurface`,
`label.secondary â†’ onSurfaceVariant`, `cta.bg â†’ primary`,
`cta.fg â†’ onPrimary`, `separator â†’ outlineVariant`, `danger â†’ error`.
El par `cta.bg`/`cta.fg` es el importante: es lo que evita repetir el error
de blanco sobre verde claro al portar el tema oscuro.



