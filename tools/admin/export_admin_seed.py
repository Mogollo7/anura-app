"""Datos reales de Antioquia para el módulo administrativo.

El Admin nació con 41 especies simuladas que no coinciden con el paquete que corre
en el teléfono. Este script exporta, sin inventar nada, lo que el Admin necesita
para trabajar con el paquete real:

  - las especies con estado visual del catálogo de Antioquia (VISUAL_ENABLED y
    VISUAL_EXCLUDED_REVIEW), con fotos e individuos curados reales;
  - las referencias que viajan en el paquete del teléfono (mismo muestreo que
    pipeline_dataset/paquetes_zonales.py) y cuántas fotos quedan para val/test;
  - altitud por especie: registros del departamento con elevación propia (GBIF)
    o la muestra SRTM90 más cercana ya en caché (≤ 6 km);
  - presencia por subregión: observaciones reales (SUBREGIONS/*/subregion.json);
  - metadatos del paquete del teléfono y de los encoders que existen de verdad;
  - la comparación viejo contra nuevo (evaluation/admin_v2_comparison/results.json).

Uso:  python tools/admin/export_admin_seed.py
Salida: D:\\server\\Anura\\admin\\src\\data\\antioquia-real.json
"""

import csv
import hashlib
import json
import math
import sqlite3
import sys
import types
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(r"D:\Anura")
DEPTO = ROOT / "COLOMBIA_ANURA" / "ANTIOQUIA"
PHONE_PKG = ROOT / "anura-android/app/src/main/assets/packages/antioquia/package.sqlite"
PHONE_ENCODER = ROOT / "anura-android/app/src/main/assets/models/encoder_anura_fp16.onnx"
OPENSET_BIN = ROOT / "anura-android/app/src/main/assets/openset/openset_v1.1.0_clean.bin"
SERVER_BIOCLIP25 = Path(r"D:\server\Anura\models\hub\models--imageomics--bioclip-2.5-vith14")
RESULTS = ROOT / "evaluation" / "admin_v2_comparison" / "results.json"
OUT = Path(r"D:\server\Anura\admin\src\data\antioquia-real.json")

sys.path.insert(0, str(ROOT / "pipeline_dataset"))
sys.modules.setdefault("sqlite_vec", types.ModuleType("sqlite_vec"))
import paquetes_zonales as pz  # noqa: E402

# Carpeta de SUBREGIONS → id que usa el Admin
SUBREGION_ID = {
    "VALLE_DE_ABURRA": "01_valle_de_aburra", "ORIENTE": "02_oriente", "SUROESTE": "03_suroeste",
    "OCCIDENTE": "04_occidente", "NORTE": "05_norte", "NORDESTE": "06_nordeste",
    "MAGDALENA_MEDIO": "07_magdalena_medio", "BAJO_CAUCA": "08_bajo_cauca", "URABA": "09_uraba_antioqueno",
}


def sha256(path, limit=None):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def sin_tildes(t):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", t.upper()) if unicodedata.category(c) != "Mn").strip()


def cargar_municipios():
    """Polígonos DANE de los municipios de Antioquia (geo/antioquia_municipios.geojson), con su caja."""
    g = json.loads((ROOT / "geo" / "antioquia_municipios.geojson").read_text(encoding="utf-8"))
    out = []
    for f in g["features"]:
        geom = f["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        anillos = [np.array(poly[0], dtype=np.float64) for poly in polys]
        todos = np.concatenate(anillos)
        out.append((sin_tildes(f["properties"]["MPIO_CNMBR"]), anillos, todos.min(0), todos.max(0)))
    return out


def dentro(lon, lat, anillo):
    x, y = anillo[:, 0], anillo[:, 1]
    x2, y2 = np.roll(x, -1), np.roll(y, -1)
    cruza = ((y > lat) != (y2 > lat)) & (lon < (x2 - x) * (lat - y) / np.where(y2 - y == 0, 1e-12, y2 - y) + x)
    return bool(cruza.sum() % 2)


def municipio_de(lon, lat, municipios):
    for nombre, anillos, lo, hi in municipios:
        if lo[0] <= lon <= hi[0] and lo[1] <= lat <= hi[1] and any(dentro(lon, lat, a) for a in anillos):
            return nombre
    return None


def main():
    catalogo = json.loads((DEPTO / "catalog" / "catalog_v1.json").read_text(encoding="utf-8"))
    guia = json.loads((ROOT / "COLOMBIA_ANURA" / "taxonomy" / "taxonomy_guide.json").read_text(encoding="utf-8"))
    taxa = [t for t in catalogo["taxa"] if t["visual_status"] in ("VISUAL_ENABLED", "VISUAL_EXCLUDED_REVIEW")]
    visuales = {t["taxon_id"] for t in taxa if t["visual_status"] == "VISUAL_ENABLED"}

    # Referencias del teléfono y particiones
    split = {}
    for part in ("train", "val", "test"):
        for e in json.loads(pz.MANIFIESTO.read_text(encoding="utf-8"))["particiones"][part]:
            if not e.get("aumentada"):
                split[e["ruta"].replace("\\", "/")] = part
    legado = {tid: guia[tid]["directory_legacy"] for tid in visuales}
    refs, prueba = pz.seleccionar_referencias(visuales, legado, split)
    ref_n = Counter(r[1] for r in refs)
    ref_ind = defaultdict(set)
    for r in refs:
        ref_ind[r[1]].add(r[2])
    test_n = Counter(p[1] for p in prueba)
    val_n = Counter()
    for rel, part in split.items():
        if part == "val":
            carpeta = rel.split("/")[0]
            for tid, d in legado.items():
                if d == carpeta:
                    val_n[tid] += 1

    # Altitud
    dem = json.loads((ROOT / "COLOMBIA_ANURA" / "cache" / "opentopodata_srtm90m.json").read_text(encoding="utf-8"))
    pts = np.array([[float(a) for a in k.split(",")] for k in dem])
    vals = np.array(list(dem.values()), dtype=np.float64)

    def near(lat, lon):
        d2 = (pts[:, 0] - lat) ** 2 + ((pts[:, 1] - lon) * math.cos(math.radians(lat))) ** 2
        i = int(d2.argmin())
        return (None if math.isnan(vals[i]) else float(vals[i])), math.sqrt(d2[i]) * 111.0

    # Subregión de cada registro: point-in-polygon contra los municipios DANE (cubre GBIF e iNaturalist).
    municipios = cargar_municipios()
    muni_a_sub = {}
    for carpeta, sid in SUBREGION_ID.items():
        for m in json.loads((DEPTO / "SUBREGIONS" / carpeta / "subregion.json").read_text(encoding="utf-8"))["municipalities"]:
            muni_a_sub[sin_tildes(m)] = sid
    presencia = defaultdict(Counter)
    sin_municipio = 0

    alts = defaultdict(list)
    fuentes = defaultdict(Counter)
    registros = defaultdict(Counter)
    for r in csv.DictReader((DEPTO / "occurrences" / "records_v1.csv").open(encoding="utf-8")):
        registros[r["taxon_id"]][r["source"]] += 1
        m = municipio_de(float(r["longitude"]), float(r["latitude"]), municipios)
        if m and m in muni_a_sub:
            presencia[r["taxon_id"]][muni_a_sub[m]] += 1
        else:
            sin_municipio += 1
        if r["elevation_m"]:
            alts[r["taxon_id"]].append(float(r["elevation_m"]))
            fuentes[r["taxon_id"]]["registro"] += 1
        else:
            h, km = near(float(r["latitude"]), float(r["longitude"]))
            if h is not None and km <= 6:
                alts[r["taxon_id"]].append(h)
                fuentes[r["taxon_id"]]["dem"] += 1

    # Subregiones reales
    por_nombre = defaultdict(dict)
    subregiones = []
    for carpeta, sid in SUBREGION_ID.items():
        d = json.loads((DEPTO / "SUBREGIONS" / carpeta / "subregion.json").read_text(encoding="utf-8"))
        for s in d["species"]:
            # Por id de iNaturalist: las listas de subregión usan el nombre de iNaturalist, no el del catálogo.
            clave = str(s.get("inaturalist_taxon_id") or s["scientific_name"])
            por_nombre[clave][sid] = por_nombre[clave].get(sid, 0) + s["observations_in_subregion"]
        subregiones.append({"id": sid, "observaciones": d["observations"], "especiesObservadas": d["species_observed"],
                            "chao1": d["species_estimated_chao1"], "completitud": d["completeness"],
                            "municipios": len(d["municipalities"])})

    especies = []
    for t in sorted(taxa, key=lambda t: (t["family"], t["genus"], t["scientific_name"])):
        tid = t["taxon_id"]
        hs = np.array(alts.get(tid, []))
        alt = None
        if len(hs):
            alt = {"n": int(len(hs)), "media": round(float(hs.mean())), "desviacion": round(float(hs.std())),
                   "min": round(float(hs.min())), "max": round(float(hs.max())),
                   "p05": round(float(np.percentile(hs, 5))), "p95": round(float(np.percentile(hs, 95))),
                   "fuente": dict(fuentes[tid])}
        especies.append({
            "taxonId": tid, "familia": t["family"], "genero": t["genus"], "epiteto": t["species_epithet"],
            "especie": t["scientific_name"], "estadoVisual": t["visual_status"],
            "motivoExclusion": t.get("visual_exclusion_reason") or None,
            "estadoDatos": t.get("visual_data_status"), "evidencia": t["occurrence_evidence"],
            "fotosCuradas": t.get("photos_curated", 0), "individuosCurados": t.get("individuals_curated", 0),
            "fotosReferenciaPaquete": ref_n.get(tid, 0), "individuosReferenciaPaquete": len(ref_ind.get(tid, ())),
            "fotosVal": val_n.get(tid, 0), "fotosPrueba": test_n.get(tid, 0),
            "registros": dict(registros.get(tid, {})), "altitud": alt,
            "subregiones": dict(presencia.get(tid, {})),
            "gbifKey": t.get("gbif_species_key"), "inatTaxonId": guia.get(tid, {}).get("inaturalist_taxon_id"),
            "carpetaDataset": guia.get(tid, {}).get("directory_legacy"),
        })

    con = sqlite3.connect(PHONE_PKG)
    pkg_info = dict(con.execute("select key, value from package_info").fetchall())
    seed = {
        "generado": date.today().isoformat(),
        "fuentes": {
            "catalogo": "COLOMBIA_ANURA/ANTIOQUIA/catalog/catalog_v1.json",
            "particiones": "training/manifiesto.json",
            "altitud": "occurrences/records_v1.csv + cache SRTM90 (OpenTopoData)",
            "subregiones": "COLOMBIA_ANURA/ANTIOQUIA/SUBREGIONS/*/subregion.json",
            "fotos": "D:/Anura/data cleaned/<carpetaDataset>/",
        },
        "paqueteTelefono": {
            "archivo": "anura-android/app/src/main/assets/packages/antioquia/package.sqlite",
            "bytes": PHONE_PKG.stat().st_size, "info": pkg_info,
            "openSet": {"archivo": "openset/openset_v1.1.0_clean.bin", "bytes": OPENSET_BIN.stat().st_size,
                        "metodo": "Mahalanobis Ledoit-Wolf compartida, τ 39,354", "centroides": 41, "permitidosAntioquia": 30},
            "decision": "k-NN k=5 coseno sobre las referencias; el prior de zona y el clima solo reordenan las alternativas mostradas",
        },
        "encoders": {
            "telefono": {"archivo": "encoder_anura_fp16.onnx", "bytes": PHONE_ENCODER.stat().st_size,
                         "sha256": pkg_info.get("encoder_onnx_sha256"), "base": "BioCLIP 1 · ViT-B/16 con fine-tuning",
                         "ajustado": True, "checkpoint": "bioclip/checkpoints/bioclip_anura_mejor.pt",
                         "checkpointSha256": pkg_info.get("encoder_checkpoint_sha256"), "dimensiones": 512},
            "servidor": {"repo": "imageomics/bioclip-2.5-vith14", "base": "BioCLIP 2.5 · ViT-H/14",
                         "dimensiones": 1024, "instalado": SERVER_BIOCLIP25.exists(),
                         "usadoPor": "services/ai-service (/api/predict + clasificador sklearn custom_model.pkl)"},
        },
        "subregiones": subregiones,
        "especies": especies,
        "comparacion": json.loads(RESULTS.read_text(encoding="utf-8")) if RESULTS.exists() else None,
    }
    # Mismo método con BioCLIP 1 PURO (sin fine-tuning): ¿conviene cambiar el encoder del teléfono?
    puro = RESULTS.with_name("results_puro.json")
    if puro.exists():
        rp = json.loads(puro.read_text(encoding="utf-8"))
        seed["comparacionEncoderPuro"] = {"fecha": rp["fecha"], "nuevo": rp["nuevo"], "clusters": rp["clusters"],
                                          "top1_knn": rp["viejo"]["top1_visual_sin_rechazo"]}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(seed, ensure_ascii=False, indent=1), encoding="utf-8")
    seed["fuentes"]["presenciaSubregion"] = f"records_v1.csv → municipio DANE (point-in-polygon) → subregión; {sin_municipio} registros sin municipio asignable"
    OUT.write_text(json.dumps(seed, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"sin municipio: {sin_municipio}")
    print(f"{len(especies)} especies ({len(visuales)} visuales) · {len(subregiones)} subregiones → {OUT}")
    for e in especies:
        print(f"  {e['especie']:32s} {e['estadoVisual']:24s} fotos {e['fotosCuradas']:4d} ind {e['individuosCurados']:4d} "
              f"ref {e['fotosReferenciaPaquete']:3d} alt {e['altitud']['media'] if e['altitud'] else '—'} "
              f"sub {len(e['subregiones'])}")


if __name__ == "__main__":
    main()
