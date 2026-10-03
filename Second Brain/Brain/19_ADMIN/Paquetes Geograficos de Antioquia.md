---
title: "Paquetes Geográficos de Antioquia"
tags: [admin, anura, paquetes]
created: 2026-09-25
status: draft
---

# Paquetes Geográficos de Antioquia

Un paquete raíz y nueve subregiones oficiales. Sirven como barrera biogeográfica (Cauca, Magdalena, pisos de las cordilleras, Caribe, Chocó), no como adorno administrativo. Texto territorial: [[Fuente - Arbol de Paquetes de Antioquia]]. Cifras: [[Fuente - Riqueza Teorica de Antioquia]] y [[Especies Entrenables y Huerfanas]].

La unidad que se versiona es la subregión. El piso térmico no crea otro paquete: filtra candidatos en memoria. Decisión en [[Decisiones de Escalabilidad del Admin]].

| Piso | Cota | Uso |
| --- | --- | --- |
| `lowland` | por debajo de 1000 m | Filtro de consulta, no archivo JSON propio |
| `premontane` | 1000–2000 m | Filtro de consulta |
| `montane` | 2000–3000 m | Filtro de consulta |
| `paramo` | por encima de 3000 m | Filtro de consulta |

Ejemplo de la fuente: Caldas, 1800 m carga `01_Valle_de_Aburra` y la gaussiana deja unas 15–20 especies activas. Otra nota habla de 12–30. Son estimaciones, no un censo. Cada centroide de 512 en FP16 pesa 1 KiB, así que 55 especies pesan **55 KiB**. No es 64 KiB: esos 64 KiB son el tamaño de la matriz default 512×64 FP16, y solo mientras esa configuración no cambie.

> [!NOTE] «Zona A / B / C»
> Una fuente dibuja subpaquetes sin nombre debajo de Oriente, Norte y Urabá. No se implementa. El árbol es raíz Antioquia más nueve subregiones, con `parent_id` para poder añadir otro departamento después.

La app puede ofrecer Antioquia y, debajo, casillas por subregión. Una especie generalista se repite en varios paquetes. Por eso **no se suman** las filas para obtener el total del departamento.

## Las nueve subregiones

| Id | Zona | Municipios citados | Cota dominante | Lectura ecológica de la fuente |
| --- | --- | --- | --- | --- |
| 01 | Valle de Aburrá | Medellín, Caldas, Envigado, Bello, Girardota, Barbosa, Sabaneta, Itagüí, La Estrella, Copacabana | 1300–2800 m | Periurbano y ladera. Ejemplos citados: *Pristimantis illex*, *Dendropsophus columbianus*, *Rhinella horribilis* |
| 02 | Oriente | Rionegro, La Ceja, Guarne, Marinilla, El Retiro, Sonsón, Guatapé, San Carlos | 200–3000 m | Altiplano y vertiente al Magdalena |
| 03 | Suroeste | Jardín, Andes, Jericó, Ciudad Bolívar, Támesis, Fredonia, Santa Bárbara | 600–3400 m | Cafetero y Farallones del Citará |
| 04 | Occidente | Santa Fe de Antioquia, Sopetrán, San Jerónimo, Cañasgordas, Dabeiba, Frontino | 500–3800 m | Cañón seco hasta páramo de Frontino |
| 05 | Norte | Santa Rosa de Osos, Belmira, Yarumal, San Pedro de los Milagros, Ituango | 1000–3300 m | Belmira y cañón del Cauca |
| 06 | Nordeste | Amalfi, Anorí, Vegachí, Yolombó, San Roque, Segovia, Remedios | 200–2500 m | Porce, Nechí, transición andina |
| 07 | Magdalena Medio | Puerto Berrío, Puerto Nare, Puerto Triunfo, Yondó, Maceo | 100–600 m | Tierras bajas, Hylidae y Leptodactylidae |
| 08 | Bajo Cauca | Caucasia, El Bagre, Nechí, Tarazá, Zaragoza, Cáceres | 50–400 m | Ciénagas. La fuente escribe «Cacerí»; tratarlo como Cáceres salvo corrección tuya |
| 09 | Urabá | Turbo, Apartadó, Chigorodó, Carepa, Mutatá, Necoclí, Arboletes, Murindó, Vigía del Fuerte | 0–800 m | Chocó y Darién. Dendrobatidae y Centrolenidae |

La fuente del árbol escribe `09_Urabä_Antioqueno` con diéresis. El id estable para el JSON, usado en los ejemplos, es `09_uraba_antioqueno`.

## Dos columnas que no son el mismo número

| Zona | Riqueza teórica (rango) | Centroides estimados en el árbol | Entrenables con foto (punto) |
| --- | --- | --- | --- |
| 01 Aburrá | 25–35 | 20–35 | ~25 |
| 02 Oriente | 50–70 | 45–70 | ~42 |
| 03 Suroeste | 60–80 | 50–80 | ~40 |
| 04 Occidente | 70–90 | 60–90 | ~45 |
| 05 Norte | 45–65 | 40–65 | ~32 |
| 06 Nordeste | 55–80 | 55–80 | ~35 |
| 07 Magdalena Medio | 40–55 | 35–55 | ~38 |
| 08 Bajo Cauca | 35–50 | 30–50 | ~28 |
| 09 Urabá | 90–120 o más | 80–120 o más | ~55 |

Esas columnas vienen de notas distintas. El punto «entrenable» es el que puede volverse centroide. El rango teórico incluye literatura sin foto. Suma prohibida: ver [[Especies Entrenables y Huerfanas]].
