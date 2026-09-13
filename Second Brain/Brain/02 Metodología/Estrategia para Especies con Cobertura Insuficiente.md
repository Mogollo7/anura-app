---
title: "Estrategia para Especies con Cobertura Insuficiente"
proyecto: Anura
tipo: metodologÃ­a
estado: activo
tags: [anura, metodologÃ­a, dataset, taxonomÃ­a, cola-larga, cascada, sqlite-vec]
---

# Estrategia para Especies con Cobertura Insuficiente

[[Anura â€” Ãndice General]] Â· [[Estrategia de ConstrucciÃ³n del Dataset]] Â· [[Modelo de VisiÃ³n â€” BioCLIP]] Â· [[Base Vectorial (SQLite-vec)]] Â· [[Open-Set Recognition]]

> [!abstract] El problema en una frase
> Ocho de las 28 especies del catÃ¡logo no llegan a los 70 individuos que la [[Estrategia de ConstrucciÃ³n del Dataset|estrategia de dataset]] fija como mÃ­nimo para identificaciÃ³n, y una de ellas tiene apenas 11. La salida no es inflar el dataset con material de dudosa calidad ni fingir una precisiÃ³n que no se tiene: es **dejar que el sistema responda al nivel taxonÃ³mico que la evidencia sÃ­ sostiene**.

## 1. El argumento central: la escasez es de especie, no de gÃ©nero ni de familia

Es la observaciÃ³n que hace viable todo lo demÃ¡s. Una especie con 11 individuos es un problema de grano fino, pero esos mismos 11 individuos son **11 ejemplos mÃ¡s de su gÃ©nero y 11 mÃ¡s de su familia**, donde el agregado es holgado.

Conteos efectivos tras aplicar el tope de 70 observaciones por especie (`training/analizar_cobertura.py`):

| Especie | Individuos | Su gÃ©nero | Su familia | Rescate |
| --- | ---: | ---: | ---: | --- |
| *Dendropsophus norandinus* | 11 | **268** (Dendropsophus) | **673** (Hylidae) | âœ… gÃ©nero |
| *Hyloxalus picachos* | 22 | 22 (gÃ©nero monoespecÃ­fico aquÃ­) | **92** (Dendrobatidae) | âœ… familia |
| *Sachatamia electrops* | 23 | 23 | 23 (Centrolenidae) | âŒ **huÃ©rfana** |
| *Pristimantis vilarsi* | 33 | **313** | **313** | âœ… parcial |
| *Phyllomedusa tarsius* | 45 | 45 | **115** | âœ… parcial |
| *Dendropsophus reticulatus* | 51 | **268** | **673** | âœ… parcial |
| *Boana xerophylla* | 55 | **265** | **673** | âœ… parcial |
| *Dendropsophus triangulum* | 66 | **268** | **673** | âœ… parcial |

**27 de 28 especies quedan cubiertas por la jerarquÃ­a.** Solo *Sachatamia electrops* se queda sin red: es la Ãºnica centrolÃ©nida del catÃ¡logo, asÃ­ que ni su gÃ©nero ni su familia acumulan datos de ninguna otra especie (Â§5).

Esto no es un apaÃ±o: es exactamente para lo que sirve una arquitectura jerÃ¡rquica, y es defendible ante un jurado porque la alternativa â€”predecir especie siempre, con la confianza que seaâ€” produce errores mÃ¡s caros que una abstenciÃ³n informada. A un herpetÃ³logo, *"Dendropsophus, gÃ©nero seguro"* le sirve; una especie equivocada afirmada con aplomo, no: le hace desconfiar de todo el sistema.

## 2. Por quÃ© la Multi-Head Loss ya estÃ¡ haciendo este trabajo

La pÃ©rdida de destilaciÃ³n (C-8 en [[Inconsistencias y Decisiones Pendientes]]) entrena tres cabezas **en paralelo**, no en cascada:

$$\mathcal{L} = \alpha \sum_{n \in \{fam, gen, esp\}} \mathcal{L}_{CE}^{(n)} + (1-\alpha)\, T^2 \sum_{n} D_{KL}^{(n)}$$

Consecuencia que importa aquÃ­: cada imagen produce **tres gradientes**. La foto de *D. norandinus* es una seÃ±al dÃ©bil para la cabeza de especie (11 individuos) pero una seÃ±al fuerte para la de gÃ©nero (268) y muy fuerte para la de familia (673). No hay ninguna foto desperdiciada, y las especies de la cola contribuyen a que el modelo aprenda bien los niveles superiores â€” de los que ellas mismas se beneficiarÃ¡n en inferencia.

Esto tambiÃ©n explica por quÃ© **no** se usa ponderaciÃ³n por inversa de frecuencia pura. Multiplicar por ~6 el gradiente de una clase de 11 individuos fuerza al modelo a memorizarlos para poder reportarlos, que es justo lo que la polÃ­tica de Â§3 dice que no hay que hacer. Se usa amortiguaciÃ³n en raÃ­z cuadrada (`pesos_de_clase` en `train_student.py`): compensa el desbalance sin exigirle al softmax una frontera que esos individuos no sostienen.

## 3. Techo de resoluciÃ³n por especie

Cada especie recibe un **nivel mÃ¡ximo que el sistema puede afirmar sobre ella**, derivado de su cobertura (`training/politica_resolucion.json`):

| Nivel | Criterio | QuÃ© afirma el sistema | Especies |
| --- | --- | --- | ---: |
| **A** | â‰¥ 70 individuos | Especie, umbral de confianza estÃ¡ndar | 20 |
| **B** | 30â€“69 individuos | Especie, **umbral mÃ¡s exigente** | 5 |
| **C** | < 30, pero gÃ©nero o familia â‰¥ 70 | **Nunca especie por softmax** â€” baja a gÃ©nero o familia | 2 |
| **D** | < 30 y sin rescate jerÃ¡rquico | Familia, y candidata natural a open-set | 1 |

Los umbrales de arranque (A: 0,50 Â· B: 0,70) **no son definitivos**: se recalibran en validaciÃ³n junto con el umbral open-set mediante *temperature scaling*, tarea del 17 sep del [[Cronograma y Plan de Trabajo|cronograma]]. Fijarlos a ojo y no volver a mirarlos serÃ­a el error clÃ¡sico.

Implementado en `training/cascada.py`, junto con el **enmascarado jerÃ¡rquico** que impide predicciones taxonÃ³micamente imposibles (Familia = Hylidae con Especie = *Rhinella horribilis*), segÃºn [[Modelo de VisiÃ³n â€” BioCLIP]] Â§4.

## 4. Por quÃ© la base vectorial cubre la cola mejor que el softmax

AquÃ­ estÃ¡ la segunda mitad de la estrategia, y es la razÃ³n por la que el diseÃ±o de [[Base Vectorial (SQLite-vec)|sqlite-vec]] con columnas taxonÃ³micas separadas no es un detalle de implementaciÃ³n sino parte del mÃ©todo.

Una cabeza softmax ajustada sobre 8 individuos de entrenamiento aprende una frontera de decisiÃ³n mal calibrada: no tiene ejemplos suficientes para saber dÃ³nde termina la clase. Una bÃºsqueda k-NN sobre embeddings de referencia, en cambio, **solo necesita que el vecino mÃ¡s cercano sea correcto** â€” no tiene que estimar ninguna frontera. Para la cola larga, esa diferencia es decisiva.

De ahÃ­ el reparto de responsabilidades:

```
Niveles A y B  â†’  cabezas softmax (especie directa)
Niveles C y D  â†’  k-NN en sqlite-vec contra embeddings de referencia,
                  con respaldo por columna `genero` / `familia`
```

El esquema ya previsto lo soporta sin cambios, porque la taxonomÃ­a vive en columnas, no embebida en el nombre de la clase:

```sql
CREATE TABLE anfibios_vectores (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    especie       TEXT NOT NULL,
    genero        TEXT NOT NULL,
    familia       TEXT NOT NULL,
    zona_anatomica TEXT NOT NULL,
    vector        BLOB NOT NULL
);
```

Eso permite la consulta en cascada en el dispositivo: buscar vecinos a nivel de especie y, si la similitud queda en zona gris, **reagrupar los mismos vecinos por `genero` o `familia`** y responder a ese nivel. No hace falta un Ã­ndice distinto por nivel taxonÃ³mico ni un segundo modelo: es un `GROUP BY` sobre el resultado que ya se tiene.

Encaja ademÃ¡s con el patrÃ³n "estilo Merlin" de paquetes regionales (C-6): aÃ±adir individuos de referencia de una especie escasa es **actualizar un `.sqlite`**, no reentrenar ni reempaquetar el APK. Es la vÃ­a de mejora continua mÃ¡s barata que tiene el proyecto, y conviene decirlo asÃ­ en el documento.

## 5. El caso huÃ©rfano: *Sachatamia electrops*

Es la Ãºnica especie sin rescate jerÃ¡rquico: 23 individuos, Ãºnico representante de *Sachatamia* y de Centrolenidae en el catÃ¡logo. Opciones, no excluyentes:

1. **Complementar con fuente secundaria** â€” iNaturalist/GBIF filtrado por calidad y coordenadas verificables, la vÃ­a ya prevista en [[Estrategia de ConstrucciÃ³n del Dataset]]. Es la mÃ¡s directa: subirla de 23 a ~70 la mueve a nivel B.
2. **Incorporar otra centrolÃ©nida al catÃ¡logo** â€” darÃ­a a Centrolenidae el agregado que hoy no tiene y convertirÃ­a el rescate familiar en real. Cambia el alcance de las 28 especies (C-3), asÃ­ que es decisiÃ³n de proyecto, no tÃ©cnica.
3. **Tratarla como caso de open-set** â€” dejar que el detector de [[Open-Set Recognition]] la marque como "no registrada con confianza" en vez de forzar una afirmaciÃ³n. Es la opciÃ³n honesta si no da tiempo a 1 ni a 2 antes del 27 de septiembre.

> [!note] Un matiz biolÃ³gico a favor
> Las centrolÃ©nidas ("ranas de cristal") tienen un carÃ¡cter diagnÃ³stico muy marcado â€”piel ventral translÃºcida con vÃ­sceras visiblesâ€” que las separa del resto del catÃ¡logo con poca ambigÃ¼edad morfolÃ³gica. Es razonable esperar que 23 individuos rindan mejor de lo que su nÃºmero sugiere. Pero **es una hipÃ³tesis, no un resultado**: hay que medirla en el conjunto de test antes de apoyarse en ella, y si se cumple, vale la pena reportarla como hallazgo.

## 6. CÃ³mo se reporta esto en el trabajo de grado

Un Top-1 de especie plano sobre las 28 clases oculta exactamente lo que este diseÃ±o hace bien. Las mÃ©tricas que hay que dar, en [[MÃ©tricas Offline]] y [[Experimentos y Resultados]]:

| MÃ©trica | QuÃ© mide | Por quÃ© |
| --- | --- | --- |
| Top-1 / Top-3 de especie | Rendimiento de grano fino | Comparable con la literatura |
| **Acierto en el nivel afirmado** | Â¿Es correcto lo que el sistema realmente respondiÃ³? | Es lo que recibe el usuario; una respuesta de gÃ©nero correcta **cuenta como acierto** |
| DistribuciÃ³n de niveles afirmados | % de respuestas a nivel especie / gÃ©nero / familia | Mide cuÃ¡nto se abstiene el sistema â€” si se abstiene siempre, la cascada es inÃºtil |
| Consistencia taxonÃ³mica | % de predicciones jerÃ¡rquicamente vÃ¡lidas | Credibilidad ante un herpetÃ³logo |
| Desglose por nivel A/B/C/D | Rendimiento segregado por cobertura | Demuestra que la polÃ­tica es necesaria, no decorativa |

Las cuatro primeras ya las calcula `evaluar()` en `training/train_student.py`.

> [!warning] La trampa que hay que evitar al reportar
> El "acierto en el nivel afirmado" se puede inflar trivialmente bajando siempre a familia: con 9 familias, acertar es fÃ¡cil. Por eso **nunca se reporta solo**, siempre junto a la distribuciÃ³n de niveles afirmados. Las dos cifras juntas son honestas; cada una por separado, no.

## 7. QuÃ© falta por decidir o medir

- [ ] Decidir el destino de *Sachatamia electrops* (Â§5, opciones 1â€“3) â€” antes del 18 sep para que dÃ© tiempo a recolectar si se elige la 1.
- [ ] Recalibrar los umbrales A/B en validaciÃ³n con *temperature scaling* (17 sep, junto con open-set).
- [ ] Medir si el rescate por gÃ©nero de *D. norandinus* funciona de verdad: Â¿acierta el gÃ©nero cuando falla la especie?
- [ ] Verificar la hipÃ³tesis morfolÃ³gica de las centrolÃ©nidas (Â§5, nota).
- [ ] Decidir si las especies de nivel C/D entran en los paquetes regionales `.sqlite` con **mÃ¡s** vectores de referencia por individuo para compensar (la vÃ­a k-NN de Â§4).

## Archivos de implementaciÃ³n

```
training/analizar_cobertura.py      â†’ asigna niveles y escribe politica_resolucion.json
training/politica_resolucion.json   â†’ la polÃ­tica, versionada
training/cascada.py                 â†’ enmascarado jerÃ¡rquico + cascada de decisiÃ³n
training/train_student.py           â†’ pesos amortiguados + mÃ©tricas de cascada
```



