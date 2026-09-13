---
title: "Plan de AcciÃ³n y Arquitectura Conceptual"
proyecto: Anura
fuente: "Notion â€” Proyecto IdentificaciÃ³n de Anuros Colombia"
tags: [anura, desarrollo, arquitectura]
---

# Plan de AcciÃ³n y Arquitectura Conceptual

> [!warning] Documento histÃ³rico â€” parcialmente superado
> Esta es la propuesta original de Notion. La arquitectura vigente sustituyÃ³ **EfficientNet-B0 por BioCLIP como Ãºnico backbone** (visiÃ³n y audio), decisiÃ³n confirmada por el autor y documentada en [[Modelo de VisiÃ³n â€” BioCLIP]] y en [[Inconsistencias y Decisiones Pendientes]] (C-2). El resto de la idea general â€” Ã¡rbol de decisiones jerÃ¡rquico, embeddings morfolÃ³gicos, metric learning y base vectorial â€” sigue vigente y es exactamente lo que las notas de [[MetodologÃ­a â€” Ãndice|MetodologÃ­a]] y de esta misma secciÃ³n de Desarrollo TÃ©cnico desarrollan en detalle. Se conserva el texto original sin alterar por trazabilidad.

## Desarrollo tÃ©cnico (cÃ³digo y arquitectura)

## Plan de acciÃ³n

Una vez identificadas las caracterÃ­sticas clave para la clasificaciÃ³n e identificaciÃ³n de los anuros, se propone un mÃ©todo para la creaciÃ³n de la app que facilite su documentaciÃ³n.

### Idea general

Modelo de visiÃ³n inteligente basado en patrones para la identificaciÃ³n de anfibios del orden Anura.

Estos vertebrados poseen caracterÃ­sticas clave que los dividen en familia, gÃ©nero y especie. Mediante un **Ã¡rbol de decisiones**, se reduce la carga de identificaciÃ³n de caracterÃ­sticas, se eliminan posibles resultados y se disminuye el margen de error, utilizando **morfologÃ­a visual, metadatos y sonido**, creando un modelo **multimodal** mÃ¡s preciso.

### Herramientas

Para la creaciÃ³n de la app, se entrena un modelo que aprenda a generar **vectores morfolÃ³gicos (embeddings)** de cada imagen. Cada imagen pasa por una red neuronal y se transforma en un vector numÃ©rico. Estos vectores se comparan usando **distancia euclidiana** o **cosine similarity**, mediante *metric learning*. Esto ayuda a agilizar el desarrollo de software y permite escalar sin necesidad de reentrenar todo el modelo.

#### Arquitectura (conceptual)

- **Backbone de visiÃ³n:** una serie de capas dentro de una red neuronal procesa imÃ¡genes de entrada para identificar patrones jerÃ¡rquicos.
- Modelos propuestos: **EfficientNet** y **PyTorch**.
- **Triplet loss:** se evalÃºan 3 imÃ¡genes: una base A, una correcta P y una incorrecta N. Se busca que A estÃ© mÃ¡s cerca de P que de N.
    - Dist(A,P) + margen < Dist(A,N)

#### TecnologÃ­as (lista)

- EfficientNet-B0
- PyTorch
- Triplet Loss
- Base de datos
- Base vectorial (Qdrant)

---

[[Modelo de VisiÃ³n â€” BioCLIP]] *(sustituyÃ³ a la propuesta original de EfficientNet)*

[[ImplementaciÃ³n de Triplet Loss]]

[[Base Vectorial (SQLite-vec)]]

[[API Backend]]

[[App MÃ³vil]]



