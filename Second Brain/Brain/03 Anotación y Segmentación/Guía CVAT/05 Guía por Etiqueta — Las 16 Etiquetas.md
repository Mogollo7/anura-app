---
title: "Guía por Etiqueta â€” Las 16 Etiquetas"
tipo: guía
proyecto: Anura
fuente: "Guia_CVAT_Anuro.docx (v1.0)"
tags: [anura, cvat, anotación, segmentación]
---

# Guía por Etiqueta â€” Las 16 Etiquetas

â† [[04 Estándares Generales (anuro_completo)]] · [[Guía CVAT â€” àndice]] · [[06 Flujo de Trabajo Operativo]] â†’

Esta sección documenta cada una de las 16 etiquetas del esquema en el orden de la jerarquía (sección 2). Para cada atributo se explica el antecedente â€” por qué se registra ese rasgo y qué significa en términos herpetológicos â€” y el criterio exacto para elegir cada valor.


### 4.1 anuro_completo

**Tipo de trazo:** Any (caja o polígono) · **Color en CVAT:** #54b49e

**Cómo trazarlo:** Enmarca al individuo completo visible en la imagen, con un bounding box o un polígono si prefieres segmentar el contorno exacto. Es siempre la primera etiqueta que se aplica.


![[cvat-26.png]]
*Figura 4.1 â€” anuro_completo etiquetado: bounding box sobre el individuo completo, con vista, calidad_enfoque y postura configurados en el panel derecho.*


Sus 6 atributos (especie, vista, calidad_enfoque, postura, sexo_aparente, estadio) están documentados en la Sección 3, porque son estándares transversales que aplican a la imagen completa. Recuerda que vista, calidad_enfoque y postura son mutables â€” pueden cambiarse por frame si estás anotando un track de video. Empieza siempre por especie: si la reconoces, el Anexo C te da las características fijas del resto de las etiquetas para esa especie.


### 4.2 cabeza

**Tipo de trazo:** Polígono · **Color en CVAT:** #eb6d5d

**Cómo trazarlo:** Bordea la cabeza desde el borde posterior del tímpano/cuello hasta la punta del hocico.


![[cvat-27.png]]
*Figura 4.2 â€” Segmentación de la cabeza.*


**Atributo: forma_general**

**Antecedente / por qué se registra:** *La proporción ancho/largo de la cabeza y su relación con el cuerpo es un carácter usado en claves taxonómicas para separar familias y géneros (p. ej. cabezas muy anchas en Ceratophryidae vs. estrechas en Craugastoridae).*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| ancha | El ancho de la cabeza es visiblemente mayor a su longitud, o similar al ancho del cuerpo. |
| estrecha | La cabeza es claramente más larga que ancha, de perfil alargado. |
| triangular | Los lados convergen desde la base del cráneo hacia el hocico, formando un contorno en cuña. |
| ovalada | Contorno redondeado sin ángulos marcados; valor por defecto cuando no destaca ninguna de las anteriores. |


### 4.3 hocico

**Tipo de trazo:** Polígono · **Color en CVAT:** #e67e22

**Cómo trazarlo:** Bordea la zona anterior de la cabeza, desde el borde anterior de los ojos hasta la punta del rostro.


![[cvat-28.jpg]]
*Figura 4.3 â€” Clave visual de forma del hocico en vista dorsal: (A) redondeado, (B) puntiagudo, (C) truncado, (D) acuminado.*

![[cvat-29.png]]
*Figura 4.4 â€” Ejemplo de hocico etiquetado en CVAT.*


**Atributo: forma**

**Antecedente / por qué se registra:** *La forma del hocico en vista dorsal y de perfil es uno de los caracteres diagnósticos más usados en claves dicotómicas de anuros, porque varía consistentemente por género y a veces por especie.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| redondeado | Borde anterior suave y semicircular, sin vértices ni ángulos marcados; el contorno del ápice continàºa una curva uniforme. Comàºn en Dendropsophus spp., Rhinella spp. |
| puntiagudo | Termina en un ángulo agudo definido pero corto; los bordes laterales convergen claramente hacia un punto central bien definido, sin proyección alargada. Comàºn en varias especies de Pristimantis. |
| truncado | El extremo anterior es plano o cortado transversalmente (casi recto), formando una línea frontal casi horizontal o vertical en lugar de una curva o punta. Presente en Centrolene spp. y el género Platymantis. |
| acuminado | Extremadamente alargado, terminando en una punta fina y prominente, a veces proyectada en forma de "flecha" o apéndice. Presente en Rhinella rostrata y el grupo Scinax rostratus. |


#### Reglas para evitar dudas

- Prioriza la vista dorsal: si la imagen es dorsal, juzga la convergencia de los bordes laterales hacia el centro.

- Si la vista es lateral, evalàºa el perfil del rostro en vez de la vista superior.

- Si la toma es cenital inclinada y la punta no se distingue con precisión, selecciona la categoría más cercana visualmente y no fuerces una decisión â€” ante duda real, es preferible marcar la imagen para revisión que adivinar.


### 4.4 ojo

**Tipo de trazo:** Polígono · **Color en CVAT:** #f1c40f

**Cómo trazarlo:** Circunscribe todo el globo ocular visible.


![[cvat-30.png]]
*Figura 4.5 â€” Ejemplo de etiquetado del ojo.*


**Atributo: lado**

**Antecedente / por qué se registra:** *El lado del ojo es indispensable para poder comparar rasgos entre individuos y para saber, en vista lateral, cuál ojo corresponde a la estructura anotada.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| izquierdo / derecho | Gira mentalmente hacia el lado al que está mirando la rana (perspectiva del animal, no de la cámara) para determinar el lado. |
| no_determinable | Vista frontal o dorsal donde ambos ojos son simétricos y no hay forma de diferenciarlos sin ambigüedad. |


**Atributo: orientacion**

**Antecedente / por qué se registra:** *La orientación de la pupila (horizontal, vertical u oblicua) se correlaciona fuertemente con el hábito de la especie (diurno/nocturno, terrestre/arborícola) y es un carácter estándar en identificación de campo.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| horizontal | El eje más largo de la pupila es paralelo al plano de la boca. Muy comàºn en Hylidae (p. ej. Dendropsophus), Craugastoridae (Pristimantis) y Bufonidae (Rhinella). |
| vertical | El eje principal de la pupila se extiende de arriba a abajo. Típico de especies nocturnas o arborícolas avanzadas como Phyllomedusidae (Agalychnis, Phyllomedusa). |
| oblicua | La pupila no es totalmente horizontal ni vertical, está inclinada. Presente en algunas Microhylidae o en especímenes fotografiados en ángulo no cenital. |


> [!note] Tip para el anotador
> Si la pupila es una hendidura muy fina (contraída por la luz), determina la orientación siguiendo la dirección de la hendidura, no la forma general del ojo.


**Atributo: forma_pupila**

**Antecedente / por qué se registra:** *La forma de la pupila (más allá de su orientación) ayuda a distinguir géneros con pupilas romboidales o elípticas atípicas.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| redonda / elipsoidal / romboidal | Selecciona segàºn el contorno visible de la pupila con la luz disponible en la foto. |
| no_visible | El brillo, la sombra o el ángulo no permiten distinguir el contorno de la pupila del iris. |


**Atributo: color_iris**

**Antecedente / por qué se registra:** *El color del iris es un carácter de coloración, àºtil sobre todo cuando se combina con otros rasgos (nunca como àºnico criterio de especie).*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| Cualquiera de las 8 opciones | Selecciona el color dominante del iris con buena luz; usa "no_determinable" si el reflejo o la sombra impiden juzgarlo con confianza. |


**Atributo: tamano_relativo**

**Antecedente / por qué se registra:** *El tamaño del ojo respecto a la cabeza es relevante en géneros con ojos proporcionalmente muy grandes (p. ej. Centrolenidae) frente a géneros con ojos pequeños y hábitos fosoriales.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| grande / mediano / pequeño | Compara el diámetro del ojo con el ancho de la cabeza: grande si supera ~1/3 del ancho craneal, pequeño si es notablemente menor a eso, mediano en el rango intermedio. |


### 4.5 timpano

**Tipo de trazo:** Polígono · **Color en CVAT:** #9b59b6

**Cómo trazarlo:** Delimita la membrana timpánica, circular u ovalada, ubicada detrás del ojo.


![[cvat-31.png]]
*Figura 4.6 â€” Ejemplo de etiquetado del tímpano y su relación con el ojo.*


**Atributo: lado**

**Antecedente / por qué se registra:** *Igual que en ojo â€” necesario para trazabilidad anatómica y comparación entre individuos.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| izquierdo / derecho / no_determinable | Mismo criterio que en la etiqueta ojo: perspectiva del animal, no de la cámara. |


**Atributo: visibilidad**

**Antecedente / por qué se registra:** *Si el tímpano está oculto, cualquier atributo que dependa de verlo (tamaño relativo) debe marcarse como no evaluable en vez de forzar una estimación.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| visible | La membrana timpánica se distingue con claridad; puede ser transparente, lisa o con anillo periférico marcado. |
| oculto_pliegue | El tímpano está parcialmente cubierto por un pliegue supratimpánico o por una glándula (p. ej. la parotoide en Rhinella). |
| no_evaluable | Cubierto por completo por vegetación, lodo, sombra fuerte, desenfoque, o el ángulo de la toma no lo muestra. |


**Atributo: tamano_relativo_ojo**

**Antecedente / por qué se registra:** *La proporción tímpano/ojo es uno de los caracteres diagnósticos clásicos en claves de anuros: separa géneros con tímpanos muy prominentes (p. ej. algunas Leptodactylidae) de aquellos con tímpano reducido u oculto.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| mayor | El diámetro del tímpano es visiblemente mayor al diámetro del ojo. |
| igual | Ambos diámetros son aproximadamente equivalentes. |
| menor | El tímpano es claramente más pequeño que el ojo â€” es la relación más comàºn en la mayoría de anuros. |
| no_evaluable | No se puede comparar de forma confiable por oclusión, ángulo o enfoque. |


### 4.6 dorso_flancos

**Tipo de trazo:** Polígono · **Color en CVAT:** #2e7d32

**Cómo trazarlo:** Delimita toda la región dorsal superior y los laterales del cuerpo, excluyendo la cabeza y las extremidades.


![[cvat-32.jpg]]
*Figura 4.8 â€” dorso_flancos etiquetado (color_base: marron_pardo, patron: liso, textura: lisa, linea_vertebral: ausente).*


**Atributo: color_base**

**Antecedente / por qué se registra:** *El color de fondo dorsal es el rasgo de coloración más citado en descripciones de especie, aunque por sí solo nunca es diagnóstico â€” varía con edad, humedad de la piel y estado de estrés del animal.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| 8 opciones de color | Elige el color que domina visualmente la mayor superficie del dorso con buena iluminación; usa "no_determinable" ante sombra fuerte o sobreexposición. |


**Atributo: patron**

**Antecedente / por qué se registra:** *El patrón dorsal (cómo se distribuye el color, no el color en sí) es más estable entre individuos de una misma especie que el color base, por lo que suele tener mayor peso diagnóstico.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| liso | Color uniforme sin marcas secundarias distinguibles. |
| manchado | Manchas discretas, irregulares, dispersas sobre el fondo. |
| rayado | Líneas longitudinales o transversales continuas. |
| granular | Textura de grano fino visible como patrón (no confundir con textura de la piel, ver abajo). |
| verrugoso | Protuberancias o verrugas visibles como parte del patrón de superficie. |
| mixto | Combinación clara de dos o más patrones anteriores (p. ej. rayas + manchas). |


**Atributo: textura**

**Antecedente / por qué se registra:** *La textura de la piel (lisa vs. verrugosa) separa familias completas (p. ej. Bufonidae verrugosa vs. Hylidae generalmente lisa) y es uno de los primeros rasgos que evalàºa un herpetólogo al identificar en campo.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| lisa / granulosa / verrugosa / plegada | Evalàºa el relieve de la piel independientemente del color: lisa sin relieve, granulosa con grano fino uniforme, verrugosa con protuberancias notorias, plegada con pliegues cutáneos evidentes. |


**Atributo: linea_vertebral**

**Antecedente / por qué se registra:** *La presencia de una línea vertebral clara es un carácter polimórfico dentro de varias especies (algunas poblaciones la tienen, otras no) y por eso se registra por separado del patrón general.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| ausente / presente_delgada / presente_ancha | Observa si hay una línea longitudinal centrada en la columna vertebral, y evalàºa su grosor relativo al ancho del dorso. |


### 4.7 vientre

**Tipo de trazo:** Polígono · **Color en CVAT:** #1565c0

**Cómo trazarlo:** Delimita la zona ventral desde la garganta hasta la ingle, sin incluir las patas.


![[cvat-33.png]]
*Figura 4.7 â€” Ejemplo real de vientre etiquetado en CVAT (color_base: blanco_crema, patron: reticulado).*


**Atributo: color_base**

**Antecedente / por qué se registra:** *El color ventral suele ser más estable que el dorsal (menos expuesto a variación por sustrato/camuflaje) y es un carácter frecuente en descripciones taxonómicas, especialmente en géneros con vientres de colores de advertencia (aposemáticos).*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| blanco_crema | Tono pálido, blanquecino o amarillento claro â€” el más comàºn en la mayoría de ranas y sapos. |
| amarillo | Tono amarillo brillante o intenso, a veces limitado a la ingle pero extendido por el vientre. |
| translucido | La piel es tan fina que se distinguen órganos, màºsculos o el saco vitelino â€” típico en algunas especies de vidrio (Centrolenidae). |
| manchado_oscuro | Fondo claro densamente cubierto de melanina en puntos o parches oscuros. |
| azul_turquesa | Azul vibrante, poco comàºn, presente en ciertas especies venenosas o de coloración aposemática. |
| otro | Cualquier color que no encaje en las anteriores (p. ej. rosa, rojo, negro total sin manchas). |
| no_determinable | Foto borrosa, animal muy oscuro o iluminación insuficiente para distinguir el color. |


**Atributo: patron**

**Antecedente / por qué se registra:** *Igual que en dorso, el patrón ventral tiende a ser más consistente intraespecíficamente que el color base, y en varios géneros aposemáticos el patrón ventral es justamente el carácter de advertencia diagnóstico.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| liso | Color uniforme, sin marcas secundarias, puntos ni reticulado. |
| moteado | Pequeñas manchas o puntos dispersos, irregulares y de tamaño reducido. |
| reticulado | Patrón de red o malla: líneas oscuras forman un entramado sobre fondo claro, o viceversa. |
| manchas_grandes | Marcas definidas de gran tamaño, irregulares o redondeadas, que ocupan una porción significativa del vientre. |


### 4.8 ingle_muslo

**Tipo de trazo:** Polígono · **Color en CVAT:** #c2185b

**Cómo trazarlo:** Polígono sobre la zona de unión de la pata trasera con el cuerpo (área axilar interna del muslo).


![[cvat-34.jpg]]
*Figura 4.9a â€” ingle_muslo etiquetado en una especie con la pata extendida y sin color flash (color_patron: liso, color_flash: ausente).*

![[cvat-35.jpg]]
*Figura 4.9b â€” ingle_muslo con la pata recogida: la región no se distingue bien, por eso color_patron queda en no_evaluable.*


**Atributo: color_patron**

**Antecedente / por qué se registra:** *La región inguinal suele quedar oculta en reposo y solo se revela al extender la pata â€” por eso es una de las zonas más subvaloradas en fotografía de campo, pese a ser muy diagnóstica en varias familias (Leptodactylidae, Hylidae, Bufonidae).*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| liso / manchado / marmoreado / reticulado / barreado | Igual criterio visual que en dorso/vientre, aplicado específicamente a la piel de la ingle y cara interna del muslo. |
| no_evaluable | La pata está recogida y la región inguinal no es visible en la foto â€” este es el valor más frecuente en fotos de reposo. |


**Atributo: color_flash**

**Antecedente / por qué se registra:** *El "color flash" inguinal es una estrategia antidepredadora bien documentada: colores brillantes ocultos que se exponen solo al saltar, y que en muchas especies son más diagnósticos que el color dorsal.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| ausente | No hay color contrastante distinto del patrón general del cuerpo. |
| rojo / naranja / amarillo / azul | Color vívido y contrastante claramente distinto del resto del cuerpo, visible en la cara interna del muslo o la ingle. |
| otro | Color flash presente pero que no corresponde a ninguna de las opciones anteriores. |


### 4.9 glandulas_pliegues

**Tipo de trazo:** Polígono · **Color en CVAT:** #16a085

**Cómo trazarlo:** Contornea glándulas específicas (p. ej. parotoides) o pliegues cutáneos, uno por estructura encontrada â€” puedes repetir esta etiqueta varias veces sobre la misma imagen.


![[cvat-36.jpg]]
*Figura 4.10a â€” glandulas_pliegues etiquetada (tipo: dorsolateral, prominencia: moderada).*

![[cvat-37.jpg]]
*Figura 4.10b â€” glándula grande justo detrás del ojo/tímpano de un sapo â€” compara el tamaño con la figura anterior.*

> [!note] Corrección sobre la Figura 4.10b
> En esa captura la glándula se etiquetó como tipo: dorsolateral, pero por su posición (justo detrás del ojo/tímpano, hinchada, de forma triangular) y su tamaño, corresponde a tipo: parotoide segàºn la Sección 4.9 de esta guía. àšsala como ejemplo de tamaño/prominencia, pero al etiquetar tu propia foto de una glándula en esa posición, marca parotoide, no dorsolateral.


**Atributo: tipo**

**Antecedente / por qué se registra:** *Las glándulas y pliegues cutáneos son estructuras de defensa química (parotoides) o caracteres taxonómicos clásicos (crestas dorsolaterales) usados para separar géneros enteros (p. ej. la parotoide prominente es diagnóstica de Rhinella/Bufonidae).*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| parotoide | Glándula grande detrás del ojo/tímpano, típica de sapos verdaderos (Bufonidae). |
| dorsolateral | Glándula alargada a lo largo del costado dorsal, sin formar necesariamente un pliegue elevado continuo. |
| cresta_dorsolateral | Pliegue de piel elevado y continuo que recorre el dorso lateralmente, más definido como relieve que como glándula difusa. |
| pliegue_supratimpanico | Pliegue de piel justo por encima del tímpano; con frecuencia es la estructura que lo cubre parcialmente (ver timpano.visibilidad = oculto_pliegue). |
| inguinal | Glándula en la región de la ingle. |
| femoral | Glándula sobre la cara dorsal o posterior del muslo. |
| otra | Cualquier estructura glandular o pliegue que no corresponda a las anteriores; describe en un comentario de CVAT si es posible. |


**Atributo: prominencia**

**Antecedente / por qué se registra:** *Registrar el grado de desarrollo (no solo presencia/ausencia) permite luego correlacionar tamaño glandular con especie o con estado de alerta del animal.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| ausente / leve / moderada / marcada | Evalàºa qué tanto se eleva o distingue la estructura respecto a la piel circundante: ausente si no hay relieve perceptible, marcada si es claramente prominente al tacto visual. |


### 4.10 saco_vocal

**Tipo de trazo:** Polígono · **Color en CVAT:** #8e44ad

**Cómo trazarlo:** Polígono sobre la región gular (garganta) cuando el saco vocal es visible, inflado o no. Solo aplica cuando la estructura es identificable â€” en la mayoría de fotos no lo será.


![[cvat-38.jpg]]
*Figura 4.11 â€” saco_vocal etiquetado (presencia: presente_no_inflado, posicion: subgular_bilateral).*

> [!note] Cómo reconocer el saco vocal aunque esté desinflado
> Si la piel de la parte del mentón/garganta se ve medio arrugada o con pliegues sueltos, eso es el saco vocal (presente_no_inflado). Si esa zona se ve lisa y tensa igual que el resto de la garganta, no está presente.


**Atributo: presencia**

**Antecedente / por qué se registra:** *El saco vocal es exclusivo de machos en la inmensa mayoría de anuros, por lo que es el carácter más directo para asignar sexo_aparente = macho, y su posición ayuda a separar familias completas.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| ausente | No se observa ninguna estructura gular distendible; también se usa si el sexo del individuo no permite tenerlo (posible hembra) o la garganta no es visible. |
| presente_no_inflado | Se distingue el pliegue o la piel laxa característica del saco vocal en reposo, sin estar inflado. |
| presente_inflado | El saco está visiblemente distendido, generalmente durante el canto. |


**Atributo: posicion**

**Antecedente / por qué se registra:** *La posición del saco vocal (subgular medial, subgular bilateral o lateral) es un carácter taxonómico de peso: por ejemplo, los sacos vocales bilaterales laterales son típicos de ciertas familias tropicales y ausentes en otras.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| subgular_medial | Una sola bolsa centrada bajo la garganta. |
| subgular_bilateral | Dos bolsas simétricas bajo la garganta, separadas por una línea media. |
| lateral | Bolsas ubicadas a los lados de la cabeza, cerca de la comisura de la boca, en vez de centradas en la garganta. |
| no_aplica | Usar junto con presencia = ausente. |


### 4.11 extremidad_anterior

**Tipo de trazo:** Polígono · **Color en CVAT:** #afd68b

**Cómo trazarlo:** Traza el brazo completo desde la inserción axilar hasta la muñeca.


### 4.12 extremidad_posterior

**Tipo de trazo:** Polígono · **Color en CVAT:** #00838f

**Cómo trazarlo:** Traza la pata completa desde la ingle hasta el tobillo.


![[cvat-39.jpg]]
*Figura 4.12 â€” extremidad_anterior (verde) y extremidad_posterior (azul) etiquetadas.*


**Atributo: lado**

**Antecedente / por qué se registra:** *El lado es obligatorio en las 4 extremidades â€” sin él, no es posible distinguir asimetrías individuales (p. ej. una pata regenerada o dañada) de variación real entre especies.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| izquierdo / derecho / no_determinable | Perspectiva del animal, igual que en ojo/tímpano. Si la vista es dorsal y ambas patas del mismo tipo son simétricas y no se puede diferenciar el origen, usa no_determinable solo como àºltimo recurso. |


### 4.13 tuberculo_metatarsal

**Tipo de trazo:** Polígono · **Color en CVAT:** #6d4c41

**Cómo trazarlo:** Polígono pequeño sobre la protuberancia en la base del pie (borde interno del tarso), visible en vista ventral o lateral del pie.


![[cvat-40.jpg]]
*Figura 4.13 â€” tuberculo_metatarsal etiquetado: siempre está en el borde de la pata, como un pequeño saliente.*

> [!note] Dónde buscarlo
> El tubérculo metatarsal siempre está detrás de la pata de la rana (borde interno de la base del pie), como un pequeño bulto sobresaliente â€” no en el centro del pie ni en los dedos.


**Atributo: presencia**

**Antecedente / por qué se registra:** *El tubérculo metatarsal interno es un carácter clásico de claves dicotómicas (muy usado para separar Bufonidae y Leptodactylidae de otras familias) porque se relaciona con hábitos fosoriales â€” sirve para cavar.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| ausente / presente | Busca una protuberancia córnea o carnosa en el borde interno de la base del pie; si no hay relieve distinguible, es ausente. |


**Atributo: forma**

**Antecedente / por qué se registra:** *La forma del tubérculo (comprimido tipo "pala" vs. redondeado) se asocia al grado de especialización fosorial de la especie.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| comprimido / redondeado / no_evaluable | Comprimido si tiene un borde afilado tipo pala (típico de especies excavadoras), redondeado si es una protuberancia roma, no_evaluable si el ángulo o enfoque no lo permiten distinguir. |


### 4.14 dedos

**Tipo de trazo:** Polígono · **Color en CVAT:** #d35400

**Cómo trazarlo:** Un polígono por cada dedo o artejo individual, NO un polígono para toda la mano o pie de una vez. Repite la etiqueta dedos una vez por cada dedo visible, tanto en extremidades delanteras como traseras.


![[cvat-41.jpg]]
*Figura 4.14 â€” cada dedo etiquetado por separado con su propio polígono (aquí, dedos posteriores).*

> [!note] Error comàºn: no agrupes los dedos
> Solo se etiqueta dedo por dedo, nunca la mano o el pie entero como un solo polígono â€” tanto en extremidades traseras como delanteras.


**Atributo: extremidad**

**Antecedente / por qué se registra:** *Separar mano de pie es necesario porque la presencia y tamaño de discos digitales casi siempre difiere entre extremidades anteriores y posteriores dentro del mismo individuo.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| anterior / posterior | Anterior = mano (brazo), posterior = pie (pata trasera). |


**Atributo: presencia_discos**

**Antecedente / por qué se registra:** *Los discos digitales (almohadillas adhesivas en la punta de los dedos) son el carácter que distingue a la mayoría de las ranas arborícolas (Hylidae, Centrolenidae) de las terrestres, y su tamaño se correlaciona con el grado de vida arbórea.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| ausente | La punta del dedo termina en forma cónica simple, sin ensanchamiento. |
| presente_pequeno | Hay un ligero ensanchamiento en la punta, apenas mayor que el ancho del dedo. |
| presente_grande | Disco claramente ensanchado, tipo "ventosa", notoriamente más ancho que el resto del dedo. |


### 4.15 palmeadura

**Tipo de trazo:** Polígono · **Color en CVAT:** #2ecc71

**Cómo trazarlo:** Traza el borde de la membrana interdigital, es decir, la piel que conecta los dedos entre sí.


![[cvat-42.jpg]]
*Figura 4.15 â€” palmeadura etiquetada (extremidad: posterior, grado: ausente). Foto: Elson Meneses-Pelayo.*


**Atributo: extremidad**

**Antecedente / por qué se registra:** *Igual que en dedos: el grado de palmeadura casi siempre difiere entre manos y pies, y es la extremidad posterior la que suele ser diagnóstica (hábito acuático).*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| anterior / posterior | Anterior = mano, posterior = pie. |


**Atributo: grado**

**Antecedente / por qué se registra:** *El grado de palmeadura entre los dedos posteriores es uno de los caracteres más citados para inferir el grado de hábito acuático de una especie: a mayor palmeadura, mayor dependencia del agua para desplazarse.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| ausente | No hay membrana visible entre los dedos; quedan completamente libres. |
| basal | La membrana solo conecta la base de los dedos, dejando la mayor parte de cada dedo libre. |
| parcial | La membrana alcanza aproximadamente hasta la mitad de la longitud de los dedos. |
| completa | La membrana llega casi hasta la punta de los dedos, dejando libre solo el disco o la àºltima falange. |


### 4.16 region_cloacal

**Tipo de trazo:** Polígono · **Color en CVAT:** #048713

**Cómo trazarlo:** Contornea la zona posterior en la unión de las extremidades traseras (área anal).


![[cvat-43.jpg]]
*Figura 4.16 â€” region_cloacal etiquetada, en vista posterior/dorsal entre las dos patas traseras.*


**Atributo: visibilidad**

**Antecedente / por qué se registra:** *Se registra por separado del resto porque en la gran mayoría de fotos de campo esta zona simplemente no es visible, y es más àºtil marcar explícitamente esa ausencia que dejar la etiqueta sin aplicar.*


| **Valor CVAT** | **Criterio de identificación** |
| --- | --- |
| visible / no_observable | Marca visible solo si puedes distinguir con claridad el contorno de la región cloacal; en cualquier otro caso, no_observable. |



