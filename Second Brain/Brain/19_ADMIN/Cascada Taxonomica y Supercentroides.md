---
title: "Cascada Taxonómica y Supercentroides"
tags: [admin, anura, taxonomia]
created: 2026-09-25
status: draft
---

# Cascada Taxonómica y Supercentroides

Si la especie exacta no cierra, el sistema baja de nivel en vez de soltar un error vacío. Especificación: [[Fuente - ETI-SCH-2026]]. No sustituye a [[OSR en Tres Capas]]: primero se intenta la especie (y el clúster); el fallback es lo que queda cuando eso no alcanza.

## Orden

```text
Especie o clúster  →  si no alcanza τ
Género sp.         →  si no alcanza τ de género
Familia sp.        →  si no alcanza τ de familia
Rechazo abierto
```

| Nivel | Rango de τ en la fuente | Qué exige |
| --- | --- | --- |
| Especie | 0,72–0,85 | Textura y patrón |
| Género | 0,60–0,70 | Morfología, tolera color |
| Familia | 0,50–0,58 | Proporciones generales |

Esos rangos son hipótesis. Otro bloque de entradas aprieta género a 0,62–0,65 y familia a 0,52–0,55. Misma advertencia de unidad que en [[Contradicciones del Modo Administrativo]].

Fórmulas de la fuente, sin pesos por género:

- Género: suma de los centroides de sus especies, renormalizada L2.
- Familia: suma de los super-centroides de sus géneros, renormalizada L2.

> [!WARNING] Contradicción detectada: «ponderar» sin coeficientes
> El apartado 1.2 de ETI-SCH dice que la familia pondera a los géneros, y no da pesos.
> **Decisión:** suma L2, un voto por género. Sin `genus_weight`. Ver [[Decisiones de Escalabilidad del Admin]].

> [!WARNING] Contradicción detectada: el pseudocódigo traga al intruso
> Si la especie es de un clúster y el residuo falla, el código de la fuente no devuelve `02_OSR_CLUSTER`: sigue hacia género.
> **Decisión:** el código es `OSR_CLUSTER`. El género puede mostrarse aparte si supera su umbral, y no cuenta como especie. Ver [[Decisiones de Escalabilidad del Admin]].

## Qué muestra la interfaz

| Estado | Ejemplo de copia en la fuente | Siguiente gesto |
| --- | --- | --- |
| Especie | *Pristimantis illex*, certeza alta | Ficha |
| Género | *Pristimantis* sp. | Pedir vientre o canto |
| Familia | Strabomantidae sp. | Pedir sustrato y altitud |
| Rechazo | Muestra no identificada | Guardar para auditoría con BioCLIP 2.5 |

Fotos malas (flash, lodo, ejemplar dañado) pueden perder especie y género y aun así devolver familia. Eso es la «malla» de la [[Fuente - Roadmap Excepciones Fase 1 y 2]].

## Costo que la fuente afirma, y no está medido aquí

Unos **85 KB** extra por subpaquete para nodos de familia y género, del orden de **0,3 ms** extra en CPU ARM, y una cobertura de respuesta de **98,7 %**. El escenario de referencia es 10 familias y 30 géneros. Tratar esas tres cifras como estimación de diseño, no como resultado del vault.

Ejemplos de nodos en el JSON: Strabomantidae τ familia 0,52; Hylidae 0,55; *Pristimantis* τ género 0,62; *Dendropsophus* 0,64. Son ilustración.
