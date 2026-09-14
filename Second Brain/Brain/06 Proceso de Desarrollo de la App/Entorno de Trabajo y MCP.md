---
title: "Entorno de Trabajo y MCP"
proyecto: Anura
tipo: proceso-desarrollo
estado: operativo
tags: [anura, proceso, herramientas, mcp, penpot, automatización]
---

# Entorno de Trabajo y MCP

[[Anura â€” àndice General]] · [[Proceso de Desarrollo â€” àndice]] · [[Diseño de Interfaz (Penpot)]] · [[Stack Tecnológico]]

> [!abstract] Qué documenta esta nota
> Cómo está montado el entorno con el que se edita el diseño de forma programática, qué herramientas hay disponibles y â€”sobre todoâ€” **las trampas concretas del API que ya costaron trabajo perdido**. La §4 es la parte que ahorra tiempo real a quien retome esto.

## 1. Montaje

```
Claude Code  â”€â”€MCPâ”€â”€â–¶  servidor local :9001  â”€â”€â–¶  Plugin MCP dentro de Penpot
                                                        â”‚
                                                        â–¼
                                              Archivo de diseño ANURA
```

Tres piezas, y **las tres tienen que estar vivas**:

| Pieza | Dónde | Cómo se levanta |
| --- | --- | --- |
| Declaración del servidor | `D:\Anura\.mcp.json` | Se lee al iniciar la sesión |
| Servidor puente | `http://localhost:9001` | Proceso local |
| Plugin dentro de Penpot | Navegador, sobre el archivo abierto | Menàº de plugins â†’ Penpot MCP Plugin |

La forma del archivo de configuración:

```json
{
  "mcpServers": {
    "penpot": {
      "url": "http://localhost:9001/mcp/stream?userToken=<TOKEN>"
    }
  }
}
```

> [!danger] El token es una credencial
> `.mcp.json` lleva un `userToken` de sesión **en texto plano**. Da acceso al archivo de diseño. No debe subirse a control de versiones ni compartirse en capturas; si el repositorio es pàºblico o compartido, añadir `.mcp.json` a `.gitignore` y rotar el token. Esta nota documenta la *forma* del archivo, nunca su contenido real.

Síntoma habitual: las herramientas de documentación responden pero `execute_code` devuelve *"the connector's server isn't responding"*. Eso significa que **el plugin dentro de Penpot se cayó**, no el servidor. Se arregla solo desde el navegador, volviendo a ejecutar el plugin sobre el archivo.

## 2. Herramientas disponibles

| Herramienta | Para qué |
| --- | --- |
| `execute_code` | Ejecuta JavaScript contra el Penpot Plugin API. Es el caballo de batalla |
| `export_shape` | Renderiza cualquier board o grupo a PNG. **La verificación visual real** |
| `penpot_api_info` | Documentación de un tipo del API (`Board`, `Fill`, `Gradient`, `OpenOverlay`â€¦) |
| `high_level_overview` | Guía general del API; no necesita el plugin conectado |
| `import_image` | Sube una imagen al archivo |

## 3. Método de trabajo

1. **Leer antes de escribir.** Antes de crear nada, extraer del archivo los patrones que ya existen (medidas, colores, radios, nombres) y copiarlos. El diseño del autor es la fuente de verdad, no las convenciones genéricas.
2. **Tandas cortas.** Un `execute_code` por unidad de trabajo pequeña, no un script gigante (ver §4).
3. **Verificar con `export_shape`** después de cada tanda. Un board puede quedar estructuralmente correcto y visualmente roto; los nàºmeros no lo delatan, la imagen sí.
4. **Helpers en `storage`.** El objeto `storage` persiste entre llamadas dentro de una misma sesión del plugin: allí viven las funciones de fábrica (`rect`, `ell`, 
ewBoard`, `popup`, `tarjetaObs`, 
avbar`) para no reescribir medidas en cada llamada.
5. **Auditar botones muertos.** Buscar por expresión regular los nombres que empiezan por `Botón` o contienen `redirige`, y comprobar si el propio elemento **o algàºn ancestro dentro del board** tiene interacción. Sin el paso del ancestro, los botones agrupados dan falsos positivos.

## 4. Trampas del API que ya costaron trabajo

> [!warning] Esta sección es la razón principal de la nota
> Cada punto corresponde a un error que ya ocurrió y que se detectó tarde.

**`penpot.group()` invalida las referencias previas.**
Tras agrupar, las variables que apuntaban a las formas quedan obsoletas. Añadirles una interacción **falla en silencio**: no lanza error y la interacción no queda. Si hay que agrupar y luego cablear, volver a buscar las formas por nombre después del `group()`.

**`resize()` sobre un board escala a los hijos.**
Si un hijo tiene las restricciones por defecto (`scale`), redimensionar el contenedor lo deforma. Fijar siempre `constraintsHorizontal = 'left'` y `constraintsVertical = 'top'` **en el momento de crear** cada forma. Un mapa estirado a lo ancho es el síntoma clásico.

**`findShape` por nombre puede devolver el grupo o su hijo.**
Cuando un grupo y su rectángulo interno comparten nombre, la bàºsqueda devuelve el primero que encuentra. Mover "la fila" puede mover solo el rectángulo y dejar el switch atrás. Acotar la bàºsqueda con `type` o con el board como raíz.

**`storage` se pierde al recargar el plugin.**
Toda caída de conexión implica volver a declarar los helpers. Conviene tenerlos en un àºnico bloque reutilizable.

**Scripts largos cortan la conexión.**
El patrón observado: los `execute_code` extensos â€”decenas de formas más agrupacionesâ€” tumban el plugin a mitad de ejecución, dejando el trabajo **parcialmente aplicado**. Eso es peor que fallar entero, porque el archivo queda en un estado intermedio que hay que auditar. Preferir tandas de una pantalla.

**Propiedades de solo lectura.**
`width`, `height`, `parentX`, `parentY` y `bounds` no se pueden asignar. Usar `resize(w, h)` y `shape.x = parent.x + offset` (o `penpotUtils.setParentXY`).

**Los colores van en hexadecimal con mayàºsculas** (`#B1B2B5`, no `#b1b2b5`).

**Los arrays de `fills` y `strokes` son inmutables.** Hay que reemplazar el array completo, no modificar un elemento.

## 5. Por qué automatizar el diseño en vez de dibujarlo a mano

No es una preferencia de herramienta, resuelve tres problemas concretos del sprint:

- **Consistencia por construcción.** Una tarjeta de observación definida como función se replica idéntica en cinco listados. A mano, cinco copias divergen.
- **Cableado masivo.** Conectar cuatro pestañas de navbar en seis pantallas son 24 interacciones; el navbar completo del archivo superó las 180. A mano es donde aparecen los botones muertos.
- **Auditoría.** Se puede preguntar al archivo "¿qué botón no lleva a ningàºn lado?" y obtener una lista. Esa pregunta no se puede hacer mirando.

El coste es el de §4: el API tiene bordes afilados y el plugin se cae. Compensa mientras el trabajo sea repetitivo y sistemático; para decisiones estéticas puntuales, es más rápido a mano.

## 6. Qué falta por decidir o montar

- [ ] Sacar `.mcp.json` del control de versiones y rotar el token
- [ ] Decidir si el mockup aprobado se exporta a un catálogo de imágenes dentro de `99 Recursos/` como respaldo, dado que el archivo de Penpot es un punto àºnico de fallo
- [ ] Evaluar si conviene convertir los componentes recurrentes en **componentes de biblioteca** de Penpot, en vez de copias independientes, antes de que el archivo crezca más



