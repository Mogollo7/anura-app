"""Experimento A/B — mismo modelo (Fase 4, checkpoint vigente), mismas imágenes,
dos formas de presentarlas: completa (variante A) vs. recortada por el segmentador
binario CON el fix del bounding box (componente conexo más grande, no todos los
píxeles marcados — ver fase_4_transfer_learning.py::_recortar_por_mascara).

No es un reentrenamiento: es una prueba de inferencia pareada, para saber si el
recorte arreglado ayuda o perjudica al modelo YA entrenado en imagen completa,
antes de decidir si vale la pena reentrenar Fase 4 en variante C corregida.

Muestra: N imágenes aleatorias del split de TEST (nunca visto en entrenamiento),
cubriendo especies aleatorias — reproducible con semilla fija.

Uso:
    python bioclip/scripts/exp_ab_crop_vs_completa.py
"""

import json
import sys
from pathlib import Path

import numpy as np
import open_clip
import torch
from PIL import Image
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "training"))

from fase_4_transfer_learning import BioClipMultiHead  # noqa: E402
from taxonomia import vocabularios  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ_DATOS = Path(r"D:\Anura\data cleaned")
MASCARAS_DIR = Path(r"D:\Anura\segmentacion\mascaras_dataset")
MANIFIESTO = Path(r"D:\Anura\training\manifiesto.json")
CHECKPOINT = Path(r"D:\Anura\bioclip\checkpoints\bioclip_anura_mejor.pt")
MODELO_HF = "hf-hub:imageomics/bioclip"

SALIDA_JSON = Path(r"D:\Anura\bioclip\evaluation\exp_ab_crop_vs_completa.json")
SALIDA_MUESTRAS = Path(r"D:\Anura\bioclip\evaluation\muestras_recorte")
N_MUESTRA = 150
N_IMAGENES_EJEMPLO = 10
SEMILLA = 20260912


def recortar_con_fix(imagen: Image.Image, mascara: np.ndarray, enmascarar: bool = True) -> tuple[Image.Image, dict]:
    """Misma lógica ya aplicada en fase_4_transfer_learning.py: componente
    conexo más grande (no el bbox de todos los píxeles marcados) + fondo a
    negro pixel a pixel dentro del recorte (variante C real, no solo zoom).
    `enmascarar=False` reproduce la versión previa (solo zoom, sin pintar
    el fondo) para comparar ambas variantes del fix en el mismo experimento."""
    info = {"tenia_mascara": True, "n_componentes": 0, "fg_frac": 0.0, "bbox_frac": 0.0}
    if not mascara.any():
        info["tenia_mascara"] = False
        return imagen, info
    etiquetas, n_componentes = ndimage.label(mascara)
    info["n_componentes"] = int(n_componentes)
    m = mascara
    if n_componentes > 1:
        tamanos = ndimage.sum(mascara, etiquetas, range(1, n_componentes + 1))
        m = etiquetas == (np.argmax(tamanos) + 1)
    info["fg_frac"] = float(m.mean())

    if enmascarar:
        arr = np.array(imagen)
        arr[~m] = 0
        imagen = Image.fromarray(arr)

    filas = np.any(m, axis=1)
    cols = np.any(m, axis=0)
    y0, y1 = np.where(filas)[0][[0, -1]]
    x0, x1 = np.where(cols)[0][[0, -1]]
    info["bbox_frac"] = float(((y1 - y0 + 1) * (x1 - x0 + 1)) / m.size)
    return imagen.crop((int(x0), int(y0), int(x1) + 1, int(y1) + 1)), info


@torch.no_grad()
def predecir(modelo, tensor, dispositivo):
    x = tensor.unsqueeze(0).to(dispositivo)
    with torch.autocast(device_type="cuda" if "cuda" in dispositivo else "cpu"):
        _, (_, _, logits_esp) = modelo(x)
    probs = torch.softmax(logits_esp.float(), dim=-1)[0].cpu()
    return probs


def main():
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"{'='*88}\nEXPERIMENTO A/B — recorte (fix aplicado) vs. imagen completa\n"
          f"Mismo modelo (Fase 4), mismas imágenes, mismo checkpoint\n{'='*88}\n")

    familias, generos, especies = vocabularios()
    idx_de_especie = {e: i for i, e in enumerate(especies)}
    manifiesto = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    entradas_test = manifiesto["particiones"]["test"]

    rng = np.random.default_rng(SEMILLA)
    idx_muestra = rng.choice(len(entradas_test), size=min(N_MUESTRA, len(entradas_test)), replace=False)
    muestra = [entradas_test[i] for i in idx_muestra]
    especies_en_muestra = sorted(set(e["especie"] for e in muestra))
    print(f"Muestra: {len(muestra)} imágenes, {len(especies_en_muestra)} especies distintas (semilla {SEMILLA})")

    print("\nCargando modelo (checkpoint Fase 4 vigente)...")
    modelo_clip, _, preprocess = open_clip.create_model_and_transforms(MODELO_HF)
    ck = torch.load(CHECKPOINT, map_location="cpu", weights_only=False)
    modelo = BioClipMultiHead(modelo_clip.visual, len(familias), len(generos), len(especies))
    modelo.visual.load_state_dict(ck["visual_state_dict"])
    modelo.cabeza_familia.load_state_dict(ck["cabezas_state_dict"]["familia"])
    modelo.cabeza_genero.load_state_dict(ck["cabezas_state_dict"]["genero"])
    modelo.cabeza_especie.load_state_dict(ck["cabezas_state_dict"]["especie"])
    modelo = modelo.to(dispositivo).eval()

    resultados = []
    con_mascara_usable = 0
    print("\nProcesando pares (completa vs. recorte con fix)...")
    for i, entrada in enumerate(muestra):
        ruta_img = RAIZ_DATOS / entrada["ruta"]
        # mascaras_dataset se generó desde `data dirty` (estructura Especie/fotos/archivo),
        # mientras que el manifiesto usa rutas de `data cleaned` (Especie/archivo, sin "fotos").
        ruta_rel = Path(entrada["ruta"])
        ruta_mascara = MASCARAS_DIR / ruta_rel.parent / "fotos" / ruta_rel.with_suffix(".png").name
        y_real = idx_de_especie[entrada["especie"]]

        with Image.open(ruta_img).convert("RGB") as img_completa:
            probs_completa = predecir(modelo, preprocess(img_completa), dispositivo)

            info = {"tenia_mascara": False}
            if ruta_mascara.exists():
                mascara = np.array(Image.open(ruta_mascara).convert("L")) > 127
                img_zoom, info = recortar_con_fix(img_completa, mascara, enmascarar=False)
                img_mascara, _ = recortar_con_fix(img_completa, mascara, enmascarar=True)
            else:
                img_zoom = img_completa
                img_mascara = img_completa
            probs_zoom = predecir(modelo, preprocess(img_zoom), dispositivo)
            probs_mascara = predecir(modelo, preprocess(img_mascara), dispositivo)

        if info.get("tenia_mascara"):
            con_mascara_usable += 1

        resultados.append({
            "ruta": entrada["ruta"],
            "especie": entrada["especie"],
            "y_real": y_real,
            "top1_completa": int(probs_completa.argmax()),
            "top1_zoom": int(probs_zoom.argmax()),
            "top1_mascara": int(probs_mascara.argmax()),
            "prob_correcta_completa": float(probs_completa[y_real]),
            "prob_correcta_zoom": float(probs_zoom[y_real]),
            "prob_correcta_mascara": float(probs_mascara[y_real]),
            "top3_completa": probs_completa.topk(3).indices.tolist(),
            "top3_zoom": probs_zoom.topk(3).indices.tolist(),
            "top3_mascara": probs_mascara.topk(3).indices.tolist(),
            **info,
        })
        if (i + 1) % 30 == 0:
            print(f"  {i+1}/{len(muestra)}...")

    print(f"\nCon máscara usable: {con_mascara_usable}/{len(muestra)} "
          f"({con_mascara_usable/len(muestra):.1%})")

    # ── Métricas pareadas — 3 vías ──
    top1 = {k: np.mean([r[f"top1_{k}"] == r["y_real"] for r in resultados])
            for k in ("completa", "zoom", "mascara")}
    top3 = {k: np.mean([r["y_real"] in r[f"top3_{k}"] for r in resultados])
            for k in ("completa", "zoom", "mascara")}

    print(f"\n{'='*88}\nRESULTADOS (mismo modelo, mismas {len(muestra)} imágenes, 3 formas de presentar la foto)\n{'='*88}")
    print(f"{'':<28}{'TOP-1':>10}{'TOP-3':>10}")
    print(f"{'Imagen completa':<28}{top1['completa']:>9.1%}{top3['completa']:>10.1%}")
    print(f"{'Recorte zoom (sin máscara)':<28}{top1['zoom']:>9.1%}{top3['zoom']:>10.1%}")
    print(f"{'Recorte + fondo a negro (C real)':<28}{top1['mascara']:>9.1%}{top3['mascara']:>10.1%}")

    for nombre, clave in (("zoom", "zoom"), ("máscara (C real)", "mascara")):
        mejoro = sum(1 for r in resultados
                     if r[f"top1_{clave}"] == r["y_real"] and r["top1_completa"] != r["y_real"])
        empeoro = sum(1 for r in resultados
                      if r["top1_completa"] == r["y_real"] and r[f"top1_{clave}"] != r["y_real"])
        print(f"\nCambio pareado — {nombre} vs. completa (Top-1):")
        print(f"  Corrigió lo que completa fallaba : {mejoro}")
        print(f"  Dañó lo que completa acertaba    : {empeoro}")
        print(f"  Sin cambio                        : {len(resultados) - mejoro - empeoro}")

    # ── 10 imágenes de ejemplo: completa | zoom | fondo a negro (3 paneles) ──
    print(f"\nGuardando {N_IMAGENES_EJEMPLO} imágenes de ejemplo (completa | zoom | máscara real)...")
    SALIDA_MUESTRAS.mkdir(parents=True, exist_ok=True)
    candidatas = [r for r in resultados if r.get("tenia_mascara")]
    rng.shuffle(candidatas)
    for j, r in enumerate(candidatas[:N_IMAGENES_EJEMPLO]):
        ruta_img = RAIZ_DATOS / r["ruta"]
        ruta_rel = Path(r["ruta"])
        ruta_mascara = MASCARAS_DIR / ruta_rel.parent / "fotos" / ruta_rel.with_suffix(".png").name
        with Image.open(ruta_img).convert("RGB") as img:
            mascara = np.array(Image.open(ruta_mascara).convert("L")) > 127
            zoom, _ = recortar_con_fix(img, mascara, enmascarar=False)
            con_mascara, _ = recortar_con_fix(img, mascara, enmascarar=True)
            especie_corta = r["especie"]
            h = img.height
            def ajustar(im):
                return im.resize((int(im.width * h / im.height), h)) if im.height > 0 else im
            zoom_r, mascara_r = ajustar(zoom), ajustar(con_mascara)
            ancho_total = img.width + zoom_r.width + mascara_r.width + 40
            lienzo = Image.new("RGB", (ancho_total, h + 40), "white")
            x = 0
            for panel in (img, zoom_r, mascara_r):
                lienzo.paste(panel, (x, 30))
                x += panel.width + 20
            nombre = f"{j:02d}_{especie_corta}_fg{r['fg_frac']:.0%}_bbox{r['bbox_frac']:.0%}.jpg"
            lienzo.save(SALIDA_MUESTRAS / nombre, quality=90)
    print(f"  Guardadas en {SALIDA_MUESTRAS} (orden: completa | zoom sin máscara | zoom con fondo a negro)")

    SALIDA_JSON.parent.mkdir(parents=True, exist_ok=True)
    SALIDA_JSON.write_text(json.dumps({
        "n_muestra": len(muestra),
        "semilla": SEMILLA,
        "n_especies": len(especies_en_muestra),
        "con_mascara_usable": con_mascara_usable,
        "top1_completa": top1["completa"],
        "top1_zoom": top1["zoom"],
        "top1_mascara": top1["mascara"],
        "top3_completa": top3["completa"],
        "top3_zoom": top3["zoom"],
        "top3_mascara": top3["mascara"],
        "detalle": resultados,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nGuardado en {SALIDA_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
