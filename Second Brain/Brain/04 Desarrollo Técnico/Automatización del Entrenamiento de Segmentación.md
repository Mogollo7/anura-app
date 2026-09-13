---
title: "AutomatizaciÃ³n del Entrenamiento de SegmentaciÃ³n"
proyecto: Anura
tipo: desarrollo-tÃ©cnico
estado: propuesta-de-diseÃ±o
tags: [anura, desarrollo, segmentaciÃ³n, mlops, automatizaciÃ³n, yolo-seg]
---

# AutomatizaciÃ³n del Entrenamiento de SegmentaciÃ³n

[[Anura â€” Ãndice General]] Â· [[GuÃ­a CVAT â€” Ãndice]] Â· [[Ciclo de Vida del Modelo (MLOps)]] Â· [[OptimizaciÃ³n para Inferencia en MÃ³vil]] Â· [[Cronograma y Plan de Trabajo]]

> [!abstract] Por quÃ© existe esta nota
> El equipo entrega **todos los datos de la segmentaciÃ³n semÃ¡ntica** en la semana del 9â€“11 de septiembre de 2026 ([[Cronograma y Plan de Trabajo]] Â§0). Con el prototipo debido el 27, no hay margen para que el entrenamiento del segmentador sea un proceso manual e iterativo: tiene que ser un **pipeline** que alguien dispara y supervisa, no algo que alguien programa de nuevo cada vez. Esta nota fija ese pipeline **antes** de que lleguen los datos, para que el dÃ­a que lleguen solo haga falta ejecutarlo.

## 1. QuÃ© significa "automatizado, solo con supervisiÃ³n"

No significa AutoML ni bÃºsqueda de arquitectura. Significa que entre "llegan los datos" y "hay un modelo v1 con mÃ©tricas" no hay pasos manuales de programaciÃ³n â€” solo una ejecuciÃ³n y una revisiÃ³n humana de los resultados:

```
Export CVAT â”€â”€â–¶ Script de conversiÃ³n â”€â”€â–¶ Script de entrenamiento â”€â”€â–¶ Script de evaluaciÃ³n â”€â”€â–¶ RevisiÃ³n humana
  (dato)         (formato YOLO-seg)         (config fija)              (mÃ©tricas + muestras)      (aprobar / ajustar dato)
```

La persona supervisa **el resultado**, no escribe el bucle de entrenamiento cada vez. Si algo falla, se corrige el dato o la configuraciÃ³n y se vuelve a correr el mismo pipeline â€” no se improvisa un script nuevo.

## 2. Dos modelos de segmentaciÃ³n, no confundirlos

| | SegmentaciÃ³n binaria (Etapa I) | SegmentaciÃ³n anatÃ³mica (esta nota) |
| --- | --- | --- |
| QuÃ© separa | Individuo vs. fondo | 16 regiones anatÃ³micas (`anuro_completo` + 15 partes) |
| Ya entrenado | SÃ­ â€” es lo que explica el ~99 % de la Etapa I ([[Modelo de VisiÃ³n â€” BioCLIP]] Â§7) | No â€” es el que llega la semana del 9â€“11 sep |
| Formato de anotaciÃ³n | MÃ¡scara binaria | PolÃ­gonos multi-clase, esquema de la [[GuÃ­a CVAT â€” Ãndice\|guÃ­a CVAT v1.0]] |
| Rol en el pipeline | Recorte limpio antes de BioCLIP (variante C) | Recorte **y** evidencia anatÃ³mica para el "por quÃ©" (RF-06, HU-03) |

Documentar formalmente el modelo binario de la Etapa I (arquitectura, entrenamiento) sigue pendiente ([[Modelo de VisiÃ³n â€” BioCLIP]] Â§10) â€” es un antecedente directo de este pipeline, con menos clases.

> [!warning] El modelo binario dejÃ³ de ser una apuesta segura al escalar (2026-09-11/12)
> La fila "Rol en el pipeline: recorte limpio antes de BioCLIP (variante C)" describÃ­a el plan, no un resultado confirmado a esta escala. Al probarlo sobre las 41 especies del catÃ¡logo actual (no las 10 de la Etapa I), el recorte binario **empeorÃ³** el Top-1 frente a no segmentar (EXP-011 en [[Experimentos y Resultados]]). Causa sin diagnosticar todavÃ­a â€” candidatos: calidad de mÃ¡scara en fotos de campo mÃ¡s heterogÃ©neas que las 10 especies originales, o pÃ©rdida de contexto Ãºtil que el ViT sÃ­ aprovechaba en imagen completa. **Esta segmentaciÃ³n anatÃ³mica (16 clases) sigue siendo un desarrollo aparte, sin relaciÃ³n con ese fracaso** â€” se retoma cuando sea posible, y su rol de "evidencia del por quÃ©" (RF-06) no depende de que el recorte binario funcione. Ver C-13 en [[Inconsistencias y Decisiones Pendientes]].

## 3. El pipeline, paso a paso

### 3.1 ConversiÃ³n del export de CVAT

CVAT exporta en varios formatos; el que evita trabajo manual de conversiÃ³n es **"Datumaro 1.0"** o **"CVAT for images 1.1"** con las mÃ¡scaras de polÃ­gono, convertido a **formato YOLO-seg** (un `.txt` por imagen, clases + polÃ­gonos normalizados) mediante un script Ãºnico y determinista:

```
convertir_cvat_a_yolo.py
  entrada:  export_cvat.zip (Datumaro o CVAT 1.1)
  salida:   dataset_yolo/
              images/{train,val,test}/
              labels/{train,val,test}/
              data.yaml
```

Reglas que el script debe aplicar sin intervenciÃ³n manual:

- **Aplicar el mismo split congelado** del dataset de identificaciÃ³n ([[Estrategia de ConstrucciÃ³n del Dataset]]) â€” el segmentador no puede tener su propia particiÃ³n aleatoria, o se rompe la trazabilidad de quÃ© imagen fue vista en quÃ© etapa.
- **Excluir automÃ¡ticamente clases con muy pocos ejemplos** anotados (por debajo de un umbral, p. ej. 5 instancias) y reportarlo en el log, en vez de dejar que el entrenamiento falle a mitad de camino o produzca una clase inservible en silencio.
- **Validar geometrÃ­a** (polÃ­gonos con â‰¥ 3 puntos, dentro de los lÃ­mites de la imagen) antes de escribir el `.txt` â€” un polÃ­gono corrupto de CVAT no debe descubrirse a mitad del entrenamiento.

### 3.2 Entrenamiento con configuraciÃ³n fija

Con **Ultralytics YOLO-seg** (ya usado como referencia en [[App MÃ³vil]] y [[Stack TecnolÃ³gico]]), el entrenamiento es un Ãºnico comando/llamada, no un bucle escrito a mano:

```python
from ultralytics import YOLO

modelo = YOLO("yolov8n-seg.pt")  # o yolov8s-seg.pt si el dataset lo sostiene
modelo.train(
    data="dataset_yolo/data.yaml",
    epochs=150,
    imgsz=640,
    patience=20,        # early stopping â€” evita juzgar a mano cuÃ¡ndo parar
    seed=42,             # reproducibilidad, ver Ciclo de Vida del Modelo (MLOps)
    project="segmentacion_anura",
    name="v1",
)
```

La configuraciÃ³n (`epochs`, `imgsz`, augmentaciÃ³n, `patience`) se fija **una vez**, en un archivo versionado junto al commit ([[Ciclo de Vida del Modelo (MLOps)]] Â§2), no como argumentos escritos a mano en la terminal cada vez. Si el dataset crece o cambia, se vuelve a correr el mismo comando â€” eso es "supervisiÃ³n", no "entrenamiento manual".

> [!tip] Elegir el tamaÃ±o de modelo por presupuesto, no por costumbre
> `yolov8n-seg` es el punto de partida porque es el que mÃ¡s margen deja dentro de los 150 MB del RNF-05 junto a BioCLIP ([[OptimizaciÃ³n para Inferencia en MÃ³vil]]). Subir a `yolov8s-seg` solo si 
` no alcanza la precisiÃ³n mÃ­nima y sobra presupuesto de tamaÃ±o â€” medirlo, no asumirlo, como en el resto del proyecto.

### 3.3 EvaluaciÃ³n automÃ¡tica y reporte para supervisiÃ³n humana

El script de evaluaciÃ³n corre sin intervenciÃ³n y produce lo Ãºnico que la persona necesita revisar:

- **MÃ©tricas por clase** (mAP50, mAP50-95, precisiÃ³n/recall) sobre el split de test â€” nunca sobre val, que ya se usÃ³ para el early stopping.
- **Una cuadrÃ­cula de imÃ¡genes de muestra** con las mÃ¡scaras predichas superpuestas (20â€“30 imÃ¡genes, incluyendo las de peor mAP por clase) â€” es lo que una persona puede revisar en minutos para decidir "esto sirve" sin mirar miles de imÃ¡genes una por una.
- **Alerta automÃ¡tica** si alguna clase queda por debajo de un umbral mÃ­nimo (p. ej. mAP50 < 0.5), seÃ±alando que esa regiÃ³n necesita mÃ¡s anotaciones, no mÃ¡s Ã©pocas de entrenamiento.

### 3.4 QuÃ© decide la persona (y quÃ© no)

| Decide la persona | Lo hace el script |
| --- | --- |
| Â¿Las mÃ©tricas y las muestras visuales son aceptables para el prototipo? | Calcular las mÃ©tricas |
| Â¿QuÃ© clase necesita mÃ¡s datos anotados? | Detectar quÃ© clase estÃ¡ por debajo del umbral |
| Â¿Se promueve este modelo a "vigente" en el pipeline de identificaciÃ³n? | Registrar la versiÃ³n, exportar a ONNX/LiteRT |
| Ajustar el conjunto de datos (pedir mÃ¡s anotaciÃ³n de una regiÃ³n) | Convertir, entrenar y evaluar de nuevo con el dataset ampliado |

Ninguna de las columnas de la izquierda requiere escribir cÃ³digo de entrenamiento nuevo. Eso es lo que hace que el proceso quepa en el sprint sin depender de que alguien estÃ© disponible para reprogramar cada corrida.

## 4. Del modelo entrenado al dispositivo

Mismo camino que el resto de los modelos del proyecto â€” no es un proceso aparte:

```
modelo.pt (Ultralytics)
      â†“  export ONNX / TFLite nativo de Ultralytics
   modelo.onnx / modelo.tflite
      â†“  cuantizaciÃ³n INT8 (dataset de calibraciÃ³n del train)
   modelo cuantizado (10â€“25 MB, ver OptimizaciÃ³n para Inferencia en MÃ³vil Â§5)
      â†“
   Android (LiteRT o ONNX Runtime Mobile)
```

Ultralytics exporta directamente a ONNX y a TFLite (`model.export(format="tflite", int8=True)`), lo que evita un paso de conversiÃ³n manual adicional al de [[OptimizaciÃ³n para Inferencia en MÃ³vil]] Â§1.

## 5. QuÃ© falta por decidir o medir

- [ ] Confirmar `yolov8n-seg` vs. `yolov8s-seg` con los datos reales (pendiente hasta la entrega del 9â€“11 sep).
- [ ] Fijar el umbral mÃ­nimo de mAP50 por clase que bloquea la promociÃ³n a "vigente".
- [ ] Escribir `convertir_cvat_a_yolo.py` y probarlo con un export parcial o sintÃ©tico **antes** de la entrega real, para no perder los primeros dÃ­as de la semana 1 del sprint depurando el conversor.
- [ ] Decidir si las clases con pocos ejemplos se agrupan (p. ej. todas las de "tubÃ©rculos") en vez de excluirse, siguiendo la misma lÃ³gica de agrupaciÃ³n que ya se aplicÃ³ al reducir de 18 a 16 etiquetas (I-2 en [[Inconsistencias y Decisiones Pendientes]]).

## 6. DiagnÃ³stico validado â€” por quÃ© el segmentador binario empeorÃ³ el resultado (2026-09-12)

> [!success] DiagnÃ³stico completo, con evidencia cuantitativa y visual â€” ver EXP-011/EXP-012 en [[Experimentos y Resultados]]
> Tres causas combinadas: (1) el segmentador se entrenÃ³ con solo 9 especies y se aplicÃ³ a 41 â€” domain shift real en las 32 no vistas; (2) `fg_medio` (fracciÃ³n de imagen marcada como rana) es de apenas 6-18% en todo el dataset, seÃ±al de que el modelo detecta muy poco foreground incluso en especies conocidas; (3) **bug de diseÃ±o**: el recorte tomaba el bounding-box de *todos* los pÃ­xeles marcados como foreground, sin filtrar componentes conexos â€” un solo falso positivo en la esquina opuesta de la imagen bastaba para estirar el recorte hasta casi la imagen completa. Medido sobre 161 mÃ¡scaras de `Dendrobates_truncatus`: 34,2 % tenÃ­an â‰¥2 "islas" de foreground separadas, y el bbox resultante promediaba el doble del Ã¡rea real de la rana (15,8 % vs. 7,4 %).
>
> **Segundo problema encontrado el mismo dÃ­a**: el cÃ³digo de `_recortar_por_mascara` solo recortaba la imagen al bbox â€” **nunca aplicaba la mÃ¡scara pixel a pixel** (poner el fondo a negro), pese a que esa es la definiciÃ³n documentada de variante C en [[Modelo de VisiÃ³n â€” BioCLIP]] Â§5 y la que sostuvo el ~99 % de la Etapa I. Corregido tambiÃ©n.
>
> **Ambos fixes se validaron con un experimento pareado de 3 vÃ­as**: mismo modelo (checkpoint vigente, entrenado en variante A), mismas 150 imÃ¡genes de test â€” imagen completa vs. zoom sin mÃ¡scara vs. zoom con fondo a negro (variante C real):
>
> | | Top-1 |
> | --- | --- |
> | Imagen completa | **60,7 %** |
> | Zoom sin mÃ¡scara | 50,7 % |
> | Zoom + fondo a negro (C real) | **44,7 %** |
>
> **Resultado contraintuitivo pero consistente**: aplicar la mÃ¡scara real (fondo a negro) empeora *mÃ¡s* que solo hacer zoom, no menos. Ninguno de los dos fixes, aplicados solo en *inferencia*, resuelve el problema â€” porque el modelo actual nunca vio ni recortes ni fondos negros en su entrenamiento (mismatch de dominio en ambos casos, mÃ¡s severo cuanto mÃ¡s se aleja la entrada de lo visto). Esto **no** significa que segmentar sea mal camino: significa que la pregunta correcta es otra. La que queda abierta: Â¿mejora el Top-1 si se **reentrena** Fase 4 desde cero sobre el recorte con fondo a negro, ya con ambos fixes? Eso no se ha probado todavÃ­a â€” ver EXP-012/EXP-013 en [[Experimentos y Resultados]].

## 7. DiseÃ±o propuesto: explicabilidad por parte anatÃ³mica (segmentaciÃ³n semÃ¡ntica, 16 clases)

> [!abstract] La pregunta que resuelve
> No es "cuÃ¡l es la especie" (eso ya lo responde el clasificador global) sino **"por quÃ©"** â€” RF-06 / HU-03: mostrarle al usuario quÃ© parte de la rana coincide con la especie propuesta y en quÃ© grado, usando las 16 regiones anatÃ³micas de la [[GuÃ­a CVAT â€” Ãndice|guÃ­a CVAT v1.0]] una vez que ese segmentador (distinto del binario) estÃ© entrenado.

Reutiliza exactamente el mismo patrÃ³n de ingenierÃ­a que ya funcionÃ³ para el prior geogrÃ¡fico ([[OptimizaciÃ³n para Inferencia en MÃ³vil]] Â§6): un banco de referencias precalculado + similitud coseno + un peso de combinaciÃ³n â€” no requiere entrenar nada nuevo mÃ¡s allÃ¡ del propio segmentador semÃ¡ntico.

```mermaid
flowchart TD
    A[Foto de la rana] --> B["Segmentador SEMÃNTICO<br/>16 regiones anatÃ³micas<br/>(pendiente: datos CVAT, distinto del binario)"]
    B --> C1[Recorte: dorso]
    B --> C2[Recorte: vientre]
    B --> C3[Recorte: patas]
    B --> C4[Recorte: cabeza/tÃ­mpano]
    C1 --> D["Mismo encoder BioCLIP<br/>ya extraÃ­do (Fase 6/7, fp16)"]
    C2 --> D
    C3 --> D
    C4 --> D
    D --> E1[Embedding dorso]
    D --> E2[Embedding vientre]
    D --> E3[Embedding patas]
    D --> E4[Embedding cabeza]
    F["Banco de prototipos<br/>por (especie, parte)<br/>precalculado sobre train"] --> G{"Similitud coseno<br/>por parte, 0-100%"}
    E1 --> G
    E2 --> G
    E3 --> G
    E4 --> G
    G --> H["Dorso: 91% Dendrobates truncatus<br/>Vientre: 62%<br/>Patas: 84%<br/>Cabeza: no visible"]
    H --> I[FusiÃ³n con la predicciÃ³n<br/>del clasificador de imagen completa]
    I --> J[Resultado + evidencia<br/>por parte, para la UI]
```

**MecÃ¡nica del "coincide en X%":**

1. **Banco de prototipos** (cÃ¡lculo directo, no entrenamiento): para cada (especie, parte anatÃ³mica), promediar los embeddings 512-d de esa parte sobre las fotos de train donde estÃ© claramente segmentada â€” mismo cÃ¡lculo que el prior geogrÃ¡fico, cambiando coordenadas por vectores de imagen.
2. **Al clasificar una foto nueva**: por cada parte visible y bien segmentada (mismo criterio de `fg_min`/`fg_max` que ya usa GATE 2 del segmentador binario), se recorta, se pasa por el encoder, y se compara contra el prototipo de esa parte para las especies candidatas (top-3 del clasificador global).
3. **El "X%"** es la similitud coseno normalizada (0-100 %) â€” el mismo tipo de cÃ¡lculo que ya corre en producciÃ³n para el prior geogrÃ¡fico.
4. **Partes no visibles u ocluidas** se marcan explÃ­citamente "no observable" â€” no se fuerza una comparaciÃ³n con ruido. Encaja con el diseÃ±o de UI de "presente/ausente/no observable" ya previsto para el 18 sep en [[Cronograma y Plan de Trabajo]].

**Por quÃ© no es solo cosmÃ©tico:** si una parte da baja coincidencia con la especie top-1 del clasificador global pero alta con la top-2, es seÃ±al de que el clasificador se puede estar equivocando â€” la fusiÃ³n por partes puede **corregir** la predicciÃ³n, no solo justificarla. Misma lÃ³gica que el prior geogrÃ¡fico: dos fuentes de evidencia independientes combinadas superan a una sola.

**Riesgos a validar antes de construir esto en serio:**
- Requiere que el segmentador semÃ¡ntico estÃ© entrenado primero (sigue pendiente).
- Cobertura desigual por (especie, parte) â€” mismo problema ya visto con el prior geogrÃ¡fico en especies escasas (`Boana_xerophylla`, `Pristimantis_vilarsi`).
- Las partes no son seÃ±ales independientes (dorso y patas suelen covariar en patrÃ³n de color) â€” empezar con un peso simple tipo `w=0,75` del prior geogrÃ¡fico y medir el efecto real en Top-1, no asumirlo.

## 8. Estrategia refinada (2026-09-12) â€” identificar primero, segmentar y explicar despuÃ©s

> [!important] Reemplaza el orden de fusiÃ³n del Â§7 a la luz del diagnÃ³stico de hoy
> El Â§7 proponÃ­a segmentar todas las partes y **fusionar** esa evidencia con el clasificador global para decidir la especie (con posibilidad de corregirlo). EXP-011/012/013 (Â§6, arriba) mostraron que **cualquier transformaciÃ³n de la imagen que el clasificador no vio en entrenamiento â€” recorte, fondo a negro â€” le hace daÃ±o real** (hasta âˆ’16 pp de Top-1). Fusionar evidencia de partes segmentadas en la decisiÃ³n final arriesgarÃ­a meter ese mismo daÃ±o por la puerta de atrÃ¡s. La estrategia refinada evita el riesgo por diseÃ±o: **el clasificador global nunca deja de ver la imagen completa** â€” la segmentaciÃ³n entra Ãºnicamente *despuÃ©s*, como capa de explicaciÃ³n, no de decisiÃ³n.

**El flujo, en el orden correcto:**

```mermaid
flowchart TD
    A[Foto de la rana] --> B["Clasificador global<br/>(imagen COMPLETA, sin recorte â€”<br/>el que ya funciona: 57% Top-1 / 82% Top-3)"]
    B --> C["Especie mÃ¡s probable<br/>ej. Dendrobates truncatus, 78%"]
    C --> D["Segmentador SEMÃNTICO<br/>16 regiones anatÃ³micas<br/>(pendiente: datos CVAT)"]
    D --> E1[Recorte: dorso]
    D --> E2[Recorte: vientre]
    D --> E3[Recorte: patas]
    D --> E4[Recorte: cabeza/tÃ­mpano]
    E1 --> F["Encoder BioCLIP<br/>(ya extraÃ­do, fp16)"]
    E2 --> F
    E3 --> F
    E4 --> F
    F --> G["Comparar CADA parte<br/>SOLO contra el prototipo de<br/>Dendrobates truncatus<br/>(la especie ya decidida, no top-3)"]
    G --> H["Dorso: 91% coincide con<br/>el patrÃ³n tÃ­pico de D. truncatus<br/>Patas: 84% Â· Vientre: 62%<br/>Cabeza: no visible"]
    C --> I[Resultado final al usuario]
    H --> I
```

**Diferencias concretas con el diseÃ±o del Â§7:**

| | Â§7 (fusiÃ³n, superado) | Â§8 (identificar â†’ explicar, vigente) |
| --- | --- | --- |
| Orden | Segmentar todas las partes â†’ comparar contra top-3 â†’ fusionar para decidir | Clasificar con imagen completa â†’ decidir â†’ segmentar â†’ explicar esa decisiÃ³n |
| Contra quÃ© se compara cada parte | Prototipos de las 3 especies candidatas | Prototipos de **una sola especie**, la ya identificada |
| Â¿Puede la segmentaciÃ³n cambiar la especie mostrada? | SÃ­ (esa era la idea) | **No** â€” la segmentaciÃ³n nunca decide, solo explica |
| Riesgo si el segmentador semÃ¡ntico falla en una foto | Corrompe la decisiÃ³n final | Solo empobrece la explicaciÃ³n (menos partes "coinciden", el resultado principal no cambia) |
| ExposiciÃ³n al mismatch de dominio encontrado hoy | Alto â€” mete recortes/mÃ¡scaras en el camino de decisiÃ³n | Ninguno â€” el clasificador nunca ve nada distinto de la imagen completa |

**Por quÃ© el orden importa tanto:** desacopla dos preguntas que antes estaban mezcladas. "Â¿QuÃ© especie es?" la responde el modelo que ya sabemos que funciona, sin tocarlo. "Â¿Por quÃ© esta especie?" es un problema de **explicabilidad post-hoc** â€” puede fallar parcialmente (una parte oculta, un segmentador impreciso en una especie rara) sin que eso degrade nunca la respuesta principal. Es mÃ¡s simple de construir, mÃ¡s simple de depurar cuando algo sale mal (los dos pasos son independientes), y no repite el error del dÃ­a de hoy.

**Ajuste al mecanismo del banco de prototipos (Â§7), con este orden:**
1. El banco de prototipos por (especie, parte) sigue siendo necesario y se calcula igual (Â§7, paso 1) â€” para **todas** las especies, porque no se sabe de antemano cuÃ¡l va a identificarse.
2. Al llegar una foto: primero el paso Bâ†’C del diagrama (clasificar, imagen completa). ReciÃ©n con la especie ya fija, se segmenta y se compara **solo contra esa especie** â€” no hace falta calcular ni mostrar similitud contra las demÃ¡s candidatas, lo que ademÃ¡s simplifica la UI (una sola fila de evidencia por parte, no una tabla de 3Ã—4).
3. Si se quiere seÃ±alar dudas (ej. "esta identificaciÃ³n podrÃ­a estar equivocada"), eso se hace aparte, comparando la confianza global del Top-1 vs. Top-2 del clasificador â€” no metiendo la segmentaciÃ³n en esa decisiÃ³n.

## Referencias

- Ultralytics YOLO â€” documentaciÃ³n de entrenamiento y exportaciÃ³n de modelos de segmentaciÃ³n. [docs.ultralytics.com/tasks/segment](https://docs.ultralytics.com/tasks/segment/)
- CVAT â€” formatos de exportaciÃ³n (Datumaro, CVAT for images, Segmentation mask). [docs.cvat.ai/docs/manual/advanced/formats](https://docs.cvat.ai/docs/manual/advanced/formats/)



