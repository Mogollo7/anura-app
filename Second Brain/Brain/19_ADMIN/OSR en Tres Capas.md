---
title: "OSR en Tres Capas"
tags: [admin, anura, osr]
created: 2026-09-25
status: draft
---

# OSR en Tres Capas

Barrera para no clasificar a la fuerza una especie no vista, un morfo no catalogado o algo fuera de distribución. Especificación: [[Fuente - ETI-OSR-2026]]. El menú alternativo (OpenMax, GAN, MC Dropout, ensambles) está en [[Fuente - Estrategias OSR Alternativas]] y **no** entra al teléfono.

> [!WARNING] Esto es diseño. El vault ya midió otra cosa
> [[DECISION_LOG]] y [[FASE_13_CALIBRACION_INDEPENDIENTE]] calibraron Mahalanobis (τ 39,35 a KAR 95 %, FAR 91 %, demasiado permisivo). Weibull sobre distancia coseno no tiene corrida registrada aquí. El Admin debe guardar `tau_kind` y no sustituir el ensayo por esta especificación.

Relacionado en el cerebro: [[Open-Set Recognition]].

## Las tres capas

1. **Geometría global.** Distancia al centroide de cada especie del paquete. `d = 1 - similitud coseno`. Cada especie tiene su radio, ajustado con una Weibull de cola inversa (escala η, forma β), no un umbral único para todo el paquete. Una polimórfica (*Oophaga histrionica* en el ejemplo) queda con radio holgado. Una uniforme (*Rhinella horribilis*) queda con radio estrecho. Si ninguna especie supera su radio: `01_OSR_GLOBAL`.
2. **Manifold del clúster.** Solo si la muestra cayó en un complejo. Se proyecta con `W`, se reconstruye y se mide `E_rec`. Si pasa de épsilon: `02_OSR_CLUSTER` (intruso que el adaptador querría encajar en A, B, C o D). Dimensión de trabajo de `W`: ver [[Microadaptadores y Transfer Learning]].
3. **Ecología.** Gaussiana de altitud (μ, σ) y prior de hábitat. Si la probabilidad de altitud baja de **0,05**, el puntaje cae a cero: `03_OSR_GEO_FAIL`.

> [!WARNING] Contradicción detectada: la capa 3 y el fallo del clúster
> El documento maestro corta la capa 3 solo por altitud; esta especificación mezcla altitud y hábitat. El pseudocódigo de la cascada, si falla el residuo, cae a género en vez de emitir intruso.
> **Decisión:** si `P(altitud | especie)` baja del `umbral_geo` del paquete, la política elige `OSR_GEO` o solo penalización. 0,05 es el valor inicial de las notas. El `IdentificationResult` guarda `geographic_context` para explicar GPS dudoso, altitud estimada o borde de rango. Ver [[Decisiones de Escalabilidad del Admin]].

## Estados para la app y para SQLite

| Código | Qué ve la persona | Qué hace el servidor al sincronizar |
| --- | --- | --- |
| `00_MATCH_OK` | Especie, ficha, certeza | Ocurrencia normal |
| `01_OSR_GLOBAL` | Fuera del catálogo local, guardada para revisión | Cola de auditoría con BioCLIP 2.5. Candidata a centroide nuevo (~2 KB en la estimación) |
| `02_OSR_CLUSTER` | Parecida al complejo X, rasgos que no cierran | Revisar si el adaptador debe crecer (A, B, C → D, ~10 KB en la estimación) |
| `03_OSR_GEO_FAIL` | Se parece a una especie, fuera de su cota o de su zona | Revisar GPS o una expansión de rango. No es un alta automática |

La cascada de género y familia usa otros nombres (`STATUS_GENUS_SP`, `STATUS_FAMILY_SP`). Hace falta un solo enum: [[Contradicciones del Modo Administrativo]].

## Qué se guarda en el teléfono cuando hay rechazo

Foto comprimida, embedding de 512, GPS, altitud y sustrato, en SQLite. Cuando hay red, la cola (la fuente dice Hostinger) pasa al worker del PC: BioCLIP 2.5 a 1024 dimensiones más una persona. Ese embedding de 1024 **no** se escribe en el paquete de 512. Ver [[Arquitectura Desacoplada]].

El cierre del ciclo crea un candidato de centroide o de matriz. Publicar es otra decisión: [[Worker Releases y Sandbox]].

## Calibración dentro del Admin

Ruta `/admin/osr`, fase 9. El worker propone alfa, tau de especie, tau de género, tau de familia y épsilon. La persona valida. El simulador (fase 10) debe mostrar qué capa rechazó y con qué número, para no mezclar 0,32, 0,78 y 39,35.
