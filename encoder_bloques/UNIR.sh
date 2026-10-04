#!/bin/sh
# Une los bloques y verifica el sha256 del ONNX completo.
set -e
cd "$(dirname "$0")"
sha256sum -c SHA256_BLOQUES.txt
cat encoder_anura_fp16.onnx.*.part > encoder_anura_fp16.onnx
echo "219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad  encoder_anura_fp16.onnx" | sha256sum -c
