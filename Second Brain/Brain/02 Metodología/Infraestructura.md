---
title: "Infraestructura"
proyecto: Anura
tipo: metodología
estado: propuesta-de-diseño
tags: [anura, metodología, infraestructura, despliegue, costes]
---

# Infraestructura

[[Anura â€” àndice General]] · [[API Backend]] · [[App Móvil]] · [[Escalabilidad]] · [[Riesgos del Proyecto]]

## 1. La pregunta de fondo: ¿modelo en servidor o en dispositivo?

La respuesta del proyecto es **ambos**, y no por indecisión: son dos fases con requisitos distintos.

| | Fase 1 â€” Web/servidor | Fase 2 â€” Dispositivo |
| --- | --- | --- |
| Motivo | Validar modelos rápido, iterar sin publicar versiones de app | Funcionar en campo sin cobertura (RNF-10) |
| Modelo | El mejor disponible (BioCLIP 2 / ViT-L) | Cuantizado y reducido (ViT-B INT8) |
| Actualización | Instantánea, sin tocar clientes | Requiere descargar paquete o publicar versión |
| Coste marginal | Por inferencia (GPU) | Cero |
| Latencia | â‰¤ 3 s (RNF-01), depende de la red | â‰¤ 4 s (RNF-02), determinista |
| Privacidad | Las imágenes salen del dispositivo | No sale nada |

Que el trabajo de campo ocurra en zonas rurales sin cobertura no es un detalle: es el motivo por el que la Fase 2 existe, y es lo que diferencia a Anura de las plataformas que ya existen.

## 2. Entornos

```
DESARROLLO           â†’  PRUEBAS/STAGING        â†’  PRODUCCIà“N
local                   réplica reducida          servicio real
datos sintéticos        subconjunto anonimizado   datos reales
sin GPU o GPU local     GPU compartida            GPU o CPU optimizada
```

Regla no negociable: **el conjunto de test nunca se toca desde desarrollo**. Cada evaluación contra test debe ser un acto deliberado y registrado ([[Experimentos y Resultados]]), no algo que ocurra en cada iteración; si no, el test deja de ser test.

## 3. Componentes y opciones

| Componente | Opción principal | Alternativa | Comentario |
| --- | --- | --- | --- |
| API + Auth + BD | **Supabase** (PostgreSQL) | Postgres autogestionado | Ya decidido en las notas originales; capa gratuita suficiente para el TFG |
| Inferencia | Contenedor con FastAPI + PyTorch | Servicio serverless con GPU | Ver §4 |
| Vectores | Qdrant Cloud (capa gratuita) | **pgvector en Supabase** | pgvector evita un servicio más; ver [[API Backend]] §2 |
| Ficheros | Supabase Storage | S3 / Cloudflare R2 | R2 no cobra egreso: relevante si se sirven muchas imágenes |
| Entrenamiento | Google Colab Pro / Kaggle | GPU de la universidad | Colab basta para linear probing; el fine-tuning pide más |
| Seguimiento de experimentos | **MLflow** o Weights & Biases | Hoja de cálculo disciplinada | Ver [[Ciclo de Vida del Modelo (MLOps)]] |
| Repositorio | GitHub | GitLab | Con versionado de datos vía DVC o Git LFS |
| CI/CD | GitHub Actions | â€” | Tests, linter, build del APK |
| Monitorización | Sentry (errores) + logs | Grafana | §5 |

## 4. El coste real está en la GPU de inferencia

Es la partida que puede desbordar el presupuesto de un proyecto universitario, así que conviene dimensionarla con honestidad:

- Un contenedor con GPU **encendido 24/7** es la opción cara y casi siempre innecesaria en la Fase 1, donde el tráfico será esporádico (pruebas, demos, defensa).
- **CPU es viable** para ViT-B/16 si se acepta una latencia de 1â€“3 s por imagen y baja concurrencia. Para el alcance del TFG probablemente sea suficiente, y reduce el coste a casi cero.
- **Serverless con GPU** (escala a cero) evita pagar por inactividad, a costa de *cold starts* que pueden ser de decenas de segundos â€” inaceptable durante una demostración en vivo.

> [!tip] Estrategia pragmática
> Fase 1 en **CPU** con el modelo cuantizado y una cola para picos. Reservar GPU solo para las campañas de entrenamiento y para el reprocesado por lotes de la base vectorial. Si en la defensa hace falta latencia garantizada, se enciende una instancia temporal ese día.

## 5. Monitorización: qué vigilar

Más allá de uptime y errores, un sistema de ML necesita vigilar cosas que un backend normal no:

| Señal | Qué indica | Umbral de alarma sugerido |
| --- | --- | --- |
| **Tasa de "desconocido"** | Sube â†’ llegan especies fuera del catálogo, o el modelo se degradó | Desviación > 20 % sobre la línea base |
| **Distribución de confianza** | Se desplaza â†’ *drift* en las imágenes de entrada | Cambio significativo en la mediana |
| **Tasa de refutación experta** | El modelo se equivoca más de lo esperado | > 15 % de las validadas |
| **Distribución de especies predichas** | Colapso a pocas clases | Entropía cayendo |
| **Latencia p95** | Cumplimiento del RNF-01 | > 3 s |
| **Fallos de sincronización** | Datos de campo atascados en dispositivos | Cualquier acumulación persistente |

Las tres primeras son formas de detectar **deriva de datos** (*data drift*), que en este dominio es esperable y no patológica: la fauna cambia con la estación, la app se usa en zonas nuevas, los usuarios cambian de teléfono. Lo importante es detectarla y decidir, no evitarla.

## 6. Copias de seguridad y reproducibilidad

Lo que hay que poder recuperar, y que es fácil olvidar hasta que se pierde:

- **Base de datos**: copia diaria automática, retención â‰¥ 30 días.
- **Imágenes y audios originales de campo**: son **irremplazables**. No existe una segunda oportunidad de fotografiar ese individuo esa noche. Copia redundante en al menos dos ubicaciones, incluida una fuera del proveedor cloud.
- **Anotaciones de CVAT**: exportar y versionar periódicamente, no dejarlas viviendo solo dentro de la herramienta. Representan cientos de horas de trabajo humano.
- **Pesos de cada modelo entrenado** que haya producido un resultado reportado, con su configuración exacta.
- **Los splits train/val/test** como listas de identificadores versionadas. Sin esto, ningàºn resultado es reproducible.

> [!danger] El activo más valioso del proyecto no es el código
> Es el dataset anotado. El código se reescribe en semanas; las anotaciones y las fotos de campo, no.

## 7. Qué falta por decidir o medir

- [ ] Elegir proveedor y región de despliegue (latencia desde Colombia).
- [ ] Decidir pgvector vs. Qdrant Cloud.
- [ ] Fijar presupuesto mensual máximo y alarma de gasto.
- [ ] Definir política de retención de imágenes originales.
- [ ] Montar copias de seguridad automáticas **antes** de acumular datos de campo.



