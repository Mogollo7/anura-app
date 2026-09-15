# Auditoría de arquitectura de paquetes — ANURA / runtime Merlin

Fecha: 2026-09-14
Alcance: `visual_catalog/`, `regional_packages/`, `covariance/`, `threshold/`,
`taxonomy/species/species_registry.json`, `tools/catalog/build_regional_package.py`,
`tools/catalog/validation_gate.py`, `validation/merlin_identification_flow/`.

---

## 1. Veredicto del estado PREVIO

> ## `PACKAGE_ARCHITECTURE_MISSING`

Antes de este trabajo **no existía un sistema de paquetes**. Existían
*manifiestos con forma de paquete*, que es una cosa distinta.

Lo que sí existía, verificado por lectura directa de los archivos:

| Artefacto | Qué es realmente | Qué NO es |
|---|---|---|
| `visual_catalog/v1.0.0/manifest.json` | Lista congelada de 41 `species_ids` + threshold + `encoder_sha256`. `"status": "FROZEN"` | No es instalable, no tiene payload, no tiene checksum de contenido propio, no se puede activar ni desactivar |
| `regional_packages/ANTIOQUIA/v1.0.0/manifest.json` | Documento de **alcance**: intersección por `species_id` entre la presencia regional y el release visual (28 especies) | No contiene prototipos, ni metadata de especies, ni checksum, ni versión de esquema. Es un informe, no un paquete |
| `regional_packages/CAUCA/v1.0.0/manifest.json` | Igual, 17 especies | Igual |
| `COLOMBIA_ANURA/ANTIOQUIA/antioquia_v1.sqlite` | Base de datos regional de contenido/biodiversidad | No participa en la ruta de inferencia visual |
| `covariance/v1.0.0`, `threshold/v1.0.0` | Releases congelados versionados (matriz de precisión, umbral) con `sha256` declarado | Son releases de **calibración**, no paquetes de especies desplegables |
| `taxonomy/species/species_registry.json` | Registro de 42 especies con `species_id` estable y `visual_lifecycle_status` | Ver sección 3 |
| `tools/catalog/build_regional_package.py` (202 líneas) | Genera el manifiesto de alcance regional | No instala, no valida integridad, no activa |
| `tools/catalog/validation_gate.py` (120 líneas) | Gate de validación para incorporar especies | No gestiona el ciclo de vida de un paquete en el dispositivo |

**Operaciones ausentes por completo**: `install`, `validate`, `activate`,
`deactivate`, `uninstall`, `active_species`, estado local persistente,
verificación de integridad en instalación, política de versionado, y una
abstracción de fuente de descarga.

### Consecuencia directa: el bug `DYNAMIC_REMOVE_SPECIES_FAIL`

Como no había noción de "catálogo activo", `OpenSetReleaseAdapter.__init__`
construía los centroides **una sola vez** desde el release congelado y además
hacía:

```python
self.centroids = np.asarray(list(means.values()), dtype=np.float32)
```

descartando el mapeo `species_id → centroide`. El adaptador no sabía a qué
especie pertenecía cada fila. Por eso `assess()` no podía filtrar por catálogo
ni reportar la especie más cercana, y una especie "desactivada" seguía
aportando su centroide. Reproducido y medido (§4 del informe post-bugfix).

---

## 2. "Catálogo de especies con flag `active`" ≠ "sistema de paquetes instalables"

Esta distinción es el núcleo de la auditoría y conviene no confundirla.

**Un catálogo con flag** es una tabla de especies donde cada fila tiene un
booleano. Vive dentro de la app, se distribuye con ella, y "añadir una especie"
significa publicar una versión nueva del binario. No tiene payload propio: los
prototipos deben venir de otro lado. No tiene integridad verificable de forma
independiente ni versión propia. `species_registry.json` con
`visual_lifecycle_status` es exactamente esto: útil como *registro taxonómico*,
insuficiente como *mecanismo de despliegue*.

**Un sistema de paquetes instalables** distribuye unidades autocontenidas y
versionadas (manifest + prototipos + metadata + taxonomía + grupos de
similitud), con checksum verificable antes de instalar, con estado local
persistente de qué está instalado y qué está activo, y con un ciclo de vida
completo. Añadir especies no requiere reconstruir la app; requiere instalar un
paquete. La activación es un estado del dispositivo, no del release.

Un flag `active` dentro de un release congelado **no puede** resolver el bug de
Open Set, porque el release seguiría siendo la fuente de verdad de los
centroides. Lo que resuelve el bug es invertir la dirección: la fuente de
verdad pasa a ser el catálogo activo, y el release histórico queda reducido a
lo que legítimamente aporta (matriz de precisión, umbral, contrato de encoder).

---

## 3. Lo que sí estaba bien y se conserva

- `species_id` estable (`ANU_COL_XXXX_YYY_001`) como clave de relación; el
  nombre científico nunca se usa como clave. Los paquetes nuevos heredan esto.
- Contrato de encoder por `sha256` presente en los tres manifiestos del release
  (`visual_catalog`, `covariance`, `threshold`) y verificado en el arranque del
  adaptador. **Se conserva sin cambios.**
- Separación explícita entre "presencia regional" y "soporte visual" en los
  manifiestos regionales. Los paquetes construidos respetan esa frontera: solo
  entran especies con soporte visual real.

---

## 4. Veredicto del estado POSTERIOR

> ## `PACKAGE_ARCHITECTURE_PARTIAL`

Implementado en `package_manager.py` (+ `build_test_packages.py`):

- **Operaciones completas**: `list_available`, `install`, `validate`,
  `activate`, `deactivate`, `uninstall`, `active_species`, más
  `active_prototypes`, `active_species_metadata`,
  `active_visual_similarity_groups`, `set_species_enabled`.
- **Estado local persistente** en `packages_root/state.json` +
  `packages_root/installed/<package_id>/<version>/`, separado de los releases
  históricos, que no se tocan.
- **Integridad**: `payload_sha256` determinista (sha256 sobre la lista ordenada
  `<relpath>:<sha256>`, excluyendo el propio manifest). Se valida **antes** de
  instalar; un prototipo alterado silenciosamente se rechaza (verificado).
- **Versionado**: `v1.0.1` se instala **junto a** `v1.0.0` sin sobrescribirla;
  reinstalar la misma versión exacta se **rechaza** salvo `allow_reinstall=True`
  explícito. Solo una versión de un `package_id` puede estar activa a la vez.
- **Fuente genérica**: `PackageSource` (ABC) → `fetch` → `validate` →
  `LocalPackageManager`. Implementada `FilesystemPackageSource`. HTTP / GitHub
  Releases / Drive encajan implementando dos métodos; **no se implementó
  ninguna integración con Drive**, solo la abstracción que la permitiría.
- **Offline**: verificado ejecutando el ciclo completo de catálogo con
  `socket.socket` parcheado para lanzar excepción. Ninguna operación abre red.
- **Frontera del encoder**: el paquete **no contiene** BioCLIP. Se verifica que
  no exista ningún `.onnx/.pt/.pth/.bin/.safetensors` en el payload y que
  `contains_encoder` sea `false`. El paquete solo declara el *contrato*
  (`encoder_id` + `encoder_sha256`), que se valida en la instalación.

### Paquetes reales construidos (no stubs)

Derivados de artefactos existentes en solo lectura:

| package_id | versión | especies | prototipos | grupos |
|---|---|---|---|---|
| `anura_antioquia_visual` | v1.0.0 | 28 | centroides Fase-13 GEO-6 | 3 |
| `anura_antioquia_visual` | v1.0.1 | 27 | ídem (sin *Scinax ruber*) | 3 |
| `anura_cauca_visual` | v1.0.0 | 17 | centroides Fase-13 GEO-6 | 2 |

Fuentes: `evaluation/fase13/embeddings/{reference,train}_embeddings.npz`
(prototipos), `taxonomy/species/species_registry.json` (metadata),
`regional_packages/{ANTIOQUIA,CAUCA}/v1.0.0/manifest.json` (alcance),
`visual_catalog/v1.0.0/manifest.json` (filtro de release).

### Por qué `PARTIAL` y no `COMPLETE`

Lo que falta para declarar `COMPLETE` es real y no debe disimularse:

1. **Ninguna fuente remota implementada ni probada.** Solo filesystem. La
   abstracción existe; el transporte real (reintentos, descarga parcial,
   verificación en tránsito, TLS) no.
2. **Sin firma criptográfica.** SHA-256 detecta corrupción y manipulación
   accidental, no un atacante que regenere manifest y payload. Falta firma
   asimétrica y confianza en una clave del publicador.
3. **Sin migración entre versiones de esquema.** `schema_version` se compara por
   igualdad exacta; no hay ruta de upgrade.
4. **`dependencies` y `minimum_app_version` se declaran pero no se hacen
   cumplir.** Los campos existen en el manifest; el resolutor no.
5. **No validado en Android.** Hay Java 22 pero no Gradle, ni Android SDK, ni
   adb en este entorno. El adaptador Kotlin queda `NOT_VERIFIED` (ver
   `MOBILE_IDENTIFICATION_CONTRACT.md`).
6. **Los paquetes construidos comparten prototipos con el release histórico**
   (mismos centroides de Fase 13). Es correcto para probar el ciclo de vida,
   pero no ejercita el caso de un paquete con prototipos genuinamente nuevos
   generados fuera de Fase 13.
