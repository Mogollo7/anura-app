DOCUMENTO MAESTRO DE ARQUITECTURA TÉCNICA Y ESPECIFICACIONES SISTÉMICAS: PROYECTO ANURA
1. Visión General y Filosofía de Arquitectura
El Proyecto ANURA está concebido como una plataforma de ingeniería de software e Inteligencia Artificial enfocada en la identificación taxonómica de anuros (ranas y sapos) en campo para el departamento de Antioquia, Colombia.
El sistema resuelve la tensión fundamental entre alta precisión en especies crípticas y autonomía 100\% offline en dispositivos móviles mediante un principio de Desacoplamiento Total entre el Extractor Base y el Catálogo Taxonómico.
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DISPOSITIVO MÓVIL (OFFLINE - EDGE)                    │
│                                                                             │
│   [ Foto en Campo ] + [ GPS / Altitud / Microhábitat ]                      │
│          │                                                                  │
│          ▼                                                                  │
│   ┌──────────────┐      Vector e_x (512d)   ┌───────────────────────────┐   │
│   │ BioCLIP 1    │ ───────────────────────> │ CASCADA TAXONÓMICA LOCAL  │   │
│   │ (CONGELADO)  │                          │ Paquete JSON Subregional  │   │
│   └──────────────┘                          │ Nivel 1: Especie / Cluster │   │
│    ONNX (~100 MB)                           │ Nivel 2: Género sp.       │   │
│    Instalación Única                        │ Nivel 3: Familia sp.      │   │
│                                             │ Nivel 4: Open Set (OOD)   │   │
│                                             └───────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ Sincronización diferida (Wi-Fi/Red)
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SERVIDOR / SERVIDOR LOCAL (PC WORKER)                 │
│                                                                             │
│   [ Backend Hostinger ] ──────────> [ Worker PC: BioCLIP 2.5 (ViT-H/14) ]    │
│   Queue de Sincronización           Auditoría OSR, Fine-Tuning y Compilación│
│                                     de Paquetes JSON (< 1 MB OTA)           │
└─────────────────────────────────────────────────────────────────────────────┘

Principios Doctrinarios de Diseño:
 * Inferencia Local a Costo 0\text{ USD}: La inferencia en el celular se ejecuta de forma local mediante ONNX Runtime Mobile / TFLite procesado en la NPU/CPU del smartphone. No hay dependencia de APIs de pago en la nube por consulta.
 * Inmutabilidad del Executable y Encoder: El encoder pesado BioCLIP 1 (ViT-B/16, 512\text{d}) pesa \sim 100\text{--}150\text{ MB} y se instala una sola vez en la aplicación móvil. Nunca se vuelve a descargar ni a reentrenar globalmente.
 * Actualización de Catálogo Ultraliviana (Over-The-Air - OTA): La adición de nuevas especies o la resolución de complejos confusos se realiza mediante archivos JSON o binarios subregionales de entre 30\text{ KB} y 1.2\text{ MB}.
 * Infraestructura de Servidor Económica: El backend en la nube (Hostinger, \sim 3\text{--}8\text{ USD/mes}) actúa como puente de datos. Toda la carga pesada de auditoría y entrenamiento reentrenado se ejecuta en una PC local con GPU NVIDIA corriendo BioCLIP 2.5 (ViT-H/14, 1024\text{d}).
2. Extractor Visual y Estrategia de Transfer Learning No Agresivo
El uso de Transfer Learning tradicional (Fine-Tuning completo de todas las capas) sobre el encoder de BioCLIP en dispositivos móviles provoca Olvido Catastrófico (Catastrophic Forgetting), descalibrando el espacio latente y destruyendo la capacidad Zero-Shot general del modelo.
Para evitar re-descargas del modelo base y mantener la estabilidad del espacio vectorial, el proyecto utiliza la estrategia de Tuning por Micro-Adaptadores en Cascada (Cascaded Micro-Adapter Tuning).
[Foto de Entrada] ──> [BioCLIP 1 Limpio (Congelado)] ──> Vector e_x (512d)
                                                            │
                     ┌──────────────────────────────────────┴──────────────────────────────────────┐
                     ▼                                                                             ▼
        [Especie Diferenciable]                                                       [Grupo/Par Críptico Confuso]
      Identificación Coseno Directa                                                     Activa Micro-Adaptador W_cluster
      con Centroide L2 (Nivel 1)                                                       Matriz de 30-50 KB en el JSON
                                                                                                   │
                                                                                                   ▼
                                                                                     v' = W_cluster · e_x
                                                                                     Proyección y Desempate

2.1. Adaptadores Jerárquicos por Clúster Multiclase
 * Nivel Base: Para la gran mayoría de las especies diferenciables, el vector e_x de BioCLIP 1 se compara directamente mediante similitud coseno contra los centroides unitarios \hat{C}_k.
 * Nivel Críptico (Micro-Adaptadores): Cuando un grupo de N especies comparte morfologías casi idénticas (ej. un complejo de Pristimantis), el Módulo Administrativo entrena una matriz de proyección lineal liviana W_{\text{clúster}} \in \mathbb{R}^{512 \times m} (m \le 512) usando ArcFace Loss:
Donde m=0.35 es el margen angular y s=30 es la escala. Esta mini-matriz (de 30\text{ a }50\text{ KB}) se incrusta en el JSON del paquete subregional y se ejecuta en la app únicamente cuando la muestra cae en el área de incertidumbre de ese clúster.
3. Estructuración Territorial de Paquetes Geográficos (Antioquia)
El paquete completo de Antioquia se fragmenta en 9 Subpaquetes Subregionales basados en las divisiones biogeográficas oficiales, subdivididos internamente por Pisos Térmicos (Altitud).
3.1. Riqueza Teórica vs. Riqueza Real Entrenable
A nivel literario (SiB Colombia / Instituto Humboldt), Antioquia reporta \sim 230 especies de anuros. Sin embargo, al filtrar "especies huérfanas" (aquellas sin fotografías públicas utilizables o solo presentes en frascos de museos), el catálogo real entrenable se sitúa entre 120 y 140 especies, las cuales representan más del 98\% de las interacciones reales en campo.
[ Catálogo Teórico en Literatura (SiB / Humboldt) ] ────────────── ~230 especies
                       │
                       ├── (- 60 a 70 spp) Sin fotos públicas / Solo holotipos de museo
                       ├── (- 20 a 30 spp) Registros dudosos / Complejos no resueltos
                       ▼
[ Catálogo Real Entrenable (Fotos Disponibles) ] ───────────────── ~130 especies (120 - 140)

3.2. Distribución de Especies por Subpaquete Subregional
| Subpaquete / Zona | Riqueza Teórica | Especies Reales Entrenables | Pisos Térmicos Predominantes |
|---|---|---|---|
| 01. Valle de Aburrá | ~30 spp. | ~25 spp. | Premontano / Montano (1300 - 2800\text{ msnm}) |
| 02. Oriente Antioqueño | ~60 spp. | ~42 spp. | Altiplano / Vertiente (200 - 3000\text{ msnm}) |
| 03. Suroeste Antioqueño | ~70 spp. | ~40 spp. | Cafetero / Citará (600 - 3400\text{ msnm}) |
| 04. Occidente Antioqueño | ~80 spp. | ~45 spp. | Seco / Páramo Frontino (500 - 3800\text{ msnm}) |
| 05. Norte Antioqueño | ~55 spp. | ~32 spp. | Montano / Belmira (1000 - 3300\text{ msnm}) |
| 06. Nordeste Antioqueño | ~70 spp. | ~35 spp. | Transición / Anorí (200 - 2500\text{ msnm}) |
| 07. Magdalena Medio | ~50 spp. | ~38 spp. | Tierras Bajas (100 - 600\text{ msnm}) |
| 08. Bajo Cauca | ~40 spp. | ~28 spp. | Planicies / Humedales (50 - 400\text{ msnm}) |
| 09. Urabá Antioqueño | ~110 spp. | ~55 spp. | Chocó Biogeográfico (0 - 800\text{ msnm}) |
3.3. Requerimientos de Dataset e Individuos por Especie
Para generar un centroide estable normalizado L_2 (\hat{C}_k = \frac{\sum e_i}{\Vert{}\sum e_i\Vert{}_2}), el dataset de imágenes debe cumplir con criterios de variabilidad biológica estricta:
 * Mínimo Viable (Especies Raras): 10–15 fotos procedentes de al menos 3–5 individuos diferentes.
 * Recomendado (Estándar): 30–50 fotos de 8–12 individuos diferentes.
 * Óptimo (Especies Polimórficas / Frecuentes): 80–100+ fotos de 15+ individuos.
 * Gestión de Polimorfismo: Para especies con morfos de coloración drásticamente opuestos (ej. Oophaga histrionica), el sistema no promedia las imágenes en un solo vector, sino que genera Sub-centroides por Morfo (Oophaga_red_morph, Oophaga_yellow_morph).
4. Integración Multimodal y Ponderación Bayesiana de Contexto
Los datos de contexto actúan como un filtro pasabanda bayesiano que ajusta la probabilidad prior antes y después de la inferencia visual.
4.1. Variables de Contexto y Grado de Impacto
 * Coordenadas GPS (Lat/Long) [10/10]: Carga automáticamente el paquete subregional.
 * Altitud (msnm) [10/10]: Leída por sensor o cruce DEM. Determina el perfil Gaussiano.
 * Microhábitat / Sustrato [8/10]: Selección manual mediante Chips: [Hojarasca], [Vegetación], [Quebrada/Agua], [Roca].
 * Patrón Temporo-Lumbreras [8/10]: Hora del día y temporada de lluvias.
 * Señal Bioacústica [10/10]: Grabación de audio de 3–5 segundos para desempate directo de especies gemelas.
4.2. Ecuación de Puntuación Dinámica Conjunta
Donde la probabilidad altitudinal P(\text{Altitud} \mid k) está parametrizada por una distribución Gaussiana:
4.3. Matriz de Pesos Variables por Perfil Ecológico
| Perfil Ecológico | Peso Visual (w_v) | Peso Geográfico (w_g) | Peso Microhábitat (w_m) | Comportamiento del Sistema |
|---|---|---|---|---|
| Generalista (ej. Rhinella horribilis) | 80\% | 10\% (\sigma = 1000\text{m}) | 10\% | Permisivo con la ubicación; manda la imagen. |
| Microendémica (ej. Pristimantis Páramo) | 30\% | 60\% (\sigma = 120\text{m}) | 10\% | Filtro estricto; colapsa el score si la altitud no coincide. |
| Par Críptico (Complejos confusos) | 35\% | 35\% | 30\% | Exige coincidencia de sustrato o canto para desempate. |
5. Protocolo de Reconocimiento en Espacio Abierto (OSR - 3 Capas)
El motor OSR previene la sobreconfianza (Overconfidence Bias) mediante un pipeline de rechazo en 3 capas.
                           [ Vector e_x (BioCLIP 1 - 512d) ]
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ CAPA 1: UMBRALES ELÁSTICOS EVT POR CENTROIDE (t_k)                                  │
│ ¿Sim_cos(e_x, C_k) >= t_k para alguna especie del paquete?                          │
└─────────────────────────────────────────────────────────────────────────────────────┘
                       │ Sí                                   │ No
                       ▼                                      ▼
┌───────────────────────────────────────────────────────┐  [ RECHAZO: OSR_DESCONOCIDO ]
│ CAPA 2: RESIDUO DE RECONSTRUCCIÓN EN MICRO-ADAPTADORES│
│ En clústeres crípticos: ¿El error E_rec <= ε_cluster? │
└───────────────────────────────────────────────────────┘
                       │ Sí                                   │ No
                       ▼                                      ▼
┌───────────────────────────────────────────────────────┐  [ RECHAZO: OSR_INTRUSO_CLÚSTER ]
│ CAPA 3: INTERRUPTOR BAYESIANO DE ALTITUD              │
│ ¿P(Altitud | k) >= 0.05?                              │
└───────────────────────────────────────────────────────┘
                       │ Sí                                   │ No
                       ▼                                      ▼
        [ CLASIFICACIÓN ACEPTADA ]                         [ RECHAZO: OSR_INCOHERENCIA_GEO ]

Detalle Operativo de las Capas:
 * Capa 1 (EVT / Distribución de Weibull): Cada centroide \hat{C}_k posee un radio de corte adaptativo \tau_k = \mu_{\text{intra}} + \alpha \cdot \sigma_{\text{intra}}. Especies polimórficas poseen un \tau_k amplio; especies uniformes, uno estrecho.
 * Capa 2 (Residuo de Manifold E_{\text{rec}}): En clústeres crípticos, evalúa si la muestra pertenece al subespacio del adaptador calculando el error de reconstrucción:
   
   
   Si E_{\text{rec}} > \epsilon_{\text{clúster}}, la muestra es rechazada como un intruso no visto en el clúster.
 * Capa 3 (Interruptor Pasabanda Altitudinal): Si P(\text{Altitud} \mid k) < 0.05, el puntaje colapsa a cero, forzando la salida a OSR_INCOHERENCIA_GEO.
6. Cascada Taxonómica de Fallback con Super-Centroides
Para evitar rechazos categóricos ante fotos difíciles, juveniles o géneros raros, el sistema implementa Super-Centroides de Género (\hat{C}_{G_g}) y Familia (\hat{C}_{F_f}) calculados mediante normalización L_2 agregada.
[ NIVEL 1: ESPECIE EXACTA ] ─────────> ¿Sim_cos >= τ_k y E_rec <= ε? ───> ACEPTADO (Especie Exacta)
          │ Fallo
          ▼
[ NIVEL 2: GÉNERO FALLBACK ] ────────> ¿Sim_cos >= τ_Gg? ──────────────> ASIGNADO (Pristimantis sp.)
          │ Fallo
          ▼
[ NIVEL 3: FAMILIA FALLBACK ] ───────> ¿Sim_cos >= τ_Ff? ──────────────> ASIGNADO (Strabomantidae sp.)
          │ Fallo
          ▼
[ NIVEL 4: RECHAZO TOTAL ] ─────────────────────────────────────────────> OSR_OUT_OF_DISTRIBUTION

Fórmulas de Agregación:
 * Super-Centroide de Género: \hat{C}_{G_g} = \frac{\sum_{k \in G_g} \hat{C}_k}{\left\Vert{} \sum \hat{C}_k \right\Vert{}_2}
 * Super-Centroide de Familia: \hat{C}_{F_f} = \frac{\sum_{g \in F_f} \hat{C}_{G_g}}{\left\Vert{} \sum \hat{C}_{G_g} \right\Vert{}_2}
 * Desigualdad de Umbrales: \tau_k (0.75-0.85) \ge \tau_{G_g} (0.60-0.70) \ge \tau_{F_f} (0.50-0.58)
7. Arquitectura del Módulo Administrativo
El Módulo Administrativo es la suite central en el servidor/PC local que gestiona la Ingesta, Anotación, Entrenamiento y Compilación de paquetes.
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                             MÓDULO ADMINISTRATIVO CENTRAL                              │
├──────────────────────┬──────────────────────┬──────────────────┬───────────────────────┤
│ 1. INGESTA & SCRAPING│ 2. ANOTACIÓN MORFO-  │ 3. CONTEXTO &    │ 4. ENGINE FINE-TUNING │
│    AUTOMÁTICO        │    METRÍA & EDAD     │    PESOS         │    & PACKAGER         │
├──────────────────────┼──────────────────────┼──────────────────┼───────────────────────┤
│ • Connectors: GBIF,  │ • CVAT Polígonos     │ • Slider weights │ • Layer Freezing      │
│   iNaturalist, SiB.  │   cabeza/cloaca/ojo. │   (wv, wg, wm).  │   (ViT-B/16).         │
│ • pHash Deduplication│ • Estimación LRC     │ • Gaussiana μ, σ │ • ArcFace Margin      │
│   y filtro de ruido. │   (mm) y edad.       │   altitudinal.   │   (m=0.35, s=30).     │
│ • Control de Especies│ • Morfos de color    │ • Matriz sustrato│ • Export: L2 Centroids│
│   Huérfanas.         │   (Sub-centroides).  │   y microhábitat.│   + JSON Compiler.    │
└──────────────────────┴──────────────────────┴──────────────────┴───────────────────────┘

8. Especificación del Esquema JSON Subregional Híbrido
Estructura completa del paquete compilado (09_uraba_v3.json) listo para distribución OTA a la aplicación móvil:
{
  "package_metadata": {
    "package_id": "09_uraba_antioqueno_v3",
    "region_name": "Urabá y Chocó Biogeográfico",
    "version": "3.2.0",
    "last_updated": "2026-09-25",
    "embedding_dim": 512,
    "quantization": "FP16"
  },
  "family_nodes": [
    {
      "family_id": "Dendrobatidae",
      "canonical_name": "Dendrobatidae sp.",
      "common_name": "Ranas venenosas",
      "centroid": [0.0124, -0.0912, 0.8123, "... 512 floats ..."],
      "rejection_tau_family": 0.52
    },
    {
      "family_id": "Centrolenidae",
      "canonical_name": "Centrolenidae sp.",
      "common_name": "Ranas de cristal",
      "centroid": [-0.1042, 0.3211, 0.1190, "... 512 floats ..."],
      "rejection_tau_family": 0.55
    }
  ],
  "genus_nodes": [
    {
      "genus_id": "Oophaga",
      "family_id": "Dendrobatidae",
      "canonical_name": "Oophaga sp.",
      "centroid": [0.0312, -0.0891, 0.7712, "... 512 floats ..."],
      "rejection_tau_genus": 0.62
    }
  ],
  "species_catalog": [
    {
      "taxon_id": "Oophaga_histrionica",
      "genus_id": "Oophaga",
      "canonical_name": "Oophaga histrionica",
      "sub_centroids": [
        {
          "morph_id": "red_morph",
          "vector": [0.0421, -0.1102, 0.8841, "... 512 floats ..."]
        },
        {
          "morph_id": "yellow_morph",
          "vector": [-0.1201, 0.0451, 0.7912, "... 512 floats ..."]
        }
      ],
      "rejection_tau": 0.78,
      "context_parameters": {
        "altitude_mean_msnm": 250,
        "altitude_std_dev": 180,
        "weights": { "visual": 0.85, "geo": 0.10, "habitat": 0.05 },
        "substrate_priors": { "hojarasca": 0.9, "vegetacion": 0.7, "agua": 0.1 }
      }
    }
  ],
  "cryptic_clusters": [
    {
      "cluster_id": "pristimantis_uraba_cluster_01",
      "confused_species": ["Pristimantis_species_A", "Pristimantis_species_B"],
      "micro_adapter_matrix": [
        [0.0123, -0.0451, "... matriz W_cluster de 512x64 floats (35 KB) ..."]
      ],
      "epsilon_reconstruction": 0.16
    }
  ]
}

9. Resumen Sintético de Decisiones de Arquitectura
 * Inferencia Local: Procesamiento local 100\% offline en el celular a costo $0 USD.
 * Inmutabilidad del Modelo Base: bioclip_v1.onnx congelado en el APK (100\text{ MB}). Cero re-descargas pesadas.
 * Evolución por Micro-Adaptadores: Entrenamiento ligero con ArcFace únicamente para grupos crípticos. Las matrices (30\text{--}50\text{ KB}) viajan en el JSON del paquete subregional.
 * Manejo de Open Set en 3 Capas: EVT (Weibull) \rightarrow Residuo de Manifold (E_{\text{rec}}) \rightarrow Gatekeeper Altitudinal Gaussiano.
 * Cascada Taxonómica: Caída elegante de 4 niveles: Especie \rightarrow Género sp. \rightarrow Familia sp. \rightarrow Open Set.
 * Módulo Administrativo en Servidor: Ingesta automatizada, filtro pHash, anotación morph en CVAT, cálculo de centroides L_2 y exportación OTA.