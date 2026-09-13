# Auditoria de peso del modelo ANURA

Fecha de auditoria: 2026-09-13

## Alcance y ubicacion

Los dos nombres solicitados no existen directamente bajo `D:\Anura\bioclip\`.
Los artefactos correspondientes se encontraron en
`D:\Anura\bioclip\checkpoints\`. La auditoria fue de solo lectura: no se
convirtieron, cuantizaron, comprimieron, reexportaron ni sobrescribieron
modelos.

Todas las conversiones usan 1 KB = 1024 bytes, 1 MB = 1024^2 bytes y
1 GB = 1024^3 bytes.

## Tabla principal

| Archivo | Tamano MB | Tamano GB | Formato | Dtype | Parametros/tensores | Uso |
|---|---:|---:|---|---|---:|---|
| `bioclip_anura_mejor.pt` | 328.979133 | 0.321269 | PyTorch checkpoint | FP32 | 86,223,933 valores; 158 tensores | Modelo de entrenamiento/clasificador |
| `encoder_anura_fp16.onnx` | 165.381051 | 0.161505 | ONNX | Inicializadores FP16; I/O FP32 | 169 inicializadores; 86,192,673 valores | Encoder visual de inferencia |
| `encoder_anura.onnx` | 329.779930 | 0.322051 | ONNX | Inicializadores FP32; I/O FP32 | 169 inicializadores; 86,192,673 valores | Encoder visual FP32 de referencia |
| `encoder_anura.pt` | 328.856631 | 0.321149 | PyTorch | FP32 | 86,192,640 valores | Encoder FP32 de referencia |
| `encoder_anura_fp16.pt` | 164.449975 | 0.160596 | PyTorch | FP16 | No se recargo en esta auditoria; artefacto exportado existente | Encoder FP16 de referencia |
| `anura_clasificador_fp16.onnx` | 165.603886 | 0.161723 | ONNX | Inicializadores FP16; I/O FP32 | 177 inicializadores; 86,223,969 valores | Clasificador completo para inferencia |
| `anura_clasificador.onnx` | 330.061861 | 0.322326 | ONNX | Inicializadores FP32; I/O FP32 | 177 inicializadores; 86,223,969 valores | Clasificador completo FP32 de referencia |

## Parte 2 - Verificacion FP16 de PyTorch

El archivo `bioclip_anura_mejor.pt` es legible y contiene un diccionario con
`visual_state_dict` y `cabezas_state_dict`.

| Categoria | Cantidad de tensores | Cantidad de valores |
|---|---:|---:|
| Parametros/valores totales | 158 | 86,223,933 |
| FP32 | 158 | 86,223,933 |
| FP16 | 0 | 0 |
| BF16 | 0 | 0 |
| Otros dtypes | 0 | 0 |

El bloque visual contiene 86,192,640 valores FP32. Las cabezas contienen
31,293 valores FP32. Por tanto:

**¿PyTorch esta realmente FP16?: NO.**

El checkpoint de entrenamiento auditado es completamente FP32. Esto no
implica que el archivo separado `encoder_anura_fp16.pt` sea equivalente al
checkpoint completo: el primero es un encoder, mientras que
`bioclip_anura_mejor.pt` incluye tambien las cabezas.

## Parte 3 - Analisis ONNX

### `encoder_anura_fp16.onnx`

- Valido estructuralmente con `onnx.checker.check_model`.
- Entrada: `imagen`, dtype FLOAT/FP32, shape `[1, 3, 224, 224]`.
- Salida: `embedding`, dtype FLOAT/FP32, shape `[1, 512]`.
- Inicializadores: 156 FLOAT16 y 13 INT64.
- Valores en inicializadores: 86,192,644 FLOAT16 y 29 INT64.
- No tiene salidas de familia, genero o especie.
- La dimension de embedding es **512**.
- El pipeline existente aplica `L2 normalize` al embedding. La metadata
  `encoder_metadata.json` tambien declara `normalizado_l2: true`. El grafo
  ONNX auditado no expone una salida adicional de norma; la normalizacion
  debe considerarse parte del pipeline de inferencia posterior al encoder.

**¿ONNX esta realmente FP16?: PARCIAL.**

Los pesos almacenados estan en FP16, pero entrada, salida y tipos de
interfaz permanecen en FP32. No es un modelo FP16 extremo a extremo.

### Clasificador ONNX disponible

`anura_clasificador_fp16.onnx` es valido y contiene el encoder mas las
cabezas de clasificacion. Tiene entrada `[1, 3, 224, 224]` FLOAT/FP32 y
salidas FLOAT/FP32:

- `prob_familia`: `[1, 7]`
- `prob_genero`: `[1, 13]`
- `prob_especie`: `[1, 41]`

Sus 163 inicializadores de pesos son FLOAT16; los 14 restantes son INT64.
Por ello tambien es FP16 solo en los pesos y parcial en el grafo completo.

## Parte 4 - Comparacion FP32 vs FP16

### Encoder ONNX comparable

| Metrica | Resultado |
|---|---:|
| FP32 (`encoder_anura.onnx`) | 329.779930 MB |
| FP16 (`encoder_anura_fp16.onnx`) | 165.381051 MB |
| Ahorro absoluto | 164.398879 MB (172,384,719 bytes) |
| Ahorro porcentual | 49.851087% |
| Factor de reduccion | 1.994061x |

### Encoder PyTorch comparable

| Metrica | Resultado |
|---|---:|
| FP32 (`encoder_anura.pt`) | 328.856631 MB |
| FP16 (`encoder_anura_fp16.pt`) | 164.449975 MB |
| Ahorro absoluto | 164.406656 MB (172,392,874 bytes) |
| Ahorro porcentual | 49.993413% |
| Factor de reduccion | 1.999737x |

### Clasificador ONNX comparable

| Metrica | Resultado |
|---|---:|
| FP32 (`anura_clasificador.onnx`) | 330.061861 MB |
| FP16 (`anura_clasificador_fp16.onnx`) | 165.603886 MB |
| Ahorro absoluto | 164.457975 MB (172,446,686 bytes) |
| Ahorro porcentual | 49.826410% |
| Factor de reduccion | 1.993080x |

La reduccion cercana al 50% es coherente con sustituir los pesos FLOAT de
4 bytes por FLOAT16 de 2 bytes. Las diferencias frente a exactamente 50%
provienen de operadores, constantes INT64, metadata y cambios menores en
la serializacion del grafo.

## Parte 5 - Parametros vs tamano

Para el encoder ONNX FP16, considerando solo los 86,192,644 valores FLOAT16
de inicializadores:

- bytes de pesos teoricos: 172,385,288 bytes;
- tamano del archivo: 173,414,601 bytes;
- sobrecoste de serializacion, grafo, operadores, metadata y constantes:
  1,029,313 bytes;
- bytes por valor FLOAT16 incluyendo solo el archivo: 2.012 bytes/valor;
- bytes por valor FLOAT16 considerando solo los pesos: 2.000 bytes/valor.

Para el encoder ONNX FP32, los mismos 86,192,644 valores FLOAT requieren
345,770,576 bytes teoricos. El archivo mide 345,799,320 bytes; el resto
corresponde principalmente a grafo, metadata y constantes.

## Parte 6 - Modelo para movil

### Modelo de entrenamiento

`bioclip_anura_mejor.pt` es el checkpoint PyTorch de entrenamiento. Incluye
el encoder visual y las tres cabezas jerarquicas en el `state_dict`; no es
el artefacto movil mas directo.

### Modelo de inferencia movil

El artefacto completo identificado por la configuracion local de recursos
moviles es `anura_clasificador_fp16.onnx`:

```text
Encoder movil: anura_clasificador_fp16.onnx
Tamano: 165.603886 MB (0.161723 GB)
Dtype: pesos FLOAT16; entrada y salidas FLOAT/FP32
Output: familia [1,7], genero [1,13], especie [1,41]
```

`encoder_anura_fp16.onnx` contiene unicamente el encoder visual y produce
un embedding de 512 dimensiones. No contiene el clasificador ni las
cabezas de familia, genero o especie. Para convertir ese encoder en una
identificacion completa hacen falta cabezas clasificadoras equivalentes,
vocabulario y el codigo de inferencia.

## Parte 7 - Tamano minimo estimado para SITRana offline

El clasificador ONNX completo ya contiene encoder y cabezas, por lo que no
se suma `encoder_anura_fp16.onnx` a ese paquete. Solo se suman archivos
reales existentes:

| Componente | Archivo | Bytes | MB |
|---|---|---:|---:|
| Encoder + clasificador | `bioclip/checkpoints/anura_clasificador_fp16.onnx` | 173,648,260 | 165.603886 |
| Vocabularios | `bioclip/checkpoints/vocabulario.json` | 1,667 | 0.001590 |
| Indice/vector DB (opcional para kNN) | `bioclip/paquetes_regionales/antioquia_v1.sqlite` | 6,705,152 | 6.394531 |
| Configuracion/prior (opcional para prior geografico) | `bioclip/checkpoints/prior_geografico_movil.json` | 34,520 | 0.032921 |

Totales:

- **Minimo para clasificacion jerarquica offline:** 173,649,927 bytes =
  165.605475 MB = 0.161724 GB (ONNX completo + vocabulario).
- **Con kNN y prior geografico:** 180,389,599 bytes =
  172.022907 MB = 0.167991 GB.

No se identifico un archivo de configuracion de preprocessing separado
necesario para el calculo. El preprocessing de imagen y la normalizacion
L2 deben ser proporcionados por el runtime. No se incluyeron imagenes del
dataset ni archivos de entrenamiento.

## Parte 8 - SHA-256

| Archivo | SHA-256 calculado | Hash documentado | Resultado |
|---|---|---|---|
| `bioclip/checkpoints/bioclip_anura_mejor.pt` | `98a6c54d6edb27e2b0344b8bbbaebd2ab749b1bf5136991ff73b37f66ee2c1ac` | `98A6C54D6EDB27E2B0344B8BBBAEBD2AB749B1BF5136991FF73B37F66EE2C1AC` | Coincide |
| `bioclip/checkpoints/encoder_anura_fp16.onnx` | `219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad` | `219E860E6FA9A80FB30A59FC8F61911421BBD53A4537DCA831803D3AB446B2AD` | Coincide |

La comparacion se hizo ignorando mayusculas/minusculas. El registro
documentado esta en `evaluation/open_set_v1/hashes_sha256.txt`.

## Parte 9 - Integridad

- PyTorch: **OK**; checkpoint legible con `torch.load(..., map_location="cpu")`.
- ONNX encoder FP16: **OK**; `onnx.load` y `onnx.checker.check_model`
  completados sin error.
- ONNX clasificador FP16: **OK**; carga y validacion estructural sin error.
- No fue necesario modificar ningun archivo para inspeccionarlo.
- No se ejecutaron conversiones, exportaciones ni cuantizacion.

## Verificacion FP16

```text
¿PyTorch esta realmente FP16?: NO
¿ONNX esta realmente FP16?: PARCIAL
```

## Ahorro

```text
FP32: 329.779930 MB (encoder ONNX)
FP16: 165.381051 MB (encoder ONNX)
Ahorro: 164.398879 MB
Porcentaje: 49.851087%
```

## Modelo movil

```text
Encoder movil: anura_clasificador_fp16.onnx contiene encoder y cabezas
Tamano: 165.603886 MB
Dtype: pesos FP16; I/O FP32
Output: familia [1,7], genero [1,13], especie [1,41]
Archivos adicionales: vocabulario; kNN/prior solo si se habilitan
Tamaño total estimado: 165.605475 MB minimo; 172.022907 MB con kNN y prior
```

