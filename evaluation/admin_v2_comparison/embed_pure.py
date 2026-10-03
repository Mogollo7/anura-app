"""Vectores de BioCLIP 1 PURO (sin fine-tuning) para las mismas fotos de la comparación.

Pregunta: ¿el método nuevo del Admin funciona mejor con el encoder puro que con el
encoder con fine-tuning que corre hoy en el teléfono? Mismas fotos, mismo método;
solo cambia el encoder.

Usa hf-hub:imageomics/bioclip desde la caché local (sin red) y su preprocesamiento
oficial, en la GPU del PC.

Uso:  .venv-train\\Scripts\\python.exe evaluation/admin_v2_comparison/embed_pure.py
Salida: evaluation/admin_v2_comparison/embeddings/pure.npz  (paths, vectors)
"""

import json
import os
import sys
import types
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")

import numpy as np
import open_clip
import torch
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(r"D:\Anura")
HERE = ROOT / "evaluation" / "admin_v2_comparison"
DATA_CLEANED = ROOT / "data cleaned"

sys.path.insert(0, str(ROOT / "pipeline_dataset"))
sys.modules.setdefault("sqlite_vec", types.ModuleType("sqlite_vec"))
import paquetes_zonales as pz  # noqa: E402


def rutas():
    guia = json.loads((ROOT / "COLOMBIA_ANURA" / "taxonomy" / "taxonomy_guide.json").read_text(encoding="utf-8"))
    catalogo = json.loads((ROOT / "COLOMBIA_ANURA" / "ANTIOQUIA" / "catalog" / "catalog_v1.json").read_text(encoding="utf-8"))
    visuales = {t["taxon_id"] for t in catalogo["taxa"] if t["visual_status"] == "VISUAL_ENABLED"}
    legado = {tid: guia[tid]["directory_legacy"] for tid in visuales}
    split = {}
    for part in ("train", "val", "test"):
        for e in json.loads(pz.MANIFIESTO.read_text(encoding="utf-8"))["particiones"][part]:
            if not e.get("aumentada"):
                split[e["ruta"].replace("\\", "/")] = part
    refs, prueba = pz.seleccionar_referencias(visuales, legado, split)
    val = np.load(HERE / "embeddings" / "val.npz")["paths"].tolist()
    unk = np.load(HERE / "embeddings" / "unknown.npz")["paths"].tolist()
    claves = [r[0] for r in refs] + [p[0] for p in prueba] + list(val)
    archivos = [DATA_CLEANED / c for c in claves] + [Path(u) for u in unk]
    return claves + list(unk), archivos


def main():
    claves, archivos = rutas()
    print(f"{len(claves)} fotos")
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    model, _, preprocess = open_clip.create_model_and_transforms("hf-hub:imageomics/bioclip")
    model = model.to(dev).eval()
    out = np.zeros((len(claves), 512), dtype=np.float32)
    lote = 64
    with torch.no_grad():
        for i in range(0, len(archivos), lote):
            x = torch.stack([preprocess(Image.open(p).convert("RGB")) for p in archivos[i:i + lote]]).to(dev)
            v = model.encode_image(x).float()
            out[i:i + len(x)] = torch.nn.functional.normalize(v, dim=-1).cpu().numpy()
            if (i // lote) % 20 == 0:
                print(f"  {i + len(x)}/{len(archivos)}")
    np.savez(HERE / "embeddings" / "pure.npz", paths=np.array(claves), vectors=out)
    print("Listo")


if __name__ == "__main__":
    main()
