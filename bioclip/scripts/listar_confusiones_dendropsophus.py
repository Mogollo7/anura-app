"""Lista las imágenes de test de Dendropsophus mal clasificadas, con ruta real
y predicción del modelo, para inspección visual manual (posible mal etiquetado
en origen — Dendropsophus es un género con alta tasa de confusión conocida en
iNaturalist mismo).

Uso:
    python bioclip/scripts/listar_confusiones_dendropsophus.py
"""

import json
import sys
from pathlib import Path

import open_clip
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "training"))

from fase_4_transfer_learning import BioClipMultiHead  # noqa: E402
from taxonomia import vocabularios  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ_DATOS = Path(r"D:\Anura\data cleaned")
MANIFIESTO = Path(r"D:\Anura\training\manifiesto.json")
CHECKPOINT = Path(r"D:\Anura\bioclip\checkpoints\bioclip_anura_mejor.pt")
MODELO_HF = "hf-hub:imageomics/bioclip"


class DatasetTest(Dataset):
    def __init__(self, entradas, preprocess):
        self.entradas = entradas
        self.preprocess = preprocess

    def __len__(self):
        return len(self.entradas)

    def __getitem__(self, idx):
        entrada = self.entradas[idx]
        with Image.open(RAIZ_DATOS / entrada["ruta"]).convert("RGB") as img:
            tensor = self.preprocess(img)
        return tensor, entrada["idx_especie"], idx


def main():
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    familias, generos, especies = vocabularios()
    manifiesto = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    entradas_test = manifiesto["particiones"]["test"]

    modelo_clip, _, preprocess_val = open_clip.create_model_and_transforms(MODELO_HF)
    checkpoint = torch.load(CHECKPOINT, map_location=dispositivo, weights_only=False)
    modelo = BioClipMultiHead(modelo_clip.visual, len(familias), len(generos), len(especies)).to(dispositivo)
    modelo.visual.load_state_dict(checkpoint["visual_state_dict"])
    modelo.cabeza_familia.load_state_dict(checkpoint["cabezas_state_dict"]["familia"])
    modelo.cabeza_genero.load_state_dict(checkpoint["cabezas_state_dict"]["genero"])
    modelo.cabeza_especie.load_state_dict(checkpoint["cabezas_state_dict"]["especie"])
    modelo.eval()

    dl = DataLoader(DatasetTest(entradas_test, preprocess_val), batch_size=32, num_workers=2)

    resultados = []
    with torch.no_grad():
        for x, y_esp, idxs in dl:
            x = x.to(dispositivo)
            with torch.autocast(device_type="cuda" if "cuda" in dispositivo else "cpu"):
                _, (_, _, logits_esp) = modelo(x)
            preds = logits_esp.float().argmax(-1).cpu()
            for i, y, p in zip(idxs.tolist(), y_esp.tolist(), preds.tolist()):
                resultados.append((i, y, p))

    print(f"{'RUTA':<70}{'REAL':<28}{'PREDICHO':<28}")
    print("-" * 126)
    n_mostradas = 0
    for i, y, p in resultados:
        especie_real = especies[y]
        especie_pred = especies[p]
        if not especie_real.startswith("Dendropsophus"):
            continue
        if y == p:
            continue
        ruta = entradas_test[i]["ruta"]
        print(f"{ruta:<70}{especie_real:<28}{especie_pred:<28}")
        n_mostradas += 1

    print(f"\nTotal fallos en Dendropsophus: {n_mostradas}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
