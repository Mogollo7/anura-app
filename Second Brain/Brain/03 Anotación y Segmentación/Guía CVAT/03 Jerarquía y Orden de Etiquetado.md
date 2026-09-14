---
title: "Jerarquía y Orden de Etiquetado"
tipo: guía
proyecto: Anura
fuente: "Guia_CVAT_Anuro.docx (v1.0)"
tags: [anura, cvat, anotación, segmentación]
---

# Jerarquía y Orden de Etiquetado

â† [[02 Primeros Pasos en CVAT]] · [[Guía CVAT â€” àndice]] · [[04 Estándares Generales (anuro_completo)]] â†’

Etiquetar en un orden consistente evita que se te olviden partes y hace que el trabajo sea comparable entre anotadores. Sigue siempre este orden:


| **Nivel** | **Qué incluye** | **Ejemplo de etiquetas** |
| --- | --- | --- |
| 1. Contenedor principal | El individuo completo. Se aplica primero, siempre. | anuro_completo |
| 2. Anatomía principal | Regiones anatómicas mayores, trazadas de mayor a menor tamaño. | cabeza, dorso_flancos, vientre, extremidad_anterior, extremidad_posterior |
| 3. Detalles anatómicos | Estructuras específicas dentro de las regiones mayores. | hocico, ojo, timpano, glandulas_pliegues, ingle_muslo, saco_vocal, tuberculo_metatarsal, dedos, palmeadura, region_cloacal |



