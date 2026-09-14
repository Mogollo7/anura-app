---
title: "Escalabilidad"
proyecto: Anura
tipo: metodología
estado: redactado
tags: [anura, metodología, escalabilidad, versionado, mlops]
---

# Escalabilidad

[[Anura â€” àndice General]] · [[Base Vectorial (SQLite-vec)]] · [[Ciclo de Vida del Modelo (MLOps)]] · [[Open-Set Recognition]] · [[Infraestructura]]

> [!abstract] La promesa de la arquitectura
> El diseño de Anura permite **crecer sin reentrenar**. Es la ventaja principal de basarse en embeddings + base vectorial en lugar de un clasificador cerrado, y conviene entender exactamente hasta dónde llega esa promesa y dónde deja de cumplirse.

## 1. Añadir una especie nueva: los tres niveles

No todas las incorporaciones cuestan lo mismo. Distinguirlo evita reentrenamientos innecesarios y también falsas expectativas.

### Nivel 1 â€” Solo base vectorial (horas)

```
Especie nueva (con imágenes validadas)
        â†“
BioCLIP (sin tocar) â†’ embeddings
        â†“
Alta en la base vectorial + ficha técnica + plantilla morfológica
        â†“
Nuevo paquete regional â†’ descarga
```

Qué gana el sistema: bàºsqueda por similitud contra esa especie, ficha técnica, y que deje de aparecer como "desconocida". **No** aparece todavía en las cabezas de clasificación jerárquica.

Es el camino habitual y el que hace realista mantener el catálogo al día.

### Nivel 2 â€” Reentrenar las cabezas (horas)

Los embeddings ya están cacheados; solo se reentrenan las capas lineales de Familia/Género/Especie. Barato: minutos de cómputo. Ahora la especie sí participa en la clasificación y en el Top-3.

Cadencia razonable: cuando se acumulen varias especies nuevas o suficiente material nuevo de las existentes.

### Nivel 3 â€” Reentrenar el backbone (días)

Solo se justifica cuando:
- Se han incorporado muchas especies o mucho volumen nuevo.
- Aparece un grupo taxonómico que el espacio actual separa mal (por ejemplo, un género críptico entero).
- Se cambia de versión de BioCLIP.

> [!warning] Cambiar el backbone invalida toda la base vectorial
> Un embedding de un modelo no es comparable con el de otro. Reentrenar el backbone obliga a **reindexar todas las observaciones** y a distribuir paquetes nuevos a todos los dispositivos. Es una operación costosa y disruptiva: hay que planificarla, no improvisarla, y agrupar varios cambios en una misma versión mayor.

## 2. Versionado

Tres cosas se versionan por separado y sus versiones deben viajar juntas en cada predicción:

```
modelo_vision   v1.2   (backbone + cabezas)
dataset         v3      (splits congelados)
paquete_region  antioquia_v5
```

Esquema recomendado, tipo semántico:

| Cambio | Incremento | Consecuencia |
| --- | --- | --- |
| Nuevas fichas, correcciones de texto | patch (1.2.**1**) | Nada que reindexar |
| Especies nuevas, cabezas reentrenadas | minor (1.**3**.0) | Paquete nuevo; embeddings siguen valiendo |
| Backbone distinto o dimensión distinta | **major (2**.0.0) | Reindexado completo, incompatible con paquetes previos |

Toda predicción guardada debe llevar `version_modelo` y `version_dataset` ([[API Backend]] §3). Sin eso, dentro de seis meses será imposible saber si una identificación errónea del histórico fue un fallo real o una versión antigua.

Y un requisito operativo: **el servidor debe seguir aceptando datos de versiones anteriores** durante un tiempo. Un investigador puede estar tres semanas en campo con la versión anterior instalada; rechazar su sincronización sería perder trabajo irreemplazable.

## 3. Crecimiento del índice vectorial

| Volumen | Situación | Estrategia |
| --- | --- | --- |
| < 10 k | Estado actual | àndice àºnico, sin optimizaciones |
| 10 k â€“ 100 k | Adopción inicial | HNSW ajustado, cuantización escalar |
| 100 k â€“ 1 M | Uso comunitario real | Particionar por región; cuantización binaria para el primer filtrado |
| > 1 M | Escala tipo iNaturalist | Sharding, índice jerárquico, reindexado incremental |

En el dispositivo la escala es distinta y no crece igual: el paquete regional se mantiene en el orden de miles a decenas de miles de vectores por diseño. Si un paquete regional creciera demasiado, la respuesta correcta es **partirlo en subregiones**, no comprimirlo más.

Una decisión que evita el problema antes de tenerlo: al índice global solo entran **observaciones validadas**, y para las especies muy fotografiadas se puede limitar el nàºmero de ejemplares representativos (submuestreo por diversidad, no por orden de llegada). El índice es una *memoria curada*, no un archivo de todo lo que ha pasado por la app.

## 4. Escalar el catálogo: del alcance actual a las 911 especies

El [[Objetivos y Alcance|alcance]] declara explícitamente que no se cubrirá toda la anurofauna nacional. La ruta de crecimiento realista:

```
Etapa I     10-15 especies    validación del método
Etapa II    ~30 especies      cobertura Antioquia + Guaviare
Etapa III   50-100 especies   priorizadas por región y disponibilidad de datos
Largo plazo  â†’  crecimiento comunitario continuo
```

El cuello de botella **no es el modelo**: es el dato validado. Por cada especie hacen falta ~70 individuos con verificación taxonómica, más su ficha morfológica del Anexo C. Eso es trabajo de campo y de experto, no de cómputo. Cualquier plan de crecimiento que ignore esto es irreal.

Fuentes de escalado del dato, en orden de coste creciente por especie: registros pàºblicos curados (GBIF, iNaturalist con filtrado estricto) â†’ colecciones y museos â†’ colecta propia dirigida a los huecos del catálogo.

## 5. Escalar personas: el flujo de curaduría

A partir de cierto volumen, el crecimiento lo sostiene la comunidad, no el equipo. Eso exige que el circuito de validación funcione:

```
Usuario observa â†’ sistema predice â†’ si duda o refuta (HU-03)
        â†“
Cola de revisión experta
        â†“
Validada â†’ entra al índice â†’ (acumulando) â†’ reentrenamiento periódico
```

Requisitos para que no se rompa: roles y permisos claros ([[API Backend]]), cola de revisión con prioridad (las observaciones marcadas como desconocidas primero, que son las más informativas), y trazabilidad de quién validó qué.

## 6. Qué falta por decidir o medir

- [ ] Fijar el esquema de versionado y aplicarlo desde ya, antes de tener histórico que migrar.
- [ ] Definir la política de qué entra al índice global.
- [ ] Establecer la cadencia de reentrenamiento de cabezas.
- [ ] Definir la ventana de compatibilidad hacia atrás para sincronización.
- [ ] Priorizar las siguientes especies a incorporar segàºn región y datos disponibles.



