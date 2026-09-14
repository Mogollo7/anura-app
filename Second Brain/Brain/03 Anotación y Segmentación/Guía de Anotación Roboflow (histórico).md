---
title: "Guía de Anotación Roboflow (histórico)"
proyecto: Anura
fuente: "Notion â€” Proyecto Identificación de Anuros Colombia"
tags: [anura, anotación, histórico]
---

# Guía de Anotación Roboflow (histórico)

**Objetivo del Anotador:** Delimitar manualmente el cuerpo y las partes anatómicas clave sobre imágenes originales sin procesar.

#### **A. Criterios de Selección y Limpieza de Imágenes (Pre-Anotación)**

Antes de anotar una imagen en Roboflow, el etiquetador debe descartarla si cumple con alguna de estas condiciones:

- **Fuera de Foco / Borrosa:** Caracteres como el tímpano o patrones de piel no son reconocibles.
- **Oclusión Extrema:** Más del 80% del espécimen está cubierto por vegetación o sustrato.
- **Iluminación Inservible:** Imagen completamente quemada (sobreexpuesta) o en penumbra total (subexpuesta) sin detalle visible.
- **Imágenes Duplicadas:** Ráfagas continuas (>95% de similitud) del mismo ángulo e individuo.

#### **B. Estándar de Clases Anatómicas para Segmentación en Roboflow**

| **ID** | **Clase Anatomía** | **Indicaciones Precisas de Etiquetado Manual** |
| --- | --- | --- |
| **0** | **Fondo (Background)** | àreas fuera de la silueta del anuro (hojarasca, rocas, agua, ramas). |
| **1** | **Cuerpo / Torso** | Polígono continuo siguiendo el contorno principal del espécimen. |
| **2** | **Ojos** | Polígono ajustado al borde exacto de la órbita ocular. Evitar fondo alrededor. |
| **3** | **Manos / Dedos Ant.** | Extremidades anteriores, incluyendo discos digitales visibles. |
| **4** | **Patas / Dedos Post.** | Extremidades posteriores, incluyendo membranas interdigitales. |
| **5** | **Tímpano** | **Clase Crítica (Rara):** Delimitar con alta precisión la membrana timpánica. |
| **6** | **Boca** | Delimitación del contorno labial/mandibular visible. |
| **7** | **Piel / Textura** | Opcional/Sujeto a visibilidad de tubérculos o crestas. |

> **Regla de Oclusión Parcial:** Si una pata o parte del torso está tapada por una hoja, **nunca adivinar la forma oculta**. Etiquetar àºnicamente la superficie visible.
> 

#### **Modelo 2: Pipeline de Identificación de Especie (Paquetes y JSON Automático)**

**Objetivo:** Generar el conjunto masivo de entrenamiento para la clasificación/identificación de especies a partir de las imágenes aprobadas.

#### **A. Generación Automática del Dataset de Entrenamiento**

1. **Paso 1:** Las imágenes originales y validadas se agrupan en paquetes.
2. **Paso 2:** Se ejecuta la canalización de **Data Augmentation** al vuelo (*batch processing*), aplicando las transformaciones permitidas (geometría, brillo, sombreado, degradación) para ampliar las **550 imágenes originales de Train** a un lote sintético de **5,100 a 6,000 imágenes**.
3. **Paso 3 (Etiquetado Automático en JSON):** El sistema genera automáticamente el archivo `.json` de anotación con las etiquetas taxonómicas jerárquicas (`Familia` $\rightarrow$ `Género` $\rightarrow$ `Especie`), asociando cada imagen derivada/augmentada con sus metadatos y coordenadas de recorte.

#### **Matriz de Transformaciones de Augmentation (Modelo 2)**

| **Categoria** | **Transformación** | **Parámetros** | **Probabilidad (p)** | **Propósito Técnico** |
| --- | --- | --- | --- | --- |
| **Geometría** | HorizontalFlip | â€” | 0.5 | Espejado horizontal |
| **Geometría** | VerticalFlip | â€” | 0.3 | Poses invertidas |
| **Geometría** | RandomRotate90 | 90° | 0.5 | Rotaciones ortogonales |
| **Geometría** | ShiftScaleRotate | limit=0.2, R_lim=0.3 | 0.5 | Zoom ($\pm 20\%$) y variabilidad de pose |
| **Geometría** | ElasticTransform | alpha=120, sigma=6 | 0.3 | Deformación orgánica (pose real) |
| **Geometría** | GridDistortion | â€” | 0.2 | Deformación de superficie |
| **Geometría** | Perspective | â€” | 0.3 | Cambio de ángulo de cámara |
| **Iluminación** | RandomBrightnessContrast | limits=0.3 | 0.5 | Condiciones de luz de campo |
| **Iluminación** | RandomShadow | â€” | 0.2 | Sombras de follaje |
| **Color** | HueSaturationValue | hue=10, sat=20, val=20 | 0.3 | Variación intraespecífica (**Hue restringido**) |
| **Color** | RGBShift | r=15, g=15, b=15 | 0.3 | Temperatura de color |
| **Calidad** | CLAHE | clip=4.0 | 0.3 | Contraste local en sustratos oscuros |
| **Calidad** | GaussianBlur | blur_limit=3 | 0.2 | Desenfoque de lente móvil |
| **Calidad** | GaussNoise | var_limit=(10,50) | 0.2 | Ruido de sensor ISO en noche |
| **Calidad** | ImageCompression | quality=60-100 | 0.3 | Artefactos JPEG de compresión móvil |
| **Estructura** | CoarseDropout | holes=8, size=32 | 0.3 | Oclusión sintética para anti-overfitting |

#### **Estructura y Reglas del Split de Datos**

| **Etapa** | **Imágenes Originales** | **Con Augmentación** | **Método de Etiquetado** | **Destino / Propósito** |
| --- | --- | --- | --- | --- |
| **Train** | **550** | **5,100 â€“ 6,000** | Automático en **JSON** (post-augmentation) | Entrenamiento de ambos modelos. |
| **Validación** | **120** | **N/A (Sin Augmentation)** | Manual (Roboflow) / JSON Limpio | Ajuste de hiperparámetros y *early stopping*. |
| **Test** | **120** | **N/A (Sin Augmentation)** | Manual (Roboflow) / JSON Limpio | Evaluación final y benchmarking offline. |

#### **Reglas para Evitar Fuga de Información (*Data Leakage*):**

1. **Split por Localidad / Individuo (GroupSplit):** Fotografías del mismo espécimen o tomadas en el mismo punto de campo pertenecen **100% al mismo conjunto** (*Train*, *Val* o *Test*).
2. **Aislamiento de Augmentación:** La augmentación se aplica **àºnicamente** a los paquetes del conjunto de *Train*. *Val* y *Test* permanecen intactos con datos originales de campo.
3. **Filtrado Open-Set:** Imágenes de especies no incluidas en el modelo o falsos positivos (hojas, insectos) se reservan para verificar la capacidad del sistema móvil de responder *"Especie No Registrada / Desconocida"*.



