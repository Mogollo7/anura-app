---
title: "Decisiones de escalabilidad del Admin"
tags: [admin, anura, decisiones]
created: 2026-09-25
status: refined
---

# Decisiones de escalabilidad del Admin

Cierre de diseño del 2026-09-25 para construir [[Modo Administrativo]]. El criterio fue este: el teléfono hace poco trabajo y descarga kilobytes; una especie nueva es una inserción, no un reentrenamiento del encoder; el catálogo puede crecer de Antioquia a otros departamentos sin cambiar el compilador.

Estas decisiones no reescriben [[DECISION_LOG]]. Las mediciones siguen siendo mediciones. Lo que se cierra aquí es qué hacer cuando las notas se contradicen. El relato de cada choque permanece en [[Contradicciones del Modo Administrativo]]. Las fuentes literales no se recortan.

## Regla de oro

Un solo espacio vectorial: **BioCLIP 1 congelado, 512 dimensiones, normalización L2**. Todo lo que cambia con el tiempo vive en el JSON del paquete. Si una mejora obliga a redistribuir el ONNX, no entra.

## Decisiones

### 1. El encoder no se toca

El Admin no regenera `bioclip_v1.onnx`. ArcFace (margen 0,35, escala 30) entrena solo la matriz del clúster. Cross-Entropy y el fine-tuning de las últimas capas del ViT quedan fuera del plan: cada reentrenamiento descalibraría el espacio y obligaría a reinstalar el modelo en todos los teléfonos.

### 2. Dos mecanismos, dos nombres

`desempate_criptico` es la matriz del clúster. `cascada_taxonomica` es especie → género → familia → rechazo. Ningún campo se llama «nivel 2».

### 3. Un intruso no se convierte en especie

Si la muestra entra a un clúster y el residuo supera épsilon, el código que se guarda y se encola es `OSR_CLUSTER`. No hay alta de especie.

El género y la familia sí pueden mostrarse como etiqueta secundaria, si su propia similitud supera su umbral. La persona en campo ve «no cierra con el complejo, se parece a *Pristimantis*». El servidor recibe un candidato para ampliar la matriz, no un género disfrazado de acierto.

### 4. La altitud es un umbral del paquete, no una ley

Puntaje = `wv * similitud + wg * P(altitud) + wm * P(hábitat)`, con los tres pesos sumando 1.

La regla es:

```text
Si P(altitud | especie) < umbral_geo del paquete
→ OSR_GEO, o solo penalización, según la política de ese paquete
```

`umbral_geo` es configurable. **0,05** es el valor inicial de las notas, no una constante permanente. Hace falta validarlo. Hay GPS malo, altitud estimada y observaciones en el borde del rango: el resultado tiene que explicar el contexto geográfico para que el herpetólogo vea por qué salió `OSR_GEO`. El hábitat pondera el puntaje. No rescata por sí solo una cota que la política del paquete ya marcó como rechazo. Los pesos manuales siguen visibles y no se pisan en silencio.

### 5. En el teléfono solo hay producto punto

La inferencia móvil compara cosenos contra centroides L2. Es un producto punto. Cada centroide de 512 en FP16 pesa **1 KiB**. Una subregión de 55 especies pesa **55 KiB** (56320 bytes), no 64 KiB.

El Admin ajusta una Weibull por especie sobre las distancias del entrenamiento y **guarda el corte ya convertido en similitud coseno** (`tau_kind: cosine_similarity`). El teléfono no evalúa la Weibull ni arrastra una covarianza.

Mahalanobis se queda en el worker, como experimento de comparación. El ensayo del cerebro (τ 39,35, FAR 91 %) no se empaqueta. Si más adelante Mahalanobis gana en FAR y KAR dentro del simulador, se cambia el calibrador del Admin; el teléfono sigue recibiendo un corte de coseno.

Los valores 0,32 y 0,78 de los ejemplos no se copian. 0,72–0,85 es hipótesis hasta que el simulador calibre con datos reales.

### 6. La matriz y el tope del clúster son configuración

La forma inicial de la matriz es **512×64, FP16**. El tamaño no es una constante científica: es `filas × columnas × bytes del tipo`. Con ese default da **64 KiB** exactos (65536 bytes). Los JSON de ejemplo que dicen «35 KB» para una matriz densa de 512×64 no cuadran. Si cambian filas, columnas o el tipo, cambian los bytes. El artefacto guarda las tres cifras. 512×512 no es el default: pesa como otro modelo.

Quién pertenece al complejo lo define el **herpetólogo**. El sistema no parte un clúster al llegar a 13 especies.

`MAX_CLUSTER_SPECIES = 12` es un límite **configurable del pipeline**, no una ley biológica. Si el complejo lo supera, o si dos miembros siguen a menos de 0,02 de coseno después del entrenamiento, el Admin avisa: «este clúster supera el límite operativo recomendado; conviene dividirlo en subclústeres». Dividir, reentrenar y tocar otros paquetes solo ocurre si el herpetólogo lo pide.

### 7. Pesos por especie y por paquete

La ficha guarda tres números visibles: calculado, manual y efectivo. El efectivo es el manual si existe; si no, el calculado. Las tablas 80/10/10, los rangos y el perfil de quebrada son **plantillas** para rellenar una ficha nueva.

El prior global 0,75 del EXP-007 no se escribe en `wg`. Demostró que la geografía ayuda. No es el esquema de tres pesos.

### 8. Nueve descargas, no treinta y seis

La unidad que se versiona y se baja es la **subregión**. Antioquia tiene nueve. El piso térmico (`lowland`, `premontane`, `montane`, `paramo`) filtra candidatos en memoria con la gaussiana de altitud. No es un paquete hijo.

Esas 55 especies ocupan 55 KiB de centroides. Partir cada subregión en cuatro pisos multiplicaría releases, checksums y solapes sin ahorrar nada que el teléfono note. «Zona A / B / C» no se implementa.

Una especie en varias subregiones es una fila por paquete, con su contexto. El censo del departamento no es la suma de esas filas. Las cifras 220–235, 120–140 y ~85 siguen como estimación hasta la curación.

El esquema lleva `parent_id`. El primer padre es Antioquia. Otro departamento entra como otra raíz, con el mismo compilador.

### 9. Individuo, luego observación, luego foto

Esa es la cadena. El dataset es la membresía versionada de fotografías, no el padre biológico. Train y test se parten por **individuo**, si no las métricas futuras miden al mismo animal dos veces.

Sacar una foto mala la quita del entrenamiento y deja la observación. Invalidar la observación saca todas sus fotos y guarda el motivo. Cambiar el nombre común no recalcula embeddings. Cambiar fotos, taxonomía, morfo o la membresía del dataset sí invalida lo que está debajo.

### 10. Tres centroides, y el global se presta

No se promedia un morfo rojo con uno amarillo.

| Vector | Cuándo existe |
| --- | --- |
| Global | Siempre, a nivel especie. Referencia común. |
| Regional | Cuando el paquete tiene al menos 3 individuos distintos de esa especie. |
| Morfo | Solo si el herpetólogo declaró ese morfo en ese paquete. |

Con menos de 3 individuos regionales, el paquete apunta al centroide global con `borrowed: true` y la ficha queda en `WARNING`. La especie rara entra al catálogo sin envenenar un promedio local de una sola rana. Juveniles no tienen vector hasta juntar 10 fotos y pasar por un release.

### 11. El primer ciclo no carga lo que aún no decide

Audio, YOLO, scraper, OTA real y la app no se construyen en las 15 fases. El JSON reserva `audio_signature_id`. CVAT en este ciclo es manual, con pHash y Laplaciano `Var < 100`. El scraper, cuando exista, propone filas. No publica.

### 12. 512 y 1024 no se mezclan

El compilador solo acepta vectores `BioCLIP-1-frozen` de dimensión 512. BioCLIP 2.5 (1024) audita rechazos en el PC. Un solo espacio mantiene comparables los centroides de todos los paquetes futuros.

### 13. El JSON y el ONNX no comparten cifra

El Admin muestra dos artefactos distintos. El error a evitar es pintar ~100 MB en la ficha del paquete.

| Artefacto | Qué se muestra |
| --- | --- |
| `bioclip_v1.onnx` | **165,6 MB** medidos. Latencia **403 ms** a 1 hilo y **154 ms** a 4 hilos. |
| JSON de la subregión | Los bytes del archivo compilado. Una subregión de 55 especies son **55 KiB** de centroides. La matriz default suma **64 KiB**. El orden real es de decenas a unos pocos cientos de KiB, no megabytes. |

«100 MB» en las notas apunta al encoder, y ni siquiera coincide con los 165,6 MB medidos. «Menos de 150 ms» sigue siendo objetivo, no la ficha del modelo actual.

### 14. Seis estados, dentro de un resultado que se explica

Los seis códigos son estados del motor. `OSR_GEO` no compite con `MATCH_SPECIES` como si fueran la misma clase de acierto: es un desenlace que tiene que mostrar la evidencia.

```text
IdentificationResult
├── status
│   ├── MATCH_SPECIES
│   ├── MATCH_GENUS
│   ├── MATCH_FAMILY
│   ├── OSR_GLOBAL
│   ├── OSR_CLUSTER
│   └── OSR_GEO
├── candidate
├── confidence
├── evidence
├── geographic_context
└── provenance
```

| Estado | Qué significa |
| --- | --- |
| `MATCH_SPECIES` | Especie aceptada |
| `MATCH_GENUS` | Solo género |
| `MATCH_FAMILY` | Solo familia |
| `OSR_GLOBAL` | Lejos de todo centroide del paquete |
| `OSR_CLUSTER` | Intruso de complejo. Puede llevar género o familia en `candidate` |
| `OSR_GEO` | La política geográfica del paquete no dejó pasar esa especie |

`geographic_context` guarda altitud leída, si era estimada, `P(altitud)`, `umbral_geo` y la política aplicada (rechazo o penalización). Así el modo herpetólogo ve por qué se llegó a `OSR_GEO`, incluido un GPS dudoso o un borde de distribución. `provenance` dice paquete, encoder, experimento y versión. `00_MATCH_OK` y `STATUS_GENUS_SP` se leen como estos estados. No hay un segundo enum.

### 15. El compilador sigue al documento maestro

Familia, género, especie y `cryptic_clusters` en un JSON por subregión. La estrategia de arquitectura se conserva como variante histórica. Sus nombres `cryptic_groups` y su `rejection_tau: 0,32` no salen del compilador.

El super-centroide de género es la suma L2 de los centroides de sus especies. El de familia es la suma L2 de los de sus géneros, **un voto por género**. Sin `genus_weight`: un género de cuarenta especies no debe aplastar a uno de dos, y no hay datos para aprender pesos.

### 16. El worker calcula. No decide ciencia

El worker sí produce embeddings, centroides, scores, umbrales propuestos, métricas, artefactos y la compilación del paquete.

El worker no crea una especie, no declara que dos especies forman un complejo, no cambia pesos científicos, no declara un morfo y no aprueba la publicación científica.

```text
Worker
  → resultado técnico
  → Herpetólogo (validación científica)
  → Administrador (validación técnica)
  → Release
```

Estados del release: `DRAFT` → `VALIDATING` → `READY` → `APPROVED` → `PUBLISHED`, más `ROLLED_BACK`. El sandbox no escribe en el paquete publicado.

### 17. El Admin muestra el ciclo, no solo el paquete

El módulo no es un empaquetador. La interfaz recorre:

```text
Dataset → Curación → Taxonomía → Individuos → Observaciones → Imágenes
  → Embeddings → Centroides → Morfos → Clústeres → Contexto geográfico
  → OSR → Validación → Experimento → Paquete
  → Aprobación científica → Aprobación técnica → Release
```

Grafana no forma parte del algoritmo. Es infraestructura de observabilidad, detrás de la UI técnica. La UI científica dibuja con ECharts. Ver [[Observabilidad y Simulador]].

La tabla que dice «Fase 1 (Listo)» es un presupuesto (consulta a 0 USD, proxy del orden de 3–8 USD/mes). No es evidencia de que el worker exista.

Los nombres de los JSON de ejemplo, incluido `Pristimantis_belmet`, no se dan de alta solos.

## 18. Qué se acepta de la revisión posterior, y qué no

La revisión que compara este cierre con el borrador anterior acierta en seis puntos, y en dos deshace correcciones ya hechas.

| Punto | Qué pasa con él |
| --- | --- |
| 9 JSON, filtro térmico en memoria | Queda. La cifra fina es **55 KiB**, no ~56 KB. |
| Train/test por individuo | Queda. |
| Centroide prestado bajo 3 individuos | Queda. |
| No mostrar ~100 MB como si fuera el paquete | Queda. El paquete va en KiB. El ONNX va en 165,6 MB. |
| Seis estados canónicos | Quedan, dentro de `IdentificationResult`. `OSR_GEO` no es un acierto más. |
| Doble aval antes del OTA | Queda. |
| Coseno en el teléfono, Weibull en el PC | Queda. Mahalanobis no viaja. |
| Encoder congelado | Queda. |
| Audio, YOLO, scraper y la app fuera del ciclo de centroides | Queda. |
| Partir el clúster solo al pasar de 12 | No queda. `MAX_CLUSTER_SPECIES` avisa. Divide el herpetólogo. |
| `P < 0,05` como freno inflexible | No queda. 0,05 es el valor inicial de `umbral_geo`. La política del paquete elige rechazo o penalización. |

## Qué queda aplazado a propósito

GAN, MC Dropout, ensambles y OpenMax en el móvil. Covarianza de Mahalanobis dentro del APK. Fine-tuning del ViT. Treinta y seis paquetes por piso térmico. Publicación automática. Métricas inventadas.

Esas piezas no mejoran el siguiente resultado útil, que es un paquete versionado, simulado y aprobado. Si un experimento del simulador demuestra que otra calibración baja el FAR sin subir el rechazo de especies conocidas, se cambia el calibrador del Admin. El contrato del teléfono sigue siendo un coseno y un corte.
