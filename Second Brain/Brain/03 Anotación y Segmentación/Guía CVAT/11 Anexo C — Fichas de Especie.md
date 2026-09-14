---
title: "Anexo C â€” Fichas de Especie"
tipo: guía
proyecto: Anura
fuente: "Guia_CVAT_Anuro.docx (v1.0)"
tags: [anura, cvat, anotación, segmentación]
---

# Anexo C â€” Fichas de Especie

â† [[10 Anexo B â€” Capturas de Pantalla]] · [[Guía CVAT â€” àndice]]

El nombre de la especie está en el nombre del archivo, visible en la barra superior central de CVAT al abrir la imagen (ver Figura 3.1, Sección 3.0). Cuando reconozcas ese nombre, no necesitas evaluar a ojo cada atributo de esa foto: varios de ellos son diagnósticos de la especie y prácticamente siempre tienen el mismo valor. Otros, en cambio, dependen de la foto concreta (el ángulo, la postura, si el individuo es joven o adulto) y deben seguir juzgándose imagen por imagen, sin importar qué tan bien conozcas la especie.


> [!note] Por qué esta sección solo tiene una ficha completa por ahora
> Le pedí al equipo un ejemplo de referencia (Rhinella horribilis) y lo usé para construir la plantilla de abajo â€” la separación en tres niveles (siempre fijo / típico pero revisa la foto / siempre por imagen) sale de ese ejemplo. Para las otras 29 especies de la lista NO inventé características a partir de lo que "recuerdo" sobre cada una: con solo el nombre no tengo forma de garantizar que un rasgo diagnóstico que recito de memoria sea correcto para esa especie puntual, y una ficha de especie mal hecha es peor que no tener ficha â€” el anotador la usaría para fijar valores en decenas de fotos sin volver a mirar la imagen. Al final de esta sección te pregunto cómo quieres completarlas.


### C.1 Ficha completa â€” Rhinella horribilis (especie de referencia)

Familia Bufonidae. Esta ficha fue construida a partir de la descripción que el equipo aportó para esta especie, reorganizada en el formato de tres niveles que usarán las demás fichas.


#### Nivel 1 â€” Siempre fijo para esta especie (no lo evalàºes, ya lo sabes)


| **Etiqueta.atributo** | **Valor fijo** | **Por qué es fijo** |
| --- | --- | --- |
| anuro_completo.especie | rhinella_horribilis | Es el dato que define toda la ficha; se fija leyendo el nombre del archivo en la barra superior de CVAT. |
| hocico.canto_rostral | definido | Rhinella horribilis tiene crestas óseas cefálicas (canto rostral, supraorbitarias, parietales) bien desarrolladas â€” es un rasgo esquelético, no cambia entre individuos. |
| timpano.tamano_relativo_ojo | menor | El tímpano es proporcionalmente menor que el ojo en toda la especie. |
| glandulas_pliegues.tipo | parotoide | El rasgo diagnóstico de la especie: glándulas parotoides enormes, triangulares, es lo primero que separa a Rhinella de otros géneros en campo. |
| glandulas_pliegues.prominencia | marcada | Consistente con lo anterior â€” son de las parotoides más grandes y evidentes entre los anuros del dataset. |
| palmeadura (extremidad: anterior).grado | ausente | Los sapos del género Rhinella son terrestres; las manos no tienen membrana interdigital. |
| dedos (extremidad: anterior/posterior).presencia_discos | ausente | Especie terrestre, sin hábito arborícola â€” no desarrolla discos digitales adhesivos. |


#### Nivel 2 â€” Típico de la especie, pero confirma en la foto (no es 100% absoluto)


| **Etiqueta.atributo** | **Valor más comàºn** | **Por qué solo es "típico" y no fijo** |
| --- | --- | --- |
| cabeza.forma_general | ancha | La cabeza es ancha y robusta en la mayoría de individuos, pero el ángulo de la foto puede hacerla ver distinta. |
| hocico.forma | truncado (perfil) / redondeado (dorsal) | Cambia segàºn el ángulo de toma â€” de perfil cae casi vertical (truncado), visto desde arriba se percibe más redondeado. Decide segàºn la vista de esa foto, no de memoria. |
| timpano.visibilidad | visible | Suele ser grande y visible, pero a veces queda parcialmente tapado por las verrugas de la piel â€” si en la foto no se distingue bien, usa oculto_pliegue o no_evaluable igual que con cualquier otra especie. |
| dorso_flancos.color_base | marron_pardo | Es el color más frecuente, pero también aparecen individuos grisáceos o amarillentos â€” si la foto muestra otro color claramente, regístralo tal cual, no fuerces marron_pardo. |
| dorso_flancos.patron | manchado | Lo más comàºn es manchado o reticulado, pero hay individuos casi lisos â€” mira la foto. |
| dorso_flancos.textura | verrugosa | Rasgo muy consistente (piel cubierta de espinas queratinizadas), pero en fotos de baja resolución puede leerse más como granulosa â€” usa tu criterio de la Sección 4.6 si dudas. |
| dorso_flancos.linea_vertebral | ausente | Es lo habitual, pero algunos individuos sí presentan una línea pálida â€” confírmalo en la imagen. |
| vientre.color_base | blanco_crema | Típico, con variación hacia amarillento pálido. |
| vientre.patron | moteado | El moteado oscuro es frecuente, sobre todo hacia garganta y pecho, pero su intensidad varía mucho entre individuos. |
| palmeadura (extremidad: posterior).grado | parcial | La palmeadura posterior moderada es típica, pero "moderada" puede caer en basal o parcial segàºn el individuo â€” compara con la Sección 4.15 antes de fijarlo. |


#### Nivel 3 â€” Siempre se evalàºa por imagen, nunca se fija por especie


| **Etiqueta.atributo** | **Por qué nunca es fijo** |
| --- | --- |
| anuro_completo.vista / postura / calidad_enfoque | Son propiedades de la fotografía, no del animal â€” cambian en cada imagen por definición (Sección 3.1â€“3.3). |
| anuro_completo.sexo_aparente | Depende de si esa foto puntual muestra callosidades nupciales o saco vocal â€” no de la especie. Usa indeterminado salvo que el carácter sea visible en esa imagen. |
| anuro_completo.estadio | Corrección importante: aunque Rhinella horribilis es una especie de gran tamaño adulto, eso no significa que toda foto muestre un adulto â€” también se fotografían juveniles y metamorfos de la especie, que son mucho más pequeños. Fijar estadio = adulto por especie etiquetaría mal a cualquier juvenil fotografiado. Evalàºa el tamaño y las proporciones de ese individuo puntual (Sección 3.4), no asumas por la especie. |


### C.2 Fichas de las demás 27 especies

Cada ficha lista àºnicamente los atributos que una fuente taxonómica real respalda con claridad â€” no se completó ningàºn atributo por relleno. Cuando una ficha tiene pocas filas, es intencional: la fuente disponible no daba para más, no es un descuido. Todas usan el mismo esquema Etiqueta.atributo â†’ Valor CVAT que el resto de esta guía. Recuerda: especie, vista, calidad_enfoque, postura, sexo_aparente y estadio (Sección 3) SIEMPRE se evalàºan por imagen, nunca se toman de esta ficha.


> [!note] Limitación de las bàºsquedas
> AmphibiaWeb y varias páginas de Amphibian Species of the World (AMNH) bloquearon el acceso automatizado con CAPTCHA durante la investigación â€” donde eso pasó, se usó Wikipedia, ResearchGate, PMC u otras fuentes secundarias que citan esas fuentes primarias, y se marcó "confianza baja" en las filas donde el respaldo fue indirecto (caché de buscador en vez de la fuente fetcheada). Pristimantis norandinus no tiene ficha porque el nombre parece inválido â€” ver su aviso abajo. Pristimantis vilarsi tiene identidad confirmada por el equipo pero aàºn sin datos morfológicos.


#### Aromobatidae

**Rheobates palmatus** (valor CVAT: rheobates_palmatus)

*Rana de quebrada andina, corpulenta, endémica de Colombia (cordilleras Oriental y Central), con pies fuertemente palmeados.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| dorso_flancos.textura | granulosa | piel posteriormente granular |
| dorso_flancos.color_base | marron_pardo | críptico, pardo o gris (ambos posibles) |
| palmeadura (posterior).grado | completa | palmeadura extensa en los pies |
| dorso_flancos.patron | manchado | confianza baja â€” fuente secundaria en caché |
| glandulas_pliegues.tipo | dorsolateral | franja dorsolateral pálida, a veces interrumpida â€” confianza baja |


**Fuente(s):** *Wikipedia â€” Rheobates palmatus*


#### Bufonidae

**Rhinella alata** (valor CVAT: rhinella_alata)

*Sapo pequeño-mediano de hojarasca, grupo Rhinella margaritifera, de Panamá y Chocó colombiano a Ecuador.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| hocico.forma | acuminado | subacuminado dorsal, redondeado a protuberante de perfil â€” valor más cercano |
| hocico.canto_rostral | definido | presente aunque descrito como poco marcado |
| glandulas_pliegues.tipo | parotoide | glándulas parotoides pequeñas y alargadas |
| glandulas_pliegues.prominencia | leve | glándulas descritas como pequeñas |
| dorso_flancos.textura | verrugosa | verrugas, pàºstulas y tubérculos cónicos |
| dorso_flancos.patron | mixto | hilera de tubérculos + línea mediodorsal |
| dorso_flancos.linea_vertebral | presente_delgada | línea mediodorsal a menudo presente |
| vientre.color_base | blanco_crema | crema a amarillento (especímenes preservados) |
| vientre.patron | moteado | marcas oscuras irregulares |
| dedos.presencia_discos | presente_pequeno | pequeños nódulos terminales |


**Fuente(s):** *Vallejo & Jungfer et al., Systematics of the R. margaritifera complex (PMC4432321)*

**Rhinella sp. (grupo margaritifera)** (valor CVAT: rhinella_sp_margaritifera)

*No es una especie àºnica â€” es un placeholder de grupo. Usa esto solo como base terrestre genérica, nunca como ficha fija de una especie concreta.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| glandulas_pliegues.tipo | parotoide | rasgo que define al grupo |
| dorso_flancos.textura | verrugosa | tubérculos pequeños y grandes, hilera lateral engrosada |
| dorso_flancos.color_base | marron_pardo | coloración críptica "hoja muerta" â€” muy variable entre especies del grupo |
| dorso_flancos.patron | mixto | patrón disruptivo por crestas craneales + manchas |


**Fuente(s):** *PMC3909798 â€” nueva especie del grupo R. margaritifera, Peràº*


#### Centrolenidae

**Sachatamia electrops** (valor CVAT: sachatamia_electrops)

*Rana de cristal de ojos verdes con marca blanca tipo "ojo eléctrico", descrita en 2017 de la Cordillera Central, Antioquia.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| hocico.forma | truncado | hocico truncado en vista dorsal y lateral, consistente en las fuentes |
| dorso_flancos.color_base | verde | dorso verde lima en vida |
| dorso_flancos.patron | manchado | manchas amarillas y azul oscuro |
| palmeadura (anterior).grado | parcial | palmeadura extensa entre dedos III-IV de la mano |
| dedos.presencia_discos | presente_grande | discos adhesivos típicos de Centrolenidae â€” confianza baja, rasgo de familia más que cita directa |


**Fuente(s):** *Rada, Jeckel, Caorsi, Barrientos, Rivera-Correa & Grant (2017), South American J. Herpetology 12(2)*


#### Craugastoridae

**Craugastor raniformis** (valor CVAT: craugastor_raniformis)

*Rana terrestre relativamente grande de bosque hàºmedo (Colombia y Panamá), con fuerte dimorfismo sexual de tamaño (hembras mucho más grandes).*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| hocico.forma | puntiagudo | "a rather pointed snout", confirmado directamente |


**Fuente(s):** *Wikipedia â€” Craugastor raniformis*


#### Dendrobatidae

**Dendrobates truncatus** (valor CVAT: dendrobates_truncatus)

*Rana venenosa diurna y terrestre, endémica de Colombia (bosque seco Caribe y valle del Magdalena), con llamativas franjas dorsolaterales en "U".*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| dorso_flancos.color_base | negro | fondo negro consistente en todas las fuentes |
| dorso_flancos.patron | rayado | dos franjas dorsolaterales naranja-amarillo que se unen en el hocico, forma de "U" |
| vientre.color_base | manchado_oscuro | negro con manchas blanquecinas/amarillentas/verdosas |
| vientre.patron | moteado | manchas irregulares |
| dedos.presencia_discos | presente_pequeno | discos pequeños típicos del género â€” confianza baja |


**Fuente(s):** *Amphibian Species of the World (AMNH) · fuentes secundarias alineadas (dendrowiki, pierrewildlife)*

**Hyloxalus picachus** (valor CVAT: hyloxalus_picachus)

*Rana cohete pequeña, endémica del piedemonte submontano de la Cordillera Oriental, Caquetá.*


| **Aviso** El nombre válido parece ser Hyloxalus picachos (Ardila-Robayo, Acosta-Galvis & Coloma, 2000), no "picachus". Confirma la ortografía correcta antes de usar este valor en CVAT. |  |  |
| --- | --- | --- |
| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| palmeadura (posterior).grado | basal | palmeadura basal en los pies â€” confianza baja, fuente comparativa indirecta |


**Fuente(s):** *Wikipedia â€” Hyloxalus picachos · Amphibian Species of the World (listado, bloqueado)*

**Leucostethus fraterdanieli** (valor CVAT: leucostethus_fraterdanieli)

*Rana cohete andina pequeña ("Santa Rita rocket frog") de la vertiente oriental de la Cordillera Central, Colombia.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| ingle_muslo.color_flash | amarillo | marcas flash amarillo limón/dorado en axila, ingle, vientre y cara oculta del muslo â€” bien respaldado |
| vientre.color_base | azul_turquesa | descrito como "blanco azulado" â€” valor más cercano, no es turquesa saturado |
| vientre.patron | reticulado | patrón ventral marmoleado/reticulado, diagnóstico frente a congéneres |
| palmeadura (posterior).grado | ausente | palmeadura ausente o rudimentaria |
| glandulas_pliegues.tipo | dorsolateral | franja dorsolateral pálida presente |
| glandulas_pliegues.prominencia | leve | descrita como pálida, no marcada |


**Fuente(s):** *Grant & Rada (2018) vía ResearchGate · Amphibian Species of the World*


#### Hylidae

**Boana cinereascens** (valor CVAT: boana_cinereascens)

*Hylido mediano-pequeño arborícola, dorso verdoso-grisáceo capaz de cambiar de tono.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| hocico.forma | truncado | cabeza más ancha que larga, hocico truncado |
| hocico.canto_rostral | indefinido | descrito como indistinto y redondeado |
| timpano.tamano_relativo_ojo | menor | ojos grandes y protuberantes, mayores que el tímpano |
| glandulas_pliegues.tipo | pliegue_supratimpanico | pliegue supratimpánico presente |
| dorso_flancos.textura | granulosa | flancos, ingle y muslos granulares |


**Fuente(s):** *AmphibiaWeb sp/807 · ResearchGate â€” Resolving the taxonomic puzzle of B. cinerascens*

**Boana lanciformis** (valor CVAT: boana_lanciformis)

*Hylido grande (hembras 68â€“81 mm), dorso pardo claro a grisáceo con barras transversales oscuras.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| dorso_flancos.textura | lisa | "el dorso es liso" |
| dorso_flancos.color_base | marron_pardo | marrón claro a café grisáceo |
| dorso_flancos.patron | rayado | rayas transversales oscuras |
| vientre.color_base | blanco_crema | parte ventral más clara â€” aproximación, no confirmado como blanco/crema puro |


**Fuente(s):** *Amphibian Species of the World · Museo de Zoología U. del Azuay · Wikipedia â€” Basin tree frog*

**Boana punctata** (valor CVAT: boana_punctata)

*Hylido pequeño (SVL 3â€“4 cm), verde pálido de día con manchas rojizas; fluorescente bajo luz UV.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| dorso_flancos.textura | lisa | piel dorsal lisa |
| dorso_flancos.color_base | verde | verde pálido de día â€” cambia de noche, no es 100% fijo |
| dorso_flancos.patron | manchado | manchas rojizo-oscuras de día / motas amarillentas de noche |
| vientre.color_base | blanco_crema | "underside is white" |


**Fuente(s):** *Wikipedia â€” Polka-dot tree frog · Amphibian Species of the World*

**Boana xerophylla** (valor CVAT: boana_xerophylla)

*Hylido de tamaño moderado (SVL ~49.7 mm), canto rostral redondeado, pliegue supratimpánico marcado.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| hocico.canto_rostral | indefinido | "rounded and almost indistinct" |
| glandulas_pliegues.tipo | pliegue_supratimpanico | se extiende del ojo hacia la inserción del brazo |
| dorso_flancos.color_base | marron_pardo | pardo oscuro a verde â€” variable, no estrictamente fijo |
| dedos.presencia_discos | presente_grande | dedos con discos redondeados grandes |
| palmeadura (anterior).grado | parcial | fórmula de membrana parcial en la mano |
| palmeadura (posterior).grado | parcial | palmeadura considerable pero no completa en el pie |
| vientre.color_base | blanco_crema | solo confirmado en región pericloacal, no en todo el vientre â€” cautela |


**Fuente(s):** *Wikipedia â€” Boana xerophylla (basado en Vera Candioti et al. 2021, Zootaxa)*

**Dendropsophus bogerti** (valor CVAT: dendropsophus_bogerti)

*Hylido pequeño endémico de los Andes de Colombia (Cordillera Central). Dimorfismo sexual de color: machos verde-amarillento, hembras pardo dorado/beige.*


| **Aviso** El color dorsal cambia entre sexos â€” no trates dorso_flancos.color_base como un valor àºnico fijo sin mirar la foto. |  |  |
| --- | --- | --- |
| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| hocico.forma | redondeado | hocico corto y redondeado |
| timpano.tamano_relativo_ojo | menor | tímpano muy indistinto â€” aproximación, no medición directa |
| palmeadura (anterior).grado | basal | dedos de la mano palmeados en la base |
| palmeadura (posterior).grado | parcial | dedos del pie algo más de la mitad palmeados |
| ingle_muslo.color_flash | naranja | superficies ocultas de las extremidades naranja brillante |
| vientre.color_base | amarillo | garganta amarillo brillante, vientre pardo-amarillento pálido |


**Fuente(s):** *Wikipedia â€” Dendropsophus bogerti (Cochran & Goin 1970, revisión Duellman)*

**Dendropsophus microcephalus** (valor CVAT: dendropsophus_microcephalus)

*Hylido pequeño de cabeza chica, dorso liso amarillo pálido a anaranjado con líneas pardas, sin patrón de reloj de arena (lo distingue de D. ebraccatus).*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| hocico.canto_rostral | definido | forma una cresta distinta |
| dorso_flancos.textura | lisa | dorsalmente lisa |
| dorso_flancos.color_base | amarillo_naranja | amarillo pálido a brillante / amarillo-pardo anaranjado |
| dorso_flancos.patron | rayado | dos líneas pardas paralelas â€” SIN reloj de arena (diagnóstico negativo vs. D. ebraccatus) |
| vientre.color_base | blanco_crema | crema pálido o blanco ventralmente |
| ingle_muslo.color_flash | amarillo | muslos translàºcidos amarillos sin pigmento |
| palmeadura (anterior).grado | basal | palmeadura reducida en la mano |
| palmeadura (posterior).grado | parcial | palmeadura moderada en el pie |
| dedos.presencia_discos | presente_pequeno | discos expandidos, tamaño no cuantificado â€” especie pequeña |


**Fuente(s):** *Wikipedia â€” Dendropsophus microcephalus · The Herpetology of Trinidad and Tobago*

**Dendropsophus reticulatus** (valor CVAT: dendropsophus_reticulatus)

*Hylido pequeño de tierras bajas amazónicas, asociado a bosques inundables y cuerpos de agua temporales.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| dorso_flancos.patron | mixto | "uniforme, a veces con manchas pardo oscuras redondeadas" â€” muy variable entre individuos |


**Fuente(s):** *AmphibiaWeb sp/8601 (extracto indexado) · Wikipedia*

**Dendropsophus triangulum** (valor CVAT: dendropsophus_triangulum)

*Hylido de la cuenca alta amazónica â€” es en realidad un complejo de al menos 5 especies confirmadas (D. triangulum species complex), lo que hace poco confiable cualquier "rasgo fijo".*


| **Aviso** Complejo de especies polimórfico â€” trata esta ficha como referencia débil, no como diagnóstico cerrado. |  |  |
| --- | --- | --- |
| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| dorso_flancos.patron | manchado | patrón triangular/reloj de arena reportado, pero muy variable dentro del complejo |
| dorso_flancos.color_base | marron_pardo | pardo, amarillo o crema apagado de día |


**Fuente(s):** *Wikipedia â€” Dendropsophus triangulum*

**Hyloscirtus palmeri** (valor CVAT: hyloscirtus_palmeri)

*Rana de torrente andina (grupo H. bogotensis), bosques hàºmedos montanos y quebradas del Valle del Cauca.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| hocico.forma | acuminado | subacuminado dorsal, redondeado de perfil â€” mezcla segàºn ángulo |
| hocico.canto_rostral | definido | distinto y ligeramente cóncavo |
| palmeadura (posterior).grado | completa | dedos del pie completamente palmeados â€” típico de ranas de torrente |


**Fuente(s):** *ResearchGate â€” comparación taxonómica H. palmeri · Wikipedia â€” Palmer's tree frog*

**Phyllomedusa tarsius** (valor CVAT: phyllomedusa_tarsius)

*Rana mono arbórea nocturna (Phyllomedusinae), de Brasil, Colombia, Ecuador, Peràº y Venezuela.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| dorso_flancos.color_base | verde | cabeza, cuerpo, muslos y antebrazos verde brillante |
| ingle_muslo.color_flash | azul | flancos, antebrazos y membrana entre 4º-5º dedo del pie azules â€” rasgo diagnóstico |
| vientre.color_base | otro | blanco y naranja mezclados â€” no encaja en una sola opción del esquema |


**Fuente(s):** *Duellman 1961, Revista de Biología Tropical · Wikipedia*

**Pithecopus hypochondrialis** (valor CVAT: pithecopus_hypochondrialis)

*Rana mono de patas naranjas, piedemonte andino oriental y sabanas de la Orinoquía colombiana hasta la Amazonia.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| dorso_flancos.color_base | verde | capaz de cambio rápido de color como camuflaje â€” no 100% fijo |
| ingle_muslo.color_flash | naranja | rasgo diagnóstico clásico y muy consistente: flancos naranja-rojizo sobre blanco-crema con rayas negras, muslos internos tipo "tigre" |


**Fuente(s):** *Wikipedia · iNaturalist · guías de cría (apoyo secundario)*

**Scinax ruber** (valor CVAT: scinax_ruber)

*Rana arbórea de hocico rojo, amplia distribución amazónica y Escudo Guayanés hasta Panamá, comàºn en áreas alteradas.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| hocico.forma | redondeado | hocico redondeado, no acuminado |
| dorso_flancos.textura | lisa | lisa a finamente tuberculada â€” matiz, más cercano a lisa |
| dorso_flancos.color_base | marron_pardo | tono canela/pardo a verde apagado |
| dorso_flancos.patron | rayado | franja pálida bordeada de oscuro desde el párpado + línea vertebral discontinua |
| dorso_flancos.linea_vertebral | presente_delgada | línea mediodorsal canela discontinua |
| vientre.color_base | amarillo | vientre amarillo |
| ingle_muslo.color_flash | naranja | ingle con manchas amarillas bordeadas de negro; muslos posteriores moteados naranja/amarillo |


**Fuente(s):** *Wikipedia â€” Scinax ruber (fetch completo)*


#### Leptodactylidae

**Engystomops pustulosus** (valor CVAT: engystomops_pustulosus)

*Rana tàºngara, pequeña, nocturna y terrestre, famosa por su canto de dos partes ("whine + chuck") con saco vocal inflable.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| hocico.forma | puntiagudo | puntiagudo dorsal, redondeado de perfil |
| glandulas_pliegues.tipo | parotoide | glándula parotoide triangular pequeña |
| glandulas_pliegues.prominencia | leve | descrita como pequeña |
| dorso_flancos.color_base | marron_pardo | base gris-parda |
| dorso_flancos.patron | verrugoso | tubérculos en filas longitudinales con manchas oscuras |
| dorso_flancos.textura | verrugosa | consistente en ambas fuentes |
| vientre.color_base | blanco_crema | tostado a amarillo, granular |
| vientre.patron | liso | piel ventral granular pero patrón uniforme |
| saco_vocal.posicion | subgular_medial | saco àºnico y oscuro bajo la garganta, no pareado |
| palmeadura (anterior).grado | ausente | todos los dedos de la mano sin palmeadura |
| palmeadura (posterior).grado | basal | solo un reborde lateral leve en los dedos del pie |
| dedos.presencia_discos | ausente | dedos sin discos adhesivos |


**Fuente(s):** *Herpetology of Trinidad and Tobago · Wikipedia â€” Tàºngara frog*

**Leptodactylus colombiensis** (valor CVAT: leptodactylus_colombiensis)

*Rana terrestre de bosques andinos de piedemonte (300â€“2300 m), 5º miembro colombiano del grupo L. latrans, históricamente confundida con L. validus.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| dorso_flancos.color_base | marron_pardo | pardo más oscuro |
| dorso_flancos.patron | manchado | manchas irregulares en el dorso; bandas del muslo más anchas e irregulares que en L. validus |


**Fuente(s):** *PMC5904439 â€” L. validus en Colombia: distribución e identificación · Amphibian Species of the World*


#### Strabomantidae

**Pristimantis achatinus** **â€” Cutín Comàºn de Occidente** (valor CVAT: pristimantis_achatinus)

*Rana de lluvia de desarrollo directo, de Panamá oriental a través de Colombia hasta el occidente de Ecuador; terrestre, a veces sube a vegetación baja.*


| **Aviso** El nombre del roster original era "acanthinus" â€” el equipo confirmó que el nombre correcto es achatinus. |  |  |
| --- | --- | --- |
| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| hocico.forma | acuminado | subacuminado en vista dorsal, redondeado de perfil â€” mezcla segàºn ángulo, como en otros Pristimantis |
| timpano.tamano_relativo_ojo | igual | tímpano grande, 70â€“93% del diámetro del ojo |
| dorso_flancos.textura | granulosa | piel dorsal finamente granular ("shagreen"), con dos tubérculos escapulares subcónicos |
| dorso_flancos.patron | manchado | patrón dorsal en chevrones / forma de "W" |
| glandulas_pliegues.tipo | cresta_dorsolateral | pliegues dorsolaterales débiles y discontinuos en la mitad del dorso |
| glandulas_pliegues.prominencia | leve | descritos como débiles |


**Fuente(s):** *Amphibian Species of the World (AMNH) · PMC8763812 â€” clave comparativa de Pristimantis · bàºsqueda agregada de descripciones taxonómicas*

**Pristimantis norandinus** (valor CVAT: pristimantis_norandinus)

*Nombre no confirmado como especie válida.*


> [!note] Aviso
> Bàºsquedas repetidas (AmphibiaWeb, GBIF, Amphibian Species of the World, Wikipedia, ResearchGate) no encontraron ningàºn "Pristimantis norandinus". El àºnico taxón encontrado con ese epíteto es Dendropsophus norandinus â€” una especie de otra familia (Hylidae). Verifica este nombre contra la fuente original de tu listado antes de usarlo: puede ser un error de tipeo o una confusión con otra especie.


**Pristimantis paisa** (valor CVAT: pristimantis_paisa)

*Rana de desarrollo directo endémica de la Cordillera Central, Antioquia (1800â€“3100 m); descrita por Lynch & Ardila-Robayo, 1999.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| dorso_flancos.color_base | marron_pardo | "drab brown" |
| dorso_flancos.patron | liso | "without well developed patterns" |
| dorso_flancos.textura | lisa | "skin is smooth" |
| vientre.color_base | blanco_crema | flancos y vientre blanco a crema sin manchas |
| vientre.patron | liso | sin manchas |
| palmeadura (anterior).grado | ausente | dedos con discos y quillas laterales pero sin membrana |
| palmeadura (posterior).grado | ausente | ídem en los pies |
| dedos.presencia_discos | presente_pequeno | discos y quillas laterales presentes, tamaño no cuantificado |


**Fuente(s):** *Wikipedia â€” Pristimantis paisa · ResearchGate*

**Pristimantis penelopus** (valor CVAT: pristimantis_penelopus)

*Rana pequeña-mediana de desarrollo directo, grupo P. unistrigatus, norte de Colombia. Machos 24.5â€“28.8 mm LHC, hembras 30.1â€“38.4 mm LHC.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| hocico.forma | redondeado | dorsal: redondeado o subacuminado; perfil: redondeado o truncado |
| hocico.canto_rostral | indefinido | redondeado a angulado, nunca agudo |
| ojo.tamano_relativo | grande | moderadamente grande y prominente; diámetro mayor que la distancia ojo-narina |
| timpano.visibilidad | visible | pequeño y circular |
| timpano.tamano_relativo_ojo | menor | ~1/3 a 1/4 del diámetro del ojo |
| glandulas_pliegues.tipo | pliegue_supratimpanico | débil o ausente; sin crestas craneales ni pliegues dorsolaterales |
| glandulas_pliegues.prominencia | leve | cuando presente, descrito como débil |
| dorso_flancos.textura | granulosa | dorso finamente granular, flancos fuertemente granulares |
| dorso_flancos.color_base | marron_pardo | muy variable: pardo amarillento pálido a pardo oscuro, o grisáceo |
| dorso_flancos.patron | manchado | marca en "W" o X interrumpida escapular; banda interorbital; barras oblicuas en los flancos |
| vientre.color_base | blanco_crema | crema o amarillento pálido |
| vientre.patron | liso | generalmente uniforme, sin manchas oscuras (a veces teñido de pardo hacia la garganta) |
| dedos.presencia_discos | presente_grande | discos grandes y bien desarrollados, más anchos que largos, con reborde lateral |
| palmeadura (posterior).grado | ausente | dedos del pie libres, unidos solo en la base por un pliegue pequeño |
| tuberculo_metatarsal.presencia | presente | interno ovalado, moderado (2-3x el externo); externo pequeño y redondeado |
| tuberculo_metatarsal.forma | redondeado | ambos tubérculos redondeados, no tipo pala |


**Fuente(s):** *Lynch & Rueda-Almonacid (1999), descripción original · revisiones taxonómicas posteriores â€” aportado por el equipo*

**Pristimantis taeniatus** (valor CVAT: pristimantis_taeniatus)

*Rana de lluvia de desarrollo directo, de Panamá central a través del Chocó y los Andes colombianos (Boulenger, 1912); tolerante a hábitats alterados.*


| **Aviso** Existe una morfa rayada minoritaria (~10%) â€” no asumas rayado solo por el nombre de la especie. |  |  |
| --- | --- | --- |
| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| dorso_flancos.color_base | marron_pardo | consistente |
| dorso_flancos.patron | manchado | morfa dominante (~90%): motas oscuras formando un patrón occipital en "W" |
| dorso_flancos.linea_vertebral | ausente | en la morfa dominante â€” existe una morfa rayada minoritaria |
| dorso_flancos.textura | granulosa | lisa hacia adelante, granulosa hacia atrás â€” valor más cercano para la región diagnóstica |
| palmeadura (anterior).grado | ausente | sin membrana entre dedos |
| palmeadura (posterior).grado | ausente | sin membrana entre dedos |


**Fuente(s):** *Wikipedia â€” Pristimantis taeniatus · AmphibiaWeb sp/3234 (listado, no accesible directamente)*

**Pristimantis vilarsi** **â€” Ranita Selvática Comàºn** (valor CVAT: pristimantis_vilarsi)

*Rana pequeña a mediana, terrestre y nocturna, asociada a la hojarasca de la selva amazónica. Perfil típico aportado por el equipo; confirma siempre los rasgos variables en la fotografía concreta.*


| **Etiqueta.atributo** | **Valor** | **Nota / respaldo** |
| --- | --- | --- |
| cabeza.forma_general | ancha | moderadamente ancha, ovalada o ligeramente triangular; confirma segàºn el ángulo de la foto |
| hocico.forma | subacuminado | visto dorsalmente puntiagudo o subacuminado; de perfil redondeado o truncado |
| hocico.canto_rostral | definido | casi recto |
| ojo.tamano_relativo | grande | moderadamente grande y prominente |
| ojo.color_iris | bronce | generalmente bronce o cobrizo, con posible reticulación oscura y franja horizontal clara; confirma el color en la foto |
| timpano.visibilidad | visible | distinto, ovalado o circular |
| timpano.tamano_relativo_ojo | menor | aproximadamente 1/2 a 2/3 del diámetro del ojo |
| dorso_flancos.color_base | marron_pardo | muy variable: marrón claro a chocolate oscuro o grisáceo |
| dorso_flancos.patron | manchado | moteado irregular, posible marca interescapular en W invertida, máscara facial oscura y barras oblicuas en los flancos |
| dorso_flancos.textura | granulosa | dorso liso a finamente granuloso; flancos fuertemente granulares |
| dorso_flancos.linea_vertebral | ausente | usualmente ausente, aunque puede aparecer una línea fina y pálida |
| vientre.color_base | blanco_crema | blanco crema o amarillento pálido; visible solo en vista ventral |
| vientre.patron | liso | generalmente liso o finamente moteado, sobre todo en garganta y pecho |
| dedos.presencia_discos | presente_pequeno | discos pequeños pero evidentes en manos y pies |
| palmeadura (anterior).grado | ausente | dedos de la mano sin membrana interdigital |
| palmeadura (posterior).grado | ausente | dedos del pie libres; pueden presentar rebordes laterales estrechos |
| tuberculo_metatarsal.presencia | presente | tubérculo interno ovalado y prominente; externo pequeño y redondeado |
| tuberculo_metatarsal.forma | redondeado | tubérculos metatarsales redondeados |


**Fuente(s):** *Descripción morfológica aportada por el equipo; pendiente de cotejo con una fuente taxonómica primaria*



