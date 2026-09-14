---
title: "Primeros Pasos en CVAT"
tipo: guía
proyecto: Anura
fuente: "Guia_CVAT_Anuro.docx (v1.0)"
tags: [anura, cvat, anotación, segmentación]
---

# Primeros Pasos en CVAT

â† [[01 Introducción y Objetivo del Proyecto]] · [[Guía CVAT â€” àndice]] · [[03 Jerarquía y Orden de Etiquetado]] â†’

Esta sección cubre el flujo completo desde cero: crear tu cuenta, crear la organización (grupo) del equipo, invitar a los demás integrantes, crear el proyecto Anuro con sus 16 etiquetas, y finalmente crear la tarea con las imágenes a anotar.


### 1.1 Crear una cuenta en CVAT

Paso 1: ingresa al sitio oficial de CVAT (cvat.ai), haz clic en "Try CVAT online" y crea una cuenta con tu correo institucional.


![[cvat-02.png]]
*Figura 1.1 â€” Página de inicio de CVAT ("Data Annotation Platform for Vision AI").*


Una vez creada la cuenta e iniciada sesión, verás la interfaz principal:


![[cvat-03.png]]
*Figura 1.2 â€” Panel principal de CVAT después de iniciar sesión.*


### 1.2 Crear la organización (grupo de trabajo)


> [!note] Importante: solo una persona por pod crea la organización
> Estamos usando la cuenta gratuita de CVAT, y ese plan solo admite 2 personas por organización/workspace. Por eso el equipo se divide en pods de 2 personas, y dentro de cada pod solo UNA persona ejecuta este paso 1.2 y crea la organización â€” la otra persona del pod NO crea una organización nueva, simplemente espera la invitación (paso 1.3). Si todos crean su propia organización terminamos con organizaciones sueltas de una sola persona en vez de pods funcionando.


Si te toca crear la organización de tu pod: ve al menàº de organizaciones y selecciona "Organize" para ver el panel de organizaciones.


![[cvat-04.png]]
*Figura 1.3 â€” Panel de organizaciones.*


Crea la organización de tu pod (por ejemplo "Anuro-Pod1", o el nombre acordado), completa los datos solicitados y confirma con "Crear la organización". Después dale a "Submit".


![[cvat-05.png]]
*Figura 1.4 â€” Formulario de creación de organización.*


### 1.3 Invitar a tu compañero de pod

Con la organización creada, ve al menàº de tu perfil (arriba a la derecha) y entra a "Settings" para llegar al panel de invitaciones.


![[cvat-06.jpg]]
*Figura 1.5 â€” Desde el menàº de perfil, entra a "Settings" para llegar a las invitaciones de la organización.*


Dale al botón "Invite members", pon el nombre de usuario o correo de tu compañero de pod y envía la invitación. Tu compañero debe aceptar la solicitud desde el panel de "Organización e invitación" que le aparece a la derecha â€” no hace falta elegir un rol especial entre ustedes dos; con el rol por defecto que asigna CVAT al invitar ya puede anotar y ver el proyecto.


![[cvat-07.jpg]]
*Figura 1.6 â€” Botón "Invite members" y miembros ya aceptados en la organización.*


### 1.4 Crear el proyecto (workspace) Anuro

Ve al panel superior donde están "Projects", "Tasks" y "Jobs", y entra a "Projects".


![[cvat-08.png]]
*Figura 1.7 â€” Navegación al panel de proyectos.*


Haz clic en el botón azul con el símbolo "+" a la derecha, y elige "Crear nuevo proyecto" (no "Crear desde backup").


![[cvat-09.png]]
*Figura 1.8 â€” Botón para crear un proyecto nuevo.*


Se abrirá un panel pidiendo el nombre del proyecto y las etiquetas. Nómbralo "Anuro" (o el nombre acordado por el equipo).


![[cvat-10.png]]
*Figura 1.9 â€” Panel de creación de proyecto nuevo.*


### 1.5 Configurar las 16 etiquetas (modo Raw)

En el panel de etiquetas del proyecto, ve a la pestaña "Raw" en vez de crear las etiquetas una por una manualmente.


![[cvat-11.png]]
*Figura 1.10 â€” Selector de modo "Raw" para las etiquetas.*


Descarga el JSON desde el enlace del Anexo A, abre el archivo, copia todo su contenido y pégalo en ese campo "Raw". Esto crea las 16 etiquetas (más el atributo especie, ver Anexo A) con sus colores y atributos exactamente como están definidos â€” evita errores de tipeo que ocurrirían creándolas manualmente una por una.


### 1.6 Crear la tarea (Task) y cargar las imágenes

Desde "Crear", ve a la pestaña "Tarea" y haz clic en el botón azul con "+".


![[cvat-12.png]]
*Figura 1.11 â€” Creación de una tarea nueva.*


Ponle un nombre a la tarea, selecciona el proyecto "Anuro" en "Project", y carga las imágenes correspondientes a tu equipo.


> [!note] Reparto de imágenes por equipo
> El trabajo cuenta con un total de 816 imágenes repartidas entre los equipos. Carga àºnicamente el lote asignado a tu equipo, disponible en esta carpeta de Drive: . Si el enlace te pide acceso al abrirlo, avisa a quien administra la carpeta para que la comparta como "Cualquier persona con el enlace".


### 1.7 Configurar el segmento de trabajo (Jobs)

En la pantalla de configuración de la tarea, cambia "Sorting method" a "Natural" y "Segment size" a 82. Esto divide la tarea en jobs de tamaño manejable para que cada persona tenga una porción de trabajo bien delimitada y el servidor no se sature.


![[cvat-13.png]]
*Figura 1.12 â€” Panel de configuración de la tarea (sorting method y segment size).*


Los jobs son las divisiones del trabajo en secciones que se cargan en el servidor, evitando que este colapse con archivos muy grandes.


![[cvat-14.png]]
*Figura 1.13 â€” Ventana de jobs generados para la tarea.*


### 1.8 Abrir un job y conocer la interfaz de etiquetado

Haz clic en el job que te fue asignado para entrar a la interfaz de anotación:


![[cvat-15.png]]
*Figura 1.14 â€” Interior de un job, listo para etiquetar.*


A la izquierda están las herramientas de dibujo. CVAT ofrece dos formas de trazar un polígono, y no son intercambiables â€” usa la que corresponde segàºn el tamaño de la estructura:


| **Herramienta** | **Cuándo usarla** |
| --- | --- |
| Herramienta mágica / IA ("Interact") | Para regiones GRANDES: anuro_completo, cabeza, dorso_flancos, vientre, extremidad_anterior, extremidad_posterior. Ubica la parte, haz clic en "Interact" y deja que el modelo proponga el contorno; ajàºstalo si se sale del borde real. |
| Herramienta de polígono manual | Para estructuras PEQUEà‘AS o de borde fino: ojo, timpano, hocico, glandulas_pliegues, ingle_muslo, saco_vocal, tuberculo_metatarsal, dedos, palmeadura, region_cloacal. La herramienta mágica no es precisa a esta escala â€” traza el polígono punto por punto, con zoom. |


![[cvat-16.png]]
*Figura 1.15 â€” Herramienta de trazado en la barra lateral izquierda de CVAT.*


A la derecha aparece el panel de objetos. Cuando creas una forma nueva, el panel se abre en la pestaña "Label" â€” cámbialo a "Object" para ver y editar los atributos (vista, calidad_enfoque, postura, etc.) segàºn lo que observes en la imagen.


![[cvat-17.png]]
*Figura 1.16 â€” Panel derecho de CVAT: cambiar de "Label" a "Object" para editar atributos.*

> [!note] Guarda tus anotaciones â€” CVAT no autoguarda de forma agresiva
> CVAT tiene autoguardado periódico, pero no reemplaza el guardado manual. Guarda con Ctrl+S (o el botón "Save") cada pocas anotaciones y siempre antes de cerrar el job o cambiar de pestaña. Perder una sesión de etiquetado por no guardar es trabajo que hay que repetir â€” y con solo 2 personas por pod, no sobra tiempo para reanotar.


### 1.9 Video tutorial y más información

Todas las funcionalidades específicas de la interfaz de CVAT (manejo de la herramienta en sí, no el criterio biológico que cubre esta guía) están explicadas en esta lista de reproducción: .


> [!note] Cambia la pista de audio si el video no está en tu idioma
> Algunos videos de la lista pueden tener el audio original en otro idioma. En YouTube, mientras reproduces el video: toca el ícono de engranaje (âš™) o los tres puntos del reproductor â†’ "Pista de audio" (Audio track) â†’ elige "Español" o el idioma en el que te sientas más cómodo/a. Si esa opción no aparece, usa los subtítulos automáticos traducidos (âš™ â†’ Subtítulos â†’ Traducir automáticamente).



