---
title: "Estrategia de ConstrucciÃ³n del Dataset"
proyecto: Anura
fuente: "Notion â€” Proyecto IdentificaciÃ³n de Anuros Colombia"
tags: [anura, metodologÃ­a, dataset]
---

# Estrategia de ConstrucciÃ³n del Dataset

## Estrategia de construcciÃ³n de dataset

#### **Objetivo del Dataset**

- **Tarea Principal:** Construir un conjunto de datos representativo que integre mÃºltiples individuos provenientes de diversas Ã¡reas geogrÃ¡ficas, orientado al entrenamiento y validaciÃ³n de modelos de inteligencia artificial para la automatizaciÃ³n del procesamiento de datos en anfibios.
- **Requerimientos Base:**
    - InclusiÃ³n de mÃºltiples especies de anuros.
    - MÃ­nimo **70 individuos por especie**.
    - Etiquetado jerÃ¡rquico estructurado a nivel de **Familia, GÃ©nero y Especie**.
    - IntegraciÃ³n en una **base de datos vectorial** para optimizar la bÃºsqueda por similitud y mejorar el flujo de procesamiento de datos.

> [!important] Cifras reales confirmadas para el prototipo del 27 de septiembre (2026-09-05)
> El catÃ¡logo del prototipo son las **28 especies** de C-3 ([[Inconsistencias y Decisiones Pendientes]]). Confirmado por el autor: **70 individuos/especie** para el modelo de identificaciÃ³n â€” el requisito original, cumplido, no una reducciÃ³n (riesgo D-3 en [[Riesgos del Proyecto]] no se materializÃ³) â€” y **25â€“30 imÃ¡genes/especie** para el subconjunto ya anotado del modelo de segmentaciÃ³n anatÃ³mica, un modelo distinto con un requisito de volumen menor, dentro del rango 20â€“40/especie ya previsto para el segmentador en I-5.

#### **Niveles de ClasificaciÃ³n y Metas de DesempeÃ±o**

Las metas de rendimiento evaluadas exclusivamente a partir de informaciÃ³n visual (sin inclusiÃ³n de metadatos de contexto como ubicaciÃ³n o bioacÃºstica en esta fase inicial) son:

- **Familia:** PrecisiÃ³n objetivo del **90% al 95%**.
- **GÃ©nero:** PrecisiÃ³n objetivo del **80% al 85%**.
- **Especie:** PrecisiÃ³n objetivo de al menos **80%**.

#### **Resultados Obtenidos (Etapa I)**

La evaluaciÃ³n preliminar del modelo sobre el conjunto de validaciÃ³n alcanzÃ³ una **Exactitud Global (Validation Accuracy) del 95.69%**.

> [!important] ActualizaciÃ³n del autor â€” la cifra real es ~99 %
> El resultado real de la Etapa I fue de **~99 % de exactitud**, no 95,69 %. Es un resultado legÃ­timo, no un indicio de fuga de informaciÃ³n: se apoya en (1) **segmentaciÃ³n binaria individuo-vs-fondo** aplicada antes de pasar la imagen al modelo de clasificaciÃ³n, (2) **70 individuos por especie** en estas 10 especies, con las fotos de cada individuo confinadas a un Ãºnico conjunto (train/val/test), y (3) diversidad de individuos en vez de tomas repetidas del mismo ejemplar. Detalle metodolÃ³gico completo, y por quÃ© esto satisface exactamente lo que un split riguroso exige, en [[Modelo de VisiÃ³n â€” BioCLIP]] Â§7. Se conserva la cifra y la tabla originales por trazabilidad del documento fuente.

**Tabla 1.** *MÃ©tricas de desempeÃ±o por especie en la Etapa I.*

| **Especie** | **PrecisiÃ³n** | **Sensibilidad (Recall)** | **PuntuaciÃ³n F1 (F1-Score)** |
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

- **DesempeÃ±o Sobresaliente:** Especies como *Dendrobates truncatus*, *Hyloscirtus palmeri*, *Leucostethus fraterdanieli* y *Rhinella alata* alcanzaron un *F1-Score* perfecto de 1.00, lo que demuestra alta separabilidad visual en estos taxones.
- **Complejidad TaxonÃ³mica Detectada:** Se observa una ligera disminuciÃ³n en el desempeÃ±o dentro del gÃ©nero *Pristimantis* (*P. paisa* con F1 de 0.86 y *P. penelopus* con F1 de 0.86), reflejando la alta variabilidad morfolÃ³gica y cripticidad taxonÃ³mica caracterÃ­stica del grupo.

### **Estrategia y Estructura del Dataset de Anuros**

#### **Resumen de Etapas de ConstrucciÃ³n**

- **Etapa I (Fase Inicial de ValidaciÃ³n Visual):**
    - **NÃºmero de Clases (Especies):** 14 especies mencionadas en el texto original; **10 especies confirmadas** por el autor y por la Tabla 1 de resultados â€” usar esta Ãºltima como cifra oficial ([[Inconsistencias y Decisiones Pendientes]], C-3).
    - **Diversidad TaxonÃ³mica:** 4 familias y 6 gÃ©neros.
    - **Enfoque:** EvaluaciÃ³n del modelo base sin metadatos de contexto (solo imÃ¡genes).
- **Etapa II (ExpansiÃ³n GeogrÃ¡fica y TaxonÃ³mica):**
    - **Regiones de Muestreo:** Antioquia y San JosÃ© del Guaviare (SerranÃ­a de La Lindosa).
    - **Objetivo:** Capturar variabilidad intraespecÃ­fica e interespecÃ­fica mediante una cobertura biogeogrÃ¡fica mÃ¡s amplia.

#### **DistribuciÃ³n BiogeogrÃ¡fica del Dataset (Etapa II)**

#### **A. RegiÃ³n Antioquia**

Se dividiÃ³ el muestreo en tres subregiones clave, sumadas a las especies de distribuciÃ³n general en el departamento:

- **Especies Generalistas de Antioquia:** *Pristimantis acanthinus*, *Pristimantis paisa*, *Rhinella alata*, *Rhinella horribilis* y *Dendropsophus bogerti*.
- **SubregiÃ³n San Rafael:** *Rheobates palmatus*, *Sachatamia electrops*, *Scinax ruber*, *Craugastor raniformis*, *Hyloscirtus palmeri*, *Pristimantis norandinus*, *Dendropsophus microcephalus* y *Pristimantis taeniatus*.
- **SubregiÃ³n Caldas:** *Leucostethus fraterdanieli*.
- **SubregiÃ³n CaracolÃ­:** *Dendrobates truncatus*, *Engystomops pustulosus* y *Pristimantis penelopus*.

[Antioquia - Google Drive](https://drive.google.com/drive/folders/1P_KadCV-HXcmhqQVQzk_UeepTuR--QrD?usp=drive_link)

#### **B. RegiÃ³n San JosÃ© del Guaviare (SerranÃ­a de La Lindosa)**

- **Especies de la Guayana / Amazonia:** *Dendropsophus reticulatus*, *Dendropsophus triangulum*, *Boana cinereascens*, *Boana lanciformis*, *Boana punctata*, *Boana xerophylla*, *Pithecopus hypochondrialis*, *Phyllomedusa tarsius*, *Hyloxalus picachus*, *Pristimantis vilarsi*, *Leptodactylus colombiensis* y *Rhinella* sp. (grupo *margaritifera*).

[San JosÃ© del Guaviare - Google Drive](https://drive.google.com/drive/folders/1PuI0g2HQrKMRl64alf-XWSTfEioZDZe7?usp=drive_link)

---

[[Listado de Individuos y Arreglo TaxonÃ³mico]]

---

### **Fuentes de Datos y Trazabilidad**

#### **Fuentes Primarias**

- **Registro de Campo Propio:** Los datos fotogrÃ¡ficos primarios provienen del trabajo de campo realizado por el investigador Miguel Ãngel Vergara Mazo, enfocado en la recolecciÃ³n *in situ* de muestras visuales de especÃ­menes de anuros en diversas localidades del departamento de Antioquia (incluyendo los municipios de Caldas, CaracolÃ­ y San Rafael) y en la SerranÃ­a de La Lindosa (San JosÃ© del Guaviare).

[dataset - Google Drive](https://drive.google.com/drive/folders/1yce4TNLlO_yAS7cyWdp1395PQU3gFZWj?usp=sharing)

### Calidad y EstandarizaciÃ³n de Datos de Campo

Cada muestra primaria del *dataset* cuenta con **validaciÃ³n taxonÃ³mica previa** realizada por expertos y **metadatos biolÃ³gicos asociados** a su hÃ¡bitat natural.

Para robustecer la variabilidad geogrÃ¡fica y la precisiÃ³n de los modelos, el proceso de estandarizaciÃ³n integra las siguientes reglas:

1. **Enriquecimiento VÃ­a Registros PÃºblicos Georreferenciados:**
    - Se descargan e integran registros biolÃ³gicos de plataformas pÃºblicas (como GBIF e iNaturalist) verificando que cuenten con coordenadas geogrÃ¡ficas precisas e incertidumbre espacial controlada.
    

> [!info]
> Los anuros presentan un alto grado de **polimorfismo**, lo que puede generar variaciones significativas en la apariencia de individuos de una misma especie dependiendo de su ubicaciÃ³n geogrÃ¡fica. Por esta razÃ³n, se recomienda aplicar **filtros por ubicaciÃ³n geogrÃ¡fica** durante la selecciÃ³n de los datos de entrenamiento, con el fin de evitar introducir sesgos o â€œcontaminarâ€ el conjunto de datos con patrones geogrÃ¡ficos que puedan afectar la capacidad de generalizaciÃ³n del modelo. Los datos excluidos del entrenamiento pueden conservarse como **datos de apoyo o evaluaciÃ³n secundaria**.
    
    - A cada imagen de entrenamiento proveniente de estos repositorios o colectas asociadas se le asigna la coordenada exacta de avistamiento del individuo si es posible sino se le aplican una de otra fotografÃ­a para entrenamiento.
2. **Beneficios de la GeorreferenciaciÃ³n en el Entrenamiento:**
    - **Contexto Geoespacial:** Permite que las imÃ¡genes de entrenamiento conserven su ubicaciÃ³n real para cruzar la distribuciÃ³n geogrÃ¡fica de las especies con variables bioclimÃ¡ticas (altitud, temperatura, precipitaciÃ³n) en anÃ¡lisis posteriores.
    - **PrevenciÃ³n de Sesgo GeogrÃ¡fico:** Garantiza una distribuciÃ³n espacial amplia en el conjunto de *Train*, evitando que el modelo aprenda Ãºnicamente patrones de una sola localidad o regiÃ³n.
    - **Filtrado de Calidad:** Las muestras que carezcan de coordenadas verificables o presenten discrepancias entre la distribuciÃ³n conocida de la especie y la ubicaciÃ³n registrada son marcadas para revisiÃ³n manual o descartadas.

#### **Fuentes Secundarias**

- **Plataformas de Ciencia Ciudadana ([iNaturalist](https://www.inaturalist.org/)):** Se utiliza la API de iNaturalist como fuente complementaria de imÃ¡genes. Sin embargo, los datos obtenidos pasan por un **proceso de control y revisiÃ³n manual**, con el fin de verificar su calidad, identificaciÃ³n taxonÃ³mica y procedencia, evitando asÃ­ la incorporaciÃ³n de imÃ¡genes que puedan **contaminar o introducir sesgos en los datos de entrenamiento**.
- **Criterio de InclusiÃ³n:** El recurso secundario se activa Ãºnicamente en aquellas especies donde las capturas fotogrÃ¡ficas de fuente primaria no alcanzan el umbral mÃ­nimo requerido de **70 individuos independientes**.

#### **Trazabilidad y GestiÃ³n de Almacenamiento**

- **GeneraciÃ³n de *Embeddings*:** En lugar de distribuir los archivos de imagen crudos de alto volumen, la canalizaciÃ³n de procesamiento genera y conserva exclusivamente los vectores de caracterÃ­sticas (*embeddings*) extraÃ­dos durante la etapa de representaciÃ³n visual.
- **Empaquetado BiogeogrÃ¡fico Modular:** Los *embeddings* se agrupan y empaquetan modularmente por regiones biogeogrÃ¡ficas (por ejemplo, RegiÃ³n Antioquia y RegiÃ³n Guaviare).
- **Eficiencia de Despliegue:** Esta arquitectura de almacenamiento optimizado permite a los usuarios e investigadores descargar Ãºnicamente los paquetes vectoriales especÃ­ficos segÃºn la zona de prueba o el contexto de interÃ©s, reduciendo drÃ¡sticamente los tiempos de transferencia y los requerimientos computacionales del sistema.

#### Propuesta: tabla de seguimiento del dataset (reemplaza la base de datos vacÃ­a de Notion)

El enlace a esta base en Notion estÃ¡ vacÃ­o (M-5 en [[Inconsistencias y Decisiones Pendientes]]); en vez de dejarlo vacÃ­o tambiÃ©n aquÃ­, esta es la estructura mÃ­nima operativa para que el equipo sepa en quÃ© estado estÃ¡ cada especie sin tener que preguntarlo:

| Campo | Contenido |
| --- | --- |
| Especie | Una fila por cada una de las 28 especies |
| Familia / GÃ©nero | Para poder agrupar y detectar huecos taxonÃ³micos |
| RegiÃ³n biogeogrÃ¡fica | Antioquia / Guaviare / ambas |
| N.Âº individuos propios | Contador real, actualizado al recolectar |
| N.Âº imÃ¡genes por individuo | Para distinguir, por ejemplo, "70 individuos con 1 foto" de "35 individuos con 2 fotos" â€” el total de imÃ¡genes no basta, lo que cuenta es el nÃºmero de individuos distintos |
| Fuente | Campo propio / iNaturalist / GBIF |
| VerificaciÃ³n taxonÃ³mica | Pendiente / Verificada por experto |
| Split asignado | Train / Val / Test â€” fijado una vez, nunca recalculado por especie suelta |
| Anotado en CVAT | SÃ­ / No / En proceso |

Mantenerla como una hoja de cÃ¡lculo simple (o una tabla en este mismo vault) es suficiente para el sprint; no hace falta Notion para esto.

### Criterios de calidad

Para la **V2**, al incorporar **procesamiento offline en el mÃ³vil**, el flujo cambia sustancialmente: el procesamiento morfolÃ³gico, la inferencia del modelo y la optimizaciÃ³n deben ocurrir directamente en el dispositivo antes de cualquier sincronizaciÃ³n.

#### Flujo de imÃ¡genes en V2 (MÃ³vil Offline-First)

- **Captura y Procesamiento Local:**
    - **Inferencia Offline:** La imagen se pasa directamente al modelo local (escalada en memoria a la resoluciÃ³n de entrada requerida, ej. 224Ã—224) para obtener la predicciÃ³n sin depender de conexiÃ³n.
    - **CompresiÃ³n Local:** Se redimensiona la imagen a **1024Ã—768 px** (formato 4:3) y se convierte a **WebP al 80% de calidad**, reduciendo el peso de ~300 KB a **~70-100 KB**.
- **Almacenamiento en Cola (Offline Storage):**
    - La imagen optimizada (~80 KB) y sus metadatos (predicciÃ³n local, coordenadas GPS, fecha/hora) se guardan en el almacenamiento local del dispositivo (SQLite / Base de datos local).
    - Al trabajar con la versiÃ³n optimizada en local, el almacenamiento del telÃ©fono no se satura aunque el usuario registre decenas de especÃ­menes en campo.
- **SincronizaciÃ³n Diferida (Background Sync):**
    - Una vez que el dispositivo detecta conexiÃ³n a internet (Wi-Fi o datos), se dispara la sincronizaciÃ³n en segundo plano enviando el paquete ligero (~80 KB por registro) al servidor/backend.

#### Resumen de Especificaciones V1 vs. V2

| **ParÃ¡metro** | **VersiÃ³n 1 (Web / Servidor)** | **VersiÃ³n 2 (MÃ³vil Offline)** |
| --- | --- | --- |
| **Lugar de Procesamiento** | Servidor | **Dispositivo MÃ³vil (Edge)** |
| **Inferencia / PredicciÃ³n** | Online (VÃ­a API) | **Offline (En el dispositivo)** |
| **ResoluciÃ³n Guardada** | 600 Ã— 450 px | **1024 Ã— 768 px** |
| **CompresiÃ³n** | Sin compresiÃ³n (Original) | **WebP 80% (CompresiÃ³n local)** |
| **Peso Promedio** | ~300 KB | **~70 - 100 KB** |
| **Estrategia de Datos** | Carga inmediata | **Cola local + SincronizaciÃ³n diferida** |

#### Propuesta: tabla de seguimiento de imÃ¡genes (reemplaza la base de datos vacÃ­a de Notion)

| Campo | Contenido |
| --- | --- |
| ID de imagen | Hash o UUID, no el nombre de archivo original |
| Especie / Individuo | VÃ­nculo a la tabla de dataset de arriba |
| Vista | Dorsal / ventral / lateral / detalle |
| ResoluciÃ³n y formato originales | Antes de procesar |
| ResoluciÃ³n y formato procesados | 1024Ã—768 WebP 80 % (V2, ver tabla arriba) |
| Fecha y coordenadas de captura | Cuando existan |
| Anotada en CVAT | SÃ­ / No |
| Split | Train / Val / Test |

La estrategia de **compresiÃ³n y miniaturas en tiempo de ejecuciÃ³n** (para no decodificar imÃ¡genes completas en el Listado de la app) estÃ¡ en [[App MÃ³vil]] Â§6 â€” esta tabla es sobre el dataset de entrenamiento, esa nota es sobre el runtime de la app.

---

#### EstÃ¡ndar Ã“ptimo Recomendado (BioacÃºstica MÃ³vil)

| **ParÃ¡metro** | **Valor Ã“ptimo** | **JustificaciÃ³n TÃ©cnica** |
| --- | --- | --- |
| **Formato** | **WAV / PCM 16-bit** (Raw) | Los algoritmos de extracciÃ³n de caracterÃ­sticas (espectrogramas, MFCCs) e inferencia requieren datos sin pÃ©rdidas. Evita MP3 o AAC, ya que la compresiÃ³n psicoacÃºstica descarta armÃ³nicos finos e interrumpe las frecuencias dominantes. |
| **Tasa de Muestreo** | **44.1 kHz** (o 22.05 kHz) | Por el teorema de Nyquist, 44.1 kHz captura frecuencias de hasta 22.05 kHz, cubriendo holgadamente el espectro vocal de la mayorÃ­a de anuros y fauna (1 kHz - 12 kHz). |
| **Canales** | **Mono (1 canal)** | Reduce el tamaÃ±o del archivo a la mitad sin perder informaciÃ³n acÃºstica relevante para la identificaciÃ³n del canto. |
| **DuraciÃ³n** | **3 a 5 segundos** | Suficiente para registrar mÃºltiples notas o pulsos repetitivos del canto de advertencia (*advertisement call*). Las ventanas largas (e.g., 30s) aumentan innecesariamente el peso y dificultan el aislamiento de eventos de sonido. |
| **SNR MÃ­nimo** | **â‰¥ 15 dB a 20 dB** | Garantiza que la frecuencia dominante de las notas resalte claramente sobre el ruido de fondo (viento, agua, lluvia o ruido ambiental). Un SNR menor a 10 dB suele degradar fuertemente la matriz del espectrograma. |

### EstimaciÃ³n de Peso y Recurso

- **Archivo de audio limpio (WAV Mono 44.1kHz 16-bit, 5s):** **~441 KB**
- **Audio comprimido para almacenamiento local/sync (FLAC):** **~200 KB - 250 KB** (compresiÃ³n sin pÃ©rdidas para la cola de sincronizaciÃ³n offline).
- **Matriz de espectrograma de entrada al modelo (Mel-Spectrogram):** Una vez procesado en el mÃ³vil, la ventana de audio de 3-5s se convierte en una matriz 2D pequeÃ±a (ej. 128 bins Ã— 256 pasos), requiriendo un costo de inferencia muy bajo en el procesador del dispositivo.

*Estrategia de Manejo de Audio* (base de datos vacÃ­a en Notion)

#### Contingencia de audio (si no se alcanza el volumen propio a tiempo)

> [!important] DecisiÃ³n: crecimiento progresivo, no todo-o-nada
> La rama acÃºstica **no debe bloquear el prototipo del 27 de septiembre** ([[Cronograma y Plan de Trabajo]] Â§0). Al reutilizar BioCLIP como codificador acÃºstico ([[Modelo de VisiÃ³n â€” BioCLIP]] Â§8), el volumen necesario para calibrar y validar es menor que el de entrenar un backbone de audio desde cero â€” pero sigue haciendo falta grabaciones reales para el subconjunto de especies que la incluyan.

Fuentes externas evaluadas, en orden de relevancia para anuros neotropicales:

| Fuente | QuÃ© ofrece | CÃ³mo usarla aquÃ­ |
| --- | --- | --- |
| **AnuraSet** (CaÃ±as et al., 2023) | ~93 000 fragmentos de 3 s, 42 especies de anuros neotropicales, grabaciÃ³n pasiva en Brasil; descarga directa (~10,5 GB) en [Zenodo](https://zenodo.org/records/8056090) y cÃ³digo en [GitHub â€” soundclim/anuraset](https://github.com/soundclim/anuraset) | Referencia externa ya prevista en el riesgo D-5; Ãºtil sobre todo para gÃ©neros compartidos con el catÃ¡logo de Anura (p. ej. *Boana*, *Dendropsophus*, *Scinax*, *Rhinella*) aunque las especies exactas no coincidan siempre â€” sirve para calibrar/validar el codificador acÃºstico compartido, no como sustituto de grabaciones propias de las 28 especies objetivo |
| **Xeno-canto â€” colecciÃ³n Anura** | Base de grabaciones de fauna abierta; colecciÃ³n especÃ­fica de anuros iniciada en marzo de 2024, con cobertura mundial creciente | Revisar especie por especie del catÃ¡logo de Anura si hay grabaciones con licencia compatible (CC); es la fuente con mayor probabilidad de tener **especies exactas** del catÃ¡logo, aunque la cobertura por especie es desigual y hay que verificarla, no asumirla |
| **iNaturalist (observaciones con audio)** | Observaciones de ciencia ciudadana que a veces incluyen grabaciÃ³n de audio, ya usada como fuente secundaria de imÃ¡genes en este mismo documento | Mismo criterio de control de calidad ya aplicado a las imÃ¡genes: verificaciÃ³n taxonÃ³mica e identificaciÃ³n antes de incorporar cualquier audio |

**Procedimiento de la semana 1 del sprint** ([[Cronograma y Plan de Trabajo]] Â§0):

1. Cruzar las 28 especies del catÃ¡logo (C-3 en [[Inconsistencias y Decisiones Pendientes]]) contra AnuraSet y Xeno-canto para ver cuÃ¡ntas tienen cobertura directa o a nivel de gÃ©nero.
2. Si el subconjunto cubierto es razonable (criterio a fijar con el equipo, p. ej. â‰¥ 8â€“10 especies o sus gÃ©neros): implementar la rama acÃºstica **solo para ese subconjunto** en el prototipo, dejando el resto como "sin audio" â€” el sistema ya estÃ¡ diseÃ±ado para funcionar con modalidades ausentes (RNF-06, [[Arquitectura Multimodal]] Â§3).
3. Si la cobertura es insuficiente incluso a nivel de gÃ©nero: declarar la rama acÃºstica como trabajo futuro para el prototipo del 27 de septiembre, sin que esto afecte al resto del pipeline â€” es exactamente la salida que ya contempla el punto de decisiÃ³n "Â¿Hay datos de audio suficientes?" en [[Cronograma y Plan de Trabajo]].
4. Cualquiera que sea el resultado, el crecimiento posterior es **modular**: aÃ±adir audio de una especie nueva no reentrena el codificador (es el mismo BioCLIP compartido) â€” solo aÃ±ade embeddings acÃºsticos a la base vectorial, igual que el Nivel 1 de [[Escalabilidad]] para imÃ¡genes.

---

#### **Flujo General de PreparaciÃ³n de Datos**

```
[Capturas de Campo]
       â”‚
       â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  MODELO 1: SEGMENTACIÃ“N SEMÃNTICA (Manual en Roboflow)  â”‚
â”‚  â€¢ SelecciÃ³n de imÃ¡genes originales limpia             â”‚
â”‚  â€¢ Trazo manual de partes anatÃ³micas (0 a 7)            â”‚
â”‚  â€¢ GeneraciÃ³n de mÃ¡scaras / JSON                       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                           â”‚
                           â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  MODELO 2: IDENTIFICACIÃ“N DE ESPECIE (AutomÃ¡tico)      â”‚
â”‚  â€¢ AplicaciÃ³n de Data Augmentation por lotes/paquetes  â”‚
â”‚  â€¢ GeneraciÃ³n automÃ¡tica de archivo JSON de anotaciÃ³n  â”‚
â”‚  â€¢ GeneraciÃ³n de 5,100 - 6,000 muestras para Train     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

[[GuÃ­a de AnotaciÃ³n Roboflow (histÃ³rico)]]

---

#### **Control de Duplicados**

- **Filtrado por Hash de PercepciÃ³n (pHash / Difference Hash):** EliminaciÃ³n automÃ¡tica de imÃ¡genes idÃ©nticas o rÃ¡fagas continuas donde no exista variaciÃ³n morfolÃ³gica o de pose (>95% de similitud estructural).
- **Aislamiento de Indiviuos:** FotografÃ­as del mismo espÃ©cimen tomadas en el mismo evento de muestreo deben agruparse bajo un Ãºnico ID de Individuo.

#### **Criterios de ExclusiÃ³n (Descarte Directo)**

- **Fuera de Foco/Desenfoque severo:** FotografÃ­as donde los caracteres diagnÃ³sticos clave (tÃ­mpano, textura de piel, tubÃ©rculos) sean irreconocibles por movimiento o mala focalizaciÃ³n.
- **OclusiÃ³n Extrema:** ImÃ¡genes donde el espÃ©cimen estÃ© cubierto en mÃ¡s de un $80\%$ por sustrato o vegetaciÃ³n, impidiendo la delimitaciÃ³n del torso.
- **IluminaciÃ³n Degradada:** ExposiciÃ³n extrema (completamente subexpuesta sin detalle en sombras o sobreexpuesta con pÃ­xeles quemados en el patrÃ³n de coloraciÃ³n).
- **Audio Degradado:** Fragmentos con $SNR < 10\text{ dB}$, saturaciÃ³n de micrÃ³fono por proximidad excesiva, o interferencia dominante de ruido eÃ³lico/lluvia sobre la frecuencia fundamental del canto.

---

### **Variabilidad Necesaria (Criterios de InclusiÃ³n y Diversidad)**

Para garantizar la generalizaciÃ³n del modelo en campo bajo operaciÃ³n offline, el dataset debe recopilar:

- **VariaciÃ³n Visual:** MÃºltiples Ã¡ngulos (dorsal, lateral, ventral), variedad de sustratos (hojarasca, rocas, vegetaciÃ³n, musgo), distintas distancias de captura y oclusiones parciales naturales.
- **VariaciÃ³n por Individuo:** Muestreo balanceado entre machos, hembras, juveniles y adultos, asÃ­ como polimorfismos cromÃ¡ticos (morfos de coloraciÃ³n dentro de la misma especie).
- **VariaciÃ³n Ambiental:** Capturas diurnas y nocturnas (con uso de linterna/flash), condiciones de lluvia/humedad alta y diversidad de microhÃ¡bitats.
- **VariaciÃ³n GeogrÃ¡fica:** Colectas distribuidas en diferentes departamentos, valles interandinos y gradientes de elevaciÃ³n para mitigar el sesgo por poblaciones locales.
- **VariaciÃ³n Temporal:** Registros recopilados en diferentes Ã©pocas del aÃ±o (temporadas secas y de lluvias/picos reproductivos).

---

### **Data Augmentation y PolÃ­ticas de No Sesgo**

#### **Transformaciones Permitidas (Imagen)**

- **GeomÃ©tricas:** `HorizontalFlip` (p=0.5), `VerticalFlip` (p=0.3), `RandomRotate90` (p=0.5), `ShiftScaleRotate` (lÃ­mite 20%, p=0.5), `ElasticTransform` y `GridDistortion` (deformaciÃ³n orgÃ¡nica suave para simular postura).
- **Color e IluminaciÃ³n:** `RandomBrightnessContrast` (pm 30%), `RandomShadow` (p=0.2), `HueSaturationValue` (lÃ­mite estricto en Hue: pm 10, Saturation/Value: pm 20), `CLAHE` (clip=4.0).

#### **Transformaciones Permitidas (Audio)**

- **Espectrograma / Dominio de Onda:** `TimeShift` (desplazamiento temporal), adiciÃ³n de ruido blanco/ambiental de fondo suave (SNR  15 dB), `FrequencyMasking` y `TimeMasking` (SpecAugment sobre la matriz de espectrograma).

#### **Transformaciones NO Permitidas (Riesgo BiolÃ³gico)**

- **ModificaciÃ³n Excesiva de Color (`HueShift > 15`):** Alterar los tonos drÃ¡sticamente invalida la respuesta del modelo en especies donde la coloraciÃ³n o aposematismo es el carÃ¡cter taxonÃ³mico primario (ej. *Dendrobatidae*).
- **InversiÃ³n de Espectrogramas / Pitch Shift Extremo en Audio:** Alterar la frecuencia fundamental o la estructura de pulsos del canto de advertencia genera patrones acusticamente imposibles que confunden al clasificador.
- **Deformaciones GeomÃ©tricas Extremas:** Estiramientos no proporcionales que alteren la morfometrÃ­a corporal del anuro (ej. relaciÃ³n longitud hocico-cloaca).

#### **PolÃ­tica para No Sesgar el Dataset**

- **Balanceo por Undersampling/Oversampling:** Las especies hiper-representadas en bases pÃºblicas se limitan en cantidad; las especies raras o endÃ©micas reciben oversampling mediante la tuberÃ­a de augmentaciÃ³n sintÃ©tica controlada.
- **NormalizaciÃ³n de Fondo:** Incluir conscientemente imÃ¡genes con fondos neutros o variados para evitar que la red asocie una especie a un tipo especÃ­fico de hoja o color de fondo (*shortcut learning*).

---

### **DivisiÃ³n del Dataset y EvitaciÃ³n de Fuga de InformaciÃ³n**

#### **Estrategia de Split**

- **Estrategia Principal:** **Split por Localidad / GeogrÃ¡fico (GroupKFold / GroupSplit)**.
- **JustificaciÃ³n:** Garantiza que imÃ¡genes o cantos registrados en la misma localidad o en el mismo evento de campo no queden repartidos entre entrenamiento y prueba.

#### **Estructura del Dataset**

| **Etapa** | **ImÃ¡genes Originales** | **Con AugmentaciÃ³n** | **Notas MetodolÃ³gicas** |
| --- | --- | --- | --- |
| **Train** | 550 | 5,100 \ 6,000 | AugmentaciÃ³n aplicada **exclusivamente** a Train. Oversampling en clases raras/crÃ­ticas. |
| **ValidaciÃ³n** | 120 | N/A | Sin augmentaciÃ³n. EvaluaciÃ³n limpia para selecciÃ³n de hiperparÃ¡metros y *early stopping*. |
| **Test** | 120 | N/A | Datos nunca vistos durante el entrenamiento. EvaluaciÃ³n final y referencia para optimizaciÃ³n mÃ³vil (Edge). |

#### **Reglas para Evitar Fuga de InformaciÃ³n (*Data Leakage*)**

1. **Aislamiento Temporal de AugmentaciÃ³n:** Las transformaciones sintÃ©ticas se aplican **al vuelo (*on-the-fly*)** durante el bucle de entrenamiento, jamÃ¡s antes de realizar el corte *Train/Val/Test*.
2. **Agrupamiento por Individuo/SesiÃ³n:** Todas las tomas, Ã¡ngulos o audios derivados de un mismo espÃ©cimen o sitio exacto de muestreo pertenecen **100% al mismo grupo** (*Train*, *Val* o *Test*).
3. **No ContaminaciÃ³n de NormalizaciÃ³n:** Las estadÃ­sticas de normalizaciÃ³n (media y desviaciÃ³n estÃ¡ndar de RGB) se calculan Ãºnicamente sobre el conjunto de *Train* y se aplican a *Val* y *Test*.

---

### **Conjunto Open-Set (Manejo de Especies Desconocidas)**

- **ImplementaciÃ³n:** **SÃ­**.
- **PropÃ³sito:** Crucial para el despliegue mÃ³vil offline. Si un usuario fotografÃ­a un organismo o anuro de una especie no presente en el modelo, la app debe clasificarlo como *"Desconocido / Especie No Registrada"* en lugar de forzar una falsa predicciÃ³n de alta confianza.
- **ConstrucciÃ³n del Conjunto Open-Set:**
    - **InclusiÃ³n de "Out-of-Distribution" (OOD):** Se compone de un subconjunto de imÃ¡genes de otras familias de anuros no incluidas en el modelo, otros anfÃ­bios (ej. salamandras, cecilias), e insectos/objetos de hojarasca comunes en el hÃ¡bitat.
    - **TÃ©cnica de Inferencia Offline:** ImplementaciÃ³n de umbrales de incertidumbre por calibraciÃ³n de probabilidad (**Temperature Scaling**) y capa de detecciÃ³n **Out-of-Distribution** basada en la distancia del vector de caracterÃ­sticas (*embeddings*) extraÃ­do por el modelo frente a los centroides de las clases conocidas.

#### Propuesta: tabla de seguimiento del conjunto Open-Set (reemplaza la base de datos vacÃ­a de Notion)

La metodologÃ­a completa estÃ¡ en [[Open-Set Recognition]]; lo que faltaba era la estructura operativa para llevar la cuenta del conjunto recolectado:

| Campo | Contenido |
| --- | --- |
| ID de muestra | UUID |
| Tipo | Near-OOD (anuro fuera del catÃ¡logo) / Far-OOD (otro anfibio, insecto, hojarasca, objeto) |
| DescripciÃ³n | QuÃ© es exactamente |
| Fuente | Campo propio / iNaturalist / GBIF |
| Uso | ValidaciÃ³n (fijar umbral) / Test (reportar AUROC, nunca el mismo conjunto que validaciÃ³n) |

Separar near-OOD de far-OOD en la tabla desde el inicio evita el error mÃ¡s comÃºn de la secciÃ³n 4 de [[Open-Set Recognition]]: reportar solo el promedio y esconder que detectar una hoja es fÃ¡cil pero detectar un *Pristimantis* fuera de catÃ¡logo es lo difÃ­cil.



