---
title: "Plan de Acción y Arquitectura Conceptual"
proyecto: Anura
fuente: "Notion â€” Proyecto Identificación de Anuros Colombia"
tags: [anura, desarrollo, arquitectura]
---

# Plan de Acción y Arquitectura Conceptual

> [!warning] Documento histórico â€” parcialmente superado
> Esta es la propuesta original de Notion. La arquitectura vigente sustituyó **EfficientNet-B0 por BioCLIP como àºnico backbone** (visión y audio), decisión confirmada por el autor y documentada en [[Modelo de Visión â€” BioCLIP]] y en [[Inconsistencias y Decisiones Pendientes]] (C-2). El resto de la idea general â€” árbol de decisiones jerárquico, embeddings morfológicos, metric learning y base vectorial â€” sigue vigente y es exactamente lo que las notas de [[Metodología â€” àndice|Metodología]] y de esta misma sección de Desarrollo Técnico desarrollan en detalle. Se conserva el texto original sin alterar por trazabilidad.

## Desarrollo técnico (código y arquitectura)

## Plan de acción

Una vez identificadas las características clave para la clasificación e identificación de los anuros, se propone un método para la creación de la app que facilite su documentación.

### Idea general

Modelo de visión inteligente basado en patrones para la identificación de anfibios del orden Anura.

Estos vertebrados poseen características clave que los dividen en familia, género y especie. Mediante un **árbol de decisiones**, se reduce la carga de identificación de características, se eliminan posibles resultados y se disminuye el margen de error, utilizando **morfología visual, metadatos y sonido**, creando un modelo **multimodal** más preciso.

### Herramientas

Para la creación de la app, se entrena un modelo que aprenda a generar **vectores morfológicos (embeddings)** de cada imagen. Cada imagen pasa por una red neuronal y se transforma en un vector numérico. Estos vectores se comparan usando **distancia euclidiana** o **cosine similarity**, mediante *metric learning*. Esto ayuda a agilizar el desarrollo de software y permite escalar sin necesidad de reentrenar todo el modelo.

#### Arquitectura (conceptual)

- **Backbone de visión:** una serie de capas dentro de una red neuronal procesa imágenes de entrada para identificar patrones jerárquicos.
- Modelos propuestos: **EfficientNet** y **PyTorch**.
- **Triplet loss:** se evalàºan 3 imágenes: una base A, una correcta P y una incorrecta N. Se busca que A esté más cerca de P que de N.
    - Dist(A,P) + margen < Dist(A,N)

#### Tecnologías (lista)

- EfficientNet-B0
- PyTorch
- Triplet Loss
- Base de datos
- Base vectorial (Qdrant)

---

[[Modelo de Visión â€” BioCLIP]] *(sustituyó a la propuesta original de EfficientNet)*

[[Implementación de Triplet Loss]]

[[Base Vectorial (SQLite-vec)]]

[[API Backend]]

[[App Móvil]]



