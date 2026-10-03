---
title: "Esquema JSON del Paquete"
tags: [admin, anura, json]
created: 2026-09-25
status: draft
---

# Esquema JSON del Paquete

Contrato que compila la fase 12. Hay tres ejemplos completos, conservados sin recortar, en [[Fuente - Documento Maestro de Arquitectura]], [[Fuente - Estrategia de Arquitectura y Transfer Learning]] y [[Fuente - ETI-SCH-2026]]. Este nodo fija **un** esquema para implementar. Los ejemplos no se borran.

> [!WARNING] Contradicción detectada: los ejemplos no usan los mismos campos ni la misma escala
> `cryptic_groups` frente a `cryptic_clusters`. `sub_centroids` frente a `centroids`. `rejection_tau` 0,32 frente a 0,78. Versiones de ejemplo 2.4.0, 3.1.0 y 3.2.0. `total_species: 55` solo aparece en un ejemplo.
> **Decisión:** un JSON por subregión, esquema del documento maestro. `tau_kind` es `cosine_similarity`. El piso térmico no parte el archivo. Ver [[Decisiones de Escalabilidad del Admin]].

## Objeto

- `package_metadata`: `package_id`, `region_name`, `version`, `last_updated`, `embedding_dim` (**512**), `quantization` (`FP16` o `FP32`), encoder (`BioCLIP-1-frozen`).
- `family_nodes[]`: `family_id`, nombre, nombre común, centroide, `rejection_tau_family`, `tau_kind`.
- `genus_nodes[]`: `genus_id`, `family_id`, nombre, centroide, `rejection_tau_genus`, `tau_kind`.
- `species_catalog[]`: `taxon_id`, `genus_id`, nombre, lista de sub-centroides (`morph_id` + vector), `rejection_tau`, `tau_kind`, y `context_parameters`.
- `context_parameters`: `altitude_mean_msnm`, `altitude_std_dev`, `weights` (`visual`, `geo`, `habitat`), `substrate_priors`, y hueco opcional `audio_signature_id` aunque el audio no se construya ahora.
- `cryptic_clusters[]`: `cluster_id`, especies, matriz, dimensiones, bytes, `epsilon_reconstruction`, desempate de contexto.
- Procedencia, en el manifest y no solo dentro del vector: dataset, experimento, individuos, imágenes, fecha, estado. Ver [[Modo Administrativo]].
- `manifest` y checksum, fuera del vector, en la fase 12.

El id de ejemplo repetido es `09_uraba_antioqueno`. Otro ejemplo usa `02_oriente_antioqueno`. Los floats de 512 dimensiones de las fuentes son marcadores de posición (`"... 512 floats ..."`), no vectores reales.

## Lo que el compilador debe rechazar

- Dimensión distinta de 512, o encoder distinto de BioCLIP 1. BioCLIP 2.5 no entra aquí.
- Pesos que no sumen 1, si los tres están presentes.
- Publicar sin checksum, sin manifest o sin las dos aprobaciones. Ver [[Worker Releases y Sandbox]].
- Un único centroide cuando la ficha declara morfos opuestos. Ver [[Morfos y Especiacion Regional]].

## Tamaño esperado, como diseño

Especie normal: del orden de **2 KB**. Micro-adaptador: decenas de KB, no el ONNX de ~100–165 MB. Paquete de zona: por debajo de **1 MB**, con menciones de **50 KB–1,2 MB** según qué lleve. El teléfono no reinstala el encoder para absorber el cambio.
