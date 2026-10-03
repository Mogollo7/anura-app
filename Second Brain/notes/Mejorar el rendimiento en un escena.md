Mejorar el rendimiento en un escenario de Open Set Recognition (OSR) requiere dos cosas fundamentales: hacer que las representaciones de las clases conocidas sean extremadamente compactas y definir fronteras de decisión cerradas (bounded regions) para saber con certeza cuándo una muestra no pertenece a nada conocido.
Aquí tienes las mejores estrategias técnicas para optimizar tu modelo frente a clases no vistas:
1. Perfeccionar el Espacio Latente (Metric Learning)
Las funciones de pérdida tradicionales como Cross-Entropy crean límites de decisión infinitos. Debes forzar a que las clases conocidas ocupen "bolsillos" o esferas hiper-compactas en el espacio vectorial.
 * Pérdidas con Margen Angular (ArcFace / CosFace):
   Añaden un penalizador angular estricto durante el entrenamiento. Esto disminuye la varianza intra-clase (comprime las muestras de una misma especie) y aumenta la distancia inter-clase, dejando vastas "zonas vacías" en el espacio vectorial que corresponden al espacio Open Set.
 * Center Loss o Contrastive Loss:
   Añadir una pérdida secundaria como Center Loss penaliza la distancia entre los embeddings de las muestras y sus respectivos centroides durante el entrenamiento:
   
   
   Esto actúa como un "imán" que atrae los datos hacia el centroide de su clase.
2. Algoritmos de Rechazo basados en EVT (Extreme Value Theory)
En lugar de usar la salida directa de Softmax (que genera sobreconfianza), aplica modelos estadísticos sobre las distancias a los centroides:
 * OpenMax (Reemplazo de Softmax):
   Calcula la distancia de las muestras a los centroides de entrenamiento. Mediante una distribución de Weibull (Teoría de Valores Extremos), estima la probabilidad de que una muestra esté "demasiado lejos" de cualquier clase conocida y redistribuye las probabilidades hacia una clase explícita de Desconocido (K+1).
 * Distancia Mahalanobis con Covarianza Cierta:
   En lugar de medir la distancia euclidiana simple al centroide, utiliza la distancia de Mahalanobis, la cual toma en cuenta la forma y varianza de la distribución de cada clase conocida. Muestras con una distancia superior a un umbral \tau estadístico son rechazadas.
3. Exposición a Muestras Out-of-Distribution (OOD Training / Outlier Exposure)
Le enseñas al modelo qué aspecto tiene lo "desconocido" durante la fase de entrenamiento:
 * Generación Sintética de "Casi-Conocidos" (GANs / VAEs):
   Usa un modelo generativo para crear imágenes/vectores sintéticos que caigan justo en las fronteras de decisión de tus clases conocidas (boundary samples). Entrena a la red para que asigne a estas muestras sintéticas una etiqueta de rechazo o alta entropía.
 * Outlier Exposure (OE):
   Añade un conjunto secundario de datos muy variado (que no contenga ninguna de tus clases conocidas) y aplica una pérdida de regularización para que la salida del modelo ante estos datos sea uniforme (máxima entropía / incertidumbre pura).
4. Estimación de Incertidumbre y Ensambles
 * Monte Carlo Dropout (MC Dropout):
   Mantén el Dropout activo durante la inferencia y realiza N pasadas de la misma muestra. Si la varianza de las predicciones es alta, la muestra está en una zona de alta incertidumbre y debe clasificarse como Open Set.
 * Ensembles de Modelos:
   Entrenar 3 o 5 modelos con diferentes inicializaciones/arquitecturas. Si los modelos discrepan fuertemente sobre la clase asignada a una muestra, es un indicador claro de que se trata de una clase desconocida.
Resumen de Pipeline Recomendado
| Paso | Técnica | Efecto |
|---|---|---|
| Entrenamiento | Extractor con ArcFace + Center Loss | Crea agrupaciones hiper-compactas por clase. |
| Calibración | Modelado de distancias con OpenMax / Weibull | Define el radio máximo permitido por clase. |
| Inferencia | Umbral Mahalanobis + MC Dropout | Detecta y rechaza muestras que caen fuera de los radios o presentan alta varianza. |Nota botar totalmente el mecanismo de entrenamiento manual bota el actual considerarlo un fracaso absoluto y pasar a ejecución de entrenamiento utilizando el modo administrativo para crear paquetes y para reentrenar el modelo cloude