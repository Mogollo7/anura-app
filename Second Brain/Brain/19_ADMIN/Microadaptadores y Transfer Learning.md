---
title: "Microadaptadores y Transfer Learning"
tags: [admin, anura, microadaptadores]
created: 2026-09-25
status: draft
---

# Microadaptadores y Transfer Learning

Cómo separar especies casi idénticas sin volver a descargar el encoder. Fuentes: [[Fuente - Microadaptadores Multiclase]], [[Fuente - Documento Maestro de Arquitectura]], [[Fuente - Metric Learning y Olvido Catastrofico]], [[Fuente - Espacio Vectorial y Margen]].

## Qué se adopta para construir

> [!WARNING] Contradicción detectada: dos notas piden descongelar BioCLIP 1
> Piden fine-tuning de las últimas capas, Triplet o ArcFace sobre el ViT, y centroides calculados con ese encoder nuevo. Eso rompe el ONNX congelado del teléfono.
> **Decisión:** BioCLIP 1 permanece congelado. ArcFace entrena solo `W`. La forma inicial es 512×64 FP16 (64 KiB). `MAX_CLUSTER_SPECIES = 12` es un límite configurable. El sistema avisa. El herpetólogo decide si se divide. Ver [[Decisiones de Escalabilidad del Admin]].

El fine-tuning clásico (una capa densa con Cross-Entropy) descalibra el espacio, olvida el preentrenamiento y dibuja fronteras sin margen. Por eso el plan no añade una cabeza `Dense(N clases)` al móvil.

## Cómo desempata un clúster

1. BioCLIP 1 limpio indica que la foto cae en un grupo críptico (varias *Pristimantis* de la misma subregión, por ejemplo).
2. La app carga solo la matriz de ese clúster.
3. Proyecta el vector de 512 dimensiones y separa a los miembros.

Añadir la especie E al grupo A–D reentrena **únicamente** esa matriz, en el PC, con las fotos de A–E. No toca el ONNX, ni los clústeres de otras subregiones. El JSON de esa subregión pasa, en la estimación de la fuente, de unos 40 KB a unos 50 KB. El teléfono baja ese JSON.

Si el grupo crece a 15–20 especies, la misma fuente propone un árbol de subclústeres. Eso es una recomendación que el Admin puede mostrar. No parte el complejo al pasar de 12. `MAX_CLUSTER_SPECIES` avisa. Los miembros los sigue eligiendo el herpetólogo.

La forma inicial es 512×64 en FP16, que pesa **64 KiB**. Los «35 KB» y «40–50 KB» de las fuentes no coinciden con esa matriz densa. El tamaño real es filas × columnas × bytes, y se guarda en el artefacto. ArcFace de partida: margen 0,35 y escala 30.

## Contrato mínimo dentro del paquete

```text
cryptic_clusters[]
  cluster_id
  member_species[]
  micro_adapter_matrix
  cluster_centroids por especie
  epsilon_reconstruction
  context_tiebreaker (pesos de altitud y microhábitat)
```

Los nombres `cryptic_groups`, `W_pair` y `W_cluster` aparecen en variantes. El compilador usa un solo nombre. Ver [[Esquema JSON del Paquete]].

Quien crea el clúster es el herpetólogo. El sistema solo puede decir «estas dos puntuaciones están demasiado cerca». Ver [[Roles del Admin]].
