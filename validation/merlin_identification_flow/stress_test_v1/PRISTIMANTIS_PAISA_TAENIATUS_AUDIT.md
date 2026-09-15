# Auditoria Pristimantis paisa / taeniatus

## 1. Distancia y overlap

- CENTROID_DISTANCE (esta corrida): 0.194403 (confirma el 0.1944 de la fase anterior: True)
- Percentil entre las 820 distancias de pares: 0.00 (0=el par mas cercano posible)
- Intra-species variance A (paisa): mean_dist_to_centroid=0.6481 (n=189)
- Intra-species variance B (taeniatus): mean_dist_to_centroid=0.6288 (n=73)
- Cross-species overlap: 21.7% de embeddings de paisa mas cerca del centroide de taeniatus; 21.9% al reves.

## 2. K-means k=2 (division en subclusters)

- paisa: {"silhouette_score": 0.1077, "cluster_sizes": [112, 77], "full_centroid_dist_to_other_species": 0.1944, "closest_sub_centroid_dist_to_other_species": 0.2563, "splitting_improves_separation": true, "justified": false}
- taeniatus: {"silhouette_score": 0.122, "cluster_sizes": [25, 48], "full_centroid_dist_to_other_species": 0.1944, "closest_sub_centroid_dist_to_other_species": 0.2628, "splitting_improves_separation": true, "justified": false}

## 3. Geografia / Altitud

{
  "geography": {
    "species_a_cells": 21,
    "species_b_cells": 30,
    "cell_overlap_count": 14,
    "distinguishable_by_geography": false
  },
  "elevation": {
    "species_a_p5_p95": [
      1279.0,
      2659.0
    ],
    "species_b_p5_p95": [
      603.7,
      2066.3
    ],
    "overlap_range": [
      1279.0,
      2066.3
    ],
    "distinguishable_by_altitude": false
  }
}

## 4. Ablacion A/B/C/D (especifica del par, n=0)

{
  "A_visual_only": null,
  "B_visual_geo": null,
  "C_visual_altitude": null,
  "D_visual_geo_altitude": null
}

Solo train_embeddings.npz conserva obs_id en el path para esta pareja; 0/159 tenian coordenadas en el cache de iNaturalist ya existente. Elevacion por muestra NO se recupero en esta pasada (neutral=0.5 en alt_score) -- usar elevation por observacion individual requeriria mas llamadas nuevas a OpenTopoData de las que caben en el presupuesto de esta corrida; el ANALISIS a nivel de POBLACION (rango p5-p95 por especie, calculado arriba) SI esta completo.

## 5. Veredicto

`SEPARATION_DIFFICULT`

{
  "CENTROID_DISTANCE": 0.194403,
  "CENTROID_DISTANCE_PERCENTILE_AMONG_820_PAIRS": 0.0,
  "INTRA_SPECIES_VARIANCE": {
    "Pristimantis paisa": {
      "n": 189,
      "mean_dist_to_centroid": 0.648063063621521,
      "std_dist_to_centroid": 0.14415572583675385,
      "max_dist_to_centroid": 1.299068808555603
    },
    "Pristimantis taeniatus": {
      "n": 73,
      "mean_dist_to_centroid": 0.6287965774536133,
      "std_dist_to_centroid": 0.13191388547420502,
      "max_dist_to_centroid": 0.9323211908340454
    }
  },
  "CROSS_SPECIES_OVERLAP": {
    "Pristimantis paisa_embeddings_closer_to_Pristimantis taeniatus_centroid": {
      "n": 189,
      "n_closer_to_other_species": 41,
      "fraction_misassigned": 0.21693121693121692
    },
    "Pristimantis taeniatus_embeddings_closer_to_Pristimantis paisa_centroid": {
      "n": 73,
      "n_closer_to_other_species": 16,
      "fraction_misassigned": 0.2191780821917808
    }
  },
  "VISUAL_ONLY_PERFORMANCE": "NOT_VERIFIED",
  "VISUAL_GEO_PERFORMANCE": "NOT_VERIFIED",
  "VISUAL_ALTITUDE_PERFORMANCE": "NOT_VERIFIED",
  "VISUAL_GEO_ALTITUDE_PERFORMANCE": "NOT_VERIFIED",
  "ablation_not_verified_reason": "0 de 159 muestras de este par en train_embeddings.npz tienen obs_id presente en fase23a_geographic_context/cache/inat_observations_cache.json -- ese cache se construyo especificamente para el pool de evaluacion GEO (KNOWN con coords 0 por diseno, UNKNOWN 412/412), no para el split de entrenamiento general. No se hizo ninguna llamada nueva a la API de iNaturalist para rellenar esto (fuera del alcance de la regla de reutilizar cache de OpenTopoData/iNaturalist ya congelada).",
  "SEPARATION_CONCLUSION": "SEPARATION_DIFFICULT",
  "VISUAL_HARD_PAIR": true
}
