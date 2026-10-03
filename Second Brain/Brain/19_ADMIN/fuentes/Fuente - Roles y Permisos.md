---
title: "Roles de administrador y herpetólogo"
tags: [fuente, admin, roles]
created: 2026-09-25
status: draft
source: "Second Brain/notes/ómo dividiría los roles.md"
---

# Roles de administrador y herpetólogo

> [!NOTE] Fuente literal
> Transcripción íntegra de `notes/ómo dividiría los roles.md`. No está resumida. Mapa: [[00_Indice_Principal]]. Nodo de trabajo: [[Roles del Admin]] · [[Worker Releases y Sandbox]].

ómo dividiría los roles
No los llamaría necesariamente “dos superusuarios”. Haría:
1. Administrador del sistema
Tiene control técnico completo:
ADMINISTRADOR
├── Dashboard
├── Usuarios y permisos
├── Datasets
├── Taxonomía
├── Especies
├── Individuos / observaciones
├── Curación
├── Experimentos
├── Embeddings
├── Centroides
├── Micro-adapters
├── Contexto
├── OSR
├── Paquetes
├── Worker
├── Validación técnica
├── Releases
├── Sandbox
├── Debug
└── Auditoría
Puede configurar el sistema, ejecutar procesos, administrar usuarios y revisar absolutamente todo.
2. Herpetólogo
Su interfaz debe estar pensada para conocimiento biológico, no para informática.
Por ejemplo:
HERPETÓLOGO
├── Inicio
├── Especies
├── Observaciones
├── Individuos
├── Revisión de imágenes
├── Morfos / especiación
├── Distribución
├── Altitud
├── Microhábitat
├── Pesos ecológicos
├── LRC / morfometría
├── Complejos crípticos
└── Revisiones pendientes
Pero no debería ver cosas como:
configuración del Worker;
GPU/VRAM;
Python;
ONNX;
configuración de infraestructura;
logs técnicos completos;
administración de usuarios;
permisos;
checksum interno;
configuración del servidor;
parámetros que puedan romper el pipeline.
Puede participar en el proceso científico sin necesitar saber cómo está implementado.
Y aquí entra el Wizard que mencionabas
Yo haría un Wizard de simulación de roles.
Al entrar al prototipo:
┌───────────────────────────────┐
│     SIMULADOR ADMIN ANURA     │
│                               │
│  ¿Cómo quieres visualizar     │
│  el sistema?                 │
│                               │
│  [ Administrador ]            │
│  [ Herpetólogo ]              │
└───────────────────────────────┘
No hay autenticación real todavía.
Simplemente permite cambiar el rol y comprobar cómo cambia la interfaz.
Después probaría los flujos
Por ejemplo, como herpetólogo:
Especies
   ↓
Pristimantis X
   ↓
Revisar datos
   ↓
Imágenes
   ↓
¿Adulto?
¿Juvenil?
¿Morph?
   ↓
Revisar LRC
   ↓
Revisar distribución
   ↓
Revisar pesos
   ↓
Guardar revisión
Mientras que el administrador tendría:
Pristimantis X
   ↓
Dataset
   ↓
Embeddings
   ↓
Centroides
   ↓
Micro-adapter
   ↓
OSR
   ↓
Experimento
   ↓
Paquete
El herpetólogo no necesita entender qué es un embedding para validar una especie.
Lo más importante: permisos por acción, no solamente por pantalla
No haría simplemente:
Admin ve todo / Herpetólogo ve algunas páginas.
También definiría permisos:
Acción
Admin
Herpetólogo
Ver especies
✓
✓
Editar taxonomía
✓
✓
Revisar fotografías
✓
✓
Validar adulto/juvenil
✓
✓
Definir Morph ID
✓
✓
Definir LRC
✓
✓
Definir microhábitat
✓
✓
Definir pesos wv/wg/wm
✓
✓
Crear complejo críptico
✓
✓
Ejecutar entrenamiento
✓
—
Modificar configuración del Worker
✓
—
Ver GPU/VRAM
✓
—
Configurar OSR técnico
✓
quizá solo ver/revisar
Generar paquete
✓
—
Aprobar paquete científico
✓
✓
Publicar paquete
✓
—
Administrar usuarios
✓
—
Debug técnico
✓
—
La parte de aprobar puede dividirse incluso mejor:
HERPETÓLOGO
    ↓
Validación científica
    ↓
✓ aprobado científicamente

ADMINISTRADOR
    ↓
Validación técnica
    ↓
✓ paquete técnicamente válido

    ↓
RELEASE
Eso encaja muchísimo con lo que estás planteando.
