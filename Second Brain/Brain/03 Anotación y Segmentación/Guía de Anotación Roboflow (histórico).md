---
title: "GuÃ­a de AnotaciÃ³n Roboflow (histÃ³rico)"
proyecto: Anura
fuente: "Notion â€” Proyecto IdentificaciÃ³n de Anuros Colombia"
tags: [anura, anotaciÃ³n, histÃ³rico]
---

# GuÃ­a de AnotaciÃ³n Roboflow (histÃ³rico)

**Objetivo del Anotador:** Delimitar manualmente el cuerpo y las partes anatÃ³micas clave sobre imÃ¡genes originales sin procesar.

#### **A. Criterios de SelecciÃ³n y Limpieza de ImÃ¡genes (Pre-AnotaciÃ³n)**

Antes de anotar una imagen en Roboflow, el etiquetador debe descartarla si cumple con alguna de estas condiciones:

- **Fuera de Foco / Borrosa:** Caracteres como el tÃ­mpano o patrones de piel no son reconocibles.
- **OclusiÃ³n Extrema:** MÃ¡s del 80% del espÃ©cimen estÃ¡ cubierto por vegetaciÃ³n o sustrato.
- **IluminaciÃ³n Inservible:** Imagen completamente quemada (sobreexpuesta) o en penumbra total (subexpuesta) sin detalle visible.
- **ImÃ¡genes Duplicadas:** RÃ¡fagas continuas (>95% de similitud) del mismo Ã¡ngulo e individuo.

#### **B. EstÃ¡ndar de Clases AnatÃ³micas para SegmentaciÃ³n en Roboflow**

| **ID** | **Clase AnatomÃ­a** | **Indicaciones Precisas de Etiquetado Manual** |
| --- | --- | --- |
| **0** | **Fondo (Background)** | Ãreas fuera de la silueta del anuro (hojarasca, rocas, agua, ramas). |
| **1** | **Cuerpo / Torso** | PolÃ­gono continuo siguiendo el contorno principal del espÃ©cimen. |
| **2** | **Ojos** | PolÃ­gono ajustado al borde exacto de la Ã³rbita ocular. Evitar fondo alrededor. |
| **3** | **Manos / Dedos Ant.** | Extremidades anteriores, incluyendo discos digitales visibles. |
| **4** | **Patas / Dedos Post.** | Extremidades posteriores, incluyendo membranas interdigitales. |
| **5** | **TÃ­mpano** | **Clase CrÃ­tica (Rara):** Delimitar con alta precisiÃ³n la membrana timpÃ¡nica. |
| **6** | **Boca** | DelimitaciÃ³n del contorno labial/mandibular visible. |
| **7** | **Piel / Textura** | Opcional/Sujeto a visibilidad de tubÃ©rculos o crestas. |

> **Regla de OclusiÃ³n Parcial:** Si una pata o parte del torso estÃ¡ tapada por una hoja, **nunca adivinar la forma oculta**. Etiquetar Ãºnicamente la superficie visible.
> 

#### **Modelo 2: Pipeline de IdentificaciÃ³n de Especie (Paquetes y JSON AutomÃ¡tico)**

**Objetivo:** Generar el conjunto masivo de entrenamiento para la clasificaciÃ³n/identificaciÃ³n de especies a partir de las imÃ¡genes aprobadas.

#### **A. GeneraciÃ³n AutomÃ¡tica del Dataset de Entrenamiento**

1. **Paso 1:** Las imÃ¡genes originales y validadas se agrupan en paquetes.
2. **Paso 2:** Se ejecuta la canalizaciÃ³n de **Data Augmentation** al vuelo (*batch processing*), aplicando las transformaciones permitidas (geometrÃ­a, brillo, sombreado, degradaciÃ³n) para ampliar las **550 imÃ¡genes originales de Train** a un lote sintÃ©tico de **5,100 a 6,000 imÃ¡genes**.
3. **Paso 3 (Etiquetado AutomÃ¡tico en JSON):** El sistema genera automÃ¡ticamente el archivo `.json` de anotaciÃ³n con las etiquetas taxonÃ³micas jerÃ¡rquicas (`Familia` $\rightarrow$ `GÃ©nero` $\rightarrow$ `Especie`), asociando cada imagen derivada/augmentada con sus metadatos y coordenadas de recorte.

#### **Matriz de Transformaciones de Augmentation (Modelo 2)**

| **Categoria** | **TransformaciÃ³n** | **ParÃ¡metros** | **Probabilidad (p)** | **PropÃ³sito TÃ©cnico** |
| --- | --- | --- | --- | --- |
| **GeometrÃ­a** | HorizontalFlip | â€” | 0.5 | Espejado horizontal |
| **GeometrÃ­a** | VerticalFlip | â€” | 0.3 | Poses invertidas |
| **GeometrÃ­a** | RandomRotate90 | 90Â° | 0.5 | Rotaciones ortogonales |
| **GeometrÃ­a** | ShiftScaleRotate | limit=0.2, R_lim=0.3 | 0.5 | Zoom ($\pm 20\%$) y variabilidad de pose |
| **GeometrÃ­a** | ElasticTransform | alpha=120, sigma=6 | 0.3 | DeformaciÃ³n orgÃ¡nica (pose real) |
| **GeometrÃ­a** | GridDistortion | â€” | 0.2 | DeformaciÃ³n de superficie |
| **GeometrÃ­a** | Perspective | â€” | 0.3 | Cambio de Ã¡ngulo de cÃ¡mara |
| **IluminaciÃ³n** | RandomBrightnessContrast | limits=0.3 | 0.5 | Condiciones de luz de campo |
| **IluminaciÃ³n** | RandomShadow | â€” | 0.2 | Sombras de follaje |
| **Color** | HueSaturationValue | hue=10, sat=20, val=20 | 0.3 | VariaciÃ³n intraespecÃ­fica (**Hue restringido**) |
| **Color** | RGBShift | r=15, g=15, b=15 | 0.3 | Temperatura de color |
| **Calidad** | CLAHE | clip=4.0 | 0.3 | Contraste local en sustratos oscuros |
| **Calidad** | GaussianBlur | blur_limit=3 | 0.2 | Desenfoque de lente mÃ³vil |
| **Calidad** | GaussNoise | var_limit=(10,50) | 0.2 | Ruido de sensor ISO en noche |
| **Calidad** | ImageCompression | quality=60-100 | 0.3 | Artefactos JPEG de compresiÃ³n mÃ³vil |
| **Estructura** | CoarseDropout | holes=8, size=32 | 0.3 | OclusiÃ³n sintÃ©tica para anti-overfitting |

#### **Estructura y Reglas del Split de Datos**

| **Etapa** | **ImÃ¡genes Originales** | **Con AugmentaciÃ³n** | **MÃ©todo de Etiquetado** | **Destino / PropÃ³sito** |
| --- | --- | --- | --- | --- |
| **Train** | **550** | **5,100 â€“ 6,000** | AutomÃ¡tico en **JSON** (post-augmentation) | Entrenamiento de ambos modelos. |
| **ValidaciÃ³n** | **120** | **N/A (Sin Augmentation)** | Manual (Roboflow) / JSON Limpio | Ajuste de hiperparÃ¡metros y *early stopping*. |
| **Test** | **120** | **N/A (Sin Augmentation)** | Manual (Roboflow) / JSON Limpio | EvaluaciÃ³n final y benchmarking offline. |

#### **Reglas para Evitar Fuga de InformaciÃ³n (*Data Leakage*):**

1. **Split por Localidad / Individuo (GroupSplit):** FotografÃ­as del mismo espÃ©cimen o tomadas en el mismo punto de campo pertenecen **100% al mismo conjunto** (*Train*, *Val* o *Test*).
2. **Aislamiento de AugmentaciÃ³n:** La augmentaciÃ³n se aplica **Ãºnicamente** a los paquetes del conjunto de *Train*. *Val* y *Test* permanecen intactos con datos originales de campo.
3. **Filtrado Open-Set:** ImÃ¡genes de especies no incluidas en el modelo o falsos positivos (hojas, insectos) se reservan para verificar la capacidad del sistema mÃ³vil de responder *"Especie No Registrada / Desconocida"*.



