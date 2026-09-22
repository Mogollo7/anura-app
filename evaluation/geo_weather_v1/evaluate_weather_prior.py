"""Paso 2: evalua si un prior de temperatura/humedad por especie mejora el ranking visual,
con el MISMO protocolo de control de fuga que pipeline_dataset/paquetes_zonales.py (train/test
congelados en training/manifiesto.json, prior calculado SOLO con train).

Combinacion: score(s) = voto_knn(s) * likelihood_clima(s)^w
  likelihood_clima(s) = exp(-0.5*z_temp^2) * exp(-0.5*z_hum^2)   (z-score contra media/std de la
  especie en train). Especies sin >=MIN_N observaciones de clima en train, o imagenes de prueba
  sin clima resuelto, quedan neutras (likelihood=1): nunca se penaliza por falta de dato.

Uso: python evaluation/geo_weather_v1/evaluate_weather_prior.py
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(r"D:/Anura/pipeline_dataset")))
import paquetes_zonales as pz  # noqa: E402
from fetch_weather import cargar_seleccion  # noqa: E402

OUT = Path(__file__).parent
MIN_N = 3


def gauss_z(x, mean, std):
    std = max(std, 1e-6)
    return math.exp(-0.5 * ((x - mean) / std) ** 2)


def main():
    referencias, prueba, _dir_d = cargar_seleccion()
    obs_clima = json.loads((OUT / "obs_clima.json").read_text(encoding="utf-8"))
    print(f"referencias={len(referencias)} prueba={len(prueba)} obs_con_clima={len(obs_clima)}")

    sha_ck = pz.sha256_archivo(pz.CHECKPOINT)
    emb_ref = pz.embeddings([r[0] for r in referencias], sha_ck)
    emb_test = pz.embeddings([p[0] for p in prueba], sha_ck)
    taxon_ref = [r[1] for r in referencias]

    # ── Prior de clima: SOLO con referencias (train), por especie, dedupe por obs ──
    por_especie = {}
    for rel, tid, obs in referencias:
        c = obs_clima.get(obs)
        if c is None:
            continue
        por_especie.setdefault(tid, {}).setdefault(obs, c)  # dedupe: 1 valor por individuo
    stats = {}
    for tid, por_obs in por_especie.items():
        temps = [c["temp_c"] for c in por_obs.values()]
        hums = [c["humidity_pct"] for c in por_obs.values()]
        if len(temps) >= MIN_N:
            stats[tid] = {
                "n": len(temps),
                "temp_mean": float(np.mean(temps)), "temp_std": float(np.std(temps)),
                "hum_mean": float(np.mean(hums)), "hum_std": float(np.std(hums)),
            }
    print(f"especies con prior de clima (n>={MIN_N}): {len(stats)} / {len(por_especie)} con algun dato")

    # ── Evaluacion ──
    votos = pz.votos_knn(emb_test, emb_ref, taxon_ref)
    con_clima_test = [i for i, (_, _, obs) in enumerate(prueba) if obs in obs_clima]
    print(f"imagenes de prueba con clima resuelto: {len(con_clima_test)} / {len(prueba)}")

    def evaluar(pesos_w):
        resultados = {w: {"top1": 0, "top3": 0} for w in pesos_w}
        top1_v = top3_v = 0
        n = len(con_clima_test)
        for i in con_clima_test:
            rel, tid_real, obs = prueba[i]
            v = votos[i]
            clima_obs = obs_clima[obs]
            orden_v = [s for s, _ in v.most_common()]
            top1_v += orden_v[0] == tid_real
            top3_v += tid_real in orden_v[:3]
            for w in pesos_w:
                combinado = {}
                for s, voto in v.items():
                    st = stats.get(s)
                    if st is None:
                        combinado[s] = voto  # neutro: sin prior para esta especie
                        continue
                    like = gauss_z(clima_obs["temp_c"], st["temp_mean"], st["temp_std"]) * \
                        gauss_z(clima_obs["humidity_pct"], st["hum_mean"], st["hum_std"])
                    combinado[s] = voto * (like ** w)
                orden_c = sorted(combinado, key=lambda s: -combinado[s])
                resultados[w]["top1"] += orden_c[0] == tid_real
                resultados[w]["top3"] += tid_real in orden_c[:3]
        print(f"\nEvaluacion sobre {n} imagenes de prueba CON clima resuelto:")
        print(f"  visual solo       Top-1 {top1_v / n:.1%}  Top-3 {top3_v / n:.1%}")
        for w in pesos_w:
            r = resultados[w]
            print(f"  visual x clima w={w:<4} Top-1 {r['top1'] / n:.1%}  Top-3 {r['top3'] / n:.1%}")
        return {"n": n, "visual_only": {"top1": top1_v / n, "top3": top3_v / n},
                "visual_x_clima": {str(w): {"top1": resultados[w]["top1"] / n, "top3": resultados[w]["top3"] / n}
                                    for w in pesos_w}}

    resultado = evaluar([0.2, 0.5, 0.75, 1.0])
    resultado["especies_con_prior"] = len(stats)
    resultado["stats_por_especie"] = stats
    (OUT / "resultado_evaluacion_clima.json").write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8",
    )
    print(f"\nGuardado: {OUT / 'resultado_evaluacion_clima.json'}")


if __name__ == "__main__":
    main()
