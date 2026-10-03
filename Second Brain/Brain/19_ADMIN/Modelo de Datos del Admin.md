---
title: "Modelo de Datos del Admin"
tags: [admin, anura, datos]
created: 2026-09-25
status: draft
---

# Modelo de Datos del Admin

Reglas para la fase 1 de [[Plan de Construccion del Admin]]. Texto completo en [[Fuente - Modelo de Datos y Reglas del Admin]] y en el árbol de la [[Fuente - Plan de Fases para Construir el Admin]]. El choque de jerarquía está en [[Contradicciones del Modo Administrativo]].

## Cadena que sí se implementa

> [!WARNING] Contradicción detectada: el ASCII de la fase 1 invierte el orden
> Ese diagrama pone Observación encima de Individuo. La sección B de la fuente de reglas, y la prosa de la misma fase 1, dicen lo contrario.
> **Decisión:** la cadena de abajo. El dataset es la membresía versionada. Train y test se parten por individuo. Ver [[Decisiones de Escalabilidad del Admin]].

```text
Especie
└── Individuo
    └── Observación
        └── Fotografía
```

- **Individuo:** el animal. Varias fotos del mismo ejemplar cuelgan del mismo individuo para no colar el mismo bicho en train y en test.
- **Observación:** el evento. Trae `observation_id`, individuo, especie, coordenadas, fecha y fuente. En iNaturalist, una observación puede traer varias fotos. No asumir «1 observación = 1 individuo».
- **Fotografía:** pertenece a una observación y, por esa vía, a un individuo.
- **Dataset:** versión (`antioquia_dataset_2026_09_24` es el ejemplo de las notas). Incluye o excluye fotografías. Borrar una foto mala la saca del entrenamiento y de los datos derivados. La observación original se conserva. Si la observación entera es inválida, salen todas sus imágenes, salen los derivados y queda registrado el motivo.

## Taxonomía y configuración

```text
Familia
└── Género
    └── Especie
        ├── Morfos (pueden cambiar según el paquete)
        ├── Estadios de vida
        ├── Rangos de LRC por especie
        └── Configuración regional por paquete
```

La especiación no es un único juego de morfos para toda la especie. El herpetólogo decide, por paquete, si hay morfos y cuáles. Detalle en [[Morfos y Especiacion Regional]].

## Qué calcula el sistema y qué escribe la persona

| Dato | Quién lo pone | Regla |
| --- | --- | --- |
| Municipio, subregión, paquete, altitud | Calculados desde coordenadas | El herpetólogo puede corregir |
| Estadio de vida | Manual en la primera versión | Adulto, juvenil, metamórfico, larva, desconocido |
| Rango de LRC | Por especie, no global | Método: manual, regla LRC, o pendiente |
| Morfo | Herpetólogo | Distinto por paquete |
| Pesos `wv`, `wg`, `wm` | Herpetólogo, por especie y paquete | El sistema puede sugerir revisión; no pisa el valor manual |
| Complejo críptico | Herpetólogo | El sistema solo alerta si dos especies quedan muy cerca |
| Centroides, embeddings, τ, épsilon | Worker | La persona valida o ajusta |

Flujo territorial automático, con OpenTopoData **mock** al principio:

```text
Coordenadas → limpieza → altitud → polígono → municipio → subregión → paquete
```

La pantalla muestra «datos calculados» y deja corregir.

La LRC no decide sola el estadio: hay solapamiento entre especies. Sexo (macho / hembra) queda reservado para cuando existan datos, no para la primera versión.

## Qué cambio obliga a recalcular

| Si cambia | Embeddings y centroides |
| --- | --- |
| Nombre común | No se recalculan |
| Imágenes, taxonomía, Morph ID, membresía del dataset | Pueden invalidar las etapas de abajo |

El Admin tiene que saber la dependencia. No se rehace todo el paquete por un cambio administrativo.

## Paquete, como objeto

```text
Antioquia
└── Paquete (una de las 9 subregiones)
    └── Especie en ese paquete
        ├── Centroide regional
        ├── Morfos / sub-centroides
        ├── Contexto ecológico
        └── Configuración OSR
```

El centroide global de la especie no se elimina. Convive con el regional y con el de morfo. Ver [[Centroides y Muestras]].

## Versionado de un release

Ejemplo tal como está en la fuente, no como versión ya publicada:

- Paquete: `09_uraba_antioqueno`
- Versión: `3.2.0`
- Dataset: `antioquia_dataset_2026_09_24`
- Experimento: `EXP-0042`
- Encoder: `BioCLIP-1-frozen`
- Centroides: `CENT-2026-09-25`
- OSR: `OSR-2026-09-25`
- Estado: `APPROVED`

Estados de especie y de release: [[Modo Administrativo]].

## Alerta que no decide

Ejemplo de la fuente: *Pristimantis* A en 0,61 y *Pristimantis* B en 0,58. El Admin avisa «alta similitud». El herpetólogo elige si crea o actualiza el complejo. Nadie más.

Los requisitos tampoco son iguales para todas las especies. Una puede no tener morfos, ni juveniles, ni complejo. Otra puede tener los tres. La ficha lo declara. Ver [[Entradas y Ficha de Especie]].
