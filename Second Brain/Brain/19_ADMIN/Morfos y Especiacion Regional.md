---
title: "Morfos y Especiación Regional"
tags: [admin, anura, morfos]
created: 2026-09-25
status: draft
---

# Morfos y Especiación Regional

La apariencia no es una sola por especie, ni igual en todos los paquetes. Texto de reglas: [[Fuente - Modelo de Datos y Reglas del Admin]].

```text
Especie
├── Paquete Norte
│   ├── Morfo A
│   └── Morfo B
├── Paquete Oriente
│   └── Morfo A
└── Paquete Urabá
    ├── Morfo C
    └── Sin especiación
```

El herpetólogo decide si hay especiación y qué morfos existen en cada paquete. Un paquete puede no tener morfos aunque otro sí.

Eso no convierte a los morfos en especies. El centroide global sigue siendo la referencia de «es la misma especie». El regional dice cómo se ve ahí. El sub-centroide dice la variante. Ver [[Centroides y Muestras]].

## Ejemplos que las fuentes usan como esquema

- *Oophaga histrionica*: `red_morph` y `yellow_morph`, con vectores separados. El JSON de la estrategia a veces trae solo el morfo rojo; el maestro trae rojo y amarillo. Conservar ambos ejemplos en las fuentes. El compilador debe aceptar una lista, no un único morfo.
- *Pristimantis* polimórfico: liso, rayado, manchas. La nota de muestras habla de `Pristimantis_X_morfo_A` y `morfo_B`.

> [!WARNING] Nombres de ejemplo
> No dar de alta `red_morph` ni `Pristimantis_belmet` solo porque aparecen en un JSON ilustrativo. Ver [[Contradicciones del Modo Administrativo]].

## Qué no automatizar todavía

El estadio (adulto, juvenil, metamórfico, larva, desconocido) es manual. Un juvenil que no alcance el umbral del adulto cae a género (`Pristimantis sp.`), no a un centroide juvenil inexistente. El sub-centroide juvenil entra cuando haya al menos 10 fotos y alguien lo publique en el JSON (+2 KB en la estimación de la fuente). Ver [[Roadmap Fase 1 y Fase 2]] y [[Cascada Taxonomica y Supercentroides]].
