---
title: "CHEAT SHEET â€” Componentes de UI (Referencia Rápida)"
proyecto: Anura
tipo: referencia
estado: v1-07-sep-2026
tags: [anura, diseño, cheat-sheet, compose, kotlin, referencia-rapida]
---

# CHEAT SHEET â€” Componentes de UI (Referencia Rápida)

**Imprime esto o pinlo en tu monitor.** Fuente de verdad: [[Componentes de UI â€” Especificación Detallada]]

---

## PALETA (Cópialo en colors.kt)

```kotlin
object AnuraColors {
    val Medio = Color(0xFF626264)      // Barra superior, botones
    val Claro = Color(0xFFB1B2B5)      // Superficies, texto
    val Oscuro = Color(0xFF373738)     // Pop-ups, estado activo
    val Imagen = Color(0xFFeeeeee)     // Placeholder de fotos
}
```

---

## MEDIDAS FIJAS

| Propiedad | Valor |
|-----------|-------|
| **Radio borde** | 30pt |
| **Alto botón** | 60pt |
| **Ancho pantalla** | 393pt |
| **Alto pantalla** | 852pt |
| **Escala texto** | 25 (título) · 20 (normal) · 15 (descriptivo) · 10 (mínimo) |

---

## COMPONENTES NUEVOS (Nivel 1 = Hoy)

### Campo numérico â€” Altitud
- **Ubicación:** Paso 2 (metadatos)
- **Placeholder:** "Altitud (msnm)"
- **Rango:** 0â€“5000
- **Opcional:** âœ… Sí (RNF-06)

```kotlin
TextField(
    value = altitud,
    onValueChange = { altitud = it.filter { c -> c.isDigit() } },
    label = { Text("Altitud (msnm)") },
    modifier = Modifier.height(60.dp)
)
```

### Selector â€” Ecosistema
- **Ubicación:** Paso 2, bajo Altitud
- **Opciones:** Bosque · Agua · Zona abierta · àrea urbana · Otro
- **Opcional:** âœ… Sí

### Botón "Omitir"
- **Ubicación:** Pie de cada paso (1, 2, 4)
- **Etiqueta:** "Omitir este paso"
- **Alto:** 60pt
- **Color:** #626264
- **Estado guardado:** 
ull` (no `""`)

---

## POP-UPS (Nivel 2)

### Permiso de cámara
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ ðŸ“· Acceso a cámara  â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Anura necesita      â”‚
â”‚ acceder a tu        â”‚
â”‚ cámara...           â”‚
â”‚ [ Permitir ] [ No ] â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```
- **Cuándo:** Usuario toca "Tomar foto" en Paso 4
- **Denegado:** Pop-up secundario â†’ "Abre Ajustes"

### Permiso de micrófono
- Idéntico a cámara, pero: "ðŸŽ¤ Acceso al micrófono"

### Permiso de ubicación
- Idéntico, pero: "ðŸ“ Acceso a la ubicación"

### Foto borrosa
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ âš ï¸ Foto borrosa     â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Prueba:             â”‚
â”‚ â€¢ Acercarte más     â”‚
â”‚ â€¢ Limpiar lente     â”‚
â”‚ â€¢ Mejor luz         â”‚
â”‚ [ Tomar otra ]      â”‚
â”‚ [ Aceptar ]         â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```
- **Cuándo:** Post-captura si desenfoque > umbral
- **Acciones:** Retomar · Guardar igual

### Analizando (progreso)
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Analizando...       â”‚
â”‚ Seg. 50% â–ˆâ–ˆâ–ˆ        â”‚
â”‚ ID  20% â–ˆ           â”‚
â”‚ Audio 0% â€”          â”‚
â”‚ ~3-4s               â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```
- **No cancelable**
- **Etapas:** Segmentación â†’ BioCLIP â†’ Clasificación â†’ Open-set

---

## VARIANTES (Nivel 3)

### Observación PROPIA
```
[ Foto ]  [â¤ï¸] [âš ï¸]
Nombre comàºn
Nombre científico
[ ðŸ“ Editar ] [ ðŸ—‘ï¸ Borrar ]
```

### Observación AJENA
```
[ Foto ]  [ðŸ¤] [âš ï¸]
Nombre comàºn
Nombre científico
@usuario · Hace 2h
[ ðŸ’¬ Comentar ] [ ðŸ‘ Apoyar ] [ ðŸš© Reportar ]
```

### Perfil PROPIO
- Avatar + **Editar perfil**
- Privadas â†’ **visible**
- Botones: Ajustes · Cerrar sesión

### Perfil AJENO
- Avatar + **Seguir**
- Privadas â†’ **ocultas**
- Botones: Contactar · Reportar

### Comentario PROPIO
```
Tàº · Hace 1h
"Texto..."
[ âœï¸ Editar ] [ ðŸ—‘ï¸ Borrar ]
```

### Comentario AJENO
```
@usuario · Hace 1h
"Texto..."
[ ðŸ’¬ Responder ] [ ðŸš© Reportar ]
```

---

## DISTINTIVOS (Nivel 4)

### Estado de sincronización (esquina tarjeta)
| Estado | Icono | Color | Significado |
|--------|-------|-------|------------|
| LOCAL | ðŸ’¾ | Gris | No sincronizado |
| EN_COLA | â³ | àmbar | Esperando |
| SINCRONIZADA | âœ… | Verde | OK servidor |
| VALIDADA | ðŸ”’ | Azul | Experto OK |

---

## CASOS ESPECIALES (Nivel 4â€“5)

### Open-set: No registrada
```
âš ï¸ Especie no registrada
Mejor: Género Dendropsophus (67%)
[ Ver detalles ]
[ Editar ] [ Guardar igual ]
```

### Ficha de especie: 4 pestañas
1. **Recuento** â€” Fotos, árbol, estadísticas
2. **Morfología** â€” Tamaño, coloración, dimorfismo
3. **Bioacàºstica** â€” Canto, Hz, espectrograma, ejemplo audio
4. **Ecología** â€” Hábitat, distribución, amenazas, IUCN

### Mis observaciones: Visibilidad
- **Pop-up al guardar:**
  ```
  â—‹ Privada (solo tàº)
  â—‹ Pàºblica
  [ Guardar privada ] [ Guardar pàºblica ]
  ```

### Salida de campo: Cierre
```
âœ… 12 observaciones
âœ… 7 especies
âš ï¸ 10 sin audio
¿Privada o pàºblica?
[ Editar notas ]
```

---

## PATRONES DE Cà“DIGO

### Componente con variante propio/ajeno

```kotlin
@Composable
fun ObservationCard(
    obs: Observacion,
    isOwn: Boolean
) {
    Column {
        // Encabezado comàºn
        
        if (isOwn) {
            // Botones: Editar, Eliminar
            ActionButtons(
                onEdit = {}, 
                onDelete = {}
            )
        } else {
            // Botones: Comentar, Apoyar, Reportar
            ActionButtons(
                onComment = {}, 
                onLike = {}, 
                onReport = {}
            )
        }
    }
}
```

### Pop-up de permiso genérico

```kotlin
@Composable
fun PermissionSheet(
    permission: String,
    title: String,
    description: String,
    icon: String,
    onGranted: () -> Unit
) {
    ModalBottomSheet {
        // Solicita y maneja
    }
}
```

---

## CHECKLIST DE IMPLEMENTACIà“N

- [ ] Paso 2: Altitud + Ecosistema + Omitir
- [ ] Pop-up: Permisos (3)
- [ ] Pop-up: Foto borrosa
- [ ] Pop-up: Analizando con progreso
- [ ] Tarjeta observación: variante propia + ajena
- [ ] Perfil: variante propia + ajena
- [ ] Comentario: variante propia + ajena
- [ ] Distintivo: Estado de sincronización
- [ ] Resultado: Open-set
- [ ] Ficha: 4 pestañas (Recuento, Morfo, Bio, Eco)
- [ ] Perfil: "Mis publicaciones" con privada/pàºblica
- [ ] Salida de campo: Cierre con pop-up

---

## ERRORES COMUNES

âŒ **No hacer:**
- Promediar embeddings de varias vistas (RF-02) â€” cada vista es independiente
- Mostrar privadas en perfil ajeno â€” es un agujero de seguridad
- Aceptar foto borrosa sin advertencia â€” deja huellas en dataset
- Botones con colores iguales al fondo â€” desaparecen

âœ… **Hacer:**
- Validar 
ull` separado de `""` en Paso 1, 2, 4
- Reutilizar `ActionButtons()` en todas las variantes
- Guardar estado de sincronización antes de pop-up de análisis
- Testear variantes propio/ajeno con dos usuarios reales

---

## REFERENCIAS NORMATIVAS

| Req | Componente |
|-----|-----------|
| RF-04 | Altitud, Ecosistema |
| RF-10 | 4 pestañas ficha |
| RF-13 | Distintivos de sincronización |
| RNF-06 | Botón "Omitir" |
| RNF-14 | Pop-ups de permisos |
| HU-01 caso 2 | Pop-up foto borrosa |
| HU-02 caso 3 | Resultado open-set |
| HU-04 | Resumen salida de campo |

**Fuente de verdad:** [[Componentes de UI â€” Especificación Detallada]]



