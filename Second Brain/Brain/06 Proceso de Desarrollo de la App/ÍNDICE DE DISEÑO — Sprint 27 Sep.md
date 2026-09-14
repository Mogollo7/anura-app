---
title: "àNDICE DE DISEà‘O â€” Sprint 27 Sep"
proyecto: Anura
tipo: índice
estado: v1-07-sep-2026
tags: [anura, diseño, índice, sprint-prototipo, penpot, composable]
---

# àNDICE DE DISEà‘O â€” Sprint 27 Sep

**Navegación centralizada de todos los documentos de diseño e implementación para el prototipo del 27 de septiembre.**

---

## Documentos principales

| Documento | Propósito | Acceso | àšltima actualización |
|-----------|----------|--------|---------------------|
| [[Diseño de Interfaz (Penpot)]] | Especificación de wireframe, componentes, navegación | Penpot (42 boards) | 2026-09-07 |
| [[Componentes de UI â€” Especificación Detallada]] | Traducción técnica a Compose: medidas, colores, estados | ðŸ“– Documento (niveles 1â€“5) | 2026-09-07 |
| [[CHEAT SHEET â€” Componentes de UI (Referencia Rápida)]] | Resumen imprimible para desarrolladores | ðŸ–¨ï¸ Tira rápida | 2026-09-07 |
| [[Sistema de Estilos HIG â€” Refactor de Paleta y Elevación]] | Paleta, contraste, sombras, radios, tipografía y modo Luz roja | ðŸŽ¨ Tokens + CSS | 2026-09-08 |

---

## Qué se completó hoy (07 sep)

### Nivel 1: Campos y validación (sin interacción compleja)
- âœ… **Altitud (msnm):** Campo numérico 0â€“5000, opcional
- âœ… **Ecosistema:** Selector (Bosque, Agua, Zona abierta, àrea urbana, Otro)
- âœ… **Botón "Omitir":** Patrón para Pasos 1, 2, 4 (RNF-06)
- âœ… **Modo luz roja:** ~~trabajo futuro~~ â†’ **construido el 08-sep** como tema completo (tokens + 2 boards). Ver [[Sistema de Estilos HIG â€” Refactor de Paleta y Elevación]]

### Nivel 2: Pop-ups de sistema y feedback
- âœ… **Permiso de cámara:** Pop-up con manejo de denegación â†’ Ajustes
- âœ… **Permiso de micrófono:** Idéntico a cámara
- âœ… **Permiso de ubicación:** Idéntico a cámara
- âœ… **Foto borrosa:** Pop-up de advertencia + "Tomar de nuevo" / "Aceptar"
- âœ… **Analizando (progreso):** Modal con 4 etapas (Seg. â†’ ID â†’ Análisis â†’ Audio)

### Nivel 3: Variantes de contexto (propio vs. ajeno)
- âœ… **Tarjeta de observación (2 variantes):** Propia (Editar, Borrar) + Ajena (Comentar, Apoyar, Reportar)
- âœ… **Perfil (2 variantes):** Propio (Editar, Privadas, Ajustes) + Ajeno (Seguir, Sin privadas, Reportar)
- âœ… **Comentario (2 variantes):** Propio (Editar, Borrar) + Ajeno (Responder, Reportar)
- âœ… **Estados de sincronización:** Distintivo 20à—20pt (LOCAL, EN_COLA, SINCRONIZADA, VALIDADA)

### Nivel 4: Análisis y bàºsqueda
- âœ… **Resultado open-set:** "Especie no registrada" â†’ Mejor coincidencia a nivel género
- âœ… **Acciones:** Editar/Reenviar · Guardar igual · Volver

### Nivel 5: Vistas complejas y gestión de datos
- âœ… **Ficha de especie (4 pestañas):**
  - Recuento (fotos, árbol taxonómico, estadísticas)
  - Morfología (tamaño, coloración, dimorfismo, crestas)
  - Bioacàºstica (tipo de canto, Hz, espectrograma, ejemplo audio)
  - Ecología (hábitat, distribución, amenazas, IUCN)
- âœ… **Mis publicaciones:** Pestañas (Todas, Pàºblicas, Privadas)
- âœ… **Pop-up de visibilidad:** Privada/Pàºblica al guardar observación
- âœ… **Salida de campo (cierre):** Resumen + pop-up de confirmación Privada/Pàºblica

---

## Trazabilidad de requisitos

### Requisitos funcionales (RF)
| RF | Descripción | Componente(s) | Estado |
|----|------------|--------------|--------|
| RF-04 | Captura de metadatos (altitud, ecosistema) | Nivel 1: Campos en Paso 2 | âœ… |
| RF-10 | Ficha técnica completa | Nivel 5: 4 pestañas | âœ… |
| RF-13 | Sincronización diferida (estados) | Nivel 3: Distintivos | âœ… |

### Requisitos no funcionales (RNF)
| RNF | Descripción | Componente(s) | Estado |
|-----|-----------|--------------|--------|
| RNF-06 | Tolerancia a datos faltantes ("Omitir") | Nivel 1: Botón Omitir | âœ… |
| RNF-14 | Permisos en el momento de uso | Nivel 2: 3 Pop-ups | âœ… |

### Historias de usuario (HU)
| HU | Descripción | Componente(s) | Estado |
|----|-----------|--------------|--------|
| HU-01 caso 2 | Captura con foto borrosa | Nivel 2: Pop-up + acciones | âœ… |
| HU-02 caso 3 | Especie no registrada (open-set) | Nivel 4: Resultado open-set | âœ… |
| HU-04 | Salidas de campo comunitarias | Nivel 5: Cierre + privada/pàºblica | âœ… |

---

## Cómo usar estos documentos

### Para diseñadores en Penpot
1. Leer [[Diseño de Interfaz (Penpot)]] §7.2 "POR HACER"
2. Crear/actualizar boards para niveles 2â€“5
3. Validar medidas contra [[Componentes de UI â€” Especificación Detallada]] §Medidas fijas
4. Usar paleta: [[Componentes de UI â€” Especificación Detallada]] §PALETA

### Para desarrolladores en Kotlin/Compose
1. **Primera vez:** Leer [[CHEAT SHEET â€” Componentes de UI (Referencia Rápida)]] (5 min)
2. **Implementando Paso 2:** Consultar [[Componentes de UI â€” Especificación Detallada]] §NIVEL 1 (campos)
3. **Implementando pop-ups:** Consultar [[Componentes de UI â€” Especificación Detallada]] §NIVEL 2
4. **Implementando variantes:** Consultar [[Componentes de UI â€” Especificación Detallada]] §NIVEL 3
5. **Casos especiales:** Consultar [[Componentes de UI â€” Especificación Detallada]] §NIVEL 4â€“5

---

## Patrones reutilizables (copy-paste en Compose)

Todos están en [[Componentes de UI â€” Especificación Detallada]] §Guía de implementación en Compose

- `ObservationCard(isOwn: Boolean)` â€” Tarjeta propia vs. ajena
- `PermissionRequestBottomSheet()` â€” Pop-up genérico de permisos
- `ActionButtons()` â€” Botones contextuales (Editar/Borrar vs. Comentar/Apoyar)

---

## Próximos pasos de diseño

| Paso | Responsable | Fecha | Descripción |
|------|------------|-------|------------|
| 1 | Diseño | 08 sep | *(Opcional)* Crear boards faltantes en Penpot (niveles 2â€“5) para aprobación visual |
| 2 | Desarrollo | 08â€“18 sep | Implementar componentes en Kotlin siguiendo esta especificación |
| 3 | Testing | 19â€“24 sep | Verificar variantes propio/ajeno en dispositivo real |
| 4 | QA | 24â€“26 sep | Pulir UI, revisar temas oscuro/claro, one-hand controls |

---

## Preguntas frecuentes de implementación

**P: ¿Debo crear cada pop-up como un composable separado?**
R: No. Usa un `PermissionRequestBottomSheet()` genérico con parámetros (título, descripción, icono, permiso).

**P: ¿Qué pasa si el usuario niega un permiso?**
R: Mostrar pop-up secundario "Permiso denegado" â†’ Botón "Abre Ajustes" â†’ `startActivity(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)`

**P: ¿Los campos "Omitir" deben guardar 
ull` o `""`?**
R: **
ull`** â€” la validación post-análisis debe distinguir "usuario eligió omitir" de "usuario no llenó campo".

**P: ¿Cómo renderizo 4 pestañas de ficha en Compose?**
R: Usa `HorizontalPager` o `LazyRow` de `androidx.compose.foundation.pager`, con indicador en la barra.

**P: ¿La variante "ajena" de perfil oculta botones o mostrar botones diferentes?**
R: **Muestra botones diferentes.** No uses `.visible = false` (mala UX). Condición: `if (isOwn) { ... } else { ... }`

---

## Actualización del cronograma

**07 sep (Lun):** Especificación de componentes completada (niveles 1â€“5).
**08 sep (Mar):** Línea base del modelo + script CVATâ†’YOLO.
**09 sep (Mié):** Llegada datos de segmentación (cuello de botella H4).

---

## Contacto y validación

- **Dudas sobre especificación:** Consultar [[Componentes de UI â€” Especificación Detallada]]
- **Dudas de diseño en Penpot:** Consultar [[Diseño de Interfaz (Penpot)]]
- **Dudas de implementación:** Consultar [[CHEAT SHEET â€” Componentes de UI (Referencia Rápida)]]
- **Errores encontrados:** Actualizar sección de "Errores comunes" en CHEAT SHEET

---

Generado: 2026-09-07 | Fuente de verdad: [[Componentes de UI â€” Especificación Detallada]]



