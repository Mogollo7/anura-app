"""
export_mobile_inference.py — Exporta lo que Android necesita para reproducir la identificación de PC.

Salidas:
  anura-android/app/src/test/resources/golden/openset_v1.1.0_clean.bin   centroides + precisión + tau (referencia de paridad)
  anura-android/app/src/test/resources/golden/openset_v1.1.0_clean.json  procedencia y hashes
  anura-android/app/src/test/resources/golden/allowed_ids_golden.json    especies del paquete de referencia
  (El APK ya no trae modelo Open Set: cada paquete regional lleva el suyo en la tabla open_set_model,
   mismo formato ANOS; lo compila dataset-service, src/osrModelo.js.)
  anura-android/app/src/test/resources/golden/golden_v1.json           embeddings/decisiones de referencia
  anura-android/app/src/test/resources/golden/preprocess_*.bin         caso de prueba del preprocesado
  <--images-out>/                                                       imágenes del set de referencia (no van al repo)

Receta de centroides y Mahalanobis: se importan de tools/catalog/run_open_set_evaluation.py (no se copian).
Formato .bin (little-endian): b"ANOS", int32 version=1, int32 dim, int32 k, float64 tau,
float64[dim*dim] precision (row-major), float64[k*dim] centroides, k x (int32 len + utf8 species_id).
"""
import argparse
import hashlib
import json
import shutil
import struct
import sys
from pathlib import Path

import numpy as np
import onnxruntime as ort
import open_clip
import sqlite_vec
import sqlite3
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "catalog"))
from run_open_set_evaluation import compute_centroids, min_mahalanobis  # noqa: E402
from taxonomic_resolution import SpeciesResolver  # noqa: E402

ANDROID = ROOT / "anura-android" / "app" / "src"
PACKAGE = ROOT / "COLOMBIA_ANURA/ANTIOQUIA/packages/v1.0.0/antioquia_base_v1.0.0.sqlite"
ENCODER = ROOT / "bioclip/checkpoints/encoder_anura_fp16.onnx"
CATALOG = ROOT / "visual_catalog/v1.0.0/manifest.json"
COVARIANCE = ROOT / "covariance/v1.1.0_CLEAN/covariance_matrix.npz"
THRESHOLD = ROOT / "threshold/v1.1.0_CLEAN/manifest.json"
REF_EMB = ROOT / "evaluation/fase13/embeddings/reference_embeddings.npz"
TRAIN_EMB = ROOT / "evaluation/fase13/embeddings/train_embeddings.npz"
EVAL_EMB = ROOT / "evaluation/open_set_v1/knn/knn_embeddings.npz"
EVAL_LABELS = ROOT / "evaluation/open_set_v1/knn/knn_open_set_results.json"
IMAGES_ROOT = ROOT / "data cleaned"
K_VECINOS = 5

GOLDEN_PLAN = [
    ("Dendrobates_truncatus", "KNOWN_IN_PACKAGE"),
    ("Pristimantis_paisa", "KNOWN_IN_PACKAGE"),
    ("Boana_boans", "KNOWN_IN_PACKAGE"),
    ("Rhinella_horribilis", "KNOWN_IN_PACKAGE"),
    ("Engystomops_pustulosus", "KNOWN_IN_PACKAGE"),
    ("Scinax_ruber", "KNOWN_IN_PACKAGE"),
    ("Hyloscirtus_palmeri", "KNOWN_IN_PACKAGE"),
    ("Pristimantis_achatinus", "KNOWN_IN_PACKAGE"),
    ("Pithecopus_hypochondrialis", "KNOWN_NOT_IN_PACKAGE"),
    ("Sachatamia_electrops", "UNKNOWN"),
    ("Sachatamia_electrops", "UNKNOWN"),
    ("Hyloxalus_picachos", "UNKNOWN"),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_resolver():
    return SpeciesResolver(ROOT / "training/taxonomia.py", ROOT / "taxonomy/species/species_registry.json")


def package_allowed_ids(resolver, release_ids) -> list[str]:
    """IDs del catalogo de 41 centroides que SI estan en el paquete regional instalado (VISUAL_ENABLED).
    El Open Set solo debe comparar contra especies que el paquete realmente ofrece: comparar contra
    las 41 nacionales aceptaria erroneamente especies que Antioquia ni siquiera tiene."""
    conn = sqlite3.connect(PACKAGE)
    pkg_species = [r[0] for r in conn.execute("select scientific_name from taxa where visual_status='VISUAL_ENABLED'")]
    conn.close()
    allowed = []
    for name in pkg_species:
        sid = resolver.resolve(name)["species_id"]
        if sid in release_ids:
            allowed.append(sid)
    return sorted(set(allowed))


def build_centroids(resolver, release_ids):
    ref = np.load(REF_EMB)
    train = np.load(TRAIN_EMB)
    
    ref_canonical = np.array([resolver.resolve(n)["canonical_name"] for n in ref["species"]])
    train_canonical = np.array([resolver.resolve(n)["canonical_name"] for n in train["species"]])
    ref_centroids = compute_centroids(ref["embeddings"], ref_canonical)
    train_centroids = compute_centroids(train["embeddings"], train_canonical)
    centroids = {}
    for name, c in ref_centroids.items():
        sid = resolver.resolve(name.replace("_", " "))["species_id"]
        if sid in release_ids:
            centroids[sid] = c
    for name, c in train_centroids.items():
        sid = resolver.resolve(name.replace("_", " "))["species_id"]
        if sid in release_ids and sid not in centroids:
            centroids[sid] = c
    return dict(sorted(centroids.items()))


def write_openset_bin(path: Path, precision: np.ndarray, centroids: dict, tau: float):
    ids = list(centroids.keys())
    mat = np.stack([centroids[i] for i in ids]).astype("<f8")
    dim = precision.shape[0]
    with open(path, "wb") as f:
        f.write(b"ANOS")
        f.write(struct.pack("<iiid", 1, dim, len(ids), tau))
        f.write(np.ascontiguousarray(precision, dtype="<f8").tobytes())
        f.write(mat.tobytes())
        for sid in ids:
            raw = sid.encode("utf-8")
            f.write(struct.pack("<i", len(raw)))
            f.write(raw)


def read_openset_bin(path: Path):
    data = path.read_bytes()
    assert data[:4] == b"ANOS"
    version, dim, k, tau = struct.unpack_from("<iiid", data, 4)
    off = 4 + struct.calcsize("<iiid")
    precision = np.frombuffer(data, "<f8", dim * dim, off).reshape(dim, dim)
    off += dim * dim * 8
    cents = np.frombuffer(data, "<f8", k * dim, off).reshape(k, dim)
    off += k * dim * 8
    ids = []
    for _ in range(k):
        (n,) = struct.unpack_from("<i", data, off)
        off += 4
        ids.append(data[off:off + n].decode("utf-8"))
        off += n
    return version, precision, dict(zip(ids, cents)), tau


def export_preprocess_case(preprocess, out_dir: Path):
    """Caso sintético retrato (no cuadrado) para verificar el Resize bicúbico + CenterCrop de Kotlin."""
    rng = np.random.default_rng(20260922)
    h, w = 241, 317
    pixels = rng.integers(0, 256, size=(h, w, 3), dtype=np.uint8)
    tensor = preprocess(Image.fromarray(pixels, "RGB")).numpy().astype("<f4")
    with open(out_dir / "preprocess_input_rgb.bin", "wb") as f:
        f.write(struct.pack("<ii", w, h))
        f.write(pixels.tobytes())
    (out_dir / "preprocess_expected_chw.bin").write_bytes(tensor.tobytes())
    return {"width": w, "height": h, "expected_shape": list(tensor.shape)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images-out", required=True, help="Carpeta fuera del repo para las imágenes del set de referencia")
    args = ap.parse_args()

    golden_dir = ANDROID / "test/resources/golden"
    assets = golden_dir
    golden_dir.mkdir(parents=True, exist_ok=True)
    images_out = Path(args.images_out)
    images_out.mkdir(parents=True, exist_ok=True)

    threshold = json.loads(THRESHOLD.read_text(encoding="utf-8"))
    tau = float(threshold["threshold"])
    precision = np.load(COVARIANCE)["precision"].astype(np.float64)
    resolver = build_resolver()
    release_ids = set(json.loads(CATALOG.read_text(encoding="utf-8"))["species_ids"])
    centroids = build_centroids(resolver, release_ids)
    allowed_ids = package_allowed_ids(resolver, release_ids)
    print(f"[centroides] {len(centroids)} especies (catalogo nacional), tau={tau}")
    print(f"[paquete] {len(allowed_ids)} especies permitidas para Open Set restringido")

    allowed_path = assets / "allowed_ids_golden.json"
    allowed_path.write_text(json.dumps({"ANTIOQUIA": allowed_ids}, indent=1), encoding="utf-8")

    bin_path = assets / "openset_v1.1.0_clean.bin"
    write_openset_bin(bin_path, precision, centroids, tau)
    _, precision_rt, centroids_rt, tau_rt = read_openset_bin(bin_path)

    # Paridad 1: el .bin reproduce exactamente los scores oficiales sobre el set de evaluación
    eval_emb = np.load(EVAL_EMB)["embeddings"].astype(np.float32)
    official = min_mahalanobis(eval_emb, centroids, precision)
    exported = min_mahalanobis(eval_emb, centroids_rt, precision_rt)
    parity_max_abs = float(np.max(np.abs(official - exported)))
    records = json.loads(EVAL_LABELS.read_text(encoding="utf-8"))["records"]
    y_unknown = np.array([r["known_unknown"] == "UNKNOWN" for r in records])
    kar = float(np.mean(official[~y_unknown] <= tau))
    far = float(np.mean(official[y_unknown] <= tau))
    decisions_changed = int(np.sum((official <= tau) != (exported <= tau)))
    print(f"[paridad .bin] max|dscore|={parity_max_abs:.3e}  decisiones cambiadas={decisions_changed}  KAR={kar:.4f}  FAR={far:.4f}")
    # centroides originales en float32 vs exportados en float64: solo ruido de redondeo
    assert parity_max_abs < 1e-5 and decisions_changed == 0

    manifest = {
        "artifact": "openset_v1.1.0_clean.bin",
        "allowed_by_package_file": "allowed_ids_golden.json",
        "allowed_by_package_sha256": sha256_file(allowed_path),
        "format": "ANOS v1 little-endian (ver docstring de tools/mobile/export_mobile_inference.py)",
        "method": threshold["calibration_method"],
        "metric": threshold["metric"],
        "tau": tau,
        "centroid_count": len(centroids),
        "species_ids": list(centroids.keys()),
        "threshold_release": threshold["threshold_release"],
        "covariance_release": "covariance_1.1.0_CLEAN",
        "catalog_release": json.loads(CATALOG.read_text(encoding="utf-8"))["catalog_release"],
        "encoder_onnx_sha256": sha256_file(ENCODER),
        "sha256": sha256_file(bin_path),
        "eval_parity": {"max_abs_score_diff": parity_max_abs, "kar": kar, "far": far, "n": len(records)},
    }
    (assets / "openset_v1.1.0_clean.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")

    # Set de referencia: ONNX fp16 en CPU + sqlite-vec del paquete + Mahalanobis
    _, _, preprocess = open_clip.create_model_and_transforms("hf-hub:imageomics/bioclip")
    session = ort.InferenceSession(str(ENCODER), providers=["CPUExecutionProvider"])
    restricted_centroids = {k: v for k, v in centroids.items() if k in set(allowed_ids)}
    conn = sqlite3.connect(PACKAGE)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    names = dict(conn.execute("select taxon_id, scientific_name from taxa"))

    used = set()
    golden = []
    for species, case in GOLDEN_PLAN:
        rec = next(r for r in records if r["true_species"] == species and r["path"] not in used)
        used.add(rec["path"])
        src = IMAGES_ROOT / rec["path"].replace("\\", "/")
        image = Image.open(src)
        x = preprocess(image).unsqueeze(0).numpy().astype(np.float32)
        emb = session.run(["embedding"], {"imagen": x})[0][0].astype(np.float32)
        emb = emb / np.linalg.norm(emb)
        rows_k1 = conn.execute(
            "select taxon_id, distance from vec_references where embedding match ? and k = ? order by distance",
            (emb.astype("<f4").tobytes(), K_VECINOS + 1),
        ).fetchall()
        rows = rows_k1[:K_VECINOS]
        # margen entre el 5.º y el 6.º vecino: si es ~0, el conjunto top-5 depende de ruido numérico
        k_boundary_gap = float(rows_k1[K_VECINOS][1] - rows_k1[K_VECINOS - 1][1])
        votes = {}
        for taxon, dist in rows:
            votes[taxon] = votes.get(taxon, 0.0) + (1.0 - dist)
        predicted = max(votes, key=votes.get)
        def mahalanobis_against(subset: dict) -> tuple[float, str]:
            ids = list(subset.keys())
            C = np.stack([subset[i] for i in ids])
            diff = emb.astype(np.float64)[None, :] - C
            d2 = np.einsum("kd,de,ke->k", diff, precision, diff)
            i = int(np.argmin(d2))
            return float(np.sqrt(max(0.0, d2[i]))), ids[i]

        score, nearest_full = mahalanobis_against(centroids)
        score_restricted, nearest_restricted = mahalanobis_against(restricted_centroids)
        file_name = f"golden_{len(golden):02d}_{species}.jpg"
        shutil.copyfile(src, images_out / file_name)
        golden.append({
            "file": file_name,
            "source_path": rec["path"],
            "true_species": species.replace("_", " "),
            "case": case,
            "embedding": [float(v) for v in emb],
            "neighbors": [{"taxon_id": t, "scientific_name": names[t], "distance": float(d)} for t, d in rows],
            "k_boundary_gap": k_boundary_gap,
            "predicted_taxon_id": predicted,
            "predicted_scientific_name": names[predicted],
            "mahalanobis_min": score,
            "nearest_centroid": nearest_full,
            "decision": "ACCEPT" if score <= tau else "REJECT",
            "mahalanobis_min_restricted": score_restricted,
            "nearest_centroid_restricted": nearest_restricted,
            "decision_restricted": "ACCEPT" if score_restricted <= tau else "REJECT",
        })
        print(
            f"  {file_name:<48} pred={names[predicted]:<28} maha={score:7.3f} {golden[-1]['decision']:<7} "
            f"restr={score_restricted:7.3f} {golden[-1]['decision_restricted']}",
        )

    out = {
        "encoder_onnx_sha256": manifest["encoder_onnx_sha256"],
        "package_sha256": sha256_file(PACKAGE),
        "openset_sha256": manifest["sha256"],
        "tau": tau,
        "k": K_VECINOS,
        "preprocess_case": export_preprocess_case(preprocess, golden_dir),
        "images": golden,
    }
    (golden_dir / "golden_v1.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"[OK] {len(golden)} imágenes de referencia en {images_out}")


if __name__ == "__main__":
    main()
