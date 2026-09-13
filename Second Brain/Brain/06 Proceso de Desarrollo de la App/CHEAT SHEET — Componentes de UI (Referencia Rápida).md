---
title: "CHEAT SHEET â€” Componentes de UI (Referencia RÃ¡pida)"
proyecto: Anura
tipo: referencia
estado: v1-07-sep-2026
tags: [anura, diseÃ±o, cheat-sheet, compose, kotlin, referencia-rapida]
---

# CHEAT SHEET â€” Componentes de UI (Referencia RÃ¡pida)

**Imprime esto o pinlo en tu monitor.** Fuente de verdad: [[Componentes de UI â€” EspecificaciÃ³n Detallada]]

---

## PALETA (CÃ³pialo en colors.kt)

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
| **Alto botÃ³n** | 60pt |
| **Ancho pantalla** | 393pt |
| **Alto pantalla** | 852pt |
| **Escala texto** | 25 (tÃ­tulo) Â· 20 (normal) Â· 15 (descriptivo) Â· 10 (mÃ­nimo) |

---

## COMPONENTES NUEVOS (Nivel 1 = Hoy)

### Campo numÃ©rico â€” Altitud
- **UbicaciÃ³n:** Paso 2 (metadatos)
- **Placeholder:** "Altitud (msnm)"
- **Rango:** 0â€“5000
- **Opcional:** âœ… SÃ­ (RNF-06)

```kotlin
TextField(
    value = altitud,
    onValueChange = { altitud = it.filter { c -> c.isDigit() } },
    label = { Text("Altitud (msnm)") },
    modifier = Modifier.height(60.dp)
)
```

### Selector â€” Ecosistema
- **UbicaciÃ³n:** Paso 2, bajo Altitud
- **Opciones:** Bosque Â· Agua Â· Zona abierta Â· Ãrea urbana Â· Otro
- **Opcional:** âœ… SÃ­

### BotÃ³n "Omitir"
- **UbicaciÃ³n:** Pie de cada paso (1, 2, 4)
- **Etiqueta:** "Omitir este paso"
- **Alto:** 60pt
- **Color:** #626264
- **Estado guardado:** 
ull` (no `""`)

---

## POP-UPS (Nivel 2)

### Permiso de cÃ¡mara
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ ðŸ“· Acceso a cÃ¡mara  â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Anura necesita      â”‚
â”‚ acceder a tu        â”‚
â”‚ cÃ¡mara...           â”‚
â”‚ [ Permitir ] [ No ] â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```
- **CuÃ¡ndo:** Usuario toca "Tomar foto" en Paso 4
- **Denegado:** Pop-up secundario â†’ "Abre Ajustes"

### Permiso de micrÃ³fono
- IdÃ©ntico a cÃ¡mara, pero: "ðŸŽ¤ Acceso al micrÃ³fono"

### Permiso de ubicaciÃ³n
- IdÃ©ntico, pero: "ðŸ“ Acceso a la ubicaciÃ³n"

### Foto borrosa
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ âš ï¸ Foto borrosa     â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Prueba:             â”‚
â”‚ â€¢ Acercarte mÃ¡s     â”‚
â”‚ â€¢ Limpiar lente     â”‚
â”‚ â€¢ Mejor luz         â”‚
â”‚ [ Tomar otra ]      â”‚
â”‚ [ Aceptar ]         â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```
- **CuÃ¡ndo:** Post-captura si desenfoque > umbral
- **Acciones:** Retomar Â· Guardar igual

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
- **Etapas:** SegmentaciÃ³n â†’ BioCLIP â†’ ClasificaciÃ³n â†’ Open-set

---

## VARIANTES (Nivel 3)

### ObservaciÃ³n PROPIA
```
[ Foto ]  [â¤ï¸] [âš ï¸]
Nombre comÃºn
Nombre cientÃ­fico
[ ðŸ“ Editar ] [ ðŸ—‘ï¸ Borrar ]
```

### ObservaciÃ³n AJENA
```
[ Foto ]  [ðŸ¤] [âš ï¸]
Nombre comÃºn
Nombre cientÃ­fico
@usuario Â· Hace 2h
[ ðŸ’¬ Comentar ] [ ðŸ‘ Apoyar ] [ ðŸš© Reportar ]
```

### Perfil PROPIO
- Avatar + **Editar perfil**
- Privadas â†’ **visible**
- Botones: Ajustes Â· Cerrar sesiÃ³n

### Perfil AJENO
- Avatar + **Seguir**
- Privadas â†’ **ocultas**
- Botones: Contactar Â· Reportar

### Comentario PROPIO
```
TÃº Â· Hace 1h
"Texto..."
[ âœï¸ Editar ] [ ðŸ—‘ï¸ Borrar ]
```

### Comentario AJENO
```
@usuario Â· Hace 1h
"Texto..."
[ ðŸ’¬ Responder ] [ ðŸš© Reportar ]
```

---

## DISTINTIVOS (Nivel 4)

### Estado de sincronizaciÃ³n (esquina tarjeta)
| Estado | Icono | Color | Significado |
|--------|-------|-------|------------|
| LOCAL | ðŸ’¾ | Gris | No sincronizado |
| EN_COLA | â³ | Ãmbar | Esperando |
| SINCRONIZADA | âœ… | Verde | OK servidor |
| VALIDADA | ðŸ”’ | Azul | Experto OK |

---

## CASOS ESPECIALES (Nivel 4â€“5)

### Open-set: No registrada
```
âš ï¸ Especie no registrada
Mejor: GÃ©nero Dendropsophus (67%)
[ Ver detalles ]
[ Editar ] [ Guardar igual ]
```

### Ficha de especie: 4 pestaÃ±as
1. **Recuento** â€” Fotos, Ã¡rbol, estadÃ­sticas
2. **MorfologÃ­a** â€” TamaÃ±o, coloraciÃ³n, dimorfismo
3. **BioacÃºstica** â€” Canto, Hz, espectrograma, ejemplo audio
4. **EcologÃ­a** â€” HÃ¡bitat, distribuciÃ³n, amenazas, IUCN

### Mis observaciones: Visibilidad
- **Pop-up al guardar:**
  ```
  â—‹ Privada (solo tÃº)
  â—‹ PÃºblica
  [ Guardar privada ] [ Guardar pÃºblica ]
  ```

### Salida de campo: Cierre
```
âœ… 12 observaciones
âœ… 7 especies
âš ï¸ 10 sin audio
Â¿Privada o pÃºblica?
[ Editar notas ]
```

---

## PATRONES DE CÃ“DIGO

### Componente con variante propio/ajeno

```kotlin
@Composable
fun ObservationCard(
    obs: Observacion,
    isOwn: Boolean
) {
    Column {
        // Encabezado comÃºn
        
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

### Pop-up de permiso genÃ©rico

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

## CHECKLIST DE IMPLEMENTACIÃ“N

- [ ] Paso 2: Altitud + Ecosistema + Omitir
- [ ] Pop-up: Permisos (3)
- [ ] Pop-up: Foto borrosa
- [ ] Pop-up: Analizando con progreso
- [ ] Tarjeta observaciÃ³n: variante propia + ajena
- [ ] Perfil: variante propia + ajena
- [ ] Comentario: variante propia + ajena
- [ ] Distintivo: Estado de sincronizaciÃ³n
- [ ] Resultado: Open-set
- [ ] Ficha: 4 pestaÃ±as (Recuento, Morfo, Bio, Eco)
- [ ] Perfil: "Mis publicaciones" con privada/pÃºblica
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
- Guardar estado de sincronizaciÃ³n antes de pop-up de anÃ¡lisis
- Testear variantes propio/ajeno con dos usuarios reales

---

## REFERENCIAS NORMATIVAS

| Req | Componente |
|-----|-----------|
| RF-04 | Altitud, Ecosistema |
| RF-10 | 4 pestaÃ±as ficha |
| RF-13 | Distintivos de sincronizaciÃ³n |
| RNF-06 | BotÃ³n "Omitir" |
| RNF-14 | Pop-ups de permisos |
| HU-01 caso 2 | Pop-up foto borrosa |
| HU-02 caso 3 | Resultado open-set |
| HU-04 | Resumen salida de campo |

**Fuente de verdad:** [[Componentes de UI â€” EspecificaciÃ³n Detallada]]



