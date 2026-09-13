"""Fase 6c — ¿Cuánto mejora el reconocimiento si se usa la ubicación?

Mide el efecto de combinar la predicción visual con un prior geográfico:

    P(especie | foto, lugar)  ∝  P(especie | foto) · P(especie | lugar)^w

El prior P(especie | lugar) se estima SOLO con las observaciones de train
(conteo de vecinos dentro de un radio, con suavizado add-alpha). Usar las
coordenadas de test para calibrarlo sería fuga de datos y la mejora reportada
sería ficticia.

Advertencia que el script mide explícitamente: el split es por observación,
así que una foto de test nunca está en train — pero puede estar a 100 m de una
de train (mismo usuario, misma salida de campo). Eso infla el beneficio
aparente del prior. Por eso se reporta la mejora también sobre el subconjunto
de test *geográficamente aislado*, que es la estimación honesta de lo que
pasaría con un usuario en un sitio nuevo.

Uso:
    python bioclip/scripts/fase_6c_prior_geografico.py
"""

import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
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
RAIZ_COORDS = Path(r"D:\Anura\data dirty")
MANIFIESTO = Path(r"D:\Anura\training\manifiesto.json")
CHECKPOINT = Path(r"D:\Anura\bioclip\checkpoints\bioclip_anura_mejor.pt")
SALIDA = Path(r"D:\Anura\bioclip\evaluation\prior_geografico.json")
MODELO_HF = "hf-hub:imageomics/bioclip"

RADIO_KM = 50.0     # vecindario para estimar el prior
ALPHA = 0.5         # suavizado: ninguna especie recibe probabilidad cero
AISLADO_KM = 25.0   # umbral para considerar una obs de test "geográficamente nueva"
PESOS = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]
UMBRAL_ACCURACY_M = 10_000  # descarta coordenadas con imprecisión mayor al radio del prior


def cargar_coordenadas():
    """obs_id -> (lat, lon), leído de los volcados del scraper.

    Descarta observaciones con positional_accuracy > UMBRAL_ACCURACY_M: si el
    propio iNaturalist reporta que el punto puede estar a más de 10 km de
    donde dice, meterlo en un prior de radio 50 km es ruido, no señal.
    """
    coords = {}
    descartadas_por_accuracy = 0
    for archivo in RAIZ_COORDS.glob("*/coordenadas_distribucion.json"):
        try:
            registros = json.loads(archivo.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for r in registros:
            lat, lon = r.get("latitude"), r.get("longitude")
            acc = r.get("positional_accuracy")
            if lat is None or lon is None:
                continue
            if acc is not None and acc > UMBRAL_ACCURACY_M:
                descartadas_por_accuracy += 1
                continue
            coords[str(r["observation_id"])] = (float(lat), float(lon))
    print(f"Descartadas por positional_accuracy > {UMBRAL_ACCURACY_M/1000:.0f} km: "
          f"{descartadas_por_accuracy}")
    return coords


def obs_id_de(ruta: str) -> str | None:
    m = re.search(r"obs_(\d+)_photo", ruta)
    return m.group(1) if m else None


def haversine(lat1, lon1, lat2, lon2):
    """Distancia en km entre un punto y arrays de puntos."""
    r = 6371.0
    p1, p2 = math.radians(lat1), np.radians(lat2)
    dp = np.radians(lat2 - lat1)
    dl = np.radians(lon2 - lon1)
    a = np.sin(dp / 2) ** 2 + math.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


class DatasetTest(Dataset):
    def __init__(self, entradas, preprocess):
        self.entradas = entradas
        self.preprocess = preprocess

    def __len__(self):
        return len(self.entradas)

    def __getitem__(self, idx):
        e = self.entradas[idx]
        with Image.open(RAIZ_DATOS / e["ruta"]).convert("RGB") as img:
            return self.preprocess(img), e["idx_especie"], idx


def main():
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    familias, generos, especies = vocabularios()
    idx_de_especie = {e: i for i, e in enumerate(especies)}
    manifiesto = json.loads(MANIFIESTO.read_text(encoding="utf-8"))

    print(f"{'='*78}\nFASE 6c: ¿Cuánto aporta la ubicación?\n{'='*78}")

    coords = cargar_coordenadas()
    print(f"Observaciones con coordenadas: {len(coords):,}")

    # ── Prior: SOLO observaciones reales de train ──
    puntos_train = defaultdict(list)  # idx_especie -> [(lat, lon)]
    obs_train_vistas = set()
    for e in manifiesto["particiones"]["train"]:
        if e.get("aumentada"):
            continue
        oid = obs_id_de(e["ruta"])
        if oid is None or oid in obs_train_vistas or oid not in coords:
            continue
        obs_train_vistas.add(oid)
        puntos_train[idx_de_especie[e["especie"]]].append(coords[oid])

    n_train_geo = sum(len(v) for v in puntos_train.values())
    print(f"Observaciones de train con coordenadas (base del prior): {n_train_geo:,}")
    print(f"Especies con soporte geográfico: {len(puntos_train)}/{len(especies)}")

    lat_train = {k: np.array([p[0] for p in v]) for k, v in puntos_train.items()}
    lon_train = {k: np.array([p[1] for p in v]) for k, v in puntos_train.items()}

    # ── Test: solo las que tienen coordenadas ──
    entradas_test = manifiesto["particiones"]["test"]
    con_geo = [(i, coords[obs_id_de(e["ruta"])]) for i, e in enumerate(entradas_test)
               if obs_id_de(e["ruta"]) in coords]
    print(f"Imágenes de test con coordenadas: {len(con_geo)}/{len(entradas_test)}"
          f"  ({len(con_geo)/len(entradas_test):.0%})\n")
    if not con_geo:
        print("Sin solape de coordenadas: no se puede evaluar el prior.")
        return 1

    # ── Predicciones visuales ──
    print("Ejecutando el modelo sobre test...")
    modelo_clip, _, preprocess = open_clip.create_model_and_transforms(MODELO_HF)
    ck = torch.load(CHECKPOINT, map_location="cpu", weights_only=False)
    modelo = BioClipMultiHead(modelo_clip.visual, len(familias), len(generos), len(especies))
    modelo.visual.load_state_dict(ck["visual_state_dict"])
    modelo.cabeza_familia.load_state_dict(ck["cabezas_state_dict"]["familia"])
    modelo.cabeza_genero.load_state_dict(ck["cabezas_state_dict"]["genero"])
    modelo.cabeza_especie.load_state_dict(ck["cabezas_state_dict"]["especie"])
    modelo = modelo.to(dispositivo).eval()

    dl = DataLoader(DatasetTest(entradas_test, preprocess), batch_size=32, num_workers=2)
    logits_todos = torch.zeros(len(entradas_test), len(especies))
    etiquetas = torch.zeros(len(entradas_test), dtype=torch.long)
    with torch.no_grad():
        for x, y, idxs in dl:
            x = x.to(dispositivo)
            with torch.autocast(device_type="cuda" if "cuda" in dispositivo else "cpu"):
                _, (_, _, lg) = modelo(x)
            logits_todos[idxs] = lg.float().cpu()
            etiquetas[idxs] = y

    # ── Prior geográfico + distancia al train más cercano (para el corte honesto) ──
    print(f"Estimando prior en radio de {RADIO_KM:.0f} km...\n")
    filas, log_prior, dist_min = [], [], []
    for i, (lat, lon) in con_geo:
        conteos = np.full(len(especies), ALPHA)
        d_min = float("inf")
        for k in puntos_train:
            d = haversine(lat, lon, lat_train[k], lon_train[k])
            conteos[k] += float((d <= RADIO_KM).sum())
            d_min = min(d_min, float(d.min()))
        filas.append(i)
        log_prior.append(np.log(conteos / conteos.sum()))
        dist_min.append(d_min)

    filas = np.array(filas)
    log_prior = torch.tensor(np.array(log_prior), dtype=torch.float32)
    dist_min = np.array(dist_min)
    log_post_visual = torch.log_softmax(logits_todos[filas], dim=-1)
    y = etiquetas[filas]

    aislados = dist_min > AISLADO_KM
    print(f"Test con coords: {len(filas)}  |  geográficamente aislados (>{AISLADO_KM:.0f} km "
          f"de cualquier obs de train de su especie): {int(aislados.sum())}")

    print(f"\nDistribución de distancia al train más cercano de la misma especie:")
    for umbral in (0.5, 1, 2, 5, 10, 25, 50):
        n = int((dist_min > umbral).sum())
        print(f"  > {umbral:>5.1f} km : {n:>4} obs ({n/len(dist_min):>5.1%})")

    # ── Barrido del peso ──
    print(f"\n{'='*78}")
    print(f"{'PESO w':<10}{'TOP-1':>10}{'Δ':>9}{'TOP-3':>10}{'TOP-1 aislados':>17}{'Δ aisl.':>10}")
    print(f"{'='*78}")

    resultados = []
    base_top1 = base_ais = None
    for w in PESOS:
        comb = log_post_visual + w * log_prior
        pred = comb.argmax(-1)
        top1 = (pred == y).float().mean().item()
        top3 = (comb.topk(3, -1).indices == y.unsqueeze(-1)).any(-1).float().mean().item()
        if aislados.sum():
            t1a = (pred[aislados] == y[aislados]).float().mean().item()
        else:
            t1a = float("nan")
        if w == 0.0:
            base_top1, base_ais = top1, t1a
        d = (top1 - base_top1) * 100
        da = (t1a - base_ais) * 100
        marca = "  <- solo imagen" if w == 0.0 else ""
        print(f"{w:<10.2f}{top1:>9.1%}{d:>+8.1f}pp{top3:>9.1%}{t1a:>16.1%}{da:>+9.1f}pp{marca}")
        resultados.append({"peso": w, "top1": top1, "top3": top3, "top1_aislados": t1a})

    mejor = max(resultados, key=lambda r: r["top1"])
    print(f"{'='*78}")
    print(f"\nMejor peso: w={mejor['peso']:.2f}  ->  Top-1 {base_top1:.1%} -> {mejor['top1']:.1%} "
          f"({(mejor['top1']-base_top1)*100:+.1f} pp)")

    # ── ¿Cuánto del beneficio es biogeografía y cuánto es memorizar el punto? ──
    # Si la ganancia viniera de entender dónde vive cada especie, debería
    # sostenerse al alejarse de los puntos ya vistos en train. Si viene de
    # memorizar localidades, se desploma con la distancia.
    print(f"\n{'='*78}\n¿LA GANANCIA SOBREVIVE AL ALEJARSE DE LOS PUNTOS DE TRAIN?\n{'='*78}")
    print(f"{'CORTE':<14}{'N':>6}{'SOLO IMAGEN':>14}{'CON UBICACIÓN':>16}{'Δ':>10}")
    print("-" * 78)
    w_mejor = mejor["peso"]
    comb_mejor = log_post_visual + w_mejor * log_prior
    pred_mejor = comb_mejor.argmax(-1)
    pred_base = log_post_visual.argmax(-1)
    curva = []
    for umbral in (0.0, 0.5, 1, 2, 5, 10, 25):
        m = torch.tensor(dist_min > umbral)
        n = int(m.sum())
        if n < 5:
            continue
        b = (pred_base[m] == y[m]).float().mean().item()
        g = (pred_mejor[m] == y[m]).float().mean().item()
        etiqueta = "todas" if umbral == 0 else f"> {umbral:g} km"
        print(f"{etiqueta:<14}{n:>6}{b:>13.1%}{g:>15.1%}{(g-b)*100:>+9.1f}pp")
        curva.append({"umbral_km": umbral, "n": n, "top1_solo_imagen": b, "top1_con_ubicacion": g})

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps({
        "config": {"radio_km": RADIO_KM, "alpha": ALPHA, "aislado_km": AISLADO_KM},
        "cobertura": {
            "test_total": len(entradas_test),
            "test_con_coords": len(filas),
            "test_aislados": int(aislados.sum()),
            "train_obs_con_coords": n_train_geo,
        },
        "barrido": resultados,
        "mejor": mejor,
        "curva_por_distancia": curva,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Guardado en {SALIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
