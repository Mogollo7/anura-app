---
title: "Centroides y Muestras"
tags: [admin, anura, centroides]
created: 2026-09-25
status: draft
---

# Centroides y Muestras

Reglas para armar un centroide con BioCLIP sin exigir miles de fotos ni un dataset balanceado. Texto íntegro: [[Fuente - Centroides Estables y Muestras]]. El cálculo es la fase 6 de [[Plan de Construccion del Admin]].

El centroide de especie es la media de embeddings normalizada a la hiperesfera:

`C = suma(e_i) / ||suma(e_i)||`

Esa normalización L2 evita que una especie de 200 fotos opaque a una de 15 dentro de un softmax. No evita un centroide malo si las 15 fotos son del mismo animal.

## Cuántas fotos, de cuántos individuos

| Calidad | Fotos por especie | Individuos distintos | Para qué |
| --- | --- | --- | --- |
| Mínimo viable | 10–15 | 3–5 | Especies raras. Centroide básico. |
| Recomendado | 30–50 | 8–12 | Aguanta luz, humedad y postura. |
| Óptimo | 80–100 o más | 15 o más | Polimorfismo, dimorfismo, juveniles. |

Cincuenta fotos de la misma rana en la misma salida ajustan al individuo y al fondo, no a la especie. Hacen falta salidas, fotógrafos, horas y piel seca o mojada distintas.

## A quién darle más fuerza

No se reparte el mismo número de fotos.

- **Polimórficas** (*Pristimantis* en el ejemplo): 50–100 fotos, o sub-centroides por morfo. No dejar un solo punto medio si los colores son opuestos. Ver [[Morfos y Especiacion Regional]].
- **Pares casi idénticos:** más muestras para separar el detalle. En el plan actual eso alimenta el micro-adaptador, no un fine-tuning del encoder. Ver [[Microadaptadores y Transfer Learning]].
- **Las que la gente va a fotografiar casi siempre** (ejemplos de la fuente: *Dendropsophus columbianus*, *Rhinella horribilis*): el centroide tiene que ser el más estable, porque concentra las consultas.
- **Raras, con 10–15 fotos de 3 individuos:** sirven como mínimo viable. No se descartan por desbalance.

## Mezcla visual al curar

- **Ángulos:** 60 % dorsolateral, 25 % dorsal, 15 % cabeza, tímpano o vientre.
- **Luz y fondo:** flash nocturno, luz de día, hoja, hojarasca, roca.
- **Humedad:** seca y mojada. El brillo del agua mueve al Vision Transformer.

## Tres vectores, no uno

| Vector | Qué representa |
| --- | --- |
| Centroide global | Referencia de la especie, independiente del paquete |
| Centroide regional | Cómo se ve esa especie dentro de un paquete |
| Sub-centroide de morfo | Una variante en esa especie y esa región |

> [!WARNING] Contradicción detectada: promediar morfos
> La nota de muestras acepta un centroide en el punto medio de todos los morfos. El documento maestro y las reglas de datos no promedian morfos opuestos, y exigen conservar el global.
> **Decisión:** tres vectores. Sin promedio de morfos opuestos. Con menos de 3 individuos en el paquete, se presta el global (`borrowed: true`). Ver [[Decisiones de Escalabilidad del Admin]].

Juvenil, metamorfosis y larva no generan sub-centroide el día 1. Hace falta un contrato `sub_centroids` vacío de juveniles hasta juntar al menos **10** imágenes de esa clase. Eso es Fase 2: [[Roadmap Fase 1 y Fase 2]].

Cada centroide guarda procedencia: paquete, versión de dataset, individuos, imágenes, fecha, experimento, encoder y estado. Ver [[Modo Administrativo]].
