---
title: "Notas Originales â€” MÃ©todo de AnotaciÃ³n y Plantillas TaxonÃ³micas"
proyecto: Anura
tipo: fuente-original
descripcion: "Notas de trabajo originales: separaciÃ³n entre segmentaciÃ³n universal, extractor de atributos y plantillas taxonÃ³micas por especie."
tags: [anura, fuente-original, notas]
---

nota dice roboflow Ã©rp todo quedo para cvat esta es la porpiesta en la guia cvat quedo todo lo final 



SÃ­. Te lo dejarÃ­a como un mÃ©todo completo y ordenado para Anura, separando claramente lo que se entrena en Roboflow de lo que se construye como conocimiento mediante plantillas.

1. Objetivo general

El sistema tendrÃ¡ un modelo universal de segmentaciÃ³n anatÃ³mica de anuros.

Su funciÃ³n no serÃ¡ identificar especies, sino responder:

> Â¿DÃ³nde estÃ¡n las regiones anatÃ³micas de la rana?

DespuÃ©s, otro sistema utilizarÃ¡ esas regiones para obtener caracterÃ­sticas morfolÃ³gicas y compararlas con las plantillas de las especies.

Imagen
  â†“
SegmentaciÃ³n universal
  â†“
Regiones anatÃ³micas
  â†“
CaracterÃ­sticas morfolÃ³gicas
  â†“
BioCLIP + base vectorial
  +
Plantilla taxonÃ³mica
  â†“
IdentificaciÃ³n + explicaciÃ³n

---

2. Entrenamiento en Roboflow

Dataset

Utilizas individuos de tus 23 especies, pero las especies no son las clases del segmentador.

Como objetivo:

20 individuos/especie: mÃ­nimo

30 individuos/especie: recomendado

40+ individuos/especie: excelente

Con 30:

23 Ã— 30 = 690 individuos.

Cada individuo puede tener varias fotografÃ­as.

Muy importante

Todas las fotografÃ­as del mismo individuo deben permanecer en el mismo conjunto:

IND_001
 â”œâ”€â”€ dorsal
 â”œâ”€â”€ lateral
 â””â”€â”€ ventral

No:

dorsal â†’ train
lateral â†’ test

porque producirÃ­a fuga de informaciÃ³n.

---

3. Clases de segmentaciÃ³n

No utilizarÃ­a las 18 regiones originales como 18 clases obligatorias.

Para una primera versiÃ³n universal utilizarÃ­a aproximadamente:

Regiones principales

1. Anuro / rana completa
2. Cabeza
3. Hocico
4. Ojos
5. RegiÃ³n timpÃ¡nica
6. Dorso y flancos
7. Vientre
8. GlÃ¡ndulas y pliegues
9. Extremidades anteriores
10. Extremidades posteriores
11. Dedos
12. Palmeadura
13. RegiÃ³n cloacal

Algunas pueden posteriormente dividirse en subregiones.

Por ejemplo:

Extremidad posterior
â”œâ”€â”€ pie
â”œâ”€â”€ dedos
â”œâ”€â”€ palmeadura
â”œâ”€â”€ tubÃ©rculos
â””â”€â”€ tarso/talÃ³n

Pero no necesitas convertir cada detalle en una clase desde el principio.

---

4. Â¿QuÃ© haces con cada fotografÃ­a?

En Roboflow dibujas mÃ¡scaras, no simplemente cajas.

Ejemplo:

FotografÃ­a
   â†“
MÃ¡scara ANURO
   â†“
MÃ¡scara CABEZA
   â†“
MÃ¡scara OJOS
   â†“
MÃ¡scara TÃMPANO
   â†“
MÃ¡scara DORSO
   â†“
MÃ¡scara EXTREMIDADES

Solo etiquetas lo que realmente es observable.

Si el vientre no aparece:

vientre = no observable

No significa:

vientre = ausente

---

5. Estrategia de entrenamiento

No empezarÃ­a anotando las 1.800 imÃ¡genes manualmente.

HarÃ­a:

400â€“600 imÃ¡genes
        â†“
AnotaciÃ³n manual de alta calidad
        â†“
Entrenamiento V1
        â†“
EvaluaciÃ³n
        â†“
PreanotaciÃ³n del resto
        â†“
CorrecciÃ³n manual
        â†“
Dataset V2
        â†“
Entrenamiento final

Esto reduce muchÃ­simo el trabajo.

AdemÃ¡s, seleccionarÃ­a imÃ¡genes de diferentes:

especies

individuos

familias/gÃ©neros

vistas

tamaÃ±os

fondos

iluminaciones

posiciones

condiciones de fotografÃ­a

Porque quieres que sea un segmentador universal de anuros, no un segmentador especializado en tus 23 especies.

---

6. Â¿DÃ³nde entran los atributos?

AquÃ­ estÃ¡ la separaciÃ³n fundamental:

Roboflow aprende:

> DÃ³nde estÃ¡ el ojo.

Modelo de atributos aprende:

> CÃ³mo es ese ojo.

Por ejemplo:

OJO
 â†“
orientaciÃ³n
forma
color
tamaÃ±o relativo

Y:

PALMEADURA
 â†“
presencia
grado
extensiÃ³n

No convertirÃ­a:

ojo_vertical
ojo_horizontal
ojo_azul

en clases de segmentaciÃ³n.

---

7. Las plantillas

Las plantillas no se entrenan en Roboflow.

Son una base de conocimiento estructurada para cada especie.

Por ejemplo:

ESPECIE X

Cabeza
 â”œâ”€â”€ hocico: redondeado
 â”œâ”€â”€ ojos: orientaciÃ³n horizontal
 â””â”€â”€ tÃ­mpano: visible

Piel
 â”œâ”€â”€ textura: lisa
 â”œâ”€â”€ color: verde
 â””â”€â”€ azul brillante: presente

Extremidades
 â”œâ”€â”€ dedos: ...
 â””â”€â”€ palmeadura: alta

GlÃ¡ndulas
 â””â”€â”€ presentes

Estos valores deben provenir de fuentes taxonÃ³micas confiables, no de una estimaciÃ³n inventada por el modelo.

---

8. Cada caracterÃ­stica debe tener informaciÃ³n adicional

Por ejemplo:

caracterÃ­stica:
  ojos.orientacion

valor esperado:
  horizontal

importancia:
  alta

variabilidad:
  baja

fuente:
  literatura taxonÃ³mica

Esto permite diferenciar caracterÃ­sticas muy diagnÃ³sticas de caracterÃ­sticas variables.

---

9. La comparaciÃ³n con la plantilla

El sistema obtiene:

FOTOGRAFÃA
   â†“
SegmentaciÃ³n
   â†“
Ojos
   â†“
orientaciÃ³n = vertical

La plantilla dice:

Especie X
ojos.orientaciÃ³n = horizontal

Entonces:

âŒ ContradicciÃ³n

Pero si la regiÃ³n no es visible:

ojos â†’ no observable

el resultado es:

â“ No evaluable

No debe considerarse una contradicciÃ³n.

---

10. Tres/cuatro tipos de evidencia

Para cada caracterÃ­stica:

âœ… Compatible

La observaciÃ³n coincide con la plantilla.

âŒ Contradictoria

La observaciÃ³n es incompatible.

â“ No observable

La fotografÃ­a no permite evaluarla.

âš ï¸ Variable

La caracterÃ­stica puede variar dentro de la especie y, por tanto, tiene poco peso como contradicciÃ³n.

Esto es especialmente importante para coloraciÃ³n, porque iluminaciÃ³n, edad, sexo, estado reproductivo y otros factores pueden modificar la apariencia.

---

11. Resultado final

Supongamos que BioCLIP produce:

Boana X â†’ 87%
Boana Y â†’ 8%
Otra â†’ 5%

La plantilla aÃ±ade:

Boana X

âœ“ TÃ­mpano compatible
âœ“ Hocico compatible
âœ“ Palmeadura compatible
âŒ OrientaciÃ³n ocular incompatible
? RegiÃ³n cloacal no observable

Entonces Anura podrÃ­a presentar:

> Boana X â€” 87%

Evidencia compatible: tÃ­mpano, hocico y palmeadura.

Evidencia contradictoria: orientaciÃ³n de los ojos.

No evaluable: regiÃ³n cloacal.

AsÃ­ no dependes Ãºnicamente de la probabilidad de BioCLIP.

---

12. Arquitectura completa

ðŸ“· IMAGEN
                         â”‚
                         â–¼
              SEGMENTADOR UNIVERSAL
                         â”‚
                         â–¼
                REGIONES ANATÃ“MICAS
                         â”‚
                         â–¼
               EXTRACTOR DE ATRIBUTOS
                         â”‚
              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
              â–¼                     â–¼
           BioCLIP              PLANTILLA
              â”‚                     â”‚
              â–¼                     â–¼
       Embedding visual       Evidencia anatÃ³mica
              â”‚                     â”‚
              â–¼                     â”‚
       Base vectorial               â”‚
              â”‚                     â”‚
              â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                         â–¼
                  FUSIÃ“N DE EVIDENCIA
                         â”‚
                         â–¼
             Familia â†’ GÃ©nero â†’ Especie
                         â”‚
                         â–¼
                   EXPLICACIÃ“N

13. Y cuando agregues una especie nueva

Esta es la ventaja principal de todo el diseÃ±o:

ESPECIE 24
   â”‚
   â”œâ”€â”€ ImÃ¡genes
   â”œâ”€â”€ Embeddings
   â””â”€â”€ Plantilla morfolÃ³gica
             â”‚
             â–¼
        Base vectorial

No tienes que crear otro segmentador.

El segmentador continÃºa siendo:

> "universal para anuros".

La nueva especie solamente necesita incorporarse al conocimiento taxonÃ³mico y al sistema de identificaciÃ³n.

En una frase

**Roboflow aprende la anatomÃ­a; el modelo de atributos aprende las caracterÃ­sticas; BioCLIP aprende la representaciÃ³n visual; la base vectorial aporta memoria de ejemplares; y las plantillas aportan conocimiento taxonÃ³mico explÃ­cito para explicar y verificar la predicciÃ³n.**



