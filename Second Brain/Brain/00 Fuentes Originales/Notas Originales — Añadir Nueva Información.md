---
title: "Notas Originales â€” AÃ±adir Nueva InformaciÃ³n"
proyecto: Anura
tipo: fuente-original
descripcion: "Bandeja de entrada del autor: preguntas abiertas sobre arquitectura distribuida, reducciÃ³n del modelo para mÃ³vil y uso de claves taxonÃ³micas."
tags: [anura, fuente-original, notas]
---

estas seccion se aÃ±ade nueva infroamcion sobre el poryecto teoria arquiteruta y todo:

Mecanismo de construcciÃ³n del modelo de Inteligencia Artificial: aplicaciÃ³n Anura para dispositivos mÃ³viles.

Arquitectura de sistemas distribuidos:
â€¢ En offline serÃ­a SQLite.
â€¢ En online se utilizarÃ­a PostgreSQL con Supabase para mayor facilidad.

TambiÃ©n se considera como una necesidad obligatoria realizar una sincronizaciÃ³n cuando se pierde conectividad para poder mostrar la base de datos vectorial distribuida y clusterizada. Esto es necesario para poder ubicar segÃºn coordenadas vectoriales el resultado y mejorar asÃ­ el funcionamiento de la aplicaciÃ³n con su precisiÃ³n.

Como se sabe, Anura se basa principalmente en familia, gÃ©nero y especie, lo cual coincide con el mecanismo de ejecuciÃ³n de la base de datos vectorial, pero se desconoce cÃ³mo aplicarlo.



Nota principal:

Se desea organizar el modelo principal de inteligencia artificial y encontrar la ruta mÃ¡s Ã³ptima para reducir su volumen utilizando herramientas de Kotlin (o Core ML/TFLite) para su desarrollo, permitiendo que se pueda utilizar en mÃ³vil.

La idea es que el modelo de IA, basado en BioCLIP/BlockClip, no solamente le dÃ© el resultado de la especie de la rana utilizando Top-3, sino que tambiÃ©n le diga por quÃ© es esa rana utilizando la segmentaciÃ³n semÃ¡ntica activada.

Puntos clave que se deben investigar y profundizar:

1. CÃ³mo se harÃ­a esto, cÃ³mo se integrarÃ­a y cÃ³mo se optimizarÃ­a.
2. CÃ³mo aplicar dentro del proyecto el entrenamiento realizado con las claves taxonÃ³micas que se encuentran en la guÃ­a de segmentaciÃ³n de SBT (montada como documento de Word).

El objetivo es lograr que el modelo escanee la rana y:
â€¢ Le diga quÃ© especie es.
â€¢ Indique que se encontrÃ³ una coincidencia muy alta por sus proporciones.
â€¢ Determine, por ejemplo, si coincide en cierto porcentaje o si es macho o hembra por ciertas caracterÃ­sticas, entre otras anotaciones utilizando la segmentaciÃ³n semÃ¡ntica que hizo durante el entrenamiento.



