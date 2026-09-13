---
title: "Cronograma y Plan de Trabajo"
proyecto: Anura
tipo: proyecto
estado: sprint-27-sep-fijado
tags: [anura, cronograma, planificaciÃ³n]
---

# Cronograma y Plan de Trabajo

[[Anura â€” Ãndice General]] Â· [[Roadmap y Fases]] Â· [[Riesgos del Proyecto]] Â· [[Experimentos y Resultados]]

> [!important] Fecha lÃ­mite fijada: prototipo listo y desplegado el 27 de septiembre de 2026
> El autor fijÃ³ el plazo el 2026-09-05: **22 dÃ­as** para un prototipo funcional de extremo a extremo, desplegado (APK instalable + demo web) â€” no el documento de grado completo ni la sustentaciÃ³n. Eso cambia el cronograma de fondo: H12â€“H15 (piloto de campo con â‰¥ 150 observaciones, documento final, sustentaciÃ³n) **no caben** en 22 dÃ­as y quedan fuera de este sprint. Lo que sigue mantiene la estructura completa de hitos del trabajo de grado, con el sprint del prototipo superpuesto en Â§0.

## 0. Sprint al prototipo (05â€“27 de septiembre de 2026)

> [!abstract] QuÃ© significa "prototipo listo y desplegado" aquÃ­
> Extremo a extremo, sobre el catÃ¡logo de **28 especies** (C-3 resuelta â†’ [[Inconsistencias y Decisiones Pendientes]]): foto(s) â†’ segmentaciÃ³n â†’ BioCLIP **v1** â†’ Top-3 â†’ evidencia anatÃ³mica ("por quÃ©") â†’ bÃºsqueda vectorial local â†’ contexto geogrÃ¡fico, funcionando **offline en un APK** y en paralelo como demo web. Audio y multi-individuo son condicionales (puntos Go/No-Go abajo). Piloto de campo, documento final y sustentaciÃ³n quedan para despuÃ©s del 27 â€” ver Â§2.

### Calendario dÃ­a a dÃ­a

> [!tip] CÃ³mo leer esta tabla
> Cada dÃ­a tiene un **objetivo** (quÃ© debe quedar cerrado hoy), **quÃ© aprender** (para que el sprint tambiÃ©n sea formativo, no solo ejecuciÃ³n) y un **entregable concreto** (verificable, no "avanzar en..."). El diseÃ±o de la app (pantallas, marca, logo) se planifica primero como mockup y se aprueba **secciÃ³n por secciÃ³n** antes de pasar cada pantalla a cÃ³digo Kotlin â€” asÃ­ no se escribe UI dos veces.

#### Semana 1 Â· Cimientos, diseÃ±o y arranque en paralelo

| Fecha  | DÃ­a       | Objetivo del dÃ­a                                                      | Tareas clave                                                                                                                                                                                                                           | QuÃ© aprender hoy                                                                  | Entregable                                                                                                          |
| ------ | --------- | --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| 05 sep | SÃ¡b (hoy) | Cerrar decisiones bloqueantes y arrancar el diseÃ±o                    | 28 especies (C-3), BioCLIP v1, alcance del prototipo cerrados; iniciar mockup de la **pantalla de carga** con el logo y color de marca ya definidos                                                                                    | Principios bÃ¡sicos de jerarquÃ­a visual y tipografÃ­a (HIG)                         | [[Inconsistencias y Decisiones Pendientes]] actualizado + brief de diseÃ±o + mockup de pantalla de carga en revisiÃ³n |
| 06 sep | Dom       | Asegurar BioCLIP v1 + mockup de login/logout                          | Descargar y verificar pesos BioCLIP v1 (`imageomics/bioclip`, HF) y su licencia; backup inmediato de fotos/anotaciones (riesgo D-6); mockup de **login** y **logout**                                                                  | CÃ³mo se cargan checkpoints de Hugging Face con `open_clip`                        | Pesos BioCLIP v1 verificados + backup hecho + mockup login/logout para aprobar                                      |
| 07 sep | Lun       | Congelar el dataset + mockup de captura                               | `GroupSplit` por individuo sobre las 28 especies (70 individuos/especie para identificaciÃ³n); marcar huecos por especie; mockup de **pantalla de captura** (cÃ¡mara, obturador, controles a una mano)                                   | QuÃ© es `GroupSplit`/`GroupKFold` y por quÃ© evita fuga de informaciÃ³n              | Split v1 congelado y versionado + mockup de captura para aprobar                                                    |
| 08 sep | Mar       | LÃ­nea base del modelo + script de conversiÃ³n de segmentaciÃ³n          | Extraer embeddings BioCLIP v1 zero-shot (sin entrenar) sobre el dataset congelado; escribir y probar `convertir_cvat_a_yolo.py` con los datos parciales de segmentaciÃ³n ya anotados (25â€“30/especie)                                    | CÃ³mo funciona la clasificaciÃ³n zero-shot con modelos tipo CLIP (prompts de texto) | LÃ­nea base zero-shot medida + script de conversiÃ³n CVATâ†’YOLO probado                                                |
| 09 sep | MiÃ©       | **Llegada de los datos de segmentaciÃ³n** (comprometida por el equipo) | Disparar el entrenamiento automatizado en cuanto llegue el export de CVAT â†’ [[AutomatizaciÃ³n del Entrenamiento de SegmentaciÃ³n]]; mientras entrena, iniciar el proyecto Gradle/Kotlin real con las pantallas ya aprobadas en el mockup | Estructura de un proyecto Gradle Kotlin + Compose (mÃ³dulos, version catalog)      | Entrenamiento de segmentaciÃ³n lanzado + proyecto Android inicializado                                               |
| 10 sep | Jue       | Supervisar segmentaciÃ³n + implementar pantallas de captura            | Revisar mÃ©tricas y muestras del segmentador (solo supervisiÃ³n, no reentrenar a mano); implementar en Compose las pantallas de Captura y ConfirmaciÃ³n siguiendo el mockup ya aprobado                                                   | CameraX bÃ¡sico: preview + captura de foto                                         | Reporte de mÃ©tricas de segmentaciÃ³n v1 + pantallas de captura funcionando (sin modelo aÃºn)                          |
| 11 sep | Vie       | Cierre de semana 1                                                    | Aprobar/promover el modelo de segmentaciÃ³n v1; Room (`Observacion`+`Foto`) y Listado funcionando; investigar cobertura de AnuraSet/Xeno-canto para las 28 especies                                                                     | Room: `@Entity`/`@Dao`/`@Database` en Kotlin                                      | SegmentaciÃ³n v1 lista + esqueleto Android con captura â†’ guardado â†’ listado, sin red ni modelo de identificaciÃ³n     |

#### Semana 2 Â· NÃºcleo de identificaciÃ³n y optimizaciÃ³n mÃ³vil

| Fecha | DÃ­a | Objetivo del dÃ­a | Tareas clave | QuÃ© aprender hoy | Entregable |
| --- | --- | --- | --- | --- | --- |
| 12 sep | SÃ¡b | Cabezas de clasificaciÃ³n jerÃ¡rquica | Entrenar Familia/GÃ©nero/Especie sobre embeddings cacheados, usando el recorte segmentado (variante C, la de la Etapa I) | QuÃ© es un *linear probe* sobre embeddings congelados | MÃ©tricas Top-1/Top-3 iniciales del modelo de identificaciÃ³n |
| 13 sep | Dom | CuantizaciÃ³n | BioCLIP v1: INT8 pesos + FP16 activaciones; segmentador: INT8; medir Î” F1 en ambos | QuÃ© hacen la cuantizaciÃ³n INT8 y FP16 a un modelo, y por quÃ© las activaciones del ViT son mÃ¡s sensibles | Modelos cuantizados + tabla de degradaciÃ³n medida |
| 14 sep | Lun | ConversiÃ³n + mockup de resultado | Exportar a LiteRT y probar ONNX Runtime Mobile en paralelo con el ViT; mockup de la **pantalla de resultado** (Top-3 + evidencia anatÃ³mica "por quÃ©") | Diferencias prÃ¡cticas entre LiteRT y ONNX Runtime Mobile | Ruta de conversiÃ³n elegida + mockup de resultado para aprobar |
| 15 sep | Mar | ObjectBox embebido | Integrar ObjectBox en el dispositivo con un paquete simulado (10â€“50 k vectores); medir latencia y memoria | QuÃ© es HNSW y cÃ³mo lo implementa ObjectBox embebido | ObjectBox funcionando en el dispositivo de prueba, con cifras medidas |
| 16 sep | MiÃ© | Paquetes geogrÃ¡ficos reales | Generar `manifest.json` + `vectors.bin` + `payload.db` + fichas para Antioquia y Guaviare | Por quÃ© normalizar L2 y usar distancia coseno para embeddings | Dos paquetes regionales generados y descargables |
| 17 sep | Jue | Open-set mÃ­nimo viable | Distancia a centroide + *temperature scaling*; fijar el umbral en validaciÃ³n | QuÃ© miden AUROC y FPR@95TPR, y por quÃ© accuracy no aplica aquÃ­ | Detector open-set con umbral fijado y congelado |
| 18 sep | Vie | UI de resultado real + decisiÃ³n de audio | Implementar en Compose la pantalla de resultado con datos reales del modelo (ya no mockup); **punto Go/No-Go de audio**: decidir cobertura AnuraSet/Xeno-canto para las 28 especies | CÃ³mo representar en UI los tres estados "presente / ausente / no observable" sin reducirlos a un booleano | Pantalla de resultado funcionando con el modelo real + decisiÃ³n de audio registrada |

#### Semana 3 Â· IntegraciÃ³n, mediciÃ³n y despliegue

| Fecha | DÃ­a | Objetivo del dÃ­a | Tareas clave | QuÃ© aprender hoy | Entregable |
| --- | --- | --- | --- | --- | --- |
| 19 sep | SÃ¡b | Pipeline completo en el dispositivo | Conectar captura â†’ segmentaciÃ³n â†’ BioCLIP â†’ clasificaciÃ³n â†’ ObjectBox â†’ contexto geogrÃ¡fico â†’ open-set â†’ resultado, todo dentro del APK | CÃ³mo perfilar latencia por etapa en Android (Profiler) | Primer recorrido end-to-end funcionando en el dispositivo (aunque sea lento o con errores) |
| 20 sep | Dom | Multi-foto real + decisiÃ³n multi-individuo | Implementar agregaciÃ³n de varias vistas (dorsal/ventral/lateral) por observaciÃ³n (RF-02); decidir si multi-individuo (RF-03, opcional) entra o queda fuera del prototipo | Por quÃ© no promediar embeddings de vistas distintas ([[Arquitectura Multimodal]] Â§1.1) | Multi-foto funcionando + decisiÃ³n de multi-individuo documentada |
| 21 sep | Lun | MediciÃ³n real | Latencia p95, memoria pico y baterÃ­a en un dispositivo de referencia real de gama media/baja | CÃ³mo medir consumo de baterÃ­a real de una app Android | Tabla de [[OptimizaciÃ³n para Inferencia en MÃ³vil]] Â§5 rellena con datos reales |
| 22 sep | Mar | Demo web de respaldo | API `/identify` con FastAPI + Qdrant en servidor; fichas tÃ©cnicas; desplegar en capa gratuita | Despliegue bÃ¡sico de FastAPI en una capa gratuita (Render/Fly.io/Railway) | Demo web desplegada y accesible por URL |
| 23 sep | MiÃ© | Pulido de UI y modo campo | Modo oscuro/alto contraste real (RNF-07), controles a una mano (RNF-08), feedback hÃ¡ptico | CÃ³mo maneja Compose los temas claro/oscuro dinÃ¡micos correctamente | UI pulida cumpliendo RNF-07/RNF-08 |
| 24 sep | Jue (colchÃ³n) | Pruebas reales y correcciÃ³n de errores | Probar el flujo completo repetidamente, anotar fallos, corregir por prioridad | â€” (foco en estabilidad, no en aprendizaje nuevo) | Lista de errores conocidos cerrada o triageada |
| 25 sep | Vie (colchÃ³n) | Empaquetado | Firmar el APK; decidir canal (testing interno de Play o APK directo); instalaciÃ³n limpia probada | Firma de APK / `bundletool` si se usa AAB | APK instalable, probado en un dispositivo limpio |
| 26 sep | SÃ¡b (colchÃ³n) | Ensayo general | Recorrido completo como si fuera la entrega real; preparar un guion breve de demo | â€” | Ensayo exitoso + guion de demo listo |
| **27 sep** | **Dom** | **Entrega del prototipo** | Despliegue final; verificar que APK + demo web funcionan de extremo a extremo sobre las 28 especies | â€” | **Prototipo entregado: APK + demo web** |

> [!warning] QuÃ© queda explÃ­citamente fuera del 27 de septiembre
> Piloto de campo con â‰¥ 150 observaciones validadas por experto (H12), documento final de trabajo de grado (H14), sustentaciÃ³n (H15), exportaciÃ³n Darwin Core completa (HU-05), mÃ³dulo comunitario a escala, iOS. Son la continuaciÃ³n natural en la secciÃ³n 2 de abajo â€” no se pierden, se secuencian despuÃ©s del prototipo.

## 1. ParÃ¡metros fijados

| ParÃ¡metro | Valor |
| --- | --- |
| Fecha de inicio del sprint | 2026-09-05 |
| Fecha de entrega del prototipo (fijada por el autor) | **2026-09-27** |
| Fecha de entrega del documento de grado | *(por fijar por el equipo â€” no depende del sprint del prototipo)* |
| Fecha de sustentaciÃ³n | *(por fijar por el equipo)* |
| Integrantes y dedicaciÃ³n semanal | *(por fijar â€” el sprint asume trabajo paralelo en â‰¥ 3 frentes: modelo, mÃ³vil, backend)* |
| Ventana(s) de salida de campo | *(por fijar â€” el piloto de campo queda fuera del sprint del prototipo)* |
| Disponibilidad del herpetÃ³logo validador | *(por fijar)* |
| Restricciones estacionales (Ã©poca de lluvias / actividad reproductiva) | No aplica a este sprint (no hay salida de campo prevista antes del 27 sep) |

> [!tip] La estacionalidad sigue mandando sobre el resto del cronograma
> Aunque no afecta al sprint del prototipo, sÃ­ afecta al piloto de campo (H12) que viene despuÃ©s: los anuros tienen picos de actividad reproductiva asociados a las lluvias, y esa ventana no se puede mover libremente. Conviene fijarla cuanto antes, en paralelo a este sprint.

## 2. Hitos

| # | Hito | Entregable verificable | Depende de | Fecha | Responsable | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| **H1** | Marco teÃ³rico y metodolÃ³gico cerrado | Documento con introducciÃ³n, referente teÃ³rico, objetivos y metodologÃ­a | â€” | ya cerrado | | âœ… en gran parte |
| **H2** | Decisiones de arquitectura fijadas | [[Inconsistencias y Decisiones Pendientes]] resuelto | H1 | 2026-09-06 | | ðŸŸ¡ nÃºcleo cerrado 2026-09-05 (C-3, BioCLIP v1, alcance) |
| **H3** | Dataset v1 consolidado y verificado | Split congelado, verificaciÃ³n taxonÃ³mica, copias de seguridad | H1 | 2026-09-08 | | |
| **H4** | Esquema de anotaciÃ³n aplicado | â‰¥ 400â€“600 imÃ¡genes anotadas en CVAT | H3 | 2026-09-11 (entrega comprometida por el equipo) | | |
| **H5** | Modelo de segmentaciÃ³n v1 | Modelo entrenado + mÃ©tricas | H4 | 2026-09-13 (automatizado â€” [[AutomatizaciÃ³n del Entrenamiento de SegmentaciÃ³n]]) | | |
| **H6** | Modelo de identificaciÃ³n v1 | BioCLIP + cabezas jerÃ¡rquicas + mÃ©tricas offline | H3, H5 | 2026-09-15 | | |
| **H7** | Open-set operativo (versiÃ³n mÃ­nima) | Detector implementado + umbral fijado en validaciÃ³n | H6 | 2026-09-17 | | MÃ­nimo viable para el sprint; AUROC/FPR95 completos quedan para H13 |
| **H8** | Backend + base vectorial | API funcional con `/identify` y repositorio | H6 | 2026-09-19 | | |
| **H9** | Plataforma web (Fase 1) | Demostrador web con Top-3 y fichas | H8 | 2026-09-23 | | |
| **H10** | Modelos optimizados para mÃ³vil | Modelos cuantizados dentro del presupuesto | H6, H7 | 2026-09-18 | | |
| **H11** | App mÃ³vil offline (prototipo) | APK con inferencia local; sincronizaciÃ³n puede quedar mÃ­nima | H10, H8 | **2026-09-27** | | Entrega del sprint |
| **H12** | Piloto de campo | â‰¥ 150 observaciones con verdad experta | H11 | *posterior al 27 sep â€” por fijar* | | Fuera del sprint del prototipo |
| **H13** | Resultados consolidados | Todas las tablas de [[MÃ©tricas Offline]] rellenas | H12 | *posterior al 27 sep* | | |
| **H14** | Documento final | Trabajo de grado completo | H13 | *posterior al 27 sep* | | |
| **H15** | SustentaciÃ³n | | H14 | *posterior al 27 sep* | | |

## 3. Ruta crÃ­tica

```
H3 dataset â”€â”€â–¶ H4 anotaciÃ³n â”€â”€â–¶ H5 segmentaciÃ³n â”€â”€â”
                                                   â”œâ”€â”€â–¶ H10 optimizaciÃ³n â”€â”€â–¶ H11 app â”€â”€â–¶ H12 piloto â”€â”€â–¶ H13 â”€â”€â–¶ H14
                    H6 identificaciÃ³n â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**H4 (anotaciÃ³n) es el cuello de botella.** Es trabajo humano que no se acelera con mÃ¡s cÃ³mputo: cientos de imÃ¡genes segmentadas regiÃ³n por regiÃ³n segÃºn la [[GuÃ­a CVAT â€” Ãndice|guÃ­a CVAT]]. La estrategia ya prevista de anotar 400â€“600 manualmente, entrenar V1, preanotar el resto y corregir es lo que hace viable el volumen â€” conviene no saltÃ¡rsela.

Si H4 se retrasa, se retrasa todo lo demÃ¡s. Vale la pena sobredimensionar el equipo de anotaciÃ³n al inicio.

## 4. Paralelizables (para no encadenar todo)

Estas tareas no dependen de la ruta crÃ­tica y pueden avanzar simultÃ¡neamente:

- RedacciÃ³n del documento (marco teÃ³rico ya estÃ¡ muy avanzado).
- DiseÃ±o de UI y prototipo de la app con datos simulados.
- Backend y esquema de base de datos (no necesita el modelo final).
- Fichas tÃ©cnicas de especie y plantillas morfolÃ³gicas (Anexo C).
- TrÃ¡mite de permisos â†’ [[Consideraciones EcolÃ³gicas y Ã‰ticas]] (empezar cuanto antes: los tiempos administrativos no dependen del equipo).
- Montaje de copias de seguridad e infraestructura.

## 5. Seguimiento semanal

| Semana | Foco | Hecho | Bloqueos | Siguiente |
| --- | --- | --- | --- | --- |
| **1 (05â€“11 sep)** | Decisiones + diseÃ±o + arranque paralelo | **05 sep:** C-3 (28 especies), BioCLIP v1, alcance cerrado **06 sep:** âœ… Pesos BioCLIP v1 verificados, caracterÃ­sticas Ã³ptimas definidas para su rol de teacher (ViT-B/16, ~86M params) **07 sep:** EspecificaciÃ³n de componentes de UI completada (niveles 1â€“5, todos los mockups faltantes documentados) **08 sep:** âœ… Pivote de arquitectura on-device cerrado (C-5/C-6/C-7 en [[Inconsistencias y Decisiones Pendientes]]): BioCLIP-INT8 descartado por fracaso real, EdgeNeXt-Tiny destilado confirmado, SQLite/sqlite-vec reemplaza ObjectBox, audio con modelo propio, Galaxy A30 como dispositivo de referencia **11 sep:** âœ… Fase 4 (Transfer Learning) ejecutada, dos veces â€” variante C (segmentaciÃ³n binaria) probada y descartada por peor resultado (EXP-011); C-8 (MobileNetV3-Small), C-10 (destilaciÃ³n INVIABLE, 33pp de degradaciÃ³n) y C-11 (nueva arquitectura: BioCLIP fp16 completo, sin destilar) decididos el mismo dÃ­a. âŒ Room + Listado Android, planeados para hoy, **no se hicieron** | Segmentador binario da peor resultado al escalar a 41 especies, causa sin diagnosticar; desarrollo Android sin arrancar | Android arranca el **lunes 14 sep**, no el 07-11 sep como preveÃ­a el plan â€” 3 dÃ­as de desfase en ese frente, mientras que el modelo/optimizaciÃ³n mÃ³vil (Fases 5-7c, 12 sep) va 2-3 dÃ­as *adelantado* sobre la Semana 2 |
| **2 (12â€“18 sep)** | NÃºcleo de identificaciÃ³n y optimizaciÃ³n mÃ³vil | **12 sep:** âœ… Fase 5 (evaluaciÃ³n completa 41 especies) + limpieza de dataset (fotos no representativas, coordenadas) + Fases 6-7c completas: encoder extraÃ­do, fp16/int8 comparados (int8 descartado en toda variante), ONNX exportado y validado (165,6 MB), RAM/latencia medidas en emulaciÃ³n de hilos, prior geogrÃ¡fico aÃ±adido (+15 a +25pp, no estaba en el plan original) + documentaciÃ³n consolidada en Obsidian | Discrepancia de catÃ¡logo sin resolver: el checkpoint entrenado usa 41 especies, no las 28 de C-3 | Desarrollo Android arranca el 14 sep â€” el trabajo de modelo va adelantado, pero corre el riesgo de tener que esperar si Android no alcanza a absorber esa ventaja antes del 27 |

## 6. Puntos de decisiÃ³n

Momentos en que hay que decidir explÃ­citamente si se continÃºa o se recorta alcance. Definirlos ahora evita decidirlo tarde y a la fuerza (riesgo P-1 en [[Riesgos del Proyecto]]).

| Punto | Pregunta | Si la respuesta es noâ€¦ |
| --- | --- | --- |
| Tras H6 | Â¿Se alcanzan las metas de precisiÃ³n con solo visiÃ³n? | Revisar dataset antes de aÃ±adir modalidades |
| Tras H6 | Â¿Hay datos de audio suficientes? | Declarar la rama acÃºstica como trabajo futuro |
| Tras H10 | Â¿Los modelos caben y responden en el mÃ³vil? | Activar el plan B de [[OptimizaciÃ³n para Inferencia en MÃ³vil]] Â§6 |
| A mitad de plazo | Â¿La Fase 2 es alcanzable? | Reducir a demostrador mÃ³vil y reforzar la Fase 1 |



