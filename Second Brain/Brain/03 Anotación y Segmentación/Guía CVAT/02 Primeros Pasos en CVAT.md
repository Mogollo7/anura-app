---
title: "Primeros Pasos en CVAT"
tipo: guÃ­a
proyecto: Anura
fuente: "Guia_CVAT_Anuro.docx (v1.0)"
tags: [anura, cvat, anotaciÃ³n, segmentaciÃ³n]
---

# Primeros Pasos en CVAT

â† [[01 IntroducciÃ³n y Objetivo del Proyecto]] Â· [[GuÃ­a CVAT â€” Ãndice]] Â· [[03 JerarquÃ­a y Orden de Etiquetado]] â†’

Esta secciÃ³n cubre el flujo completo desde cero: crear tu cuenta, crear la organizaciÃ³n (grupo) del equipo, invitar a los demÃ¡s integrantes, crear el proyecto Anuro con sus 16 etiquetas, y finalmente crear la tarea con las imÃ¡genes a anotar.


### 1.1 Crear una cuenta en CVAT

Paso 1: ingresa al sitio oficial de CVAT (cvat.ai), haz clic en â€œTry CVAT onlineâ€ y crea una cuenta con tu correo institucional.


![[cvat-02.png]]
*Figura 1.1 â€” PÃ¡gina de inicio de CVAT (â€œData Annotation Platform for Vision AIâ€).*


Una vez creada la cuenta e iniciada sesiÃ³n, verÃ¡s la interfaz principal:


![[cvat-03.png]]
*Figura 1.2 â€” Panel principal de CVAT despuÃ©s de iniciar sesiÃ³n.*


### 1.2 Crear la organizaciÃ³n (grupo de trabajo)


> [!note] Importante: solo una persona por pod crea la organizaciÃ³n
> Estamos usando la cuenta gratuita de CVAT, y ese plan solo admite 2 personas por organizaciÃ³n/workspace. Por eso el equipo se divide en pods de 2 personas, y dentro de cada pod solo UNA persona ejecuta este paso 1.2 y crea la organizaciÃ³n â€” la otra persona del pod NO crea una organizaciÃ³n nueva, simplemente espera la invitaciÃ³n (paso 1.3). Si todos crean su propia organizaciÃ³n terminamos con organizaciones sueltas de una sola persona en vez de pods funcionando.


Si te toca crear la organizaciÃ³n de tu pod: ve al menÃº de organizaciones y selecciona â€œOrganizeâ€ para ver el panel de organizaciones.


![[cvat-04.png]]
*Figura 1.3 â€” Panel de organizaciones.*


Crea la organizaciÃ³n de tu pod (por ejemplo â€œAnuro-Pod1â€, o el nombre acordado), completa los datos solicitados y confirma con â€œCrear la organizaciÃ³nâ€. DespuÃ©s dale a â€œSubmitâ€.


![[cvat-05.png]]
*Figura 1.4 â€” Formulario de creaciÃ³n de organizaciÃ³n.*


### 1.3 Invitar a tu compaÃ±ero de pod

Con la organizaciÃ³n creada, ve al menÃº de tu perfil (arriba a la derecha) y entra a â€œSettingsâ€ para llegar al panel de invitaciones.


![[cvat-06.jpg]]
*Figura 1.5 â€” Desde el menÃº de perfil, entra a â€œSettingsâ€ para llegar a las invitaciones de la organizaciÃ³n.*


Dale al botÃ³n â€œInvite membersâ€, pon el nombre de usuario o correo de tu compaÃ±ero de pod y envÃ­a la invitaciÃ³n. Tu compaÃ±ero debe aceptar la solicitud desde el panel de â€œOrganizaciÃ³n e invitaciÃ³nâ€ que le aparece a la derecha â€” no hace falta elegir un rol especial entre ustedes dos; con el rol por defecto que asigna CVAT al invitar ya puede anotar y ver el proyecto.


![[cvat-07.jpg]]
*Figura 1.6 â€” BotÃ³n â€œInvite membersâ€ y miembros ya aceptados en la organizaciÃ³n.*


### 1.4 Crear el proyecto (workspace) Anuro

Ve al panel superior donde estÃ¡n â€œProjectsâ€, â€œTasksâ€ y â€œJobsâ€, y entra a â€œProjectsâ€.


![[cvat-08.png]]
*Figura 1.7 â€” NavegaciÃ³n al panel de proyectos.*


Haz clic en el botÃ³n azul con el sÃ­mbolo â€œ+â€ a la derecha, y elige â€œCrear nuevo proyectoâ€ (no â€œCrear desde backupâ€).


![[cvat-09.png]]
*Figura 1.8 â€” BotÃ³n para crear un proyecto nuevo.*


Se abrirÃ¡ un panel pidiendo el nombre del proyecto y las etiquetas. NÃ³mbralo â€œAnuroâ€ (o el nombre acordado por el equipo).


![[cvat-10.png]]
*Figura 1.9 â€” Panel de creaciÃ³n de proyecto nuevo.*


### 1.5 Configurar las 16 etiquetas (modo Raw)

En el panel de etiquetas del proyecto, ve a la pestaÃ±a â€œRawâ€ en vez de crear las etiquetas una por una manualmente.


![[cvat-11.png]]
*Figura 1.10 â€” Selector de modo â€œRawâ€ para las etiquetas.*


Descarga el JSON desde el enlace del Anexo A, abre el archivo, copia todo su contenido y pÃ©galo en ese campo â€œRawâ€. Esto crea las 16 etiquetas (mÃ¡s el atributo especie, ver Anexo A) con sus colores y atributos exactamente como estÃ¡n definidos â€” evita errores de tipeo que ocurrirÃ­an creÃ¡ndolas manualmente una por una.


### 1.6 Crear la tarea (Task) y cargar las imÃ¡genes

Desde â€œCrearâ€, ve a la pestaÃ±a â€œTareaâ€ y haz clic en el botÃ³n azul con â€œ+â€.


![[cvat-12.png]]
*Figura 1.11 â€” CreaciÃ³n de una tarea nueva.*


Ponle un nombre a la tarea, selecciona el proyecto â€œAnuroâ€ en â€œProjectâ€, y carga las imÃ¡genes correspondientes a tu equipo.


> [!note] Reparto de imÃ¡genes por equipo
> El trabajo cuenta con un total de 816 imÃ¡genes repartidas entre los equipos. Carga Ãºnicamente el lote asignado a tu equipo, disponible en esta carpeta de Drive: . Si el enlace te pide acceso al abrirlo, avisa a quien administra la carpeta para que la comparta como â€œCualquier persona con el enlaceâ€.


### 1.7 Configurar el segmento de trabajo (Jobs)

En la pantalla de configuraciÃ³n de la tarea, cambia â€œSorting methodâ€ a â€œNaturalâ€ y â€œSegment sizeâ€ a 82. Esto divide la tarea en jobs de tamaÃ±o manejable para que cada persona tenga una porciÃ³n de trabajo bien delimitada y el servidor no se sature.


![[cvat-13.png]]
*Figura 1.12 â€” Panel de configuraciÃ³n de la tarea (sorting method y segment size).*


Los jobs son las divisiones del trabajo en secciones que se cargan en el servidor, evitando que este colapse con archivos muy grandes.


![[cvat-14.png]]
*Figura 1.13 â€” Ventana de jobs generados para la tarea.*


### 1.8 Abrir un job y conocer la interfaz de etiquetado

Haz clic en el job que te fue asignado para entrar a la interfaz de anotaciÃ³n:


![[cvat-15.png]]
*Figura 1.14 â€” Interior de un job, listo para etiquetar.*


A la izquierda estÃ¡n las herramientas de dibujo. CVAT ofrece dos formas de trazar un polÃ­gono, y no son intercambiables â€” usa la que corresponde segÃºn el tamaÃ±o de la estructura:


| **Herramienta** | **CuÃ¡ndo usarla** |
| --- | --- |
| Herramienta mÃ¡gica / IA (â€œInteractâ€) | Para regiones GRANDES: anuro_completo, cabeza, dorso_flancos, vientre, extremidad_anterior, extremidad_posterior. Ubica la parte, haz clic en â€œInteractâ€ y deja que el modelo proponga el contorno; ajÃºstalo si se sale del borde real. |
| Herramienta de polÃ­gono manual | Para estructuras PEQUEÃ‘AS o de borde fino: ojo, timpano, hocico, glandulas_pliegues, ingle_muslo, saco_vocal, tuberculo_metatarsal, dedos, palmeadura, region_cloacal. La herramienta mÃ¡gica no es precisa a esta escala â€” traza el polÃ­gono punto por punto, con zoom. |


![[cvat-16.png]]
*Figura 1.15 â€” Herramienta de trazado en la barra lateral izquierda de CVAT.*


A la derecha aparece el panel de objetos. Cuando creas una forma nueva, el panel se abre en la pestaÃ±a â€œLabelâ€ â€” cÃ¡mbialo a â€œObjectâ€ para ver y editar los atributos (vista, calidad_enfoque, postura, etc.) segÃºn lo que observes en la imagen.


![[cvat-17.png]]
*Figura 1.16 â€” Panel derecho de CVAT: cambiar de â€œLabelâ€ a â€œObjectâ€ para editar atributos.*

> [!note] Guarda tus anotaciones â€” CVAT no autoguarda de forma agresiva
> CVAT tiene autoguardado periÃ³dico, pero no reemplaza el guardado manual. Guarda con Ctrl+S (o el botÃ³n â€œSaveâ€) cada pocas anotaciones y siempre antes de cerrar el job o cambiar de pestaÃ±a. Perder una sesiÃ³n de etiquetado por no guardar es trabajo que hay que repetir â€” y con solo 2 personas por pod, no sobra tiempo para reanotar.


### 1.9 Video tutorial y mÃ¡s informaciÃ³n

Todas las funcionalidades especÃ­ficas de la interfaz de CVAT (manejo de la herramienta en sÃ­, no el criterio biolÃ³gico que cubre esta guÃ­a) estÃ¡n explicadas en esta lista de reproducciÃ³n: .


> [!note] Cambia la pista de audio si el video no estÃ¡ en tu idioma
> Algunos videos de la lista pueden tener el audio original en otro idioma. En YouTube, mientras reproduces el video: toca el Ã­cono de engranaje (âš™) o los tres puntos del reproductor â†’ â€œPista de audioâ€ (Audio track) â†’ elige â€œEspaÃ±olâ€ o el idioma en el que te sientas mÃ¡s cÃ³modo/a. Si esa opciÃ³n no aparece, usa los subtÃ­tulos automÃ¡ticos traducidos (âš™ â†’ SubtÃ­tulos â†’ Traducir automÃ¡ticamente).



