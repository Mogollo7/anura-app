---
title: "Índice principal del modo administrativo"
tags: [admin, anura, moc]
created: 2026-09-25
status: refined
---

# Índice principal del modo administrativo

Mapa de este sector del cerebro. Empieza por [[Modo Administrativo]]. Las notas de `Second Brain/notes` no se modificaron. Aquí hay **21 transcripciones literales** (20 con texto y un `1.txt` vacío) y **21 nodos de trabajo**, además de este índice. No eran 24 documentos: en la carpeta había 20 Markdown y un texto vacío.

Nada de este mapa cierra solo las contradicciones. La lista para revisar está en [[Contradicciones del Modo Administrativo]].

## 1. Núcleo

- [[Modo Administrativo]] — qué es y qué se construye.
- [[Decisiones de Escalabilidad del Admin]] — cierre de diseño: encoder congelado, 9 paquetes, coseno en el teléfono, límites configurables y el herpetólogo como autoridad científica.
- [[Arquitectura Desacoplada]] — teléfono con el encoder de BioCLIP 1 (con fine-tuning, sin reentrenar); PC que compila paquetes.
- [[Plan de Construccion del Admin]] — quince fases, de datos a debug.
- [[Roadmap Fase 1 y Fase 2]] — qué sale a campo sin audio ni YOLO, y qué se reserva.
- [[Prueba Real del Creador de Paquetes]] — el Admin usado de punta a punta y el método medido con los vectores reales de Antioquia (viejo contra nuevo, puro contra fine-tuning).
- [[Plan del Backend Real]] — etapas para volver reales Modelo, Operación y Sistema y conectarlos con el teléfono; versiones, Portainer, Grafana y roles.
- [[Ficha Publica, Explorador y Destacados]] — la ficha que ve la gente (app y web), el Explorador y cómo se administra "Rana del día"; hoy escritos a mano en el código.

## 2. Personas, datos y curación

- [[Roles del Admin]] — administrador, herpetólogo, permisos por acción, doble aprobación.
- [[Modelo de Datos del Admin]] — individuo, observación, fotografía, qué se recalcula.
- [[Entradas y Ficha de Especie]] — los cinco bloques que alimentan al worker.
- [[Curacion e Ingesta]] — pHash, Laplaciano, CVAT manual, descarte reversible.

## 3. Territorio y catálogo

- [[Paquetes Geograficos de Antioquia]] — nueve subregiones, municipios, pisos térmicos.
- [[Especies Entrenables y Huerfanas]] — de ~230 en literatura a ~130 entrenables.

## 4. Representación

- [[Centroides y Muestras]] — fotos, individuos, tres tipos de centroide.
- [[Morfos y Especiacion Regional]] — morfos distintos según el paquete.
- [[Microadaptadores y Transfer Learning]] — ArcFace solo en la matriz del clúster.

## 5. Decisión

- [[Contexto Ecologico y Pesos]] — GPS, altitud, sustrato, pesos por especie y paquete.
- [[OSR en Tres Capas]] — Weibull, residuo, corte ecológico, códigos de rechazo.
- [[Cascada Taxonomica y Supercentroides]] — especie, género, familia, rechazo.

## 6. Salida del sistema

- [[Esquema JSON del Paquete]] — contrato único del compilador.
- [[Worker Releases y Sandbox]] — mock, PC, aprobación, rollback.
- [[Observabilidad y Simulador]] — ECharts para la ciencia, Grafana solo como motor.

## 7. Revisión

- [[Contradicciones del Modo Administrativo]]
- [[Auditoria de Implementacion del Admin]] — estado real de la construcción en código: qué fase quedó completa, parcial o pendiente, y qué le queda debiendo a fases futuras.

## 8. Fuentes literales

Texto completo, con alerta encima cuando choca con otra nota.

- [[Fuente - Documento Maestro de Arquitectura]]
- [[Fuente - Estrategia de Arquitectura y Transfer Learning]]
- [[Fuente - Plan de Fases para Construir el Admin]]
- [[Fuente - Modelo de Datos y Reglas del Admin]]
- [[Fuente - Roles y Permisos]]
- [[Fuente - Entradas del Administrador]]
- [[Fuente - Roadmap Excepciones Fase 1 y 2]]
- [[Fuente - Observabilidad Grafana y ECharts]]
- [[Fuente - Arbol de Paquetes de Antioquia]]
- [[Fuente - Riqueza Teorica de Antioquia]]
- [[Fuente - Especies Huerfanas y Catalogo Entrenable]]
- [[Fuente - Centroides Estables y Muestras]]
- [[Fuente - Microadaptadores Multiclase]]
- [[Fuente - Metric Learning y Olvido Catastrofico]]
- [[Fuente - Espacio Vectorial y Margen]]
- [[Fuente - Contexto Multimodal]]
- [[Fuente - Pesos Variables por Especie]]
- [[Fuente - ETI-OSR-2026]]
- [[Fuente - ETI-SCH-2026]]
- [[Fuente - Estrategias OSR Alternativas]]
- [[Fuente - Archivo 1 vacio]]

## Lectura corta para empezar a construir

[[Decisiones de Escalabilidad del Admin]] → [[Modo Administrativo]] → [[Modelo de Datos del Admin]] → [[Plan de Construccion del Admin]].

El resto del cerebro, cuando un número de estas notas choque con una medición: [[DECISION_LOG]], [[00_CONTRADICTIONS]], [[FASE_13_CALIBRACION_INDEPENDIENTE]].
