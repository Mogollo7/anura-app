---
title: "Anexo C â€” Fichas de Especie"
tipo: guÃ­a
proyecto: Anura
fuente: "Guia_CVAT_Anuro.docx (v1.0)"
tags: [anura, cvat, anotaciÃ³n, segmentaciÃ³n]
---

# Anexo C â€” Fichas de Especie

â† [[10 Anexo B â€” Capturas de Pantalla]] Â· [[GuÃ­a CVAT â€” Ãndice]]

El nombre de la especie estÃ¡ en el nombre del archivo, visible en la barra superior central de CVAT al abrir la imagen (ver Figura 3.1, SecciÃ³n 3.0). Cuando reconozcas ese nombre, no necesitas evaluar a ojo cada atributo de esa foto: varios de ellos son diagnÃ³sticos de la especie y prÃ¡cticamente siempre tienen el mismo valor. Otros, en cambio, dependen de la foto concreta (el Ã¡ngulo, la postura, si el individuo es joven o adulto) y deben seguir juzgÃ¡ndose imagen por imagen, sin importar quÃ© tan bien conozcas la especie.


> [!note] Por quÃ© esta secciÃ³n solo tiene una ficha completa por ahora
> Le pedÃ­ al equipo un ejemplo de referencia (Rhinella horribilis) y lo usÃ© para construir la plantilla de abajo â€” la separaciÃ³n en tres niveles (siempre fijo / tÃ­pico pero revisa la foto / siempre por imagen) sale de ese ejemplo. Para las otras 29 especies de la lista NO inventÃ© caracterÃ­sticas a partir de lo que "recuerdo" sobre cada una: con solo el nombre no tengo forma de garantizar que un rasgo diagnÃ³stico que recito de memoria sea correcto para esa especie puntual, y una ficha de especie mal hecha es peor que no tener ficha â€” el anotador la usarÃ­a para fijar valores en decenas de fotos sin volver a mirar la imagen. Al final de esta secciÃ³n te pregunto cÃ³mo quieres completarlas.


### C.1 Ficha completa â€” Rhinella horribilis (especie de referencia)

Familia Bufonidae. Esta ficha fue construida a partir de la descripciÃ³n que el equipo aportÃ³ para esta especie, reorganizada en el formato de tres niveles que usarÃ¡n las demÃ¡s fichas.


#### Nivel 1 â€” Siempre fijo para esta especie (no lo evalÃºes, ya lo sabes)


| **Etiqueta.atributo** | **Valor fijo** | **Por quÃ© es fijo** |
| --- | --- | --- |
| anuro_completo.especie | rhinella_horribilis | Es el dato que define toda la ficha; se fija leyendo el nombre del archivo en la barra superior de CVAT. |
| hocico.canto_rostral | definido | Rhinella horribilis tiene crestas Ã³seas cefÃ¡licas (canto rostral, supraorbitarias, parietales) bien desarrolladas â€” es un rasgo esquelÃ©tico, no cambia entre individuos. |
| timpano.tamano_relativo_ojo | menor | El tÃ­mpano es proporcionalmente menor que el ojo en toda la especie. |
| glandulas_pliegues.tipo | parotoide | El rasgo diagnÃ³stico de la especie: glÃ¡ndulas parotoides enormes, triangulares, es lo primero que separa a Rhinella de otros gÃ©neros en campo. |
| glandulas_pliegues.prominencia | marcada | Consistente con lo anterior â€” son de las parotoides mÃ¡s grandes y evidentes entre los anuros del dataset. |
| palmeadura (extremidad: anterior).grado | ausente | Los sapos del gÃ©nero Rhinella son terrestres; las manos no tienen membrana interdigital. |
| dedos (extremidad: anterior/posterior).presencia_discos | ausente | Especie terrestre, sin hÃ¡bito arborÃ­cola â€” no desarrolla discos digitales adhesivos. |


#### Nivel 2 â€” TÃ­pico de la especie, pero confirma en la foto (no es 100% absoluto)


| **Etiqueta.atributo** | **Valor mÃ¡s comÃºn** | **Por quÃ© solo es "tÃ­pico" y no fijo** |
| --- | --- | --- |
| cabeza.forma_general | ancha | La cabeza es ancha y robusta en la mayorÃ­a de individuos, pero el Ã¡ngulo de la foto puede hacerla ver distinta. |
| hocico.forma | truncado (perfil) / redondeado (dorsal) | Cambia segÃºn el Ã¡ngulo de toma â€” de perfil cae casi vertical (truncado), visto desde arriba se percibe mÃ¡s redondeado. Decide segÃºn la vista de esa foto, no de memoria. |
| timpano.visibilidad | visible | Suele ser grande y visible, pero a veces queda parcialmente tapado por las verrugas de la piel â€” si en la foto no se distingue bien, usa oculto_pliegue o no_evaluable igual que con cualquier otra especie. |
| dorso_flancos.color_base | marron_pardo | Es el color mÃ¡s frecuente, pero tambiÃ©n aparecen individuos grisÃ¡ceos o amarillentos â€” si la foto muestra otro color claramente, regÃ­stralo tal cual, no fuerces marron_pardo. |
| dorso_flancos.patron | manchado | Lo mÃ¡s comÃºn es manchado o reticulado, pero hay individuos casi lisos â€” mira la foto. |
| dorso_flancos.textura | verrugosa | Rasgo muy consistente (piel cubierta de espinas queratinizadas), pero en fotos de baja resoluciÃ³n puede leerse mÃ¡s como granulosa â€” usa tu criterio de la SecciÃ³n 4.6 si dudas. |
| dorso_flancos.linea_vertebral | ausente | Es lo habitual, pero algunos individuos sÃ­ presentan una lÃ­nea pÃ¡lida â€” confÃ­rmalo en la imagen. |
| vientre.color_base | blanco_crema | TÃ­pico, con variaciÃ³n hacia amarillento pÃ¡lido. |
| vientre.patron | moteado | El moteado oscuro es frecuente, sobre todo hacia garganta y pecho, pero su intensidad varÃ­a mucho entre individuos. |
| palmeadura (extremidad: posterior).grado | parcial | La palmeadura posterior moderada es tÃ­pica, pero "moderada" puede caer en basal o parcial segÃºn el individuo â€” compara con la SecciÃ³n 4.15 antes de fijarlo. |


#### Nivel 3 â€” Siempre se evalÃºa por imagen, nunca se fija por especie


| **Etiqueta.atributo** | **Por quÃ© nunca es fijo** |
| --- | --- |
| anuro_completo.vista / postura / calidad_enfoque | Son propiedades de la fotografÃ­a, no del animal â€” cambian en cada imagen por definiciÃ³n (SecciÃ³n 3.1â€“3.3). |
| anuro_completo.sexo_aparente | Depende de si esa foto puntual muestra callosidades nupciales o saco vocal â€” no de la especie. Usa indeterminado salvo que el carÃ¡cter sea visible en esa imagen. |
| anuro_completo.estadio | CorrecciÃ³n importante: aunque Rhinella horribilis es una especie de gran tamaÃ±o adulto, eso no significa que toda foto muestre un adulto â€” tambiÃ©n se fotografÃ­an juveniles y metamorfos de la especie, que son mucho mÃ¡s pequeÃ±os. Fijar estadio = adulto por especie etiquetarÃ­a mal a cualquier juvenil fotografiado. EvalÃºa el tamaÃ±o y las proporciones de ese individuo puntual (SecciÃ³n 3.4), no asumas por la especie. |


### C.2 Fichas de las demÃ¡s 27 especies

Cada ficha lista Ãºnicamente los atributos que una fuente taxonÃ³mica real respalda con claridad â€” no se completÃ³ ningÃºn atributo por relleno. Cuando una ficha tiene pocas filas, es intencional: la fuente disponible no daba para mÃ¡s, no es un descuido. Todas usan el mismo esquema Etiqueta.atributo â†’ Valor CVAT que el resto de esta guÃ­a. Recuerda: especie, vista, calidad_enfoque, postura, sexo_aparente y estadio (SecciÃ³n 3) SIEMPRE se evalÃºan por imagen, nunca se toman de esta ficha.


> [!note] LimitaciÃ³n de las bÃºsquedas
> AmphibiaWeb y varias pÃ¡ginas de Amphibian Species of the World (AMNH) bloquearon el acceso automatizado con CAPTCHA durante la investigaciÃ³n â€” donde eso pasÃ³, se usÃ³ Wikipedia, ResearchGate, PMC u otras fuentes secundarias que citan esas fuentes primarias, y se marcÃ³ "confianza baja" en las filas donde el respaldo fue indirecto (cachÃ© de buscador en vez de la fuente fetcheada). Pristimantis norandinus no tiene ficha porque el nombre parece invÃ¡lido â€” ver su aviso abajo. Pristimantis vilarsi tiene identidad confirmada por el equipo pero aÃºn sin datos morfolÃ³gicos.


#### Aromobatidae

**Rheobates palmatus** (valor CVAT: rheobates_palmatus)

*Rana de quebrada andina, corpulenta, endÃ©mica de Colombia (cordilleras Oriental y Central), con pies fuertemente palmeados.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| dorso_flancos.textura | granulosa | piel posteriormente granular |
| dorso_flancos.color_base | marron_pardo | crÃ­ptico, pardo o gris (ambos posibles) |
| palmeadura (posterior).grado | completa | palmeadura extensa en los pies |
| dorso_flancos.patron | manchado | confianza baja â€” fuente secundaria en cachÃ© |
| glandulas_pliegues.tipo | dorsolateral | franja dorsolateral pÃ¡lida, a veces interrumpida â€” confianza baja |


**Fuente(s):** *Wikipedia â€” Rheobates palmatus*


#### Bufonidae

**Rhinella alata** (valor CVAT: rhinella_alata)

*Sapo pequeÃ±o-mediano de hojarasca, grupo Rhinella margaritifera, de PanamÃ¡ y ChocÃ³ colombiano a Ecuador.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| hocico.forma | acuminado | subacuminado dorsal, redondeado a protuberante de perfil â€” valor mÃ¡s cercano |
| hocico.canto_rostral | definido | presente aunque descrito como poco marcado |
| glandulas_pliegues.tipo | parotoide | glÃ¡ndulas parotoides pequeÃ±as y alargadas |
| glandulas_pliegues.prominencia | leve | glÃ¡ndulas descritas como pequeÃ±as |
| dorso_flancos.textura | verrugosa | verrugas, pÃºstulas y tubÃ©rculos cÃ³nicos |
| dorso_flancos.patron | mixto | hilera de tubÃ©rculos + lÃ­nea mediodorsal |
| dorso_flancos.linea_vertebral | presente_delgada | lÃ­nea mediodorsal a menudo presente |
| vientre.color_base | blanco_crema | crema a amarillento (especÃ­menes preservados) |
| vientre.patron | moteado | marcas oscuras irregulares |
| dedos.presencia_discos | presente_pequeno | pequeÃ±os nÃ³dulos terminales |


**Fuente(s):** *Vallejo & Jungfer et al., Systematics of the R. margaritifera complex (PMC4432321)*

**Rhinella sp. (grupo margaritifera)** (valor CVAT: rhinella_sp_margaritifera)

*No es una especie Ãºnica â€” es un placeholder de grupo. Usa esto solo como base terrestre genÃ©rica, nunca como ficha fija de una especie concreta.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| glandulas_pliegues.tipo | parotoide | rasgo que define al grupo |
| dorso_flancos.textura | verrugosa | tubÃ©rculos pequeÃ±os y grandes, hilera lateral engrosada |
| dorso_flancos.color_base | marron_pardo | coloraciÃ³n crÃ­ptica "hoja muerta" â€” muy variable entre especies del grupo |
| dorso_flancos.patron | mixto | patrÃ³n disruptivo por crestas craneales + manchas |


**Fuente(s):** *PMC3909798 â€” nueva especie del grupo R. margaritifera, PerÃº*


#### Centrolenidae

**Sachatamia electrops** (valor CVAT: sachatamia_electrops)

*Rana de cristal de ojos verdes con marca blanca tipo "ojo elÃ©ctrico", descrita en 2017 de la Cordillera Central, Antioquia.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| hocico.forma | truncado | hocico truncado en vista dorsal y lateral, consistente en las fuentes |
| dorso_flancos.color_base | verde | dorso verde lima en vida |
| dorso_flancos.patron | manchado | manchas amarillas y azul oscuro |
| palmeadura (anterior).grado | parcial | palmeadura extensa entre dedos III-IV de la mano |
| dedos.presencia_discos | presente_grande | discos adhesivos tÃ­picos de Centrolenidae â€” confianza baja, rasgo de familia mÃ¡s que cita directa |


**Fuente(s):** *Rada, Jeckel, Caorsi, Barrientos, Rivera-Correa & Grant (2017), South American J. Herpetology 12(2)*


#### Craugastoridae

**Craugastor raniformis** (valor CVAT: craugastor_raniformis)

*Rana terrestre relativamente grande de bosque hÃºmedo (Colombia y PanamÃ¡), con fuerte dimorfismo sexual de tamaÃ±o (hembras mucho mÃ¡s grandes).*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| hocico.forma | puntiagudo | "a rather pointed snout", confirmado directamente |


**Fuente(s):** *Wikipedia â€” Craugastor raniformis*


#### Dendrobatidae

**Dendrobates truncatus** (valor CVAT: dendrobates_truncatus)

*Rana venenosa diurna y terrestre, endÃ©mica de Colombia (bosque seco Caribe y valle del Magdalena), con llamativas franjas dorsolaterales en "U".*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| dorso_flancos.color_base | negro | fondo negro consistente en todas las fuentes |
| dorso_flancos.patron | rayado | dos franjas dorsolaterales naranja-amarillo que se unen en el hocico, forma de "U" |
| vientre.color_base | manchado_oscuro | negro con manchas blanquecinas/amarillentas/verdosas |
| vientre.patron | moteado | manchas irregulares |
| dedos.presencia_discos | presente_pequeno | discos pequeÃ±os tÃ­picos del gÃ©nero â€” confianza baja |


**Fuente(s):** *Amphibian Species of the World (AMNH) Â· fuentes secundarias alineadas (dendrowiki, pierrewildlife)*

**Hyloxalus picachus** (valor CVAT: hyloxalus_picachus)

*Rana cohete pequeÃ±a, endÃ©mica del piedemonte submontano de la Cordillera Oriental, CaquetÃ¡.*


| **Aviso** El nombre vÃ¡lido parece ser Hyloxalus picachos (Ardila-Robayo, Acosta-Galvis & Coloma, 2000), no "picachus". Confirma la ortografÃ­a correcta antes de usar este valor en CVAT. |  |  |
| --- | --- | --- |
| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| palmeadura (posterior).grado | basal | palmeadura basal en los pies â€” confianza baja, fuente comparativa indirecta |


**Fuente(s):** *Wikipedia â€” Hyloxalus picachos Â· Amphibian Species of the World (listado, bloqueado)*

**Leucostethus fraterdanieli** (valor CVAT: leucostethus_fraterdanieli)

*Rana cohete andina pequeÃ±a ("Santa Rita rocket frog") de la vertiente oriental de la Cordillera Central, Colombia.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| ingle_muslo.color_flash | amarillo | marcas flash amarillo limÃ³n/dorado en axila, ingle, vientre y cara oculta del muslo â€” bien respaldado |
| vientre.color_base | azul_turquesa | descrito como "blanco azulado" â€” valor mÃ¡s cercano, no es turquesa saturado |
| vientre.patron | reticulado | patrÃ³n ventral marmoleado/reticulado, diagnÃ³stico frente a congÃ©neres |
| palmeadura (posterior).grado | ausente | palmeadura ausente o rudimentaria |
| glandulas_pliegues.tipo | dorsolateral | franja dorsolateral pÃ¡lida presente |
| glandulas_pliegues.prominencia | leve | descrita como pÃ¡lida, no marcada |


**Fuente(s):** *Grant & Rada (2018) vÃ­a ResearchGate Â· Amphibian Species of the World*


#### Hylidae

**Boana cinereascens** (valor CVAT: boana_cinereascens)

*Hylido mediano-pequeÃ±o arborÃ­cola, dorso verdoso-grisÃ¡ceo capaz de cambiar de tono.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| hocico.forma | truncado | cabeza mÃ¡s ancha que larga, hocico truncado |
| hocico.canto_rostral | indefinido | descrito como indistinto y redondeado |
| timpano.tamano_relativo_ojo | menor | ojos grandes y protuberantes, mayores que el tÃ­mpano |
| glandulas_pliegues.tipo | pliegue_supratimpanico | pliegue supratimpÃ¡nico presente |
| dorso_flancos.textura | granulosa | flancos, ingle y muslos granulares |


**Fuente(s):** *AmphibiaWeb sp/807 Â· ResearchGate â€” Resolving the taxonomic puzzle of B. cinerascens*

**Boana lanciformis** (valor CVAT: boana_lanciformis)

*Hylido grande (hembras 68â€“81 mm), dorso pardo claro a grisÃ¡ceo con barras transversales oscuras.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| dorso_flancos.textura | lisa | "el dorso es liso" |
| dorso_flancos.color_base | marron_pardo | marrÃ³n claro a cafÃ© grisÃ¡ceo |
| dorso_flancos.patron | rayado | rayas transversales oscuras |
| vientre.color_base | blanco_crema | parte ventral mÃ¡s clara â€” aproximaciÃ³n, no confirmado como blanco/crema puro |


**Fuente(s):** *Amphibian Species of the World Â· Museo de ZoologÃ­a U. del Azuay Â· Wikipedia â€” Basin tree frog*

**Boana punctata** (valor CVAT: boana_punctata)

*Hylido pequeÃ±o (SVL 3â€“4 cm), verde pÃ¡lido de dÃ­a con manchas rojizas; fluorescente bajo luz UV.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| dorso_flancos.textura | lisa | piel dorsal lisa |
| dorso_flancos.color_base | verde | verde pÃ¡lido de dÃ­a â€” cambia de noche, no es 100% fijo |
| dorso_flancos.patron | manchado | manchas rojizo-oscuras de dÃ­a / motas amarillentas de noche |
| vientre.color_base | blanco_crema | "underside is white" |


**Fuente(s):** *Wikipedia â€” Polka-dot tree frog Â· Amphibian Species of the World*

**Boana xerophylla** (valor CVAT: boana_xerophylla)

*Hylido de tamaÃ±o moderado (SVL ~49.7 mm), canto rostral redondeado, pliegue supratimpÃ¡nico marcado.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| hocico.canto_rostral | indefinido | "rounded and almost indistinct" |
| glandulas_pliegues.tipo | pliegue_supratimpanico | se extiende del ojo hacia la inserciÃ³n del brazo |
| dorso_flancos.color_base | marron_pardo | pardo oscuro a verde â€” variable, no estrictamente fijo |
| dedos.presencia_discos | presente_grande | dedos con discos redondeados grandes |
| palmeadura (anterior).grado | parcial | fÃ³rmula de membrana parcial en la mano |
| palmeadura (posterior).grado | parcial | palmeadura considerable pero no completa en el pie |
| vientre.color_base | blanco_crema | solo confirmado en regiÃ³n pericloacal, no en todo el vientre â€” cautela |


**Fuente(s):** *Wikipedia â€” Boana xerophylla (basado en Vera Candioti et al. 2021, Zootaxa)*

**Dendropsophus bogerti** (valor CVAT: dendropsophus_bogerti)

*Hylido pequeÃ±o endÃ©mico de los Andes de Colombia (Cordillera Central). Dimorfismo sexual de color: machos verde-amarillento, hembras pardo dorado/beige.*


| **Aviso** El color dorsal cambia entre sexos â€” no trates dorso_flancos.color_base como un valor Ãºnico fijo sin mirar la foto. |  |  |
| --- | --- | --- |
| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| hocico.forma | redondeado | hocico corto y redondeado |
| timpano.tamano_relativo_ojo | menor | tÃ­mpano muy indistinto â€” aproximaciÃ³n, no mediciÃ³n directa |
| palmeadura (anterior).grado | basal | dedos de la mano palmeados en la base |
| palmeadura (posterior).grado | parcial | dedos del pie algo mÃ¡s de la mitad palmeados |
| ingle_muslo.color_flash | naranja | superficies ocultas de las extremidades naranja brillante |
| vientre.color_base | amarillo | garganta amarillo brillante, vientre pardo-amarillento pÃ¡lido |


**Fuente(s):** *Wikipedia â€” Dendropsophus bogerti (Cochran & Goin 1970, revisiÃ³n Duellman)*

**Dendropsophus microcephalus** (valor CVAT: dendropsophus_microcephalus)

*Hylido pequeÃ±o de cabeza chica, dorso liso amarillo pÃ¡lido a anaranjado con lÃ­neas pardas, sin patrÃ³n de reloj de arena (lo distingue de D. ebraccatus).*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| hocico.canto_rostral | definido | forma una cresta distinta |
| dorso_flancos.textura | lisa | dorsalmente lisa |
| dorso_flancos.color_base | amarillo_naranja | amarillo pÃ¡lido a brillante / amarillo-pardo anaranjado |
| dorso_flancos.patron | rayado | dos lÃ­neas pardas paralelas â€” SIN reloj de arena (diagnÃ³stico negativo vs. D. ebraccatus) |
| vientre.color_base | blanco_crema | crema pÃ¡lido o blanco ventralmente |
| ingle_muslo.color_flash | amarillo | muslos translÃºcidos amarillos sin pigmento |
| palmeadura (anterior).grado | basal | palmeadura reducida en la mano |
| palmeadura (posterior).grado | parcial | palmeadura moderada en el pie |
| dedos.presencia_discos | presente_pequeno | discos expandidos, tamaÃ±o no cuantificado â€” especie pequeÃ±a |


**Fuente(s):** *Wikipedia â€” Dendropsophus microcephalus Â· The Herpetology of Trinidad and Tobago*

**Dendropsophus reticulatus** (valor CVAT: dendropsophus_reticulatus)

*Hylido pequeÃ±o de tierras bajas amazÃ³nicas, asociado a bosques inundables y cuerpos de agua temporales.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| dorso_flancos.patron | mixto | "uniforme, a veces con manchas pardo oscuras redondeadas" â€” muy variable entre individuos |


**Fuente(s):** *AmphibiaWeb sp/8601 (extracto indexado) Â· Wikipedia*

**Dendropsophus triangulum** (valor CVAT: dendropsophus_triangulum)

*Hylido de la cuenca alta amazÃ³nica â€” es en realidad un complejo de al menos 5 especies confirmadas (D. triangulum species complex), lo que hace poco confiable cualquier "rasgo fijo".*


| **Aviso** Complejo de especies polimÃ³rfico â€” trata esta ficha como referencia dÃ©bil, no como diagnÃ³stico cerrado. |  |  |
| --- | --- | --- |
| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| dorso_flancos.patron | manchado | patrÃ³n triangular/reloj de arena reportado, pero muy variable dentro del complejo |
| dorso_flancos.color_base | marron_pardo | pardo, amarillo o crema apagado de dÃ­a |


**Fuente(s):** *Wikipedia â€” Dendropsophus triangulum*

**Hyloscirtus palmeri** (valor CVAT: hyloscirtus_palmeri)

*Rana de torrente andina (grupo H. bogotensis), bosques hÃºmedos montanos y quebradas del Valle del Cauca.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| hocico.forma | acuminado | subacuminado dorsal, redondeado de perfil â€” mezcla segÃºn Ã¡ngulo |
| hocico.canto_rostral | definido | distinto y ligeramente cÃ³ncavo |
| palmeadura (posterior).grado | completa | dedos del pie completamente palmeados â€” tÃ­pico de ranas de torrente |


**Fuente(s):** *ResearchGate â€” comparaciÃ³n taxonÃ³mica H. palmeri Â· Wikipedia â€” Palmer's tree frog*

**Phyllomedusa tarsius** (valor CVAT: phyllomedusa_tarsius)

*Rana mono arbÃ³rea nocturna (Phyllomedusinae), de Brasil, Colombia, Ecuador, PerÃº y Venezuela.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| dorso_flancos.color_base | verde | cabeza, cuerpo, muslos y antebrazos verde brillante |
| ingle_muslo.color_flash | azul | flancos, antebrazos y membrana entre 4Âº-5Âº dedo del pie azules â€” rasgo diagnÃ³stico |
| vientre.color_base | otro | blanco y naranja mezclados â€” no encaja en una sola opciÃ³n del esquema |


**Fuente(s):** *Duellman 1961, Revista de BiologÃ­a Tropical Â· Wikipedia*

**Pithecopus hypochondrialis** (valor CVAT: pithecopus_hypochondrialis)

*Rana mono de patas naranjas, piedemonte andino oriental y sabanas de la OrinoquÃ­a colombiana hasta la Amazonia.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| dorso_flancos.color_base | verde | capaz de cambio rÃ¡pido de color como camuflaje â€” no 100% fijo |
| ingle_muslo.color_flash | naranja | rasgo diagnÃ³stico clÃ¡sico y muy consistente: flancos naranja-rojizo sobre blanco-crema con rayas negras, muslos internos tipo "tigre" |


**Fuente(s):** *Wikipedia Â· iNaturalist Â· guÃ­as de crÃ­a (apoyo secundario)*

**Scinax ruber** (valor CVAT: scinax_ruber)

*Rana arbÃ³rea de hocico rojo, amplia distribuciÃ³n amazÃ³nica y Escudo GuayanÃ©s hasta PanamÃ¡, comÃºn en Ã¡reas alteradas.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| hocico.forma | redondeado | hocico redondeado, no acuminado |
| dorso_flancos.textura | lisa | lisa a finamente tuberculada â€” matiz, mÃ¡s cercano a lisa |
| dorso_flancos.color_base | marron_pardo | tono canela/pardo a verde apagado |
| dorso_flancos.patron | rayado | franja pÃ¡lida bordeada de oscuro desde el pÃ¡rpado + lÃ­nea vertebral discontinua |
| dorso_flancos.linea_vertebral | presente_delgada | lÃ­nea mediodorsal canela discontinua |
| vientre.color_base | amarillo | vientre amarillo |
| ingle_muslo.color_flash | naranja | ingle con manchas amarillas bordeadas de negro; muslos posteriores moteados naranja/amarillo |


**Fuente(s):** *Wikipedia â€” Scinax ruber (fetch completo)*


#### Leptodactylidae

**Engystomops pustulosus** (valor CVAT: engystomops_pustulosus)

*Rana tÃºngara, pequeÃ±a, nocturna y terrestre, famosa por su canto de dos partes ("whine + chuck") con saco vocal inflable.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| hocico.forma | puntiagudo | puntiagudo dorsal, redondeado de perfil |
| glandulas_pliegues.tipo | parotoide | glÃ¡ndula parotoide triangular pequeÃ±a |
| glandulas_pliegues.prominencia | leve | descrita como pequeÃ±a |
| dorso_flancos.color_base | marron_pardo | base gris-parda |
| dorso_flancos.patron | verrugoso | tubÃ©rculos en filas longitudinales con manchas oscuras |
| dorso_flancos.textura | verrugosa | consistente en ambas fuentes |
| vientre.color_base | blanco_crema | tostado a amarillo, granular |
| vientre.patron | liso | piel ventral granular pero patrÃ³n uniforme |
| saco_vocal.posicion | subgular_medial | saco Ãºnico y oscuro bajo la garganta, no pareado |
| palmeadura (anterior).grado | ausente | todos los dedos de la mano sin palmeadura |
| palmeadura (posterior).grado | basal | solo un reborde lateral leve en los dedos del pie |
| dedos.presencia_discos | ausente | dedos sin discos adhesivos |


**Fuente(s):** *Herpetology of Trinidad and Tobago Â· Wikipedia â€” TÃºngara frog*

**Leptodactylus colombiensis** (valor CVAT: leptodactylus_colombiensis)

*Rana terrestre de bosques andinos de piedemonte (300â€“2300 m), 5Âº miembro colombiano del grupo L. latrans, histÃ³ricamente confundida con L. validus.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| dorso_flancos.color_base | marron_pardo | pardo mÃ¡s oscuro |
| dorso_flancos.patron | manchado | manchas irregulares en el dorso; bandas del muslo mÃ¡s anchas e irregulares que en L. validus |


**Fuente(s):** *PMC5904439 â€” L. validus en Colombia: distribuciÃ³n e identificaciÃ³n Â· Amphibian Species of the World*


#### Strabomantidae

**Pristimantis achatinus** **â€” CutÃ­n ComÃºn de Occidente** (valor CVAT: pristimantis_achatinus)

*Rana de lluvia de desarrollo directo, de PanamÃ¡ oriental a travÃ©s de Colombia hasta el occidente de Ecuador; terrestre, a veces sube a vegetaciÃ³n baja.*


| **Aviso** El nombre del roster original era "acanthinus" â€” el equipo confirmÃ³ que el nombre correcto es achatinus. |  |  |
| --- | --- | --- |
| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| hocico.forma | acuminado | subacuminado en vista dorsal, redondeado de perfil â€” mezcla segÃºn Ã¡ngulo, como en otros Pristimantis |
| timpano.tamano_relativo_ojo | igual | tÃ­mpano grande, 70â€“93% del diÃ¡metro del ojo |
| dorso_flancos.textura | granulosa | piel dorsal finamente granular ("shagreen"), con dos tubÃ©rculos escapulares subcÃ³nicos |
| dorso_flancos.patron | manchado | patrÃ³n dorsal en chevrones / forma de "W" |
| glandulas_pliegues.tipo | cresta_dorsolateral | pliegues dorsolaterales dÃ©biles y discontinuos en la mitad del dorso |
| glandulas_pliegues.prominencia | leve | descritos como dÃ©biles |


**Fuente(s):** *Amphibian Species of the World (AMNH) Â· PMC8763812 â€” clave comparativa de Pristimantis Â· bÃºsqueda agregada de descripciones taxonÃ³micas*

**Pristimantis norandinus** (valor CVAT: pristimantis_norandinus)

*Nombre no confirmado como especie vÃ¡lida.*


> [!note] Aviso
> BÃºsquedas repetidas (AmphibiaWeb, GBIF, Amphibian Species of the World, Wikipedia, ResearchGate) no encontraron ningÃºn "Pristimantis norandinus". El Ãºnico taxÃ³n encontrado con ese epÃ­teto es Dendropsophus norandinus â€” una especie de otra familia (Hylidae). Verifica este nombre contra la fuente original de tu listado antes de usarlo: puede ser un error de tipeo o una confusiÃ³n con otra especie.


**Pristimantis paisa** (valor CVAT: pristimantis_paisa)

*Rana de desarrollo directo endÃ©mica de la Cordillera Central, Antioquia (1800â€“3100 m); descrita por Lynch & Ardila-Robayo, 1999.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| dorso_flancos.color_base | marron_pardo | "drab brown" |
| dorso_flancos.patron | liso | "without well developed patterns" |
| dorso_flancos.textura | lisa | "skin is smooth" |
| vientre.color_base | blanco_crema | flancos y vientre blanco a crema sin manchas |
| vientre.patron | liso | sin manchas |
| palmeadura (anterior).grado | ausente | dedos con discos y quillas laterales pero sin membrana |
| palmeadura (posterior).grado | ausente | Ã­dem en los pies |
| dedos.presencia_discos | presente_pequeno | discos y quillas laterales presentes, tamaÃ±o no cuantificado |


**Fuente(s):** *Wikipedia â€” Pristimantis paisa Â· ResearchGate*

**Pristimantis penelopus** (valor CVAT: pristimantis_penelopus)

*Rana pequeÃ±a-mediana de desarrollo directo, grupo P. unistrigatus, norte de Colombia. Machos 24.5â€“28.8 mm LHC, hembras 30.1â€“38.4 mm LHC.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| hocico.forma | redondeado | dorsal: redondeado o subacuminado; perfil: redondeado o truncado |
| hocico.canto_rostral | indefinido | redondeado a angulado, nunca agudo |
| ojo.tamano_relativo | grande | moderadamente grande y prominente; diÃ¡metro mayor que la distancia ojo-narina |
| timpano.visibilidad | visible | pequeÃ±o y circular |
| timpano.tamano_relativo_ojo | menor | ~1/3 a 1/4 del diÃ¡metro del ojo |
| glandulas_pliegues.tipo | pliegue_supratimpanico | dÃ©bil o ausente; sin crestas craneales ni pliegues dorsolaterales |
| glandulas_pliegues.prominencia | leve | cuando presente, descrito como dÃ©bil |
| dorso_flancos.textura | granulosa | dorso finamente granular, flancos fuertemente granulares |
| dorso_flancos.color_base | marron_pardo | muy variable: pardo amarillento pÃ¡lido a pardo oscuro, o grisÃ¡ceo |
| dorso_flancos.patron | manchado | marca en "W" o X interrumpida escapular; banda interorbital; barras oblicuas en los flancos |
| vientre.color_base | blanco_crema | crema o amarillento pÃ¡lido |
| vientre.patron | liso | generalmente uniforme, sin manchas oscuras (a veces teÃ±ido de pardo hacia la garganta) |
| dedos.presencia_discos | presente_grande | discos grandes y bien desarrollados, mÃ¡s anchos que largos, con reborde lateral |
| palmeadura (posterior).grado | ausente | dedos del pie libres, unidos solo en la base por un pliegue pequeÃ±o |
| tuberculo_metatarsal.presencia | presente | interno ovalado, moderado (2-3x el externo); externo pequeÃ±o y redondeado |
| tuberculo_metatarsal.forma | redondeado | ambos tubÃ©rculos redondeados, no tipo pala |


**Fuente(s):** *Lynch & Rueda-Almonacid (1999), descripciÃ³n original Â· revisiones taxonÃ³micas posteriores â€” aportado por el equipo*

**Pristimantis taeniatus** (valor CVAT: pristimantis_taeniatus)

*Rana de lluvia de desarrollo directo, de PanamÃ¡ central a travÃ©s del ChocÃ³ y los Andes colombianos (Boulenger, 1912); tolerante a hÃ¡bitats alterados.*


| **Aviso** Existe una morfa rayada minoritaria (~10%) â€” no asumas rayado solo por el nombre de la especie. |  |  |
| --- | --- | --- |
| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| dorso_flancos.color_base | marron_pardo | consistente |
| dorso_flancos.patron | manchado | morfa dominante (~90%): motas oscuras formando un patrÃ³n occipital en "W" |
| dorso_flancos.linea_vertebral | ausente | en la morfa dominante â€” existe una morfa rayada minoritaria |
| dorso_flancos.textura | granulosa | lisa hacia adelante, granulosa hacia atrÃ¡s â€” valor mÃ¡s cercano para la regiÃ³n diagnÃ³stica |
| palmeadura (anterior).grado | ausente | sin membrana entre dedos |
| palmeadura (posterior).grado | ausente | sin membrana entre dedos |


**Fuente(s):** *Wikipedia â€” Pristimantis taeniatus Â· AmphibiaWeb sp/3234 (listado, no accesible directamente)*

**Pristimantis vilarsi** **â€” Ranita SelvÃ¡tica ComÃºn** (valor CVAT: pristimantis_vilarsi)

*Rana pequeÃ±a a mediana, terrestre y nocturna, asociada a la hojarasca de la selva amazÃ³nica. Perfil tÃ­pico aportado por el equipo; confirma siempre los rasgos variables en la fotografÃ­a concreta.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| cabeza.forma_general | ancha | moderadamente ancha, ovalada o ligeramente triangular; confirma segÃºn el Ã¡ngulo de la foto |
| hocico.forma | subacuminado | visto dorsalmente puntiagudo o subacuminado; de perfil redondeado o truncado |
| hocico.canto_rostral | definido | casi recto |
| ojo.tamano_relativo | grande | moderadamente grande y prominente |
| ojo.color_iris | bronce | generalmente bronce o cobrizo, con posible reticulaciÃ³n oscura y franja horizontal clara; confirma el color en la foto |
| timpano.visibilidad | visible | distinto, ovalado o circular |
| timpano.tamano_relativo_ojo | menor | aproximadamente 1/2 a 2/3 del diÃ¡metro del ojo |
| dorso_flancos.color_base | marron_pardo | muy variable: marrÃ³n claro a chocolate oscuro o grisÃ¡ceo |
| dorso_flancos.patron | manchado | moteado irregular, posible marca interescapular en W invertida, mÃ¡scara facial oscura y barras oblicuas en los flancos |
| dorso_flancos.textura | granulosa | dorso liso a finamente granuloso; flancos fuertemente granulares |
| dorso_flancos.linea_vertebral | ausente | usualmente ausente, aunque puede aparecer una lÃ­nea fina y pÃ¡lida |
| vientre.color_base | blanco_crema | blanco crema o amarillento pÃ¡lido; visible solo en vista ventral |
| vientre.patron | liso | generalmente liso o finamente moteado, sobre todo en garganta y pecho |
| dedos.presencia_discos | presente_pequeno | discos pequeÃ±os pero evidentes en manos y pies |
| palmeadura (anterior).grado | ausente | dedos de la mano sin membrana interdigital |
| palmeadura (posterior).grado | ausente | dedos del pie libres; pueden presentar rebordes laterales estrechos |
| tuberculo_metatarsal.presencia | presente | tubÃ©rculo interno ovalado y prominente; externo pequeÃ±o y redondeado |
| tuberculo_metatarsal.forma | redondeado | tubÃ©rculos metatarsales redondeados |


**Fuente(s):** *DescripciÃ³n morfolÃ³gica aportada por el equipo; pendiente de cotejo con una fuente taxonÃ³mica primaria*



