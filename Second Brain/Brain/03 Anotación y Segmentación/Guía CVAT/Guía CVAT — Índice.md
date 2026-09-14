---
title: "Guía CVAT â€” àndice"
proyecto: Anura
tipo: índice
fuente: "Guia_CVAT_Anuro.docx (v1.0)"
tags: [anura, cvat, anotación, índice]
---

# Guía CVAT â€” àndice

[[Anura â€” àndice General]]

Manual interno de anotación del equipo Anura (v1.0), convertido desde el documento original de Word con sus 44 figuras. **Es la especificación vigente de anotación**, y sustituye al esquema previo en Roboflow ([[Guía de Anotación Roboflow (histórico)]]).

> [!abstract] Qué enseña esta guía
> A segmentar cada individuo fotografiado en sus partes anatómicas y describir cada parte con atributos estandarizados, para que el modelo aprenda a identificar como lo haría un herpetólogo â€”mirando caracteres concretosâ€” en vez de memorizar la imagen completa.

## Secciones

| # | Nota | Contenido |
| --- | --- | --- |
| 01 | [[01 Introducción y Objetivo del Proyecto]] | Por qué se anota así y por qué importa la consistencia |
| 02 | [[02 Primeros Pasos en CVAT]] | Cuenta, organización, pods, proyecto, 16 etiquetas, tareas y jobs |
| 03 | [[03 Jerarquía y Orden de Etiquetado]] | En qué orden se anota cada parte |
| 04 | [[04 Estándares Generales (anuro_completo)]] | especie · vista · calidad_enfoque · postura · estadio · sexo_aparente |
| 05 | [[05 Guía por Etiqueta â€” Las 16 Etiquetas]] | Cada etiqueta con su criterio y su antecedente biológico |
| 06 | [[06 Flujo de Trabajo Operativo]] | Fases 0 a 6 de una sesión de anotación |
| 07 | [[07 Reglas Generales de Calidad]] | Qué hace válida una anotación |
| 08 | [[08 Glosario de Términos Anatómicos]] | Vocabulario herpetológico necesario |
| 09 | [[09 Anexo A â€” JSON de Configuración CVAT]] | Configuración *raw* de las etiquetas |
| 10 | [[10 Anexo B â€” Capturas de Pantalla]] | Estado de las figuras |
| 11 | [[11 Anexo C â€” Fichas de Especie]] | Caracteres fijos por especie (3 niveles) |

## Las 16 etiquetas

`anuro_completo` · `cabeza` · `hocico` · `ojo` · `timpano` · `dorso_flancos` · `vientre` · `ingle_muslo` · `glandulas_pliegues` · `saco_vocal` · `extremidad_anterior` · `extremidad_posterior` · `tuberculo_metatarsal` · `dedos` · `palmeadura` · `region_cloacal`

## Las tres reglas que más importan

1. **Etiquetar solo lo observable.** Si una pata está tapada por una hoja, se etiqueta la superficie visible y nunca se adivina la forma oculta.
2. **No observable â‰  ausente.** Que no se vea la palmeadura no significa que la rana no la tenga. La distinción recorre todo el sistema, desde la anotación hasta la explicación que ve el usuario ([[Pipeline del Sistema]] §2).
3. **La consistencia entre anotadores es el dato.** Dos personas usando criterios distintos para el mismo carácter no se compensan estadísticamente: el modelo aprende esa ambigüedad como si fuera señal real.

## El Anexo C y la explicabilidad

Las fichas de especie del [[11 Anexo C â€” Fichas de Especie|Anexo C]] no son solo una ayuda para el anotador. Son la **base de conocimiento taxonómico** contra la que el sistema compara lo que observa, y lo que permite responder *por qué* identificó una especie y no otra ([[Pipeline del Sistema]] §2, RF-06, HU-03).

Su estructura de tres niveles â€”siempre fijo / típico pero confirmable / evaluable por imagenâ€” es lo que evita tanto adivinar como reevaluar en cada foto lo que ya se sabe de la especie.

## Relación con el resto del proyecto

| Esta guía alimenta aâ€¦ | Cómo |
| --- | --- |
| [[Estrategia de Construcción del Dataset]] | Define qué se anota y con qué criterios de calidad |
| [[Pipeline del Sistema]] | Las 16 regiones son la salida del modelo de segmentación |
| [[Modelo de Visión â€” BioCLIP]] | El recorte de `anuro_completo` es la entrada al extractor visual |
| [[Historias de Usuario]] | HU-03: el herpetólogo refuta señalando la región concreta |



