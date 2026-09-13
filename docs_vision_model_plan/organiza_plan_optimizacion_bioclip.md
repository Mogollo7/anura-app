# **Plan de Optimización y Fine-Tuning Directo de BioCLIP para Clasificación de Anuros**

Este documento detalla la estrategia técnica para superar el estancamiento en el rendimiento del modelo de visión (métricas anteriores en 0.2), abandonando el complejo esquema de destilación Profesor-Alumno en favor de un enfoque directo de **Linear Probing seguido de Fine-Tuning Selectivo** sobre el modelo fundacional **BioCLIP**.

## **1\. Fundamentos de la Estrategia**

Intentar entrenar redes desde cero o aplicar destilación avanzada con un volumen acotado de datos (80 imágenes por especie) suele provocar colapsos matemáticos o sobreajuste severo. BioCLIP posee un espacio vectorial preentrenado con millones de imágenes de flora y fauna, lo que le otorga una comprensión profunda de texturas, patrones dorsales y morfologías biológicas.  
En lugar de obligar al modelo a aprender a "ver" desde cero, la estrategia consiste en **congelar su conocimiento base** y adaptar únicamente su capa superior de decisión a las 28 especies de anuros locales.

## **2\. Fase 1: Linear Probing (Congelamiento Total del Backbone)**

El objetivo de esta primera fase es romper el estancamiento métrico inicial entrenando únicamente un nuevo clasificador lineal superior.

### **Configuración Técnica**

* **Congelamiento de Capas:** Se desactiva la gradiente del 100% del codificador (*backbone*) de BioCLIP (requires\_grad \= False).  
* **Nueva Capa Densa:** Se añade un clasificador lineal (*Linear Head*) con una salida de 28 neuronas (una por cada especie del proyecto) conectadas a la última capa de características de BioCLIP.  
* **Hiperparámetros Recomendados:**  
  * **Optimizador:** AdamW.  
  * **Learning Rate ($lr$):** $1 \\times 10^{-3}$ (un valor relativamente alto, seguro para entrenar capas nuevas desde cero).  
  * **Épocas:** 10 a 15 épocas.  
  * **Tamaño de Lote (*Batch Size*):** 16 o 32 (según la memoria VRAM disponible).

*Resultado esperado:* El modelo convergdrá rápidamente en pocas épocas, elevando la precisión base al superar el sesgo inicial y evitando que las características biológicas preentrenadas se corrompan.

## **3\. Fase 2: Fine-Tuning Selectivo (Ajuste Fino de Capas Posteriores)**

Una vez que el modelo ha convergido de forma estable en la Fase 1, se procede a especializar ligeramente las capas más altas del modelo para capturar los micro-detalles propios de los anuros neotropicales.

### **Configuración Técnica**

* **Descongelamiento Parcial:** Se mantienen congeladas las capas tempranas y medias del codificador, pero se **descongelan exclusivamente las últimas 2 o 3 capas** (o bloques de atención finales) de BioCLIP junto con la cabeza de clasificación.  
* **Reducción Radical del Learning Rate:** Para evitar destruir el conocimiento previo del modelo (*catastrophic forgetting*), se reduce el *learning rate* en dos o tres órdenes de magnitud.  
  * **Learning Rate ($lr$):** $1 \\times 10^{-5}$ o $5 \\times 10^{-6}$.  
* **Épocas:** 5 a 8 épocas adicionales con parada temprana (*Early Stopping*) vigilando la pérdida en el conjunto de validación.

## **4\. Pipeline de Preprocesamiento y Normalización de Datos**

Para alimentar correctamente el modelo con las 80 imágenes por especie sin deformar las características corporales de los anuros:

* **Letterboxing (Mantenimiento de Relación de Aspecto):** Las imágenes no deben redimensionarse a la fuerza de forma cuadrada (lo que ensancha o estira artificialmente a las ranas). Se rellenan los espacios sobrantes con bordes neutros (gris o negro) para ajustar la imagen al tamaño de entrada requerido por BioCLIP (ej. $224 \\times 224$ píxeles).  
* **Aumento de Datos Específico para Campo:**  
  * Variaciones severas de brillo y contraste para simular la fotografía nocturna con linterna frente a luz diurna difusa.  
  * Volteos horizontales (*Random Horizontal Flip*) para duplicar la variabilidad espacial.  
  * Rotaciones moderadas ($\\pm 15^\\circ$) para simular desalineaciones en la captura manual.

## **5\. Mitigación de Confusión en Especies Similares**

Cuando el dataset incluye especies filogenéticamente cercanas (como múltiples taxones del género *Pristimantis*), una función de pérdida de entropía cruzada estándar puede penalizar en exceso al modelo cuando confunde variantes visuales sutiles.

* **Uso de Label Smoothing (Suavizado de Etiquetas):** Aplicar un factor de suavizado (ej. $\\epsilon \= 0.1$) en la función de pérdida evita que el modelo genere logits excesivamente seguros y lo vuelve más tolerante a la variabilidad natural intraespecífica.

## **6\. Despliegue y Exportación sin Cuantización Agresiva**

Para evitar el fallo crítico reportado previamente con la cuantización INT8 en tareas de visión y extracción de embeddings:

* **Salida en FP16 (Media Precisión):** Exportar el modelo final optimizado a formato de media precisión (FP16).  
* **Ventajas Operativas:** Reduce el tamaño físico del archivo a la mitad en comparación con el modelo original de 32 bits (FP32), preserva con total exactitud la integridad matemática de las distancias vectoriales y mantiene la compatibilidad de aceleración por hardware en procesadores móviles modernos (Snapdragon / MediaTek) sin deformar las representaciones internas.