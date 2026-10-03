ETI-OSR-2026: Especificación Técnica y Matemática de Open Set Recognition (OSR) en Tres Capas
1. Objetivo y Fundamentación Teórica
El motor de reconocimiento en espacio abierto (Open Set Recognition - OSR) para el proyecto ANURA establece la barrera de decisión matemática que impide la clasificación forzada (Overconfidence Bias) cuando el usuario fotografía especies no registradas, morfos no catalogados o elementos fuera de distribución (Out-of-Distribution - OOD).
Frente a los métodos tradicionales basados en un umbral escalar único —vulnerables ante el polimorfismo y los pares crípticos—, esta estrategia implementa un Pipeline de Filtrado Jerárquico en Tres Capas. El sistema actúa como un tamiz sucesivo que evalúa la geometría global, la topología del mánifold local y la viabilidad ecológica de la muestra antes de emitir un veredicto de clasificación.
                           [ Vector e_x (BioCLIP 1 - 512d) ]
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ CAPA 1: DISTANCIA ESTOCÁSTICA Y EMBEDDING GLOBAL (EVT)                              │
│ ¿La similitud coseno supera el radio elástico t_k de algún centroide conocido?      │
└─────────────────────────────────────────────────────────────────────────────────────┘
                       │ Sí                                   │ No
                       ▼                                      ▼
┌───────────────────────────────────────────────────────┐  [ RECHAZO: OSR_DESCONOCIDO ]
│ CAPA 2: RESIDUO DE RECONSTRUCCIÓN EN MICRO-ADAPTADORES│
│ En clústeres crípticos: ¿El error de proyección E_rec │
│ es menor al umbral de subespacio ε_cluster?           │
└───────────────────────────────────────────────────────┘
                       │ Sí                                   │ No
                       ▼                                      ▼
┌───────────────────────────────────────────────────────┐  [ RECHAZO: OSR_INTRUSO_CLÚSTER ]
│ CAPA 3: INTERRUPTOR DE SEGURIDAD BAYESIANO (ECOLOGÍA) │
│ ¿La probabilidad conjunta P(Altitud) × P(Hábitat)     │
│ es biológicamente viables?                            │
└───────────────────────────────────────────────────────┘
                       │ Sí                                   │ No
                       ▼                                      ▼
        [ CLASIFICACIÓN ACEPTADA ]                         [ RECHAZO: OSR_INCOHERENCIA_GEO ]

2. Capa 1: Distancia Estocástica con Umbrales Adaptativos EVT (\tau_k)
La primera capa valida la posición del vector de entrada e_x \in \mathbb{R}^{512} extraído por el encoder congelado BioCLIP 1 respecto a los centroides normalizados \hat{C}_k cargados en el paquete geográfico subregional.
2.1. Modelado por Teoría de Valores Extremos (EVT)
En lugar de un umbral fijo global, cada especie k posee un radio de rechazo \tau_k ajustado dinámicamente en el Módulo Administrativo ajustando una Distribución de Weibull de Cola Inversa sobre las distancias intra-clase del dataset de entrenamiento:
Donde d = 1 - \text{Sim}_{\text{cos}}(e_x, \hat{C}_k), \eta_k es el parámetro de escala y \beta_k es el parámetro de forma.
2.2. Condición de Aceptación/Rechazo de Capa 1
Para un paquete local con K especies, se calcula la distancia máxima de similitud:
> Efecto: Especies con alto polimorfismo (ej. Oophaga histrionica) reciben un umbral \tau_k elástico y tolerante, mientras que especies de morfología uniforme (ej. Rhinella horribilis) operan bajo un umbral \tau_k estrecho y riguroso.
> 
3. Capa 2: Control de Mánifold y Error de Reconstrucción de Micro-Adaptadores (E_{\text{rec}})
Cuando la muestra cae en la zona de influencia de un Clúster Críptico Multiclase (un grupo de N especies visualmente indistinguibles como A, B, C, D), la similitud del Nivel 1 no basta. Un micro-adaptador entrenado con ArcFace buscará separar las clases, pero si la foto corresponde a una especie no vista E (intruso), el adaptador intentará asignarla erróneamente a A, B, C o D.
Para evitarlo, la Capa 2 mide la ortogonalidad y el residuo de proyección en el subespacio del clúster.
3.1. Proyección y Reconstrucción Vectorial
Sea W_{\text{clúster}} \in \mathbb{R}^{d \times m} la matriz de proyección ortogonal del micro-adaptador (donde d=512 y m \ll d es la dimensión reducida del clúster):
 * Proyección al Subespacio:
   
 * Reconstrucción al Espacio Original:
   
 * Cálculo del Error de Reconstrucción (E_{\text{rec}}):
   
3.2. Condición de Aceptación/Rechazo de Capa 2
El valor E_{\text{rec}} mide qué tanto se aleja el vector de la "superficie matemática" (mánifold) definida por las especies conocidas del clúster:
Donde \epsilon_{\text{clúster}} es la tolerancia máxima permitida para el subespacio del clúster.
4. Capa 3: Interruptor de Seguridad Bayesiano (Gatekeeper Ecológico)
Un vector puede superar las Capas 1 y 2 por coincidencias visuales (ej. artefactos de luz, patrones de vegetación de fondo). La Capa 3 actúa como un filtro pasabanda biológico utilizando las coordenadas GPS, la altitud (h) y el microhábitat ingresados o detectados.
4.1. Función de Probabilidad Altitudinal Gaussiana
Cada especie k define su nicho altitudinal mediante una distribución Gaussiana con media \mu_k y desviación estándar \sigma_k:
4.2. Ponderación por Microhábitat y Sustrato
Se asigna una matriz de probabilidad prior P(\text{Hábitat} \mid k) \in [0.01, 1.0] basada en el sustrato reportado (Hojarasca, Vegetación, Quebrada, Roca).
4.3. Puntuación Final Conjunta y Condición de Corte
Donde w_v, w_g, w_m son los pesos normalizados (w_v + w_g + w_m = 1.0).
Si la probabilidad altitudinal es menor al 5\% (P < 0.05), el sistema colapsa la puntuación a cero, forzando la salida a Open Set independientemente de la similitud visual.
5. Matriz de Estados de Salida del Sistema
El motor OSR categoriza el resultado en uno de los siguientes estados estructurados para la interfaz de la aplicación móvil y la base de datos local SQLite:
| Código de Salida | Estado | Acción de la App Móvil | Tratamiento en Servidor (Sincronización) |
|---|---|---|---|
| 00_MATCH_OK | Aceptado | Muestra especie, ficha técnica y nivel de certeza. | Registro estándar de ocurrencia. |
| 01_OSR_GLOBAL | Especie Desconocida Global | "Especie fuera del catálogo local. Guardada para revisión." | Pasa a cola de auditoría con BioCLIP 2.5. Candidata a nuevo centroide (+2 KB). |
| 02_OSR_CLUSTER | Intruso en Clúster Críptico | "Rana similar a complejo [X], pero con rasgos no coincidentes." | Evaluada en servidor para determinar si requiere ampliar el micro-adaptador (A, B, C \rightarrow +D). |
| 03_OSR_GEO_FAIL | Incoherencia Geográfica | "Visualmente similar a [Especie], pero fuera de su rango altitudinal/geográfico." | Revisión de coordenadas GPS o registro de expansión de rango poblacional. |
6. Ciclo de Vida de Ingesta y Alimentación Continua (Closed-Loop)
[ CAPTURA RECHAZADA EN CAMPO (SQLite Local) ]
  ├── Foto comprimida (.jpg)
  ├── Embedding e_x (512 floats)
  └── Metadata (GPS, Altitud h, Sustrato)
            │
            ▼ (Sincronización Wi-Fi / Red)
[ BACKEND HOSTINGER (Queue Ingestion) ]
            │
            ▼
[ WORKER LOCAL: BioCLIP 2.5 (ViT-H/14, 1024d) + EXPERTO HUMANO ]
            │
            ├───────────────► Si es Especie Nueva Normal:
            │                 1. Calcula nuevo centroide L2 (512d).
            │                 2. Inserta en JSON subregional (+2 KB).
            │
            └───────────────► Si es Especie Nueva en Clúster Críptico:
                              1. Reentrena matriz W_cluster en PC local (30 seg).
                              2. Actualiza la matriz en el JSON subregional (+10 KB).
            │
            ▼
[ ACTUALIZACIÓN OTA AL MÓVIL ]
El usuario descarga el JSON actualizado (< 100 KB) sin modificar el ejecutable ni el encoder ONNX.

Este esquema de tres capas garantiza que la aplicación móvil opere con una tasa de falsos positivos cercana a cero, manteniendo su peso ultraliviano y convirtiendo cada rechazo de campo en una oportunidad automatizada para enriquecer el catálogo taxonómico.