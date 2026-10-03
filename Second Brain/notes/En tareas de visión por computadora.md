En tareas de visión por computadora para herpetología —especialmente cuando se trabaja con segmentación o clasificación de especies con morfologías similares— el solapamiento o la cercanía excesiva de los datos en el espacio vectorial (donde los embeddings o "vectoroides" de distintas especies/clases quedan apelotonados) es un problema muy común.
Para separar la representación de las especies dentro del espacio latente sin destruir la capacidad de identificación y permitiendo que el modelo siga aprendiendo/creciendo con nuevas muestras en el futuro, se utilizan varias técnicas de estructuración de espacio vectorial:
1. Cambiar la función de pérdida a una de Margen Mínimo (Metric Learning)
Si estás usando pérdidas de clasificación estándar como Cross-Entropy, el modelo solo busca separar las clases lo justo para clasificarlas, pero no fuerza a que los vectores de una misma especie estén hiper-compactos ni a que especies distintas mantengan un "margen de seguridad".
 * ArcFace / CosFace / Additive Margin Softmax:
   Estas pérdidas añaden un margen angular estricto en la esfera de los embeddings. Fuerzan a que el modelo penalice a las especies parecidas si sus vectores no guardan una distancia mínima entre sí, desplegando los datos en la hiperesfera y abriendo espacio para especies futuras.
 * Contrastive Loss / Triplet Loss:
   Permite entrenar al modelo usando tripletas (Ancla, Positivo, Negativo):
   * Ancla: Imagen de Rana Especie A.
   * Positivo: Otra imagen de Rana Especie A.
   * Negativo: Imagen de Rana Especie B (la especie parecida).
     El objetivo es acercar A a su igual y empujar activamente a B fuera de su zona de influencia por un margen \alpha.
2. Normalización de Embeddings (L2 Normalization)
Asegúrate de aplicar normalización L2 a la salida del extractor de características (la penúltima capa densa) antes de calcular distancias o centroides:
 * Efecto: Proyecta todos los vectores a una superficie esférica de radio 1.
 * Por qué ayuda: Elimina la variación por "magnitud" (provocada por diferencias de iluminación, escala o fondo en la foto de la rana) y deja únicamente la distancia cosenoidal (ángulo), haciendo que las diferencias morfológicas finas sean las que dicten la posición en el espacio.
3. Ajuste de Granularidad mediante "Hard Negative Mining"
Si el modelo confunde dos géneros o especies muy parecidas, el entrenamiento estándar no le prestará suficiente atención a esos pares difíciles.
 * Estrategia: Durante el entrenamiento, filtra y presenta con mayor frecuencia al modelo los casos donde la rana A y la rana B tienen la menor distancia vectorial (los "negativos más difíciles").
 * Resultado: La red se ve obligada a aprender patrones morfológicos de alta resolución (p. ej., patrón de manchas, textura de la piel, forma del tímpano o pliegues dorsolaterales) en lugar de características globales simples.
4. Mantener la Capacidad de Crecimiento Continuo (Evitar Catastrophic Forgetting)
Para permitir que el sistema acepte nuevas especies o datos sin colapsar el espacio vectorial que ya separaste:
 * Estructura tipo Prototypical Networks (Few-Shot / Class-Centroids):
   En lugar de entrenar una capa final tipo Dense(N_clases), utiliza un enfoque basado en prototipos (centroides). Cada especie está representada por el centroide de sus vectores. Para clasificar, se mide la distancia coseno al centroide más cercano.
   * Para agregar una especie nueva: Solo necesitas extraer los vectores de las nuevas fotos, calcular su centroide y guardarlo en la base de datos vectorial (vía FAISS o ChromaDB), sin necesidad de reentrenar toda la red neuronal.
 * Fijar un margen de reserva (Slack space):
   Al entrenar con ArcFace, configurar un margen angular amplio (ej. m = 0.35 a 0.5) garantiza que el espacio vectorial no se sature rápidamente, dejando "espacio libre" en la esfera latente para cuando incorpores nuevos géneros o especies.
Resumen de Implementación Recomendada
 * Extrae la capa de embeddings de tu modelo y aplícale Normalización L2.
 * Entrena o haz fine-tuning usando ArcFace Loss o Triplet Loss aumentando el peso de las parejas de especies que se solapan (Hard Negative Mining).
 * Utiliza la distancia coseno sobre los centroides de cada especie para medir la separación.