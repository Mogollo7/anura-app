"""Evaluacion umbral 'rana vs no-rana': compara la distancia Mahalanobis min-a-centroide
(mismo mecanismo Open Set de Fase 13 / tools/catalog/run_open_set_evaluation.py) para:
  - especies CONOCIDAS (deberian aceptarse, score bajo)
  - especies DESCONOCIDAS pero SI son anuros (Hyloxalus_picachos, Sachatamia_electrops — Fase 13)
  - imagenes NO-RANA (negativos genericos de Wikimedia Commons)

Pregunta que responde: ¿el mismo umbral tau=39.35 (KAR95%) separa 'no-rana' de
'rana desconocida', o ambos caen igual de lejos de los centroides?
"""
import io
import json
import sys
from pathlib import Path

import numpy as np
import torch
import open_clip
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)

ANURA_ROOT = Path(r"D:\Anura")
NEGATIVOS_DIR = Path(__file__).parent / "negativos"
MODELO_HF = "hf-hub:imageomics/bioclip"

TAU = 39.35406371422803  # threshold/v1.0.0 KAR95%, congelado en Fase 13

# Scores conocidos de Fase 13 (FASE13_FINAL_METRICS.json) para especies DESCONOCIDAS
# que SI son anuros (fuera del catalogo pero dentro del dominio biologico)
SCORES_UNKNOWN_ANURO_FASE13 = {
    "Hyloxalus_picachos": [40.628686012573404, 46.64891122021613, 27.66623920490018, 33.39311248271728,
                            28.808223406515953, 28.796953542715315, 37.1454564804038, 34.02677366053322,
                            32.38369164708735, 27.215121214010814, 32.0264189606483, 28.35744455267602,
                            27.28556729813777, 28.720910053847014, 36.53078484773658],
}


def compute_centroids(X, y):
    return {c: np.mean(X[y == c], axis=0) for c in np.unique(y)}


def min_mahalanobis(X, centroids, precision_matrix):
    classes = list(centroids.keys())
    C = np.array([centroids[c] for c in classes])
    diff = X[:, None, :] - C[None, :, :]
    d2 = np.einsum("nkd,de,nke->nk", diff, precision_matrix, diff)
    return np.sqrt(np.maximum(0.0, np.min(d2, axis=1)))


def embed_images(paths, modelo, preprocesar, dispositivo):
    embeddings = []
    for p in paths:
        img = Image.open(p).convert("RGB")
        tensor = preprocesar(img).unsqueeze(0).to(dispositivo)
        with torch.no_grad():
            feat = modelo.encode_image(tensor)
            feat = feat / feat.norm(dim=-1, keepdim=True)  # L2-normalizado, igual que el catalogo
        embeddings.append(feat.cpu().numpy()[0])
    return np.array(embeddings, dtype=np.float32)


def main():
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Dispositivo: {dispositivo}")

    print("Cargando BioCLIP v1 (mismo encoder que el catalogo: bioclip_anura_v1)...")
    modelo, _, preprocesar = open_clip.create_model_and_transforms(MODELO_HF)
    modelo = modelo.to(dispositivo).eval()

    print("Cargando precision matrix (covariance/v1.1.0_CLEAN)...")
    cov_data = np.load(ANURA_ROOT / "covariance/v1.1.0_CLEAN/covariance_matrix.npz")
    precision_matrix = cov_data["precision"]

    print("Cargando embeddings de referencia/train (Fase 13) para reconstruir centroides...")
    sys.path.insert(0, str(ANURA_ROOT / "tools/catalog"))
    from taxonomic_resolution import SpeciesResolver

    resolver = SpeciesResolver(
        ANURA_ROOT / "training/taxonomia.py",
        ANURA_ROOT / "taxonomy/species/species_registry.json",
    )
    with open(ANURA_ROOT / "visual_catalog/v1.0.0/manifest.json", encoding="utf-8") as f:
        release_species_ids = set(json.load(f)["species_ids"])

    ref = np.load(ANURA_ROOT / "evaluation/fase13/embeddings/reference_embeddings.npz")
    train = np.load(ANURA_ROOT / "evaluation/fase13/embeddings/train_embeddings.npz")

    ref_canonical = np.array([resolver.resolve(n)["canonical_name"] for n in ref["species"]])
    train_canonical = np.array([resolver.resolve(n)["canonical_name"] for n in train["species"]])

    ref_centroids = compute_centroids(ref["embeddings"], ref_canonical)
    train_centroids = compute_centroids(train["embeddings"], train_canonical)

    all_centroids = {}
    for name, c in ref_centroids.items():
        sid = resolver.resolve(name.replace("_", " "))["species_id"]
        if sid in release_species_ids:
            all_centroids[sid] = c
    for name, c in train_centroids.items():
        sid = resolver.resolve(name.replace("_", " "))["species_id"]
        if sid in release_species_ids and sid not in all_centroids:
            all_centroids[sid] = c

    print(f"Centroides disponibles: {len(all_centroids)} / {len(release_species_ids)} especies del catalogo")

    # ── Embeber negativos (no-rana) ──
    neg_paths = sorted(p for p in NEGATIVOS_DIR.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
    print(f"\nImagenes no-rana encontradas: {len(neg_paths)}")
    neg_emb = embed_images(neg_paths, modelo, preprocesar, dispositivo)
    neg_scores = min_mahalanobis(neg_emb, all_centroids, precision_matrix)

    resultado_negativos = [
        {"file": p.name, "score": float(s), "decision": "ACCEPT" if s <= TAU else "REJECT"}
        for p, s in zip(neg_paths, neg_scores)
    ]

    # ── Comparacion de distribuciones ──
    print("\n" + "=" * 70)
    print(f"TAU (umbral congelado Fase 13, KAR95%) = {TAU:.2f}")
    print("=" * 70)

    print(f"\nNO-RANA (n={len(neg_scores)}):")
    print(f"  media={neg_scores.mean():.2f}  min={neg_scores.min():.2f}  max={neg_scores.max():.2f}")
    rechazados_neg = int((neg_scores > TAU).sum())
    print(f"  REJECT (score > tau): {rechazados_neg}/{len(neg_scores)} ({100*rechazados_neg/len(neg_scores):.1f}%)")

    for especie, scores in SCORES_UNKNOWN_ANURO_FASE13.items():
        arr = np.array(scores)
        print(f"\nRANA DESCONOCIDA (fuera de catalogo) — {especie} (n={len(arr)}, Fase 13):")
        print(f"  media={arr.mean():.2f}  min={arr.min():.2f}  max={arr.max():.2f}")
        rechazados = int((arr > TAU).sum())
        print(f"  REJECT (score > tau): {rechazados}/{len(arr)} ({100*rechazados/len(arr):.1f}%)")

    print("\n" + "-" * 70)
    print("Detalle por imagen no-rana:")
    for r in sorted(resultado_negativos, key=lambda r: r["score"]):
        print(f"  {r['score']:7.2f}  {r['decision']:7s}  {r['file']}")

    out = {
        "tau": TAU,
        "negativos": resultado_negativos,
        "resumen_no_rana": {
            "n": len(neg_scores), "media": float(neg_scores.mean()),
            "min": float(neg_scores.min()), "max": float(neg_scores.max()),
            "reject_rate": rechazados_neg / len(neg_scores),
        },
        "resumen_rana_desconocida_fase13": {
            especie: {"media": float(np.mean(s)), "min": float(np.min(s)), "max": float(np.max(s)),
                      "reject_rate": float((np.array(s) > TAU).sum() / len(s))}
            for especie, s in SCORES_UNKNOWN_ANURO_FASE13.items()
        },
    }
    out_path = Path(__file__).parent / "resultado_umbral_no_rana.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nGuardado: {out_path}")


if __name__ == "__main__":
    main()
