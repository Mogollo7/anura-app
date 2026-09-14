---
title: "Estándares Generales (anuro_completo)"
tipo: guía
proyecto: Anura
fuente: "Guia_CVAT_Anuro.docx (v1.0)"
tags: [anura, cvat, anotación, segmentación]
---

# Estándares Generales (anuro_completo)

â† [[03 Jerarquía y Orden de Etiquetado]] · [[Guía CVAT â€” àndice]] · [[05 Guía por Etiqueta â€” Las 16 Etiquetas]] â†’

Estos seis atributos se rellenan sobre el contenedor principal antes de pasar a las partes del cuerpo. Cinco son metadatos de la fotografía y del individuo (no rasgos taxonómicos, pero condicionan qué otras etiquetas podrás completar con confianza); el primero, especie, sí es taxonómico y cambia cómo abordas todo lo demás.


### 3.0 especie


> [!note] Mira arriba en la parte superior central de la imagen antes de empezar
> El nombre de la especie no está escrito sobre la foto â€” está en el NOMBRE DEL ARCHIVO, y lo ves en la barra superior central de CVAT cuando abres la imagen (donde dice algo como "Scinax_ruber_large_7.jpg..."). Revisa ese nombre ANTES de etiquetar: si reconoces la especie, ve al Anexo C (Fichas de especie) â€” ahí están las características morfológicas que esa especie SIEMPRE tiene, para que no tengas que evaluarlas a ojo en cada foto. Lo que sí cambia foto a foto (vista, postura, calidad_enfoque, y a veces sexo_aparente/estadio) se sigue decidiendo por imagen, como el resto de esta sección explica.

![[cvat-18.jpg]]
*Figura 3.1 â€” El nombre de archivo (con la especie) aparece en la barra superior central de CVAT al abrir la imagen â€” aquí, "Scinax_ruber_large_7".*


Antecedente: registrar la especie como dato estructurado (en vez de dejarla solo en el nombre del archivo o en la memoria del anotador) permite luego cruzar automáticamente cada anotación con su ficha de características fijas, y es en sí mismo el dato que el modelo de identificación necesita como etiqueta de verdad (ground truth).


| **Valor** | **Criterio** |
| --- | --- |
| Nombre de especie (30 opciones) | Usa el nombre que aparece en el archivo. La lista completa de valores válidos y su ficha de características está en el Anexo C. |
| otra_no_listada | El nombre del archivo corresponde a una especie que no está en la lista del Anexo C. |
| no_determinable | El nombre del archivo no indica especie, o es ilegible/genérico. |


### 3.1 vista

Antecedente: la vista determina qué estructuras diagnósticas son visibles. Una foto en vista ventral no permite evaluar el patrón dorsal, y viceversa â€” declarar la vista evita que se etiqueten como "no_determinable" estructuras que en realidad no correspondía observar en ese ángulo.


| **Valor** | **Criterio** |
| --- | --- |
| dorsal | Cámara sobre el animal; se ve la espalda completa (cabeza, dorso, extremidades desde arriba). |
| ventral | Se ve el vientre (el animal está boca arriba o fotografiado desde abajo, p. ej. sobre vidrio). |
| lateral | Perfil del animal; un costado completo visible, el otro oculto. |
| frontal | Cámara de frente al hocico; ambos ojos y el hocico centrados. |
| detalle_macro | Encuadre muy cerrado sobre una sola estructura (ojo, tímpano, dedos), sin el cuerpo completo visible. |


### 3.2 calidad_enfoque

Antecedente: el modelo no debe aprender rasgos de una imagen borrosa como si fueran ciertos. Marcar la calidad permite excluir o ponderar imágenes de baja confianza durante el entrenamiento.


| **Valor** | **Criterio** |
| --- | --- |
| alta | La estructura relevante está nítida a resolución normal, sin necesidad de zoom mental para distinguir bordes. |
| media | Se distingue la forma general pero los bordes finos (p. ej. borde de la pupila) no son completamente nítidos. |
| borrosa_parcial | Solo parte de la imagen está enfocada (p. ej. motion blur en las patas) o hay grano/ruido considerable. |


### 3.3 postura

Antecedente: la postura corporal determina qué estructuras quedan expuestas u ocultas en el momento de la toma. Es un criterio fotográfico de triage, no una clasificación de comportamiento â€” su función es avisar de antemano qué tan completa puede ser la anotación del resto del cuerpo en esa imagen.


| **Valor** | **Se considera cuandoâ€¦** |
| --- | --- |
| extendida | Las cuatro extremidades están visibles y no recogidas contra el cuerpo; es la postura de reposo típica sobre una percha u hoja. Es la más favorable para etiquetar todas las partes. |
| recogida | Las patas traseras están flexionadas hacia el cuerpo (postura "en cuclillas"), comàºn en reposo diurno o camuflaje. Los pies suelen quedar parcialmente ocultos bajo el cuerpo. |
| salto | El cuerpo está en extensión dinámica, con las patas traseras extendidas hacia atrás o en fase de impulso; con frecuencia hay motion blur. |
| parcialmente_oculta | El animal está tapado por vegetación, agua, sustrato o una mano, independientemente de su postura corporal. Tiene prioridad sobre las otras tres cuando la oclusión impide ver más del 30% del cuerpo. |


> [!note] Regla de desempate
> Si compiten dos categorías (p. ej. una rana saltando que además queda tapada por una hoja), usa parcialmente_oculta si la oclusión afecta a más del 30% del cuerpo visible; de lo contrario, describe la postura corporal (salto/recogida/extendida).

![[cvat-19.jpg]]
*Figura 3.2a â€” postura: extendida.*

![[cvat-20.jpg]]
*Figura 3.2b â€” postura: recogida.*

![[cvat-21.jpg]]
*Figura 3.2c â€” postura: salto.*

![[cvat-22.jpg]]
*Figura 3.2d â€” postura: parcialmente_oculta.*


### 3.4 estadio

Antecedente: la coloración, las proporciones corporales y la presencia de caracteres sexuales secundarios cambian sustancialmente con la edad del individuo. Sin este atributo, la variación morfológica por desarrollo se mezclaría con la variación entre especies, contaminando el entrenamiento del modelo.


| **Valor** | **Se considera cuandoâ€¦** |
| --- | --- |
| adulto | El individuo tiene las proporciones corporales definitivas de la especie, sin restos de cola ni membranas branquiales. Puede presentar caracteres sexuales secundarios (saco vocal, callosidades nupciales) segàºn sexo y época. |
| juvenil | Ya completó la metamorfosis (sin cola ni rasgos larvarios) pero es claramente más pequeño que un adulto típico de esa forma corporal, y no muestra caracteres sexuales secundarios. |
| metamorfo | Está en transición visible de larva a adulto: presenta restos de cola (aunque sea un muñón) y/o rasgos larvarios residuales. Es la categoría más ambigua â€” ante la duda, documenta con nota aparte para revisión. |


![[cvat-23.jpg]]
*Figura 3.3a â€” estadio: adulto.*

![[cvat-24.jpg]]
*Figura 3.3b â€” estadio: juvenil (pareja adulto/juvenil para comparar tamaño).*

![[cvat-25.jpg]]
*Figura 3.3c â€” estadio: metamorfo (restos de cola larvaria visibles).*


### 3.5 sexo_aparente

Antecedente: cuando el dimorfismo sexual está presente (tamaño, color, saco vocal, callosidades), es una fuente real de variación morfológica dentro de una misma especie que, sin registrar, podría confundirse con variación entre especies.


| **Valor** | **Se considera cuandoâ€¦** |
| --- | --- |
| macho | Es visible al menos un carácter sexual secundario: saco vocal, callosidad nupcial en el primer dedo de la mano, o tamaño corporal notablemente menor que la hembra típica de la especie (si se conoce). |
| hembra | Cuerpo de mayor tamaño relativo, vientre distendido con huevos visibles, y ausencia de saco vocal o callosidades. |
| indeterminado | Valor por defecto: no hay ningàºn carácter sexual visible o diagnosticable en la imagen. Es el valor esperado en la mayoría de las fotos de campo. |


> [!note] Estas definiciones necesitan validación de un experto
> Las definiciones de postura, estadio y sexo_aparente en esta sección son un criterio operativo razonable, pero fueron redactadas sin la revisión de un herpetólogo del equipo. Antes de usarlas para etiquetar en serio, pídele a la persona con más criterio taxonómico del grupo que las confirme o ajuste â€” un criterio biológico mal definido contamina todo el dataset de entrenamiento, y es mucho más barato corregirlo aquí que reetiquetar cientos de imágenes después.



