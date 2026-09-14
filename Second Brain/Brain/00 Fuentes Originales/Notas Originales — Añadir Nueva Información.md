---
title: "Notas Originales â€” Añadir Nueva Información"
proyecto: Anura
tipo: fuente-original
descripcion: "Bandeja de entrada del autor: preguntas abiertas sobre arquitectura distribuida, reducción del modelo para móvil y uso de claves taxonómicas."
tags: [anura, fuente-original, notas]
---

estas seccion se añade nueva infroamcion sobre el poryecto teoria arquiteruta y todo:

Mecanismo de construcción del modelo de Inteligencia Artificial: aplicación Anura para dispositivos móviles.

Arquitectura de sistemas distribuidos:
â€¢ En offline sería SQLite.
â€¢ En online se utilizaría PostgreSQL con Supabase para mayor facilidad.

También se considera como una necesidad obligatoria realizar una sincronización cuando se pierde conectividad para poder mostrar la base de datos vectorial distribuida y clusterizada. Esto es necesario para poder ubicar segàºn coordenadas vectoriales el resultado y mejorar así el funcionamiento de la aplicación con su precisión.

Como se sabe, Anura se basa principalmente en familia, género y especie, lo cual coincide con el mecanismo de ejecución de la base de datos vectorial, pero se desconoce cómo aplicarlo.



Nota principal:

Se desea organizar el modelo principal de inteligencia artificial y encontrar la ruta más óptima para reducir su volumen utilizando herramientas de Kotlin (o Core ML/TFLite) para su desarrollo, permitiendo que se pueda utilizar en móvil.

La idea es que el modelo de IA, basado en BioCLIP/BlockClip, no solamente le dé el resultado de la especie de la rana utilizando Top-3, sino que también le diga por qué es esa rana utilizando la segmentación semántica activada.

Puntos clave que se deben investigar y profundizar:

1. Cómo se haría esto, cómo se integraría y cómo se optimizaría.
2. Cómo aplicar dentro del proyecto el entrenamiento realizado con las claves taxonómicas que se encuentran en la guía de segmentación de SBT (montada como documento de Word).

El objetivo es lograr que el modelo escanee la rana y:
â€¢ Le diga qué especie es.
â€¢ Indique que se encontró una coincidencia muy alta por sus proporciones.
â€¢ Determine, por ejemplo, si coincide en cierto porcentaje o si es macho o hembra por ciertas características, entre otras anotaciones utilizando la segmentación semántica que hizo durante el entrenamiento.



