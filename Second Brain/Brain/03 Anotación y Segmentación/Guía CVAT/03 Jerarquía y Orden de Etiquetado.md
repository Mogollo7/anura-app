---
title: "JerarquÃ­a y Orden de Etiquetado"
tipo: guÃ­a
proyecto: Anura
fuente: "Guia_CVAT_Anuro.docx (v1.0)"
tags: [anura, cvat, anotaciÃ³n, segmentaciÃ³n]
---

# JerarquÃ­a y Orden de Etiquetado

â† [[02 Primeros Pasos en CVAT]] Â· [[GuÃ­a CVAT â€” Ãndice]] Â· [[04 EstÃ¡ndares Generales (anuro_completo)]] â†’

Etiquetar en un orden consistente evita que se te olviden partes y hace que el trabajo sea comparable entre anotadores. Sigue siempre este orden:


| **Nivel** | **QuÃ© incluye** | **Ejemplo de etiquetas** |
| --- | --- | --- |
| 1. Contenedor principal | El individuo completo. Se aplica primero, siempre. | anuro_completo |
| 2. AnatomÃ­a principal | Regiones anatÃ³micas mayores, trazadas de mayor a menor tamaÃ±o. | cabeza, dorso_flancos, vientre, extremidad_anterior, extremidad_posterior |
| 3. Detalles anatÃ³micos | Estructuras especÃ­ficas dentro de las regiones mayores. | hocico, ojo, timpano, glandulas_pliegues, ingle_muslo, saco_vocal, tuberculo_metatarsal, dedos, palmeadura, region_cloacal |



