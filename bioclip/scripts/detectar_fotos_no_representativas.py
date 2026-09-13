"""Detecta fotos de diagnóstico de campo (mano humana) o múltiples individuos
(amplexo) usando BioCLIP zero-shot texto-imagen, sobre TODO el dataset limpio
(las 41+ especies de `data cleaned`, no solo el manifiesto de entrenamiento).

No es un filtro perfecto — es un candidato para revisión manual, priorizado por
similitud de texto. Los prompts de "hábitat natural" compiten contra los de
"mano"/"amplexo": si un prompt sospechoso gana con margen, se marca para revisar.

Uso:
    python bioclip/scripts/detectar_fotos_no_representativas.py
"""

import json
import sys
from pathlib import Path

import open_clip
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(r"D:\Anura\data cleaned")
INVENTARIO = RAIZ / "dataset_limpio.json"
SALIDA = Path(r"D:\Anura\bioclip\evaluation\fotos_no_representativas.json")
MODELO_HF = "hf-hub:imageomics/bioclip"

PROMPTS_SOSPECHOSOS = [
    "a photo of a frog held in a human hand",
    "a close-up photo of a frog's hand or foot held by human fingers, showing webbing",
    "a photo of a frog's white belly held upside down by a person",
    "a photo of two frogs mating in amplexus, one on top of the other",
]
PROMPTS_NATURALES = [
    "a photo of a frog on a leaf in its natural habitat",
    "a photo of a frog on a branch or tree trunk in the forest",
    "a photo of a single frog on the ground or on a rock",
]


class DatasetInventario(Dataset):
    def __init__(self, registros, preprocess):
        self.registros = registros
        self.preprocess = preprocess

    def __len__(self):
        return len(self.registros)

    def __getitem__(self, idx):
        ruta = self.registros[idx]["ruta"]
        try:
            with Image.open(RAIZ / ruta).convert("RGB") as img:
                return self.preprocess(img), idx
        except (OSError, ValueError):
            return torch.zeros(3, 224, 224), -1


def main():
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Dispositivo: {dispositivo}")

    inventario = json.loads(INVENTARIO.read_text(encoding="utf-8"))
    registros = [r for r in inventario["imagenes"] if r.get("estado") != "cuarentena_pendiente_seleccion_manual"]
    print(f"Imágenes a analizar: {len(registros)}")

    modelo, _, preprocess = open_clip.create_model_and_transforms(MODELO_HF)
    tokenizer = open_clip.get_tokenizer(MODELO_HF)
    modelo = modelo.to(dispositivo).eval()

    todos_prompts = PROMPTS_SOSPECHOSOS + PROMPTS_NATURALES
    with torch.no_grad():
        texto_tok = tokenizer(todos_prompts).to(dispositivo)
        emb_texto = modelo.encode_text(texto_tok)
        emb_texto = emb_texto / emb_texto.norm(dim=-1, keepdim=True)

    ds = DatasetInventario(registros, preprocess)
    dl = DataLoader(ds, batch_size=64, num_workers=4)

    n_sosp = len(PROMPTS_SOSPECHOSOS)
    candidatos = []
    procesadas = 0
    with torch.no_grad():
        for x, idxs in dl:
            x = x.to(dispositivo)
            with torch.autocast(device_type="cuda" if "cuda" in dispositivo else "cpu"):
                emb_img = modelo.encode_image(x)
            emb_img = emb_img.float()
            emb_img = emb_img / emb_img.norm(dim=-1, keepdim=True)
            sim = (emb_img @ emb_texto.float().T).cpu()  # (batch, n_prompts)

            mejor_sospechoso, _ = sim[:, :n_sosp].max(dim=1)
            mejor_natural, _ = sim[:, n_sosp:].max(dim=1)
            margen = mejor_sospechoso - mejor_natural

            for j, idx in enumerate(idxs.tolist()):
                if idx == -1:
                    continue
                procesadas += 1
                if margen[j].item() > 0.02:  # el prompt sospechoso gana con margen
                    prompt_idx = sim[j, :n_sosp].argmax().item()
                    candidatos.append({
                        "ruta": registros[idx]["ruta"],
                        "especie": registros[idx]["especie"],
                        "prompt_sospechoso": PROMPTS_SOSPECHOSOS[prompt_idx],
                        "similitud_sospechosa": float(mejor_sospechoso[j]),
                        "similitud_natural": float(mejor_natural[j]),
                        "margen": float(margen[j]),
                    })
            if procesadas % 2048 < 64:
                print(f"  procesadas {procesadas}/{len(registros)}...")

    candidatos.sort(key=lambda c: -c["margen"])
    print(f"\nTotal candidatas a revisar: {len(candidatos)} de {procesadas} ({len(candidatos)/procesadas:.1%})")

    print(f"\n{'RUTA':<65}{'ESPECIE':<28}{'MARGEN':>8}")
    print("-" * 101)
    for c in candidatos[:60]:
        print(f"{c['ruta']:<65}{c['especie']:<28}{c['margen']:>8.3f}")

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps({
        "prompts_sospechosos": PROMPTS_SOSPECHOSOS,
        "prompts_naturales": PROMPTS_NATURALES,
        "total_analizadas": procesadas,
        "candidatos": candidatos,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nGuardado en {SALIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
