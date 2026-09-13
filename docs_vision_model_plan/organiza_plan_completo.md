# **Plan de Ejecución Táctico: Sistema Móvil de Identificación de Anuros (Entrega: 27 de Septiembre de 2026\)**

## **1\. Cronograma del Sprint (13 al 27 de Septiembre de 2026\)**

Con la recepción del dataset completamente etiquetado este domingo 13 de septiembre, el plan de trabajo se estructura en un sprint de dos semanas enfocado exclusivamente en ingeniería de modelos, vectorización e integración móvil.

| Fase | Fechas | Objetivos Clave | Entregables |
| :---- | :---- | :---- | :---- |
| **Fase 1: Ingesta y Validación** | Sept 14 – Sept 15 | Exportación desde CVAT, validación de esquemas JSON de 19 partes y particionado estratificado (Train/Val) para las 28 especies. | Dataset limpio y estructurado en la nube (Google Drive / Colab). |
| **Fase 2: Entrenamiento y Destilación** | Sept 16 – Sept 20 | Entrenamiento del modelo híbrido (ROI global \+ segmentación de subpartes) usando BioCLIP como profesor y MobileNetV3 como alumno. | Pesos del modelo entrenado y validado en formato PyTorch. |
| **Fase 3: Vectorización y Base de Datos** | Sept 21 – Sept 23 | Extracción de embeddings por zonas anatómicas, estructuración de tablas en SQLite y configuración de la extensión sqlite-vec para Caldas. | Archivo .sqlite regional optimizado y empaquetado (.zip). |
| **Fase 4: Motor Lógico y App Móvil** | Sept 24 – Sept 26 | Conversión a .tflite (INT8), integración del motor de reglas JSON y acople con el GPS nativo en la aplicación móvil. | APK / Versión de prueba móvil instalable. |
| **Fase 5: Pruebas y Estabilización** | Sept 27 | Pruebas de campo simuladas (baja luz, oclusión parcial) y entrega final del sistema. | Informe técnico y despliegue del MVP. |

## **2\. Arquitectura General del Sistema**

El software opera mediante un flujo descentralizado y 100% offline que combina visión por computador con lógica taxonómica estructurada:

* **Módulo de Visión (TFLite):** Recibe la imagen de campo, aísla al espécimen mediante la máscara anuro\_completo y segmenta las estructuras anatómicas clave.  
* **Módulo de Vectores (sqlite-vec):** Compara los embeddings extraídos por zonas contra una base de datos local fragmentada por coordenadas geográficas.  
* **Motor de Reglas Biológicas (JSON):** Actúa como filtro final, cruzando la predicción visual con los rangos taxonómicos oficiales (familia, género, especie) y el contexto de ubicación GPS.

## **3\. Pipeline de Entrenamiento (Enfoque Profesor-Alumno)**

Para garantizar alta precisión a pesar de las limitaciones de datos por especie:

> 1. **Congelamiento del Profesor:** Se utiliza **BioCLIP** con pesos preentrenados en millones de especímenes biológicos para extraer características visuales profundas sin modificar sus capas base.  
> 2. **Optimización del Alumno:** Se entrena una arquitectura compacta (**MobileNetV3**) optimizada para hardware móvil mediante una función de pérdida híbrida que combina la entropía cruzada y la divergencia de Kullback-Leibler (KL) frente a las salidas del profesor.  
> 3. **Aumento de Datos en Tiempo Real:** Se aplican transformaciones geométricas y cromáticas agresivas (simulación de luz nocturna de linterna, rotaciones y recortes) para robustecer el aprendizaje frente a condiciones reales de campo en Caldas.

## **4\. Estructura de Datos Vectoriales y Sharding Geográfico**

Para minimizar el uso de memoria RAM y almacenamiento en dispositivos de gama media:

* **Esquema de la Tabla SQLite:**  
  SQL  
  CREATE TABLE anfibios\_vectores (  
      id INTEGER PRIMARY KEY AUTOINCREMENT,  
      especie TEXT NOT NULL,  
      genero TEXT NOT NULL,  
      familia TEXT NOT NULL,  
      zona\_anatomica TEXT NOT NULL,  
      vector BLOB NOT NULL  
  );

* **Fragmentación por Región:** Los embeddings no se agrupan en un archivo global masivo, sino en paquetes regionales acotados por un manifiesto (manifest.json) que evalúa el GPS del usuario para descargar únicamente las especies reportadas en la ecorregión (ej. departamento de Caldas).

## **5\. Integración del Motor de Reglas y Validación Taxonómica**

La decisión final no depende exclusivamente de la similitud visual, sino de una validación lógica estructurada mediante un archivo JSON de conocimiento biológico:

JSON  
{  
  "especies": \[  
    {  
      "nombre\_cientifico": "Pristimantis acanthinus",  
      "genero": "Pristimantis",  
      "familia": "Strabomantidae",  
      "perfil\_biologico": {  
        "ojo": {  
          "color\_iris\_permitido": \["rojo\_naranja", "cobre"\],  
          "orientacion\_pupila": "horizontal"  
        },  
        "glandulas\_pliegues": {  
          "tipo\_obligatorio": "ausente"  
        }  
      }  
    }  
  \]  
}

* **Lógica de Cruce:** Si el modelo visual detecta una alta similitud pero encuentra una contradicción directa con el perfil biológico del JSON (ej. presencia de glándulas parotídeas marcadas en una especie que carece de ellas), el motor lógico penaliza la predicción o desciende el nivel de certeza a categoría de género/familia.

## **6\. Despliegue Móvil y Cuantización**

* **Formato Final:** Exportación de los modelos entrenados a **TensorFlow Lite (.tflite)**.  
* **Cuantización INT8:** Conversión de precisión de punto flotante (FP32) a enteros de 8 bits, reduciendo el tamaño combinado de los modelos y la base de datos a un rango de **12 MB a 15 MB** totales en el almacenamiento local del teléfono.  
* **Ejecución Offline:** Todo el pipeline de inferencia, cálculo de distancias de Coseno con sqlite-vec y filtrado GPS opera de manera local, garantizando funcionamiento en zonas rurales sin cobertura de red.