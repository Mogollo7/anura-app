---
title: "Estrategia para Especies con Cobertura Insuficiente"
proyecto: Anura
tipo: metodología
estado: activo
tags: [anura, metodología, dataset, taxonomía, cola-larga, cascada, sqlite-vec]
---

# Estrategia para Especies con Cobertura Insuficiente

[[Anura â€” àndice General]] · [[Estrategia de Construcción del Dataset]] · [[Modelo de Visión â€” BioCLIP]] · [[Base Vectorial (SQLite-vec)]] · [[Open-Set Recognition]]

> [!abstract] El problema en una frase
> Ocho de las 28 especies del catálogo no llegan a los 70 individuos que la [[Estrategia de Construcción del Dataset|estrategia de dataset]] fija como mínimo para identificación, y una de ellas tiene apenas 11. La salida no es inflar el dataset con material de dudosa calidad ni fingir una precisión que no se tiene: es **dejar que el sistema responda al nivel taxonómico que la evidencia sí sostiene**.

## 1. El argumento central: la escasez es de especie, no de género ni de familia

Es la observación que hace viable todo lo demás. Una especie con 11 individuos es un problema de grano fino, pero esos mismos 11 individuos son **11 ejemplos más de su género y 11 más de su familia**, donde el agregado es holgado.

Conteos efectivos tras aplicar el tope de 70 observaciones por especie (`training/analizar_cobertura.py`):

| Especie | Individuos | Su género | Su familia | Rescate |
| --- | ---: | ---: | ---: | --- |
| *Dendropsophus norandinus* | 11 | **268** (Dendropsophus) | **673** (Hylidae) | âœ… género |
| *Hyloxalus picachos* | 22 | 22 (género monoespecífico aquí) | **92** (Dendrobatidae) | âœ… familia |
| *Sachatamia electrops* | 23 | 23 | 23 (Centrolenidae) | âŒ **huérfana** |
| *Pristimantis vilarsi* | 33 | **313** | **313** | âœ… parcial |
| *Phyllomedusa tarsius* | 45 | 45 | **115** | âœ… parcial |
| *Dendropsophus reticulatus* | 51 | **268** | **673** | âœ… parcial |
| *Boana xerophylla* | 55 | **265** | **673** | âœ… parcial |
| *Dendropsophus triangulum* | 66 | **268** | **673** | âœ… parcial |

**27 de 28 especies quedan cubiertas por la jerarquía.** Solo *Sachatamia electrops* se queda sin red: es la àºnica centrolénida del catálogo, así que ni su género ni su familia acumulan datos de ninguna otra especie (§5).

Esto no es un apaño: es exactamente para lo que sirve una arquitectura jerárquica, y es defendible ante un jurado porque la alternativa â€”predecir especie siempre, con la confianza que seaâ€” produce errores más caros que una abstención informada. A un herpetólogo, *"Dendropsophus, género seguro"* le sirve; una especie equivocada afirmada con aplomo, no: le hace desconfiar de todo el sistema.

## 2. Por qué la Multi-Head Loss ya está haciendo este trabajo

La pérdida de destilación (C-8 en [[Inconsistencias y Decisiones Pendientes]]) entrena tres cabezas **en paralelo**, no en cascada:

$$\mathcal{L} = \alpha \sum_{n \in \{fam, gen, esp\}} \mathcal{L}_{CE}^{(n)} + (1-\alpha)\, T^2 \sum_{n} D_{KL}^{(n)}$$

Consecuencia que importa aquí: cada imagen produce **tres gradientes**. La foto de *D. norandinus* es una señal débil para la cabeza de especie (11 individuos) pero una señal fuerte para la de género (268) y muy fuerte para la de familia (673). No hay ninguna foto desperdiciada, y las especies de la cola contribuyen a que el modelo aprenda bien los niveles superiores â€” de los que ellas mismas se beneficiarán en inferencia.

Esto también explica por qué **no** se usa ponderación por inversa de frecuencia pura. Multiplicar por ~6 el gradiente de una clase de 11 individuos fuerza al modelo a memorizarlos para poder reportarlos, que es justo lo que la política de §3 dice que no hay que hacer. Se usa amortiguación en raíz cuadrada (`pesos_de_clase` en `train_student.py`): compensa el desbalance sin exigirle al softmax una frontera que esos individuos no sostienen.

## 3. Techo de resolución por especie

Cada especie recibe un **nivel máximo que el sistema puede afirmar sobre ella**, derivado de su cobertura (`training/politica_resolucion.json`):

| Nivel | Criterio | Qué afirma el sistema | Especies |
| --- | --- | --- | ---: |
| **A** | â‰¥ 70 individuos | Especie, umbral de confianza estándar | 20 |
| **B** | 30â€“69 individuos | Especie, **umbral más exigente** | 5 |
| **C** | < 30, pero género o familia â‰¥ 70 | **Nunca especie por softmax** â€” baja a género o familia | 2 |
| **D** | < 30 y sin rescate jerárquico | Familia, y candidata natural a open-set | 1 |

Los umbrales de arranque (A: 0,50 · B: 0,70) **no son definitivos**: se recalibran en validación junto con el umbral open-set mediante *temperature scaling*, tarea del 17 sep del [[Cronograma y Plan de Trabajo|cronograma]]. Fijarlos a ojo y no volver a mirarlos sería el error clásico.

Implementado en `training/cascada.py`, junto con el **enmascarado jerárquico** que impide predicciones taxonómicamente imposibles (Familia = Hylidae con Especie = *Rhinella horribilis*), segàºn [[Modelo de Visión â€” BioCLIP]] §4.

## 4. Por qué la base vectorial cubre la cola mejor que el softmax

Aquí está la segunda mitad de la estrategia, y es la razón por la que el diseño de [[Base Vectorial (SQLite-vec)|sqlite-vec]] con columnas taxonómicas separadas no es un detalle de implementación sino parte del método.

Una cabeza softmax ajustada sobre 8 individuos de entrenamiento aprende una frontera de decisión mal calibrada: no tiene ejemplos suficientes para saber dónde termina la clase. Una bàºsqueda k-NN sobre embeddings de referencia, en cambio, **solo necesita que el vecino más cercano sea correcto** â€” no tiene que estimar ninguna frontera. Para la cola larga, esa diferencia es decisiva.

De ahí el reparto de responsabilidades:

```
Niveles A y B  â†’  cabezas softmax (especie directa)
Niveles C y D  â†’  k-NN en sqlite-vec contra embeddings de referencia,
                  con respaldo por columna `genero` / `familia`
```

El esquema ya previsto lo soporta sin cambios, porque la taxonomía vive en columnas, no embebida en el nombre de la clase:

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

Eso permite la consulta en cascada en el dispositivo: buscar vecinos a nivel de especie y, si la similitud queda en zona gris, **reagrupar los mismos vecinos por `genero` o `familia`** y responder a ese nivel. No hace falta un índice distinto por nivel taxonómico ni un segundo modelo: es un `GROUP BY` sobre el resultado que ya se tiene.

Encaja además con el patrón "estilo Merlin" de paquetes regionales (C-6): añadir individuos de referencia de una especie escasa es **actualizar un `.sqlite`**, no reentrenar ni reempaquetar el APK. Es la vía de mejora continua más barata que tiene el proyecto, y conviene decirlo así en el documento.

## 5. El caso huérfano: *Sachatamia electrops*

Es la àºnica especie sin rescate jerárquico: 23 individuos, àºnico representante de *Sachatamia* y de Centrolenidae en el catálogo. Opciones, no excluyentes:

1. **Complementar con fuente secundaria** â€” iNaturalist/GBIF filtrado por calidad y coordenadas verificables, la vía ya prevista en [[Estrategia de Construcción del Dataset]]. Es la más directa: subirla de 23 a ~70 la mueve a nivel B.
2. **Incorporar otra centrolénida al catálogo** â€” daría a Centrolenidae el agregado que hoy no tiene y convertiría el rescate familiar en real. Cambia el alcance de las 28 especies (C-3), así que es decisión de proyecto, no técnica.
3. **Tratarla como caso de open-set** â€” dejar que el detector de [[Open-Set Recognition]] la marque como "no registrada con confianza" en vez de forzar una afirmación. Es la opción honesta si no da tiempo a 1 ni a 2 antes del 27 de septiembre.

> [!note] Un matiz biológico a favor
> Las centrolénidas ("ranas de cristal") tienen un carácter diagnóstico muy marcado â€”piel ventral translàºcida con vísceras visiblesâ€” que las separa del resto del catálogo con poca ambigüedad morfológica. Es razonable esperar que 23 individuos rindan mejor de lo que su nàºmero sugiere. Pero **es una hipótesis, no un resultado**: hay que medirla en el conjunto de test antes de apoyarse en ella, y si se cumple, vale la pena reportarla como hallazgo.

## 6. Cómo se reporta esto en el trabajo de grado

Un Top-1 de especie plano sobre las 28 clases oculta exactamente lo que este diseño hace bien. Las métricas que hay que dar, en [[Métricas Offline]] y [[Experimentos y Resultados]]:

| Métrica | Qué mide | Por qué |
| --- | --- | --- |
| Top-1 / Top-3 de especie | Rendimiento de grano fino | Comparable con la literatura |
| **Acierto en el nivel afirmado** | ¿Es correcto lo que el sistema realmente respondió? | Es lo que recibe el usuario; una respuesta de género correcta **cuenta como acierto** |
| Distribución de niveles afirmados | % de respuestas a nivel especie / género / familia | Mide cuánto se abstiene el sistema â€” si se abstiene siempre, la cascada es inàºtil |
| Consistencia taxonómica | % de predicciones jerárquicamente válidas | Credibilidad ante un herpetólogo |
| Desglose por nivel A/B/C/D | Rendimiento segregado por cobertura | Demuestra que la política es necesaria, no decorativa |

Las cuatro primeras ya las calcula `evaluar()` en `training/train_student.py`.

> [!warning] La trampa que hay que evitar al reportar
> El "acierto en el nivel afirmado" se puede inflar trivialmente bajando siempre a familia: con 9 familias, acertar es fácil. Por eso **nunca se reporta solo**, siempre junto a la distribución de niveles afirmados. Las dos cifras juntas son honestas; cada una por separado, no.

## 7. Qué falta por decidir o medir

- [ ] Decidir el destino de *Sachatamia electrops* (§5, opciones 1â€“3) â€” antes del 18 sep para que dé tiempo a recolectar si se elige la 1.
- [ ] Recalibrar los umbrales A/B en validación con *temperature scaling* (17 sep, junto con open-set).
- [ ] Medir si el rescate por género de *D. norandinus* funciona de verdad: ¿acierta el género cuando falla la especie?
- [ ] Verificar la hipótesis morfológica de las centrolénidas (§5, nota).
- [ ] Decidir si las especies de nivel C/D entran en los paquetes regionales `.sqlite` con **más** vectores de referencia por individuo para compensar (la vía k-NN de §4).

## Archivos de implementación

```
training/analizar_cobertura.py      â†’ asigna niveles y escribe politica_resolucion.json
training/politica_resolucion.json   â†’ la política, versionada
training/cascada.py                 â†’ enmascarado jerárquico + cascada de decisión
training/train_student.py           â†’ pesos amortiguados + métricas de cascada
```



