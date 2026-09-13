El almacenamiento total requerido en el dispositivo móvil se compone de tres elementos principales: el modelo de visión/clasificación, el modelo de segmentación anatómica y la base de datos vectorial local (sqlite-vec).  
*Nota técnica inicial:* El número de individuos de entrenamiento (80 para visión y 30 para segmentación) **no afecta** el tamaño físico de los pesos de las redes neuronales, ya que el tamaño de un modelo depende estrictamente de su arquitectura (número de capas y canales). Sin embargo, el volumen de individuos y especies (28 especies) sí determina directamente el tamaño de la base de datos de embeddings en sqlite-vec.  
A continuación se detalla el cálculo de pesos para un despliegue optimizado en dispositivos móviles utilizando **cuantización a INT8** (el estándar recomendado) frente al formato completo en FP32:

### **1\. Desglose de Componentes del Sistema**

| Componente del Sistema | Arquitectura Base / Estructura | Tamaño Estimado (INT8 \- Móvil) | Tamaño Estimado (FP32 \- Completo) |
| :---- | :---- | :---- | :---- |
| **Modelo de Visión / Clasificador** | MobileNetV3-Small / Extractor de Embeddings | **\~3.5 MB – 5.0 MB** | \~12.0 MB – 15.0 MB |
| **Modelo de Segmentación (17 partes)** | U-Net con Codificador MobileNetV3 | **\~4.5 MB – 7.0 MB** | \~18.0 MB – 25.0 MB |
| **Base de Datos Vectorial (sqlite-vec)** | 28 especies $\\times$ vectores de zonas anatómicas | **\~2.0 MB – 3.0 MB** | \~2.0 MB – 3.0 MB |

### **2\. Cálculo Detallado de la Base de Datos Vectorial (sqlite-vec)**

Para dimensionar el archivo SQLite con las 28 especies:

* **Estructura por especie:** Se almacenan vectores de 128 dimensiones (en formato Float32, donde cada dimensión ocupa 4 bytes $\\rightarrow$ $128 \\times 4 \= 512$ bytes por vector).  
* **Zonas anatómicas:** Si se generan embeddings independientes para las partes clave (ej. 17 partes poligonales más 1 vector global del anuro\_completo, totalizando 18 zonas por individuo de referencia).  
* **Muestras de referencia:** Si se guardan de forma conservadora 3 individuos de referencia validados por cada una de las 28 especies:  
  * Total de vectores: $28 \\text{ especies} \\times 3 \\text{ individuos} \\times 18 \\text{ zonas} \= 1,512 \\text{ vectores}$.  
  * Espacio de datos puros: $1,512 \\times 512 \\text{ bytes} \= 774,144 \\text{ bytes}$ ($\\approx 0.77 \\text{ MB}$).  
* **Sobrecabeza de Índices y Metadatos:** Al sumar la estructura relacional de SQLite con las columnas de metadatos taxonómicos (familia, genero, especie, zona\_anatomica) y los índices de búsqueda espacial de sqlite-vec, el archivo físico final de la base de datos regional se estabiliza entre **2.0 MB y 3.0 MB**.

### **3\. Peso Total del Paquete en el Dispositivo**

* **Peso Total Optimizado (INT8):** Sumando el modelo de visión (\~4 MB), el modelo de segmentación (\~5.5 MB) y la base de datos SQLite (\~2.5 MB), el peso total de la aplicación dedicado a la inteligencia artificial y su taxonomía es de aproximadamente **12 MB**.  
* **Peso Total sin Cuantización (FP32):** Si se mantiene la precisión de punto flotante completa, el paquete asciende a unos **38 MB a 43 MB**.

Este consumo de almacenamiento es sumamente bajo y garantiza que el sistema pueda operar de forma completamente local, fluida y sin conexión a internet en teléfonos de gama media.