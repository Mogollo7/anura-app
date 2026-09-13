---
title: "ÃNDICE DE DISEÃ‘O â€” Sprint 27 Sep"
proyecto: Anura
tipo: Ã­ndice
estado: v1-07-sep-2026
tags: [anura, diseÃ±o, Ã­ndice, sprint-prototipo, penpot, composable]
---

# ÃNDICE DE DISEÃ‘O â€” Sprint 27 Sep

**NavegaciÃ³n centralizada de todos los documentos de diseÃ±o e implementaciÃ³n para el prototipo del 27 de septiembre.**

---

## Documentos principales

| Documento | PropÃ³sito | Acceso | Ãšltima actualizaciÃ³n |
|-----------|----------|--------|---------------------|
| [[DiseÃ±o de Interfaz (Penpot)]] | EspecificaciÃ³n de wireframe, componentes, navegaciÃ³n | Penpot (42 boards) | 2026-09-07 |
| [[Componentes de UI â€” EspecificaciÃ³n Detallada]] | TraducciÃ³n tÃ©cnica a Compose: medidas, colores, estados | ðŸ“– Documento (niveles 1â€“5) | 2026-09-07 |
| [[CHEAT SHEET â€” Componentes de UI (Referencia RÃ¡pida)]] | Resumen imprimible para desarrolladores | ðŸ–¨ï¸ Tira rÃ¡pida | 2026-09-07 |
| [[Sistema de Estilos HIG â€” Refactor de Paleta y ElevaciÃ³n]] | Paleta, contraste, sombras, radios, tipografÃ­a y modo Luz roja | ðŸŽ¨ Tokens + CSS | 2026-09-08 |

---

## QuÃ© se completÃ³ hoy (07 sep)

### Nivel 1: Campos y validaciÃ³n (sin interacciÃ³n compleja)
- âœ… **Altitud (msnm):** Campo numÃ©rico 0â€“5000, opcional
- âœ… **Ecosistema:** Selector (Bosque, Agua, Zona abierta, Ãrea urbana, Otro)
- âœ… **BotÃ³n "Omitir":** PatrÃ³n para Pasos 1, 2, 4 (RNF-06)
- âœ… **Modo luz roja:** ~~trabajo futuro~~ â†’ **construido el 08-sep** como tema completo (tokens + 2 boards). Ver [[Sistema de Estilos HIG â€” Refactor de Paleta y ElevaciÃ³n]]

### Nivel 2: Pop-ups de sistema y feedback
- âœ… **Permiso de cÃ¡mara:** Pop-up con manejo de denegaciÃ³n â†’ Ajustes
- âœ… **Permiso de micrÃ³fono:** IdÃ©ntico a cÃ¡mara
- âœ… **Permiso de ubicaciÃ³n:** IdÃ©ntico a cÃ¡mara
- âœ… **Foto borrosa:** Pop-up de advertencia + "Tomar de nuevo" / "Aceptar"
- âœ… **Analizando (progreso):** Modal con 4 etapas (Seg. â†’ ID â†’ AnÃ¡lisis â†’ Audio)

### Nivel 3: Variantes de contexto (propio vs. ajeno)
- âœ… **Tarjeta de observaciÃ³n (2 variantes):** Propia (Editar, Borrar) + Ajena (Comentar, Apoyar, Reportar)
- âœ… **Perfil (2 variantes):** Propio (Editar, Privadas, Ajustes) + Ajeno (Seguir, Sin privadas, Reportar)
- âœ… **Comentario (2 variantes):** Propio (Editar, Borrar) + Ajeno (Responder, Reportar)
- âœ… **Estados de sincronizaciÃ³n:** Distintivo 20Ã—20pt (LOCAL, EN_COLA, SINCRONIZADA, VALIDADA)

### Nivel 4: AnÃ¡lisis y bÃºsqueda
- âœ… **Resultado open-set:** "Especie no registrada" â†’ Mejor coincidencia a nivel gÃ©nero
- âœ… **Acciones:** Editar/Reenviar Â· Guardar igual Â· Volver

### Nivel 5: Vistas complejas y gestiÃ³n de datos
- âœ… **Ficha de especie (4 pestaÃ±as):**
  - Recuento (fotos, Ã¡rbol taxonÃ³mico, estadÃ­sticas)
  - MorfologÃ­a (tamaÃ±o, coloraciÃ³n, dimorfismo, crestas)
  - BioacÃºstica (tipo de canto, Hz, espectrograma, ejemplo audio)
  - EcologÃ­a (hÃ¡bitat, distribuciÃ³n, amenazas, IUCN)
- âœ… **Mis publicaciones:** PestaÃ±as (Todas, PÃºblicas, Privadas)
- âœ… **Pop-up de visibilidad:** Privada/PÃºblica al guardar observaciÃ³n
- âœ… **Salida de campo (cierre):** Resumen + pop-up de confirmaciÃ³n Privada/PÃºblica

---

## Trazabilidad de requisitos

### Requisitos funcionales (RF)
| RF | DescripciÃ³n | Componente(s) | Estado |
|----|------------|--------------|--------|
| RF-04 | Captura de metadatos (altitud, ecosistema) | Nivel 1: Campos en Paso 2 | âœ… |
| RF-10 | Ficha tÃ©cnica completa | Nivel 5: 4 pestaÃ±as | âœ… |
| RF-13 | SincronizaciÃ³n diferida (estados) | Nivel 3: Distintivos | âœ… |

### Requisitos no funcionales (RNF)
| RNF | DescripciÃ³n | Componente(s) | Estado |
|-----|-----------|--------------|--------|
| RNF-06 | Tolerancia a datos faltantes ("Omitir") | Nivel 1: BotÃ³n Omitir | âœ… |
| RNF-14 | Permisos en el momento de uso | Nivel 2: 3 Pop-ups | âœ… |

### Historias de usuario (HU)
| HU | DescripciÃ³n | Componente(s) | Estado |
|----|-----------|--------------|--------|
| HU-01 caso 2 | Captura con foto borrosa | Nivel 2: Pop-up + acciones | âœ… |
| HU-02 caso 3 | Especie no registrada (open-set) | Nivel 4: Resultado open-set | âœ… |
| HU-04 | Salidas de campo comunitarias | Nivel 5: Cierre + privada/pÃºblica | âœ… |

---

## CÃ³mo usar estos documentos

### Para diseÃ±adores en Penpot
1. Leer [[DiseÃ±o de Interfaz (Penpot)]] Â§7.2 "POR HACER"
2. Crear/actualizar boards para niveles 2â€“5
3. Validar medidas contra [[Componentes de UI â€” EspecificaciÃ³n Detallada]] Â§Medidas fijas
4. Usar paleta: [[Componentes de UI â€” EspecificaciÃ³n Detallada]] Â§PALETA

### Para desarrolladores en Kotlin/Compose
1. **Primera vez:** Leer [[CHEAT SHEET â€” Componentes de UI (Referencia RÃ¡pida)]] (5 min)
2. **Implementando Paso 2:** Consultar [[Componentes de UI â€” EspecificaciÃ³n Detallada]] Â§NIVEL 1 (campos)
3. **Implementando pop-ups:** Consultar [[Componentes de UI â€” EspecificaciÃ³n Detallada]] Â§NIVEL 2
4. **Implementando variantes:** Consultar [[Componentes de UI â€” EspecificaciÃ³n Detallada]] Â§NIVEL 3
5. **Casos especiales:** Consultar [[Componentes de UI â€” EspecificaciÃ³n Detallada]] Â§NIVEL 4â€“5

---

## Patrones reutilizables (copy-paste en Compose)

Todos estÃ¡n en [[Componentes de UI â€” EspecificaciÃ³n Detallada]] Â§GuÃ­a de implementaciÃ³n en Compose

- `ObservationCard(isOwn: Boolean)` â€” Tarjeta propia vs. ajena
- `PermissionRequestBottomSheet()` â€” Pop-up genÃ©rico de permisos
- `ActionButtons()` â€” Botones contextuales (Editar/Borrar vs. Comentar/Apoyar)

---

## PrÃ³ximos pasos de diseÃ±o

| Paso | Responsable | Fecha | DescripciÃ³n |
|------|------------|-------|------------|
| 1 | DiseÃ±o | 08 sep | *(Opcional)* Crear boards faltantes en Penpot (niveles 2â€“5) para aprobaciÃ³n visual |
| 2 | Desarrollo | 08â€“18 sep | Implementar componentes en Kotlin siguiendo esta especificaciÃ³n |
| 3 | Testing | 19â€“24 sep | Verificar variantes propio/ajeno en dispositivo real |
| 4 | QA | 24â€“26 sep | Pulir UI, revisar temas oscuro/claro, one-hand controls |

---

## Preguntas frecuentes de implementaciÃ³n

**P: Â¿Debo crear cada pop-up como un composable separado?**
R: No. Usa un `PermissionRequestBottomSheet()` genÃ©rico con parÃ¡metros (tÃ­tulo, descripciÃ³n, icono, permiso).

**P: Â¿QuÃ© pasa si el usuario niega un permiso?**
R: Mostrar pop-up secundario "Permiso denegado" â†’ BotÃ³n "Abre Ajustes" â†’ `startActivity(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)`

**P: Â¿Los campos "Omitir" deben guardar 
ull` o `""`?**
R: **
ull`** â€” la validaciÃ³n post-anÃ¡lisis debe distinguir "usuario eligiÃ³ omitir" de "usuario no llenÃ³ campo".

**P: Â¿CÃ³mo renderizo 4 pestaÃ±as de ficha en Compose?**
R: Usa `HorizontalPager` o `LazyRow` de `androidx.compose.foundation.pager`, con indicador en la barra.

**P: Â¿La variante "ajena" de perfil oculta botones o mostrar botones diferentes?**
R: **Muestra botones diferentes.** No uses `.visible = false` (mala UX). CondiciÃ³n: `if (isOwn) { ... } else { ... }`

---

## ActualizaciÃ³n del cronograma

**07 sep (Lun):** EspecificaciÃ³n de componentes completada (niveles 1â€“5).
**08 sep (Mar):** LÃ­nea base del modelo + script CVATâ†’YOLO.
**09 sep (MiÃ©):** Llegada datos de segmentaciÃ³n (cuello de botella H4).

---

## Contacto y validaciÃ³n

- **Dudas sobre especificaciÃ³n:** Consultar [[Componentes de UI â€” EspecificaciÃ³n Detallada]]
- **Dudas de diseÃ±o en Penpot:** Consultar [[DiseÃ±o de Interfaz (Penpot)]]
- **Dudas de implementaciÃ³n:** Consultar [[CHEAT SHEET â€” Componentes de UI (Referencia RÃ¡pida)]]
- **Errores encontrados:** Actualizar secciÃ³n de "Errores comunes" en CHEAT SHEET

---

Generado: 2026-09-07 | Fuente de verdad: [[Componentes de UI â€” EspecificaciÃ³n Detallada]]



