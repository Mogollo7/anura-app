---
title: "Objetivos y Alcance"
proyecto: Anura
fuente: "Notion â€” Proyecto Identificación de Anuros Colombia"
tags: [anura, proyecto, requisitos]
---

# Objetivos y Alcance

## Objetivos

### Objetivo general

Desarrollar e implementar una **aplicación móvil con capacidad de funcionamiento offline**, basada en **BioCLIP, visión computacional, segmentación semántica y una base de datos vectorial**, para apoyar la identificación y el monitoreo de anfibios del orden Anura presentes en Colombia, incorporando un sistema de inteligencia artificial abierto con evaluación guiada paso a paso y detección de especies no registradas, y alcanzar una **Top-3 Accuracy mínima del 85 %** sobre un conjunto de prueba independiente y controlado.

### Objetivos específicos

- **Implementar y adaptar BioCLIP** mediante técnicas de transferencia de conocimiento para realizar la identificación de especies de anuros, aprovechando sus representaciones visuales y semánticas para el reconocimiento de especímenes.
- **Implementar un modelo de segmentación semántica basado en YOLO** para identificar y delimitar el organismo dentro de las imágenes, separándolo de su entorno y facilitando el análisis de características morfológicas relevantes para la identificación.
- **Integrar BioCLIP con una base de datos vectorial** para almacenar representaciones de los especímenes y realizar bàºsquedas por similitud, permitiendo incorporar nuevos registros y especies sin requerir necesariamente un reentrenamiento completo del modelo.
- **Implementar un mecanismo de Open-Set Recognition** que permita detectar posibles especies no registradas o desconocidas para el sistema, reduciendo la probabilidad de clasificarlas incorrectamente como especies conocidas.
- **Desarrollar un sistema de inteligencia artificial abierto basado en un proceso de evaluación paso a paso**, que integre los resultados de BioCLIP, la segmentación semántica y la información ecológica disponible para analizar progresivamente las características del espécimen, presentar los criterios utilizados y orientar al usuario hacia la identificación más probable.
- **Integrar información ecológica, ambiental y geográfica** relacionada con los registros de presencia de anuros, con el propósito de complementar el proceso de identificación y proporcionar contexto sobre la posible distribución de las especies.
- **Optimizar los componentes de inteligencia artificial para su ejecución en dispositivos móviles**, aplicando técnicas de reducción de tamaño y consumo computacional cuando sea necesario, con el propósito de permitir el funcionamiento de las principales capacidades de reconocimiento sin conexión permanente a Internet.
- **Desarrollar y validar una aplicación móvil funcional con capacidad offline**, integrando BioCLIP, segmentación semántica, bàºsqueda vectorial, detección de especies desconocidas, información ecológica y el sistema de evaluación guiada, mediante pruebas en condiciones controladas y de campo.

---

[[Historias de Usuario]]

## **Requerimientos Funcionales (RF)**

### **1. Entrada y Procesamiento Multimodal**

- **RF-01: Captura e Ingesta Multimodal (Imágenes y Audio)**
    - **RF-01.1:** El sistema debe permitir la carga/captura de fotografías en formatos estándar (JPEG, PNG).
    - **RF-01.2:** El sistema debe permitir la carga/grabación de archivos de audio (WAV, MP3) con vocalizaciones de anuros.
- **RF-02: Análisis de Màºltiples Fotografías de un Mismo Individuo**
    - El sistema debe permitir asociar màºltiples tomas de un mismo espécimen (ej. vista dorsal, ventral, lateral) a una sola observación para consolidar la inferencia.
- **RF-03: Detección y Análisis Multi-Individuo en una Imagen**
    - El sistema debe detectar, delimitar (bounding boxes) y evaluar màºltiples especímenes presentes en una sola fotografía, permitiendo la identificación taxonómica independiente para cada individuo.
- **RF-04: Entrada de Variables Contextuales (Metadatos)**
    - El sistema debe registrar o capturar metadatos geográficos y ambientales: coordenadas GPS, altitud (msnm), tipo de ecosistema, época del año/mes y hora de observación.

### **2. Inferencia, Segmentación y Clasificación Taxonómica**

- **RF-05: Clasificación Taxonómica y Predicción Top-3**
    - El sistema debe clasificar el espécimen entregando su jerarquía completa (Familia, Género, Especie) y listar las 3 especies más probables junto con sus respectivos porcentajes de confianza/probabilidad.
- **RF-06: Segmentación Semántica y Análisis Anatómico Paso a Paso**
    - El sistema debe segmentar las regiones anatómicas clave del anuro (ej. iris/ojo, piel dorsal, muslos/patrones, extremidades/ventosas).
    - Debe entregar un desglose explicativo paso a paso con el porcentaje de similitud morfológica detectado en cada región anatómica respecto a los patrones de referencia de la especie.
- **RF-07: Análisis Bioacàºstico mediante Espectrogramas**
    - El sistema debe convertir el audio ingresado en espectrogramas para extraer características (frecuencia dominante/fundamental, ritmos continuos o pulsados) y clasificar el tipo de canto (reproductivo o territorial).
- **RF-08: Inferencia Funsionada/Ensemble (Visión + Audio + Metadatos)**
    - El sistema debe integrar las probabilidades obtenidas de la imagen, el espectrograma y la distribución geográfica conocida para recalcular y ajustar el ranking Top-3 final.

### **3. Despliegue y Funcionalidades por Fase**

#### **Fase 1: Plataforma Web y Módulo Científico Comunitario (tipo iNaturalist)**

- **RF-09: Repositorio y Registro de Observaciones**
    - El sistema debe permitir a los usuarios crear, almacenar, editar y publicar observaciones de anuros con sus fotos, audios, metadatos y resultados de clasificación.
- **RF-10: Visualización de Fichas Técnicas Completes**
    - El sistema debe desplegar la ficha técnica estructurada de la especie (Taxonomía, Morfología, Bioacàºstica, Distribución/Hábitat, Ecología/Comportamiento, Estado de Conservación UICN y Notas científicas).
- **RF-11: Exploración y Mapa de Registros Comunitarios**
    - El sistema debe proveer una interfaz gráfica (estilo iNaturalist) con mapas interactivos y filtros para explorar las observaciones de la comunidad por especie, ubicación y fecha.

#### **Fase 2: Aplicación Móvil Android (Funcionamiento Offline)**

- **RF-12: Modo Offline para Ejecución en Campo**
    - La aplicación móvil debe almacenar e inferir modelos optimizados (**LiteRT** â€” antes TensorFlow Lite, renombrado en 2024, ver [[Optimización para Inferencia en Móvil]] §1 / ONNX) directamente en el dispositivo, permitiendo clasificar imágenes y audios sin necesidad de conexión a Internet.
- **RF-13: Sincronización Diferida de Datos**
    - La app debe guardar las observaciones tomadas en campo de forma local y sincronizarlas automáticamente con el repositorio web cuando el dispositivo detecte conectividad a Internet.
- **RF-14: Captura Bioacàºstica en Dispositivo Móvil**
    - La app móvil debe incluir un módulo integrado para la grabación de audio en tiempo real con preprocesamiento de reducción de ruido ambiental.

---

## **Requerimientos No Funcionales (RNF)**

### **1. Rendimiento y Tiempo de Respuesta**

- **RNF-01: Tiempo de Inferencia en Plataforma Web (Fase 1)**
    - El procesamiento de imágenes y la inferencia del modelo (incluyendo segmentación semántica y ranking Top-3) en el backend web no debe superar los **3 segundos** por petición en condiciones normales de red.
- **RNF-02: Tiempo de Inferencia Offline en Dispositivos Móviles (Fase 2)**
    - La inferencia local en la aplicación Android (ejecutando modelos optimizados como **LiteRT**/ONNX) no debe tomar más de **4 segundos** para la clasificación visual y de audio combinada.
- **RNF-03: Latencia de Carga de Fichas Técnicas**
    - La recuperación y despliegue de las fichas técnicas de especies desde la base de datos debe realizarse en menos de **1 segundo**.

### **2. Precisión, Eficiencia y Modelos Offline**

- **RNF-04: Métrica de Calidad Top-3 (Top-3 Accuracy)**
    - El modelo de visión artificial debe alcanzar una precisión acumulada (Top-3) mínima del **85%** en el conjunto de prueba para las **28 especies** del catálogo del prototipo (cifra fijada el 2026-09-05, ver [[Inconsistencias y Decisiones Pendientes]] C-3). Las "50 especies" quedan como meta de largo plazo (Etapa III de [[Escalabilidad]] §4), no como el conjunto evaluado en el prototipo del 27 de septiembre.
- **RNF-05: Optimización y Tamaño de los Modelos Enbebidos**
    - El tamaño total de los modelos quantizados (visión + audio + metadatos) almacenados localmente en la app móvil no debe exceder los **150 MB**, garantizando compatibilidad con dispositivos de gama media/baja.
- **RNF-06: Tolerancia a la Fragmentación de Datos**
    - El algoritmo de fusión/ensemble debe ser capaz de emitir una predicción válida incluso si faltan datos secundarios (por ejemplo, si la observación no incluye audio o si las coordenadas GPS están deshabilitadas).

### **3. Usabilidad en Campo e Interfaz de Usuario**

- **RNF-07: Interfaz para Entornos de Alta Luminosidad y Trabajo Nocturno**
    - La interfaz de la aplicación móvil debe incluir un diseño de alto contraste y soporte de **Modo Oscuro (Dark Mode)** para facilitar la lectura durante salidas de campo nocturnas o bajo luz solar directa.
- **RNF-08: Operabilidad a Una Sola Mano**
    - Los componentes clave de la UI móvil (botón de captura, inicio de grabación de audio y guardar observación) deben estar ubicados estratégicamente para permitir el uso rápido del dispositivo con una sola mano en terreno.
- **RNF-09: Eficiencia Energética**
    - La ejecución de la inferencia local y la adquisición de datos de sensores (GPS/micrófono) no debe degradar la batería del dispositivo móvil en más de un **5% por cada hora** de uso continuo en campo.

### **4. Disponibilidad, Almacenamiento y Sincronización**

- **RNF-10: Operatividad Offline Absoluta (Fase 2)**
    - El 100% de las funcionalidades de captura, procesamiento local, consulta de fichas técnicas descargadas y guardado de observaciones debe funcionar sin ningàºn tipo de conectividad a redes móviles o Wi-Fi.
- **RNF-11: Persistencia Local y Tolerancia a Fallos**
    - En caso de cierre imprevisto de la aplicación o agotamiento de la batería, los datos recopilados en campo que aàºn no se hayan sincronizado deben permanecer almacenados de forma segura en la base de datos local del dispositivo (ej. Room / SQLite).

### **5. Seguridad, Privacidad y Gestión de Datos**

- **RNF-12: Encriptación de Datos Sensibles**
    - Toda la comunicación entre los clientes (Web/App) y la API del servidor debe realizarse mediante protocolos cifrados HTTPS/TLS 1.3.
- **RNF-13: Protección de Coordenadas de Especies Amenazadas**
    - Las observaciones de especies categorizadas por la UICN como Amenazadas (Vulnerable, En Peligro, En Peligro Crítico) deben implementar una **ofuscación geográfica/espacial** (Buffer de 1 a 5 km) en las vistas pàºblicas del mapa estilo *iNaturalist* para prevenir la caza furtiva o la alteración del hábitat.
- **RNF-14: Gestión de Sesiones y Permisos**
    - La aplicación móvil debe solicitar estrictamente solo los permisos necesarios (*Cámara, Micrófono, Ubicación en tiempo de ejecución*) en el momento exacto en que la funcionalidad sea requerida por el usuario.

---

## **Alcance y Delimitaciones**

### **1. Alcance**

#### **Modalidades soportadas y capacidades de entrada**

- **Imágenes (Visión Artificial):**
    - **Análisis multinivel de especímenes:** Evaluación de imágenes que contengan **màºltiples individuos** en una misma toma, así como combinación de **màºltiples fotografías de un mismo individuo** (ej. vista dorsal, ventral, lateral) para refinar la extracción de características morfológicas y aumentar la precisión de la inferencia.
    - **Segmentación Semántica Desglosada:** Identificación y análisis anatómico paso a paso por partes del espécimen (ej. patrón del iris, piel dorsal, extremidades, muslos, presencia de ventosas).
- **Audio / Bioacàºstica:**
    - Análisis de vocalizaciones (cantos reproductivos, territoriales) a partir de espectrogramas (frecuencia, intensidad, ritmo continuo/pulsado) utilizando redes neuronales convolucionales para complementar la identificación taxonómica en condiciones de baja visibilidad o soporte multimodal.
- **Variables Contextuales / Metadatos:**
    - Uso de variables ambientales y de ubicación (coordenadas GPS, rango altitudinal msnm, ecosistema/hábitat, época del año/lluvias y hora de actividad) para validar la probabilidad de presencia geográfica de la especie.

#### **Nivel de salida y estructura de resultados del sistema**

Para cada análisis ejecutado, el sistema entregará:

1. **Clasificación Taxonómica:** Jerarquía completa (*Familia*, *Género*, *Especie*).
2. **Predicción Probabilística (Top 3):** Las 3 especies más probables con su respectivo porcentaje de similitud o confianza.
3. **Desglose Anatómico (Segmentación Semántica):** Explicación detallada parte por parte de la rana, indicando los porcentajes de similitud morfológica detectados en cada estructura anatómica respecto al patrón de referencia.
4. **Ficha Técnica Completa de la Especie (ej. *Craugastor raniformis*):**
    - **Nombres y Taxonomía:** Nombre científico, nombre comàºn y jerarquía taxonómica completa.
    - **Morfología Detallada:** Tamaño/dimorfismo sexual, coloración dorsal/ventral, patrones en muslos/extremidades, características del iris/ojos y textura de la piel.
    - **Bioacàºstica:** Tipo de canto (reproductivo/territorial), frecuencia/ritmo y temporalidad de actividad vocal.
    - **Distribución y Hábitat:** Rango altitudinal (msnm), ecosistemas (ej. bosque hàºmedo, bosque seco), microhábitat (hojarasca, riachuelos, vegetación nocturna) y condiciones de temperatura/humedad.
    - **Ecología y Comportamiento:** Patrones de actividad (nocturna/diurna), modo reproductivo (ej. desarrollo directo), dieta/depredadores y rol como bioindicador.
    - **Estado de Conservación:** Categoría UICN (ej. Preocupación Menor - LC), tendencia poblacional, amenazas y observaciones/notas científicas.

#### **Estrategia de Despliegue y Plataformas**

- **Fase 1 (Plataforma Web / Repositorio Científico):**
    - Despliegue inicial en entorno **Web** enfocado en la validación de modelos.
    - Permite procesar imágenes, entregar la predicción Top 3 y desplegar las fichas técnicas.
    - Incluye un módulo estilo repositorio/comunidad (similar al enfoque de *iNaturalist*) para montar, visualizar, almacenar y compartir observaciones registradas.
- **Fase 2 (Aplicación Móvil - Android Offline):**
    - Desarrollo de aplicación nativa/optimizada para **Android**.
    - Integración de capacidades **Offline** (modelos embebidos e inferencia en dispositivo) para garantizar funcionamiento continuo en zonas sin cobertura de red.
    - Integración completa del módulo de captura y procesamiento de audio/bioacàºstica en campo.

#### **Contexto de uso**

- Salidas de campo y prácticas universitarias de biología/herpetología.
- Estudios de Impacto Ambiental (EIA) y caracterización de fauna.
- Proyectos de monitoreo y conservación participativa en zonas rurales.
- Actividades pedagógicas e investigación formativa en colegios y universidades.

### **2. Delimitaciones (Lo que NO incluye)**

- **Renacuajos y fases larvales:**
    - El sistema se limita exclusivamente a especímenes adultos debido a las marcadas diferencias morfológicas y ontogenéticas en etapas larvales.
- **Análisis moleculares o genéticos:**
    - No se realizan pruebas de laboratorio ni secuenciación de ADN. La identificación es 100% no invasiva (visual, bioacàºstica y espacial).
- **Diagnóstico de salud o fitosanitario:**
    - El sistema no evalàºa el estado de salud del espécimen ni detecta afecciones patógenas (como la presencia del hongo *Batrachochytrium dendrobatidis* / quitridiomicosis).
- **Cobertura total de la anurofauna nacional:**
    - Colombia cuenta con más de **911 especies de ranas y sapos** registradas. El alcance inicial del sistema seleccionará un conjunto priorizado de especies (acotado por disponibilidad de datos morfológicos, acàºsticos y relevancia ecológica), sin abarcar la totalidad de la diversidad del país en la primera versión.
- **Garantía de precisión bajo condiciones extremas:**
    - No se garantiza un 100% de precisión ante tomas con oclusión severa del espécimen, desenfoque extremo, iluminación nula o audios con alta contaminación por ruido ambiental sin filtrar.



