# Guía de identidad visual Android — Anura

Normas supremas de branding e identidad visual para la app móvil (claro, oscuro y luz roja).  
**No inventa marca:** consolida Penpot, la nota HIG de la bóveda y los tokens Kotlin ya vigentes.

## Fuente de verdad

| Capa | Dónde |
|------|--------|
| Diseño | Penpot · archivo ANURA · página `Mockup Final` · sets `anura-claro`, `anura-oscuro`, `anura-luz-roja` |
| Proceso | `Second Brain/Brain/06 Proceso de Desarrollo de la App/Sistema de Estilos HIG — Refactor de Paleta y Elevación.md` |
| Código | `app/.../designsystem/theme/AnuraColorTokens.kt`, `AnuraTheme.kt`, `AnuraExtendedColors.kt` |
| Plataforma | Skill Material 3 (`android-design-guidelines`) — **Anura gana** si hay conflicto |

Implementación UI: siempre `MaterialTheme.colorScheme` o `AnuraTheme.extendedColors`.  
Esta guía es el contrato; los hex viven solo en `AnuraColorTokens`.

---

## Identidad

- **Producto:** Anura — observación de anuros en campo.
- **Mood:** HIG neutro + **verde rana** como único acento de marca.
- **Temas** (`AnuraThemeMode`):
  - `Claro`
  - `Oscuro`
  - `LuzRoja` — tema explícito de campo nocturno; **no** se deriva de `isSystemInDarkTheme()`
  - `Sistema` — resuelve a Claro u Oscuro según el dispositivo

---

## Prohibiciones críticas

1. **Nunca** hardcodear hex/RGB en composables.
2. **Nunca** Dynamic Color / Material You por wallpaper (§3.7-P4): el color carga semántica (IUCN, toxicidad, luz roja).
3. Texto en **`sp`**; targets táctiles ≥ **48 dp**.
4. Señal de peligro / IUCN / toxicidad: **icono + texto**; el color solo refuerza.
5. Favorito en **rojo de sistema**, no en verde de marca.
6. Sobre claro: CTA y texto de acento con **tinta** (`accentInk` / `#1E7A34`), no el matiz vivo `#34C759` como texto.
7. Ante conflicto con Material genérico (p. ej. “no usar negro puro”), **prevalece esta guía Anura**.

---

## Tokens por tema

Valores alineados con Penpot y `AnuraColorTokens.kt`.

| Rol | Claro | Oscuro | Luz roja |
|-----|-------|--------|----------|
| Acento (tint) | `#34C759` | `#30D158` | `#6B1F19` (ink/icon `#FF453A`) |
| Acento tinta / icono | `#1E7A34` / `#2AA84A` | `#30D158` | `#FF453A` |
| On accent | `#FFFFFF` | `#0B2B14` | `#000000` |
| bgBase | `#F2F2F7` | `#000000` | `#000000` |
| bgElevated | `#FFFFFF` | `#1C1C1E` | `#160000` |
| bgSubtle | `#E5E5EA` | `#2C2C2E` | `#210605` |
| separator | `#C6C6C8` | `#38383A` | `#5A170F` |
| labelPrimary | `#1C1C1E` | `#FFFFFF` | `#FF453A` |
| labelSecondary | `#8E8E93` | `#8E8E93` | `#B3352C` |
| labelTertiary | `#C7C7CC` | `#636366` | `#B3352C` |
| boardBackground | `#EFF4F0` | `#000000` | `#000000` |
| danger | `#D70015` | `#FF453A` | `#FF453A` |
| warning | `#FF9500` | `#FF9F0A` | `#FF453A` |
| info | `#007AFF` | `#0A84FF` | `#FF453A` |
| success | `#248A3D` | `#30D158` | `#FF453A` |

**Override vs Material R1.8:** Anura **sí usa negro puro** (`#000000`) en Oscuro y Luz roja para `bgBase` / `boardBackground` — decisión de campo nocturno / Penpot.

**Nota contraste:** `#8E8E93` como secundario es decisión consciente (systemGray HIG); no siempre alcanza AA sobre fondos claros. Para metadatos críticos a pleno sol, preferir contraste reforzado cuando exista token AA en el design system.

---

## Verde rana (rampa obligatoria)

| Token | Valor | Uso |
|-------|-------|-----|
| Matiz / tint | `#34C759` | Marca, switch, wash ~12 % — **no** texto sobre claro |
| Icon / fill | `#2AA84A` | Relleno con glifo blanco (FAB, botones circulares) |
| Tinta / ink | `#1E7A34` | Texto verde, iconos, CTA con label blanco (AA sobre blanco) |
| Vivo oscuro | `#30D158` | Modo oscuro; on-accent oscuro (`#0B2B14`), **no** blanco sobre ese verde |

**Regla:** sobre claro → tinta; sobre oscuro o foto → vivo.

---

## Geometría y tipografía (móvil)

- **Radios:** 12 botón / miniatura · 16 tarjeta · 20 modal · cápsula (`999`) en chips y píldora de tab.
- **Tipografía:** escala tipo iOS (Title 1 … Caption) vía `MaterialTheme.typography` + `sp`.
- **Elevación:** sombras en claro; más opacas en oscuro; **sin sombras en Luz roja**.
- **Glass sobre foto:** `extendedColors.glassLight` / `onGlass` (texto siempre blanco sobre media).
- **Borde de tarjeta / píldora:** `cardStroke` = `labelPrimary` al 12 % de opacidad.
- **Board:** splash / home / auth / wizard usan `boardBackground`, no confundir con `bgBase` en claro (`#EFF4F0` vs `#F2F2F7`).

---

## Luz roja (visión nocturna)

- Monocromo rojo sobre negro: preserva la adaptación a la oscuridad del observador.
- Sin sombras; danger / warning / info / success colapsan a `#FF453A`.
- Media: filtro vía `AnuraTheme.mediaColorFilter` cuando aplica (cero emisión blanca/azul en fotos críticas).

---

## Mapeo Material 3

`AnuraColorTokens.toColorScheme(isDark)`:

| Token Anura | Rol M3 |
|-------------|--------|
| `accentTint` | `primary` / `primaryContainer` |
| `labelOnAccent` | `onPrimary` / `onPrimaryContainer` |
| `bgBase` | `background` |
| `labelPrimary` | `onBackground` / `onSurface` |
| `bgElevated` | `surface` |
| `bgSubtle` | `surfaceVariant` |
| `labelSecondary` | `onSurfaceVariant` |
| `labelTertiary` | `outline` |
| `separator` | `outlineVariant` |
| `statusDanger` | `error` |

Roles **solo** en `AnuraTheme.extendedColors`: `accentIcon`, `accentInk`, `accentPressed`, `warning` / `info` / `success` (+ `on*`), placeholders, glass, `boardBackground`, `cardStroke`.

```
Penpot Mockup Final
        │
        ▼
 AnuraColorTokens ──► MaterialTheme.colorScheme ──► Composables
        │
        └──► AnuraTheme.extendedColors ──────────► Composables
```

---

## Checklist rápido al implementar UI

- [ ] ¿El color sale de `colorScheme` o `extendedColors`?
- [ ] ¿CTA en claro usa tinta, no `#34C759` como texto?
- [ ] ¿Target ≥ 48 dp y texto en `sp`?
- [ ] ¿Peligro/IUCN tienen icono + etiqueta, no solo color?
- [ ] ¿Favorito es rojo de sistema?
- [ ] ¿Luz roja sin sombras y sin blancos en media crítica?
- [ ] ¿Pantallas de board usan `boardBackground`?

---

## Fuera de esta guía

- Web / `anura-hig.css` (paralelo, mismo espíritu; no es el contrato de este repo Android).
- Cambios de valor de token: van primero a Penpot, luego a `AnuraColorTokens.kt`, luego a esta tabla.
