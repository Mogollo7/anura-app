---
title: "Cinco bloques de datos que entrega el administrador"
tags: [fuente, admin, datos]
created: 2026-09-25
status: draft
source: "Second Brain/notes/Para entrenar el modelo, calcular l.md"
---

# Cinco bloques de datos que entrega el administrador

> [!NOTE] Fuente literal
> Transcripción íntegra de `notes/Para entrenar el modelo, calcular l.md`. No está resumida. Mapa: [[00_Indice_Principal]]. Nodo de trabajo: [[Entradas y Ficha de Especie]] · [[Plan de Construccion del Admin]].

Para entrenar el modelo, calcular los centroides, calibrar las barreras de decisión y empaquetar los archivos JSON en el Módulo Administrativo, el administrador (herpetólogo o administrador del sistema) debe entregar cinco bloques de datos estructurados.
1. Dataset de Imágenes y Anotaciones Taxonómicas
Es la materia prima visual necesaria para extraer embeddings con BioCLIP 1 y calcular los centroides L_2.
 * Fotografías Curadas y Filtradas: Lote de imágenes limpias por especie (mínimo 10–15 imágenes de adultos, libres de borrosidad extrema o duplicados).
 * Taxonomía Oficial (Nomenclatura):
   * Family (ej. Strabomantidae)
   * Genus (ej. Pristimantis)
   * Species / Taxon_ID (ej. Pristimantis_illex)
   * Common Name (ej. Rana de lluvia de montaña)
 * Etiquetas de Desarrollo y Morfología:
   * Life Stage (Adult, Juvenile, Metamorph, Larva).
   * Morph ID (Identificador si es una especie polimórfica, ej. red_morph, yellow_morph).
 * Anotación de Medición (CVAT Export / COCO JSON):
   * Polígono/Línea de Longitud Rostro-Cloaca (LRC en mm) y cuadro delimitador (Bounding Box) del ejemplar.
2. Metadatos Ecológicos y Mapeo Territorial (Ficha de la Especie)
Datos biológicos para configurar la Capa 3 de OSR (Gatekeeper Bayesiano) y asignar las especies a sus paquetes subregionales.
 * Perfil Altitudinal:
   * Altitud media (\mu_{\text{altitud}} en msnm).
   * Desviación estándar (\sigma_{\text{altitud}} en msnm) o rango absoluto [mínimo, máximo].
 * Matriz de Probabilidades de Sustrato / Microhábitat (P(\text{Hábitat} \mid S_k)):
   * Asignación de probabilidades prior por tipo de superficie (valores entre 0.01 y 1.0):
     * Hojarasca: 0.90
     * Vegetación / Hoja: 0.70
     * Quebrada / Agua: 0.05
     * Roca: 0.10
 * Mapeo Subregional (Asignación Territorial):
   * Lista de las 9 subregiones de Antioquia donde la especie está confirmada (ej. ["02_oriente", "05_norte"]).
 * Pesos del Perfil de Especie (w_v, w_g, w_m):
   * Asignación del balance de importancia: Peso Visual (w_v), Peso Geográfico (w_g) y Peso de Microhábitat (w_m), asegurando que w_v + w_g + w_m = 1.0.
3. Configuración de Complejos y Clústeres Crípticos
Información necesaria para que el servidor entrene los Micro-Adaptadores (W_{\text{clúster}}) para pares o grupos confusos.
 * Definición de Grupo Críptico:
   * Cluster ID (ej. pristimantis_altiplano_cluster).
   * Lista de especies involucradas (ej. ["Pristimantis_illex", "Pristimantis_penelopus"]).
 * Hiperparámetros de Entrenamiento (ArcFace Loss):
   * Margen angular (m = 0.35).
   * Escala (s = 30).
   * Épocas de entrenamiento (típicamente 20–50 épocas en GPU local) y Tasa de Aprendizaje (Learning Rate).
4. Parámetros de Calibración OSR y Umbrales de Rechazo
Datos numéricos para definir las barreras de rechazo y los tres niveles de la Cascada Taxonómica.
 * Factor de Elasticidad EVT (\alpha):
   * Multiplicador para calcular el radio de rechazo específico de especie:
     
 * Tolerancia de Reconstrucción de Manifold (\epsilon_{\text{clúster}}):
   * Error de reconstrucción máximo permitido (E_{\text{rec}}) para detectar especies intrusas dentro de un micro-adaptador.
 * Umbrales Manuales de Super-Centroides:
   * Asignación o validación de los umbrales de caída a nivel de Género (\tau_{\text{género}} \approx 0.62\text{--}0.65) y Familia (\tau_{\text{familia}} \approx 0.52\text{--}0.55).
5. Metadatos de Publicación del Paquete Subregional
Información de empaquetado para la distribución OTA (Over-The-Air) hacia la app móvil.
 * Versión del Paquete: (ej. v3.2.0).
 * ID del Paquete Subregional: (ej. 09_uraba_antioqueno).
 * Formato de Cuantización de Vectores: (ej. FP16 para reducir peso en disco o FP32 para precisión completa).
Resumen del Flujo de Entrada en el Módulo Admin
┌──────────────────────────────────────────────────────────────────────────────────┐
│                          ENTRADAS DEL ADMINISTRADOR                              │
├───────────────────────────────┬──────────────────────────────────────────────────┤
│ DATASET VISUAL                │ Fotos curadas + Bounding Boxes / LRC + Taxonomía.│
│ FICHA ECOLÓGICA               │ Altitud (μ, σ) + Matriz Sustratos + Subregiones. │
│ CONFIGURACIÓN DE CLÚSTERES    │ Listas de especies crípticas a entrenar ArcFace. │
│ PARÁMETROS OSR                │ Factores α de Weibull + Tolerancia ε de Manifold.│
│ METADATOS BUILD               │ Versión JSON + ID Subregional + Cuantización.    │
└───────────────────────────────┴──────────────────────────────────────────────────┘
                                         │
                                         ▼
                 [ EJECUCIÓN DE COMPILACIÓN EN PC / WORKER LOCAL ]
                                         │
                                         ▼
            [ EXPIDE PAQUETE JSON OTA SUBOBJETIVO (< 1 MB POR ZONA) ]
