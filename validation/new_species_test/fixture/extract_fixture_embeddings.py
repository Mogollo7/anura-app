"""
extract_fixture_embeddings.py — Extrae embeddings del fixture usando EXACTAMENTE el mismo
contrato de encoder que Fase 13 (create_model_and_transforms hf-hub:imageomics/bioclip +
checkpoint bioclip_anura_mejor.pt), sin modificar el encoder ni sus checkpoints.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import torch
from PIL import Image
import open_clip

MODEL_NAME = "hf-hub:imageomics/bioclip"
CHECKPOINT_PATH = Path(r"D:\Anura\bioclip\checkpoints\bioclip_anura_mejor.pt")
ENCODER_ONNX_PATH = Path(r"D:\Anura\bioclip\checkpoints\encoder_anura_fp16.onnx")


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    fixture_manifest_path = Path(r"D:\Anura\validation\new_species_test\fixture\fixture_manifest.json")
    with open(fixture_manifest_path, encoding="utf-8") as f:
        fixture = json.load(f)

    print("=== VERIFICANDO CONTRATO DE ENCODER (sin modificar) ===")
    encoder_sha256 = sha256_of_file(ENCODER_ONNX_PATH)
    expected_sha256 = "219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad"
    print(f"  encoder_anura_fp16.onnx SHA256: {encoder_sha256}")
    print(f"  Coincide con contrato Fase 13:  {encoder_sha256 == expected_sha256}")
    assert encoder_sha256 == expected_sha256, "ERROR: encoder fue modificado o es distinto al de Fase 13"

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\nCargando BioCLIP (mismo loader que Fase 13) en {device}...")
    model, _, preprocess = open_clip.create_model_and_transforms(MODEL_NAME)
    checkpoint = torch.load(CHECKPOINT_PATH, map_location="cpu", weights_only=False)
    model.visual.load_state_dict(checkpoint["visual_state_dict"])
    visual_model = model.visual.to(device).eval()

    vectors = []
    image_ids = []
    with torch.no_grad():
        for img_rec in fixture["images"]:
            with Image.open(img_rec["path"]).convert("RGB") as img:
                t_img = preprocess(img).unsqueeze(0).to(device)
            emb = visual_model(t_img)
            emb = emb / emb.norm(dim=-1, keepdim=True)
            vectors.append(emb.cpu().numpy()[0])
            image_ids.append(img_rec["image_id"])

    vectors = np.array(vectors, dtype=np.float32)
    print(f"\nEmbeddings extraidos: {vectors.shape}")
    assert vectors.shape[1] == 512, f"ERROR: dimension {vectors.shape[1]} != 512"

    out_npz = Path(r"D:\Anura\validation\new_species_test\fixture\testus_syntheticus_embeddings.npz")
    np.savez_compressed(
        out_npz,
        embeddings=vectors,
        image_ids=np.array(image_ids),
        species_id=np.array(["ANU_COL_TEST_SYN_001"] * len(vectors)),
    )

    contract = {
        "encoder_id": "bioclip_anura_v1",
        "encoder_sha256": encoder_sha256,
        "embedding_dimension": int(vectors.shape[1]),
        "preprocessing_version": f"open_clip.create_model_and_transforms({MODEL_NAME})",
        "normalization_version": "L2",
        "checkpoint_sha256": sha256_of_file(CHECKPOINT_PATH),
        "n_embeddings": int(vectors.shape[0]),
        "matches_fase13_contract": True,
    }
    with open(Path(r"D:\Anura\validation\new_species_test\fixture\embedding_contract_verified.json"), "w", encoding="utf-8") as f:
        json.dump(contract, f, indent=2)

    print(f"\n[OK] Embeddings guardados: {out_npz}")
    print(f"[OK] Contrato verificado y guardado")
    print(json.dumps(contract, indent=2))


if __name__ == "__main__":
    main()
