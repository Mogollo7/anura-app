"""
upcast_encoder_fp32.py — Convierte encoder_anura_fp16.onnx a cómputo FP32 conservando EXACTAMENTE los
mismos valores de pesos (cada peso FP16 se representa sin pérdida en FP32).

Motivo: en CPU ARM, ONNX Runtime ejecuta el grafo FP16 con kernels lentos (~14 s por imagen en el teléfono).
El grafo FP32 usa los kernels optimizados de MLAS. Se valida contra el set de referencia generado con el FP16.

Uso: python tools/mobile/upcast_encoder_fp32.py --out <ruta.onnx>
"""
import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort
import open_clip
from onnx import TensorProto, numpy_helper
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "bioclip/checkpoints/encoder_anura_fp16.onnx"
GOLDEN = ROOT / "anura-android/app/src/test/resources/golden/golden_v1.json"
IMAGES_ROOT = ROOT / "data cleaned"


def upcast(model: onnx.ModelProto) -> onnx.ModelProto:
    graph = model.graph
    for i, init in enumerate(graph.initializer):
        if init.data_type == TensorProto.FLOAT16:
            arr = numpy_helper.to_array(init).astype(np.float32)
            graph.initializer[i].CopyFrom(numpy_helper.from_array(arr, init.name))
    for node in graph.node:
        if node.op_type == "Cast":
            for attr in node.attribute:
                if attr.name == "to" and attr.i == TensorProto.FLOAT16:
                    attr.i = TensorProto.FLOAT
        for attr in node.attribute:
            if attr.type == onnx.AttributeProto.TENSOR and attr.t.data_type == TensorProto.FLOAT16:
                attr.t.CopyFrom(numpy_helper.from_array(numpy_helper.to_array(attr.t).astype(np.float32), attr.t.name))
    for vi in list(graph.value_info) + list(graph.input) + list(graph.output):
        if vi.type.tensor_type.elem_type == TensorProto.FLOAT16:
            vi.type.tensor_type.elem_type = TensorProto.FLOAT
    return model


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)

    model = upcast(onnx.load(str(SOURCE)))
    onnx.checker.check_model(model)
    onnx.save(model, str(out))
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    print(f"[upcast] {out} {out.stat().st_size / 2**20:.1f} MB sha256={sha}")

    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    _, _, preprocess = open_clip.create_model_and_transforms("hf-hub:imageomics/bioclip")
    s16 = ort.InferenceSession(str(SOURCE), providers=["CPUExecutionProvider"])
    s32 = ort.InferenceSession(str(out), providers=["CPUExecutionProvider"])
    worst = 1.0
    for im in golden["images"]:
        x = preprocess(Image.open(IMAGES_ROOT / im["source_path"].replace("\\", "/"))).unsqueeze(0).numpy()
        t0 = time.perf_counter()
        e16 = s16.run(["embedding"], {"imagen": x})[0][0]
        t1 = time.perf_counter()
        e32 = s32.run(["embedding"], {"imagen": x})[0][0]
        t2 = time.perf_counter()
        e16, e32 = e16 / np.linalg.norm(e16), e32 / np.linalg.norm(e32)
        ref = np.array(im["embedding"], dtype=np.float32)
        cos_golden = float(e32 @ ref)
        worst = min(worst, cos_golden)
        print(f"  {im['file']:<46} cos(fp32,golden)={cos_golden:.6f} cos(fp16,golden)={float(e16 @ ref):.6f} "
              f"fp16={1000*(t1-t0):.0f}ms fp32={1000*(t2-t1):.0f}ms")
    print(f"[upcast] peor coseno vs set de referencia: {worst:.6f}")


if __name__ == "__main__":
    main()
