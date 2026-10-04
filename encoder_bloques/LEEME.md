# Encoder Anura (fp16) en bloques

Archivo: `encoder_anura_fp16.onnx` · 173 414 601 bytes · sha256 `219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad`
(es el mismo sha de `package_info.encoder_onnx_sha256` de los paquetes actuales).

GitHub rechaza archivos de más de 100 MB, por eso va en 5 bloques (`*.part`, 40 MiB cada uno).

## Unir (en el otro servidor)
    git fetch origin encoder-bloques && git checkout origin/encoder-bloques -- encoder_bloques
    sh encoder_bloques/UNIR.sh
Verifica cada bloque, une y comprueba el sha del total. Si falla un `-c`, no uses el archivo.
Luego copia `encoder_anura_fp16.onnx` a `models/encoder/` del servidor (carpeta que ya usa model-service).

## Después
Borra la rama (`git push origin --delete encoder-bloques`) cuando termines; los bloques no deben vivir en main.
El protocolo de subida/descarga por sha está en `PROTOCOLO_ENCODER_Y_OBSERVACIONES.md`.
