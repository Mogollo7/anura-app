---
title: "Flujo de Trabajo Operativo"
tipo: guía
proyecto: Anura
fuente: "Guia_CVAT_Anuro.docx (v1.0)"
tags: [anura, cvat, anotación, segmentación]
---

# Flujo de Trabajo Operativo

â† [[05 Guía por Etiqueta â€” Las 16 Etiquetas]] · [[Guía CVAT â€” àndice]] · [[07 Reglas Generales de Calidad]] â†’

Etiquetar bien no es solo dibujar polígonos: es sistematizar la captura de datos biológicos en un orden que minimice el error humano y el olvido de partes. Sigue estas fases en orden para cada imagen.


### Fase 0 â€” Preparación del entorno

Antes de etiquetar una sola imagen, confirma lo siguiente:

- Tienes esta guía a mano (o el video tutorial) para consultar dudas de criterio, no solo de manejo de la herramienta.

- Las 16 etiquetas están cargadas en el proyecto vía Raw (Sección 1.5), con los colores exactos del Anexo A â€” así se identifica de un vistazo qué ya está etiquetado.

- Conoces el orden de etiquetado de la Sección 2 antes de empezar.


### Fase 1 â€” Triaje de la imagen (etiquetado global)

Paso 1.1 â€” Etiqueta anuro_completo: dibuja el bounding box o polígono que encierre al animal por completo.

Condición operativa: rellena obligatoriamente los 5 atributos (vista, calidad_enfoque, postura, sexo_aparente, estadio) antes de pasar a las partes del cuerpo. Si la calidad es "borrosa_parcial" en un grado severo, evalàºa si vale la pena continuar etiquetando el resto de la imagen o descartarla.


### Fase 2 â€” Segmentación y atributos de cabeza y tronco

Una vez validado el animal completo, etiqueta las regiones principales de mayor a menor tamaño.

Paso 2.1 â€” cabeza: polígono desde el hocico hasta el inicio del tronco/patas anteriores. Atributo: forma_general.

Paso 2.2 â€” hocico (opcional segàºn granularidad del proyecto): polígono de la punta de la cabeza. Atributos: forma, canto_rostral.

Paso 2.3 â€” dorso_flancos: polígono de toda la parte superior y lateral del cuerpo, excluyendo cabeza y patas. Rellena los 4 atributos (color_base, patron, textura, linea_vertebral).


### Fase 3 â€” Detalles de ojos, tímpanos y glándulas

Este es el paso más delicado por el tamaño reducido de los polígonos y la necesidad de usar correctamente el atributo lado.

Paso 3.1 â€” ojo: polígono preciso alrededor del globo ocular. Atributo crítico: lado (fundamental, decídelo primero); luego orientacion, forma_pupila, color_iris, tamano_relativo.


> [!note] Condición operativa
> Si la rana está en vista lateral, solo se etiqueta el ojo visible. Usa no_determinable àºnicamente cuando de verdad no puedas asignar un lado, no como salida fácil.


Paso 3.2 â€” timpano: polígono circular detrás del ojo. Atributos: lado, visibilidad, tamano_relativo_ojo.

Paso 3.3 â€” glandulas_pliegues: un polígono por cada estructura glandular visible (p. ej. pliegue dorsolateral, parotoide). Atributos: tipo, prominencia.

Paso 3.4 â€” saco_vocal (si es identificable): polígono sobre la región gular. Atributos: presencia, posicion. En la mayoría de fotos de campo esta etiqueta simplemente no aplicará â€” no la fuerces.


### Fase 4 â€” Región ventral e ingle

Requiere una vista ventral, o que el animal esté siendo sostenido/manipulado de forma que muestre el vientre.

Paso 4.1 â€” vientre: polígono desde la garganta hasta la cloaca, sin incluir las patas. Usa la guía visual de la Sección 4.7 para color_base y patron.

Paso 4.2 â€” ingle_muslo: polígono en la zona de unión de la pata trasera con el cuerpo. Atributos: color_patron, color_flash. Si la pata está recogida y esta zona no es visible, usa no_evaluable en color_patron y ausente en color_flash en vez de omitir la etiqueta.


### Fase 5 â€” Extremidades y detalles distales

Requiere precisión; se recomienda etiquetar primero las 4 extremidades completas y luego hacer zoom para dedos, palmeadura y tubérculo metatarsal.

Paso 5.1 â€” extremidad_anterior (x2) y extremidad_posterior (x2): polígono de contorno completo de cada pata. Atributo lado obligatorio en las 4.

Paso 5.2 â€” dedos y palmeadura: polígonos precisos sobre manos y pies, con zoom. Atributos: extremidad (anterior/posterior), presencia_discos, grado de palmeadura.

Paso 5.3 â€” tuberculo_metatarsal: polígono pequeño en la base del pie, en vista ventral/lateral. Atributos: presencia, forma.


### Fase 6 â€” Cierre y control de calidad

Paso 6.1 â€” region_cloacal: polígono pequeño en la zona anal, si es visible. Atributo: visibilidad.

Paso 6.2 â€” Revisión final: oculta la imagen de fondo en CVAT y observa solo los polígonos trazados. ¿Tienen los colores correctos segàºn el Anexo A? ¿Falta alguna estructura visible en la foto original?


![[cvat-44.png]]
*Figura 5.1 â€” Validación cruzada: revisión de una anotación ya completada.*


### Resumen de condiciones operativas para el éxito


| **Condición** | **Detalle** |
| --- | --- |
| Consistencia de zoom | Para partes pequeñas (ojo, tímpano, dedos, tubérculo metatarsal), haz zoom in (300â€“500%) antes de trazar el polígono. |
| Atributos en cascada | El atributo lado siempre debe ser el primero en definirse al etiquetar partes pares. |
| Manejo de la incertidumbre | No inventes información. Si un color o forma no es determinable con confianza, usa el valor no_determinable / no_evaluable correspondiente â€” es preferible a un dato falso. |
| Validación cruzada | Recomendado: al inicio del proyecto, haz que una segunda persona revise el 10% de las anotaciones de cada anotador para calibrar criterio entre el equipo. |



