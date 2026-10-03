---
title: "Auditoría de Implementación del Admin"
tags: [admin, anura, auditoria, implementacion]
created: 2026-09-26
status: living
---

# Auditoría de Implementación del Admin

Registro vivo de qué tanto el código real (`D:\server\Anura\admin`, Next.js) cumple lo que este mapa exige. No es una nota de diseño como [[Decisiones de Escalabilidad del Admin]] — es el estado de la CONSTRUCCIÓN, fase por fase, actualizado cada vez que se cierra una. Se actualiza a sí misma: cuando una fase nueva depende de algo que quedó incompleto en una fase vieja, o corrige algo de una fase vieja, queda anotado aquí en ambos sentidos.

Convenciones de estado: **completo** (cumple lo que pide el bloque del vault que le toca), **parcial** (cubre el núcleo, deja un gap explícito), **pendiente** (todavía no se construye).

Numeración: las fases `F<n>` de este admin NO son las 15 fases de [[Plan de Construccion del Admin]] uno a uno — son unidades de trabajo del mismo tamaño, mapeadas a los bloques de ese plan según se van necesitando. Cada entrada dice a qué bloque del vault corresponde.

## F13 — Curación (`/curacion`)

**Corresponde a:** Fase 2 del plan (`Curacion e Ingesta`), más la jerarquía de [[Modelo de Datos del Admin]].

**Estado: completo** para el núcleo de la fase 2. Jerarquía real Especie→Individuo→Observación→Fotografía (antes no existía — `observations.ts` del admin es otra cosa: reportes de usuarios de la app para moderación, no dataset científico). Duplicados por pHash simulado, borrosas `Var<100`, excluir foto sin tocar observación, invalidar observación con motivo, estadio de vida por individuo, piso mínimo de fotos entrenables (`MIN_FOTOS_ENTRENABLE=10`, con aviso de huérfana), trazabilidad de cada acción.

**Pendiente, dejado fuera a propósito (no es un gap, es de otra fase):**
- Crear/importar dataset (subir archivos) — no hay backend real que reciba archivos.
- CVAT / bounding-box de LRC — herramienta externa; el admin solo importará su resultado numérico (ver F15).
- `morph_id` — se declara por paquete en la Ficha de Especie, no en curación (ver F15).

## F14 — Roles del panel (`/sistema` → pestaña "Roles y permisos")

**Corresponde a:** [[Roles del Admin]].

**Estado: completo**, con una decisión explícita del usuario que ADAPTA el vault, no lo sigue literal: el vault pide un simulador de rol al entrar (preguntar Admin/Herpetólogo, sin cuentas reales). Se reemplazó por un sistema real de cuentas: un super usuario raíz (no degradable, no suspendible) crea cuentas y les asigna permiso por acción — la matriz de 18 acciones del vault coincide 1:1.

**Gap real, no resuelto:** "Configurar OSR técnico" tiene 3 estados en el vault para el herpetólogo (sí/no/"ver o revisar, no configurar"); el checkbox de la cuenta lo colapsó a binario (sin acceso). Pendiente si se necesita ese matiz cuando exista la pantalla de OSR (F21).

**Dependencia hacia adelante:** cuando F19 (Micro-adaptadores), F21 (OSR) y F23 (Compilador/Releases) existan, sus pantallas deben LEER el permiso de esta cuenta (`gestionarCuentas`, `ejecutarEntrenamiento`, `configurarOSR`, `publicarPaquete`, etc.) para ocultar/bloquear acciones — hoy esas fases no existen, así que el permiso está declarado pero nada lo consulta todavía. No es un bug de F14, es trabajo que F19/F21/F23 heredan.

> **Actualizado en F17:** `ejecutarEntrenamiento` y `verGPU` ya se consultan de verdad en `/ia` (la herpetóloga no puede lanzar jobs ni ve GPU/VRAM). Siguen sin consultarse: `crearComplejo` (F19), `configurarOSR` (F21), `generarPaquete`/`aprobarCientifico`/`publicarPaquete` (F23), `debugTecnico` (F24).
>
> **Actualizado en F19 — gap cerrado:** las cuentas se guardan (navegador) y hay un selector "operando como" en la barra superior que leen todas las pantallas. Sistema solo deja crear o editar cuentas con `gestionarCuentas`. Micro-adaptadores lee `crearComplejo`, `ejecutarEntrenamiento` y `aprobarCientifico`.

> **Actualizado en F21 — gap cerrado:** `/osr` lee `configurarOSR`. El tercer estado del herpetólogo ("ver o revisar, no configurar") queda resuelto sin checkbox nuevo: todos ven y revisan la calibración, y ajustarla o validarla exige el permiso. Siguen sin consultarse: `generarPaquete`/`publicarPaquete` (F23) y `debugTecnico` (F24).
>
> **Actualizado en F23:** `generarPaquete`, `aprobarCientifico` y `publicarPaquete` se leen en `/compilador`.
>
> **Actualizado en F24 — gap cerrado:** `/laboratorio` lee `debugTecnico`. Quien no lo tiene ve la rama científica (código, capas, τ, P de altitud, comparación coseno/Mahalanobis). La traza del encoder (norma, dimensión, foto) queda oculta.
>
> **Gap nuevo detectado en F17 (resuelto en F19):** no hay una sesión global de "quién está operando". `/ia` tiene su propio selector "Operando como" con las cuentas semilla; las cuentas creadas en Sistema viven solo en el estado de esa página y no llegan a `/ia`. Cuando haya más de una pantalla que lea permisos, el selector debe subir a la barra superior y guardarse en un solo lugar.

## F15 — Ficha de especie (`/ficha-especie`)

**Corresponde a:** [[Entradas y Ficha de Especie]], bloques 1 (parcial) y 2 (completo).

**Estado: completo** para los bloques 1-2. Punto de partida explícito del usuario: "los datos no aparecen de la nada" — el perfil ecológico y los pesos wv/wg/wm se CALCULAN agregando las observaciones curadas de F13 (altitud real, prior de sustrato real con sesgo por familia biológica — Centrolenidae→quebrada, Bufonidae→hojarasca), no se elige una plantilla a mano. Verificado con *Sachatamia ilex*: dio "especialista de quebrada" 50/20/30, exacto a la tabla del vault. (En F18 se corrigió que las altitudes de curación no respetaban el rango de la especie: la cifra pasó de 2.031 ± 972 m a 1.098 ± 544 m y el prior de quebrada de 0,67 a 0,62; el perfil derivado no cambió.) Calculado/manual/efectivo con el patrón ya usado en [[Contexto Ecologico y Pesos]]. Morfos declarados por el herpetólogo (vacíos por defecto). LRC en "pendiente" por defecto (sin CVAT no hay medición real que mostrar, así que no se inventa un rango).

**Bloques 3-4-5 correctamente NO están aquí** (son Fase 7/9/12 del plan — F19/F21/F23 en esta numeración); la ficha deja una nota apuntando ahí en vez de fingir esos campos.

**Gap real, no resuelto:** el "estado científico" completo (`DRAFT/DATASET_READY/EMBEDDINGS_READY/CENTROID_READY/VALIDATING/VALIDATED/WARNING/BLOCKED/PUBLISHED` de [[Modo Administrativo]]) se simplificó a un badge binario "Entrenable/No entrenable". Los estados intermedios no se pueden mostrar honestamente hasta que F17 (embeddings) y F18 (centroides) existan y produzcan ese dato de verdad.

> **Actualizado en F17 — gap cerrado en parte:** la ficha ya muestra `DRAFT` / `DATASET_READY` / `EMBEDDINGS_READY` de verdad (este último cuando un job completado del worker cubre la especie con el dataset vigente). "Entrenable" dejó de contarse sobre la muestra de curación y ahora usa la membresía completa del dataset: ≥ 10 fotos activas y ≥ 3 individuos (mínimo viable de [[Centroides y Muestras]]). Siguen pendientes: `CENTROID_READY` (F18), `VALIDATING`/`VALIDATED` (F22), `WARNING` (centroide prestado, F18), `BLOCKED`, `PUBLISHED` (F23).
>
> **Actualizado en F18:** `CENTROID_READY` y `WARNING` ya son reales. Quedan `VALIDATING`/`VALIDATED` (F22) y `BLOCKED`/`PUBLISHED` (F23).

**Gap heredado que esta fase resolvió parcialmente:** en el borrador de F15 se usó "distribución por departamento" para la lista de subregiones (gap señalado ahí mismo). F16 lo corrigió: ahora la ficha muestra `subregionesAntioquia` real (ver F16) y el selector de "paquete" para declarar morfos usa las 9 subregiones reales, no departamentos.

## F16 — Territorio real de Antioquia (`/paquetes`, panel de 9 subregiones)

**Corresponde a:** [[Paquetes Geograficos de Antioquia]] y la decisión #8 de [[Decisiones de Escalabilidad del Admin]] ("nueve descargas, no treinta y seis").

**Estado: PARCIAL — gap grande, documentado aquí a propósito.**

Lo que sí quedó completo: las 9 subregiones reales existen como datos (`lib/packages/antioquia-subregiones.ts`) con sus municipios, cotas y lectura ecológica reales de la fuente, y el catálogo de especies por subregión se calcula por solape real de rango de altitud (`catalog.getSpeciesDetail` vs la cota de cada subregión) — no es un número inventado. Se ve en `/paquetes` (panel nuevo, debajo de la tabla de paquetes) y ahora alimenta la Ficha de Especie (F15).

**Lo que NO se migró, y por qué:** el modelo de paquetes que ya existía (`lib/mock/packages.ts`) sigue tratando **Antioquia como 1 solo paquete versionado** (con su historial `1.0.0→2.4.0`), no como 9. Migrar de verdad ese modelo a 9 releases independientes por subregión toca **~15 archivos** que ya dependen de la forma actual: `devices.ts`/`health.ts` (paquetes instalados en cada teléfono), `sync.ts` (paquetes desactualizados), `notifications.ts` (segmentación por paquete instalado), `validation.ts` (el ancla `isAntioquiaPilot` de Fase 13 real: AUROC 0,6248, KAR 85,38 %, 9A/32B), `vector-db.ts` (colecciones), `updates.ts`, `audit.ts`, el wizard completo (`paquetes/nuevo`, 6 archivos de pasos). Hacerlo sin romper esas invariantes (los números que ya verificamos como coherentes en fases 6-9) es una fase propia — no un ajuste dentro de F16.

**Decisión tomada esta fase:** construir la estructura territorial real de forma ADITIVA (nueva, no rompe nada existente) y dejar el modelo de release versionado como está, marcado explícitamente como deuda. La alternativa (migrar todo ahora) tenía alto riesgo de romper Dispositivos, Notificaciones, Sincronización y Validación sin que el usuario lo pidiera explícitamente.

**Dependencia hacia adelante, marcada para cuando se necesite:**
- F23 (Compilador/Releases) es, según el propio plan, quien compila "un JSON **por subregión**" — es el punto natural donde el modelo de release por subregión tiene que existir de verdad, no antes. Si F23 se construye sobre `packages.ts` tal cual está hoy (1 paquete = Antioquia entera), va a heredar el mismo gap. **Marcar esto antes de empezar F23.**
- Cuando esa migración ocurra, revisar en orden: `packages.ts` → `vector-db.ts` → `validation.ts` (¿el ancla de Fase 13 se mueve a qué subregión, o se queda como "paquete raíz Antioquia" agregado?) → `devices.ts`/`health.ts` → `notifications.ts`/`sync.ts` → el wizard.

## F17 — Worker y embeddings (`/ia`)

**Corresponde a:** Fase 5 del plan ([[Plan de Construccion del Admin]], [[Worker Releases y Sandbox]]), más las decisiones #1, #12, #13 y #16 de [[Decisiones de Escalabilidad del Admin]] y la separación técnica/científica de [[Observabilidad y Simulador]].

**Estado: completo** para la fase 5 con worker mock. Checklist de la fuente: job ✓, progreso ✓, GPU ✓, VRAM ✓, logs ✓, tiempo ✓, dataset usado ✓, encoder usado ✓, artefactos ✓. Cadena `Job → Worker PC → BioCLIP 1 → 512-d → validación → almacenamiento` ✓, con sus seis controles: dimensión 512, encoder `BioCLIP-1-frozen`, sin NaN/Inf, norma L2, sin repetidos, procedencia completa.

De dónde sale cada número (nada escrito a mano):
- **Entrada:** la membresía curada del dataset (`lib/worker/membership.ts`) = referencia − duplicados pHash − borrosas Laplaciano, con la tasa de descarte medida en la muestra de `/curacion` de cada especie.
- **Encoder:** cifras MEDIDAS del [[DECISION_LOG]] (EXP-008/009): 165,6 MB, 403 ms a 1 hilo, 154 ms a 4 hilos, ~405 MB de pico. Viven en un solo archivo (`lib/worker/encoder.ts`).
- **Fallo por VRAM:** sale de aritmética (contexto CUDA + pesos + activaciones × batch contra 6.144 MB). Batch 256 no cabe y el job falla sin escribir artefactos.
- **Regla 512/1024:** un vector de BioCLIP 2.5 inyectado a propósito cae a cuarentena y no se guarda con los demás.
- **Permisos:** solo quien tiene `ejecutarEntrenamiento` lanza jobs; solo quien tiene `verGPU` ve la telemetría.

Verificado en navegador: job de Urabá con vector ajeno (1.888 vectores + 1 en cuarentena), job con batch 256 (falla por VRAM), cuenta de herpetóloga (botón bloqueado, telemetría oculta).

**Gaps reales de F17, no resueltos:**
- La telemetría (GPU %, img/s) y el rendimiento de la RTX 4050 son **estimaciones**: el vault no tiene benchmark del worker. La pantalla lo dice. Cuando exista el PC real, reemplazar `WORKER_GPU` y `THROUGHPUT` por mediciones.
- Los jobs lanzados en la sesión no se guardan. Solo el job semilla `JOB-2026-09-24-001` (catálogo completo, `EXP-0042`) es visible desde otras pantallas.
- Las exclusiones manuales de `/curacion` no llegan al worker (son estado del navegador, no hay backend).
- El contrato `ExperimentResult` de [[Observabilidad y Simulador]] (`metrics`, `curves`, `confusionMatrix`, `distributions`, `bySpecies`, `byRegion`, `artifacts`, `logs`) solo está cubierto en `bySpecies`, `artifacts` y `logs`. Métricas y curvas son de F22.
- La separación train/test por individuo (decisión #9) no ocurre aquí: los vectores guardan `individual_id`, pero el corte se hace en F18/F22.

**Correcciones a fases viejas hechas en F17 (el código viejo no coincidía con el vault):**
- **ONNX de 173 MB → 165,6 MB medidos** en `devices/health.ts`, `/paquetes` y el paso Vectores del wizard. Ahora leen de `lib/worker/encoder.ts`.
- **El conteo de vectores ignoraba la curación.** El wizard (paso Vectores) y DB vectorial contaban la referencia bruta, con duplicados y borrosas. Ahora los dos usan la misma membresía que el worker. Antioquia pasó de 4.841 a **4.605** vectores, y el job de catálogo del worker da la misma cifra.

**Deuda vieja que F17 destapó y NO corrigió:**
- `lib/mock/packages.ts` tiene escrito a mano `4.410` vectores para Antioquia v2.4.0. Ya no coincidía con 4.841 y ahora tampoco con 4.605. Se corrige cuando el modelo de paquetes migre (dependencia de F16 → F23).

## Contradicción abierta — qué lleva el paquete del teléfono

**Esto lo tiene que decidir una persona antes de F18.**

- **Este mapa dice** ([[Decisiones de Escalabilidad del Admin]] #5 y #13, [[Esquema JSON del Paquete]]): el teléfono recibe un **JSON por subregión** con **centroides** L2 en FP16 (1 KiB por especie, unos 55 KiB por subregión). En el teléfono solo se calcula coseno contra un umbral ya convertido (`tau_kind: cosine_similarity`). Mahalanobis se queda en el worker como comparación y no viaja.
- **El admin viejo dice** (wizard de F5, `/paquetes`, DB vectorial, validación de F6): el paquete es un `.sqlite` con sqlite-vec y **todos los vectores de referencia** en float32 (megabytes), centroides "Grupo A/B" con **umbral de Mahalanobis** al percentil 95.
- **La app Android real hace** (memoria del proyecto `anura_android_sqlite_vec_integracion`): ONNX + sqlite-vec, con open set por Mahalanobis.

Las tres no pueden ser verdad a la vez. F18 (centroides) y F21 (OSR) se construyen de forma distinta según lo que se decida, y F23 (compilador) emite un formato u otro. No se tocó nada de esto en F17: los vectores del worker (512-d, L2) sirven para los dos caminos.

> **Decisión del usuario (2026-09-26): los dos, comparados.** El admin calcula ambas calibraciones sobre los mismos vectores: (a) centroides L2 + umbral de coseno, que es lo que dice este mapa, y (b) sqlite-vec + Mahalanobis, que es lo que hace hoy la app Android. El simulador y la validación las comparan con métricas medidas: FAR, KAR y AUROC. Así lo prevé la decisión #5, que permite cambiar el calibrador si Mahalanobis gana en el simulador. El compilador (F23) emite el formato que gane, con la comparación como evidencia. Consecuencias:
> - **F18:** calcula los tres centroides (global, regional, morfo, con `borrowed`) y además la covarianza por especie (Grupo A propia, Grupo B agrupada con shrinkage) para el camino Mahalanobis.
> - **F21:** calcula el τ de coseno (Weibull) y el umbral de Mahalanobis, sin elegir uno a mano.
> - **F22 y F24:** muestran la comparación.
> - Ninguna nota del vault se reescribe hasta que exista esa medición.

## F18 — Centroides y morfos (`/centroides`)

**Corresponde a:** Fase 6 del plan, [[Centroides y Muestras]], [[Morfos y Especiacion Regional]], decisiones #9 y #10 de [[Decisiones de Escalabilidad del Admin]], supercentroides de [[Cascada Taxonomica y Supercentroides]], y la decisión del usuario "comparar los dos caminos".

**Estado: completo** para la fase 6, con los gaps de abajo. Contra la fuente:
- Embeddings → agrupación por especie → **global** → **por paquete** → ¿morfos? → **sub-centroide**: ✓.
- **Global siempre; regional con ≥ 3 individuos en la subregión; si no, `borrowed: true`** y la especie queda en `WARNING`: ✓. En Urabá: 17 especies con centroide, 14 regionales propios, 3 prestados.
- **Morfo solo si el herpetólogo lo declaró** en esa subregión; sub-centroide cuando hay ≥ 3 individuos etiquetados. Nunca se promedian morfos: ✓. Si se declara un morfo sin datos, se avisa que el compilador rechazará un único centroide (regla de [[Esquema JSON del Paquete]]).
- **Juveniles**: se estima cuántas fotos hay; con ≥ 10 queda "elegible", pero el contrato `sub_centroids` juvenil sigue vacío hasta un release de Fase 2 ([[Roadmap Fase 1 y Fase 2]]). Estadio manual, sin clasificación automática: ✓.
- **Corte por individuo (decisión #9)**: el centroide sale del 80 % de los individuos; el 20 % queda apartado para calibrar el rechazo (F21) y validar (F22): ✓.
- **Procedencia** del lote `CENT-2026-09-25`: dataset, `EXP-0042`, job, encoder, fecha, individuos y vectores por especie: ✓.
- **Supercentroides** de género y familia (suma L2, un voto por género, sin `genus_weight`): se cuentan y se suman al peso del paquete. Sus umbrales τ son de F21.
- **Camino Mahalanobis (decisión "ambos")**: grupo A (≥ 200 individuos, covarianza propia) o B (agrupada), y el peso que eso agrega. En Urabá: **35 KiB** por coseno, **4 MiB** por Mahalanobis y **3,7 MiB** con el `.sqlite` viejo. El tamaño no decide; decide la comparación de FAR/KAR/AUROC en F21–F22.

Verificado de punta a punta en un build de producción limpio: morfo declarado en la Ficha → 3 individuos etiquetados en Curación → sub-centroide calculado en `/centroides`.

**Gaps reales de F18, no resueltos:**
- No hay vectores de verdad: el centroide es metadato (cuántos individuos, vectores, estado), no 512 números. Es el mismo límite de todo el admin mientras no exista el worker real.
- Los individuos por subregión se **estiman**: la fracción de individuos curados de la muestra que cae en cada subregión, aplicada al total. La subregión de cada observación se asigna por la cabecera municipal más cercana cuya cota admite su altitud. Es una aproximación del point-in-polygon DANE; hay que reemplazarla cuando el admin lea el geo-service.
- Morfos declarados y etiquetas de morfo se guardan en el navegador (`localStorage`): cada persona ve los suyos y no se comparten. Hace falta backend.
- 33 de 41 especies quedan en `WARNING` porque les falta el regional en al menos una subregión. Es lo que dice la decisión #10, pero es una alerta por especie cuando el préstamo es por paquete. **Pregunta abierta:** ¿el `WARNING` debería vivir por especie **y paquete**?
- Hay dos cálculos de centroides: esta pantalla y el paso "Centroides" del asistente viejo (Grupo A/B de Mahalanobis, percentil 95). Hay que unificarlos en F21/F23.

**Gaps de fases anteriores que F18 cerró:**
- **F13:** ya se puede etiquetar el `morph_id` de cada individuo en Curación cuando la ficha declara morfos. Era lo que la fase 2 pedía "si la ficha lo pide" y había quedado pendiente.
- **F15:** la ficha muestra `CENTROID_READY` / `WARNING` reales. Además tenía un bug: la lista de morfos no se separaba por especie y se perdía al recargar. Ahora usa el almacén compartido y guarda la subregión por id.
- **F17:** el corte train/test por individuo, que había quedado pendiente "para F18/F22", ya existe.

**Corrección a datos viejos hecha en F18:** las altitudes de las observaciones curadas se generaban al azar entre 40 y 3.600 m, sin mirar el rango de la especie en el Catálogo. Ahora caen dentro del rango, con un 6 % de registros fuera de él para que Calidad de datos tenga algo real que detectar. Esto cambió las cifras de la ficha: ver la nota en F15.

> **Actualizado en F19:**
> - **Pregunta del `WARNING` resuelta por el usuario:** el aviso es por especie **y** subregión. La especie en sí queda `CENTROID_READY` si tiene centroide global; el préstamo o un morfo sin datos ponen en `WARNING` solo su fila de esa subregión. En Urabá quedan 3 en `WARNING`; como especie, las 41 están `CENTROID_READY`.
> - **"No hay vectores de verdad" → simulado:** existen embeddings de 512-d simulados (`lib/centroids/embedding-sim.ts`) con la jerarquía familia → género → especie, una dirección común a todos los anuros, variación por individuo y por foto, un componente de escena compartido y rasgos diagnósticos finos. Centroide L2, dispersión, especie más cercana, confusión y micro-adaptadores se calculan sobre esos vectores. Calibración con Node: 83,9 % de acierto con lista cerrada y centroide más cercano, 100 % a nivel de género, error concentrado en *Pristimantis*. Es plausible frente al 66,2 % medido del vault, que incluye el rechazo de desconocidas. **Las métricas medidas del vault siguen siendo la referencia**: esto sirve para la mecánica.
> - **Dos cálculos de centroides → unificados:** el paso "Centroides" del asistente de paquetes usa ahora el mismo cálculo que `/centroides` (corte por individuo, regionales propios y prestados, dispersión y vecino medidos). El umbral de Mahalanobis queda como el camino de comparación. Los borradores viejos guardados en el navegador muestran "recalcular" hasta volver a correr el paso.

**Nota operativa (resuelta en F19):** el servidor de desarrollo del puerto 3011 quedó con la caché de Turbopack corrupta tras muchas ediciones seguidas (errores como `getSpeciesDetail is not defined` o `module factory is not available` para el icono `Target`). El build de producción pasa limpio. Para verificar se agregó la configuración `anura-admin-prod` (puerto 3012, `next start`) en `.claude/launch.json`. Reiniciar el servidor de desarrollo lo arregla.

**Cambio de puerto (F19):** el servidor de desarrollo del admin pasó al **3012** (`anura-admin` en `.claude/launch.json`) y el de producción de verificación al **3013** (`anura-admin-prod`). La caché corrupta `.next/dev` se borró. El 3010 sigue siendo el de Docker (`admin-web`).

## F19 — Micro-adaptadores (`/micro-adaptadores`)

**Corresponde a:** Fase 7 del plan (`/admin/adapters`), [[Microadaptadores y Transfer Learning]], decisión #6 de [[Decisiones de Escalabilidad del Admin]], capa 2 de [[OSR en Tres Capas]] (ε de reconstrucción) y el desempate por contexto del [[Roadmap Fase 1 y Fase 2]].

**Estado: completo** para la fase 7 con entrenamiento simulado. Contra la fuente:
- **El sistema alerta y no decide:** detecta pares con alta confusión, medida con los individuos apartados sobre los vectores simulados. El herpetólogo propone y crea el clúster (`crearComplejo`). En el Valle de Aburrá hay 32 pares alertados, encabezados por *Pristimantis*: ✓.
- **Flujo** herpetólogo elige especies → crea clúster → configura ArcFace → el worker entrena (`ejecutarEntrenamiento`) → micro-adaptador → validación (`aprobarCientifico`): ✓. Si se cambian los miembros o la configuración, el entrenamiento queda "desactualizado" y hay que repetirlo.
- **Encoder congelado:** solo se entrena W. Por defecto **512 × 64 FP16 = 64 KiB**, calculado como filas × columnas × bytes; con 512 columnas avisa que pesa como otro modelo: ✓.
- **ArcFace** margen 0,35, escala 30, épocas 20–50, tasa de aprendizaje configurable (la fuente no fija el número): ✓. Quedan registrados para el worker real.
- **`MAX_CLUSTER_SPECIES = 12`** avisa que conviene dividir, pero no divide; lo decide el herpetólogo: ✓.
- **ε (capa 2):** percentil 95 del error de reconstrucción de los miembros apartados, con falso rechazo de miembros de ~5 %. Se prueba con intrusos del paquete: 100 % rechazados si son de otra familia y ~48 % si son del mismo género. Eso coincide con lo que dice el vault: la capa 2 no alcanza para congéneres, y por eso está la capa 3 de contexto: ✓.
- **Desempate por contexto:** altitud media ± desviación y sustrato dominante de cada miembro, sacados de su ficha. Si dos miembros siguen solapados, dice si el contexto puede desempatarlos o si quedan pendientes de auditoría: ✓.
- **Contrato del paquete:** `cryptic_clusters[]` con `cluster_id`, miembros, matriz, centroides del clúster y `epsilon_reconstruction`: ✓ (lo emitirá el compilador en F23).

Verificado en el navegador:
- Clúster de las 7 *Pristimantis*: acierto 46,4 % → **64,3 %** con el adaptador; ε 0,060; 64,9 KiB en el JSON.
- Clúster de 2 especies: 75 % → 87,5 %.
- Con la cuenta de herpetóloga: no puede entrenar, sí crear y validar.

**Adaptaciones y gaps reales de F19:**
- **El entrenamiento es simulado:** W sale de un discriminante tipo LDA en forma cerrada (subespacio reducido, covarianza dentro de especie con contracción 0,5, autovectores por Jacobi), no de ArcFace. La pantalla lo dice. En el worker real, ArcFace reemplaza esta función con el mismo contrato de entrada y salida.
- **La regla "0,02 de coseno tras entrenar" se tradujo** a separación de Fisher d′ < 1 en el espacio del adaptador. Con 2 especies, el coseno entre prototipos centrados siempre da −1, así que no sirve como medida. Antes de entrenar se sigue mostrando el margen de coseno de 512-d, con aviso bajo 0,02. Hay que revisarlo cuando exista ArcFace real, cuya salida sí está normalizada.
- **Pocos datos para medir:** el acierto sale de pocos individuos apartados (unos 4 por especie en la simulación), así que tiene varianza alta.
- **Clústeres en el navegador:** los clústeres y su validación se guardan en el navegador (`localStorage`), igual que los morfos. Hace falta backend.
- **ε se propone aquí**; según el plan, su calibración definitiva es parte del OSR (F21).

**Gaps de fases anteriores que F19 cerró:** sesión global y cuentas guardadas (F14/F17); `WARNING` por especie y subregión, vectores simulados y unificación de los dos cálculos de centroides (F18).

## F20 — Contexto ecológico: origen, rango manual y atípicos (`/ficha-especie`)

**Corresponde a:** el resto de [[Entradas y Ficha de Especie]] bloque 2 y [[Contexto Ecologico y Pesos]] que F15 había dejado sin cerrar — captura de GPS/altitud con corrección manual, y "el Admin puede estimar la gaussiana desde los registros y, además, ofrecer sliders de override... el override es visible, no sustituye al valor manual en silencio".

**Estado: completo.** No abrí una fase nueva: F20 ya vivía en gran parte dentro de la Ficha de especie (F15) — el pedido del usuario era completar lo que le faltaba, no duplicar la pantalla.

- **Id real de la fuente:** cada observación de iNaturalist o GBIF trae ahora su id de esa plataforma (`fuenteId` en `curation.ts`), con enlace directo a `inaturalist.org/observations/<id>` o `gbif.org/occurrence/<id>`. Las de campo muestran "sin id externo" — no se inventa uno. Esto es lo que pedía el usuario: "poder utilizar coordenadas según scraping... que tiene un id".
- **Rango manual de altitud:** además de la media±desviación calculada, la ficha ahora muestra y deja corregir el rango real (mín–máx) de las observaciones activas, con el mismo patrón calculado/manual/efectivo que ya usan los pesos — el manual nunca se pisa en silencio.
- **Atípicos, detectados y excluibles:** cada observación que cae fuera del rango real de la especie (Catálogo) más un margen de 150 m se marca "atípica". Se puede excluir del cálculo ecológico (altitud, sustrato, pesos propuestos) sin tocar el dataset de entrenamiento de Curación, que sigue siendo una decisión aparte. Esto es lo que pedía el usuario: "poder corregir errores, limpiar datos, ver valores atípicos y poder eliminarlos evitando generalización" — antes la media se calculaba siempre sobre las 18-20 observaciones completas, sin forma de sacar una lectura de GPS mala.
- Verificado en el navegador (build de producción): excluir una observación baja el conteo y recalcula media/desviación; guardar un rango manual (1200–2500 m) lo refleja como "Efectivo: manual".

**Gap real:** las exclusiones y el rango manual no persisten (estado de sesión del componente, como los pesos manuales) — se pierden al recargar. Igual que los pesos, es intencional por ahora: no hay backend. Si se quiere que sobrevivan a un refresh, hay que moverlas a `localStorage` como los morfos y clústeres.

## F21 — OSR en tres capas (`/osr`)

**Corresponde a:** Fase 9 del plan (`/admin/osr`), [[OSR en Tres Capas]], [[Fuente - ETI-OSR-2026]], bloque 4 de [[Entradas y Ficha de Especie]] (α, ε, τ de género y familia), [[Cascada Taxonomica y Supercentroides]], decisiones #3, #4, #5 y #14 de [[Decisiones de Escalabilidad del Admin]], punto 5 de [[Contradicciones del Modo Administrativo]] y la decisión del usuario "los dos caminos, comparados".

**Estado: completo** para la fase 9, con los gaps de abajo. Nueva subsección de navegación "Decisión". Contra la fuente:
- **El worker propone, la persona valida o ajusta:** cada parámetro muestra "propuesto por el worker" o "manual (propuesto X) · volver". Validar guarda quién y cuándo; si cambia la calibración o un clúster se reentrena, la validación queda **vencida**: ✓.
- **Capa 1, Weibull por especie:** se ajusta por máxima verosimilitud sobre d = 1 − coseno de los vectores de **entrenamiento** de cada especie. Radio = α · F⁻¹(p); lo que se guarda es el corte en similitud (`tau_kind: cosine_similarity`), como pide la decisión #5. α (elasticidad) y p (cobertura, 0,95) son los parámetros de la persona: ✓.
- **Supercentroides y cascada:** género = suma L2 de sus especies, familia = suma L2 de sus géneros, un voto por género. Su τ sale de la misma Weibull. Los rangos de la fuente (género 0,60–0,70, familia 0,50–0,58) se muestran como hipótesis y se marcan si el calculado cae fuera; no se imponen. Cada τ de nodo tiene override manual: ✓.
- **Capa 2, ε del clúster:** lee los clústeres entrenados de Micro-adaptadores en esa subregión, parte del ε p95 que propuso F19 y lo deja ajustar con una curva p80/p90/p95/p99 (miembros rechazados vs desconocidas atajadas). **Esto cierra el "ε se propone aquí; su calibración definitiva es parte del OSR" que dejó F19:** ✓.
- **Capa 3, `umbral_geo` y política** (rechazo `OSR_GEO` o solo penalización), 0,05 como valor inicial y no constante (decisión #4). Se mide contra las observaciones curadas reales de F13, separando las atípicas de F20 (GPS malo, rechazo correcto) de los registros buenos que el umbral tumbaría (rechazo injusto): ✓.
- **Comparación coseno vs Mahalanobis sin elegir:** mismas fotos, tres caminos (coseno con un solo umbral, coseno con Weibull por especie, Mahalanobis con covarianza A propia / B agrupada al percentil 95), con KAR, FAR, AUROC y acierto entre aceptadas, más la tabla a la misma cobertura p. La fila medida del vault (τ 39,35, KAR 95 %, FAR 91 %, AUROC 0,6248) queda al lado como referencia, no mezclada: ✓.
- **Estados:** la cascada reporta `MATCH_SPECIES/GENUS/FAMILY`, `OSR_CLUSTER` y `OSR_GLOBAL` por tipo de foto: ✓. `OSR_GEO` se mide aparte (ver gap).
- **Contrato para F23:** vista previa del JSON (`rejection_tau`, `rejection_tau_genus`, `rejection_tau_family`, `epsilon_reconstruction`, `umbral_geo`, política, y la comparación de Mahalanobis como evidencia, que no viaja): ✓.
- **Permisos:** ajustar y validar requieren `configurarOSR`; cualquiera ve y revisa. **Esto cierra el gap de F14** (el tercer estado del herpetólogo, "ver o revisar, no configurar"): no hacía falta un checkbox extra, porque ver es universal y configurar es el permiso.

**Cómo se mide sin hacer trampa:** todo se ajusta con el 80 % de individuos de entrenamiento y se mide con el 20 % apartado (decisión #9) más un banco de **16 especies que el paquete no conoce**: 4 congéneres no catalogadas (*Pristimantis*, *Boana*, *Rhinella*, *Leptodactylus* sp.), 3 de géneros fuera del catálogo (*Smilisca phaeota*, *Craugastor raniformis*, *Atelopus* sp.), 2 de familias fuera del catálogo (*Lithobates vaillanti*, Ranidae; *Pipa myersi*, Pipidae) y especies del catálogo que no están en esa subregión. Para cada una se sabe qué debería devolver la app (su género, su familia o rechazo).

**Verificado** (Node y navegador, build de producción):
- Valle de Aburrá, p = 0,95: coseno Weibull KAR 89,5 %, FAR 20,4 %, AUROC 0,908; Mahalanobis KAR 89,0 %, FAR 29,6 %, AUROC 0,853.
- Urabá: coseno FAR 38,5 % frente a Mahalanobis 44,5 %. En las tres subregiones probadas, Mahalanobis es más permisivo. Es la misma dirección que el FAR de 91 % medido en el vault.
- Las congéneres son las que se cuelan por la capa 1 (~70 % terminan en `MATCH_SPECIES` sin clúster), como dice la fuente. Con el clúster de 7 *Pristimantis* de F19 (ε 0,060): 4,8 % de miembros rechazados y 7 de 26 congéneres desconocidas atajadas. Con ε en p80 (0,054): 19 % de miembros rechazados y 20 de 26 atajadas. Ese compromiso es lo que la persona decide.
- Familias ausentes: 100 % en `OSR_GLOBAL`.
- Capa 3 en Valle de Aburrá: 623 observaciones curadas; 22 bajo 0,05, de las cuales 16 de 18 atípicas atajadas y 6 registros buenos (1 %) rechazados.
- Permisos: la herpetóloga ve todo con los campos bloqueados. Validar → "Validada por…"; cambiar ε → "vencida".

**Gaps reales de F21, no resueltos:**
- **La Weibull por especie casi no se distingue del umbral único en la simulación** (τ 0,67–0,73; umbral único 0,708). Los embeddings simulados dan casi la misma dispersión a todas las especies: no hay polimorfismo simulado salvo el de un morfo declarado. La ventaja que la fuente espera (radio holgado para *Oophaga histrionica*, estrecho para *Rhinella horribilis*) **no se puede demostrar sin vectores reales**. La pantalla lo dice.
- **El τ de familia sale por encima del rango de la fuente** (0,61–0,72 frente a 0,50–0,58). Puede ser la simulación o que la hipótesis de la fuente sea laxa. Se marca y no se corrige a mano.
- **Weibull sobre todas las distancias, no solo la cola:** con ~48 vectores por especie no alcanza para ajustar la cola sola, como haría EVT estricto. Con datos reales (cientos por especie) conviene ajustar solo la cola.
- **Mahalanobis aproximado:** covarianza regularizada (16 ejes propios más varianza isotrópica, no 512×512 completa). El grupo A se contrae 30 % hacia la agrupada, porque en la simulación tiene 16 individuos de entrenamiento, no 200. Sirve para comparar la mecánica; su τ (~25–30) no es comparable con el 39,35 real.
- **`OSR_GEO` no entra en la tabla de la cascada de esta pantalla:** las fotos del lote no tienen altitud propia. La capa 3 se mide aparte con observaciones curadas. **Cerrado en F24:** el simulador une las tres capas en la foto.
- **La política "penalización" solo se describía aquí.** **Cerrado en F24:** el simulador calcula wv·coseno + wg·P(altitud) + wm·P(hábitat) por foto.
- **Calibración guardada en el navegador** (`anura-admin:osr:v1`), igual que morfos y clústeres. Hace falta backend.
- **Métricas simuladas más optimistas que las reales** (AUROC 0,83–0,91 frente a 0,6248 medido). La simulación es más fácil que BioCLIP en campo. Las cifras del vault siguen siendo la referencia.

**Dependencias hacia adelante:** F22 (validación técnica) debe repetir la comparación coseno/Mahalanobis con sus propias pruebas y leer si la calibración está validada. F23 (compilador) toma el JSON de la tarjeta "Lo que recibirá el compilador" y emite el camino que gane. F24 (simulador) une las tres capas con altitud real por foto y aplica la política de penalización.

> **Actualizado en F24 — estos dos gaps cerrados:** el simulador recibe foto + altitud + sustrato y mete `OSR_GEO` en la misma rama que la capa 1 y la capa 2. Con política "rechazo" el puntaje cae a 0; con "penalización" el puntaje es wv·coseno + wg·P(altitud) + wm·P(hábitat) y la especie se mantiene. La comparación coseno/Mahalanobis de ESA foto se muestra al lado. Mahalanobis sigue sin viajar en el JSON.

## F22 — Validación técnica (`/validacion-tecnica`)

**Corresponde a:** Fase 11 del plan (`/admin/validation`), lista de la sección "Qué construir": taxonomía, dataset, individuos, duplicados, embeddings, dimensión 512, NaN, normalización L2, centroides, morfos, OSR, JSON, manifest, checksum y consistencia. "Cuando haya datos reales: accuracy, precision, recall, FAR, KAR, AUROC y matriz de confusión. **No inventar métricas.**"

**No es la misma pantalla que `/validacion` (F6).** Esa sigue siendo la capa de consumo del modelo ya publicado por departamento (matriz de confusión, Top-1/Top-5 anclados al piloto de Antioquia) — no se toca, sigue existiendo tal cual la dejó F6. `/validacion-tecnica` es el checklist de consistencia de un paquete en construcción (subregión) ANTES de compilarlo: no inventa un accuracy nuevo, reutiliza lo que ya midieron las fases anteriores.

**Estado: completo** para la fase 11. Contra la fuente:
- **Taxonomía, dataset, individuos, duplicados:** se leen de `datasetMembership` (F13/F17) y del corte 80/20 por individuo (F18) — no se recalculan, solo se verifica que sean consistentes (individuos entrenamiento + apartados = individuos, piso `MIN_FOTOS_ENTRENABLE`/`MIN_INDIVIDUOS_ENTRENABLE`).
- **Embeddings, dimensión 512, NaN, normalización L2:** en vez de reinventar estos cinco checks, la pantalla **reutiliza tal cual** los `checks[]` que el job del worker (F17, `planJob`) ya calcula en su etapa "validando" (`dim`, `encoder`, `nan`, `l2`, `dup`, `prov`) — están ahí desde F17 y nadie los había expuesto en una pantalla propia.
- **Centroides y morfos:** se leen de `getSpeciesCentroids` (F18/19) para la subregión elegida — préstamo, morfo sin datos, avisos, tal cual.
- **OSR:** se llama al mismo `calibratePackage`/`evaluateOsr` de F21, con los gates reales de los clústeres ENTRENADOS de esa subregión (misma huella que `/osr`, para que "validado" en una pantalla signifique lo mismo en la otra). El KAR/FAR/AUROC que se muestran son los que ya midió F21 — no se inventa un accuracy de validación aparte.
- **JSON, manifest, checksum:** se declara explícitamente **pendiente** — el compilador (F23) no existe todavía, así que no hay artefacto que revisar. Es honesto con "no inventar métricas": no se simula un checksum de un archivo que no se genera.
- **Estados de especie:** primera pantalla que muestra el juego completo del vault (`DRAFT/DATASET_READY/EMBEDDINGS_READY/CENTROID_READY/WARNING/BLOCKED/VALIDATING/VALIDATED`) unificando lo que F15 (ficha) y F18 (centroides) ya mostraban por separado y de forma más simple — esas pantallas NO se tocan, siguen con su propio badge reducido.
- **Gate de "lista para compilar":** bloquea solo por especies `BLOCKED`/`DRAFT` o por la calibración OSR de esa subregión sin validar o vencida. Una especie en `WARNING` (centroide prestado, morfo sin datos) **no bloquea** — es un estado aceptado por decisión #10 del vault, no una falla.

**Verificado** (Node y navegador, build de producción): Valle de Aburrá con 34 especies da 28 `WARNING` (centroide prestado — Valle de Aburrá no es la subregión de origen de casi ninguna) y 6 `VALIDATING`. Validar la calibración en `/osr` y volver aquí cambió el badge de "vencido" a "validado" y el gate de "No listo para compilar" a "Listo para compilar (F23)" sin recargar nada más — confirma que las dos pantallas comparten la misma huella (`osrFingerprint`) sobre los mismos gates reales.

**Bug encontrado y corregido durante la propia verificación:** la primera versión calculaba la huella de OSR con una lista de clústeres vacía (`gates: []`) por no volver a entrenar los adaptadores aquí, mientras `/osr` la calcula con los clústeres reales entrenados — la validación nunca coincidía y toda subregión con un clúster activo aparecía "vencida" aunque se acabara de validar. Se corrigió reconstruyendo los mismos `gates` (con `trainAdapter`) que usa `/osr`, antes de reportar el hallazgo.

**Gaps reales de F22:**
- El check de "Complejo críptico" es binario (creado/entrenado/validado); no repite el ε ni la tasa de rechazo de intrusos — esos números ya están en `/osr`, aquí solo importa el estado.
- Igual que las demás pantallas nuevas, no hay backend: `/osr` y `/centroides` guardan su estado en el navegador, así que esta pantalla lee lo mismo que haya en esa sesión.
- El único job semilla de F17 cubre el catálogo completo, así que el check "sin job de embeddings" nunca se dispara en la práctica — queda listo para cuando existan jobs por subregión.

## F23 — Compilador y releases (`/compilador`)

**Corresponde a:** Fases 12 y 13 del plan, [[Esquema JSON del Paquete]], [[Worker Releases y Sandbox]], decisión #8 ("nueve descargas, no treinta y seis") y #15 de [[Decisiones de Escalabilidad del Admin]].

**Decisión sobre el gap de F16, tomada antes de empezar:** el modelo de release versionado viejo (`lib/mock/packages.ts`) sigue tratando Antioquia como 1 paquete por departamento — migrarlo tocaría ~15 archivos que ya están verificados (dispositivos, sincronización, notificaciones, validación, DB vectorial). F23 **no migra eso**: crea un modelo de release **nuevo y correcto**, por subregión (`lib/compiler/release-store.ts`, clave `anura-admin:releases:v1`), igual que F16 ya había hecho aditivo con las 9 subregiones reales en `/paquetes` sin tocar el wizard viejo. `/paquetes` sigue existiendo tal cual; `/compilador` es la fuente de verdad nueva para lo que de verdad se compila y se publica.

**Estado: completo.** Contra la fuente:
- **Un JSON por subregión**, nunca por piso térmico: ✓.
- **Compilador une, no recalcula:** taxonomía (catálogo), centroides y morfos (F18/19), contexto (F15/F20 — altitud, pesos, sustrato), OSR (F21 — τ por especie/género/familia ya calibrado y validado) y micro-adaptadores (clústeres entrenados **y validados** de F19) en un solo objeto, exactamente el esquema del documento maestro (`package_metadata`, `family_nodes`, `genus_nodes`, `species_catalog` con `sub_centroids`, `cryptic_clusters`, `tau_kind: cosine_similarity`).
- **Lo que el compilador debe rechazar, los cuatro puntos de la fuente, verificados uno a uno:**
  1. Dimensión ≠ 512 o encoder ≠ BioCLIP-1-frozen: chequeado contra `ENCODER`, no supuesto.
  2. Pesos que no suman 1: por especie, contra `sheet.calculado.pesos`.
  3. Publicar sin checksum, sin manifest o sin las dos aprobaciones: estructuralmente imposible — el release no tiene botón de publicar hasta `APPROVED`, y el manifest+checksum se generan juntos, nunca por separado.
  4. Centroide único con morfos opuestos: si hay ≥1 morfo declarado en esa subregión y no todos llegan a los 3 individuos etiquetados, la especie entera rechaza la compilación en vez de fundir los morfos en un centroide falso.
- **Vectores como marcador de posición** (`"… 512 floats …"`), igual que los tres ejemplos del vault — no se inventa un vector BioCLIP que no existe.
- **Releases:** `VALIDATING → READY → APPROVED → PUBLISHED`, y `ROLLED_BACK`. Publicar exige aval científico primero (`aprobarCientifico`) y técnico después (`publicarPaquete`), en ese orden — el botón de aval técnico no existe hasta que el científico ya se dio. Publicar una versión nueva pasa la anterior `PUBLISHED` a `ROLLED_BACK` automáticamente (solo una vigente por subregión); revertir una publicada hace que la anterior vuelva a ser vigente. Ningún estado se salta.
  - **Gap cerrado:** `generarPaquete`, `aprobarCientifico` y `publicarPaquete` — las tres declaradas desde F14 y sin consultarse por ninguna pantalla — ahora se leen aquí de verdad.
- **Compilar exige la validación técnica al día (F22):** si el gate de `/validacion-tecnica` no está aprobado (especie `BLOCKED`/`DRAFT`, o OSR sin validar/vencido), el botón "Generar paquete" queda bloqueado con los motivos exactos y un enlace a esa pantalla — encadena F21→F22→F23 tal como pide el orden del plan.
- **Descarga real** del JSON compilado (botón "JSON" por release, `Blob`+`<a download>`), no solo una vista previa.

**Verificado en el navegador** (build de producción): en Urabá, sin OSR validado, "Generar paquete" queda bloqueado con el motivo exacto. En Valle de Aburrá (con OSR ya validado en F21/F22): generar v1.0.0 → aval científico → aval técnico → publicar → queda "vigente"; generar v1.0.1 sin tocar nada más → sigue en "Validando" (no pisa la vigente); publicar v1.0.1 pasa v1.0.0 a "histórico" automáticamente; revertir v1.0.1 devuelve v1.0.0 a vigente. Con la cuenta de herpetóloga: "Generar paquete" y "Revertir" quedan bloqueados (le faltan `generarPaquete`/`publicarPaquete`).

**Bug encontrado y corregido en la propia verificación:** la primera versión marcaba el release recién compilado como "Desactualizada" apenas se creaba. Causa: el badge de vigencia comparaba la huella guardada contra la huella del campo de versión EN PANTALLA (que ya había avanzado a la siguiente versión sugerida) en vez de contra la huella de la propia versión del release. Se corrigió recalculando la vigencia con la versión de cada release, no con la del formulario.

**Gaps reales de F23:**
- Los releases viven en el navegador (`localStorage`), igual que morfos, clústeres y OSR — sin backend, se pierden al limpiar el sitio.
- `species_catalog`/`cryptic_clusters` en el manifest usan vectores marcador de posición: el tamaño estimado del paquete (KiB) es real (bytes por centroide/matriz), pero no hay 512 floats de verdad detrás todavía — mismo límite de todo el admin sin worker real.
- El aval técnico y "publicar" comparten el mismo permiso (`publicarPaquete`) en dos clics distintos porque la matriz de 18 acciones del vault no separa esas dos firmas; queda documentado, no es un olvido.
- No hay comparación entre releases (diff de qué cambió de una versión a otra) — el manifest completo se puede descargar y comparar a mano.

> **Actualizado en F24:** el manifest ahora congela `decision.umbral_geo` y `decision.politica_geo`, y el ε del clúster es el efectivo (manual si la persona lo ajustó, si no el propuesto). Un release compilado antes de esto no trae `decision`: el simulador lo dice y aplica 0,05 + rechazo, que es el valor inicial del vault, en vez de mezclar la calibración en vivo con un artefacto viejo. Hay que volver a compilar para que el teléfono y el simulador usen la misma política.

## F24 — Simulador de identificación (`/laboratorio`)

**Corresponde a:** Fase 10 del plan (`/admin/simulator`), sección Simulador de [[Observabilidad y Simulador]], estados de [[OSR en Tres Capas]] y el cierre del ciclo ("el simulador debe mostrar qué capa rechazó y con qué número"). El sandbox del teléfono que ya vivía en esta ruta se quedó como segunda pestaña: prueba descarga y sync, y no toca el release.

**Estado: completo** para la fase 10 con embeddings simulados. Contra la fuente:
- **Entrada:** foto (embedding apartado) + altitud + sustrato. ✓
- **Salida:** especie, género, familia o no concluyente, y la rama (capa 1, residuo, corte geográfico o cascada). ✓ Los códigos que ve la persona son los de la tabla del vault: `00_MATCH_OK`, `01_OSR_GLOBAL`, `02_OSR_CLUSTER`, `03_OSR_GEO_FAIL`, más `STATUS_GENUS` y `STATUS_FAMILY`.
- **Consume un release `PUBLISHED`.** Sin release vigente no corre: inventar un paquete sería el gap al revés. Los τ, el ε y la política salen del JSON, no de la pantalla de OSR en vivo. ✓
- **No escribe.** Ni checksum, ni candidato, ni publicación. El rechazo explica la vuelta del ciclo (cola de auditoría, crecer el adaptador, revisar GPS) y se queda en la pantalla. ✓
- **Comparación** coseno (viaja) contra Mahalanobis (no viaja) para esa foto. ✓
- **`debugTecnico`:** la traza del encoder queda detrás del permiso. La rama científica la ve cualquiera. ✓

**El asistente de paquetes no es el compilador.** Sus pasos de vectores, centroides, pruebas y publicación avisan que arman el borrador departamental (.sqlite). El ciclo que el simulador lee es OSR → validación técnica → compilador. La barra lateral agrupa los 14 pasos en esas tres partes.

**Navegación:** cada grupo es un botón. Al abrirlo muestra una frase de qué cierra ese bloque y, dentro, cada subsección hace lo mismo antes de listar sus pantallas.

**Gaps reales de F24:**
- La geometría sigue siendo simulada (los mismos vectores de F18/F21). El JSON no trae 512 floats; el simulador los reconstruye con la calibración de esa subregión y aplica los τ congelados.
- Si el release nombra un clúster y esta sesión no tiene la matriz entrenada, la capa 2 no se inventa: se avisa y se mantiene el match de la capa 1.
- Sigue sin backend. Publicar, simular y volver a curar ocurren en el mismo navegador.

## Recorrido real, datos reales y cierre de gaps (2026-09-26)

**Pedido:** usar el Admin de verdad para crear un paquete, auditar diseño y textos (design-critique, design-system, ux-copy, Apple HIG, ux-writing), probar con el paquete de Antioquia del teléfono y dejar el plan del backend. Hallazgos, números y decisiones: [[Prueba Real del Creador de Paquetes]]. Plan: [[Plan del Backend Real]].

**Cambios en el código (`D:/server/Anura/admin`):**
- **Datos reales.** `src/data/antioquia-real.json` (exportado por `D:/Anura/tools/admin/export_admin_seed.py`) alimenta catálogo, conteos, altitud de la ficha, presencia por subregión, encoders y la prueba. Se acabaron las 41 especies simuladas y los rangos de altitud aleatorios.
- **Wizard eliminado.** `/paquetes/nuevo`, `components/packages/wizard/*`, `lib/packages/{draft,storage,providers,types}.ts`. Regiones muestra el paquete del teléfono y las 9 subregiones reales. El único creador es Release.
- **Operación → Actualizaciones.** Lee los releases reales del creador; ya no tiene "Publicar ahora" ni correcciones de catálogo inventadas.
- **Gaps de persistencia cerrados:**
  - fichas (`anura-admin:fichas:v1`);
  - curación con opción de reincluir (`anura-admin:curacion:v1`);
  - jobs del worker (`anura-admin:jobs:v1`), que ahora descuentan las exclusiones manuales de Curación (gap de F17).
- **Regla de dos personas.** Quien entrena ≠ quien valida el clúster; aval científico ≠ técnico. Publicar pide confirmación.
- **Textos.** La LRC queda en Fase 2 sin efecto. ArcFace aparece deshabilitado (el entrenamiento es LDA). Se nombran bien el encoder con fine-tuning y el BioCLIP 2.5 del servidor. Se reemplazaron los enums crudos y "Validando" sin nada corriendo, y se quitaron los enlaces a iNaturalist/GBIF con ids simulados.
- **Accesibilidad.** Terciario ≥ 4,5:1 en claro y oscuro; texto mínimo de 11 px; ARIA en las gráficas nuevas.
- **Gráficas de resumen.** Tarjeta "Prueba con los datos reales" (OSR, Métricas) y avance del plan (Sistema).
- **Lint.** Se corrigieron dos `setState` dentro de efectos que venían de antes (navegación y simulador).

**Verificación.** `tsc`, `eslint` (0 errores) y `next build` pasan. Recorrido en el build de producción (3013) sobre 02 Oriente:
1. job de 27 especies;
2. clúster *P. paisa* ↔ *P. penelopus*;
3. OSR validada;
4. release 1.0.0 con 27 especies y nodos con centroide;
5. aval científico que bloquea el técnico a la misma persona;
6. aval técnico de otra cuenta;
7. diálogo de publicar;
8. release visible en Actualizaciones.

**Sigue abierto:**
- El teléfono no lee el paquete del creador (M4 y C1).
- Fotos, vectores y telemetría siguen simulados (M1–M2).
- No hay "paquete en construcción" compartido entre pantallas.
- El explorador de Métricas sigue simulado debajo de la tarjeta real.

## Pendiente de fases futuras (no auditado todavía, no existen)

F12 (verificación Docker, cierre). El simulador de identificación ya no está en esta lista: es F24.

Relacionado: [[00_Indice_Principal]], [[Plan de Construccion del Admin]], [[Modelo de Datos del Admin]].
