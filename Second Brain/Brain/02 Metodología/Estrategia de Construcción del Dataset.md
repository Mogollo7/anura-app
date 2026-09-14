---
title: "Estrategia de Construcción del Dataset"
proyecto: Anura
fuente: "Notion â€” Proyecto Identificación de Anuros Colombia"
tags: [anura, metodología, dataset]
---

# Estrategia de Construcción del Dataset

## Estrategia de construcción de dataset

#### **Objetivo del Dataset**

- **Tarea Principal:** Construir un conjunto de datos representativo que integre màºltiples individuos provenientes de diversas áreas geográficas, orientado al entrenamiento y validación de modelos de inteligencia artificial para la automatización del procesamiento de datos en anfibios.
- **Requerimientos Base:**
    - Inclusión de màºltiples especies de anuros.
    - Mínimo **70 individuos por especie**.
    - Etiquetado jerárquico estructurado a nivel de **Familia, Género y Especie**.
    - Integración en una **base de datos vectorial** para optimizar la bàºsqueda por similitud y mejorar el flujo de procesamiento de datos.

> [!important] Cifras reales confirmadas para el prototipo del 27 de septiembre (2026-09-05)
> El catálogo del prototipo son las **28 especies** de C-3 ([[Inconsistencias y Decisiones Pendientes]]). Confirmado por el autor: **70 individuos/especie** para el modelo de identificación â€” el requisito original, cumplido, no una reducción (riesgo D-3 en [[Riesgos del Proyecto]] no se materializó) â€” y **25â€“30 imágenes/especie** para el subconjunto ya anotado del modelo de segmentación anatómica, un modelo distinto con un requisito de volumen menor, dentro del rango 20â€“40/especie ya previsto para el segmentador en I-5.

#### **Niveles de Clasificación y Metas de Desempeño**

Las metas de rendimiento evaluadas exclusivamente a partir de información visual (sin inclusión de metadatos de contexto como ubicación o bioacàºstica en esta fase inicial) son:

- **Familia:** Precisión objetivo del **90% al 95%**.
- **Género:** Precisión objetivo del **80% al 85%**.
- **Especie:** Precisión objetivo de al menos **80%**.

#### **Resultados Obtenidos (Etapa I)**

La evaluación preliminar del modelo sobre el conjunto de validación alcanzó una **Exactitud Global (Validation Accuracy) del 95.69%**.

> [!important] Actualización del autor â€” la cifra real es ~99 %
> El resultado real de la Etapa I fue de **~99 % de exactitud**, no 95,69 %. Es un resultado legítimo, no un indicio de fuga de información: se apoya en (1) **segmentación binaria individuo-vs-fondo** aplicada antes de pasar la imagen al modelo de clasificación, (2) **70 individuos por especie** en estas 10 especies, con las fotos de cada individuo confinadas a un àºnico conjunto (train/val/test), y (3) diversidad de individuos en vez de tomas repetidas del mismo ejemplar. Detalle metodológico completo, y por qué esto satisface exactamente lo que un split riguroso exige, en [[Modelo de Visión â€” BioCLIP]] §7. Se conserva la cifra y la tabla originales por trazabilidad del documento fuente.

**Tabla 1.** *Métricas de desempeño por especie en la Etapa I.*

| **Especie** | **Precisión** | **Sensibilidad (Recall)** | **Puntuación F1 (F1-Score)** |
| --- | --- | --- | --- |
| *Dendrobates truncatus* | 100% | 100% | 1.00 |
| *Dendropsophus bogerti* | 96% | 96% | 0.96 |
| *Dendropsophus microcephalus* | 93% | 100% | 0.96 |
| *Hyloscirtus palmeri* | 100% | 100% | 1.00 |
| *Leucostethus fraterdanieli* | 100% | 100% | 1.00 |
| *Pristimantis acanthinus* | 95% | 95% | 0.95 |
| *Pristimantis paisa* | 85% | 88% | 0.86 |
| *Pristimantis penelopus* | 90% | 83% | 0.86 |
| *Rhinella alata* | 100% | 100% | 1.00 |
| *Rhinella horribilis* | 100% | 95% | 0.97 |

### **Observaciones Principales sobre los Resultados:**

- **Desempeño Sobresaliente:** Especies como *Dendrobates truncatus*, *Hyloscirtus palmeri*, *Leucostethus fraterdanieli* y *Rhinella alata* alcanzaron un *F1-Score* perfecto de 1.00, lo que demuestra alta separabilidad visual en estos taxones.
- **Complejidad Taxonómica Detectada:** Se observa una ligera disminución en el desempeño dentro del género *Pristimantis* (*P. paisa* con F1 de 0.86 y *P. penelopus* con F1 de 0.86), reflejando la alta variabilidad morfológica y cripticidad taxonómica característica del grupo.

### **Estrategia y Estructura del Dataset de Anuros**

#### **Resumen de Etapas de Construcción**

- **Etapa I (Fase Inicial de Validación Visual):**
    - **Nàºmero de Clases (Especies):** 14 especies mencionadas en el texto original; **10 especies confirmadas** por el autor y por la Tabla 1 de resultados â€” usar esta àºltima como cifra oficial ([[Inconsistencias y Decisiones Pendientes]], C-3).
    - **Diversidad Taxonómica:** 4 familias y 6 géneros.
    - **Enfoque:** Evaluación del modelo base sin metadatos de contexto (solo imágenes).
- **Etapa II (Expansión Geográfica y Taxonómica):**
    - **Regiones de Muestreo:** Antioquia y San José del Guaviare (Serranía de La Lindosa).
    - **Objetivo:** Capturar variabilidad intraespecífica e interespecífica mediante una cobertura biogeográfica más amplia.

#### **Distribución Biogeográfica del Dataset (Etapa II)**

#### **A. Región Antioquia**

Se dividió el muestreo en tres subregiones clave, sumadas a las especies de distribución general en el departamento:

- **Especies Generalistas de Antioquia:** *Pristimantis acanthinus*, *Pristimantis paisa*, *Rhinella alata*, *Rhinella horribilis* y *Dendropsophus bogerti*.
- **Subregión San Rafael:** *Rheobates palmatus*, *Sachatamia electrops*, *Scinax ruber*, *Craugastor raniformis*, *Hyloscirtus palmeri*, *Pristimantis norandinus*, *Dendropsophus microcephalus* y *Pristimantis taeniatus*.
- **Subregión Caldas:** *Leucostethus fraterdanieli*.
- **Subregión Caracolí:** *Dendrobates truncatus*, *Engystomops pustulosus* y *Pristimantis penelopus*.

[Antioquia - Google Drive](https://drive.google.com/drive/folders/1P_KadCV-HXcmhqQVQzk_UeepTuR--QrD?usp=drive_link)

#### **B. Región San José del Guaviare (Serranía de La Lindosa)**

- **Especies de la Guayana / Amazonia:** *Dendropsophus reticulatus*, *Dendropsophus triangulum*, *Boana cinereascens*, *Boana lanciformis*, *Boana punctata*, *Boana xerophylla*, *Pithecopus hypochondrialis*, *Phyllomedusa tarsius*, *Hyloxalus picachus*, *Pristimantis vilarsi*, *Leptodactylus colombiensis* y *Rhinella* sp. (grupo *margaritifera*).

[San José del Guaviare - Google Drive](https://drive.google.com/drive/folders/1PuI0g2HQrKMRl64alf-XWSTfEioZDZe7?usp=drive_link)

---

[[Listado de Individuos y Arreglo Taxonómico]]

---

### **Fuentes de Datos y Trazabilidad**

#### **Fuentes Primarias**

- **Registro de Campo Propio:** Los datos fotográficos primarios provienen del trabajo de campo realizado por el investigador Miguel àngel Vergara Mazo, enfocado en la recolección *in situ* de muestras visuales de especímenes de anuros en diversas localidades del departamento de Antioquia (incluyendo los municipios de Caldas, Caracolí y San Rafael) y en la Serranía de La Lindosa (San José del Guaviare).

[dataset - Google Drive](https://drive.google.com/drive/folders/1yce4TNLlO_yAS7cyWdp1395PQU3gFZWj?usp=sharing)

### Calidad y Estandarización de Datos de Campo

Cada muestra primaria del *dataset* cuenta con **validación taxonómica previa** realizada por expertos y **metadatos biológicos asociados** a su hábitat natural.

Para robustecer la variabilidad geográfica y la precisión de los modelos, el proceso de estandarización integra las siguientes reglas:

1. **Enriquecimiento Vía Registros Pàºblicos Georreferenciados:**
    - Se descargan e integran registros biológicos de plataformas pàºblicas (como GBIF e iNaturalist) verificando que cuenten con coordenadas geográficas precisas e incertidumbre espacial controlada.
    

> [!info]
> Los anuros presentan un alto grado de **polimorfismo**, lo que puede generar variaciones significativas en la apariencia de individuos de una misma especie dependiendo de su ubicación geográfica. Por esta razón, se recomienda aplicar **filtros por ubicación geográfica** durante la selección de los datos de entrenamiento, con el fin de evitar introducir sesgos o "contaminar" el conjunto de datos con patrones geográficos que puedan afectar la capacidad de generalización del modelo. Los datos excluidos del entrenamiento pueden conservarse como **datos de apoyo o evaluación secundaria**.
    
    - A cada imagen de entrenamiento proveniente de estos repositorios o colectas asociadas se le asigna la coordenada exacta de avistamiento del individuo si es posible sino se le aplican una de otra fotografía para entrenamiento.
2. **Beneficios de la Georreferenciación en el Entrenamiento:**
    - **Contexto Geoespacial:** Permite que las imágenes de entrenamiento conserven su ubicación real para cruzar la distribución geográfica de las especies con variables bioclimáticas (altitud, temperatura, precipitación) en análisis posteriores.
    - **Prevención de Sesgo Geográfico:** Garantiza una distribución espacial amplia en el conjunto de *Train*, evitando que el modelo aprenda àºnicamente patrones de una sola localidad o región.
    - **Filtrado de Calidad:** Las muestras que carezcan de coordenadas verificables o presenten discrepancias entre la distribución conocida de la especie y la ubicación registrada son marcadas para revisión manual o descartadas.

#### **Fuentes Secundarias**

- **Plataformas de Ciencia Ciudadana ([iNaturalist](https://www.inaturalist.org/)):** Se utiliza la API de iNaturalist como fuente complementaria de imágenes. Sin embargo, los datos obtenidos pasan por un **proceso de control y revisión manual**, con el fin de verificar su calidad, identificación taxonómica y procedencia, evitando así la incorporación de imágenes que puedan **contaminar o introducir sesgos en los datos de entrenamiento**.
- **Criterio de Inclusión:** El recurso secundario se activa àºnicamente en aquellas especies donde las capturas fotográficas de fuente primaria no alcanzan el umbral mínimo requerido de **70 individuos independientes**.

#### **Trazabilidad y Gestión de Almacenamiento**

- **Generación de *Embeddings*:** En lugar de distribuir los archivos de imagen crudos de alto volumen, la canalización de procesamiento genera y conserva exclusivamente los vectores de características (*embeddings*) extraídos durante la etapa de representación visual.
- **Empaquetado Biogeográfico Modular:** Los *embeddings* se agrupan y empaquetan modularmente por regiones biogeográficas (por ejemplo, Región Antioquia y Región Guaviare).
- **Eficiencia de Despliegue:** Esta arquitectura de almacenamiento optimizado permite a los usuarios e investigadores descargar àºnicamente los paquetes vectoriales específicos segàºn la zona de prueba o el contexto de interés, reduciendo drásticamente los tiempos de transferencia y los requerimientos computacionales del sistema.

#### Propuesta: tabla de seguimiento del dataset (reemplaza la base de datos vacía de Notion)

El enlace a esta base en Notion está vacío (M-5 en [[Inconsistencias y Decisiones Pendientes]]); en vez de dejarlo vacío también aquí, esta es la estructura mínima operativa para que el equipo sepa en qué estado está cada especie sin tener que preguntarlo:

| Campo | Contenido |
| --- | --- |
| Especie | Una fila por cada una de las 28 especies |
| Familia / Género | Para poder agrupar y detectar huecos taxonómicos |
| Región biogeográfica | Antioquia / Guaviare / ambas |
| N.º individuos propios | Contador real, actualizado al recolectar |
| N.º imágenes por individuo | Para distinguir, por ejemplo, "70 individuos con 1 foto" de "35 individuos con 2 fotos" â€” el total de imágenes no basta, lo que cuenta es el nàºmero de individuos distintos |
| Fuente | Campo propio / iNaturalist / GBIF |
| Verificación taxonómica | Pendiente / Verificada por experto |
| Split asignado | Train / Val / Test â€” fijado una vez, nunca recalculado por especie suelta |
| Anotado en CVAT | Sí / No / En proceso |

Mantenerla como una hoja de cálculo simple (o una tabla en este mismo vault) es suficiente para el sprint; no hace falta Notion para esto.

### Criterios de calidad

Para la **V2**, al incorporar **procesamiento offline en el móvil**, el flujo cambia sustancialmente: el procesamiento morfológico, la inferencia del modelo y la optimización deben ocurrir directamente en el dispositivo antes de cualquier sincronización.

#### Flujo de imágenes en V2 (Móvil Offline-First)

- **Captura y Procesamiento Local:**
    - **Inferencia Offline:** La imagen se pasa directamente al modelo local (escalada en memoria a la resolución de entrada requerida, ej. 224à—224) para obtener la predicción sin depender de conexión.
    - **Compresión Local:** Se redimensiona la imagen a **1024à—768 px** (formato 4:3) y se convierte a **WebP al 80% de calidad**, reduciendo el peso de ~300 KB a **~70-100 KB**.
- **Almacenamiento en Cola (Offline Storage):**
    - La imagen optimizada (~80 KB) y sus metadatos (predicción local, coordenadas GPS, fecha/hora) se guardan en el almacenamiento local del dispositivo (SQLite / Base de datos local).
    - Al trabajar con la versión optimizada en local, el almacenamiento del teléfono no se satura aunque el usuario registre decenas de especímenes en campo.
- **Sincronización Diferida (Background Sync):**
    - Una vez que el dispositivo detecta conexión a internet (Wi-Fi o datos), se dispara la sincronización en segundo plano enviando el paquete ligero (~80 KB por registro) al servidor/backend.

#### Resumen de Especificaciones V1 vs. V2

| **Parámetro** | **Versión 1 (Web / Servidor)** | **Versión 2 (Móvil Offline)** |
| --- | --- | --- |
| **Lugar de Procesamiento** | Servidor | **Dispositivo Móvil (Edge)** |
| **Inferencia / Predicción** | Online (Vía API) | **Offline (En el dispositivo)** |
| **Resolución Guardada** | 600 à— 450 px | **1024 à— 768 px** |
| **Compresión** | Sin compresión (Original) | **WebP 80% (Compresión local)** |
| **Peso Promedio** | ~300 KB | **~70 - 100 KB** |
| **Estrategia de Datos** | Carga inmediata | **Cola local + Sincronización diferida** |

#### Propuesta: tabla de seguimiento de imágenes (reemplaza la base de datos vacía de Notion)

| Campo | Contenido |
| --- | --- |
| ID de imagen | Hash o UUID, no el nombre de archivo original |
| Especie / Individuo | Vínculo a la tabla de dataset de arriba |
| Vista | Dorsal / ventral / lateral / detalle |
| Resolución y formato originales | Antes de procesar |
| Resolución y formato procesados | 1024à—768 WebP 80 % (V2, ver tabla arriba) |
| Fecha y coordenadas de captura | Cuando existan |
| Anotada en CVAT | Sí / No |
| Split | Train / Val / Test |

La estrategia de **compresión y miniaturas en tiempo de ejecución** (para no decodificar imágenes completas en el Listado de la app) está en [[App Móvil]] §6 â€” esta tabla es sobre el dataset de entrenamiento, esa nota es sobre el runtime de la app.

---

#### Estándar à“ptimo Recomendado (Bioacàºstica Móvil)

| **Parámetro** | **Valor à“ptimo** | **Justificación Técnica** |
| --- | --- | --- |
| **Formato** | **WAV / PCM 16-bit** (Raw) | Los algoritmos de extracción de características (espectrogramas, MFCCs) e inferencia requieren datos sin pérdidas. Evita MP3 o AAC, ya que la compresión psicoacàºstica descarta armónicos finos e interrumpe las frecuencias dominantes. |
| **Tasa de Muestreo** | **44.1 kHz** (o 22.05 kHz) | Por el teorema de Nyquist, 44.1 kHz captura frecuencias de hasta 22.05 kHz, cubriendo holgadamente el espectro vocal de la mayoría de anuros y fauna (1 kHz - 12 kHz). |
| **Canales** | **Mono (1 canal)** | Reduce el tamaño del archivo a la mitad sin perder información acàºstica relevante para la identificación del canto. |
| **Duración** | **3 a 5 segundos** | Suficiente para registrar màºltiples notas o pulsos repetitivos del canto de advertencia (*advertisement call*). Las ventanas largas (e.g., 30s) aumentan innecesariamente el peso y dificultan el aislamiento de eventos de sonido. |
| **SNR Mínimo** | **â‰¥ 15 dB a 20 dB** | Garantiza que la frecuencia dominante de las notas resalte claramente sobre el ruido de fondo (viento, agua, lluvia o ruido ambiental). Un SNR menor a 10 dB suele degradar fuertemente la matriz del espectrograma. |

### Estimación de Peso y Recurso

- **Archivo de audio limpio (WAV Mono 44.1kHz 16-bit, 5s):** **~441 KB**
- **Audio comprimido para almacenamiento local/sync (FLAC):** **~200 KB - 250 KB** (compresión sin pérdidas para la cola de sincronización offline).
- **Matriz de espectrograma de entrada al modelo (Mel-Spectrogram):** Una vez procesado en el móvil, la ventana de audio de 3-5s se convierte en una matriz 2D pequeña (ej. 128 bins à— 256 pasos), requiriendo un costo de inferencia muy bajo en el procesador del dispositivo.

*Estrategia de Manejo de Audio* (base de datos vacía en Notion)

#### Contingencia de audio (si no se alcanza el volumen propio a tiempo)

> [!important] Decisión: crecimiento progresivo, no todo-o-nada
> La rama acàºstica **no debe bloquear el prototipo del 27 de septiembre** ([[Cronograma y Plan de Trabajo]] §0). Al reutilizar BioCLIP como codificador acàºstico ([[Modelo de Visión â€” BioCLIP]] §8), el volumen necesario para calibrar y validar es menor que el de entrenar un backbone de audio desde cero â€” pero sigue haciendo falta grabaciones reales para el subconjunto de especies que la incluyan.

Fuentes externas evaluadas, en orden de relevancia para anuros neotropicales:

| Fuente | Qué ofrece | Cómo usarla aquí |
| --- | --- | --- |
| **AnuraSet** (Cañas et al., 2023) | ~93 000 fragmentos de 3 s, 42 especies de anuros neotropicales, grabación pasiva en Brasil; descarga directa (~10,5 GB) en [Zenodo](https://zenodo.org/records/8056090) y código en [GitHub â€” soundclim/anuraset](https://github.com/soundclim/anuraset) | Referencia externa ya prevista en el riesgo D-5; àºtil sobre todo para géneros compartidos con el catálogo de Anura (p. ej. *Boana*, *Dendropsophus*, *Scinax*, *Rhinella*) aunque las especies exactas no coincidan siempre â€” sirve para calibrar/validar el codificador acàºstico compartido, no como sustituto de grabaciones propias de las 28 especies objetivo |
| **Xeno-canto â€” colección Anura** | Base de grabaciones de fauna abierta; colección específica de anuros iniciada en marzo de 2024, con cobertura mundial creciente | Revisar especie por especie del catálogo de Anura si hay grabaciones con licencia compatible (CC); es la fuente con mayor probabilidad de tener **especies exactas** del catálogo, aunque la cobertura por especie es desigual y hay que verificarla, no asumirla |
| **iNaturalist (observaciones con audio)** | Observaciones de ciencia ciudadana que a veces incluyen grabación de audio, ya usada como fuente secundaria de imágenes en este mismo documento | Mismo criterio de control de calidad ya aplicado a las imágenes: verificación taxonómica e identificación antes de incorporar cualquier audio |

**Procedimiento de la semana 1 del sprint** ([[Cronograma y Plan de Trabajo]] §0):

1. Cruzar las 28 especies del catálogo (C-3 en [[Inconsistencias y Decisiones Pendientes]]) contra AnuraSet y Xeno-canto para ver cuántas tienen cobertura directa o a nivel de género.
2. Si el subconjunto cubierto es razonable (criterio a fijar con el equipo, p. ej. â‰¥ 8â€“10 especies o sus géneros): implementar la rama acàºstica **solo para ese subconjunto** en el prototipo, dejando el resto como "sin audio" â€” el sistema ya está diseñado para funcionar con modalidades ausentes (RNF-06, [[Arquitectura Multimodal]] §3).
3. Si la cobertura es insuficiente incluso a nivel de género: declarar la rama acàºstica como trabajo futuro para el prototipo del 27 de septiembre, sin que esto afecte al resto del pipeline â€” es exactamente la salida que ya contempla el punto de decisión "¿Hay datos de audio suficientes?" en [[Cronograma y Plan de Trabajo]].
4. Cualquiera que sea el resultado, el crecimiento posterior es **modular**: añadir audio de una especie nueva no reentrena el codificador (es el mismo BioCLIP compartido) â€” solo añade embeddings acàºsticos a la base vectorial, igual que el Nivel 1 de [[Escalabilidad]] para imágenes.

---

#### **Flujo General de Preparación de Datos**

```
[Capturas de Campo]
       â”‚
       â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  MODELO 1: SEGMENTACIà“N SEMàNTICA (Manual en Roboflow)  â”‚
â”‚  â€¢ Selección de imágenes originales limpia             â”‚
â”‚  â€¢ Trazo manual de partes anatómicas (0 a 7)            â”‚
â”‚  â€¢ Generación de máscaras / JSON                       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                           â”‚
                           â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  MODELO 2: IDENTIFICACIà“N DE ESPECIE (Automático)      â”‚
â”‚  â€¢ Aplicación de Data Augmentation por lotes/paquetes  â”‚
â”‚  â€¢ Generación automática de archivo JSON de anotación  â”‚
â”‚  â€¢ Generación de 5,100 - 6,000 muestras para Train     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

[[Guía de Anotación Roboflow (histórico)]]

---

#### **Control de Duplicados**

- **Filtrado por Hash de Percepción (pHash / Difference Hash):** Eliminación automática de imágenes idénticas o ráfagas continuas donde no exista variación morfológica o de pose (>95% de similitud estructural).
- **Aislamiento de Indiviuos:** Fotografías del mismo espécimen tomadas en el mismo evento de muestreo deben agruparse bajo un àºnico ID de Individuo.

#### **Criterios de Exclusión (Descarte Directo)**

- **Fuera de Foco/Desenfoque severo:** Fotografías donde los caracteres diagnósticos clave (tímpano, textura de piel, tubérculos) sean irreconocibles por movimiento o mala focalización.
- **Oclusión Extrema:** Imágenes donde el espécimen esté cubierto en más de un $80\%$ por sustrato o vegetación, impidiendo la delimitación del torso.
- **Iluminación Degradada:** Exposición extrema (completamente subexpuesta sin detalle en sombras o sobreexpuesta con píxeles quemados en el patrón de coloración).
- **Audio Degradado:** Fragmentos con $SNR < 10\text{ dB}$, saturación de micrófono por proximidad excesiva, o interferencia dominante de ruido eólico/lluvia sobre la frecuencia fundamental del canto.

---

### **Variabilidad Necesaria (Criterios de Inclusión y Diversidad)**

Para garantizar la generalización del modelo en campo bajo operación offline, el dataset debe recopilar:

- **Variación Visual:** Màºltiples ángulos (dorsal, lateral, ventral), variedad de sustratos (hojarasca, rocas, vegetación, musgo), distintas distancias de captura y oclusiones parciales naturales.
- **Variación por Individuo:** Muestreo balanceado entre machos, hembras, juveniles y adultos, así como polimorfismos cromáticos (morfos de coloración dentro de la misma especie).
- **Variación Ambiental:** Capturas diurnas y nocturnas (con uso de linterna/flash), condiciones de lluvia/humedad alta y diversidad de microhábitats.
- **Variación Geográfica:** Colectas distribuidas en diferentes departamentos, valles interandinos y gradientes de elevación para mitigar el sesgo por poblaciones locales.
- **Variación Temporal:** Registros recopilados en diferentes épocas del año (temporadas secas y de lluvias/picos reproductivos).

---

### **Data Augmentation y Políticas de No Sesgo**

#### **Transformaciones Permitidas (Imagen)**

- **Geométricas:** `HorizontalFlip` (p=0.5), `VerticalFlip` (p=0.3), `RandomRotate90` (p=0.5), `ShiftScaleRotate` (límite 20%, p=0.5), `ElasticTransform` y `GridDistortion` (deformación orgánica suave para simular postura).
- **Color e Iluminación:** `RandomBrightnessContrast` (pm 30%), `RandomShadow` (p=0.2), `HueSaturationValue` (límite estricto en Hue: pm 10, Saturation/Value: pm 20), `CLAHE` (clip=4.0).

#### **Transformaciones Permitidas (Audio)**

- **Espectrograma / Dominio de Onda:** `TimeShift` (desplazamiento temporal), adición de ruido blanco/ambiental de fondo suave (SNR  15 dB), `FrequencyMasking` y `TimeMasking` (SpecAugment sobre la matriz de espectrograma).

#### **Transformaciones NO Permitidas (Riesgo Biológico)**

- **Modificación Excesiva de Color (`HueShift > 15`):** Alterar los tonos drásticamente invalida la respuesta del modelo en especies donde la coloración o aposematismo es el carácter taxonómico primario (ej. *Dendrobatidae*).
- **Inversión de Espectrogramas / Pitch Shift Extremo en Audio:** Alterar la frecuencia fundamental o la estructura de pulsos del canto de advertencia genera patrones acusticamente imposibles que confunden al clasificador.
- **Deformaciones Geométricas Extremas:** Estiramientos no proporcionales que alteren la morfometría corporal del anuro (ej. relación longitud hocico-cloaca).

#### **Política para No Sesgar el Dataset**

- **Balanceo por Undersampling/Oversampling:** Las especies hiper-representadas en bases pàºblicas se limitan en cantidad; las especies raras o endémicas reciben oversampling mediante la tubería de augmentación sintética controlada.
- **Normalización de Fondo:** Incluir conscientemente imágenes con fondos neutros o variados para evitar que la red asocie una especie a un tipo específico de hoja o color de fondo (*shortcut learning*).

---

### **División del Dataset y Evitación de Fuga de Información**

#### **Estrategia de Split**

- **Estrategia Principal:** **Split por Localidad / Geográfico (GroupKFold / GroupSplit)**.
- **Justificación:** Garantiza que imágenes o cantos registrados en la misma localidad o en el mismo evento de campo no queden repartidos entre entrenamiento y prueba.

#### **Estructura del Dataset**

| **Etapa** | **Imágenes Originales** | **Con Augmentación** | **Notas Metodológicas** |
| --- | --- | --- | --- |
| **Train** | 550 | 5,100 \ 6,000 | Augmentación aplicada **exclusivamente** a Train. Oversampling en clases raras/críticas. |
| **Validación** | 120 | N/A | Sin augmentación. Evaluación limpia para selección de hiperparámetros y *early stopping*. |
| **Test** | 120 | N/A | Datos nunca vistos durante el entrenamiento. Evaluación final y referencia para optimización móvil (Edge). |

#### **Reglas para Evitar Fuga de Información (*Data Leakage*)**

1. **Aislamiento Temporal de Augmentación:** Las transformaciones sintéticas se aplican **al vuelo (*on-the-fly*)** durante el bucle de entrenamiento, jamás antes de realizar el corte *Train/Val/Test*.
2. **Agrupamiento por Individuo/Sesión:** Todas las tomas, ángulos o audios derivados de un mismo espécimen o sitio exacto de muestreo pertenecen **100% al mismo grupo** (*Train*, *Val* o *Test*).
3. **No Contaminación de Normalización:** Las estadísticas de normalización (media y desviación estándar de RGB) se calculan àºnicamente sobre el conjunto de *Train* y se aplican a *Val* y *Test*.

---

### **Conjunto Open-Set (Manejo de Especies Desconocidas)**

- **Implementación:** **Sí**.
- **Propósito:** Crucial para el despliegue móvil offline. Si un usuario fotografía un organismo o anuro de una especie no presente en el modelo, la app debe clasificarlo como *"Desconocido / Especie No Registrada"* en lugar de forzar una falsa predicción de alta confianza.
- **Construcción del Conjunto Open-Set:**
    - **Inclusión de "Out-of-Distribution" (OOD):** Se compone de un subconjunto de imágenes de otras familias de anuros no incluidas en el modelo, otros anfíbios (ej. salamandras, cecilias), e insectos/objetos de hojarasca comunes en el hábitat.
    - **Técnica de Inferencia Offline:** Implementación de umbrales de incertidumbre por calibración de probabilidad (**Temperature Scaling**) y capa de detección **Out-of-Distribution** basada en la distancia del vector de características (*embeddings*) extraído por el modelo frente a los centroides de las clases conocidas.

#### Propuesta: tabla de seguimiento del conjunto Open-Set (reemplaza la base de datos vacía de Notion)

La metodología completa está en [[Open-Set Recognition]]; lo que faltaba era la estructura operativa para llevar la cuenta del conjunto recolectado:

| Campo | Contenido |
| --- | --- |
| ID de muestra | UUID |
| Tipo | Near-OOD (anuro fuera del catálogo) / Far-OOD (otro anfibio, insecto, hojarasca, objeto) |
| Descripción | Qué es exactamente |
| Fuente | Campo propio / iNaturalist / GBIF |
| Uso | Validación (fijar umbral) / Test (reportar AUROC, nunca el mismo conjunto que validación) |

Separar near-OOD de far-OOD en la tabla desde el inicio evita el error más comàºn de la sección 4 de [[Open-Set Recognition]]: reportar solo el promedio y esconder que detectar una hoja es fácil pero detectar un *Pristimantis* fuera de catálogo es lo difícil.



