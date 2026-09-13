---
title: "GuÃ­a CVAT â€” Ãndice"
proyecto: Anura
tipo: Ã­ndice
fuente: "Guia_CVAT_Anuro.docx (v1.0)"
tags: [anura, cvat, anotaciÃ³n, Ã­ndice]
---

# GuÃ­a CVAT â€” Ãndice

[[Anura â€” Ãndice General]]

Manual interno de anotaciÃ³n del equipo Anura (v1.0), convertido desde el documento original de Word con sus 44 figuras. **Es la especificaciÃ³n vigente de anotaciÃ³n**, y sustituye al esquema previo en Roboflow ([[GuÃ­a de AnotaciÃ³n Roboflow (histÃ³rico)]]).

> [!abstract] QuÃ© enseÃ±a esta guÃ­a
> A segmentar cada individuo fotografiado en sus partes anatÃ³micas y describir cada parte con atributos estandarizados, para que el modelo aprenda a identificar como lo harÃ­a un herpetÃ³logo â€”mirando caracteres concretosâ€” en vez de memorizar la imagen completa.

## Secciones

| # | Nota | Contenido |
| --- | --- | --- |
| 01 | [[01 IntroducciÃ³n y Objetivo del Proyecto]] | Por quÃ© se anota asÃ­ y por quÃ© importa la consistencia |
| 02 | [[02 Primeros Pasos en CVAT]] | Cuenta, organizaciÃ³n, pods, proyecto, 16 etiquetas, tareas y jobs |
| 03 | [[03 JerarquÃ­a y Orden de Etiquetado]] | En quÃ© orden se anota cada parte |
| 04 | [[04 EstÃ¡ndares Generales (anuro_completo)]] | especie Â· vista Â· calidad_enfoque Â· postura Â· estadio Â· sexo_aparente |
| 05 | [[05 GuÃ­a por Etiqueta â€” Las 16 Etiquetas]] | Cada etiqueta con su criterio y su antecedente biolÃ³gico |
| 06 | [[06 Flujo de Trabajo Operativo]] | Fases 0 a 6 de una sesiÃ³n de anotaciÃ³n |
| 07 | [[07 Reglas Generales de Calidad]] | QuÃ© hace vÃ¡lida una anotaciÃ³n |
| 08 | [[08 Glosario de TÃ©rminos AnatÃ³micos]] | Vocabulario herpetolÃ³gico necesario |
| 09 | [[09 Anexo A â€” JSON de ConfiguraciÃ³n CVAT]] | ConfiguraciÃ³n *raw* de las etiquetas |
| 10 | [[10 Anexo B â€” Capturas de Pantalla]] | Estado de las figuras |
| 11 | [[11 Anexo C â€” Fichas de Especie]] | Caracteres fijos por especie (3 niveles) |

## Las 16 etiquetas

`anuro_completo` Â· `cabeza` Â· `hocico` Â· `ojo` Â· `timpano` Â· `dorso_flancos` Â· `vientre` Â· `ingle_muslo` Â· `glandulas_pliegues` Â· `saco_vocal` Â· `extremidad_anterior` Â· `extremidad_posterior` Â· `tuberculo_metatarsal` Â· `dedos` Â· `palmeadura` Â· `region_cloacal`

## Las tres reglas que mÃ¡s importan

1. **Etiquetar solo lo observable.** Si una pata estÃ¡ tapada por una hoja, se etiqueta la superficie visible y nunca se adivina la forma oculta.
2. **No observable â‰  ausente.** Que no se vea la palmeadura no significa que la rana no la tenga. La distinciÃ³n recorre todo el sistema, desde la anotaciÃ³n hasta la explicaciÃ³n que ve el usuario ([[Pipeline del Sistema]] Â§2).
3. **La consistencia entre anotadores es el dato.** Dos personas usando criterios distintos para el mismo carÃ¡cter no se compensan estadÃ­sticamente: el modelo aprende esa ambigÃ¼edad como si fuera seÃ±al real.

## El Anexo C y la explicabilidad

Las fichas de especie del [[11 Anexo C â€” Fichas de Especie|Anexo C]] no son solo una ayuda para el anotador. Son la **base de conocimiento taxonÃ³mico** contra la que el sistema compara lo que observa, y lo que permite responder *por quÃ©* identificÃ³ una especie y no otra ([[Pipeline del Sistema]] Â§2, RF-06, HU-03).

Su estructura de tres niveles â€”siempre fijo / tÃ­pico pero confirmable / evaluable por imagenâ€” es lo que evita tanto adivinar como reevaluar en cada foto lo que ya se sabe de la especie.

## RelaciÃ³n con el resto del proyecto

| Esta guÃ­a alimenta aâ€¦ | CÃ³mo |
| --- | --- |
| [[Estrategia de ConstrucciÃ³n del Dataset]] | Define quÃ© se anota y con quÃ© criterios de calidad |
| [[Pipeline del Sistema]] | Las 16 regiones son la salida del modelo de segmentaciÃ³n |
| [[Modelo de VisiÃ³n â€” BioCLIP]] | El recorte de `anuro_completo` es la entrada al extractor visual |
| [[Historias de Usuario]] | HU-03: el herpetÃ³logo refuta seÃ±alando la regiÃ³n concreta |



