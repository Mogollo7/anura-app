"""Paquete de Antioquia: el del teléfono (v1.0.0) contra el que arma el creador del Admin.

Mismos datos para los dos, método distinto:

  VIEJO  (lo que corre hoy en anura-android)
    - 4.034 vectores de referencia (≤300 por especie, 30 especies visuales), k-NN k=5 coseno.
    - La especie sale SOLO del voto visual (AnuraIdentifier.kt: el prior de zona no decide).
    - Rechazo: Mahalanobis Ledoit-Wolf compartida (openset_v1.1.0_clean.bin), τ 39,35,
      restringida a las 30 especies de ANTIOQUIA (allowed_by_package.json).

  NUEVO  (19_ADMIN: Curación → Centroides → Clústeres → OSR → Validación → Compilador)
    - Centroide L2 por especie con las MISMAS fotos de referencia (sin morfos: los datos
      reales no traen etiqueta de morfo, así que no se inventa ninguno).
    - Supercentroides de género y familia (suma L2, un voto por género).
    - Capa 1: radio por especie = cuantil Weibull de sus distancias de entrenamiento
      (cobertura 0,95, α 1). Igual que lib/osr/osr.ts del Admin.
    - Cascada: especie → género → familia → OSR_GLOBAL, con τ de nodo por Weibull.
    - Capa 2: clústeres crípticos SUGERIDOS por la confusión en la partición val
      (el herpetólogo tiene que confirmarlos); W = subespacio del clúster (≤64 columnas),
      ε = p95 del error de reconstrucción de sus miembros.
    - Capa 3: gaussiana de altitud por especie con los registros del departamento
      (sin las observaciones de prueba); P(altitud) < 0,05 → OSR_GEO.

  Calibración: partición train (referencias) y val. Medición: partición test (conocidas)
  y unknown_open_set_v2 (especies que el paquete no trae). Nada de val ni de test entra
  a los centroides.

Uso:  python evaluation/admin_v2_comparison/compare_packages.py
Salida: evaluation/admin_v2_comparison/{results.json, package_admin_antioquia_v2.json, REPORT.md}
"""

import csv
import json
import math
import re
import struct
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(r"D:\Anura")
HERE = ROOT / "evaluation" / "admin_v2_comparison"
DEPTO = ROOT / "COLOMBIA_ANURA" / "ANTIOQUIA"
CACHE = ROOT / "COLOMBIA_ANURA" / "cache" / "embeddings" / "98a6c54d6edb27e2.npz"
DEM_CACHE = ROOT / "COLOMBIA_ANURA" / "cache" / "opentopodata_srtm90m.json"
OPENSET_BIN = ROOT / "anura-android" / "app" / "src" / "main" / "assets" / "openset" / "openset_v1.1.0_clean.bin"
ALLOWED = ROOT / "anura-android" / "app" / "src" / "main" / "assets" / "openset" / "allowed_by_package.json"
INAT_CACHE = ROOT / "data" / "unknown_open_set_v2" / "manifests" / "_inat_cache"

sys.path.insert(0, str(ROOT / "pipeline_dataset"))
# El script del paquete importa sqlite_vec para escribir la base; aquí solo se reutiliza su muestreo.
import types  # noqa: E402
sys.modules.setdefault("sqlite_vec", types.ModuleType("sqlite_vec"))
import paquetes_zonales as pz  # noqa: E402  (mismo muestreo de referencias que el paquete del teléfono)

COBERTURA = 0.95
ALPHA = 1.0
UMBRAL_GEO = 0.05
CONFUSION_CLUSTER = 0.10  # fracción de val de A que cae en B (o al revés) para sugerir el par
COLUMNAS_W = 64
K_OLD = 5
# "fine_tuning": encoder_anura (el del teléfono). "puro": BioCLIP 1 sin fine-tuning (embed_pure.py).
ENCODER_KIND = sys.argv[1] if len(sys.argv) > 1 else "fine_tuning"


# ── utilidades ────────────────────────────────────────────────────────────
def l2(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def fit_weibull(xs):
    """Máxima verosimilitud (β por bisección, η cerrado). Idéntica a fitWeibull de osr.ts."""
    x = np.asarray([v for v in xs if v > 1e-9], dtype=np.float64)
    if len(x) < 2:
        return 1.0, float(x[0]) if len(x) else 1e-3
    mx = x.max()
    u = x / mx
    lnu = np.log(u)
    mean_ln = lnu.mean()

    def g(b):
        p = u ** b
        return (p * lnu).sum() / p.sum() - 1 / b - mean_ln

    lo, hi = 0.05, 200.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if g(mid) > 0:
            hi = mid
        else:
            lo = mid
    beta = (lo + hi) / 2
    eta = mx * ((u ** beta).mean()) ** (1 / beta)
    return float(beta), float(eta)


def weibull_q(beta, eta, p):
    return eta * (-math.log(1 - p)) ** (1 / beta)


def auroc(known, unknown):
    """P(puntaje de rechazo de una conocida < el de una desconocida). Mann-Whitney con empates."""
    k = np.asarray(known, dtype=np.float64)
    u = np.asarray(unknown, dtype=np.float64)
    allv = np.concatenate([k, u])
    order = allv.argsort(kind="mergesort")
    ranks = np.empty(len(allv))
    ranks[order] = np.arange(1, len(allv) + 1)
    for v in np.unique(allv):
        m = allv == v
        if m.sum() > 1:
            ranks[m] = ranks[m].mean()
    r_u = ranks[len(k):].sum()
    return float((r_u - len(u) * (len(u) + 1) / 2) / (len(k) * len(u)))


def p_altitud(h, mu, sigma):
    z = abs(h - mu) / max(sigma, 1.0)
    return math.erfc(z / math.sqrt(2))


def read_openset(path):
    b = path.read_bytes()
    assert b[:4] == b"ANOS"
    _, dim, k, tau = struct.unpack_from("<iiid", b, 4)
    off = 24
    prec = np.frombuffer(b, dtype="<f8", count=dim * dim, offset=off).reshape(dim, dim)
    off += dim * dim * 8
    cents = np.frombuffer(b, dtype="<f8", count=k * dim, offset=off).reshape(k, dim)
    off += k * dim * 8
    ids = []
    for _ in range(k):
        n = struct.unpack_from("<i", b, off)[0]
        off += 4
        ids.append(b[off:off + n].decode())
        off += n
    return prec, cents, ids, tau


# ── datos ─────────────────────────────────────────────────────────────────
def load():
    guia = json.loads((ROOT / "COLOMBIA_ANURA" / "taxonomy" / "taxonomy_guide.json").read_text(encoding="utf-8"))
    catalogo = json.loads((DEPTO / "catalog" / "catalog_v1.json").read_text(encoding="utf-8"))
    taxa = {t["taxon_id"]: t for t in catalogo["taxa"]}
    visuales = sorted(t for t, v in taxa.items() if v["visual_status"] == "VISUAL_ENABLED")
    legado = {tid: guia[tid]["directory_legacy"] for tid in visuales}
    split = {}
    for part in ("train", "val", "test"):
        for e in json.loads(pz.MANIFIESTO.read_text(encoding="utf-8"))["particiones"][part]:
            if not e.get("aumentada"):
                split[e["ruta"].replace("\\", "/")] = part
    refs, prueba = pz.seleccionar_referencias(set(visuales), legado, split)
    cache = np.load(CACHE)
    cm = dict(zip(cache["paths"].tolist(), cache["vectors"]))
    emb_ref = l2(np.stack([cm[r[0]] for r in refs]).astype(np.float64))
    emb_test = l2(np.stack([cm[p[0]] for p in prueba]).astype(np.float64))
    val = np.load(HERE / "embeddings" / "val.npz")
    unk = np.load(HERE / "embeddings" / "unknown.npz")
    emb_val = l2(val["vectors"].astype(np.float64))
    emb_unk = l2(unk["vectors"].astype(np.float64))
    if ENCODER_KIND == "puro":
        pure = np.load(HERE / "embeddings" / "pure.npz")
        pm = dict(zip(pure["paths"].tolist(), pure["vectors"]))
        emb_ref = l2(np.stack([pm[r[0]] for r in refs]).astype(np.float64))
        emb_test = l2(np.stack([pm[p[0]] for p in prueba]).astype(np.float64))
        emb_val = l2(np.stack([pm[p] for p in val["paths"].tolist()]).astype(np.float64))
        emb_unk = l2(np.stack([pm[p] for p in unk["paths"].tolist()]).astype(np.float64))
    return dict(
        taxa=taxa, visuales=visuales, guia=guia,
        refs=refs, emb_ref=emb_ref, tax_ref=np.array([r[1] for r in refs]), obs_ref=[r[2] for r in refs],
        prueba=prueba, emb_test=emb_test, tax_test=np.array([p[1] for p in prueba]), obs_test=[p[2] for p in prueba],
        emb_val=emb_val, tax_val=val["taxon"],
        emb_unk=emb_unk, sp_unk=unk["species"], obs_unk=unk["obs"],
    )


def altitudes(D):
    """Altitud por registro: la del propio registro (GBIF) o la muestra DEM SRTM90 más cercana ya en caché."""
    dem = json.loads(DEM_CACHE.read_text(encoding="utf-8"))
    pts = np.array([[float(a) for a in k.split(",")] for k in dem])
    vals = np.array(list(dem.values()), dtype=np.float64)

    def near(lat, lon):
        d2 = (pts[:, 0] - lat) ** 2 + ((pts[:, 1] - lon) * math.cos(math.radians(lat))) ** 2
        i = int(d2.argmin())
        return (float(vals[i]), math.sqrt(d2[i]) * 111.0) if not math.isnan(vals[i]) else (None, None)

    recs = list(csv.DictReader((DEPTO / "occurrences" / "records_v1.csv").open(encoding="utf-8")))
    test_obs = {f"inat:{o}" for o in D["obs_test"]}
    por_especie = defaultdict(list)
    alt_de = {}
    fuente = Counter()
    for r in recs:
        lat, lon = float(r["latitude"]), float(r["longitude"])
        if r["elevation_m"]:
            h = float(r["elevation_m"])
            fuente["registro"] += 1
        else:
            h, km = near(lat, lon)
            if h is None or km > 6:
                continue
            fuente["dem_cercano"] += 1
        alt_de[r["record_id"]] = h
        if r["record_id"] not in test_obs:  # sin fuga: la prueba no alimenta la gaussiana
            por_especie[r["taxon_id"]].append(h)
    gauss = {}
    for tid in D["visuales"]:
        hs = por_especie.get(tid, [])
        if len(hs) >= 5:
            gauss[tid] = (float(np.mean(hs)), float(max(np.std(hs), 50.0)), len(hs))
    test_alt = [alt_de.get(f"inat:{o}") for o in D["obs_test"]]

    # Desconocidas: ubicación de la observación iNat (caché del scraper), altitud por DEM si cae en Antioquia.
    loc = {}
    for f in INAT_CACHE.glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        for o in d.get("results", []) if isinstance(d, dict) else d:
            if o.get("location"):
                la, lo = map(float, o["location"].split(","))
                loc[str(o["id"])] = (la, lo)
    unk_alt = []
    for o in D["obs_unk"]:
        if o in loc:
            h, km = near(*loc[o])
            unk_alt.append(h if (h is not None and km <= 6) else None)
        else:
            unk_alt.append(None)
    return gauss, test_alt, unk_alt, dict(fuente)


# ── método viejo ──────────────────────────────────────────────────────────
def old_method(D):
    prec, cents, ids, tau = read_openset(OPENSET_BIN)
    allowed = set(json.loads(ALLOWED.read_text(encoding="utf-8"))["ANTIOQUIA"])
    keep = [i for i, x in enumerate(ids) if x in allowed]
    C = cents[keep]

    def maha(X):
        out = np.empty(len(X))
        for i, x in enumerate(X):
            diff = x[None, :] - C
            out[i] = math.sqrt(max(0.0, float(np.min(np.einsum("ij,jk,ik->i", diff, prec, diff)))))
        return out

    def knn(X):
        sim = X @ D["emb_ref"].T
        preds = []
        for row in sim:
            idx = np.argpartition(-row, K_OLD - 1)[:K_OLD]
            v = Counter()
            for j in idx:  # KnnVote.votes: suma de (1 - distancia coseno) = similitud
                v[D["tax_ref"][j]] += float(row[j])
            best = None
            for j in sorted(idx, key=lambda j: -row[j]):
                t = D["tax_ref"][j]
                if best is None or v[t] > v[best]:
                    best = t
            preds.append(best)
        return np.array(preds)

    return dict(
        tau=tau, n_centroids=len(keep),
        pred_test=knn(D["emb_test"]), maha_test=maha(D["emb_test"]),
        pred_unk=knn(D["emb_unk"]), maha_unk=maha(D["emb_unk"]),
    )


# ── creador del Admin ─────────────────────────────────────────────────────
def build_admin_package(D, gauss):
    tx = D["taxa"]
    sp = D["visuales"]
    genus = {t: tx[t]["genus"] for t in sp}
    family = {t: tx[t]["family"] for t in sp}

    # Centroides L2 (mismas fotos que el teléfono usa como referencias)
    cent = np.stack([l2(D["emb_ref"][D["tax_ref"] == t].sum(0)) for t in sp])
    individuos = {t: len({o for o, x in zip(D["obs_ref"], D["tax_ref"]) if x == t}) for t in sp}
    fotos = {t: int((D["tax_ref"] == t).sum()) for t in sp}

    generos = sorted(set(genus.values()))
    gcent = np.stack([l2(cent[[i for i, t in enumerate(sp) if genus[t] == g]].sum(0)) for g in generos])
    familias = sorted(set(family.values()))
    fam_de_gen = {g: family[next(t for t in sp if genus[t] == g)] for g in generos}
    fcent = np.stack([l2(gcent[[i for i, g in enumerate(generos) if fam_de_gen[g] == f]].sum(0)) for f in familias])

    # Capa 1 + nodos: Weibull sobre distancias de entrenamiento
    wb, radio = {}, {}
    for i, t in enumerate(sp):
        d = 1 - D["emb_ref"][D["tax_ref"] == t] @ cent[i]
        wb[t] = fit_weibull(d)
        radio[t] = ALPHA * weibull_q(*wb[t], COBERTURA)
    # Variante: radio ajustado con las fotos APARTADAS (val) — las de entrenamiento quedan pegadas a su propio centroide.
    radio_val = {}
    for i, t in enumerate(sp):
        dv = 1 - D["emb_val"][D["tax_val"] == t] @ cent[i]
        radio_val[t] = ALPHA * weibull_q(*fit_weibull(dv), COBERTURA) if len(dv) >= 5 else radio[t]
    tau_g = {}
    for gi, g in enumerate(generos):
        mask = np.isin(D["tax_ref"], [t for t in sp if genus[t] == g])
        tau_g[g] = 1 - ALPHA * weibull_q(*fit_weibull(1 - D["emb_ref"][mask] @ gcent[gi]), COBERTURA)
    tau_f = {}
    for fi, f in enumerate(familias):
        mask = np.isin(D["tax_ref"], [t for t in sp if family[t] == f])
        tau_f[f] = 1 - ALPHA * weibull_q(*fit_weibull(1 - D["emb_ref"][mask] @ fcent[fi]), COBERTURA)

    # Capa 2: clústeres sugeridos por la confusión en val (nearest-centroid)
    pred_val = np.array(sp)[np.argmax(D["emb_val"] @ cent.T, 1)]
    n_val = Counter(D["tax_val"].tolist())
    conf = Counter(zip(D["tax_val"].tolist(), pred_val.tolist()))
    pares = set()
    for (a, b), n in conf.items():
        if a != b and n_val[a] and n / n_val[a] >= CONFUSION_CLUSTER:
            pares.add(tuple(sorted((a, b))))
    padre = {t: t for t in sp}

    def raiz(t):
        while padre[t] != t:
            padre[t] = padre[padre[t]]
            t = padre[t]
        return t

    for a, b in pares:
        padre[raiz(a)] = raiz(b)
    grupos = defaultdict(list)
    for t in sp:
        grupos[raiz(t)].append(t)
    clusters = []
    for miembros in sorted((g for g in grupos.values() if len(g) >= 2), key=lambda g: -len(g)):
        idx = [sp.index(t) for t in miembros]
        X = D["emb_ref"][np.isin(D["tax_ref"], miembros)]
        base = [cent[idx].mean(0)] + [cent[i] for i in idx]
        resid = np.concatenate([D["emb_ref"][D["tax_ref"] == t] - cent[sp.index(t)] for t in miembros])
        _, _, vt = np.linalg.svd(resid, full_matrices=False)
        _, _, vt_all = np.linalg.svd(X, full_matrices=False)
        cols = np.stack(base + list(vt[:28]) + list(vt_all[:COLUMNAS_W]))
        q, _ = np.linalg.qr(cols.T)
        W = q[:, :COLUMNAS_W]
        erec = lambda Z, W=W: np.clip(1 - ((Z @ W) ** 2).sum(1), 0, None)
        e_m = erec(X)
        eps = float(np.percentile(e_m, 95))
        # Desempate dentro del clúster: LDA con contracción sobre las coordenadas de W
        Z = X @ W
        y = D["tax_ref"][np.isin(D["tax_ref"], miembros)]
        mus = np.stack([Z[y == t].mean(0) for t in miembros])
        Sw = sum(np.cov((Z[y == t] - mus[k]).T, bias=True) * (y == t).sum() for k, t in enumerate(miembros)) / len(Z)
        Sw = 0.7 * Sw + 0.3 * np.trace(Sw) / Sw.shape[0] * np.eye(Sw.shape[0])
        Sinv = np.linalg.inv(Sw)
        clusters.append(dict(id=f"CL_{len(clusters) + 1:02d}", miembros=miembros, W=W, eps=eps, mus=mus, Sinv=Sinv,
                             erec=erec, falso_rechazo_train=float((e_m > eps).mean())))
    cluster_de = {t: c for c in clusters for t in c["miembros"]}

    return dict(sp=sp, genus=genus, family=family, cent=cent, generos=generos, gcent=gcent, familias=familias,
                fcent=fcent, fam_de_gen=fam_de_gen, radio=radio, radio_val=radio_val, wb=wb, tau_g=tau_g, tau_f=tau_f, clusters=clusters,
                cluster_de=cluster_de, gauss=gauss, individuos=individuos, fotos=fotos, pares=sorted(pares))


def admin_identify(P, X, alts, geo=True, capa2=True, radios="radio"):
    """Cascada del Admin. Devuelve (estado, especie|None, genero|None, familia|None, score_rechazo)."""
    cos = X @ P["cent"].T
    cg = X @ P["gcent"].T
    cf = X @ P["fcent"].T
    rad = np.array([P[radios][t] for t in P["sp"]])
    score = ((1 - cos) / rad).min(1)
    out = []
    for i in range(len(X)):
        ok = np.where(1 - cos[i] <= rad)[0]
        if len(ok):
            k = ok[np.argmax(cos[i][ok])]
            t = P["sp"][k]
            c = P["cluster_de"].get(t) if capa2 else None
            if c is not None:
                x = X[i:i + 1]
                if c["erec"](x)[0] > c["eps"]:
                    out.append(("OSR_CLUSTER", None, P["genus"][t], None, score[i]))
                    continue
                z = (x @ c["W"])[0]
                dd = [float((z - m) @ c["Sinv"] @ (z - m)) for m in c["mus"]]
                t = c["miembros"][int(np.argmin(dd))]
            if geo and alts[i] is not None and t in P["gauss"]:
                mu, sd, _ = P["gauss"][t]
                if p_altitud(alts[i], mu, sd) < UMBRAL_GEO:
                    out.append(("OSR_GEO", None, P["genus"][t], None, score[i]))
                    continue
            out.append(("MATCH_SPECIES", t, P["genus"][t], P["family"][t], score[i]))
            continue
        g = [j for j, gg in enumerate(P["generos"]) if cg[i, j] >= P["tau_g"][gg]]
        if g:
            j = max(g, key=lambda j: cg[i, j])
            out.append(("MATCH_GENUS", None, P["generos"][j], P["fam_de_gen"][P["generos"][j]], score[i]))
            continue
        f = [j for j, ff in enumerate(P["familias"]) if cf[i, j] >= P["tau_f"][ff]]
        if f:
            j = max(f, key=lambda j: cf[i, j])
            out.append(("MATCH_FAMILY", None, None, P["familias"][j], score[i]))
            continue
        out.append(("OSR_GLOBAL", None, None, None, score[i]))
    return out


# ── taxonomía de las desconocidas ─────────────────────────────────────────
FAMILIA_DE_GENERO = {
    "Craugastor": "Craugastoridae", "Dendropsophus": "Hylidae", "Espadarana": "Centrolenidae",
    "Leptodactylus": "Leptodactylidae", "Rhinella": "Bufonidae", "Scinax": "Hylidae", "Smilisca": "Hylidae",
    "Hyloxalus": "Dendrobatidae", "Pristimantis": "Strabomantidae", "Sachatamia": "Centrolenidae",
    "Boana": "Hylidae", "Hyalinobatrachium": "Centrolenidae", "Trachycephalus": "Hylidae",
}


def ideal_unknown(genero, P):
    if genero in P["generos"]:
        return "MATCH_GENUS"
    if FAMILIA_DE_GENERO.get(genero) in P["familias"]:
        return "MATCH_FAMILY"
    return "OSR_GLOBAL"


def main():
    D = load()
    print(f"Referencias {len(D['refs'])}  prueba {len(D['prueba'])}  val {len(D['emb_val'])}  desconocidas {len(D['emb_unk'])}")
    gauss, test_alt, unk_alt, fuente_alt = altitudes(D)
    print(f"Gaussianas de altitud: {len(gauss)}/30  prueba con altitud {sum(a is not None for a in test_alt)}  "
          f"desconocidas con altitud en Antioquia {sum(a is not None for a in unk_alt)}")

    O = old_method(D)  # con el encoder puro el .bin no aplica (se calibró con fine-tuning); se reporta solo el k-NN
    P = build_admin_package(D, gauss)
    print(f"Clústeres sugeridos: {[c['miembros'] for c in P['clusters']]}")

    y = D["tax_test"]
    n = len(y)
    res = {"fecha": date.today().isoformat(), "datos": {
        "referencias": len(D["refs"]), "prueba_conocidas": n, "val_calibracion": len(D["emb_val"]),
        "desconocidas": len(D["emb_unk"]), "especies_desconocidas": sorted(set(D["sp_unk"].tolist())),
        "altitud_fuente": fuente_alt, "prueba_con_altitud": sum(a is not None for a in test_alt),
        "desconocidas_con_altitud": sum(a is not None for a in unk_alt)}}

    # VIEJO
    acc_old = O["maha_test"] <= O["tau"]
    acc_old_u = O["maha_unk"] <= O["tau"]
    res["viejo"] = {
        "top1_visual_sin_rechazo": float((O["pred_test"] == y).mean()),
        "kar": float(acc_old.mean()),
        "aceptadas_y_correctas": float(((O["pred_test"] == y) & acc_old).mean()),
        "far": float(acc_old_u.mean()),
        "auroc": auroc(O["maha_test"], O["maha_unk"]),
        "desconocidas_respuesta_segura": float((~acc_old_u).mean()),
        "desconocidas_nivel_correcto": 0.0,  # el paquete viejo no tiene cascada: rechaza o nombra una especie
        "tau": O["tau"],
    }

    # NUEVO: variantes para aislar cada capa
    variantes = {
        "capa1_cascada": dict(geo=False, capa2=False),
        "capa1_cascada_clusters": dict(geo=False, capa2=True),
        "completo_tres_capas": dict(geo=True, capa2=True),
        "completo_radio_val": dict(geo=True, capa2=True, radios="radio_val"),
        "sin_altitud_radio_val": dict(geo=False, capa2=True, radios="radio_val"),
    }
    res["nuevo"] = {}
    for nombre, kw in variantes.items():
        rk = admin_identify(P, D["emb_test"], test_alt, **kw)
        ru = admin_identify(P, D["emb_unk"], unk_alt, **kw)
        est_k = Counter(r[0] for r in rk)
        est_u = Counter(r[0] for r in ru)
        sp_ok = sum(1 for r, t in zip(rk, y) if r[0] == "MATCH_SPECIES" and r[1] == t)
        sp_bad = sum(1 for r, t in zip(rk, y) if r[0] == "MATCH_SPECIES" and r[1] != t)
        gen_ok = sum(1 for r, t in zip(rk, y) if r[0] in ("MATCH_GENUS", "OSR_CLUSTER", "OSR_GEO") and r[2] == P["genus"][t])
        nivel_ok = 0
        especie_falsa_u = 0
        for r, sp_u in zip(ru, D["sp_unk"]):
            g = sp_u.split("_")[0]
            ideal = ideal_unknown(g, P)
            if r[0] == "MATCH_SPECIES":
                especie_falsa_u += 1
            elif ideal == "MATCH_GENUS" and r[2] == g:
                nivel_ok += 1  # "Género sp." (o clúster/altitud del género correcto)
            elif ideal == "MATCH_FAMILY" and r[0] == "MATCH_FAMILY" and r[3] == FAMILIA_DE_GENERO.get(g):
                nivel_ok += 1
            elif ideal == "OSR_GLOBAL" and r[0] in ("OSR_GLOBAL", "OSR_CLUSTER", "OSR_GEO"):
                nivel_ok += 1
        res["nuevo"][nombre] = {
            "especie_correcta": sp_ok / n,
            "especie_equivocada": sp_bad / n,
            "kar": est_k["MATCH_SPECIES"] / n,
            "genero_correcto_sin_especie": gen_ok / n,
            "estados_conocidas": dict(est_k),
            "far": especie_falsa_u / len(ru),
            "auroc": auroc([r[4] for r in rk], [r[4] for r in ru]),
            "estados_desconocidas": dict(est_u),
            "desconocidas_respuesta_segura": 1 - especie_falsa_u / len(ru),
            "desconocidas_nivel_correcto": nivel_ok / len(ru),
        }

    # Misma exigencia: el camino nuevo al KAR del viejo
    s_k = np.array([r[4] for r in admin_identify(P, D["emb_test"], test_alt, geo=False, capa2=False)])
    s_u = np.array([r[4] for r in admin_identify(P, D["emb_unk"], unk_alt, geo=False, capa2=False)])
    thr = np.quantile(s_k, res["viejo"]["kar"])
    res["misma_exigencia"] = {"kar_objetivo": res["viejo"]["kar"], "far_viejo": res["viejo"]["far"],
                              "far_nuevo_capa1": float((s_u <= thr).mean())}

    # Por especie desconocida
    por_unk = {}
    rn = admin_identify(P, D["emb_unk"], unk_alt, geo=True, capa2=True)
    for s in sorted(set(D["sp_unk"].tolist())):
        m = D["sp_unk"] == s
        est = Counter(r[0] for r, mm in zip(rn, m) if mm)
        por_unk[s] = {"n": int(m.sum()), "ideal": ideal_unknown(s.split("_")[0], P),
                      "viejo_aceptada_como_especie": float(acc_old_u[m].mean()),
                      "nuevo_estados": dict(est)}
    res["por_desconocida"] = por_unk

    # Por especie conocida
    por_sp = {}
    rfull = admin_identify(P, D["emb_test"], test_alt, geo=True, capa2=True)
    for t in P["sp"]:
        m = y == t
        if not m.any():
            continue
        por_sp[D["taxa"][t]["scientific_name"]] = {
            "n": int(m.sum()), "fotos_ref": P["fotos"][t], "individuos_ref": P["individuos"][t],
            "viejo_ok": float(((O["pred_test"] == y) & acc_old)[m].mean()),
            "nuevo_ok": float(np.mean([r[0] == "MATCH_SPECIES" and r[1] == t for r, mm in zip(rfull, m) if mm])),
            "radio": P["radio"][t], "tau_cos": 1 - P["radio"][t],
            "geo_rechazos": int(sum(1 for r, mm in zip(rfull, m) if mm and r[0] == "OSR_GEO")),
        }
    res["por_especie"] = por_sp
    res["clusters"] = [{"id": c["id"], "miembros": [D["taxa"][t]["scientific_name"] for t in c["miembros"]],
                        "epsilon": c["eps"], "columnas": int(c["W"].shape[1]),
                        "bytes_fp16": int(c["W"].size * 2)} for c in P["clusters"]]
    res["nodos"] = {"generos": {g: P["tau_g"][g] for g in P["generos"]}, "familias": {f: P["tau_f"][f] for f in P["familias"]}}

    # Tamaños
    bytes_viejo = (ROOT / "anura-android/app/src/main/assets/packages/antioquia/package.sqlite").stat().st_size + OPENSET_BIN.stat().st_size
    bytes_nuevo = (len(P["sp"]) + len(P["generos"]) + len(P["familias"])) * 512 * 2 + sum(c["W"].size * 2 for c in P["clusters"])
    res["tamano"] = {"viejo_bytes": bytes_viejo, "nuevo_vectores_y_matrices_bytes_fp16": bytes_nuevo}

    # JSON del paquete (esquema de 19_ADMIN/Esquema JSON del Paquete)
    pkg = {
        "package_metadata": {"package_id": "COL_ANURA/ANTIOQUIA/admin", "region_name": "Antioquia (departamento completo, mismo alcance que el paquete del teléfono)",
                             "version": "2.0.0-rc1", "last_updated": date.today().isoformat(), "embedding_dim": 512,
                             "quantization": "FP16", "encoder": "encoder_anura_fp16.onnx (BioCLIP 1 ViT-B/16 con fine-tuning, sin reentrenar desde 2026-09-12)",
                             "tau_kind": "cosine_similarity", "cobertura": COBERTURA, "alpha": ALPHA, "umbral_geo": UMBRAL_GEO},
        "family_nodes": [{"family_id": f, "rejection_tau_family": round(P["tau_f"][f], 4), "tau_kind": "cosine_similarity",
                          "centroid": [round(float(v), 5) for v in P["fcent"][i]]} for i, f in enumerate(P["familias"])],
        "genus_nodes": [{"genus_id": g, "family_id": P["fam_de_gen"][g], "rejection_tau_genus": round(P["tau_g"][g], 4),
                         "tau_kind": "cosine_similarity", "centroid": [round(float(v), 5) for v in P["gcent"][i]]}
                        for i, g in enumerate(P["generos"])],
        "species_catalog": [{
            "taxon_id": t, "genus_id": P["genus"][t], "nombre": D["taxa"][t]["scientific_name"],
            "sub_centroids": [{"morph_id": "global", "dim": 512, "vector": [round(float(v), 5) for v in P["cent"][i]]}],
            "rejection_tau": round(1 - P["radio"][t], 4), "tau_kind": "cosine_similarity",
            "weibull": {"beta": round(P["wb"][t][0], 4), "eta": round(P["wb"][t][1], 6)},
            "context_parameters": {
                "altitude_mean_msnm": round(P["gauss"][t][0]) if t in P["gauss"] else None,
                "altitude_std_dev": round(P["gauss"][t][1]) if t in P["gauss"] else None,
                "weights": None, "substrate_priors": None, "audio_signature_id": None},
            "provenance": {"fotos": P["fotos"][t], "individuos": P["individuos"][t], "dataset": "training/manifiesto.json (train)",
                           "encoder_checkpoint_sha256": "98a6c54d6edb27e2…"},
        } for i, t in enumerate(P["sp"])],
        "cryptic_clusters": [{"cluster_id": c["id"], "member_species": c["miembros"], "dim": 512, "columnas": int(c["W"].shape[1]),
                              "bytes": int(c["W"].size * 2), "epsilon_reconstruction": round(c["eps"], 5),
                              "estado": "SUGERIDO — falta que el herpetólogo lo confirme"} for c in P["clusters"]],
    }
    res["encoder"] = ENCODER_KIND
    if ENCODER_KIND == "puro":
        res["viejo"] = {"top1_visual_sin_rechazo": res["viejo"]["top1_visual_sin_rechazo"], "nota": "k-NN con vectores puros; el rechazo Mahalanobis del teléfono no aplica"}
    sufijo = "" if ENCODER_KIND == "fine_tuning" else "_puro"
    (HERE / f"package_admin_antioquia_v2{sufijo}.json").write_text(json.dumps(pkg, ensure_ascii=False), encoding="utf-8")
    (HERE / f"results{sufijo}.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("viejo", "nuevo", "misma_exigencia", "tamano")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
