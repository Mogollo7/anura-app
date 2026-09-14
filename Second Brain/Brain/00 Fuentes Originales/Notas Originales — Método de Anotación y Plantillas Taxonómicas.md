---
title: "Notas Originales â€” Método de Anotación y Plantillas Taxonómicas"
proyecto: Anura
tipo: fuente-original
descripcion: "Notas de trabajo originales: separación entre segmentación universal, extractor de atributos y plantillas taxonómicas por especie."
tags: [anura, fuente-original, notas]
---

nota dice roboflow érp todo quedo para cvat esta es la porpiesta en la guia cvat quedo todo lo final 



Sí. Te lo dejaría como un método completo y ordenado para Anura, separando claramente lo que se entrena en Roboflow de lo que se construye como conocimiento mediante plantillas.

1. Objetivo general

El sistema tendrá un modelo universal de segmentación anatómica de anuros.

Su función no será identificar especies, sino responder:

> ¿Dónde están las regiones anatómicas de la rana?

Después, otro sistema utilizará esas regiones para obtener características morfológicas y compararlas con las plantillas de las especies.

Imagen
  â†“
Segmentación universal
  â†“
Regiones anatómicas
  â†“
Características morfológicas
  â†“
BioCLIP + base vectorial
  +
Plantilla taxonómica
  â†“
Identificación + explicación

---

2. Entrenamiento en Roboflow

Dataset

Utilizas individuos de tus 23 especies, pero las especies no son las clases del segmentador.

Como objetivo:

20 individuos/especie: mínimo

30 individuos/especie: recomendado

40+ individuos/especie: excelente

Con 30:

23 à— 30 = 690 individuos.

Cada individuo puede tener varias fotografías.

Muy importante

Todas las fotografías del mismo individuo deben permanecer en el mismo conjunto:

IND_001
 â”œâ”€â”€ dorsal
 â”œâ”€â”€ lateral
 â””â”€â”€ ventral

No:

dorsal â†’ train
lateral â†’ test

porque produciría fuga de información.

---

3. Clases de segmentación

No utilizaría las 18 regiones originales como 18 clases obligatorias.

Para una primera versión universal utilizaría aproximadamente:

Regiones principales

1. Anuro / rana completa
2. Cabeza
3. Hocico
4. Ojos
5. Región timpánica
6. Dorso y flancos
7. Vientre
8. Glándulas y pliegues
9. Extremidades anteriores
10. Extremidades posteriores
11. Dedos
12. Palmeadura
13. Región cloacal

Algunas pueden posteriormente dividirse en subregiones.

Por ejemplo:

Extremidad posterior
â”œâ”€â”€ pie
â”œâ”€â”€ dedos
â”œâ”€â”€ palmeadura
â”œâ”€â”€ tubérculos
â””â”€â”€ tarso/talón

Pero no necesitas convertir cada detalle en una clase desde el principio.

---

4. ¿Qué haces con cada fotografía?

En Roboflow dibujas máscaras, no simplemente cajas.

Ejemplo:

Fotografía
   â†“
Máscara ANURO
   â†“
Máscara CABEZA
   â†“
Máscara OJOS
   â†“
Máscara TàMPANO
   â†“
Máscara DORSO
   â†“
Máscara EXTREMIDADES

Solo etiquetas lo que realmente es observable.

Si el vientre no aparece:

vientre = no observable

No significa:

vientre = ausente

---

5. Estrategia de entrenamiento

No empezaría anotando las 1.800 imágenes manualmente.

Haría:

400â€“600 imágenes
        â†“
Anotación manual de alta calidad
        â†“
Entrenamiento V1
        â†“
Evaluación
        â†“
Preanotación del resto
        â†“
Corrección manual
        â†“
Dataset V2
        â†“
Entrenamiento final

Esto reduce muchísimo el trabajo.

Además, seleccionaría imágenes de diferentes:

especies

individuos

familias/géneros

vistas

tamaños

fondos

iluminaciones

posiciones

condiciones de fotografía

Porque quieres que sea un segmentador universal de anuros, no un segmentador especializado en tus 23 especies.

---

6. ¿Dónde entran los atributos?

Aquí está la separación fundamental:

Roboflow aprende:

> Dónde está el ojo.

Modelo de atributos aprende:

> Cómo es ese ojo.

Por ejemplo:

OJO
 â†“
orientación
forma
color
tamaño relativo

Y:

PALMEADURA
 â†“
presencia
grado
extensión

No convertiría:

ojo_vertical
ojo_horizontal
ojo_azul

en clases de segmentación.

---

7. Las plantillas

Las plantillas no se entrenan en Roboflow.

Son una base de conocimiento estructurada para cada especie.

Por ejemplo:

ESPECIE X

Cabeza
 â”œâ”€â”€ hocico: redondeado
 â”œâ”€â”€ ojos: orientación horizontal
 â””â”€â”€ tímpano: visible

Piel
 â”œâ”€â”€ textura: lisa
 â”œâ”€â”€ color: verde
 â””â”€â”€ azul brillante: presente

Extremidades
 â”œâ”€â”€ dedos: ...
 â””â”€â”€ palmeadura: alta

Glándulas
 â””â”€â”€ presentes

Estos valores deben provenir de fuentes taxonómicas confiables, no de una estimación inventada por el modelo.

---

8. Cada característica debe tener información adicional

Por ejemplo:

característica:
  ojos.orientacion

valor esperado:
  horizontal

importancia:
  alta

variabilidad:
  baja

fuente:
  literatura taxonómica

Esto permite diferenciar características muy diagnósticas de características variables.

---

9. La comparación con la plantilla

El sistema obtiene:

FOTOGRAFàA
   â†“
Segmentación
   â†“
Ojos
   â†“
orientación = vertical

La plantilla dice:

Especie X
ojos.orientación = horizontal

Entonces:

âŒ Contradicción

Pero si la región no es visible:

ojos â†’ no observable

el resultado es:

â“ No evaluable

No debe considerarse una contradicción.

---

10. Tres/cuatro tipos de evidencia

Para cada característica:

âœ… Compatible

La observación coincide con la plantilla.

âŒ Contradictoria

La observación es incompatible.

â“ No observable

La fotografía no permite evaluarla.

âš ï¸ Variable

La característica puede variar dentro de la especie y, por tanto, tiene poco peso como contradicción.

Esto es especialmente importante para coloración, porque iluminación, edad, sexo, estado reproductivo y otros factores pueden modificar la apariencia.

---

11. Resultado final

Supongamos que BioCLIP produce:

Boana X â†’ 87%
Boana Y â†’ 8%
Otra â†’ 5%

La plantilla añade:

Boana X

âœ“ Tímpano compatible
âœ“ Hocico compatible
âœ“ Palmeadura compatible
âŒ Orientación ocular incompatible
? Región cloacal no observable

Entonces Anura podría presentar:

> Boana X â€” 87%

Evidencia compatible: tímpano, hocico y palmeadura.

Evidencia contradictoria: orientación de los ojos.

No evaluable: región cloacal.

Así no dependes àºnicamente de la probabilidad de BioCLIP.

---

12. Arquitectura completa

ðŸ“· IMAGEN
                         â”‚
                         â–¼
              SEGMENTADOR UNIVERSAL
                         â”‚
                         â–¼
                REGIONES ANATà“MICAS
                         â”‚
                         â–¼
               EXTRACTOR DE ATRIBUTOS
                         â”‚
              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
              â–¼                     â–¼
           BioCLIP              PLANTILLA
              â”‚                     â”‚
              â–¼                     â–¼
       Embedding visual       Evidencia anatómica
              â”‚                     â”‚
              â–¼                     â”‚
       Base vectorial               â”‚
              â”‚                     â”‚
              â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                         â–¼
                  FUSIà“N DE EVIDENCIA
                         â”‚
                         â–¼
             Familia â†’ Género â†’ Especie
                         â”‚
                         â–¼
                   EXPLICACIà“N

13. Y cuando agregues una especie nueva

Esta es la ventaja principal de todo el diseño:

ESPECIE 24
   â”‚
   â”œâ”€â”€ Imágenes
   â”œâ”€â”€ Embeddings
   â””â”€â”€ Plantilla morfológica
             â”‚
             â–¼
        Base vectorial

No tienes que crear otro segmentador.

El segmentador continàºa siendo:

> "universal para anuros".

La nueva especie solamente necesita incorporarse al conocimiento taxonómico y al sistema de identificación.

En una frase

**Roboflow aprende la anatomía; el modelo de atributos aprende las características; BioCLIP aprende la representación visual; la base vectorial aporta memoria de ejemplares; y las plantillas aportan conocimiento taxonómico explícito para explicar y verificar la predicción.**



