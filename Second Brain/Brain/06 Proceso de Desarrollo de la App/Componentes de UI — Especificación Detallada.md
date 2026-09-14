---
title: "Componentes de UI â€” Especificación Detallada"
proyecto: Anura
tipo: especificación-técnica
estado: draft-07-sep-2026
tags: [anura, diseño, componentes, compose, kotlin]
---

# Componentes de UI â€” Especificación Detallada

[[Anura â€” àndice General]] · [[Diseño de Interfaz (Penpot)]] · [[App Móvil]] · [[Stack Tecnológico]]

> [!abstract] Qué es esto
> Traducción de baja fidelidad a especificación técnica ejecutable en Compose. Cada componente incluye: nombre, medidas, colores, estados interactivos, trazabilidad contra requisitos y ejemplos de composición.
>
> No es un replacement de Penpot; es la **fuente de verdad para implementar en Kotlin** cuando se escriba cada pantalla.

---

## NIVEL 1: Campos y etiquetas (sin estado interactivo)

### Campo de entrada numérico â€” Altitud

| Propiedad | Valor |
|-----------|-------|
| **Req** | RF-04 (metadatos) |
| **Uso** | Paso 2, sección de metadatos |
| **Alto** | 60pt |
| **Ancho** | 320pt (contenedor de 355pt menos margins) |
| **Tipo** | `TextField` numérico |
| **Placeholder** | "Altitud (msnm)" |
| **Rango** | 0â€“5000 |
| **Color fondo** | Degradado suave, adaptado al fondo de la pantalla |
| **Color borde** | #626264 (medio) |
| **Validación** | Acepta solo nàºmeros; si sale del rango, lo ajusta al límite |
| **Estado vacío** | Permitido (RNF-06) |

**Patrón de composición en Paso 2:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Paso 2: Cuándo la viste      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Fecha            [fecha]    â”‚
â”‚ Hora             [hora]     â”‚
â”‚ Altitud (msnm)   [campo]    â”‚
â”‚ Ecosistema       [dropdown] â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Campo selector â€” Ecosistema/Microhábitat

| Propiedad | Valor |
|-----------|-------|
| **Req** | RF-04 (metadatos) |
| **Uso** | Paso 2, bajo Altitud |
| **Alto** | 60pt |
| **Ancho** | 320pt |
| **Tipo** | `DropdownMenu` / `ExposedDropdownMenuBox` |
| **Opciones** | Bosque · Agua · Zona abierta · àrea urbana · Otro |
| **Placeholder** | "Seleccionar ecosistema..." |
| **Color fondo** | Igual a campos textuales |
| **Color de la opción activa** | #626264 (realce) |
| **Estado vacío** | Permitido (RNF-06) |

---

## NIVEL 2: Pop-ups de interacción de sistema

### Pop-up: Permiso de cámara

| Propiedad | Valor |
|-----------|-------|
| **Req** | RNF-14 (permisos en el momento de uso) |
| **Cuándo aparece** | Usuario presiona "Tomar foto" en Paso 4 |
| **Ancho** | 90% (~330pt en viewport 393pt) |
| **Alto** | Contenido variable, máx 400pt |
| **Tipo** | Bottom sheet / Modal |
| **Fondo** | #373738 (oscuro) |
| **Radio superior** | 30pt |

**Estructura:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  ðŸ“· Acceso a la cámara           â”‚  (título, 25pt)
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Anura necesita acceder a tu      â”‚  (descripción, 15pt, #626264)
â”‚ cámara para capturar fotos de    â”‚
â”‚ anuros. Permítelo en el siguienteâ”‚
â”‚ paso.                            â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [ Permitir ]  [ Ahora no ]       â”‚  (botones 60pt alto)
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Estados:**
- **Permitido:** Cierra el pop-up, avanza a pantalla de captura
- **Denegado:** Muestra pop-up secundario "Permiso denegado â€” ve a Ajustes"
  - Botones: "Abrir Ajustes" · "Cancelar"
  - Acción: `startActivity(Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, ...))`
- **Cancelado:** Regresa al Paso 4 sin cambios

### Pop-up: Permiso de micrófono

| Propiedad | Valor |
|-----------|-------|
| **Req** | RNF-14 |
| **Cuándo aparece** | Usuario presiona "Grabar audio" en Paso 4 |
| **Estructura** | Idéntica a pop-up de cámara |
| **Texto** | "Anura necesita acceder a tu micrófono para grabar los cantos de los anuros." |
| **Título** | ðŸŽ¤ Acceso al micrófono |

### Pop-up: Permiso de ubicación

| Propiedad | Valor |
|-----------|-------|
| **Req** | RF-04 (metadatos), RNF-14 |
| **Cuándo aparece** | Usuario abre Paso 1 ("Dónde la viste") |
| **Estructura** | Idéntica a las anteriores |
| **Texto** | "Anura registra tu ubicación para ayudarte a recordar dónde viste el anuro. Puedes editar la ubicación después." |
| **Título** | ðŸ“ Acceso a la ubicación |
| **Permiso** | `ACCESS_COARSE_LOCATION` + `ACCESS_FINE_LOCATION` |

---

### Pop-up: Foto borrosa (error de captura)

| Propiedad | Valor |
|-----------|-------|
| **Req** | HU-01 caso 2 (captura con mala calidad) |
| **Cuándo aparece** | Después de tomar foto, si modelo detecta desenfoque |
| **Ancho** | 90% (330pt) |
| **Alto** | ~350pt |
| **Tipo** | Bottom sheet |
| **Fondo** | #373738 (oscuro) |
| **Icono** | âš ï¸ o ðŸš« (desenfoque) |

**Estructura:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  âš ï¸ Foto borrosa                 â”‚  (título, 25pt)
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ La foto está muy borrosa para    â”‚  (descripción, 15pt)
â”‚ analizar. Prueba:                â”‚
â”‚ â€¢ Acercarte más                  â”‚
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
| **Req** | HU-01, RF-05, RF-06 (feedback durante análisis) |
| **Cuándo aparece** | Justo después de presionar "Analizar" en Paso 5 |
| **Ancho** | 90% (330pt) |
| **Tipo** | Modal no cancelable (bloquea interacción) |
| **Fondo** | #373738 con 80% opacidad oscurecida |
| **Cierre** | Automático cuando completa, o timeout 30s |

**Estructura:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚   Analizando...                  â”‚  (título, 20pt, blanco)
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  ðŸ”„ Segmentación        50%  â–ˆâ–ˆâ–ˆ â”‚
â”‚  ðŸ”„ Identificación      20%  â–ˆ   â”‚
â”‚  ðŸ”„ Análisis de audio    0%  â€”   â”‚
â”‚                                  â”‚
â”‚  Tiempo: ~3-4 segundos           â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Detalles técnicos:**
- **Barra de progreso:** LinearProgressIndicator de Compose
- **Etapas:**
  1. Segmentación (recorte de individuo): ~1s
  2. Extracción de embeddings BioCLIP: ~1s
  3. Clasificación jerárquica + bàºsqueda vectorial: ~0.5s
  4. Open-set + contexto geográfico: ~0.5s
  5. (Opcional) Análisis de audio si se capturó: ~1-2s
- **Color de progreso:** #626264 (gris medio)
- **Cancelación:** Imposible (por diseño â€” evita estados corruptos)

---

## NIVEL 3: Variantes de contexto (propio vs. ajeno)

### Tarjeta de observación â€” Variante propia

**Ubicación:** Listado de "Mis observaciones"

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ [ðŸ“· imagen]  [â¤ï¸ guardado]       â”‚  (imagen 167à—196, corazón arriba)
â”‚             [âš ï¸ estado IUCN]      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Nombre comàºn                     â”‚  (15pt, #626264)
â”‚ Nombre científico                â”‚  (10pt, gris más claro)
â”‚ Hace 2 horas                     â”‚  (10pt, timestamp)
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [ðŸ“ Editar] [ðŸ—‘ï¸ Eliminar]       â”‚  (botones 60pt, solo en propia)
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Botones en propio:**
- `Editar`: Abre la observación en modo editable, permite cambiar metadatos, foto, audio
- `Eliminar`: Pop-up de confirmación "¿Eliminar esta observación?"
- Color botones: #626264 sobre fondo claro

### Tarjeta de observación â€” Variante ajena

**Ubicación:** Explorando observaciones de otros usuarios

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ [ðŸ“· imagen]  [â¤ï¸ no guardado]    â”‚  (imagen 167à—196, corazón vacío)
â”‚             [âš ï¸ estado IUCN]      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Nombre comàºn                     â”‚
â”‚ Nombre científico                â”‚
â”‚ @usuario · Hace 2 horas          â”‚  (username + timestamp)
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [ðŸ’¬ Comentar] [ðŸ‘ Apoyar ID]    â”‚  (botones 60pt, otros en ajena)
â”‚ [ðŸš© Reportar]                    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Botones en ajena:**
- `Comentar`: Abre vista de comentarios
- `Apoyar ID`: Incrementa contador de apoyo a la identificación propuesta
- `Reportar`: Pop-up de denuncias ("Foto inadecuada", "Especie incorrecta", "Otro")
- Color botones: #626264

---

### Perfil â€” Variante propia

**Ubicación:** Mi perfil (accesible desde navbar)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ [ðŸŽ­ avatar]  [âœï¸ Editar perfil] â”‚  (avatar 60pt, botón derecha)
â”‚ @nombre_usuario                  â”‚
â”‚ "Herpetólogo aventurero"         â”‚  (bio)
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ 42 observaciones  â”‚ 15 seguidos  â”‚
â”‚ 7 seguidores      â”‚              â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ðŸ“Œ Observaciones pàºblicas        â”‚  (pestañas)
â”‚ ðŸ“Œ Observaciones privadas        â”‚  (SOLO en propio)
â”‚ â­ Favoritos                     â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [Listado de observaciones...]    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [Ajustes]  [Cerrar sesión]       â”‚  (botones inferiores, SOLO en propio)
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Elementos àºnicos en propio:**
- Botón "Editar perfil": Abre formulario de nombre, bio, foto
- Pestaña "Observaciones privadas": Solo visible al propietario
- Botones "Ajustes" y "Cerrar sesión": Acceso a configuración
- Color botones: #626264

### Perfil â€” Variante ajena

**Ubicación:** Ver perfil de otro usuario

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ [ðŸŽ­ avatar]  [âž• Seguir]         â”‚  (botón "Seguir", no "Editar")
â”‚ @nombre_usuario                  â”‚
â”‚ "Herpetólogo aventurero"         â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ 42 observaciones  â”‚ 15 seguidos  â”‚
â”‚ 7 seguidores      â”‚              â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ðŸ“Œ Observaciones pàºblicas        â”‚  (solo pàºblica, sin privadas)
â”‚ â­ Favoritos                     â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [Listado de observaciones...]    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [ðŸ’¬ Contactar]  [ðŸš© Reportar]   â”‚  (botones nuevos, no "Ajustes")
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Elementos àºnicos en ajena:**
- Botón "Seguir" (no "Editar")
- Sin pestaña de privadas
- Botones "Contactar" y "Reportar" al pie
- Sin acceso a "Ajustes"

---

### Comentario â€” Variante propia

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ ðŸ‘¤ Tàº · Hace 1 hora              â”‚
â”‚ "Excelente foto, ¿dónde fue?"   â”‚
â”‚ [ âœï¸ Editar ]  [ ðŸ—‘ï¸ Borrar ]    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Botones:** Editar · Borrar

### Comentario â€” Variante ajena

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ ðŸ‘¤ @otro_usuario · Hace 1 hora   â”‚
â”‚ "Excelente foto, ¿dónde fue?"   â”‚
â”‚ [ ðŸ’¬ Responder ]  [ ðŸš© Reportar]â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Botones:** Responder · Reportar

---

## NIVEL 4: Estados de sincronización (distintivos)

### Distintivo de estado en observación

**Ubicación:** Esquina inferior derecha de la tarjeta de observación (para RF-13)

| Estado | Icono | Color | Significado |
|--------|-------|-------|------------|
| LOCAL | ðŸ’¾ | #CCCCCC (gris claro) | Guardada localmente, no sincronizada aàºn |
| EN_COLA | â³ | #FFC107 (ámbar) | Esperando sincronización |
| SINCRONIZADA | âœ… | #4CAF50 (verde) | Sincronizada con servidor |
| VALIDADA | ðŸ”’ | #2196F3 (azul) | Validada por experto (fuera de sprint) |

**Tamaño:** 20à—20pt, ubicado en (145, 170) respecto a la esquina superior izquierda de la tarjeta

**Comportamiento:** 
- Tooltip al pasar el dedo: "Sincronizada a las 14:32"
- Tap: Abre pop-up con detalles de sincronización

---

## NIVEL 5: Vistas complejas

### Resultado del análisis â€” Caso open-set (no registrada)

**Cuándo aparece:** BioCLIP genera embedding, open-set rechaza a umbral, la especie no está en el catálogo

**Estructura:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚        Resultado del análisis                â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  âš ï¸ Especie no registrada en el catálogo    â”‚  (título 20pt)
â”‚                                              â”‚
â”‚  Mejor coincidencia: GÉNERO Dendropsophus  â”‚  (15pt)
â”‚  Confianza: 67%                              â”‚
â”‚                                              â”‚
â”‚  Las 28 especies del catálogo actual no     â”‚  (descripción 15pt)
â”‚  incluyen esta. Podría ser:                  â”‚
â”‚  â€¢ Una especie nueva para la región          â”‚
â”‚  â€¢ Una especie muy rara                      â”‚
â”‚  â€¢ Merece un segundo análisis                â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  [Ver detalles de análisis]                  â”‚  (expandible)
â”‚  â€¢ Segmentación: 95%                         â”‚
â”‚  â€¢ Similitud de contexto geográfico: 12%     â”‚
â”‚  â€¢ Audio (si hay): No coincide               â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  [ Editar y reenviar ]  [ Guardar igual ]   â”‚  (60pt botones)
â”‚  [ Volver atrás ]                            â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Botones:**
- `Editar y reenviar`: Regresa a Paso 4, permite cambiar foto/audio
- `Guardar igual`: Guarda con etiqueta "GENERO" en lugar de especie específica
- `Volver atrás`: Regresa al listado sin guardar

---

### Ficha de especie â€” Cuatro pestañas técnicas

**Requisito:** RF-10 (ficha técnica completa)

**Ubicación:** Accesible desde "Detalles de observación" o desde "Explorar â†’ Especies"

**Barra de secciones:** Desplazable horizontalmente (HorizontalPager o LazyRow)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ [Recuento] [Morfología] [Bioacàºstica]   â”‚  (tabs desplazables)
â”‚             [Ecología]                  â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Contenido de la pestaña activa...       â”‚
â”‚ [Descripción larga, imágenes, datos]    â”‚
â”‚                                         â”‚
â”‚ [Mostrar más]                           â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

#### Pestaña 1: Recuento (ya existe)
- Carrusel de fotos
- àrbol taxonómico
- Estadísticas de capturas (nàºmero de registros)

#### Pestaña 2: Morfología

**Contenido:**
- **Tamaño:** Rango de longitud rostro-cloaca (mm), con diagrama
- **Peso:** Rango en gramos
- **Coloración:** Descripción + mini-galería de patrones dorsales/ventrales
- **Crestas y membranas:** Presencia/ausencia, con etiquetas anatómicas
- **Reproducción:** Amplexo tipo (axial/inguinal), tamaño de huevo
- **Dimorfismo sexual:** Descripción y fotos comparativas
- **Fuente:** Referencia bibliográfica o link a Amphibiaweb/IUCN

**Estructura de UI:**
```
Cada atributo morfológico:
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ ðŸ“ Tamaño (LSC)            â”‚  (icono + label)
â”‚ 18â€“25 mm                   â”‚  (valor)
â”‚ [Mostrar diagrama]         â”‚  (botón expandible)
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [Diagrama de medida LSC]   â”‚  (imagen expandida)
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

#### Pestaña 3: Bioacàºstica

**Contenido:**
- **Tipo de canto:** Reproducción, territorial, cortejo
- **Frecuencia dominante:** Rango en Hz con espectrograma
- **Duración de nota:** Milisegundos, con waveform
- **Tasa de repetición:** Notas/segundo
- **Ejemplo de audio:** Widget de reproducción (botón play, barra de progreso)
- **Contexto temporal:** Cuándo canta (época del año, hora del día)

**Estructura de UI:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ ðŸŽµ Canto de reproducción   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [â–¶ï¸ Reproducir ejemplo]    â”‚  (botón play)
â”‚ â–“â–“â–“â–‘â–‘â–‘â–‘â–‘  0:45 / 1:20     â”‚  (barra de progreso)
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Frecuencia dominante       â”‚
â”‚ 800â€“1200 Hz                â”‚  (valor)
â”‚ [Mostrar espectrograma]    â”‚  (expandible)
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [Espectrograma real]       â”‚  (imagen)
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

#### Pestaña 4: Ecología

**Contenido:**
- **Hábitat:** Tipos de ecosistema (bosque hàºmedo, sabana, etc.), altitud (msnm)
- **Microhábitat:** Dosel, sotobosque, suelo, agua
- **Actividad:** Nocturno, diurno, crepuscular
- **Reproducción:** Tipo de amplexo, lugar de reproducción (charco, arroyo, árbol)
- **Dieta:** Qué come (insectos, otros anuros, etc.)
- **Distribución:** Mapa simplificado de rango geográfico
- **Amenazas:** Pérdida de hábitat, hongos, contaminación
- **Estado IUCN:** Categoría con icono

**Estructura de UI:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ ðŸŒ³ Hábitat                 â”‚
â”‚ Bosque hàºmedo 800â€“1800m    â”‚  (valor + rango altitud)
â”‚ [Mapa simplificado]        â”‚  (expandible)
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ðŸ—ºï¸ Distribución            â”‚
â”‚ [Mapa de rango]            â”‚  (imagen de distribución)
â”‚ Colombia (endemismo regional)
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ðŸ”´ Estado IUCN             â”‚
â”‚ Vulnerable (VU)            â”‚  (icono + categoría)
â”‚ [Ver en IUCN Red List]     â”‚  (link externo)
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

### Sección "Mis publicaciones" (con variantes pàºblica/privada)

**Ubicación:** En el perfil propio (no en ajena)

**Estructura:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Mis observaciones                 â”‚
â”‚ [ðŸ“Œ Todas] [ðŸŒ Pàºblicas] [ðŸ”’ Privadas]
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [ Listado de tarjetas ]           â”‚
â”‚                                   â”‚
â”‚ [ Botón de compartir/visibilidad] â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Pestañas:**
- **Todas:** Muestra pàºblicas + privadas (solo tàº ves esto)
- **Pàºblicas:** Visibles para otros usuarios
- **Privadas:** Solo tàº las ves (marcadas con ðŸ”’)

**Pop-up de visibilidad:**

Cuando el usuario guarda una observación nueva, aparece:
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Visibilidad de la observación    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ â—‹ Privada (solo tàº)             â”‚  (seleccionable)
â”‚ â—‹ Pàºblica                        â”‚  (seleccionable)
â”‚                                  â”‚
â”‚ Las pàºblicas ayudan a otros a    â”‚
â”‚ aprender; la ubicación exacta    â”‚
â”‚ se ofusca para especies          â”‚
â”‚ amenazadas.                      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [ Guardar como privada ]         â”‚  (60pt botones)
â”‚ [ Guardar como pàºblica ]         â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## Trazabilidad de requisitos completados

| Req | Nivel | Componente | Estado |
|-----|-------|-----------|--------|
| RF-04 | 1 | Campos de altitud + ecosistema | âœ… Especificado |
| RF-13 | 4 | Distintivos de sincronización | âœ… Especificado |
| RNF-06 | 1 | Botón "Omitir" en pasos | âœ… Especificado |
| RNF-14 | 2 | Pop-ups de permisos (3) | âœ… Especificado |
| HU-01 caso 2 | 2 | Pop-up de foto borrosa | âœ… Especificado |
| HU-02 caso 3 | 4 | Resultado open-set | âœ… Especificado |
| RF-10 | 5 | Cuatro pestañas de ficha | âœ… Especificado |
| § Variantes | 3 | Propio vs. ajeno (4 elementos) | âœ… Especificado |

---

## Guía de implementación en Compose

### Patrón para reutilizar componentes

```kotlin
// Componente genérico de tarjeta de observación
@Composable
fun ObservationCard(
    observation: Observacion,
    isOwn: Boolean,  // true = variante propia, false = ajena
    onEdit: () -> Unit,
    onDelete: () -> Unit,
    onComment: () -> Unit,
    onLike: () -> Unit
) {
    // Renderiza diferente segàºn isOwn
    if (isOwn) {
        // Botones: Editar, Eliminar
    } else {
        // Botones: Comentar, Apoyar, Reportar
    }
}
```

### Patrón para pop-ups de permisos

```kotlin
// Genérico para cualquier permiso
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

**Cuándo aparece:** Usuario presiona "Cerrar salida" en una sesión de campo activa

**Pantalla previa: Salida de campo en curso**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Salida de campo: Páramo La Breña â”‚
â”‚ Iniciada: 14:30 · Duración: 4h   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ðŸ“Š Resumen                       â”‚
â”‚ Observaciones: 12                â”‚  (nàºmero de registros)
â”‚ Especies: 7                      â”‚
â”‚ Ubicaciones àºnicas: 8            â”‚
â”‚ Audio capturado: 340 MB          â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [Editar detalles] [Mostrar mapa] â”‚
â”‚                                  â”‚
â”‚ [Cerrar salida]                  â”‚  (botón 60pt)
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Pop-up de cierre:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Cerrar salida de campo           â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ âœ… 12 observaciones registradas  â”‚
â”‚ âœ… 7 especies àºnicas             â”‚
â”‚ âœ… Fecha: 07 sep 2026            â”‚
â”‚ âœ… Duración: 4 horas 23 minutos  â”‚
â”‚ âš ï¸  10 observaciones sin audio    â”‚
â”‚                                  â”‚
â”‚ ¿Quieres hacerla pàºblica?        â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [ Privada ]  [ Pàºblica ]         â”‚  (60pt botones)
â”‚ [ Editar notas ]                 â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Estados finales:**
- **Privada:** Guardada en dispositivo, solo visible para tí
- **Pàºblica:** Sincronizada con servidor, contribuye a mapa comunitario
- **Editar notas:** Abre campo de texto para agregar observaciones (contexto, condiciones climáticas, equipo)

**Persistencia:**
- La salida queda en el historial
- Accesible desde "Mis salidas de campo" en perfil
- Exportable como Darwin Core (Etapa 2, post-27 sep)

---

## Siguientes pasos

1. **HILO DE VALIDACIà“N:** Revisar esta especificación en Penpot, confirmar medidas y colores
2. **IMPLEMENTACIà“N:** Pasar cada nivel a Compose siguiendo los patrones de reutilización
3. **TESTING:** Verificar variantes propio/ajeno en dispositivo real antes de mergear



