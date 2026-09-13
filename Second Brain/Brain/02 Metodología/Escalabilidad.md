---
title: "Escalabilidad"
proyecto: Anura
tipo: metodologÃ­a
estado: redactado
tags: [anura, metodologÃ­a, escalabilidad, versionado, mlops]
---

# Escalabilidad

[[Anura â€” Ãndice General]] Â· [[Base Vectorial (SQLite-vec)]] Â· [[Ciclo de Vida del Modelo (MLOps)]] Â· [[Open-Set Recognition]] Â· [[Infraestructura]]

> [!abstract] La promesa de la arquitectura
> El diseÃ±o de Anura permite **crecer sin reentrenar**. Es la ventaja principal de basarse en embeddings + base vectorial en lugar de un clasificador cerrado, y conviene entender exactamente hasta dÃ³nde llega esa promesa y dÃ³nde deja de cumplirse.

## 1. AÃ±adir una especie nueva: los tres niveles

No todas las incorporaciones cuestan lo mismo. Distinguirlo evita reentrenamientos innecesarios y tambiÃ©n falsas expectativas.

### Nivel 1 â€” Solo base vectorial (horas)

```
Especie nueva (con imÃ¡genes validadas)
        â†“
BioCLIP (sin tocar) â†’ embeddings
        â†“
Alta en la base vectorial + ficha tÃ©cnica + plantilla morfolÃ³gica
        â†“
Nuevo paquete regional â†’ descarga
```

QuÃ© gana el sistema: bÃºsqueda por similitud contra esa especie, ficha tÃ©cnica, y que deje de aparecer como "desconocida". **No** aparece todavÃ­a en las cabezas de clasificaciÃ³n jerÃ¡rquica.

Es el camino habitual y el que hace realista mantener el catÃ¡logo al dÃ­a.

### Nivel 2 â€” Reentrenar las cabezas (horas)

Los embeddings ya estÃ¡n cacheados; solo se reentrenan las capas lineales de Familia/GÃ©nero/Especie. Barato: minutos de cÃ³mputo. Ahora la especie sÃ­ participa en la clasificaciÃ³n y en el Top-3.

Cadencia razonable: cuando se acumulen varias especies nuevas o suficiente material nuevo de las existentes.

### Nivel 3 â€” Reentrenar el backbone (dÃ­as)

Solo se justifica cuando:
- Se han incorporado muchas especies o mucho volumen nuevo.
- Aparece un grupo taxonÃ³mico que el espacio actual separa mal (por ejemplo, un gÃ©nero crÃ­ptico entero).
- Se cambia de versiÃ³n de BioCLIP.

> [!warning] Cambiar el backbone invalida toda la base vectorial
> Un embedding de un modelo no es comparable con el de otro. Reentrenar el backbone obliga a **reindexar todas las observaciones** y a distribuir paquetes nuevos a todos los dispositivos. Es una operaciÃ³n costosa y disruptiva: hay que planificarla, no improvisarla, y agrupar varios cambios en una misma versiÃ³n mayor.

## 2. Versionado

Tres cosas se versionan por separado y sus versiones deben viajar juntas en cada predicciÃ³n:

```
modelo_vision   v1.2   (backbone + cabezas)
dataset         v3      (splits congelados)
paquete_region  antioquia_v5
```

Esquema recomendado, tipo semÃ¡ntico:

| Cambio | Incremento | Consecuencia |
| --- | --- | --- |
| Nuevas fichas, correcciones de texto | patch (1.2.**1**) | Nada que reindexar |
| Especies nuevas, cabezas reentrenadas | minor (1.**3**.0) | Paquete nuevo; embeddings siguen valiendo |
| Backbone distinto o dimensiÃ³n distinta | **major (2**.0.0) | Reindexado completo, incompatible con paquetes previos |

Toda predicciÃ³n guardada debe llevar `version_modelo` y `version_dataset` ([[API Backend]] Â§3). Sin eso, dentro de seis meses serÃ¡ imposible saber si una identificaciÃ³n errÃ³nea del histÃ³rico fue un fallo real o una versiÃ³n antigua.

Y un requisito operativo: **el servidor debe seguir aceptando datos de versiones anteriores** durante un tiempo. Un investigador puede estar tres semanas en campo con la versiÃ³n anterior instalada; rechazar su sincronizaciÃ³n serÃ­a perder trabajo irreemplazable.

## 3. Crecimiento del Ã­ndice vectorial

| Volumen | SituaciÃ³n | Estrategia |
| --- | --- | --- |
| < 10 k | Estado actual | Ãndice Ãºnico, sin optimizaciones |
| 10 k â€“ 100 k | AdopciÃ³n inicial | HNSW ajustado, cuantizaciÃ³n escalar |
| 100 k â€“ 1 M | Uso comunitario real | Particionar por regiÃ³n; cuantizaciÃ³n binaria para el primer filtrado |
| > 1 M | Escala tipo iNaturalist | Sharding, Ã­ndice jerÃ¡rquico, reindexado incremental |

En el dispositivo la escala es distinta y no crece igual: el paquete regional se mantiene en el orden de miles a decenas de miles de vectores por diseÃ±o. Si un paquete regional creciera demasiado, la respuesta correcta es **partirlo en subregiones**, no comprimirlo mÃ¡s.

Una decisiÃ³n que evita el problema antes de tenerlo: al Ã­ndice global solo entran **observaciones validadas**, y para las especies muy fotografiadas se puede limitar el nÃºmero de ejemplares representativos (submuestreo por diversidad, no por orden de llegada). El Ã­ndice es una *memoria curada*, no un archivo de todo lo que ha pasado por la app.

## 4. Escalar el catÃ¡logo: del alcance actual a las 911 especies

El [[Objetivos y Alcance|alcance]] declara explÃ­citamente que no se cubrirÃ¡ toda la anurofauna nacional. La ruta de crecimiento realista:

```
Etapa I     10-15 especies    validaciÃ³n del mÃ©todo
Etapa II    ~30 especies      cobertura Antioquia + Guaviare
Etapa III   50-100 especies   priorizadas por regiÃ³n y disponibilidad de datos
Largo plazo  â†’  crecimiento comunitario continuo
```

El cuello de botella **no es el modelo**: es el dato validado. Por cada especie hacen falta ~70 individuos con verificaciÃ³n taxonÃ³mica, mÃ¡s su ficha morfolÃ³gica del Anexo C. Eso es trabajo de campo y de experto, no de cÃ³mputo. Cualquier plan de crecimiento que ignore esto es irreal.

Fuentes de escalado del dato, en orden de coste creciente por especie: registros pÃºblicos curados (GBIF, iNaturalist con filtrado estricto) â†’ colecciones y museos â†’ colecta propia dirigida a los huecos del catÃ¡logo.

## 5. Escalar personas: el flujo de curadurÃ­a

A partir de cierto volumen, el crecimiento lo sostiene la comunidad, no el equipo. Eso exige que el circuito de validaciÃ³n funcione:

```
Usuario observa â†’ sistema predice â†’ si duda o refuta (HU-03)
        â†“
Cola de revisiÃ³n experta
        â†“
Validada â†’ entra al Ã­ndice â†’ (acumulando) â†’ reentrenamiento periÃ³dico
```

Requisitos para que no se rompa: roles y permisos claros ([[API Backend]]), cola de revisiÃ³n con prioridad (las observaciones marcadas como desconocidas primero, que son las mÃ¡s informativas), y trazabilidad de quiÃ©n validÃ³ quÃ©.

## 6. QuÃ© falta por decidir o medir

- [ ] Fijar el esquema de versionado y aplicarlo desde ya, antes de tener histÃ³rico que migrar.
- [ ] Definir la polÃ­tica de quÃ© entra al Ã­ndice global.
- [ ] Establecer la cadencia de reentrenamiento de cabezas.
- [ ] Definir la ventana de compatibilidad hacia atrÃ¡s para sincronizaciÃ³n.
- [ ] Priorizar las siguientes especies a incorporar segÃºn regiÃ³n y datos disponibles.



