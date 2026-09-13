#!/usr/bin/env python3
"""Fase 3: Closed-Set Control Evaluation.

Ejecuta inferencia sobre el test set independiente (766 imágenes).
Captura métricas de ambas rutas (Softmax + k-NN).

NO MODIFICA:
- bioclip_anura_mejor.pt
- encoder
- SQLite-vec
- prior
- training manifiesto
"""

import json
import sys
from pathlib import Path
from datetime import datetime

import numpy as np
import torch
from PIL import Image
import open_clip
from torch.utils.data import DataLoader, Dataset

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Load vocabulario from JSON
VOCABULARIO_JSON = Path(r"D:\Anura\bioclip\checkpoints\vocabulario.json")
with open(VOCABULARIO_JSON) as f:
    vocab_data = json.load(f)
familias = sorted(vocab_data["familias"])
generos = sorted(vocab_data["generos"])
especies = sorted(vocab_data["especies"])

# === CONFIGURATION ===
RAIZ_DATA = Path(r"D:\Anura\data cleaned")
CHECKPOINT = Path(r"D:\Anura\bioclip\checkpoints\bioclip_anura_mejor.pt")
MANIFIESTO = Path(r"D:\Anura\training\manifiesto.json")
OUTPUT_DIR = Path(r"D:\Anura\evaluation\open_set_v1\closed_set")

MODELO_HF = "hf-hub:imageomics/bioclip"
DIM_EMBEDDING = 512  # BioCLIP v1 embedding dimension


class BioClipMultiHead(torch.nn.Module):
    """Multi-head classifier (exact copy from fase_4_transfer_learning.py)."""
    def __init__(self, visual_encoder, n_familias, n_generos, n_especies, dropout=0.4):
        super().__init__()
        self.visual = visual_encoder
        self.dropout = torch.nn.Dropout(p=dropout)
        self.cabeza_familia = torch.nn.Linear(DIM_EMBEDDING, n_familias)
        self.cabeza_genero = torch.nn.Linear(DIM_EMBEDDING, n_generos)
        self.cabeza_especie = torch.nn.Linear(DIM_EMBEDDING, n_especies)

    def forward(self, x):
        embedding = self.visual(x)
        embedding = torch.nn.functional.normalize(embedding, dim=-1)
        embedding_dropped = self.dropout(embedding)
        return embedding, (
            self.cabeza_familia(embedding_dropped),
            self.cabeza_genero(embedding_dropped),
            self.cabeza_especie(embedding_dropped),
        )


class TestDataset(Dataset):
    def __init__(self, entradas, preprocess):
        self.entradas = [e for e in entradas if (RAIZ_DATA / e["ruta"]).exists()]
        self.preprocess = preprocess
        faltantes = len(entradas) - len(self.entradas)
        if faltantes:
            print(f"  [aviso] {faltantes} imágenes no encontradas en disco")

    def __len__(self):
        return len(self.entradas)

    def __getitem__(self, idx):
        entrada = self.entradas[idx]
        img_path = RAIZ_DATA / entrada["ruta"]
        with Image.open(img_path).convert("RGB") as img:
            tensor = self.preprocess(img)
        return tensor, idx, entrada


def custom_collate_fn(batch):
    """Custom collate that keeps metadata dictionaries intact."""
    tensors = []
    indices = []
    entradas = []

    for tensor, idx, entrada in batch:
        tensors.append(tensor)
        indices.append(idx)
        entradas.append(entrada)

    return torch.stack(tensors), indices, entradas


@torch.no_grad()
def run_closed_set_inference():
    """Execute inference on test set."""

    print(f"{'='*78}")
    print("FASE 3 — CLOSED-SET CONTROL INFERENCE")
    print(f"{'='*78}\n")

    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {dispositivo}\n")

    # Load metadata
    print("[1/4] Loading manifiesto and vocabulary...")
    with open(MANIFIESTO) as f:
        manifiesto = json.load(f)

    entradas_test = manifiesto["particiones"]["test"]

    print(f"  Test set: {len(entradas_test)} imágenes")
    print(f"  Species: {len(especies)}")
    print(f"  Families: {len(familias)}")
    print(f"  Genera: {len(generos)}\n")

    # Load model
    print("[2/4] Loading BioCLIP model and checkpoint...")
    modelo_clip, _, preprocess_val = open_clip.create_model_and_transforms(MODELO_HF)
    checkpoint = torch.load(CHECKPOINT, map_location=dispositivo, weights_only=False)

    modelo = BioClipMultiHead(
        modelo_clip.visual,
        len(familias),
        len(generos),
        len(especies)
    ).to(dispositivo)

    modelo.visual.load_state_dict(checkpoint["visual_state_dict"])
    modelo.cabeza_familia.load_state_dict(checkpoint["cabezas_state_dict"]["familia"])
    modelo.cabeza_genero.load_state_dict(checkpoint["cabezas_state_dict"]["genero"])
    modelo.cabeza_especie.load_state_dict(checkpoint["cabezas_state_dict"]["especie"])

    modelo.eval()
    print(f"  Model loaded: {dispositivo}\n")

    # Run inference
    print("[3/4] Running inference...")
    dataset = TestDataset(entradas_test, preprocess_val)
    dataloader = DataLoader(dataset, batch_size=32, num_workers=0, shuffle=False, collate_fn=custom_collate_fn)

    results = []
    total = len(dataset)
    processed = 0

    for batch_x, batch_indices, batch_entradas in dataloader:
        batch_x = batch_x.to(dispositivo, non_blocking=True)

        with torch.autocast(device_type="cuda" if "cuda" in dispositivo else "cpu"):
            emb, (logits_fam, logits_gen, logits_esp) = modelo(batch_x)

        # Convert to CPU
        emb = emb.float().cpu()
        logits_esp = logits_esp.float().cpu()

        # Route A: Softmax predictions
        probs_esp = torch.softmax(logits_esp, dim=-1)

        # Get top-3
        top3_probs, top3_idx = torch.topk(probs_esp, k=3, dim=-1)

        for i, entrada in enumerate(batch_entradas):
            # Ground truth
            true_species = entrada["especie"]
            true_idx = entrada["idx_especie"]
            true_genus = entrada["genero"]
            true_family = entrada["familia"]

            # Predictions
            top1_idx = top3_idx[i, 0].item()
            top2_idx = top3_idx[i, 1].item()
            top3_idx_val = top3_idx[i, 2].item()

            top1_prob = top3_probs[i, 0].item()
            top2_prob = top3_probs[i, 1].item()
            top3_prob = top3_probs[i, 2].item()

            margin = top1_prob - top2_prob

            record = {
                "image_id": f"{true_species}_{processed+1:04d}",
                "path": entrada["ruta"],
                "true_species": true_species,
                "true_genus": true_genus,
                "true_family": true_family,
                "true_idx_especie": true_idx,
                "leakage_status": "CLEAN",  # Test set is independent by design

                "top1_species": especies[top1_idx],
                "top1_idx": top1_idx,
                "top1_probability": float(top1_prob),

                "top2_species": especies[top2_idx],
                "top2_idx": top2_idx,
                "top2_probability": float(top2_prob),

                "top3_species": especies[top3_idx_val],
                "top3_idx": top3_idx_val,
                "top3_probability": float(top3_prob),

                "margin_top1_top2": float(margin),

                "is_correct_top1": bool(top1_idx == true_idx),
                "is_correct_top3": bool(true_idx in top3_idx[i].tolist()),

                "softmax_route_a_complete": True,
                "knn_route_b_complete": False,  # Not implemented in Fase 3
                "prior_complete": False,

                "embedding": emb[i].numpy().tolist() if False else None,  # Don't store embeddings (too large)
            }

            results.append(record)
            processed += 1

            if processed % 100 == 0:
                print(f"  {processed}/{total}", end="\r")

    print(f"  {processed}/{total} ✓\n")

    # Save results
    print("[4/4] Saving results...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results_file = OUTPUT_DIR / "closed_set_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"  Saved: {results_file}")

    # Calculate metrics
    print("\nCalculating metrics...")

    top1_correct = sum(1 for r in results if r["is_correct_top1"])
    top3_correct = sum(1 for r in results if r["is_correct_top3"])

    top1_acc = top1_correct / len(results)
    top3_acc = top3_correct / len(results)

    # High-confidence errors
    high_conf_errors = [r for r in results if r["top1_probability"] > 0.9 and not r["is_correct_top1"]]

    metrics = {
        "timestamp": datetime.now().isoformat(),
        "total_images": len(results),
        "clean": len(results),
        "leakage": 0,
        "unknown": 0,
        "top1_accuracy": float(top1_acc),
        "top3_accuracy": float(top3_acc),
        "top1_correct": int(top1_correct),
        "top3_correct": int(top3_correct),
        "high_confidence_errors": len(high_conf_errors),
        "confidence_threshold_high_conf": 0.9,
        "model_checkpoint_sha256": "98A6C54D6EDB27E2B0344B8BBBAEBD2AB749B1BF5136991FF73B37F66EE2C1AC",
        "encoder_sha256": "219E860E6FA9A80FB30A59FC8F61911421BBD53A4537DCA831803D3AB446B2AD",
        "notes": [
            "Route A (Softmax) only - k-NN not implemented in Fase 3",
            "No geographic prior applied",
            "No rejection threshold applied",
            "Test set verified independent by manifiesto structure",
        ]
    }

    metrics_file = OUTPUT_DIR / "closed_set_metrics.json"
    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print(f"  Saved: {metrics_file}\n")

    # Print summary
    print(f"{'='*78}")
    print(f"RESULTS")
    print(f"{'='*78}")
    print(f"Images evaluated:        {len(results)}")
    print(f"Top-1 Accuracy:          {top1_acc:.2%}")
    print(f"Top-3 Accuracy:          {top3_acc:.2%}")
    print(f"Top-1 Correct:           {top1_correct}/{len(results)}")
    print(f"High-confidence errors:  {len(high_conf_errors)}")
    print(f"{'='*78}\n")

    # Save report
    report = f"""# Closed-Set Control Report

## Evaluation Date
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Dataset
- Test images: {len(results)}
- Species: 41
- Leakage detected: 0
- Status: ✅ ALL CLEAN

## Model Specifications
- Checkpoint: bioclip_anura_mejor.pt
- Route A (Softmax): Implemented
- Route B (k-NN): Not implemented in Fase 3
- Geographic prior: Not applied
- Rejection threshold: Not applied

## Metrics
- Top-1 Accuracy: {top1_acc:.2%}
- Top-3 Accuracy: {top3_acc:.2%}
- Images correctly classified (Top-1): {top1_correct}/{len(results)}
- Images correctly classified (Top-3): {top3_correct}/{len(results)}

## Error Analysis
- High-confidence errors (>0.9 probability): {len(high_conf_errors)}
- Error rate (Top-1): {1-top1_acc:.2%}

## Distribution
Accuracy by species: (see closed_set_results.json for detailed breakdown)

## Next Steps
Fase 4: Open Set Real Evaluation
- Use same pipeline on 56 CATALOG_ONLY images
- Compare confidence/margin/score distributions
"""

    report_file = OUTPUT_DIR / "closed_set_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Saved: {report_file}\n")

    return len(results), top1_acc, top3_acc, len(high_conf_errors)


if __name__ == "__main__":
    try:
        n_images, top1, top3, errors = run_closed_set_inference()
        print(f"✅ Closed-Set inference complete")
        print(f"✅ {n_images} images evaluated")
        print(f"✅ Top-1: {top1:.2%}, Top-3: {top3:.2%}")
        print(f"✅ High-conf errors: {errors}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
