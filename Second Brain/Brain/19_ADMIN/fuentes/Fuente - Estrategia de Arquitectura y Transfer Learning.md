---
title: "Estrategia de arquitectura y transfer learning no agresivo"
tags: [fuente, arquitectura, admin]
created: 2026-09-25
status: draft
source: "Second Brain/notes/Estrategia de Arquitectura, Transfe.md"
---

# Estrategia de arquitectura y transfer learning no agresivo

> [!WARNING] Duplicado del documento maestro, con cifras distintas
> Conserva el texto completo. Divergencias: umbral de confianza mayor o igual a 0.85, `rejection_tau: 0.32`, esquema `cryptic_groups`, matriz hasta 512 por 512, versión de paquete 2.4.0. No fusionar borrando. Base preferida para el compilador: [[Fuente - Documento Maestro de Arquitectura]]. Detalle en [[Contradicciones del Modo Administrativo]].

> [!NOTE] Fuente literal
> Transcripción íntegra de `notes/Estrategia de Arquitectura, Transfe.md`. No está resumida. Mapa: [[00_Indice_Principal]]. Nodo de trabajo: [[Arquitectura Desacoplada]] · [[Fuente - Documento Maestro de Arquitectura]].

Estrategia de Arquitectura, Transfer Learning No Agresivo y Despliegue Modular (Proyecto ANURA)
1. Filosofía de Arquitectura: Desacoplamiento Total (Encoder vs. Catálogo)
La arquitectura del sistema se basa en la separación estricta entre la capacidad de extracción visual (el Encoder) y las representaciones taxonómicas (los Paquetes Geográficos). Esto garantiza inferencia 100\% offline en el dispositivo móvil con costo operativo de 0\text{ USD} por consulta y cero re-descargas pesadas del ejecutable.
┌────────────────────────────────────────────────────────────────────────┐
│                        DISPOSITIVO MÓVIL (EDGE)                        │
│                                                                        │
│   [ Foto en Campo ]                                                    │
│          │                                                             │
│          ▼                                                             │
│   ┌──────────────┐      Vector 512d       ┌────────────────────────┐   │
│   │  BioCLIP 1   │ ─────────────────────> │ Clasificación Cascada  │   │
│   │ (CONGELADO)  │                        │ (Paquete JSON Local)   │   │
│   └──────────────┘                        └────────────────────────┘   │
│    ONNX (~100 MB)                            2 KB por especie normal   │
│    Instalación única                         + Micro-Adapter (30 KB)   │
└────────────────────────────────────────────────────────────────────────┘
                                   │ Sincronización cuando hay señal
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      SERVIDOR & WORKER LOCAL (PC)                      │
│                                                                        │
│   [ Queue Hostinger ] ──────────> [ BioCLIP 2.5 (ViT-H/14) en PC ]     │
│                                   Auditoría, OSR y Reentrenamiento    │
└────────────────────────────────────────────────────────────────────────┘

2. Estrategia de Transfer Learning No Agresivo: Micro-Adaptadores en Cascada
En lugar de aplicar un Fine-Tuning tradicional sobre el encoder de BioCLIP 1 —el cual descalibra el espacio vectorial general, destruye la capacidad Zero-Shot y obliga al usuario a reinstalar archivos ONNX de >100\text{ MB}— se utiliza Tuning por Micro-Adaptadores en Cascada (Cascaded Micro-Adapter Tuning).
Principios del Transfer Learning No Agresivo:
 * Encoder Base Intacto: El archivo bioclip_v1.onnx (512\text{d}) se mantiene congelado en el teléfono.
 * Matrices de Proyección Ligeras (W_{\text{pair}}): Para pares o complejos de especies crípticas que el BioCLIP limpio confunde, el servidor entrena únicamente una matriz de proyección lineal pequeña (W \in \mathbb{R}^{512 \times 64} o \mathbb{R}^{512 \times 512}) utilizando ArcFace Loss.
 * Inclusión en el Paquete JSON: Esta matriz pesa entre 30\text{ KB} y 100\text{ KB} y se adjunta dentro del archivo JSON del paquete geográfico de la subregión correspondiente.
3. Pipeline de Clasificación Offline en Dos Niveles (Edge)
                       [ Foto capturada en campo ]
                                    │
                                    ▼
                      [ Extractor BioCLIP 1 Limpio ]
                                    │
                            Vector  v (512d)
                                    │
                                    ▼
            [ Nivel 1: Similitud Coseno vs. Centroides L2 ]
            (Filtrado previo por GPS + Altitud + Microhábitat)
                                    │
               ┌────────────────────┴────────────────────┐
               ▼                                         ▼
      [ Confianza High ≥ 0.85 ]                 [ Confianza Dudosa / Par Críptico ]
   Especie identificada directa               Especie_A (0.87) vs. Especie_B (0.86)
               │                                         │
               ▼                                         ▼
     [ Resultado Instantáneo ]                  [ Nivel 2: Cargar Micro-Adaptador ]
                                                Carga W_pair del JSON (30-50 KB)
                                                         │
                                                         ▼
                                                v' = W_pair · v
                                                         │
                                                         ▼
                                                [ Desempate Fino / Resultado ]

Funcionamiento detallado:
 * Nivel 1 (Filtro Global + Contexto): Mide la distancia coseno entre el vector v y los centroides normalizados \hat{C}_k del paquete local. Si la especie es diferenciable (ej. Rhinella horribilis), el Nivel 1 resuelve la identificación en < 100\text{ ms}.
 * Nivel 2 (Desempate por Micro-Adaptador): Si la consulta cae en la zona de incertidumbre de un "Grupo Críptico" predefinido, la app multiplica el vector v por la mini-matriz W_{\text{pair}} presente en el JSON, proyectando la muestra a un espacio sub-dimensional donde los rasgos micro-anatómicos de esas dos especies específicas están maximizados.
4. Protocolo de Incorporación de Nuevas Especies
El sistema distingue entre dos escenarios de actualización para evitar re-descargas del modelo base:
                                [ Nueva Especie a Añadir ]
                                            │
                       ┌────────────────────┴────────────────────┐
                       ▼                                         ▼
           [ Caso A: Especie Normal ]               [ Caso B: Especie Críptica / Compleja ]
         Visualmente diferenciable                    Forma parte de un complejo confuso
                       │                                         │
                       ▼                                         ▼
           Extraer vector medio (512d)              Entrenar Micro-Adaptador W_pair
           con fotos de referencia                  con ArcFace en Servidor
                       │                                         │
                       ▼                                         ▼
            Añadir 512 floats al JSON                 Añadir centroides + Matriz W_pair
             Impacto: +2 KB/especie                   Impacto: +30 KB a +100 KB total
                       │                                         │
                       └────────────────────┬────────────────────┘
                                            │
                                            ▼
                          [ Descarga OTA en Celular (100 KB - 1.2 MB) ]
                          Cero cambios al archivo bioclip_v1.onnx (100 MB)

5. Gestión de Open Set Recognition (OSR) y Contexto Bayesiano
Para evitar sobreconfianza ante especies no vistas o fuera del paquete geográfico, se aplican límites de decisión cerrados combinados con un filtro de probabilidad prior.
A. Detección de Open Set (Rechazo por Umbral \tau_k)
Cada centroide \hat{C}_k almacena un radio máximo permitido \tau_k (calibrado en el servidor mediante la distancia de Mahalanobis o la distribución de Weibull/OpenMax):
B. Scoring Contextual Dinámico (Filtro Bayesiano)
El sistema pondera el resultado visual con los datos ingresados por el usuario o sensores del celular mediante funciones Gaussianas parametrizadas por especie:
Donde la probabilidad altitudinal es:
Matriz de Pesos Variables por Perfil Ecológico:
| Perfil de la Especie | Peso Visual (w_v) | Peso Geográfico (w_g) | Peso Microhábitat (w_m) | Comportamiento |
|---|---|---|---|---|
| Generalista (ej. Rhinella horribilis) | 80\% | 10\% (\sigma = 1000\text{m}) | 10\% | Permisivo con ubicación; prioriza la imagen. |
| Microendémica (ej. Pristimantis de Páramo) | 30\% | 60\% (\sigma = 120\text{m}) | 10\% | Anula la predicción si la altitud no coincide. |
| Par Críptico (Complejos confusos) | 35\% | 35\% | 30\% | Requiere coincidencia de sustrato/canto para desempate. |
6. Módulo Administrativo Completo de Entrenamiento y Gestión
Plataforma central que gestiona la recolección, anotación, calibración de pesos y empaquetamiento final.
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
│ • Control de Especies│ • Morfos de color    │ • Matriz sustrato│ • Expor: L2 Centroids │
│   Huérfanas.         │   (Sub-centroides).  │   y microhábitat.│   + JSON Compiler.    │
└──────────────────────┴──────────────────────┴──────────────────┴───────────────────────┘

Funciones Clave del Módulo Administrativo:
 * Scraping y Filtro de Ruido:
   * Descarga masiva por Taxon ID desde GBIF, iNaturalist y SiB Colombia.
   * Filtro pHash para eliminar duplicados/ráfagas y descarte automático de especímenes de museo en formol o fotos desenfocadas.
 * Anotación de Morfología y Determinación de Edad:
   * Integración con CVAT para polígonos de proporciones: relación Tímpano/Ojo, Longitud Rostro-Cloaca (LRC en mm).
   * Etiquetado de estadio vital: [Renacuajo], [Juvenil], [Adulto Macho], [Adulto Hembra].
   * Gestión de Sub-centroides por Morfo: Si una especie es polimórfica, genera vectores independientes para cada patrón de coloración (morfo_liso, morfo_rayado).
 * Parametrización de Contexto:
   * Sliders para definir manualmente o calcular estadísticamente \mu_{\text{altitud}}, \sigma_{\text{altitud}} y los pesos w_v, w_g, w_m.
 * Calculador de Centroides y Empaquetador:
   * Aplica normalización L2 unitaria (\hat{C}_k = \frac{\sum e_i}{\Vert{}\sum e_i\Vert{}_2}) sobre el dataset validado.
   * Compila el árbol de paquetes jerárquicos de Antioquia (9 Subregiones \times 4 Pisos Térmicos).
7. Estructura Estándar del Paquete JSON Subregional (09_uraba.json)
{
  "package_metadata": {
    "package_id": "09_uraba_antioqueno",
    "region_name": "Urabá y Chocó Biogeográfico",
    "version": "2.4.0",
    "total_species": 55,
    "embedding_dim": 512,
    "quantization": "FP16"
  },
  "species_catalog": [
    {
      "taxon_id": "Oophaga_histrionica",
      "canonical_name": "Oophaga histrionica",
      "sub_centroids": [
        {
          "morph_id": "red_morph",
          "vector": [0.0421, -0.1102, 0.8841, "... 512 floats ..."]
        }
      ],
      "rejection_tau": 0.32,
      "context_parameters": {
        "altitude_mean_msnm": 250,
        "altitude_std_dev": 180,
        "weights": { "visual": 0.85, "geo": 0.10, "habitat": 0.05 },
        "substrate_priors": { "hojarasca": 0.9, "vegetacion": 0.7, "agua": 0.1 }
      }
    }
  ],
  "cryptic_groups": [
    {
      "group_id": "pristimantis_complex_01",
      "confused_species": ["Pristimantis_species_A", "Pristimantis_species_B"],
      "micro_adapter_matrix": [
        [0.0123, -0.0451, "... matriz W_pair de 512x64 floats (35 KB) ..."]
      ],
      "context_tiebreaker": {
        "preferred_variable": "altitude_msnm",
        "weight_override": 0.50
      }
    }
  ]
}

8. Distribución de los 9 Subpaquetes de Antioquia
El mapa de empaquetamiento territorial se compone de 1 Paquete Raíz dividido en 9 Subpaquetes Subregionales con especies reales filtradas (fotografiadas) y listas para inferencia offline:
[PAQUETE RAÍZ: ANTIOQUIA_MASTER] (~130 Especies Reales con Fotos)
 │
 ├── 01_Valle_de_Aburra (~25 spp)  ──> Enfoque periurbano / ladera.
 ├── 02_Oriente_Antioqueno (~42 spp) ──> Altiplano y embalses.
 ├── 03_Suroeste_Antioqueno (~40 spp) ──> Farallones del Citará / Cafetera.
 ├── 04_Occidente_Antioqueno (~45 spp) ──> Cañón del Cauca a Páramo Frontino.
 ├── 05_Norte_Antioqueno (~32 spp)  ──> Belmira y bosques de niebla.
 ├── 06_Nordeste_Antioqueno (~35 spp) ──> Transición Anorí/Amalfi.
 ├── 07_Magdalena_Medio (~38 spp)    ──> Tierras bajas y ciénagas.
 ├── 08_Bajo_Cauca (~28 spp)         ──> Planicies aluviales del Norte.
 └── 09_Uraba_Antioqueno (~55 spp)   ──> Chocó biogeográfico y Darién.

Resumen Técnico Ejecutivo
| Aspecto | Implementación Seleccionada | Beneficio Clave |
|---|---|---|
| Inferencia Móvil | BioCLIP 1 congelado en ONNX + Inferencia Coseno Local. | $0 USD de costo operativo, 100\% offline, latencia < 150\text{ ms}. |
| Transfer Learning | Micro-Adaptadores en Cascada (Nivel 2) en el JSON. | Reentrena solo pares crípticos sin modificar el ONNX del móvil. |
| Actualización | Descarga OTA de archivos JSON de centroides (50\text{ KB} - 1.2\text{ MB}). | El usuario nunca vuelve a descargar el ejecutable/encoder pesado. |
| Auditoría Servidor | BioCLIP 2.5 (ViT-H/14, 1024d) en PC Worker local. | Resuelve capturas marcadas como OPEN_SET cuando hay conexión. |
| Open Set & Contexto | Radios \tau_k + Función Gaussiana Altitudinal + Microhábitat. | Evita falsos positivos y filtra el 90% de especies no viables por GPS. |
