# **Plan Maestro de Entrenamiento y Despliegue: Esquema Profesor-Alumno con Jerarquía Taxonómica**

Este documento integra la especificación completa del sistema de visión por computador y base de datos local, incorporando de manera explícita el **etiquetado jerárquico por familia, género y especie** en todo el flujo de entrenamiento, destilación y almacenamiento vectorial.

## **1\. Arquitectura y Especificaciones de Modelos**

El sistema opera bajo una estructura asimétrica que procesa el conocimiento en la nube y lo compacta para su ejecución local en dispositivos con recursos limitados (Samsung Galaxy A30, 4 GB de RAM).

* **Modelo Profesor (Teacher):** BioCLIP v2.5 (especializado en el Árbol de la Vida). Sus capas base se mantienen congeladas o con ajuste sutil para preservar su comprensión profunda de la herpetología y las relaciones filogenéticas.  
* **Modelo Alumno (Student):** MobileNetV3-Small. Red compacta optimizada para despliegue local mediante .tflite.  
* **Esquema de Etiquetado y Datos:** Las 80 imágenes por especie (para las 28 especies de anuros de Caldas) y sus respectivas anotaciones de segmentación están estructuradas de forma estricta bajo una **jerarquía taxonómica trivel: Familia $\\rightarrow$ Género $\\rightarrow$ Especie**, asegurando que cada vector y predicción mantenga trazabilidad biológica completa.

## **2\. El Núcleo Matemático: Función de Pérdida de Destilación**

Para superar el estancamiento previo (métricas en 0.2), el alumno no aprende únicamente de etiquetas duras, sino que imita la distribución de probabilidad suavizada del profesor mediante **Divergencia de Kullback-Leibler (KL Divergence)** con escala de temperatura.

### **A. Ecuación de Suavizado (Logits a Probabilidades)**

Los *logits* ($z$) de salida se escalan con un parámetro de temperatura $T \= 4.0$ para exponer los matices secundarios de similitud estructural, vital para diferenciar taxones cercanos (ej. múltiples especies del género *Pristimantis*):

$$q\_i \= \\frac{\\exp(z\_i / T)}{\\sum\_j \\exp(z\_j / T)}$$

### **B. Función de Pérdida Híbrida Total**

La optimización del alumno combina el error frente a las etiquetas verdaderas y la guía del profesor:

$$\\mathcal{L}\_{total} \= \\alpha \\cdot \\mathcal{L}\_{CE}(y, \\sigma(z^{student})) \+ (1 \- \\alpha) \\cdot \\left( T^2 \\cdot D\_{KL}(P^{teacher} \\parallel P^{student}) \\right)$$

* $\\alpha \= 0.3$ (Peso para las etiquetas reales de familia, género y especie).  
* $(1 \- \\alpha) \= 0.7$ (Peso para la guía de razonamiento taxonómico heredada de BioCLIP v2.5).

## **3\. Plan de Entrenamiento Paso a Paso (The Master Recipe)**

### **Fase 1: Preparación, Validación y Jerarquía Taxonómica (Lunes 14 – Martes 15\)**

> 1. Verificar que el dataset exportado este domingo incluya metadatos limpios estructurados por **familia, género y especie**.  
> 2. Aplicar un pipeline de preprocesamiento con **Letterboxing** (relleno neutro para conservar la proporción geométrica de los anuros) y *Data Augmentation* agresivo (variaciones de brillo para simular luz nocturna de linterna, volteos horizontales y rotaciones de $\\pm 15^\\circ$).

### **Fase 2: Precalentamiento del Alumno \- Warm-up (Miércoles 16\)**

Para evitar el colapso matemático al iniciar la destilación, el MobileNetV3-Small recibe un entrenamiento base:

* Entrenar al alumno **durante 5 épocas** utilizando Entropía Cruzada tradicional (CrossEntropyLoss) sobre las etiquetas de especie.  
* Optimizador: AdamW con *learning rate* de $1 \\times 10^{-3}$.

### **Fase 3: Ciclo de Destilación Conjunta (Jueves 17 – Sábado 19\)**

Ejecutado en una GPU en la nube (Google Colab / entorno dedicado):

> 1. Cargar BioCLIP v2.5 en modo evaluación (model\_teacher.eval(), requires\_grad \= False).  
> 2. Cargar el MobileNetV3-Small precalentado en modo entrenamiento.  
> 3. En cada iteración del *DataLoader*:  
   * Pasar el lote por el profesor para extraer los *logits* suavizados con $T \= 4.0$.  
   * Pasar el mismo lote por el alumno.  
   * Calcular la $\\mathcal{L}\_{total}$ combinando Entropía Cruzada jerárquica y KL Divergence.  
   * Actualizar **únicamente** los pesos del alumno mediante retropropagación.  
> 4. Hiperparámetros:  
   * Optimizador: AdamW.  
   * Learning Rate: $1 \\times 10^{-4}$.  
   * Épocas: 15 a 20 con parada temprana (*Early Stopping*).

## **4\. Estructura de Datos Vectoriales y Esquema SQLite (sqlite-vec)**

Para que la base de datos local aproveche la taxonomía completa en las consultas de vecinos más cercanos ($k$-NN), las tablas se estructuran de la siguiente forma:

SQL  
CREATE TABLE anfibios\_vectores (  
    id INTEGER PRIMARY KEY AUTOINCREMENT,  
    especie TEXT NOT NULL,  
    genero TEXT NOT NULL,  
    familia TEXT NOT NULL,  
    zona\_anatomica TEXT NOT NULL,  
    vector BLOB NOT NULL  
);

* **Uso en Inferencia:** Si la similitud vectorial de especie presenta dudas debido a condiciones de campo deficientes, el sistema realiza un respaldo lógico agrupando por columnas de genero o familia, evitando fallos absolutos.

## **5\. Optimización y Empaquetado para el Galaxy A30 (Domingo 20 – Lunes 21\)**

Evitando el fallo crítico de la cuantización INT8 sobre vectores de características y previniendo bloqueos de memoria (OOM):

> 1. **Exportación a FP16 (Media Precisión):**  
   * Convertir el modelo alumno entrenado a formato **TensorFlow Lite (.tflite)** en precisión FP16.  
   * *Peso resultante del modelo:* **\~4.5 MB a 6 MB**.  
   * *Ventaja:* Reduce el archivo a la mitad frente a FP32 sin corromper la precisión matemática de los vectores de embedding ni los bordes de segmentación.  
> 2. **Consolidación de la Base Vectorial Regional:**  
   * Empaquetar los embeddings de referencia filtrados por el sharding geográfico de Caldas.  
   * *Peso de la base de datos local:* **\~2.5 MB**.  
> 3. **Peso Total del Despliegue Local:** El paquete combinado (Modelo .tflite \+ Base SQLite \+ Motor de Reglas JSON) pesará menos de **10 MB a 12 MB**, garantizando un consumo operativo inferior a 60 MB de RAM en el Samsung Galaxy A30.

## **6\. Estimación de Probabilidad de Éxito**

* **Probabilidad de Éxito Global: 85% – 92%.**  
* **Justificación Técnica:** La disponibilidad del dataset estructurado por familia, género y especie este fin de semana elimina el cuello de botella de etiquetado; el uso de BioCLIP v2.5 como profesor proporciona la base taxonómica experta; y el uso de **FP16** en lugar de INT8 agresivo protege la estabilidad geométrica y métrica del modelo en dispositivos móviles de gama media.