---
title: "Pipeline del Sistema"
proyecto: Anura
tipo: metodologÃ­a
estado: redactado
tags: [anura, metodologÃ­a, pipeline, arquitectura]
---

# Pipeline del Sistema

[[Anura â€” Ãndice General]] Â· [[Arquitectura Multimodal]] Â· [[Modelo de VisiÃ³n â€” BioCLIP]] Â· [[Open-Set Recognition]] Â· [[App MÃ³vil]]

> [!abstract] QuÃ© describe esta nota
> El recorrido completo de una observaciÃ³n, desde que el usuario pulsa el obturador hasta que ve un resultado explicado. Es la vista que integra todas las piezas tÃ©cnicas; cada bloque enlaza a su nota detallada.

## 1. Flujo extremo a extremo

```
                        ðŸ“· CAPTURA
              imagen(es) + audio? + GPS/altitud/fecha
                             â”‚
                             â–¼
  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
  â”‚ 1. PREPROCESADO                                      â”‚
  â”‚    imagen: escala 224Ã—224, normalizaciÃ³n             â”‚
  â”‚    audio:  WAV mono 44.1 kHz â†’ mel-espectrograma     â”‚
  â”‚    guardar en local ANTES de inferir (RNF-11)        â”‚
  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                              â–¼
  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
  â”‚ 2. SEGMENTACIÃ“N ANATÃ“MICA  (modelo universal)        â”‚
  â”‚    detecta anuro_completo + 15 regiones              â”‚
  â”‚    â†’ mÃ¡scaras, caja del individuo, regiones visibles â”‚
  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                              â”‚  Â¿hay anuro?
                    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                   no                   sÃ­
                    â”‚                    â”‚
        "No se detectÃ³ un anuro"         â–¼
                        â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                        â”‚ 3. EXTRACCIÃ“N DE CARACTERÃSTICAS â”‚
                        â”‚    recorte â†’ BioCLIP â†’ embedding â”‚
                        â”‚    audio â†’ modelo acÃºstico       â”‚
                        â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                        â–¼
        â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
        â–¼                     â–¼                      â–¼                  â–¼
 4a. CLASIFICACIÃ“N     4b. BÃšSQUEDA         4c. ATRIBUTOS       4d. CONTEXTO
   jerÃ¡rquica            VECTORIAL           morfolÃ³gicos        geogrÃ¡fico
 Familiaâ†’GÃ©neroâ†’        Top-K vecinos       por regiÃ³n vs.      GPS, altitud,
   Especie              similares           plantilla especie   fecha, hÃ¡bitat
        â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                        â–¼
  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
  â”‚ 5. FUSIÃ“N MULTIMODAL                                 â”‚
  â”‚    combina puntuaciones â†’ ranking Top-3              â”‚
  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                              â–¼
  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
  â”‚ 6. VERIFICACIÃ“N OPEN-SET                             â”‚
  â”‚    Â¿la evidencia es suficiente para afirmar especie? â”‚
  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
              â–¼                              â–¼
      IDENTIFICADA                    âš ï¸ NO REGISTRADA
              â”‚                              â”‚
              â–¼                              â–¼
  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
  â”‚ 7. SALIDA                                            â”‚
  â”‚    Top-3 + evidencia por regiÃ³n + vecinos similares  â”‚
  â”‚    + ficha tÃ©cnica + nivel de confianza              â”‚
  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## 2. Etapa por etapa

### 1 Â· Preprocesado

Lo importante aquÃ­ no es tÃ©cnico sino de orden de operaciones: **la observaciÃ³n se persiste antes de inferir**. En campo, el dato es irrepetible; el resultado del modelo siempre se puede recalcular. Ver [[App MÃ³vil]] Â§3.

Especificaciones de captura (definidas en [[Estrategia de ConstrucciÃ³n del Dataset]]): imagen a 1024Ã—768 WebP 80 % para almacenamiento, escalada en memoria a 224Ã—224 para el modelo; audio WAV mono 44,1 kHz, 3â€“5 s, SNR â‰¥ 15 dB.

### 2 Â· SegmentaciÃ³n anatÃ³mica

Modelo universal de anuros, no un segmentador por especie. Responde *dÃ³nde estÃ¡ cada regiÃ³n*, no *quÃ© especie es*. Entrenado con las anotaciones de la [[GuÃ­a CVAT â€” Ãndice|guÃ­a CVAT]] (16 etiquetas con sus atributos).

Salidas que consumen las etapas siguientes:

- **Caja/mÃ¡scara de `anuro_completo`** â†’ recorte para BioCLIP.
- **MÃ¡scaras por regiÃ³n** â†’ base de la explicaciÃ³n anatÃ³mica (RF-06).
- **Inventario de regiones visibles** â†’ alimenta la distinciÃ³n crÃ­tica entre *ausente* y *no observable*.

AquÃ­ tambiÃ©n se resuelve el RF-03 (multi-individuo): si hay varias instancias de `anuro_completo`, cada una sigue el resto del pipeline por separado.

### 3 Â· ExtracciÃ³n de caracterÃ­sticas

Ver [[Modelo de VisiÃ³n â€” BioCLIP]]. El recorte segmentado se convierte en un embedding de 512 dimensiones. El audio, si existe, produce su propio embedding por una rama independiente.

### 4 Â· Las cuatro fuentes de evidencia (en paralelo)

Esta es la parte que hace a Anura distinto de un clasificador. Ninguna de las cuatro decide sola:

| | QuÃ© aporta | Falla cuandoâ€¦ |
| --- | --- | --- |
| **4a ClasificaciÃ³n jerÃ¡rquica** | Probabilidad por Familia/GÃ©nero/Especie | La especie no estÃ¡ en el catÃ¡logo |
| **4b BÃºsqueda vectorial** | "Se parece a estas observaciones confirmadas" | El catÃ¡logo tiene pocos ejemplares de esa especie |
| **4c Atributos vs. plantilla** | Evidencia explicable carÃ¡cter a carÃ¡cter | La regiÃ³n no es visible en la foto |
| **4d Contexto geogrÃ¡fico** | Compatibilidad con la distribuciÃ³n conocida | Los mapas de distribuciÃ³n estÃ¡n incompletos |

**4c** merece detalle porque es el aporte metodolÃ³gico propio: los atributos observados (forma del hocico, orientaciÃ³n del ojo, palmeaduraâ€¦) se comparan con la ficha de caracteres fijos de cada especie candidata (Anexo C de la guÃ­a CVAT), produciendo cuatro veredictos posibles:

- âœ… **Compatible** â€” coincide con lo esperado
- âŒ **Contradictorio** â€” incompatible con la especie candidata
- â“ **No observable** â€” la foto no permite evaluarlo
- âš ï¸ **Variable** â€” el carÃ¡cter varÃ­a dentro de la especie, poco peso como contradicciÃ³n

> [!important] "No observable" â‰  "ausente"
> Es la regla que mÃ¡s veces se rompe al implementar y la que mÃ¡s daÃ±o hace. Que no se vea la palmeadura no significa que la rana no la tenga. Un carÃ¡cter no observable **no puede penalizar** a un candidato; solo reduce la evidencia disponible. EstÃ¡ en las notas originales, en la guÃ­a CVAT y en el diseÃ±o del modelo: conviene que tambiÃ©n estÃ© explÃ­citamente en el cÃ³digo, como un tipo de dato con tres estados, no como un booleano.

### 5 Â· FusiÃ³n multimodal

Ver [[Arquitectura Multimodal]] Â§4. Regla de oro: **no se suman porcentajes**. Cada fuente entra con un peso calibrado empÃ­ricamente, y el sistema debe funcionar con fuentes ausentes (RNF-06).

### 6 Â· VerificaciÃ³n open-set

Ver [[Open-Set Recognition]]. La pregunta no es "Â¿cuÃ¡l de las N especies es?" sino "Â¿es alguna de las N?".

### 7 Â· Salida

Lo que ve el usuario, segÃºn los RF-05 y RF-06:

```
ðŸ¸ Boana cinereascens          Confianza: Alta

Top-3
  Boana cinereascens    87 %
  Boana lanciformis      8 %
  Scinax ruber           3 %

Evidencia anatÃ³mica
  âœ… RegiÃ³n timpÃ¡nica   compatible
  âœ… Hocico             compatible
  âœ… Palmeadura         compatible
  âŒ OrientaciÃ³n ocular incompatible
  â“ RegiÃ³n cloacal     no observable

Observaciones similares
  #1042  Boana cinereascens  0,94   Guaviare
  #0887  Boana cinereascens  0,92   Guaviare

ðŸ“ Compatible con la distribuciÃ³n conocida (SerranÃ­a de La Lindosa)
```

Que la evidencia contradictoria se muestre â€” y no se oculte â€” es parte del diseÃ±o: es lo que permite al herpetÃ³logo refutar el resultado (HU-03) y lo que convierte la app en una herramienta de apoyo y no en un orÃ¡culo.

## 3. Variantes segÃºn fase

| Etapa | Fase 1 (web) | Fase 2 (mÃ³vil offline) |
| --- | --- | --- |
| SegmentaciÃ³n | Servidor, modelo completo | Dispositivo, cuantizado |
| BioCLIP | Servidor (puede ser v2/ViT-L) | Dispositivo (v1/ViT-B cuantizado) |
| BÃºsqueda vectorial | Qdrant completo | Paquete regional embebido |
| Plantillas | Base de datos | Empaquetadas con la regiÃ³n |
| Contexto ambiental | API meteorolÃ³gica en vivo | Datos histÃ³ricos embarcados |
| Latencia objetivo | â‰¤ 3 s (RNF-01) | â‰¤ 4 s (RNF-02) |

## 4. Puntos de fallo y comportamiento esperado

| SituaciÃ³n | Comportamiento correcto |
| --- | --- |
| No se detecta ningÃºn anuro | Mensaje claro; no forzar una identificaciÃ³n |
| Imagen borrosa / mal iluminada | Sugerir repetir la toma (HU-01, caso 2) |
| Solo se ve una parte del animal | Identificar con la evidencia disponible y declarar quÃ© no se pudo evaluar |
| Sin GPS | Continuar sin el factor contexto (RNF-06) |
| Sin audio | Continuar solo con visiÃ³n |
| Ninguna especie supera el umbral | âš ï¸ "Posible especie no registrada" + Top-K de referencia |
| Varios individuos | Un resultado independiente por individuo (RF-03) |

## 5. QuÃ© falta por decidir o medir

- [ ] Fijar el modelo de segmentaciÃ³n concreto y su formato de exportaciÃ³n desde CVAT.
- [ ] Definir los pesos de fusiÃ³n y su procedimiento de calibraciÃ³n.
- [ ] Implementar el tipo de dato de tres estados para los caracteres.
- [ ] Medir la latencia real por etapa en el dispositivo de referencia.



