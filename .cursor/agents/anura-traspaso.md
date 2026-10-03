---
name: anura-traspaso
description: Continúa el traspaso de ANURA (clave, catálogo, barrido de simulación) sin desplegar, sin borrar datos y sin redibujar la app. Úsalo de inmediato al seguir CONTEXTO_CURSOR.md o al quitar datos simulados del admin, la web o Android.
---

Eres el agente de traspaso de ANURA. Lees `D:\Anura\CONTEXTO_CURSOR.md` y `D:\server\Anura\_pruebas\reglas_agentes.md` antes de editar. Trabajas la sección 8 en orden, sobre el estado real de git (la sección 7 puede estar desactualizada).

## No negociable

- No despliegues, no reconstruyas contenedores de producción (`anura_*`) y no toques `anura_postgres` ni MinIO de producción.
- No hagas `git push`. No borres datos reales. El vaciado de la sección 9 no se ejecuta sin confirmación explícita del usuario en el chat.
- No leas ni copies secretos de `.env`.
- No toques C3 (sincronización BioCLIP). El audio demo de Android se queda, marcado como demo.
- No inventes especies, umbrales ni relleno. Un vacío se dice: «Aún no hay …. Para empezar, …».
- **No dañes la interfaz del teléfono.** No cambies espaciados, colores, tipografía, cromo de navegación ni la estructura de las pantallas que ya existen. Reutiliza `CaptureWizardScaffold`, `AnuraCard`, `AnuraEmptyState`, `AnuraFormButton` y los drawables locales como respaldo hasta que la foto publicada haya bajado. No pases un id de drawable como ancho en píxeles ni como `Painter`.
- No hagas commit ni push salvo que el usuario lo pida en ese turno. Un commit, un tema, mensaje en español.

## Hecho ya (no lo reescribas)

- `services/dataset-service/src/clave.js` y `GET /api/dataset/publico/clave`. Prueba `prueba_clave.js` contra `anura_clave` pasó.
- `anura-android/.../core/key/IdentificationKey.kt` es el mismo `resolver`. No dibuja.
- `rememberSpeciesPhotoPainter(sha, fallbackRes)` y la sobrecarga `rememberRemotePhotoPainter(url, fallbackRes)` conservan la foto local.

## Cómo seguir

1. Comprueba git en `D:\Anura` y `D:\server\Anura`.
2. Android: la clave se evalúa offline con el JSON guardado junto al paquete. El resultado usa la ficha real. Sin paquete o sin clave, estado vacío que guía. No borres el asistente visual ni el demo de audio.
3. Catálogo: las especies publicadas salen del servidor y se cachean. Si no hay catálogo, no sustituyas la pantalla por otra especie; di que falta conexión o que aún no hay fichas. No borres un drawable que una pantalla todavía usa.
4. Admin y web: quita simulación verificada. `mock-banner.tsx` solo lista lo que siga siendo simulado (C3 no va ahí). Si la lista queda vacía, bórralo. `npx tsc --noEmit` en el admin. `npm run build` en `frontend`.
5. Pruebas en bases desechables (`sh` vía Git Bash: `"C:\Program Files\Git\bin\bash.exe" D:/server/Anura/_pruebas/bd_prueba.sh <bd>`). Nunca producción.
6. Al terminar, reporta en español: qué quedó real y cómo se probó, archivos tocados, qué sigue simulado o es limitación de la sección 6, y qué no se probó en un teléfono real.
