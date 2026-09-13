"""Identifica, entre las fotos de Sachatamia_electrops recién scrapeadas, cuáles
muestran el vientre translúcido (rasgo diagnóstico real de Centrolenidae —
"ranas de cristal": se ve a los órganos internos a través de la piel ventral).

A diferencia del resto del dataset (donde vientre/mano = descartar), aquí el
vientre SÍ es información válida y valiosa: es literalmente el carácter que
da nombre al grupo. Se marca cada foto con su tipo (dorsal/lateral vs ventral
translúcido) en vez de descartar una u otra — ambas aportan, pero no deben
mezclarse sin distinción porque son dos "vistas" visualmente muy distintas de
la misma especie.

Uso:
    python bioclip/scripts/detectar_vientre_translucido.py
"""

import json
import sys
from pathlib import Path

import open_clip
import torch
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CARPETA = Path(r"D:\Anura\data dirty\Sachatamia_electrops\fotos")
SALIDA = Path(r"D:\Anura\bioclip\evaluation\sachatamia_clasificacion_vista.json")
MODELO_HF = "hf-hub:imageomics/bioclip"

PROMPTS = [
    "a photo of a glass frog's translucent ventral skin showing internal organs and bones",
    "a photo of a frog's dorsal side, green skin, seen from above or the side in its habitat",
]


def main():
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    archivos = sorted(
        p for p in CARPETA.iterdir()
        if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )
    print(f"Fotos encontradas: {len(archivos)}")

    modelo, _, preprocess = open_clip.create_model_and_transforms(MODELO_HF)
    tokenizer = open_clip.get_tokenizer(MODELO_HF)
    modelo = modelo.to(dispositivo).eval()

    with torch.no_grad():
        texto_tok = tokenizer(PROMPTS).to(dispositivo)
        emb_texto = modelo.encode_text(texto_tok)
        emb_texto = emb_texto / emb_texto.norm(dim=-1, keepdim=True)

    resultados = []
    with torch.no_grad():
        for ruta in archivos:
            try:
                with Image.open(ruta).convert("RGB") as img:
                    x = preprocess(img).unsqueeze(0).to(dispositivo)
            except (OSError, ValueError):
                continue
            with torch.autocast(device_type="cuda" if "cuda" in dispositivo else "cpu"):
                emb_img = modelo.encode_image(x)
            emb_img = emb_img.float()
            emb_img = emb_img / emb_img.norm(dim=-1, keepdim=True)
            sim = (emb_img @ emb_texto.float().T).cpu().squeeze(0)
            es_ventral = bool(sim[0] > sim[1])
            resultados.append({
                "archivo": ruta.name,
                "sim_ventral_translucido": float(sim[0]),
                "sim_dorsal_habitat": float(sim[1]),
                "vista": "ventral_translucido" if es_ventral else "dorsal_lateral",
            })

    ventral = [r for r in resultados if r["vista"] == "ventral_translucido"]
    dorsal = [r for r in resultados if r["vista"] == "dorsal_lateral"]
    print(f"\nVentral translúcido: {len(ventral)}")
    for r in sorted(ventral, key=lambda r: -r["sim_ventral_translucido"]):
        print(f"  {r['archivo']:<45} sim={r['sim_ventral_translucido']:.3f}")
    print(f"\nDorsal/lateral (hábitat): {len(dorsal)}")

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nGuardado en {SALIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
