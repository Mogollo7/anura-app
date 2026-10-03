---
title: "Cuántas fotos e individuos hacen falta para un centroide"
tags: [fuente, centroides, dataset]
created: 2026-09-25
status: draft
source: "Second Brain/notes/Para construir centroides estables.md"
---

# Cuántas fotos e individuos hacen falta para un centroide

> [!WARNING] Polimorfismo: promedio único frente a sub-centroides
> Esta nota admite un centroide en el punto medio de todos los morfos o dos sub-centroides. La regla posterior, en [[Fuente - Modelo de Datos y Reglas del Admin]] y en el documento maestro, no promedia morfos de color opuesto y además conserva centroide global y regional. Ver [[Contradicciones del Modo Administrativo]].

> [!NOTE] Fuente literal
> Transcripción íntegra de `notes/Para construir centroides estables.md`. No está resumida. Mapa: [[00_Indice_Principal]]. Nodo de trabajo: [[Centroides y Muestras]] · [[Morfos y Especiacion Regional]].

Para construir centroides estables con un extractor visual como BioCLIP, no necesitas miles de fotos por especie, pero sí una diversidad biológica mínima de muestras. Además, no todas las especies deben tener la misma cantidad de fotos; forzar un conjunto de datos perfectamente balanceado en herpetología es un error técnico.
1. Cantidad de Fotos e Individuos Requeridos por Especie
Para calcular el vector centroide de una especie no basta con tener muchas fotos del mismo ejemplar en el mismo ángulo. Lo que da estabilidad al vector es la variación entre diferentes individuos.
| Nivel de Calidad | Fotos Totales por Especie | Individuos Diferentes (Mínimo) | Propósito y Fiabilidad |
|---|---|---|---|
| Mínimo Viable | 10 – 15 fotos | 3 – 5 individuos | Permite generar un centroide básico. Útil para especies raras o de difícil acceso. |
| Recomendado | 30 – 50 fotos | 8 – 12 individuos | Centroide estable. Absorbe cambios de iluminación, humedad y postura de la rana. |
| Optimo / Robusto | 80 – 100+ fotos | 15+ individuos | Excelente separación vectorial. Captura polimorfismo, dimorfismo sexual y fases juveniles. |
¿Por qué es vital variar los individuos y no solo las fotos?
Si tomas 50 fotos de la misma rana en una sola sesión de campo, el centroide no aprenderá a identificar a la especie, sino a ese individuo en particular bajo esa luz específica (overfitting de fondo y textura). Necesitas fotos de distintas salidas de campo, diferentes fotógrafos, horas del día y estados de humedad de la piel.
2. ¿Deben tener la misma fuerza o dar más peso a unas que a otras?
No deben tener el mismo número de fotos. Asignar más esfuerzo y datos a ciertas especies sobre otras es una estrategia necesaria por tres razones principales:
A. Especies que necesitan "MÁS FUERZA" (Mayor volumen de datos)
 * Especies Polimórficas (Ej. Género Pristimantis):
   * Ranas donde individuos de la misma especie tienen patrones de coloración drásticamente opuestos (unas son lisas, otras tienen rayas dorsales, otras manchas rojas o amarillas).
   * Estrategia: Necesitan más fotos (50–100+) para que el centroide quede en el "punto medio real" de todos los morfos, o incluso considerar crear 2 sub-centroides para la misma especie (ej. Pristimantis_X_morfo_A y Pristimantis_X_morfo_B).
 * Pares Confusos / Especies "Gemelas":
   * Especies distintas que habitan en la misma zona y son morfológicamente casi idénticas a simple vista.
   * Estrategia: Requieren más datos para aplicar Hard Negative Mining durante el ajuste del encoder. El modelo necesita muchas muestras para encontrar el detalle anatómico diminuto que las separa.
 * Especies de Alta Frecuencia (Las más comunes):
   * Ranas urbanas o periurbanas que los usuarios fotografiarán el 80% del tiempo (ej. Dendropsophus columbianus, Rhinella horribilis).
   * Estrategia: Su centroide debe ser ultra-preciso. Si este centroide está mal calculado por falta de variabilidad, el sistema fallará en la gran mayoría de las consultas reales.
B. Especies con POCOS DATOS (Raras o Crípticas)
 * Para las especies de las que solo consigas 10 a 15 fotos de 3 individuos, la ventaja de usar centroides con normalización L2 es que no sufren el sesgo de clase (class imbalance bias) que afecta a los clasificadores tradicionales (Softmax).
 * Como el centroide es un promedio unitario:
   
   
   El vector resultante de 15 fotos de alta calidad ocupa un lugar exacto en la esfera latente sin ser "opacado" por la especie que tiene 200 fotos.
3. Criterios de Diversidad para las Fotos de un Paquete
Al seleccionar o curar las fotos para construir los centroides de tu paquete geográfico, asegúrate de cumplir con la siguiente proporción de variabilidad visual:
 * Ángulos: 60% vista dorsolateral (la típica foto de rana), 25% vista dorsal pura, 15% acercamiento a cabeza/tímpano o patrón ventral.
 * Iluminación y ambiente: Mezlcar fotos tomadas con flash nocturno, luz natural diurna, fondo de hoja verde, hojarasca café y sustrato rocoso.
 * Estado de humedad: Ranas secas vs. ranas completamente mojadas (el brillo del agua altera la reflexión de luz y la textura capturada por el Vision Transformer).
