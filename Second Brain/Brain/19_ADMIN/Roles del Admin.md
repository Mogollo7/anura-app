---
title: "Roles del Admin"
tags: [admin, anura, roles]
created: 2026-09-25
status: draft
---

# Roles del Admin

Texto íntegro: [[Fuente - Roles y Permisos]]. No son dos superusuarios intercambiables. El permiso es por **acción**, no solo por pantalla.

## Quién ve qué

**Administrador del sistema.** Control técnico: dashboard, usuarios, datasets, taxonomía, especies, individuos, curación, experimentos, embeddings, centroides, micro-adaptadores, contexto, OSR, paquetes, worker, validación técnica, releases, sandbox, debug y auditoría.

**Herpetólogo.** Interfaz de conocimiento biológico: inicio, especies, observaciones, individuos, revisión de imágenes, morfos, distribución, altitud, microhábitat, pesos, LRC, complejos crípticos y revisiones pendientes.

El herpetólogo **no** ve configuración del worker, GPU, Python, ONNX, infraestructura, logs técnicos completos, usuarios, permisos, checksum interno ni parámetros que puedan romper el pipeline. Puede validar una especie sin saber qué es un embedding.

## Prototipo → real (S1, 2026-09-27)

**Ya hay autenticación real.** `/login` en el Admin pide correo y contraseña contra `auth-service` (la misma cuenta de ANURA Mobile). Si ese correo es una cuenta del panel (`auth.panel_accounts`), entra con sus permisos reales por acción, verificados en el servidor en cada llamada a `/api/panel/*`; si no lo es, ve la app pero no el panel. Cada alta, cambio de permiso o baja de cuenta queda en `audit.log`. Detalle en [[Plan del Backend Real]] (S1).

Sigue existiendo el simulador de antes ("operar como"), pero **solo cuando nadie inició sesión** — modo demostración, para revisar la interfaz sin depender del servidor. Con sesión real no hay "operar como otra persona": se opera como quien entró.

Flujo del herpetólogo: especie → datos → imágenes → adulto, juvenil o morfo → LRC → distribución → pesos → guardar revisión.

Flujo del administrador, sobre la misma especie: dataset → embeddings → centroides → micro-adaptador → OSR → experimento → paquete.

## Matriz de acciones

| Acción | Admin | Herpetólogo |
| --- | --- | --- |
| Ver especies | sí | sí |
| Editar taxonomía | sí | sí |
| Revisar fotografías | sí | sí |
| Validar adulto o juvenil | sí | sí |
| Definir morph id | sí | sí |
| Definir LRC | sí | sí |
| Definir microhábitat | sí | sí |
| Definir pesos `wv` / `wg` / `wm` | sí | sí |
| Crear complejo críptico | sí | sí |
| Ejecutar entrenamiento | sí | no |
| Modificar el worker | sí | no |
| Ver GPU y VRAM | sí | no |
| Configurar OSR técnico | sí | ver o revisar, no configurar |
| Generar paquete | sí | no |
| Aprobar paquete científico | sí | sí |
| Publicar paquete | sí | no |
| Administrar usuarios | sí | no |
| Debug técnico | sí | no |

## Doble compuerta antes del release

```text
Herpetólogo → validación científica → aprobado en ciencia
Administrador → validación técnica → paquete técnicamente válido
        → RELEASE
```

Encaja con la fase 13 de [[Worker Releases y Sandbox]]: no hay publicación automática.

La observabilidad técnica (GPU, logs) y el resultado científico (AUROC, confusión) no van en la misma gráfica. Ver [[Observabilidad y Simulador]].
