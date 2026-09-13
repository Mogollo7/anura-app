"""Fase 4 — Open Set Real, control Softmax únicamente.

Usa el manifiesto de open-set como única fuente de selección y reutiliza la
misma arquitectura, checkpoint y preprocessing de la evaluación de Fase 3.
No ejecuta k-NN, prior ni rechazo.
"""

import hashlib
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import torch
import open_clip
from PIL import Image
from torch.utils.data import DataLoader, Dataset

ROOT = Path(r"D:\Anura")
MANIFEST = ROOT / "evaluation" / "open_set_v1" / "dataset" / "open_set_manifest.json"
DATA_ROOT = ROOT / "data cleaned"
VOCABULARY = ROOT / "bioclip" / "checkpoints" / "vocabulario.json"
CHECKPOINT = ROOT / "bioclip" / "checkpoints" / "bioclip_anura_mejor.pt"
OUTPUT = ROOT / "evaluation" / "open_set_v1" / "open_set"
MODEL_NAME = "hf-hub:imageomics/bioclip"
EMBEDDING_DIM = 512
EXPECTED_COUNTS = {"Hyloxalus_picachos": 15, "Sachatamia_electrops": 41}


with VOCABULARY.open(encoding="utf-8") as handle:
    VOCAB = json.load(handle)
SPECIES = sorted(VOCAB["especies"])
GENERA = sorted(VOCAB["generos"])
FAMILIES = sorted(VOCAB["familias"])


class BioClipMultiHead(torch.nn.Module):
    def __init__(self, visual_encoder, n_families, n_genera, n_species, dropout=0.4):
        super().__init__()
        self.visual = visual_encoder
        self.dropout = torch.nn.Dropout(p=dropout)
        self.family_head = torch.nn.Linear(EMBEDDING_DIM, n_families)
        self.genus_head = torch.nn.Linear(EMBEDDING_DIM, n_genera)
        self.species_head = torch.nn.Linear(EMBEDDING_DIM, n_species)

    def forward(self, inputs):
        embedding = torch.nn.functional.normalize(self.visual(inputs), dim=-1)
        dropped = self.dropout(embedding)
        return embedding, (
            self.family_head(dropped),
            self.genus_head(dropped),
            self.species_head(dropped),
        )


class OpenSetDataset(Dataset):
    def __init__(self, entries, preprocess):
        self.entries = entries
        self.preprocess = preprocess

    def __len__(self):
        return len(self.entries)

    def __getitem__(self, index):
        entry = self.entries[index]
        with Image.open(DATA_ROOT / entry["path"]).convert("RGB") as image:
            return self.preprocess(image), index


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_entries():
    with MANIFEST.open(encoding="utf-8") as handle:
        manifest = json.load(handle)
    entries = [
        entry for entry in manifest
        if entry.get("leakage_status") == "CLEAN"
        and entry.get("open_set_group") == "CATALOG_ONLY"
    ]
    if len(entries) != 56:
        raise RuntimeError(f"Selección inesperada: {len(entries)} imágenes; se esperaban 56")
    counts = Counter(entry["true_species"] for entry in entries)
    if dict(counts) != EXPECTED_COUNTS:
        raise RuntimeError(f"Distribución inesperada: {dict(counts)}")
    for entry in entries:
        image_path = DATA_ROOT / entry["path"]
        if not image_path.exists():
            raise FileNotFoundError(image_path)
        if sha256(image_path) != entry["sha256"]:
            raise RuntimeError(f"SHA256 no coincide: {image_path}")
    return entries


@torch.no_grad()
def main():
    entries = load_entries()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"FASE 4 — OPEN SET REAL (Softmax únicamente), device={device}")
    print(f"Imágenes: {len(entries)}; distribución: {dict(Counter(e['true_species'] for e in entries))}")

    clip_model, _, preprocess = open_clip.create_model_and_transforms(MODEL_NAME)
    checkpoint = torch.load(CHECKPOINT, map_location=device, weights_only=False)
    model = BioClipMultiHead(
        clip_model.visual, len(FAMILIES), len(GENERA), len(SPECIES)
    ).to(device)
    model.visual.load_state_dict(checkpoint["visual_state_dict"])
    model.family_head.load_state_dict(checkpoint["cabezas_state_dict"]["familia"])
    model.genus_head.load_state_dict(checkpoint["cabezas_state_dict"]["genero"])
    model.species_head.load_state_dict(checkpoint["cabezas_state_dict"]["especie"])
    model.eval()

    loader = DataLoader(
        OpenSetDataset(entries, preprocess),
        batch_size=32,
        num_workers=0,
        shuffle=False,
    )
    results = []
    for batch, indices in loader:
        batch = batch.to(device)
        with torch.autocast(device_type="cuda" if device == "cuda" else "cpu"):
            _, (_, _, species_logits) = model(batch)
        probabilities = torch.softmax(species_logits.float().cpu(), dim=-1)
        top_probs, top_indices = torch.topk(probabilities, k=3, dim=-1)
        for row, index in enumerate(indices.tolist()):
            entry = entries[index]
            results.append({
                "image_id": entry["image_id"],
                "path": entry["path"],
                "true_species": entry["true_species"],
                "open_set_group": entry["open_set_group"],
                "leakage_status": entry["leakage_status"],
                "top1_species": SPECIES[top_indices[row, 0].item()],
                "top1_probability": top_probs[row, 0].item(),
                "top2_species": SPECIES[top_indices[row, 1].item()],
                "top2_probability": top_probs[row, 1].item(),
                "top3_species": SPECIES[top_indices[row, 2].item()],
                "top3_probability": top_probs[row, 2].item(),
                "margin_top1_top2": (top_probs[row, 0] - top_probs[row, 1]).item(),
                "softmax_route_a_complete": True,
                "knn_route_b_complete": False,
                "prior_complete": False,
                "rejection_applied": False,
            })

    OUTPUT.mkdir(parents=True, exist_ok=True)
    results_path = OUTPUT / "open_set_results.json"
    results_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    known_species = set(SPECIES)
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "total_images": len(results),
        "clean": sum(r["leakage_status"] == "CLEAN" for r in results),
        "leakage": sum(r["leakage_status"] != "CLEAN" for r in results),
        "catalog_only": sum(r["open_set_group"] == "CATALOG_ONLY" for r in results),
        "predicted_known_class_rate": sum(r["top1_species"] in known_species for r in results) / len(results),
        "top1_probability_mean": sum(r["top1_probability"] for r in results) / len(results),
        "margin_mean": sum(r["margin_top1_top2"] for r in results) / len(results),
        "by_true_species": {
            species: {
                "count": sum(r["true_species"] == species for r in results),
                "top1_probability_mean": sum(
                    r["top1_probability"] for r in results if r["true_species"] == species
                ) / EXPECTED_COUNTS[species],
            }
            for species in EXPECTED_COUNTS
        },
        "comparison": "Fase 3 Softmax únicamente vs Fase 4 Softmax únicamente",
        "knn_executed": False,
        "prior_applied": False,
        "rejection_applied": False,
    }
    (OUTPUT / "open_set_metrics.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    report = [
        "# Fase 4 — Open Set Real",
        "",
        f"- Fecha: {metrics['timestamp']}",
        f"- Imágenes evaluadas: {metrics['total_images']}",
        f"- CLEAN / leakage: {metrics['clean']} / {metrics['leakage']}",
        f"- CATALOG_ONLY: {metrics['catalog_only']}",
        f"- Top-1 predicho dentro de las 41 clases: {metrics['predicted_known_class_rate']:.2%}",
        f"- Probabilidad Top-1 media: {metrics['top1_probability_mean']:.6f}",
        f"- Margen Top-1 - Top-2 medio: {metrics['margin_mean']:.6f}",
        "",
        "Comparación primaria: Fase 3 Softmax únicamente vs Fase 4 Softmax únicamente.",
        "No se ejecutaron k-NN, prior geográfico, rechazo ni thresholds.",
    ]
    (OUTPUT / "open_set_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Resultados guardados en {OUTPUT}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        raise
