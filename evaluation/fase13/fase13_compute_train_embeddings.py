import os
import json
import sys
from pathlib import Path
import numpy as np
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
import open_clip

MODEL_NAME = "hf-hub:imageomics/bioclip"

class TrainDataset(Dataset):
    def __init__(self, records, base_dir, transform):
        self.records = records
        self.base_dir = base_dir
        self.transform = transform
        self.valid_items = []

        for r in records:
            rel_path = r.get('OriginalPath', r.get('FileName', r.get('ruta', '')))
            sp = r.get('Species', r.get('especie', ''))
            sha = r.get('SHA256', r.get('sha256', ''))

            full_path = base_dir / rel_path
            if not full_path.exists():
                raise FileNotFoundError(f"Imagen no encontrada: {full_path}")

            self.valid_items.append((full_path, str(rel_path), sp, sha))

    def __len__(self):
        return len(self.valid_items)

    def __getitem__(self, idx):
        full_path, rel_path, sp, sha = self.valid_items[idx]
        with Image.open(full_path).convert("RGB") as img:
            t_img = self.transform(img)
        return t_img, sp, rel_path, sha

def compute_train_embeddings(manifest_path, out_npz_path, visual_model, device, preprocess):
    if out_npz_path.exists():
        print(f"Embeddings TRAIN ya existen en {out_npz_path}. Omitiendo cómputo.", flush=True)
        return

    print(f"\n--- Procesando TRAIN (CUDA PyTorch) ---", flush=True)
    with open(manifest_path, 'r', encoding='utf-8-sig') as f:
        records = json.load(f)
    if not isinstance(records, list):
        records = records.get('records', [])

    base_dir = Path(r"D:\Anura\data cleaned")
    ds = TrainDataset(records, base_dir, preprocess)
    dl = DataLoader(ds, batch_size=32, shuffle=False, num_workers=0)

    vectors = []
    species_list = []
    paths_list = []
    sha256_list = []

    with torch.no_grad():
        for imgs, sps, paths, shas in dl:
            imgs = imgs.to(device)
            embs = visual_model(imgs)
            embs = embs / embs.norm(dim=-1, keepdim=True)

            vectors.append(embs.cpu().numpy())
            species_list.extend(sps)
            paths_list.extend(paths)
            sha256_list.extend(shas)

    vectors = np.concatenate(vectors, axis=0).astype(np.float32)
    print(f"Vectors shape: {vectors.shape}", flush=True)

    out_npz_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out_npz_path,
        embeddings=vectors,
        species=np.array(species_list),
        paths=np.array(paths_list),
        sha256=np.array(sha256_list)
    )
    print(f"Guardado exitoso en: {out_npz_path}", flush=True)

def run():
    train_manifest_path = Path(r"D:\Anura\evaluation\fase13\manifests\TRAIN_manifest.json")
    out_dir = Path(r"D:\Anura\evaluation\fase13\embeddings")
    train_out_npz = out_dir / "train_embeddings.npz"

    if train_out_npz.exists():
        print(f"Embeddings TRAIN ya existen en {out_dir}. Continuando.", flush=True)
        print("\n>>> TRAIN EMBEDDINGS: COMPLETADO <<<", flush=True)
        return

    if not train_manifest_path.exists():
        print(f"ERROR: TRAIN manifest no encontrado en {train_manifest_path}")
        print("Ejecuta primero: fase13_generate_train_manifest.py")
        import sys
        sys.exit(1)

    checkpoint_path = Path(r"D:\Anura\bioclip\checkpoints\bioclip_anura_mejor.pt")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Cargando modelo PyTorch BioCLIP en dispositivo: {device}...", flush=True)

    model, _, preprocess = open_clip.create_model_and_transforms(MODEL_NAME)
    checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
    model.visual.load_state_dict(checkpoint['visual_state_dict'])
    visual_model = model.visual.to(device).eval()

    compute_train_embeddings(train_manifest_path, train_out_npz, visual_model, device, preprocess)

    print("\n>>> TRAIN EMBEDDINGS: COMPLETADO <<<", flush=True)

if __name__ == "__main__":
    run()
