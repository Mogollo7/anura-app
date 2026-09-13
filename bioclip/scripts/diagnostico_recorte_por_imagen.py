"""Diagnóstico: ¿el daño del recorte se concentra en fotos borrosas / bbox pequeño?

Extiende experimento_recorte_vs_completa.py (mismo dataset, mismo encoder
zero-shot) pero guarda el acierto/fallo POR IMAGEN de test en ambos modos, y lo
cruza con dos métricas explicativas:

  - nitidez: varianza del Laplaciano de la imagen COMPLETA (mayor = más nítida)
  - area_mascara: fracción del área total que ocupa el bounding box de la
    máscara (menor = la rana ocupaba poco del encuadre, más ampliación al
    recortar y reescalar a 224x224)

Hipótesis a probar: las imágenes que acertaban en modo completo y fallan en
modo recortado ("dañadas por el recorte") tienen nitidez menor y/o
area_mascara menor que las que no se dañan. Si es así, la causa dominante es
la dificultad de la foto (borrosa/lejana), no el recorte en sí sobre fotos
buenas.

Uso:
    python bioclip/scripts/diagnostico_recorte_por_imagen.py
"""

import io
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import open_clip
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)

RAIZ_DATOS = Path(r"D:\Anura\data dirty")
MANIFIESTO = Path(r"D:\Anura\training\manifiesto.json")
MASCARAS = Path(r"D:\Anura\segmentacion\mascaras_dataset")
SALIDA = Path(r"D:\Anura\bioclip\evaluation\diagnostico_recorte_por_imagen.json")
MODELO_HF = "hf-hub:imageomics/bioclip"


def bbox_mascara(ruta_relativa: str):
    ruta_mascara = MASCARAS / Path(ruta_relativa).with_suffix(".png")
    if not ruta_mascara.exists():
        return None
    with Image.open(ruta_mascara).convert("L") as m:
        mascara = np.array(m)
    filas = np.any(mascara > 127, axis=1)
    cols = np.any(mascara > 127, axis=0)
    if not filas.any() or not cols.any():
        return None
    y0, y1 = np.where(filas)[0][[0, -1]]
    x0, x1 = np.where(cols)[0][[0, -1]]
    return int(x0), int(y0), int(x1) + 1, int(y1) + 1, mascara.shape[1], mascara.shape[0]


def nitidez_laplaciano(ruta_absoluta: Path) -> float:
    img = cv2.imread(str(ruta_absoluta), cv2.IMREAD_GRAYSCALE)
    if img is None:
        return float("nan")
    return float(cv2.Laplacian(img, cv2.CV_64F).var())


class DatasetComparacion(Dataset):
    def __init__(self, entradas, preprocess, recortar: bool):
        self.entradas = entradas
        self.preprocess = preprocess
        self.recortar = recortar

    def __len__(self):
        return len(self.entradas)

    def __getitem__(self, idx):
        entrada = self.entradas[idx]
        with Image.open(RAIZ_DATOS / entrada["ruta"]).convert("RGB") as img:
            if self.recortar:
                caja = bbox_mascara(entrada["ruta"])
                if caja is not None:
                    x0, y0, x1, y1, _, _ = caja
                    img = img.crop((x0, y0, x1, y1))
            tensor = self.preprocess(img)
        return tensor, entrada["idx_especie"]


@torch.no_grad()
def extraer(visual, dl, dispositivo):
    embs, etiquetas = [], []
    for x, y in dl:
        x = x.to(dispositivo)
        with torch.autocast(device_type="cuda" if "cuda" in dispositivo else "cpu"):
            e = visual(x)
        e = e.float()
        e = e / e.norm(dim=-1, keepdim=True)
        embs.append(e.cpu().numpy())
        etiquetas.append(y.numpy())
    return np.concatenate(embs), np.concatenate(etiquetas)


def knn_predecir(emb_train, y_train, emb_test, k=5):
    similitudes = emb_test @ emb_train.T
    vecinos = np.argsort(-similitudes, axis=1)[:, :k]
    n_clases = int(y_train.max()) + 1
    predicciones = np.empty(len(emb_test), dtype=int)
    for i in range(len(emb_test)):
        votos = np.zeros(n_clases)
        for j in vecinos[i]:
            votos[y_train[j]] += similitudes[i, j]
        predicciones[i] = np.argmax(votos)
    return predicciones


def main():
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Dispositivo: {dispositivo}")

    manifiesto = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    entradas_train = manifiesto["particiones"]["train"]
    entradas_test = manifiesto["particiones"]["test"]
    print(f"train={len(entradas_train)} test={len(entradas_test)}")

    modelo_clip, _, preprocess = open_clip.create_model_and_transforms(MODELO_HF)
    visual = modelo_clip.visual.to(dispositivo).eval()

    predicciones = {}
    for modo, recortar in (("completa", False), ("recortada", True)):
        t0 = time.time()
        dl_train = DataLoader(DatasetComparacion(entradas_train, preprocess, recortar), batch_size=32, num_workers=0)
        dl_test = DataLoader(DatasetComparacion(entradas_test, preprocess, recortar), batch_size=32, num_workers=0)
        emb_train, y_train = extraer(visual, dl_train, dispositivo)
        emb_test, y_test = extraer(visual, dl_test, dispositivo)
        pred = knn_predecir(emb_train, y_train, emb_test)
        predicciones[modo] = pred
        print(f"  [{modo}] listo en {time.time()-t0:.0f}s, top1={np.mean(pred == y_test):.1%}")

    print("Calculando nitidez y area_mascara por imagen de test...")
    registros = []
    for i, entrada in enumerate(entradas_test):
        ruta = entrada["ruta"]
        nit = nitidez_laplaciano(RAIZ_DATOS / ruta)
        caja = bbox_mascara(ruta)
        area_frac = None
        if caja is not None:
            x0, y0, x1, y1, w, h = caja
            area_frac = ((x1 - x0) * (y1 - y0)) / (w * h)
        acierto_completa = bool(predicciones["completa"][i] == y_test[i])
        acierto_recortada = bool(predicciones["recortada"][i] == y_test[i])
        if acierto_completa and not acierto_recortada:
            categoria = "danada_por_recorte"
        elif not acierto_completa and acierto_recortada:
            categoria = "mejorada_por_recorte"
        elif acierto_completa and acierto_recortada:
            categoria = "acierta_ambos"
        else:
            categoria = "falla_ambos"
        registros.append({
            "ruta": ruta,
            "especie": entrada["especie"],
            "nitidez": nit,
            "area_mascara": area_frac,
            "acierto_completa": acierto_completa,
            "acierto_recortada": acierto_recortada,
            "categoria": categoria,
        })

    import statistics as st
    grupos = {}
    for cat in ("danada_por_recorte", "mejorada_por_recorte", "acierta_ambos", "falla_ambos"):
        subset = [r for r in registros if r["categoria"] == cat]
        nitideces = [r["nitidez"] for r in subset if r["nitidez"] == r["nitidez"]]
        areas = [r["area_mascara"] for r in subset if r["area_mascara"] is not None]
        grupos[cat] = {
            "n": len(subset),
            "nitidez_media": st.mean(nitideces) if nitideces else None,
            "nitidez_mediana": st.median(nitideces) if nitideces else None,
            "area_mascara_media": st.mean(areas) if areas else None,
            "area_mascara_mediana": st.median(areas) if areas else None,
        }

    print(f"\n{'='*78}\nRESUMEN POR CATEGORÍA\n{'='*78}")
    print(f"{'categoria':<22}{'n':>5}{'nitidez_med':>14}{'area_mask_med':>16}")
    for cat, g in grupos.items():
        nm = f"{g['nitidez_mediana']:.1f}" if g["nitidez_mediana"] is not None else "n/a"
        am = f"{g['area_mascara_mediana']:.1%}" if g["area_mascara_mediana"] is not None else "n/a"
        print(f"{cat:<22}{g['n']:>5}{nm:>14}{am:>16}")

    dañadas = grupos["danada_por_recorte"]
    resto = [r for r in registros if r["categoria"] != "danada_por_recorte"]
    nit_resto = [r["nitidez"] for r in resto if r["nitidez"] == r["nitidez"]]
    area_resto = [r["area_mascara"] for r in resto if r["area_mascara"] is not None]

    print(f"\n{'='*78}\nVEREDICTO\n{'='*78}")
    if dañadas["nitidez_mediana"] is not None and nit_resto:
        rel_nit = dañadas["nitidez_mediana"] / st.median(nit_resto)
        print(f"Nitidez mediana [dañadas por recorte] vs [resto]: {dañadas['nitidez_mediana']:.1f} vs {st.median(nit_resto):.1f}  (razón {rel_nit:.2f}x)")
    if dañadas["area_mascara_mediana"] is not None and area_resto:
        rel_area = dañadas["area_mascara_mediana"] / st.median(area_resto)
        print(f"Área máscara mediana [dañadas por recorte] vs [resto]: {dañadas['area_mascara_mediana']:.1%} vs {st.median(area_resto):.1%}  (razón {rel_area:.2f}x)")
    print("\nSi ambas razones son claramente < 1 (p.ej. <0.8), la teoría del usuario")
    print("(fotos difíciles/con rana pequeña son las que se dañan) queda soportada.")
    print("Si las razones rondan ~1.0, el daño está distribuido parejo y la causa")
    print("es otra (p.ej. distribución de composición, no dificultad de la foto).")

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps({
        "grupos": grupos,
        "registros": registros,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nGuardado en {SALIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
