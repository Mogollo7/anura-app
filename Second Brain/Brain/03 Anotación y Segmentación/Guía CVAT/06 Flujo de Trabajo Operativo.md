---
title: "Flujo de Trabajo Operativo"
tipo: guÃ­a
proyecto: Anura
fuente: "Guia_CVAT_Anuro.docx (v1.0)"
tags: [anura, cvat, anotaciÃ³n, segmentaciÃ³n]
---

# Flujo de Trabajo Operativo

â† [[05 GuÃ­a por Etiqueta â€” Las 16 Etiquetas]] Â· [[GuÃ­a CVAT â€” Ãndice]] Â· [[07 Reglas Generales de Calidad]] â†’

Etiquetar bien no es solo dibujar polÃ­gonos: es sistematizar la captura de datos biolÃ³gicos en un orden que minimice el error humano y el olvido de partes. Sigue estas fases en orden para cada imagen.


### Fase 0 â€” PreparaciÃ³n del entorno

Antes de etiquetar una sola imagen, confirma lo siguiente:

- Tienes esta guÃ­a a mano (o el video tutorial) para consultar dudas de criterio, no solo de manejo de la herramienta.

- Las 16 etiquetas estÃ¡n cargadas en el proyecto vÃ­a Raw (SecciÃ³n 1.5), con los colores exactos del Anexo A â€” asÃ­ se identifica de un vistazo quÃ© ya estÃ¡ etiquetado.

- Conoces el orden de etiquetado de la SecciÃ³n 2 antes de empezar.


### Fase 1 â€” Triaje de la imagen (etiquetado global)

Paso 1.1 â€” Etiqueta anuro_completo: dibuja el bounding box o polÃ­gono que encierre al animal por completo.

CondiciÃ³n operativa: rellena obligatoriamente los 5 atributos (vista, calidad_enfoque, postura, sexo_aparente, estadio) antes de pasar a las partes del cuerpo. Si la calidad es â€œborrosa_parcialâ€ en un grado severo, evalÃºa si vale la pena continuar etiquetando el resto de la imagen o descartarla.


### Fase 2 â€” SegmentaciÃ³n y atributos de cabeza y tronco

Una vez validado el animal completo, etiqueta las regiones principales de mayor a menor tamaÃ±o.

Paso 2.1 â€” cabeza: polÃ­gono desde el hocico hasta el inicio del tronco/patas anteriores. Atributo: forma_general.

Paso 2.2 â€” hocico (opcional segÃºn granularidad del proyecto): polÃ­gono de la punta de la cabeza. Atributos: forma, canto_rostral.

Paso 2.3 â€” dorso_flancos: polÃ­gono de toda la parte superior y lateral del cuerpo, excluyendo cabeza y patas. Rellena los 4 atributos (color_base, patron, textura, linea_vertebral).


### Fase 3 â€” Detalles de ojos, tÃ­mpanos y glÃ¡ndulas

Este es el paso mÃ¡s delicado por el tamaÃ±o reducido de los polÃ­gonos y la necesidad de usar correctamente el atributo lado.

Paso 3.1 â€” ojo: polÃ­gono preciso alrededor del globo ocular. Atributo crÃ­tico: lado (fundamental, decÃ­delo primero); luego orientacion, forma_pupila, color_iris, tamano_relativo.


> [!note] CondiciÃ³n operativa
> Si la rana estÃ¡ en vista lateral, solo se etiqueta el ojo visible. Usa no_determinable Ãºnicamente cuando de verdad no puedas asignar un lado, no como salida fÃ¡cil.


Paso 3.2 â€” timpano: polÃ­gono circular detrÃ¡s del ojo. Atributos: lado, visibilidad, tamano_relativo_ojo.

Paso 3.3 â€” glandulas_pliegues: un polÃ­gono por cada estructura glandular visible (p. ej. pliegue dorsolateral, parotoide). Atributos: tipo, prominencia.

Paso 3.4 â€” saco_vocal (si es identificable): polÃ­gono sobre la regiÃ³n gular. Atributos: presencia, posicion. En la mayorÃ­a de fotos de campo esta etiqueta simplemente no aplicarÃ¡ â€” no la fuerces.


### Fase 4 â€” RegiÃ³n ventral e ingle

Requiere una vista ventral, o que el animal estÃ© siendo sostenido/manipulado de forma que muestre el vientre.

Paso 4.1 â€” vientre: polÃ­gono desde la garganta hasta la cloaca, sin incluir las patas. Usa la guÃ­a visual de la SecciÃ³n 4.7 para color_base y patron.

Paso 4.2 â€” ingle_muslo: polÃ­gono en la zona de uniÃ³n de la pata trasera con el cuerpo. Atributos: color_patron, color_flash. Si la pata estÃ¡ recogida y esta zona no es visible, usa no_evaluable en color_patron y ausente en color_flash en vez de omitir la etiqueta.


### Fase 5 â€” Extremidades y detalles distales

Requiere precisiÃ³n; se recomienda etiquetar primero las 4 extremidades completas y luego hacer zoom para dedos, palmeadura y tubÃ©rculo metatarsal.

Paso 5.1 â€” extremidad_anterior (x2) y extremidad_posterior (x2): polÃ­gono de contorno completo de cada pata. Atributo lado obligatorio en las 4.

Paso 5.2 â€” dedos y palmeadura: polÃ­gonos precisos sobre manos y pies, con zoom. Atributos: extremidad (anterior/posterior), presencia_discos, grado de palmeadura.

Paso 5.3 â€” tuberculo_metatarsal: polÃ­gono pequeÃ±o en la base del pie, en vista ventral/lateral. Atributos: presencia, forma.


### Fase 6 â€” Cierre y control de calidad

Paso 6.1 â€” region_cloacal: polÃ­gono pequeÃ±o en la zona anal, si es visible. Atributo: visibilidad.

Paso 6.2 â€” RevisiÃ³n final: oculta la imagen de fondo en CVAT y observa solo los polÃ­gonos trazados. Â¿Tienen los colores correctos segÃºn el Anexo A? Â¿Falta alguna estructura visible en la foto original?


![[cvat-44.png]]
*Figura 5.1 â€” ValidaciÃ³n cruzada: revisiÃ³n de una anotaciÃ³n ya completada.*


### Resumen de condiciones operativas para el Ã©xito


| **CondiciÃ³n** | **Detalle** |
| --- | --- |
| Consistencia de zoom | Para partes pequeÃ±as (ojo, tÃ­mpano, dedos, tubÃ©rculo metatarsal), haz zoom in (300â€“500%) antes de trazar el polÃ­gono. |
| Atributos en cascada | El atributo lado siempre debe ser el primero en definirse al etiquetar partes pares. |
| Manejo de la incertidumbre | No inventes informaciÃ³n. Si un color o forma no es determinable con confianza, usa el valor no_determinable / no_evaluable correspondiente â€” es preferible a un dato falso. |
| ValidaciÃ³n cruzada | Recomendado: al inicio del proyecto, haz que una segunda persona revise el 10% de las anotaciones de cada anotador para calibrar criterio entre el equipo. |



