---
title: "GuÃ­a por Etiqueta â€” Las 16 Etiquetas"
tipo: guÃ­a
proyecto: Anura
fuente: "Guia_CVAT_Anuro.docx (v1.0)"
tags: [anura, cvat, anotaciÃ³n, segmentaciÃ³n]
---

# GuÃ­a por Etiqueta â€” Las 16 Etiquetas

â† [[04 EstÃ¡ndares Generales (anuro_completo)]] Â· [[GuÃ­a CVAT â€” Ãndice]] Â· [[06 Flujo de Trabajo Operativo]] â†’

Esta secciÃ³n documenta cada una de las 16 etiquetas del esquema en el orden de la jerarquÃ­a (secciÃ³n 2). Para cada atributo se explica el antecedente â€” por quÃ© se registra ese rasgo y quÃ© significa en tÃ©rminos herpetolÃ³gicos â€” y el criterio exacto para elegir cada valor.


### 4.1 anuro_completo

**Tipo de trazo:** Any (caja o polÃ­gono) Â· **Color en CVAT:** #54b49e

**CÃ³mo trazarlo:** Enmarca al individuo completo visible en la imagen, con un bounding box o un polÃ­gono si prefieres segmentar el contorno exacto. Es siempre la primera etiqueta que se aplica.


![[cvat-26.png]]
*Figura 4.1 â€” anuro_completo etiquetado: bounding box sobre el individuo completo, con vista, calidad_enfoque y postura configurados en el panel derecho.*


Sus 6 atributos (especie, vista, calidad_enfoque, postura, sexo_aparente, estadio) estÃ¡n documentados en la SecciÃ³n 3, porque son estÃ¡ndares transversales que aplican a la imagen completa. Recuerda que vista, calidad_enfoque y postura son mutables â€” pueden cambiarse por frame si estÃ¡s anotando un track de video. Empieza siempre por especie: si la reconoces, el Anexo C te da las caracterÃ­sticas fijas del resto de las etiquetas para esa especie.


### 4.2 cabeza

**Tipo de trazo:** PolÃ­gono Â· **Color en CVAT:** #eb6d5d

**CÃ³mo trazarlo:** Bordea la cabeza desde el borde posterior del tÃ­mpano/cuello hasta la punta del hocico.


![[cvat-27.png]]
*Figura 4.2 â€” SegmentaciÃ³n de la cabeza.*


**Atributo: forma_general**

**Antecedente / por quÃ© se registra:** *La proporciÃ³n ancho/largo de la cabeza y su relaciÃ³n con el cuerpo es un carÃ¡cter usado en claves taxonÃ³micas para separar familias y gÃ©neros (p. ej. cabezas muy anchas en Ceratophryidae vs. estrechas en Craugastoridae).*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| ancha | El ancho de la cabeza es visiblemente mayor a su longitud, o similar al ancho del cuerpo. |
| estrecha | La cabeza es claramente mÃ¡s larga que ancha, de perfil alargado. |
| triangular | Los lados convergen desde la base del crÃ¡neo hacia el hocico, formando un contorno en cuÃ±a. |
| ovalada | Contorno redondeado sin Ã¡ngulos marcados; valor por defecto cuando no destaca ninguna de las anteriores. |


### 4.3 hocico

**Tipo de trazo:** PolÃ­gono Â· **Color en CVAT:** #e67e22

**CÃ³mo trazarlo:** Bordea la zona anterior de la cabeza, desde el borde anterior de los ojos hasta la punta del rostro.


![[cvat-28.jpg]]
*Figura 4.3 â€” Clave visual de forma del hocico en vista dorsal: (A) redondeado, (B) puntiagudo, (C) truncado, (D) acuminado.*

![[cvat-29.png]]
*Figura 4.4 â€” Ejemplo de hocico etiquetado en CVAT.*


**Atributo: forma**

**Antecedente / por quÃ© se registra:** *La forma del hocico en vista dorsal y de perfil es uno de los caracteres diagnÃ³sticos mÃ¡s usados en claves dicotÃ³micas de anuros, porque varÃ­a consistentemente por gÃ©nero y a veces por especie.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| redondeado | Borde anterior suave y semicircular, sin vÃ©rtices ni Ã¡ngulos marcados; el contorno del Ã¡pice continÃºa una curva uniforme. ComÃºn en Dendropsophus spp., Rhinella spp. |
| puntiagudo | Termina en un Ã¡ngulo agudo definido pero corto; los bordes laterales convergen claramente hacia un punto central bien definido, sin proyecciÃ³n alargada. ComÃºn en varias especies de Pristimantis. |
| truncado | El extremo anterior es plano o cortado transversalmente (casi recto), formando una lÃ­nea frontal casi horizontal o vertical en lugar de una curva o punta. Presente en Centrolene spp. y el gÃ©nero Platymantis. |
| acuminado | Extremadamente alargado, terminando en una punta fina y prominente, a veces proyectada en forma de â€œflechaâ€ o apÃ©ndice. Presente en Rhinella rostrata y el grupo Scinax rostratus. |


#### Reglas para evitar dudas

- Prioriza la vista dorsal: si la imagen es dorsal, juzga la convergencia de los bordes laterales hacia el centro.

- Si la vista es lateral, evalÃºa el perfil del rostro en vez de la vista superior.

- Si la toma es cenital inclinada y la punta no se distingue con precisiÃ³n, selecciona la categorÃ­a mÃ¡s cercana visualmente y no fuerces una decisiÃ³n â€” ante duda real, es preferible marcar la imagen para revisiÃ³n que adivinar.


### 4.4 ojo

**Tipo de trazo:** PolÃ­gono Â· **Color en CVAT:** #f1c40f

**CÃ³mo trazarlo:** Circunscribe todo el globo ocular visible.


![[cvat-30.png]]
*Figura 4.5 â€” Ejemplo de etiquetado del ojo.*


**Atributo: lado**

**Antecedente / por quÃ© se registra:** *El lado del ojo es indispensable para poder comparar rasgos entre individuos y para saber, en vista lateral, cuÃ¡l ojo corresponde a la estructura anotada.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| izquierdo / derecho | Gira mentalmente hacia el lado al que estÃ¡ mirando la rana (perspectiva del animal, no de la cÃ¡mara) para determinar el lado. |
| no_determinable | Vista frontal o dorsal donde ambos ojos son simÃ©tricos y no hay forma de diferenciarlos sin ambigÃ¼edad. |


**Atributo: orientacion**

**Antecedente / por quÃ© se registra:** *La orientaciÃ³n de la pupila (horizontal, vertical u oblicua) se correlaciona fuertemente con el hÃ¡bito de la especie (diurno/nocturno, terrestre/arborÃ­cola) y es un carÃ¡cter estÃ¡ndar en identificaciÃ³n de campo.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| horizontal | El eje mÃ¡s largo de la pupila es paralelo al plano de la boca. Muy comÃºn en Hylidae (p. ej. Dendropsophus), Craugastoridae (Pristimantis) y Bufonidae (Rhinella). |
| vertical | El eje principal de la pupila se extiende de arriba a abajo. TÃ­pico de especies nocturnas o arborÃ­colas avanzadas como Phyllomedusidae (Agalychnis, Phyllomedusa). |
| oblicua | La pupila no es totalmente horizontal ni vertical, estÃ¡ inclinada. Presente en algunas Microhylidae o en especÃ­menes fotografiados en Ã¡ngulo no cenital. |


> [!note] Tip para el anotador
> Si la pupila es una hendidura muy fina (contraÃ­da por la luz), determina la orientaciÃ³n siguiendo la direcciÃ³n de la hendidura, no la forma general del ojo.


**Atributo: forma_pupila**

**Antecedente / por quÃ© se registra:** *La forma de la pupila (mÃ¡s allÃ¡ de su orientaciÃ³n) ayuda a distinguir gÃ©neros con pupilas romboidales o elÃ­pticas atÃ­picas.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| redonda / elipsoidal / romboidal | Selecciona segÃºn el contorno visible de la pupila con la luz disponible en la foto. |
| no_visible | El brillo, la sombra o el Ã¡ngulo no permiten distinguir el contorno de la pupila del iris. |


**Atributo: color_iris**

**Antecedente / por quÃ© se registra:** *El color del iris es un carÃ¡cter de coloraciÃ³n, Ãºtil sobre todo cuando se combina con otros rasgos (nunca como Ãºnico criterio de especie).*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| Cualquiera de las 8 opciones | Selecciona el color dominante del iris con buena luz; usa â€œno_determinableâ€ si el reflejo o la sombra impiden juzgarlo con confianza. |


**Atributo: tamano_relativo**

**Antecedente / por quÃ© se registra:** *El tamaÃ±o del ojo respecto a la cabeza es relevante en gÃ©neros con ojos proporcionalmente muy grandes (p. ej. Centrolenidae) frente a gÃ©neros con ojos pequeÃ±os y hÃ¡bitos fosoriales.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| grande / mediano / pequeÃ±o | Compara el diÃ¡metro del ojo con el ancho de la cabeza: grande si supera ~1/3 del ancho craneal, pequeÃ±o si es notablemente menor a eso, mediano en el rango intermedio. |


### 4.5 timpano

**Tipo de trazo:** PolÃ­gono Â· **Color en CVAT:** #9b59b6

**CÃ³mo trazarlo:** Delimita la membrana timpÃ¡nica, circular u ovalada, ubicada detrÃ¡s del ojo.


![[cvat-31.png]]
*Figura 4.6 â€” Ejemplo de etiquetado del tÃ­mpano y su relaciÃ³n con el ojo.*


**Atributo: lado**

**Antecedente / por quÃ© se registra:** *Igual que en ojo â€” necesario para trazabilidad anatÃ³mica y comparaciÃ³n entre individuos.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| izquierdo / derecho / no_determinable | Mismo criterio que en la etiqueta ojo: perspectiva del animal, no de la cÃ¡mara. |


**Atributo: visibilidad**

**Antecedente / por quÃ© se registra:** *Si el tÃ­mpano estÃ¡ oculto, cualquier atributo que dependa de verlo (tamaÃ±o relativo) debe marcarse como no evaluable en vez de forzar una estimaciÃ³n.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| visible | La membrana timpÃ¡nica se distingue con claridad; puede ser transparente, lisa o con anillo perifÃ©rico marcado. |
| oculto_pliegue | El tÃ­mpano estÃ¡ parcialmente cubierto por un pliegue supratimpÃ¡nico o por una glÃ¡ndula (p. ej. la parotoide en Rhinella). |
| no_evaluable | Cubierto por completo por vegetaciÃ³n, lodo, sombra fuerte, desenfoque, o el Ã¡ngulo de la toma no lo muestra. |


**Atributo: tamano_relativo_ojo**

**Antecedente / por quÃ© se registra:** *La proporciÃ³n tÃ­mpano/ojo es uno de los caracteres diagnÃ³sticos clÃ¡sicos en claves de anuros: separa gÃ©neros con tÃ­mpanos muy prominentes (p. ej. algunas Leptodactylidae) de aquellos con tÃ­mpano reducido u oculto.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| mayor | El diÃ¡metro del tÃ­mpano es visiblemente mayor al diÃ¡metro del ojo. |
| igual | Ambos diÃ¡metros son aproximadamente equivalentes. |
| menor | El tÃ­mpano es claramente mÃ¡s pequeÃ±o que el ojo â€” es la relaciÃ³n mÃ¡s comÃºn en la mayorÃ­a de anuros. |
| no_evaluable | No se puede comparar de forma confiable por oclusiÃ³n, Ã¡ngulo o enfoque. |


### 4.6 dorso_flancos

**Tipo de trazo:** PolÃ­gono Â· **Color en CVAT:** #2e7d32

**CÃ³mo trazarlo:** Delimita toda la regiÃ³n dorsal superior y los laterales del cuerpo, excluyendo la cabeza y las extremidades.


![[cvat-32.jpg]]
*Figura 4.8 â€” dorso_flancos etiquetado (color_base: marron_pardo, patron: liso, textura: lisa, linea_vertebral: ausente).*


**Atributo: color_base**

**Antecedente / por quÃ© se registra:** *El color de fondo dorsal es el rasgo de coloraciÃ³n mÃ¡s citado en descripciones de especie, aunque por sÃ­ solo nunca es diagnÃ³stico â€” varÃ­a con edad, humedad de la piel y estado de estrÃ©s del animal.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| 8 opciones de color | Elige el color que domina visualmente la mayor superficie del dorso con buena iluminaciÃ³n; usa â€œno_determinableâ€ ante sombra fuerte o sobreexposiciÃ³n. |


**Atributo: patron**

**Antecedente / por quÃ© se registra:** *El patrÃ³n dorsal (cÃ³mo se distribuye el color, no el color en sÃ­) es mÃ¡s estable entre individuos de una misma especie que el color base, por lo que suele tener mayor peso diagnÃ³stico.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| liso | Color uniforme sin marcas secundarias distinguibles. |
| manchado | Manchas discretas, irregulares, dispersas sobre el fondo. |
| rayado | LÃ­neas longitudinales o transversales continuas. |
| granular | Textura de grano fino visible como patrÃ³n (no confundir con textura de la piel, ver abajo). |
| verrugoso | Protuberancias o verrugas visibles como parte del patrÃ³n de superficie. |
| mixto | CombinaciÃ³n clara de dos o mÃ¡s patrones anteriores (p. ej. rayas + manchas). |


**Atributo: textura**

**Antecedente / por quÃ© se registra:** *La textura de la piel (lisa vs. verrugosa) separa familias completas (p. ej. Bufonidae verrugosa vs. Hylidae generalmente lisa) y es uno de los primeros rasgos que evalÃºa un herpetÃ³logo al identificar en campo.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| lisa / granulosa / verrugosa / plegada | EvalÃºa el relieve de la piel independientemente del color: lisa sin relieve, granulosa con grano fino uniforme, verrugosa con protuberancias notorias, plegada con pliegues cutÃ¡neos evidentes. |


**Atributo: linea_vertebral**

**Antecedente / por quÃ© se registra:** *La presencia de una lÃ­nea vertebral clara es un carÃ¡cter polimÃ³rfico dentro de varias especies (algunas poblaciones la tienen, otras no) y por eso se registra por separado del patrÃ³n general.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| ausente / presente_delgada / presente_ancha | Observa si hay una lÃ­nea longitudinal centrada en la columna vertebral, y evalÃºa su grosor relativo al ancho del dorso. |


### 4.7 vientre

**Tipo de trazo:** PolÃ­gono Â· **Color en CVAT:** #1565c0

**CÃ³mo trazarlo:** Delimita la zona ventral desde la garganta hasta la ingle, sin incluir las patas.


![[cvat-33.png]]
*Figura 4.7 â€” Ejemplo real de vientre etiquetado en CVAT (color_base: blanco_crema, patron: reticulado).*


**Atributo: color_base**

**Antecedente / por quÃ© se registra:** *El color ventral suele ser mÃ¡s estable que el dorsal (menos expuesto a variaciÃ³n por sustrato/camuflaje) y es un carÃ¡cter frecuente en descripciones taxonÃ³micas, especialmente en gÃ©neros con vientres de colores de advertencia (aposemÃ¡ticos).*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| blanco_crema | Tono pÃ¡lido, blanquecino o amarillento claro â€” el mÃ¡s comÃºn en la mayorÃ­a de ranas y sapos. |
| amarillo | Tono amarillo brillante o intenso, a veces limitado a la ingle pero extendido por el vientre. |
| translucido | La piel es tan fina que se distinguen Ã³rganos, mÃºsculos o el saco vitelino â€” tÃ­pico en algunas especies de vidrio (Centrolenidae). |
| manchado_oscuro | Fondo claro densamente cubierto de melanina en puntos o parches oscuros. |
| azul_turquesa | Azul vibrante, poco comÃºn, presente en ciertas especies venenosas o de coloraciÃ³n aposemÃ¡tica. |
| otro | Cualquier color que no encaje en las anteriores (p. ej. rosa, rojo, negro total sin manchas). |
| no_determinable | Foto borrosa, animal muy oscuro o iluminaciÃ³n insuficiente para distinguir el color. |


**Atributo: patron**

**Antecedente / por quÃ© se registra:** *Igual que en dorso, el patrÃ³n ventral tiende a ser mÃ¡s consistente intraespecÃ­ficamente que el color base, y en varios gÃ©neros aposemÃ¡ticos el patrÃ³n ventral es justamente el carÃ¡cter de advertencia diagnÃ³stico.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| liso | Color uniforme, sin marcas secundarias, puntos ni reticulado. |
| moteado | PequeÃ±as manchas o puntos dispersos, irregulares y de tamaÃ±o reducido. |
| reticulado | PatrÃ³n de red o malla: lÃ­neas oscuras forman un entramado sobre fondo claro, o viceversa. |
| manchas_grandes | Marcas definidas de gran tamaÃ±o, irregulares o redondeadas, que ocupan una porciÃ³n significativa del vientre. |


### 4.8 ingle_muslo

**Tipo de trazo:** PolÃ­gono Â· **Color en CVAT:** #c2185b

**CÃ³mo trazarlo:** PolÃ­gono sobre la zona de uniÃ³n de la pata trasera con el cuerpo (Ã¡rea axilar interna del muslo).


![[cvat-34.jpg]]
*Figura 4.9a â€” ingle_muslo etiquetado en una especie con la pata extendida y sin color flash (color_patron: liso, color_flash: ausente).*

![[cvat-35.jpg]]
*Figura 4.9b â€” ingle_muslo con la pata recogida: la regiÃ³n no se distingue bien, por eso color_patron queda en no_evaluable.*


**Atributo: color_patron**

**Antecedente / por quÃ© se registra:** *La regiÃ³n inguinal suele quedar oculta en reposo y solo se revela al extender la pata â€” por eso es una de las zonas mÃ¡s subvaloradas en fotografÃ­a de campo, pese a ser muy diagnÃ³stica en varias familias (Leptodactylidae, Hylidae, Bufonidae).*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| liso / manchado / marmoreado / reticulado / barreado | Igual criterio visual que en dorso/vientre, aplicado especÃ­ficamente a la piel de la ingle y cara interna del muslo. |
| no_evaluable | La pata estÃ¡ recogida y la regiÃ³n inguinal no es visible en la foto â€” este es el valor mÃ¡s frecuente en fotos de reposo. |


**Atributo: color_flash**

**Antecedente / por quÃ© se registra:** *El â€œcolor flashâ€ inguinal es una estrategia antidepredadora bien documentada: colores brillantes ocultos que se exponen solo al saltar, y que en muchas especies son mÃ¡s diagnÃ³sticos que el color dorsal.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| ausente | No hay color contrastante distinto del patrÃ³n general del cuerpo. |
| rojo / naranja / amarillo / azul | Color vÃ­vido y contrastante claramente distinto del resto del cuerpo, visible en la cara interna del muslo o la ingle. |
| otro | Color flash presente pero que no corresponde a ninguna de las opciones anteriores. |


### 4.9 glandulas_pliegues

**Tipo de trazo:** PolÃ­gono Â· **Color en CVAT:** #16a085

**CÃ³mo trazarlo:** Contornea glÃ¡ndulas especÃ­ficas (p. ej. parotoides) o pliegues cutÃ¡neos, uno por estructura encontrada â€” puedes repetir esta etiqueta varias veces sobre la misma imagen.


![[cvat-36.jpg]]
*Figura 4.10a â€” glandulas_pliegues etiquetada (tipo: dorsolateral, prominencia: moderada).*

![[cvat-37.jpg]]
*Figura 4.10b â€” glÃ¡ndula grande justo detrÃ¡s del ojo/tÃ­mpano de un sapo â€” compara el tamaÃ±o con la figura anterior.*

> [!note] CorrecciÃ³n sobre la Figura 4.10b
> En esa captura la glÃ¡ndula se etiquetÃ³ como tipo: dorsolateral, pero por su posiciÃ³n (justo detrÃ¡s del ojo/tÃ­mpano, hinchada, de forma triangular) y su tamaÃ±o, corresponde a tipo: parotoide segÃºn la SecciÃ³n 4.9 de esta guÃ­a. Ãšsala como ejemplo de tamaÃ±o/prominencia, pero al etiquetar tu propia foto de una glÃ¡ndula en esa posiciÃ³n, marca parotoide, no dorsolateral.


**Atributo: tipo**

**Antecedente / por quÃ© se registra:** *Las glÃ¡ndulas y pliegues cutÃ¡neos son estructuras de defensa quÃ­mica (parotoides) o caracteres taxonÃ³micos clÃ¡sicos (crestas dorsolaterales) usados para separar gÃ©neros enteros (p. ej. la parotoide prominente es diagnÃ³stica de Rhinella/Bufonidae).*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| parotoide | GlÃ¡ndula grande detrÃ¡s del ojo/tÃ­mpano, tÃ­pica de sapos verdaderos (Bufonidae). |
| dorsolateral | GlÃ¡ndula alargada a lo largo del costado dorsal, sin formar necesariamente un pliegue elevado continuo. |
| cresta_dorsolateral | Pliegue de piel elevado y continuo que recorre el dorso lateralmente, mÃ¡s definido como relieve que como glÃ¡ndula difusa. |
| pliegue_supratimpanico | Pliegue de piel justo por encima del tÃ­mpano; con frecuencia es la estructura que lo cubre parcialmente (ver timpano.visibilidad = oculto_pliegue). |
| inguinal | GlÃ¡ndula en la regiÃ³n de la ingle. |
| femoral | GlÃ¡ndula sobre la cara dorsal o posterior del muslo. |
| otra | Cualquier estructura glandular o pliegue que no corresponda a las anteriores; describe en un comentario de CVAT si es posible. |


**Atributo: prominencia**

**Antecedente / por quÃ© se registra:** *Registrar el grado de desarrollo (no solo presencia/ausencia) permite luego correlacionar tamaÃ±o glandular con especie o con estado de alerta del animal.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| ausente / leve / moderada / marcada | EvalÃºa quÃ© tanto se eleva o distingue la estructura respecto a la piel circundante: ausente si no hay relieve perceptible, marcada si es claramente prominente al tacto visual. |


### 4.10 saco_vocal

**Tipo de trazo:** PolÃ­gono Â· **Color en CVAT:** #8e44ad

**CÃ³mo trazarlo:** PolÃ­gono sobre la regiÃ³n gular (garganta) cuando el saco vocal es visible, inflado o no. Solo aplica cuando la estructura es identificable â€” en la mayorÃ­a de fotos no lo serÃ¡.


![[cvat-38.jpg]]
*Figura 4.11 â€” saco_vocal etiquetado (presencia: presente_no_inflado, posicion: subgular_bilateral).*

> [!note] CÃ³mo reconocer el saco vocal aunque estÃ© desinflado
> Si la piel de la parte del mentÃ³n/garganta se ve medio arrugada o con pliegues sueltos, eso es el saco vocal (presente_no_inflado). Si esa zona se ve lisa y tensa igual que el resto de la garganta, no estÃ¡ presente.


**Atributo: presencia**

**Antecedente / por quÃ© se registra:** *El saco vocal es exclusivo de machos en la inmensa mayorÃ­a de anuros, por lo que es el carÃ¡cter mÃ¡s directo para asignar sexo_aparente = macho, y su posiciÃ³n ayuda a separar familias completas.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| ausente | No se observa ninguna estructura gular distendible; tambiÃ©n se usa si el sexo del individuo no permite tenerlo (posible hembra) o la garganta no es visible. |
| presente_no_inflado | Se distingue el pliegue o la piel laxa caracterÃ­stica del saco vocal en reposo, sin estar inflado. |
| presente_inflado | El saco estÃ¡ visiblemente distendido, generalmente durante el canto. |


**Atributo: posicion**

**Antecedente / por quÃ© se registra:** *La posiciÃ³n del saco vocal (subgular medial, subgular bilateral o lateral) es un carÃ¡cter taxonÃ³mico de peso: por ejemplo, los sacos vocales bilaterales laterales son tÃ­picos de ciertas familias tropicales y ausentes en otras.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| subgular_medial | Una sola bolsa centrada bajo la garganta. |
| subgular_bilateral | Dos bolsas simÃ©tricas bajo la garganta, separadas por una lÃ­nea media. |
| lateral | Bolsas ubicadas a los lados de la cabeza, cerca de la comisura de la boca, en vez de centradas en la garganta. |
| no_aplica | Usar junto con presencia = ausente. |


### 4.11 extremidad_anterior

**Tipo de trazo:** PolÃ­gono Â· **Color en CVAT:** #afd68b

**CÃ³mo trazarlo:** Traza el brazo completo desde la inserciÃ³n axilar hasta la muÃ±eca.


### 4.12 extremidad_posterior

**Tipo de trazo:** PolÃ­gono Â· **Color en CVAT:** #00838f

**CÃ³mo trazarlo:** Traza la pata completa desde la ingle hasta el tobillo.


![[cvat-39.jpg]]
*Figura 4.12 â€” extremidad_anterior (verde) y extremidad_posterior (azul) etiquetadas.*


**Atributo: lado**

**Antecedente / por quÃ© se registra:** *El lado es obligatorio en las 4 extremidades â€” sin Ã©l, no es posible distinguir asimetrÃ­as individuales (p. ej. una pata regenerada o daÃ±ada) de variaciÃ³n real entre especies.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| izquierdo / derecho / no_determinable | Perspectiva del animal, igual que en ojo/tÃ­mpano. Si la vista es dorsal y ambas patas del mismo tipo son simÃ©tricas y no se puede diferenciar el origen, usa no_determinable solo como Ãºltimo recurso. |


### 4.13 tuberculo_metatarsal

**Tipo de trazo:** PolÃ­gono Â· **Color en CVAT:** #6d4c41

**CÃ³mo trazarlo:** PolÃ­gono pequeÃ±o sobre la protuberancia en la base del pie (borde interno del tarso), visible en vista ventral o lateral del pie.


![[cvat-40.jpg]]
*Figura 4.13 â€” tuberculo_metatarsal etiquetado: siempre estÃ¡ en el borde de la pata, como un pequeÃ±o saliente.*

> [!note] DÃ³nde buscarlo
> El tubÃ©rculo metatarsal siempre estÃ¡ detrÃ¡s de la pata de la rana (borde interno de la base del pie), como un pequeÃ±o bulto sobresaliente â€” no en el centro del pie ni en los dedos.


**Atributo: presencia**

**Antecedente / por quÃ© se registra:** *El tubÃ©rculo metatarsal interno es un carÃ¡cter clÃ¡sico de claves dicotÃ³micas (muy usado para separar Bufonidae y Leptodactylidae de otras familias) porque se relaciona con hÃ¡bitos fosoriales â€” sirve para cavar.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| ausente / presente | Busca una protuberancia cÃ³rnea o carnosa en el borde interno de la base del pie; si no hay relieve distinguible, es ausente. |


**Atributo: forma**

**Antecedente / por quÃ© se registra:** *La forma del tubÃ©rculo (comprimido tipo â€œpalaâ€ vs. redondeado) se asocia al grado de especializaciÃ³n fosorial de la especie.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| comprimido / redondeado / no_evaluable | Comprimido si tiene un borde afilado tipo pala (tÃ­pico de especies excavadoras), redondeado si es una protuberancia roma, no_evaluable si el Ã¡ngulo o enfoque no lo permiten distinguir. |


### 4.14 dedos

**Tipo de trazo:** PolÃ­gono Â· **Color en CVAT:** #d35400

**CÃ³mo trazarlo:** Un polÃ­gono por cada dedo o artejo individual, NO un polÃ­gono para toda la mano o pie de una vez. Repite la etiqueta dedos una vez por cada dedo visible, tanto en extremidades delanteras como traseras.


![[cvat-41.jpg]]
*Figura 4.14 â€” cada dedo etiquetado por separado con su propio polÃ­gono (aquÃ­, dedos posteriores).*

> [!note] Error comÃºn: no agrupes los dedos
> Solo se etiqueta dedo por dedo, nunca la mano o el pie entero como un solo polÃ­gono â€” tanto en extremidades traseras como delanteras.


**Atributo: extremidad**

**Antecedente / por quÃ© se registra:** *Separar mano de pie es necesario porque la presencia y tamaÃ±o de discos digitales casi siempre difiere entre extremidades anteriores y posteriores dentro del mismo individuo.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| anterior / posterior | Anterior = mano (brazo), posterior = pie (pata trasera). |


**Atributo: presencia_discos**

**Antecedente / por quÃ© se registra:** *Los discos digitales (almohadillas adhesivas en la punta de los dedos) son el carÃ¡cter que distingue a la mayorÃ­a de las ranas arborÃ­colas (Hylidae, Centrolenidae) de las terrestres, y su tamaÃ±o se correlaciona con el grado de vida arbÃ³rea.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| ausente | La punta del dedo termina en forma cÃ³nica simple, sin ensanchamiento. |
| presente_pequeno | Hay un ligero ensanchamiento en la punta, apenas mayor que el ancho del dedo. |
| presente_grande | Disco claramente ensanchado, tipo â€œventosaâ€, notoriamente mÃ¡s ancho que el resto del dedo. |


### 4.15 palmeadura

**Tipo de trazo:** PolÃ­gono Â· **Color en CVAT:** #2ecc71

**CÃ³mo trazarlo:** Traza el borde de la membrana interdigital, es decir, la piel que conecta los dedos entre sÃ­.


![[cvat-42.jpg]]
*Figura 4.15 â€” palmeadura etiquetada (extremidad: posterior, grado: ausente). Foto: Elson Meneses-Pelayo.*


**Atributo: extremidad**

**Antecedente / por quÃ© se registra:** *Igual que en dedos: el grado de palmeadura casi siempre difiere entre manos y pies, y es la extremidad posterior la que suele ser diagnÃ³stica (hÃ¡bito acuÃ¡tico).*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| anterior / posterior | Anterior = mano, posterior = pie. |


**Atributo: grado**

**Antecedente / por quÃ© se registra:** *El grado de palmeadura entre los dedos posteriores es uno de los caracteres mÃ¡s citados para inferir el grado de hÃ¡bito acuÃ¡tico de una especie: a mayor palmeadura, mayor dependencia del agua para desplazarse.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| ausente | No hay membrana visible entre los dedos; quedan completamente libres. |
| basal | La membrana solo conecta la base de los dedos, dejando la mayor parte de cada dedo libre. |
| parcial | La membrana alcanza aproximadamente hasta la mitad de la longitud de los dedos. |
| completa | La membrana llega casi hasta la punta de los dedos, dejando libre solo el disco o la Ãºltima falange. |


### 4.16 region_cloacal

**Tipo de trazo:** PolÃ­gono Â· **Color en CVAT:** #048713

**CÃ³mo trazarlo:** Contornea la zona posterior en la uniÃ³n de las extremidades traseras (Ã¡rea anal).


![[cvat-43.jpg]]
*Figura 4.16 â€” region_cloacal etiquetada, en vista posterior/dorsal entre las dos patas traseras.*


**Atributo: visibilidad**

**Antecedente / por quÃ© se registra:** *Se registra por separado del resto porque en la gran mayorÃ­a de fotos de campo esta zona simplemente no es visible, y es mÃ¡s Ãºtil marcar explÃ­citamente esa ausencia que dejar la etiqueta sin aplicar.*


| **Valor CVAT** | **Criterio de identificaciÃ³n** |
| --- | --- |
| visible / no_observable | Marca visible solo si puedes distinguir con claridad el contorno de la regiÃ³n cloacal; en cualquier otro caso, no_observable. |



