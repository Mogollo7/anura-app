---
title: "Worker, Releases y Sandbox"
tags: [admin, anura, worker]
created: 2026-09-25
status: draft
---

# Worker, Releases y Sandbox

Fases 5, 12, 13, 14 y 15 de [[Plan de Construccion del Admin]]. El worker es un proceso del PC, no una pantalla de la app.

## Orden de encendido

1. **Mock.** El Admin ya crea jobs, progreso, logs y artefactos falsos con el contrato real.
2. **PC real.** La fuente apunta a una GPU local (RTX 4050). Ahí corre BioCLIP 1 para los embeddings de 512 del paquete, y BioCLIP 2.5 solo para auditar rechazos. No se cruzan dimensiones: [[Arquitectura Desacoplada]].
3. **Debug.** `/admin/debug` muestra heartbeat, CPU, RAM, GPU, VRAM, Python, ONNX, jobs y errores. El hueco para depurar la app queda reservado y desconectado.

Quién puede lanzar un entrenamiento o ver la GPU: solo el administrador. [[Roles del Admin]].

## Qué produce un job

Embeddings, centroides, scores, umbrales propuestos, métricas, artefactos, JSON, manifest y checksum. Eso es cálculo.

No produce decisiones científicas: especie nueva, miembros de un complejo, pesos científicos, morfo, ni aprobación de publicación. Si un clúster supera `MAX_CLUSTER_SPECIES`, el job deja un aviso. No parte el complejo solo.

## Publicar

```text
Worker
  → resultado técnico
  → Herpetólogo (validación científica)
  → Administrador (validación técnica)
  → Release
```

Estados: `DRAFT` → `VALIDATING` → `READY` → `APPROVED` → `PUBLISHED`, y `ROLLED_BACK`.

No hay publicación automática. Un rechazo de campo o un scraper pueden dejar un resultado técnico. No publican. Ver [[Decisiones de Escalabilidad del Admin]] y [[OSR en Tres Capas]].

Cada paquete publicado recuerda dataset, experimento, encoder, lote de centroides y lote de OSR. Ejemplo de identificadores en [[Modelo de Datos del Admin]].

## Sandbox

`/admin` en modo sandbox puede mover pesos, umbrales, centroides y comparar experimentos. Nada de eso modifica el paquete publicado. El simulador apunta al sandbox cuando se está probando, y al release solo cuando se está auditando lo ya aprobado.

## Qué no entra en este nodo

OTA real hacia los teléfonos, cola de Hostinger en producción, y conexión con la app. El contrato del JSON ya queda listo en [[Esquema JSON del Paquete]] para cuando eso se enchufe.
