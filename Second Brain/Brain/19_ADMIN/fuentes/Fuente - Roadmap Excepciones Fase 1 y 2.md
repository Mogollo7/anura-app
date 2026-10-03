---
title: "Roadmap de excepciones, Fase 1 y Fase 2"
tags: [fuente, admin, roadmap]
created: 2026-09-25
status: draft
source: "Second Brain/notes/Aquí tienes la versión actualizada.md"
---

# Roadmap de excepciones, Fase 1 y Fase 2

> [!WARNING] Duplicado y estado no ejecutado
> Esta nota repite decisiones del [[Fuente - Documento Maestro de Arquitectura]] y marca varios componentes como «Fase 1 (Listo)». En el vault eso no es evidencia de ejecución. La lectura de construcción está en [[Plan de Construccion del Admin]]: audio, YOLO, OTA real y la app quedan fuera de este ciclo. Ver [[Contradicciones del Modo Administrativo]].

> [!NOTE] Fuente literal
> Transcripción íntegra de `notes/Aquí tienes la versión actualizada.md`. No está resumida. Mapa: [[00_Indice_Principal]]. Nodo de trabajo: [[Roadmap Fase 1 y Fase 2]] · [[Modo Administrativo]] · [[Curacion e Ingesta]].

Aquí tienes la versión actualizada y blindada de la sección de Notas Adicionales, Excepciones y Hoja de Ruta (Roadmap) para integrar directamente en el Documento Maestro.
Se ajustaron formalmente los módulos de Bioacústica (Audio) y Curaduría CVAT (Módulo de Visión de Detección) dejando establecida su arquitectura como añadidos futuros modulares, permitiendo que el sistema funcione al 100\% desde el Día 1 sin depender de que estos modelos estén entrenados.
SECCIÓN DE EXCEPCIONES, NOTAS OPERATIVAS Y HOJA DE RUTA (ROADMAP)
1. Malla de Seguridad Taxonómica (Super-Centroides de Familia)
 * Función: Actúa como red de contención final de Nivel 3 antes de rechazar una captura.
 * Comportamiento en Campo: Ante fotos degradadas (flash nocturno excesivo, ejemplares cubiertos de lodo o mutilados) donde los detalles finos de especie y género se pierden, el sistema evita lanzar un error genérico y devuelve una clasificación de familia garantizada (Centrolenidae sp., Strabomantidae sp.).
 * UI/UX: La app despliega sugerencias de re-captura específicas según la familia identificada (ej. "Fotografíe la zona ventral para confirmar género").
2. Edición Manual de Pesos de Contexto (Overrides Administrativos)
 * Ajuste Dinámico vs. Override Manual: Aunque el Módulo Administrativo calcula de forma estadística la Gaussiana de altitud (\mu, \sigma) según los registros recopilados, el administrador tiene la facultad de aplicar un Override Manual mediante controles deslizantes (sliders).
 * Caso de Uso: Para especies estrictamente riparias (asociadas a cuerpos de agua), el investigador puede fijar manualmente un peso de sustrato/hábitat w_m = 0.50 y penalizar drásticamente la puntuación si el usuario no registra la presencia de agua.
3. Estrategia Incremental para Juveniles, Metamorfos y Renacuajos
 * Estado en Fase 1 (Día 1): No se requiere recopilar datasets de juveniles previa salida a producción. La aplicación se despliega con el contrato de software preparado (sub_centroids: List<SubCentroid>), pero alimentada únicamente con centroides de adultos.
 * Comportamiento Inicial: Un juvenil fotografiado en campo no superará el umbral de especie adulta (\tau_k) en la Capa 1 de OSR. El sistema aplicará la degradación natural de la Cascada Taxonómica y devolverá la clasificación correcta a nivel de género (Pristimantis sp.).
 * Evolución Futura (Fase 2): Las fotos de juveniles degradadas a sp. se almacenan en el backend local. Al acumular \ge 10 imágenes de una especie, el Módulo Admin genera el vector \hat{C}_{k,\text{juvenile}} (512\text{d}) y lo envía al móvil en la siguiente actualización JSON de 2\text{ KB}.
4. Modulo Bioacústico / Desempate por Audio (Añadido Futuro - Fase 2)
 * Estado Actual: Pendiente de implementación. No bloquea el despliegue visual de la Fase 1.
 * Diseño del Contrato (Reserva de Arquitectura):
   * La base de datos local SQLite y los archivos JSON subregionales reservan el campo opcional "audio_signature_id" y los pesos de desempate bioacústico.
 * Comportamiento Temporal (Fase 1): Ante pares o complejos crípticos visualmente indistinguibles (\Delta S < 0.02), el desempate se resuelve exclusivamente por variables de contexto (altitud, microhábitat) o se categoriza bajo el clúster Pristimantis sp. / PENDIENTE_AUDITORIA.
 * Integración Futura (Fase 2): Cuando se integre el modelo bioacústico (extractor de espectrogramas 2\text{D} / YAMNet afinado), la app permitirá grabar 3\text{--}5 segundos de canto de anuncio. El análisis de frecuencia fundamental (Hz) y tasa de pulsos tendrá poder de veto sobre el modelo visual para desempatar especies gemelas.
5. Curaduría de Dataset y Procesamiento CVAT (Fase 1 Manual vs. Fase 2 Automatizada)
 * Estado Actual de CVAT: Sin modelo de detección automática (YOLOv8) entrenado.
 * Flujo de Curaduría Inicial (Fase 1 - Heurístico/Manual):
   * Filtrado de Ruido por Código: Se aplican scripts estándar en Python sin necesidad de IA (Deduplicación por Perceptual Hash pHash y descarte de imágenes fuera de foco mediante la varianza del Operador Laplaciano \text{Var} < 100).
   * Anotación Manual en CVAT: El herpetólogo o anotador dibuja manualmente los cuadros delimitadores (Bounding Boxes) y los polígonos de Longitud Rostro-Cloaca (LRC en mm) sobre la interfaz web de CVAT.
 * Evolución Futura (Fase 2 - Auto-Annotation Pipeline):
   * Una vez que se cuente con un modelo detector ligero entrenado (ej. YOLOv8-Anura), este se conectará a CVAT como servidor de Inferencia Automática (vía Nuclio) para pre-anotar automáticamente la ubicación de la rana y sugerir la escala de medición, acelerando el proceso de entrenamiento en el servidor.
6. Matriz Consolidada de Costos, Hardware y Licenciamiento
| Componente | Estado de Implementación | Tipo de Costo | Estimación Económica | Justificación Técnica |
|---|---|---|---|---|
| Engine Móvil (BioCLIP 1) | Fase 1 (Listo) | Operativo | $0 USD | Inferencia local en CPU/NPU del teléfono vía ONNX Runtime Mobile. |
| Modelos de Adaptación (JSON) | Fase 1 (Listo) | Transferencia | $0 USD | Descargas OTA de kilobytes desde el servidor proxy. |
| Servidor Proxy (Hostinger) | Fase 1 (Listo) | Infraestructura | $3 – $8 USD / mes | VPS/Hosting básico para cola de recepción de capturas y distribución de JSONs. |
| Worker Local / PC Admin | Fase 1 (Listo) | Hardware | $0 USD (Existente) | PC con GPU NVIDIA local ejecutando BioCLIP 2.5 (ViT-H/14) para auditoría y empaquetamiento. |
| Pipeline CVAT / Auto-YOLO | Fase 2 (Futuro) | Entrenamiento | $0 USD | Curaduría inicial manual; automatización programada tras acumular imágenes. |
| Motor Bioacústico (Audio) | Fase 2 (Futuro) | Desarrollo | $0 USD | Reservado en el contrato de software; implementación posterior sin alterar el APK. |
Diagrama del Roadmap de Evolución Sistémica
┌──────────────────────────────────────────────────────────────────────────────────┐
│ FASE 1: NÚCLEO OPERATIVO MÓVIL Y MOTOR DE CENTROIDES (DESPLIEGUE INICIAL)       │
├──────────────────────────────────────────────────────────────────────────────────┤
│ • BioCLIP 1 Limpio congelado en ONNX (~100 MB).                                 │
│ • Paquetes subregionales JSON con Centroides L2 de Adultos.                      │
│ • OSR en 3 capas (EVT Weibull + Residuo Manifold + Gaussiana Altitudinal).       │
│ • Cascada Taxonómica de Fallback (Especie -> Género sp. -> Familia sp.).          │
│ • Curaduría de imágenes manual en CVAT + Filtro pHash / Laplaciano.               │
└──────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│ FASE 2: COMPLEMENTOS MODULARES Y AUTOMATIZACIÓN (ACTUALIZACIÓN SILENCIOSA)        │
├──────────────────────────────────────────────────────────────────────────────────┤
│ • Inclusión de Sub-centroides de Juveniles/Metamorfos vía JSON (+2 KB OTA).       │
│ • Desempate Bioacústico habilitado para pares crípticos (Grabación de Canto).   │
│ • Servidor de Auto-Anotación en CVAT mediante modelo YOLOv8-Anura.               │
│ • Filtro de contexto morfométrico activo (Regla / LRC en mm).                     │
└──────────────────────────────────────────────────────────────────────────────────┘

Este esquema le otorga al proyecto una base sólida, funcional y publicable hoy mismo, protegiendo la arquitectura para que el audio y la automatización de CVAT encajen limpiamente cuando estén listos.
