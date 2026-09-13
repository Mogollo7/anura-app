---
title: "IntroducciÃ³n y Objetivo del Proyecto"
tipo: guÃ­a
proyecto: Anura
fuente: "Guia_CVAT_Anuro.docx (v1.0)"
tags: [anura, cvat, anotaciÃ³n, segmentaciÃ³n]
---

# IntroducciÃ³n y Objetivo del Proyecto

[[GuÃ­a CVAT â€” Ãndice]] Â· [[02 Primeros Pasos en CVAT]] â†’

![[cvat-01.png]]

**ANURO**

*IdentificaciÃ³n herpetolÃ³gica asistida por IA*

**GuÃ­a para el Uso de CVAT**

ClasificaciÃ³n de individuos basada en morfologÃ­a


> [!note] Manual interno de anotaciÃ³n Â· Equipo Anuro
> VersiÃ³n 1.0 Â· CorporaciÃ³n Universitaria Lasallista

El proyecto Anuro desarrolla una aplicaciÃ³n mÃ³vil capaz de identificar especies de anuros (ranas y sapos) a partir de una fotografÃ­a. Para lograrlo, el equipo no entrena un clasificador de â€œcaja negraâ€ convencional: se busca abrir esa caja negra y construir un modelo de pensamiento herpetolÃ³gico, es decir, un sistema que reconozca la especie de la misma forma en que lo harÃ­a un herpetÃ³logo â€” observando y comparando partes anatÃ³micas especÃ­ficas (hocico, ojo, tÃ­mpano, patrÃ³n dorsal, palmeadura, etc.) en vez de memorizar la imagen completa.

Este esquema de anotaciÃ³n en CVAT es la pieza que hace eso posible: cada individuo fotografiado se segmenta en sus partes anatÃ³micas y cada parte se describe con atributos estandarizados (forma, color, patrÃ³n, proporciÃ³n). Ese conjunto de datos estructurado entrena, junto con BioClip, un modelo capaz no solo de decir â€œesta rana es Dendropsophusâ€ sino de explicarle al usuario por quÃ© â€” seÃ±alando quÃ© combinaciÃ³n de rasgos morfolÃ³gicos llevÃ³ a esa conclusiÃ³n.


> [!note] Por quÃ© importa la consistencia del etiquetado
> Cada persona que anota imÃ¡genes le estÃ¡ enseÃ±ando a la IA quÃ© mirar. Un criterio inconsistente entre anotadores (p. ej. dos personas usando â€œocularâ€ una â€œhocico redondeadoâ€ y otra â€œhocico truncadoâ€ para la misma rana) no se cancela estadÃ­sticamente: se convierte en ruido que el modelo aprende como si fuera seÃ±al real. Esta guÃ­a existe para eliminar esa ambigÃ¼edad antes de que llegue al dataset.


### A quiÃ©n va dirigida esta guÃ­a

A cualquier integrante del equipo que vaya a anotar imÃ¡genes en CVAT, sin necesidad de experiencia previa en herpetologÃ­a ni en la herramienta. La guÃ­a cubre desde crear la cuenta hasta el criterio exacto para decidir entre â€œredondeadoâ€ y â€œtruncadoâ€ en un hocico dudoso.


### CÃ³mo estÃ¡ organizada

- SecciÃ³n 1 â€” Primeros pasos en CVAT: cuenta, organizaciÃ³n, equipo, proyecto y tareas.

- SecciÃ³n 2 â€” JerarquÃ­a de etiquetado: en quÃ© orden se anota cada parte.

- SecciÃ³n 3 â€” EstÃ¡ndares generales: quÃ© se considera cada valor de vista, postura, estadio y sexo aparente.

- SecciÃ³n 4 â€” GuÃ­a por etiqueta: las 16 etiquetas del esquema, una por una, con criterio de identificaciÃ³n y antecedente biolÃ³gico.

- SecciÃ³n 5 â€” Flujo de trabajo operativo por fases.

- SecciÃ³n 6 â€” Reglas generales de calidad.

- Anexo A â€” Enlace de descarga del JSON de configuraciÃ³n (Raw) para pegar en CVAT.

- Anexo B â€” Estado de las capturas de pantalla.

- Anexo C â€” Fichas de especie: caracterÃ­sticas morfolÃ³gicas fijas por especie.



