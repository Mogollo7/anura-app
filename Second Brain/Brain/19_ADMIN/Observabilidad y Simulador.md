---
title: "Observabilidad y Simulador"
tags: [admin, anura, observabilidad]
created: 2026-09-25
status: draft
---

# Observabilidad y Simulador

Grafana no es parte del algoritmo de identificación. Es la infraestructura de observabilidad detrás de la UI técnica. Texto íntegro: [[Fuente - Observabilidad Grafana y ECharts]]. El ciclo completo que el Admin debe poder mostrar está en [[Decisiones de Escalabilidad del Admin]]. El simulador es la fase 10 de [[Plan de Construccion del Admin]]. El debug del worker es la fase 15.

```text
ANURA ADMIN
     │
     ├── Scientific UI → ECharts y componentes propios
     └── Technical UI  → worker, jobs, logs
              │
        ANURA BACKEND
              │
              ├── Worker → resultados de ML
              └── Observability → Prometheus / Loki → Grafana
```

El herpetólogo no entra a Grafana. Ve el ciclo: dataset, curación, taxonomía, individuos, observaciones, imágenes, embeddings, centroides, morfos, clústeres, contexto, OSR, validación, experimento, paquete y las dos aprobaciones.

## Dos clases de gráfica

**Grafana, como motor, no como iframe.** Series de infraestructura: GPU, VRAM, worker en línea, CPU, jobs por minuto, errores, logs, latencia. Detrás pueden estar Prometheus, Loki y Postgres. El usuario del Admin no tiene por qué ver la marca.

**ANURA dibuja lo científico con ECharts y componentes propios.** Por experimento: dataset, especies, individuos, imágenes, AUROC, KAR, FAR, matriz de confusión, ROC, precision-recall, histograma de scores, umbral contra FAR, especies por región y por altitud, resultados por individuo, comparación entre experimentos, y más adelante una proyección 2D de embeddings.

No mezclar «GPU al 82 %» con «AUROC del experimento 024» en el mismo panel. Eso respeta la separación de [[Roles del Admin]]: el herpetólogo no necesita la VRAM para revisar una ficha.

## Contrato del prototipo

Primero datos mock. El contrato no cambia cuando aparezca el worker:

```text
ExperimentResult
├── metrics
├── curves
├── confusionMatrix
├── distributions
├── bySpecies
├── byRegion
├── artifacts
└── logs
```

Rutas de ejemplo: `GET /api/admin/experiments/024`, `.../metrics`, `GET /api/admin/worker/status`, `GET /api/admin/logs`. El backend consulta Grafana solo cuando toca. Así se puede cambiar el motor sin rehacer la pantalla.

Mapa de la interfaz citado en la fuente: Dashboard, Datos, Especies, Individuos, Experimentos (resumen, métricas, ROC, confusión, scores, logs), Worker (estado, GPU, jobs, logs) y Releases.

## Simulador

`/admin/simulator` corre una identificación de prueba: imagen o embedding, GPS, altitud, microhábitat. Devuelve especie, género, familia o no concluyente, y la rama (capa 1, residuo, corte geográfico o fallback). Sirve para ver un τ mal unido antes de publicar. No escribe en el paquete de producción. Si el experimento es de sandbox, tampoco. Ver [[Worker Releases y Sandbox]].

Las métricas solo se muestran si existen. La fase 11 prohíbe inventarlas.
