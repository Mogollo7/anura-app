---
title: "Objetivos y Alcance"
proyecto: Anura
fuente: "Notion â€” Proyecto IdentificaciÃ³n de Anuros Colombia"
tags: [anura, proyecto, requisitos]
---

# Objetivos y Alcance

## Objetivos

### Objetivo general

Desarrollar e implementar una **aplicaciÃ³n mÃ³vil con capacidad de funcionamiento offline**, basada en **BioCLIP, visiÃ³n computacional, segmentaciÃ³n semÃ¡ntica y una base de datos vectorial**, para apoyar la identificaciÃ³n y el monitoreo de anfibios del orden Anura presentes en Colombia, incorporando un sistema de inteligencia artificial abierto con evaluaciÃ³n guiada paso a paso y detecciÃ³n de especies no registradas, y alcanzar una **Top-3 Accuracy mÃ­nima del 85 %** sobre un conjunto de prueba independiente y controlado.

### Objetivos especÃ­ficos

- **Implementar y adaptar BioCLIP** mediante tÃ©cnicas de transferencia de conocimiento para realizar la identificaciÃ³n de especies de anuros, aprovechando sus representaciones visuales y semÃ¡nticas para el reconocimiento de especÃ­menes.
- **Implementar un modelo de segmentaciÃ³n semÃ¡ntica basado en YOLO** para identificar y delimitar el organismo dentro de las imÃ¡genes, separÃ¡ndolo de su entorno y facilitando el anÃ¡lisis de caracterÃ­sticas morfolÃ³gicas relevantes para la identificaciÃ³n.
- **Integrar BioCLIP con una base de datos vectorial** para almacenar representaciones de los especÃ­menes y realizar bÃºsquedas por similitud, permitiendo incorporar nuevos registros y especies sin requerir necesariamente un reentrenamiento completo del modelo.
- **Implementar un mecanismo de Open-Set Recognition** que permita detectar posibles especies no registradas o desconocidas para el sistema, reduciendo la probabilidad de clasificarlas incorrectamente como especies conocidas.
- **Desarrollar un sistema de inteligencia artificial abierto basado en un proceso de evaluaciÃ³n paso a paso**, que integre los resultados de BioCLIP, la segmentaciÃ³n semÃ¡ntica y la informaciÃ³n ecolÃ³gica disponible para analizar progresivamente las caracterÃ­sticas del espÃ©cimen, presentar los criterios utilizados y orientar al usuario hacia la identificaciÃ³n mÃ¡s probable.
- **Integrar informaciÃ³n ecolÃ³gica, ambiental y geogrÃ¡fica** relacionada con los registros de presencia de anuros, con el propÃ³sito de complementar el proceso de identificaciÃ³n y proporcionar contexto sobre la posible distribuciÃ³n de las especies.
- **Optimizar los componentes de inteligencia artificial para su ejecuciÃ³n en dispositivos mÃ³viles**, aplicando tÃ©cnicas de reducciÃ³n de tamaÃ±o y consumo computacional cuando sea necesario, con el propÃ³sito de permitir el funcionamiento de las principales capacidades de reconocimiento sin conexiÃ³n permanente a Internet.
- **Desarrollar y validar una aplicaciÃ³n mÃ³vil funcional con capacidad offline**, integrando BioCLIP, segmentaciÃ³n semÃ¡ntica, bÃºsqueda vectorial, detecciÃ³n de especies desconocidas, informaciÃ³n ecolÃ³gica y el sistema de evaluaciÃ³n guiada, mediante pruebas en condiciones controladas y de campo.

---

[[Historias de Usuario]]

## **Requerimientos Funcionales (RF)**

### **1. Entrada y Procesamiento Multimodal**

- **RF-01: Captura e Ingesta Multimodal (ImÃ¡genes y Audio)**
    - **RF-01.1:** El sistema debe permitir la carga/captura de fotografÃ­as en formatos estÃ¡ndar (JPEG, PNG).
    - **RF-01.2:** El sistema debe permitir la carga/grabaciÃ³n de archivos de audio (WAV, MP3) con vocalizaciones de anuros.
- **RF-02: AnÃ¡lisis de MÃºltiples FotografÃ­as de un Mismo Individuo**
    - El sistema debe permitir asociar mÃºltiples tomas de un mismo espÃ©cimen (ej. vista dorsal, ventral, lateral) a una sola observaciÃ³n para consolidar la inferencia.
- **RF-03: DetecciÃ³n y AnÃ¡lisis Multi-Individuo en una Imagen**
    - El sistema debe detectar, delimitar (bounding boxes) y evaluar mÃºltiples especÃ­menes presentes en una sola fotografÃ­a, permitiendo la identificaciÃ³n taxonÃ³mica independiente para cada individuo.
- **RF-04: Entrada de Variables Contextuales (Metadatos)**
    - El sistema debe registrar o capturar metadatos geogrÃ¡ficos y ambientales: coordenadas GPS, altitud (msnm), tipo de ecosistema, Ã©poca del aÃ±o/mes y hora de observaciÃ³n.

### **2. Inferencia, SegmentaciÃ³n y ClasificaciÃ³n TaxonÃ³mica**

- **RF-05: ClasificaciÃ³n TaxonÃ³mica y PredicciÃ³n Top-3**
    - El sistema debe clasificar el espÃ©cimen entregando su jerarquÃ­a completa (Familia, GÃ©nero, Especie) y listar las 3 especies mÃ¡s probables junto con sus respectivos porcentajes de confianza/probabilidad.
- **RF-06: SegmentaciÃ³n SemÃ¡ntica y AnÃ¡lisis AnatÃ³mico Paso a Paso**
    - El sistema debe segmentar las regiones anatÃ³micas clave del anuro (ej. iris/ojo, piel dorsal, muslos/patrones, extremidades/ventosas).
    - Debe entregar un desglose explicativo paso a paso con el porcentaje de similitud morfolÃ³gica detectado en cada regiÃ³n anatÃ³mica respecto a los patrones de referencia de la especie.
- **RF-07: AnÃ¡lisis BioacÃºstico mediante Espectrogramas**
    - El sistema debe convertir el audio ingresado en espectrogramas para extraer caracterÃ­sticas (frecuencia dominante/fundamental, ritmos continuos o pulsados) y clasificar el tipo de canto (reproductivo o territorial).
- **RF-08: Inferencia Funsionada/Ensemble (VisiÃ³n + Audio + Metadatos)**
    - El sistema debe integrar las probabilidades obtenidas de la imagen, el espectrograma y la distribuciÃ³n geogrÃ¡fica conocida para recalcular y ajustar el ranking Top-3 final.

### **3. Despliegue y Funcionalidades por Fase**

#### **Fase 1: Plataforma Web y MÃ³dulo CientÃ­fico Comunitario (tipo iNaturalist)**

- **RF-09: Repositorio y Registro de Observaciones**
    - El sistema debe permitir a los usuarios crear, almacenar, editar y publicar observaciones de anuros con sus fotos, audios, metadatos y resultados de clasificaciÃ³n.
- **RF-10: VisualizaciÃ³n de Fichas TÃ©cnicas Completes**
    - El sistema debe desplegar la ficha tÃ©cnica estructurada de la especie (TaxonomÃ­a, MorfologÃ­a, BioacÃºstica, DistribuciÃ³n/HÃ¡bitat, EcologÃ­a/Comportamiento, Estado de ConservaciÃ³n UICN y Notas cientÃ­ficas).
- **RF-11: ExploraciÃ³n y Mapa de Registros Comunitarios**
    - El sistema debe proveer una interfaz grÃ¡fica (estilo iNaturalist) con mapas interactivos y filtros para explorar las observaciones de la comunidad por especie, ubicaciÃ³n y fecha.

#### **Fase 2: AplicaciÃ³n MÃ³vil Android (Funcionamiento Offline)**

- **RF-12: Modo Offline para EjecuciÃ³n en Campo**
    - La aplicaciÃ³n mÃ³vil debe almacenar e inferir modelos optimizados (**LiteRT** â€” antes TensorFlow Lite, renombrado en 2024, ver [[OptimizaciÃ³n para Inferencia en MÃ³vil]] Â§1 / ONNX) directamente en el dispositivo, permitiendo clasificar imÃ¡genes y audios sin necesidad de conexiÃ³n a Internet.
- **RF-13: SincronizaciÃ³n Diferida de Datos**
    - La app debe guardar las observaciones tomadas en campo de forma local y sincronizarlas automÃ¡ticamente con el repositorio web cuando el dispositivo detecte conectividad a Internet.
- **RF-14: Captura BioacÃºstica en Dispositivo MÃ³vil**
    - La app mÃ³vil debe incluir un mÃ³dulo integrado para la grabaciÃ³n de audio en tiempo real con preprocesamiento de reducciÃ³n de ruido ambiental.

---

## **Requerimientos No Funcionales (RNF)**

### **1. Rendimiento y Tiempo de Respuesta**

- **RNF-01: Tiempo de Inferencia en Plataforma Web (Fase 1)**
    - El procesamiento de imÃ¡genes y la inferencia del modelo (incluyendo segmentaciÃ³n semÃ¡ntica y ranking Top-3) en el backend web no debe superar los **3 segundos** por peticiÃ³n en condiciones normales de red.
- **RNF-02: Tiempo de Inferencia Offline en Dispositivos MÃ³viles (Fase 2)**
    - La inferencia local en la aplicaciÃ³n Android (ejecutando modelos optimizados como **LiteRT**/ONNX) no debe tomar mÃ¡s de **4 segundos** para la clasificaciÃ³n visual y de audio combinada.
- **RNF-03: Latencia de Carga de Fichas TÃ©cnicas**
    - La recuperaciÃ³n y despliegue de las fichas tÃ©cnicas de especies desde la base de datos debe realizarse en menos de **1 segundo**.

### **2. PrecisiÃ³n, Eficiencia y Modelos Offline**

- **RNF-04: MÃ©trica de Calidad Top-3 (Top-3 Accuracy)**
    - El modelo de visiÃ³n artificial debe alcanzar una precisiÃ³n acumulada (Top-3) mÃ­nima del **85%** en el conjunto de prueba para las **28 especies** del catÃ¡logo del prototipo (cifra fijada el 2026-09-05, ver [[Inconsistencias y Decisiones Pendientes]] C-3). Las "50 especies" quedan como meta de largo plazo (Etapa III de [[Escalabilidad]] Â§4), no como el conjunto evaluado en el prototipo del 27 de septiembre.
- **RNF-05: OptimizaciÃ³n y TamaÃ±o de los Modelos Enbebidos**
    - El tamaÃ±o total de los modelos quantizados (visiÃ³n + audio + metadatos) almacenados localmente en la app mÃ³vil no debe exceder los **150 MB**, garantizando compatibilidad con dispositivos de gama media/baja.
- **RNF-06: Tolerancia a la FragmentaciÃ³n de Datos**
    - El algoritmo de fusiÃ³n/ensemble debe ser capaz de emitir una predicciÃ³n vÃ¡lida incluso si faltan datos secundarios (por ejemplo, si la observaciÃ³n no incluye audio o si las coordenadas GPS estÃ¡n deshabilitadas).

### **3. Usabilidad en Campo e Interfaz de Usuario**

- **RNF-07: Interfaz para Entornos de Alta Luminosidad y Trabajo Nocturno**
    - La interfaz de la aplicaciÃ³n mÃ³vil debe incluir un diseÃ±o de alto contraste y soporte de **Modo Oscuro (Dark Mode)** para facilitar la lectura durante salidas de campo nocturnas o bajo luz solar directa.
- **RNF-08: Operabilidad a Una Sola Mano**
    - Los componentes clave de la UI mÃ³vil (botÃ³n de captura, inicio de grabaciÃ³n de audio y guardar observaciÃ³n) deben estar ubicados estratÃ©gicamente para permitir el uso rÃ¡pido del dispositivo con una sola mano en terreno.
- **RNF-09: Eficiencia EnergÃ©tica**
    - La ejecuciÃ³n de la inferencia local y la adquisiciÃ³n de datos de sensores (GPS/micrÃ³fono) no debe degradar la baterÃ­a del dispositivo mÃ³vil en mÃ¡s de un **5% por cada hora** de uso continuo en campo.

### **4. Disponibilidad, Almacenamiento y SincronizaciÃ³n**

- **RNF-10: Operatividad Offline Absoluta (Fase 2)**
    - El 100% de las funcionalidades de captura, procesamiento local, consulta de fichas tÃ©cnicas descargadas y guardado de observaciones debe funcionar sin ningÃºn tipo de conectividad a redes mÃ³viles o Wi-Fi.
- **RNF-11: Persistencia Local y Tolerancia a Fallos**
    - En caso de cierre imprevisto de la aplicaciÃ³n o agotamiento de la baterÃ­a, los datos recopilados en campo que aÃºn no se hayan sincronizado deben permanecer almacenados de forma segura en la base de datos local del dispositivo (ej. Room / SQLite).

### **5. Seguridad, Privacidad y GestiÃ³n de Datos**

- **RNF-12: EncriptaciÃ³n de Datos Sensibles**
    - Toda la comunicaciÃ³n entre los clientes (Web/App) y la API del servidor debe realizarse mediante protocolos cifrados HTTPS/TLS 1.3.
- **RNF-13: ProtecciÃ³n de Coordenadas de Especies Amenazadas**
    - Las observaciones de especies categorizadas por la UICN como Amenazadas (Vulnerable, En Peligro, En Peligro CrÃ­tico) deben implementar una **ofuscaciÃ³n geogrÃ¡fica/espacial** (Buffer de 1 a 5 km) en las vistas pÃºblicas del mapa estilo *iNaturalist* para prevenir la caza furtiva o la alteraciÃ³n del hÃ¡bitat.
- **RNF-14: GestiÃ³n de Sesiones y Permisos**
    - La aplicaciÃ³n mÃ³vil debe solicitar estrictamente solo los permisos necesarios (*CÃ¡mara, MicrÃ³fono, UbicaciÃ³n en tiempo de ejecuciÃ³n*) en el momento exacto en que la funcionalidad sea requerida por el usuario.

---

## **Alcance y Delimitaciones**

### **1. Alcance**

#### **Modalidades soportadas y capacidades de entrada**

- **ImÃ¡genes (VisiÃ³n Artificial):**
    - **AnÃ¡lisis multinivel de especÃ­menes:** EvaluaciÃ³n de imÃ¡genes que contengan **mÃºltiples individuos** en una misma toma, asÃ­ como combinaciÃ³n de **mÃºltiples fotografÃ­as de un mismo individuo** (ej. vista dorsal, ventral, lateral) para refinar la extracciÃ³n de caracterÃ­sticas morfolÃ³gicas y aumentar la precisiÃ³n de la inferencia.
    - **SegmentaciÃ³n SemÃ¡ntica Desglosada:** IdentificaciÃ³n y anÃ¡lisis anatÃ³mico paso a paso por partes del espÃ©cimen (ej. patrÃ³n del iris, piel dorsal, extremidades, muslos, presencia de ventosas).
- **Audio / BioacÃºstica:**
    - AnÃ¡lisis de vocalizaciones (cantos reproductivos, territoriales) a partir de espectrogramas (frecuencia, intensidad, ritmo continuo/pulsado) utilizando redes neuronales convolucionales para complementar la identificaciÃ³n taxonÃ³mica en condiciones de baja visibilidad o soporte multimodal.
- **Variables Contextuales / Metadatos:**
    - Uso de variables ambientales y de ubicaciÃ³n (coordenadas GPS, rango altitudinal msnm, ecosistema/hÃ¡bitat, Ã©poca del aÃ±o/lluvias y hora de actividad) para validar la probabilidad de presencia geogrÃ¡fica de la especie.

#### **Nivel de salida y estructura de resultados del sistema**

Para cada anÃ¡lisis ejecutado, el sistema entregarÃ¡:

1. **ClasificaciÃ³n TaxonÃ³mica:** JerarquÃ­a completa (*Familia*, *GÃ©nero*, *Especie*).
2. **PredicciÃ³n ProbabilÃ­stica (Top 3):** Las 3 especies mÃ¡s probables con su respectivo porcentaje de similitud o confianza.
3. **Desglose AnatÃ³mico (SegmentaciÃ³n SemÃ¡ntica):** ExplicaciÃ³n detallada parte por parte de la rana, indicando los porcentajes de similitud morfolÃ³gica detectados en cada estructura anatÃ³mica respecto al patrÃ³n de referencia.
4. **Ficha TÃ©cnica Completa de la Especie (ej. *Craugastor raniformis*):**
    - **Nombres y TaxonomÃ­a:** Nombre cientÃ­fico, nombre comÃºn y jerarquÃ­a taxonÃ³mica completa.
    - **MorfologÃ­a Detallada:** TamaÃ±o/dimorfismo sexual, coloraciÃ³n dorsal/ventral, patrones en muslos/extremidades, caracterÃ­sticas del iris/ojos y textura de la piel.
    - **BioacÃºstica:** Tipo de canto (reproductivo/territorial), frecuencia/ritmo y temporalidad de actividad vocal.
    - **DistribuciÃ³n y HÃ¡bitat:** Rango altitudinal (msnm), ecosistemas (ej. bosque hÃºmedo, bosque seco), microhÃ¡bitat (hojarasca, riachuelos, vegetaciÃ³n nocturna) y condiciones de temperatura/humedad.
    - **EcologÃ­a y Comportamiento:** Patrones de actividad (nocturna/diurna), modo reproductivo (ej. desarrollo directo), dieta/depredadores y rol como bioindicador.
    - **Estado de ConservaciÃ³n:** CategorÃ­a UICN (ej. PreocupaciÃ³n Menor - LC), tendencia poblacional, amenazas y observaciones/notas cientÃ­ficas.

#### **Estrategia de Despliegue y Plataformas**

- **Fase 1 (Plataforma Web / Repositorio CientÃ­fico):**
    - Despliegue inicial en entorno **Web** enfocado en la validaciÃ³n de modelos.
    - Permite procesar imÃ¡genes, entregar la predicciÃ³n Top 3 y desplegar las fichas tÃ©cnicas.
    - Incluye un mÃ³dulo estilo repositorio/comunidad (similar al enfoque de *iNaturalist*) para montar, visualizar, almacenar y compartir observaciones registradas.
- **Fase 2 (AplicaciÃ³n MÃ³vil - Android Offline):**
    - Desarrollo de aplicaciÃ³n nativa/optimizada para **Android**.
    - IntegraciÃ³n de capacidades **Offline** (modelos embebidos e inferencia en dispositivo) para garantizar funcionamiento continuo en zonas sin cobertura de red.
    - IntegraciÃ³n completa del mÃ³dulo de captura y procesamiento de audio/bioacÃºstica en campo.

#### **Contexto de uso**

- Salidas de campo y prÃ¡cticas universitarias de biologÃ­a/herpetologÃ­a.
- Estudios de Impacto Ambiental (EIA) y caracterizaciÃ³n de fauna.
- Proyectos de monitoreo y conservaciÃ³n participativa en zonas rurales.
- Actividades pedagÃ³gicas e investigaciÃ³n formativa en colegios y universidades.

### **2. Delimitaciones (Lo que NO incluye)**

- **Renacuajos y fases larvales:**
    - El sistema se limita exclusivamente a especÃ­menes adultos debido a las marcadas diferencias morfolÃ³gicas y ontogenÃ©ticas en etapas larvales.
- **AnÃ¡lisis moleculares o genÃ©ticos:**
    - No se realizan pruebas de laboratorio ni secuenciaciÃ³n de ADN. La identificaciÃ³n es 100% no invasiva (visual, bioacÃºstica y espacial).
- **DiagnÃ³stico de salud o fitosanitario:**
    - El sistema no evalÃºa el estado de salud del espÃ©cimen ni detecta afecciones patÃ³genas (como la presencia del hongo *Batrachochytrium dendrobatidis* / quitridiomicosis).
- **Cobertura total de la anurofauna nacional:**
    - Colombia cuenta con mÃ¡s de **911 especies de ranas y sapos** registradas. El alcance inicial del sistema seleccionarÃ¡ un conjunto priorizado de especies (acotado por disponibilidad de datos morfolÃ³gicos, acÃºsticos y relevancia ecolÃ³gica), sin abarcar la totalidad de la diversidad del paÃ­s en la primera versiÃ³n.
- **GarantÃ­a de precisiÃ³n bajo condiciones extremas:**
    - No se garantiza un 100% de precisiÃ³n ante tomas con oclusiÃ³n severa del espÃ©cimen, desenfoque extremo, iluminaciÃ³n nula o audios con alta contaminaciÃ³n por ruido ambiental sin filtrar.



