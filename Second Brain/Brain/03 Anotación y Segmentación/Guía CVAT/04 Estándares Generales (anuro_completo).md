---
title: "EstÃ¡ndares Generales (anuro_completo)"
tipo: guÃ­a
proyecto: Anura
fuente: "Guia_CVAT_Anuro.docx (v1.0)"
tags: [anura, cvat, anotaciÃ³n, segmentaciÃ³n]
---

# EstÃ¡ndares Generales (anuro_completo)

â† [[03 JerarquÃ­a y Orden de Etiquetado]] Â· [[GuÃ­a CVAT â€” Ãndice]] Â· [[05 GuÃ­a por Etiqueta â€” Las 16 Etiquetas]] â†’

Estos seis atributos se rellenan sobre el contenedor principal antes de pasar a las partes del cuerpo. Cinco son metadatos de la fotografÃ­a y del individuo (no rasgos taxonÃ³micos, pero condicionan quÃ© otras etiquetas podrÃ¡s completar con confianza); el primero, especie, sÃ­ es taxonÃ³mico y cambia cÃ³mo abordas todo lo demÃ¡s.


### 3.0 especie


> [!note] Mira arriba en la parte superior central de la imagen antes de empezar
> El nombre de la especie no estÃ¡ escrito sobre la foto â€” estÃ¡ en el NOMBRE DEL ARCHIVO, y lo ves en la barra superior central de CVAT cuando abres la imagen (donde dice algo como â€œScinax_ruber_large_7.jpg...â€). Revisa ese nombre ANTES de etiquetar: si reconoces la especie, ve al Anexo C (Fichas de especie) â€” ahÃ­ estÃ¡n las caracterÃ­sticas morfolÃ³gicas que esa especie SIEMPRE tiene, para que no tengas que evaluarlas a ojo en cada foto. Lo que sÃ­ cambia foto a foto (vista, postura, calidad_enfoque, y a veces sexo_aparente/estadio) se sigue decidiendo por imagen, como el resto de esta secciÃ³n explica.

![[cvat-18.jpg]]
*Figura 3.1 â€” El nombre de archivo (con la especie) aparece en la barra superior central de CVAT al abrir la imagen â€” aquÃ­, â€œScinax_ruber_large_7â€.*


Antecedente: registrar la especie como dato estructurado (en vez de dejarla solo en el nombre del archivo o en la memoria del anotador) permite luego cruzar automÃ¡ticamente cada anotaciÃ³n con su ficha de caracterÃ­sticas fijas, y es en sÃ­ mismo el dato que el modelo de identificaciÃ³n necesita como etiqueta de verdad (ground truth).


| **Valor** | **Criterio** |
| --- | --- |
| Nombre de especie (30 opciones) | Usa el nombre que aparece en el archivo. La lista completa de valores vÃ¡lidos y su ficha de caracterÃ­sticas estÃ¡ en el Anexo C. |
| otra_no_listada | El nombre del archivo corresponde a una especie que no estÃ¡ en la lista del Anexo C. |
| no_determinable | El nombre del archivo no indica especie, o es ilegible/genÃ©rico. |


### 3.1 vista

Antecedente: la vista determina quÃ© estructuras diagnÃ³sticas son visibles. Una foto en vista ventral no permite evaluar el patrÃ³n dorsal, y viceversa â€” declarar la vista evita que se etiqueten como â€œno_determinableâ€ estructuras que en realidad no correspondÃ­a observar en ese Ã¡ngulo.


| **Valor** | **Criterio** |
| --- | --- |
| dorsal | CÃ¡mara sobre el animal; se ve la espalda completa (cabeza, dorso, extremidades desde arriba). |
| ventral | Se ve el vientre (el animal estÃ¡ boca arriba o fotografiado desde abajo, p. ej. sobre vidrio). |
| lateral | Perfil del animal; un costado completo visible, el otro oculto. |
| frontal | CÃ¡mara de frente al hocico; ambos ojos y el hocico centrados. |
| detalle_macro | Encuadre muy cerrado sobre una sola estructura (ojo, tÃ­mpano, dedos), sin el cuerpo completo visible. |


### 3.2 calidad_enfoque

Antecedente: el modelo no debe aprender rasgos de una imagen borrosa como si fueran ciertos. Marcar la calidad permite excluir o ponderar imÃ¡genes de baja confianza durante el entrenamiento.


| **Valor** | **Criterio** |
| --- | --- |
| alta | La estructura relevante estÃ¡ nÃ­tida a resoluciÃ³n normal, sin necesidad de zoom mental para distinguir bordes. |
| media | Se distingue la forma general pero los bordes finos (p. ej. borde de la pupila) no son completamente nÃ­tidos. |
| borrosa_parcial | Solo parte de la imagen estÃ¡ enfocada (p. ej. motion blur en las patas) o hay grano/ruido considerable. |


### 3.3 postura

Antecedente: la postura corporal determina quÃ© estructuras quedan expuestas u ocultas en el momento de la toma. Es un criterio fotogrÃ¡fico de triage, no una clasificaciÃ³n de comportamiento â€” su funciÃ³n es avisar de antemano quÃ© tan completa puede ser la anotaciÃ³n del resto del cuerpo en esa imagen.


| **Valor** | **Se considera cuandoâ€¦** |
| --- | --- |
| extendida | Las cuatro extremidades estÃ¡n visibles y no recogidas contra el cuerpo; es la postura de reposo tÃ­pica sobre una percha u hoja. Es la mÃ¡s favorable para etiquetar todas las partes. |
| recogida | Las patas traseras estÃ¡n flexionadas hacia el cuerpo (postura â€œen cuclillasâ€), comÃºn en reposo diurno o camuflaje. Los pies suelen quedar parcialmente ocultos bajo el cuerpo. |
| salto | El cuerpo estÃ¡ en extensiÃ³n dinÃ¡mica, con las patas traseras extendidas hacia atrÃ¡s o en fase de impulso; con frecuencia hay motion blur. |
| parcialmente_oculta | El animal estÃ¡ tapado por vegetaciÃ³n, agua, sustrato o una mano, independientemente de su postura corporal. Tiene prioridad sobre las otras tres cuando la oclusiÃ³n impide ver mÃ¡s del 30% del cuerpo. |


> [!note] Regla de desempate
> Si compiten dos categorÃ­as (p. ej. una rana saltando que ademÃ¡s queda tapada por una hoja), usa parcialmente_oculta si la oclusiÃ³n afecta a mÃ¡s del 30% del cuerpo visible; de lo contrario, describe la postura corporal (salto/recogida/extendida).

![[cvat-19.jpg]]
*Figura 3.2a â€” postura: extendida.*

![[cvat-20.jpg]]
*Figura 3.2b â€” postura: recogida.*

![[cvat-21.jpg]]
*Figura 3.2c â€” postura: salto.*

![[cvat-22.jpg]]
*Figura 3.2d â€” postura: parcialmente_oculta.*


### 3.4 estadio

Antecedente: la coloraciÃ³n, las proporciones corporales y la presencia de caracteres sexuales secundarios cambian sustancialmente con la edad del individuo. Sin este atributo, la variaciÃ³n morfolÃ³gica por desarrollo se mezclarÃ­a con la variaciÃ³n entre especies, contaminando el entrenamiento del modelo.


| **Valor** | **Se considera cuandoâ€¦** |
| --- | --- |
| adulto | El individuo tiene las proporciones corporales definitivas de la especie, sin restos de cola ni membranas branquiales. Puede presentar caracteres sexuales secundarios (saco vocal, callosidades nupciales) segÃºn sexo y Ã©poca. |
| juvenil | Ya completÃ³ la metamorfosis (sin cola ni rasgos larvarios) pero es claramente mÃ¡s pequeÃ±o que un adulto tÃ­pico de esa forma corporal, y no muestra caracteres sexuales secundarios. |
| metamorfo | EstÃ¡ en transiciÃ³n visible de larva a adulto: presenta restos de cola (aunque sea un muÃ±Ã³n) y/o rasgos larvarios residuales. Es la categorÃ­a mÃ¡s ambigua â€” ante la duda, documenta con nota aparte para revisiÃ³n. |


![[cvat-23.jpg]]
*Figura 3.3a â€” estadio: adulto.*

![[cvat-24.jpg]]
*Figura 3.3b â€” estadio: juvenil (pareja adulto/juvenil para comparar tamaÃ±o).*

![[cvat-25.jpg]]
*Figura 3.3c â€” estadio: metamorfo (restos de cola larvaria visibles).*


### 3.5 sexo_aparente

Antecedente: cuando el dimorfismo sexual estÃ¡ presente (tamaÃ±o, color, saco vocal, callosidades), es una fuente real de variaciÃ³n morfolÃ³gica dentro de una misma especie que, sin registrar, podrÃ­a confundirse con variaciÃ³n entre especies.


| **Valor** | **Se considera cuandoâ€¦** |
| --- | --- |
| macho | Es visible al menos un carÃ¡cter sexual secundario: saco vocal, callosidad nupcial en el primer dedo de la mano, o tamaÃ±o corporal notablemente menor que la hembra tÃ­pica de la especie (si se conoce). |
| hembra | Cuerpo de mayor tamaÃ±o relativo, vientre distendido con huevos visibles, y ausencia de saco vocal o callosidades. |
| indeterminado | Valor por defecto: no hay ningÃºn carÃ¡cter sexual visible o diagnosticable en la imagen. Es el valor esperado en la mayorÃ­a de las fotos de campo. |


> [!note] Estas definiciones necesitan validaciÃ³n de un experto
> Las definiciones de postura, estadio y sexo_aparente en esta secciÃ³n son un criterio operativo razonable, pero fueron redactadas sin la revisiÃ³n de un herpetÃ³logo del equipo. Antes de usarlas para etiquetar en serio, pÃ­dele a la persona con mÃ¡s criterio taxonÃ³mico del grupo que las confirme o ajuste â€” un criterio biolÃ³gico mal definido contamina todo el dataset de entrenamiento, y es mucho mÃ¡s barato corregirlo aquÃ­ que reetiquetar cientos de imÃ¡genes despuÃ©s.



