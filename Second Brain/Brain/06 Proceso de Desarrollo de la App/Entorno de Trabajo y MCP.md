---
title: "Entorno de Trabajo y MCP"
proyecto: Anura
tipo: proceso-desarrollo
estado: operativo
tags: [anura, proceso, herramientas, mcp, penpot, automatizaciÃ³n]
---

# Entorno de Trabajo y MCP

[[Anura â€” Ãndice General]] Â· [[Proceso de Desarrollo â€” Ãndice]] Â· [[DiseÃ±o de Interfaz (Penpot)]] Â· [[Stack TecnolÃ³gico]]

> [!abstract] QuÃ© documenta esta nota
> CÃ³mo estÃ¡ montado el entorno con el que se edita el diseÃ±o de forma programÃ¡tica, quÃ© herramientas hay disponibles y â€”sobre todoâ€” **las trampas concretas del API que ya costaron trabajo perdido**. La Â§4 es la parte que ahorra tiempo real a quien retome esto.

## 1. Montaje

```
Claude Code  â”€â”€MCPâ”€â”€â–¶  servidor local :9001  â”€â”€â–¶  Plugin MCP dentro de Penpot
                                                        â”‚
                                                        â–¼
                                              Archivo de diseÃ±o ANURA
```

Tres piezas, y **las tres tienen que estar vivas**:

| Pieza | DÃ³nde | CÃ³mo se levanta |
| --- | --- | --- |
| DeclaraciÃ³n del servidor | `D:\Anura\.mcp.json` | Se lee al iniciar la sesiÃ³n |
| Servidor puente | `http://localhost:9001` | Proceso local |
| Plugin dentro de Penpot | Navegador, sobre el archivo abierto | MenÃº de plugins â†’ Penpot MCP Plugin |

La forma del archivo de configuraciÃ³n:

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
> `.mcp.json` lleva un `userToken` de sesiÃ³n **en texto plano**. Da acceso al archivo de diseÃ±o. No debe subirse a control de versiones ni compartirse en capturas; si el repositorio es pÃºblico o compartido, aÃ±adir `.mcp.json` a `.gitignore` y rotar el token. Esta nota documenta la *forma* del archivo, nunca su contenido real.

SÃ­ntoma habitual: las herramientas de documentaciÃ³n responden pero `execute_code` devuelve *"the connector's server isn't responding"*. Eso significa que **el plugin dentro de Penpot se cayÃ³**, no el servidor. Se arregla solo desde el navegador, volviendo a ejecutar el plugin sobre el archivo.

## 2. Herramientas disponibles

| Herramienta | Para quÃ© |
| --- | --- |
| `execute_code` | Ejecuta JavaScript contra el Penpot Plugin API. Es el caballo de batalla |
| `export_shape` | Renderiza cualquier board o grupo a PNG. **La verificaciÃ³n visual real** |
| `penpot_api_info` | DocumentaciÃ³n de un tipo del API (`Board`, `Fill`, `Gradient`, `OpenOverlay`â€¦) |
| `high_level_overview` | GuÃ­a general del API; no necesita el plugin conectado |
| `import_image` | Sube una imagen al archivo |

## 3. MÃ©todo de trabajo

1. **Leer antes de escribir.** Antes de crear nada, extraer del archivo los patrones que ya existen (medidas, colores, radios, nombres) y copiarlos. El diseÃ±o del autor es la fuente de verdad, no las convenciones genÃ©ricas.
2. **Tandas cortas.** Un `execute_code` por unidad de trabajo pequeÃ±a, no un script gigante (ver Â§4).
3. **Verificar con `export_shape`** despuÃ©s de cada tanda. Un board puede quedar estructuralmente correcto y visualmente roto; los nÃºmeros no lo delatan, la imagen sÃ­.
4. **Helpers en `storage`.** El objeto `storage` persiste entre llamadas dentro de una misma sesiÃ³n del plugin: allÃ­ viven las funciones de fÃ¡brica (`rect`, `ell`, 
ewBoard`, `popup`, `tarjetaObs`, 
avbar`) para no reescribir medidas en cada llamada.
5. **Auditar botones muertos.** Buscar por expresiÃ³n regular los nombres que empiezan por `BotÃ³n` o contienen `redirige`, y comprobar si el propio elemento **o algÃºn ancestro dentro del board** tiene interacciÃ³n. Sin el paso del ancestro, los botones agrupados dan falsos positivos.

## 4. Trampas del API que ya costaron trabajo

> [!warning] Esta secciÃ³n es la razÃ³n principal de la nota
> Cada punto corresponde a un error que ya ocurriÃ³ y que se detectÃ³ tarde.

**`penpot.group()` invalida las referencias previas.**
Tras agrupar, las variables que apuntaban a las formas quedan obsoletas. AÃ±adirles una interacciÃ³n **falla en silencio**: no lanza error y la interacciÃ³n no queda. Si hay que agrupar y luego cablear, volver a buscar las formas por nombre despuÃ©s del `group()`.

**`resize()` sobre un board escala a los hijos.**
Si un hijo tiene las restricciones por defecto (`scale`), redimensionar el contenedor lo deforma. Fijar siempre `constraintsHorizontal = 'left'` y `constraintsVertical = 'top'` **en el momento de crear** cada forma. Un mapa estirado a lo ancho es el sÃ­ntoma clÃ¡sico.

**`findShape` por nombre puede devolver el grupo o su hijo.**
Cuando un grupo y su rectÃ¡ngulo interno comparten nombre, la bÃºsqueda devuelve el primero que encuentra. Mover "la fila" puede mover solo el rectÃ¡ngulo y dejar el switch atrÃ¡s. Acotar la bÃºsqueda con `type` o con el board como raÃ­z.

**`storage` se pierde al recargar el plugin.**
Toda caÃ­da de conexiÃ³n implica volver a declarar los helpers. Conviene tenerlos en un Ãºnico bloque reutilizable.

**Scripts largos cortan la conexiÃ³n.**
El patrÃ³n observado: los `execute_code` extensos â€”decenas de formas mÃ¡s agrupacionesâ€” tumban el plugin a mitad de ejecuciÃ³n, dejando el trabajo **parcialmente aplicado**. Eso es peor que fallar entero, porque el archivo queda en un estado intermedio que hay que auditar. Preferir tandas de una pantalla.

**Propiedades de solo lectura.**
`width`, `height`, `parentX`, `parentY` y `bounds` no se pueden asignar. Usar `resize(w, h)` y `shape.x = parent.x + offset` (o `penpotUtils.setParentXY`).

**Los colores van en hexadecimal con mayÃºsculas** (`#B1B2B5`, no `#b1b2b5`).

**Los arrays de `fills` y `strokes` son inmutables.** Hay que reemplazar el array completo, no modificar un elemento.

## 5. Por quÃ© automatizar el diseÃ±o en vez de dibujarlo a mano

No es una preferencia de herramienta, resuelve tres problemas concretos del sprint:

- **Consistencia por construcciÃ³n.** Una tarjeta de observaciÃ³n definida como funciÃ³n se replica idÃ©ntica en cinco listados. A mano, cinco copias divergen.
- **Cableado masivo.** Conectar cuatro pestaÃ±as de navbar en seis pantallas son 24 interacciones; el navbar completo del archivo superÃ³ las 180. A mano es donde aparecen los botones muertos.
- **AuditorÃ­a.** Se puede preguntar al archivo "Â¿quÃ© botÃ³n no lleva a ningÃºn lado?" y obtener una lista. Esa pregunta no se puede hacer mirando.

El coste es el de Â§4: el API tiene bordes afilados y el plugin se cae. Compensa mientras el trabajo sea repetitivo y sistemÃ¡tico; para decisiones estÃ©ticas puntuales, es mÃ¡s rÃ¡pido a mano.

## 6. QuÃ© falta por decidir o montar

- [ ] Sacar `.mcp.json` del control de versiones y rotar el token
- [ ] Decidir si el mockup aprobado se exporta a un catÃ¡logo de imÃ¡genes dentro de `99 Recursos/` como respaldo, dado que el archivo de Penpot es un punto Ãºnico de fallo
- [ ] Evaluar si conviene convertir los componentes recurrentes en **componentes de biblioteca** de Penpot, en vez de copias independientes, antes de que el archivo crezca mÃ¡s



