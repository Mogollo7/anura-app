---
title: "Componentes de UI â€” EspecificaciÃ³n Detallada"
proyecto: Anura
tipo: especificaciÃ³n-tÃ©cnica
estado: draft-07-sep-2026
tags: [anura, diseÃ±o, componentes, compose, kotlin]
---

# Componentes de UI â€” EspecificaciÃ³n Detallada

[[Anura â€” Ãndice General]] Â· [[DiseÃ±o de Interfaz (Penpot)]] Â· [[App MÃ³vil]] Â· [[Stack TecnolÃ³gico]]

> [!abstract] QuÃ© es esto
> TraducciÃ³n de baja fidelidad a especificaciÃ³n tÃ©cnica ejecutable en Compose. Cada componente incluye: nombre, medidas, colores, estados interactivos, trazabilidad contra requisitos y ejemplos de composiciÃ³n.
>
> No es un replacement de Penpot; es la **fuente de verdad para implementar en Kotlin** cuando se escriba cada pantalla.

---

## NIVEL 1: Campos y etiquetas (sin estado interactivo)

### Campo de entrada numÃ©rico â€” Altitud

| Propiedad | Valor |
|-----------|-------|
| **Req** | RF-04 (metadatos) |
| **Uso** | Paso 2, secciÃ³n de metadatos |
| **Alto** | 60pt |
| **Ancho** | 320pt (contenedor de 355pt menos margins) |
| **Tipo** | `TextField` numÃ©rico |
| **Placeholder** | "Altitud (msnm)" |
| **Rango** | 0â€“5000 |
| **Color fondo** | Degradado suave, adaptado al fondo de la pantalla |
| **Color borde** | #626264 (medio) |
| **ValidaciÃ³n** | Acepta solo nÃºmeros; si sale del rango, lo ajusta al lÃ­mite |
| **Estado vacÃ­o** | Permitido (RNF-06) |

**PatrÃ³n de composiciÃ³n en Paso 2:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Paso 2: CuÃ¡ndo la viste      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Fecha            [fecha]    â”‚
â”‚ Hora             [hora]     â”‚
â”‚ Altitud (msnm)   [campo]    â”‚
â”‚ Ecosistema       [dropdown] â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Campo selector â€” Ecosistema/MicrohÃ¡bitat

| Propiedad | Valor |
|-----------|-------|
| **Req** | RF-04 (metadatos) |
| **Uso** | Paso 2, bajo Altitud |
| **Alto** | 60pt |
| **Ancho** | 320pt |
| **Tipo** | `DropdownMenu` / `ExposedDropdownMenuBox` |
| **Opciones** | Bosque Â· Agua Â· Zona abierta Â· Ãrea urbana Â· Otro |
| **Placeholder** | "Seleccionar ecosistema..." |
| **Color fondo** | Igual a campos textuales |
| **Color de la opciÃ³n activa** | #626264 (realce) |
| **Estado vacÃ­o** | Permitido (RNF-06) |

---

## NIVEL 2: Pop-ups de interacciÃ³n de sistema

### Pop-up: Permiso de cÃ¡mara

| Propiedad | Valor |
|-----------|-------|
| **Req** | RNF-14 (permisos en el momento de uso) |
| **CuÃ¡ndo aparece** | Usuario presiona "Tomar foto" en Paso 4 |
| **Ancho** | 90% (~330pt en viewport 393pt) |
| **Alto** | Contenido variable, mÃ¡x 400pt |
| **Tipo** | Bottom sheet / Modal |
| **Fondo** | #373738 (oscuro) |
| **Radio superior** | 30pt |

**Estructura:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  ðŸ“· Acceso a la cÃ¡mara           â”‚  (tÃ­tulo, 25pt)
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Anura necesita acceder a tu      â”‚  (descripciÃ³n, 15pt, #626264)
â”‚ cÃ¡mara para capturar fotos de    â”‚
â”‚ anuros. PermÃ­telo en el siguienteâ”‚
â”‚ paso.                            â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [ Permitir ]  [ Ahora no ]       â”‚  (botones 60pt alto)
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Estados:**
- **Permitido:** Cierra el pop-up, avanza a pantalla de captura
- **Denegado:** Muestra pop-up secundario "Permiso denegado â€” ve a Ajustes"
  - Botones: "Abrir Ajustes" Â· "Cancelar"
  - AcciÃ³n: `startActivity(Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, ...))`
- **Cancelado:** Regresa al Paso 4 sin cambios

### Pop-up: Permiso de micrÃ³fono

| Propiedad | Valor |
|-----------|-------|
| **Req** | RNF-14 |
| **CuÃ¡ndo aparece** | Usuario presiona "Grabar audio" en Paso 4 |
| **Estructura** | IdÃ©ntica a pop-up de cÃ¡mara |
| **Texto** | "Anura necesita acceder a tu micrÃ³fono para grabar los cantos de los anuros." |
| **TÃ­tulo** | ðŸŽ¤ Acceso al micrÃ³fono |

### Pop-up: Permiso de ubicaciÃ³n

| Propiedad | Valor |
|-----------|-------|
| **Req** | RF-04 (metadatos), RNF-14 |
| **CuÃ¡ndo aparece** | Usuario abre Paso 1 ("DÃ³nde la viste") |
| **Estructura** | IdÃ©ntica a las anteriores |
| **Texto** | "Anura registra tu ubicaciÃ³n para ayudarte a recordar dÃ³nde viste el anuro. Puedes editar la ubicaciÃ³n despuÃ©s." |
| **TÃ­tulo** | ðŸ“ Acceso a la ubicaciÃ³n |
| **Permiso** | `ACCESS_COARSE_LOCATION` + `ACCESS_FINE_LOCATION` |

---

### Pop-up: Foto borrosa (error de captura)

| Propiedad | Valor |
|-----------|-------|
| **Req** | HU-01 caso 2 (captura con mala calidad) |
| **CuÃ¡ndo aparece** | DespuÃ©s de tomar foto, si modelo detecta desenfoque |
| **Ancho** | 90% (330pt) |
| **Alto** | ~350pt |
| **Tipo** | Bottom sheet |
| **Fondo** | #373738 (oscuro) |
| **Icono** | âš ï¸ o ðŸš« (desenfoque) |

**Estructura:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  âš ï¸ Foto borrosa                 â”‚  (tÃ­tulo, 25pt)
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ La foto estÃ¡ muy borrosa para    â”‚  (descripciÃ³n, 15pt)
â”‚ analizar. Prueba:                â”‚
â”‚ â€¢ Acercarte mÃ¡s                  â”‚
â”‚ â€¢ Limpiar la lente               â”‚
â”‚ â€¢ Tomar en un lugar bien         â”‚
â”‚   iluminado                      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [ Tomar de nuevo ]  [ Aceptar ]  â”‚  (botones 60pt)
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Estados:**
- **"Tomar de nuevo":** Regresa a pantalla de captura, borra la foto anterior
- **"Aceptar":** Guarda la foto y avanza (si el usuario decide proceder a pesar de la advertencia)

---

### Pop-up: Analizando... (progreso de inferencia)

| Propiedad | Valor |
|-----------|-------|
| **Req** | HU-01, RF-05, RF-06 (feedback durante anÃ¡lisis) |
| **CuÃ¡ndo aparece** | Justo despuÃ©s de presionar "Analizar" en Paso 5 |
| **Ancho** | 90% (330pt) |
| **Tipo** | Modal no cancelable (bloquea interacciÃ³n) |
| **Fondo** | #373738 con 80% opacidad oscurecida |
| **Cierre** | AutomÃ¡tico cuando completa, o timeout 30s |

**Estructura:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚   Analizando...                  â”‚  (tÃ­tulo, 20pt, blanco)
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  ðŸ”„ SegmentaciÃ³n        50%  â–ˆâ–ˆâ–ˆ â”‚
â”‚  ðŸ”„ IdentificaciÃ³n      20%  â–ˆ   â”‚
â”‚  ðŸ”„ AnÃ¡lisis de audio    0%  â€”   â”‚
â”‚                                  â”‚
â”‚  Tiempo: ~3-4 segundos           â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Detalles tÃ©cnicos:**
- **Barra de progreso:** LinearProgressIndicator de Compose
- **Etapas:**
  1. SegmentaciÃ³n (recorte de individuo): ~1s
  2. ExtracciÃ³n de embeddings BioCLIP: ~1s
  3. ClasificaciÃ³n jerÃ¡rquica + bÃºsqueda vectorial: ~0.5s
  4. Open-set + contexto geogrÃ¡fico: ~0.5s
  5. (Opcional) AnÃ¡lisis de audio si se capturÃ³: ~1-2s
- **Color de progreso:** #626264 (gris medio)
- **CancelaciÃ³n:** Imposible (por diseÃ±o â€” evita estados corruptos)

---

## NIVEL 3: Variantes de contexto (propio vs. ajeno)

### Tarjeta de observaciÃ³n â€” Variante propia

**UbicaciÃ³n:** Listado de "Mis observaciones"

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ [ðŸ“· imagen]  [â¤ï¸ guardado]       â”‚  (imagen 167Ã—196, corazÃ³n arriba)
â”‚             [âš ï¸ estado IUCN]      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Nombre comÃºn                     â”‚  (15pt, #626264)
â”‚ Nombre cientÃ­fico                â”‚  (10pt, gris mÃ¡s claro)
â”‚ Hace 2 horas                     â”‚  (10pt, timestamp)
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [ðŸ“ Editar] [ðŸ—‘ï¸ Eliminar]       â”‚  (botones 60pt, solo en propia)
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Botones en propio:**
- `Editar`: Abre la observaciÃ³n en modo editable, permite cambiar metadatos, foto, audio
- `Eliminar`: Pop-up de confirmaciÃ³n "Â¿Eliminar esta observaciÃ³n?"
- Color botones: #626264 sobre fondo claro

### Tarjeta de observaciÃ³n â€” Variante ajena

**UbicaciÃ³n:** Explorando observaciones de otros usuarios

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ [ðŸ“· imagen]  [â¤ï¸ no guardado]    â”‚  (imagen 167Ã—196, corazÃ³n vacÃ­o)
â”‚             [âš ï¸ estado IUCN]      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Nombre comÃºn                     â”‚
â”‚ Nombre cientÃ­fico                â”‚
â”‚ @usuario Â· Hace 2 horas          â”‚  (username + timestamp)
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [ðŸ’¬ Comentar] [ðŸ‘ Apoyar ID]    â”‚  (botones 60pt, otros en ajena)
â”‚ [ðŸš© Reportar]                    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Botones en ajena:**
- `Comentar`: Abre vista de comentarios
- `Apoyar ID`: Incrementa contador de apoyo a la identificaciÃ³n propuesta
- `Reportar`: Pop-up de denuncias ("Foto inadecuada", "Especie incorrecta", "Otro")
- Color botones: #626264

---

### Perfil â€” Variante propia

**UbicaciÃ³n:** Mi perfil (accesible desde navbar)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ [ðŸŽ­ avatar]  [âœï¸ Editar perfil] â”‚  (avatar 60pt, botÃ³n derecha)
â”‚ @nombre_usuario                  â”‚
â”‚ "HerpetÃ³logo aventurero"         â”‚  (bio)
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ 42 observaciones  â”‚ 15 seguidos  â”‚
â”‚ 7 seguidores      â”‚              â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ðŸ“Œ Observaciones pÃºblicas        â”‚  (pestaÃ±as)
â”‚ ðŸ“Œ Observaciones privadas        â”‚  (SOLO en propio)
â”‚ â­ Favoritos                     â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [Listado de observaciones...]    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [Ajustes]  [Cerrar sesiÃ³n]       â”‚  (botones inferiores, SOLO en propio)
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Elementos Ãºnicos en propio:**
- BotÃ³n "Editar perfil": Abre formulario de nombre, bio, foto
- PestaÃ±a "Observaciones privadas": Solo visible al propietario
- Botones "Ajustes" y "Cerrar sesiÃ³n": Acceso a configuraciÃ³n
- Color botones: #626264

### Perfil â€” Variante ajena

**UbicaciÃ³n:** Ver perfil de otro usuario

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ [ðŸŽ­ avatar]  [âž• Seguir]         â”‚  (botÃ³n "Seguir", no "Editar")
â”‚ @nombre_usuario                  â”‚
â”‚ "HerpetÃ³logo aventurero"         â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ 42 observaciones  â”‚ 15 seguidos  â”‚
â”‚ 7 seguidores      â”‚              â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ðŸ“Œ Observaciones pÃºblicas        â”‚  (solo pÃºblica, sin privadas)
â”‚ â­ Favoritos                     â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [Listado de observaciones...]    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [ðŸ’¬ Contactar]  [ðŸš© Reportar]   â”‚  (botones nuevos, no "Ajustes")
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Elementos Ãºnicos en ajena:**
- BotÃ³n "Seguir" (no "Editar")
- Sin pestaÃ±a de privadas
- Botones "Contactar" y "Reportar" al pie
- Sin acceso a "Ajustes"

---

### Comentario â€” Variante propia

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ ðŸ‘¤ TÃº Â· Hace 1 hora              â”‚
â”‚ "Excelente foto, Â¿dÃ³nde fue?"   â”‚
â”‚ [ âœï¸ Editar ]  [ ðŸ—‘ï¸ Borrar ]    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Botones:** Editar Â· Borrar

### Comentario â€” Variante ajena

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ ðŸ‘¤ @otro_usuario Â· Hace 1 hora   â”‚
â”‚ "Excelente foto, Â¿dÃ³nde fue?"   â”‚
â”‚ [ ðŸ’¬ Responder ]  [ ðŸš© Reportar]â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Botones:** Responder Â· Reportar

---

## NIVEL 4: Estados de sincronizaciÃ³n (distintivos)

### Distintivo de estado en observaciÃ³n

**UbicaciÃ³n:** Esquina inferior derecha de la tarjeta de observaciÃ³n (para RF-13)

| Estado | Icono | Color | Significado |
|--------|-------|-------|------------|
| LOCAL | ðŸ’¾ | #CCCCCC (gris claro) | Guardada localmente, no sincronizada aÃºn |
| EN_COLA | â³ | #FFC107 (Ã¡mbar) | Esperando sincronizaciÃ³n |
| SINCRONIZADA | âœ… | #4CAF50 (verde) | Sincronizada con servidor |
| VALIDADA | ðŸ”’ | #2196F3 (azul) | Validada por experto (fuera de sprint) |

**TamaÃ±o:** 20Ã—20pt, ubicado en (145, 170) respecto a la esquina superior izquierda de la tarjeta

**Comportamiento:** 
- Tooltip al pasar el dedo: "Sincronizada a las 14:32"
- Tap: Abre pop-up con detalles de sincronizaciÃ³n

---

## NIVEL 5: Vistas complejas

### Resultado del anÃ¡lisis â€” Caso open-set (no registrada)

**CuÃ¡ndo aparece:** BioCLIP genera embedding, open-set rechaza a umbral, la especie no estÃ¡ en el catÃ¡logo

**Estructura:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚        Resultado del anÃ¡lisis                â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  âš ï¸ Especie no registrada en el catÃ¡logo    â”‚  (tÃ­tulo 20pt)
â”‚                                              â”‚
â”‚  Mejor coincidencia: GÃ‰NERO Dendropsophus  â”‚  (15pt)
â”‚  Confianza: 67%                              â”‚
â”‚                                              â”‚
â”‚  Las 28 especies del catÃ¡logo actual no     â”‚  (descripciÃ³n 15pt)
â”‚  incluyen esta. PodrÃ­a ser:                  â”‚
â”‚  â€¢ Una especie nueva para la regiÃ³n          â”‚
â”‚  â€¢ Una especie muy rara                      â”‚
â”‚  â€¢ Merece un segundo anÃ¡lisis                â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  [Ver detalles de anÃ¡lisis]                  â”‚  (expandible)
â”‚  â€¢ SegmentaciÃ³n: 95%                         â”‚
â”‚  â€¢ Similitud de contexto geogrÃ¡fico: 12%     â”‚
â”‚  â€¢ Audio (si hay): No coincide               â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  [ Editar y reenviar ]  [ Guardar igual ]   â”‚  (60pt botones)
â”‚  [ Volver atrÃ¡s ]                            â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Botones:**
- `Editar y reenviar`: Regresa a Paso 4, permite cambiar foto/audio
- `Guardar igual`: Guarda con etiqueta "GENERO" en lugar de especie especÃ­fica
- `Volver atrÃ¡s`: Regresa al listado sin guardar

---

### Ficha de especie â€” Cuatro pestaÃ±as tÃ©cnicas

**Requisito:** RF-10 (ficha tÃ©cnica completa)

**UbicaciÃ³n:** Accesible desde "Detalles de observaciÃ³n" o desde "Explorar â†’ Especies"

**Barra de secciones:** Desplazable horizontalmente (HorizontalPager o LazyRow)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ [Recuento] [MorfologÃ­a] [BioacÃºstica]   â”‚  (tabs desplazables)
â”‚             [EcologÃ­a]                  â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Contenido de la pestaÃ±a activa...       â”‚
â”‚ [DescripciÃ³n larga, imÃ¡genes, datos]    â”‚
â”‚                                         â”‚
â”‚ [Mostrar mÃ¡s]                           â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

#### PestaÃ±a 1: Recuento (ya existe)
- Carrusel de fotos
- Ãrbol taxonÃ³mico
- EstadÃ­sticas de capturas (nÃºmero de registros)

#### PestaÃ±a 2: MorfologÃ­a

**Contenido:**
- **TamaÃ±o:** Rango de longitud rostro-cloaca (mm), con diagrama
- **Peso:** Rango en gramos
- **ColoraciÃ³n:** DescripciÃ³n + mini-galerÃ­a de patrones dorsales/ventrales
- **Crestas y membranas:** Presencia/ausencia, con etiquetas anatÃ³micas
- **ReproducciÃ³n:** Amplexo tipo (axial/inguinal), tamaÃ±o de huevo
- **Dimorfismo sexual:** DescripciÃ³n y fotos comparativas
- **Fuente:** Referencia bibliogrÃ¡fica o link a Amphibiaweb/IUCN

**Estructura de UI:**
```
Cada atributo morfolÃ³gico:
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ ðŸ“ TamaÃ±o (LSC)            â”‚  (icono + label)
â”‚ 18â€“25 mm                   â”‚  (valor)
â”‚ [Mostrar diagrama]         â”‚  (botÃ³n expandible)
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [Diagrama de medida LSC]   â”‚  (imagen expandida)
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

#### PestaÃ±a 3: BioacÃºstica

**Contenido:**
- **Tipo de canto:** ReproducciÃ³n, territorial, cortejo
- **Frecuencia dominante:** Rango en Hz con espectrograma
- **DuraciÃ³n de nota:** Milisegundos, con waveform
- **Tasa de repeticiÃ³n:** Notas/segundo
- **Ejemplo de audio:** Widget de reproducciÃ³n (botÃ³n play, barra de progreso)
- **Contexto temporal:** CuÃ¡ndo canta (Ã©poca del aÃ±o, hora del dÃ­a)

**Estructura de UI:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ ðŸŽµ Canto de reproducciÃ³n   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [â–¶ï¸ Reproducir ejemplo]    â”‚  (botÃ³n play)
â”‚ â–“â–“â–“â–‘â–‘â–‘â–‘â–‘  0:45 / 1:20     â”‚  (barra de progreso)
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Frecuencia dominante       â”‚
â”‚ 800â€“1200 Hz                â”‚  (valor)
â”‚ [Mostrar espectrograma]    â”‚  (expandible)
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [Espectrograma real]       â”‚  (imagen)
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

#### PestaÃ±a 4: EcologÃ­a

**Contenido:**
- **HÃ¡bitat:** Tipos de ecosistema (bosque hÃºmedo, sabana, etc.), altitud (msnm)
- **MicrohÃ¡bitat:** Dosel, sotobosque, suelo, agua
- **Actividad:** Nocturno, diurno, crepuscular
- **ReproducciÃ³n:** Tipo de amplexo, lugar de reproducciÃ³n (charco, arroyo, Ã¡rbol)
- **Dieta:** QuÃ© come (insectos, otros anuros, etc.)
- **DistribuciÃ³n:** Mapa simplificado de rango geogrÃ¡fico
- **Amenazas:** PÃ©rdida de hÃ¡bitat, hongos, contaminaciÃ³n
- **Estado IUCN:** CategorÃ­a con icono

**Estructura de UI:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ ðŸŒ³ HÃ¡bitat                 â”‚
â”‚ Bosque hÃºmedo 800â€“1800m    â”‚  (valor + rango altitud)
â”‚ [Mapa simplificado]        â”‚  (expandible)
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ðŸ—ºï¸ DistribuciÃ³n            â”‚
â”‚ [Mapa de rango]            â”‚  (imagen de distribuciÃ³n)
â”‚ Colombia (endemismo regional)
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ðŸ”´ Estado IUCN             â”‚
â”‚ Vulnerable (VU)            â”‚  (icono + categorÃ­a)
â”‚ [Ver en IUCN Red List]     â”‚  (link externo)
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

### SecciÃ³n "Mis publicaciones" (con variantes pÃºblica/privada)

**UbicaciÃ³n:** En el perfil propio (no en ajena)

**Estructura:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Mis observaciones                 â”‚
â”‚ [ðŸ“Œ Todas] [ðŸŒ PÃºblicas] [ðŸ”’ Privadas]
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [ Listado de tarjetas ]           â”‚
â”‚                                   â”‚
â”‚ [ BotÃ³n de compartir/visibilidad] â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**PestaÃ±as:**
- **Todas:** Muestra pÃºblicas + privadas (solo tÃº ves esto)
- **PÃºblicas:** Visibles para otros usuarios
- **Privadas:** Solo tÃº las ves (marcadas con ðŸ”’)

**Pop-up de visibilidad:**

Cuando el usuario guarda una observaciÃ³n nueva, aparece:
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Visibilidad de la observaciÃ³n    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ â—‹ Privada (solo tÃº)             â”‚  (seleccionable)
â”‚ â—‹ PÃºblica                        â”‚  (seleccionable)
â”‚                                  â”‚
â”‚ Las pÃºblicas ayudan a otros a    â”‚
â”‚ aprender; la ubicaciÃ³n exacta    â”‚
â”‚ se ofusca para especies          â”‚
â”‚ amenazadas.                      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [ Guardar como privada ]         â”‚  (60pt botones)
â”‚ [ Guardar como pÃºblica ]         â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## Trazabilidad de requisitos completados

| Req | Nivel | Componente | Estado |
|-----|-------|-----------|--------|
| RF-04 | 1 | Campos de altitud + ecosistema | âœ… Especificado |
| RF-13 | 4 | Distintivos de sincronizaciÃ³n | âœ… Especificado |
| RNF-06 | 1 | BotÃ³n "Omitir" en pasos | âœ… Especificado |
| RNF-14 | 2 | Pop-ups de permisos (3) | âœ… Especificado |
| HU-01 caso 2 | 2 | Pop-up de foto borrosa | âœ… Especificado |
| HU-02 caso 3 | 4 | Resultado open-set | âœ… Especificado |
| RF-10 | 5 | Cuatro pestaÃ±as de ficha | âœ… Especificado |
| Â§ Variantes | 3 | Propio vs. ajeno (4 elementos) | âœ… Especificado |

---

## GuÃ­a de implementaciÃ³n en Compose

### PatrÃ³n para reutilizar componentes

```kotlin
// Componente genÃ©rico de tarjeta de observaciÃ³n
@Composable
fun ObservationCard(
    observation: Observacion,
    isOwn: Boolean,  // true = variante propia, false = ajena
    onEdit: () -> Unit,
    onDelete: () -> Unit,
    onComment: () -> Unit,
    onLike: () -> Unit
) {
    // Renderiza diferente segÃºn isOwn
    if (isOwn) {
        // Botones: Editar, Eliminar
    } else {
        // Botones: Comentar, Apoyar, Reportar
    }
}
```

### PatrÃ³n para pop-ups de permisos

```kotlin
// GenÃ©rico para cualquier permiso
@Composable
fun PermissionRequestBottomSheet(
    title: String,
    description: String,
    icon: String,
    permission: String,
    onGranted: () -> Unit,
    onDenied: () -> Unit
) {
    // Solicita el permiso y maneja los casos
}
```

---

### Resumen de salida de campo (cierre)

**Requisito:** HU-04 (salidas de campo comunitarias)

**CuÃ¡ndo aparece:** Usuario presiona "Cerrar salida" en una sesiÃ³n de campo activa

**Pantalla previa: Salida de campo en curso**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Salida de campo: PÃ¡ramo La BreÃ±a â”‚
â”‚ Iniciada: 14:30 Â· DuraciÃ³n: 4h   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ðŸ“Š Resumen                       â”‚
â”‚ Observaciones: 12                â”‚  (nÃºmero de registros)
â”‚ Especies: 7                      â”‚
â”‚ Ubicaciones Ãºnicas: 8            â”‚
â”‚ Audio capturado: 340 MB          â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [Editar detalles] [Mostrar mapa] â”‚
â”‚                                  â”‚
â”‚ [Cerrar salida]                  â”‚  (botÃ³n 60pt)
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Pop-up de cierre:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Cerrar salida de campo           â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ âœ… 12 observaciones registradas  â”‚
â”‚ âœ… 7 especies Ãºnicas             â”‚
â”‚ âœ… Fecha: 07 sep 2026            â”‚
â”‚ âœ… DuraciÃ³n: 4 horas 23 minutos  â”‚
â”‚ âš ï¸  10 observaciones sin audio    â”‚
â”‚                                  â”‚
â”‚ Â¿Quieres hacerla pÃºblica?        â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [ Privada ]  [ PÃºblica ]         â”‚  (60pt botones)
â”‚ [ Editar notas ]                 â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Estados finales:**
- **Privada:** Guardada en dispositivo, solo visible para tÃ­
- **PÃºblica:** Sincronizada con servidor, contribuye a mapa comunitario
- **Editar notas:** Abre campo de texto para agregar observaciones (contexto, condiciones climÃ¡ticas, equipo)

**Persistencia:**
- La salida queda en el historial
- Accesible desde "Mis salidas de campo" en perfil
- Exportable como Darwin Core (Etapa 2, post-27 sep)

---

## Siguientes pasos

1. **HILO DE VALIDACIÃ“N:** Revisar esta especificaciÃ³n en Penpot, confirmar medidas y colores
2. **IMPLEMENTACIÃ“N:** Pasar cada nivel a Compose siguiendo los patrones de reutilizaciÃ³n
3. **TESTING:** Verificar variantes propio/ajeno en dispositivo real antes de mergear



