---
title: "Proceso de Desarrollo â€” Ãndice"
proyecto: Anura
tipo: Ã­ndice
tags: [anura, proceso, Ã­ndice]
---

# Proceso de Desarrollo â€” Ãndice

[[Anura â€” Ãndice General]]

CÃ³mo se construye la aplicaciÃ³n mÃ³vil Anura: quÃ© se hace, en quÃ© orden, con quÃ© tecnologÃ­as y bajo quÃ© criterios.

## Notas

| Nota | Responde a | ActualizaciÃ³n |
| --- | --- | --- |
| [[Roadmap y Fases]] | Â¿QuÃ© se hace primero y por quÃ©? Â¿CuÃ¡l es el mÃ­nimo defendible? | |
| [[Stack TecnolÃ³gico]] | Â¿Con quÃ© se construye y por quÃ© esa elecciÃ³n? | |
| [[Arquitectura de la AplicaciÃ³n]] | Â¿CÃ³mo se organiza el cÃ³digo y el dominio? | |
| [[DiseÃ±o de Interfaz (Penpot)]] | Â¿CÃ³mo se ven las pantallas y quÃ© componentes se reutilizan? | 2026-09-07 |
| [[ÃNDICE DE DISEÃ‘O â€” Sprint 27 Sep]] | ðŸ“‘ NavegaciÃ³n centralizada de componentes (niveles 1â€“5 completados) | 2026-09-07 â­ NUEVO |
| [[Componentes de UI â€” EspecificaciÃ³n Detallada]] | TraducciÃ³n tÃ©cnica a Compose: medidas, colores, estados, variantes | 2026-09-07 â­ NUEVO |
| [[CHEAT SHEET â€” Componentes de UI (Referencia RÃ¡pida)]] | Resumen imprimible para desarrolladores (tira rÃ¡pida) | 2026-09-07 â­ NUEVO |
| [[Flujo de Datos y SincronizaciÃ³n]] | Â¿CÃ³mo funciona sin red y cÃ³mo se sincroniza despuÃ©s? | |
| [[Ciclo de Vida del Modelo (MLOps)]] | Â¿CÃ³mo se versiona, reentrena y despliega el modelo? | |
| [[Entorno de Trabajo y MCP]] | Â¿Con quÃ© herramientas se edita el diseÃ±o y quÃ© trampas tiene? | |

## Recorrido recomendado (Sprint 27 sep)

```
1. Roadmap y Fases                 â† quÃ© se construye y en quÃ© orden
        â†“
2. Stack TecnolÃ³gico               â† con quÃ©
        â†“
3. Arquitectura de la App          â† cÃ³mo se organiza
        â†“
4. DiseÃ±o de Interfaz (Penpot)     â† mockup en Penpot (42 boards)
        â†“
5. ÃNDICE DE DISEÃ‘O â­ NUEVO       â† navegaciÃ³n de especificaciones (niveles 1â€“5)
        â”œâ”€â†’ CHEAT SHEET (imprimible, 5 min)
        â””â”€â†’ EspecificaciÃ³n Detallada (referencia tÃ©cnica completa)
        â†“
6. Flujo de Datos                  â† cÃ³mo sobrevive sin conexiÃ³n
        â†“
7. Ciclo de Vida del Modelo        â† cÃ³mo evoluciona
```

**Para desarrolladores:** Saltarse 1â€“4, empezar en paso 5 (CHEAT SHEET).

## Los cuatro principios

1. **Offline-first, no "con modo offline".** La base local es la fuente de verdad; la red es una optimizaciÃ³n. Sin esto, la app no sirve para el caso de uso que la justifica.
2. **Extremo a extremo antes que perfecto.** El riesgo real no es un modelo con 82 % en vez de 88 %; es llegar sin app.
3. **El dato de campo es sagrado.** Se persiste antes de procesar, nunca se borra sin confirmaciÃ³n, y se respalda fuera del dispositivo. Es lo Ãºnico irreemplazable del proyecto.
4. **Medir antes de optimizar.** Casi todas las intuiciones sobre quÃ© es lento o quÃ© mejora la precisiÃ³n resultan equivocadas.

## DÃ³nde encaja con el resto de la bÃ³veda

| Necesitasâ€¦ | Ve a |
| --- | --- |
| Requisitos que la app debe cumplir | [[Objetivos y Alcance]] |
| QuÃ© hace el sistema al identificar | [[Pipeline del Sistema]] |
| Detalle de los modelos | [[Modelo de VisiÃ³n â€” BioCLIP]] Â· [[OptimizaciÃ³n para Inferencia en MÃ³vil]] |
| CÃ³mo se prueba en campo | [[EvaluaciÃ³n en Campo Real]] |
| QuÃ© puede salir mal | [[Riesgos del Proyecto]] |
| QuÃ© falta decidir | [[Inconsistencias y Decisiones Pendientes]] |



