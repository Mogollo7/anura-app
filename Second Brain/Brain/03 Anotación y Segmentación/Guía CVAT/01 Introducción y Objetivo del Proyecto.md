---
title: "Introducción y Objetivo del Proyecto"
tipo: guía
proyecto: Anura
fuente: "Guia_CVAT_Anuro.docx (v1.0)"
tags: [anura, cvat, anotación, segmentación]
---

# Introducción y Objetivo del Proyecto

[[Guía CVAT â€” àndice]] · [[02 Primeros Pasos en CVAT]] â†’

![[cvat-01.png]]

**ANURO**

*Identificación herpetológica asistida por IA*

**Guía para el Uso de CVAT**

Clasificación de individuos basada en morfología


> [!note] Manual interno de anotación · Equipo Anuro
> Versión 1.0 · Corporación Universitaria Lasallista

El proyecto Anuro desarrolla una aplicación móvil capaz de identificar especies de anuros (ranas y sapos) a partir de una fotografía. Para lograrlo, el equipo no entrena un clasificador de "caja negra" convencional: se busca abrir esa caja negra y construir un modelo de pensamiento herpetológico, es decir, un sistema que reconozca la especie de la misma forma en que lo haría un herpetólogo â€” observando y comparando partes anatómicas específicas (hocico, ojo, tímpano, patrón dorsal, palmeadura, etc.) en vez de memorizar la imagen completa.

Este esquema de anotación en CVAT es la pieza que hace eso posible: cada individuo fotografiado se segmenta en sus partes anatómicas y cada parte se describe con atributos estandarizados (forma, color, patrón, proporción). Ese conjunto de datos estructurado entrena, junto con BioClip, un modelo capaz no solo de decir "esta rana es Dendropsophus" sino de explicarle al usuario por qué â€” señalando qué combinación de rasgos morfológicos llevó a esa conclusión.


> [!note] Por qué importa la consistencia del etiquetado
> Cada persona que anota imágenes le está enseñando a la IA qué mirar. Un criterio inconsistente entre anotadores (p. ej. dos personas usando "ocular" una "hocico redondeado" y otra "hocico truncado" para la misma rana) no se cancela estadísticamente: se convierte en ruido que el modelo aprende como si fuera señal real. Esta guía existe para eliminar esa ambigüedad antes de que llegue al dataset.


### A quién va dirigida esta guía

A cualquier integrante del equipo que vaya a anotar imágenes en CVAT, sin necesidad de experiencia previa en herpetología ni en la herramienta. La guía cubre desde crear la cuenta hasta el criterio exacto para decidir entre "redondeado" y "truncado" en un hocico dudoso.


### Cómo está organizada

- Sección 1 â€” Primeros pasos en CVAT: cuenta, organización, equipo, proyecto y tareas.

- Sección 2 â€” Jerarquía de etiquetado: en qué orden se anota cada parte.

- Sección 3 â€” Estándares generales: qué se considera cada valor de vista, postura, estadio y sexo aparente.

- Sección 4 â€” Guía por etiqueta: las 16 etiquetas del esquema, una por una, con criterio de identificación y antecedente biológico.

- Sección 5 â€” Flujo de trabajo operativo por fases.

- Sección 6 â€” Reglas generales de calidad.

- Anexo A â€” Enlace de descarga del JSON de configuración (Raw) para pegar en CVAT.

- Anexo B â€” Estado de las capturas de pantalla.

- Anexo C â€” Fichas de especie: características morfológicas fijas por especie.



