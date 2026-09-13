---
title: "Matrices de ConfusiÃ³n"
proyecto: Anura
tipo: evaluaciÃ³n
estado: plantilla-lista-para-resultados
tags: [anura, evaluaciÃ³n, matriz-confusiÃ³n, anÃ¡lisis-error]
---

# Matrices de ConfusiÃ³n

[[Anura â€” Ãndice General]] Â· [[EvaluaciÃ³n y MÃ©tricas â€” Ãndice]] Â· [[MÃ©tricas Offline]] Â· [[Listado de Individuos y Arreglo TaxonÃ³mico]]

> [!abstract] Para quÃ© sirven aquÃ­
> Una mÃ©trica agregada dice *cuÃ¡nto* falla el modelo; la matriz de confusiÃ³n dice *con quÃ© lo confunde*. En un problema taxonÃ³mico eso es mucho mÃ¡s Ãºtil, porque los errores tienen significado biolÃ³gico: confundir dos *Pristimantis* del mismo grupo es esperable; confundir un *Dendrobates* con una *Rhinella* indica un problema serio.

## 1. Las tres matrices

| Nivel | TamaÃ±o | Utilidad |
| --- | --- | --- |
| **Familia** | 8 Ã— 8 | Legible de un vistazo. Errores aquÃ­ son graves. |
| **GÃ©nero** | ~15 Ã— 15 | Nivel mÃ¡s informativo para diagnÃ³stico |
| **Especie** | ~30 Ã— 30 | DifÃ­cil de leer entera; usar la lista de pares confundidos (Â§3) |

Normalizar **por fila** (recall por clase): cada fila suma 100 % y se lee como "de todas las imÃ¡genes reales de X, quÃ© porcentaje fue a cada predicciÃ³n". Con clases desbalanceadas es la Ãºnica lectura honesta.

## 2. Matriz por familia

Familias presentes en el dataset ([[Listado de Individuos y Arreglo TaxonÃ³mico]]): Aromobatidae, Bufonidae, Centrolenidae, Craugastoridae, Dendrobatidae, Hylidae, Leptodactylidae, Strabomantidae.

```
                  Predicho â†’
Real â†“        Arom  Bufo  Cent  Craug Dendr Hylid Lepto Strab
Aromobatidae
Bufonidae
Centrolenidae
Craugastoridae
Dendrobatidae
Hylidae
Leptodactylidae
Strabomantidae
```

*(Pegar aquÃ­ la figura generada: `![[matriz-familia-vX.png]]`)*

## 3. Pares confundidos (mÃ¡s Ãºtil que la matriz de especie completa)

Ordenar por frecuencia descendente. Esta tabla es la agenda de trabajo del proyecto.

| Real | Predicho | Frecuencia | Mismo gÃ©nero | HipÃ³tesis de causa | AcciÃ³n |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

HipÃ³tesis de causa habituales, y quÃ© implica cada una:

| Causa | CÃ³mo se reconoce | AcciÃ³n |
| --- | --- | --- |
| **Similitud morfolÃ³gica real** | Especies del mismo gÃ©nero, crÃ­pticas | Aumentar peso de audio/contexto; caracteres finos |
| **Pocos datos de una clase** | La clase minoritaria absorbe errores | MÃ¡s imÃ¡genes u *oversampling* |
| **Error de etiquetado** | ConfusiÃ³n asimÃ©trica y sistemÃ¡tica | **Revisar el dataset antes de tocar el modelo** |
| **Sesgo de fondo/localidad** | Se confunden especies que comparten sustrato | Diversificar fondos; verificar el split |
| **Calidad de imagen** | Errores concentrados en fotos malas | Reforzar el control de calidad de entrada |
| **Polimorfismo** | Falla solo un morfo de color | Cubrir morfos en el dataset |

> [!warning] El caso *Pristimantis*
> La Etapa I ya mostrÃ³ el patrÃ³n: *P. paisa* (F1 0,86) y *P. penelopus* (F1 0,86) por debajo del resto. Es el gÃ©nero con mÃ¡s especies del dataset, con cripticismo y polimorfismo bien documentados. Es esperable que sea el foco de errores â€” pero antes de asumir que es "dificultad intrÃ­nseca", hay que **descartar error de etiquetado**, que produce exactamente el mismo sÃ­ntoma y se arregla mucho mÃ¡s barato.

## 4. AnÃ¡lisis por tipo de error

No todos los errores cuestan igual. Clasificarlos guÃ­a las decisiones:

| Tipo | DescripciÃ³n | Gravedad |
| --- | --- | --- |
| **IntragenÃ©rico** | Especie equivocada, gÃ©nero correcto | Baja â€” el usuario recibe informaciÃ³n casi correcta |
| **Intrafamiliar** | GÃ©nero equivocado, familia correcta | Media |
| **Interfamiliar** | Familia equivocada | **Alta** â€” indica que el modelo no captÃ³ la morfologÃ­a bÃ¡sica |
| **Falso conocido** | Especie desconocida clasificada como conocida | **CrÃ­tica** â€” contamina la base de datos ([[Open-Set Recognition]]) |
| **Falso desconocido** | Especie conocida rechazada | Baja â€” molesta pero es recuperable |

| Tipo de error | % del total |
| --- | --- |
| IntragenÃ©rico | |
| Intrafamiliar | |
| Interfamiliar | |

Un buen modelo taxonÃ³mico concentra sus errores en la primera fila. Si hay errores interfamiliares significativos, el problema es de representaciÃ³n visual, no de granularidad fina.

## 5. Errores con coste asimÃ©trico

Dos casos donde equivocarse tiene consecuencias mÃ¡s allÃ¡ de la mÃ©trica:

- **Especies venenosas o tÃ³xicas** (Dendrobatidae): la HU-01 promete al usuario comÃºn saber si el animal es peligroso. Un falso negativo aquÃ­ â€” decir "inofensiva" a una especie tÃ³xica â€” es un error de seguridad, no estadÃ­stico. Debe reportarse por separado y tratarse con umbral conservador: ante duda, advertir.
- **Especies amenazadas UICN**: un registro mal identificado de una especie amenazada distorsiona datos de conservaciÃ³n y puede activar la ofuscaciÃ³n geogrÃ¡fica del RNF-13 sobre la especie equivocada.

## 6. Registro de anÃ¡lisis

| Fecha | VersiÃ³n modelo | Hallazgo principal | AcciÃ³n tomada | Efecto observado |
| --- | --- | --- | --- | --- |
| | | | | |

Ver tambiÃ©n: [[Experimentos y Resultados]] Â· [[Estrategia de ConstrucciÃ³n del Dataset]]



