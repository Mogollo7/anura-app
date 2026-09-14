---
title: "Cronograma y Plan de Trabajo"
proyecto: Anura
tipo: proyecto
estado: sprint-27-sep-fijado
tags: [anura, cronograma, planificación]
---

# Cronograma y Plan de Trabajo

[[Anura â€” àndice General]] · [[Roadmap y Fases]] · [[Riesgos del Proyecto]] · [[Experimentos y Resultados]]

> [!important] Fecha límite fijada: prototipo listo y desplegado el 27 de septiembre de 2026
> El autor fijó el plazo el 2026-09-05: **22 días** para un prototipo funcional de extremo a extremo, desplegado (APK instalable + demo web) â€” no el documento de grado completo ni la sustentación. Eso cambia el cronograma de fondo: H12â€“H15 (piloto de campo con â‰¥ 150 observaciones, documento final, sustentación) **no caben** en 22 días y quedan fuera de este sprint. Lo que sigue mantiene la estructura completa de hitos del trabajo de grado, con el sprint del prototipo superpuesto en §0.

## 0. Sprint al prototipo (05â€“27 de septiembre de 2026)

> [!abstract] Qué significa "prototipo listo y desplegado" aquí
> Extremo a extremo, sobre el catálogo de **28 especies** (C-3 resuelta â†’ [[Inconsistencias y Decisiones Pendientes]]): foto(s) â†’ segmentación â†’ BioCLIP **v1** â†’ Top-3 â†’ evidencia anatómica ("por qué") â†’ bàºsqueda vectorial local â†’ contexto geográfico, funcionando **offline en un APK** y en paralelo como demo web. Audio y multi-individuo son condicionales (puntos Go/No-Go abajo). Piloto de campo, documento final y sustentación quedan para después del 27 â€” ver §2.

### Calendario día a día

> [!tip] Cómo leer esta tabla
> Cada día tiene un **objetivo** (qué debe quedar cerrado hoy), **qué aprender** (para que el sprint también sea formativo, no solo ejecución) y un **entregable concreto** (verificable, no "avanzar en..."). El diseño de la app (pantallas, marca, logo) se planifica primero como mockup y se aprueba **sección por sección** antes de pasar cada pantalla a código Kotlin â€” así no se escribe UI dos veces.

#### Semana 1 · Cimientos, diseño y arranque en paralelo

| Fecha  | Día       | Objetivo del día                                                      | Tareas clave                                                                                                                                                                                                                           | Qué aprender hoy                                                                  | Entregable                                                                                                          |
| ------ | --------- | --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| 05 sep | Sáb (hoy) | Cerrar decisiones bloqueantes y arrancar el diseño                    | 28 especies (C-3), BioCLIP v1, alcance del prototipo cerrados; iniciar mockup de la **pantalla de carga** con el logo y color de marca ya definidos                                                                                    | Principios básicos de jerarquía visual y tipografía (HIG)                         | [[Inconsistencias y Decisiones Pendientes]] actualizado + brief de diseño + mockup de pantalla de carga en revisión |
| 06 sep | Dom       | Asegurar BioCLIP v1 + mockup de login/logout                          | Descargar y verificar pesos BioCLIP v1 (`imageomics/bioclip`, HF) y su licencia; backup inmediato de fotos/anotaciones (riesgo D-6); mockup de **login** y **logout**                                                                  | Cómo se cargan checkpoints de Hugging Face con `open_clip`                        | Pesos BioCLIP v1 verificados + backup hecho + mockup login/logout para aprobar                                      |
| 07 sep | Lun       | Congelar el dataset + mockup de captura                               | `GroupSplit` por individuo sobre las 28 especies (70 individuos/especie para identificación); marcar huecos por especie; mockup de **pantalla de captura** (cámara, obturador, controles a una mano)                                   | Qué es `GroupSplit`/`GroupKFold` y por qué evita fuga de información              | Split v1 congelado y versionado + mockup de captura para aprobar                                                    |
| 08 sep | Mar       | Línea base del modelo + script de conversión de segmentación          | Extraer embeddings BioCLIP v1 zero-shot (sin entrenar) sobre el dataset congelado; escribir y probar `convertir_cvat_a_yolo.py` con los datos parciales de segmentación ya anotados (25â€“30/especie)                                    | Cómo funciona la clasificación zero-shot con modelos tipo CLIP (prompts de texto) | Línea base zero-shot medida + script de conversión CVATâ†’YOLO probado                                                |
| 09 sep | Mié       | **Llegada de los datos de segmentación** (comprometida por el equipo) | Disparar el entrenamiento automatizado en cuanto llegue el export de CVAT â†’ [[Automatización del Entrenamiento de Segmentación]]; mientras entrena, iniciar el proyecto Gradle/Kotlin real con las pantallas ya aprobadas en el mockup | Estructura de un proyecto Gradle Kotlin + Compose (módulos, version catalog)      | Entrenamiento de segmentación lanzado + proyecto Android inicializado                                               |
| 10 sep | Jue       | Supervisar segmentación + implementar pantallas de captura            | Revisar métricas y muestras del segmentador (solo supervisión, no reentrenar a mano); implementar en Compose las pantallas de Captura y Confirmación siguiendo el mockup ya aprobado                                                   | CameraX básico: preview + captura de foto                                         | Reporte de métricas de segmentación v1 + pantallas de captura funcionando (sin modelo aàºn)                          |
| 11 sep | Vie       | Cierre de semana 1                                                    | Aprobar/promover el modelo de segmentación v1; Room (`Observacion`+`Foto`) y Listado funcionando; investigar cobertura de AnuraSet/Xeno-canto para las 28 especies                                                                     | Room: `@Entity`/`@Dao`/`@Database` en Kotlin                                      | Segmentación v1 lista + esqueleto Android con captura â†’ guardado â†’ listado, sin red ni modelo de identificación     |

#### Semana 2 · Nàºcleo de identificación y optimización móvil

| Fecha | Día | Objetivo del día | Tareas clave | Qué aprender hoy | Entregable |
| --- | --- | --- | --- | --- | --- |
| 12 sep | Sáb | Cabezas de clasificación jerárquica | Entrenar Familia/Género/Especie sobre embeddings cacheados, usando el recorte segmentado (variante C, la de la Etapa I) | Qué es un *linear probe* sobre embeddings congelados | Métricas Top-1/Top-3 iniciales del modelo de identificación |
| 13 sep | Dom | Cuantización | BioCLIP v1: INT8 pesos + FP16 activaciones; segmentador: INT8; medir Î” F1 en ambos | Qué hacen la cuantización INT8 y FP16 a un modelo, y por qué las activaciones del ViT son más sensibles | Modelos cuantizados + tabla de degradación medida |
| 14 sep | Lun | Conversión + mockup de resultado | Exportar a LiteRT y probar ONNX Runtime Mobile en paralelo con el ViT; mockup de la **pantalla de resultado** (Top-3 + evidencia anatómica "por qué") | Diferencias prácticas entre LiteRT y ONNX Runtime Mobile | Ruta de conversión elegida + mockup de resultado para aprobar |
| 15 sep | Mar | ObjectBox embebido | Integrar ObjectBox en el dispositivo con un paquete simulado (10â€“50 k vectores); medir latencia y memoria | Qué es HNSW y cómo lo implementa ObjectBox embebido | ObjectBox funcionando en el dispositivo de prueba, con cifras medidas |
| 16 sep | Mié | Paquetes geográficos reales | Generar `manifest.json` + `vectors.bin` + `payload.db` + fichas para Antioquia y Guaviare | Por qué normalizar L2 y usar distancia coseno para embeddings | Dos paquetes regionales generados y descargables |
| 17 sep | Jue | Open-set mínimo viable | Distancia a centroide + *temperature scaling*; fijar el umbral en validación | Qué miden AUROC y FPR@95TPR, y por qué accuracy no aplica aquí | Detector open-set con umbral fijado y congelado |
| 18 sep | Vie | UI de resultado real + decisión de audio | Implementar en Compose la pantalla de resultado con datos reales del modelo (ya no mockup); **punto Go/No-Go de audio**: decidir cobertura AnuraSet/Xeno-canto para las 28 especies | Cómo representar en UI los tres estados "presente / ausente / no observable" sin reducirlos a un booleano | Pantalla de resultado funcionando con el modelo real + decisión de audio registrada |

#### Semana 3 · Integración, medición y despliegue

| Fecha | Día | Objetivo del día | Tareas clave | Qué aprender hoy | Entregable |
| --- | --- | --- | --- | --- | --- |
| 19 sep | Sáb | Pipeline completo en el dispositivo | Conectar captura â†’ segmentación â†’ BioCLIP â†’ clasificación â†’ ObjectBox â†’ contexto geográfico â†’ open-set â†’ resultado, todo dentro del APK | Cómo perfilar latencia por etapa en Android (Profiler) | Primer recorrido end-to-end funcionando en el dispositivo (aunque sea lento o con errores) |
| 20 sep | Dom | Multi-foto real + decisión multi-individuo | Implementar agregación de varias vistas (dorsal/ventral/lateral) por observación (RF-02); decidir si multi-individuo (RF-03, opcional) entra o queda fuera del prototipo | Por qué no promediar embeddings de vistas distintas ([[Arquitectura Multimodal]] §1.1) | Multi-foto funcionando + decisión de multi-individuo documentada |
| 21 sep | Lun | Medición real | Latencia p95, memoria pico y batería en un dispositivo de referencia real de gama media/baja | Cómo medir consumo de batería real de una app Android | Tabla de [[Optimización para Inferencia en Móvil]] §5 rellena con datos reales |
| 22 sep | Mar | Demo web de respaldo | API `/identify` con FastAPI + Qdrant en servidor; fichas técnicas; desplegar en capa gratuita | Despliegue básico de FastAPI en una capa gratuita (Render/Fly.io/Railway) | Demo web desplegada y accesible por URL |
| 23 sep | Mié | Pulido de UI y modo campo | Modo oscuro/alto contraste real (RNF-07), controles a una mano (RNF-08), feedback háptico | Cómo maneja Compose los temas claro/oscuro dinámicos correctamente | UI pulida cumpliendo RNF-07/RNF-08 |
| 24 sep | Jue (colchón) | Pruebas reales y corrección de errores | Probar el flujo completo repetidamente, anotar fallos, corregir por prioridad | â€” (foco en estabilidad, no en aprendizaje nuevo) | Lista de errores conocidos cerrada o triageada |
| 25 sep | Vie (colchón) | Empaquetado | Firmar el APK; decidir canal (testing interno de Play o APK directo); instalación limpia probada | Firma de APK / `bundletool` si se usa AAB | APK instalable, probado en un dispositivo limpio |
| 26 sep | Sáb (colchón) | Ensayo general | Recorrido completo como si fuera la entrega real; preparar un guion breve de demo | â€” | Ensayo exitoso + guion de demo listo |
| **27 sep** | **Dom** | **Entrega del prototipo** | Despliegue final; verificar que APK + demo web funcionan de extremo a extremo sobre las 28 especies | â€” | **Prototipo entregado: APK + demo web** |

> [!warning] Qué queda explícitamente fuera del 27 de septiembre
> Piloto de campo con â‰¥ 150 observaciones validadas por experto (H12), documento final de trabajo de grado (H14), sustentación (H15), exportación Darwin Core completa (HU-05), módulo comunitario a escala, iOS. Son la continuación natural en la sección 2 de abajo â€” no se pierden, se secuencian después del prototipo.

## 1. Parámetros fijados

| Parámetro | Valor |
| --- | --- |
| Fecha de inicio del sprint | 2026-09-05 |
| Fecha de entrega del prototipo (fijada por el autor) | **2026-09-27** |
| Fecha de entrega del documento de grado | *(por fijar por el equipo â€” no depende del sprint del prototipo)* |
| Fecha de sustentación | *(por fijar por el equipo)* |
| Integrantes y dedicación semanal | *(por fijar â€” el sprint asume trabajo paralelo en â‰¥ 3 frentes: modelo, móvil, backend)* |
| Ventana(s) de salida de campo | *(por fijar â€” el piloto de campo queda fuera del sprint del prototipo)* |
| Disponibilidad del herpetólogo validador | *(por fijar)* |
| Restricciones estacionales (época de lluvias / actividad reproductiva) | No aplica a este sprint (no hay salida de campo prevista antes del 27 sep) |

> [!tip] La estacionalidad sigue mandando sobre el resto del cronograma
> Aunque no afecta al sprint del prototipo, sí afecta al piloto de campo (H12) que viene después: los anuros tienen picos de actividad reproductiva asociados a las lluvias, y esa ventana no se puede mover libremente. Conviene fijarla cuanto antes, en paralelo a este sprint.

## 2. Hitos

| # | Hito | Entregable verificable | Depende de | Fecha | Responsable | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| **H1** | Marco teórico y metodológico cerrado | Documento con introducción, referente teórico, objetivos y metodología | â€” | ya cerrado | | âœ… en gran parte |
| **H2** | Decisiones de arquitectura fijadas | [[Inconsistencias y Decisiones Pendientes]] resuelto | H1 | 2026-09-06 | | ðŸŸ¡ nàºcleo cerrado 2026-09-05 (C-3, BioCLIP v1, alcance) |
| **H3** | Dataset v1 consolidado y verificado | Split congelado, verificación taxonómica, copias de seguridad | H1 | 2026-09-08 | | |
| **H4** | Esquema de anotación aplicado | â‰¥ 400â€“600 imágenes anotadas en CVAT | H3 | 2026-09-11 (entrega comprometida por el equipo) | | |
| **H5** | Modelo de segmentación v1 | Modelo entrenado + métricas | H4 | 2026-09-13 (automatizado â€” [[Automatización del Entrenamiento de Segmentación]]) | | |
| **H6** | Modelo de identificación v1 | BioCLIP + cabezas jerárquicas + métricas offline | H3, H5 | 2026-09-15 | | |
| **H7** | Open-set operativo (versión mínima) | Detector implementado + umbral fijado en validación | H6 | 2026-09-17 | | Mínimo viable para el sprint; AUROC/FPR95 completos quedan para H13 |
| **H8** | Backend + base vectorial | API funcional con `/identify` y repositorio | H6 | 2026-09-19 | | |
| **H9** | Plataforma web (Fase 1) | Demostrador web con Top-3 y fichas | H8 | 2026-09-23 | | |
| **H10** | Modelos optimizados para móvil | Modelos cuantizados dentro del presupuesto | H6, H7 | 2026-09-18 | | |
| **H11** | App móvil offline (prototipo) | APK con inferencia local; sincronización puede quedar mínima | H10, H8 | **2026-09-27** | | Entrega del sprint |
| **H12** | Piloto de campo | â‰¥ 150 observaciones con verdad experta | H11 | *posterior al 27 sep â€” por fijar* | | Fuera del sprint del prototipo |
| **H13** | Resultados consolidados | Todas las tablas de [[Métricas Offline]] rellenas | H12 | *posterior al 27 sep* | | |
| **H14** | Documento final | Trabajo de grado completo | H13 | *posterior al 27 sep* | | |
| **H15** | Sustentación | | H14 | *posterior al 27 sep* | | |

## 3. Ruta crítica

```
H3 dataset â”€â”€â–¶ H4 anotación â”€â”€â–¶ H5 segmentación â”€â”€â”
                                                   â”œâ”€â”€â–¶ H10 optimización â”€â”€â–¶ H11 app â”€â”€â–¶ H12 piloto â”€â”€â–¶ H13 â”€â”€â–¶ H14
                    H6 identificación â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**H4 (anotación) es el cuello de botella.** Es trabajo humano que no se acelera con más cómputo: cientos de imágenes segmentadas región por región segàºn la [[Guía CVAT â€” àndice|guía CVAT]]. La estrategia ya prevista de anotar 400â€“600 manualmente, entrenar V1, preanotar el resto y corregir es lo que hace viable el volumen â€” conviene no saltársela.

Si H4 se retrasa, se retrasa todo lo demás. Vale la pena sobredimensionar el equipo de anotación al inicio.

## 4. Paralelizables (para no encadenar todo)

Estas tareas no dependen de la ruta crítica y pueden avanzar simultáneamente:

- Redacción del documento (marco teórico ya está muy avanzado).
- Diseño de UI y prototipo de la app con datos simulados.
- Backend y esquema de base de datos (no necesita el modelo final).
- Fichas técnicas de especie y plantillas morfológicas (Anexo C).
- Trámite de permisos â†’ [[Consideraciones Ecológicas y Éticas]] (empezar cuanto antes: los tiempos administrativos no dependen del equipo).
- Montaje de copias de seguridad e infraestructura.

## 5. Seguimiento semanal

| Semana | Foco | Hecho | Bloqueos | Siguiente |
| --- | --- | --- | --- | --- |
| **1 (05â€“11 sep)** | Decisiones + diseño + arranque paralelo | **05 sep:** C-3 (28 especies), BioCLIP v1, alcance cerrado **06 sep:** âœ… Pesos BioCLIP v1 verificados, características óptimas definidas para su rol de teacher (ViT-B/16, ~86M params) **07 sep:** Especificación de componentes de UI completada (niveles 1â€“5, todos los mockups faltantes documentados) **08 sep:** âœ… Pivote de arquitectura on-device cerrado (C-5/C-6/C-7 en [[Inconsistencias y Decisiones Pendientes]]): BioCLIP-INT8 descartado por fracaso real, EdgeNeXt-Tiny destilado confirmado, SQLite/sqlite-vec reemplaza ObjectBox, audio con modelo propio, Galaxy A30 como dispositivo de referencia **11 sep:** âœ… Fase 4 (Transfer Learning) ejecutada, dos veces â€” variante C (segmentación binaria) probada y descartada por peor resultado (EXP-011); C-8 (MobileNetV3-Small), C-10 (destilación INVIABLE, 33pp de degradación) y C-11 (nueva arquitectura: BioCLIP fp16 completo, sin destilar) decididos el mismo día. âŒ Room + Listado Android, planeados para hoy, **no se hicieron** | Segmentador binario da peor resultado al escalar a 41 especies, causa sin diagnosticar; desarrollo Android sin arrancar | Android arranca el **lunes 14 sep**, no el 07-11 sep como preveía el plan â€” 3 días de desfase en ese frente, mientras que el modelo/optimización móvil (Fases 5-7c, 12 sep) va 2-3 días *adelantado* sobre la Semana 2 |
| **2 (12â€“18 sep)** | Nàºcleo de identificación y optimización móvil | **12 sep:** âœ… Fase 5 (evaluación completa 41 especies) + limpieza de dataset (fotos no representativas, coordenadas) + Fases 6-7c completas: encoder extraído, fp16/int8 comparados (int8 descartado en toda variante), ONNX exportado y validado (165,6 MB), RAM/latencia medidas en emulación de hilos, prior geográfico añadido (+15 a +25pp, no estaba en el plan original) + documentación consolidada en Obsidian | Discrepancia de catálogo sin resolver: el checkpoint entrenado usa 41 especies, no las 28 de C-3 | Desarrollo Android arranca el 14 sep â€” el trabajo de modelo va adelantado, pero corre el riesgo de tener que esperar si Android no alcanza a absorber esa ventaja antes del 27 |

## 6. Puntos de decisión

Momentos en que hay que decidir explícitamente si se continàºa o se recorta alcance. Definirlos ahora evita decidirlo tarde y a la fuerza (riesgo P-1 en [[Riesgos del Proyecto]]).

| Punto | Pregunta | Si la respuesta es noâ€¦ |
| --- | --- | --- |
| Tras H6 | ¿Se alcanzan las metas de precisión con solo visión? | Revisar dataset antes de añadir modalidades |
| Tras H6 | ¿Hay datos de audio suficientes? | Declarar la rama acàºstica como trabajo futuro |
| Tras H10 | ¿Los modelos caben y responden en el móvil? | Activar el plan B de [[Optimización para Inferencia en Móvil]] §6 |
| A mitad de plazo | ¿La Fase 2 es alcanzable? | Reducir a demostrador móvil y reforzar la Fase 1 |



