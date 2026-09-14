---
title: "Proceso de Desarrollo â€” àndice"
proyecto: Anura
tipo: índice
tags: [anura, proceso, índice]
---

# Proceso de Desarrollo â€” àndice

[[Anura â€” àndice General]]

Cómo se construye la aplicación móvil Anura: qué se hace, en qué orden, con qué tecnologías y bajo qué criterios.

## Notas

| Nota | Responde a | Actualización |
| --- | --- | --- |
| [[Roadmap y Fases]] | ¿Qué se hace primero y por qué? ¿Cuál es el mínimo defendible? | |
| [[Stack Tecnológico]] | ¿Con qué se construye y por qué esa elección? | |
| [[Arquitectura de la Aplicación]] | ¿Cómo se organiza el código y el dominio? | |
| [[Diseño de Interfaz (Penpot)]] | ¿Cómo se ven las pantallas y qué componentes se reutilizan? | 2026-09-07 |
| [[àNDICE DE DISEà‘O â€” Sprint 27 Sep]] | ðŸ“‘ Navegación centralizada de componentes (niveles 1â€“5 completados) | 2026-09-07 â­ NUEVO |
| [[Componentes de UI â€” Especificación Detallada]] | Traducción técnica a Compose: medidas, colores, estados, variantes | 2026-09-07 â­ NUEVO |
| [[CHEAT SHEET â€” Componentes de UI (Referencia Rápida)]] | Resumen imprimible para desarrolladores (tira rápida) | 2026-09-07 â­ NUEVO |
| [[Flujo de Datos y Sincronización]] | ¿Cómo funciona sin red y cómo se sincroniza después? | |
| [[Ciclo de Vida del Modelo (MLOps)]] | ¿Cómo se versiona, reentrena y despliega el modelo? | |
| [[Entorno de Trabajo y MCP]] | ¿Con qué herramientas se edita el diseño y qué trampas tiene? | |

## Recorrido recomendado (Sprint 27 sep)

```
1. Roadmap y Fases                 â† qué se construye y en qué orden
        â†“
2. Stack Tecnológico               â† con qué
        â†“
3. Arquitectura de la App          â† cómo se organiza
        â†“
4. Diseño de Interfaz (Penpot)     â† mockup en Penpot (42 boards)
        â†“
5. àNDICE DE DISEà‘O â­ NUEVO       â† navegación de especificaciones (niveles 1â€“5)
        â”œâ”€â†’ CHEAT SHEET (imprimible, 5 min)
        â””â”€â†’ Especificación Detallada (referencia técnica completa)
        â†“
6. Flujo de Datos                  â† cómo sobrevive sin conexión
        â†“
7. Ciclo de Vida del Modelo        â† cómo evoluciona
```

**Para desarrolladores:** Saltarse 1â€“4, empezar en paso 5 (CHEAT SHEET).

## Los cuatro principios

1. **Offline-first, no "con modo offline".** La base local es la fuente de verdad; la red es una optimización. Sin esto, la app no sirve para el caso de uso que la justifica.
2. **Extremo a extremo antes que perfecto.** El riesgo real no es un modelo con 82 % en vez de 88 %; es llegar sin app.
3. **El dato de campo es sagrado.** Se persiste antes de procesar, nunca se borra sin confirmación, y se respalda fuera del dispositivo. Es lo àºnico irreemplazable del proyecto.
4. **Medir antes de optimizar.** Casi todas las intuiciones sobre qué es lento o qué mejora la precisión resultan equivocadas.

## Dónde encaja con el resto de la bóveda

| Necesitasâ€¦ | Ve a |
| --- | --- |
| Requisitos que la app debe cumplir | [[Objetivos y Alcance]] |
| Qué hace el sistema al identificar | [[Pipeline del Sistema]] |
| Detalle de los modelos | [[Modelo de Visión â€” BioCLIP]] · [[Optimización para Inferencia en Móvil]] |
| Cómo se prueba en campo | [[Evaluación en Campo Real]] |
| Qué puede salir mal | [[Riesgos del Proyecto]] |
| Qué falta decidir | [[Inconsistencias y Decisiones Pendientes]] |



