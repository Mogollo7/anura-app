---
title: "Plan de Construcción del Admin"
tags: [admin, anura, plan]
created: 2026-09-25
status: draft
---

# Plan de Construcción del Admin

Orden para implementar [[Modo Administrativo]] sin pedir un MLOps completo de una vez. Texto íntegro: [[Fuente - Plan de Fases para Construir el Admin]]. El modelo que estas fases usan está en [[Modelo de Datos del Admin]].

> [!WARNING] Contradicción detectada: el árbol ASCII de la fase 1
> Pone Observación encima de Individuo. No implementar ese dibujo. La jerarquía válida está en [[Modelo de Datos del Admin]].

Fuera de las 15 fases, por decisión de la misma fuente: **audio, CVAT real, YOLO / auto-anotación, OTA real y la app móvil**.

## Fases

1. **Arquitectura y datos.** Dataset versionado, individuo separado de observación, fotografías, taxonomía, estadio, morph id, GPS, altitud calculada, municipio, subregión, paquete, estados, especiación distinta por paquete. Sin entrenamiento real.
2. **Curación.** Rutas `/admin/datasets` y `/admin/curation`. Importar, subir, asociar taxonomía, marcar estadio y morfo, duplicados, mala calidad, sacar una imagen sin destruir la observación, invalidar una observación, trazabilidad. OpenTopoData queda mock.
3. **Ficha científica.** `/admin/taxonomy`. Taxonomía, dataset, individuos, estadio, morfos, LRC, altitud, microhábitat, distribución, pesos, complejos y estado científico. Los requisitos de datos dependen de la especie.
4. **Paquetes.** `/admin/packages`. Las 9 subregiones. Una especie puede repetirse, con otro contexto, otros morfos, con o sin especiación, y con centroide regional. Global, regional y morfo no son el mismo vector.
5. **Worker y embeddings.** Job → worker del PC → BioCLIP 1 → vectores de 512 → validación → almacén. Primero worker mock. Después el PC real (la fuente menciona una RTX 4050). La pantalla muestra job, progreso, GPU, VRAM, logs, tiempo, dataset, encoder y artefactos.
6. **Centroides.** Global, luego por paquete, luego sub-centroide solo si esa especie tiene morfos en ese paquete. Estadio manual. La LRC queda preparada, sin clasificar juvenil todavía. Ver [[Centroides y Muestras]].
7. **Micro-adaptadores.** `/admin/adapters`. El herpetólogo elige las especies, crea el clúster, configura ArcFace, el worker entrena, sale la matriz y alguien la valida. El sistema puede alertar confusión; no arma el complejo solo. Ver [[Microadaptadores y Transfer Learning]].
8. **Contexto.** `/admin/context`. Por especie y paquete: media y desviación de altitud, sustratos, pesos. Mostrar calculado, manual y efectivo. Nunca pisar el manual en silencio. Ver [[Contexto Ecologico y Pesos]].
9. **OSR.** `/admin/osr`. Del dataset validado a embeddings, centroides, distribuciones, EVT / Weibull, alfa, tau de especie, género y familia, y épsilon del clúster. Calcula el worker. La persona valida o ajusta. El tipo de umbral tiene que convivir con lo ya medido: [[OSR en Tres Capas]].
10. **Simulador.** `/admin/simulator`. Imagen o embedding, más GPS, altitud y microhábitat. Devuelve especie, género, familia o no concluyente, y explica la rama. Ver [[Observabilidad y Simulador]].
11. **Validación.** `/admin/validation`. Taxonomía, dataset, individuos, duplicados, embeddings, dimensión 512, NaN, normalización L2, centroides, morfos, OSR, JSON, manifest, checksum y consistencia. Cuando haya datos reales: accuracy, precision, recall, FAR, KAR, AUROC y matriz de confusión. **No inventar métricas.**
12. **Compilación.** Taxonomía + centroides + morfos + contexto + OSR + micro-adaptadores → JSON → manifest → checksum → paquete listo. Ver [[Esquema JSON del Paquete]].
13. **Releases.** `DRAFT` → `VALIDATING` → `READY` → `APPROVED` → `PUBLISHED`, y `ROLLED_BACK`. Sin publicación automática. Ver [[Worker Releases y Sandbox]].
14. **Sandbox.** Probar pesos, umbrales, centroides, paquetes y experimentos. Nada de eso toca producción.
15. **Debug.** `/admin/debug`. Worker en línea o no, heartbeat, CPU, RAM, GPU, VRAM, Python, BioCLIP, ONNX, jobs, logs y errores. Dejar hueco para el debug de la app, sin conectarlo.

## Orden

```text
datos → curación → fichas → paquetes → embeddings
  → centroides → clústeres → contexto → OSR
  → simulador → validación → compilador
  → release → sandbox → debug del worker
```

Ese orden es el que evita construir el worker real antes de tener el modelo científico. El abandono del entrenamiento manual está en [[Fuente - Estrategias OSR Alternativas]] y se aplica a partir de la fase 5: los paquetes y el reentrenamiento salen de aquí, no de un flujo paralelo a mano.
