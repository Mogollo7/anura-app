Es una evolución natural y técnicamente impecable de la arquitectura. Este concepto se conoce en Inteligencia Artificial como Adaptadores Jerárquicos por Clústeres Multiclase (Multi-Class Micro-Adapters) o Árboles de Adaptación Modular.
En lugar de limitar el desempate a parejas (A vs. B), organizas las especies difíciles en Complejos o Clústeres Crípticos de N especies (A, B, C, D, E...). Así es como funciona esta dinámica acumulativa sin generar conflictos entre especies ni obligar a descargar el encoder base.
1. ¿Cómo funciona un Micro-Adaptador Multiclase (A, B, C, D...)?
Cuando un grupo de especies del mismo género en una subregión comparte rasgos morfológicos extremadamente similares (por ejemplo, 5 especies del género Pristimantis en el Oriente Antioqueño):
 * Nivel 1 (BioCLIP Limpio): Detecta que la foto pertenece al "Clúster Críptico X" (donde conviven las especies A, B, C, D).
 * Nivel 2 (Adaptador del Clúster): La app móvil carga la matriz de proyección específica de ese clúster (W_{\text{Clúster\_X}}).
 * Proyección y Desempate: Esta matriz proyecta el vector de 512 dimensiones de BioCLIP a un subespacio especializado de K dimensiones (donde K es el número de especies del clúster). En este subespacio, los rasgos distintivos de A, B, C y D están maximizados y separados entre sí.
2. ¿Cómo se añaden especies de forma acumulativa sin romper nada?
El gran beneficio de esta arquitectura modular es el Aislamiento Total por Clúster. Si en el futuro descubres o incorporas una nueva especie críptica E a un grupo existente que ya tenía a A, B, C, D:
[ A, B, C, D ]  ───> Se descubre la Especie E ───> [ A, B, C, D, E ]
      │                                                  │
      ▼                                                  ▼
 Reentrenar solo W_Clúster_X                       Reentrenar W_Clúster_X
 (Tarda 30 segundos en PC)                         (Involucra a las 5 especies del grupo)
      │                                                  │
      ▼                                                  ▼
 Matriz W de 40 KB                                 Matriz W de 50 KB

Lo que sucede en tu Servidor / Módulo Administrativo:
 * No tocas el Encoder BioCLIP 1 (.onnx): Sigue congelado e intacto en el celular.
 * No tocas los demás Clústeres: Las ranas del Urabá, del Valle de Aburrá o del Magdalena Medio no se ven afectadas en absoluto.
 * Reentrenas ÚNICAMENTE la matriz del Clúster X: Tomas las fotos de referencia de A, B, C, D y la nueva E. Ejecutas un entrenamiento ligero con ArcFace en tu PC (tarda menos de 1 minuto) para calcular la nueva matriz de proyección W_{\text{Clúster\_X}} ajustada ahora para 5 clases.
 * Actualizas el JSON: La matriz W_{\text{Clúster\_X}} pasa de pesar 40\text{ KB} a 50\text{ KB} dentro del archivo JSON de esa subregión.
Lo que sucede en el Celular del Usuario:
 * El celular detecta la actualización y descarga el nuevo archivo JSON de 50\text{ KB}.
 * Ahora el sistema identifica A, B, C, D y E sin haber cambiado el archivo principal del modelo ni haber afectado la precisión de ninguna otra especie del catálogo.
3. Estructura Jerárquica en el Archivo de Paquete (JSON)
Así se representa un clúster acumulativo de N especies dentro del paquete subregional:
{
  "package_id": "02_oriente_antioqueno",
  "cryptic_clusters": [
    {
      "cluster_id": "cluster_pristimantis_altiplano",
      "member_species": [
        "Pristimantis_illex",
        "Pristimantis_penelopus",
        "Pristimantis_dorsopictus",
        "Pristimantis_NUEVA_ESPECIE_E"
      ],
      "cluster_adapter_matrix": [
        [0.0123, -0.0451, "... matriz W proyectora de 50 KB ..."]
      ],
      "cluster_centroids": {
        "Pristimantis_illex": [0.041, -0.112, "... 512 floats ..."],
        "Pristimantis_penelopus": [-0.210, 0.551, "... 512 floats ..."],
        "Pristimantis_dorsopictus": [0.115, 0.002, "... 512 floats ..."],
        "Pristimantis_NUEVA_ESPECIE_E": [0.891, -0.312, "... 512 floats ..."]
      },
      "context_tiebreaker": {
        "altitude_weight": 0.40,
        "microhabitat_weight": 0.30
      }
    }
  ]
}

4. ¿Qué pasa si el grupo crece demasiado (ej. 15–20 especies similares)?
Si un grupo de especies crípticas crece mucho (por ejemplo, en el Chocó o en el Urabá donde hay docenas de especies del mismo género), en lugar de una sola matriz grande, la clasificación se organiza en un Árbol de Decisión en Cascada:
                              [ Clúster General Pristimantis ]
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       ▼                                           ▼
          [ Sub-clúster A: Vientre Amarillo ]         [ Sub-clúster B: Vientre Manchado ]
                 (Especies A, B, C)                         (Especies D, E, F)
                       │                                           │
                       ▼                                           ▼
            Mini-Adaptador A (25 KB)                    Mini-Adaptador B (25 KB)

 * Nivel 1: El modelo identifica que es una Pristimantis.
 * Nivel 2 (Sub-clúster): Un primer micro-adaptador evalúa un rasgo macro (ej. patrón ventral o inglés) y divide la búsqueda en dos subgrupos.
 * Nivel 3 (Especie Final): Un segundo micro-adaptador de 20\text{ KB} resuelve la especie exacta.
Ventajas de esta Dinámica Acumulativa
 * Cero Interferencias (Modularidad Pura): Entrenar o corregir la especie E dentro del Clúster X no altera los pesos de las especies del Clúster Y. No existe el riesgo de "descalibrar" el resto del sistema (Catastrophic Forgetting).
 * Escalabilidad Infinita: Puedes empezar con un paquete simple de 3 especies crípticas en un clúster e ir encajando F, G, H a medida que recopiles fotos en campo.
 * Descargas Peticionadas / Ligeras: El celular solo descarga la actualización del clúster que cambió. Tu backend en Hostinger solo sirve pequeños archivos de actualización de kilobytes.