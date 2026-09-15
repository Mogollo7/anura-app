# AI_TO_ANDROID_HANDOFF

**Fecha:** 2026-09-14
**Supersede parcialmente:** `FINAL_FREEZE_REPORT.md` (no se sobrescribe; se conserva como evidencia histórica).
**Regla de lectura:** todo lo marcado `NOT_VERIFIED` no fue comprobado en este entorno. No asumir que funciona.

---

## ESTADO DE FREEZE

```
AI_LOGIC_FREEZE      = NO
AI_FREEZE_READY      = NO
MOBILE_RUNTIME_FREEZE = NOT_VERIFIED
```

**Motivo único y concreto del `NO`:** la arquitectura de catálogo/paquetes quedó corregida y verificada, pero la **calidad de decisión del Open Set no alcanza un mínimo operativo** (AUROC 0.538, FAR 0.850 con el catálogo completo activo). No se declara `YES` porque los scripts terminen sin error.

Lo que **sí** está estable, reproducible y congelable: encoder, preprocessing, contrato, gestor de paquetes, catálogo activo, reglas de similitud visual, proveedor geográfico. Lo que **no**: el umbral de aceptación.

---

## 1. Qué se corrigió

### 1.1 `DYNAMIC_REMOVE_SPECIES_FAIL` — fuga de catálogo (CERRADA)

**Causa raíz:** `OpenSetReleaseAdapter.__init__` construía la matriz de centroides una sola vez desde `visual_catalog/v1.0.0/manifest.json["species_ids"]` y ejecutaba `self.centroids = np.asarray(list(means.values()))`, **descartando el mapeo `species_id → centroide`**. El adaptador no sabía a qué especie pertenecía cada centroide, por lo que era estructuralmente incapaz de filtrar por catálogo activo.

**Corrección:** se conserva `centroid_by_species` (dict) + `release_species_ids`; `assess()` pasó de `assess(embedding)` a `assess(embedding, active_species_ids, active_prototypes)` y resuelve la matriz **en tiempo de llamada**. Flujo actual garantizado:

```
paquetes instalados → paquetes activos → especies activas → prototipos activos → Open Set
```

Nunca `release histórico → todos los centroides → Open Set`. Sin especies activas devuelve `NO_CONCLUYENTE` con `reason: NO_ACTIVE_SPECIES_IN_CATALOG` (no puede devolver `ESPECIE_CONOCIDA`). `assess()` ahora reporta `nearest_species_id`, `active_centroid_count`, `excluded_centroid_count`, `centroid_source`.

El release histórico se sigue leyendo para matriz de precisión, threshold y validación del contrato de encoder SHA-256. No se borró nada.

### 1.2 Arquitectura de paquetes instalables (IMPLEMENTADA)

**Estado previo: `PACKAGE_ARCHITECTURE_MISSING`.** No existía sistema de paquetes. `visual_catalog/v1.0.0/manifest.json` era una lista congelada de 41 `species_ids`; los `regional_packages/*/v1.0.0/manifest.json` son *informes de alcance* sin payload, sin prototipos, sin checksum ni versión de esquema. Cero operaciones de ciclo de vida.

**Estado actual: `PACKAGE_ARCHITECTURE_PARTIAL`.** `package_manager.py` implementa `list_available`, `install`, `validate`, `activate`, `deactivate`, `uninstall`, `active_species` (+ `active_prototypes`, `active_species_metadata`, `set_species_enabled`). Estado local en `packages_root/state.json` + `installed/`. SHA-256 del payload validado **antes** de instalar. Versionado lado a lado; duplicado exacto rechazado salvo `allow_reinstall=True`. Abstracción `PackageSource` con `FilesystemPackageSource` funcional — **sin acoplamiento a Google Drive** (solo la interfaz queda preparada). Offline verificado parcheando `socket.socket`.

**El paquete NO contiene BioCLIP.** El encoder permanece independiente y compartido:

```
BioCLIP ONNX (compartido, congelado)
      ↓ embedding 512-D
paquetes instalados/activos → prototipos → ranking + Open Set
```

Por qué es `PARTIAL` y no `COMPLETE`: sin fuente remota real, sin firma criptográfica, sin migración de esquema, `dependencies`/`minimum_app_version` declarados pero no exigidos.

### 1.3 Grupos de similitud visual (CONFIGURABLES, no hardcodeados)

`visual_similarity_groups.json`, sembrado con **evidencia medida**: distancia euclidiana entre los 41 centroides, umbral = percentil 1 de las 820 parejas = **0.261652**, luego componentes conexas. 7 grupos. Pares más cercanos:

| Par | Distancia |
|---|---|
| *Pristimantis paisa* \| *taeniatus* | 0.1944 |
| *Phyllomedusa tarsius* \| *venusta* | 0.1983 |
| *Dendropsophus ebraccatus* \| *triangulum* | 0.1991 |
| *D. bogerti* \| *columbianus* | 0.2283 |
| *Boana pugnax* \| *rosenbergi* | 0.2309 |
| *Rhinella alata* \| *margaritifera* | 0.2444 |

**Garantía verificada por test:** la advertencia es puramente aditiva — `scores_identical_with_and_without_rule: true`, decisión idéntica. No modifica porcentajes, no reordena, no elige ganador.

---

## 2. Qué se validó

| Prueba | Resultado |
|---|---|
| Ciclo de vida de paquete, 13 pasos | **13/13 PASS** |
| Paso 7 (el que fallaba): centroides dejan de participar | **PASS** — Mahalanobis 25.0126 → 38.8330 (Δ +13.82) |
| Integridad: payload manipulado | **PASS** — instalación rechazada |
| Versiones conviven lado a lado | **PASS** |
| Catálogo vacío → `NO_CONCLUYENTE` | **PASS** |
| Offline (sin red) | **PASS** |
| Unit tests originales | **10/10 PASS**, scores idénticos |
| E2E originales | **6/6 PASS**, scores idénticos |
| E2E de catálogo (nuevos) | **7 PASS, 2 RESIDUAL, 0 FAIL** |

### Los 2 RESIDUAL — reportados honestamente, no como PASS

**Caso B del requisito (especie desactivada no debe dar `ESPECIE_CONOCIDA`): NO SE CUMPLE a nivel de decisión.**

Con `Dendrobates truncatus` desactivado: su centroide efectivamente ya no participa (25.0126 → 38.8330, fuga cerrada), **pero la decisión sigue siendo `ESPECIE_CONOCIDA`** porque 38.8330 < 39.35406371422803, ahora atribuida a otra especie (`DEND_TRI`).

Causa medida: **13 de los 41 centroides caen por debajo del threshold para esa imagen** (el correcto en 25.0, el resto en una banda 38.6–41.0, con el umbral dentro de esa banda). El umbral es demasiado laxo. **No se recalibró** — prohibido por protocolo.

Conclusión: la corrección de arquitectura es correcta y necesaria, pero **no es suficiente** para satisfacer el requisito observable. El bloqueo restante es el threshold, no el catálogo.

---

## 3. Qué quedó congelado

| Componente | Valor |
|---|---|
| Encoder (inferencia) | `bioclip/checkpoints/encoder_anura_fp16.onnx` |
| SHA-256 encoder | `219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad` |
| Checkpoint origen (no usado en inferencia) | `bioclip_anura_mejor.pt`, SHA-256 `98a6c54d6edb27e2b0344b8bbbaebd2ab749b1bf5136991ff73b37f66ee2c1ac` |
| Tamaño ONNX | 173.414.601 bytes |
| Preprocessing | `open_clip.create_model_and_transforms("hf-hub:imageomics/bioclip")` |
| Entrada | Float32 NCHW 1×3×224×224 |
| Salida | 512-D, L2-normalizada (verificado en runtime, tolerancia 1e-3) |
| Open Set | Mahalanobis, min-distancia a centroides **activos** |
| Threshold | `39.35406371422803` (release histórico; `thresholds_production_ready=false`) |
| Covarianza | `covariance/v1.0.0` |
| Fuente de prototipos | `evaluation/fase13/embeddings/{reference,train}_embeddings.npz` |
| Catálogo activo | vía `package_manager.py` (`packages_root/state.json`) |
| Similitud visual | `visual_similarity_groups.json` (7 grupos, umbral p1 = 0.261652) |
| Proveedor GEO | `cell_zone_map_v1.csv` + `prior_zone_taxon_v2_clean.csv`; `w_geo_rank=0.3` **experimental** |
| Contrato | `IDENTIFICATION_RESULT_SCHEMA.json` v0.2.0 (aditivo), `MOBILE_IDENTIFICATION_CONTRACT.md` |

**Prohibido sin error crítico demostrado:** fine-tuning, encoder nuevo, backbone nuevo, destilación, cambio de embedding, rejector aprendido.

---

## 4. Limitaciones que permanecen

1. **Open Set general defectuoso — el bloqueo principal.** Con el catálogo completo activo: **AUROC 0.538, FAR 0.850, KAR 0.824**. Casi azar. Históricos: Fase 16 FAR≈0.939, Fase 20 ≈0.911, Fase 23A ≈0.754.

2. **Reducir el catálogo NO mitiga el problema.** Medido: 41→17 especies baja FAR solo 0.850→0.811 y el **AUROC cae por debajo del azar (0.4618)**. La diferencia 0.9107→0.8500 es cambio de población evaluada, **no una mejora** — no debe citarse como logro.

3. **Especie desactivada aún puede producir `ESPECIE_CONOCIDA`** vía otro centroide bajo un umbral laxo (§2).

4. ***Rhinella marina* vs *horribilis* no es tratable con la regla de similitud visual.** *R. marina* está en el pool UNKNOWN (83 imágenes), **no en el catálogo de 41** — nunca aparecerá como candidata, así que la advertencia de UI no puede dispararse para ese par. Es un problema puro de Open Set. Distancia medida centroide-KNOWN-*horribilis* ↔ media-UNKNOWN-*marina* = **0.1745**. Es el mayor contribuyente de falsos aceptados (60/228 = 26,3%) y está confirmado como similitud visual genuina entre taxones GBIF válidos y distintos (`COL_ANURA_0003` vs `COL_ANURA_0065`), no un error de datos. **No intentar resolverlo con una etiqueta de UI.**

5. ***Rhinella rivularis* no existe** en `species_registry.json` ni en los splits de Fase 13. No se inventó ningún grupo con ella.

6. Sin clasificador **anuro vs no-anuro**. El runtime exige `is_anuran` desde una capa externa; sin confirmación responde `NO_CONCLUYENTE`.

7. GEO cubre solo las zonas congeladas de Antioquia. Fuera de cobertura: sin GEO, sin inventar score.

8. Paquetes de prueba comparten prototipos con Fase 13 — no ejercitan prototipos genuinamente nuevos.

9. Segmentación no conectada (sin contrato de rasgos estable).

10. Ninguna ruta declara `NO_REGISTRADA` automáticamente. Se mantiene.

### La única palanca identificada (NO ejecutada)

El threshold `39.354` es un punto de operación **KAR-95%**: por construcción maximiza aceptar KNOWN, y por eso el FAR es 0.85. Moverse a otro punto de operación **sobre el mismo release congelado** no es reentrenar ni tocar el modelo. **No se hizo** porque el protocolo vigente exige conservar 39.354 hasta que exista un protocolo independiente aprobado. Requiere decisión explícita del responsable, no del implementador.

---

## 5. Cómo añadir una nueva especie (sin reentrenar BioCLIP)

```
nueva especie
   ↓ dataset/imágenes
   ↓ preprocesamiento/segmentación (OpenCV donde aplique)   ← NOT_VERIFIED: no integrado aún
   ↓ embeddings con el ONNX congelado (219e860e…)
   ↓ prototipo/centroide
   ↓ registro en metadata de especie + taxonomía
   ↓ empaquetado versionado (manifest + checksum SHA-256)
   ↓ package_manager.install(source) → validate() → activate()
   ↓ disponible para ranking + Open Set
```

No requiere tocar el encoder. Requisito: el paquete debe declarar el SHA-256 del encoder con el que se generaron sus prototipos; el runtime valida compatibilidad de contrato antes de usarlos.

**Gate obligatorio antes de activar un lote nuevo en producción:** validación independiente (ver `tools/catalog/validation_gate.py`). Un paquete que instala no es un paquete validado.

---

## 6. Estado exacto del runtime Android

```
AndroidToolchain: NOT_AVAILABLE
```

Verificado en esta máquina:

| Herramienta | Estado |
|---|---|
| Java | 22.0.2 ✓ |
| Gradle | **no instalado** ✗ |
| Android SDK / `ANDROID_HOME` | **no existe** ✗ |
| `adb` | **no instalado** ✗ |
| Gradle wrapper en el proyecto | **ausente** ✗ |

Existe: `android-merlin-identification/` con `build.gradle.kts`, `settings.gradle.kts`, `AndroidManifest.xml` y Kotlin (`IdentificationContract.kt`, `BioClipOnnxEncoder.kt`, `BioClipPreprocessor.kt`, `ContractValidator.kt`, `MerlinIdentificationAdapter.kt`).

| Ítem del checklist | Estado |
|---|---|
| APK compilable | `NOT_VERIFIED` |
| ONNX ejecutado en Android | `NOT_VERIFIED` |
| Paridad preprocessing Android ↔ desktop | `NOT_VERIFIED` |
| Offline en dispositivo | `NOT_VERIFIED` |
| Latencia y memoria en dispositivo | `NOT_VERIFIED` |
| `IdentificationResult` operativo en Android | `NOT_VERIFIED` |
| OpenCV integrado en el pipeline | `NOT_VERIFIED` |

**Para desbloquear:** instalar Android SDK (API ≥ 24) + `ANDROID_HOME`, añadir Gradle wrapper, empaquetar como assets el ONNX (173,4 MB — considerar descarga diferida vs bundle), los prototipos activos, la matriz de precisión, el threshold, la taxonomía y `visual_similarity_groups.json`.

**Pendiente y recomendado antes de escribir Android:** generar un *golden fixture* de paridad en desktop (imágenes fijas + tensor preprocesado + embedding de referencia con tolerancia numérica declarada) para que un test instrumentado valide paridad de forma reproducible. **No declarar paridad por intuición.**

---

## 7. Instrucciones reproducibles

Desde `D:\Anura\validation\merlin_identification_flow\`:

```bash
python run_tests.py                          # 10 unit tests
python run_runtime_e2e.py                    # E2E individual
python run_runtime_e2e_suite.py              # suite E2E original (6)
python test_package_lifecycle.py             # ciclo de vida, 13 pasos
python test_package_offline_integrity.py     # offline + integridad SHA-256
python run_runtime_e2e_catalog_suite.py      # E2E de catálogo activo/desactivado
python run_open_set_post_bugfix_audit.py     # auditoría Open Set post-bugfix
```

Requisitos: `onnxruntime`, `open_clip`, `numpy`, `Pillow`. El transform de OpenCLIP necesita caché local de HF la primera vez; después es offline.

Reconstruir paquetes de prueba: `python build_test_packages.py`.
Re-sembrar grupos de similitud: `python seed_visual_similarity_groups.py`.

**Integridad metodológica verificada:** ningún artefacto congelado protegido fue modificado (`git status`); sin `ground_truth_species` en rutas de inferencia; sin commits.

---

## 8. Recomendación de decisión

La IA está **arquitectónicamente lista** y **cualitativamente insuficiente** en un punto concreto: la aceptación Open Set.

Dos caminos, ambos legítimos y sin tocar el modelo:

**A. Decisión de producto (desbloquea Android ya).** Asumir que el sistema no puede afirmar `ESPECIE_CONOCIDA` de forma autoritativa con AUROC 0.538, y hacer que el producto presente siempre candidatos ordenados + evidencia + advertencias, reservando la aceptación firme para cuando exista un umbral validado. Esto es honesto y compatible con la experiencia tipo Merlin.

**B. Punto de operación (requiere tu aprobación explícita).** Definir un protocolo independiente para elegir un punto distinto sobre el mismo release congelado, con split propio y criterio de FAR objetivo declarado *antes* de mirar resultados. No es reentrenar. No se hizo aquí por respetar el protocolo vigente.

Lo que **no** se recomienda: seguir iterando sobre el modelo, el encoder o el embedding.
