---
title: "Roadmap Fase 1 y Fase 2"
tags: [admin, anura, roadmap]
created: 2026-09-25
status: draft
---

# Roadmap Fase 1 y Fase 2

Qué tiene que funcionar sin audio y sin detector automático, y qué se enchufa después. Texto íntegro: [[Fuente - Roadmap Excepciones Fase 1 y 2]]. No confundir esta «fase 1 de producto» con la fase 1 de datos de [[Plan de Construccion del Admin]]. Aquí se habla del núcleo que sale a campo. Allá, del orden para programar el Admin.

> [!WARNING] «Listo» no es evidencia
> La tabla de costos marca el motor móvil, los JSON, Hostinger y el worker como Fase 1 lista. En este vault eso sigue en **NOT_EXECUTED** hasta que haya corrida. Léela como presupuesto: móvil y JSON a 0 USD por consulta, proxy 3–8 USD/mes, PC ya existente, CVAT automático y audio a 0 USD de licencia cuando existan.

## Núcleo que no espera a los módulos futuros

- BioCLIP 1 congelado, ONNX del orden de 100 MB en la fuente (medición distinta en [[Arquitectura Desacoplada]]).
- JSON con centroides L2 de **adultos**.
- OSR de tres capas y cascada hasta familia.
- Curación manual: CVAT, pHash, Laplaciano `Var < 100`. Ver [[Curacion e Ingesta]].
- Contrato `sub_centroids` ya presente, aunque solo haya adultos.
- Campo opcional `audio_signature_id` y pesos bioacústicos reservados, sin modelo de canto.
- Si dos especies quedan a menos de **0,02** de similitud y no hay canto, desempata el contexto o queda el clúster como pendiente de auditoría.

## Lo que entra después, sin cambiar el APK

| Añadido | Disparador en la fuente |
| --- | --- |
| Sub-centroide de juvenil, metamorfosis o larva | Al menos 10 imágenes acumuladas de esa clase. Unos 2 KB más en el JSON |
| Canto | Extractor de espectrograma o YAMNet afinado. 3–5 segundos. Puede vetar al modelo visual en gemelas |
| Auto-anotación CVAT | YOLOv8-Anura servido por Nuclio, cuando exista |
| Filtro morfométrico de LRC | Cuando los rangos por especie estén validados. No el día 1 |

Un juvenil fotografiado antes de eso no supera el τ del adulto y baja a género. Es el comportamiento correcto del primer núcleo, no un fallo. Ver [[Morfos y Especiacion Regional]].

Los sliders de override ecológico (por ejemplo `wm = 0,50` en una riparia) sí pertenecen al Admin desde el principio, aunque el cálculo automático de la gaussiana también exista. Ver [[Contexto Ecologico y Pesos]].
