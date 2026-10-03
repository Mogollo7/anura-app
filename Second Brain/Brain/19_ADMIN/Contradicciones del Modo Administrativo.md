---
title: "Contradicciones del Modo Administrativo"
tags: [admin, anura, contradicciones]
created: 2026-09-25
status: refined
---

# Contradicciones del Modo Administrativo

Nada de esta lista está borrado en las fuentes. Cada bloque conserva el choque. La decisión para construir está cerrada en [[Decisiones de Escalabilidad del Admin]] (2026-09-25): menos cómputo en el teléfono, inserción de especies sin reentrenar el encoder, y un compilador que sirva para otros departamentos.

Ese cierre es de diseño. No sustituye una medición. El registro medido sigue siendo [[DECISION_LOG]]. La política del vault está en [[00_CONTRADICTIONS]].

## 1. Encoder congelado frente a fine-tuning del ViT

**Textos que congelan** BioCLIP 1 en el teléfono y solo entrenan el micro-adaptador: [[Fuente - Documento Maestro de Arquitectura]], [[Fuente - Estrategia de Arquitectura y Transfer Learning]], [[Fuente - Microadaptadores Multiclase]], [[Fuente - Plan de Fases para Construir el Admin]].

**Textos que descongelan** las últimas capas (learning rate `10^-5`, bloques 8–10 del ViT-B/16, y luego centroides con ese encoder nuevo): [[Fuente - Metric Learning y Olvido Catastrofico]], [[Fuente - Espacio Vectorial y Margen]].

**Dentro de los propios textos que congelan**, el cuadro del Admin dice «Engine Fine-Tuning» y «Layer Freezing (ViT-B/16)».

**Decisión:** el Admin no regenera `bioclip_v1.onnx`. ArcFace se aplica a la matriz `W` del clúster. La crítica al Cross-Entropy se conserva. El fine-tuning del encoder base no entra al plan.

## 2. «Nivel 2» significa dos mecanismos distintos

En [[Fuente - Estrategia de Arquitectura y Transfer Learning]], el nivel 2 es el micro-adaptador de desempate.

En [[Fuente - Documento Maestro de Arquitectura]] y [[Fuente - ETI-SCH-2026]], el nivel 2 es el fallback de género, el 3 es la familia y el 4 es el rechazo.

**Decisión:** en datos y en interfaz, dos nombres: `desempate_criptico` y `cascada_taxonomica`. No usar «nivel 2» solo.

## 3. Intruso de clúster frente a caída a género

[[Fuente - ETI-OSR-2026]]: si el error de reconstrucción supera a épsilon, el estado es `02_OSR_CLUSTER`. No clasifica.

El pseudocódigo de [[Fuente - ETI-SCH-2026]]: si el residuo falla, no devuelve intruso; sigue hacia género.

**Decisión:** el código encolado es `OSR_CLUSTER`. No se asigna especie. Género o familia pueden ir como etiqueta secundaria si superan su propio umbral. Ver [[Decisiones de Escalabilidad del Admin]].

## 4. La capa ecológica no está definida igual

[[Fuente - ETI-OSR-2026]] exige probabilidad conjunta de altitud y hábitat, y colapsa si la probabilidad baja de **0,05**.

[[Fuente - Documento Maestro de Arquitectura]] corta solo con `P(altitud | especie) >= 0,05`.

**Decisión:** si `P(altitud | especie)` baja del `umbral_geo` del paquete, la política de ese paquete elige rechazo (`OSR_GEO`) o solo penalización. 0,05 es el valor inicial de las notas, no una constante. El resultado guarda el contexto geográfico. Ver [[Decisiones de Escalabilidad del Admin]].

## 5. El número tau no tiene unidad estable

| Dónde | Valor | Lectura posible |
| --- | --- | --- |
| JSON de la estrategia, Oophaga | `rejection_tau: 0,32` | Parece distancia, no similitud |
| Estrategia, nivel 1 | confianza alta ≥ **0,85** | Similitud |
| Maestro y ETI-SCH, especie | **0,72–0,85**, ejemplo **0,78** | Similitud coseno |
| Maestro, género / familia | **0,60–0,70** / **0,50–0,58** | Similitud |
| Entradas del admin | género **0,62–0,65**, familia **0,52–0,55** | Subconjunto del rango anterior |
| ETI-OSR | `d = 1 - coseno`, Weibull sobre distancias | Distancia |
| [[DECISION_LOG]] C-16 | Mahalanobis **39,35** (KAR 95 %), FAR **91 %** | Otra escala, ya medida, demasiado permisiva |

**Decisión:** el teléfono solo compara cosenos. El Admin ajusta la Weibull en el PC y guarda el corte ya convertido a similitud (`tau_kind: cosine_similarity`). Mahalanobis no viaja en el paquete. 0,32 y 0,78 no se copian. Ver [[Decisiones de Escalabilidad del Admin]].

## 6. Tamaño y forma del micro-adaptador

Las fuentes dicen, a la vez, matriz **512×64**, **512×m** con m ≤ 512, y **512×512**. El peso estimado salta entre **30 KB**, **30–50 KB**, **30–100 KB**, **35 KB**, **40→50 KB** y **+10 KB** al añadir una especie. El tiempo de reentreno se dice de **30 segundos**, de **menos de 1 minuto** y de **20–50 épocas**.

**Decisión:** la forma inicial es 512×64 FP16, que pesa 64 KiB. Ese tamaño es `filas × columnas × bytes`, no una constante. `MAX_CLUSTER_SPECIES = 12` es un límite configurable del pipeline. El sistema avisa si se supera. No crea otro clúster solo. Los miembros los define el herpetólogo. Ver [[Decisiones de Escalabilidad del Admin]].

## 7. Pesos ecológicos que no son una sola tabla

| Perfil | Documento maestro | Nota de pesos variables | JSON de ejemplo |
| --- | --- | --- | --- |
| Generalista | 80 / 10 / 10, σ = 1000 m | 70–80 / 10–15 / 5–10 | Oophaga 0,85 / 0,10 / 0,05 |
| Microendémica | 30 / 60 / 10, σ = 120 m | 30–40 / 50–60 / 10 | — |
| Par críptico | 35 / 35 / 30 | 35 / 35 / 30, o canto | — |
| Especialista de quebrada | no aparece | 50 / 20 / 30 | — |

El EXP-007 del cerebro adoptó un prior geográfico global con peso **0,75**. Eso no es el trío `wv / wg / wm`.

**Decisión:** la ficha es por **especie y paquete**, con tres valores visibles: calculado, manual y efectivo. Los perfiles son plantillas. El 0,75 del experimento no se escribe en el mismo campo. El sistema no sobrescribe el valor manual.

## 8. Catálogo de ~130 especies frente a 340 filas regionales

El departamento se estima en **220–235** especies (~230 en varias notas). Entrenables con foto pública: **120–140**, y con más de 50 fotos: **~85**.

La suma de la columna «especies reales» por subpaquete es **25+42+40+45+32+35+38+28+55 = 340**.

Los rangos de una misma zona tampoco coinciden entre notas. Urabá teórico: **90–120**, **~110** o **80–120** centroides, y entrenable **~55**. Aburrá: **25–35**, **~30** o **20–35**. Una consulta en memoria se estima en **12–30** especies, y el ejemplo de Caldas a 1800 m habla de **15–20** centroides.

**Decisión:** guardar la pertenencia especie–paquete, muchos a muchos. No sumar paquetes para obtener el censo. Todas estas cifras quedan marcadas como **estimación** hasta la curación. El `total_species: 55` del JSON de Urabá es ejemplo de esquema, alineado con la cifra entrenable de esa zona, no con la teórica.

## 9. Individuo y observación, en orden invertido

[[Fuente - Plan de Fases para Construir el Admin]], árbol de la fase 1: Dataset → Observación → Individuo → Fotografías.

La misma fase, en prosa, pide fotografías asociadas a individuos. [[Fuente - Modelo de Datos y Reglas del Admin]] (sección B) dice: Especie → Individuo → Observaciones → Imágenes. También advierte que una observación de iNaturalist no es lo mismo que un individuo.

**Decisión:** **Individuo** (animal) tiene varias **observaciones** (eventos); cada observación tiene varias **fotografías**. El dataset es una membresía versionada, no el padre biológico. Quitar una imagen del entrenamiento no borra la observación. Invalidar la observación saca todas sus imágenes y deja el motivo.

## 10. Un centroide, o tres

Hay fórmulas que promedian todas las fotos en un solo vector. [[Fuente - Centroides Estables y Muestras]] acepta el punto medio de los morfos **o** dos sub-centroides. El documento maestro y las reglas posteriores prohíben promediar morfos opuestos (ejemplo: *Oophaga histrionica*) y piden conservar el centroide **global**, el **regional** y el de **morfo**.

**Decisión:** centroide global, regional y de morfo. No se promedian morfos opuestos. Con menos de 3 individuos en el paquete, se presta el global con `borrowed: true`. Ver [[Decisiones de Escalabilidad del Admin]].

## 11. Dos dibujos del territorio

Un dibujo: 9 subregiones oficiales y 4 pisos térmicos. Otro: paquete regional y debajo «zona A / B / C», sin nombres.

**Decisión:** se versionan 9 paquetes, uno por subregión. El piso térmico filtra en memoria y no crea paquetes hijos. «Zona A/B/C» no se implementa. Ver [[Decisiones de Escalabilidad del Admin]].

## 12. Qué es del día 1 y qué es Fase 2

El cuadro del Admin muestra scraping, CVAT, fine-tuning y empaquetado como si fueran el presente. [[Fuente - Roadmap Excepciones Fase 1 y 2]] y las 15 fases dejan audio, YOLOv8, auto-anotación, sub-centroides de juvenil, filtro morfométrico activo, OTA real y la app **fuera** del primer ciclo. La curación inicial es pHash, varianza del Laplaciano y CVAT manual.

**Decisión:** el modelo de datos reserva los campos. Las pantallas de las fases 1–15 no dependen de audio, YOLO ni de la app. El scraping es un conector futuro, no un bloqueo de la fase 2.

## 13. BioCLIP 1 (512) y BioCLIP 2.5 (1024) no se mezclan

Los centroides del paquete móvil salen de **BioCLIP 1, 512 dimensiones**. La auditoría en el PC usa **BioCLIP 2.5, ViT-H/14, 1024 dimensiones**.

**Decisión:** el compilador rechaza un vector cuya dimensión o cuyo `encoder` no sea `BioCLIP-1-frozen` / 512. BioCLIP 2.5 no escribe el JSON móvil.

## 14. Tamaño del ONNX y latencia: diseño frente a medición

Las notas dicen ONNX de **~100 MB** o **100–150 MB**, y latencia menor de **100 ms** o **150 ms**.

[[DECISION_LOG]] registra artefacto FP16 de **165,6 MB**, pico de **~405 MB**, **403 ms** a 1 hilo y **154 ms** a 4 hilos.

**Decisión:** el Admin separa el ONNX (**165,6 MB**, 403 ms a 1 hilo, 154 ms a 4 hilos) del JSON de la subregión (KiB reales: 55 KiB de centroides en el ejemplo de 55 especies). ~100 MB no se muestra como tamaño del paquete. Ver [[Decisiones de Escalabilidad del Admin]].

## 15. Menú amplio de OSR frente al pipeline de tres capas

[[Fuente - Estrategias OSR Alternativas]] recomienda OpenMax, Mahalanobis, MC Dropout, GAN, outlier exposure y ensambles. La misma nota pide abandonar el entrenamiento manual y pasar al modo administrativo.

Ese menú no cabe en un móvil con encoder congelado y costo 0 por consulta. Mahalanobis, además, ya tiene un ensayo en el cerebro (C-16) y no se tira a la basura: el ensayo salió demasiado permisivo (FAR 91 %).

**Decisión:** el móvil no lleva GAN, MC Dropout, ensambles ni OpenMax. La calibración de trabajo es Weibull en el PC, convertida a un corte de coseno. Mahalanobis queda como comparación offline, no como umbral empaquetado. Ver [[Decisiones de Escalabilidad del Admin]].

## 16. Dos vocabularios de estado

[[Fuente - ETI-OSR-2026]]: `00_MATCH_OK`, `01_OSR_GLOBAL`, `02_OSR_CLUSTER`, `03_OSR_GEO_FAIL`.

[[Fuente - ETI-SCH-2026]]: `STATUS_OK`, `STATUS_GENUS_SP`, `STATUS_FAMILY_SP`, `STATUS_OPEN_SET`.

Género y familia no tienen código en la tabla OSR. El intruso de clúster no tiene código en la cascada.

**Decisión:** un `IdentificationResult` con `status`, `candidate`, `confidence`, `evidence`, `geographic_context` y `provenance`. Los estados son `MATCH_SPECIES`, `MATCH_GENUS`, `MATCH_FAMILY`, `OSR_GLOBAL`, `OSR_CLUSTER` y `OSR_GEO`. Ver [[Decisiones de Escalabilidad del Admin]].

## 17. Documento maestro y estrategia son casi el mismo texto

[[Fuente - Estrategia de Arquitectura y Transfer Learning]] y [[Fuente - Documento Maestro de Arquitectura]] repiten filosofía, cuadro de cuatro columnas, pesos y el ejemplo de Urabá.

El maestro añade la cascada de cuatro niveles, `family_nodes`, `genus_nodes`, OSR en tres capas y `rejection_tau: 0,78` (versión de ejemplo 3.2.0).

La estrategia conserva piezas que el maestro no repite igual: confianza ≥ 0,85, `rejection_tau: 0,32`, `cryptic_groups`, matriz hasta 512×512 y versión 2.4.0.

**Decisión:** el compilador sigue el esquema híbrido del maestro (familia, género, especie, clúster). La estrategia se conserva como variante, no se borra.

## 18. Super-centroide de familia «ponderado» sin pesos

[[Fuente - ETI-SCH-2026]] dice que la familia pondera linealmente a sus géneros. La fórmula escrita en el maestro es una suma y una normalización L2, sin coeficientes.

**Decisión:** implementar suma + L2, sin peso por género, hasta que exista un campo `genus_weight`. «Ponderar» sin números no se puede programar.

## 19. El ciclo de rechazo suena automático; el release no lo es

El closed-loop de OSR describe calcular un centroide nuevo y actualizar el JSON cuando llega una captura rechazada. La fase 13 prohíbe la publicación automática y exige aprobación humana. Hay doble compuerta: el herpetólogo avala la ciencia y el administrador avala la técnica.

**Decisión:** el worker calcula embeddings, centroides, scores, umbrales, métricas, artefactos y el paquete. No crea especies, ni complejos, ni morfos, ni pesos científicos, ni publica. Herpetólogo, luego administrador, luego release. Ver [[Decisiones de Escalabilidad del Admin]].

## 20. «Listo» en la tabla de costos no es un estado del vault

[[Fuente - Roadmap Excepciones Fase 1 y 2]] marca motor móvil, JSON, Hostinger y worker como «Fase 1 (Listo)», con Hostinger a **3–8 USD/mes** y el resto a **0 USD**.

**Decisión:** leer esa tabla como presupuesto de diseño. No como evidencia de que el Admin, el OTA o el worker ya existen.

## 21. Nombres usados como ejemplo

*Oophaga histrionica*, *Rhinella horribilis*, *Dendropsophus columbianus*, *Pristimantis illex*, *Pristimantis penelopus*, *Pristimantis dorsopictus* y `Pristimantis_belmet` aparecen para ilustrar JSON y pesos. `Pristimantis_belmet` no viene acompañado de una ficha taxonómica en estas notas.

**Decisión:** no dar de alta esas especies en el Admin solo porque están en un ejemplo. Verificar nomenclatura en la ficha antes de publicar un paquete.

## 22. «BioCLIP 1 congelado» no es BioCLIP 1 puro

Estas notas hablan de BioCLIP 1 congelado, sin fine-tuning, y rechazan tocar el ViT. El teléfono corre `encoder_anura_fp16.onnx`, que sale de `bioclip_anura_mejor.pt`: BioCLIP 1 **con fine-tuning** en ranas (sha del checkpoint `98a6c54d…`).

**Medido (2026-09-26):** con el método de tres capas y las mismas fotos, el puro identifica igual (top-1 k-NN 59,0 % contra 59,2 %) pero rechaza peor (FAR 84,2 % contra 75,7 %; AUROC 0,599 contra 0,652). Ver [[Prueba Real del Creador de Paquetes]].

**Decisión:** «congelado» significa que el encoder con fine-tuning **no se vuelve a entrenar** desde el 2026-09-12, porque es el que tienen los teléfonos. El compilador exige `encoder_anura_fp16`, no un «BioCLIP-1-frozen» genérico.

## 23. BioCLIP 2.5 sí existe

[[Inconsistencias y Decisiones Pendientes]] (C-8, 2026-09-11) dice que «BioCLIP v2.5» no existe. El servidor lo usa: `services/ai-service` carga `hf-hub:imageomics/bioclip-2.5-vith14`, que está en la caché local (`open_clip_config.json`: ViT-H/14, `embed_dim` 1024).

**Decisión:** la nota C-8 quedó vieja en ese punto. Hay tres modelos distintos y no se mezclan:
- teléfono: BioCLIP 1 con fine-tuning, 512;
- servidor: BioCLIP 2.5, 1024, para la web y para auditar rechazos;
- Admin: usa el del teléfono para todo lo que viaja en un paquete.

La opción del worker que mete un vector de 1024 es una prueba de la compuerta, no un uso del modelo.

## 24. El paquete del Admin no lo lee el teléfono

[[Esquema JSON del Paquete]] define un JSON por subregión con centroides, nodos y clústeres. La app lee `package.sqlite` (4.034 vectores, k-NN k=5) y `openset_v1.1.0_clean.bin` (Mahalanobis τ 39,35).

**Decisión pendiente del autor:** formato v2. Propuesta: SQLite por subregión con las tablas del esquema. Ver [[Plan del Backend Real]] M4. Mientras no exista el lector, el paquete del creador solo se usa en el simulador.

## 25. Altitud: rechazo o penalización

Con registros reales, `umbral_geo` 0,05 como rechazo ataja 31 desconocidas y tumba 25 fotos buenas de 167. `AnuraIdentifier.kt` ya documenta un caso de campo: el prior de zona volteó una identificación visual correcta.

**Decisión pendiente del autor:** mantener `OSR_GEO` como rechazo o pasar la capa 3 a penalización.

## Aclaración que no es contradicción

Los centroides L2 no heredan el sesgo de conteo de un softmax. Aun así, las especies polimórficas, las comunes y los pares confusos necesitan **más diversidad de individuos**. Una cosa es que 200 fotos no apaguen a la especie de 15. Otra es que 15 fotos del mismo animal no hagan un centroide de especie.
