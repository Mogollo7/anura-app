---
title: "Pipeline del Sistema"
proyecto: Anura
tipo: metodología
estado: redactado
tags: [anura, metodología, pipeline, arquitectura]
---

# Pipeline del Sistema

[[Anura â€” àndice General]] · [[Arquitectura Multimodal]] · [[Modelo de Visión â€” BioCLIP]] · [[Open-Set Recognition]] · [[App Móvil]]

> [!abstract] Qué describe esta nota
> El recorrido completo de una observación, desde que el usuario pulsa el obturador hasta que ve un resultado explicado. Es la vista que integra todas las piezas técnicas; cada bloque enlaza a su nota detallada.

## 1. Flujo extremo a extremo

```
                        ðŸ“· CAPTURA
              imagen(es) + audio? + GPS/altitud/fecha
                             â”‚
                             â–¼
  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
  â”‚ 1. PREPROCESADO                                      â”‚
  â”‚    imagen: escala 224à—224, normalización             â”‚
  â”‚    audio:  WAV mono 44.1 kHz â†’ mel-espectrograma     â”‚
  â”‚    guardar en local ANTES de inferir (RNF-11)        â”‚
  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                              â–¼
  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
  â”‚ 2. SEGMENTACIà“N ANATà“MICA  (modelo universal)        â”‚
  â”‚    detecta anuro_completo + 15 regiones              â”‚
  â”‚    â†’ máscaras, caja del individuo, regiones visibles â”‚
  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                              â”‚  ¿hay anuro?
                    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                   no                   sí
                    â”‚                    â”‚
        "No se detectó un anuro"         â–¼
                        â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                        â”‚ 3. EXTRACCIà“N DE CARACTERàSTICAS â”‚
                        â”‚    recorte â†’ BioCLIP â†’ embedding â”‚
                        â”‚    audio â†’ modelo acàºstico       â”‚
                        â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                        â–¼
        â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
        â–¼                     â–¼                      â–¼                  â–¼
 4a. CLASIFICACIà“N     4b. BàšSQUEDA         4c. ATRIBUTOS       4d. CONTEXTO
   jerárquica            VECTORIAL           morfológicos        geográfico
 Familiaâ†’Géneroâ†’        Top-K vecinos       por región vs.      GPS, altitud,
   Especie              similares           plantilla especie   fecha, hábitat
        â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                        â–¼
  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
  â”‚ 5. FUSIà“N MULTIMODAL                                 â”‚
  â”‚    combina puntuaciones â†’ ranking Top-3              â”‚
  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                              â–¼
  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
  â”‚ 6. VERIFICACIà“N OPEN-SET                             â”‚
  â”‚    ¿la evidencia es suficiente para afirmar especie? â”‚
  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
              â–¼                              â–¼
      IDENTIFICADA                    âš ï¸ NO REGISTRADA
              â”‚                              â”‚
              â–¼                              â–¼
  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
  â”‚ 7. SALIDA                                            â”‚
  â”‚    Top-3 + evidencia por región + vecinos similares  â”‚
  â”‚    + ficha técnica + nivel de confianza              â”‚
  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## 2. Etapa por etapa

### 1 · Preprocesado

Lo importante aquí no es técnico sino de orden de operaciones: **la observación se persiste antes de inferir**. En campo, el dato es irrepetible; el resultado del modelo siempre se puede recalcular. Ver [[App Móvil]] §3.

Especificaciones de captura (definidas en [[Estrategia de Construcción del Dataset]]): imagen a 1024à—768 WebP 80 % para almacenamiento, escalada en memoria a 224à—224 para el modelo; audio WAV mono 44,1 kHz, 3â€“5 s, SNR â‰¥ 15 dB.

### 2 · Segmentación anatómica

Modelo universal de anuros, no un segmentador por especie. Responde *dónde está cada región*, no *qué especie es*. Entrenado con las anotaciones de la [[Guía CVAT â€” àndice|guía CVAT]] (16 etiquetas con sus atributos).

Salidas que consumen las etapas siguientes:

- **Caja/máscara de `anuro_completo`** â†’ recorte para BioCLIP.
- **Máscaras por región** â†’ base de la explicación anatómica (RF-06).
- **Inventario de regiones visibles** â†’ alimenta la distinción crítica entre *ausente* y *no observable*.

Aquí también se resuelve el RF-03 (multi-individuo): si hay varias instancias de `anuro_completo`, cada una sigue el resto del pipeline por separado.

### 3 · Extracción de características

Ver [[Modelo de Visión â€” BioCLIP]]. El recorte segmentado se convierte en un embedding de 512 dimensiones. El audio, si existe, produce su propio embedding por una rama independiente.

### 4 · Las cuatro fuentes de evidencia (en paralelo)

Esta es la parte que hace a Anura distinto de un clasificador. Ninguna de las cuatro decide sola:

| | Qué aporta | Falla cuandoâ€¦ |
| --- | --- | --- |
| **4a Clasificación jerárquica** | Probabilidad por Familia/Género/Especie | La especie no está en el catálogo |
| **4b Bàºsqueda vectorial** | "Se parece a estas observaciones confirmadas" | El catálogo tiene pocos ejemplares de esa especie |
| **4c Atributos vs. plantilla** | Evidencia explicable carácter a carácter | La región no es visible en la foto |
| **4d Contexto geográfico** | Compatibilidad con la distribución conocida | Los mapas de distribución están incompletos |

**4c** merece detalle porque es el aporte metodológico propio: los atributos observados (forma del hocico, orientación del ojo, palmeaduraâ€¦) se comparan con la ficha de caracteres fijos de cada especie candidata (Anexo C de la guía CVAT), produciendo cuatro veredictos posibles:

- âœ… **Compatible** â€” coincide con lo esperado
- âŒ **Contradictorio** â€” incompatible con la especie candidata
- â“ **No observable** â€” la foto no permite evaluarlo
- âš ï¸ **Variable** â€” el carácter varía dentro de la especie, poco peso como contradicción

> [!important] "No observable" â‰  "ausente"
> Es la regla que más veces se rompe al implementar y la que más daño hace. Que no se vea la palmeadura no significa que la rana no la tenga. Un carácter no observable **no puede penalizar** a un candidato; solo reduce la evidencia disponible. Está en las notas originales, en la guía CVAT y en el diseño del modelo: conviene que también esté explícitamente en el código, como un tipo de dato con tres estados, no como un booleano.

### 5 · Fusión multimodal

Ver [[Arquitectura Multimodal]] §4. Regla de oro: **no se suman porcentajes**. Cada fuente entra con un peso calibrado empíricamente, y el sistema debe funcionar con fuentes ausentes (RNF-06).

### 6 · Verificación open-set

Ver [[Open-Set Recognition]]. La pregunta no es "¿cuál de las N especies es?" sino "¿es alguna de las N?".

### 7 · Salida

Lo que ve el usuario, segàºn los RF-05 y RF-06:

```
ðŸ¸ Boana cinereascens          Confianza: Alta

Top-3
  Boana cinereascens    87 %
  Boana lanciformis      8 %
  Scinax ruber           3 %

Evidencia anatómica
  âœ… Región timpánica   compatible
  âœ… Hocico             compatible
  âœ… Palmeadura         compatible
  âŒ Orientación ocular incompatible
  â“ Región cloacal     no observable

Observaciones similares
  #1042  Boana cinereascens  0,94   Guaviare
  #0887  Boana cinereascens  0,92   Guaviare

ðŸ“ Compatible con la distribución conocida (Serranía de La Lindosa)
```

Que la evidencia contradictoria se muestre â€” y no se oculte â€” es parte del diseño: es lo que permite al herpetólogo refutar el resultado (HU-03) y lo que convierte la app en una herramienta de apoyo y no en un oráculo.

## 3. Variantes segàºn fase

| Etapa | Fase 1 (web) | Fase 2 (móvil offline) |
| --- | --- | --- |
| Segmentación | Servidor, modelo completo | Dispositivo, cuantizado |
| BioCLIP | Servidor (puede ser v2/ViT-L) | Dispositivo (v1/ViT-B cuantizado) |
| Bàºsqueda vectorial | Qdrant completo | Paquete regional embebido |
| Plantillas | Base de datos | Empaquetadas con la región |
| Contexto ambiental | API meteorológica en vivo | Datos históricos embarcados |
| Latencia objetivo | â‰¤ 3 s (RNF-01) | â‰¤ 4 s (RNF-02) |

## 4. Puntos de fallo y comportamiento esperado

| Situación | Comportamiento correcto |
| --- | --- |
| No se detecta ningàºn anuro | Mensaje claro; no forzar una identificación |
| Imagen borrosa / mal iluminada | Sugerir repetir la toma (HU-01, caso 2) |
| Solo se ve una parte del animal | Identificar con la evidencia disponible y declarar qué no se pudo evaluar |
| Sin GPS | Continuar sin el factor contexto (RNF-06) |
| Sin audio | Continuar solo con visión |
| Ninguna especie supera el umbral | âš ï¸ "Posible especie no registrada" + Top-K de referencia |
| Varios individuos | Un resultado independiente por individuo (RF-03) |

## 5. Qué falta por decidir o medir

- [ ] Fijar el modelo de segmentación concreto y su formato de exportación desde CVAT.
- [ ] Definir los pesos de fusión y su procedimiento de calibración.
- [ ] Implementar el tipo de dato de tres estados para los caracteres.
- [ ] Medir la latencia real por etapa en el dispositivo de referencia.



