---
title: "Infraestructura"
proyecto: Anura
tipo: metodologÃ­a
estado: propuesta-de-diseÃ±o
tags: [anura, metodologÃ­a, infraestructura, despliegue, costes]
---

# Infraestructura

[[Anura â€” Ãndice General]] Â· [[API Backend]] Â· [[App MÃ³vil]] Â· [[Escalabilidad]] Â· [[Riesgos del Proyecto]]

## 1. La pregunta de fondo: Â¿modelo en servidor o en dispositivo?

La respuesta del proyecto es **ambos**, y no por indecisiÃ³n: son dos fases con requisitos distintos.

| | Fase 1 â€” Web/servidor | Fase 2 â€” Dispositivo |
| --- | --- | --- |
| Motivo | Validar modelos rÃ¡pido, iterar sin publicar versiones de app | Funcionar en campo sin cobertura (RNF-10) |
| Modelo | El mejor disponible (BioCLIP 2 / ViT-L) | Cuantizado y reducido (ViT-B INT8) |
| ActualizaciÃ³n | InstantÃ¡nea, sin tocar clientes | Requiere descargar paquete o publicar versiÃ³n |
| Coste marginal | Por inferencia (GPU) | Cero |
| Latencia | â‰¤ 3 s (RNF-01), depende de la red | â‰¤ 4 s (RNF-02), determinista |
| Privacidad | Las imÃ¡genes salen del dispositivo | No sale nada |

Que el trabajo de campo ocurra en zonas rurales sin cobertura no es un detalle: es el motivo por el que la Fase 2 existe, y es lo que diferencia a Anura de las plataformas que ya existen.

## 2. Entornos

```
DESARROLLO           â†’  PRUEBAS/STAGING        â†’  PRODUCCIÃ“N
local                   rÃ©plica reducida          servicio real
datos sintÃ©ticos        subconjunto anonimizado   datos reales
sin GPU o GPU local     GPU compartida            GPU o CPU optimizada
```

Regla no negociable: **el conjunto de test nunca se toca desde desarrollo**. Cada evaluaciÃ³n contra test debe ser un acto deliberado y registrado ([[Experimentos y Resultados]]), no algo que ocurra en cada iteraciÃ³n; si no, el test deja de ser test.

## 3. Componentes y opciones

| Componente | OpciÃ³n principal | Alternativa | Comentario |
| --- | --- | --- | --- |
| API + Auth + BD | **Supabase** (PostgreSQL) | Postgres autogestionado | Ya decidido en las notas originales; capa gratuita suficiente para el TFG |
| Inferencia | Contenedor con FastAPI + PyTorch | Servicio serverless con GPU | Ver Â§4 |
| Vectores | Qdrant Cloud (capa gratuita) | **pgvector en Supabase** | pgvector evita un servicio mÃ¡s; ver [[API Backend]] Â§2 |
| Ficheros | Supabase Storage | S3 / Cloudflare R2 | R2 no cobra egreso: relevante si se sirven muchas imÃ¡genes |
| Entrenamiento | Google Colab Pro / Kaggle | GPU de la universidad | Colab basta para linear probing; el fine-tuning pide mÃ¡s |
| Seguimiento de experimentos | **MLflow** o Weights & Biases | Hoja de cÃ¡lculo disciplinada | Ver [[Ciclo de Vida del Modelo (MLOps)]] |
| Repositorio | GitHub | GitLab | Con versionado de datos vÃ­a DVC o Git LFS |
| CI/CD | GitHub Actions | â€” | Tests, linter, build del APK |
| MonitorizaciÃ³n | Sentry (errores) + logs | Grafana | Â§5 |

## 4. El coste real estÃ¡ en la GPU de inferencia

Es la partida que puede desbordar el presupuesto de un proyecto universitario, asÃ­ que conviene dimensionarla con honestidad:

- Un contenedor con GPU **encendido 24/7** es la opciÃ³n cara y casi siempre innecesaria en la Fase 1, donde el trÃ¡fico serÃ¡ esporÃ¡dico (pruebas, demos, defensa).
- **CPU es viable** para ViT-B/16 si se acepta una latencia de 1â€“3 s por imagen y baja concurrencia. Para el alcance del TFG probablemente sea suficiente, y reduce el coste a casi cero.
- **Serverless con GPU** (escala a cero) evita pagar por inactividad, a costa de *cold starts* que pueden ser de decenas de segundos â€” inaceptable durante una demostraciÃ³n en vivo.

> [!tip] Estrategia pragmÃ¡tica
> Fase 1 en **CPU** con el modelo cuantizado y una cola para picos. Reservar GPU solo para las campaÃ±as de entrenamiento y para el reprocesado por lotes de la base vectorial. Si en la defensa hace falta latencia garantizada, se enciende una instancia temporal ese dÃ­a.

## 5. MonitorizaciÃ³n: quÃ© vigilar

MÃ¡s allÃ¡ de uptime y errores, un sistema de ML necesita vigilar cosas que un backend normal no:

| SeÃ±al | QuÃ© indica | Umbral de alarma sugerido |
| --- | --- | --- |
| **Tasa de "desconocido"** | Sube â†’ llegan especies fuera del catÃ¡logo, o el modelo se degradÃ³ | DesviaciÃ³n > 20 % sobre la lÃ­nea base |
| **DistribuciÃ³n de confianza** | Se desplaza â†’ *drift* en las imÃ¡genes de entrada | Cambio significativo en la mediana |
| **Tasa de refutaciÃ³n experta** | El modelo se equivoca mÃ¡s de lo esperado | > 15 % de las validadas |
| **DistribuciÃ³n de especies predichas** | Colapso a pocas clases | EntropÃ­a cayendo |
| **Latencia p95** | Cumplimiento del RNF-01 | > 3 s |
| **Fallos de sincronizaciÃ³n** | Datos de campo atascados en dispositivos | Cualquier acumulaciÃ³n persistente |

Las tres primeras son formas de detectar **deriva de datos** (*data drift*), que en este dominio es esperable y no patolÃ³gica: la fauna cambia con la estaciÃ³n, la app se usa en zonas nuevas, los usuarios cambian de telÃ©fono. Lo importante es detectarla y decidir, no evitarla.

## 6. Copias de seguridad y reproducibilidad

Lo que hay que poder recuperar, y que es fÃ¡cil olvidar hasta que se pierde:

- **Base de datos**: copia diaria automÃ¡tica, retenciÃ³n â‰¥ 30 dÃ­as.
- **ImÃ¡genes y audios originales de campo**: son **irremplazables**. No existe una segunda oportunidad de fotografiar ese individuo esa noche. Copia redundante en al menos dos ubicaciones, incluida una fuera del proveedor cloud.
- **Anotaciones de CVAT**: exportar y versionar periÃ³dicamente, no dejarlas viviendo solo dentro de la herramienta. Representan cientos de horas de trabajo humano.
- **Pesos de cada modelo entrenado** que haya producido un resultado reportado, con su configuraciÃ³n exacta.
- **Los splits train/val/test** como listas de identificadores versionadas. Sin esto, ningÃºn resultado es reproducible.

> [!danger] El activo mÃ¡s valioso del proyecto no es el cÃ³digo
> Es el dataset anotado. El cÃ³digo se reescribe en semanas; las anotaciones y las fotos de campo, no.

## 7. QuÃ© falta por decidir o medir

- [ ] Elegir proveedor y regiÃ³n de despliegue (latencia desde Colombia).
- [ ] Decidir pgvector vs. Qdrant Cloud.
- [ ] Fijar presupuesto mensual mÃ¡ximo y alarma de gasto.
- [ ] Definir polÃ­tica de retenciÃ³n de imÃ¡genes originales.
- [ ] Montar copias de seguridad automÃ¡ticas **antes** de acumular datos de campo.



