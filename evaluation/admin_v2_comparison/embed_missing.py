"""Embeddings que faltan para comparar el método del teléfono con el del Admin.

Usa el MISMO encoder que viaja en el teléfono (encoder_anura.onnx, la versión FP32
de encoder_anura_fp16.onnx) y el mismo preprocesamiento (lado corto a 224 bicúbico,
recorte central 224, media/desviación de CLIP). Calcula:

  - val   : imágenes de la partición "val" de las 30 especies visuales del paquete
            (sirven para calibrar radios y detectar clústeres; nunca se usan para medir)
  - unk   : especies desconocidas (unknown_open_set_v2, primario + suplementario)

Antes de calcular, comprueba contra la caché del paquete que el encoder y el
preprocesamiento reproducen los vectores del teléfono.

Uso:  python evaluation/admin_v2_comparison/embed_missing.py
"""

import json
import sys
from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(r"D:\Anura")
OUT = ROOT / "evaluation" / "admin_v2_comparison" / "embeddings"
ENCODER = ROOT / "bioclip" / "checkpoints" / "encoder_anura.onnx"
CACHE = ROOT / "COLOMBIA_ANURA" / "cache" / "embeddings" / "98a6c54d6edb27e2.npz"
DATA_CLEANED = ROOT / "data cleaned"
MANIFIESTO = ROOT / "training" / "manifiesto.json"
MEAN = np.array([0.48145466, 0.4578275, 0.40821073], dtype=np.float32)
STD = np.array([0.26862954, 0.26130258, 0.27577711], dtype=np.float32)


def preprocess(path):
    img = Image.open(path).convert("RGB")
    w, h = img.size
    if w <= h:
        nw, nh = 224, int(224 * h / w)
    else:
        nw, nh = int(224 * w / h), 224
    img = img.resize((nw, nh), Image.BICUBIC)
    left, top = int(round((nw - 224) / 2.0)), int(round((nh - 224) / 2.0))
    img = img.crop((left, top, left + 224, top + 224))
    x = (np.asarray(img, dtype=np.float32) / 255.0 - MEAN) / STD
    return x.transpose(2, 0, 1)[None]


def embed(sess, paths):
    out = np.zeros((len(paths), 512), dtype=np.float32)
    for i, p in enumerate(paths):
        v = sess.run(None, {"imagen": preprocess(p)})[0][0]
        out[i] = v / np.linalg.norm(v)
        if (i + 1) % 100 == 0:
            print(f"    {i + 1}/{len(paths)}")
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    opts = ort.SessionOptions()
    opts.intra_op_num_threads = 8
    sess = ort.InferenceSession(str(ENCODER), opts, providers=["CPUExecutionProvider"])

    # 1. Paridad con el teléfono
    cache = np.load(CACHE)
    muestras = [(p, v) for p, v in zip(cache["paths"][::400], cache["vectors"][::400])]
    cos = []
    for rel, v in muestras:
        e = embed(sess, [DATA_CLEANED / rel])[0]
        cos.append(float(e @ (v / np.linalg.norm(v))))
    print(f"Paridad con la caché del paquete ({len(cos)} fotos): coseno mínimo {min(cos):.5f}")
    if min(cos) < 0.995:
        raise SystemExit("El encoder o el preprocesamiento no reproducen los vectores del teléfono")

    # 2. Validación (partición val) de las especies visuales
    guia = json.loads((ROOT / "COLOMBIA_ANURA" / "taxonomy" / "taxonomy_guide.json").read_text(encoding="utf-8"))
    catalogo = json.loads((ROOT / "COLOMBIA_ANURA" / "ANTIOQUIA" / "catalog" / "catalog_v1.json").read_text(encoding="utf-8"))
    visuales = sorted(t["taxon_id"] for t in catalogo["taxa"] if t["visual_status"] == "VISUAL_ENABLED")
    legado = {tid: guia[tid]["directory_legacy"] for tid in visuales}
    carpeta_a_tid = {v: k for k, v in legado.items()}
    val = []
    for e in json.loads(MANIFIESTO.read_text(encoding="utf-8"))["particiones"]["val"]:
        if e.get("aumentada"):
            continue
        rel = e["ruta"].replace("\\", "/")
        carpeta = rel.split("/")[0]
        if carpeta in carpeta_a_tid and (DATA_CLEANED / rel).exists():
            val.append((rel, carpeta_a_tid[carpeta]))
    print(f"Validación: {len(val)} imágenes")
    if not (OUT / "val.npz").exists():
        emb = embed(sess, [DATA_CLEANED / r for r, _ in val])
        np.savez(OUT / "val.npz", paths=np.array([r for r, _ in val]), taxon=np.array([t for _, t in val]), vectors=emb)

    # 3. Desconocidas
    if not (OUT / "unknown.npz").exists():
        paths, species, obs = [], [], []
        for f in ("validation/fase23a_open_set_automatic/embeddings/unknown_embeddings.npz",
                  "validation/open_set_calibration_v1/supplementary_unknown_embeddings.npz"):
            d = np.load(ROOT / f, allow_pickle=True)
            for p, s in zip(d["paths"], d["species"]):
                if Path(p).exists():
                    paths.append(str(p))
                    species.append(str(s).replace(" ", "_"))
                    name = Path(p).name
                    obs.append(name.split("_")[2] if name.startswith("col_obs_") else "")
        print(f"Desconocidas: {len(paths)} imágenes")
        emb = embed(sess, paths)
        np.savez(OUT / "unknown.npz", paths=np.array(paths), species=np.array(species), obs=np.array(obs), vectors=emb)
    print("Listo:", OUT)


if __name__ == "__main__":
    main()
