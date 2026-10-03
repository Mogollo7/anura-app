"""
extract_clean_known_embeddings.py — Extrae embeddings del clean_known_manifest.json
usando EXACTAMENTE el mismo encoder congelado que Fase 13 (mismo loader, mismo checkpoint).
"""
import json
from pathlib import Path

import numpy as np
import torch
from PIL import Image
import open_clip

MODEL_NAME = "hf-hub:imageomics/bioclip"
CHECKPOINT_PATH = Path(r"D:\Anura\bioclip\checkpoints\bioclip_anura_mejor.pt")
DATA_ROOT = Path(r"D:\Anura\data cleaned")


def main():
    manifest_path = Path(r"D:\Anura\validation\fase16_clean_open_set\clean_known_manifest.json")
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Cargando BioCLIP en {device}...")
    model, _, preprocess = open_clip.create_model_and_transforms(MODEL_NAME)
    checkpoint = torch.load(CHECKPOINT_PATH, map_location="cpu", weights_only=False)
    model.visual.load_state_dict(checkpoint["visual_state_dict"])
    visual_model = model.visual.to(device).eval()

    vectors = []
    image_ids = []
    species_ids = []
    n = len(manifest["images"])
    print(f"Extrayendo {n} embeddings...")

    with torch.no_grad():
        for i, img_rec in enumerate(manifest["images"]):
            full_path = DATA_ROOT / img_rec["path"]
            with Image.open(full_path).convert("RGB") as img:
                t_img = preprocess(img).unsqueeze(0).to(device)
            emb = visual_model(t_img)
            emb = emb / emb.norm(dim=-1, keepdim=True)
            vectors.append(emb.cpu().numpy()[0])
            image_ids.append(img_rec["image_id"])
            species_ids.append(img_rec["species_id"])
            if (i + 1) % 500 == 0:
                print(f"  {i+1}/{n}")

    vectors = np.array(vectors, dtype=np.float32)
    print(f"Embeddings: {vectors.shape}")

    out_npz = Path(r"D:\Anura\validation\fase16_clean_open_set\clean_known_embeddings.npz")
    np.savez_compressed(out_npz, embeddings=vectors, image_ids=np.array(image_ids), species_ids=np.array(species_ids))
    print(f"[OK] {out_npz}")


if __name__ == "__main__":
    main()
