---
title: "Pesos de contexto variables por perfil ecológico"
tags: [fuente, contexto, pesos]
created: 2026-09-25
status: draft
source: "Second Brain/notes/Sí, es totalmente conveniente y, en.md"
---

# Pesos de contexto variables por perfil ecológico

> [!WARNING] Los porcentajes no coinciden con una sola tabla
> Hay rangos (70–80 / 10–15 / 5–10) y un perfil de quebrada 50/20/30 que no está en el documento maestro (allí el generalista es 80/10/10 fijo). El JSON de Oophaga usa 0.85/0.10/0.05. Son plantillas, no la ficha final. Los pesos efectivos viven por especie y por paquete. Ver [[Contradicciones del Modo Administrativo]].

> [!NOTE] Fuente literal
> Transcripción íntegra de `notes/Sí, es totalmente conveniente y, en.md`. No está resumida. Mapa: [[00_Indice_Principal]]. Nodo de trabajo: [[Contexto Ecologico y Pesos]].

Sí, es totalmente conveniente y, en el caso de la herpetología, casi imprescindible. No todas las especies tienen la misma plasticidad ecológica: aplicar el mismo peso de ubicación a una rana generalista que a una especie microendémica de un solo páramo genera errores de clasificación graves.
¿Por qué se necesitan pesos variables por especie?
1. Endémicas de Rango Estrecho vs. Generalistas Cosmopolitas
 * Especie Generalista (Ej. Rhinella horribilis / Sapo común): Habita desde el nivel del mar hasta los 2000\text{ msnm}, en potreros, jardines urbanos, bordes de carretera y bosques.
   * Comportamiento del peso: El GPS y la altitud deben tener un peso bajo o una tolerancia muy ancha. Si el sistema penaliza fuertemente a esta rana por estar en un entorno urbano o a una altitud atípica, descartará una identificación correcta.
 * Especie Microendémica (Ej. una Pristimantis de alta montaña): Existe únicamente en una franja altitudinal de 2800\text{--}3200\text{ msnm} en una serranía específica.
   * Comportamiento del peso: El GPS y la altitud deben tener un peso dominante / restrictivo. Si el GPS marca 500\text{ msnm}, el sistema debe descartar la especie casi al 100\%, sin importar cuánto se parezca la foto visualmente.
2. Especies Crípticas vs. Especies Visualmente Inconfundibles
 * Pares Crípticos (Especies "Gemelas"): Dos especies del mismo género con un 95\% de similitud visual donde el modelo de visión duda continuamente.
   * Comportamiento del peso: Reduce el peso de la similitud visual (w_{\text{visual}}) y aumenta el peso de los variables contextuales (w_{\text{altitud}}, w_{\text{hábitat}}, w_{\text{canto}}). El contexto desempata la identificación.
 * Especies con Aposematismo / Patrón Único (Ej. Oophaga histrionica):
   * Comportamiento del peso: Si el extractor visual arroja un 98\% de similitud con un patrón de coloración inconfundible, el peso de la imagen (w_{\text{visual}}) debe predominar, absorbiendo pequeños desfases o imprecisiones en el sensor GPS del celular.
3. Especialistas Estrictas de Microhábitat
 * Para ranas de cristal (familia Centrolenidae), la presencia de vegetación adyacente a corrientes de agua (quebradas) es un requisito biológico obligatorio.
   * Comportamiento del peso: En estas especies, el parámetro de microhábitat ([Cerca a quebrada/agua]) debe llevar un peso multiplicativo alto, mientras que para una rana terrestre de hojarasca el peso del sustrato es mucho más flexible.
Tabla de Configuración de Pesos según el Perfil de la Especie
| Perfil Ecológico de la Especie | Peso Visual (w_v) | Peso GPS/Altitud (w_g) | Peso Microhábitat (w_m) | Estrategia de Ajuste |
|---|---|---|---|---|
| Generalista / Adaptable | 70% – 80% | 10% – 15% | 5% – 10% | Tolerancia geográfica amplia; prima la imagen. |
| Endémica de Alta Montaña | 30% – 40% | 50% – 60% | 10% | Filtro estricto por cota altitudinal y coordenadas. |
| Especie Críptica (Par Confuso) | 35% | 35% | 30% (o canto) | Desempate por variables ecológicas y microhábitat. |
| Especialista de Quebrada | 50% | 20% | 30% | Alta penalización si el sustrato marcado no es acuático/ripario. |
¿Cómo implementarlo elegantemente sin escribir if/else infinitos?
La forma más limpia en software e IA es representar las variables de contexto mediante Distribuciones de Probabilidad Normales (Gaussianas) parametrizadas dentro del JSON de cada especie, en lugar de asignaciones de peso manuales.
En el archivo del paquete geográfico, cada centroide de especie guarda sus propios parámetros de tolerancia:
{
  "taxon_id": "Pristimantis_belmet",
  "centroid_vector": [...],
  "context_parameters": {
    "altitude_mean_msnm": 2950,
    "altitude_std_dev": 120,
    "habitat_weights": {
      "hojarasca": 0.9,
      "bromelia": 0.8,
      "potrero_abierto": 0.05
    }
  }
}

La Fórmula de Puntuación Dinámica:
Donde la probabilidad de la altitud se calcula mediante la función Gaussiana:
 * Para la especie endémica: Su desviación estándar (\sigma_{S_k}) es muy pequeña (ej. \sigma = 120\text{ m}). Si el usuario está a 500\text{ m} de distancia de su rango altitudinal, la probabilidad cae a casi 0, anulando el puntaje final automáticamente.
 * Para la especie generalista: Su desviación estándar (\sigma_{S_k}) es muy grande (ej. \sigma = 1000\text{ m}). Moverse varios cientos de metros apenas afecta la puntuación, dejando que la similitud visual de BioCLIP tome el control.
De esta forma, los pesos se ajustan solos de manera matemática según la estrechez ecológica de cada especie.
